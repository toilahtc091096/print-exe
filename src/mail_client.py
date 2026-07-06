from __future__ import annotations

import email
import imaplib
import logging
import re
from email.header import decode_header
from email.message import Message
from pathlib import Path

from config import Config
from fs_ops import unique_path


def _decode_header_value(value: str | None) -> str:
    if not value:
        return ""
    parts = decode_header(value)
    decoded = []
    for text, charset in parts:
        if isinstance(text, bytes):
            decoded.append(text.decode(charset or "utf-8", errors="replace"))
        else:
            decoded.append(text)
    return "".join(decoded)


def _safe_filename(filename: str) -> str:
    filename = _decode_header_value(filename)
    filename = filename.replace("\\", "_").replace("/", "_").strip()
    filename = re.sub(r"[\x00-\x1f<>:\"|?*]", "_", filename)
    return filename or "attachment"


class MailClient:
    def __init__(self, config: Config) -> None:
        self.config = config

    def download_attachments(self, target_dir: Path) -> list[Path]:
        downloaded: list[Path] = []
        logging.info("Connecting to IMAP host=%s port=%s", self.config.imap_host, self.config.imap_port)
        with imaplib.IMAP4_SSL(
            self.config.imap_host,
            self.config.imap_port,
            timeout=self.config.imap_timeout_seconds,
        ) as client:
            logging.info("Logging in to IMAP as %s", self.config.imap_user)
            client.login(self.config.imap_user, self.config.imap_password)
            logging.info("Selecting mailbox/label: %s", self.config.imap_mailbox)
            status, _ = client.select(f'"{self.config.imap_mailbox}"')
            if status != "OK":
                raise RuntimeError(f"Cannot select mailbox: {self.config.imap_mailbox}")

            logging.info("Searching mailbox with criteria: %s", self.config.search_criteria)
            status, data = client.search(None, *self.config.search_criteria.split())
            if status != "OK":
                raise RuntimeError(f"Cannot search mailbox with criteria: {self.config.search_criteria}")

            message_ids = data[0].split()
            logging.info("Found %s email(s) matching criteria", len(message_ids))
            for message_id in message_ids:
                status, message_data = client.fetch(message_id, "(RFC822)")
                if status != "OK":
                    logging.warning("Cannot fetch email id=%s", message_id.decode("ascii", errors="ignore"))
                    continue

                message = email.message_from_bytes(message_data[0][1])
                saved = self._save_message_attachments(message, target_dir)
                downloaded.extend(saved)
                logging.info(
                    "Email id=%s saved %s attachment(s)",
                    message_id.decode("ascii", errors="ignore"),
                    len(saved),
                )

                if self.config.mark_email_seen:
                    client.store(message_id, "+FLAGS", "\\Seen")
                if self.config.done_mailbox:
                    self._move_message(client, message_id, self.config.done_mailbox)

        return downloaded

    def _move_message(self, client: imaplib.IMAP4_SSL, message_id: bytes, mailbox: str) -> None:
        quoted_mailbox = f'"{mailbox}"'

        status, _ = client.create(quoted_mailbox)
        if status not in {"OK", "NO"}:
            logging.warning("Cannot create/check done mailbox: %s", mailbox)

        status, _ = client._simple_command("MOVE", message_id, quoted_mailbox)
        if status == "OK":
            logging.info("Moved email %s to mailbox: %s", message_id.decode("ascii", errors="ignore"), mailbox)
            return

        logging.info("IMAP MOVE not available, falling back to COPY + delete for email %s", message_id)
        status, _ = client.copy(message_id, quoted_mailbox)
        if status != "OK":
            raise RuntimeError(f"Cannot copy email {message_id!r} to mailbox: {mailbox}")
        client.store(message_id, "+FLAGS", "\\Deleted")
        client.expunge()
        logging.info("Copied email %s to mailbox and removed from source: %s", message_id.decode("ascii", errors="ignore"), mailbox)

    def _save_message_attachments(self, message: Message, target_dir: Path) -> list[Path]:
        saved: list[Path] = []
        for part in message.walk():
            if part.get_content_maintype() == "multipart":
                continue
            if part.get("Content-Disposition") is None:
                continue

            filename = part.get_filename()
            if not filename:
                continue

            safe_name = _safe_filename(filename)
            output_path = unique_path(target_dir / safe_name)
            payload = part.get_payload(decode=True)
            if payload is None:
                continue

            output_path.write_bytes(payload)
            saved.append(output_path)
            logging.info("Saved attachment: %s", output_path)

        return saved

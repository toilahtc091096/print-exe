from __future__ import annotations

import logging
import time
from pathlib import Path

from config import Config, load_config
from fs_ops import (
    clear_directory,
    ensure_directories,
    extract_archives,
    iter_printable_files,
    move_to_printed,
    remove_empty_dirs,
)
from mail_client import MailClient
from printer import print_file


def setup_logging(base_dir: Path) -> None:
    base_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(base_dir / "worker.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def run_cycle(config: Config, mail_client: MailClient) -> None:
    ensure_directories(config.pending_dir, config.printed_dir)

    if config.delete_printed_dir_each_cycle:
        logging.info("Clearing printed directory: %s", config.printed_dir)
        clear_directory(config.printed_dir)

    downloaded = mail_client.download_attachments(config.pending_dir)
    if downloaded:
        logging.info("Downloaded %s attachment(s)", len(downloaded))

    extracted = extract_archives(config.pending_dir)
    if extracted:
        logging.info("Extracted %s archive(s)", len(extracted))

    printable_files = iter_printable_files(config.pending_dir, config.allowed_extensions)
    for file_path in printable_files:
        try:
            logging.info("Printing: %s", file_path)
            print_file(
                file_path,
                config.printer_name,
                config.print_wait_seconds,
                config.pdf_print_app_path,
                config.print_pages,
                config.print_duplex,
            )
        except Exception:
            logging.exception("Failed to print file: %s", file_path)
            continue

        try:
            moved_to = move_to_printed(file_path, config.pending_dir, config.printed_dir)
            logging.info("Moved printed file to: %s", moved_to)
        except Exception:
            logging.exception("Printed file but failed to move it to printed directory: %s", file_path)

    remove_empty_dirs(config.pending_dir)


def main() -> int:
    config = load_config()
    setup_logging(config.base_dir)
    ensure_directories(config.pending_dir, config.printed_dir)

    if config.delete_printed_dir_on_start:
        logging.info("Clearing printed directory on startup: %s", config.printed_dir)
        clear_directory(config.printed_dir)

    mail_client = MailClient(config)
    logging.info("Worker started. Mailbox=%s Pending=%s", config.imap_mailbox, config.pending_dir)

    while True:
        try:
            run_cycle(config, mail_client)
        except Exception:
            logging.exception("Worker cycle failed")
        time.sleep(config.poll_interval_seconds)


if __name__ == "__main__":
    raise SystemExit(main())

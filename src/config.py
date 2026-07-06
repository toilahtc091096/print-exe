from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def _bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if not value:
        return default
    return int(value)


@dataclass(frozen=True)
class Config:
    imap_host: str
    imap_port: int
    imap_user: str
    imap_password: str
    imap_mailbox: str
    done_mailbox: str | None
    imap_timeout_seconds: int
    search_criteria: str
    poll_interval_seconds: int
    base_dir: Path
    pending_dir: Path
    printed_dir: Path
    printer_name: str | None
    pdf_print_app_path: Path | None
    print_wait_seconds: int
    delete_printed_dir_on_start: bool
    delete_printed_dir_each_cycle: bool
    mark_email_seen: bool
    allowed_extensions: set[str]


def load_config() -> Config:
    _load_dotenv(Path.cwd() / ".env")

    base_dir = Path(os.getenv("BASE_DIR", "C:/ho_so_in"))
    pending_dir = Path(os.getenv("PENDING_DIR", str(base_dir / "chua_in")))
    printed_dir = Path(os.getenv("PRINTED_DIR", str(base_dir / "da_in")))
    allowed_extensions = {
        item.strip().lower()
        for item in os.getenv("ALLOWED_EXTENSIONS", ".pdf").split(",")
        if item.strip()
    }

    config = Config(
        imap_host=os.getenv("EMAIL_IMAP_HOST", ""),
        imap_port=_int_env("EMAIL_IMAP_PORT", 993),
        imap_user=os.getenv("EMAIL_IMAP_USER", ""),
        imap_password=os.getenv("EMAIL_IMAP_PASSWORD", ""),
        imap_mailbox=os.getenv("EMAIL_IMAP_MAILBOX", "INBOX"),
        done_mailbox=os.getenv("EMAIL_DONE_MAILBOX") or None,
        imap_timeout_seconds=_int_env("EMAIL_IMAP_TIMEOUT_SECONDS", 30),
        search_criteria=os.getenv("EMAIL_SEARCH_CRITERIA", "ALL"),
        poll_interval_seconds=_int_env("POLL_INTERVAL_SECONDS", 600),
        base_dir=base_dir,
        pending_dir=pending_dir,
        printed_dir=printed_dir,
        printer_name=os.getenv("PRINTER_NAME") or None,
        pdf_print_app_path=Path(os.environ["PDF_PRINT_APP_PATH"]) if os.getenv("PDF_PRINT_APP_PATH") else None,
        print_wait_seconds=_int_env("PRINT_WAIT_SECONDS", 10),
        delete_printed_dir_on_start=_bool_env("DELETE_PRINTED_DIR_ON_START", True),
        delete_printed_dir_each_cycle=_bool_env("DELETE_PRINTED_DIR_EACH_CYCLE", False),
        mark_email_seen=_bool_env("MARK_EMAIL_SEEN", True),
        allowed_extensions=allowed_extensions,
    )

    missing = [
        name
        for name, value in {
            "EMAIL_IMAP_HOST": config.imap_host,
            "EMAIL_IMAP_USER": config.imap_user,
            "EMAIL_IMAP_PASSWORD": config.imap_password,
        }.items()
        if not value
    ]
    if missing:
        raise ValueError("Missing required env values: " + ", ".join(missing))

    return config

from __future__ import annotations

import logging
import os
import re
import subprocess
import time
from pathlib import Path


def _find_sumatra_pdf(configured_path: Path | None) -> Path | None:
    candidates: list[Path] = []
    if configured_path:
        candidates.append(configured_path)

    for env_name in ("ProgramFiles", "ProgramFiles(x86)", "LOCALAPPDATA"):
        env_value = os.getenv(env_name)
        if env_value:
            candidates.append(Path(env_value) / "SumatraPDF" / "SumatraPDF.exe")

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def _build_sumatra_print_settings(print_pages: str | None, print_duplex: str | None) -> list[str]:
    settings: list[str] = []
    if print_pages:
        settings.append(print_pages)
    if print_duplex:
        settings.append(print_duplex)
    return settings


def _infer_sumatra_print_settings(
    path: Path,
    print_pages: str | None,
    print_duplex: str | None,
) -> tuple[list[str], str | None]:
    stem = path.stem

    if re.fullmatch(r"HAN[0-9A-Za-z]+", stem):
        return ["1"], "matched HAN filename rule"

    if re.fullmatch(r"\d+", stem):
        return ["1,7", "duplexlong"], "matched numeric filename rule"

    return _build_sumatra_print_settings(print_pages, print_duplex), None


def _print_pdf(
    path: Path,
    printer_name: str | None,
    pdf_print_app_path: Path | None,
    print_pages: str | None,
    print_duplex: str | None,
) -> bool:
    sumatra_path = _find_sumatra_pdf(pdf_print_app_path)
    if not sumatra_path:
        return False

    command = [str(sumatra_path), "-silent"]
    print_settings, matched_rule = _infer_sumatra_print_settings(path, print_pages, print_duplex)
    if matched_rule:
        logging.info("Using PDF print rule for %s: %s", path.name, matched_rule)
    if print_settings:
        command.extend(["-print-settings", ",".join(print_settings)])
    if printer_name:
        command.extend(["-print-to", printer_name])
    else:
        command.append("-print-to-default")
    command.append(str(path.resolve()))

    subprocess.run(command, check=True)
    return True


def print_file(
    path: Path,
    printer_name: str | None,
    wait_seconds: int,
    pdf_print_app_path: Path | None = None,
    print_pages: str | None = None,
    print_duplex: str | None = None,
) -> None:
    absolute_path = str(path.resolve())
    if path.suffix.lower() == ".pdf" and _print_pdf(
        path, printer_name, pdf_print_app_path, print_pages, print_duplex
    ):
        if wait_seconds > 0:
            time.sleep(wait_seconds)
        return

    if print_pages or print_duplex:
        logging.warning(
            "PRINT_PAGES/PRINT_DUPLEX is set, but these controls are only applied to PDF files through SumatraPDF. "
            "File will print with the current app/printer default: %s",
            path,
        )

    if printer_name:
        command = [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            f'Start-Process -FilePath "{absolute_path}" -Verb PrintTo -ArgumentList "{printer_name}" -WindowStyle Hidden',
        ]
    else:
        command = [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            f'Start-Process -FilePath "{absolute_path}" -Verb Print -WindowStyle Hidden',
        ]

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as exc:
        if path.suffix.lower() == ".pdf":
            raise RuntimeError(
                "Cannot print PDF because Windows has no PDF app associated with the Print action. "
                "Install SumatraPDF and set PDF_PRINT_APP_PATH, or set a default PDF app that supports Print."
            ) from exc
        raise

    if wait_seconds > 0:
        time.sleep(wait_seconds)

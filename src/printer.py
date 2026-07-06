from __future__ import annotations

import os
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


def _print_pdf(path: Path, printer_name: str | None, pdf_print_app_path: Path | None) -> bool:
    sumatra_path = _find_sumatra_pdf(pdf_print_app_path)
    if not sumatra_path:
        return False

    command = [str(sumatra_path), "-silent"]
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
) -> None:
    absolute_path = str(path.resolve())
    if path.suffix.lower() == ".pdf" and _print_pdf(path, printer_name, pdf_print_app_path):
        if wait_seconds > 0:
            time.sleep(wait_seconds)
        return

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

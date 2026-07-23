from __future__ import annotations

import time
import shutil
from pathlib import Path


ARCHIVE_EXTENSIONS = {
    ".zip",
    ".tar",
    ".tar.gz",
    ".tgz",
    ".tar.bz2",
    ".tbz2",
    ".tar.xz",
    ".txz",
}


def _is_archive(path: Path) -> bool:
    name = path.name.lower()
    return any(name.endswith(extension) for extension in ARCHIVE_EXTENSIONS)


def ensure_directories(*paths: Path) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def clear_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    for child in path.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path

    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    counter = 1
    while True:
        candidate = parent / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def extract_archives(root: Path) -> list[Path]:
    extracted_dirs: list[Path] = []

    for archive_path in list(root.rglob("*")):
        if not archive_path.is_file() or not _is_archive(archive_path):
            continue

        target_dir = unique_path(archive_path.with_suffix(""))
        target_dir.mkdir(parents=True, exist_ok=False)
        shutil.unpack_archive(str(archive_path), str(target_dir))
        archive_path.unlink()
        extracted_dirs.append(target_dir)

    return extracted_dirs


def iter_printable_files(root: Path, allowed_extensions: set[str]) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in allowed_extensions:
            files.append(path)
    return sorted(files, key=lambda item: str(item).lower())


def move_to_printed(
    path: Path,
    pending_dir: Path,
    printed_dir: Path,
    *,
    retries: int = 5,
    retry_delay_seconds: float = 1.0,
) -> Path:
    relative_path = path.relative_to(pending_dir)

    last_error: OSError | None = None
    for attempt in range(retries + 1):
        target = unique_path(printed_dir / relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)

        try:
            shutil.move(str(path), str(target))
            return target
        except OSError as exc:
            last_error = exc
            if attempt >= retries:
                break
            time.sleep(retry_delay_seconds)

    assert last_error is not None
    raise last_error


def remove_empty_dirs(root: Path) -> None:
    for path in sorted(root.rglob("*"), key=lambda item: len(item.parts), reverse=True):
        if path.is_dir():
            try:
                path.rmdir()
            except OSError:
                pass

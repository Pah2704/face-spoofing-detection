"""Safe, selective extraction of OULU-NPU Protocol 1 members."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import os
from pathlib import Path, PurePosixPath
import shutil
import tarfile
from typing import Callable, Iterable

from .oulu import (
    SPLIT_ORDER,
    VideoRecord,
    load_protocol_1,
    protocol_directory,
)


GIB = 1024**3


class ArchiveError(RuntimeError):
    """Raised for unsafe, incomplete or inconsistent dataset archives."""


@dataclass(frozen=True, slots=True)
class ArchivePlan:
    selected_files: int
    selected_bytes: int
    missing_files: int
    missing_bytes: int
    existing_files: int
    archives: dict[str, dict[str, int]]

    def to_dict(self) -> dict[str, object]:
        return {
            "selected_files": self.selected_files,
            "selected_bytes": self.selected_bytes,
            "missing_files": self.missing_files,
            "missing_bytes": self.missing_bytes,
            "existing_files": self.existing_files,
            "archives": self.archives,
        }


@dataclass(frozen=True, slots=True)
class ExtractionProgress:
    completed_files: int
    total_files: int
    completed_bytes: int
    total_bytes: int
    current_member: str


def _safe_member_name(name: str) -> bool:
    path = PurePosixPath(name)
    return bool(name) and not path.is_absolute() and ".." not in path.parts


def _index_archive(
    archive_path: Path,
) -> tuple[tarfile.TarFile, dict[str, tarfile.TarInfo]]:
    if not archive_path.is_file():
        raise ArchiveError(f"Missing archive: {archive_path}.")

    archive = tarfile.open(archive_path, mode="r:")
    index: dict[str, tarfile.TarInfo] = {}
    try:
        for member in archive.getmembers():
            if not _safe_member_name(member.name):
                raise ArchiveError(
                    f"Unsafe path {member.name!r} in {archive_path}."
                )
            if member.issym() or member.islnk():
                raise ArchiveError(
                    f"Links are not allowed in dataset archive: {member.name}."
                )
            if member.name in index:
                raise ArchiveError(
                    f"Duplicate member {member.name!r} in {archive_path}."
                )
            index[member.name] = member
    except Exception:
        archive.close()
        raise
    return archive, index


def ensure_protocol_files(raw_root: Path | str, protocol: int = 1) -> Path:
    """Extract only one protocol directory from Protocols.tar when needed."""

    root = Path(raw_root)
    target_dir = protocol_directory(root, protocol)
    required = ("Train.txt", "Dev.txt", "Test.txt")
    if all((target_dir / name).is_file() for name in required):
        return target_dir

    archive_path = root / "Protocols.tar"
    archive, index = _index_archive(archive_path)
    prefix = f"Protocols/Protocol_{protocol}/"
    selected = [
        member
        for name, member in index.items()
        if name.startswith(prefix) and member.isfile()
    ]
    if not selected:
        archive.close()
        raise ArchiveError(
            f"No files for Protocol {protocol} found in {archive_path}."
        )

    try:
        for member in selected:
            _copy_member(archive, member, root)
    finally:
        archive.close()

    if not all((target_dir / name).is_file() for name in required):
        raise ArchiveError(
            f"Protocol {protocol} extraction completed but required files are missing."
        )
    return target_dir


def _required_members(
    records: Iterable[VideoRecord], include_eye_locations: bool
) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for record in records:
        grouped[record.archive_name].append(record.video_member)
        if include_eye_locations:
            grouped[record.archive_name].append(record.eye_member)
    return grouped


def plan_extraction(
    records: Iterable[VideoRecord],
    raw_root: Path | str,
    *,
    include_eye_locations: bool = True,
) -> ArchivePlan:
    """Resolve selected members, sizes and remaining disk requirements."""

    root = Path(raw_root)
    grouped = _required_members(records, include_eye_locations)
    total_files = 0
    total_bytes = 0
    missing_files = 0
    missing_bytes = 0
    existing_files = 0
    archive_summaries: dict[str, dict[str, int]] = {}

    for archive_name in sorted(grouped):
        archive_path = root / archive_name
        archive, index = _index_archive(archive_path)
        try:
            archive_selected = 0
            archive_bytes = 0
            archive_missing = 0
            for member_name in grouped[archive_name]:
                member = index.get(member_name)
                if member is None or not member.isfile():
                    raise ArchiveError(
                        f"Required member {member_name!r} missing from {archive_path}."
                    )
                archive_selected += 1
                archive_bytes += member.size
                destination = root / PurePosixPath(member_name)
                if destination.exists():
                    if not destination.is_file():
                        raise ArchiveError(
                            f"Extraction target exists but is not a file: "
                            f"{destination}."
                        )
                    actual_size = destination.stat().st_size
                    if actual_size != member.size:
                        raise ArchiveError(
                            f"Refusing to overwrite {destination}: existing size "
                            f"{actual_size} differs from archive size {member.size}."
                        )
                    existing_files += 1
                else:
                    archive_missing += 1
                    missing_files += 1
                    missing_bytes += member.size

            total_files += archive_selected
            total_bytes += archive_bytes
            archive_summaries[archive_name] = {
                "selected_files": archive_selected,
                "selected_bytes": archive_bytes,
                "missing_files": archive_missing,
            }
        finally:
            archive.close()

    return ArchivePlan(
        selected_files=total_files,
        selected_bytes=total_bytes,
        missing_files=missing_files,
        missing_bytes=missing_bytes,
        existing_files=existing_files,
        archives=archive_summaries,
    )


def _copy_member(
    archive: tarfile.TarFile, member: tarfile.TarInfo, raw_root: Path
) -> None:
    if not member.isfile() or not _safe_member_name(member.name):
        raise ArchiveError(f"Refusing to extract invalid member: {member.name!r}.")

    destination = raw_root / PurePosixPath(member.name)
    resolved_root = raw_root.resolve()
    resolved_destination = destination.resolve()
    if resolved_root not in resolved_destination.parents:
        raise ArchiveError(
            f"Member would escape raw root: {member.name!r}."
        )

    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_name(destination.name + ".part")
    if partial.exists():
        partial.unlink()

    source = archive.extractfile(member)
    if source is None:
        raise ArchiveError(f"Cannot read archive member: {member.name}.")
    try:
        with partial.open("wb") as target:
            shutil.copyfileobj(source, target, length=8 * 1024 * 1024)
    except Exception:
        partial.unlink(missing_ok=True)
        raise
    finally:
        source.close()

    if partial.stat().st_size != member.size:
        actual = partial.stat().st_size
        partial.unlink(missing_ok=True)
        raise ArchiveError(
            f"Size mismatch extracting {member.name}: {actual} != {member.size}."
        )
    os.replace(partial, destination)
    try:
        os.utime(destination, (member.mtime, member.mtime))
    except (OSError, OverflowError):
        pass


def extract_protocol_1(
    raw_root: Path | str,
    *,
    include_eye_locations: bool = True,
    reserve_gib: float = 5.0,
    progress: Callable[[ExtractionProgress], None] | None = None,
) -> ArchivePlan:
    """Extract only files selected by Protocol 1, leaving archives untouched."""

    root = Path(raw_root)
    ensure_protocol_files(root, protocol=1)
    records = load_protocol_1(root)
    extraction_plan = plan_extraction(
        records, root, include_eye_locations=include_eye_locations
    )

    free_bytes = shutil.disk_usage(root).free
    reserve_bytes = int(reserve_gib * GIB)
    if extraction_plan.missing_bytes + reserve_bytes > free_bytes:
        raise ArchiveError(
            "Insufficient disk space for selective extraction: "
            f"need {extraction_plan.missing_bytes / GIB:.1f} GiB plus "
            f"{reserve_gib:.1f} GiB reserve, have {free_bytes / GIB:.1f} GiB."
        )

    grouped = _required_members(records, include_eye_locations)
    completed_files = 0
    completed_bytes = 0
    total_files = extraction_plan.missing_files
    total_bytes = extraction_plan.missing_bytes

    for archive_name in sorted(grouped):
        archive_path = root / archive_name
        archive, index = _index_archive(archive_path)
        try:
            for member_name in grouped[archive_name]:
                member = index[member_name]
                destination = root / PurePosixPath(member_name)
                if (
                    destination.is_file()
                    and destination.stat().st_size == member.size
                ):
                    continue
                _copy_member(archive, member, root)
                completed_files += 1
                completed_bytes += member.size
                if progress is not None:
                    progress(
                        ExtractionProgress(
                            completed_files=completed_files,
                            total_files=total_files,
                            completed_bytes=completed_bytes,
                            total_bytes=total_bytes,
                            current_member=member_name,
                        )
                    )
        finally:
            archive.close()

    return plan_extraction(
        records, root, include_eye_locations=include_eye_locations
    )

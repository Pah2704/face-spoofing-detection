"""Strict parser and invariants for OULU-NPU Protocol 1."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable


SPLIT_ORDER = ("train", "dev", "test")
SPLIT_DIRS = {
    "train": "Train_files",
    "dev": "Dev_files",
    "test": "Test_files",
}
SPLIT_PROTOCOL_FILES = {
    "train": "Train.txt",
    "dev": "Dev.txt",
    "test": "Test.txt",
}
SPLIT_ARCHIVES = {
    "train": "Train_files.tar",
    "dev": "Dev_files.tar",
    "test": "Test_files.tar",
}

PROTOCOL_1_EXPECTED = {
    "train": {
        "total": 1200,
        "live": 240,
        "spoof": 960,
        "sessions": {1, 2},
        "subjects": set(range(1, 21)),
    },
    "dev": {
        "total": 900,
        "live": 180,
        "spoof": 720,
        "sessions": {1, 2},
        "subjects": set(range(21, 36)),
    },
    "test": {
        "total": 600,
        "live": 120,
        "spoof": 480,
        "sessions": {3},
        "subjects": set(range(36, 56)),
    },
}

ACCESS_INFO = {
    1: ("live", "none"),
    2: ("print", "printer_1"),
    3: ("print", "printer_2"),
    4: ("replay", "display_1"),
    5: ("replay", "display_2"),
}

VIDEO_ID_RE = re.compile(
    r"^(?P<phone>[1-6])_(?P<session>[1-3])_"
    r"(?P<subject>\d{2})_(?P<access>[1-5])$"
)
PROTOCOL_LINE_RE = re.compile(r"^(?P<label>[+-]\d+),(?P<video_id>[^,\s]+)$")


class OuluDataError(ValueError):
    """Raised when OULU-NPU metadata violates the expected contract."""


@dataclass(frozen=True, slots=True)
class VideoRecord:
    """One video selected by the official Protocol 1 lists."""

    video_id: str
    split: str
    protocol_label: int
    label: int
    label_name: str
    attack_type: str
    attack_instrument: str
    phone_id: int
    session_id: int
    subject_id: int
    access_id: int

    @property
    def split_dir(self) -> str:
        return SPLIT_DIRS[self.split]

    @property
    def archive_name(self) -> str:
        return SPLIT_ARCHIVES[self.split]

    @property
    def video_member(self) -> str:
        return f"{self.split_dir}/{self.video_id}.avi"

    @property
    def eye_member(self) -> str:
        return f"{self.split_dir}/{self.video_id}.txt"

    def video_path(self, raw_root: Path) -> Path:
        return raw_root / self.video_member

    def eye_path(self, raw_root: Path) -> Path:
        return raw_root / self.eye_member


@dataclass(frozen=True, slots=True)
class ProtocolValidation:
    """Validation result for a set of protocol records."""

    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    counts: dict[str, dict[str, int]]

    @property
    def ok(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict[str, object]:
        return {
            "ok": self.ok,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "counts": self.counts,
        }


def protocol_directory(raw_root: Path, protocol: int = 1) -> Path:
    if protocol != 1:
        raise OuluDataError(
            f"Only Protocol 1 is implemented in the critical path; got {protocol}."
        )
    return raw_root / "Protocols" / "Protocol_1"


def parse_video_id(video_id: str) -> tuple[int, int, int, int]:
    """Parse Phone_Session_Subject_Access while preserving strict formatting."""

    match = VIDEO_ID_RE.fullmatch(video_id)
    if match is None:
        raise OuluDataError(
            f"Malformed video id {video_id!r}; expected Phone_Session_User_Access."
        )

    phone = int(match.group("phone"))
    session = int(match.group("session"))
    subject = int(match.group("subject"))
    access = int(match.group("access"))
    if not 1 <= subject <= 55:
        raise OuluDataError(
            f"Subject id out of OULU-NPU range in {video_id!r}: {subject}."
        )
    return phone, session, subject, access


def _expected_protocol_label(split: str, access: int) -> int:
    if access == 1:
        return 1
    if split == "test" and access in {4, 5}:
        return -2
    return -1


def parse_protocol_line(line: str, *, split: str, line_number: int) -> VideoRecord:
    """Convert one official protocol row to the internal spoof-positive labels."""

    normalized = line.strip()
    match = PROTOCOL_LINE_RE.fullmatch(normalized)
    if match is None:
        raise OuluDataError(
            f"Malformed {split} protocol row at line {line_number}: {line!r}."
        )

    protocol_label = int(match.group("label"))
    video_id = match.group("video_id")
    phone, session, subject, access = parse_video_id(video_id)
    expected_label = _expected_protocol_label(split, access)
    if protocol_label != expected_label:
        raise OuluDataError(
            f"Protocol label mismatch for {video_id}: got {protocol_label:+d}, "
            f"expected {expected_label:+d} from access type {access}."
        )

    attack_type, attack_instrument = ACCESS_INFO[access]
    is_spoof = int(access != 1)
    return VideoRecord(
        video_id=video_id,
        split=split,
        protocol_label=protocol_label,
        label=is_spoof,
        label_name="spoof" if is_spoof else "live",
        attack_type=attack_type,
        attack_instrument=attack_instrument,
        phone_id=phone,
        session_id=session,
        subject_id=subject,
        access_id=access,
    )


def load_protocol_1(raw_root: Path | str) -> list[VideoRecord]:
    """Load the three official Protocol 1 lists in deterministic order."""

    root = Path(raw_root)
    protocol_dir = protocol_directory(root, protocol=1)
    if not protocol_dir.is_dir():
        raise OuluDataError(
            f"Protocol directory not found: {protocol_dir}. "
            f"Extract {root / 'Protocols.tar'} before continuing."
        )

    records: list[VideoRecord] = []
    for split in SPLIT_ORDER:
        path = protocol_dir / SPLIT_PROTOCOL_FILES[split]
        if not path.is_file():
            raise OuluDataError(f"Missing official protocol file: {path}.")
        with path.open("r", encoding="utf-8-sig", newline=None) as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    raise OuluDataError(
                        f"Blank row in {path} at line {line_number}."
                    )
                records.append(
                    parse_protocol_line(
                        line, split=split, line_number=line_number
                    )
                )
    return records


def _expected_video_ids(split: str) -> set[str]:
    expected = PROTOCOL_1_EXPECTED[split]
    return {
        f"{phone}_{session}_{subject:02d}_{access}"
        for phone in range(1, 7)
        for session in sorted(expected["sessions"])
        for subject in sorted(expected["subjects"])
        for access in range(1, 6)
    }


def validate_protocol_1(records: Iterable[VideoRecord]) -> ProtocolValidation:
    """Validate counts, Cartesian coverage, labels and split leakage."""

    materialized = list(records)
    errors: list[str] = []
    warnings: list[str] = []
    counts: dict[str, dict[str, int]] = {}

    ids = [record.video_id for record in materialized]
    duplicate_ids = sorted(
        video_id for video_id, count in Counter(ids).items() if count > 1
    )
    if duplicate_ids:
        errors.append(
            "Duplicate video_id across protocol rows: "
            + ", ".join(duplicate_ids[:10])
        )

    records_by_split: dict[str, list[VideoRecord]] = defaultdict(list)
    for record in materialized:
        records_by_split[record.split].append(record)

    for split in SPLIT_ORDER:
        split_records = records_by_split.get(split, [])
        label_counts = Counter(record.label_name for record in split_records)
        counts[split] = {
            "total": len(split_records),
            "live": label_counts["live"],
            "spoof": label_counts["spoof"],
        }
        expected = PROTOCOL_1_EXPECTED[split]
        for key in ("total", "live", "spoof"):
            actual_value = counts[split][key]
            expected_value = int(expected[key])
            if actual_value != expected_value:
                errors.append(
                    f"{split} {key} count is {actual_value}, "
                    f"expected {expected_value}."
                )

        actual_ids = {record.video_id for record in split_records}
        expected_ids = _expected_video_ids(split)
        missing = sorted(expected_ids - actual_ids)
        unexpected = sorted(actual_ids - expected_ids)
        if missing:
            errors.append(
                f"{split} is missing {len(missing)} expected ids; "
                f"examples: {', '.join(missing[:5])}."
            )
        if unexpected:
            errors.append(
                f"{split} contains {len(unexpected)} unexpected ids; "
                f"examples: {', '.join(unexpected[:5])}."
            )

    subject_sets = {
        split: {record.subject_id for record in records_by_split.get(split, [])}
        for split in SPLIT_ORDER
    }
    for index, left in enumerate(SPLIT_ORDER):
        for right in SPLIT_ORDER[index + 1 :]:
            overlap = sorted(subject_sets[left] & subject_sets[right])
            if overlap:
                errors.append(
                    f"Subject leakage between {left} and {right}: {overlap}."
                )

    if len(materialized) != sum(
        int(PROTOCOL_1_EXPECTED[split]["total"]) for split in SPLIT_ORDER
    ):
        errors.append(
            f"Protocol 1 total is {len(materialized)}, expected 2700."
        )

    return ProtocolValidation(
        errors=tuple(errors),
        warnings=tuple(warnings),
        counts=counts,
    )


"""Atomic, auditable experiment artifact helpers."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import sys
import tarfile
import tempfile
from typing import Iterable, Mapping


def sha256_file(path: Path | str) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while chunk := handle.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_bytes(payload: object) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def config_hash(payload: object) -> str:
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def _json_default(value: object):
    if isinstance(value, Path):
        return value.as_posix()
    if hasattr(value, "item") and callable(value.item):
        return value.item()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable.")


def atomic_write_json(path: Path | str, payload: object) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="",
        prefix=destination.name + ".",
        suffix=".tmp",
        dir=destination.parent,
        delete=False,
    )
    temporary = Path(handle.name)
    try:
        with handle:
            json.dump(
                payload,
                handle,
                indent=2,
                ensure_ascii=False,
                default=_json_default,
            )
            handle.write("\n")
        os.replace(temporary, destination)
        destination.chmod(0o644)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def atomic_write_csv(
    path: Path | str,
    fieldnames: Iterable[str],
    rows: Iterable[Mapping[str, object]],
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="",
        prefix=destination.name + ".",
        suffix=".tmp",
        dir=destination.parent,
        delete=False,
    )
    temporary = Path(handle.name)
    names = list(fieldnames)
    try:
        with handle:
            writer = csv.DictWriter(handle, fieldnames=names)
            writer.writeheader()
            for row in rows:
                writer.writerow(
                    {name: _csv_value(row.get(name, "")) for name in names}
                )
        os.replace(temporary, destination)
        destination.chmod(0o644)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def _csv_value(value: object) -> object:
    if isinstance(value, float):
        return format(value, ".17g")
    if hasattr(value, "item") and callable(value.item):
        converted = value.item()
        return format(converted, ".17g") if isinstance(converted, float) else converted
    return value


def atomic_joblib_dump(path: Path | str, model: object) -> None:
    import joblib

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".tmp")
    temporary.unlink(missing_ok=True)
    try:
        joblib.dump(model, temporary)
        os.replace(temporary, destination)
        destination.chmod(0o644)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def atomic_torch_save(path: Path | str, payload: object) -> None:
    """Serialize a PyTorch checkpoint and publish it atomically."""

    import torch

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".tmp")
    temporary.unlink(missing_ok=True)
    try:
        torch.save(payload, temporary)
        os.replace(temporary, destination)
        destination.chmod(0o644)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def create_run_directory(
    run_root: Path | str,
    *,
    experiment_id: str,
    model_name: str,
    seed: int,
    resolved_config_hash: str,
    run_id: str | None = None,
) -> Path:
    root = Path(run_root)
    root.mkdir(parents=True, exist_ok=True)
    if run_id is None:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        run_id = (
            f"{experiment_id.lower()}_{timestamp}_{model_name}_"
            f"seed{seed}_{resolved_config_hash[:8]}"
        )
    destination = root / run_id
    destination.mkdir(parents=False, exist_ok=False)
    for child in ("model", "selection", "predictions", "metrics", "figures"):
        (destination / child).mkdir()
    return destination


def _source_tree_paths(project_root: Path | str) -> list[Path]:
    root = Path(project_root).resolve()
    return sorted(
        [
            *root.glob("src/**/*.py"),
            *root.glob("configs/**/*.yaml"),
            root / "pyproject.toml",
        ],
        key=lambda path: path.relative_to(root).as_posix(),
    )


def source_tree_sha256(project_root: Path | str) -> str:
    root = Path(project_root).resolve()
    digest = hashlib.sha256()
    for path in _source_tree_paths(root):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(4, "big"))
        digest.update(relative)
        digest.update(bytes.fromhex(sha256_file(path)))
    return digest.hexdigest()


def write_source_tree_snapshot(
    run_dir: Path | str,
    project_root: Path | str,
    *,
    expected_sha256: str | None = None,
) -> dict[str, object]:
    """Store the exact hashed source/config tree inside an experiment run.

    The workspace is intentionally usable without Git.  A run therefore keeps
    a deterministic uncompressed tar archive of the files covered by
    :func:`source_tree_sha256`, so later repository work cannot orphan the
    provenance hash recorded at run start.
    """

    root = Path(project_root).resolve()
    before = source_tree_sha256(root)
    if expected_sha256 is not None and before != expected_sha256:
        raise RuntimeError(
            "source tree changed before snapshot creation: "
            f"expected {expected_sha256}, found {before}"
        )

    destination = Path(run_dir) / "source" / "source_tree.tar"
    destination.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        prefix=destination.name + ".",
        suffix=".tmp",
        dir=destination.parent,
        delete=False,
    )
    temporary = Path(handle.name)
    handle.close()
    archived_files = 0
    try:
        with tarfile.open(temporary, mode="w") as archive:
            for path in _source_tree_paths(root):
                if not path.is_file():
                    continue
                relative = path.relative_to(root).as_posix()
                info = archive.gettarinfo(str(path), arcname=relative)
                info.uid = 0
                info.gid = 0
                info.uname = ""
                info.gname = ""
                info.mtime = 0
                with path.open("rb") as source:
                    archive.addfile(info, source)
                archived_files += 1

        after = source_tree_sha256(root)
        if after != before:
            raise RuntimeError(
                "source tree changed while its run snapshot was being created"
            )
        os.replace(temporary, destination)
        destination.chmod(0o644)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise

    return {
        "path": destination.relative_to(Path(run_dir)).as_posix(),
        "files": archived_files,
        "bytes": destination.stat().st_size,
        "sha256": sha256_file(destination),
        "source_tree_sha256": before,
    }


def environment_metadata(project_root: Path | str) -> dict[str, object]:
    packages = (
        "numpy",
        "scikit-learn",
        "joblib",
        "opencv-contrib-python",
        "opencv-python",
        "torch",
        "torchvision",
        "Pillow",
        "matplotlib",
    )
    versions: dict[str, str | None] = {}
    for package in packages:
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = None
    thread_variables = {
        name: os.environ.get(name)
        for name in (
            "OMP_NUM_THREADS",
            "MKL_NUM_THREADS",
            "OPENBLAS_NUM_THREADS",
            "NUMEXPR_NUM_THREADS",
            "CUBLAS_WORKSPACE_CONFIG",
        )
    }
    accelerator: dict[str, object] = {
        "cuda_available": False,
        "cuda_version": None,
        "cudnn_version": None,
        "devices": [],
    }
    try:
        import torch

        accelerator = {
            "cuda_available": bool(torch.cuda.is_available()),
            "cuda_version": torch.version.cuda,
            "cudnn_version": torch.backends.cudnn.version(),
            "devices": [
                {
                    "index": index,
                    "name": torch.cuda.get_device_name(index),
                    "total_memory_bytes": torch.cuda.get_device_properties(
                        index
                    ).total_memory,
                }
                for index in range(torch.cuda.device_count())
            ],
            "determinism": {
                "algorithms_enabled": torch.are_deterministic_algorithms_enabled(),
                "cudnn_benchmark": torch.backends.cudnn.benchmark,
                "cudnn_deterministic": torch.backends.cudnn.deterministic,
                "cuda_matmul_allow_tf32": torch.backends.cuda.matmul.allow_tf32,
                "cudnn_allow_tf32": torch.backends.cudnn.allow_tf32,
            },
        }
    except (ImportError, RuntimeError):
        pass

    return {
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "packages": versions,
        "accelerator": accelerator,
        "thread_environment": thread_variables,
        "git_commit": None,
        "git_dirty": None,
        "source_tree_sha256": source_tree_sha256(project_root),
    }


def finalize_run_manifest(
    run_dir: Path | str,
    *,
    status: str = "complete",
) -> dict[str, object]:
    root = Path(run_dir)
    inventory = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name == "run_manifest.json":
            continue
        inventory.append(
            {
                "relative_path": path.relative_to(root).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    payload = {
        "status": status,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "files": inventory,
    }
    atomic_write_json(root / "run_manifest.json", payload)
    return payload


__all__ = [
    "atomic_joblib_dump",
    "atomic_torch_save",
    "atomic_write_csv",
    "atomic_write_json",
    "canonical_json_bytes",
    "config_hash",
    "create_run_directory",
    "environment_metadata",
    "finalize_run_manifest",
    "sha256_file",
    "source_tree_sha256",
    "write_source_tree_snapshot",
]

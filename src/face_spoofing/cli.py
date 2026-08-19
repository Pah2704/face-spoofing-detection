"""Command-line entry point for the reproducible project pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys

from .data.archives import (
    ArchiveError,
    ExtractionProgress,
    ensure_protocol_files,
    extract_protocol_1,
    plan_extraction,
)
from .data.manifest import write_json_atomic, write_video_manifest
from .data.oulu import OuluDataError, load_protocol_1, validate_protocol_1
from .data.preprocess import (
    PreprocessConfig,
    PreprocessProgress,
    create_qc_montage,
    run_preprocessing,
)
from .data.validate import validate_extracted_protocol_1


DEFAULT_RAW_ROOT = Path("data/raw/oulu_npu")
DEFAULT_MANIFEST = Path("data/manifests/videos_protocol1.csv")
DEFAULT_REPORT = Path("data/manifests/validation_protocol1.json")
DEFAULT_FACES_ROOT = Path("data/processed/faces")
DEFAULT_FRAME_MANIFEST = Path("data/manifests/frames_protocol1.csv")
DEFAULT_PREPROCESS_SUMMARY = Path(
    "data/manifests/preprocess_protocol1_summary.json"
)
DEFAULT_QC_MONTAGE = Path(
    "data/quality_control/protocol1_faces_montage.jpg"
)
DEFAULT_PROCESSED_REPORT = Path(
    "data/manifests/validation_processed_protocol1.json"
)
DEFAULT_LBP_CACHE_ROOT = Path("data/processed/features/lbp")
DEFAULT_LBP_RUN_ROOT = Path("artifacts/runs/lbp_svm")
DEFAULT_RGB_LBP_CACHE_ROOT = Path("data/processed/features/rgb_lbp")
DEFAULT_RGB_LBP_RUN_ROOT = Path("artifacts/runs/rgb_lbp_svm")
DEFAULT_MOBILENET_RUN_ROOT = Path("artifacts/runs/mobilenet_v2")
DEFAULT_RESNET_RUN_ROOT = Path("artifacts/runs/resnet18")
DEFAULT_RESNET_FINETUNE_RUN_ROOT = Path("artifacts/runs/resnet18_finetune")


def _print_json(payload: object) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _require_protocol_one(protocol: int) -> None:
    if protocol != 1:
        raise OuluDataError(
            "Only OULU-NPU Protocol 1 is implemented in the main scope."
        )


def _load_valid_records(raw_root: Path, protocol: int):
    _require_protocol_one(protocol)
    records = load_protocol_1(raw_root)
    validation = validate_protocol_1(records)
    if not validation.ok:
        raise OuluDataError(
            "Protocol validation failed:\n- " + "\n- ".join(validation.errors)
        )
    return records, validation


def _inspect_data(args: argparse.Namespace) -> int:
    raw_root = args.raw_root
    records, validation = _load_valid_records(raw_root, args.protocol)
    extraction = plan_extraction(records, raw_root)
    disk = shutil.disk_usage(raw_root)
    payload = {
        "ok": validation.ok,
        "raw_root": raw_root.as_posix(),
        "protocol": args.protocol,
        "protocol_validation": validation.to_dict(),
        "extraction": extraction.to_dict(),
        "disk": {
            "total_bytes": disk.total,
            "used_bytes": disk.used,
            "free_bytes": disk.free,
        },
    }
    _print_json(payload)
    return 0


def _extract_data(args: argparse.Namespace) -> int:
    raw_root = args.raw_root
    _require_protocol_one(args.protocol)
    ensure_protocol_files(raw_root, protocol=args.protocol)
    records, validation = _load_valid_records(raw_root, args.protocol)
    before = plan_extraction(records, raw_root)
    if args.dry_run:
        _print_json(
            {
                "ok": validation.ok,
                "dry_run": True,
                "protocol": args.protocol,
                "raw_root": raw_root.as_posix(),
                "extraction": before.to_dict(),
            }
        )
        return 0

    last_reported = {"files": -1}

    def show_progress(progress: ExtractionProgress) -> None:
        should_report = (
            progress.completed_files == progress.total_files
            or progress.completed_files % 100 == 0
        )
        if should_report and progress.completed_files != last_reported["files"]:
            last_reported["files"] = progress.completed_files
            byte_percent = (
                100.0 * progress.completed_bytes / progress.total_bytes
                if progress.total_bytes
                else 100.0
            )
            print(
                f"Extracted {progress.completed_files}/{progress.total_files} "
                f"files ({byte_percent:.1f}% bytes): "
                f"{progress.current_member}",
                flush=True,
            )

    after = extract_protocol_1(
        raw_root,
        reserve_gib=args.reserve_gib,
        progress=show_progress,
    )
    _print_json(
        {
            "ok": after.missing_files == 0,
            "dry_run": False,
            "protocol": args.protocol,
            "raw_root": raw_root.as_posix(),
            "before": before.to_dict(),
            "after": after.to_dict(),
        }
    )
    return 0 if after.missing_files == 0 else 1


def _build_manifest(args: argparse.Namespace) -> int:
    records, validation = _load_valid_records(args.raw_root, args.protocol)
    summary = write_video_manifest(
        records,
        args.raw_root,
        args.output,
        probe_report_path=args.validation_report,
    )
    _print_json(
        {
            "ok": validation.ok,
            "protocol_validation": validation.to_dict(),
            "manifest_summary": summary,
        }
    )
    return 0


def _validate_data(args: argparse.Namespace) -> int:
    records, _ = _load_valid_records(args.raw_root, args.protocol)
    report = validate_extracted_protocol_1(
        records,
        args.raw_root,
        probe_per_group=args.probe_per_group,
        full_probe=args.full_probe,
    )
    write_json_atomic(args.report, report)
    probes = report["probes"]
    displayed_probes = probes[:12]
    _print_json(
        {
            "ok": report["ok"],
            "report": args.report.as_posix(),
            "error_count": report["error_count"],
            "errors": report["errors"][:20],
            "stats": report["stats"],
            "probes_shown": displayed_probes,
            "probe_results_in_report": len(probes),
        }
    )
    return 0 if report["ok"] else 1


def _preprocess_data(args: argparse.Namespace) -> int:
    records, _ = _load_valid_records(args.raw_root, args.protocol)
    config = PreprocessConfig(
        frames_per_video=args.frames_per_video,
        output_size=args.output_size,
        margin=args.margin,
        model_selection=args.model_selection,
        min_detection_confidence=args.min_detection_confidence,
        detection_max_side=args.detection_max_side,
        png_compression=args.png_compression,
    )
    last_reported = {"videos": -1}

    def show_progress(progress: PreprocessProgress) -> None:
        should_report = (
            progress.completed_videos == progress.total_videos
            or progress.completed_videos % 25 == 0
        )
        if should_report and progress.completed_videos != last_reported["videos"]:
            last_reported["videos"] = progress.completed_videos
            rate = (
                100.0
                * progress.detected_faces
                / progress.requested_faces
                if progress.requested_faces
                else 0.0
            )
            print(
                f"Processed {progress.completed_videos}/"
                f"{progress.total_videos} videos; "
                f"face detection {rate:.2f}%; "
                f"latest={progress.current_video_id}",
                flush=True,
            )

    summary = run_preprocessing(
        records,
        raw_root=args.raw_root,
        output_root=args.output_root,
        frame_manifest=args.frame_manifest,
        summary_path=args.summary,
        config=config,
        workers=args.workers,
        force=args.force,
        limit_per_group=args.limit_per_group,
        progress=show_progress,
    )
    qc = None
    if args.qc_per_group > 0 and summary["faces_detected"] > 0:
        qc = create_qc_montage(
            args.frame_manifest,
            args.qc_output,
            per_group=args.qc_per_group,
            seed=42,
        )
    summary["qc"] = qc
    write_json_atomic(args.summary, summary)
    _print_json(
        {
            "ok": summary["ok"],
            "summary": args.summary.as_posix(),
            "frame_manifest": args.frame_manifest.as_posix(),
            "stats": {
                key: summary[key]
                for key in (
                    "videos",
                    "cache_hits",
                    "frames_requested",
                    "manifest_rows",
                    "faces_detected",
                    "faces_failed",
                    "detection_rate",
                    "status_counts",
                    "by_split_label",
                )
            },
            "warnings": summary["warnings"][:20],
            "video_errors": summary["video_errors"][:20],
            "qc": qc,
        }
    )
    return 0 if summary["ok"] else 1


def _validate_processed_data(args: argparse.Namespace) -> int:
    from .data.processed_validation import validate_processed_faces

    records, _ = _load_valid_records(args.raw_root, args.protocol)
    report = validate_processed_faces(
        records,
        frame_manifest=args.frame_manifest,
        output_root=args.output_root,
        frames_per_video=args.frames_per_video,
        output_size=args.output_size,
        check_images=not args.skip_image_check,
    )
    write_json_atomic(args.report, report)
    _print_json(
        {
            "ok": report["ok"],
            "report": args.report.as_posix(),
            "error_count": report["error_count"],
            "errors": report["errors"][:20],
            "stats": report["stats"],
        }
    )
    return 0 if report["ok"] else 1


def _train_lbp_variant(args: argparse.Namespace, *, color_mode: str) -> int:
    from .features.cache import LbpCacheConfig, build_lbp_cache
    from .models.lbp_svm import LBPSVMConfig
    from .training.lbp_experiment import (
        run_lbp_svm_experiment,
        run_rgb_lbp_svm_experiment,
    )

    feature_config = LbpCacheConfig(
        color_mode=color_mode,
        image_size=128,
        radius=1,
        points=8,
        grid_rows=8,
        grid_cols=8,
    )
    display_name = "RGB-LBP" if color_mode == "rgb" else "LBP"
    print(
        f"Preparing content-addressed {display_name} cache "
        f"({feature_config.feature_dim} dimensions)...",
        flush=True,
    )
    dataset = build_lbp_cache(
        args.frame_manifest,
        args.feature_cache_root,
        config=feature_config,
        workers=args.feature_workers,
        project_root=args.project_root,
        force=args.force_feature_cache,
    )
    print(
        f"{display_name} cache ready: {dataset.cache_dir} "
        f"({len(dataset.features)} valid frames, "
        f"{len(dataset.excluded_rows)} excluded).",
        flush=True,
    )
    model_config = LBPSVMConfig(
        c_values=tuple(args.c_values),
        seed=args.seed,
    )
    experiment_runner = (
        run_rgb_lbp_svm_experiment
        if color_mode == "rgb"
        else run_lbp_svm_experiment
    )
    result = experiment_runner(
        dataset,
        frame_manifest=args.frame_manifest,
        run_root=args.run_root,
        project_root=args.project_root,
        model_config=model_config,
        run_id=args.run_id,
    )
    _print_json(result)
    return 0


def _train_lbp_svm(args: argparse.Namespace) -> int:
    return _train_lbp_variant(args, color_mode="grayscale")


def _train_rgb_lbp_svm(args: argparse.Namespace) -> int:
    return _train_lbp_variant(args, color_mode="rgb")


def _train_mobilenet_v2(args: argparse.Namespace) -> int:
    from .models.mobilenet_v2 import MobileNetV2Config
    from .training.mobilenet_experiment import (
        MobileNetTrainingConfig,
        run_mobilenet_v2_experiment,
    )

    max_epochs = 1 if args.smoke else args.max_epochs
    minimum_epochs = 1 if args.smoke else args.minimum_epochs
    patience = 1 if args.smoke else args.patience
    training_config = MobileNetTrainingConfig(
        batch_size=args.batch_size,
        num_workers=args.workers,
        max_epochs=max_epochs,
        minimum_epochs=minimum_epochs,
        early_stopping_patience=patience,
        learning_rate=args.learning_rate,
        weight_decay=args.weight_decay,
        seed=args.seed,
        device=args.device,
        smoke=args.smoke,
        smoke_videos_per_label=args.smoke_videos_per_label,
    )
    print(
        "Running E02 MobileNetV2 "
        f"({'smoke' if args.smoke else 'main'}) on {args.device}; "
        f"batch={args.batch_size}, epochs={max_epochs}...",
        flush=True,
    )
    result = run_mobilenet_v2_experiment(
        frame_manifest=args.frame_manifest,
        run_root=args.run_root,
        project_root=args.project_root,
        model_config=MobileNetV2Config(),
        training_config=training_config,
        run_id=args.run_id,
    )
    _print_json(result)
    return 0


def _train_resnet18(args: argparse.Namespace) -> int:
    from .models.resnet18 import ResNet18Config
    from .training.mobilenet_experiment import CnnTrainingConfig
    from .training.resnet_experiment import run_resnet18_experiment

    max_epochs = 1 if args.smoke else args.max_epochs
    minimum_epochs = 1 if args.smoke else args.minimum_epochs
    patience = 1 if args.smoke else args.patience
    training_config = CnnTrainingConfig(
        batch_size=args.batch_size,
        num_workers=args.workers,
        max_epochs=max_epochs,
        minimum_epochs=minimum_epochs,
        early_stopping_patience=patience,
        learning_rate=args.learning_rate,
        weight_decay=args.weight_decay,
        seed=args.seed,
        device=args.device,
        smoke=args.smoke,
        smoke_videos_per_label=args.smoke_videos_per_label,
    )
    print(
        "Running E03 ResNet18 "
        f"({'smoke' if args.smoke else 'main'}) on {args.device}; "
        f"batch={args.batch_size}, epochs={max_epochs}...",
        flush=True,
    )
    result = run_resnet18_experiment(
        frame_manifest=args.frame_manifest,
        run_root=args.run_root,
        project_root=args.project_root,
        model_config=ResNet18Config(),
        training_config=training_config,
        run_id=args.run_id,
    )
    _print_json(result)
    return 0


def _train_resnet18_finetune(args: argparse.Namespace) -> int:
    from .models.resnet18 import ResNet18Config
    from .training.mobilenet_experiment import CnnTrainingConfig
    from .training.resnet_experiment import run_resnet18_finetune_experiment

    max_epochs = 1 if args.smoke else args.max_epochs
    minimum_epochs = 1 if args.smoke else args.minimum_epochs
    patience = 1 if args.smoke else args.patience
    training_config = CnnTrainingConfig(
        batch_size=args.batch_size,
        num_workers=args.workers,
        max_epochs=max_epochs,
        minimum_epochs=minimum_epochs,
        early_stopping_patience=patience,
        learning_rate=args.learning_rate,
        backbone_learning_rate=args.backbone_learning_rate,
        weight_decay=args.weight_decay,
        seed=args.seed,
        device=args.device,
        smoke=args.smoke,
        smoke_videos_per_label=args.smoke_videos_per_label,
    )
    print(
        "Running E04 ResNet18 fine-tune layer4 "
        f"({'smoke' if args.smoke else 'main'}) on {args.device}; "
        f"batch={args.batch_size}, epochs={max_epochs}, "
        f"layer4_lr={args.backbone_learning_rate}, "
        f"head_lr={args.learning_rate}...",
        flush=True,
    )
    result = run_resnet18_finetune_experiment(
        frame_manifest=args.frame_manifest,
        run_root=args.run_root,
        project_root=args.project_root,
        model_config=ResNet18Config(experiment_id="E04"),
        training_config=training_config,
        run_id=args.run_id,
    )
    _print_json(result)
    return 0


def _path(value: str) -> Path:
    return Path(value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="face-spoofing",
        description="Face anti-spoofing baselines for OULU-NPU.",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    data_parser = commands.add_parser(
        "data", help="Inspect, extract and validate OULU-NPU data."
    )
    data_commands = data_parser.add_subparsers(
        dest="data_command", required=True
    )

    def add_dataset_arguments(command: argparse.ArgumentParser) -> None:
        command.add_argument(
            "--raw-root",
            type=_path,
            default=DEFAULT_RAW_ROOT,
            help=f"OULU-NPU raw root (default: {DEFAULT_RAW_ROOT}).",
        )
        command.add_argument(
            "--protocol",
            type=int,
            choices=[1],
            default=1,
            help="Official protocol number; main scope supports only 1.",
        )

    inspect_parser = data_commands.add_parser(
        "inspect",
        help="Validate official lists and calculate selective extraction size.",
    )
    add_dataset_arguments(inspect_parser)
    inspect_parser.set_defaults(handler=_inspect_data)

    extract_parser = data_commands.add_parser(
        "extract",
        help="Extract only Protocol 1 videos and eye metadata from the tar files.",
    )
    add_dataset_arguments(extract_parser)
    extract_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Calculate selected files and disk requirements without extracting.",
    )
    extract_parser.add_argument(
        "--reserve-gib",
        type=float,
        default=5.0,
        help="Minimum free disk space to retain after extraction (default: 5).",
    )
    extract_parser.set_defaults(handler=_extract_data)

    manifest_parser = data_commands.add_parser(
        "build-manifest",
        help="Write the canonical Protocol 1 video manifest.",
    )
    add_dataset_arguments(manifest_parser)
    manifest_parser.add_argument(
        "--output",
        type=_path,
        default=DEFAULT_MANIFEST,
        help=f"Manifest CSV output (default: {DEFAULT_MANIFEST}).",
    )
    manifest_parser.add_argument(
        "--validation-report",
        type=_path,
        default=DEFAULT_REPORT,
        help=(
            "Optional full-probe report used to enrich video metadata "
            f"(default: {DEFAULT_REPORT})."
        ),
    )
    manifest_parser.set_defaults(handler=_build_manifest)

    validate_parser = data_commands.add_parser(
        "validate",
        help="Validate extracted AVI and eye-metadata files.",
    )
    add_dataset_arguments(validate_parser)
    validate_parser.add_argument(
        "--report",
        type=_path,
        default=DEFAULT_REPORT,
        help=f"JSON report output (default: {DEFAULT_REPORT}).",
    )
    validate_parser.add_argument(
        "--probe-per-group",
        type=int,
        default=1,
        help="ffprobe samples per split/label group (default: 1).",
    )
    validate_parser.add_argument(
        "--full-probe",
        action="store_true",
        help="ffprobe every selected video instead of representative samples.",
    )
    validate_parser.set_defaults(handler=_validate_data)

    preprocess_parser = data_commands.add_parser(
        "preprocess",
        help="Sample 10 frames/video and cache shared MediaPipe face crops.",
    )
    add_dataset_arguments(preprocess_parser)
    preprocess_parser.add_argument(
        "--output-root",
        type=_path,
        default=DEFAULT_FACES_ROOT,
        help=f"Face crop root (default: {DEFAULT_FACES_ROOT}).",
    )
    preprocess_parser.add_argument(
        "--frame-manifest",
        type=_path,
        default=DEFAULT_FRAME_MANIFEST,
        help=f"Frame manifest output (default: {DEFAULT_FRAME_MANIFEST}).",
    )
    preprocess_parser.add_argument(
        "--summary",
        type=_path,
        default=DEFAULT_PREPROCESS_SUMMARY,
        help=f"Preprocessing summary JSON (default: {DEFAULT_PREPROCESS_SUMMARY}).",
    )
    preprocess_parser.add_argument(
        "--qc-output",
        type=_path,
        default=DEFAULT_QC_MONTAGE,
        help=f"QC montage output (default: {DEFAULT_QC_MONTAGE}).",
    )
    preprocess_parser.add_argument("--workers", type=int, default=4)
    preprocess_parser.add_argument("--frames-per-video", type=int, default=10)
    preprocess_parser.add_argument("--output-size", type=int, default=256)
    preprocess_parser.add_argument("--margin", type=float, default=0.2)
    preprocess_parser.add_argument("--model-selection", type=int, default=0)
    preprocess_parser.add_argument(
        "--min-detection-confidence", type=float, default=0.5
    )
    preprocess_parser.add_argument(
        "--detection-max-side", type=int, default=640
    )
    preprocess_parser.add_argument("--png-compression", type=int, default=3)
    preprocess_parser.add_argument(
        "--limit-per-group",
        type=int,
        default=0,
        help="Smoke test: process N videos per split/label; 0 means all.",
    )
    preprocess_parser.add_argument(
        "--qc-per-group",
        type=int,
        default=20,
        help="QC samples per split/label group; 0 disables montage.",
    )
    preprocess_parser.add_argument(
        "--force",
        action="store_true",
        help="Ignore matching per-video cache metadata and reprocess.",
    )
    preprocess_parser.set_defaults(handler=_preprocess_data)

    processed_parser = data_commands.add_parser(
        "validate-processed",
        help="Validate the frame manifest and every generated face crop.",
    )
    add_dataset_arguments(processed_parser)
    processed_parser.add_argument(
        "--frame-manifest",
        type=_path,
        default=DEFAULT_FRAME_MANIFEST,
    )
    processed_parser.add_argument(
        "--output-root",
        type=_path,
        default=DEFAULT_FACES_ROOT,
    )
    processed_parser.add_argument(
        "--report",
        type=_path,
        default=DEFAULT_PROCESSED_REPORT,
    )
    processed_parser.add_argument("--frames-per-video", type=int, default=10)
    processed_parser.add_argument("--output-size", type=int, default=256)
    processed_parser.add_argument(
        "--skip-image-check",
        action="store_true",
        help="Skip decoding PNG files; intended only for fast diagnostics.",
    )
    processed_parser.set_defaults(handler=_validate_processed_data)

    train_parser = commands.add_parser(
        "train", help="Train and evaluate project baselines."
    )
    train_commands = train_parser.add_subparsers(
        dest="train_command", required=True
    )
    lbp_parser = train_commands.add_parser(
        "lbp-svm",
        help="Run E01 LBP-SVM with dev-only model and threshold selection.",
    )
    lbp_parser.add_argument(
        "--frame-manifest",
        type=_path,
        default=DEFAULT_FRAME_MANIFEST,
    )
    lbp_parser.add_argument(
        "--feature-cache-root",
        type=_path,
        default=DEFAULT_LBP_CACHE_ROOT,
    )
    lbp_parser.add_argument(
        "--run-root",
        type=_path,
        default=DEFAULT_LBP_RUN_ROOT,
    )
    lbp_parser.add_argument(
        "--project-root",
        type=_path,
        default=Path("."),
    )
    lbp_parser.add_argument("--run-id", default=None)
    lbp_parser.add_argument("--feature-workers", type=int, default=6)
    lbp_parser.add_argument("--seed", type=int, default=42)
    lbp_parser.add_argument(
        "--c-values",
        type=float,
        nargs="+",
        default=[1e-4, 1e-3, 1e-2, 1e-1, 1.0, 10.0],
    )
    lbp_parser.add_argument(
        "--force-feature-cache",
        action="store_true",
        help="Rebuild this derived feature cache after validation failure.",
    )
    lbp_parser.set_defaults(handler=_train_lbp_svm)

    rgb_lbp_parser = train_commands.add_parser(
        "rgb-lbp-svm",
        help="Run E05 RGB-LBP-SVM as a colour ablation of E01.",
    )
    rgb_lbp_parser.add_argument(
        "--frame-manifest",
        type=_path,
        default=DEFAULT_FRAME_MANIFEST,
    )
    rgb_lbp_parser.add_argument(
        "--feature-cache-root",
        type=_path,
        default=DEFAULT_RGB_LBP_CACHE_ROOT,
    )
    rgb_lbp_parser.add_argument(
        "--run-root",
        type=_path,
        default=DEFAULT_RGB_LBP_RUN_ROOT,
    )
    rgb_lbp_parser.add_argument(
        "--project-root",
        type=_path,
        default=Path("."),
    )
    rgb_lbp_parser.add_argument("--run-id", default=None)
    rgb_lbp_parser.add_argument("--feature-workers", type=int, default=6)
    rgb_lbp_parser.add_argument("--seed", type=int, default=42)
    rgb_lbp_parser.add_argument(
        "--c-values",
        type=float,
        nargs="+",
        default=[1e-4, 1e-3, 1e-2, 1e-1, 1.0, 10.0],
    )
    rgb_lbp_parser.add_argument(
        "--force-feature-cache",
        action="store_true",
        help="Rebuild this derived feature cache after validation failure.",
    )
    rgb_lbp_parser.set_defaults(handler=_train_rgb_lbp_svm)

    mobilenet_parser = train_commands.add_parser(
        "mobilenet-v2",
        help=(
            "Run E02 MobileNetV2 with dev-only checkpoint and threshold "
            "selection."
        ),
    )
    mobilenet_parser.add_argument(
        "--frame-manifest", type=_path, default=DEFAULT_FRAME_MANIFEST
    )
    mobilenet_parser.add_argument(
        "--run-root", type=_path, default=DEFAULT_MOBILENET_RUN_ROOT
    )
    mobilenet_parser.add_argument(
        "--project-root", type=_path, default=Path(".")
    )
    mobilenet_parser.add_argument("--run-id", default=None)
    mobilenet_parser.add_argument(
        "--device", choices=["auto", "cpu", "cuda"], default="auto"
    )
    mobilenet_parser.add_argument("--batch-size", type=int, default=16)
    mobilenet_parser.add_argument("--workers", type=int, default=4)
    mobilenet_parser.add_argument("--max-epochs", type=int, default=15)
    mobilenet_parser.add_argument("--minimum-epochs", type=int, default=3)
    mobilenet_parser.add_argument("--patience", type=int, default=3)
    mobilenet_parser.add_argument("--learning-rate", type=float, default=1e-4)
    mobilenet_parser.add_argument("--weight-decay", type=float, default=1e-4)
    mobilenet_parser.add_argument("--seed", type=int, default=42)
    mobilenet_parser.add_argument(
        "--smoke",
        action="store_true",
        help=(
            "Run one epoch on a small balanced train/dev subset and skip test."
        ),
    )
    mobilenet_parser.add_argument(
        "--smoke-videos-per-label",
        type=int,
        default=2,
        help="Whole videos per label and split used by --smoke (default: 2).",
    )
    mobilenet_parser.set_defaults(handler=_train_mobilenet_v2)

    resnet_parser = train_commands.add_parser(
        "resnet18",
        help="Run E03 ResNet18 with dev-only checkpoint/threshold selection.",
    )
    resnet_parser.add_argument(
        "--frame-manifest", type=_path, default=DEFAULT_FRAME_MANIFEST
    )
    resnet_parser.add_argument(
        "--run-root", type=_path, default=DEFAULT_RESNET_RUN_ROOT
    )
    resnet_parser.add_argument("--project-root", type=_path, default=Path("."))
    resnet_parser.add_argument("--run-id", default=None)
    resnet_parser.add_argument(
        "--device", choices=["auto", "cpu", "cuda"], default="auto"
    )
    resnet_parser.add_argument("--batch-size", type=int, default=16)
    resnet_parser.add_argument("--workers", type=int, default=4)
    resnet_parser.add_argument("--max-epochs", type=int, default=15)
    resnet_parser.add_argument("--minimum-epochs", type=int, default=3)
    resnet_parser.add_argument("--patience", type=int, default=3)
    resnet_parser.add_argument("--learning-rate", type=float, default=1e-4)
    resnet_parser.add_argument("--weight-decay", type=float, default=1e-4)
    resnet_parser.add_argument("--seed", type=int, default=42)
    resnet_parser.add_argument(
        "--smoke",
        action="store_true",
        help="Run one epoch on balanced train/dev videos and skip test.",
    )
    resnet_parser.add_argument(
        "--smoke-videos-per-label", type=int, default=2
    )
    resnet_parser.set_defaults(handler=_train_resnet18)

    resnet_finetune_parser = train_commands.add_parser(
        "resnet18-finetune",
        help="Run E04 ResNet18 with only layer4 and the head trainable.",
    )
    resnet_finetune_parser.add_argument(
        "--frame-manifest", type=_path, default=DEFAULT_FRAME_MANIFEST
    )
    resnet_finetune_parser.add_argument(
        "--run-root", type=_path, default=DEFAULT_RESNET_FINETUNE_RUN_ROOT
    )
    resnet_finetune_parser.add_argument(
        "--project-root", type=_path, default=Path(".")
    )
    resnet_finetune_parser.add_argument("--run-id", default=None)
    resnet_finetune_parser.add_argument(
        "--device", choices=["auto", "cpu", "cuda"], default="auto"
    )
    resnet_finetune_parser.add_argument("--batch-size", type=int, default=16)
    resnet_finetune_parser.add_argument("--workers", type=int, default=4)
    resnet_finetune_parser.add_argument("--max-epochs", type=int, default=15)
    resnet_finetune_parser.add_argument(
        "--minimum-epochs", type=int, default=3
    )
    resnet_finetune_parser.add_argument("--patience", type=int, default=3)
    resnet_finetune_parser.add_argument(
        "--learning-rate", type=float, default=1e-4,
        help="Classifier-head learning rate; locked to 1e-4 for E04.",
    )
    resnet_finetune_parser.add_argument(
        "--backbone-learning-rate", type=float, default=1e-5,
        help="ResNet layer4 learning rate; locked to 1e-5 for E04.",
    )
    resnet_finetune_parser.add_argument(
        "--weight-decay", type=float, default=1e-4
    )
    resnet_finetune_parser.add_argument("--seed", type=int, default=42)
    resnet_finetune_parser.add_argument(
        "--smoke",
        action="store_true",
        help="Run one epoch on balanced train/dev videos and skip test.",
    )
    resnet_finetune_parser.add_argument(
        "--smoke-videos-per-label", type=int, default=2
    )
    resnet_finetune_parser.set_defaults(handler=_train_resnet18_finetune)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except (
        ArchiveError,
        ImportError,
        OuluDataError,
        OSError,
        RuntimeError,
        ValueError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

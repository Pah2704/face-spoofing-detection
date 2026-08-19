#!/usr/bin/env python3
"""Benchmark E01--E03 on the same 600 test crops without changing scores."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import statistics
import time

import numpy as np

from face_spoofing.data.cnn_dataset import CnnFrameDataset
from face_spoofing.features.cache import LbpCacheConfig
from face_spoofing.features.lbp import extract_lbp
from face_spoofing.models.mobilenet_v2 import load_mobilenet_v2_checkpoint
from face_spoofing.models.resnet18 import load_resnet18_checkpoint
from face_spoofing.training.artifacts import atomic_write_json, sha256_file


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument(
        "--manifest", type=Path, default=Path("data/manifests/frames_protocol1.csv")
    )
    parser.add_argument(
        "--lbp-cache",
        type=Path,
        default=Path(
            "data/processed/features/lbp/"
            "bbfd395b02a3f89ac23c0d187dfef43319add4a7a7e740b9e26abfadacf9eb78"
        ),
    )
    parser.add_argument(
        "--lbp-model",
        type=Path,
        default=Path(
            "artifacts/runs/lbp_svm/e01_20260712_lbp_svm_seed42_verified/"
            "model/lbp_svm.joblib"
        ),
    )
    parser.add_argument(
        "--mobilenet-model",
        type=Path,
        default=Path(
            "artifacts/runs/mobilenet_v2/e02_20260712_mobilenet_v2_seed42/"
            "model/best.pt"
        ),
    )
    parser.add_argument(
        "--resnet-model",
        type=Path,
        default=Path(
            "artifacts/runs/resnet18/e03_20260713_resnet18_seed42/model/best.pt"
        ),
    )
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/benchmarks/baseline_latency_test600.json"),
    )
    return parser.parse_args()


def _resolve(root: Path, path: Path) -> Path:
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def _synchronize(torch, device) -> None:
    if device.type == "cuda":
        torch.cuda.synchronize(device)


def _pure_cnn(torch, model, sample, device, batch_size: int) -> dict[str, float]:
    values = sample.repeat(batch_size, 1, 1, 1).to(device)
    model.eval()
    with torch.inference_mode():
        for _ in range(20):
            torch.sigmoid(model(values))
        _synchronize(torch, device)
        started = time.perf_counter()
        for _ in range(100):
            torch.sigmoid(model(values))
        _synchronize(torch, device)
    elapsed = time.perf_counter() - started
    return {
        "batch_size": batch_size,
        "iterations": 100,
        "seconds_per_frame": elapsed / (100 * batch_size),
    }


def _pure_lbp(model, feature: np.ndarray, batch_size: int) -> dict[str, float]:
    values = np.repeat(feature[np.newaxis, :], batch_size, axis=0)
    for _ in range(20):
        model.decision_function(values)
    started = time.perf_counter()
    for _ in range(1000):
        model.decision_function(values)
    elapsed = time.perf_counter() - started
    return {
        "batch_size": batch_size,
        "iterations": 1000,
        "seconds_per_frame": elapsed / (1000 * batch_size),
    }


def _cnn_end_to_end(
    torch,
    model,
    dataset,
    indices,
    device,
    *,
    batch_size: int,
    workers: int,
) -> float:
    subset = torch.utils.data.Subset(dataset, indices)
    loader = torch.utils.data.DataLoader(
        subset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=workers,
        pin_memory=device.type == "cuda",
        persistent_workers=False,
    )
    _synchronize(torch, device)
    started = time.perf_counter()
    with torch.inference_mode():
        for batch in loader:
            images = batch["image"].to(device, non_blocking=True)
            torch.sigmoid(model(images))
    _synchronize(torch, device)
    return time.perf_counter() - started


def _lbp_feature(path: Path, config: LbpCacheConfig) -> np.ndarray:
    import cv2

    cv2.setNumThreads(1)
    image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise RuntimeError(f"cannot decode {path}")
    image = cv2.resize(
        image,
        (config.image_size, config.image_size),
        interpolation=cv2.INTER_AREA,
    )
    return extract_lbp(
        image,
        radius=config.radius,
        points=config.points,
        grid_rows=config.grid_rows,
        grid_cols=config.grid_cols,
    )


def _lbp_end_to_end(model, paths, workers: int) -> float:
    config = LbpCacheConfig()
    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as executor:
        features = np.stack(list(executor.map(lambda p: _lbp_feature(p, config), paths)))
    model.decision_function(features)
    return time.perf_counter() - started


def main() -> int:
    args = _arguments()
    root = args.project_root.resolve()
    if args.batch_size <= 0 or args.workers <= 0 or args.repeats <= 0:
        raise ValueError("batch-size, workers and repeats must be positive")
    os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
    import joblib
    import torch

    torch.manual_seed(42)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    manifest = _resolve(root, args.manifest)
    dataset = CnnFrameDataset(manifest, "test", project_root=root, training=False)
    indices = [index for index, record in enumerate(dataset.records) if record.sample_index == 0]
    if len(indices) != 600:
        raise RuntimeError(f"expected one sample for 600 test videos, found {len(indices)}")
    video_ids = [dataset.records[index].video_id for index in indices]
    paths = [dataset.records[index].face_path for index in indices]
    subset_hash = hashlib.sha256("\n".join(video_ids).encode("utf-8")).hexdigest()

    lbp_model_path = _resolve(root, args.lbp_model)
    mobile_path = _resolve(root, args.mobilenet_model)
    resnet_path = _resolve(root, args.resnet_model)
    lbp_model = joblib.load(lbp_model_path)
    mobile, _ = load_mobilenet_v2_checkpoint(mobile_path, map_location=device)
    resnet, _ = load_resnet18_checkpoint(resnet_path, map_location=device)
    mobile = mobile.to(device).eval()
    resnet = resnet.to(device).eval()
    sample = dataset[indices[0]]["image"].unsqueeze(0)
    lbp_sample = _lbp_feature(paths[0], LbpCacheConfig())

    # One unmeasured pass warms CUDA kernels and OS image cache.
    _cnn_end_to_end(torch, mobile, dataset, indices, device, batch_size=args.batch_size, workers=args.workers)
    _cnn_end_to_end(torch, resnet, dataset, indices, device, batch_size=args.batch_size, workers=args.workers)
    _lbp_end_to_end(lbp_model, paths, args.workers)

    e2e = {"LBP-SVM": [], "MobileNetV2": [], "ResNet18": []}
    for _ in range(args.repeats):
        e2e["LBP-SVM"].append(_lbp_end_to_end(lbp_model, paths, args.workers))
        e2e["MobileNetV2"].append(
            _cnn_end_to_end(torch, mobile, dataset, indices, device, batch_size=args.batch_size, workers=args.workers)
        )
        e2e["ResNet18"].append(
            _cnn_end_to_end(torch, resnet, dataset, indices, device, batch_size=args.batch_size, workers=args.workers)
        )

    result = {
        "scope": {
            "input": "one processed face crop per test video (sample_index=0)",
            "frames": 600,
            "subset_video_ids_sha256": subset_hash,
            "batch_size": args.batch_size,
            "workers": args.workers,
            "repeats": args.repeats,
            "device": str(device),
            "gpu": torch.cuda.get_device_name(device) if device.type == "cuda" else None,
        },
        "models": {
            "LBP-SVM": {
                "path": lbp_model_path.relative_to(root).as_posix(),
                "sha256": sha256_file(lbp_model_path),
                "pure_batch1": _pure_lbp(lbp_model, lbp_sample, 1),
                "pure_batch16": _pure_lbp(lbp_model, lbp_sample, args.batch_size),
            },
            "MobileNetV2": {
                "path": mobile_path.relative_to(root).as_posix(),
                "sha256": sha256_file(mobile_path),
                "pure_batch1": _pure_cnn(torch, mobile, sample, device, 1),
                "pure_batch16": _pure_cnn(torch, mobile, sample, device, args.batch_size),
            },
            "ResNet18": {
                "path": resnet_path.relative_to(root).as_posix(),
                "sha256": sha256_file(resnet_path),
                "pure_batch1": _pure_cnn(torch, resnet, sample, device, 1),
                "pure_batch16": _pure_cnn(torch, resnet, sample, device, args.batch_size),
            },
        },
        "end_to_end_from_crop": {
            name: {
                "seconds": values,
                "median_seconds": statistics.median(values),
                "median_seconds_per_frame": statistics.median(values) / 600,
            }
            for name, values in e2e.items()
        },
        "caveat": (
            "LBP runs on CPU with threaded feature extraction; CNNs run on GPU. "
            "Results describe this machine, not mobile/CPU deployment."
        ),
    }
    output = _resolve(root, args.output)
    atomic_write_json(output, result)
    print(json.dumps({"output": output.as_posix(), **result}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Linear SVM model used by the E01 LBP baseline."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Iterable


@dataclass(frozen=True, slots=True)
class LBPSVMConfig:
    """Reproducible estimator and development-search configuration."""

    c_values: tuple[float, ...] = (
        1e-4,
        1e-3,
        1e-2,
        1e-1,
        1.0,
        10.0,
    )
    class_weight: str = "balanced"
    penalty: str = "l2"
    loss: str = "squared_hinge"
    dual: bool = False
    tol: float = 1e-4
    max_iter: int = 20_000
    seed: int = 42
    standardize: bool = True

    def validate(self) -> None:
        if not self.c_values:
            raise ValueError("c_values must contain at least one value.")
        if any(
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(float(value))
            or float(value) <= 0
            for value in self.c_values
        ):
            raise ValueError("Every C value must be a finite positive number.")
        if len(set(float(value) for value in self.c_values)) != len(
            self.c_values
        ):
            raise ValueError("c_values must not contain duplicates.")
        if self.class_weight != "balanced":
            raise ValueError("E01 requires class_weight='balanced'.")
        if self.penalty != "l2" or self.loss != "squared_hinge":
            raise ValueError("E01 is locked to L2 penalty and squared_hinge loss.")
        if self.dual:
            raise ValueError("E01 requires dual=False because n_samples > n_features.")
        if not math.isfinite(self.tol) or self.tol <= 0:
            raise ValueError("tol must be finite and positive.")
        if self.max_iter <= 0:
            raise ValueError("max_iter must be positive.")
        if isinstance(self.seed, bool) or not isinstance(self.seed, int):
            raise TypeError("seed must be an integer.")

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["c_values"] = list(self.c_values)
        return payload


def build_lbp_svm(c_value: float, config: LBPSVMConfig):
    """Build a train-only scaler plus spoof-positive LinearSVC pipeline."""

    config.validate()
    c = float(c_value)
    if c not in {float(value) for value in config.c_values}:
        raise ValueError(f"C={c} is not in the resolved development grid.")

    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.svm import LinearSVC

    steps = []
    if config.standardize:
        steps.append(("scaler", StandardScaler()))
    steps.append(
        (
            "svm",
            LinearSVC(
                C=c,
                penalty=config.penalty,
                loss=config.loss,
                dual=config.dual,
                tol=config.tol,
                max_iter=config.max_iter,
                class_weight=config.class_weight,
                random_state=config.seed,
            ),
        )
    )
    return Pipeline(steps)


def assert_spoof_positive_estimator(estimator) -> None:
    """Reject estimators whose decision score orientation is ambiguous."""

    svm = estimator.named_steps.get("svm")
    if svm is None or not hasattr(svm, "classes_"):
        raise ValueError("Estimator is not fitted or has no SVM step.")
    classes = [int(value) for value in svm.classes_]
    if classes != [0, 1]:
        raise ValueError(
            f"Expected estimator classes [0, 1], found {classes}; "
            "decision_function orientation would be unsafe."
        )


__all__ = [
    "LBPSVMConfig",
    "assert_spoof_positive_estimator",
    "build_lbp_svm",
]


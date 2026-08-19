"""Model factories for face anti-spoofing baselines."""

from .lbp_svm import LBPSVMConfig, build_lbp_svm

_MOBILENET_EXPORTS = {
    "MobileNetV2Config",
    "assert_spoof_logit_contract",
    "build_mobilenet_v2",
    "load_mobilenet_v2_checkpoint",
    "save_mobilenet_v2_checkpoint",
    "spoof_probability",
}

_RESNET_EXPORTS = {
    "ResNet18Config",
    "build_resnet18",
    "load_resnet18_checkpoint",
    "save_resnet18_checkpoint",
}


def __getattr__(name: str):
    """Load optional deep-learning dependencies only when E02 is requested."""

    if name in _MOBILENET_EXPORTS:
        from . import mobilenet_v2

        return getattr(mobilenet_v2, name)
    if name in _RESNET_EXPORTS:
        from . import resnet18

        return getattr(resnet18, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "LBPSVMConfig",
    "build_lbp_svm",
    *sorted(_MOBILENET_EXPORTS),
    *sorted(_RESNET_EXPORTS),
]

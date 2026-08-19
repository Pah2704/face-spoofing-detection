from __future__ import annotations

import unittest

import numpy as np

from face_spoofing.models.lbp_svm import (
    LBPSVMConfig,
    assert_spoof_positive_estimator,
    build_lbp_svm,
)


class LbpSvmModelTests(unittest.TestCase):
    def test_config_rejects_invalid_grid(self):
        with self.assertRaisesRegex(ValueError, "finite positive"):
            LBPSVMConfig(c_values=(0.0,)).validate()
        with self.assertRaisesRegex(ValueError, "duplicates"):
            LBPSVMConfig(c_values=(0.1, 0.1)).validate()

    def test_pipeline_fits_with_spoof_positive_score(self):
        features = np.array(
            [
                [-2.0, -1.0],
                [-1.0, -2.0],
                [1.0, 2.0],
                [2.0, 1.0],
            ],
            dtype=np.float32,
        )
        labels = np.array([0, 0, 1, 1], dtype=np.int8)
        config = LBPSVMConfig(c_values=(0.1,))
        estimator = build_lbp_svm(0.1, config)
        estimator.fit(features, labels)

        assert_spoof_positive_estimator(estimator)
        scores = estimator.decision_function(features)
        self.assertLess(float(scores[:2].max()), float(scores[2:].min()))

    def test_unfitted_estimator_is_rejected(self):
        estimator = build_lbp_svm(0.1, LBPSVMConfig(c_values=(0.1,)))
        with self.assertRaisesRegex(ValueError, "not fitted"):
            assert_spoof_positive_estimator(estimator)


if __name__ == "__main__":
    unittest.main()


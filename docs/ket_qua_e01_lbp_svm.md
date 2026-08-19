# Kết quả E01 — LBP-SVM trên OULU-NPU Protocol 1

## 1. Trạng thái

E01 đã hoàn tất ngày 12/07/2026 với run bất biến:

~~~text
artifacts/runs/lbp_svm/e01_20260712_lbp_svm_seed42_verified/
~~~

Model chỉ được fit trên `train`. Siêu tham số và hai threshold được chọn trên
`dev`, sau đó khóa trước khi truy cập feature `test`. Không refit bằng
`train + dev` và không điều chỉnh lại theo kết quả test.

## 2. Dữ liệu và đặc trưng đã khóa

| Hạng mục | Giá trị |
|---|---|
| Protocol | OULU-NPU Protocol 1 |
| Nhãn | live = 0, spoof = 1 |
| Frame/video | 10 vị trí lấy đều |
| Crop hợp lệ | 26.999/27.000 |
| Ngoại lệ | `3_1_28_4__00`, dev spoof, `no_face` |
| Đầu vào | grayscale 128 x 128 |
| LBP | uniform, radius 1, 8 điểm |
| Spatial grid | 8 x 8, histogram L1 theo từng cell |
| Feature dimension | 640 float32/frame |
| Cache fingerprint | `bbfd395b02a3f89ac23c0d187dfef43319add4a7a7e740b9e26abfadacf9eb78` |
| Số feature | train 12.000, dev 8.999, test 6.000 |

Video ngoại lệ vẫn được đánh giá bằng trung bình của 9 frame hợp lệ. Không có
video nào bị loại khỏi dev hoặc test.

## 3. Cấu hình model và model selection

- `StandardScaler` chỉ fit trên 12.000 frame train.
- `LinearSVC`: L2, squared hinge, `dual=false`, `class_weight=balanced`,
  `tol=1e-4`, `max_iter=20000`, seed 42.
- Grid tìm kiếm C trên dev: `1e-4, 1e-3, 1e-2, 1e-1, 1, 10`.
- Score video là trung bình `decision_function` của các frame hợp lệ.
- Chọn C theo thứ tự video-level: ACER thấp hơn, APCER thấp hơn, F1 cao hơn,
  rồi C nhỏ hơn.
- C được chọn: `0.0001`; cả sáu trial đều hội tụ.
- Threshold frame: `-0.30493875271174625`.
- Threshold video: `-0.40009589818659047`.
- Quy tắc quyết định: `score >= threshold` là spoof.

## 4. Kết quả chính

Các số dưới đây dùng threshold tương ứng đã chọn trên dev. Giá trị metric được
biểu diễn theo phần trăm.

| Split | Cấp | N | Accuracy | Precision | Recall | F1 | APCER | BPCER | ACER |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Dev | Frame | 8.999 | 85,58 | 97,23 | 84,37 | 90,35 | 15,63 | 9,61 | 12,62 |
| Dev | Video | 900 | 89,11 | 96,98 | 89,17 | 92,91 | 10,83 | 11,11 | **10,97** |
| Test | Frame | 6.000 | 83,02 | 87,37 | 92,08 | 89,66 | 7,92 | 53,25 | 30,58 |
| Test | Video | 600 | 83,67 | 86,31 | 94,58 | 90,26 | 5,42 | 60,00 | **32,71** |

Confusion matrix video-level:

| Split | TN | FP | FN | TP |
|---|---:|---:|---:|---:|
| Dev | 160 | 20 | 78 | 642 |
| Test | 48 | 72 | 26 | 454 |

APCER video-level theo loại attack:

| Split | Print | Replay |
|---|---:|---:|
| Dev | 8,61% | 13,06% |
| Test | 3,33% | 7,50% |

## 5. Diễn giải

Trên dev, mean aggregation theo video cải thiện ACER từ 12,62% xuống 10,97%
và F1 từ 90,35% lên 92,91%. Tuy nhiên, kết quả này không chuyển sang test:
video ACER test là 32,71%, cao hơn frame ACER 30,58%.

Sai số test tập trung ở lớp live. Model từ chối nhầm 72/120 video live, làm
BPCER tăng lên 60%, trong khi chỉ nhận nhầm 26/480 attack là live, nên APCER
chỉ 5,42%. F1 vẫn cao do lớp spoof chiếm 80% test; vì vậy không được dùng F1
đơn lẻ để kết luận model cân bằng tốt. Đây là dấu hiệu baseline texture cổ
điển nhạy với domain shift giữa các split/session của Protocol 1.

Kết quả test được giữ nguyên để phản ánh khả năng tổng quát hóa thật. Không
dùng test để đổi C, threshold, preprocessing hay cách aggregation.

## 6. Artifact và kiểm chứng

Run chứa đầy đủ:

- model đã serialize và metadata tại `model/`;
- toàn bộ trial C tại `selection/c_search.csv`;
- threshold cùng score contract tại `threshold.json`;
- prediction của mọi row manifest và mọi video tại `predictions/`;
- metric, attack breakdown và coverage tại `metrics/`;
- confusion matrix dev/test tại `figures/`;
- môi trường, timing, source-tree hash và checksum tại
  `environment.json`, `timing.json`, `run_manifest.json`.

Model đã được load lại sau khi lưu và decision score dev/test khớp với sai số
tuyệt đối tối đa `1e-12`. `run_manifest.json` kiểm kê 18 artifact có SHA-256,
bao gồm source snapshot khớp source-tree hash của E01. Bộ test hiện tại đã mở
rộng lên 95 ca và đều đạt.

Run xác minh tái tạo byte-for-byte model, prediction, metric, threshold,
config và confusion figure của run đầu. Các tệp timing, environment, result,
manifest và thời gian fit trong bảng C thay đổi đúng như kỳ vọng giữa hai lần
chạy.

Thời gian trong run xác minh là 134,82 giây; riêng trích feature cache lần đầu là
23,67 giây. `test_decision_seconds_per_frame` chỉ đo SVM trên feature đã cache,
không phải end-to-end latency từ video.

## 7. Báo cáo phụ tương thích script OULU

Đối chiếu `Baseline/Tools/performances.m` cho threshold dev-EER
`-0.39482009448824246`, E01 có kết quả test video:

| Nhóm | APCER | BPCER | ACER |
|---|---:|---:|---:|
| Print | 3,75% | 60,00% | 31,88% |
| Replay | 7,50% | 60,00% | 33,75% |
| Worst-case | 7,50% | 60,00% | **33,75%** |

Dev EER là 11,11%. Đây là báo cáo secondary; bảng min-ACER ở trên vẫn là
policy chính để so sánh nhất quán E01–E03.

## 8. Lệnh tái lập

~~~bash
env OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1 \
    PYTHONPATH=src \
conda run --no-capture-output -n ai_env \
python -m face_spoofing train lbp-svm \
  --frame-manifest data/manifests/frames_protocol1.csv \
  --feature-cache-root data/processed/features/lbp \
  --run-root artifacts/runs/lbp_svm \
  --project-root . \
  --run-id <run_id_moi> \
  --feature-workers 6 \
  --seed 42 \
  --c-values 0.0001 0.001 0.01 0.1 1.0 10.0
~~~

Không dùng lại run ID hiện có vì pipeline chủ động từ chối ghi đè artifact.
Config tham chiếu nằm tại `configs/models/lbp_svm.yaml` và
`configs/experiments/e01_lbp_svm.yaml`.

## 9. Bước tiếp theo

E02 MobileNetV2 và E03 ResNet18 đã hoàn tất trên cùng split/crop/evaluator.
So sánh cuối tại `docs/ket_qua_tong_hop_e01_e03.md`.

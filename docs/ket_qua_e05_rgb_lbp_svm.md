# Kết quả E05 — RGB-LBP-SVM

## 1. Mục tiêu và trạng thái

E05 là ablation màu của E01: giữ nguyên dữ liệu, crop, kích thước 128×128,
$LBP^{riu2}_{8,1}$, lưới 8×8, `StandardScaler`, `LinearSVC`, lưới $C$, seed,
aggregation, threshold policy và evaluator; chỉ thay LBP grayscale 640D bằng
ba descriptor trên R–G–B ghép theo thứ tự cố định thành 1.920D.

Main run đã hoàn tất:

`artifacts/runs/rgb_lbp_svm/e05_20260721_rgb_lbp_svm_seed42/`

Run tái lập:

`artifacts/runs/rgb_lbp_svm/e05_20260721_rgb_lbp_svm_seed42_repro/`

Feature cache:

`data/processed/features/rgb_lbp/8a837aeb66b98001fce3431e4760a4be80b9bb8262604929ceb33f4fb4792a3b/`

## 2. Contract đã khóa

| Thành phần | Giá trị |
|---|---|
| Experiment/model | E05 / `rgb_lbp_svm` |
| Input | RGB 128×128, OpenCV BGR được đổi sang RGB |
| Feature order | `[LBP(R), LBP(G), LBP(B)]` |
| LBP mỗi kênh | riu2, P=8, R=1, 10 bin, grid 8×8 |
| Feature dimension | 640/kênh; 1.920 tổng |
| Histogram | L1 theo từng cell, từng kênh |
| Classifier | train-only `StandardScaler` + `LinearSVC` |
| SVM | L2, squared hinge, `dual=False`, balanced class |
| C grid | 1e-4, 1e-3, 1e-2, 1e-1, 1, 10 |
| Selected C | **1e-4** |
| Seed | 42 |
| Frame threshold | -0,4523026030 từ dev frame |
| Video threshold | -0,3479599407 từ dev video |
| Score | lớn hơn nghĩa là spoof; `score >= threshold` |

Coverage đúng 12.000/8.999/6.000 frame train/dev/test, 900 dev video và 600
test video. Một dev frame `no_face` được loại giống E01.

## 3. Kết quả chính

| Split | Cấp | Accuracy | Precision | Recall | F1 | APCER | BPCER | ACER |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Dev | Frame | 96,22% | 98,68% | 96,57% | 97,61% | 3,43% | 5,17% | **4,30%** |
| Dev | Video | 96,67% | 99,57% | 96,25% | 97,88% | 3,75% | 1,67% | **2,71%** |
| Test | Frame | 88,45% | 93,81% | 91,60% | 92,70% | 8,40% | 24,17% | **16,28%** |
| Test | Video | 88,33% | 95,15% | 90,00% | 92,51% | 10,00% | 18,33% | **14,17%** |

Confusion matrix test video: `TN=98, FP=22, FN=48, TP=432`.

## 4. Ablation trực tiếp với E01 grayscale

| Test video | E01 Gray-LBP | E05 RGB-LBP | E05 − E01 |
|---|---:|---:|---:|
| Feature dimension | 640 | 1.920 | ×3 |
| Accuracy | 83,67% | **88,33%** | +4,67 điểm % |
| F1 | 90,26% | **92,51%** | +2,25 điểm % |
| APCER | **5,42%** | 10,00% | +4,58 điểm % |
| BPCER | 60,00% | **18,33%** | **-41,67 điểm %** |
| ACER | 32,71% | **14,17%** | **-18,54 điểm %** |
| FP / FN | 72 / 26 | **22 / 48** | -50 / +22 |

RGB-LBP cải thiện rất lớn tính cân bằng của E01: số live video bị chặn sai giảm
từ 72 xuống 22. Đổi lại, số attack bị chấp nhận sai tăng từ 26 lên 48. Vì ACER
cân hai loại lỗi, mức giảm BPCER lớn hơn làm ACER giảm 18,54 điểm phần trăm.
Do đó kết luận đúng là **màu giúp operating point cân bằng hơn**, không phải
RGB-LBP tốt hơn E01 ở mọi tiêu chí an ninh.

Trên dev, ACER giảm từ 10,97% xuống 2,71%. Khoảng cách dev→test của E05 là
+11,46 điểm, thấp hơn gap +21,74 điểm của E01 nhưng vẫn đáng kể.

## 5. Frame và video aggregation

| Model | Test frame ACER | Test video ACER | Video − frame |
|---|---:|---:|---:|
| E01 Gray-LBP | 30,58% | 32,71% | +2,13 điểm % |
| E05 RGB-LBP | 16,28% | **14,17%** | **-2,11 điểm %** |

Khác E01, mean aggregation có lợi cho E05. Ở E05, APCER tăng từ 8,40% lên
10,00% nhưng BPCER giảm từ 24,17% xuống 18,33%, nên ACER video thấp hơn. Kết
quả tiếp tục cho thấy aggregation không có tác động cố định; nó phụ thuộc phân
phối score của từng biểu diễn.

## 6. Attack breakdown

Tại threshold min-ACER chính:

| Nhóm test | Số attack | Bỏ lọt | APCER |
|---|---:|---:|---:|
| Print | 240 | 19 | 7,92% |
| Replay | 240 | 29 | 12,08% |
| Printer 1 | 120 | 10 | 8,33% |
| Printer 2 | 120 | 9 | 7,50% |
| Display 1 | 120 | 11 | 9,17% |
| Display 2 | 120 | 18 | **15,00%** |

Replay khó hơn print, chủ yếu do `display_2`. So với E01, APCER tăng ở cả
print (3,33%→7,92%) và replay (7,50%→12,08%). Cải thiện tổng thể của E05 vì
thế đến từ giảm false positive trên live nhiều hơn là tăng nhận diện attack.

Policy phụ dev-EER tương thích OULU chọn threshold -0,4016573466, dev EER
2,78% và cho test worst-case ACER 16,04% (`BPCER=22,50%`, worst APCER=9,58%).
Nó vẫn tốt hơn nhiều so với worst-case 33,75% của E01.

## 7. Lưới C

`C=1e-4` và `C=1e-3` cùng dev video ACER 2,7083%, APCER 3,75% và F1 97,88%.
Tie-break cuối ưu tiên C nhỏ hơn nên chọn `1e-4`. Sáu trial không phát
`ConvergenceWarning`; số vòng lặp lần lượt là 6, 7, 9, 261, 17 và 12.

Không đổi C sau khi đọc test. Threshold frame/video cũng được khóa từ dev trước
khi `test_idx` được lấy trong runner.

## 8. Tài nguyên

| Hạng mục | E01 Gray-LBP | E05 RGB-LBP | Tỷ lệ E05/E01 |
|---|---:|---:|---:|
| Feature dimension | 640 | 1.920 | 3,00× |
| Compressed feature cache | 20,79 MB | 62,14 MB | 2,99× |
| Feature extraction | 23,67 s | 73,00 s | 3,08× |
| Model artifact | 21.693 B | 62.653 B | 2,89× |
| Selected fit | 0,678 s | 2,822 s | 4,16× |
| Test decision/frame | 2,20 µs | 7,26 µs | 3,29× |

Các số decision chỉ đo SVM trên feature đã cache, chưa gồm đọc ảnh, resize và
trích LBP. Dù tăng gần ba lần, model E05 vẫn chỉ khoảng 61,2 KiB và nhẹ hơn rất
nhiều so với CNN.

Hệ số SVM trong không gian feature đã standardize phân bổ L1 theo R/G/B là
35,75% / 32,72% / 31,54%. Đây chỉ là mô tả độ lớn hệ số, không phải bằng chứng
nhân quả hay xếp hạng tầm quan trọng kênh.

## 9. Kiểm chứng artifact và tái lập

- Main run có 17 artifact được phủ bởi `run_manifest.json`; 17/17 checksum
  kiểm tra lại thành công.
- `model/metadata.json` xác nhận scaler fit 12.000 mẫu, feature 1.920D, classes
  `[0,1]`, 1.920 hệ số khác 0 và model reload tolerance `1e-12`.
- Runner reload model và xác nhận score dev/test cùng label không thay đổi.
- Run tái lập dùng lại đúng content-addressed cache và không đổi config.
- 13 artifact ổn định — config, threshold, model, dev/test metric, prediction
  và figure — giống byte-for-byte giữa main/repro.
- Toàn bộ 106 unit test pass sau khi thêm E05; cache E01 cũ vẫn load đúng
  fingerprint và shape `(26999, 640)`.
- Regression run E01 sau khi tổng quát hóa runner cho E05 có 10 core artifact
  (config, threshold, model, metric và prediction) giống byte-for-byte với run
  E01 verified; kết quả grayscale không bị thay đổi.

## 10. Lệnh tái lập

```bash
env OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1 \
    PYTHONPATH=src \
conda run --no-capture-output -n ai_env \
python -m face_spoofing train rgb-lbp-svm \
  --frame-manifest data/manifests/frames_protocol1.csv \
  --feature-cache-root data/processed/features/rgb_lbp \
  --run-root artifacts/runs/rgb_lbp_svm \
  --project-root . \
  --run-id <run_id_moi> \
  --feature-workers 6 \
  --seed 42 \
  --c-values 0.0001 0.001 0.01 0.1 1.0 10.0
```

Không ghi đè hai run đã khóa. Dùng run ID mới khi tái lập.

## 11. Kết luận

H5 được ủng hộ trong cấu hình đã khóa: giữ thông tin màu bằng RGB-LBP giảm test
video ACER từ 32,71% xuống 14,17%. Đây là kết quả ACER thấp nhất trong năm cấu
hình E01–E05, thấp hơn E04 ResNet18 0,63 điểm; tuy nhiên E04 vẫn có APCER và F1
tốt hơn. Với chỉ một seed/protocol, chênh lệch nhỏ E05–E04 không đủ để tuyên bố
RGB-LBP tổng quát hơn ResNet18 fine-tuned.

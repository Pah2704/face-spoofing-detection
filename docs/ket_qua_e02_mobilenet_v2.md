# Kết quả E02 — MobileNetV2 trên OULU-NPU Protocol 1

## 1. Trạng thái và giao thức

E02 đã hoàn tất với run chính:

~~~text
artifacts/runs/mobilenet_v2/e02_20260712_mobilenet_v2_seed42/
~~~

Run dùng đúng manifest/crop của E01. Checkpoint chỉ được chọn bằng dev video
ACER; threshold frame, video và threshold EER tương thích OULU đều được ghi
vào `selection/frozen.json` trước khi test dataset được dựng và suy luận.

## 2. Cấu hình đã khóa

| Hạng mục | Giá trị |
|---|---|
| Backbone | torchvision MobileNetV2, `IMAGENET1K_V2` |
| Input | RGB 224 x 224, ImageNet normalization |
| Augmentation train | horizontal flip 0,5 |
| Backbone | freeze toàn bộ, kể cả BatchNorm statistics |
| Head | dropout 0,2 + một spoof logit |
| Loss | weighted BCE; `pos_weight = 2400/9600 = 0,25` |
| Optimizer | Adam, LR `1e-4`, weight decay `1e-4` |
| Batch / worker | 16 / 4 |
| Epoch | tối đa 15, minimum 3, patience 3 |
| Aggregation | mean spoof probability |
| Seed / device | 42 / RTX 3060 CUDA |

Một spoof logit với weighted BCE tương đương bài toán cross-entropy nhị phân;
score cao hơn luôn có nghĩa là spoof. Main run chỉ train head 1.281 tham số;
fine-tune backbone được giữ làm ablation, không trộn vào baseline chính.

## 3. Coverage và model selection

- Train: 12.000 frame, 1.200 video.
- Dev: 8.999/9.000 frame, 900 video; `3_1_28_4__00` là `no_face`.
- Test: 6.000/6.000 frame, 600 video.
- Best checkpoint: epoch 15, dev video ACER 13,75%.
- Threshold frame min-ACER: `0.5233199596405029`.
- Threshold video min-ACER: `0.5125711590051651`.
- Threshold video dev-EER tương thích OULU: `0.4487620919942856`.

## 4. Kết quả chính — dev min-ACER

| Split | Cấp | N | Accuracy | Precision | Recall | F1 | APCER | BPCER | ACER |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Dev | Frame | 8.999 | 82,08 | 97,21 | 79,89 | 87,70 | 20,11 | 9,17 | 14,64 |
| Dev | Video | 900 | 83,00 | 97,49 | 80,83 | 88,38 | 19,17 | 8,33 | **13,75** |
| Test | Frame | 6.000 | 77,25 | 91,20 | 79,21 | 84,78 | 20,79 | 30,58 | 25,69 |
| Test | Video | 600 | 78,33 | 91,27 | 80,63 | 85,62 | 19,38 | 30,83 | **25,10** |

Video aggregation cải thiện nhẹ so với frame-level ở cả dev và test. So với
E01 LBP-SVM, E02 kém hơn trên dev (13,75% so với 10,97%) nhưng tốt hơn rõ ở
test (25,10% so với 32,71%). Lợi ích chính là BPCER test giảm từ 60,00% xuống
30,83%; đổi lại APCER test tăng từ 5,42% lên 19,38%.

APCER test video theo attack type gần cân bằng: print 19,17%, replay 19,58%.

## 5. Báo cáo phụ tương thích script OULU

`Baseline/Tools/performances.m` trong `Baseline.tar` chọn threshold EER trên
dev rồi báo APCER riêng print/replay và worst-case. Kết quả phụ E02:

| Split | Nhóm | APCER | BPCER | ACER |
|---|---|---:|---:|---:|
| Dev | Print | 12,22% | 13,89% | 13,06% |
| Dev | Replay | 15,28% | 13,89% | 14,58% |
| Test | Print | 15,00% | 36,67% | 25,83% |
| Test | Replay | 15,83% | 36,67% | 26,25% |
| Test | Worst-case | 15,83% | 36,67% | **26,25%** |

Policy này là secondary để đối chiếu official baseline; không thay kết quả
min-ACER chính đã dùng thống nhất cho E01–E03.

## 6. Chi phí và artifact

| Hạng mục | Giá trị |
|---|---:|
| Tổng tham số | 2.225.153 |
| Tham số train | 1.281 |
| Checkpoint | 9.151.038 bytes |
| Training 15 epoch | 306,50 giây |
| Tổng run | 438,47 giây |
| Peak GPU memory | 263.034.368 bytes |
| Pure-model latency, batch 1 | 3,656 ms/frame |
| Test end-to-end từ crop, batch 16 | 0,895 ms/frame |

Hai latency có điều kiện đo khác nhau nên không so trực tiếp: pure-model dùng
batch 1 đã nằm trên GPU; end-to-end dùng batch 16 và bao gồm đọc/resize crop.

Run có 24 artifact được kiểm kê SHA-256, gồm checkpoint best/last, history,
frozen/test marker, prediction đầy đủ, metric, figure, environment CUDA và
source snapshot. Checkpoint load lại cho dev probability sai lệch tối đa `0`.
Hai smoke run cuối tái lập byte-for-byte checkpoint, prediction và metric.

## 7. Lệnh tái lập

~~~bash
env OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1 \
    PYTHONPATH=src \
conda run --no-capture-output -n ai_env \
python -m face_spoofing train mobilenet-v2 \
  --frame-manifest data/manifests/frames_protocol1.csv \
  --run-root artifacts/runs/mobilenet_v2 \
  --project-root . \
  --run-id <run_id_moi> \
  --device cuda \
  --batch-size 16 \
  --workers 4 \
  --max-epochs 15 \
  --minimum-epochs 3 \
  --patience 3 \
  --learning-rate 0.0001 \
  --weight-decay 0.0001 \
  --seed 42
~~~

Config tham chiếu: `configs/models/mobilenet_v2.yaml` và
`configs/experiments/e02_mobilenet_v2.yaml`.

## 8. Bước tiếp theo

E03 ResNet18 đã hoàn tất với cùng CNN dataset, augmentation, loss, batch,
checkpoint policy và evaluator. So sánh cuối tại
`docs/ket_qua_tong_hop_e01_e03.md`.

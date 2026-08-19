# Kết quả E03 — ResNet18 trên OULU-NPU Protocol 1

## 1. Trạng thái

Run chính đã hoàn tất:

~~~text
artifacts/runs/resnet18/e03_20260713_resnet18_seed42/
~~~

E03 dùng chung CNN dataset, transform, weighted loss, batch, seed, checkpoint
selection và evaluator với E02. Test chỉ được dựng sau khi checkpoint epoch 15
và các threshold dev đã được khóa.

## 2. Cấu hình

| Hạng mục | Giá trị |
|---|---|
| Backbone | ResNet18 `IMAGENET1K_V1` |
| Input | RGB 224 x 224, ImageNet normalization |
| Augmentation | horizontal flip 0,5 |
| Training | freeze backbone/BatchNorm, train head 513 tham số |
| Loss | weighted BCE, spoof `pos_weight=0,25` |
| Optimizer | Adam, LR `1e-4`, weight decay `1e-4` |
| Batch / worker | 16 / 4 |
| Epoch | 15, minimum 3, patience 3 |
| Aggregation | mean spoof probability |
| Seed / device | 42 / RTX 3060 CUDA |

Threshold frame là `0.5747010707855225`; threshold video là
`0.5859636425971985`; threshold dev-EER phụ là `0.5763986438512803`.

## 3. Kết quả chính — dev min-ACER

| Split | Cấp | N | Accuracy | Precision | Recall | F1 | APCER | BPCER | ACER |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Dev | Frame | 8.999 | 86,01 | 95,76 | 86,33 | 90,80 | 13,67 | 15,28 | 14,47 |
| Dev | Video | 900 | 86,44 | 96,57 | 86,11 | 91,04 | 13,89 | 12,22 | **13,06** |
| Test | Frame | 6.000 | 79,05 | 91,75 | 81,10 | 86,10 | 18,90 | 29,17 | 24,03 |
| Test | Video | 600 | 78,33 | 92,07 | 79,79 | 85,49 | 20,21 | 27,50 | **23,85** |

Video aggregation giảm ACER ở cả dev và test. Test print APCER là 19,58%,
replay APCER là 20,83%; sai số tương đối cân bằng giữa hai attack type.

## 4. Báo cáo phụ tương thích OULU

Với threshold dev-EER theo `Baseline/Tools/performances.m`:

| Split | Nhóm | APCER | BPCER | ACER |
|---|---|---:|---:|---:|
| Dev | Print | 11,39% | 13,89% | 12,64% |
| Dev | Replay | 15,28% | 13,89% | 14,58% |
| Test | Print | 18,75% | 27,50% | 23,13% |
| Test | Replay | 18,75% | 27,50% | 23,13% |
| Test | Worst-case | 18,75% | 27,50% | **23,13%** |

## 5. Chi phí và artifact

| Hạng mục | Giá trị |
|---|---:|
| Tổng tham số | 11.177.025 |
| Tham số train | 513 |
| Checkpoint | 44.790.078 bytes |
| Training 15 epoch | 272,51 giây |
| Tổng run | 407,59 giây |
| Peak GPU memory | 272.971.264 bytes |
| Pure-model latency batch 1 | 1,589 ms/frame |
| Test end-to-end batch 16 | 0,829 ms/frame |

ResNet18 lớn hơn MobileNetV2 gần 4,9 lần theo checkpoint nhưng nhanh hơn trên
RTX 3060 trong phép đo hiện tại. Đây là đặc tính kernel/GPU của môi trường đo,
không có nghĩa ResNet18 luôn nhanh hơn trên CPU hoặc thiết bị mobile.

Run có 24 artifact qua SHA-256, source snapshot, frozen/test marker và đủ mọi
prediction row. Checkpoint reload cho dev probability sai lệch tối đa `0`.
Hai smoke run tạo checkpoint và prediction giống byte-for-byte.

## 6. Lệnh tái lập

~~~bash
env OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1 \
    PYTHONPATH=src \
conda run --no-capture-output -n ai_env \
python -m face_spoofing train resnet18 \
  --frame-manifest data/manifests/frames_protocol1.csv \
  --run-root artifacts/runs/resnet18 \
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

Config tham chiếu: `configs/models/resnet18.yaml` và
`configs/experiments/e03_resnet18.yaml`.

## 7. Ablation tiếp theo

E04 đã mở riêng `layer4` của cùng ResNet18 và giảm test video ACER từ 23,85%
xuống 14,79%. Kết quả, kiểm soát leakage và lệnh tái lập tại
`docs/ket_qua_e04_resnet18_finetune_layer4.md`.

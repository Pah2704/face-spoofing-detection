# Kết quả E04 — Fine-tune layer4 của ResNet18

## 1. Mục tiêu và trạng thái

E04 là một ablation có chủ đích để trả lời câu hỏi: đặc trưng ImageNet
head-only của E03 có đang giới hạn khả năng học cue giả mạo hay không?

Main run đã hoàn tất ngày 14/07/2026:

~~~text
artifacts/runs/resnet18_finetune/
└── e04_20260714_resnet18_finetune_layer4_seed42/
~~~

E04 giữ nguyên dữ liệu, crop, transform, loss, aggregation, model selection và
evaluator của E03. Thay đổi duy nhất là mở `layer4` của ResNet18 và dùng
learning rate nhỏ hơn cho phần backbone này.

## 2. Cấu hình đã khóa trước main run

| Hạng mục | Giá trị |
|---|---|
| Khởi tạo | ResNet18 `IMAGENET1K_V1` |
| Frozen | stem, layer1, layer2, layer3 và BatchNorm tương ứng |
| Trainable | layer4, BatchNorm layer4 và classification head |
| Trainable params | 8.394.241 / 11.177.025 |
| Head / layer4 LR | `1e-4` / `1e-5` |
| Optimizer | Adam, weight decay `1e-4` |
| Loss | weighted BCE, `pos_weight=0,25` |
| Batch / worker | 16 / 4 |
| Epoch | tối đa 15, minimum 3, patience 3 |
| Transform | resize 224, flip ngang 0,5 ở train, ImageNet normalize |
| Selection | dev video `(ACER, APCER, -F1, epoch)` |
| Seed / AMP | 42 / tắt |

CLI từ chối learning rate hoặc seed khác cấu hình E04. Hai smoke run một epoch
tạo checkpoint, prediction, metric, threshold, figure và source snapshot giống
byte-for-byte ở 12 artifact ổn định. History khác nhau đúng ở các cột timing.

## 3. Model selection và threshold

Early stopping dừng sau epoch 9; best checkpoint là epoch 6.

| Epoch | Dev video ACER | Trạng thái |
|---:|---:|---|
| 1 | 3,96% | best |
| 2 | 2,78% | best |
| 3 | 2,92% | không cải thiện |
| 4 | 2,78% | best theo tie-break |
| 5 | 2,64% | best |
| 6 | **2,57%** | best cuối |
| 7 | 2,78% | không cải thiện |
| 8 | 2,71% | không cải thiện |
| 9 | 2,64% | patience đạt 3 |

Các threshold được khóa trên dev trước khi dựng test dataset:

- Frame min-ACER: `0.1373463273048401`.
- Video min-ACER: `0.13102353289723395`.
- Video dev-EER tương thích OULU: `0.27227422446012495`.

## 4. Kết quả chính

| Split | Cấp | N | Accuracy | Precision | Recall | F1 | APCER | BPCER | ACER |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Dev | Frame | 8.999 | 97,32 | 99,01 | 97,62 | 98,31 | 2,38 | 3,89 | 3,13 |
| Dev | Video | 900 | 98,22 | 99,03 | 98,75 | 98,89 | 1,25 | 3,89 | **2,57** |
| Test | Frame | 6.000 | 90,85 | 94,81 | 93,69 | 94,25 | 6,31 | 20,50 | **13,41** |
| Test | Video | 600 | 90,83 | 94,00 | 94,58 | 94,29 | 5,42 | 24,17 | **14,79** |

Confusion matrix video-level:

| Split | TN | FP | FN | TP |
|---|---:|---:|---:|---:|
| Dev | 173 | 7 | 9 | 711 |
| Test | 91 | 29 | 26 | 454 |

APCER test video theo nhóm:

| Nhóm | APCER |
|---|---:|
| Print | 7,08% |
| Replay | 3,75% |
| Printer 1 | 7,50% |
| Printer 2 | 6,67% |
| Display 1 | 5,83% |
| Display 2 | 1,67% |

Video aggregation giảm APCER từ 6,31% xuống 5,42% nhưng tăng BPCER từ 20,50%
lên 24,17%; vì vậy ACER xấu hơn frame-level 1,39 điểm phần trăm. Fine-tuning
không làm cho mean aggregation luôn có lợi.

## 5. So sánh trực tiếp E03 và E04

Hai hàng dưới dùng cùng test video và policy dev min-ACER.

| Model | Trainable params | F1 | APCER | BPCER | ACER |
|---|---:|---:|---:|---:|---:|
| E03 ResNet18 head-only | 513 | 85,49% | 20,21% | 27,50% | 23,85% |
| E04 fine-tune layer4 | 8.394.241 | **94,29%** | **5,42%** | **24,17%** | **14,79%** |
| Thay đổi E04 − E03 | +8.393.728 | +8,80 điểm | -14,79 điểm | -3,33 điểm | **-9,06 điểm** |

Fine-tuning layer4 cải thiện cả hai thành phần ACER, đặc biệt giảm mạnh attack
bị chấp nhận là live. Điều này ủng hộ giả thuyết rằng head-only chưa đủ để điều
chỉnh đặc trưng ImageNet cho cue presentation attack.

Khoảng cách dev → test của E04 vẫn là +12,22 điểm ACER, nên fine-tuning chưa
giải quyết domain shift. Kết quả chỉ có một seed và không được dùng để mở thêm
tuning trên test Protocol 1.

## 6. Báo cáo phụ tương thích OULU

Với threshold dev-EER:

| Nhóm test | APCER | BPCER | ACER |
|---|---:|---:|---:|
| Print | 9,58% | 13,33% | 11,46% |
| Replay | 7,08% | 13,33% | 10,21% |
| Worst-case | 9,58% | 13,33% | **11,46%** |

Ranking E04 tốt hơn E03 cũng giữ nguyên ở policy phụ: worst-case ACER giảm từ
23,13% xuống 11,46%.

## 7. Chi phí và artifact

| Hạng mục | E03 head-only | E04 layer4 |
|---|---:|---:|
| Tổng params | 11.177.025 | 11.177.025 |
| Trainable params | 513 | 8.394.241 |
| Epoch đã chạy | 15 | 9 |
| Training time | 272,51 s | 216,54 s |
| Peak GPU memory | 272.971.264 B | 373.958.144 B |
| Checkpoint | 44.790.078 B | 44.790.334 B |
| Pure batch-1 latency trong run | 1,589 ms | 1,759 ms |

E04 dừng sớm hơn nên tổng training time thấp hơn E03 dù mỗi epoch có backward
qua layer4; không nên diễn giải rằng fine-tuning rẻ hơn head-only. Inference
graph và tổng số tham số không đổi, vì vậy chi phí triển khai về bản chất vẫn
là ResNet18.

Main run có 24 artifact qua SHA-256. Checkpoint hash trong marker khóa và test
marker giống nhau; test bắt đầu sau frozen marker khoảng 6,5 giây. Source
snapshot khớp environment source hash và checkpoint reload cho probability sai
lệch tối đa bằng 0.

## 8. Lệnh tái lập

~~~bash
env CUBLAS_WORKSPACE_CONFIG=:4096:8 \
    OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1 \
    PYTHONPATH=src \
conda run --no-capture-output -n ai_env \
python -m face_spoofing train resnet18-finetune \
  --frame-manifest data/manifests/frames_protocol1.csv \
  --run-root artifacts/runs/resnet18_finetune \
  --project-root . \
  --run-id <run_id_moi> \
  --device cuda \
  --batch-size 16 \
  --workers 4 \
  --max-epochs 15 \
  --minimum-epochs 3 \
  --patience 3 \
  --learning-rate 0.0001 \
  --backbone-learning-rate 0.00001 \
  --weight-decay 0.0001 \
  --seed 42
~~~

Config tham chiếu:

- `configs/models/resnet18_finetune_layer4.yaml`
- `configs/experiments/e04_resnet18_finetune_layer4.yaml`

Không dùng lại run ID hiện có và không thay cấu hình theo kết quả test E04.

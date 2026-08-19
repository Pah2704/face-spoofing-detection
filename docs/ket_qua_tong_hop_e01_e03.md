# Tổng hợp ba baseline OULU-NPU Protocol 1

> Tài liệu này giữ nguyên phép so sánh ba baseline E01–E03. Ablation E04
> fine-tune `layer4` được thực hiện sau đó và đạt test video ACER 14,79%; xem
> `docs/ket_qua_e04_resnet18_finetune_layer4.md`.

## Kết quả chính ở video-level

Threshold của từng model được chọn độc lập trên dev bằng cùng mục tiêu
min-ACER; test không tham gia model/threshold selection.

| Model | Dev F1 | Dev APCER | Dev BPCER | Dev ACER | Test F1 | Test APCER | Test BPCER | Test ACER |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| LBP-SVM | **92,91%** | **10,83%** | 11,11% | **10,97%** | **90,26%** | **5,42%** | 60,00% | 32,71% |
| MobileNetV2 | 88,38% | 19,17% | **8,33%** | 13,75% | 85,62% | 19,38% | 30,83% | 25,10% |
| ResNet18 | 91,04% | 13,89% | 12,22% | 13,06% | 85,49% | 20,21% | **27,50%** | **23,85%** |

Không có một model thắng mọi metric. LBP-SVM có dev ACER/F1 và test APCER
tốt nhất nhưng từ chối nhầm 60% live test. ResNet18 có test ACER tốt nhất nhờ
cân bằng hai loại lỗi hơn. MobileNetV2 chỉ kém ResNet18 1,25 điểm ACER test,
trong khi checkpoint nhỏ hơn đáng kể.

Domain shift dev → test ACER:

| Model | Chênh lệch |
|---|---:|
| LBP-SVM | +21,74 điểm % |
| MobileNetV2 | +11,35 điểm % |
| ResNet18 | +10,80 điểm % |

## Frame so với video

| Model | Test frame ACER | Test video ACER | Thay đổi |
|---|---:|---:|---:|
| LBP-SVM | 30,58% | 32,71% | +2,13 điểm % |
| MobileNetV2 | 25,69% | 25,10% | -0,58 điểm % |
| ResNet18 | 24,03% | 23,85% | -0,18 điểm % |

Mean aggregation giúp hai CNN nhẹ nhưng không bảo đảm luôn tốt hơn: với
LBP-SVM và threshold video chọn trên dev, ACER test xấu hơn frame-level.

## Báo cáo phụ tương thích OULU

Worst-case test ACER với threshold dev-EER:

| Model | Worst-case ACER |
|---|---:|
| LBP-SVM | 33,75% |
| MobileNetV2 | 26,25% |
| ResNet18 | **23,13%** |

Ranking này nhất quán với policy min-ACER chính.

## Chi phí mô hình

| Model | Params | Artifact model | Train time | Pure batch 1 | E2E batch 16 |
|---|---:|---:|---:|---:|---:|
| LBP-SVM | 640 hệ số | 21,7 KB | 0,68 giây selected fit | 0,163 ms | **0,733 ms** |
| MobileNetV2 | 2,23 M | 9,15 MB | 306,50 giây | 3,247 ms | 0,991 ms |
| ResNet18 | 11,18 M | 44,79 MB | 272,51 giây | **1,595 ms** | 0,966 ms |

Pure LBP không gồm trích feature; cột E2E dùng cùng 600 face crop và có trích
LBP. MobileNetV2 là model CNN nhỏ nhất; ResNet18 chạy nhanh hơn trên RTX 3060
ở phép đo này nhưng có checkpoint lớn hơn khoảng 4,9 lần. Chi tiết tại
`docs/benchmark_tai_nguyen_e01_e03.md`.

## Kết luận trong phạm vi baseline

- Chọn ResNet18 nếu ưu tiên ACER tổng thể trên cấu hình GPU đã đo.
- Chọn MobileNetV2 nếu ưu tiên kích thước mà chấp nhận tăng 1,25 điểm ACER.
- LBP-SVM hữu ích làm baseline rất nhỏ và bảo thủ với attack, nhưng BPCER test
  quá cao cho một hệ thống xác thực cân bằng.

Đây là kết quả một seed, head-only transfer learning và không phải tuyên bố
SOTA. Fine-tune backbone, nhiều seed và benchmark CPU/mobile là thí nghiệm phụ,
không được điều chỉnh bằng test hiện có.

## Cập nhật E04 — fine-tune layer4

E04 giữ nguyên ResNet18 pretrained, dữ liệu và evaluator của E03; chỉ mở
`layer4` với LR `1e-5` và head với LR `1e-4`. Cấu hình được khóa trước main run,
test chỉ được dựng sau marker checkpoint/threshold.

| ResNet18 | Dev video ACER | Test video F1 | Test APCER | Test BPCER | Test ACER |
|---|---:|---:|---:|---:|---:|
| E03 head-only | 13,06% | 85,49% | 20,21% | 27,50% | 23,85% |
| E04 layer4 | **2,57%** | **94,29%** | **5,42%** | **24,17%** | **14,79%** |

E04 giảm test ACER 9,06 điểm phần trăm, xác nhận việc thích nghi block cuối có
ý nghĩa. Kết quả vẫn chỉ có một seed và dev–test gap còn 12,22 điểm; không mở
thêm tuning dựa trên test Protocol 1.

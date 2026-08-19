# Benchmark tài nguyên E01–E03

## Thiết lập

- Cùng máy: RTX 3060 12 GB, environment được khóa trong từng run.
- Cùng subset: 600 test video, lấy crop `sample_index=0` của mỗi video.
- End-to-end bắt đầu từ PNG face crop đã preprocess; không gồm decode video
  gốc và face detector.
- Batch 16, 4 worker, warm-up trước khi đo, 3 lần lặp; báo median.
- LBP-SVM chạy CPU với trích LBP đa luồng; hai CNN chạy CUDA.

Subset video ID có SHA-256
`9f675f0e4b9733a002888c6471e046e08f4e85af6bc31c9d5c32b86ad5402c48`.
Kết quả máy đọc được tại
`artifacts/benchmarks/baseline_latency_test600.json`.

## Pure-model latency

| Model | Batch 1 | Batch 16 |
|---|---:|---:|
| LBP-SVM trên feature cache | 0,1633 ms/frame | **0,0113 ms/frame** |
| MobileNetV2 GPU | 3,2472 ms/frame | 0,6475 ms/frame |
| ResNet18 GPU | **1,5946 ms/frame** | 0,5930 ms/frame |

LBP pure-model không gồm trích feature. ResNet18 nhanh hơn MobileNetV2 trên
GPU này dù lớn hơn, do hiệu quả kernel/phần cứng; không suy ra cùng kết quả
trên thiết bị mobile.

## End-to-end từ face crop

| Model | Median 600 frame | Median/frame | Xấp xỉ 10 frame/video |
|---|---:|---:|---:|
| LBP-SVM | 0,4397 s | **0,7329 ms** | 7,33 ms |
| MobileNetV2 | 0,5944 s | 0,9907 ms | 9,91 ms |
| ResNet18 | 0,5794 s | 0,9657 ms | 9,66 ms |

Các giá trị video là phép nhân tuyến tính 10 frame, chưa gồm face detection
và video I/O. Chênh lệch nhỏ ở end-to-end cho thấy đọc/resize ảnh và batching
chiếm phần đáng kể; pure-model latency không đủ để dự đoán toàn pipeline.

## Kích thước và chất lượng

| Model | Model artifact | Test video ACER |
|---|---:|---:|
| LBP-SVM | 21,7 KB | 32,71% |
| MobileNetV2 | 9,15 MB | 25,10% |
| ResNet18 | 44,79 MB | **23,85%** |

MobileNetV2 là điểm cân bằng kích thước/chất lượng tốt: giảm khoảng 4,9 lần
checkpoint so với ResNet18 và chỉ mất 1,25 điểm ACER. ResNet18 phù hợp hơn nếu
ưu tiên ACER trên GPU đã đo; LBP-SVM phù hợp khi kích thước/tính đơn giản quan
trọng hơn lỗi cân bằng.

## Tái lập

~~~bash
PYTHONPATH=src conda run --no-capture-output -n ai_env \
python scripts/benchmark_baselines.py \
  --project-root . \
  --batch-size 16 \
  --workers 4 \
  --repeats 3
~~~

## Cập nhật E04

E04 fine-tune `layer4` không thay đổi inference graph hoặc tổng số tham số so
với E03; chỉ trọng số và training policy thay đổi. Vì vậy benchmark triển khai
chuẩn hóa của ResNet18 vẫn là tham chiếu phù hợp. Trong main run E04, pure
batch-1 latency là 1,759 ms/frame, training 9 epoch mất 216,54 giây và peak
GPU memory là 373.958.144 byte. E03 dùng 272.971.264 byte peak memory.

Training time E04 thấp hơn tổng E03 vì early stopping ở epoch 9 thay vì chạy
15 epoch, không có nghĩa một epoch fine-tune rẻ hơn head-only.

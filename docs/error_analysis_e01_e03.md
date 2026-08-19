# Error analysis ba baseline trên test Protocol 1

Phân tích này chỉ đọc prediction đã khóa; không dùng để đổi model, threshold
hay preprocessing.

## 1. Số lỗi và mức chồng lấp

| Model | Live → spoof (FP/BPCER count) | Spoof → live (FN/APCER count) |
|---|---:|---:|
| LBP-SVM | 72 | 26 |
| MobileNetV2 | 37 | 93 |
| ResNet18 | 33 | 97 |

- 16 live video bị cả ba model từ chối nhầm.
- MobileNetV2 và ResNet18 cùng sai 23/33 FP của ResNet18.
- Chỉ 2 attack video bị cả ba model bỏ lọt; MobileNetV2 và ResNet18 cùng bỏ
  lọt 50 video.
- ResNet18 có 4 FP và 47 FN không xuất hiện đồng thời ở hai model còn lại.

Điều này xác nhận khác biệt chính về operating behavior: LBP-SVM rất bảo thủ
với attack nhưng từ chối nhiều live, còn hai CNN cân bằng hơn nhưng chấp nhận
nhầm nhiều attack hơn.

## 2. ResNet18 theo phone và attack medium

Mọi test video thuộc session 3. Mỗi phone có 20 live và 80 spoof video.

| Phone | FP / 20 live | BPCER | FN / 80 spoof | APCER |
|---:|---:|---:|---:|---:|
| 1 | 7 | 35,00% | 6 | 7,50% |
| 2 | 4 | 20,00% | 15 | 18,75% |
| 3 | 8 | 40,00% | 10 | 12,50% |
| 4 | 5 | 25,00% | 18 | 22,50% |
| 5 | 7 | 35,00% | 25 | 31,25% |
| 6 | 2 | 10,00% | 23 | 28,75% |

Phone 5–6 có APCER cao nhất, trong khi phone 3 có BPCER cao nhất. Đây là dấu
hiệu model còn nhạy với thiết bị capture/presentation, dù Protocol 1 chủ yếu
đánh giá điều kiện môi trường chưa thấy.

Theo attack instrument, số FN ResNet18 trên 120 video/nhóm:

| Instrument | FN | APCER |
|---|---:|---:|
| Printer 1 | 31 | 25,83% |
| Printer 2 | 16 | 13,33% |
| Display 1 | 30 | 25,00% |
| Display 2 | 20 | 16,67% |

## 3. Ca sai với confidence cao

Live bị ResNet18 dự đoán spoof mạnh nhất:

| Video | Phone | Subject | Score | LBP / Mobile / ResNet |
|---|---:|---:|---:|---|
| `6_3_46_1` | 6 | 46 | 0,9774 | live / spoof / spoof |
| `3_3_46_1` | 3 | 46 | 0,9679 | spoof / spoof / spoof |
| `1_3_41_1` | 1 | 41 | 0,9639 | spoof / spoof / spoof |
| `4_3_46_1` | 4 | 46 | 0,9605 | live / spoof / spoof |
| `1_3_46_1` | 1 | 46 | 0,9551 | spoof / spoof / spoof |

Subject 46 xuất hiện trong 4/5 ca, gợi ý subject/appearance-specific failure
cần được xem xét trong phân tích crop/video thủ công sau này.

Attack bị ResNet18 dự đoán live mạnh nhất:

| Video | Type / instrument | Score | LBP / Mobile / ResNet |
|---|---|---:|---|
| `6_3_44_4` | replay / display 1 | 0,0194 | live / live / live |
| `6_3_44_5` | replay / display 2 | 0,0460 | spoof / live / live |
| `4_3_50_4` | replay / display 1 | 0,0880 | spoof / spoof / live |
| `6_3_53_2` | print / printer 1 | 0,1255 | spoof / spoof / live |
| `5_3_44_5` | replay / display 2 | 0,1387 | spoof / live / live |

## 4. Chất lượng crop của các ca đại diện

Cả 10 video trong hai bảng đều có đủ 10/10 crop với status `ok_scaled`.
Detector confidence trung bình nằm trong khoảng 0,938–0,975 và confidence nhỏ
nhất vẫn trên 0,931. Vì vậy các lỗi confidence cao này không có dấu hiệu đến
từ việc detector bỏ mặt; nguyên nhân hợp lý hơn là domain/subject/device và
đặc trưng presentation chưa được head-only model phân tách tốt.

Kết luận này chỉ dựa trên metadata detector, chưa thay thế kiểm tra hình ảnh
thủ công từng video.

## 5. Cập nhật sau ablation E04

E04 fine-tune `layer4` giảm lỗi test video của ResNet18 từ 33 FP / 97 FN xuống
29 FP / 26 FN. APCER print là 7,08%, replay là 3,75%; BPCER là 24,17%. Mức
giảm FN lớn cho thấy layer4 đã thích nghi tốt hơn với cue attack, trong khi
false rejection của live vẫn là nguồn lỗi lớn hơn.

Phân tích này chỉ đọc prediction E04 sau main run. Không dùng các nhóm lỗi để
đổi threshold hoặc mở thêm tuning trên test Protocol 1.

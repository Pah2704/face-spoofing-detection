# Báo cáo thực nghiệm phát hiện giả mạo khuôn mặt trên OULU-NPU

## So sánh baseline, fine-tune ResNet18 và RGB-LBP-SVM trên Protocol 1

**Ngày cập nhật kết quả:** 21/07/2026

**Phạm vi:** OULU-NPU Protocol 1, một seed cố định bằng 42

**Kết quả chính:** trong ba baseline, ResNet18 head-only đạt test video ACER
thấp nhất, 23,85%. Ablation E04 mở `layer4` của ResNet18 giảm ACER còn
14,79%, cho thấy head-only chưa thích nghi đủ với cue giả mạo. Ablation E05
giữ LBP riêng trên R/G/B đạt ACER 14,17%, chủ yếu nhờ BPCER giảm mạnh so với
LBP grayscale.

## Tóm tắt

Báo cáo xây dựng và đánh giá một pipeline phát hiện giả mạo khuôn mặt ở cấp
video trên OULU-NPU Protocol 1. Ba baseline đại diện cho ba mức độ phức tạp
được so sánh trên cùng split, frame và crop khuôn mặt: đặc trưng texture
LBP kết hợp Linear SVM, MobileNetV2 và ResNet18 pretrained ImageNet. Mỗi video
được lấy đều 10 frame; score frame được lấy trung bình để tạo score video.
Siêu tham số, checkpoint và threshold chỉ được chọn trên dev, sau đó khóa
trước khi đánh giá test.

Trên 600 video test, ba baseline lần lượt đạt ACER 32,71%, 25,10% và 23,85%.
LBP-SVM có APCER thấp nhưng từ chối nhầm 60,00% bona-fide video, cho thấy F1
cao không đồng nghĩa với cân bằng lỗi tốt khi dữ liệu lệch lớp. Một ablation
được khóa trước mở riêng `layer4` của ResNet18, giảm test ACER từ 23,85% xuống
14,79% và tăng F1 từ 85,49% lên 94,29%. Mean aggregation không luôn tốt hơn:
với E04, frame ACER 13,41% thấp hơn video ACER 14,79%. Kết quả chỉ phản ánh
một seed; báo cáo không đưa ra tuyên bố state of the art.

Ngày 21/07/2026, E05 được bổ sung với cùng contract E01 nhưng feature
`[LBP(R),LBP(G),LBP(B)]` 1.920D. E05 đạt test video F1 92,51%, APCER 10,00%,
BPCER 18,33% và ACER 14,17%. So với E01, ACER giảm 18,54 điểm nhưng APCER tăng
4,58 điểm; vì vậy màu cải thiện cân bằng lỗi chứ không thắng ở mọi metric.

# Chương 1. Giới thiệu

## 1.1. Bối cảnh và vấn đề nghiên cứu

Hệ thống xác thực khuôn mặt có thể bị đánh lừa bằng ảnh in hoặc video phát lại.
Face anti-spoofing, còn gọi là presentation attack detection, có nhiệm vụ phân
biệt mẫu bona-fide/live với mẫu attack/spoof trước khi kết quả được chuyển đến
hệ nhận dạng. Một mô hình hữu dụng không chỉ cần nhận ra attack mà còn phải
hạn chế từ chối nhầm người dùng thật.

Đề tài tập trung vào câu hỏi thực nghiệm: trong một pipeline chung và điều kiện
đánh giá không rò rỉ test, đặc trưng texture cổ điển và hai CNN pretrained cân
bằng chất lượng, kích thước và tốc độ như thế nào?

## 1.2. Mục tiêu

Ba mục tiêu có thể kiểm chứng là:

1. So sánh ACER và F1 video-level của LBP-SVM, MobileNetV2 và ResNet18.
2. Xác định mean aggregation từ frame sang video có cải thiện kết quả không.
3. Đánh giá trade-off giữa sai số, kích thước model và latency trên cùng máy.
4. Kiểm tra liệu fine-tune `layer4` có khắc phục giới hạn của ResNet18
   head-only hay không.

## 1.3. Phạm vi

Phần chính chỉ sử dụng OULU-NPU Protocol 1, bài toán nhị phân với `live = 0`,
`spoof = 1`, 10 frame/video và seed 42. E04 chỉ là một ablation fine-tune
`layer4` đã đăng ký trước; không mở grid search dựa trên test. Protocol 2–4,
cross-dataset, temporal network, domain adaptation và mô hình FAS chuyên biệt
nằm ngoài phạm vi.

# Chương 2. Cơ sở phương pháp

## 2.1. LBP-SVM

Local Binary Pattern mã hóa quan hệ sáng tối giữa một pixel và các láng giềng,
nhờ đó mô tả texture cục bộ có thể xuất hiện ở ảnh in hoặc màn hình. Baseline
dùng uniform LBP với 8 láng giềng, bán kính 1 trên ảnh xám 128 × 128. Ảnh được
chia grid 8 × 8; histogram 10 bin chuẩn hóa L1 của 64 cell tạo vector 640
chiều. `StandardScaler` và Linear SVM chỉ được fit bằng train.

E05 áp dụng cùng descriptor độc lập trên R, G và B rồi ghép theo thứ tự cố
định, tạo 1.920 chiều. Mọi thành phần SVM/selection/evaluation giữ nguyên E01.

## 2.2. MobileNetV2 và ResNet18

Hai CNN nhận RGB 224 × 224 với ImageNet normalization. MobileNetV2 đại diện
cho kiến trúc gọn nhẹ dùng inverted residual; ResNet18 đại diện cho CNN residual
phổ biến. Cả hai dùng pretrained ImageNet, đóng băng backbone và BatchNorm,
chỉ học một head sinh spoof logit. Thiết kế này giữ phép so sánh baseline đơn
giản và giảm chi phí, nhưng cũng giới hạn khả năng thích nghi với cue giả mạo.
E04 giữ nguyên ResNet18 pretrained nhưng mở `layer4` với learning rate `1e-5`
và head với learning rate `1e-4` để kiểm tra trực tiếp giới hạn này.

## 2.3. Gộp video và chỉ số

Với video có các frame score \(s_1,\ldots,s_K\), score video là:

\[
s_{video}=\frac{1}{K}\sum_{i=1}^{K}s_i.
\]

Quy tắc dự đoán là `score >= threshold` thì spoof. Với spoof là lớp dương:

\[
APCER=\frac{FN}{TP+FN},\qquad
BPCER=\frac{FP}{TN+FP},\qquad
ACER=\frac{APCER+BPCER}{2}.
\]

APCER đo tỷ lệ attack bị chấp nhận là live; BPCER đo tỷ lệ live bị từ chối là
spoof. ACER là metric chính vì cân bằng hai rủi ro, không bị tỷ lệ 80% spoof
chi phối như accuracy hoặc F1.

# Chương 3. Dữ liệu và pipeline

## 3.1. Dữ liệu

Protocol 1 chính thức được giữ nguyên ở cấp video, không chia ngẫu nhiên ở cấp
frame.

| Split | Video | Live | Spoof | Frame dự kiến | Crop hợp lệ |
|---|---:|---:|---:|---:|---:|
| Train | 1.200 | 240 | 960 | 12.000 | 12.000 |
| Dev | 900 | 180 | 720 | 9.000 | 8.999 |
| Test | 600 | 120 | 480 | 6.000 | 6.000 |
| **Tổng** | **2.700** | **540** | **2.160** | **27.000** | **26.999** |

Ngoại lệ duy nhất là frame đầu của dev attack `3_1_28_4__00`, không phát hiện
được mặt. Row này được giữ với trạng thái `no_face`; video vẫn được đánh giá
bằng 9 frame còn lại. Tỷ lệ crop hợp lệ là 99,9963%.

## 3.2. Tiền xử lý chung

Pipeline thực hiện lần lượt:

1. đọc split Protocol 1 và tạo video manifest;
2. lấy đều 10 vị trí từ đầu đến cuối mỗi video;
3. phát hiện khuôn mặt bằng MediaPipe, thêm margin 20% và lưu crop 256 × 256;
4. ghi quan hệ video–frame, trạng thái detector và fingerprint tiền xử lý;
5. tạo đầu vào riêng cho LBP hoặc CNN từ cùng crop;
6. dự đoán frame, mean aggregation và đánh giá video.

Không model nào được dùng crop hoặc frame index riêng. Dữ liệu raw bất biến;
manifest là nguồn xác định split và nhãn.

## 3.3. Cấu hình mô hình

| Thành phần | LBP-SVM | MobileNetV2 | ResNet18 |
|---|---|---|---|
| Input | Gray 128 × 128 | RGB 224 × 224 | RGB 224 × 224 |
| Feature/backbone | Uniform LBP, grid 8 × 8 | ImageNet V2 | ImageNet V1 |
| Phần được train | Scaler + LinearSVC | Head 1.281 params | Head 513 params |
| Loss | Squared hinge | Weighted BCE | Weighted BCE |
| Optimizer | LinearSVC | Adam | Adam |
| LR / weight decay | theo solver | 1e-4 / 1e-4 | 1e-4 / 1e-4 |
| Batch / epoch | không áp dụng | 16 / 15 | 16 / 15 |
| Augmentation | không | flip ngang 0,5 | flip ngang 0,5 |
| Video score | mean decision score | mean probability | mean probability |

LBP-SVM tìm `C` trong `1e-4` đến `10` và chọn `C = 1e-4` trên dev. Hai CNN
dùng `pos_weight = 0,25` để bù tỷ lệ lớp, tối đa 15 epoch, minimum 3 và
patience 3. Best checkpoint của cả hai là epoch 15.

E04 giữ toàn bộ cấu hình E03, chỉ mở `layer4` và BatchNorm thuộc layer4. Có
8.394.241 tham số trainable; early stopping chọn epoch 6 và dừng ở epoch 9.

# Chương 4. Thiết kế thực nghiệm và tái lập

## 4.1. Nguyên tắc chống leakage

- Tất cả frame của một video thuộc cùng split chính thức.
- Scaler, SVM và CNN chỉ fit trên train.
- `C`, checkpoint và threshold được chọn bằng dev video ACER.
- Marker khóa checkpoint/threshold được ghi trước khi dựng test dataset CNN.
- Test chỉ được suy luận một lần trong main run và không được dùng để tune.
- Score luôn hướng về spoof; cùng evaluator được dùng cho cả ba model.

Threshold chính tối thiểu hóa tuple `(ACER, APCER, threshold)` trên mọi operating
point của dev. Evaluator phụ tái tạo chính sách dev-EER và worst-case ACER từ
script baseline OULU để kiểm tra chéo.

## 4.2. Artifact và kiểm chứng

Mỗi main run lưu config resolved, môi trường, source snapshot, checkpoint,
threshold, prediction từng frame/video, metric, figure và SHA-256 manifest.
E01 được chạy lại và tái tạo model/prediction/metric chính; E02, E03 và E04
đều có hai smoke run cho checkpoint, prediction và metric giống byte-for-byte
ở các artifact ổn định.

Evaluator và pipeline có 106 unit test. Thuật toán quét threshold hiện có độ phức tạp
\(O(n\log n)\); kết quả được so sánh với exhaustive reference trên dữ liệu có
tie và với sáu artifact dev frame/video thật. Mọi trường metric và threshold
khớp chính xác; 8.999 frame được xử lý trong khoảng 33–34 ms trên máy hiện tại.

## 4.3. Thiết lập benchmark

Benchmark dùng cùng 600 test crop ở `sample_index = 0`, batch 16, 4 worker,
warm-up và median của 3 lần lặp. CNN chạy trên RTX 3060 12 GB; LBP-SVM chạy
CPU đa luồng. End-to-end được tính từ PNG face crop, không gồm decode video
gốc và face detector.

# Chương 5. Kết quả và thảo luận

## 5.1. Kết quả ba baseline ở video-level

Threshold của từng model được chọn độc lập trên dev; các giá trị sau biểu diễn
theo phần trăm.

| Model | Split | Accuracy | Precision | Recall | F1 | APCER | BPCER | ACER |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| LBP-SVM | Dev | 89,11 | 96,98 | 89,17 | **92,91** | **10,83** | 11,11 | **10,97** |
| MobileNetV2 | Dev | 83,00 | 97,49 | 80,83 | 88,38 | 19,17 | **8,33** | 13,75 |
| ResNet18 | Dev | 86,44 | 96,57 | 86,11 | 91,04 | 13,89 | 12,22 | 13,06 |
| RGB-LBP-SVM E05 | Dev | 96,67 | 99,57 | 96,25 | 97,88 | 3,75 | 1,67 | **2,71** |
| LBP-SVM | Test | 83,67 | 86,31 | **94,58** | **90,26** | **5,42** | 60,00 | 32,71 |
| MobileNetV2 | Test | 78,33 | 91,27 | 80,63 | 85,62 | 19,38 | 30,83 | 25,10 |
| ResNet18 | Test | 78,33 | **92,07** | 79,79 | 85,49 | 20,21 | **27,50** | **23,85** |
| RGB-LBP-SVM E05 | Test | 88,33 | 95,15 | 90,00 | 92,51 | 10,00 | **18,33** | **14,17** |

Confusion matrix ở test video-level:

| Model | TN | FP | FN | TP |
|---|---:|---:|---:|---:|
| LBP-SVM | 48 | 72 | 26 | 454 |
| MobileNetV2 | 83 | 37 | 93 | 387 |
| ResNet18 | 87 | 33 | 97 | 383 |
| RGB-LBP-SVM E05 | 98 | 22 | 48 | 432 |

Không model nào tốt nhất ở mọi metric. LBP-SVM nhận ra attack mạnh nhưng tạo
72 false positive trên chỉ 120 live video. Do spoof chiếm 80% test, model vẫn
có F1 90,26%; đây là minh họa vì sao kết luận chỉ từ F1 sẽ gây hiểu nhầm.
ResNet18 có ACER thấp nhất nhờ giảm BPCER xuống 27,50%, dù APCER hơi cao hơn
MobileNetV2.

## 5.2. Ablation E04: head-only so với fine-tune layer4

| ResNet18 | Trainable params | Dev ACER | Test F1 | Test APCER | Test BPCER | Test ACER |
|---|---:|---:|---:|---:|---:|---:|
| E03 head-only | 513 | 13,06% | 85,49% | 20,21% | 27,50% | 23,85% |
| E04 layer4 + head | 8.394.241 | **2,57%** | **94,29%** | **5,42%** | **24,17%** | **14,79%** |

E04 giảm test ACER 9,06 điểm phần trăm và tăng F1 8,80 điểm. APCER giảm mạnh
14,79 điểm trong khi BPCER giảm 3,33 điểm. Kết quả ủng hộ giả thuyết rằng head
tuyến tính trên đặc trưng ImageNet đóng băng chưa đủ cho cue presentation
attack. Cấu hình E04 đã được khóa trước main run và test chỉ được dựng sau
marker checkpoint/threshold; không có vòng tune tiếp theo từ kết quả này.

## 5.2.1. Ablation E05: grayscale LBP so với RGB-LBP

| Test video | E01 Gray-LBP | E05 RGB-LBP | E05 − E01 |
|---|---:|---:|---:|
| F1 | 90,26% | **92,51%** | +2,25 điểm % |
| APCER | **5,42%** | 10,00% | +4,58 điểm % |
| BPCER | 60,00% | **18,33%** | -41,67 điểm % |
| ACER | 32,71% | **14,17%** | -18,54 điểm % |

E05 giảm false positive từ 72 xuống 22 nhưng tăng false negative từ 26 lên
48. Thông tin màu sửa operating point mất cân bằng của E01; không được diễn
giải là tăng đồng thời an ninh và tiện dụng ở mọi ngưỡng.

## 5.3. Domain shift dev sang test

| Model | Dev ACER | Test ACER | Tăng tuyệt đối |
|---|---:|---:|---:|
| LBP-SVM | 10,97% | 32,71% | +21,74 điểm % |
| MobileNetV2 | 13,75% | 25,10% | +11,35 điểm % |
| ResNet18 | 13,06% | 23,85% | +10,80 điểm % |
| ResNet18 E04 | 2,57% | 14,79% | +12,22 điểm % |
| RGB-LBP-SVM E05 | 2,71% | 14,17% | +11,46 điểm % |

LBP-SVM đứng đầu trên dev nhưng cuối trên test, cho thấy texture thủ công nhạy
với thay đổi điều kiện môi trường/session. Hai CNN cũng suy giảm đáng kể; vì
backbone bị đóng băng, head tuyến tính chưa học được biểu diễn chuyên biệt đủ
mạnh cho domain test. E04 cải thiện tuyệt đối lớn nhưng khoảng cách dev–test
vẫn còn 12,22 điểm, nên fine-tuning chưa giải quyết domain shift.

## 5.4. Frame-level và video-level

| Model | Test frame ACER | Test video ACER | Thay đổi |
|---|---:|---:|---:|
| LBP-SVM | 30,58% | 32,71% | +2,13 điểm % |
| MobileNetV2 | 25,69% | 25,10% | -0,58 điểm % |
| ResNet18 | 24,03% | 23,85% | -0,18 điểm % |
| ResNet18 E04 | **13,41%** | 14,79% | +1,39 điểm % |
| RGB-LBP-SVM E05 | 16,28% | **14,17%** | -2,11 điểm % |

Mean aggregation làm mượt hai CNN nhưng mức cải thiện nhỏ. Nó không bảo đảm
tốt hơn: score LBP mang bias có hệ thống trên live test nên trung bình nhiều
frame không loại được bias, và threshold video chọn trên dev còn làm ACER test
tăng. Vì vậy câu hỏi thứ hai chỉ được trả lời có điều kiện, không phải khẳng
định video-level luôn ổn định hơn. E04 làm rõ thêm điểm này: aggregation giảm
APCER nhưng tăng BPCER đủ nhiều để ACER video cao hơn frame.

## 5.5. Báo cáo phụ tương thích OULU

Với threshold dev-EER và worst-case giữa print/replay:

| Model | Test worst-case ACER |
|---|---:|
| LBP-SVM | 33,75% |
| MobileNetV2 | 26,25% |
| ResNet18 | 23,13% |
| ResNet18 E04 | **11,46%** |
| RGB-LBP-SVM E05 | 16,04% |

Ba baseline E01–E03 giữ thứ hạng và E04/E05 đều tốt hơn E01 rõ rệt, nhưng
E04/E05 đổi vị trí ở policy phụ. Chênh lệch nhỏ giữa hai model tốt nhất vì thế
không bền trước quy tắc threshold/attack aggregation.

## 5.6. Chi phí và trade-off triển khai

| Model | Tổng params / hệ số | Model artifact | Train time | Pure batch 1 | E2E batch 16 |
|---|---:|---:|---:|---:|---:|
| LBP-SVM | 640 hệ số | 21,7 KB | 0,68 s selected fit | 0,163 ms | **0,733 ms/frame** |
| MobileNetV2 | 2,23 M | 9,15 MB | 306,50 s | 3,247 ms | 0,991 ms/frame |
| ResNet18 | 11,18 M | 44,79 MB | 272,51 s | **1,595 ms** | 0,966 ms/frame |

Pure LBP chỉ đo SVM trên feature cache; E2E có tính trích LBP. ResNet18 nhanh
hơn MobileNetV2 trên RTX 3060 ở phép đo này dù lớn hơn, phản ánh hiệu quả
kernel/phần cứng chứ không chứng minh ưu thế trên CPU/mobile. MobileNetV2 là
điểm cân bằng kích thước–chất lượng rõ nhất: checkpoint nhỏ hơn ResNet18 khoảng
4,9 lần và chỉ kém 1,25 điểm ACER test.

E04 không thay đổi inference graph hay tổng số tham số ResNet18. Nó tăng số
tham số trainable từ 513 lên 8.394.241 và peak GPU memory từ 273,0 MB lên
374,0 MB. Run dừng ở epoch 9, mất 216,54 giây huấn luyện; con số thấp hơn E03
do early stopping sớm hơn, không có nghĩa mỗi epoch fine-tune rẻ hơn.

E05 có 1.920 hệ số, model 62.653 byte, feature cache nén 62,14 MB và mất 73,00
giây để trích đủ 26.999 frame. Selected fit mất 2,82 giây. Chưa có benchmark
E2E chuẩn hóa nên không đặt decision time từ feature cache cạnh latency E01–E03.

## 5.7. Phân tích lỗi

Ba model cùng sai 16 live video nhưng chỉ cùng bỏ lọt 2 attack video. Hai CNN
cùng sai 23 false positive và 50 false negative, cho thấy chúng chia sẻ một
phần failure mode từ biểu diễn ImageNet/head-only.

Với ResNet18, APCER cao nhất ở phone 5 và 6, lần lượt 31,25% và 28,75%; BPCER
cao nhất ở phone 3, 40,00%. Attack qua `printer 1` và `display 1` có APCER
25,83% và 25,00%, cao hơn hai instrument còn lại. Subject 46 xuất hiện ở 4/5
live video bị dự đoán spoof với confidence cao nhất.

Mười video lỗi đại diện đều có đủ 10 crop, detector status `ok_scaled` và
confidence trung bình 0,938–0,975. Metadata không cho thấy lỗi phát hiện mặt
rõ ràng; giả thuyết hợp lý hơn là model nhạy với subject, thiết bị và cue trình
diễn. Đây vẫn là suy luận từ metadata, chưa thay thế kiểm tra hình ảnh thủ công.

E04 giảm false negative test từ 97 xuống 26 và false positive từ 33 xuống 29.
Ở policy min-ACER, print APCER là 7,08% và replay APCER là 3,75%; cải thiện
không chỉ tập trung vào một loại attack.

## 5.8. Hạn chế

- Chỉ có một seed nên chưa ước lượng được độ biến thiên thống kê.
- Chỉ Protocol 1; chưa kiểm tra thay đổi camera, attack medium và cross-dataset
  đầy đủ như Protocol 2–4.
- Ba baseline CNN chỉ train head; E04 mới fine-tune một stage của ResNet18 và
  chưa đánh giá kiến trúc/loss FAS chuyên biệt.
- Mean score bỏ qua thông tin chuyển động và quan hệ thời gian.
- Benchmark CNN dùng một GPU desktop; chưa có CPU, edge hay điện thoại thật.
- Pipeline latency chưa gồm decode video và face detection.
- Phân tích lỗi chưa kiểm tra thủ công toàn bộ video và không được dùng để
  điều chỉnh lại test hiện tại.

# Chương 6. Kết luận và hướng phát triển

## 6.1. Kết luận

Trong ba baseline đã khóa, ResNet18 head-only là lựa chọn tốt nhất nếu ưu tiên
ACER tổng thể; MobileNetV2 phù hợp hơn khi kích thước model là ràng buộc chính.
LBP-SVM rất nhỏ nhưng BPCER 60% khiến nó không phù hợp làm hệ xác thực cân
bằng. E04 đạt ACER 14,79% và chứng minh việc thích nghi layer4 có ý nghĩa hơn
chỉ học head. E05 đạt ACER thấp nhất 14,17% nhờ giữ texture màu, nhưng E04 vẫn
có F1/APCER tốt hơn; không có model thắng mọi tiêu chí.

Các câu hỏi nghiên cứu được trả lời như sau:

1. ResNet18 có test video ACER tốt nhất; LBP-SVM có F1 cao nhất nhưng lỗi mất
   cân bằng nghiêm trọng.
2. Video aggregation cải thiện nhẹ hai CNN, nhưng không cải thiện LBP-SVM.
3. MobileNetV2 cho trade-off kích thước–chất lượng tốt nhất; ResNet18 cho chất
   lượng tốt nhất trong môi trường GPU hiện tại.
4. Fine-tune layer4 cải thiện rõ ResNet18 head-only, nhưng chưa loại bỏ domain
   shift và không làm video aggregation luôn tốt hơn.
5. RGB-LBP giảm ACER E01 18,54 điểm chủ yếu nhờ giảm BPCER; APCER tăng nên cần
   chọn operating point theo rủi ro ứng dụng.

## 6.2. Hướng phát triển ưu tiên

1. Chạy tối thiểu ba seed và báo trung bình, độ lệch chuẩn hoặc khoảng tin cậy.
2. Mở Protocol 2–4 bằng evaluator chính thức, không dùng lại test Protocol 1
   để chọn cấu hình.
3. Đánh giá temporal pooling hoặc consistency giữa frame.
4. Benchmark pipeline đầy đủ trên CPU và thiết bị edge/mobile mục tiêu.
5. Kiểm tra thủ công các nhóm lỗi theo subject, phone và attack instrument;
   sau đó thiết kế thí nghiệm mới trên dev hoặc protocol khác.

## Phụ lục. Đầu ra và lệnh tái lập

Các báo cáo chi tiết:

- `docs/ket_qua_e01_lbp_svm.md`
- `docs/ket_qua_e02_mobilenet_v2.md`
- `docs/ket_qua_e03_resnet18.md`
- `docs/ket_qua_e04_resnet18_finetune_layer4.md`
- `docs/ket_qua_e05_rgb_lbp_svm.md`
- `docs/ket_qua_tong_hop_e01_e03.md`
- `docs/error_analysis_e01_e03.md`
- `docs/benchmark_tai_nguyen_e01_e03.md`

Ba baseline chính và ablation E04:

- `artifacts/runs/lbp_svm/e01_20260712_lbp_svm_seed42_verified/`
- `artifacts/runs/mobilenet_v2/e02_20260712_mobilenet_v2_seed42/`
- `artifacts/runs/resnet18/e03_20260713_resnet18_seed42/`
- `artifacts/runs/resnet18_finetune/e04_20260714_resnet18_finetune_layer4_seed42/`
- `artifacts/runs/rgb_lbp_svm/e05_20260721_rgb_lbp_svm_seed42/`

Chuỗi lệnh chuẩn bị dữ liệu và huấn luyện từng baseline nằm trong `README.md`
và báo cáo riêng tương ứng. Chạy kiểm thử bằng:

~~~bash
PYTHONPATH=src conda run --no-capture-output -n ai_env \
python -m unittest discover -s tests -p "test_*.py" -v
~~~

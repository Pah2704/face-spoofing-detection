# Đề cương chi tiết đề tài

# So sánh LBP-SVM, ResNet18 và MobileNetV2 cho bài toán phát hiện giả mạo khuôn mặt trên OULU-NPU

**Tên tiếng Anh đề xuất:**  
**A Comparative Study of LBP-SVM, ResNet18, and MobileNetV2 for Face Spoofing Detection on OULU-NPU**

---

## 1. Định vị đề tài

Đề tài thuộc hướng **phát hiện giả mạo khuôn mặt** (*Face Spoofing Detection / Face Anti-Spoofing / Face Presentation Attack Detection*) trong hệ thống xác thực sinh trắc học.

Bài toán không tập trung vào việc xác định **người trong ảnh là ai** như nhận dạng khuôn mặt thông thường, mà tập trung vào câu hỏi:

> Mẫu khuôn mặt đầu vào là khuôn mặt thật của người đang hiện diện, hay là mẫu giả mạo như ảnh in, video phát lại hoặc màn hình điện thoại/máy tính?

Trong hệ thống xác thực khuôn mặt, module phát hiện giả mạo nên được đặt **trước** bước nhận dạng danh tính:

```text
Video/Image
    ↓
Face Detection / Face Cropping
    ↓
Face Spoofing Detection
    ↓
Nếu Live → Face Recognition / Verification
Nếu Spoof → Reject
```

Như vậy, đề tài không thay thế hệ nhận dạng khuôn mặt, mà bổ sung một lớp kiểm tra an toàn ở đầu vào nhằm giảm nguy cơ hệ thống bị đánh lừa bởi ảnh hoặc video giả.

---

## 2. Lý do chọn đề tài

Xác thực khuôn mặt ngày càng phổ biến vì thuận tiện, không cần tiếp xúc và có thể triển khai trên điện thoại, máy tính xách tay hoặc camera giám sát. Tuy nhiên, hệ thống xác thực khuôn mặt có thể bị tấn công bằng các phương tiện đơn giản như:

- Ảnh in khuôn mặt.
- Ảnh khuôn mặt hiển thị trên màn hình.
- Video phát lại trên điện thoại hoặc máy tính bảng.
- Các hình thức giả mạo nâng cao hơn như mặt nạ 3D hoặc deepfake.

Trong phạm vi báo cáo này, đề tài tập trung vào các dạng tấn công thường gặp trong bộ dữ liệu OULU-NPU, chủ yếu là **print attack** và **replay attack**.

Với giới hạn thời gian và phần cứng, đề tài không đặt mục tiêu đề xuất mô hình SOTA mới. Thay vào đó, đề tài thực hiện một so sánh thực nghiệm có kiểm soát giữa:

1. **LBP-SVM** – phương pháp truyền thống dựa trên đặc trưng texture.
2. **ResNet18** – mô hình CNN phổ biến, đại diện cho hướng học sâu tiêu chuẩn.
3. **MobileNetV2** – mô hình CNN nhẹ, phù hợp với bối cảnh thiết bị di động và phần cứng hạn chế.

---

## 3. Phạm vi đề tài

### 3.1. Phạm vi chính

| Thành phần | Chốt thực hiện |
|---|---|
| Dataset | OULU-NPU |
| Protocol | Ưu tiên Protocol 1 |
| Bài toán | Binary classification: Live / Spoof |
| Dữ liệu đầu vào | Video, trích frame |
| Mô hình | LBP-SVM, ResNet18, MobileNetV2 |
| Cách đánh giá | Frame-level và video-level |
| Cách gộp video | Mean probability / Mean score |
| Metric chính | ACER, F1-score |
| Metric phụ | Accuracy, Precision, Recall, APCER, BPCER, Confusion matrix |

### 3.2. Không thực hiện trong phần chính

Các nội dung sau **không đưa vào phần chính** để tránh quá tải:

| Nội dung | Lý do |
|---|---|
| Replay-Attack | Chỉ dùng làm hướng mở rộng hoặc so sánh trong tương lai |
| Cross-dataset evaluation | Cần thêm dataset và thời gian xử lý |
| Few-shot / Meta-learning | Phức tạp, không phù hợp phạm vi báo cáo hiện tại |
| Attention pooling | Có thể để phần mở rộng nếu pipeline chính ổn định |
| CDCN / CDCN++ | Chỉ dùng làm SOTA tham chiếu trong related work |
| OULU-NPU Protocol 2–4 | Chỉ làm nếu còn thời gian sau khi hoàn tất Protocol 1 |

---

## 4. Mục tiêu nghiên cứu

### 4.1. Mục tiêu tổng quát

Đánh giá và so sánh hiệu quả của ba phương pháp **LBP-SVM, ResNet18 và MobileNetV2** trong bài toán phát hiện giả mạo khuôn mặt trên bộ dữ liệu **OULU-NPU**, từ đó phân tích sự đánh đổi giữa độ chính xác, độ ổn định và chi phí tính toán.

### 4.2. Mục tiêu cụ thể

1. Xây dựng pipeline xử lý video cho bài toán phát hiện giả mạo khuôn mặt.
2. Trích frame từ video và chuẩn hóa vùng khuôn mặt.
3. Cài đặt baseline truyền thống **LBP-SVM**.
4. Fine-tune hoặc huấn luyện nhẹ hai mô hình học sâu **ResNet18** và **MobileNetV2**.
5. Đánh giá kết quả ở cả mức frame và mức video.
6. So sánh các mô hình dựa trên các chỉ số Accuracy, F1-score, APCER, BPCER và ACER.
7. Phân tích mô hình nào phù hợp hơn trong điều kiện phần cứng hạn chế.

---

## 5. Câu hỏi nghiên cứu

### 5.1. Câu hỏi chính

> Trong bài toán phát hiện giả mạo khuôn mặt trên OULU-NPU, các phương pháp LBP-SVM, ResNet18 và MobileNetV2 khác nhau như thế nào về hiệu quả phát hiện, độ ổn định ở mức video và chi phí tính toán?

### 5.2. Câu hỏi phụ

1. **LBP-SVM** có còn là baseline hợp lý cho bài toán phát hiện giả mạo khuôn mặt không?
2. **ResNet18** có cải thiện rõ rệt so với LBP-SVM trong cùng điều kiện dữ liệu không?
3. **MobileNetV2** có đạt hiệu quả gần ResNet18 nhưng nhẹ hơn về chi phí tính toán không?
4. Việc gộp kết quả nhiều frame thành kết quả video-level có làm mô hình ổn định hơn không?
5. Với giới hạn phần cứng, mô hình nào là lựa chọn cân bằng nhất giữa hiệu quả và khả năng triển khai?

---

## 6. Cơ sở lý thuyết cần trình bày

### 6.1. Hệ sinh trắc học

Một hệ sinh trắc học thường gồm các bước:

```text
Sensor / Data Acquisition
    ↓
Quality Assessment
    ↓
Feature Extraction
    ↓
Matching / Classification
    ↓
Decision
```

Trong xác thực khuôn mặt, dữ liệu đầu vào là ảnh hoặc video khuôn mặt. Hệ thống sẽ phát hiện khuôn mặt, trích đặc trưng và so khớp với mẫu đã đăng ký.

Tuy nhiên, pipeline truyền thống thường giả định rằng mẫu đầu vào là mẫu thật. Đây là điểm yếu khiến hệ thống có thể bị tấn công bằng ảnh hoặc video giả.

### 6.2. Face recognition và face spoofing detection

Cần phân biệt rõ:

| Bài toán | Câu hỏi cần trả lời |
|---|---|
| Face verification | Có đúng là người A không? |
| Face identification | Người này là ai trong cơ sở dữ liệu? |
| Face spoofing detection | Mẫu khuôn mặt này là thật hay giả? |

Đề tài này thuộc bài toán thứ ba: **Face spoofing detection**.

### 6.3. Presentation attack / Spoofing attack

**Presentation attack** là tấn công bằng cách đưa một mẫu sinh trắc giả vào cảm biến nhằm đánh lừa hệ thống.

Trong bài toán khuôn mặt, các dạng tấn công phổ biến gồm:

| Kiểu tấn công | Mô tả |
|---|---|
| Print attack | Dùng ảnh in của khuôn mặt |
| Replay attack | Phát video khuôn mặt trên điện thoại/máy tính bảng |
| Display attack | Hiển thị ảnh khuôn mặt trên màn hình |
| Mask attack | Dùng mặt nạ 3D, không nằm trong phạm vi chính của đề tài |

### 6.4. Đặc trưng texture và LBP

**Local Binary Pattern (LBP)** là đặc trưng mô tả texture cục bộ của ảnh. LBP thường được dùng trong face anti-spoofing vì ảnh in hoặc màn hình phát lại có thể tạo ra các dấu hiệu texture khác với da thật, ví dụ:

- Vân giấy.
- Nhiễu in.
- Moiré pattern.
- Phản chiếu màn hình.
- Bề mặt phẳng, thiếu chiều sâu tự nhiên.

Trong đề tài, LBP được dùng làm **baseline truyền thống**.

### 6.5. SVM

**Support Vector Machine (SVM)** là bộ phân loại truyền thống, thường dùng tốt với vector đặc trưng thủ công như LBP histogram.

Trong đề tài:

```text
Frame khuôn mặt
    ↓
LBP feature
    ↓
Histogram vector
    ↓
SVM classifier
    ↓
Live / Spoof score
```

### 6.6. ResNet18

**ResNet18** là mô hình CNN có skip connection, giúp huấn luyện mạng sâu ổn định hơn. Trong đề tài, ResNet18 được dùng như một baseline học sâu tiêu chuẩn.

Cách dùng đề xuất:

- Dùng trọng số pretrained ImageNet.
- Thay fully connected layer cuối thành 2 lớp: live/spoof.
- Giai đoạn đầu: freeze backbone, chỉ train classifier head.
- Nếu còn thời gian: unfreeze layer cuối để fine-tune nhẹ.

### 6.7. MobileNetV2

**MobileNetV2** là mô hình CNN nhẹ, được thiết kế cho thiết bị di động và môi trường tài nguyên hạn chế. Mô hình dùng inverted residual block và depthwise separable convolution để giảm số tham số và chi phí tính toán.

Trong đề tài, MobileNetV2 được dùng để kiểm tra giả thuyết:

> Một mô hình nhẹ có thể đạt hiệu quả chấp nhận được trong bài toán phát hiện giả mạo khuôn mặt, đồng thời phù hợp hơn với triển khai thực tế trên thiết bị hạn chế tài nguyên.

---

## 7. Dataset: OULU-NPU

### 7.1. Lý do chọn OULU-NPU

OULU-NPU là một bộ dữ liệu phổ biến cho bài toán **face presentation attack detection** trong bối cảnh xác thực khuôn mặt trên thiết bị di động.

Lý do chọn:

1. Có video thật và video tấn công.
2. Có các dạng tấn công phổ biến như print attack và replay attack.
3. Phù hợp với bối cảnh mobile authentication.
4. Có protocol đánh giá rõ ràng.
5. Đủ hiện đại và có giá trị hơn so với các bộ dữ liệu quá đơn giản.

### 7.2. Phạm vi sử dụng dataset

Đề tài ưu tiên sử dụng:

```text
OULU-NPU Protocol 1
```

Lý do:

- Vừa sức với thời gian và phần cứng.
- Vẫn đủ để đánh giá mô hình trong điều kiện có biến thiên môi trường.
- Tránh quá tải khi phải chạy toàn bộ 4 protocol.

### 7.3. Nhãn dữ liệu

Dữ liệu được quy về hai lớp:

| Nhãn | Ý nghĩa |
|---|---|
| Live / Bonafide | Khuôn mặt thật |
| Spoof / Attack | Mẫu giả mạo |

### 7.4. Đơn vị đánh giá

Vì dữ liệu là video, đề tài đánh giá ở hai mức:

| Mức đánh giá | Ý nghĩa |
|---|---|
| Frame-level | Dự đoán từng frame riêng lẻ |
| Video-level | Gộp dự đoán của nhiều frame để đưa ra quyết định cho cả video |

Video-level là kết quả chính cần báo cáo.

---

## 8. Pipeline phương pháp

### 8.1. Pipeline tổng quát

```text
OULU-NPU video
    ↓
Frame extraction
    ↓
Face detection / crop
    ↓
Resize / normalization
    ↓
Model inference
    ↓
Frame-level prediction
    ↓
Mean probability aggregation
    ↓
Video-level prediction
    ↓
Evaluation
```

### 8.2. Trích frame

Do giới hạn phần cứng, không xử lý toàn bộ frame trong mỗi video. Đề xuất:

| Cấu hình | Mục đích |
|---|---|
| 5 frame/video | Cấu hình nhẹ, chạy nhanh |
| 10 frame/video | Cấu hình chính, cân bằng |
| 20 frame/video | Chỉ dùng nếu phần cứng cho phép |

Cấu hình khuyến nghị:

```text
10 frames/video
```

Cách lấy frame:

- Lấy đều theo thời gian từ đầu đến cuối video.
- Không lấy ngẫu nhiên nếu muốn tái lập kết quả.
- Loại frame quá mờ hoặc không phát hiện được khuôn mặt nếu cần.

### 8.3. Phát hiện và crop khuôn mặt

Có thể dùng một trong các công cụ:

| Công cụ | Ghi chú |
|---|---|
| OpenCV Haar Cascade | Nhẹ, dễ dùng, nhưng có thể crop kém |
| MTCNN | Chính xác hơn, hơi nặng hơn |
| RetinaFace | Tốt hơn, nhưng có thể quá nặng |
| MediaPipe Face Detection | Cân bằng, dễ dùng |

Khuyến nghị thực tế:

```text
MediaPipe Face Detection hoặc MTCNN
```

Sau khi phát hiện:

1. Lấy bounding box khuôn mặt.
2. Mở rộng bounding box thêm một biên nhỏ nếu cần.
3. Crop vùng mặt.
4. Resize về kích thước chuẩn.

### 8.4. Resize và normalization

| Mô hình | Kích thước đầu vào |
|---|---|
| LBP-SVM | 128×128 hoặc 224×224 |
| ResNet18 | 224×224 |
| MobileNetV2 | 224×224 |

Với CNN pretrained ImageNet, cần normalize theo mean/std của ImageNet.

---

## 9. Phương pháp 1: LBP-SVM

### 9.1. Vai trò

LBP-SVM là baseline truyền thống đại diện cho hướng **handcrafted feature + classical classifier**.

### 9.2. Pipeline

```text
Cropped face frame
    ↓
Convert to grayscale
    ↓
Extract LBP feature
    ↓
Compute LBP histogram
    ↓
Train SVM
    ↓
Predict live/spoof score
```

### 9.3. Cấu hình đề xuất

| Thành phần | Giá trị đề xuất |
|---|---|
| Ảnh đầu vào | Grayscale |
| Resize | 128×128 |
| LBP radius | 1 hoặc 2 |
| LBP points | 8 hoặc 16 |
| Histogram | Chuẩn hóa L1 hoặc L2 |
| Classifier | SVM |
| Kernel | Linear trước, RBF nếu còn thời gian |
| Chọn tham số | Dựa trên development set |

### 9.4. Ưu điểm

- Chạy nhanh.
- Không cần GPU.
- Dễ giải thích.
- Phù hợp làm baseline.

### 9.5. Hạn chế

- Phụ thuộc nhiều vào texture.
- Có thể kém khi điều kiện ánh sáng thay đổi.
- Khó học đặc trưng phức tạp như CNN.

---

## 10. Phương pháp 2: ResNet18

### 10.1. Vai trò

ResNet18 là baseline học sâu tiêu chuẩn, dùng để kiểm tra hiệu quả của CNN so với đặc trưng thủ công.

### 10.2. Pipeline

```text
Cropped face frame
    ↓
Resize 224×224
    ↓
ImageNet normalization
    ↓
ResNet18 backbone
    ↓
Classifier head
    ↓
Live/spoof probability
```

### 10.3. Cấu hình huấn luyện đề xuất

| Thành phần | Giá trị đề xuất |
|---|---|
| Pretrained | ImageNet |
| Input size | 224×224 |
| Output | 2 classes |
| Loss | Cross-Entropy Loss |
| Optimizer | Adam hoặc SGD |
| Batch size | 8 hoặc 16 |
| Epoch | 5–15 |
| Learning rate | 1e-4 cho head, 1e-5 nếu fine-tune |
| Strategy | Freeze backbone trước, fine-tune layer cuối nếu còn thời gian |

### 10.4. Ưu điểm

- Mạnh hơn LBP-SVM.
- Dễ triển khai bằng PyTorch.
- Là baseline CNN phổ biến.

### 10.5. Hạn chế

- Tốn tài nguyên hơn LBP-SVM.
- Có thể overfit nếu train ít dữ liệu hoặc chọn frame chưa tốt.
- Chưa tối ưu riêng cho face anti-spoofing như CDCN++.

---

## 11. Phương pháp 3: MobileNetV2

### 11.1. Vai trò

MobileNetV2 là mô hình học sâu nhẹ, phù hợp với bối cảnh mobile và phần cứng hạn chế.

### 11.2. Pipeline

```text
Cropped face frame
    ↓
Resize 224×224
    ↓
ImageNet normalization
    ↓
MobileNetV2 backbone
    ↓
Classifier head
    ↓
Live/spoof probability
```

### 11.3. Cấu hình huấn luyện đề xuất

| Thành phần | Giá trị đề xuất |
|---|---|
| Pretrained | ImageNet |
| Input size | 224×224 |
| Output | 2 classes |
| Loss | Cross-Entropy Loss |
| Optimizer | Adam |
| Batch size | 8 hoặc 16 |
| Epoch | 5–15 |
| Learning rate | 1e-4 |
| Strategy | Freeze backbone trước, fine-tune block cuối nếu còn thời gian |

### 11.4. Ưu điểm

- Nhẹ hơn ResNet18.
- Phù hợp với thiết bị hạn chế tài nguyên.
- Cân bằng tốt giữa tốc độ và hiệu quả.

### 11.5. Hạn chế

- Có thể kém ResNet18 nếu dữ liệu đủ lớn và phần cứng đủ mạnh.
- Nếu chỉ train head, khả năng thích nghi với domain face spoofing có thể chưa cao.

---

## 12. Gộp kết quả frame thành video

### 12.1. Lý do cần video-level evaluation

OULU-NPU là video dataset. Nếu chỉ đánh giá từng frame riêng lẻ, kết quả có thể thiếu ổn định vì:

- Một số frame bị mờ.
- Mặt bị lệch.
- Ánh sáng thay đổi.
- Frame không chứa dấu hiệu spoof rõ ràng.

Do đó, kết quả chính nên báo cáo ở mức video.

### 12.2. Mean probability aggregation

Với mỗi video có `T` frame, mô hình dự đoán xác suất spoof cho từng frame:

```text
p1, p2, ..., pT
```

Video score được tính:

```text
p_video = mean(p1, p2, ..., pT)
```

Quyết định:

```text
Nếu p_video >= threshold → Spoof
Nếu p_video < threshold → Live
```

Threshold có thể chọn:

- Mặc định 0.5.
- Hoặc chọn trên development set để tối ưu ACER.

### 12.3. Với LBP-SVM

Nếu SVM có hỗ trợ probability:

```text
p_video = mean(probability scores)
```

Nếu không dùng probability:

```text
score_video = mean(decision scores)
```

Sau đó chọn threshold trên development set.

---

## 13. Chỉ số đánh giá

### 13.1. Quy ước lớp dương

Khuyến nghị thống nhất:

```text
Positive class = Spoof / Attack
Negative class = Live / Bonafide
```

### 13.2. Accuracy

```text
Accuracy = Số mẫu dự đoán đúng / Tổng số mẫu
```

Dễ hiểu nhưng không nên là metric chính.

### 13.3. Precision

```text
Precision = TP / (TP + FP)
```

Cho biết trong các mẫu được dự đoán là spoof, có bao nhiêu mẫu thật sự là spoof.

### 13.4. Recall

```text
Recall = TP / (TP + FN)
```

Cho biết mô hình phát hiện được bao nhiêu mẫu spoof thật sự.

### 13.5. F1-score

```text
F1 = 2 × Precision × Recall / (Precision + Recall)
```

Phù hợp khi cần cân bằng precision và recall.

### 13.6. APCER

**APCER** (*Attack Presentation Classification Error Rate*) là tỷ lệ mẫu tấn công bị nhận nhầm là live.

```text
APCER = Số mẫu attack bị dự đoán là live / Tổng số mẫu attack
```

APCER cao nghĩa là nguy hiểm, vì nhiều mẫu giả mạo lọt qua hệ thống.

### 13.7. BPCER

**BPCER** (*Bona Fide Presentation Classification Error Rate*) là tỷ lệ mẫu thật bị nhận nhầm là attack.

```text
BPCER = Số mẫu live bị dự đoán là spoof / Tổng số mẫu live
```

BPCER cao nghĩa là hệ thống gây khó chịu cho người dùng thật.

### 13.8. ACER

**ACER** (*Average Classification Error Rate*) là trung bình của APCER và BPCER.

```text
ACER = (APCER + BPCER) / 2
```

Trong đề tài, **ACER là metric chính**.

---

## 14. Thiết kế thực nghiệm

### 14.1. Thí nghiệm chính

| STT | Mô hình | Dataset | Protocol | Gộp video | Metric chính |
|---|---|---|---|---|---|
| 1 | LBP-SVM | OULU-NPU | Protocol 1 | Mean score | ACER, F1 |
| 2 | MobileNetV2 | OULU-NPU | Protocol 1 | Mean probability | ACER, F1 |
| 3 | ResNet18 | OULU-NPU | Protocol 1 | Mean probability | ACER, F1 |

### 14.2. Thí nghiệm phụ nếu còn thời gian

| Thí nghiệm phụ | Ý nghĩa |
|---|---|
| 5 frame/video vs 10 frame/video | Đánh đổi tốc độ và hiệu quả |
| Frame-level vs video-level | Kiểm tra lợi ích của gộp video |
| Freeze backbone vs fine-tune block cuối | Kiểm tra lợi ích fine-tuning |
| MobileNetV2 vs ResNet18 về thời gian inference | Đánh giá tính thực tế khi triển khai |

### 14.3. Nguyên tắc tránh sai lệch

1. Không trộn train/dev/test.
2. Không chia frame ngẫu nhiên nếu làm mất split gốc.
3. Tất cả frame của một video phải thuộc đúng split của video đó.
4. Threshold nên chọn trên development set, không chọn trên test set.
5. Kết quả test chỉ báo cáo sau khi đã chốt mô hình và threshold.

---

## 15. Bảng kết quả dự kiến

### 15.1. Bảng kết quả chính

| Phương pháp | Accuracy | Precision | Recall | F1-score | APCER | BPCER | ACER |
|---|---:|---:|---:|---:|---:|---:|---:|
| LBP-SVM |  |  |  |  |  |  |  |
| MobileNetV2 |  |  |  |  |  |  |  |
| ResNet18 |  |  |  |  |  |  |  |

### 15.2. Bảng chi phí tính toán

| Phương pháp | Số tham số | Thời gian train | Thời gian inference/video | Có cần GPU? |
|---|---:|---:|---:|---|
| LBP-SVM | Thấp |  |  | Không |
| MobileNetV2 | Trung bình thấp |  |  | Nên có |
| ResNet18 | Trung bình |  |  | Nên có |

### 15.3. Bảng frame-level vs video-level

| Phương pháp | Frame-level F1 | Video-level F1 | Frame-level ACER | Video-level ACER |
|---|---:|---:|---:|---:|
| LBP-SVM |  |  |  |  |
| MobileNetV2 |  |  |  |  |
| ResNet18 |  |  |  |  |

---

## 16. Cách phân tích kết quả

### 16.1. Nếu LBP-SVM tốt

Có thể kết luận:

- Texture vẫn là tín hiệu mạnh trong phát hiện giả mạo.
- Với điều kiện phần cứng hạn chế, LBP-SVM là baseline đáng cân nhắc.
- Tuy nhiên, LBP-SVM có thể khó tổng quát nếu thay đổi dataset hoặc thiết bị.

### 16.2. Nếu ResNet18 tốt nhất

Có thể kết luận:

- CNN học được đặc trưng phân biệt live/spoof tốt hơn đặc trưng thủ công.
- ResNet18 phù hợp khi có đủ tài nguyên huấn luyện.
- Cần xem xét nguy cơ overfit và chi phí tính toán.

### 16.3. Nếu MobileNetV2 gần bằng ResNet18

Có thể kết luận:

- MobileNetV2 là lựa chọn cân bằng tốt giữa hiệu quả và chi phí.
- Phù hợp với bối cảnh xác thực khuôn mặt trên thiết bị di động.
- Có thể là mô hình khuyến nghị trong điều kiện phần cứng hạn chế.

### 16.4. Nếu video-level tốt hơn frame-level

Có thể kết luận:

- Gộp nhiều frame giúp quyết định ổn định hơn.
- Một số frame riêng lẻ có thể nhiễu, mờ hoặc thiếu thông tin.
- Video-level evaluation phù hợp hơn với bản chất của OULU-NPU.

### 16.5. Nếu kết quả CNN không tốt

Cần phân tích:

- Có thể do số epoch ít.
- Có thể do crop face chưa tốt.
- Có thể do freeze backbone quá nhiều.
- Có thể do số frame/video quá ít.
- Có thể do chưa cân bằng lớp hoặc threshold chưa tối ưu.

---

## 17. Related Work cần đưa vào

### 17.1. Nhóm nền tảng sinh trắc học

1. **Handbook of Biometrics**  
   Dùng cho phần hệ sinh trắc học, spoof detection, biometric system security.

2. **Handbook of Face Recognition**  
   Dùng cho pipeline nhận dạng khuôn mặt, phát hiện mặt, trích đặc trưng, xử lý video.

### 17.2. Nhóm LBP / texture-based FAS

1. **Chingovska, Anjos, Marcel – On the Effectiveness of Local Binary Patterns in Face Anti-spoofing**  
   Nền tảng cho LBP trong face anti-spoofing.

2. **Boulkenafet et al. – Face Spoofing Detection Using Colour Texture Analysis**  
   Mở rộng hướng texture sang color texture.

### 17.3. Nhóm dataset OULU-NPU

1. **Boulkenafet et al. – OULU-NPU: A Mobile Face Presentation Attack Database with Real-World Variations**  
   Bài gốc của dataset OULU-NPU.

### 17.4. Nhóm deep learning FAS

1. **Liu, Jourabloo, Liu – Learning Deep Models for Face Anti-Spoofing: Binary or Auxiliary Supervision**  
   Bài quan trọng cho hướng dùng deep learning và auxiliary supervision.

2. **Yu et al. – Searching Central Difference Convolutional Networks for Face Anti-Spoofing**  
   CDCN/CDCN++ là SOTA tham chiếu mạnh trên OULU-NPU.

3. **Yu et al. – Deep Learning for Face Anti-Spoofing: A Survey**  
   Survey tổng quan để phân loại phương pháp và dataset.

### 17.5. Nhóm lightweight / mobile models

1. Các nghiên cứu dùng MobileNetV2 hoặc mô hình nhẹ cho face anti-spoofing.
2. Các nghiên cứu transfer learning cho face anti-spoofing.
3. Có thể đưa vào phần thảo luận nếu muốn nhấn mạnh tính thực tế của MobileNetV2.

---

## 18. Cấu trúc báo cáo đề xuất

## Chương 1. Giới thiệu

### 1.1. Bối cảnh

- Xác thực khuôn mặt ngày càng phổ biến.
- Ưu điểm: tiện lợi, không tiếp xúc, phù hợp thiết bị di động.
- Nguy cơ: bị tấn công bằng ảnh in hoặc video replay.

### 1.2. Vấn đề nghiên cứu

- Hệ nhận dạng khuôn mặt cần kiểm tra tính thật/giả của mẫu đầu vào.
- Face spoofing detection là bước bảo vệ trước face recognition.

### 1.3. Mục tiêu

- So sánh LBP-SVM, ResNet18, MobileNetV2 trên OULU-NPU.
- Đánh giá ở frame-level và video-level.
- Phân tích hiệu quả và chi phí tính toán.

### 1.4. Phạm vi

- Chỉ dùng OULU-NPU.
- Ưu tiên Protocol 1.
- Không làm cross-dataset/few-shot/attention trong phần chính.

### 1.5. Cấu trúc báo cáo

Tóm tắt các chương còn lại.

---

## Chương 2. Cơ sở lý thuyết và nghiên cứu liên quan

### 2.1. Hệ sinh trắc học

- Khái niệm biometric authentication.
- Sensor, feature extraction, matcher, decision.

### 2.2. Nhận dạng khuôn mặt và phát hiện giả mạo

- Face recognition vs face spoofing detection.
- Vai trò của anti-spoofing module.

### 2.3. Presentation attack

- Print attack.
- Replay attack.
- Display attack.
- Mask attack, nêu mở rộng.

### 2.4. LBP và SVM

- Nguyên lý LBP.
- Vì sao texture hữu ích trong phát hiện giả mạo.
- Vai trò của SVM.

### 2.5. CNN, ResNet18 và MobileNetV2

- CNN tự học đặc trưng.
- ResNet18 là CNN baseline.
- MobileNetV2 là CNN nhẹ.

### 2.6. Nghiên cứu liên quan

- LBP-based methods.
- CNN-based methods.
- OULU-NPU benchmark.
- CDCN++ như SOTA tham chiếu.

---

## Chương 3. Dữ liệu và phương pháp

### 3.1. Bộ dữ liệu OULU-NPU

- Mục tiêu của dataset.
- Loại dữ liệu.
- Nhãn live/spoof.
- Protocol 1.

### 3.2. Tiền xử lý dữ liệu

- Đọc video.
- Trích frame.
- Crop khuôn mặt.
- Resize.
- Normalize.

### 3.3. Phương pháp LBP-SVM

- Trích LBP.
- Histogram.
- Huấn luyện SVM.
- Dự đoán frame/video.

### 3.4. Phương pháp ResNet18

- Pretrained model.
- Thay classifier head.
- Freeze/fine-tune.
- Dự đoán xác suất.

### 3.5. Phương pháp MobileNetV2

- Pretrained model.
- Thay classifier head.
- Freeze/fine-tune.
- Dự đoán xác suất.

### 3.6. Gộp kết quả video

- Mean probability.
- Threshold.
- Video-level prediction.

---

## Chương 4. Thiết kế thực nghiệm

### 4.1. Cấu hình thực nghiệm

- Phần cứng.
- Phần mềm.
- Python, PyTorch, scikit-learn, OpenCV/MediaPipe.

### 4.2. Cấu hình huấn luyện

- Số frame/video.
- Batch size.
- Epoch.
- Learning rate.
- Optimizer.

### 4.3. Chỉ số đánh giá

- Accuracy.
- Precision.
- Recall.
- F1.
- APCER.
- BPCER.
- ACER.
- Confusion matrix.

### 4.4. Các thí nghiệm

- LBP-SVM.
- MobileNetV2.
- ResNet18.
- Frame-level vs video-level nếu có.

---

## Chương 5. Kết quả và thảo luận

### 5.1. Kết quả tổng quan

Bảng so sánh ba mô hình.

### 5.2. So sánh LBP-SVM và CNN

- LBP-SVM nhẹ, dễ chạy.
- CNN học đặc trưng sâu hơn.

### 5.3. So sánh ResNet18 và MobileNetV2

- ResNet18 có thể mạnh hơn.
- MobileNetV2 nhẹ hơn, phù hợp mobile.

### 5.4. Phân tích video-level

- Gộp frame có thể giúp ổn định hơn.
- Phân tích các lỗi thường gặp.

### 5.5. So sánh với SOTA tham chiếu

- Nhắc CDCN++ đạt kết quả rất mạnh trên OULU-NPU.
- Đề tài không tái hiện CDCN++ vì giới hạn phần cứng.
- Mục tiêu là so sánh baseline trong điều kiện thực tế hơn.

### 5.6. Hạn chế

- Chỉ dùng OULU-NPU Protocol 1.
- Chưa đánh giá Protocol 2–4.
- Chưa đánh giá cross-dataset.
- Chưa dùng attention hoặc temporal modeling.
- Chưa dùng depth/pseudo-depth supervision.

---

## Chương 6. Kết luận và hướng phát triển

### 6.1. Kết luận

- Tóm tắt mô hình nào tốt nhất theo ACER/F1.
- Tóm tắt mô hình nào nhẹ nhất.
- Đưa ra khuyến nghị lựa chọn mô hình.

### 6.2. Hướng phát triển

1. Mở rộng sang OULU-NPU Protocol 2–4.
2. Đánh giá thêm trên Replay-Attack.
3. Thực hiện cross-dataset evaluation.
4. Thử attention pooling hoặc temporal modeling.
5. Thử các mô hình chuyên biệt như CDCN, DeepPixBiS, PatchNet.
6. Thử few-shot/domain adaptation nếu có thêm thời gian.

---

## 19. Kế hoạch triển khai

### Giai đoạn 1. Chuẩn bị dữ liệu

- Tải OULU-NPU.
- Kiểm tra cấu trúc thư mục.
- Đọc protocol split.
- Viết script trích frame.
- Viết script crop face.

Kết quả cần có:

```text
data_processed/
    train/
        live/
        spoof/
    dev/
        live/
        spoof/
    test/
        live/
        spoof/
```

Hoặc lưu theo metadata CSV:

```text
video_id, frame_path, label, split
```

### Giai đoạn 2. LBP-SVM

- Trích LBP feature.
- Train SVM.
- Đánh giá frame-level.
- Gộp video-level.
- Lưu kết quả.

### Giai đoạn 3. MobileNetV2

- Tạo dataset loader.
- Load pretrained MobileNetV2.
- Train classifier head.
- Đánh giá.
- Lưu kết quả.

### Giai đoạn 4. ResNet18

- Load pretrained ResNet18.
- Train classifier head.
- Fine-tune nhẹ nếu kịp.
- Đánh giá.
- Lưu kết quả.

### Giai đoạn 5. Tổng hợp báo cáo

- Bảng kết quả.
- Confusion matrix.
- Biểu đồ so sánh.
- Phân tích trade-off.
- Viết kết luận.

---

## 20. Checklist hoàn thành

| Hạng mục | Trạng thái |
|---|---|
| Chốt tên đề tài | Chưa/Đã |
| Tải OULU-NPU | Chưa/Đã |
| Đọc protocol split | Chưa/Đã |
| Trích frame | Chưa/Đã |
| Crop face | Chưa/Đã |
| Train LBP-SVM | Chưa/Đã |
| Train MobileNetV2 | Chưa/Đã |
| Train ResNet18 | Chưa/Đã |
| Đánh giá frame-level | Chưa/Đã |
| Đánh giá video-level | Chưa/Đã |
| Tính ACER/F1 | Chưa/Đã |
| Vẽ confusion matrix | Chưa/Đã |
| Viết Related Work | Chưa/Đã |
| Viết Methodology | Chưa/Đã |
| Viết Results & Discussion | Chưa/Đã |
| Viết Conclusion | Chưa/Đã |

---

## 21. Câu định vị ngắn có thể đưa vào báo cáo

> This study focuses on face spoofing detection, a security module in biometric authentication systems that determines whether an input face sample is captured from a live person or from a spoofing medium such as a printed photo or replayed video. Instead of proposing a new state-of-the-art model, this work compares a traditional texture-based method, LBP-SVM, with two deep learning baselines, ResNet18 and MobileNetV2, on the OULU-NPU dataset. The goal is to analyze the trade-off between detection performance, video-level stability, and computational cost under resource-constrained conditions.

Bản tiếng Việt:

> Nghiên cứu này tập trung vào bài toán phát hiện giả mạo khuôn mặt, một module bảo mật trong hệ thống xác thực sinh trắc học nhằm xác định mẫu khuôn mặt đầu vào được thu từ người thật hay từ phương tiện giả mạo như ảnh in hoặc video phát lại. Thay vì đề xuất một mô hình mới đạt SOTA, đề tài so sánh phương pháp truyền thống dựa trên texture là LBP-SVM với hai mô hình học sâu ResNet18 và MobileNetV2 trên bộ dữ liệu OULU-NPU. Mục tiêu là phân tích sự đánh đổi giữa hiệu quả phát hiện, độ ổn định ở mức video và chi phí tính toán trong điều kiện tài nguyên hạn chế.

---

## 22. Kết luận chốt chiến lược

Cấu hình chính của đề tài:

```text
Dataset: OULU-NPU
Protocol: Protocol 1
Models: LBP-SVM, MobileNetV2, ResNet18
Frame sampling: 10 frames/video
Aggregation: Mean probability / Mean score
Evaluation: Video-level
Main metrics: ACER, F1-score
Scope: No cross-dataset, no few-shot, no attention in main experiment
```

Đây là cấu hình phù hợp nhất với mục tiêu báo cáo, giới hạn thời gian và giới hạn phần cứng, đồng thời vẫn đủ chiều sâu để phân tích sự khác biệt giữa phương pháp truyền thống và học sâu trong bài toán phát hiện giả mạo khuôn mặt.

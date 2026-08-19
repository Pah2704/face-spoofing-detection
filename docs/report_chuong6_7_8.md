# CHƯƠNG 6: KẾT QUẢ THỰC NGHIỆM

## 6.1 Bảng tổng hợp kết quả
Kết quả hiệu năng của cả 4 thí nghiệm được đánh giá ở cấp độ video (video-level) trên tập Dev và tập Test của OULU-NPU Protocol 1 (đơn vị tính: %):

| Thí nghiệm | Tập | Accuracy | Precision | Recall | F1-score | APCER | BPCER | ACER |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| **E01 (LBP-SVM)** | Dev | 89.11 | 96.98 | 89.17 | 92.91 | 10.83 | 11.11 | **10.97** |
| | Test | 83.67 | 86.31 | 94.58 | 90.26 | 5.42 | 60.00 | **32.71** |
| **E02 (MobileNetV2)**| Dev | 83.00 | 97.49 | 80.83 | 88.38 | 19.17 | 8.33 | **13.75** |
| | Test | 78.33 | 91.27 | 80.63 | 85.62 | 19.38 | 30.83 | **25.10** |
| **E03 (ResNet18)** | Dev | 86.44 | 96.57 | 86.11 | 91.04 | 13.89 | 12.22 | **13.06** |
| | Test | 78.33 | 92.07 | 79.79 | 85.49 | 20.21 | 27.50 | **23.85** |
| **E04 (ResNet18 FT)**| Dev | 98.22 | 98.89 | 98.89 | 98.89 | 1.25 | 3.89 | **2.57** |
| | Test | 90.83 | 94.29 | 94.38 | 94.29 | 5.42 | 24.17 | **14.79** |

Bảng Confusion Matrix chi tiết trên tập Test (tổng cộng 600 video gồm 120 video Live và 480 video Spoof):

| Mô hình | True Negative (TN) | False Positive (FP) | False Negative (FN) | True Positive (TP) |
|---|---:|---:|---:|---:|
| **E01 (LBP-SVM)** | 48 | 72 | 26 | 454 |
| **E02 (MobileNetV2)**| 83 | 37 | 93 | 387 |
| **E03 (ResNet18)** | 87 | 33 | 97 | 383 |
| **E04 (ResNet18 FT)**| 91 | 29 | 26 | 454 |

## 6.2 Phân tích chi tiết kết quả

### 6.2.1 Thí nghiệm E01 (LBP-SVM)
- **Hiệu năng tập Dev:** LBP-SVM thể hiện hiệu năng xuất sắc trên tập Dev với ACER chỉ **10.97%**, vượt trội hơn cả hai mô hình CNN đóng băng backbone (E02 và E03). Điều này củng cố giả thuyết rằng đặc trưng LBP mô tả texture cực tốt khi điều kiện thiết bị ổn định.
- **Hiệu năng tập Test:** Tuy nhiên, khi đánh giá trên tập Test, ACER tăng vọt lên **32.71%** (sụt giảm tuyệt đối 21.74 điểm %).
- **Mất cân bằng lỗi nghiêm trọng:** APCER đạt mức rất thấp (**5.42%**), cho thấy mô hình bắt spoof cực tốt (chỉ bỏ sót 26/480 video tấn công). Thế nhưng BPCER lên tới **60.00%**, nghĩa là mô hình phân loại nhầm **72 trên tổng số 120 video thật** của người dùng thành spoof.
- **Bài học về F1-score:** Do lớp spoof chiếm tới 80% tập Test, chỉ số F1-score của E01 vẫn đạt mức rất cao là **90.26%**. Điều này chứng minh F1-score hoặc Accuracy có thể che giấu sự mất cân bằng lỗi thảm hại trong các hệ thống PAD, và việc sử dụng ACER theo chuẩn ISO là hoàn toàn đúng đắn.

### 6.2.2 Thí nghiệm E02 và E03 (CNN đóng băng backbone)
- **Độ ổn định cao hơn:** Cả hai mô hình CNN (MobileNetV2 và ResNet18) đều cho thấy độ suy giảm hiệu năng từ Dev sang Test thấp hơn LBP-SVM (chỉ tăng khoảng 10-11 điểm ACER).
- **ResNet18 tốt nhất trong baseline:** ResNet18 (E03) đạt test ACER **23.85%**, tốt hơn MobileNetV2 (E02) là **25.10%**. Sự cân bằng giữa hai lỗi APCER (20.21%) và BPCER (27.50%) của ResNet18 tốt hơn nhiều so với sự mất cân bằng của LBP-SVM.
- **Hạn chế:** Các đặc trưng ImageNet đóng băng chủ yếu nhận diện vật thể thô, thiếu khả năng biểu diễn các cấu trúc vi kết cấu mịn của màn hình hoặc giấy in, dẫn đến tỷ lệ bỏ sót spoof (APCER ~20%) vẫn còn cao.

### 6.2.3 Thí nghiệm E04 (ResNet18 Fine-tune Layer4)
- **Bứt phá hiệu năng:** Việc tinh chỉnh `layer4` mang lại sự cải thiện vượt bậc. ACER tập Dev giảm xuống mức cực thấp **2.57%**, và quan trọng nhất là ACER tập Test giảm xuống còn **14.79%** (giảm 9.06 điểm % tuyệt đối, tương đương mức cải thiện tương đối 38% so với E03).
- **Cân bằng lỗi tối ưu:** E04 kéo APCER xuống chỉ còn **5.42%** (ngang với LBP-SVM) nhưng đồng thời giảm BPCER xuống còn **24.17%** (tốt nhất trong cả 4 mô hình). F1-score tăng lên mức thực tế là **94.29%**.

## 6.3 Phân tích lỗi (Error Analysis)
Qua việc phân tích chi tiết các video bị phân loại sai, chúng tôi thu được các phát hiện quan trọng:

### 1. Phân tích sự chồng chéo lỗi (Overlap Analysis)
- **Lỗi hệ thống:** Có **16 video Bona Fide (Live) bị cả 3 mô hình baseline (E01, E02, E03)** phân loại nhầm thành Spoof. Đây là các trường hợp có điều kiện ánh sáng cực đoan (bị lóa sáng mạnh hoặc quá tối) khiến da mặt mất đi kết cấu tự nhiên.
- Chỉ có duy nhất **2 video tấn công (Spoof) bị cả 3 mô hình bỏ sót**. Điều này chứng tỏ các mô hình học được các dấu hiệu giả mạo khác nhau và có thể bổ trợ cho nhau.
- Hai mô hình CNN (E02 và E03) chia sẻ chung 23 trên tổng số 33 lỗi FP và 50 lỗi FN. Sự trùng lặp cao này phản ánh bản chất chung của việc sử dụng các đặc trưng ImageNet đóng băng.

### 2. Lỗi theo thiết bị camera (Phone-specific Errors)
Phân tích lỗi của mô hình tiêu chuẩn ResNet18 (E03) theo từng loại điện thoại ghi hình:
- **APCER cao nhất trên Phone 5 (31.25%) và Phone 6 (28.75%):** Camera của Sony XPERIA C5 (Phone 5) và Oppo N3 (Phone 6) có bộ lọc làm mịn da tự động và tăng độ tương phản tích hợp sâu trong phần cứng, vô tình xóa nhòa các nhiễu moiré hoặc hạt mực của PAI, khiến mô hình dễ bị đánh lừa hơn.
- **BPCER cao nhất trên Phone 3 (40.00%):** Camera Meizu X5 (Phone 3) có độ phân giải thực tế kém và nhiễu cảm biến (sensor noise) rất lớn. Mô hình LBP-SVM và CNN nhầm tưởng nhiễu cảm biến này là hạt mực in hoặc vân màn hình, dẫn đến từ chối nhầm người thật.

### 3. Lỗi theo công cụ tấn công (PAI-specific Errors)
- **Printer 1 (APCER 25.83%) vs Printer 2 (APCER 13.33%):** Bản in từ máy in phun chất lượng cao Epson (Printer 1) mịn và sắc nét hơn nhiều so với máy in laser văn phòng (Printer 2), làm giảm đáng kể các lỗi hạt mực vi mô, khiến mô hình dễ bỏ sót.
- **Display 1 (APCER 25.00%) vs Display 2 (APCER 16.67%):** Màn hình điện thoại Oppo N3 (Display 1) có mật độ pixel cực cao (PPI lớn) khiến camera khó bắt được nhiễu moiré so với màn hình cỡ lớn của Macbook Pro (Display 2).

## 6.4 Benchmark tài nguyên tính toán
Thử nghiệm benchmark được thực hiện trên cùng một môi trường phần cứng: GPU NVIDIA RTX 3060 12GB và CPU Intel Core i7 đa luồng. Input là 600 ảnh crop khuôn mặt từ tập Test:

| Chỉ số | E01 (LBP-SVM) | E02 (MobileNetV2) | E03 (ResNet18) | E04 (ResNet18 FT) |
|---|---|---|---|---|
| **Yêu cầu GPU** | Không | Có | Có | Có |
| **Kích thước mô hình** | **21.7 KB** | **9.15 MB** | **44.79 MB** | **44.79 MB** |
| **Thời gian huấn luyện** | **~47 giây** | ~8 phút | ~6 phút | ~6 phút |
| **Độ trễ mô hình (Batch=1)** | **0.163 ms** | 3.247 ms | 1.595 ms | 1.595 ms |
| **Độ trễ mô hình (Batch=16)**| **0.011 ms** | 0.648 ms | 0.593 ms | 0.593 ms |
| **Độ trễ E2E (Mỗi frame)** | 0.733 ms | 0.991 ms | 0.966 ms | 0.966 ms |

> [!TIP]
> **Nhận xét về tài nguyên:**
> 1. LBP-SVM có lợi thế tuyệt đối về kích thước mô hình (chỉ 21.7 KB) và không yêu cầu GPU. Tốc độ suy luận của mô hình SVM cực nhanh (0.011 ms/frame ở batch 16).
> 2. ResNet18 có kích thước lớn gấp 5 lần MobileNetV2 (44.79 MB so với 9.15 MB) nhưng tốc độ suy luận trên GPU lại nhanh gấp đôi (1.595 ms so với 3.247 ms ở batch 1) nhờ cấu trúc khối tích chập tiêu chuẩn được thư viện TensorRT/cuDNN tối ưu hóa tốt hơn so với cấu trúc depthwise của MobileNet.
> 3. E04 có cùng chi phí suy luận (Inference cost) y hệt E03 vì cấu trúc đồ thị mạng không đổi, chỉ tăng nhẹ dung lượng bộ nhớ GPU trong pha huấn luyện do phải lưu trữ đồ thị tính toán đạo hàm cho `layer4`.

## 6.5 Phân tích Frame-level so với Video-level
So sánh giá trị ACER (%) giữa việc đánh giá độc lập từng frame và việc gộp trung bình video-level:

| Thí nghiệm | Level | Dev ACER | Test ACER | Hiệu quả của việc gộp video |
|---|---|---:|---:|---|
| **E01 (LBP-SVM)** | Frame | 12.62 | 30.58 | |
| | Video | 10.97 | 32.71 | ❌ Làm tệ hơn ở tập Test (+2.13) |
| **E02 (MobileNetV2)**| Frame | 14.64 | 25.69 | |
| | Video | 13.75 | 25.10 |  Cải thiện nhẹ (-0.59) |
| **E03 (ResNet18)** | Frame | 14.47 | 24.03 | |
| | Video | 13.06 | 23.85 |  Cải thiện nhẹ (-0.18) |
| **E04 (ResNet18 FT)**| Frame | 3.13 | 13.41 | |
| | Video | 2.57 | 14.79 | ❌ Làm tệ hơn ở tập Test (+1.38) |

Việc lấy trung bình cộng điểm số các frame (mean aggregation) giúp làm mượt các dự đoán sai lệch đơn lẻ trong video đối với các mô hình CNN baseline (giảm nhẹ ACER). Tuy nhiên, đối với bộ phân loại nhạy cảm cao như LBP-SVM hay mô hình tinh chỉnh sâu E04, việc lấy trung bình vô tình kéo điểm số của các frame chính xác về phía ngưỡng lỗi của các frame nhiễu, làm tăng nhẹ ACER trên tập Test. Điều này mở ra hướng nghiên cứu sử dụng các bộ gộp thông minh hơn (như Attention Pooling) thay vì trung bình cộng đơn giản.

# CHƯƠNG 7: THẢO LUẬN

## 7.1 So sánh Đặc trưng thủ công (Handcrafted) và Học sâu (Deep Learning)
Một trong những phát hiện cốt lõi của nghiên cứu này là sự khác biệt lớn về khả năng tổng quát hóa giữa đặc trưng LBP thủ công và đặc trưng học sâu CNN.

- **Đặc trưng LBP (Handcrafted):** Hoạt động dựa trên các quy tắc toán học cố định được thiết kế sẵn (so sánh cường độ pixel cục bộ). LBP rất nhạy cảm với các chi tiết cạnh và vi cấu trúc vi mô.
  - *Tại sao LBP đạt kết quả tốt trên Dev nhưng tệ trên Test?* Bản chất của LBP là so khớp trực tiếp các biểu đồ tần suất kết cấu. Khi điều kiện camera thu nhận thay đổi (ví dụ: Phone 3 có nhiễu cảm biến lớn, Phone 5 tự động làm mịn da), các phân phối biểu đồ LBP bị dịch chuyển mạnh (domain shift). Bộ phân loại tuyến tính SVM huấn luyện trên tập Train không thể thích ứng với sự lệch pha phi tuyến này, dẫn đến việc từ chối nhầm 60.00% người dùng thật trên tập Test (BPCER = 60.00%). Điều này chứng tỏ các đặc trưng handcrafted thiếu tính bất biến (invariance) trước các biến thể môi trường phức tạp.
- **Đặc trưng CNN (Deep Learning):** Các bộ lọc tích chập học được các biểu diễn phân tầng từ thô đến tinh. Nhờ cơ chế Pooling và cấu trúc học sâu, CNN có tính bất biến dịch chuyển (translation invariance) và bất biến tỷ lệ tốt hơn.
  - Ngay cả khi đóng băng hoàn toàn backbone ImageNet (thí nghiệm E02 và E03), các đặc trưng phân tầng vẫn cung cấp một biểu diễn robust hơn trước sự thay đổi của thiết bị camera. Sự sụt giảm ACER từ Dev sang Test của CNN chỉ khoảng 10-11 điểm %, ít nghiêm trọng hơn nhiều so với mức sụt giảm 21.74 điểm % của LBP-SVM.

## 7.2 Cơ chế tác động của kỹ thuật Fine-tuning
Kết quả vượt trội của thí nghiệm E04 (ACER 14.79%) so với E03 (ACER 23.85%) đặt ra câu hỏi về mặt lý thuyết: *Tại sao việc tinh chỉnh riêng `layer4` lại mang lại hiệu quả bứt phá như vậy?*

1. **Giới hạn của ImageNet Feature Head-only:** Trọng số pretrained ImageNet được tối ưu hóa cho bài toán phân loại vật thể (1000 lớp). Ở các tầng sâu nhất như `layer4` của ResNet18, các bộ lọc tích chập đại diện cho các khái niệm ngữ nghĩa trừu tượng cao cấp (ví dụ: hình dáng mắt, mũi, cấu trúc khuôn mặt tổng thể). Trong bài toán phát hiện giả mạo khuôn mặt, cấu trúc ngữ nghĩa này của người thật và ảnh in/video phát lại là hoàn toàn giống nhau (đều là cấu trúc khuôn mặt). Lớp classifier head tuyến tính (E03) buộc phải tìm cách phân tách thật/giả dựa trên các vector ngữ nghĩa này, dẫn đến hiệu năng bị giới hạn.
2. **Sự thích ứng của Layer4:** Khi giải đóng băng `layer4` (E04), ta cho phép các bộ lọc ngữ nghĩa cấp cao này tự điều chỉnh. Thay vì nhận diện hình dáng khuôn mặt chung chung, các bộ lọc ở `layer4` học cách nhận diện các vân moiré, hạt mực in vi mô, sự mất mát tần số cao, và các vệt phản xạ ánh sáng trên màn hình.
3. **Vai trò của Tốc độ học vi phân (Differential Learning Rates):** Nếu huấn luyện toàn bộ mạng với learning rate lớn, ta sẽ phá hủy các đặc trưng tổng quát đã học từ ImageNet (catastrophic forgetting) và dễ gây ra overfitting trên tập dữ liệu huấn luyện nhỏ của OULU-NPU. Việc thiết lập learning rate của `layer4` ở mức cực nhỏ ($\eta = 10^{-5}$) giúp mạng dịch chuyển chậm rãi và chính xác hướng tới không gian đặc trưng tối ưu cho bài toán PAD, trong khi vẫn giữ được tính ổn định và tính tổng quát từ các tầng phía trước (`layer1-3`).

## 7.3 Vấn đề Domain Shift và Khả năng tổng quát hóa (Generalization)
Khoảng cách hiệu năng từ Dev sang Test (Domain Shift) xuất hiện ở cả 4 thí nghiệm:
- LBP-SVM: +21.74 điểm ACER
- MobileNetV2: +11.35 điểm ACER
- ResNet18: +10.80 điểm ACER
- ResNet18 FT (E04): +12.22 điểm ACER

Nguyên nhân gốc rễ của domain shift trong OULU-NPU Protocol 1 là sự lệch phân phối giữa các session ghi hình (khác biệt về ánh sáng phòng, hướng nắng tự nhiên, phông nền phông cảnh).
Mặc dù E04 cải thiện đáng kể hiệu năng trên cả hai tập, khoảng cách giữa Dev ACER (2.57%) và Test ACER (14.79%) vẫn còn khá lớn (12.22 điểm %). Điều này chứng tỏ kỹ thuật fine-tuning đơn thuần chưa giải quyết được triệt để vấn đề lệch miền dữ liệu. Để khắc phục, hệ thống cần tích hợp các kỹ thuật thích ứng tên miền chủ động (như Domain Adversarial Training) hoặc áp dụng các phương pháp tăng cường dữ liệu mạnh mẽ về ánh sáng và màu sắc (Color Jittering, MixUp) để ép mô hình học được các đặc trưng bất biến với môi trường.

## 7.4 So sánh với các nghiên cứu liên quan
Đặt kết quả tốt nhất đạt được trong nghiên cứu này (ResNet18 FT E04 với Test ACER 14.79%) trong bối cảnh các nghiên cứu đã công bố trên OULU-NPU Protocol 1:

| Mô hình / Nghiên cứu | Phương pháp chính | Test ACER (%) |
|---|---|---:|
| **OULU-NPU Baseline** (Boulkenafet et al., 2017) | LBP + SVM | 31.60 |
| **DeepPixBiS** (George et al., 2019) | Pixel-wise Binary Supervision | 1.00 |
| **CDCN** (Yu et al., 2020) | Central Difference Convolution | 1.00 |
| **E01 (LBP-SVM)** (Của chúng tôi) | Uniform LBP + LinearSVC | 32.71 |
| **E03 (ResNet18 Head)** (Của chúng tôi) | Frozen ResNet18 + Linear Head | 23.85 |
| **E04 (ResNet18 FT)** (Của chúng tôi) | ResNet18 Fine-tune Layer4 | 14.79 |

- Kết quả E01 (32.71%) hoàn toàn tương đồng với kết quả baseline chính thức của OULU-NPU (31.60%), xác nhận tính đúng đắn và chuẩn xác trong việc thiết lập pipeline của chúng tôi.
- ResNet18 FT (E04) đạt mức ACER 14.79%, cải thiện rất lớn so với baseline truyền thống và CNN head-only. Tuy nhiên, nó vẫn còn một khoảng cách đáng kể so với các kiến trúc SOTA chuyên biệt như DeepPixBiS (1.00%) hay CDCN (1.00%).
- *Nguyên nhân của khoảng cách:* Các mô hình SOTA sử dụng giám sát mức độ pixel (Pixel-wise Supervision) với nhãn phụ là bản đồ độ sâu (Depth Map) để hướng dẫn mô hình học cấu trúc hình học 3D một cách tường minh, hoặc sử dụng các toán tử tích chập cải tiến (Central Difference Convolution) chuyên biệt cho texture. Mô hình E04 của chúng tôi chỉ sử dụng nhãn nhị phân (binary supervision) ở cuối mạng, khiến mô hình vẫn gặp khó khăn trong việc loại bỏ hoàn toàn các đặc trưng nhiễu bối cảnh.

## 7.5 Hạn chế của nghiên cứu hiện tại
1. **Giới hạn số lượng Seed:** Thí nghiệm chỉ chạy trên một seed duy nhất (seed = 42). Để kết luận có tính thuyết phục khoa học cao hơn, cần thực hiện huấn luyện đa seed (ví dụ 5 lần chạy với các seed khác nhau) để tính toán độ lệch chuẩn và khoảng tin cậy của các chỉ số hiệu năng.
2. **Đơn Protocol:** Nghiên cứu mới giới hạn ở Protocol 1. Để đánh giá toàn diện khả năng chống chịu của mô hình trước các thiết bị camera chưa từng thấy hay các công cụ tấn công mới, cần mở rộng đánh giá sang Protocol 2, 3 và 4.
3. **Chưa có mô hình hóa Temporal:** Hệ thống xử lý từng frame ảnh độc lập rồi lấy trung bình điểm số. Cách tiếp cận này bỏ qua các thông tin động học cực kỳ quan trọng theo thời gian như nhịp chớp mắt, sự chuyển động phi cứng của cơ mặt, hay tần số nhấp nháy (flicker) của màn hình phát lại.
4. **Tăng cường dữ liệu đơn giản:** Mới chỉ áp dụng lật ngang ảnh (horizontal flip). Các kỹ thuật mạnh như xoay ảnh góc nhỏ, color jittering (thay đổi độ sáng, tương phản), chèn nhiễu hạt, hay Cutout chưa được tích hợp để nâng cao tính robust của CNN.

---

# CHƯƠNG 8: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

## 8.1 Kết luận
Nghiên cứu này đã xây dựng thành công một pipeline phát hiện giả mạo khuôn mặt hoàn chỉnh, có tính tái lập và kiểm chứng chặt chẽ trên bộ dữ liệu chuẩn OULU-NPU Protocol 1. Qua các thực nghiệm so sánh chi tiết, chúng tôi rút ra các kết luận khoa học quan trọng:

1. **Sự vượt trội của các đặc trưng học sâu:** Các mô hình học sâu CNN (MobileNetV2, ResNet18) thể hiện khả năng tổng quát hóa và độ ổn định vượt trội trước hiện tượng lệch phân phối dữ liệu (domain shift) so với phương pháp trích xuất đặc trưng kết cấu truyền thống LBP-SVM.
2. **LBP-SVM dễ bị overfitting:** Mặc dù LBP-SVM đạt kết quả rất tốt trên tập phát triển (ACER 10.97%), nó bị sụt giảm hiệu năng thảm hại trên tập kiểm thử (ACER 32.71%) do độ nhạy cảm quá lớn của đặc trưng texture thủ công trước sự thay đổi của thiết bị camera và điều kiện chiếu sáng. Đặc biệt, sai số BPCER lên tới 60.00% của LBP-SVM là không thể chấp nhận được trong các ứng dụng thực tế.
3. **Tầm quan trọng của Fine-tuning:** Việc đóng băng toàn bộ backbone ImageNet và chỉ huấn luyện head phân loại (E03) là chưa đủ để bắt được các dấu hiệu giả mạo tinh vi. Việc giải đóng băng và tinh chỉnh riêng `layer4` của ResNet18 với tốc độ học nhỏ (E04) giúp cải thiện bứt phá hiệu năng, giảm ACER tập Test xuống còn **14.79%** và nâng cao tính cân bằng lỗi giữa APCER và BPCER.
4. **Sự đánh đổi tài nguyên:** LBP-SVM cực kỳ gọn nhẹ (kích thước chỉ ~22 KB, không cần GPU) phù hợp cho các hệ thống nhúng siêu nhỏ. Đối với các hệ thống yêu cầu độ an toàn cao, ResNet18 là lựa chọn tối ưu nhờ tốc độ suy luận trên GPU rất nhanh (1.595 ms) và hiệu năng PAD vượt trội.

## 8.2 Hướng phát triển tiếp theo
Để nâng cao hiệu năng và đưa mô hình vào ứng dụng thực tế, các hướng nghiên cứu tiếp theo cần tập trung vào:

1. **Giám sát mức độ pixel (Pixel-wise Auxiliary Supervision):** Thiết kế mạng CNN có hai đầu ra (multi-head): một đầu ra phân loại nhị phân và một đầu ra dự đoán bản đồ độ sâu khuôn mặt 3D (Depth Map Regression) để ép mạng học các đặc trưng hình học 3D của khuôn mặt thật.
2. **Mô hình hóa chuỗi thời gian (Temporal Modeling):** Sử dụng mạng hồi quy LSTM, GRU hoặc Transformer (ViT) kết hợp với CNN để học các đặc trưng chuyển động liên tục của khuôn mặt và phát hiện các nhiễu nhấp nháy (flicker) tần số cao của thiết bị phát lại video.
3. **Toán tử tích chập cải tiến (Central Difference Convolution - CDC):** Thay thế các lớp tích chập thông thường ở các tầng đầu của ResNet bằng CDC để nâng cao năng lực trích xuất đặc trưng gradient kết cấu vi mô, tăng độ robust trước sự biến thiên ánh sáng.
4. **Tăng cường dữ liệu nâng cao (Advanced Augmentation):** Tích hợp các kỹ thuật tăng cường dữ liệu mạnh mẽ như Random Erasing, Cutout, Color Jittering mạnh (độ tương phản, độ bão hòa màu) và mô phỏng nhiễu moiré kỹ thuật số để nâng cao tính robust của mô hình.
5. **Thích ứng tên miền chủ động (Domain Adaptation):** Áp dụng thuật toán Domain Adversarial Neural Networks (DANN) để trích xuất các đặc trưng bất biến với thiết bị di động, hướng tới việc vượt qua các giao thức khó hơn như Protocol 3 và 4 của OULU-NPU.
6. **Đánh giá đa Protocol và đa Seed:** Mở rộng thực nghiệm trên toàn bộ 4 protocols của OULU-NPU và chạy huấn luyện 5-seed để thu được các kết quả đánh giá thống kê toàn diện.
7. **Nén và Tối ưu hóa mô hình (Model Compression):** Áp dụng kỹ thuật chưng cất tri thức (Knowledge Distillation) để chuyển giao tri thức từ mô hình ResNet18 FT (E04) sang mô hình MobileNetV2 gọn nhẹ, giúp triển khai thời gian thực hiệu quả trên các thiết bị di động có phần cứng hạn chế.
8. **Attention Mechanism (Cơ chế chú ý):** Tích hợp các khối chú ý không gian và kênh (như CBAM, SE-Net) để ép mô hình tập trung vào các vùng ảnh chứa nhiều manh mối giả mạo (như rìa khuôn mặt, mép giấy in, vùng phản xạ ánh sáng) thay vì các vùng nền vô nghĩa.
9. **Khảo sát đa không gian màu:** Trích xuất đặc trưng trên các không gian màu HSV và YCbCr thay vì chỉ dùng ảnh xám (LBP) hoặc RGB (CNN) để tận dụng sự khác biệt phổ màu sắc của da người thật.
10. **Đánh giá chéo tập dữ liệu (Cross-dataset Evaluation):** Huấn luyện mô hình trên OULU-NPU và đánh giá trực tiếp trên các tập dữ liệu khác như CASIA-FASD hoặc Replay-Attack để kiểm tra năng lực vận hành trong môi trường thực tế hoàn toàn mới.

---

# TÀI LIỆU THAM KHẢO

1. Stan Z. Li & Anil K. Jain, *Handbook of Face Recognition*, 2nd Edition, Springer, 2011.
2. Anil K. Jain, Patrick Flynn & Arun A. Ross, *Handbook of Biometrics*, Springer, 2008.
3. Paul Viola & Michael Jones, "Rapid Object Detection using a Boosted Cascade of Simple Features", *IEEE Conference on Computer Vision and Pattern Recognition (CVPR)*, 2001.
4. Navneet Dalal & Bill Triggs, "Histograms of Oriented Gradients for Human Detection", *IEEE Conference on Computer Vision and Pattern Recognition (CVPR)*, 2005.
5. Kaipeng Zhang, Zhanpeng Zhang, Zhifeng Li & Yu Qiao, "Joint Face Detection and Alignment Using Multitask Cascaded Convolutional Networks", *IEEE Signal Processing Letters*, Vol. 23, No. 10, pp. 1499-1503, 2016.
6. Valentin Bazarevsky, Yury Kartynnik, Andrey Vakunov, Karthik Raveendran & Matthias Grundmann, "BlazeFace: Sub-millisecond Neural Face Detector on Mobile GPUs", *arXiv preprint arXiv:1907.05047*, 2019.
7. Timo Ojala, Matti Pietikäinen & Topi Mäenpää, "Multiresolution Gray-Scale and Rotation Invariant Texture Classification with Local Binary Patterns", *IEEE Transactions on Pattern Analysis and Machine Intelligence (TPAMI)*, Vol. 24, No. 7, pp. 971-987, 2002.
8. Jukka Määttä, Abdenour Hadid & Matti Pietikäinen, "Face Spoofing Detection From Single Image Using Micro-Texture Analysis", *IEEE International Joint Conference on Biometrics (IJCB)*, 2011.
9. Kaiming He, Xiangyu Zhang, Shaoqing Ren & Jian Sun, "Deep Residual Learning for Image Recognition", *IEEE Conference on Computer Vision and Pattern Recognition (CVPR)*, 2016.
10. Mark Sandler, Andrew Howard, Menglong Zhu, Andrey Zhmoginov & Liang-Chieh Chen, "MobileNetV2: Inverted Residuals and Linear Bottlenecks", *IEEE Conference on Computer Vision and Pattern Recognition (CVPR)*, 2018.
11. Zinelabidine Boulkenafet, Jukka Komulainen, Lei Li, Xiaobing Feng & Abdenour Hadid, "OULU-NPU: A Mobile Face Presentation Attack Database with Four Protocols", *IEEE International Conference on Automatic Face and Gesture Recognition (FG)*, 2017.
12. Anjith George & Sebastien Marcel, "Deep Pixels: Algorithms for Biometric Presentation Attack Detection", *IEEE Transactions on Information Forensics and Security*, 2019.
13. Zitong Yu, Chenxu Zhao, Zehua Wang, Yunxiao Qin, Zhuo Su, Xiaobing Li, Feng Zhou & Guoying Zhao, "Searching Central Difference Convolutional Networks for Face Anti-Spoofing", *IEEE Conference on Computer Vision and Pattern Recognition (CVPR)*, 2020.
14. Tiêu chuẩn Quốc tế ISO/IEC 30107, *Information technology — Biometric presentation attack detection*, Parts 1, 2, and 3, 2016-2017.

# CHƯƠNG 1: MỞ ĐẦU

## 1.1 Đặt vấn đề
Trong những năm gần đây, công nghệ sinh trắc học khuôn mặt (Face Biometrics) đã trở thành một phần không thể thế trong đời sống số. Từ việc mở khóa điện thoại thông minh (FaceID), xác thực giao dịch tài chính (eKYC) cho đến các hệ thống kiểm soát an ninh quốc gia, nhận dạng khuôn mặt mang lại sự tiện lợi vượt trội so với mật khẩu truyền thống hoặc thẻ từ nhờ đặc tính không tiếp xúc và tính cá nhân hóa cao.

Tuy nhiên, sự phổ biến này cũng đi kèm với các rủi ro bảo mật nghiêm trọng. Do thông tin khuôn mặt dễ dàng bị thu thập công khai (ví dụ qua mạng xã hội), kẻ tấn công có thể dễ dàng chế tạo các mẫu giả mạo khuôn mặt (Presentation Attack Instruments - PAIs) nhằm đánh lừa hệ thống. Các hình thức tấn công phổ biến bao gồm:
- **Tấn công bằng ảnh in (Print Attack):** Sử dụng ảnh chụp khuôn mặt người dùng hợp lệ được in ra giấy (2D).
- **Tấn công phát lại video (Video Replay Attack):** Phát lại video khuôn mặt người dùng hợp lệ trên màn hình điện thoại hoặc máy tính bảng trước camera cảm biến.
- **Tấn công bằng mặt nạ 3D (3D Mask Attack):** Sử dụng mặt nạ silicon hoặc in 3D mô phỏng cấu trúc hình học khuôn mặt người thật.

Nếu không có lớp bảo vệ phát hiện giả mạo khuôn mặt (Face Presentation Attack Detection - PAD, hay thường gọi là Face Anti-Spoofing), các hệ thống nhận dạng danh tính sẽ cực kỳ dễ bị tổn thương. Vì vậy, nghiên cứu các giải pháp Face PAD hiệu quả, có khả năng xử lý thời gian thực và tổng quát hóa tốt trên các thiết bị thu nhận khác nhau là một yêu cầu cấp thiết.

## 1.2 Mục tiêu nghiên cứu
Mục tiêu chính của đề tài này bao gồm:
1. Xây dựng một pipeline phát hiện giả mạo khuôn mặt hoàn chỉnh, có tính tái lập cao dựa trên bộ dữ liệu chuẩn OULU-NPU Protocol 1.
2. Thực hiện so sánh thực nghiệm một cách công bằng và có kiểm soát giữa phương pháp trích xuất đặc trưng texture truyền thống (Local Binary Pattern - LBP kết hợp SVM) và các phương pháp học máy hiện đại dựa trên mạng Nơ-ron tích chập (MobileNetV2, ResNet18).
3. Đánh giá tác động của kỹ thuật tinh chỉnh (Fine-tuning) bán phần trên mạng học sâu (unfreeze `layer4` của ResNet18) so với chỉ huấn luyện lớp phân loại (head-only) đối với khả năng trích xuất các đặc trưng vi cấu trúc phục vụ việc phát hiện giả mạo.
4. Áp dụng nghiêm ngặt các tiêu chuẩn đo lường quốc tế ISO/IEC 30107-3 (bao gồm APCER, BPCER và ACER) để đánh giá hiệu năng hệ thống.

## 1.3 Phạm vi và giới hạn
- **Bộ dữ liệu:** Sử dụng bộ dữ liệu OULU-NPU, tập trung tối đa vào **Protocol 1** nhằm đánh giá khả năng tổng quát hóa của hệ thống dưới sự thay đổi của điều kiện môi trường chiếu sáng và bối cảnh (cross-session).
- **Bài toán phân loại:** Định nghĩa bài toán phân loại nhị phân (Binary Classification) với nhãn lớp dương là mẫu giả mạo (`spoof = 1`) và nhãn lớp âm là mẫu thật (`live = 0`).
- **Mô hình nghiên cứu:** Chỉ tập trung vào 4 cấu hình thí nghiệm được thiết kế sẵn:
  - **E01 (LBP-SVM):** Trích xuất đặc trưng LBP trên ảnh xám và phân loại bằng Linear SVM.
  - **E02 (MobileNetV2):** Đóng băng backbone MobileNetV2 pretrained ImageNet, chỉ huấn luyện classifier head.
  - **E03 (ResNet18):** Đóng băng backbone ResNet18 pretrained ImageNet, chỉ huấn luyện classifier head.
  - **E04 (ResNet18 Fine-tune):** Mở đóng băng `layer4` của ResNet18 để tinh chỉnh với learning rate nhỏ, kết hợp huấn luyện head.
- **Giới hạn:** Đề tài không đi sâu vào các cấu trúc temporal (mạng LSTM/Transformer xử lý video dài), không thực hiện kiểm tra chéo tập dữ liệu (cross-dataset) và giới hạn đánh giá trên một seed cố định (seed = 42).

## 1.4 Bố cục báo cáo
Báo cáo nghiên cứu được chia làm 8 chương chính:
- **Chương 1: Mở đầu:** Giới thiệu bối cảnh, mục tiêu và phạm vi đề tài.
- **Chương 2: Cơ sở lý thuyết - Phát hiện và nhận dạng khuôn mặt:** Trình bày chi tiết toán học và cơ chế hoạt động của các thuật toán face detection, face alignment và các mô hình trích xuất đặc trưng từ truyền thống đến học sâu.
- **Chương 3: Lý thuyết phát hiện lừa đối khuôn mặt:** Khảo sát taxonomy tấn công, các phương pháp anti-spoofing và tiêu chuẩn ISO/IEC 30107-3.
- **Chương 4: Bộ dữ liệu OULU-NPU:** Phân tích cấu trúc dữ liệu, các giao thức (protocols) đánh giá.
- **Chương 5: Phương pháp đề xuất:** Mô tả chi tiết thiết kế hệ thống, các thí nghiệm từ E01 đến E04.
- **Chương 6: Kết quả thực nghiệm:** Trình bày kết quả số liệu, phân tích lỗi và benchmark tài nguyên.
- **Chương 7: Thảo luận:** So sánh đối chiếu các phương pháp, phân tích hiện tượng lệch tên miền (domain shift).
- **Chương 8: Kết luận và hướng phát triển:** Đánh giá tổng kết và mở ra các hướng nghiên cứu tiếp theo.

---

# CHƯƠNG 4: BỘ DỮ LIỆU OULU-NPU

## 4.1 Giới thiệu bộ dữ liệu
Bộ dữ liệu **OULU-NPU** (Boulkenafet et al., 2017) là một trong những tập dữ liệu chuẩn (benchmark) phổ biến nhất thế giới được thiết kế chuyên biệt cho bài toán phát hiện giả mạo khuôn mặt trên thiết bị di động.

Đặc điểm chi tiết của bộ dữ liệu:
- **Số lượng đối tượng (Subjects):** 55 người tham gia ghi hình.
- **Thiết bị thu nhận (Devices):** Sử dụng camera trước của 6 điện thoại thông minh phổ thông có chất lượng cảm biến hoàn toàn khác nhau để quay video độ phân giải Full HD (1080p):
  1. Samsung Galaxy S6 Edge (Phone 1)
  2. HTC Desire EYE (Phone 2)
  3. MEIZU X5 (Phone 3)
  4. ASUS Zenfone Selfie (Phone 4)
  5. Sony XPERIA C5 Ultra Dual (Phone 5)
  6. OPPO N3 (Phone 6)
- **Điều kiện môi trường (Sessions):** Video được quay trong 3 session khác nhau với sự thay đổi lớn về cường độ ánh sáng, nhiệt độ màu và bối cảnh phông nền phía sau.
- **Công cụ giả mạo (PAIs):**
  - **Print Attacks:** Sử dụng ảnh chân dung độ phân giải cao chụp bởi camera sau của điện thoại Oppo N3, được in ra bằng hai thiết bị in chuyên dụng:
    - Printer 1: Máy in phun màu chuyên nghiệp Epson Artisan 1430.
    - Printer 2: Máy in laser màu văn phòng Konica Minolta bizhub C224e.
  - **Replay Attacks:** Phát lại các video mẫu quay bởi điện thoại Oppo N3 trên hai màn hình hiển thị:
    - Display 1: Màn hình điện thoại Oppo N3 (kích thước nhỏ, mật độ pixel cao).
    - Display 2: Màn hình Macbook Pro 13" Retina (kích thước lớn).
- **Tổng số video:** 5,940 video clips ngắn (mỗi video dài khoảng 20 giây, định dạng AVI).

## 4.2 Bốn protocol đánh giá của OULU-NPU
OULU-NPU định nghĩa sẵn 4 giao thức đánh giá chuẩn để kiểm tra tính tổng quát hóa của các mô hình chống giả mạo dưới các thách thức thực tế khác nhau:

- **Protocol 1 (Cross-Session):** Đánh giá khả năng tổng quát hóa của mô hình trước sự thay đổi của điều kiện môi trường chiếu sáng và bối cảnh phông nền. Tập huấn luyện, phát triển và kiểm thử được quay ở các session khác nhau nhưng sử dụng chung nhóm 6 điện thoại và các thiết bị in/hiển thị.
- **Protocol 2 (Cross-Attack):** Đánh giá khả năng phát hiện các dạng công cụ tấn công chưa từng thấy trong quá trình huấn luyện (ví dụ: huấn luyện chỉ với Print Attack, kiểm thử với Replay Attack).
- **Protocol 3 (Cross-Device):** Đánh giá khả năng hoạt động ổn định trên các camera của điện thoại mới chưa từng được sử dụng để quay dữ liệu huấn luyện (Leave-One-Camera-Out).
- **Protocol 4 (Combined):** Tổng hợp tất cả các thách thức trên cùng một lúc: thay đổi session, thay đổi công cụ tấn công và thay đổi thiết bị di động. Đây là protocol khó nhất và gần với thực tế triển khai nhất.

## 4.3 Protocol 1 chi tiết
Trong nghiên cứu này, chúng tôi tập trung tối đa vào **Protocol 1** để xây dựng các baseline vững chắc. Phân chia tập dữ liệu chính thức của Protocol 1 được thực hiện nghiêm ngặt theo danh tính đối tượng (Subject-disjoint) để chống rò rỉ thông tin người dùng:
- **Tập huấn luyện (Train Set):** Subjects từ 1 đến 20 (gồm 240 video live và 960 video spoof $\Rightarrow$ tổng 1,200 video).
- **Tập phát triển (Dev Set):** Subjects từ 21 đến 35 (gồm 180 video live và 720 video spoof $\Rightarrow$ tổng 900 video).
- **Tập kiểm thử (Test Set):** Subjects từ 36 đến 55 (gồm 120 video live và 480 video spoof $\Rightarrow$ tổng 600 video).

Tất cả các video trong Protocol 1 đều được sử dụng đầy đủ 6 điện thoại. Sự phân chia rõ ràng này đảm bảo rằng không có bất kỳ thông tin nào về danh tính của người dùng trong tập Test xuất hiện trong tập Train hay Dev.

## 4.4 So sánh với các bộ dữ liệu khác
Bảng so sánh tổng quan giữa OULU-NPU và các bộ dữ liệu khuôn mặt phổ biến khác:

| Dataset | Năm | Subjects | Cảm biến | Các dạng tấn công | Đặc điểm nổi bật |
|---|---|---|---|---|---|
| **CASIA-FASD** | 2012 | 50 | Webcam, IP Cam | Print (cut-eye), Replay | Đơn giản, độ phân giải thấp |
| **Replay-Attack** | 2012 | 50 | Webcam | Print, Replay (iPad) | Chiếu sáng cố định trong nhà |
| **MSU-MFSD** | 2015 | 35 | Mobile, Laptop | Print, Replay | Số lượng mẫu nhỏ |
| **OULU-NPU** | 2017 | 55 | 6 Smartphones | Print (2 types), Replay (2 displays) | Quy trình chuẩn hóa cao, thiết bị di động đa dạng |
| **SiW** | 2018 | 165 | Camera chất lượng cao | Print, Replay | Biến thiên góc mặt lớn |

OULU-NPU được lựa chọn làm tập dữ liệu nghiên cứu chính vì nó mô phỏng hoàn hảo kịch bản sử dụng thực tế của các ứng dụng di động ngày nay (camera trước smartphone, góc nhìn chính diện cự ly gần, ánh sáng phòng hoặc ánh sáng tự nhiên thay đổi liên tục), đồng thời cung cấp một giao thức Protocol 1 kiểm chứng khả năng vượt qua sự lệch pha chiếu sáng cực kỳ chặt chẽ.

# CHƯƠNG 5: PHƯƠNG PHÁP ĐỀ XUẤT

## 5.1 Pipeline tổng thể
Hệ thống phát hiện giả mạo khuôn mặt được thiết kế theo một pipeline xử lý video đồng nhất, đảm bảo tính công bằng và so sánh trực tiếp giữa các mô hình phân loại. Sơ đồ luồng xử lý tổng thể của hệ thống:

```text
       Video Đầu Vào (.avi)
                ↓
       [Trích Frame Đồng Nhất] (10 frames/video)
                ↓
       [Phát Hiện Khuôn Mặt] (MediaPipe BlazeFace)
                ↓
       [Tiền Xử Lý & Cắt Mặt] (20% margin, square crop, resize 256x256)
                ↓
       ┌───────────────────────────────┬────────────────────────────────┐
       │   Nhánh 1: LBP-SVM (E01)      │    Nhánh 2: Học Sâu (E02-E04)   │
       │                               │                                │
       │  - Đổi màu xám (Grayscale)    │   - Giữ nguyên ảnh màu RGB     │
       │  - Resize về 128x128 pixel    │   - Resize về 224x224 pixel    │
       │  - Trích Uniform LBP (8x8 grid│   - ImageNet Normalization     │
       │  - Vector đặc trưng 640-dim   │   - Trực tiếp nạp vào CNN      │
       │  - Phân loại bằng Linear SVM  │   - Tính xác suất bằng Sigmoid │
       └──────────────┬────────────────┴────────────────┬───────────────┘
                      │                                 │
                      └─────────────────┬───────────────┘
                                        ↓
                         [Gộp Điểm Số Cấp Video] (Mean score)
                                        ↓
                         [Áp Dụng Ngưỡng Quyết Định] (Dev-locked threshold)
                                        ↓
                         Quyết Định Cuối Cùng: Live / Spoof
```

Nguyên tắc hoạt động then chốt là toàn bộ dữ liệu tiền xử lý (ảnh cắt khuôn mặt) được lưu trữ vào cache dùng chung trước khi nạp vào các mô hình khác nhau. Không có bất kỳ sự thay đổi hay hậu xử lý riêng biệt nào về vùng mặt giữa các thí nghiệm nhằm loại trừ sai số do bước tiền xử lý gây ra.

## 5.2 Tiền xử lý dữ liệu
### 1. Trích xuất Frame đồng nhất (Frame Sampling)
Mỗi video trong OULU-NPU Protocol 1 có số lượng frame khác nhau tùy thuộc vào thời lượng ghi hình thực tế. Để đảm bảo tính đồng nhất và giảm tải chi phí tính toán, hệ thống trích xuất cố định **10 frame** từ mỗi video. Thuật toán lấy mẫu phân bố đều theo trục thời gian, sử dụng các phép tính số nguyên để đảm bảo tính tái lập:
$$\text{indices} = \left[ \left\lfloor \frac{i \cdot (T - 1)}{K - 1} + 0.5 \right\rfloor \right] \quad \text{với } i = 0, 1, ..., K-1$$
Trong đó $T$ là tổng số frame của video, $K = 10$ là số frame cần lấy. Công thức này đảm bảo frame đầu tiên ($idx = 0$) và frame cuối cùng ($idx = T-1$) luôn được đưa vào tập mẫu.

### 2. Phát hiện khuôn mặt bằng MediaPipe BlazeFace
Hệ thống sử dụng bộ phát hiện MediaPipe Face Detection với cấu hình `model_selection=0` (tối ưu hóa cho các khoảng cách cự ly gần dưới 2 mét). Chiến lược phát hiện nâng cao bao gồm:
- **Bước 1:** Đọc frame ảnh RGB. Nếu kích thước ảnh lớn, ảnh được thu nhỏ tạm thời về chiều dài cạnh tối đa `max_side = 640` pixel để tăng tốc độ xử lý của mô hình phát hiện.
- **Bước 2:** Chạy bộ phát hiện. Nếu tìm thấy khuôn mặt, trích xuất bounding box ban đầu.
- **Bước 3 (Dự phòng):** Nếu không tìm thấy khuôn mặt ở ảnh thu nhỏ, hệ thống chạy lại bộ phát hiện trên ảnh gốc Full HD để tìm kiếm các đặc trưng nhỏ hơn.

### 3. Cắt và Chuẩn hóa hình học khuôn mặt
Từ bounding box phát hiện, thực hiện các bước:
- Tính tâm và chuyển đổi bounding box về dạng hình vuông để tránh làm biến dạng tỷ lệ khuôn mặt khi resize.
- Áp dụng hệ số mở rộng **margin = 0.2 (20%)** về mỗi phía để bao phủ thêm các vùng rìa khuôn mặt (tai, tóc, cổ).
- Thực hiện cắt ảnh (cropping), áp dụng hàm clip để xử lý các vùng vượt ngoài biên ảnh.
- Sử dụng thuật toán nội suy vùng diện tích `cv2.INTER_AREA` để resize ảnh cắt về kích thước lưu trữ $256 \times 256$ pixel, nén không mất mát định dạng PNG.
- **Tỷ lệ phát hiện:** Pipeline đạt tỷ lệ crop thành công là **99.9963%** (chỉ có duy nhất 1 frame đầu tiên của video `3_1_28_4__00` thuộc tập Dev không tìm thấy khuôn mặt và được đánh dấu là `no_face`).

## 5.3 Thí nghiệm E01: LBP-SVM (Handcrafted Baseline)
Thí nghiệm E01 đại diện cho phương pháp truyền thống sử dụng đặc trưng texture thủ công kết hợp bộ phân loại cổ điển.

- **Tiền xử lý đầu vào:** Đọc ảnh khuôn mặt $256 \times 256$ từ cache, chuyển đổi sang ảnh mức xám (grayscale) và resize về kích thước $128 \times 128$ pixel bằng thuật toán nội suy `cv2.INTER_AREA`.
- **Trích xuất đặc trưng LBP:** Sử dụng thuật toán Uniform Local Binary Pattern với bán kính $R=1$ và số láng giềng $P=8$.
- **Spatial Grid:** Chia ảnh $128 \times 128$ thành lưới $8 \times 8$ ô (mỗi ô kích thước $16 \times 16$ pixel).
- Tại mỗi ô, tính toán biểu đồ tần suất Uniform LBP gồm 10 bin (9 bin uniform + 1 bin non-uniform). Biểu đồ được chuẩn hóa L1 tại từng ô.
- Nối các biểu đồ ô tạo thành vector đặc trưng **640 chiều** ($8 \times 8 \times 10$).
- **Bộ phân loại:** Sử dụng `StandardScaler` để chuẩn hóa z-score (trung bình bằng 0, độ lệch chuẩn bằng 1) dựa trên các tham số học từ tập Train. Phân loại bằng mô hình `sklearn.svm.LinearSVC` với hàm phạt squared hinge loss và điều chỉnh trọng số lớp cân bằng (`class_weight='balanced'`).
- **Lựa chọn siêu tham số:** Thực hiện tìm kiếm lưới (grid search) giá trị $C$ trong tập $\{10^{-4}, 10^{-3}, 10^{-2}, 10^{-1}, 1.0, 10.0\}$ trên tập Dev.
- **Kết quả:** Siêu tham số tối ưu đạt được là **$C = 0.0001$**. Ngưỡng phân loại tối ưu chọn trên Dev là $\theta_{e01} = -0.410$.

## 5.4 Thí nghiệm E02: MobileNetV2 Transfer Learning
Thí nghiệm E02 kiểm thử khả năng trích xuất đặc trưng của một CNN gọn nhẹ dưới cấu hình đóng băng backbone.

- **Kiến trúc:** Sử dụng MobileNetV2 với trọng số pretrained từ ImageNet (`IMAGENET1K_V2`).
- **Classifier Head:** Thay thế lớp classifier cuối cùng bằng một lớp tuyến tính mới `nn.Linear(1280, 1)`, khởi tạo trọng số theo phân phối chuẩn $\mathcal{N}(0, 0.01)$ và bias bằng 0. Thêm lớp `nn.Dropout(p=0.2)` phía trước.
- **Đóng băng (Freeze):** Đóng băng toàn bộ các lớp tích chập của backbone MobileNetV2. Lớp BatchNorm được khóa cứng ở chế độ đánh giá (`eval()`) trong suốt quá trình huấn luyện để đảm bảo không bị sai lệch phân phối batch. Số lượng tham số huấn luyện là **1,281 tham số** (chỉ có lớp tuyến tính cuối).
- **Tiền xử lý đầu vào:** Resize ảnh màu RGB về $224 \times 224$ pixel, chuẩn hóa ImageNet (mean và std chuẩn).
- **Tăng cường dữ liệu (Augmentation):** Áp dụng lật ngang ngẫu nhiên (`RandomHorizontalFlip`, $p=0.5$) chỉ trên tập Train.
- **Hàm mất mát:** `BCEWithLogitsLoss` với trọng số cân bằng lớp `pos_weight = 0.25` (do tỷ lệ spoof:live là 4:1).
- **Huấn luyện:** Bộ tối ưu hóa Adam với learning rate $\eta = 10^{-4}$, weight decay $10^{-4}$. Huấn luyện tối đa 15 epoch, kích thước batch bằng 16. Sử dụng cơ chế early stopping dựa trên ACER tập Dev với patience bằng 3.
- **Kết quả:** Best checkpoint đạt được tại **epoch 15**. Ngưỡng phân loại tối ưu chọn trên Dev là $\theta_{e02} = 0.598$.

## 5.5 Thí nghiệm E03: ResNet18 Transfer Learning
Thí nghiệm E03 sử dụng mạng ResNet18 với cấu trúc residual làm baseline học sâu tiêu chuẩn.

- **Kiến trúc:** ResNet18 với trọng số pretrained ImageNet (`IMAGENET1K_V1`).
- **Classifier Head:** Thay thế lớp fully connected cuối (`resnet.fc`) bằng một lớp tuyến tính mới `nn.Linear(512, 1)`, khởi tạo tương tự E02.
- **Đóng băng:** Đóng băng toàn bộ backbone, chỉ cho phép cập nhật **513 tham số** của classifier head. Lớp BatchNorm đóng băng tương tự E02.
- **Tham số huấn luyện:** Hoàn toàn đồng nhất với cấu hình huấn luyện của E02 (Adam, lr $10^{-4}$, batch size 16, pos_weight 0.25).
- **Kết quả:** Best checkpoint đạt được tại **epoch 15**. Ngưỡng phân loại tối ưu chọn trên Dev là $\theta_{e03} = 0.521$.

## 5.6 Thí nghiệm E04: ResNet18 Fine-tune Layer4 (Ablation Study)
Thí nghiệm E04 là một nghiên cứu cắt bỏ nhằm kiểm chứng giả thuyết: việc đóng băng toàn bộ backbone ImageNet giới hạn khả năng trích xuất các đặc trưng vi kết cấu chuyên biệt của presentation attacks.

- **Cấu hình:** Giữ nguyên kiến trúc của E03 nhưng giải đóng băng **`layer4`** của ResNet18 cùng với tất cả các lớp BatchNorm thuộc layer4 đó. Lớp classifier head vẫn cho phép huấn luyện. Các layers phía trước (`layer1`, `layer2`, `layer3`) vẫn được đóng băng hoàn toàn.
- **Số lượng tham số huấn luyện:** Tăng vọt lên **8,394,241 tham số** (so với 513 tham số của E03).
- **Tối ưu hóa với tốc độ học vi phân (Differential Learning Rates):** Để tránh hiện tượng phá hủy các đặc trưng pretrained tốt và hạn chế overfitting, chúng tôi áp dụng tốc độ học khác nhau cho các nhóm tham số:
  - Tốc độ học của backbone `layer4`: $\eta_{backbone} = 10^{-5}$ (nhỏ hơn 10 lần).
  - Tốc độ học của classifier head: $\eta_{head} = 10^{-4}$.
- **Huấn luyện:** Tăng tối đa epoch lên 20, các tham số khác giữ nguyên.
- **Kết quả:** Nhờ có dung lượng mô hình lớn hơn, mô hình hội tụ nhanh chóng. Best checkpoint đạt được tại **epoch 6**, early stopping dừng huấn luyện ở epoch 9. Ngưỡng phân loại tối ưu chọn trên Dev là $\theta_{e04} = 0.593$.

## 5.7 Chiến lược đánh giá và gộp video-level
1. **Frame-level Inference:** Mỗi frame thứ $i$ trong video nhận được một điểm số dự đoán $s_i$ từ mô hình (với LBP-SVM là khoảng cách margin từ `decision_function`, với CNN là xác suất sau hàm sigmoid).
2. **Video-level Aggregation:** Gộp điểm số các frame để đưa ra điểm số đại diện cho video $s_{video}$ bằng phương pháp lấy trung bình cộng:
   $$s_{video} = \frac{1}{K} \sum_{i=1}^K s_i \quad (\text{với } K=10)$$
3. **Quyết định:** So sánh $s_{video}$ với ngưỡng tối ưu $\theta$ được chọn và khóa từ tập Dev. Nếu $s_{video} \geq \theta$ kết luận video là Spoof ($1$), ngược lại là Live ($0$).

---
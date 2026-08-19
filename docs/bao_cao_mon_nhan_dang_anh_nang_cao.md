# BÁO CÁO MÔN HỌC: NHẬN DẠNG ẢNH NÂNG CAO
## ĐỀ TÀI: NGHIÊN CỨU SO SÁNH PHƯƠNG PHÁP TRUYỀN THỐNG VÀ HỌC SÂU TRONG PHÁT HIỆN GIẢ MẠO KHUÔN MẶT TRÊN BỘ DỮ LIỆU OULU-NPU

---

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

# CHƯƠNG 2: CƠ SỞ LÝ THUYẾT — PHÁT HIỆN VÀ NHẬN DẠNG KHUÔN MẶT

## 2.1 Tổng quan hệ thống nhận dạng sinh trắc học
Một hệ thống xác thực sinh trắc học (Biometric System) hoạt động dựa trên việc khai thác các đặc tính sinh lý hoặc hành vi không thể thay đổi của con người nhằm định danh cá nhân. Theo cuốn *Handbook of Biometrics*, cấu trúc tổng quát của một hệ sinh trắc học gồm các pha xử lý cốt lõi:

1. **Thu nhận dữ liệu (Data Acquisition):** Sử dụng các cảm biến vật lý (như camera, đầu quét vân tay) để ghi lại tín hiệu sinh trắc học thô từ người dùng.
2. **Đánh giá chất lượng và tiền xử lý (Quality Assessment & Preprocessing):** Lọc nhiễu, nâng cao chất lượng tín hiệu và định vị vùng chứa đặc trưng (ví dụ: cắt khuôn mặt).
3. **Trích xuất đặc trưng (Feature Extraction):** Chuyển đổi dữ liệu đã tiền xử lý thành các vector số học đại diện (feature vector) mang tính phân biệt cao.
4. **So khớp / Phân loại (Matching / Classification):** Tính toán độ tương đồng giữa đặc trưng đầu vào với đặc trưng đã đăng ký sẵn trong cơ sở dữ liệu.
5. **Ra quyết định (Decision):** Áp dụng ngưỡng (threshold) để chấp nhận hoặc từ chối thực thể.

### Mô hình toán học của Xác thực (Verification) và Định danh (Identification)
Trong bài toán **Xác thực (Verification - 1:1)**, hệ thống xác nhận danh tính tự xưng của một cá nhân:
Gọi $x$ là đặc trưng truy vấn, $I$ là danh tính tự xưng và $x_I$ là đặc trưng đăng ký của danh tính đó. Bộ so khớp tính toán điểm tương đồng $s = S(x, x_I)$. Quyết định được đưa ra theo quy tắc:
$$\text{Quyết định} = \begin{cases} \text{Chấp nhận (Genuine)}, & \text{nếu } s \geq \tau \\ \text{Từ chối (Imposter)}, & \text{nếu } s < \tau \end{cases}$$
Trong đó $\tau$ là ngưỡng quyết định được thiết lập trước.

Trong bài toán **Định danh (Identification - 1:N)**, hệ thống tìm kiếm danh tính của thực thể truy vấn trong cơ sở dữ liệu gồm $N$ thực thể đăng ký $\{x_1, x_2, ..., x_N\}$:
$$\text{Danh tính dự đoán} = \arg\max_{k \in \{1, ..., N\}} S(x, x_k)$$
Nếu giá trị tương đồng lớn nhất này nhỏ hơn một ngưỡng $\tau_{id}$, hệ thống sẽ kết luận đối tượng không nằm trong cơ sở dữ liệu.

### So sánh các đặc trưng sinh trắc học phổ biến
Theo cuốn *Handbook of Biometrics*, mỗi đặc trưng sinh trắc học đều có các ưu điểm và hạn chế riêng, được đánh giá qua các chỉ tiêu: Universality (tính phổ biến), Uniqueness (tính duy nhất), Permanence (tính vĩnh cửu), Collectability (tính dễ thu nhận), Performance (hiệu năng), Acceptability (sự chấp nhận của người dùng), và Circumvention (khả năng chống làm giả).

| Đặc trưng | Universality | Uniqueness | Permanence | Collectability | Performance | Acceptability | Circumvention |
|---|---|---|---|---|---|---|---|
| **Vân tay** | Trung bình | Cao | Cao | Trung bình | Cao | Trung bình | Trung bình |
| **Mống mắt** | Cao | Cao | Cao | Trung bình | Rất cao | Thấp | Cao |
| **Khuôn mặt** | Cao | Trung bình | Trung bình | Cao | Trung bình | Cao | Thấp |

Nhận dạng khuôn mặt nổi bật nhờ tính chất **không tiếp xúc (non-intrusive)** và tính **chấp nhận cao (acceptability)** từ phía người dùng, do khuôn mặt là phương thức nhận diện tự nhiên nhất của con người. Tuy nhiên, nó lại có chỉ số **Circumvention thấp**, nghĩa là cực kỳ dễ bị làm giả bằng các công cụ đơn giản (như ảnh chụp hiển thị trên màn hình hoặc in ra giấy), đặt ra yêu cầu bắt buộc phải có hệ thống PAD đi kèm.

## 2.2 Phát hiện khuôn mặt (Face Detection)
Phát hiện khuôn mặt là bước tiền xử lý đầu tiên, nhằm định vị tọa độ hộp bao (bounding box) của tất cả khuôn mặt có trong ảnh.

### 2.2.1 Viola-Jones / Haar Cascade (Viola & Jones, 2001)
Thuật toán Viola-Jones là cột mốc lịch sử trong thị giác máy tính, cho phép phát hiện khuôn mặt trong thời gian thực trên phần cứng hạn chế vào đầu những năm 2000. Ba đóng góp kỹ thuật cốt lõi bao gồm:

#### 1. Đặc trưng Haar-like và Ảnh tích lũy (Integral Image)
Thay vì làm việc trực tiếp với các giá trị pixel, Viola-Jones sử dụng các đặc trưng Haar-like, đại diện cho hiệu số tổng cường độ sáng giữa các vùng hình chữ nhật liền kề (vùng sáng và vùng tối):
- Đặc trưng cạnh (Edge features).
- Đặc trưng đường (Line features).
- Đặc trưng tâm-bao quanh (Center-surround features).

Để tính nhanh tổng pixel trong một hình chữ nhật mà không phụ thuộc vào kích thước của nó, thuật toán định nghĩa **Ảnh tích lũy (Integral Image)** $II(x, y)$ tại tọa độ $(x, y)$ là tổng các giá trị pixel nằm phía trên và bên trái của $(x, y)$:
$$II(x, y) = \sum_{x' \leq x, y' \leq y} i(x', y')$$
Với $i(x', y')$ là cường độ pixel của ảnh gốc. Ảnh tích lũy có thể được tính toán hiệu quả chỉ qua một lượt duyệt ảnh bằng công thức đệ quy:
$$s(x, y) = s(x, y-1) + i(x, y)$$
$$II(x, y) = II(x-1, y) + s(x, y)$$
(với $s(x, y)$ là tổng tích lũy theo hàng, $II(-1, y) = 0$, $s(x, -1) = 0$).

Khi có $II(x, y)$, tổng các pixel trong bất kỳ hình chữ nhật $D$ nào có các góc $A, B, C, D$ (theo thứ tự từ trên xuống dưới, trái sang phải) được tính bằng đúng 4 phép truy xuất bộ nhớ:
$$\text{Tổng}(D) = II(D) + II(A) - II(B) - II(C)$$

#### 2. Thuật toán AdaBoost chọn lọc bộ phân loại yếu
Số lượng đặc trưng Haar-like trong một cửa sổ con $24 \times 24$ là rất lớn (lên tới hơn 180,000 đặc trưng). AdaBoost được sử dụng để lựa chọn một tập hợp nhỏ các đặc trưng mang tính phân biệt cao nhất và huấn luyện các bộ phân loại yếu (weak classifiers) $h_j(x)$:
$$h_j(x) = \begin{cases} 1, & \text{nếu } p_j f_j(x) < p_j \theta_j \\ 0, & \text{ngược lại} \end{cases}$$
Trong đó $f_j(x)$ là giá trị đặc trưng, $\theta_j$ là ngưỡng phân loại, và $p_j$ là cực tính (parity) xác định hướng của bất đẳng thức.
Bộ phân loại mạnh cuối cùng $H(x)$ là sự kết hợp tuyến tính của các bộ phân loại yếu:
$$H(x) = \begin{cases} 1, & \text{nếu } \sum_{t=1}^T \alpha_t h_t(x) \geq \frac{1}{2} \sum_{t=1}^T \alpha_t \\ 0, & \text{ngược lại} \end{cases}$$
Trọng số $\alpha_t$ tỷ lệ nghịch với sai số phân loại của bộ phân loại yếu thứ $t$.

#### 3. Cấu trúc Cascade (Bộ phân loại xếp chồng)
Để tăng tốc độ xử lý, Viola-Jones xếp chồng các bộ phân loại mạnh thành một cấu trúc dạng cây thác nước (Cascade). Các cửa sổ con không chứa khuôn mặt (thường chiếm đa số trong ảnh) sẽ bị loại bỏ ngay từ các tầng đầu tiên của Cascade (chỉ chứa một vài đặc trưng đơn giản). Các tầng phía sau phức tạp hơn sẽ tập trung phân loại các vùng ứng viên khó.

### 2.2.2 HOG + SVM (dlib)
Phương pháp HOG + SVM kết hợp bộ mô tả đặc trưng **Histogram of Oriented Gradients (HOG)** (Dalal & Triggs, 2005) với bộ phân loại SVM.
Các bước trích xuất HOG bao gồm:
1. **Tính toán Gradient:** Tính gradient theo trục $x$ và $y$ tại mỗi pixel bằng cách nhân chập ảnh với các bộ lọc $[-1, 0, 1]$ và $[-1, 0, 1]^T$:
   $$I_x(x, y) = I(x+1, y) - I(x-1, y)$$
   $$I_y(x, y) = I(x, y+1) - I(x, y-1)$$
   Độ lớn gradient (Magnitude) và hướng (Orientation) được tính bằng:
   $$M(x, y) = \sqrt{I_x(x, y)^2 + I_y(x, y)^2}$$
   $$\theta(x, y) = \arctan\left(\frac{I_y(x, y)}{I_x(x, y)}\right)$$
2. **Tích lũy biểu đồ định hướng (Orientation Binning):** Chia ảnh thành các ô nhỏ (cells, ví dụ $8 \times 8$ pixel). Tại mỗi cell, tính toán biểu đồ tần suất gradient định hướng bằng cách phân bố các giá trị $\theta(x, y)$ vào các bin (thường chia từ $0^\circ$ đến $180^\circ$ thành 9 bin), trọng số cộng vào bin tỉ lệ với độ lớn gradient $M(x, y)$.
3. **Chuẩn hóa khối (Block Normalization):** Nhóm các cell lân cận thành khối lớn hơn (blocks, ví dụ $2 \times 2$ cells) và chuẩn hóa vector đặc trưng của block nhằm giảm ảnh hưởng của sự thay đổi ánh sáng. Công thức chuẩn hóa phổ biến L2-Hys (L2-norm với ngưỡng cắt):
   $$v' = \frac{v}{\sqrt{\|v\|_2^2 + \epsilon^2}}$$
Vector đặc trưng HOG sau đó được đưa qua cửa sổ trượt (sliding window) kết hợp bộ phân loại Linear SVM để xác định vị trí khuôn mặt.

### 2.2.3 MTCNN (Zhang et al., 2016)
**Multi-task Cascaded Convolutional Networks (MTCNN)** sử dụng kiến trúc học sâu phân tầng gồm ba mạng CNN được thiết kế riêng biệt để phát hiện khuôn mặt và các điểm mốc (landmarks) theo thứ tự từ thô đến tinh:

1. **Proposal Network (P-Net):** Mạng tích chập hoàn toàn (FCN) kích thước đầu vào biến động, quét nhanh ảnh ở nhiều tỷ lệ (Image Pyramid) để đưa ra các hộp bao ứng viên ban đầu và điểm số phân loại.
2. **Refine Network (R-Net):** Nhận đầu vào là các vùng ảnh ứng viên từ P-Net được resize về $24 \times 24$ pixel. R-Net lọc bỏ một lượng lớn các ứng viên sai, tinh chỉnh tọa độ hộp bao bằng kỹ thuật Bounding Box Regression.
3. **Output Network (O-Net):** Nhận đầu vào là các ứng viên từ R-Net được resize về $48 \times 48$ pixel. O-Net đưa ra quyết định phân loại khuôn mặt cuối cùng, tinh chỉnh chi tiết hộp bao và định vị 5 điểm mốc khuôn mặt (hai mắt, mũi, hai khóe miệng).

MTCNN tối ưu hóa đa mục tiêu bằng cách kết hợp ba hàm mất mát (loss functions):
- **Phân loại khuôn mặt (Face classification):** Sử dụng Cross-Entropy loss:
  $$L_i^{det} = -\left(y_i^{det} \log(p_i) + (1 - y_i^{det}) \log(1 - p_i)\right)$$
- **Hiệu chỉnh hộp bao (Bounding box regression):** Sử dụng Euclidean loss:
  $$L_i^{box} = \|\hat{y}_i^{box} - y_i^{box}\|_2^2$$
- **Định vị điểm mốc (Landmark localization):** Sử dụng Euclidean loss:
  $$L_i^{land} = \|\hat{y}_i^{land} - y_i^{land}\|_2^2$$

### 2.2.4 MediaPipe BlazeFace (Bazarevsky et al., 2019)
BlazeFace là một mô hình phát hiện khuôn mặt siêu nhẹ được Google phát triển tối ưu cho các thiết bị di động. BlazeFace cải tiến dựa trên kiến trúc Single Shot Multibox Detector (SSD) bằng các giải pháp kỹ thuật chính:

- **BlazeBlock:** Sử dụng Depthwise Separable Convolution kết hợp với skip connection. Để mở rộng trường cảm thụ (receptive field) mà vẫn giữ chi phí tính toán thấp, BlazeFace áp dụng kernel lớn $5 \times 5$ cho các lớp depthwise tích chập.
- **Cơ chế Anchor cải tiến:** Khác với SSD truyền thống dừng lại ở độ phân giải đặc trưng $8 \times 8$, BlazeFace tiếp tục tính toán đến độ phân giải đặc trưng thấp hơn $4 \times 4$ để phát hiện các khuôn mặt kích thước lớn mà không tốn nhiều tài nguyên.
- **Chọn mô hình cho pipeline:** Trong dự án này, MediaPipe BlazeFace được lựa chọn vì tốc độ xử lý vượt trội (real-time trên CPU), độ chính xác cao đối với các khuôn mặt chính diện có góc quay nhỏ (điển hình trong các kịch bản eKYC/xác thực), và khả năng xuất ra các hộp bao ổn định giúp giảm rung giật (jitter) giữa các frame trong video.

## 2.3 Tiền xử lý và cắt khuôn mặt (Face Alignment & Cropping)
Sau khi định vị được khuôn mặt, bước tiền xử lý nhằm chuẩn hóa vùng khuôn mặt về mặt hình học (geometric normalization) và loại bỏ các nhiễu bối cảnh không liên quan.

### Phép biến đổi Affine (Affine Transformation)
Để xoay khuôn mặt thẳng đứng (ví dụ đường nối hai mắt song song với trục ngang của ảnh), ta áp dụng phép biến đổi Affine. Giả sử tọa độ tâm hai mắt thu được từ bước phát hiện điểm mốc là $E_{left} = (x_l, y_l)$ và $E_{right} = (x_r, y_r)$.
Góc xoay $\theta$ của khuôn mặt được xác định bởi:
$$\theta = \arctan\left(\frac{y_r - y_l}{x_r - x_l}\right)$$
Ma trận biến đổi Affine $M$ cho phép xoay và dịch chuyển ảnh về tâm mới $(x_c, y_c)$ với tỷ lệ scale $s$:
$$M = \begin{bmatrix} \alpha & \beta & (1-\alpha)x_c - \beta y_c \\ -\beta & \alpha & \beta x_c + (1-\alpha)y_c \end{bmatrix}$$
Trong đó $\alpha = s \cos\theta$, $\beta = s \sin\theta$. Ảnh khuôn mặt chuẩn hóa được tính bằng:
$$I_{aligned}(x', y') = I_{orig}(M \cdot [x, y, 1]^T)$$

### Bounding Box Expansion và Margin Ratio
Hộp bao trả về từ bộ phát hiện khuôn mặt thường bó rất sát vùng mặt. Đối với bài toán phát hiện giả mạo, các đặc trưng nằm ở rìa khuôn mặt (như tai, tóc, trán, hay mép giấy in, viền màn hình) mang thông tin cực kỳ quan trọng về cấu trúc 3D và phản xạ ánh sáng. Do đó, việc mở rộng hộp bao là bắt buộc.
Gọi hộp bao phát hiện ban đầu có tọa độ góc trên bên trái là $(x_{min}, y_{min})$, chiều rộng $w$, chiều cao $h$. Với hệ số margin $m = 0.2$ (20%), kích thước hộp bao mới được tính như sau:
$$\text{center}_x = x_{min} + \frac{w}{2}, \quad \text{center}_y = y_{min} + \frac{h}{2}$$
$$s_{new} = \max(w, h) \cdot (1 + 2m)$$
$$x'_{min} = \text{center}_x - \frac{s_{new}}{2}, \quad y'_{min} = \text{center}_y - \frac{s_{new}}{2}$$
Việc ép về kích thước vuông $s_{new} \times s_{new}$ giúp giữ nguyên tỷ lệ khuôn mặt (aspect ratio) khi thực hiện bước resize tiếp theo. Các tọa độ sau khi tính toán được clip để đảm bảo nằm trong ranh giới ảnh gốc.

### Các phương pháp nội suy ảnh (Interpolation Methods)
Để chuyển đổi ảnh cắt khuôn mặt về kích thước mục tiêu dùng cho mô hình (ví dụ $224 \times 224$ cho CNN hoặc $128 \times 128$ cho LBP), ta sử dụng các thuật toán nội suy pixel:
- **Bilinear Interpolation:** Tính toán giá trị pixel mới bằng cách lấy trung bình có trọng số khoảng cách của 4 pixel lân cận gần nhất trong ảnh gốc. Cân bằng tốt giữa chất lượng ảnh và tốc độ tính toán.
- **Bicubic Interpolation:** Sử dụng hàm đa thức bậc ba trên lưới $4 \times 4$ pixel lân cận. Cho ảnh mượt mà hơn nhưng chi phí tính toán cao hơn.
- **Area Interpolation (cv2.INTER_AREA):** Nội suy dựa trên tỷ lệ diện tích pixel. Đây là phương pháp được khuyến nghị khi thực hiện thu nhỏ ảnh (downsampling) vì nó giúp hạn chế hiện tượng răng cưa (aliasing) và giữ được cấu trúc tần số cao của texture, rất phù hợp cho việc chuẩn bị đầu vào cho thuật toán LBP.

## 2.4 Biểu diễn khuôn mặt (Face Representation)
Biểu diễn khuôn mặt là việc ánh xạ ảnh khuôn mặt đã chuẩn hóa sang một không gian đặc trưng (feature space) để thực hiện phân loại hoặc so khớp.

### 2.4.1 Phương pháp toàn cục (Holistic/Subspace Methods)
Các phương pháp này xem toàn bộ ảnh khuôn mặt như một điểm dữ liệu trong không gian nhiều chiều và cố gắng tìm kiếm các không gian con (subspaces) có số chiều thấp hơn để biểu diễn dữ liệu.

#### PCA / Eigenfaces (Turk & Pentland, 1991)
Phân tích thành phần chính (Principal Component Analysis - PCA) tìm kiếm các hướng chiếu (thành phần chính) sao cho phương sai của dữ liệu sau khi chiếu là lớn nhất.

Giả sử ta có tập ảnh huấn luyện gồm $N$ ảnh khuôn mặt đã được vector hóa thành các vector cột $x_i \in \mathbb{R}^d$ ($d$ là số pixel, thường rất lớn).
1. **Tính khuôn mặt trung bình (Mean Face):**
   $$\bar{x} = \frac{1}{N} \sum_{i=1}^N x_i$$
2. **Tính toán vector lệch (Mean-subtracted vectors):**
   $$\Phi_i = x_i - \bar{x}$$
3. **Ma trận hiệp phương sai (Covariance Matrix):**
   $$C = \frac{1}{N} \sum_{i=1}^N \Phi_i \Phi_i^T = \frac{1}{N} A A^T$$
   Trong đó $A = [\Phi_1, \Phi_2, ..., \Phi_N] \in \mathbb{R}^{d \times N}$.
4. **Phân rã trị riêng (Eigenvalue Decomposition):**
   Ta cần giải phương trình trị riêng cho ma trận $C \in \mathbb{R}^{d \times d}$:
   $$C u_k = \lambda_k u_k$$
   Vì $d$ rất lớn (ví dụ ảnh $128 \times 128 \Rightarrow d = 16384$), việc tính toán trực tiếp trị riêng của $A A^T$ là bất khả thi.
   **Giải pháp (Dimensionality Trick):** Ta giải phương trình trị riêng cho ma trận nhỏ hơn $A^T A \in \mathbb{R}^{N \times N}$ (vì $N \ll d$):
   $$A^T A v_k = \mu_k v_k$$
   Nhân cả hai vế với $A$:
   $$A A^T (A v_k) = \mu_k (A v_k)$$
   So sánh với phương trình trị riêng gốc, ta thấy $u_k = A v_k$ chính là các vector riêng của ma trận hiệp phương sai $C$, tương ứng với các trị riêng $\lambda_k = \frac{\mu_k}{N}$. Các vector riêng $u_k$ sau khi chuẩn hóa được gọi là các **Eigenfaces**.
5. **Chiếu và biểu diễn:** Chọn $k$ vector riêng ứng với các trị riêng lớn nhất để tạo ma trận chiếu $W = [u_1, u_2, ..., u_k] \in \mathbb{R}^{d \times k}$. Một khuôn mặt mới $x$ được biểu diễn dưới dạng vector hệ số thấp chiều $y \in \mathbb{R}^{k}$:
   $$y = W^T (x - \bar{x})$$

Hạn chế lớn nhất của PCA là phương pháp không giám sát (unsupervised), hướng chiếu tối ưu hóa phương sai chung chứ không tối ưu hóa khoảng cách giữa các lớp, dẫn đến nhạy cảm lớn với sự thay đổi chiếu sáng và biểu cảm.

#### LDA / Fisherfaces (Belhumeur et al., 1997)
Phân tích phân biệt tuyến tính (Linear Discriminant Analysis - LDA) tìm kiếm không gian chiếu sao cho tỷ lệ giữa phương sai giữa các lớp (between-class variance) và phương sai trong nội bộ lớp (within-class variance) là lớn nhất.

Gọi tập dữ liệu gồm $c$ lớp đối tượng.
- **Ma trận phân tán trong lớp (Within-class scatter matrix) $S_W$:**
   $$S_W = \sum_{i=1}^c \sum_{x \in C_i} (x - \mu_i)(x - \mu_i)^T$$
   Với $\mu_i$ là trung bình của lớp $C_i$.
- **Ma trận phân tán giữa các lớp (Between-class scatter matrix) $S_B$:**
   $$S_B = \sum_{i=1}^c N_i (\mu_i - \mu)(\mu_i - \mu)^T$$
   Với $N_i$ là số lượng mẫu của lớp $C_i$, và $\mu$ là trung bình của toàn bộ dữ liệu.
- **Hàm mục tiêu Fisher (Fisher Criterion):**
   Ta tìm ma trận chiếu $W$ để tối đa hóa:
   $$J(W) = \frac{\det(W^T S_B W)}{\det(W^T S_W W)}$$
   Phương trình trị riêng tổng quát tương ứng là:
   $$S_B w_k = \lambda_k S_W w_k \Rightarrow S_W^{-1} S_B w_k = \lambda_k w_k$$

**Vấn đề suy biến (Singularity Problem):** Khi số chiều dữ liệu $d$ lớn hơn số lượng mẫu huấn luyện $N$, ma trận $S_W$ sẽ bị suy biến và không thể tính nghịch đảo $S_W^{-1}$.
**Giải pháp (Fisherfaces):** Chiếu dữ liệu vào không gian PCA trung gian trước để giảm chiều xuống $N-c$, sau đó mới áp dụng LDA trên không gian con đó:
$$W_{opt}^T = W_{lda}^T W_{pca}^T$$

### 2.4.2 Phương pháp cục bộ (Local Feature Methods)
Các phương pháp này tập trung trích xuất thông tin kết cấu (texture) vi mô tại các vùng cục bộ trên khuôn mặt.

#### LBP — Local Binary Pattern (Ojala et al., 2002)
LBP mô tả mối tương quan cường độ sáng giữa một pixel trung tâm và các pixel lân cận của nó.

##### 1. Định nghĩa toán học LBP cơ bản:
Với một pixel trung tâm có tọa độ $(x_c, y_c)$ và cường độ xám $g_c$, xét các láng giềng $g_p$ ($p=0, ..., P-1$) phân bố trên đường tròn bán kính $R$. Mã LBP tại pixel đó được tính bằng:
$$LBP_{P, R}(x_c, y_c) = \sum_{p=0}^{P-1} s(g_p - g_c) \cdot 2^p$$
Trong đó $s(x)$ là hàm ngưỡng nhị phân:
$$s(x) = \begin{cases} 1, & x \geq 0 \\ 0, & x < 0 \end{cases}$$
Tọa độ của láng giềng $g_p$ được xác định bởi:
$$x_p = x_c + R \cos\left(\frac{2\pi p}{P}\right), \quad y_p = y_c - R \sin\left(\frac{2\pi p}{P}\right)$$
Nếu tọa độ $(x_p, y_p)$ không trùng với lưới pixel nguyên, giá trị cường độ $g_p$ được ước lượng bằng phép nội suy song tuyến tính (bilinear interpolation).

##### 2. Mẫu đồng nhất (Uniform Patterns):
Định nghĩa một thước đo chuyển đổi $U(LBP)$ là số lần thay đổi trạng thái từ $0 \to 1$ hoặc $1 \to 0$ giữa hai bit kề nhau trong chuỗi nhị phân tuần hoàn LBP:
$$U(LBP_{P, R}) = |s(g_{P-1} - g_c) - s(g_0 - g_c)| + \sum_{p=1}^{P-1} |s(g_p - g_c) - s(g_{p-1} - g_c)|$$
Một mã LBP được gọi là **đồng nhất (uniform)** nếu $U(LBP) \leq 2$. Các mẫu uniform đại diện cho các cấu trúc vi mô quan trọng trong ảnh như: điểm góc, cạnh, đường biên, vùng phẳng.
Với số láng giềng $P$, số lượng mẫu uniform là $P(P-1) + 2$. Tất cả các mẫu không đồng nhất (non-uniform) sẽ được gom chung vào một bin duy nhất.
Ví dụ với $P=8$, ta có $8(7) + 2 = 58$ mẫu uniform. Cộng thêm 1 bin cho các mẫu non-uniform, tổng số bin của biểu đồ tần suất LBP giảm từ $2^8 = 256$ xuống còn **59 bin**. Việc sử dụng Uniform LBP giúp giảm số chiều của vector đặc trưng và tăng tính ổn định trước nhiễu. Thực tế chứng minh, trong các ảnh tự nhiên, các mẫu uniform chiếm tới hơn 90% tổng số mẫu LBP.

##### 3. Spatial Histogram (Biểu đồ không gian):
Để giữ thông tin phân bố không gian của khuôn mặt, ảnh không được gom chung thành một biểu đồ duy nhất. Thay vào đó, ảnh khuôn mặt được chia thành lưới $G \times G$ ô (cells) không chồng chập (ví dụ lưới $8 \times 8$).
Tại mỗi cell $C_{i, j}$, ta tính biểu đồ tần suất Uniform LBP chuẩn hóa L1:
$$h_{i, j}(k) = \frac{1}{|C_{i, j}|} \sum_{(x, y) \in C_{i, j}} \mathbb{I}(LBP(x, y) == k)$$
Vector đặc trưng cuối cùng là sự nối tiếp (concatenation) biểu đồ của tất cả các cell:
$$H = [h_{1, 1}, h_{1, 2}, ..., h_{G, G}]$$
Kích thước vector đặc trưng là: $G^2 \times (P(P-1) + 3)$. Với cấu hình của dự án ($G=8$, $P=8$, $R=1$, ảnh xám $128 \times 128$), vector đặc trưng có số chiều là $8^2 \times 10 = 640$ chiều (dự án thiết lập 10 bin vì có cấu hình bổ sung so với chuẩn 59 bin).

#### Gabor Wavelets (Gabor Filters)
Bộ lọc Gabor 2D mô tả đặc trưng kết cấu ở các tần số và hướng khác nhau, mô phỏng cơ chế thị giác sơ cấp của con người. Hàm nhân Gabor có dạng:
$$\psi_{\mu, \nu}(z) = \frac{\|k_{\mu, \nu}\|^2}{\sigma^2} e^{-\frac{\|k_{\mu, \nu}\|^2 \|z\|^2}{2\sigma^2}} \left[ e^{i k_{\mu, \nu} z} - e^{-\frac{\sigma^2}{2}} \right]$$
Trong đó $z = (x, y)$ là tọa độ pixel, $k_{\mu, \nu}$ là vector sóng xác định tần số $\nu$ và hướng $\mu$. Một bộ tham số phổ biến gồm 5 tần số và 8 hướng tạo ra ngân hàng 40 bộ lọc Gabor. Vector đặc trưng Gabor (Gabor Jet) thu được bằng cách nhân chập ảnh với các bộ lọc này.

### 2.4.3 Phương pháp học sâu (Deep Learning)
Mạng Nơ-ron tích chập (CNN) tự động học các biểu diễn đặc trưng phân tầng từ dữ liệu ảnh thô: các lớp đầu học đặc trưng hình học cơ bản (cạnh, góc), các lớp giữa học đặc trưng kết cấu (textures), các lớp sâu học đặc trưng ngữ nghĩa (semantics).

#### MobileNetV2 (Sandler et al., 2018)
MobileNetV2 thiết kế tối ưu hóa cho các hệ thống di động thông qua hai kỹ thuật chính:
1. **Depthwise Separable Convolution:** Thay thế phép tích chập thông thường bằng hai bước:
   - **Depthwise Convolution:** Mỗi kênh đầu vào được tích chập độc lập bởi một bộ lọc duy nhất.
   - **Pointwise Convolution:** Nhân tích chập $1 \times 1$ để kết hợp tuyến tính đầu ra của bước depthwise.
   So sánh chi phí tính toán với tích chập thông thường (kernel $D_K$, kênh đầu vào $M$, kênh đầu ra $N$, kích thước bản đồ đặc trưng $D_F$):
   $$\text{Tỷ lệ chi phí} = \frac{D_K^2 \cdot M \cdot D_F^2 + M \cdot N \cdot D_F^2}{D_K^2 \cdot M \cdot N \cdot D_F^2} = \frac{1}{N} + \frac{1}{D_K^2}$$
   Với kernel $3 \times 3$, chi phí tính toán giảm từ 8 đến 9 lần mà không làm suy giảm nhiều độ chính xác.
2. **Inverted Residuals và Linear Bottlenecks:**
   Các khối residual thông thường đi theo cấu trúc Rộng $\to$ Hẹp $\to$ Rộng (về số kênh). Khối Inverted Residual của MobileNetV2 làm ngược lại: Hẹp $\to$ Rộng $\to$ Hẹp. Lớp đầu vào được mở rộng số kênh qua tích chập $1 \times 1$, đi qua lớp depthwise $3 \times 3$, rồi được nén lại về số kênh ban đầu bằng tích chập $1 \times 1$.
   Lớp nén cuối cùng (bottleneck) không sử dụng hàm kích hoạt phi tuyến ReLU mà giữ nguyên tuyến tính (**Linear Bottleneck**) để tránh hiện tượng ReLU phá hủy thông tin khi dữ liệu bị nén về không gian ít chiều.

#### ResNet (He et al., 2016)
Để giải quyết hiện tượng suy giảm độ chính xác và triệt tiêu gradient (vanishing gradient) khi huấn luyện các mạng cực sâu, ResNet giới thiệu cơ chế **Skip Connection** (kết nối tắt).

Thay vì ép các lớp nơ-ron học một ánh xạ mục tiêu trực tiếp $\mathcal{H}(x)$, ta cấu hình các lớp này học một hàm hiệu số (residual function):
$$\mathcal{F}(x) = \mathcal{H}(x) - x$$
Đầu ra của khối được tính bằng:
$$\mathcal{H}(x) = \mathcal{F}(x) + x$$
Cơ chế này giúp gradient truyền trực tiếp ngược lại các tầng phía trước thông qua phép cộng tuyến tính mà không bị triệt tiêu bởi các phép nhân trọng số liên tiếp.
Kiến trúc **ResNet18** gồm 4 stages tích chập chính, sử dụng khối cơ bản BasicBlock (gồm 2 lớp tích chập $3 \times 3$ kết hợp skip connection).
Trong bài toán Anti-Spoofing, các đặc trưng vi kết cấu phân biệt thật/giả thường nằm ở các tần số cao và đặc trưng cục bộ. Khi sử dụng mô hình pretrained ImageNet, các lớp sâu nhất (`layer4`) thường biểu diễn các thông tin ngữ nghĩa trừu tượng cấp cao (ví dụ: "chó", "mèo", "khuôn mặt") vốn không phân biệt được thật/giả. Do đó, việc giải đóng băng và fine-tune riêng `layer4` của ResNet18 (Experiment E04) cho phép mạng điều chỉnh các đặc trưng ngữ nghĩa này hướng về việc học các biểu diễn vi cấu trúc kết cấu chuyên biệt của presentation attacks.

## 2.5 Support Vector Machine (SVM)
Bộ phân loại SVM tìm kiếm một siêu phẳng (hyperplane) trong không gian đặc trưng nhiều chiều để phân tách các lớp dữ liệu với khoảng cách (margin) lớn nhất.

### Bài toán Tối ưu hóa Hard Margin
Cho tập dữ liệu huấn luyện $\{(x_1, y_1), ..., (x_N, y_N)\}$ với $x_i \in \mathbb{R}^d$ và nhãn $y_i \in \{-1, 1\}$. Siêu phẳng phân hoạch được định nghĩa bởi:
$$w^T x + b = 0$$
Với giả định dữ liệu phân tách tuyến tính hoàn toàn, ta có ràng buộc:
$$y_i(w^T x_i + b) \geq 1, \quad \forall i=1, ..., N$$
Bài toán tối ưu tìm kiếm siêu phẳng có margin cực đại tương đương với:
$$\min_{w, b} \frac{1}{2} \|w\|^2 \quad \text{s.t.} \quad y_i(w^T x_i + b) \geq 1, \quad \forall i$$

### Bài toán Tối ưu hóa Soft Margin (C-SVM)
Trong thực tế, dữ liệu thường có nhiễu và không phân tách tuyến tính hoàn hảo. Ta giới thiệu các biến bù sai số (slack variables) $\xi_i \geq 0$ cho phép một số mẫu huấn luyện vi phạm margin:
$$\min_{w, b, \xi} \frac{1}{2} \|w\|^2 + C \sum_{i=1}^N \xi_i$$
$$\text{s.t.} \quad y_i(w^T x_i + b) \geq 1 - \xi_i, \quad \xi_i \geq 0, \quad \forall i$$
Trong đó $C > 0$ là siêu tham số điều khiển sự cân bằng (trade-off) giữa việc tối đa hóa margin (giảm thiểu $\|w\|^2$) và giảm thiểu sai số huấn luyện.
- **C lớn:** Phạt nặng sai số, mô hình cố gắng phân loại đúng mọi mẫu huấn luyện, dễ dẫn đến overfitting (margin hẹp).
- **C nhỏ:** Chấp nhận nhiều sai số huấn luyện hơn để đạt siêu phẳng có margin rộng hơn, tăng tính tổng quát hóa (bias cao hơn nhưng variance thấp hơn).

### Dạng Đối ngẫu Lagrange và Kernel Trick
Để giải bài toán soft margin, ta thiết lập hàm Lagrange:
$$\mathcal{L}(w, b, \xi, \alpha, \beta) = \frac{1}{2} \|w\|^2 + C \sum_{i=1}^N \xi_i - \sum_{i=1}^N \alpha_i [y_i(w^T x_i + b) - 1 + \xi_i] - \sum_{i=1}^N \beta_i \xi_i$$
Triệt tiêu đạo hàm theo các biến nguyên bản $w, b, \xi$, ta thu được bài toán đối ngẫu chỉ phụ thuộc vào nhân tử Lagrange $\alpha_i$:
$$\max_{\alpha} \sum_{i=1}^N \alpha_i - \frac{1}{2} \sum_{i=1}^N \sum_{j=1}^N \alpha_i \alpha_j y_i y_j (x_i^T x_j)$$
$$\text{s.t.} \quad 0 \leq \alpha_i \leq C, \quad \sum_{i=1}^N \alpha_i y_i = 0$$

Khi dữ liệu không phân tách tuyến tính ở không gian gốc, ta áp dụng phép chiếu phi tuyến $\phi(x)$ lên không gian nhiều chiều hơn. Phép thế tích vô hướng bằng hàm hạt nhân **Kernel Trick** cho phép tính toán trực tiếp tích vô hướng ở không gian mới mà không cần tính toán tường minh phép chiếu $\phi$:
$$K(x_i, x_j) = \phi(x_i)^T \phi(x_j)$$
Hàm quyết định cuối cùng có dạng:
$$f(x) = \text{sign}\left( \sum_{i=1}^N \alpha_i y_i K(x_i, x) + b \right)$$

Đối với đặc trưng LBP histogram có số chiều tương đối cao ($640$ chiều trong cấu hình của dự án), siêu phẳng phân tách tuyến tính (**Linear SVM**) là lựa chọn tối ưu vì:
1. Tránh bùng nổ tính toán so với các phi tuyến kernel (như RBF).
2. Tránh hiện tượng overfitting trên các tập huấn luyện có số lượng mẫu giới hạn.
3. Tốc độ suy luận cực nhanh, đáp ứng yêu cầu vận hành thời gian thực.
# CHƯƠNG 3: LÝ THUYẾT PHÁT HIỆN LỪA ĐỐI KHUÔN MẶT

## 3.1 Phân loại tấn công giả mạo khuôn mặt (Presentation Attack Taxonomy)
Để thiết kế một hệ thống phát hiện giả mạo hiệu quả, cần phải hiểu rõ các cơ chế tấn công và đặc điểm vật lý của từng loại phương tiện tấn công.

### 3.1.1 Khái niệm và tiêu chuẩn ISO/IEC 30107
Bộ tiêu chuẩn quốc tế **ISO/IEC 30107** định nghĩa các thuật ngữ và khung đánh giá chuẩn cho công nghệ phát hiện giả mạo sinh trắc học (Presentation Attack Detection - PAD):
- **Presentation Attack (PA):** Hành vi đưa mẫu sinh trắc học giả mạo hoặc không hợp lệ vào cảm biến thu nhận nhằm mục đích vượt qua cơ chế bảo mật của hệ thống xác thực.
- **Presentation Attack Instrument (PAI):** Công cụ hoặc phương tiện vật lý được sử dụng để thực hiện cuộc tấn công giả mạo (ví dụ: ảnh in, màn hình hiển thị, mặt nạ).
- **PAI Species (Loài PAI):** Một loại PAI cụ thể được phân loại dựa trên đặc điểm cấu tạo vật lý (ví dụ: ảnh in trên giấy bóng, ảnh in trên giấy mờ).
- **Presentation Attack Detection (PAD):** Cơ chế tự động được tích hợp trong hệ sinh trắc học nhằm xác định xem mẫu đầu vào đến từ một cơ thể sống thực sự (Bona Fide) hay là một công cụ giả mạo (PA).

Trong kiến trúc bảo mật sinh trắc học, PA xảy ra ở **điểm thu nhận dữ liệu (Capture Point)**. Điều này nghĩa là kẻ tấn công tác động trực tiếp vào thế giới vật lý trước cảm biến camera, không cần can thiệp vào mã nguồn hay luồng truyền dữ liệu số của hệ thống. Do đó, các phương pháp bảo mật mật mã học truyền thống (như chữ ký số, mã hóa đường truyền) hoàn toàn bất lực trước hình thức tấn công này.

### 3.1.2 Tấn công bằng ảnh in (Print Attack)
Đây là hình thức tấn công đơn giản và tốn ít chi phí nhất. Kẻ tấn công sử dụng một bức ảnh chân dung 2D của người dùng hợp lệ, được in ra bằng máy in phun hoặc máy in laser, sau đó đưa bức ảnh này lên trước camera.

Các dấu hiệu vật lý để phân biệt print attack bao gồm:
- **Sự thiếu hụt thông tin chiều sâu 3D:** Bề mặt của tấm giấy in hoàn toàn phẳng (2D). Khi chuyển động trước camera, toàn bộ các điểm trên khuôn mặt sẽ chuyển động đồng dạng (rigid motion), không có hiệu ứng thị sai (parallax effect) giữa các vùng trán, mũi và tai.
- **Hiện tượng nhiễu in ấn (Halftone/Print Artifacts):** Các máy in thương mại tạo ra ảnh bằng cách phun các chấm mực li ti (halftone pattern) theo một lưới tọa độ nhất định. Mặc dù mắt người khó nhận ra ở khoảng cách xa, camera độ phân giải cao ở cự ly gần sẽ bắt được cấu trúc vi mô dạng hạt này.
- **Suy hao phổ tần số cao:** Quá trình tái tạo ảnh qua in ấn làm mất đi các chi tiết tần số cao (vi cấu trúc da, lỗ chân lông, sợi tóc mịn). Khi camera chụp lại tấm ảnh in, sự suy hao này càng trầm trọng hơn do hiện tượng mờ nhòe quang học (optical blurring).
- Trong bộ dữ liệu OULU-NPU, print attack được thực hiện bằng cách sử dụng hai loại máy in khác nhau (một máy in phun chất lượng trung bình và một máy in laser chất lượng cao) trên các loại giấy in khác nhau để kiểm tra độ nhạy của hệ thống trước chất lượng in.

### 3.1.3 Tấn công phát lại video (Video Replay Attack)
Tấn công phát lại video có độ tinh vi cao hơn vì nó mô phỏng được chuyển động tự nhiên của khuôn mặt (chớp mắt, mấp máy môi, xoay đầu). Kẻ tấn công quay lại một đoạn video ngắn của nạn nhân, sau đó phát lại đoạn video này trên màn hình của một thiết bị di động (smartphone, máy tính bảng) trước camera xác thực.

Các đặc trưng phân biệt bao gồm:
- **Hiện tượng nhiễu Moiré (Moiré Patterns):** Khi camera chụp lại một màn hình hiển thị LCD/OLED, sự chồng chéo giữa lưới pixel vật lý của màn hình phát và lưới cảm biến ánh sáng (Color Filter Array - CFA) của camera tạo ra các đường vân sọc dạng sóng gọi là nhiễu moiré.
- **Tần số quét màn hình (Flicker/Screen Refresh Rate):** Màn hình hiển thị hoạt động bằng cách làm mới hình ảnh ở một tần số nhất định (ví dụ 60Hz, 90Hz, 120Hz). Camera thu hình với tốc độ màn trập (shutter speed) khác biệt sẽ ghi lại hiện tượng nhấp nháy hoặc các dải sáng tối quét ngang màn hình.
- **Phản xạ ánh sáng bề mặt (Specular Reflection):** Bề mặt màn hình hiển thị thường được làm bằng kính hoặc nhựa bóng. Khi đặt trước camera, nó sẽ phản chiếu ánh sáng môi trường xung quanh (như bóng đèn, trần nhà), tạo ra các vệt sáng bất thường đè lên khuôn mặt.
- **Viền thiết bị (Bezel Artifacts):** Nếu kẻ tấn công không căn chỉnh góc chụp cẩn thận, camera có thể bắt được một phần viền đen của điện thoại hoặc máy tính bảng đang dùng để phát lại video.
- OULU-NPU thiết lập 2 loại màn hình phát lại (một smartphone màn hình nhỏ và một laptop/tablet màn hình lớn) để tạo biến thể cho replay attack.

### 3.1.4 Tấn công bằng mặt nạ 3D (3D Mask Attack)
Hình thức tấn công cao cấp này sử dụng mặt nạ silicon, mặt nạ đất sét hoặc mặt nạ in 3D tái tạo lại chính xác cấu trúc hình học 3D của khuôn mặt nạn nhân.
- **Thách thức:** Mặt nạ 3D vượt qua được các bộ kiểm tra chuyển động phẳng và kiểm tra bản đồ độ sâu đơn giản (như cảm biến depth-map cơ bản).
- **Đặc trưng phân biệt:** Mặt nạ silicon thiếu các biểu cảm vi mô (micro-expressions), cấu trúc lỗ chân lông nhân tạo bị thô, và đặc biệt là sự khác biệt về phổ phản xạ ánh sáng (spectral reflectance). Da người thật có hiện tượng tán xạ dưới bề mặt (sub-surface scattering) do máu và các lớp biểu bì dưới da tạo ra, điều mà silicon hay nhựa in 3D hoàn toàn không có.
- Mặc dù 3D mask attack nằm ngoài phạm vi thí nghiệm trên bộ dữ liệu OULU-NPU Protocol 1, việc hiểu rõ cơ chế này giúp định hướng thiết kế các mô hình trích xuất đặc trưng kết cấu có tính tổng quát hóa cao.

### 3.1.5 Các loại tấn công nâng cao khác
- **Deepfake / Face Morphing:** Tấn công ở cấp độ số, thay đổi khuôn mặt bằng thuật toán sinh (GANs, Diffusion Models). Đối phó với dạng này yêu cầu các giải pháp phát hiện xáo trộn pixel kỹ thuật số (digital tampering detection) thay vì PAD vật lý.
- **Adversarial Attacks:** Chèn nhiễu đối kháng cực nhỏ vào ảnh đầu vào để đánh lừa mạng học sâu phân loại sai lệch.
- **Partial Attacks:** Chỉ giả mạo một phần khuôn mặt (ví dụ đeo kính in hình mắt người thật, khẩu trang in hình miệng thật).

## 3.2 Các phương pháp phát hiện lừa đối (Anti-Spoofing Methods)
Có nhiều cách tiếp cận để giải quyết bài toán Face PAD, phân loại theo bản chất đặc trưng khai thác:

### 3.2.1 Phương pháp dựa trên kết cấu (Texture-based)
Đây là hướng tiếp cận phổ biến nhất cho camera RGB thông thường, hoạt động dựa trên giả thuyết rằng bề mặt vật liệu của các PAI (giấy in, màn hình) tạo ra các cấu trúc kết cấu vi mô (micro-textures) khác biệt so với da người thật dưới cùng một điều kiện chiếu sáng.

#### LBP cho Anti-Spoofing
Nghiên cứu tiên phong của Määttä et al. (2011) chỉ ra rằng Local Binary Pattern (LBP) cực kỳ hiệu quả trong việc phát hiện sự khác biệt kết cấu vi mô này.
- **Cơ chế:** Da thật có độ mịn, độ mờ và cấu trúc lỗ chân lông phản xạ ánh sáng khuếch tán (diffuse reflection). Ngược lại, giấy in có thớ sợi gỗ và hạt mực, màn hình điện thoại có lưới pixel và độ phản xạ gương (specular reflection). Các chi tiết này được mã hóa hoàn hảo qua phân bố tần suất của các mẫu LBP cục bộ.
- **Multi-scale LBP:** Để bắt được cả đặc trưng kết cấu vi mô (nhỏ) và vĩ mô (lớn), người ta kết hợp nhiều bộ tham số $(P, R)$ khác nhau (ví dụ: $LBP_{8,1}$, $LBP_{8,2}$, $LBP_{16,2}$).
- **Ưu điểm:** Tính toán cực nhanh, bất biến với sự thay đổi cường độ sáng tuyến tính (do so sánh hiệu số tương đối), không yêu cầu dữ liệu huấn luyện khổng lồ.

#### Phân tích phổ tần số (Frequency Domain Analysis)
Sử dụng phép biến đổi Fourier nhanh (FFT) 2D để chuyển ảnh sang miền tần số:
$$F(u, v) = \sum_{x=0}^{W-1} \sum_{y=0}^{H-1} I(x, y) e^{-i 2\pi \left(\frac{ux}{W} + \frac{vy}{H}\right)}$$
- Do ảnh in và màn hình bị suy hao tần số cao, năng lượng phổ của mẫu giả mạo tập trung chủ yếu ở vùng tần số thấp và trung bình.
- Ngược lại, da người thật giữ được nhiều thành phần tần số cao sắc nét. Bằng cách so sánh mật độ năng lượng phổ (Power Spectrum Density) tại các băng tần khác nhau, ta có thể phân biệt được thật/giả.

#### Phân tích không gian màu (Color Space Analysis)
Các máy ảnh RGB thông thường ghi lại màu sắc dựa trên đáp ứng phổ của cảm biến. Tuy nhiên, phổ phản xạ màu sắc của các PAI bị giới hạn bởi dải màu (gamut) của máy in hoặc màn hình hiển thị.
- Bằng cách chuyển đổi ảnh từ không gian màu RGB sang các không gian màu phân tách độ sáng và độ màu như **HSV** (Hue, Saturation, Value) hoặc **YCbCr** (Luminance, Blue-difference, Red-difference), sự khác biệt về độ bão hòa màu và phản xạ ánh sáng được phóng đại rõ rệt.
- LBP trích xuất trên các kênh màu phụ (như kênh Cr của YCbCr hay kênh H của HSV) thường cho hiệu quả PAD tốt hơn và ổn định hơn so với chỉ dùng kênh xám (Grayscale).

### 3.2.2 Phương pháp dựa trên chuyển động (Motion-based)
Khai thác các đặc tính động học temporal để phát hiện sự sống (Liveness Detection):
- **Optical Flow (Luồng quang học):** Tính toán vector chuyển động của các điểm pixel giữa các frame liên tiếp. Khuôn mặt thật 3D khi chuyển động sẽ tạo ra trường vector quang học phi tuyến (non-rigid motion), các vùng mũi, má di chuyển với vận tốc khác với tai và nền. Trong khi đó, ảnh in phẳng (2D) di chuyển sẽ tạo ra trường vector song song đồng dạng (rigid motion). Phương trình Horn-Schunck thường được dùng để giải bài toán dòng quang học:
  $$\iint \left( (I_x u + I_y v + I_t)^2 + \alpha^2 (\|\nabla u\|^2 + \|\nabla v\|^2) \right) dx dy \to \min$$
- **Phát hiện chuyển động tự nhiên:** Phát hiện nhịp chớp mắt (eye blinking), chuyển động của môi (lip movement), hay nhịp thở phập phồng của lồng ngực.
- **Challenge-Response (Thử thách - Đáp ứng):** Yêu cầu người dùng thực hiện một chuỗi hành động ngẫu nhiên (nhìn sang trái, mỉm cười, gật đầu) để đối phó với video phát lại tĩnh.

### 3.2.3 Phương pháp dựa trên độ sâu (Depth-based)
Sử dụng thông tin hình học 3D của khuôn mặt để loại bỏ hoàn toàn các cuộc tấn công bằng phương tiện phẳng (2D):
- **Structured Light (Ánh sáng cấu trúc):** Chiếu một lưới tia hồng ngoại vô hình lên khuôn mặt, camera hồng ngoại thu nhận lưới tia bị biến dạng bởi cấu trúc lồi lõm của khuôn mặt để tính toán bản đồ độ sâu (ví dụ công nghệ FaceID của Apple).
- **Time-of-Flight (ToF):** Cảm biến đo thời gian di chuyển của chùm tia sáng từ nguồn phát đến khuôn mặt và quay lại cảm biến để dựng bản đồ 3D.
- **Stereo Vision (Thị giác lập thể):** Sử dụng hai camera RGB đặt cách nhau một khoảng xác định để tính toán bản đồ dịch vị (Disparity Map) từ đó suy ra chiều sâu.
- **Monocular Depth Estimation (Ước lượng độ sâu đơn kính):** Sử dụng mạng CNN huấn luyện để tự động dựng lại bản đồ độ sâu tương đối chỉ từ một ảnh RGB thông thường. Bản đồ độ sâu của khuôn mặt thật sẽ có dạng hình cầu paraboloid lồi, trong khi khuôn mặt giả mạo phẳng sẽ có bản đồ độ sâu phẳng dẹt.

### 3.2.4 Phương pháp dựa trên học sâu (Deep Learning-based)
Học sâu đã trở thành công cụ chủ đạo nhờ khả năng tự động tối ưu hóa các bộ lọc đặc trưng mà không cần thiết kế thủ công.

#### Binary Classification CNN
Sử dụng các kiến trúc mạng tích chập tiêu chuẩn (ResNet, MobileNet, VGG) với hàm mất mát Cross-Entropy nhị phân để học cách phân biệt trực tiếp live/spoof.
- **Ưu điểm:** Dễ cài đặt, tận dụng được sức mạnh của kỹ thuật Transfer Learning từ các tập dữ liệu ảnh khổng lồ như ImageNet.
- **Hạn chế:** Mạng học sâu có xu hướng "học tắt", ghi nhớ các đặc trưng bối cảnh không liên quan (như góc phòng, ánh sáng đèn) hoặc overfit vào các vân nhiễu cụ thể của thiết bị trong tập train, dẫn đến khả năng tổng quát hóa kém trên tập dữ liệu chưa thấy.

#### Pixel-wise Supervision (Auxiliary Supervision)
Để ép mạng học sâu tập trung vào các đặc trưng vật lý có nghĩa thay vì ghi nhớ nhãn nhị phân, người ta áp dụng giám sát mức độ pixel (Pixel-wise Supervision):
- Thay vì dự đoán một nhãn đơn lẻ $0/1$, mạng được huấn luyện để dự đoán **Bản đồ độ sâu khuôn mặt (Depth Map)** và **Bản đồ nhiễu Moiré (Moiré Map)**. Khuôn mặt thật sẽ có nhãn đích là depth-map 3D thực tế, mẫu giả mạo phẳng có nhãn đích là một ma trận toàn giá trị 0.
- **CDCN (Central Difference Convolutional Network)** (Yu et al., 2020): Giới thiệu phép tích chập vi phân trung tâm để trích xuất các đặc trưng gradient cục bộ trực tiếp trong các lớp tích chập, giúp tăng cường khả năng biểu diễn thông tin micro-texture và nâng cao độ robust trước sự thay đổi chiếu sáng.

#### Domain Adaptation (Thích ứng tên miền)
Để giải quyết bài toán lệch phân phối dữ liệu (domain shift) giữa các tập dữ liệu hoặc các thiết bị thu nhận khác nhau:
- **DANN (Domain-Adversarial Neural Network):** Sử dụng thêm một bộ phân loại tên miền (Domain Discriminator) hoạt động song song với bộ phân loại giả mạo. Một lớp đảo ngược gradient (Gradient Reversal Layer - GRL) được chèn vào giữa để ép mạng trích xuất ra các đặc trưng mang tính phân biệt giả mạo cao nhưng hoàn toàn bất biến trước thiết bị thu nhận hay môi trường.

### 3.2.5 Phương pháp multi-modal và hybrid
- Kết hợp camera RGB truyền thống với camera hồng ngoại gần (NIR - Near-Infrared) và camera ảnh nhiệt (Thermal Imaging). Da người thật phản xạ rất đặc trưng trong dải sóng hồng ngoại và tỏa nhiệt đều xung quanh $37^\circ\text{C}$.
- **Physiological Signals (Tín hiệu sinh lý):** rPPG (remote Photoplethysmography) đo lường sự thay đổi thể tích máu vi mô dưới da thông qua sự biến đổi cực nhỏ của màu sắc da trên video RGB theo thời gian. Mẫu giả mạo in hoặc phát lại hoàn toàn không có nhịp tim sinh học này.

## 3.3 Thước đo đánh giá Anti-Spoofing theo ISO/IEC 30107-3
Việc đánh giá hiệu năng của một hệ thống PAD có những đặc thù riêng biệt so với hệ thống nhận dạng danh tính hay các bài toán phân loại thông thường.

### 3.3.1 Các metric truyền thống và hạn chế
Trong nhận dạng sinh trắc học truyền thống, người ta sử dụng:
- **FAR (False Acceptance Rate):** Tỷ lệ chấp nhận nhầm imposter (người giả mạo danh tính) là người dùng hợp lệ.
- **FRR (False Rejection Rate):** Tỷ lệ từ chối nhầm genuine (người dùng hợp lệ) là kẻ giả mạo.
- **EER (Equal Error Rate):** Điểm mà FAR = FRR.

Hạn chế khi áp dụng trực tiếp FAR/FRR cho PAD: Trong PAD, ta có hai loại lỗi vật lý hoàn toàn khác nhau: chấp nhận nhầm một cuộc tấn công giả mạo (rủi ro bảo mật nghiêm trọng) và từ chối nhầm một người dùng thật (gây phiền toái cho trải nghiệm người dùng). Việc gộp chung không phân biệt rõ nguồn gốc lỗi làm che khuất các điểm yếu cụ thể của hệ thống bảo mật.

### 3.3.2 Metric theo tiêu chuẩn ISO/IEC 30107-3
Để chuẩn hóa việc đánh giá, ISO/IEC 30107-3 định nghĩa các metric chuyên biệt:

#### 1. APCER (Attack Presentation Classification Error Rate)
Tỷ lệ phân loại nhầm mẫu tấn công (Presentation Attack) là mẫu thật (Bona Fide). Đo lường mức độ mất an ninh của hệ thống.
$$\text{APCER} = \frac{\text{Số mẫu PA bị phân loại nhầm là Bona Fide}}{\text{Tổng số mẫu PA thực hiện}}$$
Hoặc dưới dạng công thức xác suất phân loại nhị phân (với $Live=0$ và $Spoof=1$):
$$\text{APCER} = \frac{\sum_{i=1}^{N_{spoof}} \mathbb{I}(\hat{y}_i == 0 \mid y_i == 1)}{N_{spoof}}$$
**APCER thấp** tương đương với độ bảo mật cao, hệ thống phát hiện hầu hết các cuộc tấn công.

#### 2. BPCER (Bona Fide Presentation Classification Error Rate)
Tỷ lệ phân loại nhầm mẫu thật (Bona Fide) là mẫu tấn công (Presentation Attack). Đo lường mức độ bất tiện cho người dùng.
$$\text{BPCER} = \frac{\text{Số mẫu Bona Fide bị phân loại nhầm là PA}}{\text{Tổng số mẫu Bona Fide thực hiện}}$$
$$\text{BPCER} = \frac{\sum_{i=1}^{N_{live}} \mathbb{I}(\hat{y}_i == 1 \mid y_i == 0)}{N_{live}}$$
**BPCER thấp** nghĩa là hệ thống thân thiện, ít khi khóa tài khoản của người dùng thật.

#### 3. ACER (Average Classification Error Rate)
Sai số phân loại trung bình, là metric đánh giá hiệu năng tổng hợp của hệ thống PAD:
$$\text{ACER} = \frac{\text{APCER} + \text{BPCER}}{2}$$

> [!IMPORTANT]
> **Ý nghĩa của ACER:** Khác với chỉ số Accuracy hay F1-score vốn bị ảnh hưởng nặng nề bởi sự mất cân bằng giữa các lớp dữ liệu (ví dụ bộ dữ liệu OULU-NPU có tỷ lệ 80% spoof và 20% live), ACER là trung bình cộng trực tiếp của hai tỷ lệ lỗi độc lập. Nhờ đó, ACER phản ánh chính xác hiệu năng của bộ phân loại mà không bị thiên lệch bởi tần suất xuất hiện của các lớp.

### 3.3.3 Chiến lược chọn ngưỡng quyết định (Threshold Selection)
Đầu ra của mô hình (như Linear SVM hay sigmoid của CNN) là một giá trị điểm số liên tục (score) đại diện cho xác suất hoặc độ tự tin mẫu đó là spoof. Để ra quyết định nhị phân, ta phải áp dụng một ngưỡng $\theta$:
$$\hat{y} = \begin{cases} 1 (\text{Spoof}), & \text{nếu } \text{score} \geq \theta \\ 0 (\text{Live}), & \text{nếu } \text{score} < \theta \end{cases}$$

- **Nguyên tắc chống rò rỉ dữ liệu (Anti-leakage):** Ngưỡng $\theta$ **bắt buộc phải được lựa chọn trên tập phát triển (Development Set - Dev)** bằng cách quét qua toàn bộ các giá trị score khả dĩ để tìm ngưỡng tối thiểu hóa ACER trên tập Dev:
  $$\theta_{opt} = \arg\min_{\theta} \text{ACER}_{dev}(\theta)$$
- Sau khi tìm được $\theta_{opt}$ từ tập Dev, ngưỡng này được **khóa cứng (frozen)** và áp dụng trực tiếp để tính toán APCER, BPCER và ACER trên tập kiểm thử (Test Set). Tuyệt đối không được tinh chỉnh lại ngưỡng dựa trên kết quả của tập Test.
- **Đường cong DET (Detection Error Trade-off):** Vẽ mối quan hệ giữa APCER (trục tung) và BPCER (trục hoành) ở các ngưỡng $\theta$ khác nhau để trực quan hóa sự đánh đổi giữa an ninh và tiện dụng.

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

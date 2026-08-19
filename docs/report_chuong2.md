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
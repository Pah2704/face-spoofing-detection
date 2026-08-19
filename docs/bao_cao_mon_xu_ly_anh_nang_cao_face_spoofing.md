# TRƯỜNG ĐẠI HỌC BÁCH KHOA HÀ NỘI
## VIỆN CÔNG NGHỆ THÔNG TIN VÀ TRUYỀN THÔNG

BÁO CÁO BÀI TẬP LỚN MÔN HỌC
XỬ LÝ ẢNH NÂNG CAO

Đề tài: Phát hiện giả mạo khuôn mặt trên bộ dữ liệu OULU-NPU

Giảng viên hướng dẫn: ...
Sinh viên thực hiện: ...
Mã số sinh viên: ...
Lớp: ...

Hà Nội, tháng 7 năm 2026

---

# Lời cam đoan

Báo cáo trình bày quá trình xây dựng và đánh giá một hệ thống phát hiện giả mạo khuôn mặt trên OULU-NPU Protocol 1. Các số liệu thực nghiệm trong báo cáo được đọc từ artifact của dự án; cấu hình, checkpoint, ngưỡng quyết định và dự đoán đều được lưu để có thể kiểm tra lại. Những kiến thức và kết quả kế thừa từ công trình khác được trích dẫn trong phần tài liệu tham khảo.

# Tóm tắt

Giả mạo khuôn mặt bằng ảnh in hoặc video phát lại là một dạng presentation attack có thể đánh lừa hệ thống xác thực chỉ dựa trên nhận dạng danh tính. Đề tài xây dựng một pipeline xử lý video hoàn chỉnh gồm lấy mẫu khung hình, phát hiện và chuẩn hóa vùng mặt, biểu diễn ảnh, phân loại, gộp điểm theo video và đánh giá theo APCER, BPCER, ACER. Năm thí nghiệm được thực hiện trên cùng dữ liệu OULU-NPU Protocol 1: LBP mức xám kết hợp SVM tuyến tính (E01), MobileNetV2 pretrained chỉ học head (E02), ResNet18 pretrained chỉ học head (E03), ResNet18 fine-tune `layer4` cùng head (E04), và RGB-LBP-SVM ghép texture ba kênh màu (E05).

Trọng tâm của báo cáo không chỉ là so sánh độ chính xác, mà còn giải thích các nguyên lý xử lý ảnh đã được dùng: lấy mẫu tín hiệu video; nội suy và chuẩn hóa ảnh; mã hóa vi kết cấu bằng Local Binary Pattern; phân lớp biên cực đại bằng SVM; tích chập, chuẩn hóa theo batch và học phần dư trong CNN; tích chập tách theo chiều sâu của MobileNetV2; học chuyển giao; chọn ngưỡng và gộp quyết định theo thời gian. Mỗi lý thuyết đều được nối với tham số cấu hình, vị trí mã nguồn và artifact thực nghiệm tương ứng.

Kết quả video-level trên test cho ACER lần lượt là 32,71% (Gray-LBP-SVM), 25,10% (MobileNetV2), 23,85% (ResNet18 head-only), 14,79% (ResNet18 fine-tune `layer4`) và 14,17% (RGB-LBP-SVM). E04 cải thiện 9,06 điểm phần trăm so với E03, còn E05 cải thiện 18,54 điểm so với E01. Các kết quả cho thấy biểu diễn ImageNet đóng băng hoàn toàn chưa đủ thích nghi với tín hiệu vi kết cấu của presentation attack và thông tin màu bổ sung đáng kể cho LBP mức xám. Tuy vậy, khoảng cách dev–test vẫn là 12,22 điểm ở E04 và 11,46 điểm ở E05; kết quả do đó chưa chứng minh được khả năng tổng quát hóa ngoài Protocol 1.

**Từ khóa:** xử lý ảnh, face anti-spoofing, presentation attack detection, LBP, SVM, ResNet18, MobileNetV2, transfer learning, OULU-NPU.

## Danh mục chữ viết tắt

| Ký hiệu | Ý nghĩa |
|---|---|
| PAD | Presentation Attack Detection |
| PAI | Presentation Attack Instrument |
| LBP | Local Binary Pattern |
| SVM | Support Vector Machine |
| CNN | Convolutional Neural Network |
| BN | Batch Normalization |
| BCE | Binary Cross-Entropy |
| TP/TN | True Positive/True Negative |
| FP/FN | False Positive/False Negative |
| APCER | Attack Presentation Classification Error Rate |
| BPCER | Bona Fide Presentation Classification Error Rate |
| ACER | Average Classification Error Rate |
| ROI | Region of Interest |

# Chương 1. Giới thiệu

## 1.1. Đặt vấn đề

Khuôn mặt là tín hiệu sinh trắc học thuận tiện vì có thể thu nhận bằng camera thông thường và không yêu cầu tiếp xúc. Nhược điểm của sự thuận tiện này là ảnh hoặc video của người dùng cũng dễ bị sao chép. Một hệ thống nhận dạng có thể trả lời “đây có phải khuôn mặt của người A không?” nhưng vẫn không trả lời được “khuôn mặt đang xuất hiện trực tiếp hay chỉ là ảnh của người A trên giấy hoặc màn hình?”. Module PAD (Presentation Attack Detection) giải quyết câu hỏi thứ hai và là lớp bảo vệ quan trọng đặt trước hoặc đi cùng hệ thống xác thực khuôn mặt.

Trong phạm vi bộ dữ liệu OULU-NPU Protocol 1, hai công cụ tấn công hiển thị (PAI) được khảo sát là ảnh in và video phát lại. Quá trình tạo giả gồm hai chuỗi thu nhận: khuôn mặt thật được camera thứ nhất ghi lại, được in/hiển thị, rồi camera của hệ thống chụp lại. Chuỗi recapture này làm biến đổi phổ tần, lượng tử hóa, màu, phản xạ, độ nét và kết cấu bề mặt. Đó là cơ sở vật lý để các thuật toán xử lý ảnh phân biệt khuôn mặt thật (live) và giả mạo (spoof).

Để giải quyết vấn đề trên và đánh giá hiệu năng của các phương pháp xử lý ảnh từ truyền thống đến học sâu, đề tài đặt ra các câu hỏi nghiên cứu sau:
- **RQ1:** Đặc trưng vi kết cấu LBP còn hiệu quả đến đâu so với CNN pretrained?
- **RQ2:** Việc chỉ học classifier head có đủ để chuyển từ miền ImageNet sang miền face PAD không?
- **RQ3:** Fine-tune tầng cuối của ResNet18 thay đổi sai số attack và live như thế nào khi các yếu tố còn lại được giữ nguyên?
- **RQ4:** Gộp trung bình điểm của mười frame có luôn tốt hơn quyết định trên từng frame không?
- **RQ5:** Chỉ số F1 có đủ để đánh giá một tập dữ liệu lệch lớp 80% spoof không?
- **RQ6:** Giữ texture riêng trên ba kênh RGB có cải thiện LBP mức xám không, và cải thiện đến từ APCER hay BPCER?

## 1.2. Mục tiêu nghiên cứu

Đề tài được thực hiện nhằm xây dựng và đánh giá so sánh các phương pháp phát hiện giả mạo khuôn mặt trên bộ dữ liệu OULU-NPU, qua đó khảo sát sự đánh đổi giữa độ chính xác và tài nguyên tính toán. Cụ thể, đề tài đặt ra bốn mục tiêu chính:

1. Xây dựng pipeline có thể tái lập từ video thô đến quyết định ở cấp video.
2. So sánh biểu diễn thủ công LBP-SVM với biểu diễn học sâu MobileNetV2 và ResNet18 trên cùng protocol, crop và quy trình đánh giá.
3. Làm rõ vai trò của các phép biến đổi ảnh và các nguyên lý học máy trong từng thí nghiệm, thay vì chỉ trình bày mô hình như một “hộp đen”.
4. Kiểm chứng tác động của học chuyển giao qua ablation E03 head-only và E04 fine-tune `layer4`.

**Phạm vi và đóng góp của đề tài:**
Nghiên cứu sử dụng 2.700 video của OULU-NPU Protocol 1 (1.200 train, 900 dev, 600 test). Bài toán nhị phân quy ước `live = 0`, `spoof = 1`; score lớn hơn luôn biểu thị xu hướng spoof. Các đóng góp chính của đề tài bao gồm: một pipeline chung có manifest, fingerprint, kiểm tra leakage và artifact; một baseline xử lý ảnh cổ điển LBP-SVM và ba cấu hình transfer learning; một ablation có kiểm soát giữa ResNet18 head-only và fine-tune `layer4`; phân tích đồng thời frame/video, APCER/BPCER/ACER, domain shift và tài nguyên; bảng truy vết từ lý thuyết đến phép xử lý thực sự có trong mã nguồn. Đề tài không khảo sát mask 3D, tín hiệu hồng ngoại/độ sâu, Protocol 2–4, cross-dataset, hoặc mô hình temporal học được.

## 1.3. Bố cục báo cáo

Báo cáo được trình bày theo cấu trúc gồm 5 chương như sau:

- **Chương 2: Cơ sở lý thuyết.** Cung cấp kiến thức nền tảng về ảnh số, đặc trưng Local Binary Pattern (LBP), thuật toán Support Vector Machine (SVM), mạng nơ-ron tích chập (CNN), kỹ thuật học chuyển giao (Transfer Learning), và các độ đo đánh giá hiệu năng mô hình (metrics).
- **Chương 3: Phương pháp đề xuất và thiết kế thực nghiệm.** Trình bày kiến trúc pipeline xử lý video, thiết kế chi tiết cho 5 thí nghiệm (E01-E05) và các cơ chế chống rò rỉ dữ liệu (anti-leakage).
- **Chương 4: Kết quả thực nghiệm và thảo luận.** Trình bày các bảng kết quả định lượng, phân tích lỗi (error analysis), đánh giá tài nguyên tính toán (benchmark tài nguyên) và các thảo luận chuyên sâu về hiệu năng của từng phương pháp.
- **Chương 5: Kết luận và hướng phát triển.** Tổng kết lại các kết quả đã đạt được, trả lời các câu hỏi nghiên cứu và đề xuất định hướng phát triển tiếp theo của đề tài.

# Chương 2. Cơ sở lý thuyết

## 2.1. Ảnh số và các phép biến đổi hình học

**Biểu diễn toán học của ảnh số và video**
Một ảnh màu liên tục có thể biểu diễn bởi hàm bức xạ

$$
f:\mathbb{R}^2\rightarrow\mathbb{R}^3,
$$

trong đó hai biến đầu là tọa độ không gian và ba thành phần đầu ra là cường độ màu. Camera thực hiện lấy mẫu theo không gian và lượng tử hóa cường độ để tạo tensor rời rạc:

$$
I[m,n,c]\in\{0,1,\ldots,255\},\quad c\in\{R,G,B\}.
$$

Đối với video, việc lấy mẫu khung hình bổ sung thêm chiều thời gian: $V[t,m,n,c]$. Tần số lấy mẫu hữu hạn của cảm biến, màn hình và camera có thể giao thoa, tạo flicker hoặc moiré. Ảnh in làm thay đổi phản xạ bề mặt và phân bố hạt mực; màn hình tạo cấu trúc điểm ảnh, phản xạ gương và một chu kỳ lấy mẫu bổ sung. Vì thế face PAD là một bài toán phân loại dựa trên dấu vết của quá trình tạo ảnh, không phải bài toán nhận dạng danh tính.

**Mô hình chuỗi thu nhận live vs spoof**
Chuỗi ảnh live có thể mô tả rút gọn là

$$
I_{live}=Q\{S(H_{cam}*L_{face})+\eta\},
$$

với $H_{cam}$ là đáp ứng quang học, $S$ là lấy mẫu, $Q$ là lượng tử hóa và $\eta$ là nhiễu. Ảnh spoof đi qua thêm một toán tử hiển thị/in $H_{PAI}$ và một lần thu nhận:

$$
I_{spoof}=Q_2\{S_2[H_{cam,2}*H_{PAI}(I_1)]+\eta_2\}.
$$

Biểu thức trên là mô hình khái niệm. Nó giải thích tại sao texture cục bộ và bộ lọc tích chập có thể khai thác khác biệt giữa hai lớp.

**Phát hiện mặt và chuẩn hóa hình học ROI**
Phát hiện mặt tìm hộp $b=(x,y,w,h)$ trên frame, tương đương với một phép biến đổi Affine đơn giản. Dự án dùng MediaPipe Face Detection với `model_selection = 0`, confidence tối thiểu 0,5. Cạnh dài của frame được co về tối đa 640 pixel trước khi detect; tọa độ sau đó được ánh xạ về ảnh gốc. Nếu không tìm thấy mặt, detector thử lại trên độ phân giải đầy đủ.

Vùng quan tâm (ROI) được đổi thành hình vuông (square crop) để tránh kéo giãn tỷ lệ khuôn mặt. Với tâm $c_x=x+w/2$, $c_y=y+h/2$, margin $m=0{,}2$, cạnh mục tiêu là

$$
s=\max(w,h)(1+2m).
$$

Hộp vuông được làm tròn, cắt theo biên ảnh và dịch lại để nằm hoàn toàn trong frame. Margin giữ lại đường viền khuôn mặt và một phần ngữ cảnh — nơi có thể chứa biên giấy hoặc phản xạ màn hình — nhưng cũng có thể đưa nền vào biểu diễn.

**Thay đổi kích thước và các phương pháp nội suy ảnh**
Crop vuông sau đó được chuẩn hóa về kích thước $256\times256$. Khi thu nhỏ, OpenCV dùng phương pháp `INTER_AREA` để ước lượng đóng góp theo diện tích, giúp hạn chế aliasing hơn lấy mẫu điểm. Khi cần phóng crop nhỏ lên 256, pipeline dùng nội suy tuyến tính. Nhánh LBP tiếp tục thu nhỏ ảnh xám xuống $128\times128$ bằng `INTER_AREA`; nhánh CNN đổi về $224\times224$ bằng nội suy bilinear có antialias.

Với điểm nguồn $(x,y)$ nằm giữa bốn pixel, bilinear interpolation được viết:

$$
I'(x,y)=\sum_{i=0}^{1}\sum_{j=0}^{1}
w_{ij}I(\lfloor x\rfloor+i,\lfloor y\rfloor+j),
$$

trong đó $w_{ij}$ phụ thuộc tuyến tính vào khoảng cách. Nội suy là một bộ lọc thông thấp cục bộ: nó làm ảnh có cùng kích thước cho batch nhưng đồng thời có thể làm suy giảm cue tần số cao. 

## 2.2. Phương pháp trích xuất đặc trưng truyền thống

**Chuẩn hóa cường độ và đặc trưng**
Đối với mạng CNN, ảnh RGB 8-bit được đưa về đoạn $[0,1]$, rồi chuẩn hóa từng kênh theo bộ trọng số ImageNet:

$$
\hat{x}_c=\frac{x_c-\mu_c}{\sigma_c},
$$

với $\mu=(0{,}485,0{,}456,0{,}406)$ và $\sigma=(0{,}229,0{,}224,0{,}225)$. Đối với đặc trưng LBP, mỗi histogram cell được chuẩn hóa L1:

$$
\hat{h}_b=\frac{h_b}{\sum_j h_j+\epsilon}.
$$

Sau khi ghép các block histogram, phép chuẩn hóa z-score với `StandardScaler` được áp dụng và chỉ fit trên tập train:

$$
z_j=\frac{x_j-\mu_j^{train}}{\sigma_j^{train}}.
$$

Hai chuẩn hóa phục vụ hai mục đích khác nhau: chuẩn hóa L1 biến số đếm thành phân bố texture cục bộ; z-score làm các chiều feature có thang đo phù hợp trước khi đưa vào SVM.

**Đặc trưng LBP (Local Binary Pattern)**
LBP mô tả cấu trúc cục bộ bằng quan hệ thứ tự giữa điểm trung tâm $g_c$ và $P$ điểm lân cận $g_p$ trên bán kính $R$. Mã cơ bản là:

$$
LBP_{P,R}=\sum_{p=0}^{P-1}s(g_p-g_c)2^p,
\qquad
s(a)=\begin{cases}1,&a\ge 0\\0,&a<0.\end{cases}
$$

Để biểu diễn hiệu quả hơn, khái niệm mẫu đồng nhất (uniform pattern) được sử dụng. Số lần chuyển bit theo vòng tròn được định nghĩa:

$$
U=|b_{P-1}-b_0|+\sum_{p=1}^{P-1}|b_p-b_{p-1}|,
\quad b_p=s(g_p-g_c).
$$

Mẫu uniform có $U\le2$. Với ánh xạ rotation-invariant uniform $LBP^{riu2}_{P,R}$:

$$
LBP^{riu2}_{P,R}=
\begin{cases}
\sum_{p=0}^{P-1}b_p,&U\le2,\\
P+1,&U>2.
\end{cases}
$$

Để giữ lại thông tin vị trí, biểu đồ tần suất không gian (spatial histogram) được tính. Ảnh $128\times128$ được chia thành lưới $8\times8$; mỗi ô có histogram 10 bin. Vector cuối cùng có độ dài 640:

$$
\mathbf{x}=[\hat{h}_{1,1};\hat{h}_{1,2};\ldots;\hat{h}_{8,8}]
\in\mathbb{R}^{8\times8\times10}=\mathbb{R}^{640}.
$$

Để không làm mất thông tin màu sắc, có thể mở rộng LBP trên không gian màu RGB. Cùng toán tử LBP được áp dụng độc lập cho 3 kênh R, G, B:

$$
\mathbf{x}_{RGB}=
[\mathbf{x}_{LBP(R)};\mathbf{x}_{LBP(G)};\mathbf{x}_{LBP(B)}]
\in\mathbb{R}^{3\times640}=\mathbb{R}^{1920}.
$$

**Bộ phân lớp SVM (Support Vector Machine)**
Với vector LBP $\mathbf{x}_i$ và nhãn $y_i\in\{-1,+1\}$, SVM tìm siêu phẳng quyết định:

$$
f(\mathbf{x})=\mathbf{w}^{T}\mathbf{x}+b
$$

Dự án sử dụng bài toán tối ưu lề mềm (soft-margin) với squared hinge loss và hàm nhân tuyến tính:

$$
\min_{\mathbf{w},b}\quad
\frac{1}{2}\|\mathbf{w}\|_2^2+
C\sum_i\alpha_{y_i}
\left[\max\left(0,1-y_i f(\mathbf{x}_i)\right)\right]^2.
$$

Trọng số lớp cân bằng được tính xấp xỉ nhằm giúp lớp live ít hơn không bị lấn át:

$$
\alpha_k=\frac{n}{K n_k}.
$$

## 2.3. Phương pháp dựa trên mạng Nơ-ron tích chập (CNN)

**Phép tính tích chập**
Với tensor đầu vào $X$, kernel $W$ và bias $b$, phép tính tích chập chéo (cross-correlation) là:

$$
Y_{i,j,o}=b_o+
\sum_{u=0}^{K_h-1}\sum_{v=0}^{K_w-1}\sum_{c=1}^{C_{in}}
W_{u,v,c,o}X_{iS+u-P,jS+v-P,c}.
$$

Ba tính chất quan trọng của CNN là kết nối cục bộ, chia sẻ trọng số và trường tiếp nhận tăng dần theo độ sâu, giúp mạng học được các biểu diễn phức tạp.

**Batch Normalization (BN)**
Với một mini-batch, BN chuẩn hóa activation:

$$
\hat{x}=\frac{x-\mu_B}{\sqrt{\sigma_B^2+\epsilon}},
\qquad y=\gamma\hat{x}+\beta.
$$

Ý nghĩa trong transfer learning: Khi train, $\mu_B,\sigma_B^2$ đến từ batch và running statistics được cập nhật; khi đánh giá, running statistics đã lưu được dùng. Nếu khóa backbone, toàn bộ BN cần ở chế độ `eval` để thống kê của ImageNet không bị thay đổi.

**Logit, sigmoid và weighted BCE**
Mạng CNN xuất một logit $z$ cho lớp spoof. Xác suất được tính thông qua hàm sigmoid:

$$
p(y=1\mid x)=\sigma(z)=\frac{1}{1+e^{-z}}.
$$

Hàm mất mát weighted binary cross-entropy (BCE) được dùng để huấn luyện:

$$
\mathcal{L}=-\frac{1}{n}\sum_i
\left[w_+ y_i\log p_i+(1-y_i)\log(1-p_i)\right].
$$

Trong đó $w_+$ là trọng số pos_weight, được tính bằng tỷ lệ số mẫu lớp âm trên lớp dương (ví dụ: $2400/9600=0{,}25$) để cân bằng tổng trọng số hai lớp.

**Adam Optimizer**
Mô hình được tối ưu bằng Adam, với moment bậc một và hai:

$$
m_t=\beta_1m_{t-1}+(1-\beta_1)g_t,
\qquad
v_t=\beta_2v_{t-1}+(1-\beta_2)g_t^2,
$$

sau khi hiệu chỉnh bias, tham số cập nhật theo $\theta_t=\theta_{t-1}-\eta\hat m_t/(\sqrt{\hat v_t}+\epsilon)$.

**Kiến trúc ResNet18**
Một residual block học phần dư $F(\mathbf{x},W)$ thay vì trực tiếp học ánh xạ $H(\mathbf{x})$:

$$
\mathbf{y}=\phi(F(\mathbf{x},W)+\mathbf{x}).
$$

Đường đồng nhất (skip connection) tạo một đường truyền gradient trực tiếp:

$$
\frac{\partial \mathbf{y}}{\partial \mathbf{x}}
\supset 1,
$$

giúp tối ưu mạng sâu dễ hơn. ResNet18 gồm stem `7x7 conv`, sau đó là cấu trúc 4 stage (`layer1`–`layer4`), mỗi stage có hai BasicBlock.

**Kiến trúc MobileNetV2**
MobileNetV2 dùng depthwise separable convolution để giảm khối lượng tính toán. Chi phí của tích chập chuẩn là:

$$
C_{standard}=HWMNK^2.
$$

Depthwise convolution kết hợp pointwise $1\times1$ có chi phí:

$$
C_{dw+pw}=HWMK^2+HWMN,
$$

với tỷ số:

$$
\frac{C_{dw+pw}}{C_{standard}}=\frac{1}{N}+\frac{1}{K^2}.
$$

Mạng tổ chức thành inverted residual block: pointwise expansion, depthwise xử lý không gian, rồi linear projection nén về linear bottleneck (không dùng ReLU ở lớp cuối).

**Kỹ thuật học chuyển giao (Transfer learning)**
Dự án áp dụng hai chiến lược: 
- Head-only: Khóa toàn bộ backbone và BN, chỉ học bộ phân lớp tuyến tính (head) mới.
- Fine-tune layer4: Mở khóa stage sâu nhất (`layer4`) và head, sử dụng learning rate nhỏ hơn cho `layer4` để thích nghi đặc trưng PAD.

## 2.4. Ngưỡng quyết định và Đánh giá hiệu năng

**Các thước đo cơ bản**
Với spoof là dương và live là âm:

$$
\mathrm{Precision}=\frac{TP}{TP+FP},\qquad
\mathrm{Recall}=\frac{TP}{TP+FN},
$$

$$
F1=\frac{2\,\mathrm{Precision}\,\mathrm{Recall}}
{\mathrm{Precision}+\mathrm{Recall}}.
$$

**Thước đo PAD chuẩn ISO/IEC 30107-3**
Trong bài toán PAD:

$$
APCER=\frac{FN}{TP+FN},
\qquad
BPCER=\frac{FP}{TN+FP},
$$

$$
ACER=\frac{APCER+BPCER}{2}.
$$

Ý nghĩa toán học: APCER đo tỷ lệ attack bị chấp nhận nhầm là live; BPCER đo tỷ lệ live bị từ chối nhầm là attack. Việc trung bình hóa thành ACER giúp đánh giá không bị thiên lệch bởi lớp spoof chiếm đa số.

**Phương pháp gộp điểm cấp video (Video-level aggregation)**
Với $K_v$ frame hợp lệ của video $v$, score (mean score) của video là trung bình cộng:

$$
\bar{s}_v=\frac{1}{K_v}\sum_{k=1}^{K_v}s_{v,k}.
$$

Trong đó $s$ là xác suất hoặc decision score. Trung bình có thể giảm nhiễu ngẫu nhiên nếu lỗi frame ít tương quan.

**Quyết định và chọn ngưỡng tối ưu**
Quyết định cuối cùng tại ngưỡng $\tau$:

$$
\hat y=\mathbb{1}[s\ge\tau].
$$

Quy trình chọn ngưỡng quét các operating point trên tập Dev và tối thiểu hóa hàm mục tiêu (ví dụ bộ khóa `(ACER, APCER, threshold)`). Sau khi chọn được ngưỡng tối ưu trên tập Dev, nó được đóng băng và áp dụng trực tiếp lên tập Test. Việc sắp xếp score giúp việc quét ngưỡng chỉ có độ phức tạp $O(n\log n)$.

# Chương 3. Phương pháp đề xuất và Thiết kế thực nghiệm

## 3.1. Thiết kế hệ thống (Pipeline)
### Bộ dữ liệu OULU-NPU và Protocol 1
OULU-NPU là cơ sở dữ liệu face PAD trên thiết bị di động gồm 5.940 video của 55 subject, thu trong ba môi trường bằng sáu điện thoại; attack được tạo bằng hai máy in và hai màn hình [10]. Bộ dữ liệu định nghĩa bốn protocol để khảo sát các nguồn biến thiên khác nhau. Dự án chỉ dùng Protocol 1 và chỉ giải nén những video được protocol liệt kê.

Phân bố local đã xác minh:

| Split | Live video | Spoof video | Tổng video | Frame mục tiêu |
|---|---:|---:|---:|---:|
| Train | 240 | 960 | 1.200 | 12.000 |
| Dev | 180 | 720 | 900 | 9.000 |
| Test | 120 | 480 | 600 | 6.000 |
| **Tổng** | **540** | **2.160** | **2.700** | **27.000** |

Có 26.999/27.000 crop giải mã hợp lệ. Một frame đầu ở dev không phát hiện được mặt và được giữ trạng thái `no_face`, không được thay bằng frame lựa chọn theo nhãn. Tỷ lệ phát hiện crop là 99,9963%.

Protocol chính thức quyết định split. Mọi frame của một video luôn ở cùng split; subject/video không bị trộn ngẫu nhiên lại. Archive gốc là bất biến, manifest là nguồn duy nhất xác định nhãn và quan hệ video–frame.

### Sơ đồ khối pipeline từ video đầu vào đến quyết định cuối cùng

```text
Video Protocol 1
       │
       ▼
Lấy đều 10 frame/video ──► manifest + metadata
       │
       ▼
MediaPipe detect ──► square crop + margin 20% ──► resize 256×256
       │
       ├──► Gray 128×128 ─► LBP riu2 8×8 ─► StandardScaler ─► LinearSVC (E01)
       ├──► RGB 128×128 ──► LBP(R/G/B), concatenate ────────► LinearSVC (E05)
       │
       └──► RGB 224×224 ──► ImageNet normalize ─► CNN one-logit (E02–E04)
                                                          │
Frame score ──────────────────────────────────────────────┘
       │
       ▼
Mean score/video ─► threshold khóa từ dev ─► APCER/BPCER/ACER trên test
```

Pipeline tách ba lớp trách nhiệm:
1. **Dữ liệu:** archive, protocol, manifest và crop dùng chung.
2. **Biểu diễn/mô hình:** LBP-SVM hoặc CNN.
3. **Đánh giá:** hướng score thống nhất, aggregation, threshold và metric dùng chung.

Sự tách biệt này ngăn mỗi model vô tình có một preprocessing hoặc evaluator thuận lợi riêng.

### Phương pháp lấy mẫu khung hình (Frame sampling)
Cấu hình cố định gồm lấy đều 10 frame/video. Các frame được lấy cách đều nhau qua toàn bộ video, có hai đầu, bằng công thức số nguyên, giúp giảm chi phí tính toán đồng thời bao phủ toàn bộ nội dung video.

### Quy trình phát hiện khuôn mặt (MediaPipe Face Detection) và cắt ảnh
Tiền xử lý sử dụng MediaPipe với confidence 0,5 để phát hiện khuôn mặt, loại bỏ phần lớn nền và giữ lại ROI (Region of Interest) mặt. Cạnh detect tối đa là 640. 

Sau khi phát hiện khuôn mặt, hệ thống thực hiện cắt ảnh (square crop) với lề mở rộng (margin) là 20%, clipping tại biên. Ảnh cắt ra sau đó được đưa về kích thước cố định, mặc định resize $256\times256$. Face detector nhận RGB, trong khi OpenCV đọc frame ở BGR; phép đổi từ `BGR → RGB` được thực hiện trước khi detect. Việc nội suy (interpolation) dùng `INTER_AREA` khi thu nhỏ và `INTER_LINEAR` khi phóng to.

### Tiền xử lý chung
#### Kiểm kê và kiểm tra dữ liệu
Pipeline kiểm tra số lượng video, khả năng đọc, label, split và trùng lặp trước khi tạo crop. Lệnh `ffprobe` được dùng để kiểm tra video. Mỗi output có fingerprint của config và manifest, vì vậy cache sai cấu hình không được tái sử dụng âm thầm.

#### Tạo crop khuôn mặt
Crop lưu ra dưới định dạng PNG với mức nén (compression) bằng 3 và vẫn được đọc theo quy ước phù hợp của từng nhánh sau đó. Việc lưu crop trung gian giúp cả bốn thí nghiệm đọc đúng cùng vùng ảnh, đồng thời cho phép kiểm tra chất lượng bằng montage và metadata hộp bao.

## 3.2. Cấu hình các thí nghiệm

### E01 — LBP-SVM
Thí nghiệm E01 thực hiện chuỗi biến đổi:
1. Đọc crop PNG trực tiếp ở định dạng grayscale (ảnh xám).
2. Resize $128\times128$ bằng `INTER_AREA`.
3. Tính $LBP^{riu2}_{8,1}$ với padding sao chép biên.
4. Chia lưới $8\times8$, histogram 10 bin/cell, chuẩn hóa L1.
5. Ghép vector 640 chiều.
6. Fit `StandardScaler` trên 12.000 train frame.
7. Fit `LinearSVC` và chọn $C$ trên tập dev thông qua grid search.
8. Lấy mean decision score cho mỗi video và áp ngưỡng video từ dev.

Giá trị siêu tham số được chọn là $C=10^{-4}$; ngưỡng frame và video lần lượt -0,3049388 và -0,4000959. Dấu âm không có nghĩa xác suất âm: SVM score là khoảng cách có dấu tới siêu phẳng, không phải xác suất.
Run chính: `artifacts/runs/lbp_svm/e01_20260712_lbp_svm_seed42_verified/`.

### E02 — MobileNetV2 Transfer Learning
Thí nghiệm E02 sử dụng input RGB $224\times224$, ImageNet normalization, horizontal flip với $p=0{,}5$ chỉ áp dụng trên tập train. Backbone MobileNetV2 ImageNet V2 cùng với Batch Normalization (BN) bị khóa (frozen backbone); training head là classifier cuối xuất ra một spoof logit. Chỉ có 1.281/2.225.153 tham số được cập nhật.

Huấn luyện dùng batch 16, optimizer Adam, learning rate $10^{-4}$, weight decay $10^{-4}$, weighted BCE với $w_+=0{,}25$, tối đa 15 epoch, tối thiểu 3 epoch, patience 3 và seed 42. Checkpoint được xếp theo tuple của dev video `(ACER, APCER, -F1, epoch)`; epoch 15 được chọn. Ngưỡng video là 0,5125712.
Run chính: `artifacts/runs/mobilenet_v2/e02_20260712_mobilenet_v2_seed42/`.

### E03 — ResNet18 Transfer Learning
Thí nghiệm E03 giữ toàn bộ transform, loss, optimizer, checkpoint policy và evaluator của E02; chỉ thay đổi backbone sang ResNet18 ImageNet V1. Lớp fully connected mới (training head) có 513 tham số, trong khi toàn bộ backbone và BN khóa. Tổng mô hình có 11.177.025 tham số. Epoch 15 được chọn; ngưỡng video là 0,5859636.
Run chính: `artifacts/runs/resnet18/e03_20260713_resnet18_seed42/`.

Việc so sánh E02/E03 khảo sát ảnh hưởng của kiến trúc pretrained trong chế độ bộ trích đặc trưng cố định, chứ không phải đánh giá đầy đủ năng lực fine-tune vì cả hai backbone đều bị khóa.

### E04 — ResNet18 Fine-tune Layer4
Thí nghiệm E04 là ablation trực tiếp của E03. Mọi yếu tố giữ nguyên ngoại trừ:
- `layer4` và BN bên trong nó được mở (unfreeze layer4).
- Sử dụng differential learning rates: `layer4` dùng learning rate $10^{-5}$; head dùng learning rate $10^{-4}$.
- 8.394.241 tham số được học thay vì chỉ 513.

Các stage stem đến `layer3` vẫn khóa và ở chế độ eval. Epoch 6 là checkpoint tốt nhất; early stopping dừng sau epoch 9. Ngưỡng video là 0,1310235. Ngưỡng này thấp hơn E03 nhưng không đồng nghĩa model "kém tự tin": calibration logit thay đổi khi feature được fine-tune, nên chất lượng phụ thuộc operating point thay vì giá trị tuyệt đối.
Run chính: `artifacts/runs/resnet18_finetune/e04_20260714_resnet18_finetune_layer4_seed42/`.

### E05 — RGB-LBP-SVM
Thí nghiệm E05 là ablation trực tiếp của E01. OpenCV đọc crop màu theo BGR, sau đó code đổi sang RGB rồi tính descriptor theo E01 (color LBP) độc lập trên từng kênh. Ba block 640 chiều này sau đó được ghép (concatenate) theo thứ tự `[R,G,B]` thành vector 1.920 chiều (1920D). Các cấu hình như `StandardScaler`, `LinearSVC`, lưới tìm kiếm C, seed, aggregation và threshold policy được giữ nguyên như E01.

Giá trị $C=10^{-4}$ được chọn; ngưỡng frame và video tương ứng là -0,4523026 và -0,3479599. Main run đạt test video F1 92,51%, APCER 10,00%, BPCER 18,33% và ACER 14,17%.
Run chính: `artifacts/runs/rgb_lbp_svm/e05_20260721_rgb_lbp_svm_seed42/`.

### Bảng truy vết lý thuyết – triển khai – mục đích

Đây là bảng trung tâm trả lời câu hỏi “trong thực nghiệm đã ứng dụng lý thuyết nào để xử lý bài toán?”.

| Lý thuyết | Cách áp dụng thực tế | Nơi kiểm chứng | Vai trò trong PAD |
|---|---|---|---|
| Lấy mẫu tín hiệu rời rạc | 10 chỉ số cách đều, có hai đầu, công thức số nguyên | `data/frame_sampler.py` | Giảm chi phí và phủ toàn video |
| Phát hiện đối tượng | MediaPipe, chọn confidence lớn nhất, retry full-res | `data/preprocess.py` | Loại phần lớn nền, giữ ROI mặt |
| Chuẩn hóa hình học | Square crop, margin 20%, clip biên | `data/preprocess.py` | Đầu vào đồng nhất, giữ cue quanh mặt |
| Nội suy/antialias | Area khi thu nhỏ; linear/bilinear khi phóng; CNN antialias | `preprocess.py`, `cnn_dataset.py`, `features/cache.py` | Chuẩn kích thước và hạn chế aliasing |
| Biến đổi màu | BGR→RGB cho detector/CNN/E05; grayscale cho E01 | `preprocess.py`, `features/cache.py` | Đúng contract màu; so sánh mất/giữ màu |
| LBP riu2 | $P=8,R=1$, 10 bin, grid $8\times8$ | `features/lbp.py` | Mã hóa vi kết cấu in/màn hình |
| Color texture fusion | Ghép `[LBP(R),LBP(G),LBP(B)]` thành 1.920D | `features/lbp.py`, config E05 | Giữ sai khác texture theo kênh màu |
| Histogram L1 | Chuẩn hóa từng cell | `features/lbp.py` | Giảm phụ thuộc số pixel/cell |
| Chuẩn hóa z-score | Fit scaler chỉ trên train | `models/lbp_svm.py` | Đồng nhất thang feature cho SVM |
| Biên cực đại | LinearSVC, squared hinge, balanced class | `models/lbp_svm.py` | Phân lớp vector texture 640D |
| Tích chập | MobileNetV2/ResNet18 pretrained | `models/mobilenet_v2.py`, `models/resnet18.py` | Học biểu diễn không gian phân cấp |
| Depthwise separable conv | Backbone MobileNetV2 | `models/mobilenet_v2.py` | Giảm tham số/checkpoint E02 |
| Residual learning | Backbone ResNet18 BasicBlock | `models/resnet18.py` | Tối ưu mạng sâu và tái sử dụng feature |
| Batch normalization | BN khóa ở E02/E03; chỉ BN layer4 train ở E04 | hai model + training runners | Kiểm soát running statistics khi transfer |
| Transfer learning | ImageNet weights; head-only và fine-tune layer4 | configs E02–E04 | Tận dụng feature chung, thích nghi miền PAD |
| Bất biến qua augmentation | Flip ngang $p=0{,}5$ chỉ trên train | `data/cnn_dataset.py` | Tăng dữ liệu mà giữ nhãn |
| Weighted empirical risk | BCE one-logit, `pos_weight=0.25` | training runners | Cân tổng đóng góp live/spoof |
| Differential learning rate | layer4 $10^{-5}$, head $10^{-4}$ | config E04 | Hạn chế phá hủy feature pretrained |
| Ước lượng theo nhiều frame | Trung bình score cùng video | `evaluation/aggregation.py` | Kết hợp bằng chứng qua thời gian |
| Lý thuyết quyết định | Threshold tối ưu dev, khóa trước test | `evaluation/threshold.py` và frozen marker | Chuyển score thành quyết định không leakage |
| Đánh giá PAD | APCER, BPCER, ACER, worst-case print/replay | `evaluation/metrics.py`, `oulu_official.py` | Tách lỗi an ninh và lỗi tiện dụng |

### Bảng biến kiểm soát

| Thành phần | Giá trị giữ cố định |
|---|---|
| Protocol | OULU-NPU Protocol 1 chính thức |
| Nhãn | `live=0`, `spoof=1` |
| Sampling | 10 frame/video, cùng index |
| Face crop | MediaPipe, margin 0,2, output 256 |
| CNN input | RGB 224, ImageNet normalize |
| CNN augmentation | horizontal flip 0,5 trên train |
| CNN loss/batch/seed | weighted BCE / 16 / 42 |
| Video aggregation | mean score |
| Chọn ngưỡng | min dev ACER, tie theo APCER rồi threshold |
| Test | chỉ đánh giá sau khi model/threshold khóa |

Biến độc lập chính là biểu diễn/mô hình ở E01–E03, phạm vi tham số được fine-tune ở cặp E03/E04, và grayscale 640D so với RGB 1.920D ở cặp E01/E05.

### Quy trình huấn luyện và lựa chọn mô hình
Trong quy trình huấn luyện, E01 tìm $C$ trên dev rồi fit model đã chọn bằng train; scaler không được refit với dev. Với E02–E04, hệ thống đánh giá checkpoint sau mỗi epoch trên dev video và lưu checkpoint tốt nhất theo ACER/APCER/F1. Patience chỉ được xét sau minimum 3 epoch. 

Sau khi train kết thúc, pipeline tiến hành reload checkpoint, dự đoán lại dev, chọn threshold cho frame/video, ghi frozen marker, rồi mới chạy suy luận trên test. Quy trình này tách bạch hai khái niệm:
- **Học tham số:** chỉ thực hiện từ tập train.
- **Lựa chọn mô hình/operating point:** chỉ thực hiện trên tập dev.

Tập test chỉ dùng để ước lượng hiệu năng sau khi đã khóa mô hình. Nếu đọc test rồi đổi cấu hình, kết quả sau đó phải được xem như một thí nghiệm mới và đòi hỏi test/protocol độc lập.

### Thiết bị và đo tài nguyên
CNN được chạy trên NVIDIA RTX 3060 12 GB, trong khi các kiến trúc như LBP-SVM dùng CPU. Benchmark chuẩn hóa được thực hiện với 600 test crop tại `sample_index=0`, batch 16, bốn worker, chạy warm-up và tính median qua ba lần chạy. End-to-end benchmark bắt đầu từ bước PNG crop (do đó chưa bao gồm decode video thô và face detection). Kết quả cho pure-model và end-to-end được báo riêng do chúng đo lường các phân đoạn pipeline khác nhau.

### Phép đánh giá chính và phụ
Các kết quả chính được báo cáo sử dụng ngưỡng min-ACER từ dev trên video-level ở tập test. Kết quả frame-level được đo để kiểm tra tác động của việc aggregation. Ngoài ra, một evaluator phụ thực hiện tái tạo chính sách dev-EER và báo worst-case giữa hai attack (print/replay) từ baseline chính thức OULU; đánh giá phụ này để kiểm tra độ ổn định của bảng xếp hạng chứ không thay thế metric chính yếu.

## 3.3. Thiết kế chống rò rỉ dữ liệu (Anti-leakage)

Sự rò rỉ dữ liệu được ngăn chặn chặt chẽ qua cơ chế thiết kế sau:
- Archive video gốc được đảm bảo không bị ghi đè; protocol và manifest có chứa checksum cố định.
- **Sự phân chia đối tượng không giao nhau (subject-disjoint):** Mọi chủ thể phân tách rõ rệt giữa Train, Dev và Test. Scaler, model weights và optimizer state chỉ được học hoàn toàn trên tập Train.
- **Quy trình khóa ngưỡng:** Mọi hyperparameter (như $C$, epoch, v.v) cùng các threshold phân loại chỉ được tối ưu và chọn từ tập Dev. Với CNN, `frozen marker` được ghi lại làm dấu chứng thực trước khi thực sự dựng data loader của tập Test. Tập Test tuyệt đối không được dùng để thay preprocessing, đồng thời cấm chạy thêm tuning dựa vào kết quả test.
- Mỗi run được lưu cùng: config resolved, environment parameters, snapshot mã nguồn, checkpoint, dự đoán metric ở cấp frame/video và cả SHA-256 manifest file. 
- Mức độ tin cậy được đảm bảo bằng 106 test pass. Hai smoke run CNN cùng với hai run trên E05 đã xác nhận artifact của system có tính ổn định giống byte-for-byte cho cả config, checkpoint, dự đoán lẫn biểu đồ metric.

### Các giả thuyết nghiên cứu
- **H1:** LBP-SVM có thể nhận biết kết cấu tái thu thập (texture recapture) nhưng nhạy cảm với domain shift do dạng biểu diễn của nó là cố định.
- **H2:** Kiến trúc CNN pretrained ở head-only có năng lực tổng quát hóa tốt hơn LBP nhờ khả năng tích lũy feature không gian phân cấp, nhưng vẫn chịu giới hạn bởi khoảng cách phân phối (domain gap) giữa ImageNet gốc và bài toán PAD.
- **H3:** Việc mở `layer4` của ResNet18 (thí nghiệm E04) giúp giảm ACER đáng kể so với E03 vì mức feature sâu cuối được phép tự do thích nghi với tín hiệu attack đặc trưng.
- **H4:** Kỹ thuật mean aggregation qua thời gian chỉ cải thiện tốt metrics nếu như nhiễu ở mức frame gần với zero-bias; ngược lại, phương pháp này sẽ tác động làm xấu kết quả nếu prediction scores bị lệch (bias) có tính hệ thống.
- **H5:** Sử dụng LBP riêng trên ba kênh màu RGB độc lập giúp bảo tồn tốt những sai khác màu sinh ra do thao tác recapture, nhờ vậy giảm chỉ số ACER tốt hơn hẳn khi so sánh với phép chiếu không gian ảnh xám (grayscale) trong E01.

# Chương 4. Kết quả thực nghiệm và Thảo luận

## 4.1. Kết quả định lượng

Các giá trị dưới đây là phần trăm. Mỗi model dùng threshold riêng đã chọn trên dev; không có threshold nào được chọn lại bằng test.

| Model | Split | Accuracy | Precision | Recall | F1 | APCER | BPCER | ACER |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| E01 LBP-SVM | Dev | 89,11 | 96,98 | 89,17 | 92,91 | 10,83 | 11,11 | **10,97** |
| E02 MobileNetV2 | Dev | 83,00 | 97,49 | 80,83 | 88,38 | 19,17 | 8,33 | **13,75** |
| E03 ResNet18 head | Dev | 86,44 | 96,57 | 86,11 | 91,04 | 13,89 | 12,22 | **13,06** |
| E04 ResNet18 layer4 | Dev | 98,22 | 99,03 | 98,75 | **98,89** | **1,25** | **3,89** | **2,57** |
| E05 RGB-LBP-SVM | Dev | 96,67 | 99,57 | 96,25 | 97,88 | 3,75 | 1,67 | **2,71** |
| E01 LBP-SVM | Test | 83,67 | 86,31 | 94,58 | 90,26 | 5,42 | 60,00 | **32,71** |
| E02 MobileNetV2 | Test | 78,33 | 91,27 | 80,63 | 85,62 | 19,38 | 30,83 | **25,10** |
| E03 ResNet18 head | Test | 78,33 | 92,07 | 79,79 | 85,49 | 20,21 | 27,50 | **23,85** |
| E04 ResNet18 layer4 | Test | **90,83** | **94,00** | **94,58** | **94,29** | **5,42** | **24,17** | **14,79** |
| E05 RGB-LBP-SVM | Test | 88,33 | **95,15** | 90,00 | 92,51 | 10,00 | **18,33** | **14,17** |

E01 tốt nhất trong ba baseline ban đầu trên dev nhưng kém nhất trên test. E05 có ACER/BPCER test tốt nhất, còn E04 có accuracy/F1/APCER tốt hơn. Chênh lệch ACER E05–E04 chỉ 0,63 điểm nên chưa đủ khẳng định ưu thế tổng quát với một seed. Vì test có 480 spoof nhưng chỉ 120 live, F1 của E01 vẫn đạt 90,26% dù 60% live bị từ chối sai. Điều này xác nhận cần đọc APCER và BPCER cùng F1.

### Confusion matrix test video

| Model | TN | FP | FN | TP | Tổng lỗi |
|---|---:|---:|---:|---:|---:|
| E01 LBP-SVM | 48 | 72 | 26 | 454 | 98 |
| E02 MobileNetV2 | 83 | 37 | 93 | 387 | 130 |
| E03 ResNet18 head | 87 | 33 | 97 | 383 | 130 |
| E04 ResNet18 layer4 | 91 | 29 | 26 | 454 | **55** |
| E05 RGB-LBP-SVM | **98** | **22** | 48 | 432 | 70 |

E04 giảm false negative từ 97 xuống 26 và false positive từ 33 xuống 29 so với E03. Phần lớn cải thiện ACER đến từ giảm attack bị bỏ lọt: APCER giảm 14,79 điểm phần trăm; BPCER giảm 3,33 điểm.

### Ablation grayscale LBP và RGB-LBP

| Test video | E01 Gray-LBP | E05 RGB-LBP | E05 − E01 |
|---|---:|---:|---:|
| Feature dimension | 640 | 1.920 | ×3 |
| F1 | 90,26% | **92,51%** | +2,25 điểm % |
| APCER | **5,42%** | 10,00% | +4,58 điểm % |
| BPCER | 60,00% | **18,33%** | **-41,67 điểm %** |
| ACER | 32,71% | **14,17%** | **-18,54 điểm %** |

Màu giảm 50 false positive live nhưng tăng 22 false negative attack. Vì vậy E05 cải thiện ACER nhờ sửa mất cân bằng nghiêm trọng của E01, không cải thiện đồng đều cả hai loại lỗi. Kết quả ủng hộ H5 trong cấu hình RGB-LBP đã khóa.

### Ablation phạm vi fine-tune ResNet18

| Chỉ số | E03 head-only | E04 `layer4` + head | E04 − E03 |
|---|---:|---:|---:|
| Tham số trainable | 513 | 8.394.241 | +8.393.728 |
| Dev ACER | 13,06% | **2,57%** | -10,49 điểm % |
| Test F1 | 85,49% | **94,29%** | +8,80 điểm % |
| Test APCER | 20,21% | **5,42%** | -14,79 điểm % |
| Test BPCER | 27,50% | **24,17%** | -3,33 điểm % |
| Test ACER | 23,85% | **14,79%** | **-9,06 điểm %** |

Đây là phép so sánh có sức giải thích cao nhất vì E03 và E04 dùng cùng kiến trúc suy luận, pretrained weights ban đầu, dữ liệu, transform, loss, aggregation và evaluator. Biến thay đổi chính là quyền cập nhật `layer4`/BN của nó và learning rate phân tầng. Kết quả ủng hộ H3, nhưng chưa chứng minh layer4 đã học chính xác cue vật lý nào; để khẳng định moiré, phản xạ hay texture cụ thể cần thêm phân tích activation/attribution và kiểm tra có kiểm soát.

### Kết quả theo policy phụ OULU

Khi dùng threshold dev-EER và lấy worst-case giữa print/replay:

| Model | Test worst-case ACER |
|---|---:|
| E01 LBP-SVM | 33,75% |
| E02 MobileNetV2 | 26,25% |
| E03 ResNet18 head | 23,13% |
| E04 ResNet18 layer4 | **11,46%** |
| E05 RGB-LBP-SVM | 16,04% |

Ba baseline E01–E03 giữ thứ hạng, nhưng E04/E05 đổi vị trí: E05 thấp hơn E04 0,63 điểm ở min-ACER chính, còn E04 thấp hơn E05 4,58 điểm ở worst-case phụ. Vì vậy chênh lệch nhỏ E04/E05 phụ thuộc operating policy. Với E04 tại policy chính, APCER print/replay là 7,08%/3,75%; với E05 là 7,92%/12,08%.

## 4.2. Phân tích lỗi (Error Analysis)

Trong ba baseline E01–E03, có 16 live video cùng bị dự đoán spoof nhưng chỉ có 2 attack video cùng bị bỏ lọt. E02 và E03 cùng sai 23 false positive và 50 false negative, cho thấy hai backbone ImageNet head-only chia sẻ một phần failure mode.

Ở E03, APCER cao nhất trên phone 5 và 6 (31,25% và 28,75%); BPCER cao nhất ở phone 3 (40,00%). `printer 1` và `display 1` có APCER 25,83% và 25,00%, cao hơn instrument còn lại. Mười video lỗi đại diện đều có đủ mười crop, confidence detector trung bình 0,938–0,975; metadata không chỉ ra lỗi phát hiện mặt rõ ràng. Đây chỉ là bằng chứng loại trừ sơ bộ. Không thể từ confidence của detector kết luận crop hoàn hảo hoặc model đã học đúng cue.

E05 còn 22 false positive và 48 false negative. APCER print/replay là 7,92%/12,08%; `display_2` khó nhất với APCER 15,00%. So với E01, lỗi attack tăng ở cả print và replay, còn BPCER giảm rất mạnh. Điều này củng cố kết luận rằng RGB-LBP dịch operating behavior theo hướng cân bằng live/attack hơn, chứ không đơn thuần tăng độ nhạy với mọi spoof.

## 4.3. Đánh giá tài nguyên tính toán (Resource Benchmark)

| Model | Tổng tham số/hệ số | Tham số trainable | Artifact | Train time | Pure batch-1 | E2E batch-16 |
|---|---:|---:|---:|---:|---:|---:|
| E01 LBP-SVM | 640 hệ số | 640 hệ số | 21,7 KB | 0,68 s selected fit | **0,163 ms** | **0,733 ms/frame** |
| E02 MobileNetV2 | 2,23 M | 1.281 | 9,15 MB | 306,50 s | 3,247 ms | 0,991 ms/frame |
| E03 ResNet18 | 11,18 M | 513 | 44,79 MB | 272,51 s | 1,595 ms | 0,966 ms/frame |
| E04 ResNet18 | 11,18 M | 8.394.241 | 44,79 MB | 216,54 s/9 epoch | 1,759 ms* | như E03 về graph |
| E05 RGB-LBP-SVM | 1.920 hệ số | 1.920 hệ số | 62,7 KB | 2,82 s selected fit | chưa đo | chưa benchmark chuẩn hóa |

\* Pure batch-1 E04 được đo trong main run, không phải cùng phép benchmark chuẩn hóa ba baseline. E04 có cùng inference graph và tổng tham số với E03 nên không có lý do lý thuyết để inference tốn thêm theo số tham số *đã từng được train*. Chênh lệch nhỏ giữa hai lần đo có thể là nhiễu runtime.

E05 chỉ có phép đo `decision_function` theo batch 6.000 test feature là 0,0073 ms/frame; đây không phải pure batch-1 hoặc E2E. Full cache mất 73,00 giây và 62,14 MB, gần ba lần E01.

MobileNetV2 nhỏ hơn ResNet18 khoảng 4,9 lần nhưng không nhanh hơn trong phép đo RTX 3060 này. Công thức FLOPs không phản ánh đầy đủ khả năng tối ưu kernel, memory access và mức song song của GPU. Không được suy rộng benchmark này sang CPU hoặc điện thoại nếu chưa đo trực tiếp.

E04 dùng peak GPU memory 374,0 MB so với 273,0 MB của E03 vì backward phải giữ activation/gradient của `layer4`. Thời gian train tổng thấp hơn E03 chỉ vì E04 dừng ở epoch 9; không có nghĩa một epoch fine-tune rẻ hơn head-only.

## 4.4. Thảo luận lý thuyết và thực tiễn

### Khoảng cách dev–test

| Model | Dev ACER | Test ACER | Chênh lệch tuyệt đối |
|---|---:|---:|---:|
| E01 LBP-SVM | 10,97% | 32,71% | +21,74 điểm % |
| E02 MobileNetV2 | 13,75% | 25,10% | +11,35 điểm % |
| E03 ResNet18 head | 13,06% | 23,85% | +10,80 điểm % |
| E04 ResNet18 layer4 | 2,57% | 14,79% | +12,22 điểm % |
| E05 RGB-LBP-SVM | 2,71% | 14,17% | +11,46 điểm % |

LBP-SVM đảo thứ hạng từ tốt nhất baseline trên dev thành kém nhất trên test, phù hợp với H1 rằng texture cố định nhạy với thay đổi phân phối. CNN giảm mức suy giảm tương đối nhưng vẫn có domain gap rõ. E04 tăng khả năng phân biệt trên cả dev và test, song dev quá tốt không đồng nghĩa test đã được giải quyết. E05 giảm gap của E01 từ 21,74 còn 11,46 điểm nhưng vẫn chưa loại bỏ domain shift.

### Frame-level so với video-level

| Model | Test frame ACER | Test video ACER | Video − frame |
|---|---:|---:|---:|
| E01 LBP-SVM | 30,58% | 32,71% | +2,13 điểm % |
| E02 MobileNetV2 | 25,69% | 25,10% | -0,58 điểm % |
| E03 ResNet18 head | 24,03% | 23,85% | -0,18 điểm % |
| E04 ResNet18 layer4 | **13,41%** | 14,79% | +1,39 điểm % |
| E05 RGB-LBP-SVM | 16,28% | **14,17%** | -2,11 điểm % |

Mean aggregation cải thiện E02/E03/E05 và làm xấu E01/E04. Với E04, aggregation giảm APCER frame 6,31% xuống video 5,42%, nhưng BPCER tăng từ 20,50% lên 24,17%; tổng hợp lại ACER tăng. Kết quả bác bỏ phiên bản mạnh của H4 rằng lấy trung bình luôn tốt hơn.

Nguyên nhân có thể là score của các frame cùng video tương quan và có bias; đây là diễn giải thống kê phù hợp với kết quả, chưa phải bằng chứng nhân quả. Muốn kết luận chắc chắn cần phân tích trajectory score và chất lượng từng frame.

### Từ vật lý recapture đến biểu diễn ảnh

Bài toán bắt đầu từ giả thuyết rằng PAI làm thay đổi quá trình tạo ảnh. Pipeline không đo trực tiếp màn hình, giấy hay chiều sâu; nó quan sát các hệ quả trên pixel. Crop mặt tăng tỷ lệ tín hiệu liên quan, resize đưa ảnh về miền kích thước chung, còn hai họ biểu diễn tìm cue theo cách khác nhau:

- Gray/RGB-LBP kiểm tra quan hệ cường độ theo từng kênh ở lân cận bán kính một pixel và đếm mẫu;
- CNN học các kernel đa kênh, đa tầng và trường tiếp nhận lớn dần.

Do resize là lọc thông thấp, cue mà model nhận được luôn là cue còn lại sau chuỗi preprocessing. Kết quả không đại diện cho mọi dấu vết vật lý trong video gốc.

### Vì sao LBP có dev tốt nhưng test xấu?

LBP có ưu điểm bất biến với biến đổi mức xám đơn điệu và rất phù hợp để mã hóa micro-texture. Tuy nhiên, ánh xạ riu2 bỏ thông tin hướng; grayscale bỏ màu; bán kính một chỉ quan sát cấu trúc rất nhỏ. Histogram không biết mẫu nào do PAI, mẫu nào do da, camera, compression hoặc blur. Linear SVM sau đó chỉ tạo một biên phẳng trên đặc trưng cố định.

Dev ACER 10,97% chứng minh feature chứa tín hiệu phân biệt trong miền dev. Test BPCER 60% cho thấy operating point không chuyển tốt sang live test. Điều này phù hợp với nhạy cảm miền, nhưng báo cáo không khẳng định nguyên nhân duy nhất là ánh sáng hay camera nếu chưa có thí nghiệm can thiệp.

### Vì sao RGB-LBP cải thiện mạnh E01?

Grayscale chiếu màu về một trục cường độ nên hai pixel khác phổ màu vẫn có thể cùng mức xám. RGB-LBP giữ ba quan hệ thứ tự cục bộ, nhờ đó SVM có thể dùng texture màu bị biến đổi qua in/hiển thị/recapture. Test ACER giảm 18,54 điểm và BPCER giảm 41,67 điểm cho thấy thông tin bị mất khi grayscale hóa có giá trị trong thiết lập này.

Tuy nhiên APCER tăng 4,58 điểm: biên quyết định mới chấp nhận live tốt hơn nhưng cũng bỏ lọt thêm attack. Kết quả không chứng minh từng kênh là cue nhân quả; hệ số chuẩn hóa phân bố tương đối đều trên R/G/B chỉ là mô tả. Cần ablation từng kênh hoặc không gian màu khác trên dev/protocol mới để tách vai trò màu.

### Vì sao MobileNetV2 nhỏ nhưng không thắng ResNet18?

Depthwise separable convolution giảm phép nhân và tham số theo công thức ở mục 2.10. Đây là tối ưu kiến trúc, không đảm bảo feature đóng băng phù hợp hơn với PAD. E02 chỉ học 1.281 tham số; mọi bộ lọc không gian vẫn là bộ lọc học từ ImageNet. E03 cũng head-only nhưng ResNet18 cho test ACER thấp hơn 1,25 điểm, có thể do biểu diễn hoặc động học phần cứng khác. Với một seed và hai pretrained recipe khác nhau, chênh lệch nhỏ này không đủ để kết luận ResNet luôn tốt hơn.

### Ý nghĩa của E04 dưới góc nhìn transfer learning

Head-only chỉ học

$$
z=\mathbf{w}^{T}\phi_{ImageNet}(x)+b.
$$

Nếu feature $\phi_{ImageNet}$ chưa tách được live/spoof, classifier tuyến tính không thể tạo thông tin mới. E04 thay nó bằng

$$
z=\mathbf{w}^{T}\phi_{layer4}(\phi_{frozen}(x);\theta_{PAD})+b,
$$

trong đó $\theta_{PAD}$ được cập nhật. `layer4` có thể tổ hợp lại feature cấp thấp thành biểu diễn phù hợp đích; shortcut giữ đường truyền thông tin và learning rate nhỏ hạn chế dịch chuyển quá mạnh.

ACER giảm 9,06 điểm là bằng chứng thực nghiệm rằng thích nghi feature hữu ích trong thiết lập này. Nó không chứng minh layer4 “nhìn thấy moiré” nếu chưa có visualization hoặc thí nghiệm triệt tiêu tần số. Cách diễn đạt đúng là kết quả *nhất quán với* giả thuyết học cue PAD chuyên biệt.

### Vai trò của weighted BCE và metric cân bằng

Weighted BCE xử lý mất cân bằng ở pha học bằng cách cân tổng đóng góp của live và spoof. ACER xử lý mất cân bằng ở pha đánh giá bằng cách tính error riêng cho mỗi lớp rồi lấy trung bình. Hai cơ chế không trùng nhau: loss tối ưu tham số liên tục trên frame train; ACER đo quyết định rời rạc trên video tại một threshold.

Kết quả E01 minh họa lý do cần cả hai phía. Recall/F1 spoof cao không bù được việc 72/120 live bị chặn. Trong ứng dụng, APCER liên quan rủi ro an ninh còn BPCER liên quan khả năng sử dụng; lựa chọn operating point cuối cùng phải dựa trên chi phí nghiệp vụ, không nhất thiết là min-ACER.

### Vì sao trung bình video có thể thất bại?

Nếu $s_{v,k}=\mu_v+\epsilon_{v,k}$ với nhiễu độc lập kỳ vọng 0, phương sai của trung bình giảm xấp xỉ $1/K$. Nhưng nếu $s_{v,k}=\mu_v+b_v+\epsilon_{v,k}$, bias $b_v$ chung cho mọi frame không giảm khi lấy trung bình. Frame cùng video còn tương quan mạnh nên mức giảm phương sai nhỏ hơn giả định độc lập.

E02/E03 được lợi nhẹ, E05 được lợi 2,11 điểm, còn E01/E04 xấu đi. Vì vậy temporal aggregation cần được xem như một mô hình thống kê có giả định. Median, trimmed mean, quality weighting, attention pooling hoặc mô hình tuần tự là hướng so sánh tiếp theo, nhưng phải chọn trên dev/protocol mới chứ không tune lại bằng test hiện tại.

### Trả lời câu hỏi nghiên cứu

1. **RQ1:** LBP có tín hiệu tốt trên dev và APCER test thấp, nhưng BPCER 60% làm ACER test kém nhất. Biểu diễn texture cố định chưa đủ tổng quát.
2. **RQ2:** Head-only tạo baseline hợp lý nhưng chưa đủ: E02/E03 còn ACER 25,10%/23,85%.
3. **RQ3:** Fine-tune `layer4` giảm E03 ACER từ 23,85% xuống 14,79%, chủ yếu do giảm attack bị bỏ lọt.
4. **RQ4:** Không. Aggregation cải thiện E02/E03/E05 nhưng làm xấu E01/E04.
5. **RQ5:** Không. E01 có F1 90,26% trong khi BPCER 60%; ACER và hai thành phần lỗi là bắt buộc để diễn giải đúng.
6. **RQ6:** Có trong E05: ACER giảm từ 32,71% xuống 14,17%. Cải thiện chủ yếu đến từ BPCER giảm 41,67 điểm, trong khi APCER tăng 4,58 điểm.

### Các đe dọa tới tính hợp lệ

- **Một seed:** chưa có trung bình, độ lệch chuẩn hoặc khoảng tin cậy.
- **Một protocol:** chưa đo robustness với camera/PAI/protocol khác hoặc cross-dataset.
- **Selection trên dev:** E04/E05 có thể đã phù hợp mạnh với dev; gap test 12,22/11,46 điểm vẫn lớn.
- **Ảnh tĩnh:** mean score không học chuyển động, rPPG, blink hoặc flicker.
- **Crop trung gian:** benchmark không gồm decode và face detector; latency chưa phải latency hệ thống hoàn chỉnh.
- **Không attribution:** cải thiện CNN chưa chỉ ra cue nhân quả mà model dùng.
- **Kích thước đầu vào khác nhau:** LBP 128 và CNN 224 là cấu hình chuẩn từng phương pháp nhưng cũng là một khác biệt ngoài classifier.
- **Một không gian màu:** E05 chỉ khảo sát RGB độc lập, chưa có HSV/YCbCr, opponent-color LBP hay ablation từng kênh.
- **Ngưỡng min-ACER:** phù hợp mục tiêu cân bằng, chưa chắc phù hợp chi phí an ninh thực tế.

# Chương 5. Kết luận và Hướng phát triển

## 5.1. Kết luận

Đề tài đã triển khai một hệ thống face PAD từ video đến quyết định video và đối chiếu hai hướng xử lý ảnh: feature thủ công LBP-SVM và feature học bằng CNN pretrained. Kết quả quan trọng nhất không phải chỉ là E04 đạt ACER 14,79%, mà là ablation E03/E04 cho thấy phạm vi fine-tune quyết định khả năng thích nghi miền. ImageNet feature đóng băng hoàn toàn tạo một bộ trích đặc trưng chung; mở `layer4` với learning rate nhỏ cho phép mạng học lại tổ hợp feature theo mục tiêu PAD và giảm ACER 9,06 điểm phần trăm.

Ablation E01/E05 bổ sung một kết luận xử lý ảnh quan trọng: phép grayscale làm mất tín hiệu có ích cho PAD. Giữ LBP riêng trên R/G/B giảm ACER 18,54 điểm, đạt 14,17% — thấp nhất trong năm cấu hình — chủ yếu nhờ BPCER giảm mạnh. E04 vẫn có F1/APCER tốt hơn; vì vậy không có một mô hình thắng ở mọi tiêu chí.

Các nguyên lý xử lý ảnh được áp dụng xuyên suốt: lấy mẫu rời rạc, chuẩn hóa ROI, nội suy, grayscale/RGB normalization, texture operator, histogram, phân lớp biên cực đại, tích chập phân cấp, residual/depthwise block, transfer learning, weighted risk, aggregation và lý thuyết quyết định. Kết quả đồng thời chỉ ra giới hạn của từng nguyên lý: grayscale LBP mất màu/ngữ cảnh, RGB-LBP tăng ba lần chiều và vẫn phụ thuộc miền, CNN phụ thuộc miền, aggregation không khử bias, và F1 không thay thế metric PAD cân bằng.

## 5.2. Hướng phát triển

1. Chạy ít nhất 3–5 seed cho E03/E04/E05, báo trung bình, độ lệch chuẩn và khoảng tin cậy; đây là bước cần làm trước khi mở rộng kiến trúc.
2. Đánh giá Protocol 2–4 với config khóa trước, không dùng test Protocol 1 để chọn tiếp hyperparameter.
3. Phân tích phổ tần, Grad-CAM/feature attribution và thí nghiệm blur/color để kiểm tra model thực sự dùng cue nào.
4. So sánh ablation từng kênh, HSV/YCbCr, opponent-color hoặc multi-scale LBP, residual texture và frequency feature trên protocol mới.
5. Thử quality-aware hoặc learned temporal aggregation trên dev độc lập.
6. Benchmark toàn pipeline gồm decode, sampling và face detection trên CPU và thiết bị edge mục tiêu.
7. Sau khi có protocol mới, khảo sát fine-tune nhiều stage, regularization, domain generalization hoặc supervision theo depth/texture.

# Tài liệu tham khảo

[1] V. Bazarevsky, Y. Kartynnik, A. Vakunov, K. Raveendran và M. Grundmann, “BlazeFace: Sub-millisecond Neural Face Detection on Mobile GPUs,” 2019. [arXiv:1907.05047](https://arxiv.org/abs/1907.05047).

[2] T. Ojala, M. Pietikäinen và T. Mäenpää, “Multiresolution Gray-Scale and Rotation Invariant Texture Classification with Local Binary Patterns,” *IEEE TPAMI*, 24(7), 971–987, 2002. [DOI: 10.1109/TPAMI.2002.1017623](https://doi.org/10.1109/TPAMI.2002.1017623).

[3] J. Määttä, A. Hadid và M. Pietikäinen, “Face Spoofing Detection From Single Images Using Micro-Texture Analysis,” *IJCB*, 2011. [DOI: 10.1109/IJCB.2011.6117510](https://doi.org/10.1109/IJCB.2011.6117510).

[4] C. Cortes và V. Vapnik, “Support-Vector Networks,” *Machine Learning*, 20, 273–297, 1995. [DOI: 10.1007/BF00994018](https://doi.org/10.1007/BF00994018).

[5] S. Ioffe và C. Szegedy, “Batch Normalization: Accelerating Deep Network Training by Reducing Internal Covariate Shift,” 2015. [arXiv:1502.03167](https://arxiv.org/abs/1502.03167).

[6] D. P. Kingma và J. Ba, “Adam: A Method for Stochastic Optimization,” 2014. [arXiv:1412.6980](https://arxiv.org/abs/1412.6980).

[7] K. He, X. Zhang, S. Ren và J. Sun, “Deep Residual Learning for Image Recognition,” *CVPR*, 2016. [CVF Open Access](https://openaccess.thecvf.com/content_cvpr_2016/html/He_Deep_Residual_Learning_CVPR_2016_paper.html).

[8] M. Sandler, A. Howard, M. Zhu, A. Zhmoginov và L.-C. Chen, “MobileNetV2: Inverted Residuals and Linear Bottlenecks,” *CVPR*, 2018. [CVF Open Access](https://openaccess.thecvf.com/content_cvpr_2018/html/Sandler_MobileNetV2_Inverted_Residuals_CVPR_2018_paper).

[9] ISO/IEC 30107-3:2023, “Information technology — Biometric presentation attack detection — Part 3: Testing and reporting.” [ISO](https://www.iso.org/standard/79520.html).

[10] Z. Boulkenafet, J. Komulainen, L. Li, X. Feng và A. Hadid, “OULU-NPU: A Mobile Face Presentation Attack Database with Real-World Variations,” *FG*, 2017. [DOI: 10.1109/FG.2017.77](https://doi.org/10.1109/FG.2017.77).

[11] R. C. Gonzalez và R. E. Woods, *Digital Image Processing*, 4th ed., Pearson, 2018, ISBN 978-0-13-335672-4.

[12] ISO/IEC 30107-1:2016, “Information technology — Biometric presentation attack detection — Part 1: Framework.” [ISO](https://www.iso.org/standard/53227.html).

# Phụ lục A. Bản đồ tài liệu và artifact

| Nội dung cần kiểm tra | Tệp/thư mục |
|---|---|
| Đề cương ban đầu | `docs/de_cuong_chi_tiet_face_spoofing_oulu_npu.md` |
| Báo cáo số liệu rút gọn | `docs/bao_cao_thuc_nghiem_face_spoofing_oulu_npu.md` |
| Kết quả E01 | `docs/ket_qua_e01_lbp_svm.md` |
| Kết quả E02 | `docs/ket_qua_e02_mobilenet_v2.md` |
| Kết quả E03 | `docs/ket_qua_e03_resnet18.md` |
| Kết quả E04 | `docs/ket_qua_e04_resnet18_finetune_layer4.md` |
| Kế hoạch/kết quả E05 | `docs/ke_hoach_e05_rgb_lbp_svm.md`, `docs/ket_qua_e05_rgb_lbp_svm.md` |
| Benchmark | `docs/benchmark_tai_nguyen_e01_e03.md` |
| Data config | `configs/data/oulu_protocol1.yaml` |
| LBP/SVM code | `src/face_spoofing/features/lbp.py`, `src/face_spoofing/models/lbp_svm.py` |
| CNN code | `src/face_spoofing/models/mobilenet_v2.py`, `src/face_spoofing/models/resnet18.py` |
| Metric/aggregation | `src/face_spoofing/evaluation/metrics.py`, `aggregation.py` |
| Artifact E01–E05 | `artifacts/runs/` |

# Phụ lục B. Cấu hình cốt lõi để tái lập

```text
Data: OULU-NPU Protocol 1; live=0; spoof=1; 10 frame/video
Crop: MediaPipe 0.5; margin=0.2; output=256x256
E01: gray128; LBP riu2 P=8,R=1; grid8x8; LinearSVC C=1e-4
E02: MobileNetV2 ImageNet V2; frozen backbone; train head 1,281 params
E03: ResNet18 ImageNet V1; frozen backbone; train head 513 params
E04: ResNet18; train layer4 at 1e-5 and head at 1e-4
E05: RGB128; concatenate LBP(R/G/B); 1,920D; LinearSVC C=1e-4
CNN: RGB224; ImageNet normalize; flip=0.5 train-only; batch=16
Loss: BCEWithLogits; pos_weight=0.25; Adam; weight_decay=1e-4
Selection: dev video ACER/APCER/F1; threshold from dev; test after freeze
Aggregation: arithmetic mean score per video
Seed: 42
```

# Phụ lục C. Checklist trước khi nộp

- [ ] Điền trường, khoa, giảng viên, sinh viên, MSSV và lớp ở trang bìa.
- [ ] Sinh mục lục, danh mục bảng/hình và đánh số trang trong bản PDF.
- [ ] Kiểm tra font/công thức khi chuyển Markdown sang Word hoặc LaTeX.
- [ ] Không thay số liệu bằng kết quả từ run khác mà chưa cập nhật artifact.
- [ ] Nếu thêm biểu đồ, lấy dữ liệu trực tiếp từ `metrics.json/result.json`.
- [ ] Phân biệt rõ kết luận thực nghiệm với giả thuyết về cue model đã học.
- [ ] Ghi rõ chỉ một seed và chỉ Protocol 1 trong phần bảo vệ.

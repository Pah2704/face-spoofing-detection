# BÁO CÁO MÔN HỌC XỬ LÝ ẢNH NÂNG CAO

## PHÁT HIỆN GIẢ MẠO KHUÔN MẶT TRÊN OULU-NPU BẰNG ĐẶC TRƯNG VI KẾT CẤU VÀ MẠNG NƠ-RON TÍCH CHẬP

---

**Trường:** ..............................................................

**Khoa/Bộ môn:** .........................................................

**Học phần:** Xử lý ảnh nâng cao

**Giảng viên hướng dẫn:** ................................................

**Học viên thực hiện:** ..................................................

**Mã số học viên:** ......................................................

**Lớp:** .................................................................

**TP. Hồ Chí Minh, tháng 7 năm 2026**

---

## Lời cam đoan

Báo cáo trình bày quá trình xây dựng và đánh giá một hệ thống phát hiện giả mạo
khuôn mặt trên OULU-NPU Protocol 1. Toàn bộ số liệu thực nghiệm trong báo cáo
được đọc trực tiếp từ artifact của dự án; cấu hình đã giải quyết, checkpoint,
ngưỡng quyết định và dự đoán ở cả cấp khung hình lẫn cấp video đều được lưu lại
để có thể kiểm tra lại một cách độc lập. Những kiến thức và kết quả kế thừa từ
bài giảng của môn học cũng như từ các công trình khác đều được trích dẫn trong
phần tài liệu tham khảo, kèm số slide hoặc số trang cụ thể.

Học viên cam đoan không sử dụng tập kiểm tra (test) vào bất kỳ quyết định thiết
kế, lựa chọn siêu tham số hay lựa chọn ngưỡng nào.

---

## Tóm tắt

Giả mạo khuôn mặt bằng ảnh in hoặc video phát lại là một dạng tấn công trình
diện (presentation attack) có khả năng đánh lừa những hệ thống xác thực chỉ dựa
trên nhận dạng danh tính. Báo cáo xây dựng một pipeline xử lý video hoàn chỉnh
gồm sáu khâu: lấy mẫu khung hình, phát hiện và chuẩn hóa vùng khuôn mặt, biểu
diễn ảnh, phân lớp, gộp điểm số theo video và đánh giá bằng bộ chỉ số APCER,
BPCER, ACER.

Bốn thí nghiệm được thực hiện trên cùng một tập dữ liệu OULU-NPU Protocol 1,
cùng một quy trình cắt mặt và cùng một bộ đánh giá: Local Binary Pattern kết hợp
máy vector hỗ trợ tuyến tính (E01), MobileNetV2 tiền huấn luyện chỉ học lớp phân
lớp (E02), ResNet18 tiền huấn luyện chỉ học lớp phân lớp (E03), và ResNet18 tinh
chỉnh khối `layer4` cùng lớp phân lớp (E04).

Trọng tâm của báo cáo không chỉ là so sánh độ chính xác giữa bốn cấu hình, mà là
giải thích một cách có hệ thống các nguyên lý xử lý ảnh và nhận dạng mẫu đã được
vận dụng: lý thuyết lấy mẫu tín hiệu; nội suy và chuẩn hóa hình học; mã hóa vi
kết cấu bằng Local Binary Pattern; giảm chiều bằng PCA và LDA; phân lớp biên cực
đại bằng SVM; tích chập, chuẩn hóa theo lô và học phần dư trong mạng nơ-ron tích
chập; tích chập tách theo chiều sâu; học chuyển giao; lý thuyết quyết định trong
việc chọn ngưỡng và gộp bằng chứng theo thời gian. Mỗi khối lý thuyết đều được
nối trực tiếp với tham số cấu hình, vị trí mã nguồn và artifact thực nghiệm
tương ứng.

Kết quả ở cấp video trên tập kiểm tra cho ACER lần lượt là 32,71% (LBP-SVM),
25,10% (MobileNetV2), 23,85% (ResNet18 head-only) và 14,79% (ResNet18 tinh chỉnh
`layer4`). Thí nghiệm E04 cải thiện 9,06 điểm phần trăm so với E03, cho thấy
biểu diễn ImageNet bị đóng băng hoàn toàn chưa đủ thích nghi với tín hiệu vi kết
cấu của tấn công trình diện. Tuy vậy, khoảng cách ACER giữa tập phát triển và
tập kiểm tra của E04 vẫn còn 12,22 điểm phần trăm; do đó kết quả chưa chứng minh
được khả năng tổng quát hóa ra ngoài phạm vi Protocol 1.

**Từ khóa:** xử lý ảnh nâng cao, phát hiện giả mạo khuôn mặt, tấn công trình
diện, Local Binary Pattern, máy vector hỗ trợ, mạng nơ-ron tích chập, học chuyển
giao, OULU-NPU.

---

## Danh mục chữ viết tắt

| Ký hiệu | Tiếng Anh | Nghĩa tiếng Việt |
|---|---|---|
| PAD | Presentation Attack Detection | Phát hiện tấn công trình diện |
| PAI | Presentation Attack Instrument | Công cụ tấn công trình diện |
| LBP | Local Binary Pattern | Mẫu nhị phân cục bộ |
| SVM | Support Vector Machine | Máy vector hỗ trợ |
| CNN | Convolutional Neural Network | Mạng nơ-ron tích chập |
| PCA | Principal Component Analysis | Phân tích thành phần chính |
| LDA | Linear Discriminant Analysis | Phân tích tách lớp tuyến tính |
| ICA | Independent Component Analysis | Phân tích thành phần độc lập |
| BN | Batch Normalization | Chuẩn hóa theo lô |
| BCE | Binary Cross-Entropy | Entropy chéo nhị phân |
| ROI | Region of Interest | Vùng quan tâm |
| TP / TN | True Positive / True Negative | Dương tính thật / Âm tính thật |
| FP / FN | False Positive / False Negative | Dương tính giả / Âm tính giả |
| APCER | Attack Presentation Classification Error Rate | Tỉ lệ tấn công bị phân loại nhầm |
| BPCER | Bona Fide Presentation Classification Error Rate | Tỉ lệ mẫu thật bị phân loại nhầm |
| ACER | Average Classification Error Rate | Tỉ lệ lỗi phân loại trung bình |
| EER | Equal Error Rate | Tỉ lệ lỗi cân bằng |
| ROC | Receiver Operating Characteristic | Đường đặc trưng hoạt động |
| RQ | Research Question | Câu hỏi nghiên cứu |
| LR | Learning Rate | Tốc độ học |

---

## Quy ước trích dẫn nguồn giáo trình

Để người đọc kiểm chứng được từng luận điểm lý thuyết, báo cáo sử dụng hệ ký
hiệu sau cho tài liệu môn học:

| Ký hiệu | Tài liệu |
|---|---|
| **[S1]** | Slide *Nhân trắc học* — Thái Hoàng Lê, Khoa CNTT, ĐH KHTN TP.HCM (58 slide) |
| **[S2]** | Slide *Nhận dạng mẫu và ứng dụng thử nghiệm* — Lê Hoàng Thái (35 slide) |
| **[S3]** | Slide *Local Binary Patterns* (54 slide) |
| **[S4]** | Slide *Principal Component Analysis — Some Mathematical Backgrounds* — A. van Erk (58 slide) |
| **[S5]** | Slide *Dimensionality Reduction Using PCA/LDA — Case Studies* (56 slide) |
| **[S6]** | Slide *PCA and LDA for Feature Reduction* — Jieping Ye, ASU (40 slide) |
| **[S7]** | Slide *An Introduction of Support Vector Machine* — Jinwei Gu, 2008 (36 slide) |
| **[S8]** | Slide *Deep Learning Tutorial* — Hung-yi Lee (109 slide) |
| **[HFR]** | *Handbook of Face Recognition*, 2nd ed., Li & Jain (eds.), Springer, 2011 |
| **[HB]** | *Handbook of Biometrics*, Jain, Flynn & Ross (eds.), Springer, 2008 |

Các tài liệu ngoài phạm vi môn học được trích theo số thứ tự trong danh mục Tài
liệu tham khảo, ví dụ [7].

> **Ghi chú minh bạch về nguồn.** Bộ slide của môn học cung cấp đầy đủ nền tảng
> cho nhân trắc học, nhận dạng mẫu, LBP, PCA/LDA, SVM và mạng nơ-ron truyền
> thẳng. Tuy nhiên, [S8] dừng lại ở mạng nơ-ron nhiều lớp, hạ gradient, ReLU và
> dropout, **không trình bày mạng tích chập**. Vì vậy các mục 7.4 đến 7.6 của
> báo cáo — phép tích chập, chuẩn hóa theo lô, học phần dư và tích chập tách
> theo chiều sâu — được xây dựng trên tài liệu ngoài [7], [8], [10], [11] và
> được ghi chú rõ ràng tại chỗ. Báo cáo không gán những nội dung này cho bài
> giảng của môn học.

---

# Chương 1. Giới thiệu

## 1.1. Đặt vấn đề

Khuôn mặt là một trong những đặc trưng nhân trắc học được sử dụng rộng rãi nhất
hiện nay. Ưu thế của nó nằm ở khả năng thu nhận: chỉ cần một camera thông
thường, không yêu cầu tiếp xúc vật lý, không đòi hỏi người dùng thực hiện thao
tác đặc biệt nào. Bảng so sánh các đặc trưng nhân trắc học trong [S1] slide 14
cho thấy khuôn mặt đạt điểm rất cao ở hai tiêu chí *khả năng thu nhận* và *khả
năng được chấp nhận bởi người dùng*.

Chính sự thuận tiện đó tạo ra lỗ hổng. Một đặc trưng có thể thu nhận từ xa bằng
camera thông thường cũng là một đặc trưng có thể **sao chép** bằng camera thông
thường. Ảnh chân dung của một người xuất hiện công khai trên mạng xã hội, ảnh
thẻ, hoặc một đoạn video ngắn đều có thể trở thành nguyên liệu để tạo ra vật giả
mạo.

Điểm mấu chốt cần phân biệt là hai câu hỏi hoàn toàn khác nhau mà một hệ thống
thị giác máy tính có thể được yêu cầu trả lời:

1. *"Khuôn mặt này có phải của người A hay không?"* — đây là bài toán **nhận
   dạng khuôn mặt**, đã có lời giải tương đối hoàn chỉnh với sơ đồ bốn khâu
   trong [S1] slide 21 và slide 28: tìm khuôn mặt, chuẩn hóa khuôn mặt, trích
   chọn đặc trưng, so khớp đặc trưng.
2. *"Khuôn mặt này đang xuất hiện trực tiếp trước camera, hay chỉ là hình ảnh
   của người A trên giấy hoặc trên màn hình?"* — đây là bài toán **phát hiện tấn
   công trình diện (PAD)**, và là trọng tâm của báo cáo này.

Một hệ thống chỉ giải quyết câu hỏi thứ nhất sẽ hoạt động hoàn hảo theo đúng
thiết kế của nó khi bị trình diện một tấm ảnh in của người A: nó nhận ra đúng
người A và cấp quyền truy cập. Lỗi ở đây không nằm ở bộ nhận dạng, mà nằm ở một
giả định ngầm chưa bao giờ được kiểm tra — giả định rằng vật được đưa vào trước
cảm biến là một khuôn mặt sống thật.

Theo phân loại các điểm tấn công vào hệ nhân trắc học trong [HB] Chương 19 và
Chương 20, tấn công trình diện nằm ở **điểm tấn công thứ nhất**, tức ngay tại
cảm biến. Đây là điểm tấn công đặc biệt vì nó không đòi hỏi kẻ tấn công phải xâm
nhập vào bất kỳ thành phần phần mềm hay kênh truyền nào của hệ thống; nó chỉ đòi
hỏi một tấm ảnh in và khả năng đứng trước camera. Bản chất "chi phí thấp, không
cần kỹ năng kỹ thuật" khiến đây là điểm tấn công thực tế nhất trong triển khai.

## 1.2. Cơ sở vật lý của bài toán

Câu hỏi nền tảng cần trả lời trước khi thiết kế bất kỳ thuật toán nào là: *về
mặt vật lý, có tồn tại sự khác biệt nào giữa ảnh của một khuôn mặt thật và ảnh
chụp lại của một khuôn mặt hay không?*

Câu trả lời nằm ở khái niệm **chuỗi thu nhận kép** hay **chuỗi tái chụp**
(recapture chain). Với một mẫu thật (bona fide), ánh sáng đi theo đường:

$$
\text{Khuôn mặt thật} \;\rightarrow\; \text{Camera hệ thống} \;\rightarrow\; \text{Ảnh số}
$$

Với một mẫu tấn công, ánh sáng phải đi qua một chuỗi dài hơn hẳn:

$$
\text{Khuôn mặt thật} \rightarrow \text{Camera 1} \rightarrow \text{Ảnh/Video số} \rightarrow \text{Máy in hoặc Màn hình} \rightarrow \text{Camera hệ thống} \rightarrow \text{Ảnh số}
$$

Mỗi mắt xích bổ sung trong chuỗi thứ hai đều là một phép biến đổi vật lý không
hoàn hảo, và mỗi phép biến đổi không hoàn hảo đều để lại dấu vết có thể đo được
trên ảnh cuối cùng. Đây chính là cơ sở vật lý cho phép các thuật toán xử lý ảnh
phân biệt hai lớp. Bảng dưới đây liệt kê các dấu vết chính, ánh xạ mỗi dấu vết
tới hệ quả quan sát được trên ảnh và tới chương của báo cáo khai thác dấu vết
đó:

| Nguồn gốc vật lý | Hệ quả đo được trên ảnh | Khai thác tại |
|---|---|---|
| Lấy mẫu lại trên lưới điểm ảnh của màn hình | Vân moiré, hiện tượng răng cưa (aliasing) tần số cao | Chương 4, Chương 5 |
| Nén và lượng tử hóa hai lần | Suy giảm chi tiết vi kết cấu, xuất hiện khối nén | Chương 5 (LBP) |
| Bề mặt phẳng thay cho bề mặt cong 3D | Mất bóng đổ tự nhiên, phân bố phản xạ bất thường | Chương 7 (CNN) |
| Sai lệch gam màu của máy in và màn hình | Dịch chuyển phân bố màu, giảm dải động | Chương 4 (mục 4.1) |
| Tái lấy nét trên bề mặt phẳng | Suy giảm năng lượng cạnh, mờ đồng đều bất thường | Chương 5 |
| Kết cấu vật liệu nền (sợi giấy, lớp phủ màn hình) | Kết cấu chồng lấn không thuộc về da | Chương 5, Chương 7 |

Từ bảng này rút ra một kết luận định hướng cho toàn bộ báo cáo: **PAD không phải
là một bài toán ngữ nghĩa mà là một bài toán về kết cấu và tần số.** Hệ thống
không cần hiểu "đây là khuôn mặt của ai" hay "biểu cảm là gì"; nó cần đo được
những biến đổi thống kê rất tinh vi ở mức vi mô của ảnh. Nhận định này giải
thích vì sao một mô tả vi kết cấu như Local Binary Pattern là ứng viên hợp lý về
mặt lý thuyết, và cũng là tiền đề để đánh giá xem một mạng tích chập tiền huấn
luyện trên tác vụ ngữ nghĩa (ImageNet) có thực sự phù hợp hay không.

## 1.3. Mục tiêu của báo cáo

Báo cáo đặt ra bốn mục tiêu cụ thể:

1. **Xây dựng một pipeline tái lập được** từ video thô đến quyết định ở cấp
   video, trong đó mọi bước biến đổi ảnh đều được ghi lại tường minh bằng tham
   số cấu hình và có thể kiểm tra lại bằng artifact.
2. **Đối chiếu hai triết lý biểu diễn ảnh** trên cùng một điều kiện thực nghiệm:
   biểu diễn *thủ công* do con người thiết kế (LBP kết hợp SVM) so với biểu diễn
   *học được* từ dữ liệu (MobileNetV2, ResNet18), với cùng protocol, cùng vùng
   cắt mặt và cùng bộ đánh giá.
3. **Làm rõ vai trò của từng nguyên lý xử lý ảnh và nhận dạng mẫu** trong mỗi
   thí nghiệm, thay vì trình bày mô hình như một hộp đen. Mỗi tham số cấu hình
   phải được biện minh bằng lý thuyết, và mỗi kết quả bất thường phải được giải
   thích bằng lý thuyết.
4. **Kiểm chứng tác động của phạm vi học chuyển giao** thông qua một thí nghiệm
   loại trừ (ablation) sạch giữa E03 (chỉ học lớp phân lớp) và E04 (mở thêm khối
   `layer4`), trong đó mọi yếu tố khác được giữ nguyên tuyệt đối.

## 1.4. Câu hỏi nghiên cứu

Năm câu hỏi sau định hướng toàn bộ thiết kế thực nghiệm và sẽ được trả lời dứt
điểm tại mục 9.7:

- **RQ1.** Đặc trưng vi kết cấu LBP còn hiệu quả đến đâu khi so với một mạng
  tích chập tiền huấn luyện, trong cùng điều kiện dữ liệu và đánh giá?
- **RQ2.** Việc chỉ học lớp phân lớp trên nền đặc trưng ImageNet đóng băng có đủ
  để chuyển từ miền ảnh tự nhiên sang miền phát hiện giả mạo khuôn mặt không?
- **RQ3.** Việc tinh chỉnh khối tích chập cuối của ResNet18 làm thay đổi sai số
  trên lớp tấn công và lớp thật như thế nào, khi mọi yếu tố còn lại được giữ
  nguyên?
- **RQ4.** Việc gộp trung bình điểm số của mười khung hình có luôn tốt hơn quyết
  định trên từng khung hình riêng lẻ không?
- **RQ5.** Chỉ số F1 có đủ để đánh giá một hệ thống PAD trên tập dữ liệu lệch
  lớp với 80% mẫu thuộc lớp tấn công không?

## 1.5. Phạm vi và giới hạn

Việc nêu rõ giới hạn ngay từ đầu là một yêu cầu về tính trung thực khoa học.
Báo cáo này **không** thực hiện những nội dung sau:

- **Chỉ Protocol 1** của OULU-NPU. Các Protocol 2, 3, 4 — vốn khảo sát khả năng
  tổng quát hóa theo công cụ tấn công, theo camera và theo môi trường — không
  được chạy. Do đó mọi kết luận về khả năng tổng quát hóa đều bị giới hạn.
- **Chỉ một hạt giống ngẫu nhiên** (seed 42). Không có giá trị trung bình, độ
  lệch chuẩn hay khoảng tin cậy trên nhiều lần chạy. Những chênh lệch nhỏ giữa
  các cấu hình vì vậy phải được diễn giải thận trọng.
- **Chỉ hai loại công cụ tấn công**: ảnh in và video phát lại. Không khảo sát
  mặt nạ 3D, mặt nạ silicon hay tấn công deepfake.
- **Không phân tích quy kết (attribution)**. Báo cáo không dùng Grad-CAM hay
  phân tích phổ tần để chứng minh mô hình thực sự nhìn vào dấu vết vật lý nào.
- **Không tuyên bố đạt trạng thái tốt nhất (SOTA)**. Mục tiêu là hiểu lý thuyết
  qua thực nghiệm có kiểm soát, không phải tối ưu con số.

## 1.6. Đóng góp

Trong phạm vi một báo cáo môn học, các đóng góp cụ thể gồm:

1. Một **pipeline PAD tái lập được hoàn toàn**, trong đó mỗi lần chạy lưu lại
   cấu hình đã giải quyết, ảnh chụp mã nguồn, thông tin môi trường, checkpoint,
   ngưỡng, dự đoán cấp khung hình và cấp video, cùng bản kê SHA-256.
2. Một **bảng truy vết lý thuyết – triển khai** (mục 9.3) ánh xạ hai mươi khái
   niệm lý thuyết tới tham số cấu hình cụ thể và vị trí mã nguồn tương ứng.
3. Một **thí nghiệm loại trừ sạch** về phạm vi tinh chỉnh (E03 so với E04), cho
   phép quy kết mức cải thiện 9,06 điểm ACER cho đúng một biến thay đổi.
4. Một **phân tích phản biện về chỉ số đánh giá**, chứng minh bằng số liệu rằng
   F1 cao có thể che giấu một hệ thống từ chối nhầm 60% người dùng hợp lệ.

## 1.7. Cấu trúc báo cáo

Báo cáo được tổ chức theo mạch đi từ khái niệm tổng quát đến chi tiết kỹ thuật,
rồi quay lại đối chiếu lý thuyết với thực nghiệm. Chương 2 đặt bài toán vào
khung khái niệm của nhân trắc học và phân loại tấn công, xác định chính xác PAD
bảo vệ được điều gì. Chương 3 trình bày khung lý thuyết nhận dạng mẫu, trong đó
pipeline của dự án được chứng minh là một hiện thân cụ thể của sơ đồ nhận dạng
mẫu kinh điển. Chương 4 đi vào các phép biến đổi ảnh ở giai đoạn tiền xử lý, bao
gồm lý thuyết lấy mẫu, phát hiện và chuẩn hóa vùng khuôn mặt, nội suy và chuẩn
hóa cường độ. Chương 5 trình bày biểu diễn đặc trưng thủ công với Local Binary
Pattern, kèm phân tích về giảm chiều bằng PCA và LDA như một lựa chọn thiết kế
được cân nhắc. Chương 6 xây dựng lý thuyết phân lớp biên cực đại. Chương 7
chuyển sang biểu diễn học sâu và học chuyển giao. Chương 8 thiết lập nền tảng lý
thuyết cho việc đánh giá và ra quyết định. Chương 9 trình bày thiết kế thực
nghiệm, kết quả định lượng và phần thảo luận nối kết quả trở lại với từng khối
lý thuyết đã xây dựng. Chương 10 kết luận và đề xuất hướng phát triển.

---

# Chương 2. Nhân trắc học và tấn công trình diện

Chương này thiết lập khung khái niệm cho toàn bộ báo cáo. Mục tiêu là xác định
chính xác vị trí của bài toán PAD trong hệ thống tri thức về nhân trắc học, và
làm rõ ranh giới của những gì PAD bảo vệ được.

## 2.1. Nhân trắc học: định nghĩa và vai trò

Theo [S1] slide 9, **nhân trắc học** được định nghĩa là việc *nhận dạng người tự
động trên cơ sở các bộ phận cơ thể riêng biệt — khuôn mặt, vân tay, tròng mắt,
võng mạc, hình bàn tay — hoặc thông qua các đặc điểm hành vi của con người như
chữ ký, dáng đi.*

Định nghĩa này có hai thành tố cần chú ý. Thứ nhất, từ *tự động* loại trừ các
phương pháp nhận diện thủ công. Thứ hai, việc phân đôi thành đặc trưng **sinh
lý** và đặc trưng **hành vi** có ý nghĩa trực tiếp với bài toán PAD: đặc trưng
sinh lý tĩnh như ảnh khuôn mặt dễ bị sao chép hơn nhiều so với đặc trưng hành vi
động, bởi vì sao chép một hình ảnh dễ hơn sao chép một quá trình.

[S1] slide 10 phân biệt ba vai trò khác nhau mà một hệ nhân trắc học có thể đảm
nhiệm:

| Vai trò | Câu hỏi hệ thống trả lời | Ví dụ ứng dụng |
|---|---|---|
| Nhận diện *chấp nhận* (positive identification) | Người đang xem xét có được hệ thống biết đến không? Nếu đúng thì cấp quyền truy nhập | Đăng nhập, mở khóa thiết bị |
| Nhận diện *độ thuộc lớn* (large scale identification) | Người này đã có trong cơ sở dữ liệu chưa? | Ngăn một người đăng ký nhiều quyền |
| *Trình duyệt* (screening) | Đây có phải người cần tìm không? | Đối chiếu danh sách theo dõi tại sân bay |

Điểm quan trọng — và cũng là luận điểm mở đầu của báo cáo — là **trong cả ba vai
trò, hệ thống đều ngầm giả định rằng mẫu sinh trắc đưa vào là mẫu thật.** Không
vai trò nào trong ba vai trò trên đặt ra câu hỏi về tính xác thực của chính vật
được trình diện. PAD chính là công việc gỡ bỏ giả định ngầm đó và biến nó thành
một phép kiểm tra tường minh.

## 2.2. Các tiêu chí của một đặc trưng nhân trắc học

Một đặc trưng sinh trắc được đánh giá theo bảy tiêu chí. Bảng dưới đây trình bày
từng tiêu chí kèm đánh giá dành riêng cho đặc trưng khuôn mặt, dựa trên [S1]
slide 14 và [HB] Chương 1:

| Tiêu chí | Nội dung | Đánh giá với khuôn mặt |
|---|---|---|
| Tính phổ quát (universality) | Mọi người đều có đặc trưng này | Rất cao |
| Tính phân biệt (distinctiveness) | Hai người khác nhau có giá trị khác nhau | Trung bình — sinh đôi cùng trứng là trường hợp khó |
| Tính bền vững (permanence) | Không đổi theo thời gian | Trung bình — thay đổi theo tuổi, cân nặng, râu tóc |
| Khả năng thu nhận (collectability) | Đo được dễ dàng bằng thiết bị | **Rất cao** — chỉ cần camera thông thường |
| Hiệu năng (performance) | Độ chính xác và tốc độ đạt được | Cao với điều kiện thu nhận kiểm soát |
| Khả năng chấp nhận (acceptability) | Người dùng sẵn sàng sử dụng | **Rất cao** — không tiếp xúc, không xâm lấn |
| **Khả năng chống giả mạo (circumvention)** | Khó bị đánh lừa bằng vật giả | **Thấp** |

Bảng này cho thấy rõ một nghịch lý mang tính cấu trúc: hai tiêu chí khiến khuôn
mặt được ưa chuộng nhất trong triển khai thực tế — *dễ thu nhận* và *dễ được
chấp nhận* — lại chính là hai tiêu chí làm nó **yếu nhất về khả năng chống giả
mạo**. Một đặc trưng có thể thu nhận từ xa bằng thiết bị phổ thông cũng là một
đặc trưng có thể tái tạo bằng thiết bị phổ thông. Đây là lý do tồn tại của toàn
bộ lĩnh vực PAD và của đề tài này.

## 2.3. Lược sử phát triển

[S1] slide 13 cung cấp các mốc phát triển chính của lĩnh vực nhân trắc học:

- **1882** — Hệ thống Bertillon chụp ảnh đối tượng và ghi lại chiều cao, chiều
  dài chân, cánh tay và các ngón tay.
- **1900** — Hệ thống Galton/Henry cho phép phân lớp ảnh vân tay, được Scotland
  Yard tiếp nhận.
- **1924** — FBI thiết lập hệ thống nhận diện ảnh vân tay.
- **1965** — AFIS được cài đặt với cơ sở dữ liệu 810.000 mẫu vân tay.
- **1971** — Bài báo đầu tiên về nhận dạng mặt người được công bố (Goldstein và
  cộng sự).
- **2000** — FBI triển khai IAFIS với hơn 47 triệu mẫu vân tay, trung bình
  50.000 lượt truy cập mỗi ngày.

Diễn tiến này cho thấy một quy luật đáng chú ý. Trong gần một thế kỷ đầu, toàn
bộ nỗ lực nghiên cứu tập trung vào việc **nâng cao độ chính xác nhận dạng**. Chỉ
khi độ chính xác đã đủ cao để các hệ thống được triển khai rộng rãi trong những
ứng dụng có giá trị — kiểm soát biên giới, thanh toán, mở khóa thiết bị — thì
chúng mới trở thành mục tiêu đáng để tấn công. PAD vì vậy là một mối quan tâm
**xuất hiện muộn**, sinh ra từ chính thành công của bài toán nhận dạng. [S1]
slide 13 cũng ghi nhận rằng *các hệ thống nhận diện hoạt động bên ngoài sự giám
sát của con người thường có sai số lớn* — đây chính là kịch bản mà tấn công
trình diện khai thác.

## 2.4. Các thách thức của hệ nhân trắc học

[S1] slide 16 liệt kê chín nhóm khó khăn của một hệ nhân trắc học:

1. Những biến đổi bên trong mỗi lớp và tính tương đồng giữa các lớp
2. Quá trình phân đoạn
3. Nhiễu đầu vào và tính hội tụ của quần thể
4. Hiệu suất hệ thống (tỉ lệ lỗi, tốc độ, chi phí)
5. Tính riêng biệt của các đặc trưng nhân trắc học
6. Sự hợp nhất của các thuộc tính nhân trắc học đa dạng
7. Tính leo thang (scalability)
8. **Những công kích đối với hệ nhân trắc học**
9. Các vấn đề riêng tư

Báo cáo này tập trung vào **thách thức thứ tám**. Tuy nhiên, cần lưu ý rằng
thách thức thứ nhất — *biến đổi bên trong mỗi lớp* — cũng đóng vai trò quan
trọng và sẽ trở lại ở phần thảo luận. Trong bài toán PAD, "biến đổi nội lớp"
chính là việc cùng một lớp `live` nhưng được thu bằng sáu điện thoại khác nhau
trong ba môi trường ánh sáng khác nhau sẽ cho những thống kê ảnh rất khác nhau.
Như sẽ thấy ở mục 9.6, đây là nguyên nhân trực tiếp khiến LBP thất bại khi
chuyển từ tập phát triển sang tập kiểm tra.

## 2.5. Phân loại tấn công và vị trí chính xác của PAD

Theo mô hình luồng thông tin của một hệ nhân trắc học trong [HB] Chương 20
(Hình 20.1, trang 404), dữ liệu đi qua chuỗi: cảm biến → trích chọn đặc trưng →
so khớp với cơ sở dữ liệu mẫu → quyết định. Mỗi mắt xích là một điểm có thể bị
tấn công:

| Điểm | Vị trí | Hình thức tấn công | PAD có xử lý? |
|---|---|---|---|
| 1 | Cảm biến | Trình diện vật giả (ảnh in, màn hình, mặt nạ) | **Có** |
| 2 | Kênh truyền cảm biến → bộ trích đặc trưng | Chặn và thay thế dữ liệu ảnh | Không |
| 3 | Bộ trích chọn đặc trưng | Thay thế vector đặc trưng | Không |
| 4 | Cơ sở dữ liệu mẫu | Sửa đổi hoặc thêm template | Không |
| 5 | Bộ so khớp | Ghi đè điểm số hoặc quyết định | Không |

Bảng này xác định ranh giới trách nhiệm một cách dứt khoát. PAD **chỉ** bảo vệ
điểm tấn công số 1. Các điểm còn lại thuộc phạm vi bảo mật hệ thống truyền
thống: mã hóa kênh truyền, ký số, kiểm soát truy cập, module phần cứng an toàn.
Một hệ thống chỉ triển khai PAD mà bỏ ngỏ các điểm 2–5 vẫn là một hệ thống không
an toàn.

Hai thuật ngữ chuẩn hóa cần được định nghĩa chính xác và sẽ dùng xuyên suốt:

- **PAI (Presentation Attack Instrument)** — công cụ tấn công trình diện, tức
  vật thể được đưa ra trước cảm biến nhằm mục đích đánh lừa. Trong Protocol 1
  của OULU-NPU, PAI gồm ảnh in trên hai loại máy in và video phát lại trên hai
  loại màn hình.
- **PAD (Presentation Attack Detection)** — quá trình tự động xác định xem mẫu
  được trình diện là mẫu thật (bona fide) hay là một PAI.

Việc PAD được đặt ở điểm 1 kéo theo một hệ quả thiết kế quan trọng: PAD phải
hoạt động **trên dữ liệu thô từ cảm biến**, trước hoặc song song với việc trích
chọn đặc trưng danh tính. Nếu đặt PAD sau khâu nhận dạng, thông tin về dấu vết
vật lý đã bị loại bỏ bởi chính các phép biến đổi bất biến mà bộ nhận dạng sử
dụng — vì bộ nhận dạng được thiết kế để *bỏ qua* những khác biệt do điều kiện
thu nhận, còn PAD lại cần *đo chính xác* những khác biệt đó. Đây là một quan sát
lý thuyết quan trọng: **hai bài toán có mục tiêu bất biến ngược nhau.**

## 2.6. Phân loại các phương pháp PAD

Các phương pháp PAD được chia thành ba nhánh lớn theo nguồn thông tin mà chúng
khai thác.

### 2.6.1. Nhánh dựa trên phần cứng bổ sung

Nhánh này trang bị thêm cảm biến ngoài camera RGB thông thường: camera hồng
ngoại gần, camera chiều sâu, cảm biến đa phổ, cảm biến nhiệt. Nguyên lý là da
người thật có đặc tính phản xạ và hấp thụ quang phổ khác biệt rõ rệt so với giấy
in hay màn hình LCD, và sự khác biệt này thể hiện mạnh nhất ở những dải bước
sóng nằm ngoài dải nhìn thấy.

[HB] mục 20.3.2 (trang 415) trình bày chi tiết nguyên lý ảnh đa phổ cho bài toán
chống giả mạo vân tay: bằng cách chiếu nhiều bước sóng khác nhau và thu nhận
đáp ứng, hệ thống dựng lại được cấu trúc dưới bề mặt da mà một bản sao bề mặt
không thể tái tạo. Nguyên lý quang phổ này áp dụng chung cho mọi đặc trưng sinh
trắc.

*Ưu điểm:* độ chính xác rất cao, rất khó đánh lừa. *Nhược điểm:* tăng chi phí
phần cứng, không triển khai được trên thiết bị phổ thông đã có sẵn.

### 2.6.2. Nhánh dựa trên phản ứng sống

Nhánh này yêu cầu người dùng thực hiện một hành động và kiểm tra phản ứng: chớp
mắt, quay đầu theo hướng chỉ định, đọc một dãy số ngẫu nhiên, mỉm cười. Cơ sở lý
thuyết là một ảnh in tĩnh không thể phản ứng, còn một video phát lại đã ghi sẵn
không thể phản ứng đúng với thử thách ngẫu nhiên được sinh tại thời điểm xác
thực.

*Ưu điểm:* rất mạnh trước tấn công ảnh in. *Nhược điểm:* đòi hỏi người dùng hợp
tác, làm tăng đáng kể thời gian xác thực và giảm trải nghiệm; hơn nữa nó thất
bại trước các tấn công video phát lại tinh vi hoặc tấn công thời gian thực bằng
deepfake.

### 2.6.3. Nhánh dựa trên phân tích ảnh thụ động

Nhánh này chỉ sử dụng chính ảnh hoặc video thu được từ camera RGB thông thường,
không cần phần cứng thêm và không cần người dùng làm gì. Hệ thống phân tích các
đặc trưng nội tại của ảnh: kết cấu bề mặt, phân bố tần số, thống kê màu, chuyển
động vi mô, biến thiên tín hiệu quang thể tích.

**Đây là nhánh mà báo cáo lựa chọn**, vì ba lý do:

1. **Tính khả thi triển khai:** không đòi hỏi thay đổi phần cứng, do đó áp dụng
   được ngay cho hạ tầng camera sẵn có.
2. **Trải nghiệm người dùng:** hoàn toàn thụ động, không làm tăng thời gian xác
   thực.
3. **Phù hợp phạm vi môn học:** đây là nhánh sử dụng trực tiếp và tập trung nhất
   các kiến thức xử lý ảnh nâng cao — phân tích kết cấu, phân tích tần số, biểu
   diễn đặc trưng và học biểu diễn.

[HFR] Chương 4 (trang 79–108) cung cấp nền tảng lý thuyết cho nhánh này thông
qua việc khảo sát các phương pháp biểu diễn cục bộ đặc trưng khuôn mặt, trong đó
Local Binary Pattern được trình bày như một công cụ trung tâm. Chương 5 của báo
cáo sẽ khai thác trực tiếp tài liệu này.

## 2.7. Kết luận chương

Chương này đã xác định ba điều. Thứ nhất, PAD giải quyết một câu hỏi mà bài toán
nhận dạng khuôn mặt về bản chất không đặt ra, và hai bài toán này có mục tiêu
bất biến ngược nhau. Thứ hai, PAD chỉ bảo vệ điểm tấn công tại cảm biến; nó là
một lớp trong kiến trúc bảo mật chứ không phải toàn bộ kiến trúc. Thứ ba, trong
ba nhánh phương pháp, nhánh phân tích ảnh thụ động là lựa chọn phù hợp nhất cả
về tính khả thi triển khai lẫn phạm vi kiến thức của môn học.

Chương tiếp theo xây dựng khung lý thuyết nhận dạng mẫu, tạo bộ khái niệm chung
để mô tả pipeline sẽ được triển khai.

---

# Chương 3. Khung lý thuyết nhận dạng mẫu

Chương này thiết lập bộ khái niệm nền tảng của lý thuyết nhận dạng mẫu và chứng
minh rằng pipeline được xây dựng trong dự án là một hiện thân cụ thể của sơ đồ
nhận dạng mẫu kinh điển. Toàn bộ chương bám sát [S2].

## 3.1. Các khái niệm nền tảng

[S2] slide 3 đưa ra bốn định nghĩa cơ sở:

- **Mẫu (pattern):** một đối tượng, quy trình hoặc sự kiện đã được gắn liền với
  một cái tên cho trước.
- **Lớp mẫu (pattern class):** một tập các mẫu có chung thuộc tính và thường
  xuất phát từ cùng một nguồn.
- **Nhận dạng (recognition) hay phân lớp (classification):** việc gán các đối
  tượng cho trước về những lớp đã được xác định trước.
- **Bộ phân lớp (classifier):** một máy dùng cho hoạt động phân loại — theo cách
  diễn đạt của Duda và Hart được trích trong slide, đó là việc *"gán một đối
  tượng cụ thể hoặc sự kiện về một bộ phân loại đã được xác định trước"*.

[S2] slide 6 bổ sung hai khái niệm mang tính kỹ thuật hơn:

- **Vector đặc trưng (feature vector)** $\mathbf{x} \in X$: một vector quan sát
  được đo lường; $\mathbf{x}$ là một điểm trong không gian đặc trưng $X$.
- **Trạng thái ẩn (hidden state)** $y \in Y$: đại lượng không đo lường trực tiếp
  được; các mẫu có cùng trạng thái ẩn sẽ thuộc về cùng một lớp.

Sự phân biệt giữa *cái đo được* và *cái cần suy ra* là điểm cốt lõi. Bảng sau
ánh xạ từng khái niệm lý thuyết vào bài toán cụ thể của báo cáo:

| Khái niệm trong [S2] | Hiện thân trong bài toán PAD của báo cáo |
|---|---|
| Mẫu (pattern) | Một video OULU-NPU, hoặc một khung hình đã cắt vùng mặt |
| Lớp mẫu (pattern class) | Hai lớp: `live` (nhãn 0) và `spoof` (nhãn 1) |
| Vector đặc trưng $\mathbf{x}$ | Vector LBP 640 chiều (E01), hoặc vector đặc trưng CNN (E02–E04) |
| Trạng thái ẩn $y$ | Vật được trình diện trước camera là khuôn mặt sống hay là PAI |
| Bộ phân lớp $q: X \to Y$ | `LinearSVC` (E01) hoặc CNN kết hợp hàm sigmoid (E02–E04) |
| Không gian đặc trưng $X$ | $\mathbb{R}^{640}$ với E01; không gian đặc trưng sâu với E02–E04 |

Điểm đáng chú ý là **trạng thái ẩn ở đây thực sự "ẩn" theo đúng nghĩa vật lý**.
Trong bài toán nhận dạng chữ viết tay, trạng thái ẩn "chữ số 5" là một khái niệm
trừu tượng nhưng con người có thể xác định trực tiếp bằng mắt. Trong bài toán
PAD, con người nhìn vào một khung hình đã cắt vùng mặt thường **không** phân
biệt được live hay spoof, vì dấu vết nằm ở mức vi mô. Đây là một bài toán mà máy
có tiềm năng vượt trội hơn người quan sát, và cũng là lý do bài toán này thú vị
về mặt xử lý ảnh.

## 3.2. Hàm quyết định

Nhiệm vụ trung tâm của nhận dạng mẫu, theo [S2] slide 6, là thiết kế một **quy
tắc quyết định** (decision rule) ánh xạ từ quan sát sang trạng thái ẩn:

$$
q : X \longrightarrow Y \qquad (3.1)
$$

[S2] slide 7 minh họa dạng đơn giản nhất của quy tắc này qua ví dụ phân biệt
vận động viên đua ngựa và cầu thủ bóng rổ dựa trên hai đặc trưng chiều cao và
cân nặng. Bộ phân lớp tuyến tính có dạng:

$$
q(\mathbf{x}) =
\begin{cases}
\text{lớp thứ nhất} & \text{nếu } \langle \mathbf{w}, \mathbf{x} \rangle + b \geq 0 \\[4pt]
\text{lớp thứ hai} & \text{nếu } \langle \mathbf{w}, \mathbf{x} \rangle + b < 0
\end{cases} \qquad (3.2)
$$

trong đó $\mathbf{w}$ là vector trọng số và $b$ là hệ số tự do. Phương trình
$\langle \mathbf{w}, \mathbf{x} \rangle + b = 0$ xác định một **siêu phẳng** chia
không gian đặc trưng thành hai nửa không gian.

Công thức (3.2) đơn giản đến mức có thể gây hiểu lầm là tầm thường, nhưng nó đặt
ra chính xác câu hỏi mà toàn bộ Chương 6 dành để trả lời: **trong vô số cặp
$(\mathbf{w}, b)$ có thể phân tách được dữ liệu huấn luyện, cặp nào là tốt
nhất?** Máy vector hỗ trợ là một câu trả lời có cơ sở toán học chặt chẽ cho câu
hỏi này.

## 3.3. Sơ đồ thành phần của một hệ nhận dạng mẫu

[S2] slide 8 mô tả kiến trúc tổng quát của một hệ thống nhận dạng mẫu:

```text
                    Teacher (cung cấp nhãn)
                            │
                            ▼
                   Learning algorithm
                            │
                            ▼
Pattern ──► Sensors and     ──► Feature      ──► Classifier ──► Class
            preprocessing        extraction                      assignment
```

Trong đó, theo đúng chú giải của slide:

- **Sensors and preprocessing** — cảm biến và tiền xử lý.
- **Feature extraction** — tạo ra những đặc trưng tách lớp tốt cho việc phân
  lớp mẫu.
- **Classifier** — bộ phân lớp.
- **Teacher** — cung cấp thông tin về trạng thái ẩn, tức là học có giám sát
  (supervised learning).
- **Learning algorithm** — thiết lập bộ nhận dạng từ tập mẫu huấn luyện.

Bảng dưới đây ánh xạ một-một sơ đồ lý thuyết này vào các module cụ thể của dự
án. Đây là bảng nền tảng, sẽ được mở rộng thành bảng truy vết đầy đủ ở mục 9.3:

| Khối trong sơ đồ [S2] slide 8 | Module tương ứng trong dự án |
|---|---|
| Sensors and preprocessing | `data/frame_sampler.py`, `data/preprocess.py` |
| Feature extraction | `features/lbp.py` (E01) hoặc backbone CNN (E02–E04) |
| Classifier | `models/lbp_svm.py`, `models/resnet18.py`, `models/mobilenet_v2.py` |
| Learning algorithm | `training/lbp_experiment.py`, `training/resnet_experiment.py`, `training/mobilenet_experiment.py` |
| Teacher (nguồn nhãn) | Tệp protocol chính thức của OULU-NPU, xử lý bởi `data/oulu.py` |
| Class assignment | `evaluation/threshold.py`, `evaluation/aggregation.py` |

Sự tương ứng chặt chẽ này không phải ngẫu nhiên. Kiến trúc phần mềm của dự án
được thiết kế có chủ đích theo sơ đồ nhận dạng mẫu kinh điển, với mục tiêu tách
bạch ba lớp trách nhiệm: lớp dữ liệu, lớp biểu diễn và mô hình, lớp đánh giá.
Sự tách bạch này bảo đảm rằng bốn thí nghiệm dùng chung một quy trình tiền xử lý
và một bộ đánh giá duy nhất — nghĩa là không có thí nghiệm nào vô tình được
hưởng một điều kiện thuận lợi riêng. Đây là điều kiện tiên quyết để phép so sánh
giữa E01 và E04 có ý nghĩa.

## 3.4. Thế nào là một đặc trưng tốt?

[S2] slide 9 nêu hai tiêu chí của một đặc trưng tốt:

- Các đối tượng thuộc **cùng một lớp** có các giá trị đặc trưng **tương tự**
  nhau.
- Các đối tượng thuộc **các lớp khác nhau** có các giá trị đặc trưng **khác
  biệt** nhau.

Diễn đạt bằng ngôn ngữ thống kê, một đặc trưng tốt phải có **phương sai nội lớp
nhỏ** và **phương sai giữa lớp lớn**. Hai tiêu chí này sẽ trở lại ở ba vị trí
quan trọng của báo cáo:

1. Tại mục 5.6, chúng chính là **hàm mục tiêu tường minh** của phân tích tách
   lớp tuyến tính LDA — tiêu chuẩn Fisher là tỉ số giữa độ phân tán giữa lớp và
   độ phân tán trong lớp.
2. Tại mục 6.2, nguyên lý biên cực đại của SVM có thể xem là một cách khác để
   đạt cùng mục tiêu: tối đa hóa khoảng cách giữa hai lớp trong không gian đặc
   trưng.
3. Tại mục 9.6, hai tiêu chí này là công cụ để chẩn đoán **vì sao LBP thất bại**
   khi chuyển miền. Vấn đề của LBP không phải là phương sai giữa lớp nhỏ — trên
   tập phát triển nó tách hai lớp rất tốt — mà là **phương sai nội lớp bị chi
   phối bởi điều kiện thu nhận** thay vì bởi bản chất live/spoof. Khi tập kiểm
   tra thay đổi camera và điều kiện chiếu sáng, phân bố của lớp `live` dịch
   chuyển đủ xa để vượt qua ranh giới quyết định đã học.

Nói cách khác, [S2] slide 9 cung cấp không chỉ một tiêu chí thiết kế mà còn một
công cụ chẩn đoán lỗi. Đây là ví dụ điển hình cho việc lý thuyết cơ bản có giá
trị thực tiễn trực tiếp.

## 3.5. Ba hướng tiếp cận nhận dạng mẫu

[S2] slide 5 phân chia các phương pháp nhận dạng thành ba hướng:

| Hướng tiếp cận | Nội dung theo [S2] slide 5 | Thí nghiệm tương ứng |
|---|---|---|
| **Nhận dạng mẫu thống kê** (statistical PR) | Dựa vào mô hình thống kê của tập mẫu cơ bản và các lớp mẫu cho trước | **E01**: histogram LBP là một mô tả thống kê, SVM là một bộ phân lớp thống kê |
| **Nhận dạng mẫu theo cấu trúc** (structural/syntactic PR) | Các lớp mẫu được biểu diễn bằng các cấu trúc hình thức như văn phạm, automata, chuỗi | Không sử dụng |
| **Mạng nơ-ron nhân tạo** (neural networks) | Bộ phân lớp là một mạng các tế bào mô hình hóa nơ-ron trong bộ não người, theo cách tiếp cận nối kết | **E02, E03, E04** |

Việc **không sử dụng hướng cấu trúc** cần được biện minh chứ không bỏ qua. Lý do
nằm ở bản chất của tín hiệu cần phát hiện: dấu vết của chuỗi tái chụp là một
hiện tượng **thống kê phân tán** trên toàn bộ ảnh — một sự thay đổi trong phân
bố tần số, trong độ tương phản cục bộ, trong thống kê nhiễu. Nó không có cấu
trúc phân cấp dạng ngữ pháp kiểu "một khuôn mặt gồm hai mắt, một mũi, một
miệng, sắp xếp theo quan hệ hình học nhất định". Cách tiếp cận cấu trúc phát huy
sức mạnh khi đối tượng có ngữ pháp nội tại rõ ràng, ví dụ nhận dạng công thức
toán học hoặc phân tích ảnh y khoa có cấu trúc giải phẫu ổn định. Với PAD, ngữ
pháp đó không tồn tại.

Như vậy, báo cáo khai thác hai trong ba hướng, và chính sự đối chiếu giữa hướng
thống kê (E01) với hướng nơ-ron (E02–E04) tạo nên trục so sánh chính của toàn bộ
thực nghiệm.

## 3.6. Các kỹ thuật kinh điển và định vị lựa chọn của báo cáo

[S1] slide 24 và slide 25 liệt kê những kỹ thuật mà môn học đã trang bị, phân
theo hai giai đoạn của pipeline nhận dạng mặt:

**Các kỹ thuật trích chọn không gian mẫu** ([S1] slide 24):

- Phân tích thành phần chính (PCA)
- Phân tích thành phần độc lập (ICA)
- Phân tích tách lớp tuyến tính (LDA)

**Các kỹ thuật phân lớp mẫu** ([S1] slide 25):

- Mạng nơ-ron nhân tạo (ANN)
- Ada-Boost
- Máy vector hỗ trợ (SVM)

Báo cáo định vị lựa chọn của mình trong bức tranh này như sau:

| Kỹ thuật | Sử dụng trong báo cáo | Ghi chú |
|---|---|---|
| PCA | Phân tích lý thuyết tại mục 5.6, không đưa vào pipeline | Có luận cứ cho quyết định này |
| LDA | Phân tích lý thuyết tại mục 5.6, không đưa vào pipeline | Giới hạn $C-1 = 1$ chiều với bài toán hai lớp |
| ICA | Không sử dụng | Nằm ngoài phạm vi |
| ANN | Sử dụng dưới dạng CNN sâu (E02–E04) | Mở rộng từ mạng truyền thẳng trong [S8] |
| Ada-Boost | Không sử dụng trực tiếp | Được nhắc tại mục 4.3 trong ngữ cảnh phát hiện mặt |
| **SVM** | **Sử dụng làm bộ phân lớp cho E01** | Trình bày đầy đủ tại Chương 6 |

Việc trình bày PCA và LDA ở mục 5.6 dù không đưa chúng vào pipeline là một lựa
chọn có chủ ý: một quyết định thiết kế chỉ có giá trị khoa học khi các phương án
bị loại bỏ cũng được phân tích. Mục 5.6 sẽ trình bày đầy đủ cơ sở toán học của
hai phương pháp này rồi đưa ra năm luận cứ cụ thể cho việc không sử dụng chúng.

## 3.7. Kết luận chương

Chương này đã thiết lập bộ khái niệm chung để mô tả bài toán: mẫu, lớp mẫu,
vector đặc trưng, trạng thái ẩn, hàm quyết định và sơ đồ thành phần của hệ nhận
dạng. Quan trọng hơn, chương đã chứng minh rằng pipeline của dự án không phải
một tập hợp kỹ thuật ngẫu nhiên mà là hiện thân trực tiếp của sơ đồ nhận dạng
mẫu kinh điển trong [S2] slide 8, với sự tương ứng một-một giữa từng khối lý
thuyết và từng module mã nguồn.

Từ chương tiếp theo, báo cáo đi vào chi tiết kỹ thuật của từng khối, bắt đầu từ
khối đầu tiên trong sơ đồ: cảm biến và tiền xử lý.
---

# Chương 4. Lý thuyết xử lý ảnh trong giai đoạn tiền xử lý

Chương này trình bày các phép biến đổi ảnh được áp dụng từ video thô đến ảnh
khuôn mặt chuẩn hóa — tức là khối *Sensors and preprocessing* trong sơ đồ [S2]
slide 8. Mỗi phép biến đổi được trình bày theo trình tự: nguyên lý toán học,
lựa chọn cụ thể của dự án, và phân tích đánh đổi.

Điểm cần nhấn mạnh ngay từ đầu: giai đoạn tiền xử lý **không trung tính**. Mỗi
phép biến đổi vừa chuẩn hóa dữ liệu vừa loại bỏ một phần thông tin. Với bài toán
PAD — nơi tín hiệu cần phát hiện nằm ở mức vi mô — việc một phép tiền xử lý vô
tình xóa mất chính tín hiệu đó là rủi ro có thật, và sẽ được kiểm chứng bằng số
liệu tại mục 9.6.

## 4.1. Ảnh số, video số và không gian màu

### 4.1.1. Biểu diễn toán học

Một ảnh số đơn sắc là một hàm rời rạc hai biến:

$$
I : \Omega \subset \mathbb{Z}^2 \longrightarrow \{0, 1, \dots, 255\} \qquad (4.1)
$$

trong đó $\Omega$ là lưới điểm ảnh hình chữ nhật kích thước $H \times W$. Một
video số bổ sung trục thời gian rời rạc:

$$
I : \Omega \times \{0, 1, \dots, T-1\} \longrightarrow \{0, 1, \dots, 255\}^3 \qquad (4.2)
$$

Biểu diễn này cho thấy ba trục lượng tử hóa độc lập: **không gian** (độ phân
giải lưới điểm ảnh), **thời gian** (tốc độ khung hình) và **cường độ** (độ sâu
bit). Đây không phải một nhận xét hình thức. Như đã phân tích ở mục 1.2, chuỗi
tái chụp tác động lên **cả ba trục**: lấy mẫu lại lưới điểm ảnh của màn hình tạo
vân moiré trên trục không gian; sự lệch pha giữa tần số quét màn hình và tốc độ
khung hình camera tạo hiện tượng nhấp nháy trên trục thời gian; nén hai lần làm
giảm dải động hiệu dụng trên trục cường độ.

### 4.1.2. Chuyển đổi không gian màu

Phép chuyển từ ảnh màu RGB sang ảnh mức xám theo chuẩn ITU-R BT.601:

$$
I_{\text{gray}}(x, y) = 0{,}299 \cdot R(x,y) + 0{,}587 \cdot G(x,y) + 0{,}114 \cdot B(x,y) \qquad (4.3)
$$

Ba trọng số này không tùy tiện: chúng phản ánh **độ nhạy phổ tương đối của hệ
thị giác người**. Tế bào hình nón nhạy với bước sóng trung bình (lục) chiếm ưu
thế, nên kênh G có trọng số lớn nhất; độ nhạy với bước sóng ngắn (lam) thấp
nhất, nên kênh B có trọng số nhỏ nhất. Công thức được thiết kế để ảnh xám thu
được có độ sáng cảm nhận gần nhất với ảnh màu gốc.

**Đánh đổi cần phân tích.** Thí nghiệm E01 chuyển ảnh sang mức xám trước khi
tính LBP, theo cấu hình `grayscale: true` trong `configs/models/lbp_svm.yaml`.
Phép chiếu từ $\mathbb{R}^3$ xuống $\mathbb{R}^1$ này làm **mất toàn bộ thông
tin sắc độ**. Đây là một quyết định đáng phân tích, vì như bảng ở mục 1.2 đã
chỉ ra, *sai lệch gam màu của máy in và màn hình* là một trong những dấu vết
spoof rõ rệt nhất: máy in không tái tạo được toàn bộ không gian màu của da
người, còn màn hình LCD có gam màu và điểm trắng khác biệt so với ánh sáng phản
xạ tự nhiên.

Nói cách khác, **E01 chủ động vứt bỏ một họ dấu vết ngay ở bước đầu tiên**. Lựa
chọn này có lý do: toán tử LBP theo định nghĩa gốc hoạt động trên ảnh đơn kênh,
và việc giữ đúng dạng chuẩn của LBP giúp E01 giữ vai trò một đường cơ sở tối
giản, dễ diễn giải. Nhưng đây là một giả thuyết cần được ghi nhận để kiểm chứng
ở phần thảo luận. Công trình của Boulkenafet và cộng sự [12] cho thấy phân tích
kết cấu **trên các kênh màu** cải thiện đáng kể hiệu năng PAD so với chỉ dùng
ảnh xám — đây là hướng phát triển được đề xuất tại mục 10.2.

Ngược lại, các thí nghiệm CNN (E02–E04) giữ nguyên ba kênh RGB, vì các mạng tiền
huấn luyện trên ImageNet nhận đầu vào ba kênh. Đây là một khác biệt có hệ thống
giữa E01 và các thí nghiệm còn lại, và cần được ghi nhận trong phần đe dọa tính
hợp lệ tại mục 9.8.

**Chi tiết triển khai quan trọng.** Thư viện OpenCV đọc khung hình theo thứ tự
kênh **BGR**, trong khi bộ phát hiện khuôn mặt MediaPipe và các mạng tiền huấn
luyện đều yêu cầu **RGB**. Phép hoán vị kênh $BGR \to RGB$ được thực hiện tường
minh trước khi đưa vào bộ phát hiện. Nếu bỏ sót bước này, ảnh sẽ bị đảo kênh đỏ
và lam — một lỗi không gây ngoại lệ chương trình nhưng làm giảm nghiêm trọng
chất lượng phát hiện và làm sai lệch mọi kết quả phía sau. Đây là một ví dụ điển
hình về lỗi thầm lặng trong pipeline xử lý ảnh.

## 4.2. Lấy mẫu khung hình

### 4.2.1. Cơ sở lý thuyết và giới hạn áp dụng

Định lý lấy mẫu Nyquist–Shannon phát biểu rằng một tín hiệu có băng thông giới
hạn bởi tần số $f_{\max}$ có thể tái tạo hoàn hảo từ các mẫu rời rạc nếu tần số
lấy mẫu thỏa $f_s > 2 f_{\max}$.

**Cần nói rõ giới hạn áp dụng của định lý này trong bối cảnh đề tài.** Tín hiệu
video khuôn mặt **không phải** tín hiệu dừng có băng thông giới hạn theo nghĩa
chặt: chuyển động đầu, thay đổi biểu cảm và biến thiên chiếu sáng là những quá
trình không dừng. Do đó việc lấy 10 khung hình trên mỗi video **không** là hệ
quả trực tiếp của định lý lấy mẫu, mà là một **heuristic kỹ thuật**. Trình bày
đúng điều này quan trọng hơn là viện dẫn định lý một cách hình thức để tạo vẻ
chặt chẽ.

### 4.2.2. Chiến lược đã sử dụng

Cấu hình trong `configs/data/oulu_protocol1.yaml`:

```yaml
sampling:
  strategy: uniform
  frames_per_video: 10
  deterministic: true
  include_first_frame: true
  include_last_frame: true
```

Với một video có $T$ khung hình, tập chỉ số được chọn theo công thức số nguyên:

$$
k_i = \left\lfloor \frac{i \cdot (T-1)}{N-1} \right\rfloor, \qquad i = 0, 1, \dots, N-1, \quad N = 10 \qquad (4.4)
$$

Công thức này bảo đảm $k_0 = 0$ và $k_{N-1} = T-1$, tức bao gồm cả khung hình
đầu và khung hình cuối.

Ba lý do cho chiến lược này:

1. **Phủ toàn bộ trục thời gian.** Lấy mẫu đều bảo đảm mọi giai đoạn của video
   đều được đại diện. Nếu chỉ lấy 10 khung đầu tiên, ta sẽ bỏ sót các biến động
   chiếu sáng hoặc chuyển động xuất hiện về sau.
2. **Tính tất định.** Không có thành phần ngẫu nhiên nào trong công thức (4.4).
   Chạy lại pipeline trên cùng dữ liệu luôn cho cùng tập khung hình — điều kiện
   cần cho khả năng tái lập.
3. **Chi phí tính toán.** Video OULU-NPU dài vài giây ở tốc độ 30 khung/giây,
   tương ứng khoảng 100–200 khung hình. Lấy 10 khung giảm chi phí giải mã, phát
   hiện mặt và trích đặc trưng khoảng 10–20 lần mà vẫn giữ được nhiều mẫu độc
   lập cho mỗi video.

### 4.2.3. Đánh đổi phải ghi nhận

Lấy mẫu thưa với bước nhảy khoảng 10–20 khung hình làm **mất hoàn toàn thông tin
động ở tần số cao**. Cụ thể, các dấu hiệu PAD sau đây trở nên không quan sát
được:

- Chớp mắt tự nhiên (tần số khoảng 0,2–0,5 Hz, thời gian mỗi lần chớp
  100–400 ms).
- Vi chuyển động không tự chủ của đầu và cơ mặt.
- Nhấp nháy do lệch pha giữa tần số quét màn hình và tốc độ khung hình camera —
  đây là một dấu vết **rất mạnh** cho tấn công phát lại.
- Biến thiên tín hiệu quang thể tích (rPPG) do nhịp tim, chỉ có ở da thật.

Đây là một giới hạn thiết kế có ý thức: dự án chọn hướng tiếp cận **dựa trên
từng khung hình tĩnh**, trong đó thông tin thời gian chỉ được sử dụng ở mức gộp
điểm số (mục 8.4) chứ không ở mức biểu diễn. [HFR] mục 4.3.1.2 (trang 86) trình
bày LBP-TOP — một mở rộng của LBP sang ba mặt phẳng trực giao trong khối không
gian–thời gian, cho phép mã hóa đồng thời diện mạo và chuyển động. Đây là hướng
khắc phục tự nhiên nhất cho giới hạn này và được đưa vào mục 10.2.

**Nối với triển khai:** `src/face_spoofing/data/frame_sampler.py`.

## 4.3. Phát hiện khuôn mặt

### 4.3.1. Vị trí trong pipeline nhận dạng

Theo sơ đồ hệ thống nhận dạng mặt người trong [S1] slide 21 và slide 28, phát
hiện khuôn mặt là **khâu đầu tiên**, cho đầu ra là vị trí, kích thước và tư thế
khuôn mặt, làm đầu vào cho khâu chuẩn hóa tiếp theo.

### 4.3.2. Tổng quan các họ phương pháp

[HFR] Chương 11 (trang 277–304) phân loại các phương pháp phát hiện khuôn mặt
thành bốn nhóm:

| Nhóm phương pháp | Nguyên lý | Đại diện |
|---|---|---|
| Dựa trên tri thức | Mã hóa quy tắc do con người đặt ra về quan hệ giữa các bộ phận khuôn mặt | Quy tắc hình học thủ công |
| Dựa trên đặc trưng bất biến | Tìm các đặc trưng ổn định trước thay đổi tư thế và chiếu sáng | Màu da, kết cấu, cạnh |
| So khớp mẫu | So sánh với mẫu khuôn mặt chuẩn | Template matching |
| **Dựa trên diện mạo** | Học mô hình từ dữ liệu | Viola–Jones/AdaBoost, mạng nơ-ron |

[S1] slide 30 cũng đề cập hướng phát hiện mặt bằng AdaBoost và bằng mạng nơ-ron
nhân tạo, cùng đề xuất kết hợp AdaBoost + ANN.

### 4.3.3. Lựa chọn của dự án

Dự án sử dụng **MediaPipe Face Detection**, một bộ phát hiện một giai đoạn dựa
trên mạng tích chập nhẹ, thuộc nhóm *dựa trên diện mạo*. Kiến trúc nền tảng là
BlazeFace [1], được thiết kế để chạy thời gian thực trên GPU di động. Cấu hình:

```yaml
detector:
  name: mediapipe
  margin: 0.2
  model_selection: 0
  min_detection_confidence: 0.5
  detection_max_side: 640
  retry_full_resolution: true
  fallback: none
```

Tham số `detection_max_side: 640` thu nhỏ ảnh trước khi phát hiện để tăng tốc,
còn `retry_full_resolution: true` bảo đảm rằng nếu lần phát hiện đầu thất bại,
hệ thống thử lại ở độ phân giải đầy đủ. Khi có nhiều khuôn mặt được phát hiện,
hệ thống chọn khuôn mặt có độ tin cậy cao nhất.

### 4.3.4. Vì sao tỉ lệ phát hiện phải rất cao — một dạng rò rỉ tinh vi

Cấu hình kiểm soát chất lượng đặt ngưỡng `minimum_face_detection_rate: 0.98`.
Con số cao này không chỉ vì lý do chất lượng dữ liệu, mà vì một lý do sâu hơn
liên quan đến **tính hợp lệ của thực nghiệm**.

Giả sử bộ phát hiện thất bại **có hệ thống** trên các ảnh giả mạo — điều hoàn
toàn có thể xảy ra, vì ảnh in bị mờ, mất tương phản, hoặc màn hình bị lóa đều
làm giảm độ tin cậy phát hiện. Khi đó, bản thân sự kiện *"không phát hiện được
khuôn mặt"* đã mang thông tin về nhãn. Nếu pipeline xử lý các trường hợp thất
bại bằng cách bỏ qua chúng, hoặc thay thế bằng một khung hình khác được chọn
theo cách phụ thuộc nhãn, thì thông tin nhãn đã **rò rỉ vào tập đặc trưng** mà
không ai nhận ra. Mô hình sau đó có thể đạt kết quả tốt một cách giả tạo.

Dự án xử lý vấn đề này bằng ba biện pháp: đặt ngưỡng tỉ lệ phát hiện tối thiểu
rất cao; giữ nguyên trạng thái `no_face` cho khung hình thất bại thay vì thay
thế; và không cho phép chọn khung hình thay thế dựa trên nhãn. Trên thực tế, tỉ
lệ phát hiện đạt được là **26.999/27.000 = 99,9963%**, với đúng một khung hình
đầu tiên ở tập phát triển không phát hiện được khuôn mặt. Con số này giải thích
vì sao tập phát triển có 8.999 khung hình thay vì 9.000 như kỳ vọng lý thuyết —
một sai lệch nhỏ nhưng cần được giải thích minh bạch thay vì làm tròn.

**Nối với triển khai:** `src/face_spoofing/data/preprocess.py`,
`src/face_spoofing/data/processed_validation.py`.

## 4.4. Chuẩn hóa hình học vùng quan tâm

### 4.4.1. Vai trò của khâu chuẩn hóa

[S1] slide 28 đặt khâu *chuẩn hóa khuôn mặt* ngay sau khâu phát hiện, với đầu ra
là "khuôn mặt được chuẩn hóa". [S1] slide 31 đề cập các phương pháp chuẩn hóa
tinh vi dựa trên mô hình hình dạng chủ động (ASM) và mô hình diện mạo chủ động
(AAM), cho phép căn chỉnh theo điểm mốc giải phẫu.

Dự án sử dụng một phương pháp chuẩn hóa **đơn giản hơn có chủ ý**: cắt hộp bao
vuông có nới biên, không căn chỉnh theo điểm mốc. Lý do nằm ở sự khác biệt mục
tiêu giữa hai bài toán đã nêu ở mục 2.5. Căn chỉnh theo điểm mốc được thiết kế
để loại bỏ biến thiên do tư thế — điều cần thiết cho **nhận dạng danh tính**.
Với **PAD**, việc biến dạng hình học ảnh (warping) để căn chỉnh sẽ áp thêm một
phép nội suy lên toàn ảnh, và phép nội suy đó chính là một bộ lọc làm thay đổi
thống kê tần số cục bộ — tức là làm nhiễu chính tín hiệu cần đo.

### 4.4.2. Cấu hình và ba câu hỏi thiết kế

```yaml
face_cache:
  output_size: 256
  format: png
  png_compression: 3
detector:
  margin: 0.2
```

**Câu hỏi 1: Vì sao cần nới biên 20%?**

Hộp bao do bộ phát hiện trả về thường bám sát vùng mặt. Tuy nhiên, với bài toán
PAD, **ranh giới giữa khuôn mặt và nền chứa lượng thông tin rất lớn**: mép của
tờ giấy in, khung viền của màn hình điện thoại, vùng phản xạ ánh sáng ở rìa bề
mặt phẳng, sự đứt gãy đột ngột của kết cấu tại biên vật giả. Cắt quá sát sẽ loại
bỏ hoàn toàn những manh mối này.

Ngược lại, nới biên quá rộng đưa nhiều nền vào ảnh, tạo nguy cơ mô hình **học
tắt** — ví dụ học nhận ra bàn tay đang cầm điện thoại, hoặc học nhận ra phông
nền đặc trưng của phòng thu dữ liệu tấn công, thay vì học dấu vết vật lý thực
sự. Giá trị 0,2 là một sự cân bằng giữa hai rủi ro này.

**Câu hỏi 2: Vì sao lưu ở định dạng PNG chứ không phải JPEG?**

Đây là quyết định thiết kế thuần túy xử lý ảnh và có tầm quan trọng đặc biệt với
bài toán này. PNG sử dụng nén **không mất mát**; JPEG sử dụng nén **có mất mát**
dựa trên biến đổi cosine rời rạc, loại bỏ có chọn lọc các hệ số tần số cao mà
mắt người ít nhạy cảm.

Tín hiệu mà PAD cần phát hiện **nằm chính xác ở dải tần số cao** đó. Nếu lưu ảnh
cắt dưới dạng JPEG, ta sẽ chồng thêm một lớp nén thứ ba lên chuỗi tái chụp vốn
đã có hai lớp nén. Lớp nén thứ ba này không chỉ làm suy giảm tín hiệu mà còn
**tạo ra dấu vết nén riêng của nó** trên cả ảnh thật lẫn ảnh giả, làm nhiễu phép
đo. Lựa chọn PNG với mức nén 3 giữ nguyên vẹn từng giá trị điểm ảnh sau khi cắt.

**Câu hỏi 3: Vì sao lưu ở 256×256 rồi mới thay đổi kích thước theo từng thí
nghiệm?**

Ba lý do. Thứ nhất, tách rời khâu tiền xử lý tốn kém (giải mã video, phát hiện
mặt) khỏi khâu huấn luyện, cho phép chạy lại nhiều thí nghiệm mà không phải xử
lý lại video. Thứ hai, bảo đảm cả bốn thí nghiệm đọc **chính xác cùng một vùng
ảnh** — điều kiện tiên quyết để phép so sánh công bằng. Thứ ba, 256 đủ lớn để cả
nhánh LBP (thu xuống 128) và nhánh CNN (thu xuống 224) đều chỉ cần **thu nhỏ**,
không phải phóng to. Phóng to không tạo ra thông tin mới mà chỉ nội suy, nên
tránh được là tốt nhất.

Khi vùng cắt lớn hơn 256, phép nội suy `INTER_AREA` được dùng; khi nhỏ hơn,
`INTER_LINEAR` được dùng. Lý do của quy tắc này được giải thích ở mục tiếp theo.

## 4.5. Thay đổi kích thước và nội suy

### 4.5.1. Bài toán

Thay đổi kích thước ảnh đòi hỏi ánh xạ mỗi điểm ảnh của lưới đích về tọa độ
tương ứng trên lưới nguồn. Tọa độ này nói chung **không nguyên**, nên giá trị
phải được nội suy từ các điểm ảnh lân cận.

### 4.5.2. Nội suy song tuyến

Với tọa độ đích ánh xạ về $(x, y)$ trên lưới nguồn, đặt $x_0 = \lfloor x
\rfloor$, $y_0 = \lfloor y \rfloor$, $a = x - x_0$, $b = y - y_0$. Giá trị nội
suy song tuyến là:

$$
I(x, y) = (1-a)(1-b) I_{00} + a(1-b) I_{10} + (1-a) b\, I_{01} + ab\, I_{11} \qquad (4.5)
$$

trong đó $I_{ij} = I(x_0 + i,\; y_0 + j)$. Đây là trung bình có trọng số của bốn
điểm ảnh lân cận, với trọng số tỉ lệ nghịch với khoảng cách.

### 4.5.3. Nội suy vùng

Khi **thu nhỏ** ảnh với hệ số lớn, nội suy song tuyến thuần túy có một khiếm
khuyết nghiêm trọng: nó chỉ lấy mẫu bốn điểm ảnh lân cận, bỏ qua toàn bộ các
điểm ảnh nguồn khác rơi vào cùng ô đích. Điều này vi phạm định lý lấy mẫu và gây
**răng cưa (aliasing)** — các thành phần tần số cao bị gập xuống thành tần số
thấp giả tạo.

Nội suy vùng khắc phục bằng cách lấy trung bình toàn bộ các điểm ảnh nguồn thuộc
ô đích:

$$
I_{\text{out}}(i, j) = \frac{1}{|\Omega_{ij}|} \sum_{(u,v) \in \Omega_{ij}} I_{\text{in}}(u, v) \qquad (4.6)
$$

trong đó $\Omega_{ij}$ là tập các điểm ảnh nguồn rơi vào ô đích $(i,j)$.

### 4.5.4. So sánh và biện minh lựa chọn

| Phép nội suy | Bản chất toán học | Dùng ở đâu | Lý do lựa chọn |
|---|---|---|---|
| **Area** | Trung bình vùng — tương đương lọc thông thấp hộp trước khi lấy mẫu | E01: $256 \to 128$ (`resize_interpolation: area`) | Hệ số thu nhỏ lớn (2×); area là bộ tiền lọc chống răng cưa tự nhiên, tránh làm hỏng thống kê LBP |
| **Bilinear + antialias** | Nội suy tuyến tính có tiền lọc chống răng cưa | E02–E04: $256 \to 224$ (`interpolation: bilinear, antialias: true`) | Khớp chính xác quy ước tiền xử lý của trọng số ImageNet trong torchvision |

Lý do chọn bilinear cho nhánh CNN không phải vì nó tốt hơn về mặt xử lý ảnh, mà
vì **tính nhất quán với quá trình tiền huấn luyện**. Trọng số ImageNet được học
trên dữ liệu qua đúng chuỗi tiền xử lý này. Dùng một phép nội suy khác sẽ tạo ra
sự lệch phân bố nhỏ giữa dữ liệu tiền huấn luyện và dữ liệu tinh chỉnh, làm giảm
hiệu quả chuyển giao.

### 4.5.5. Điểm lý thuyết cốt lõi: thu nhỏ ảnh là lọc thông thấp

Đây là nhận định quan trọng nhất của chương và cần được phát biểu tường minh.

Cả hai phép nội suy trên đều là **bộ lọc thông thấp**. Về mặt miền tần số, phép
thu nhỏ với hệ số $s$ loại bỏ mọi thành phần tần số vượt quá tần số Nyquist mới
$f_s / (2s)$. Trong trường hợp E01, ảnh 256×256 được thu xuống 128×128, tức
**một nửa dải tần số cao bị loại bỏ hoàn toàn**.

Nhưng theo phân tích ở mục 1.2, dấu vết của chuỗi tái chụp — moiré, răng cưa,
kết cấu sợi giấy, cấu trúc điểm ảnh của màn hình — **cư trú chính ở dải tần số
cao đó**. Như vậy tồn tại một mâu thuẫn thiết kế thực sự: phép tiền xử lý nhằm
chuẩn hóa dữ liệu lại có thể đang xóa chính tín hiệu cần đo.

Đây là một **giả thuyết có thể kiểm chứng**, và sẽ được đối chiếu với số liệu
thực nghiệm tại mục 9.6 khi giải thích vì sao E01 có kết quả kém trên tập kiểm
tra. Cần nhấn mạnh rằng đây là giả thuyết chứ chưa phải kết luận nhân quả: để
khẳng định, cần một thí nghiệm can thiệp trong đó chỉ thay đổi độ phân giải đầu
vào của LBP và giữ nguyên mọi yếu tố khác.

## 4.6. Chuẩn hóa cường độ

### 4.6.1. Chuẩn hóa theo thống kê ImageNet

Với các thí nghiệm CNN, mỗi kênh màu được chuẩn hóa theo trung bình và độ lệch
chuẩn của tập ImageNet:

$$
\hat{x}_c = \frac{x_c - \mu_c}{\sigma_c}, \qquad c \in \{R, G, B\} \qquad (4.7)
$$

với $\boldsymbol{\mu} = (0{,}485,\ 0{,}456,\ 0{,}406)$ và
$\boldsymbol{\sigma} = (0{,}229,\ 0{,}224,\ 0{,}225)$.

**Vì sao phải dùng đúng các hằng số này?** Vì trọng số tiền huấn luyện được học
trên dữ liệu đã chuẩn hóa theo đúng cách. Các tầng chuẩn hóa theo lô ở đầu mạng
lưu giữ thống kê chạy được ước lượng trên phân bố đó. Nếu đưa vào dữ liệu có
phân bố lệch, các tầng đầu sẽ hoạt động ngoài vùng làm việc mà chúng được hiệu
chỉnh, làm suy giảm chất lượng đặc trưng ngay từ những tầng đầu tiên và lan
truyền sai lệch qua toàn mạng.

### 4.6.2. Chuẩn hóa z-score cho đặc trưng LBP

Với E01, mỗi chiều của vector đặc trưng được chuẩn hóa độc lập:

$$
z_j = \frac{f_j - \mu_j}{\sigma_j}, \qquad j = 1, \dots, 640 \qquad (4.8)
$$

**Vì sao SVM cần bước này?** Máy vector hỗ trợ với chính quy hóa $L_2$ phạt
$\|\mathbf{w}\|^2$, tức tổng bình phương của mọi thành phần trọng số. Nếu các
chiều đặc trưng có thang đo khác nhau — ví dụ chiều thứ nhất dao động trong
$[0; 0{,}01]$ còn chiều thứ hai trong $[0; 0{,}5]$ — thì để đạt cùng ảnh hưởng
lên hàm quyết định, chiều thứ nhất cần trọng số lớn hơn 50 lần, và bị phạt nặng
hơn 2500 lần. Kết quả là chính quy hóa tác động **không đồng đều** giữa các
chiều, và tham số $C$ mất ý nghĩa nhất quán. Chuẩn hóa z-score đưa mọi chiều về
cùng thang đo, khôi phục tính đồng nhất của chính quy hóa.

### 4.6.3. Cảnh báo rò rỉ dữ liệu

Các tham số $\mu_j$ và $\sigma_j$ trong công thức (4.8) **chỉ được ước lượng
trên tập huấn luyện** (12.000 khung hình), sau đó áp dụng nguyên vẹn cho tập
phát triển và tập kiểm tra. Nếu ước lượng trên toàn bộ dữ liệu, thống kê của tập
kiểm tra sẽ ảnh hưởng đến phép biến đổi áp dụng cho tập huấn luyện — một dạng rò
rỉ tinh vi làm ước lượng hiệu năng bị lạc quan quá mức. Trong mã nguồn, bộ chuẩn
hóa được khớp (`fit`) chỉ một lần trên tập huấn luyện và không bao giờ được khớp
lại với tập phát triển.

## 4.7. Kết luận chương

Sau chuỗi biến đổi của chương này, mỗi video đã trở thành một tập 10 ảnh khuôn
mặt chuẩn hóa 256×256 lưu dưới dạng PNG không mất mát — một đầu vào chung và
công bằng cho cả bốn thí nghiệm.

Chương cũng đã chỉ ra rằng tiền xử lý không phải thao tác trung tính. Ba quyết
định — chuyển sang ảnh xám ở E01, thu nhỏ xuống 128 điểm ảnh, và lấy mẫu thưa
theo thời gian — đều loại bỏ những họ tín hiệu có khả năng hữu ích cho PAD. Ba
quyết định này tạo thành ba giả thuyết sẽ được đối chiếu với số liệu ở Chương 9.

---

# Chương 5. Biểu diễn đặc trưng thủ công: Local Binary Pattern

Chương này trình bày khối *Feature extraction* của sơ đồ [S2] slide 8 theo hướng
tiếp cận thủ công. Nội dung bám sát [S3] và [HFR] Chương 4.

## 5.1. Vì sao chọn mô tả kết cấu?

Kết luận ở mục 1.2 định hướng lựa chọn: PAD là bài toán về **kết cấu và tần số**
chứ không phải về ngữ nghĩa. Vấn đề trở thành: trong họ các mô tả kết cấu, mô tả
nào phù hợp?

[S3] slide 11 trình bày một sơ đồ định vị LBP trong toàn cảnh các phương pháp mô
tả kết cấu, bao gồm phân bố đồng xuất hiện mức xám, phân bố hiệu mức xám có dấu,
đơn vị kết cấu và phổ kết cấu, N-tuple, và textons dựa trên lọc Gabor. Trong bức
tranh đó, LBP xuất hiện như kết quả của việc **nhị phân hóa cục bộ trên tập lân
cận tròn tùy ý**.

[HFR] mục 4.1 (trang 79) nêu ba yêu cầu đối với một biểu diễn đặc trưng khuôn
mặt tốt. Đối chiếu LBP với từng yêu cầu:

| Yêu cầu theo [HFR] tr. 79 | LBP đáp ứng như thế nào |
|---|---|
| Phân biệt tốt giữa các lớp trong khi dung thứ biến thiên nội lớp | Bất biến với biến đổi đơn điệu của mức xám — dung thứ tốt với thay đổi độ sáng |
| Trích xuất được nhanh từ ảnh thô để cho phép xử lý nhanh | Chỉ cần so sánh và cộng số nguyên; không cần nhân, không cần học |
| Nằm trong không gian có số chiều thấp | Với cấu hình của dự án: 640 chiều, rất nhỏ so với 16.384 điểm ảnh của ảnh 128×128 |

Ngoài ba yêu cầu trên, LBP có một ưu thế riêng cho bài toán PAD: nó **không cần
giai đoạn học**. Bộ mô tả là cố định, do đó có thể phân tích chính xác nó đo cái
gì — điều đặc biệt có giá trị cho một báo cáo thiên về lý thuyết, nơi khả năng
diễn giải quan trọng hơn con số hiệu năng.

## 5.2. Toán tử LBP cơ bản

### 5.2.1. Định nghĩa

Toán tử LBP nguyên bản, được giới thiệu bởi Ojala và cộng sự năm 1996, hoạt động
trên lân cận $3 \times 3$. Với điểm ảnh trung tâm có mức xám $g_c$ và tám điểm
ảnh lân cận $g_0, g_1, \dots, g_7$:

$$
\text{LBP}(x_c, y_c) = \sum_{p=0}^{7} s(g_p - g_c) \cdot 2^p \qquad (5.1)
$$

trong đó hàm dấu được định nghĩa:

$$
s(t) =
\begin{cases}
1 & \text{nếu } t \geq 0 \\
0 & \text{nếu } t < 0
\end{cases} \qquad (5.2)
$$

Kết quả là một số nguyên trong khoảng $[0, 255]$, mã hóa cấu hình nhị phân của
lân cận.

### 5.2.2. Ví dụ số

[S3] slide 6 minh họa bằng một ví dụ cụ thể. Xét cửa sổ $3 \times 3$:

$$
\begin{pmatrix}
6 & 5 & 2 \\
7 & \mathbf{6} & 1 \\
9 & 8 & 7
\end{pmatrix}
$$

Điểm trung tâm có $g_c = 6$. Ngưỡng hóa từng lân cận theo quy tắc "1 nếu lớn hơn
hoặc bằng trung tâm":

$$
\begin{pmatrix}
1 & 0 & 0 \\
1 & - & 0 \\
1 & 1 & 1
\end{pmatrix}
$$

Đọc theo thứ tự và nhân với trọng số nhị phân tương ứng, ta được mẫu
`11110001` và giá trị:

$$
\text{LBP} = 1 + 16 + 32 + 64 + 128 = 241
$$

### 5.2.3. Tính chất bất biến — cơ sở lý thuyết quan trọng nhất

Giả sử toàn bộ ảnh chịu một biến đổi mức xám đơn điệu tăng $g \mapsto f(g)$, với
$f$ là hàm đơn điệu tăng. Khi đó với mọi cặp $(g_p, g_c)$:

$$
g_p \geq g_c \iff f(g_p) \geq f(g_c) \qquad (5.3)
$$

Do đó dấu của mọi hiệu $g_p - g_c$ được bảo toàn, và **mã LBP hoàn toàn không
đổi**.

Ý nghĩa thực tiễn rất lớn với bài toán này: các biến đổi độ sáng và độ tương
phản toàn cục — vốn là nguồn biến thiên chính trong OULU-NPU, do dữ liệu được
thu trong ba môi trường chiếu sáng khác nhau — **không ảnh hưởng đến mô tả LBP**.
Đây chính là tính chất "dung thứ biến thiên nội lớp" mà [HFR] trang 79 yêu cầu,
và là lý do lý thuyết mạnh nhất để chọn LBP cho bài toán này.

Tuy nhiên cần lưu ý giới hạn: tính bất biến chỉ đúng với biến đổi **đơn điệu và
toàn cục**. Thay đổi chiếu sáng cục bộ, bóng đổ, hoặc thay đổi gamma phi tuyến
theo vùng vẫn làm thay đổi mã LBP.

### 5.2.4. Chi tiết triển khai

Mã nguồn tại `src/face_spoofing/features/lbp.py` có ba chi tiết cần ghi nhận vì
chúng ảnh hưởng trực tiếp đến khả năng tái lập:

1. **Điều kiện so sánh** sử dụng `>=` (lớn hơn hoặc bằng), khớp với công thức
   (5.2). Việc chọn `>` thay vì `>=` sẽ cho kết quả khác trên các vùng ảnh phẳng
   có nhiều điểm ảnh bằng nhau — không phải chi tiết vụn vặt, vì vùng phẳng xuất
   hiện nhiều trên ảnh in bị bão hòa.
2. **Thứ tự duyệt lân cận** theo chiều kim đồng hồ, bắt đầu từ góc trên-trái.
3. **Xử lý biên** bằng nhân bản mép (`np.pad(..., mode="edge")`) thay vì đệm số
   không. Nếu đệm số không, toàn bộ viền ảnh sẽ tạo ra một khung mã LBP nhân tạo
   ứng với "cạnh sáng-tối", làm nhiễu histogram của các ô ở biên.

## 5.3. LBP tổng quát trên lân cận tròn

### 5.3.1. Định nghĩa tổng quát

Ojala, Pietikäinen và Mäenpää (2002) [2] tổng quát hóa toán tử sang lân cận tròn
với $P$ điểm lấy mẫu trên đường tròn bán kính $R$:

$$
\text{LBP}_{P,R}(x_c, y_c) = \sum_{p=0}^{P-1} s(g_p - g_c) \cdot 2^p \qquad (5.4)
$$

Tọa độ của điểm lấy mẫu thứ $p$:

$$
(x_p, y_p) = \left( x_c + R\cos\frac{2\pi p}{P},\;\; y_c - R\sin\frac{2\pi p}{P} \right) \qquad (5.5)
$$

### 5.3.2. Liên kết với lý thuyết nội suy

Công thức (5.5) nói chung cho **tọa độ không nguyên**. Giá trị mức xám tại các
tọa độ này phải được nội suy — và phép nội suy tiêu chuẩn được dùng chính là nội
suy song tuyến theo công thức (4.5) đã trình bày ở chương trước.

Đây là một liên kết đáng chú ý giữa hai chương: một khái niệm tưởng như thuần
túy thuộc về mô tả kết cấu lại phụ thuộc trực tiếp vào lý thuyết nội suy của xử
lý ảnh. Nó minh họa rằng các khối kiến thức của môn học không rời rạc mà đan cài
vào nhau.

### 5.3.3. Ý nghĩa đa tỉ lệ

[S3] slide 7 minh họa ba cấu hình: $(P=8,\ R=1{,}0)$, $(P=12,\ R=2{,}5)$ và
$(P=16,\ R=4{,}0)$. Bán kính $R$ xác định **tỉ lệ không gian** mà toán tử quan
sát: $R$ nhỏ bắt kết cấu rất mịn, $R$ lớn bắt cấu trúc thô hơn. Số điểm $P$ xác
định độ phân giải góc.

### 5.3.4. Lựa chọn của dự án và giới hạn của nó

Mã nguồn **chỉ hỗ trợ** $P = 8$, $R = 1$, và chủ động ném ngoại lệ với mọi cấu
hình khác. Biện minh:

- Theo phân tích ở mục 1.2, dấu vết tái chụp cư trú ở **tần số cao nhất**, tương
  ứng với lân cận sát nhất, tức $R = 1$.
- Giữ số chiều đặc trưng nhỏ, phù hợp vai trò đường cơ sở tối giản của E01.
- Đơn giản hóa việc kiểm chứng tính đúng đắn của cài đặt.

Đồng thời cần thừa nhận đây là một **giới hạn thực sự**. LBP đa tỉ lệ — kết hợp
nhiều cặp $(P, R)$ và ghép các histogram lại — được [HFR] mục 4.3.1.3 (trang 87)
trình bày như một mở rộng tiêu chuẩn, và đã được chứng minh cải thiện hiệu năng
trên nhiều bài toán kết cấu. Việc chỉ dùng một tỉ lệ là một trong các giả thuyết
giải thích kết quả kém của E01, và là hướng phát triển ưu tiên tại mục 10.2.

## 5.4. Mẫu uniform và giảm số bin

### 5.4.1. Định nghĩa mẫu uniform

Số **chuyển tiếp bit vòng** của một mẫu LBP được định nghĩa:

$$
U(\text{LBP}_{P,R}) = \big| s(g_{P-1} - g_c) - s(g_0 - g_c) \big|
+ \sum_{p=1}^{P-1} \big| s(g_p - g_c) - s(g_{p-1} - g_c) \big| \qquad (5.6)
$$

Một mẫu được gọi là **uniform** khi $U \leq 2$, tức chuỗi bit vòng có nhiều nhất
hai lần chuyển đổi giữa 0 và 1.

Ví dụ: `00000000` có $U = 0$; `11111111` có $U = 0$; `00011110` có $U = 2$ (một
lần chuyển 0→1 và một lần chuyển 1→0) — cả ba đều uniform. Ngược lại `01010101`
có $U = 8$, không uniform.

### 5.4.2. Ý nghĩa hình học

[S3] slide 10 chỉ ra rằng các mẫu uniform tương ứng với những **nguyên hàm kết
cấu** cơ bản của ảnh tự nhiên:

| Mẫu uniform | Cấu trúc hình học tương ứng |
|---|---|
| Spot | Điểm sáng hoặc tối cô lập |
| Spot / flat | Vùng phẳng, không có cấu trúc |
| Line end | Đầu mút của một đường |
| Edge | Cạnh — biên giữa hai vùng độ sáng khác nhau |
| Corner | Góc — giao của hai cạnh |

Đây là một danh sách đáng chú ý: nó gần như trùng khớp với tập các đặc trưng thị
giác sơ cấp mà hệ thị giác sinh học và các bộ dò đặc trưng cổ điển (Sobel,
Harris, Canny) đều hướng tới. Nói cách khác, mẫu uniform không phải một thủ
thuật kỹ thuật tùy tiện mà nắm bắt đúng những cấu trúc có ý nghĩa thị giác.

### 5.4.3. Lập luận thống kê

Với $P = 8$ có tổng cộng $2^8 = 256$ mẫu có thể, trong đó **58 mẫu là uniform**.
Tuy chỉ chiếm 22,7% về số lượng, các mẫu uniform lại chiếm phần áp đảo về **tần
suất xuất hiện** trong ảnh tự nhiên — thường trên 85–90% tổng số điểm ảnh.

Điều này dẫn đến một chiến lược giảm chiều hiệu quả: gán mỗi mẫu uniform một bin
riêng và gom **toàn bộ** mẫu không uniform vào một bin duy nhất. Lợi ích kép:

1. **Giảm chiều mạnh** mà mất rất ít thông tin, vì các mẫu bị gộp vốn hiếm gặp.
2. **Ổn định thống kê**. Đây là lợi ích quan trọng hơn nhưng thường bị bỏ qua.
   Một histogram chỉ có ý nghĩa thống kê khi mỗi bin nhận đủ số đếm. Nếu chia
   256 bin trên một ô ảnh chỉ có vài trăm điểm ảnh, phần lớn bin sẽ rỗng hoặc
   chứa một, hai mẫu — khi đó histogram phản ánh nhiễu nhiều hơn phản ánh cấu
   trúc.

### 5.4.4. Ánh xạ cụ thể của dự án

Dự án sử dụng biến thể **bất biến quay kết hợp uniform**, ký hiệu chuẩn
$\text{LBP}^{riu2}_{8,1}$. Trong biến thể này, các mẫu uniform được đánh số theo
**số bit bằng 1** — một đại lượng không đổi khi xoay mẫu:

| Bin | Nội dung | Ý nghĩa |
|---:|---|---|
| 0 | Mẫu uniform có 0 bit 1 | Trung tâm sáng hơn toàn bộ lân cận |
| 1–7 | Mẫu uniform có 1 đến 7 bit 1 | Các cấu trúc cạnh, góc, đầu đường ở mức độ khác nhau |
| 8 | Mẫu uniform có 8 bit 1 | Trung tâm tối hơn toàn bộ lân cận |
| **9** | **Toàn bộ mẫu không uniform** ($U > 2$) | Cấu trúc phức tạp hoặc nhiễu |

Tổng cộng **đúng 10 bin**, khớp với `bins: 10` trong cấu hình.

**Đánh đổi cần ghi nhận:** ánh xạ bất biến quay làm **mất thông tin hướng**. Hai
cạnh có cùng độ tương phản nhưng khác hướng sẽ cho cùng một mã. Với nhận dạng
kết cấu tổng quát, đây là ưu điểm. Với PAD, đây có thể là nhược điểm: vân moiré
có hướng đặc trưng phụ thuộc vào góc giữa lưới điểm ảnh màn hình và lưới cảm
biến camera, và thông tin hướng đó bị loại bỏ. Đây là giả thuyết thứ tư cần đối
chiếu ở Chương 9.

## 5.5. Histogram không gian và mô tả khuôn mặt

### 5.5.1. Vấn đề của histogram toàn cục

Sau khi tính mã LBP cho mọi điểm ảnh, ta có một **bản đồ mã** cùng kích thước
ảnh. Cách đơn giản nhất để thu được một vector đặc trưng là lập histogram trên
toàn bản đồ. Nhưng cách này có khiếm khuyết nghiêm trọng mà [HFR] mục 4.3.2.1
(trang 87–88) nêu rõ: histogram toàn cục chỉ mã hóa **tần suất xuất hiện** của
các vi mẫu, **mất hoàn toàn thông tin về vị trí** của chúng.

Hệ quả: hai ảnh có cùng phân bố vi mẫu nhưng sắp xếp không gian hoàn toàn khác
nhau sẽ cho cùng một mô tả. Với khuôn mặt — một đối tượng có cấu trúc không gian
ổn định — đây là sự mất mát lớn.

### 5.5.2. Giải pháp chia ô

Phương pháp chuẩn, do Ahonen, Hadid và Pietikäinen đề xuất [3] và được [HFR] mục
4.3.2 trình bày, là chia ảnh thành lưới các ô không chồng lấn, tính histogram
độc lập trên từng ô, rồi **nối** các histogram theo thứ tự cố định:

```text
┌────┬────┬────┬────┐
│ h₁ │ h₂ │ h₃ │ h₄ │
├────┼────┼────┼────┤
│ h₅ │ h₆ │ h₇ │ h₈ │      →   f = [h₁ | h₂ | … | h₆₄]
├────┼────┼────┼────┤
│ ⋮  │ ⋮  │ ⋮  │ ⋮  │
└────┴────┴────┴────┘
```

Cách làm này giữ được thông tin không gian ở mức độ thô — biết vi mẫu nào xuất
hiện ở vùng nào của khuôn mặt — trong khi vẫn giữ tính bất biến với dịch chuyển
nhỏ bên trong mỗi ô.

### 5.5.3. Ý nghĩa riêng với bài toán PAD

Với nhận dạng khuôn mặt, lưới không gian có ý nghĩa vì các bộ phận giải phẫu nằm
ở vị trí tương đối ổn định. Với PAD, lý do sâu hơn: **dấu vết giả mạo không phân
bố đều trên khuôn mặt**.

- Vùng trán và gò má là bề mặt tương đối phẳng, phản xạ mạnh — nơi hiện tượng
  lóa của màn hình và mất bóng đổ 3D thể hiện rõ nhất.
- Vùng hốc mắt và cánh mũi có độ cong lớn — nơi sự khác biệt giữa bề mặt 3D thật
  và bề mặt phẳng giả bộc lộ mạnh.
- Vùng tóc và biên khuôn mặt là nơi kết cấu vật liệu nền (sợi giấy, viền màn
  hình) dễ lộ ra nhất.

Lưới không gian cho phép bộ phân lớp tuyến tính ở bước sau **gán trọng số khác
nhau cho từng vùng**, tức là tự học xem vùng nào của khuôn mặt mang nhiều thông
tin phân biệt nhất.

### 5.5.4. Chuẩn hóa và vector đặc trưng cuối

Histogram của ô $c$ được chuẩn hóa theo chuẩn $L_1$:

$$
h_c(k) = \frac{n_c(k)}{|\Omega_c|}, \qquad k = 0, 1, \dots, 9 \qquad (5.7)
$$

trong đó $n_c(k)$ là số điểm ảnh trong ô $c$ có mã rơi vào bin $k$, và
$|\Omega_c|$ là tổng số điểm ảnh của ô.

Vector đặc trưng cuối cùng là phép nối theo thứ tự hàng-trước:

$$
\mathbf{f} = \big[\, h_1(0), \dots, h_1(9),\; h_2(0), \dots, h_2(9),\; \dots,\; h_{64}(0), \dots, h_{64}(9) \,\big] \in \mathbb{R}^{640} \qquad (5.8)
$$

**Vì sao chuẩn hóa $L_1$ theo từng ô chứ không chuẩn hóa toàn cục?** Hai lý do.
Thứ nhất, khi kích thước ảnh không chia hết cho số ô, các ô ở biên có số điểm
ảnh khác các ô ở giữa; chuẩn hóa theo từng ô bảo đảm mọi ô đóng góp như nhau bất
kể kích thước. Thứ hai, chuẩn hóa $L_1$ biến histogram đếm thành một **phân bố
xác suất rời rạc**, cho phép so sánh có ý nghĩa giữa các ảnh khác kích thước và
đặt cơ sở cho việc dùng các độ đo phân bố như $\chi^2$ nếu cần.

### 5.5.5. Phép tính số chiều và biện minh tham số

Số chiều của vector đặc trưng:

$$
\dim(\mathbf{f}) = \text{grid\_rows} \times \text{grid\_cols} \times \text{bins} = 8 \times 8 \times 10 = 640 \qquad (5.9)
$$

khớp chính xác với `feature_dim: 640` trong cấu hình.

Việc chọn đồng thời độ phân giải 128×128 và lưới $8 \times 8$ có một biện minh
thống kê định lượng. Mỗi ô có kích thước:

$$
\frac{128}{8} \times \frac{128}{8} = 16 \times 16 = 256 \text{ điểm ảnh}
$$

Với 10 bin, số đếm trung bình mỗi bin là $256 / 10 = 25{,}6$. Đây là con số vừa
đủ: theo quy tắc kinh nghiệm trong thống kê, mỗi ô của một bảng tần số nên có ít
nhất 5 quan sát để các phép kiểm định và so sánh có ý nghĩa. Với 25,6 quan sát
trung bình mỗi bin, histogram đủ ổn định.

Phép tính này cho thấy ba tham số — độ phân giải ảnh, kích thước lưới và số bin
— **không độc lập** mà phải được chọn phối hợp. Chia lưới quá mịn (ví dụ
$16 \times 16$ trên ảnh 128) sẽ cho mỗi ô chỉ 64 điểm ảnh, tức 6,4 đếm mỗi bin —
histogram trở nên nhiễu. Chia lưới quá thô sẽ mất thông tin không gian.

**Nối với triển khai:** `features/lbp.py::extract_lbp`, với tham số
`grid_rows: 8, grid_cols: 8, histogram_normalization: l1_per_cell`.

## 5.6. Giảm chiều: PCA và LDA như phương án được cân nhắc

Mục này trình bày đầy đủ cơ sở toán học của hai kỹ thuật giảm chiều kinh điển mà
[S1] slide 24 liệt kê, rồi đưa ra luận cứ cho quyết định **không** đưa chúng vào
pipeline. Một quyết định thiết kế chỉ có giá trị khoa học khi các phương án bị
loại bỏ cũng được phân tích nghiêm túc.

### 5.6.1. Bài toán giảm chiều

[S6] slide 3 định nghĩa **giảm chiều đặc trưng** (feature reduction) là phép ánh
xạ dữ liệu từ không gian nhiều chiều sang không gian ít chiều hơn, với tiêu chí
phụ thuộc bối cảnh:

- **Bối cảnh không giám sát:** cực tiểu hóa mất mát thông tin.
- **Bối cảnh có giám sát:** cực đại hóa khả năng phân biệt giữa các lớp.

Phép biến đổi tuyến tính có dạng:

$$
\mathbf{y} = G^{T} \mathbf{x}, \qquad G \in \mathbb{R}^{p \times d}, \quad d \ll p \qquad (5.10)
$$

[S6] slide 5 phân biệt hai khái niệm dễ nhầm lẫn:

| | Giảm chiều đặc trưng | Chọn lọc đặc trưng |
|---|---|---|
| Đặc trưng gốc | Sử dụng **tất cả** | Chỉ giữ **một tập con** |
| Đặc trưng mới | Tổ hợp tuyến tính của đặc trưng gốc | Chính là các đặc trưng gốc được chọn |
| Khả năng diễn giải | Thấp — trục mới thường không có ý nghĩa vật lý | Cao — giữ nguyên ý nghĩa gốc |

[S6] slide 7 nêu động cơ chính là **lời nguyền số chiều** (curse of
dimensionality): độ chính xác và hiệu quả truy vấn suy giảm nhanh khi số chiều
tăng, trong khi số chiều nội tại của dữ liệu thường nhỏ hơn nhiều số chiều biểu
kiến.

### 5.6.2. Phân tích thành phần chính

**Trực giác hình học.** [S4] slide 4–17 trình bày PCA qua một chuỗi hình minh
họa: cho tập dữ liệu, tính trọng tâm, dịch gốc tọa độ về trọng tâm, tìm hướng có
phương sai cực đại, lặp lại cho các trục trực giao còn lại, thu được lưới tọa độ
đã xoay, và cuối cùng loại bỏ bớt trục bằng phép chiếu.

**Cơ sở toán học.** Cho $M$ mẫu $\mathbf{x}_1, \dots, \mathbf{x}_M \in
\mathbb{R}^N$ với trung bình $\bar{\mathbf{x}}$. Ma trận hiệp phương sai mẫu:

$$
\Sigma = \frac{1}{M} \sum_{i=1}^{M} (\mathbf{x}_i - \bar{\mathbf{x}})(\mathbf{x}_i - \bar{\mathbf{x}})^{T} \qquad (5.11)
$$

Bài toán trị riêng:

$$
\Sigma \mathbf{u}_k = \lambda_k \mathbf{u}_k, \qquad \lambda_1 \geq \lambda_2 \geq \dots \geq \lambda_N \geq 0 \qquad (5.12)
$$

[S5] slide 7 nêu tính chất then chốt: vì $\Sigma$ là ma trận **thực và đối
xứng**, các vector riêng của nó **trực giao** và tạo thành một cơ sở của không
gian. Slide này cũng phát biểu tiêu chí tối ưu: không gian con tốt nhất là không
gian có tâm tại trung bình mẫu và có các hướng xác định bởi các vector riêng ứng
với trị riêng lớn nhất, theo nghĩa cực tiểu hóa sai số tái tạo
$\min \|\mathbf{x} - \hat{\mathbf{x}}\|$.

Hệ số chiếu của một mẫu lên thành phần chính thứ $i$, theo [S5] slide 9:

$$
b_i = \mathbf{u}_i^{T} (\mathbf{x} - \bar{\mathbf{x}}) \qquad (5.13)
$$

**Chọn số chiều giữ lại.** [S5] slide 13 đưa ra tiêu chí theo tỉ lệ phương sai
tích lũy:

$$
\frac{\sum_{i=1}^{K} \lambda_i}{\sum_{i=1}^{N} \lambda_i} \geq \theta,
\qquad \theta \text{ thường chọn } 0{,}90 \text{ đến } 0{,}95 \qquad (5.14)
$$

**Sai số do giảm chiều.** [S5] slide 14 cho công thức sai số trung bình:

$$
e = \frac{1}{2} \sum_{i=K+1}^{N} \lambda_i \qquad (5.15)
$$

tức tổng các trị riêng bị bỏ đi — một kết quả đẹp: mất mát thông tin đo được
chính xác bằng phương sai không được giữ lại.

**Ứng dụng Eigenfaces.** [S5] slide 25–28 trình bày công trình kinh điển của
Turk và Pentland (1991) [13]: mỗi vector riêng của ma trận hiệp phương sai các
ảnh khuôn mặt, khi định hình lại thành ảnh hai chiều, trông giống một "khuôn mặt
ma" — do đó có tên *eigenface*. Nhận dạng được thực hiện bằng cách chiếu ảnh mới
vào không gian eigenface và so khớp trong không gian hệ số có số chiều thấp.

### 5.6.3. Phân tích tách lớp tuyến tính

[S5] slide 37 nêu mục tiêu của LDA: khác với PCA chỉ quan tâm đến phương sai
tổng thể, LDA **đồng thời** xét đến độ phân tán trong lớp và độ phân tán giữa
lớp. Đây chính là hai tiêu chí của "đặc trưng tốt" trong [S2] slide 9, được phát
biểu dưới dạng một bài toán tối ưu.

**Ma trận độ phân tán trong lớp:**

$$
S_W = \sum_{j=1}^{C} \sum_{\mathbf{x} \in \omega_j} (\mathbf{x} - \boldsymbol{\mu}_j)(\mathbf{x} - \boldsymbol{\mu}_j)^{T} \qquad (5.16)
$$

**Ma trận độ phân tán giữa lớp:**

$$
S_B = \sum_{j=1}^{C} N_j (\boldsymbol{\mu}_j - \boldsymbol{\mu})(\boldsymbol{\mu}_j - \boldsymbol{\mu})^{T} \qquad (5.17)
$$

**Tiêu chuẩn Fisher** ([S5] slide 40):

$$
U^{*} = \arg\max_{U} \frac{\left| U^{T} S_B U \right|}{\left| U^{T} S_W U \right|} \qquad (5.18)
$$

[S5] slide 41 cho biết nghiệm là các vector riêng của bài toán trị riêng suy
rộng:

$$
S_B \mathbf{u} = \lambda S_W \mathbf{u} \qquad (5.19)
$$

Các trục này được gọi là **Fisherfaces**, theo tên gọi trong công trình của
Belhumeur, Hespanha và Kriegman [14].

**Hai giới hạn quan trọng của LDA:**

1. **Giới hạn về số chiều.** [S5] slide 39 và slide 41 chỉ ra rằng $S_B$ có hạng
   tối đa $C - 1$, do đó số vector riêng có trị riêng khác không tối đa là
   $C - 1$. Với bài toán PAD hai lớp ($C = 2$), LDA chỉ cho **đúng một chiều duy
   nhất**.
2. **Vấn đề suy biến.** Khi số mẫu nhỏ hơn số chiều, $S_W$ suy biến và không khả
   nghịch. [S5] slide 43 nêu giải pháp tiêu chuẩn: chạy PCA trước để giảm chiều,
   rồi mới áp dụng LDA trong không gian con thu được.

**LDA có luôn tốt hơn PCA?** [S5] slide 53–56 trình bày kết quả của Martinez và
Kak (2001) [15] với một kết luận phản trực giác: **không phải lúc nào cũng
vậy**. Mặc dù LDA xử lý trực tiếp bài toán phân biệt trong khi PCA thì không,
khi **tập huấn luyện nhỏ**, PCA có thể cho kết quả tốt hơn LDA. Lý do là ước
lượng $S_W$ và $S_B$ từ ít mẫu có phương sai lớn, khiến hướng chiếu học được
không ổn định.

### 5.6.4. Năm luận cứ cho việc không sử dụng PCA/LDA

| Cân nhắc | Phân tích |
|---|---|
| **1. Số chiều đã đủ nhỏ** | Vector đặc trưng 640 chiều với 12.000 mẫu huấn luyện cho tỉ lệ mẫu/chiều khoảng 18,75 — nằm trong vùng lành mạnh. Chưa chạm ngưỡng lời nguyền số chiều theo nghĩa của [S6] slide 7 |
| **2. PCA cực đại phương sai, không cực đại khả năng phân biệt** | Đây là luận cứ mạnh nhất. Phương sai lớn nhất trong tập ảnh khuôn mặt đến từ **chiếu sáng và danh tính**, không phải từ dấu vết giả mạo. PCA sẽ ưu tiên giữ lại đúng những chiều mà PAD muốn bỏ qua, và có nguy cơ loại bỏ tín hiệu tinh vi cần tìm |
| **3. LDA hai lớp chỉ cho một chiều** | Nén 640 chiều xuống 1 chiều là quá chặt; ranh giới quyết định trở thành một ngưỡng đơn trên một phép chiếu tuyến tính, mất toàn bộ khả năng biểu diễn cấu trúc còn lại |
| **4. SVM đã tự chính quy hóa** | Chuẩn $L_2$ trên $\mathbf{w}$ trong công thức (6.4) đã kiểm soát năng lực mô hình. Giảm chiều tường minh trở nên dư thừa và chỉ thêm một siêu tham số cần dò |
| **5. Đối chứng với Martinez & Kak** | [S5] slide 53–56 cho thấy giảm chiều không phải bước bắt buộc mà là lựa chọn theo bối cảnh; áp dụng máy móc có thể phản tác dụng |

**Kết luận mục.** PCA và LDA vẫn giữ giá trị như đường cơ sở đối chứng: một thí
nghiệm áp dụng PCA lên đặc trưng LBP rồi so sánh với E01 sẽ kiểm chứng trực tiếp
luận cứ số 2 ở trên. Thí nghiệm này được đưa vào mục 10.2.

## 5.7. Kết luận chương

Chương này đã xây dựng đầy đủ chuỗi biến đổi từ ảnh khuôn mặt chuẩn hóa đến
vector đặc trưng 640 chiều, với mỗi bước được biện minh bằng lý thuyết: toán tử
LBP và tính bất biến với biến đổi mức xám đơn điệu; mẫu uniform và lập luận ổn
định thống kê; lưới không gian và ý nghĩa riêng của nó với PAD; phép tính số
chiều cho thấy ba tham số phải được chọn phối hợp.

Chương cũng ghi nhận bốn giả thuyết về giới hạn của biểu diễn này: mất thông tin
màu, chỉ một tỉ lệ không gian, mất thông tin hướng do bất biến quay, và mất tần
số cao do thu nhỏ ảnh. Bốn giả thuyết này sẽ được đối chiếu với số liệu thực
nghiệm ở mục 9.6.

Chương tiếp theo trình bày khối cuối cùng của nhánh thủ công: bộ phân lớp.
---

# Chương 6. Phân lớp biên cực đại: Support Vector Machine

Chương này trình bày khối *Classifier* của sơ đồ [S2] slide 8 cho nhánh thủ
công. Nội dung bám sát mạch dẫn dắt của [S7].

## 6.1. Hàm phân biệt tuyến tính

### 6.1.1. Định nghĩa

[S7] slide 5 nhắc lại nguyên tắc chung: bộ phân lớp gán vector đặc trưng
$\mathbf{x}$ cho lớp $\omega_i$ nếu $g_i(\mathbf{x}) > g_j(\mathbf{x})$ với mọi
$j \neq i$. Với bài toán hai lớp, điều này rút gọn thành việc xét dấu của một
hàm phân biệt duy nhất.

[S7] slide 7 định nghĩa hàm phân biệt tuyến tính:

$$
g(\mathbf{x}) = \mathbf{w}^{T}\mathbf{x} + b \qquad (6.1)
$$

### 6.1.2. Ý nghĩa hình học

Tập $\{\mathbf{x} : g(\mathbf{x}) = 0\}$ là một **siêu phẳng** trong không gian
đặc trưng. Vector $\mathbf{w}$ là **vector pháp tuyến** của siêu phẳng đó; vector
pháp tuyến đơn vị là $\mathbf{n} = \mathbf{w}/\|\mathbf{w}\|$. Nửa không gian
$\mathbf{w}^T\mathbf{x} + b > 0$ được gán một lớp, nửa còn lại được gán lớp kia.

Khoảng cách có dấu từ một điểm $\mathbf{x}$ đến siêu phẳng:

$$
d(\mathbf{x}) = \frac{\mathbf{w}^{T}\mathbf{x} + b}{\|\mathbf{w}\|} \qquad (6.2)
$$

Công thức này giải thích một chi tiết sẽ gặp ở phần kết quả: điểm số mà
`LinearSVC` trả về qua `decision_function` là giá trị $g(\mathbf{x})$, tức một
**khoảng cách có dấu** chứ không phải xác suất. Do đó ngưỡng quyết định của E01
mang giá trị âm ($-0{,}4000959$) hoàn toàn hợp lệ và không hàm ý "xác suất âm".

### 6.1.3. Đặt vấn đề

[S7] slide 8 đến slide 11 lặp lại cùng một hình vẽ với các đường phân tách khác
nhau, kèm câu hỏi: *"How would you classify these points using a linear
discriminant function in order to minimize the error rate?"* và câu trả lời:
*"Infinite number of answers!"* — có vô số đáp án.

Slide 11 kết thúc bằng câu hỏi then chốt: **"Which one is the best?"**

Đây chính xác là câu hỏi đã được đặt ra tại mục 3.2 khi giới thiệu công thức
(3.2). Toàn bộ phần còn lại của chương là câu trả lời.

## 6.2. Nguyên lý biên cực đại

### 6.2.1. Định nghĩa biên

[S7] slide 12 định nghĩa **biên** (margin) là bề rộng mà ranh giới quyết định có
thể được nới ra trước khi chạm vào điểm dữ liệu đầu tiên — hình ảnh "vùng an
toàn" (safe zone) hai bên siêu phẳng.

Slide này đưa ra luận điểm trung tâm: *hàm phân biệt tuyến tính có biên cực đại
là hàm tốt nhất*, với lý do *bền vững trước điểm ngoại lai và do đó có khả năng
tổng quát hóa mạnh*.

Trực giác đằng sau luận điểm: nếu ranh giới nằm sát các điểm huấn luyện, thì một
nhiễu nhỏ trong dữ liệu mới cũng đủ đẩy điểm sang phía sai. Ranh giới có biên
rộng để lại "khoảng đệm" chịu được nhiễu. Đây là một dạng nguyên lý chính quy
hóa hình học.

[S7] slide 3 ghi công: SVM được Vapnik và cộng sự phát triển năm 1992 từ lý
thuyết học thống kê; công trình nền tảng được công bố bởi Cortes và Vapnik [4].

### 6.2.2. Dạng chuẩn tắc

Cho tập dữ liệu $\{(\mathbf{x}_i, y_i)\}_{i=1}^{n}$ với $y_i \in \{-1, +1\}$.
Điều kiện phân lớp đúng là:

$$
y_i (\mathbf{w}^{T}\mathbf{x}_i + b) > 0, \qquad \forall i
$$

[S7] slide 13 chỉ ra rằng vì $(\mathbf{w}, b)$ và $(\alpha\mathbf{w}, \alpha b)$
với $\alpha > 0$ xác định **cùng một siêu phẳng**, ta có thể chuẩn hóa thang đo
để các điểm gần nhất thỏa dấu bằng:

$$
y_i (\mathbf{w}^{T}\mathbf{x}_i + b) \geq 1, \qquad i = 1, \dots, n \qquad (6.3)
$$

Đây là **dạng chuẩn tắc**. Phép chuẩn hóa này loại bỏ tính không xác định của
thang đo và cho phép biểu diễn biên bằng một công thức đơn giản.

### 6.2.3. Từ hình học sang tối ưu

Với dạng chuẩn tắc, hai siêu phẳng biên là $\mathbf{w}^T\mathbf{x} + b = \pm 1$.
Khoảng cách giữa chúng, tính theo công thức (6.2):

$$
\text{margin} = \frac{2}{\|\mathbf{w}\|} \qquad (6.4)
$$

Đây là bước chuyển then chốt của toàn bộ lý thuyết: **cực đại hóa biên tương
đương với cực tiểu hóa $\|\mathbf{w}\|$**, và vì hàm bình phương đơn điệu tăng
trên miền không âm, tương đương với cực tiểu hóa $\frac{1}{2}\|\mathbf{w}\|^2$.
Hệ số $\frac{1}{2}$ được thêm vào thuần túy để đạo hàm gọn hơn.

Một bài toán hình học mơ hồ ("đường nào tốt nhất?") đã được biến thành một bài
toán **quy hoạch toàn phương lồi** có nghiệm duy nhất.

## 6.3. Bài toán tối ưu và đối ngẫu Lagrange

### 6.3.1. Bài toán gốc

$$
\begin{aligned}
\min_{\mathbf{w}, b} \quad & \tfrac{1}{2}\|\mathbf{w}\|^{2} \\
\text{với ràng buộc} \quad & y_i(\mathbf{w}^{T}\mathbf{x}_i + b) \geq 1, \quad i = 1, \dots, n
\end{aligned} \qquad (6.5)
$$

Đây là bài toán quy hoạch toàn phương với hàm mục tiêu lồi và ràng buộc tuyến
tính, do đó có nghiệm toàn cục duy nhất.

### 6.3.2. Hàm Lagrange và bài toán đối ngẫu

[S7] slide 20 xây dựng hàm Lagrange:

$$
L_p(\mathbf{w}, b, \boldsymbol{\alpha}) = \frac{1}{2}\|\mathbf{w}\|^{2}
- \sum_{i=1}^{n} \alpha_i \left[ y_i(\mathbf{w}^{T}\mathbf{x}_i + b) - 1 \right] \qquad (6.6)
$$

Lấy đạo hàm riêng theo $\mathbf{w}$ và $b$ rồi đặt bằng không:

$$
\frac{\partial L_p}{\partial \mathbf{w}} = 0 \;\Rightarrow\; \mathbf{w} = \sum_{i=1}^{n} \alpha_i y_i \mathbf{x}_i,
\qquad
\frac{\partial L_p}{\partial b} = 0 \;\Rightarrow\; \sum_{i=1}^{n} \alpha_i y_i = 0 \qquad (6.7)
$$

Thay ngược vào, ta thu được **bài toán đối ngẫu** ([S7] slide 20):

$$
\begin{aligned}
\max_{\boldsymbol{\alpha}} \quad & \sum_{i=1}^{n} \alpha_i - \frac{1}{2}\sum_{i=1}^{n}\sum_{j=1}^{n} \alpha_i \alpha_j y_i y_j \, \mathbf{x}_i^{T}\mathbf{x}_j \\
\text{với ràng buộc} \quad & \alpha_i \geq 0, \qquad \sum_{i=1}^{n} \alpha_i y_i = 0
\end{aligned} \qquad (6.8)
$$

### 6.3.3. Điều kiện KKT và vector hỗ trợ

[S7] slide 21 áp dụng điều kiện Karush–Kuhn–Tucker:

$$
\alpha_i \left[ y_i(\mathbf{w}^{T}\mathbf{x}_i + b) - 1 \right] = 0, \qquad \forall i \qquad (6.9)
$$

Điều kiện tích bằng không này có một hệ quả rất mạnh. Với mỗi $i$, hoặc
$\alpha_i = 0$, hoặc $y_i(\mathbf{w}^T\mathbf{x}_i + b) = 1$ — tức điểm nằm
**đúng trên siêu phẳng biên**. Do đó:

$$
\mathbf{w} = \sum_{i=1}^{n} \alpha_i y_i \mathbf{x}_i = \sum_{i \in \mathcal{SV}} \alpha_i y_i \mathbf{x}_i \qquad (6.10)
$$

Nghiệm **chỉ phụ thuộc vào các điểm nằm trên biên** — gọi là các **vector hỗ
trợ**. Mọi điểm khác, dù có bao nhiêu đi nữa, không ảnh hưởng đến siêu phẳng.
Đây là tính chất thưa (sparsity) đặc trưng của SVM và giải thích vì sao mô hình
E01 chỉ chiếm 21,7 KB dung lượng.

### 6.3.4. Hàm quyết định và cánh cửa dẫn tới kernel

[S7] slide 22 viết hàm quyết định dưới dạng:

$$
g(\mathbf{x}) = \mathbf{w}^{T}\mathbf{x} + b = \sum_{i \in \mathcal{SV}} \alpha_i y_i \, \mathbf{x}_i^{T}\mathbf{x} + b \qquad (6.11)
$$

Slide này nhấn mạnh một quan sát then chốt: hàm quyết định **chỉ phụ thuộc vào
tích vô hướng** giữa điểm cần phân lớp và các vector hỗ trợ; và việc giải bài
toán tối ưu cũng chỉ cần các tích vô hướng $\mathbf{x}_i^T\mathbf{x}_j$ giữa các
cặp điểm huấn luyện.

Dữ liệu gốc không bao giờ xuất hiện ngoài các tích vô hướng. Đây chính là cánh
cửa dẫn tới thủ thuật hạt nhân ở mục 6.5.

## 6.4. Biên mềm và tham số C

### 6.4.1. Vấn đề

[S7] slide 23 đặt câu hỏi: điều gì xảy ra nếu dữ liệu **không tách được tuyến
tính** do nhiễu hoặc điểm ngoại lai? Bài toán (6.5) khi đó **vô nghiệm**, vì
không tồn tại $(\mathbf{w}, b)$ thỏa mãn đồng thời mọi ràng buộc.

Với bài toán PAD, tình huống này gần như chắc chắn xảy ra: một số ảnh giả mạo
chất lượng rất cao có thống kê kết cấu gần như không phân biệt được với ảnh
thật, còn một số ảnh thật thu trong điều kiện xấu lại có thống kê giống ảnh giả.

### 6.4.2. Biến bù

Giải pháp là đưa vào **biến bù** (slack variable) $\xi_i \geq 0$ cho phép vi
phạm ràng buộc có kiểm soát ([S7] slide 23–24):

$$
\begin{aligned}
\min_{\mathbf{w}, b, \boldsymbol{\xi}} \quad & \frac{1}{2}\|\mathbf{w}\|^{2} + C \sum_{i=1}^{n} \xi_i \\
\text{với ràng buộc} \quad & y_i(\mathbf{w}^{T}\mathbf{x}_i + b) \geq 1 - \xi_i \\
& \xi_i \geq 0, \quad i = 1, \dots, n
\end{aligned} \qquad (6.12)
$$

Giá trị $\xi_i$ đo mức độ vi phạm của mẫu thứ $i$: $\xi_i = 0$ nghĩa là mẫu nằm
đúng hoặc ngoài biên; $0 < \xi_i < 1$ nghĩa là mẫu nằm trong vùng biên nhưng vẫn
được phân lớp đúng; $\xi_i > 1$ nghĩa là mẫu bị phân lớp sai.

### 6.4.3. Vai trò của tham số C

[S7] slide 24 nêu ngắn gọn: *"Parameter C can be viewed as a way to control
over-fitting"*. Phân tích chi tiết hơn:

| Giá trị C | Tác động lên hàm mục tiêu | Hệ quả hình học | Rủi ro |
|---|---|---|---|
| **C lớn** | Phạt nặng mọi vi phạm | Biên hẹp, ranh giới uốn theo từng điểm | Khớp quá mức (overfitting) |
| **C nhỏ** | Chấp nhận nhiều vi phạm | Biên rộng, ranh giới trơn | Khớp thiếu (underfitting) |

Tham số $C$ điều tiết sự đánh đổi kinh điển giữa **độ phức tạp mô hình** (số hạng
$\|\mathbf{w}\|^2$) và **sai số huấn luyện** (số hạng $\sum \xi_i$). Đây chính
là nguyên lý cực tiểu hóa rủi ro cấu trúc của lý thuyết học thống kê.

### 6.4.4. Dò tham số trong thực nghiệm

Dự án dò $C$ trên lưới sáu giá trị theo thang lôgarit:

$$
C \in \{10^{-4},\; 10^{-3},\; 10^{-2},\; 10^{-1},\; 1,\; 10\}
$$

Việc dò theo thang lôgarit thay vì thang tuyến tính là chuẩn mực, vì ảnh hưởng
của $C$ mang tính nhân chứ không phải cộng.

Giá trị được chọn là $C = 10^{-4}$ — **giá trị nhỏ nhất trong lưới**. Đây là một
kết quả có ý nghĩa lý thuyết đáng bàn: nó cho thấy quá trình chọn mô hình trên
tập phát triển đã ưu tiên **biên rộng và mô hình đơn giản** hơn là khớp sát dữ
liệu huấn luyện. Nói cách khác, dữ liệu tự nó chỉ ra rằng đặc trưng LBP có tỉ lệ
nhiễu cao, và mô hình cần được chính quy hóa mạnh. Điều này nhất quán với giả
thuyết rằng biểu diễn LBP mang nhiều biến thiên không liên quan đến nhãn.

Đáng lưu ý là dù đã chính quy hóa mạnh như vậy, mô hình vẫn không tổng quát hóa
được sang tập kiểm tra — cho thấy vấn đề không nằm ở việc chọn siêu tham số mà
nằm ở chính bản thân biểu diễn.

Kết quả dò được lưu tại
`artifacts/runs/lbp_svm/.../selection/c_search.csv`.

## 6.5. Thủ thuật hạt nhân

### 6.5.1. Ý tưởng

[S7] slide 25 trở đi trình bày trường hợp dữ liệu không tách được tuyến tính
trong không gian gốc nhưng tách được sau khi ánh xạ sang không gian nhiều chiều
hơn. Gọi $\phi: \mathbb{R}^{d} \to \mathcal{H}$ là ánh xạ đó. Vì bài toán (6.8)
và hàm quyết định (6.11) chỉ dùng tích vô hướng, ta chỉ cần biết:

$$
K(\mathbf{x}_i, \mathbf{x}_j) = \phi(\mathbf{x}_i)^{T} \phi(\mathbf{x}_j) \qquad (6.13)
$$

mà **không cần tính $\phi$ một cách tường minh**. Đây là thủ thuật hạt nhân:
không gian đích có thể có số chiều rất lớn, thậm chí vô hạn, nhưng chi phí tính
toán chỉ phụ thuộc vào việc tính hàm $K$.

Các hàm hạt nhân thông dụng:

| Hạt nhân | Công thức | Đặc điểm |
|---|---|---|
| Tuyến tính | $K(\mathbf{x}, \mathbf{z}) = \mathbf{x}^{T}\mathbf{z}$ | Không ánh xạ; nhanh nhất |
| Đa thức bậc $d$ | $K(\mathbf{x}, \mathbf{z}) = (\gamma \mathbf{x}^{T}\mathbf{z} + r)^{d}$ | Bắt tương tác bậc cao giữa các đặc trưng |
| Gaussian (RBF) | $K(\mathbf{x}, \mathbf{z}) = \exp(-\gamma\|\mathbf{x} - \mathbf{z}\|^{2})$ | Không gian đích vô hạn chiều; rất linh hoạt |

### 6.5.2. Vì sao dự án chọn hạt nhân tuyến tính

Cấu hình sử dụng `estimator: LinearSVC`, tức hạt nhân tuyến tính. Ba lý do:

1. **Số chiều đã cao.** Đặc trưng LBP có 640 chiều. Theo một kết quả kinh
   nghiệm quen thuộc trong học máy, khi số chiều đủ lớn so với số mẫu, dữ liệu
   thường đã gần tách được tuyến tính, và lợi ích của hạt nhân phi tuyến giảm
   đáng kể.
2. **Giữ tính sạch của phép so sánh.** Đây là lý do quan trọng nhất về mặt
   phương pháp luận. Trục so sánh chính của báo cáo là *biểu diễn thủ công so
   với biểu diễn học được*. Nếu E01 dùng SVM hạt nhân RBF, thì khi E04 thắng E01
   ta sẽ không phân biệt được nguyên nhân là do biểu diễn tốt hơn hay do bộ phân
   lớp phức tạp hơn. Giữ bộ phân lớp ở dạng tuyến tính đơn giản nhất giúp quy
   kết nguyên nhân rõ ràng.
3. **Chi phí suy luận.** Với hạt nhân tuyến tính, hàm quyết định rút gọn về một
   tích vô hướng duy nhất với $\mathbf{w}$ đã tính sẵn, cho độ trễ 0,163 ms mỗi
   mẫu — thấp hơn một bậc so với các mô hình CNN.

SVM hạt nhân RBF được đề xuất như thí nghiệm mở rộng tại mục 10.2.

## 6.6. Xử lý mất cân bằng lớp

### 6.6.1. Vấn đề

Protocol 1 của OULU-NPU có tỉ lệ lớp **live : spoof = 1 : 4**. Cụ thể, tập huấn
luyện có 240 video thật và 960 video giả, tương ứng 2.400 và 9.600 khung hình.

Với dữ liệu lệch như vậy, một bộ phân lớp cực tiểu hóa sai số tổng thể có động
cơ mạnh để thiên về lớp đa số. Trường hợp cực đoan: luôn dự đoán `spoof` cho đạt
80% độ chính xác — một mô hình vô dụng nhưng có vẻ tốt trên giấy.

### 6.6.2. Cơ chế cân bằng trọng số

Cấu hình `class_weight: balanced` gán cho mỗi lớp một trọng số tỉ lệ nghịch với
tần suất của nó:

$$
c_k = \frac{n}{K \cdot n_k} \qquad (6.14)
$$

trong đó $n$ là tổng số mẫu, $K$ là số lớp, $n_k$ là số mẫu của lớp $k$. Hàm mục
tiêu trở thành:

$$
\min_{\mathbf{w}, b, \boldsymbol{\xi}} \quad \frac{1}{2}\|\mathbf{w}\|^{2} + C \sum_{i=1}^{n} c_{y_i} \, \xi_i \qquad (6.15)
$$

Với tỉ lệ 1:4, lớp `live` nhận trọng số gấp bốn lần lớp `spoof`. Về mặt hình học,
điều này đẩy siêu phẳng dịch chuyển sao cho việc phân lớp sai một mẫu `live` bị
phạt nặng gấp bốn lần.

### 6.6.3. Liên hệ với chỉ số đánh giá

Điểm cần nhấn mạnh: cân bằng trọng số xử lý mất cân bằng ở **pha học**, nhưng
vấn đề mất cân bằng còn xuất hiện ở **pha đánh giá**. Nếu dùng độ chính xác làm
chỉ số, mô hình luôn dự đoán `spoof` vẫn đạt 80%. Do đó cần một bộ chỉ số tính
sai số riêng cho từng lớp — đây chính là động cơ của APCER, BPCER và ACER được
trình bày ở Chương 8.

Hai cơ chế này bổ sung chứ không thay thế nhau: một cơ chế tác động lên hàm mục
tiêu liên tục ở mức khung hình huấn luyện, cơ chế kia đo quyết định rời rạc ở
mức video kiểm tra.

### 6.6.4. Các siêu tham số còn lại

Để bảo đảm khả năng tái lập, các siêu tham số còn lại của `LinearSVC`:

| Tham số | Giá trị | Ý nghĩa |
|---|---|---|
| `penalty` | `l2` | Chính quy hóa chuẩn $L_2$, tương ứng số hạng $\|\mathbf{w}\|^2$ |
| `loss` | `squared_hinge` | Hàm mất mát bản lề bình phương, khả vi mọi nơi |
| `dual` | `false` | Giải bài toán gốc thay vì đối ngẫu — hiệu quả hơn khi $n > d$ |
| `tolerance` | $10^{-4}$ | Ngưỡng hội tụ |
| `max_iterations` | 20.000 | Giới hạn số vòng lặp |
| `seed` | 42 | Hạt giống ngẫu nhiên cố định |

Việc đặt `dual: false` là hợp lý vì ở đây $n = 12.000$ mẫu lớn hơn $d = 640$
chiều.

## 6.7. Kết luận chương

Chương này đã đi trọn con đường từ một câu hỏi hình học mơ hồ — *"trong vô số
siêu phẳng phân tách, cái nào tốt nhất?"* — đến một bài toán quy hoạch toàn
phương lồi có nghiệm duy nhất, thông qua nguyên lý biên cực đại. Các bước then
chốt gồm: chuẩn hóa thang đo để có dạng chuẩn tắc; biểu diễn biên bằng
$2/\|\mathbf{w}\|$; chuyển sang bài toán đối ngẫu; và áp dụng điều kiện KKT để
phát hiện rằng nghiệm chỉ phụ thuộc vào một tập con nhỏ các vector hỗ trợ.

Chương cũng phân tích ba mở rộng cần thiết cho dữ liệu thực: biên mềm với tham
số $C$ để xử lý dữ liệu không tách được, thủ thuật hạt nhân để xử lý cấu trúc
phi tuyến, và cân bằng trọng số để xử lý lệch lớp.

Đến đây, nhánh thủ công E01 đã hoàn chỉnh. Chương tiếp theo trình bày nhánh
thay thế: để cho dữ liệu tự học ra biểu diễn.

---

# Chương 7. Biểu diễn học sâu và học chuyển giao

> **Ghi chú về nguồn tài liệu.** Bộ slide [S8] cung cấp nền tảng đầy đủ cho mạng
> nơ-ron truyền thẳng: cấu trúc nơ-ron, hàm mất mát, hạ gradient, lan truyền
> ngược, ReLU, dropout, và lập luận về lợi ích của mạng sâu. Tuy nhiên [S8]
> **không trình bày mạng tích chập**. Do đó các mục 7.4 đến 7.6 được xây dựng
> trên tài liệu ngoài phạm vi môn học và được trích dẫn tương ứng: LeCun và cộng
> sự [11] cho phép tích chập, Ioffe và Szegedy [5] cho chuẩn hóa theo lô, He và
> cộng sự [7] cho học phần dư, Sandler và cộng sự [8] cho tích chập tách theo
> chiều sâu. Báo cáo không gán những nội dung này cho bài giảng của môn học.

## 7.1. Từ nơ-ron đến mạng nhiều lớp

### 7.1.1. Đơn vị cơ bản

[S8] slide 8 định nghĩa một nơ-ron nhân tạo là hàm $f: \mathbb{R}^{K} \to
\mathbb{R}$:

$$
z = \sum_{k=1}^{K} w_k a_k + b, \qquad a = \sigma(z) \qquad (7.1)
$$

với $w_k$ là các trọng số, $b$ là độ lệch (bias) và $\sigma$ là hàm kích hoạt.

So sánh công thức (7.1) với công thức (6.1) của hàm phân biệt tuyến tính cho
thấy điều quan trọng: **một nơ-ron đơn lẻ chính là một bộ phân lớp tuyến tính**
có thêm hàm kích hoạt phi tuyến. Sức mạnh của mạng nơ-ron không nằm ở đơn vị cơ
bản mà nằm ở cách tổ hợp nhiều đơn vị.

### 7.1.2. Kiến trúc nhiều lớp

[S8] slide 9 mô tả kiến trúc gồm lớp đầu vào, các lớp ẩn và lớp đầu ra. Mạng
định nghĩa một họ hàm có tham số $f_{\theta}: \mathbb{R}^{N} \to \mathbb{R}^{M}$,
trong đó $\theta$ gồm toàn bộ trọng số và độ lệch.

### 7.1.3. Định lý xấp xỉ phổ quát và nghịch lý của nó

[S8] slide 34 phát biểu **định lý xấp xỉ phổ quát**: một mạng chỉ với **một lớp
ẩn** đủ rộng có thể xấp xỉ bất kỳ hàm liên tục nào với độ chính xác tùy ý.

Định lý này đặt ra một câu hỏi tự nhiên: nếu một lớp ẩn là đủ, vì sao cần mạng
sâu? [S8] slide 35–36 so sánh trực tiếp hai cấu hình "Fat + Short" (rộng và
nông) với "Thin + Tall" (hẹp và sâu), và slide 37–40 đưa ra câu trả lời bằng lập
luận **mô-đun hóa** (modularization).

Lập luận như sau: mạng sâu xây dựng biểu diễn theo tầng bậc, trong đó các đặc
trưng ở tầng sau được tổ hợp từ các đặc trưng ở tầng trước. Sự **tái sử dụng**
các mô-đun trung gian này cho phép mạng sâu đạt cùng năng lực biểu diễn với số
tham số ít hơn nhiều so với mạng nông tương đương. Định lý xấp xỉ phổ quát nói
về *khả năng tồn tại*, không nói về *hiệu quả tham số* hay *khả năng học được
trong thực tế*.

**Liên hệ với đề tài.** Đây chính là biện minh lý thuyết cho việc chọn ResNet18
với 18 tầng thay vì một mạng truyền thẳng rộng. Với bài toán PAD, cấu trúc phân
cấp có ý nghĩa vật lý rõ ràng: tầng thấp học các bộ dò cạnh và điểm, tầng giữa tổ
hợp thành mô-típ kết cấu, tầng cao tổ hợp thành các mẫu hình đặc trưng cho bề
mặt da thật hay bề mặt in.

## 7.2. Hàm mất mát và bài toán huấn luyện

### 7.2.1. Chi phí trên tập huấn luyện

[S8] slide 20 định nghĩa chi phí trên một mẫu là khoảng cách giữa đầu ra mạng và
đích — có thể là khoảng cách Euclid hoặc entropy chéo. Slide 21 tổng hợp thành
chi phí toàn cục:

$$
C(\theta) = \sum_{r=1}^{R} L^{r}(\theta) \qquad (7.2)
$$

và phát biểu bài toán: tìm $\theta^{*}$ cực tiểu hóa $C(\theta)$.

### 7.2.2. Sigmoid và entropy chéo nhị phân

Với bài toán hai lớp, hàm sigmoid ánh xạ logit về khoảng $(0,1)$:

$$
\sigma(z) = \frac{1}{1 + e^{-z}} \qquad (7.3)
$$

Hàm mất mát entropy chéo nhị phân có trọng số lớp:

$$
L = -\frac{1}{N}\sum_{i=1}^{N}\Big[ w_{+} \, y_i \log \sigma(z_i) + (1 - y_i)\log\big(1 - \sigma(z_i)\big) \Big] \qquad (7.4)
$$

### 7.2.3. Vì sao chọn một logit thay vì softmax hai lớp

[S8] slide 16–18 trình bày softmax như lớp đầu ra chuẩn cho bài toán nhiều lớp.
Với bài toán hai lớp, softmax hai đầu ra và sigmoid một đầu ra **tương đương về
mặt biểu diễn**: có thể chứng minh rằng softmax hai lớp rút gọn thành sigmoid
của hiệu hai logit.

Dự án chọn cấu hình một logit (`output_dim: 1`, `score_type: logit`,
`loss: BCEWithLogitsLoss`) vì một lý do thực tiễn quan trọng: nó cho ra **một
điểm số vô hướng liên tục duy nhất** cho mỗi mẫu. Điểm số vô hướng này là điều
kiện cần để:

- quét ngưỡng và vẽ đường ROC/DET (mục 8.3);
- gộp điểm số theo video bằng phép trung bình (mục 8.4);
- so sánh trực tiếp với `decision_function` của SVM trên cùng một khung khái
  niệm.

Nếu dùng softmax hai đầu ra, ta sẽ phải quy ước lấy một trong hai giá trị hoặc
lấy hiệu của chúng — thêm một bước quy ước không cần thiết. Đây là ví dụ cho
thấy hai lựa chọn tương đương về lý thuyết vẫn có thể khác nhau về tính thuận
tiện kỹ thuật.

### 7.2.4. Trọng số dương

Tham số `pos_weight = 0,25` trong công thức (7.4) tương ứng $w_{+} = 0{,}25$.
Vì lớp `spoof` (dương) chiếm 80% dữ liệu, trọng số 0,25 giảm đóng góp của lớp
này xuống bằng đúng $1/4$, cân bằng lại tổng đóng góp của hai lớp. Đây là cơ chế
tương ứng với `class_weight: balanced` của SVM ở mục 6.6, áp dụng cho hàm mất
mát khả vi.

## 7.3. Tối ưu hóa

### 7.3.1. Hạ gradient

[S8] slide 22–26 trình bày thuật toán hạ gradient:

$$
\theta^{(t+1)} = \theta^{(t)} - \eta \, \nabla C\big(\theta^{(t)}\big) \qquad (7.5)
$$

Slide 24 cũng lưu ý rằng hạ gradient **không bảo đảm tìm được cực tiểu toàn
cục** — một hạn chế cần ghi nhận nhưng trong thực tế ít gây trở ngại với mạng
sâu.

### 7.3.2. Mini-batch

[S8] slide 28–30 giới thiệu biến thể mini-batch: thay vì tính gradient trên toàn
bộ tập huấn luyện ở mỗi bước, ta tính trên một lô nhỏ được lấy ngẫu nhiên. Lợi
ích gồm chi phí mỗi bước thấp hơn nhiều, và tính ngẫu nhiên của gradient giúp
thoát khỏi các điểm yên ngựa và cực tiểu địa phương nông.

Dự án dùng kích thước lô 16.

### 7.3.3. Lan truyền ngược — một điểm cần nói chính xác

[S8] slide 31 trình bày lan truyền ngược. Cần nhấn mạnh một điểm mà nhiều tài
liệu diễn đạt thiếu chính xác: **lan truyền ngược không phải là một thuật toán
tối ưu hóa.** Nó là một phương pháp **tính gradient hiệu quả** bằng cách áp dụng
quy tắc chuỗi theo thứ tự từ đầu ra ngược về đầu vào, tận dụng việc lưu lại các
giá trị trung gian để tránh tính lặp.

Thuật toán tối ưu hóa là hạ gradient (hoặc các biến thể như Adam). Lan truyền
ngược chỉ cung cấp đại lượng $\nabla C(\theta)$ cho thuật toán đó sử dụng. Phân
biệt đúng hai khái niệm này là một chi tiết nhỏ nhưng thể hiện sự chính xác về
mặt khái niệm.

### 7.3.4. Tốc độ học và thuật toán Adam

[S8] slide 55–61 phân tích ảnh hưởng của tốc độ học: quá lớn thì hàm mất mát dao
động hoặc phân kỳ, quá nhỏ thì hội tụ chậm. Slide 26–27 giới thiệu động lượng
(momentum) như một cải tiến.

Dự án sử dụng thuật toán Adam [6] — kết hợp động lượng với tốc độ học thích nghi
riêng cho từng tham số — với các siêu tham số:

| Tham số | Giá trị |
|---|---|
| Thuật toán tối ưu | Adam |
| Tốc độ học (head) | $10^{-4}$ |
| Suy giảm trọng số | $10^{-4}$ |
| Kích thước lô | 16 |
| Số epoch tối đa | 15 |
| Số epoch tối thiểu | 3 |
| Kiên nhẫn (patience) | 3 |
| Hạt giống | 42 |

Riêng E04 sử dụng **hai tốc độ học khác nhau** cho hai nhóm tham số — lý do được
giải thích ở mục 7.7.

### 7.3.5. Khớp quá mức và các biện pháp chống

[S8] slide 45–46 trình bày hiện tượng khớp quá mức và các biện pháp khắc phục,
trong đó có hàm kích hoạt mới (ReLU) và dropout.

**ReLU** ([S8] slide 48–54):

$$
\text{ReLU}(z) = \max(0, z) \qquad (7.6)
$$

Slide 48–50 giải thích động cơ chính: hàm sigmoid có đạo hàm cực đại chỉ bằng
0,25 và tiến về 0 ở hai đầu, nên khi nhân dồn qua nhiều tầng, gradient suy giảm
theo cấp số nhân — hiện tượng **tiêu biến gradient** (vanishing gradient). ReLU
có đạo hàm bằng đúng 1 trên miền dương, nên không gây suy giảm.

**Dropout** ([S8] slide 62–72): trong quá trình huấn luyện, mỗi nơ-ron bị tắt
ngẫu nhiên với xác suất $p$. Slide 70–72 diễn giải dropout như một dạng **học
tổ hợp** (ensemble): mỗi lần huấn luyện là một mạng con khác nhau, và khi suy
luận, mạng đầy đủ xấp xỉ trung bình của toàn bộ tổ hợp các mạng con.

Trong dự án, biện pháp chống khớp quá mức chính không phải dropout mà là **đóng
băng phần lớn tham số** — một dạng chính quy hóa mạnh hơn nhiều, được trình bày
ở mục 7.7. Ngoài ra dự án dùng thêm suy giảm trọng số $10^{-4}$, dừng sớm với
kiên nhẫn 3 epoch, và tăng cường dữ liệu bằng lật ngang với xác suất 0,5 **chỉ
trên tập huấn luyện**.

Việc lật ngang là phép tăng cường hợp lệ vì khuôn mặt gần đối xứng qua trục dọc
và phép lật không làm thay đổi nhãn live/spoof. Đây là một ứng dụng của nguyên
lý **bất biến có kiểm chứng**: chỉ áp dụng những phép biến đổi mà ta biết chắc
bảo toàn nhãn.

## 7.4. Phép tích chập

> *Nguồn: LeCun và cộng sự [11]. Nội dung này không có trong [S8].*

### 7.4.1. Định nghĩa

Phép tích chập hai chiều rời rạc giữa ảnh $I$ và nhân $K$:

$$
(I * K)(i, j) = \sum_{m}\sum_{n} I(i - m,\, j - n) \, K(m, n) \qquad (7.7)
$$

Trong thực tế, các thư viện học sâu cài đặt phép tương quan chéo (không lật
nhân), nhưng vì nhân được học nên sự khác biệt không có ý nghĩa thực tiễn.

### 7.4.2. Ba tính chất và ý nghĩa với PAD

| Tính chất | Nội dung | Ý nghĩa riêng với bài toán PAD |
|---|---|---|
| **Kết nối cục bộ** | Mỗi nơ-ron chỉ nhận đầu vào từ một vùng nhỏ của tầng trước | Dấu vết tái chụp là hiện tượng cục bộ ở mức vài điểm ảnh; không cần kết nối toàn cục |
| **Chia sẻ trọng số** | Cùng một nhân được áp dụng trên toàn bộ ảnh | Dấu vết xuất hiện ở mọi vị trí trên khuôn mặt; học một bộ dò dùng chung là hợp lý và giảm mạnh số tham số |
| **Bất biến tịnh tiến** | Đáp ứng dịch chuyển tương ứng khi đầu vào dịch chuyển | Khuôn mặt có thể nằm ở vị trí hơi khác nhau trong vùng cắt |

### 7.4.3. Một liên hệ lý thuyết quan trọng

Đây là điểm đáng chú ý nhất khi đối chiếu hai nhánh của báo cáo.

Các nhân tích chập ở tầng đầu tiên của một CNN đã huấn luyện, khi được trực quan
hóa, cho thấy chúng hội tụ về các **bộ dò cạnh theo nhiều hướng, bộ dò điểm và
bộ dò đốm màu**. Đối chiếu với mục 5.4.2: đây gần như **chính xác cùng tập
nguyên hàm kết cấu** mà mẫu uniform của LBP mã hóa — spot, edge, corner, line
end.

Hai phương pháp, xuất phát từ hai truyền thống hoàn toàn khác nhau, hội tụ về
cùng một tập nguyên hàm thị giác sơ cấp. Khác biệt cốt lõi nằm ở chỗ khác:

| | LBP | CNN |
|---|---|---|
| Nguyên hàm kết cấu | **Cố định** do con người thiết kế | **Học được** từ dữ liệu |
| Khả năng thích nghi miền | Không — cùng một bộ mô tả cho mọi bài toán | Có — có thể tinh chỉnh cho miền đích |
| Số tầng trừu tượng | Một tầng duy nhất | Nhiều tầng, trường tiếp nhận mở rộng dần |
| Khả năng diễn giải | Cao — biết chính xác nó đo gì | Thấp — cần công cụ quy kết |

Đây là câu trả lời khái niệm cho **RQ1**, và sẽ được đối chiếu với câu trả lời
định lượng ở mục 9.7.

### 7.4.4. Trường tiếp nhận

Trường tiếp nhận của một nơ-ron là vùng ảnh đầu vào ảnh hưởng đến giá trị của
nó. Với các tầng tích chập xếp chồng và các tầng gộp (pooling) xen kẽ, trường
tiếp nhận **mở rộng dần theo độ sâu**. Điều này cho phép mạng đồng thời phát
hiện chi tiết vi mô ở tầng thấp và mẫu hình toàn cục ở tầng cao — chính là cấu
trúc phân cấp mà lập luận mô-đun hóa của [S8] slide 37–40 mô tả.

## 7.5. Chuẩn hóa theo lô

> *Nguồn: Ioffe và Szegedy [5]. Nội dung này không có trong [S8].*

### 7.5.1. Định nghĩa

Với mỗi lô nhỏ $\mathcal{B}$, tầng chuẩn hóa theo lô thực hiện:

$$
\hat{x} = \frac{x - \mu_{\mathcal{B}}}{\sqrt{\sigma_{\mathcal{B}}^{2} + \epsilon}},
\qquad
y = \gamma \hat{x} + \beta \qquad (7.8)
$$

trong đó $\mu_{\mathcal{B}}$ và $\sigma^2_{\mathcal{B}}$ là trung bình và phương
sai tính trên lô, còn $\gamma, \beta$ là tham số học được cho phép mạng khôi
phục lại thang đo nếu cần.

Tác dụng: ổn định phân bố đầu vào của mỗi tầng trong quá trình huấn luyện, cho
phép dùng tốc độ học lớn hơn, và có tác dụng chính quy hóa nhẹ do nhiễu từ việc
ước lượng thống kê trên lô.

### 7.5.2. Vấn đề then chốt trong học chuyển giao

Mục này có tầm quan trọng đặc biệt vì nó ảnh hưởng trực tiếp đến tính đúng đắn
của các thí nghiệm E02, E03 và E04.

Tầng chuẩn hóa theo lô có **hai chế độ hoạt động**:

- **Chế độ huấn luyện:** dùng thống kê của lô hiện tại, đồng thời **cập nhật**
  thống kê chạy (running mean, running variance) bằng trung bình trượt.
- **Chế độ suy luận:** dùng thống kê chạy đã lưu, không cập nhật.

Đây là nguồn của một lỗi tinh vi rất phổ biến. Khi ta "đóng băng" backbone bằng
cách đặt `requires_grad = False` cho các trọng số, các tầng BN **vẫn tiếp tục
cập nhật thống kê chạy** nếu mạng còn ở chế độ huấn luyện. Nghĩa là mô hình
**vẫn thay đổi** qua các epoch dù không có gradient nào được áp dụng — một hành
vi ngoài ý muốn làm cho thí nghiệm "head-only" không thực sự head-only.

Dự án xử lý vấn đề này tường minh. Cấu hình của E04 ghi:

```yaml
training_policy:
  frozen_stages: [stem, layer1, layer2, layer3]
  trainable_stages: [layer4, classifier]
  batch_norm: layer4_trainable_earlier_frozen
```

Nghĩa là chỉ các tầng BN bên trong `layer4` được phép cập nhật; toàn bộ BN của
stem, layer1, layer2, layer3 được giữ ở chế độ suy luận. Với E02 và E03, toàn bộ
BN của backbone được khóa. Đây là điều kiện cần để phép so sánh E03 với E04 thực
sự chỉ khác nhau ở đúng một biến.

## 7.6. Kiến trúc mạng

### 7.6.1. Học phần dư — ResNet18

> *Nguồn: He và cộng sự [7]. Nội dung này không có trong [S8].*

**Vấn đề suy thoái.** Khi tăng độ sâu của mạng tích chập thuần túy vượt quá một
ngưỡng, sai số **trên chính tập huấn luyện** lại tăng lên. Đây không phải khớp
quá mức — khớp quá mức làm tăng sai số kiểm tra chứ không làm tăng sai số huấn
luyện. Đây là vấn đề **khó tối ưu hóa**: mạng quá sâu trở nên khó huấn luyện.

**Giải pháp.** Khối phần dư thay vì học trực tiếp ánh xạ đích $H(\mathbf{x})$ sẽ
học phần dư $F(\mathbf{x}) = H(\mathbf{x}) - \mathbf{x}$:

$$
\mathbf{y} = F(\mathbf{x}, \{W_i\}) + \mathbf{x} \qquad (7.9)
$$

**Vì sao hiệu quả.** Có hai cách giải thích, cả hai đều liên hệ với [S8]:

1. *Về mặt tối ưu hóa:* nếu ánh xạ tối ưu gần với ánh xạ đồng nhất, việc học
   $F \approx 0$ dễ hơn nhiều so với việc học $H \approx \mathbf{x}$ bằng một
   chồng tầng phi tuyến.
2. *Về mặt gradient:* kết nối tắt tạo một đường truyền gradient **trực tiếp** từ
   tầng sau về tầng trước, không qua phép nhân với đạo hàm của các tầng trung
   gian. Điều này giảm nhẹ vấn đề tiêu biến gradient mà [S8] slide 48–50 trình
   bày. Đây là điểm nối trực tiếp giữa nội dung ngoài giáo trình và nội dung
   trong giáo trình.

**Cấu trúc ResNet18:** stem (tích chập 7×7 và gộp cực đại) → layer1 → layer2 →
layer3 → layer4 → gộp trung bình toàn cục → lớp kết nối đầy đủ. Mỗi layer gồm hai
khối BasicBlock. Tổng số tham số của mô hình trong dự án là **11.177.025**.

### 7.6.2. Tích chập tách theo chiều sâu — MobileNetV2

> *Nguồn: Sandler và cộng sự [8]. Nội dung này không có trong [S8].*

**Ý tưởng.** Tách một phép tích chập chuẩn thành hai bước:

1. **Tích chập theo chiều sâu (depthwise):** áp dụng một nhân $D_K \times D_K$
   riêng cho **từng kênh** đầu vào, không trộn kênh.
2. **Tích chập điểm (pointwise):** dùng nhân $1 \times 1$ để trộn thông tin giữa
   các kênh.

**Phân tích chi phí.** Gọi $M$ là số kênh vào, $N$ là số kênh ra, $D_F$ là kích
thước bản đồ đặc trưng. Tỉ lệ chi phí giữa hai cách:

$$
\frac{D_K^{2} \cdot M \cdot D_F^{2} + M \cdot N \cdot D_F^{2}}{D_K^{2} \cdot M \cdot N \cdot D_F^{2}}
= \frac{1}{N} + \frac{1}{D_K^{2}} \qquad (7.10)
$$

Với $D_K = 3$ và $N$ đủ lớn, tỉ lệ này xấp xỉ $1/9$, tức giảm chi phí khoảng
**8 đến 9 lần**.

MobileNetV2 bổ sung hai cải tiến: **phần dư đảo ngược** (inverted residual) đặt
kết nối tắt giữa các tầng nút cổ chai hẹp thay vì giữa các tầng rộng, và **nút
cổ chai tuyến tính** (linear bottleneck) bỏ hàm kích hoạt phi tuyến ở tầng nén
để tránh mất thông tin.

**Tham số trong dự án:** 2.225.153 tham số, checkpoint 9,15 MB — nhỏ hơn
ResNet18 khoảng 4,9 lần.

**Giả thuyết cần kiểm chứng.** Cần đặt ra một cách thận trọng: mô hình có ít
tham số hơn *có thể* thiếu năng lực biểu diễn để mã hóa những dấu vết vi kết cấu
rất tinh vi của tấn công trình diện. Đây là một giả thuyết hợp lý về mặt lý
thuyết nhưng **chưa được chứng minh**, và sẽ được đối chiếu với số liệu ở mục
9.6. Cần tránh khẳng định trước kết quả.

## 7.7. Học chuyển giao

### 7.7.1. Động cơ

Protocol 1 của OULU-NPU chỉ có 1.200 video huấn luyện, tương ứng 12.000 khung
hình. Trong khi đó ResNet18 có hơn 11 triệu tham số. Tỉ lệ tham số trên mẫu như
vậy dẫn tới khớp quá mức gần như chắc chắn nếu huấn luyện từ đầu — chính là hiện
tượng mà [S8] slide 45–46 mô tả.

Học chuyển giao giải quyết bằng cách khởi tạo mạng bằng trọng số đã học trên một
tập dữ liệu lớn hơn nhiều (ImageNet với hơn một triệu ảnh), rồi chỉ điều chỉnh
một phần.

### 7.7.2. Giả thiết nền tảng

Học chuyển giao dựa trên giả thiết về **tính phân tầng của đặc trưng thị giác**:

- Các tầng thấp học đặc trưng **tổng quát**: cạnh, góc, đốm màu, kết cấu cơ bản.
  Những đặc trưng này gần như phổ dụng cho mọi bài toán thị giác.
- Các tầng cao học đặc trưng **chuyên biệt theo tác vụ**: các mẫu hình phức tạp
  gắn với những lớp cụ thể của bài toán nguồn.

### 7.7.3. Ba chiến lược

| Chiến lược | Nội dung | Thí nghiệm | Số tham số học |
|---|---|---|---:|
| **Trích đặc trưng** | Đóng băng toàn bộ backbone, chỉ học lớp phân lớp | E02 | 1.281 |
| | | E03 | 513 |
| **Tinh chỉnh một phần** | Mở khối cuối với tốc độ học nhỏ hơn | **E04** | 8.394.241 |
| **Tinh chỉnh toàn bộ** | Học lại mọi tầng | Không thực hiện | — |

Lý do **không** thực hiện tinh chỉnh toàn bộ: với 12.000 khung hình huấn luyện,
việc mở toàn bộ hơn 11 triệu tham số sẽ đưa bài toán trở lại tình trạng khớp quá
mức mà học chuyển giao vốn nhằm tránh.

### 7.7.4. Khoảng cách miền — luận điểm trung tâm của E04

Đây là lập luận lý thuyết quan trọng nhất của chương, và là cơ sở để thiết kế
thí nghiệm E04.

ImageNet là một tác vụ **ngữ nghĩa**: phân biệt chó với mèo, xe hơi với xe đạp.
Các đặc trưng hữu ích cho tác vụ này là hình dạng, bố cục bộ phận, ngữ cảnh.
Điều đáng chú ý là một mạng huấn luyện trên ImageNet được khuyến khích **bất
biến** với những thay đổi về điều kiện thu nhận: một con mèo chụp bằng máy ảnh
tốt hay máy ảnh kém, in ra giấy hay hiển thị trên màn hình, đều phải được nhận
là mèo.

PAD là một tác vụ **về kết cấu và tần số**, và mục tiêu của nó **ngược lại**:
phát hiện chính xác những khác biệt do điều kiện thu nhận gây ra.

Như vậy tồn tại một **xung đột mục tiêu bất biến** giữa hai tác vụ. Đây là cách
diễn đạt chính xác hơn của nhận định đã nêu ở mục 2.5. Hệ quả suy ra được:

- Các tầng **thấp** vẫn hữu ích, vì bộ dò cạnh và kết cấu cơ bản là chung cho
  mọi bài toán thị giác.
- Các tầng **cao** — nơi tính bất biến với điều kiện thu nhận được xây dựng mạnh
  nhất — chính là nơi hai tác vụ phân kỳ nhiều nhất.

Từ đó rút ra **giả thuyết H3**: khối `layer4`, tầng chuyên biệt nhất của
ResNet18, là khối cần được thích nghi nhất. Thí nghiệm E04 được thiết kế để kiểm
chứng chính xác giả thuyết này.

### 7.7.5. Vì sao hai tốc độ học khác nhau

E04 dùng tốc độ học $10^{-4}$ cho lớp phân lớp và $10^{-5}$ cho `layer4` — chênh
lệch đúng 10 lần. Lý do:

- **Lớp phân lớp** được khởi tạo **ngẫu nhiên**, chưa mang thông tin gì. Nó cần
  tốc độ học lớn để nhanh chóng tìm được vùng tham số hợp lý.
- **Khối `layer4`** đã mang tri thức hữu ích tích lũy từ ImageNet. Một tốc độ
  học lớn sẽ tạo ra những bước cập nhật đủ mạnh để **phá hủy** tri thức đó trong
  vài batch đầu tiên — hiện tượng gọi là **quên thảm khốc** (catastrophic
  forgetting). Tốc độ học nhỏ cho phép điều chỉnh dần dần, giữ lại phần lớn cấu
  trúc đã học trong khi thích nghi với miền mới.

Kỹ thuật này gọi là **tốc độ học phân tầng** (discriminative learning rate) và
là thực hành chuẩn trong học chuyển giao.

## 7.8. Kết luận chương

Chương này đã xây dựng nhánh biểu diễn học được, đi từ nơ-ron đơn lẻ — vốn chính
là một bộ phân lớp tuyến tính tương tự công thức (6.1) — qua lập luận mô-đun hóa
biện minh cho mạng sâu, đến các cơ chế cụ thể của tích chập, chuẩn hóa theo lô,
học phần dư và tích chập tách theo chiều sâu.

Đóng góp lý thuyết chính của chương là phân tích **xung đột mục tiêu bất biến**
giữa ImageNet và PAD, từ đó suy ra giả thuyết rằng khối tích chập cuối cùng là
khối cần thích nghi nhất. Giả thuyết này định hình toàn bộ thiết kế của thí
nghiệm E04.

Chương cũng ghi nhận rõ ràng rằng nội dung về tích chập không thuộc phạm vi bài
giảng của môn học và đã trích dẫn nguồn ngoài tương ứng.

---

# Chương 8. Lý thuyết đánh giá và ra quyết định

Chương này trình bày khối *Class assignment* của sơ đồ [S2] slide 8: cách chuyển
từ điểm số liên tục sang quyết định nhị phân, và cách đo chất lượng của quyết
định đó.

## 8.1. Vì sao độ chính xác không dùng được

### 8.1.1. Lập luận số học

Tập kiểm tra của Protocol 1 gồm 600 video: 480 giả mạo và 120 thật. Xét một "mô
hình" tầm thường luôn trả về `spoof` cho mọi đầu vào:

$$
\text{Accuracy} = \frac{480}{600} = 80\%
$$

Con số 80% nghe có vẻ khả quan. Nhưng mô hình này chặn **100% người dùng hợp
lệ** — nó hoàn toàn vô dụng trong thực tế. Bất kỳ chỉ số nào cho điểm cao với mô
hình này đều không phù hợp làm chỉ số đánh giá.

### 8.1.2. Ma trận nhầm lẫn và quy ước dấu

Với quy ước của dự án — `positive_class: spoof`, `positive_label: 1`,
`live: 0` — ma trận nhầm lẫn được định nghĩa:

| | Dự đoán `live` | Dự đoán `spoof` |
|---|---|---|
| **Thực tế `live`** | TN (đúng) | FP — người thật bị chặn |
| **Thực tế `spoof`** | FN — **tấn công lọt qua** | TP (đúng) |

**Quy ước này phải được nêu tường minh**, vì dấu và ý nghĩa của mọi chỉ số phía
sau đều phụ thuộc vào việc lớp nào được chọn làm lớp dương. Nhiều so sánh giữa
các công trình PAD trở nên vô nghĩa do quy ước khác nhau mà không được nêu rõ.

### 8.1.3. Precision, Recall, F1 và giới hạn của chúng

$$
\text{Precision} = \frac{TP}{TP + FP}, \qquad
\text{Recall} = \frac{TP}{TP + FN} \qquad (8.1)
$$

$$
F_1 = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}} \qquad (8.2)
$$

Chỉ số $F_1$ khắc phục được một phần vấn đề của độ chính xác, nhưng **vẫn chưa
đủ** cho bài toán PAD. Lý do mang tính cấu trúc: cả Precision và Recall đều được
định nghĩa quanh **lớp dương** (`spoof`). Không đại lượng nào trong công thức
(8.1) và (8.2) đo trực tiếp tỉ lệ người dùng thật bị từ chối nhầm.

Số liệu thực nghiệm minh họa điều này một cách rõ ràng: thí nghiệm E01 đạt $F_1$
trên tập kiểm tra là **90,26%** — một con số trông rất tốt — trong khi cùng lúc
đó **72 trong số 120 video thật bị từ chối**, tức tỉ lệ từ chối nhầm 60%. Một hệ
thống xác thực từ chối 60% người dùng hợp lệ là không thể triển khai, nhưng $F_1$
không hề phản ánh điều đó.

Đây là câu trả lời trực tiếp cho **RQ5** và sẽ được nhắc lại ở mục 9.7.

## 8.2. Bộ chỉ số chuẩn ISO/IEC 30107-3

### 8.2.1. Định nghĩa

Tiêu chuẩn ISO/IEC 30107-3 [9] quy định bộ chỉ số dành riêng cho đánh giá PAD,
với đặc điểm then chốt là **tính sai số riêng cho từng lớp**.

**APCER** — tỉ lệ mẫu tấn công bị phân loại nhầm thành mẫu thật:

$$
\text{APCER} = \frac{FN}{TP + FN} \qquad (8.3)
$$

**BPCER** — tỉ lệ mẫu thật bị phân loại nhầm thành tấn công:

$$
\text{BPCER} = \frac{FP}{TN + FP} \qquad (8.4)
$$

**ACER** — trung bình cộng của hai chỉ số trên:

$$
\text{ACER} = \frac{\text{APCER} + \text{BPCER}}{2} \qquad (8.5)
$$

Điểm mấu chốt về mặt toán học: APCER và BPCER có **mẫu số tách riêng** — mỗi chỉ
số được chuẩn hóa theo tổng số mẫu của chính lớp đó. Do đó sự mất cân bằng 80/20
giữa hai lớp **không** ảnh hưởng đến giá trị của chúng. Áp dụng cho mô hình tầm
thường luôn trả `spoof`: APCER = 0% nhưng BPCER = 100%, cho ACER = 50% — đúng
bằng mức đoán ngẫu nhiên, phản ánh chính xác sự vô dụng của mô hình đó.

### 8.2.2. Ý nghĩa an ninh bất đối xứng

Hai loại lỗi có bản chất và hậu quả hoàn toàn khác nhau, và điều này cần được
phân tích bằng văn xuôi chứ không chỉ bằng công thức.

**APCER cao là một lỗ hổng bảo mật.** Mỗi trường hợp APCER là một lần kẻ tấn
công cầm ảnh in của người khác và được hệ thống chấp nhận. Hậu quả có thể là
truy cập trái phép vào tài khoản ngân hàng, vượt qua kiểm soát biên giới, hoặc
mở khóa thiết bị chứa dữ liệu nhạy cảm. Hậu quả **không đối xứng và có thể không
đảo ngược**.

**BPCER cao là một lỗi trải nghiệm.** Mỗi trường hợp BPCER là một lần người dùng
hợp lệ bị từ chối. Hậu quả là phiền toái, mất thời gian, phải thử lại hoặc dùng
phương thức xác thực dự phòng. Khó chịu, nhưng thường có thể khắc phục.

Từ đó suy ra rằng **trọng số tương đối giữa hai loại lỗi phụ thuộc vào ứng
dụng**:

| Ứng dụng | Loại lỗi nghiêm trọng hơn | Lý do |
|---|---|---|
| Xác thực giao dịch tài chính | APCER | Thiệt hại tài chính không đảo ngược |
| Kiểm soát ra vào khu vực an ninh | APCER | Rủi ro an ninh vật lý |
| Mở khóa điện thoại cá nhân | BPCER | Người dùng thao tác hàng chục lần mỗi ngày |
| Điểm danh tự động | BPCER | Sai sót gây phiền toái hành chính |

Chỉ số ACER lấy **trung bình cộng** của hai đại lượng, tức ngầm giả định chúng
**quan trọng như nhau**. Đây là một giả định cần được nêu tường minh chứ không
nhận mặc định. Trong triển khai thực tế, điểm vận hành cuối cùng phải được chọn
dựa trên phân tích chi phí nghiệp vụ cụ thể, không nhất thiết là điểm cực tiểu
ACER.

### 8.2.3. Đường ROC, DET và EER

[HFR] Chương 21 (trang 551–574) trình bày các phương pháp đánh giá tổng quát
trong nhận dạng khuôn mặt, bao gồm:

- **Đường ROC** — biểu diễn quan hệ giữa tỉ lệ dương tính thật và tỉ lệ dương
  tính giả khi ngưỡng thay đổi.
- **Đường DET** — biến thể vẽ hai loại sai số trên thang lệch chuẩn, làm rõ hơn
  vùng sai số thấp.
- **EER** — điểm mà tại đó APCER bằng BPCER.

Ưu điểm của EER là nó không phụ thuộc vào việc chọn ngưỡng, nên tiện cho việc so
sánh giữa các hệ thống. Nhược điểm là nó chỉ mô tả **một điểm duy nhất** trên
đường cong và có thể không phải điểm vận hành thực tế.

Dự án sử dụng ngưỡng dev-EER làm **chính sách phụ** để tương thích với quy ước
báo cáo của OULU-NPU, bên cạnh chính sách chính là cực tiểu ACER. Việc có hai
chính sách cho phép kiểm tra tính bền vững của thứ hạng giữa các mô hình.

## 8.3. Chọn ngưỡng quyết định

### 8.3.1. Từ điểm số liên tục sang quyết định nhị phân

Cả hai họ mô hình đều sinh ra một **điểm số vô hướng liên tục**:

- E01: `decision_function` của SVM — khoảng cách có dấu tới siêu phẳng, theo
  công thức (6.2).
- E02–E04: logit trước hàm sigmoid.

Quyết định nhị phân đòi hỏi một ngưỡng $\tau$:

$$
\hat{y} =
\begin{cases}
1 \;(\text{spoof}) & \text{nếu } s \geq \tau \\
0 \;(\text{live}) & \text{nếu } s < \tau
\end{cases} \qquad (8.6)
$$

Cần nhấn mạnh: việc chọn $\tau$ **không** là một chi tiết kỹ thuật phụ. Cùng một
mô hình với hai ngưỡng khác nhau cho hai hệ thống có đặc tính an ninh hoàn toàn
khác nhau. Ngưỡng chính là điểm vận hành.

### 8.3.2. Nguyên tắc bất khả xâm phạm

**Ngưỡng chỉ được chọn trên tập phát triển, không bao giờ trên tập kiểm tra.**

Nếu chọn ngưỡng trên tập kiểm tra, ta đang tối ưu hóa một tham số bằng chính dữ
liệu dùng để đo hiệu năng. Kết quả thu được sẽ lạc quan một cách có hệ thống và
không phản ánh hiệu năng trên dữ liệu chưa từng thấy. Cấu hình khóa nguyên tắc
này bằng `test_used_for_selection: false`.

### 8.3.3. Mục tiêu và quy tắc phá hòa

Chính sách chính của dự án là cực tiểu ACER trên tập phát triển. Tuy nhiên, do
điểm số là rời rạc theo mẫu, nhiều giá trị ngưỡng khác nhau có thể cho **cùng
một** giá trị ACER. Khi đó cần một quy tắc phá hòa **tất định** để bảo đảm chạy
lại cho cùng kết quả. Cấu hình quy định thứ tự ưu tiên:

```yaml
threshold_objective: [acer, apcer, threshold]
```

Nghĩa là: ưu tiên ACER nhỏ nhất; nếu hòa, chọn APCER nhỏ nhất (thiên về an
ninh); nếu vẫn hòa, chọn giá trị ngưỡng nhỏ nhất. Việc quy định rõ quy tắc phá
hòa là một chi tiết nhỏ nhưng cần thiết cho khả năng tái lập.

### 8.3.4. Ngưỡng cấp khung hình và cấp video

Dự án chọn **hai ngưỡng độc lập**: một cho quyết định ở cấp khung hình
(`select_on_dev_frames`) và một cho quyết định ở cấp video
(`select_on_dev_videos`). Lý do là phân bố của điểm số khung hình và phân bố của
điểm số video đã gộp là hai phân bố khác nhau — phép trung bình làm thay đổi cả
vị trí lẫn độ phân tán. Dùng chung một ngưỡng cho cả hai cấp sẽ là một sai sót
về mặt thống kê.

**Ngưỡng thực tế đã chọn:**

| Thí nghiệm | Ngưỡng cấp khung hình | Ngưỡng cấp video |
|---|---:|---:|
| E01 LBP-SVM | $-0{,}3049388$ | $-0{,}4000959$ |
| E02 MobileNetV2 | — | $0{,}5125712$ |
| E03 ResNet18 head-only | — | $0{,}5859636$ |
| E04 ResNet18 `layer4` | — | $0{,}1310235$ |

Hai nhận xét cần thiết. Thứ nhất, ngưỡng âm của E01 hoàn toàn hợp lệ vì
`decision_function` trả về khoảng cách có dấu, không phải xác suất. Thứ hai,
ngưỡng của E04 ($0{,}1310235$) thấp hơn đáng kể so với E03 ($0{,}5859636$),
nhưng **không được diễn giải rằng E04 "kém tự tin hơn"**. Quá trình tinh chỉnh
làm thay đổi thang hiệu chỉnh (calibration) của logit, nên giá trị tuyệt đối của
ngưỡng giữa hai mô hình khác nhau không so sánh trực tiếp được. Chất lượng phải
được đánh giá tại điểm vận hành, thông qua các chỉ số sai số.

**Nối với triển khai:** `evaluation/threshold.py`; kết quả lưu tại
`threshold.json` trong mỗi thư mục chạy.

## 8.4. Gộp điểm số theo video

### 8.4.1. Phép gộp

Mỗi video được đại diện bởi $N = 10$ khung hình. Điểm số cấp video là trung bình
cộng:

$$
s_{\text{video}} = \frac{1}{N}\sum_{k=1}^{N} s_k \qquad (8.7)
$$

### 8.4.2. Cơ sở lý thuyết

Giả sử điểm số của khung hình thứ $k$ trong video $v$ có dạng:

$$
s_{v,k} = \mu_v + \epsilon_{v,k} \qquad (8.8)
$$

trong đó $\mu_v$ là "điểm số thật" của video và $\epsilon_{v,k}$ là nhiễu. Nếu
các nhiễu **độc lập** và có **kỳ vọng bằng không** với phương sai $\sigma^2$,
thì:

$$
\operatorname{Var}\left( \frac{1}{N}\sum_{k=1}^{N} s_{v,k} \right) = \frac{\sigma^{2}}{N} \qquad (8.9)
$$

Phương sai giảm đúng $N$ lần. Đây là lập luận chuẩn ủng hộ việc lấy trung bình.

### 8.4.3. Vì sao giả thiết có thể sai — phân tích quan trọng

Lập luận trên phụ thuộc vào hai giả thiết, và **cả hai đều đáng ngờ** trong bối
cảnh này.

**Giả thiết độc lập bị vi phạm.** Mười khung hình của cùng một video được thu
bằng **cùng một camera**, trong **cùng một điều kiện chiếu sáng**, với **cùng
một công cụ tấn công**, cách nhau chỉ vài giây. Chúng có tương quan rất mạnh.
Khi các mẫu tương quan với hệ số $\rho$, phương sai của trung bình trở thành:

$$
\operatorname{Var}\left( \bar{s} \right) = \frac{\sigma^{2}}{N}\big[1 + (N-1)\rho\big] \qquad (8.10)
$$

Với $\rho$ gần 1, hệ số giảm phương sai gần như biến mất hoàn toàn.

**Giả thiết kỳ vọng bằng không cũng có thể sai.** Nếu mô hình có **thiên lệch có
hệ thống** trên một video cụ thể — chẳng hạn video được thu bằng một mẫu điện
thoại mà mô hình xử lý kém — thì mô hình đúng hơn là:

$$
s_{v,k} = \mu_v + b_v + \epsilon_{v,k} \qquad (8.11)
$$

trong đó $b_v$ là thiên lệch **chung cho mọi khung hình** của video $v$. Lấy
trung bình **không hề khử được $b_v$**:

$$
\frac{1}{N}\sum_{k=1}^{N} s_{v,k} = \mu_v + b_v + \frac{1}{N}\sum_{k=1}^{N}\epsilon_{v,k} \;\longrightarrow\; \mu_v + b_v \qquad (8.12)
$$

Trung bình hóa chỉ khử được thành phần nhiễu ngẫu nhiên; nó **làm mượt chứ không
sửa** thiên lệch hệ thống.

Đây là cơ sở lý thuyết để dự đoán rằng phép gộp trung bình **không nhất thiết
luôn cải thiện kết quả** — và số liệu ở mục 9.5 sẽ xác nhận dự đoán này. Đây là
câu trả lời cho **RQ4**.

### 8.4.4. Các phương án gộp khác

| Phương pháp | Ưu điểm | Nhược điểm |
|---|---|---|
| Trung bình cộng | Đơn giản, hiệu quả khi nhiễu độc lập | Nhạy với giá trị ngoại lai; không khử thiên lệch |
| Trung vị | Bền vững với ngoại lai | Bỏ qua thông tin về độ lớn |
| Cực đại | Rất thiên về an ninh — một khung hình đáng ngờ là đủ | Tăng mạnh BPCER |
| Bỏ phiếu đa số | Bền vững | Mất thông tin điểm số liên tục |
| Trọng số theo chất lượng | Ưu tiên khung hình rõ nét | Cần một mô hình đánh giá chất lượng riêng |
| Gộp có học (attention) | Tối ưu theo dữ liệu | Thêm tham số, cần thêm dữ liệu |

Việc so sánh các phương án này phải được thực hiện trên tập phát triển hoặc trên
một protocol độc lập, **không** được tinh chỉnh bằng tập kiểm tra hiện tại.

**Nối với triển khai:** `evaluation/aggregation.py`, cấu hình
`aggregation: mean_decision_score`.

## 8.5. Chống rò rỉ dữ liệu

Tính hợp lệ của mọi con số trong Chương 9 phụ thuộc vào việc không có rò rỉ
thông tin từ tập kiểm tra vào quá trình xây dựng mô hình. Dự án áp dụng bảy cơ
chế, mỗi cơ chế nhằm chặn một đường rò rỉ cụ thể:

| Cơ chế | Đường rò rỉ bị chặn |
|---|---|
| Tách tập theo **định danh chủ thể** (`require_disjoint_subjects`) | Nếu cùng một người xuất hiện ở cả tập huấn luyện và tập kiểm tra, mô hình có thể nhận ra *người* thay vì nhận ra *dấu vết giả mạo* |
| Tách tập theo **định danh video** (`require_disjoint_video_ids`) | Các khung hình của cùng một video rơi vào hai tập khác nhau sẽ khiến hiệu năng bị thổi phồng nghiêm trọng |
| Ước lượng $\mu, \sigma$ **chỉ trên tập huấn luyện** | Thống kê của tập kiểm tra ảnh hưởng ngược lên phép biến đổi dữ liệu |
| Chọn $C$, epoch, ngưỡng **chỉ trên tập phát triển** | Tối ưu siêu tham số bằng chính dữ liệu dùng để đo |
| **Ghi dấu đóng băng** trước khi dựng tập kiểm tra | Bảo đảm về mặt thủ tục rằng không có điều chỉnh nào sau khi nhìn thấy tập kiểm tra |
| Dữ liệu thô **bất biến** (`raw_data_immutable: true`) | Ngăn việc vô tình sửa đổi dữ liệu gốc giữa các lần chạy |
| Cố định hạt giống, lưu `environment.json` và `run_manifest.json` | Cho phép tái lập và kiểm tra độc lập |

Ngoài ra, dự án đã chạy hai lần kiểm tra khói (smoke run) cho nhánh CNN và xác
nhận rằng các artifact sinh ra ổn định ở mức từng byte; bộ kiểm thử của dự án
hiện có 100 test đều đạt.

## 8.6. Kết luận chương

Chương này đã thiết lập nền tảng đánh giá gồm bốn thành phần. Thứ nhất, chứng
minh bằng lập luận số học rằng độ chính xác và cả $F_1$ đều không phù hợp với
bài toán PAD trên dữ liệu lệch lớp. Thứ hai, giới thiệu bộ chỉ số APCER, BPCER,
ACER với tính chất mẫu số tách riêng, và phân tích ý nghĩa an ninh bất đối xứng
của hai loại lỗi. Thứ ba, thiết lập quy trình chọn ngưỡng có kỷ luật với nguyên
tắc tuyệt đối không chạm vào tập kiểm tra. Thứ tư, phân tích cơ sở lý thuyết và
**giới hạn** của phép gộp trung bình theo video, dẫn tới một dự đoán có thể kiểm
chứng về RQ4.

Đến đây toàn bộ khung lý thuyết đã hoàn chỉnh. Chương tiếp theo trình bày kết
quả thực nghiệm và đối chiếu chúng với từng khối lý thuyết đã xây dựng.
---

# Chương 9. Thực nghiệm, kết quả và thảo luận

Toàn bộ số liệu trong chương này được đọc trực tiếp từ thư mục
`artifacts/runs/`. Không có con số nào được ước lượng hoặc làm tròn thủ công.

## 9.1. Bộ dữ liệu và protocol

### 9.1.1. OULU-NPU

OULU-NPU [10] là cơ sở dữ liệu phát hiện giả mạo khuôn mặt trên thiết bị di
động, gồm 5.940 video của 55 chủ thể, thu trong ba môi trường khác nhau bằng sáu
điện thoại. Các mẫu tấn công được tạo bằng hai máy in và hai màn hình hiển thị.

Bộ dữ liệu định nghĩa bốn protocol nhằm khảo sát các nguồn biến thiên khác nhau.
Dự án chỉ sử dụng **Protocol 1** — protocol khảo sát khả năng tổng quát hóa theo
**môi trường thu nhận**, trong đó tập huấn luyện và tập kiểm tra được thu ở các
phiên khác nhau.

### 9.1.2. Phân bố dữ liệu đã xác minh

| Tập | Video thật | Video giả | Tổng video | Khung hình mục tiêu |
|---|---:|---:|---:|---:|
| Huấn luyện (train) | 240 | 960 | 1.200 | 12.000 |
| Phát triển (dev) | 180 | 720 | 900 | 9.000 |
| Kiểm tra (test) | 120 | 480 | 600 | 6.000 |
| **Tổng** | **540** | **2.160** | **2.700** | **27.000** |

Tỉ lệ live : spoof là 1 : 4 ở cả ba tập — đây là nguồn gốc của vấn đề mất cân
bằng lớp đã phân tích ở mục 6.6 và mục 8.1.

### 9.1.3. Chất lượng tiền xử lý

Số vùng cắt khuôn mặt giải mã hợp lệ là **26.999 trên 27.000**, tương ứng tỉ lệ
phát hiện **99,9963%**. Đúng một khung hình đầu tiên ở tập phát triển không phát
hiện được khuôn mặt và được giữ nguyên trạng thái `no_face`, **không** được thay
thế bằng một khung hình khác chọn theo nhãn.

Đây là lý do tập phát triển có **8.999** khung hình thay vì 9.000 như con số lý
thuyết. Sai lệch một khung hình này được ghi nhận minh bạch thay vì làm tròn,
theo đúng nguyên tắc đã nêu ở mục 4.3.4: mọi cách xử lý khung hình thất bại mà
phụ thuộc vào nhãn đều tạo ra rò rỉ.

## 9.2. Pipeline tổng thể

```text
                    Video OULU-NPU Protocol 1
                              │
                              ▼
              Lấy đều 10 khung hình mỗi video        ← Mục 4.2
                              │
                              ▼
                  MediaPipe phát hiện mặt            ← Mục 4.3
                              │
                              ▼
          Cắt vuông + nới biên 20% → PNG 256×256     ← Mục 4.4
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
    Xám 128×128 (area)              RGB 224×224 (bilinear)   ← Mục 4.5
              │                               │
              ▼                               ▼
     LBP riu2 8×8 → 640-D            Chuẩn hóa ImageNet      ← Mục 5.5 / 4.6
              │                               │
              ▼                               ▼
        StandardScaler                  CNN một logit         ← Mục 4.6 / 7.2
              │                               │
              ▼                               ▼
          LinearSVC (E01)          MobileNetV2 / ResNet18     ← Mục 6.4 / 7.6
              │                          (E02, E03, E04)
              └───────────────┬───────────────┘
                              ▼
                  Điểm số từng khung hình
                              │
                              ▼
          Trung bình điểm số theo video                ← Mục 8.4
                              │
                              ▼
        Ngưỡng khóa từ tập phát triển                  ← Mục 8.3
                              │
                              ▼
              APCER / BPCER / ACER trên test           ← Mục 8.2
```

Pipeline tách ba lớp trách nhiệm — dữ liệu, biểu diễn và mô hình, đánh giá —
đúng theo sơ đồ lý thuyết [S2] slide 8 đã ánh xạ ở mục 3.3. Sự tách biệt này bảo
đảm không thí nghiệm nào được hưởng một quy trình tiền xử lý hay bộ đánh giá
thuận lợi riêng.

## 9.3. Bảng truy vết lý thuyết – triển khai

Đây là bảng trung tâm của báo cáo, trả lời trực tiếp câu hỏi *"trong thực nghiệm
đã ứng dụng lý thuyết nào để xử lý bài toán?"*.

| Lý thuyết | Mục | Tham số thực tế | Vị trí mã nguồn | Vai trò trong PAD |
|---|---|---|---|---|
| Lấy mẫu tín hiệu rời rạc | 4.2 | 10 khung/video, đều, tất định, có hai đầu | `data/frame_sampler.py` | Phủ trục thời gian, giảm chi phí |
| Chuyển đổi không gian màu | 4.1 | BT.601 cho E01; BGR→RGB cho detector/CNN | `data/preprocess.py`, `features/cache.py` | Đúng quy ước kênh; LBP tập trung kết cấu |
| Phát hiện đối tượng | 4.3 | MediaPipe, confidence 0,5, max side 640 | `data/preprocess.py` | Loại nền, giữ vùng khuôn mặt |
| Chuẩn hóa hình học ROI | 4.4 | Cắt vuông, margin 0,2, đầu ra 256, PNG | `data/preprocess.py` | Đầu vào đồng nhất, giữ manh mối quanh mặt |
| Nội suy vùng | 4.5 | `area`, 256→128 | `features/cache.py` | Chống răng cưa khi thu nhỏ mạnh |
| Nội suy song tuyến + antialias | 4.5 | `bilinear`, 256→224 | `data/cnn_dataset.py` | Khớp quy ước tiền xử lý ImageNet |
| Chuẩn hóa cường độ | 4.6 | mean/std ImageNet | `data/cnn_dataset.py` | Đưa đầu vào về vùng làm việc của BN |
| Chuẩn hóa z-score | 4.6 | Khớp scaler chỉ trên train | `models/lbp_svm.py` | Đồng nhất thang đo cho chính quy hóa $L_2$ |
| LBP uniform bất biến quay | 5.2–5.4 | $P=8$, $R=1$, 10 bin | `features/lbp.py` | Mã hóa vi kết cấu in/màn hình |
| Histogram không gian $L_1$ | 5.5 | Lưới 8×8 → 640 chiều, chuẩn hóa từng ô | `features/lbp.py` | Giữ thông tin vị trí của vi mẫu |
| Biên cực đại | 6.2–6.3 | `LinearSVC`, `l2`, `squared_hinge` | `models/lbp_svm.py` | Phân lớp vector kết cấu 640 chiều |
| Chính quy hóa qua tham số $C$ | 6.4 | Lưới 6 giá trị, chọn $C = 10^{-4}$ | `selection/c_search.csv` | Kiểm soát khớp quá mức |
| Cân bằng trọng số lớp | 6.6 | `class_weight: balanced` | `models/lbp_svm.py` | Cân đóng góp live/spoof khi học |
| Tích chập | 7.4 | MobileNetV2 / ResNet18 tiền huấn luyện | `models/mobilenet_v2.py`, `models/resnet18.py` | Học biểu diễn không gian phân cấp |
| Tích chập tách theo chiều sâu | 7.6.2 | Backbone MobileNetV2 | `models/mobilenet_v2.py` | Giảm tham số và dung lượng |
| Học phần dư | 7.6.1 | BasicBlock của ResNet18 | `models/resnet18.py` | Tối ưu mạng sâu, giảm tiêu biến gradient |
| Chuẩn hóa theo lô | 7.5 | BN khóa ở E02/E03; chỉ BN `layer4` mở ở E04 | training runners | Kiểm soát thống kê chạy khi chuyển giao |
| Học chuyển giao | 7.7 | Trọng số ImageNet; head-only và `layer4` | `configs/models/*.yaml` | Tận dụng đặc trưng chung, thích nghi miền |
| Bất biến qua tăng cường dữ liệu | 7.3.5 | Lật ngang $p = 0{,}5$, chỉ trên train | `data/cnn_dataset.py` | Tăng dữ liệu mà bảo toàn nhãn |
| Rủi ro kinh nghiệm có trọng số | 7.2 | BCE một logit, `pos_weight = 0,25` | training runners | Cân tổng đóng góp hai lớp |
| Tốc độ học phân tầng | 7.7.5 | `layer4`: $10^{-5}$; head: $10^{-4}$ | `configs/.../e04*.yaml` | Hạn chế quên thảm khốc |
| Gộp bằng chứng nhiều mẫu | 8.4 | Trung bình điểm số theo video | `evaluation/aggregation.py` | Kết hợp thông tin theo thời gian |
| Lý thuyết quyết định | 8.3 | Ngưỡng cực tiểu ACER, khóa từ dev | `evaluation/threshold.py` | Chuyển điểm số thành quyết định |
| Đánh giá PAD chuẩn hóa | 8.2 | APCER, BPCER, ACER, chính sách EER phụ | `evaluation/metrics.py`, `oulu_official.py` | Tách lỗi an ninh và lỗi tiện dụng |

## 9.4. Cấu hình bốn thí nghiệm

### 9.4.1. E01 — LBP kết hợp SVM tuyến tính

Chuỗi xử lý:

1. Đọc vùng cắt PNG trực tiếp ở chế độ ảnh xám.
2. Thu nhỏ về $128 \times 128$ bằng nội suy vùng.
3. Tính $\text{LBP}^{riu2}_{8,1}$ với xử lý biên bằng nhân bản mép.
4. Chia lưới $8 \times 8$, lập histogram 10 bin mỗi ô, chuẩn hóa $L_1$.
5. Nối thành vector 640 chiều.
6. Khớp `StandardScaler` trên 12.000 khung hình huấn luyện.
7. Khớp `LinearSVC`, chọn $C$ trên tập phát triển.
8. Lấy trung bình điểm số mỗi video, áp ngưỡng đã chọn từ tập phát triển.

Kết quả chọn: $C = 10^{-4}$; ngưỡng cấp khung hình $-0{,}3049388$; ngưỡng cấp
video $-0{,}4000959$.

Thư mục chạy: `artifacts/runs/lbp_svm/e01_20260712_lbp_svm_seed42_verified/`.

### 9.4.2. E02 — MobileNetV2 chỉ học lớp phân lớp

Đầu vào RGB $224 \times 224$, chuẩn hóa ImageNet, lật ngang $p = 0{,}5$ chỉ trên
tập huấn luyện. Backbone MobileNetV2 với trọng số ImageNet V2, toàn bộ trọng số
và tầng BN bị khóa. Lớp phân lớp cuối xuất một logit.

Chỉ **1.281 trên 2.225.153** tham số được cập nhật, tương đương 0,058%.

Huấn luyện: lô 16, Adam, tốc độ học $10^{-4}$, suy giảm trọng số $10^{-4}$, BCE
có trọng số với $w_+ = 0{,}25$, tối đa 15 epoch, tối thiểu 3 epoch, kiên nhẫn 3,
hạt giống 42. Checkpoint được xếp hạng theo bộ ba `(ACER, APCER, -F1, epoch)`
trên video của tập phát triển; epoch 15 được chọn. Ngưỡng cấp video
$0{,}5125712$.

Thư mục chạy: `artifacts/runs/mobilenet_v2/e02_20260712_mobilenet_v2_seed42/`.

### 9.4.3. E03 — ResNet18 chỉ học lớp phân lớp

E03 giữ **nguyên vẹn** toàn bộ phép biến đổi, hàm mất mát, thuật toán tối ưu,
chính sách chọn checkpoint và bộ đánh giá của E02; biến duy nhất thay đổi là
backbone, chuyển sang ResNet18 với trọng số ImageNet V1.

Lớp kết nối đầy đủ mới có **513** tham số; toàn bộ backbone và BN bị khóa. Tổng
mô hình có **11.177.025** tham số. Epoch 15 được chọn; ngưỡng cấp video
$0{,}5859636$.

Thư mục chạy: `artifacts/runs/resnet18/e03_20260713_resnet18_seed42/`.

Cần lưu ý về phạm vi diễn giải: so sánh E02 với E03 khảo sát ảnh hưởng của
**kiến trúc tiền huấn luyện trong chế độ bộ trích đặc trưng cố định**. Nó
**không** phải một so sánh đầy đủ về năng lực tinh chỉnh của hai kiến trúc, vì
cả hai backbone đều bị khóa hoàn toàn.

### 9.4.4. E04 — ResNet18 tinh chỉnh `layer4`

E04 là thí nghiệm loại trừ trực tiếp của E03. Mọi yếu tố được giữ nguyên tuyệt
đối, ngoại trừ bốn thay đổi liên quan đến đúng một biến:

- Khối `layer4` và các tầng BN bên trong nó được mở.
- `layer4` dùng tốc độ học $10^{-5}$.
- Lớp phân lớp dùng tốc độ học $10^{-4}$.
- **8.394.241** tham số được học thay vì 513.

Các giai đoạn stem, layer1, layer2, layer3 vẫn bị khóa và giữ ở chế độ suy luận
— bảo đảm đúng nguyên tắc đã phân tích ở mục 7.5.2.

Epoch 6 là checkpoint tốt nhất; dừng sớm kích hoạt sau epoch 9. Ngưỡng cấp video
$0{,}1310235$.

Thư mục chạy:
`artifacts/runs/resnet18_finetune/e04_20260714_resnet18_finetune_layer4_seed42/`.

### 9.4.5. Các biến được kiểm soát

| Thành phần | Giá trị giữ cố định cho mọi thí nghiệm |
|---|---|
| Protocol | OULU-NPU Protocol 1 chính thức |
| Quy ước nhãn | `live = 0`, `spoof = 1` |
| Lấy mẫu | 10 khung hình mỗi video, cùng chỉ số |
| Vùng cắt mặt | MediaPipe, margin 0,2, đầu ra 256 |
| Đầu vào CNN | RGB 224, chuẩn hóa ImageNet |
| Tăng cường dữ liệu CNN | Lật ngang 0,5, chỉ trên tập huấn luyện |
| Hàm mất mát / lô / hạt giống CNN | BCE có trọng số / 16 / 42 |
| Gộp theo video | Trung bình điểm số |
| Chọn ngưỡng | Cực tiểu ACER trên dev, phá hòa theo APCER rồi ngưỡng |
| Tập kiểm tra | Chỉ đánh giá sau khi mô hình và ngưỡng đã khóa |

Biến độc lập là **biểu diễn/kiến trúc** ở E01–E03, và **phạm vi tinh chỉnh** ở
cặp E03/E04.

## 9.5. Kết quả thực nghiệm

### 9.5.1. Kết quả đầy đủ ở cấp video

Mọi giá trị tính bằng phần trăm. Mỗi mô hình dùng ngưỡng riêng đã chọn trên tập
phát triển; không ngưỡng nào được chọn lại bằng tập kiểm tra.

| Mô hình | Tập | Accuracy | Precision | Recall | F1 | APCER | BPCER | **ACER** |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| E01 LBP-SVM | Dev | 89,11 | 96,98 | 89,17 | 92,91 | 10,83 | 11,11 | **10,97** |
| E02 MobileNetV2 | Dev | 83,00 | 97,49 | 80,83 | 88,38 | 19,17 | 8,33 | **13,75** |
| E03 ResNet18 head | Dev | 86,44 | 96,57 | 86,11 | 91,04 | 13,89 | 12,22 | **13,06** |
| E04 ResNet18 `layer4` | Dev | 98,22 | 99,03 | 98,75 | 98,89 | 1,25 | 3,89 | **2,57** |
| E01 LBP-SVM | Test | 83,67 | 86,31 | 94,58 | 90,26 | 5,42 | 60,00 | **32,71** |
| E02 MobileNetV2 | Test | 78,33 | 91,27 | 80,63 | 85,62 | 19,38 | 30,83 | **25,10** |
| E03 ResNet18 head | Test | 78,33 | 92,07 | 79,79 | 85,49 | 20,21 | 27,50 | **23,85** |
| E04 ResNet18 `layer4` | Test | **90,83** | **94,00** | **94,58** | **94,29** | **5,42** | **24,17** | **14,79** |

Ba quan sát nổi bật:

1. **E01 tốt nhất trên tập phát triển nhưng kém nhất trên tập kiểm tra** trong
   ba đường cơ sở đầu — một sự đảo ngược thứ hạng hoàn toàn.
2. **E04 tốt nhất trên mọi chỉ số kiểm tra**, ngoại trừ APCER bằng đúng E01
   (cùng 5,42%).
3. **E01 có F1 = 90,26% trong khi BPCER = 60,00%** — minh chứng số cụ thể cho
   lập luận lý thuyết ở mục 8.1.3.

### 9.5.2. Ma trận nhầm lẫn trên video kiểm tra

| Mô hình | TN | FP | FN | TP | Tổng lỗi |
|---|---:|---:|---:|---:|---:|
| E01 LBP-SVM | 48 | 72 | 26 | 454 | 98 |
| E02 MobileNetV2 | 83 | 37 | 93 | 387 | 130 |
| E03 ResNet18 head | 87 | 33 | 97 | 383 | 130 |
| E04 ResNet18 `layer4` | 91 | 29 | 26 | 454 | **55** |

Bảng này làm rõ bản chất khác nhau của các lỗi. E01 chỉ bỏ lọt 26 tấn công —
ngang với E04 — nhưng chặn nhầm 72 trên 120 người dùng thật. E04 giảm số âm tính
giả từ 97 xuống 26 so với E03, đồng thời giảm nhẹ số dương tính giả từ 33 xuống
29. Phần lớn cải thiện của E04 đến từ việc **giảm số tấn công bị bỏ lọt**.

### 9.5.3. Thí nghiệm loại trừ về phạm vi tinh chỉnh

| Chỉ số | E03 head-only | E04 `layer4` + head | Chênh lệch |
|---|---:|---:|---:|
| Tham số được học | 513 | 8.394.241 | $+8.393.728$ |
| Dev ACER | 13,06% | **2,57%** | $-10{,}49$ điểm % |
| Test F1 | 85,49% | **94,29%** | $+8{,}80$ điểm % |
| Test APCER | 20,21% | **5,42%** | $-14{,}79$ điểm % |
| Test BPCER | 27,50% | **24,17%** | $-3{,}33$ điểm % |
| **Test ACER** | 23,85% | **14,79%** | $\mathbf{-9{,}06}$ **điểm %** |

Đây là phép so sánh có sức giải thích cao nhất trong toàn bộ báo cáo, vì E03 và
E04 dùng **cùng kiến trúc suy luận, cùng trọng số khởi tạo, cùng dữ liệu, cùng
phép biến đổi, cùng hàm mất mát, cùng cách gộp và cùng bộ đánh giá**. Biến thay
đổi duy nhất là quyền cập nhật `layer4` cùng các tầng BN của nó, và tốc độ học
phân tầng đi kèm.

Kết quả ủng hộ giả thuyết H3 đã phát biểu ở mục 7.7.4. Tuy nhiên cần diễn đạt
chính xác phạm vi kết luận: kết quả này **chưa chứng minh** rằng `layer4` đã học
được chính xác dấu vết vật lý nào. Để khẳng định mô hình "nhìn thấy vân moiré"
hay "phát hiện thiếu bóng đổ 3D", cần thêm phân tích quy kết (Grad-CAM,
attribution) và thí nghiệm can thiệp có kiểm soát. Cách diễn đạt đúng là: kết
quả **nhất quán với** giả thuyết về việc học đặc trưng chuyên biệt cho PAD.

### 9.5.4. Khoảng cách giữa tập phát triển và tập kiểm tra

| Mô hình | Dev ACER | Test ACER | Chênh lệch |
|---|---:|---:|---:|
| E01 LBP-SVM | 10,97% | 32,71% | $+21{,}74$ điểm % |
| E02 MobileNetV2 | 13,75% | 25,10% | $+11{,}35$ điểm % |
| E03 ResNet18 head | 13,06% | 23,85% | $+10{,}80$ điểm % |
| E04 ResNet18 `layer4` | 2,57% | 14,79% | $+12{,}22$ điểm % |

Bảng này quan trọng hơn bảng kết quả tuyệt đối về mặt chẩn đoán. E01 có khoảng
cách lớn gần gấp đôi các mô hình CNN — bằng chứng định lượng cho việc biểu diễn
kết cấu cố định nhạy cảm với dịch chuyển miền.

Đáng chú ý là **E04 vẫn còn khoảng cách 12,22 điểm** dù đạt Dev ACER rất thấp
2,57%. Điều này cảnh báo rằng kết quả xuất sắc trên tập phát triển **không** đồng
nghĩa bài toán đã được giải quyết; một phần cải thiện có thể là do mô hình đã
khớp mạnh với đặc thù của tập phát triển.

### 9.5.5. Cấp khung hình so với cấp video

| Mô hình | Test frame ACER | Test video ACER | Chênh lệch |
|---|---:|---:|---:|
| E01 LBP-SVM | 30,58% | 32,71% | $+2{,}13$ điểm % |
| E02 MobileNetV2 | 25,69% | 25,10% | $-0{,}58$ điểm % |
| E03 ResNet18 head | 24,03% | 23,85% | $-0{,}18$ điểm % |
| E04 ResNet18 `layer4` | **13,41%** | 14,79% | $+1{,}39$ điểm % |

Phép gộp trung bình chỉ cải thiện **nhẹ** cho E02 và E03, và làm **xấu đi** kết
quả của E01 và E04. Với E04, việc gộp làm giảm APCER từ 6,31% xuống 5,42% nhưng
lại làm tăng BPCER từ 20,50% lên 24,17%; tổng hợp lại ACER tăng.

Kết quả này **bác bỏ phiên bản mạnh** của giả thuyết H4 rằng lấy trung bình luôn
tốt hơn — đúng như dự đoán lý thuyết ở mục 8.4.3.

### 9.5.6. Kết quả theo chính sách phụ

Khi dùng ngưỡng dev-EER và lấy trường hợp xấu nhất giữa hai loại tấn công (in và
phát lại):

| Mô hình | Test ACER trường hợp xấu nhất |
|---|---:|
| E01 LBP-SVM | 33,75% |
| E02 MobileNetV2 | 26,25% |
| E03 ResNet18 head | 23,13% |
| E04 ResNet18 `layer4` | **11,46%** |

Thứ hạng **không thay đổi** so với chính sách chính. Đây là một kiểm tra độ bền
quan trọng: nếu thứ hạng đảo lộn khi đổi chính sách ngưỡng, kết luận sẽ phụ
thuộc vào lựa chọn tùy ý của người thực nghiệm.

Với E04 tại chính sách chính, APCER cho tấn công in là **7,08%** và cho tấn công
phát lại là **3,75%** — cải thiện đến từ cả hai loại tấn công chứ không chỉ tập
trung vào một loại.

Việc chính sách phụ cho ACER thấp hơn chính sách chính ở E04 (11,46% so với
14,79%) không phải mâu thuẫn, vì hai chính sách dùng ngưỡng khác nhau và cách
tổng hợp sai số tấn công khác nhau.

### 9.5.7. Tài nguyên và hiệu năng

| Mô hình | Tổng tham số | Tham số học | Dung lượng | Thời gian huấn luyện | Suy luận thuần lô 1 | Đầu-cuối lô 16 |
|---|---:|---:|---:|---:|---:|---:|
| E01 LBP-SVM | 640 hệ số | 640 | 21,7 KB | 0,68 s | **0,163 ms** | **0,733 ms/khung** |
| E02 MobileNetV2 | 2,23 M | 1.281 | 9,15 MB | 306,50 s | 3,247 ms | 0,991 ms/khung |
| E03 ResNet18 | 11,18 M | 513 | 44,79 MB | 272,51 s | **1,595 ms** | 0,966 ms/khung |
| E04 ResNet18 | 11,18 M | 8.394.241 | 44,79 MB | 216,54 s / 9 epoch | 1,759 ms\* | như E03 |

\* Giá trị suy luận thuần của E04 được đo trong lần chạy chính, không phải cùng
phép đo chuẩn hóa dùng cho ba đường cơ sở. E04 có cùng đồ thị suy luận và cùng
tổng số tham số với E03, nên **không có lý do lý thuyết** để suy luận tốn thêm
thời gian theo số tham số *đã từng được huấn luyện*. Chênh lệch nhỏ giữa hai lần
đo nhiều khả năng là nhiễu thời gian chạy.

**Ba nhận xét cần thiết:**

1. **MobileNetV2 nhỏ hơn ResNet18 khoảng 4,9 lần về dung lượng nhưng không nhanh
   hơn** trong phép đo trên RTX 3060 này. Công thức giảm FLOPs ở (7.10) không
   phản ánh đầy đủ khả năng tối ưu kernel, mẫu truy cập bộ nhớ và mức song song
   thực tế của GPU. Đây là một bài học quan trọng: **độ phức tạp tính toán lý
   thuyết không đồng nghĩa với tốc độ thực tế.** Không được suy rộng kết quả
   benchmark này sang CPU hoặc thiết bị di động nếu chưa đo trực tiếp.
2. **E04 dùng bộ nhớ GPU đỉnh 374,0 MB so với 273,0 MB của E03**, vì quá trình
   lan truyền ngược phải lưu giữ kích hoạt và gradient của `layer4`.
3. **Thời gian huấn luyện của E04 thấp hơn E03 chỉ vì E04 dừng sớm ở epoch 9**,
   không có nghĩa mỗi epoch tinh chỉnh rẻ hơn epoch head-only.

Benchmark đầu-cuối bắt đầu từ ảnh PNG đã cắt, do đó **chưa bao gồm** thời gian
giải mã video thô và phát hiện khuôn mặt. Đây không phải độ trễ của hệ thống
hoàn chỉnh.

### 9.5.8. Phân tích lỗi

Trong ba đường cơ sở E01–E03, có **16 video thật** cùng bị cả ba mô hình dự đoán
nhầm thành giả mạo, nhưng chỉ có **2 video tấn công** cùng bị cả ba bỏ lọt. Sự
bất đối xứng này cho thấy các mô hình chia sẻ một tập nhỏ các mẫu thật đặc biệt
khó, có lẽ do điều kiện thu nhận bất lợi.

E02 và E03 cùng sai trên **23 dương tính giả** và **50 âm tính giả** — cho thấy
hai backbone ImageNet ở chế độ head-only chia sẻ một phần đáng kể chế độ thất
bại. Điều này củng cố lập luận ở mục 7.7.4: khi backbone bị đóng băng, hạn chế
đến từ **đặc trưng ImageNet** chứ không từ kiến trúc cụ thể.

Phân tích theo thiết bị ở E03:

| Yếu tố | Giá trị cao nhất |
|---|---|
| APCER theo điện thoại | Điện thoại 5: 31,25%; điện thoại 6: 28,75% |
| BPCER theo điện thoại | Điện thoại 3: 40,00% |
| APCER theo công cụ tấn công | Máy in 1: 25,83%; màn hình 1: 25,00% |

Mười video lỗi đại diện đều có đủ mười vùng cắt, với độ tin cậy trung bình của
bộ phát hiện trong khoảng 0,938–0,975. Siêu dữ liệu **không** chỉ ra lỗi phát
hiện khuôn mặt rõ ràng nào.

Cần thận trọng khi diễn giải: đây chỉ là **bằng chứng loại trừ sơ bộ**. Không
thể từ độ tin cậy của bộ phát hiện mà kết luận rằng vùng cắt hoàn hảo hoặc mô
hình đã học đúng manh mối.

## 9.6. Thảo luận: lý thuyết giải thích kết quả như thế nào?

Mục này là phần tổng hợp, nối từng kết quả số trở lại với khối lý thuyết tương
ứng.

### 9.6.1. Vì sao E01 tốt trên tập phát triển nhưng sụp đổ trên tập kiểm tra?

Đây là hiện tượng đáng chú ý nhất của toàn bộ thực nghiệm: Dev ACER 10,97% —
**tốt nhất trong ba đường cơ sở** — nhưng Test ACER 32,71% — **kém nhất**.

Trước hết cần khẳng định điều mà kết quả **có** chứng minh: Dev ACER 10,97% cho
thấy đặc trưng LBP **thực sự chứa tín hiệu phân biệt** trong miền của tập phát
triển. Vấn đề không phải LBP vô dụng, mà là điểm vận hành học được không chuyển
được sang miền mới.

Chẩn đoán bằng công cụ lý thuyết ở mục 3.4: một đặc trưng tốt cần phương sai nội
lớp nhỏ và phương sai giữa lớp lớn. Với LBP ở đây, phương sai giữa lớp **đủ
lớn** — bằng chứng là kết quả tốt trên dev. Vấn đề nằm ở **phương sai nội lớp bị
chi phối bởi điều kiện thu nhận** thay vì bởi bản chất live/spoof. Khi tập kiểm
tra đổi sang môi trường thu nhận khác, phân bố của lớp `live` dịch chuyển đủ xa
để vượt qua ranh giới quyết định — và kết quả là 72 trên 120 video thật bị chặn.

Bốn giả thuyết cụ thể đã được đặt ra ở các chương trước, nay được đối chiếu:

| Giả thuyết | Nguồn | Đánh giá dựa trên số liệu |
|---|---|---|
| **G1.** Mất thông tin màu do chuyển sang ảnh xám | Mục 4.1.2 | Nhất quán — sai lệch gam màu là dấu vết mạnh mà E01 không tiếp cận được; công trình [12] ủng hộ giả thuyết này |
| **G2.** Thu nhỏ về 128 điểm ảnh là lọc thông thấp, xóa tần số cao | Mục 4.5.5 | Nhất quán — nhưng chưa kiểm chứng trực tiếp; cần thí nghiệm thay đổi độ phân giải |
| **G3.** Chỉ một tỉ lệ không gian ($R = 1$) | Mục 5.3.4 | Nhất quán — LBP đa tỉ lệ là mở rộng tiêu chuẩn chưa được thử |
| **G4.** Mất thông tin hướng do ánh xạ bất biến quay | Mục 5.4.4 | Nhất quán — vân moiré có hướng đặc trưng bị loại bỏ |

Cần diễn đạt thận trọng: cả bốn giả thuyết đều **nhất quán** với kết quả quan
sát được, nhưng không giả thuyết nào được **chứng minh** bằng thực nghiệm hiện
tại. Việc phân định đóng góp của từng yếu tố đòi hỏi bốn thí nghiệm can thiệp
riêng biệt, mỗi thí nghiệm chỉ thay đổi một yếu tố.

Một quan sát bổ sung có ý nghĩa: giá trị $C = 10^{-4}$ được chọn — nhỏ nhất
trong lưới — cho thấy quá trình chọn mô hình đã **cố gắng chính quy hóa mạnh
nhất có thể**. Việc mô hình vẫn không tổng quát hóa được dù đã chính quy hóa tối
đa là bằng chứng cho thấy hạn chế nằm ở **bản thân biểu diễn**, không phải ở việc
chọn siêu tham số.

### 9.6.2. Vì sao MobileNetV2 không thắng ResNet18?

Chênh lệch thực tế là **1,25 điểm ACER** (25,10% so với 23,85%) — nghiêng về
ResNet18.

Giả thuyết đã đặt ra ở mục 7.6.2 là mô hình nhỏ hơn có thể thiếu năng lực biểu
diễn. Nhưng phân tích kỹ cho thấy giả thuyết này **không giải thích được** kết
quả, vì một lý do đơn giản: **E02 chỉ học 1.281 tham số**. Toàn bộ các bộ lọc
không gian của MobileNetV2 đều bị đóng băng ở giá trị học từ ImageNet. Trong chế
độ này, "năng lực mô hình" gần như không phải là biến số — cả hai mô hình đều
chỉ đang học một phép chiếu tuyến tính trên đặc trưng cố định.

Diễn giải hợp lý hơn: sự khác biệt đến từ **chất lượng của không gian đặc trưng
đóng băng** mà mỗi backbone cung cấp, chứ không từ số tham số. Hai backbone được
huấn luyện với công thức khác nhau (ImageNet V1 so với V2) và có cấu trúc đặc
trưng cuối khác nhau.

Tuy nhiên, với **một hạt giống duy nhất** và chênh lệch chỉ 1,25 điểm, kết luận
đúng đắn nhất là: **chênh lệch này chưa đủ để khẳng định ResNet18 vượt trội.**
Nó nằm trong khoảng dao động có thể xảy ra giữa các lần chạy. Đây là lý do mục
10.2 đặt việc chạy nhiều hạt giống lên ưu tiên số một.

### 9.6.3. E04 dưới góc nhìn học chuyển giao

Đây là kết quả có nền tảng lý thuyết vững nhất. Chế độ head-only chỉ học được
hàm:

$$
z = \mathbf{w}^{T} \phi_{\text{ImageNet}}(\mathbf{x}) + b \qquad (9.1)
$$

Nếu bản thân ánh xạ $\phi_{\text{ImageNet}}$ đã không tách được live và spoof
trong không gian đích của nó, thì **không một bộ phân lớp tuyến tính nào có thể
tạo ra thông tin mới**. Đây là một giới hạn mang tính thông tin, không phải giới
hạn về năng lực tối ưu hóa.

E04 thay thế bằng:

$$
z = \mathbf{w}^{T} \phi_{\text{layer4}}\big(\phi_{\text{frozen}}(\mathbf{x});\, \theta_{\text{PAD}}\big) + b \qquad (9.2)
$$

trong đó $\theta_{\text{PAD}}$ được cập nhật. Khối `layer4` giờ đây có thể **tổ
hợp lại** các đặc trưng cấp thấp thành một biểu diễn phù hợp với miền đích. Kết
nối tắt của khối phần dư giữ đường truyền thông tin thông suốt, còn tốc độ học
nhỏ $10^{-5}$ hạn chế dịch chuyển quá mạnh khỏi điểm khởi tạo.

Mức giảm **9,06 điểm ACER** là bằng chứng thực nghiệm rằng việc thích nghi đặc
trưng có ích trong thiết lập này — xác nhận phân tích về xung đột mục tiêu bất
biến ở mục 7.7.4.

Nhưng phải ghi nhận đầy đủ mặt còn lại: **khoảng cách dev–test của E04 vẫn là
12,22 điểm**. Mô hình đã thích nghi tốt hơn với miền dữ liệu, **nhưng chưa tổng
quát hóa**. Nói cách khác, E04 giải quyết được vấn đề "đặc trưng ImageNet không
phù hợp" nhưng chưa giải quyết được vấn đề "dịch chuyển miền giữa các môi trường
thu nhận".

### 9.6.4. Vai trò của cân bằng lớp và chỉ số đối xứng

Kết quả của E01 minh họa chính xác vì sao cần cả hai cơ chế đã trình bày ở mục
6.6.3.

Hàm mất mát có trọng số xử lý mất cân bằng ở **pha học**, bằng cách cân bằng
tổng đóng góp của hai lớp vào gradient. Chỉ số ACER xử lý mất cân bằng ở **pha
đánh giá**, bằng cách tính sai số riêng cho mỗi lớp rồi lấy trung bình. Hai cơ
chế **không trùng nhau**: một tác động lên hàm mục tiêu liên tục ở mức khung
hình huấn luyện, cơ chế kia đo quyết định rời rạc ở mức video kiểm tra tại một
ngưỡng cụ thể.

Số liệu cụ thể: E01 đạt Recall 94,58% và F1 90,26% trên lớp spoof — những con số
trông rất tốt. Nhưng 72 trên 120 video thật bị chặn. Nếu chỉ báo cáo F1, hệ
thống này có thể được đánh giá là thành công.

Điều này dẫn tới một kết luận thực tiễn quan trọng: **điểm vận hành cuối cùng
phải được chọn dựa trên chi phí nghiệp vụ, không nhất thiết là điểm cực tiểu
ACER.** Với một ứng dụng mở khóa điện thoại, BPCER 60% là hoàn toàn không chấp
nhận được dù APCER chỉ 5,42%.

### 9.6.5. Vì sao trung bình theo video có thể thất bại?

Dự đoán lý thuyết ở mục 8.4.3 được số liệu xác nhận: phép gộp cải thiện E02 và
E03 (lần lượt $-0{,}58$ và $-0{,}18$ điểm) nhưng làm xấu E01 ($+2{,}13$ điểm) và
E04 ($+1{,}39$ điểm).

Theo mô hình (8.11), nếu sai số của mô hình trên một video có thành phần thiên
lệch $b_v$ chung cho mọi khung hình, phép trung bình không khử được nó. Với E04,
cơ chế cụ thể quan sát được là: gộp làm giảm APCER (từ 6,31% xuống 5,42%) nhưng
làm tăng BPCER mạnh hơn (từ 20,50% lên 24,17%). Nghĩa là phép trung bình đẩy
phân bố điểm số của các video thật khó về phía ngưỡng theo hướng bất lợi.

Cần nhấn mạnh giới hạn của diễn giải: đây là một **giải thích thống kê nhất quán
với dữ liệu**, chưa phải bằng chứng nhân quả. Muốn kết luận chắc chắn cần phân
tích quỹ đạo điểm số theo từng khung hình và đánh giá chất lượng từng khung
hình.

Kết luận thực tiễn: **gộp theo thời gian là một mô hình thống kê có giả định,
không phải một thao tác hiển nhiên có lợi.** Trung vị, trung bình cắt xén, trọng
số theo chất lượng, hoặc gộp có học là các hướng so sánh tiếp theo — nhưng phải
được chọn trên tập phát triển hoặc protocol mới.

### 9.6.6. Từ vật lý tái chụp trở lại biểu diễn ảnh

Khép lại vòng lập luận mở đầu ở mục 1.2: bài toán xuất phát từ giả thuyết rằng
công cụ tấn công làm thay đổi quá trình tạo ảnh. Pipeline không đo trực tiếp màn
hình, giấy in hay chiều sâu; nó chỉ quan sát **hệ quả trên điểm ảnh**.

Trong chuỗi đó, mỗi khối có vai trò riêng: cắt vùng mặt làm tăng tỉ lệ tín hiệu
liên quan; thay đổi kích thước đưa ảnh về miền chung; và hai họ biểu diễn tìm
manh mối theo hai cách khác nhau — LBP kiểm tra quan hệ mức xám trong lân cận
bán kính một điểm ảnh rồi đếm mẫu, còn CNN học các nhân đa kênh với trường tiếp
nhận mở rộng dần.

Điểm cần ghi nhận thành thật: vì phép thay đổi kích thước là một bộ lọc thông
thấp, manh mối mà mô hình nhận được **luôn là manh mối còn sót lại sau chuỗi
tiền xử lý**. Kết quả của báo cáo không đại diện cho toàn bộ dấu vết vật lý có
trong video gốc.

## 9.7. Trả lời năm câu hỏi nghiên cứu

**RQ1 — Đặc trưng vi kết cấu LBP còn hiệu quả đến đâu so với CNN tiền huấn
luyện?**

LBP chứa tín hiệu phân biệt thực sự: Dev ACER 10,97% là tốt nhất trong ba đường
cơ sở, và Test APCER 5,42% ngang bằng với E04. Nhưng Test BPCER 60,00% khiến
Test ACER 32,71% trở thành kém nhất. **Kết luận:** biểu diễn kết cấu cố định vẫn
hữu ích như một đường cơ sở cực kỳ nhẹ và bảo thủ với tấn công, nhưng chưa đủ
tổng quát để dùng cho một hệ thống xác thực cân bằng.

**RQ2 — Chỉ học lớp phân lớp có đủ để chuyển từ miền ImageNet sang miền PAD
không?**

**Không đủ.** E02 và E03 chỉ đạt Test ACER lần lượt 25,10% và 23,85%. Việc hai
backbone khác nhau cùng chia sẻ 23 dương tính giả và 50 âm tính giả cho thấy hạn
chế đến từ chính đặc trưng ImageNet đóng băng, không từ kiến trúc cụ thể. Kết
quả này xác nhận phân tích về xung đột mục tiêu bất biến ở mục 7.7.4.

**RQ3 — Tinh chỉnh `layer4` thay đổi sai số như thế nào?**

Test ACER giảm từ 23,85% xuống 14,79%, tức **9,06 điểm phần trăm**. Phân rã theo
loại lỗi: APCER giảm mạnh 14,79 điểm (từ 20,21% xuống 5,42%), BPCER giảm nhẹ
3,33 điểm (từ 27,50% xuống 24,17%). **Kết luận:** cải thiện chủ yếu đến từ việc
giảm số tấn công bị bỏ lọt. Số âm tính giả giảm từ 97 xuống 26.

**RQ4 — Gộp trung bình có luôn tốt hơn không?**

**Không.** Phép gộp cải thiện nhẹ E02 ($-0{,}58$ điểm) và E03 ($-0{,}18$ điểm)
nhưng làm xấu E01 ($+2{,}13$ điểm) và E04 ($+1{,}39$ điểm). Kết quả phù hợp với
phân tích lý thuyết ở mục 8.4.3: khi sai số có thành phần thiên lệch hệ thống
chung cho cả video, phép trung bình không khử được nó.

**RQ5 — F1 có đủ để đánh giá tập dữ liệu lệch lớp không?**

**Không.** E01 đạt F1 = 90,26% trong khi BPCER = 60,00%. Một hệ thống từ chối
60% người dùng hợp lệ là không thể triển khai, nhưng F1 không phản ánh điều đó,
vì cả Precision và Recall đều được định nghĩa quanh lớp dương. Bộ ba APCER,
BPCER và ACER là bắt buộc để diễn giải đúng.

## 9.8. Các đe dọa tới tính hợp lệ

| Loại | Đe dọa cụ thể | Mức độ ảnh hưởng |
|---|---|---|
| **Hợp lệ kết luận** | Chỉ một hạt giống; không có độ lệch chuẩn hay khoảng tin cậy | Cao — chênh lệch 1,25 điểm giữa E02 và E03 có thể là nhiễu |
| **Hợp lệ ngoại tại** | Chỉ Protocol 1; không kiểm tra chéo bộ dữ liệu | Cao — không kết luận được về khả năng tổng quát hóa |
| **Hợp lệ nội tại** | Chọn mô hình trên dev có thể khiến E04 khớp mạnh với dev | Trung bình — khoảng cách dev–test 12,22 điểm là dấu hiệu |
| **Hợp lệ cấu trúc** | ACER giả định hai loại lỗi quan trọng như nhau | Trung bình — cần phân tích chi phí nghiệp vụ thực tế |
| **Hợp lệ cấu trúc** | Kích thước đầu vào khác nhau (LBP 128, CNN 224) | Trung bình — là cấu hình chuẩn của từng phương pháp nhưng cũng là một khác biệt ngoài bộ phân lớp |
| **Hợp lệ cấu trúc** | E01 dùng ảnh xám, CNN dùng RGB | Trung bình — một biến gây nhiễu có hệ thống giữa hai nhánh |
| **Giới hạn dữ liệu** | Chỉ ảnh tĩnh; không khai thác chuyển động, rPPG, nhấp nháy | Cao — bỏ qua cả một họ dấu hiệu PAD |
| **Giới hạn đo lường** | Benchmark không gồm giải mã video và phát hiện mặt | Trung bình — độ trễ báo cáo không phải độ trễ hệ thống |
| **Giới hạn diễn giải** | Không phân tích quy kết | Cao — chưa chứng minh mô hình dùng manh mối nhân quả nào |

---

# Chương 10. Kết luận và hướng phát triển

## 10.1. Kết luận

Báo cáo đã triển khai một hệ thống phát hiện giả mạo khuôn mặt hoàn chỉnh, từ
video thô đến quyết định ở cấp video, và sử dụng hệ thống này làm phương tiện để
khảo sát có kiểm soát các nguyên lý xử lý ảnh và nhận dạng mẫu.

**Về mặt kết quả định lượng,** bốn cấu hình được đánh giá trên cùng một điều kiện
cho Test ACER lần lượt 32,71%, 25,10%, 23,85% và 14,79%. Nhưng kết quả có giá
trị nhất không phải con số 14,79% của E04, mà là **thí nghiệm loại trừ E03/E04**:
khi mọi yếu tố khác được giữ nguyên tuyệt đối, việc mở khối tích chập cuối cùng
với tốc độ học nhỏ làm giảm ACER 9,06 điểm phần trăm. Kết quả này xác nhận một
dự đoán được suy ra từ lý thuyết trước khi chạy thí nghiệm: vì ImageNet và PAD
có **mục tiêu bất biến ngược nhau**, các tầng cao — nơi tính bất biến với điều
kiện thu nhận được xây dựng mạnh nhất — chính là nơi hai tác vụ phân kỳ nhiều
nhất và cần được thích nghi nhất.

**Về mặt lý thuyết,** báo cáo đã vận dụng và làm rõ vai trò của một chuỗi nguyên
lý: lý thuyết lấy mẫu tín hiệu và giới hạn áp dụng của nó với tín hiệu không
dừng; chuẩn hóa hình học vùng quan tâm và các đánh đổi của nó; nội suy và nhận
định then chốt rằng thu nhỏ ảnh là một phép lọc thông thấp có thể xóa chính tín
hiệu cần đo; toán tử LBP và tính bất biến với biến đổi mức xám đơn điệu; lập
luận thống kê đằng sau mẫu uniform; histogram không gian và ý nghĩa riêng của nó
với PAD; cơ sở toán học của PCA và LDA cùng năm luận cứ cho việc không sử dụng
chúng; nguyên lý biên cực đại và con đường từ hình học đến quy hoạch toàn phương
lồi; tích chập, chuẩn hóa theo lô, học phần dư và tích chập tách theo chiều sâu;
học chuyển giao và tốc độ học phân tầng; lý thuyết quyết định trong việc chọn
ngưỡng; và phân tích giới hạn của phép gộp bằng chứng theo thời gian.

**Về mặt phản biện,** báo cáo đồng thời chỉ ra giới hạn của từng nguyên lý. LBP
mất thông tin màu, thông tin hướng và chỉ quan sát một tỉ lệ không gian duy
nhất. Đặc trưng CNN tiền huấn luyện phụ thuộc mạnh vào miền nguồn. Phép gộp
trung bình không khử được thiên lệch hệ thống. Chỉ số F1 có thể che giấu một hệ
thống từ chối 60% người dùng hợp lệ. Bốn nhận định này đều được chứng minh bằng
số liệu cụ thể chứ không phát biểu chung chung.

**Về những gì chưa chứng minh được,** cần nói rõ. Kết quả dựa trên **một hạt
giống duy nhất** và **một protocol duy nhất**. Khoảng cách ACER giữa tập phát
triển và tập kiểm tra của E04 vẫn còn 12,22 điểm phần trăm, cho thấy mô hình đã
thích nghi tốt hơn với miền dữ liệu nhưng **chưa tổng quát hóa**. Báo cáo cũng
không chứng minh được `layer4` đã học chính xác manh mối vật lý nào — mọi phát
biểu về vân moiré hay phản xạ bề mặt trong báo cáo đều ở dạng giả thuyết nhất
quán với dữ liệu, không phải kết luận nhân quả.

## 10.2. Hướng phát triển theo thứ tự ưu tiên

| Ưu tiên | Hướng phát triển | Cơ sở lý thuyết | Kỳ vọng |
|---:|---|---|---|
| 1 | Chạy 3–5 hạt giống cho E03/E04, báo cáo trung bình và khoảng tin cậy | Mục 9.8 | Xác định chênh lệch nào có ý nghĩa thống kê |
| 2 | Đánh giá Protocol 2–4 với cấu hình khóa trước | Mục 9.8 | Đo khả năng tổng quát hóa theo PAI và camera |
| 3 | LBP đa tỉ lệ — kết hợp nhiều cặp $(P, R)$ | Mục 5.3.4; [HFR] §4.3.1.3 tr. 87 | Kiểm chứng giả thuyết G3 |
| 4 | LBP trên các kênh màu thay vì ảnh xám | Mục 4.1.2; [12] | Kiểm chứng giả thuyết G1 |
| 5 | Thí nghiệm can thiệp về độ phân giải đầu vào của LBP | Mục 4.5.5 | Kiểm chứng giả thuyết G2 |
| 6 | LBP-TOP khai thác thông tin không-thời gian | Mục 4.2.3; [HFR] §4.3.1.2 tr. 86 | Bù lại thông tin động đã mất do lấy mẫu thưa |
| 7 | Phân tích phổ tần và Grad-CAM | Mục 9.5.3 | Xác định manh mối mô hình thực sự sử dụng |
| 8 | SVM hạt nhân RBF trên đặc trưng LBP | Mục 6.5.2 | Tách ảnh hưởng của biểu diễn khỏi bộ phân lớp |
| 9 | Đối chứng PCA/LDA trên đặc trưng LBP | Mục 5.6.4 | Kiểm chứng luận cứ số 2 về phương sai và khả năng phân biệt |
| 10 | Gộp theo trọng số chất lượng hoặc gộp có học | Mục 8.4.4 | Khắc phục hạn chế của trung bình đơn giản |
| 11 | Benchmark toàn pipeline trên CPU và thiết bị biên | Mục 9.5.7 | Đo độ trễ hệ thống thực tế |
| 12 | Tinh chỉnh nhiều giai đoạn, tổng quát hóa miền | Mục 7.7.3 | Chỉ nên thực hiện sau khi có protocol đánh giá độc lập |

Thứ tự này phản ánh một nguyên tắc: **trước khi mở rộng mô hình, cần củng cố độ
tin cậy của phép đo.** Ba ưu tiên đầu không thêm bất kỳ kỹ thuật mới nào mà chỉ
làm cho các kết luận hiện có trở nên đáng tin cậy hơn — đây là điều kiện tiên
quyết trước khi đầu tư vào các mở rộng phức tạp.

---

# Tài liệu tham khảo

## A. Giáo trình và bài giảng môn học

**[S1]** Thái Hoàng Lê, *Nhân trắc học*, Khoa Công nghệ Thông tin, Trường Đại
học Khoa học Tự nhiên TP.HCM, 58 slide.

**[S2]** Lê Hoàng Thái, *Nhận dạng mẫu và ứng dụng thử nghiệm*, 35 slide.

**[S3]** *Local Binary Patterns*, slide bài giảng, 54 slide.

**[S4]** A. van Erk, *Principal Component Analysis — Some Mathematical
Backgrounds*, BiGCaT, Universiteit Maastricht, 58 slide.

**[S5]** *Dimensionality Reduction Using PCA/LDA — Case Studies: Face
Recognition Using Dimensionality Reduction*, CS 479/679 Pattern Recognition,
56 slide.

**[S6]** J. Ye, *PCA and LDA for Feature Reduction*, Department of Computer
Science and Engineering, Arizona State University, 40 slide.

**[S7]** J. Gu, *An Introduction of Support Vector Machine*, 2008, 36 slide.

**[S8]** H.-y. Lee (李宏毅), *Deep Learning Tutorial*, 109 slide.

**[HFR]** S. Z. Li và A. K. Jain (chủ biên), *Handbook of Face Recognition*,
2nd ed., Springer, 2011. ISBN 978-0-85729-931-4.

**[HB]** A. K. Jain, P. Flynn và A. A. Ross (chủ biên), *Handbook of
Biometrics*, Springer, 2008. ISBN 978-0-387-71040-2.

## B. Công trình được viện dẫn

[1] V. Bazarevsky, Y. Kartynnik, A. Vakunov, K. Raveendran và M. Grundmann,
"BlazeFace: Sub-millisecond Neural Face Detection on Mobile GPUs," 2019.
arXiv:1907.05047.

[2] T. Ojala, M. Pietikäinen và T. Mäenpää, "Multiresolution Gray-Scale and
Rotation Invariant Texture Classification with Local Binary Patterns," *IEEE
Transactions on Pattern Analysis and Machine Intelligence*, 24(7), 971–987,
2002. DOI: 10.1109/TPAMI.2002.1017623.

[3] T. Ahonen, A. Hadid và M. Pietikäinen, "Face Description with Local Binary
Patterns: Application to Face Recognition," *IEEE Transactions on Pattern
Analysis and Machine Intelligence*, 28(12), 2037–2041, 2006.
DOI: 10.1109/TPAMI.2006.244.

[4] C. Cortes và V. Vapnik, "Support-Vector Networks," *Machine Learning*, 20,
273–297, 1995. DOI: 10.1007/BF00994018.

[5] S. Ioffe và C. Szegedy, "Batch Normalization: Accelerating Deep Network
Training by Reducing Internal Covariate Shift," *ICML*, 2015.
arXiv:1502.03167.

[6] D. P. Kingma và J. Ba, "Adam: A Method for Stochastic Optimization," 2014.
arXiv:1412.6980.

[7] K. He, X. Zhang, S. Ren và J. Sun, "Deep Residual Learning for Image
Recognition," *CVPR*, 2016.

[8] M. Sandler, A. Howard, M. Zhu, A. Zhmoginov và L.-C. Chen, "MobileNetV2:
Inverted Residuals and Linear Bottlenecks," *CVPR*, 2018.

[9] ISO/IEC 30107-3, "Information technology — Biometric presentation attack
detection — Part 3: Testing and reporting."

[10] Z. Boulkenafet, J. Komulainen, L. Li, X. Feng và A. Hadid, "OULU-NPU: A
Mobile Face Presentation Attack Database with Real-World Variations," *IEEE
FG*, 2017. DOI: 10.1109/FG.2017.77.

[11] Y. LeCun, L. Bottou, Y. Bengio và P. Haffner, "Gradient-Based Learning
Applied to Document Recognition," *Proceedings of the IEEE*, 86(11),
2278–2324, 1998.

[12] Z. Boulkenafet, J. Komulainen và A. Hadid, "Face Spoofing Detection Using
Colour Texture Analysis," *IEEE Transactions on Information Forensics and
Security*, 11(8), 1818–1830, 2016.

[13] M. Turk và A. Pentland, "Eigenfaces for Recognition," *Journal of
Cognitive Neuroscience*, 3(1), 71–86, 1991.

[14] P. N. Belhumeur, J. P. Hespanha và D. J. Kriegman, "Eigenfaces vs.
Fisherfaces: Recognition Using Class Specific Linear Projection," *IEEE
Transactions on Pattern Analysis and Machine Intelligence*, 19(7), 711–720,
1997.

[15] A. M. Martinez và A. C. Kak, "PCA versus LDA," *IEEE Transactions on
Pattern Analysis and Machine Intelligence*, 23(2), 228–233, 2001.

[16] J. Määttä, A. Hadid và M. Pietikäinen, "Face Spoofing Detection From
Single Images Using Micro-Texture Analysis," *IJCB*, 2011.
DOI: 10.1109/IJCB.2011.6117510.

[17] R. C. Gonzalez và R. E. Woods, *Digital Image Processing*, 4th ed.,
Pearson, 2018. ISBN 978-0-13-335672-4.

[18] ISO/IEC 30107-1:2016, "Information technology — Biometric presentation
attack detection — Part 1: Framework."

---

# Phụ lục A. Bản đồ tài liệu và artifact

| Nội dung cần kiểm tra | Tệp hoặc thư mục |
|---|---|
| Đề cương ban đầu | `docs/de_cuong_chi_tiet_face_spoofing_oulu_npu.md` |
| Báo cáo số liệu rút gọn | `docs/bao_cao_thuc_nghiem_face_spoofing_oulu_npu.md` |
| Kết quả chi tiết E01 | `docs/ket_qua_e01_lbp_svm.md` |
| Kết quả chi tiết E02 | `docs/ket_qua_e02_mobilenet_v2.md` |
| Kết quả chi tiết E03 | `docs/ket_qua_e03_resnet18.md` |
| Kết quả chi tiết E04 | `docs/ket_qua_e04_resnet18_finetune_layer4.md` |
| Benchmark tài nguyên | `docs/benchmark_tai_nguyen_e01_e03.md` |
| Phân tích lỗi | `docs/error_analysis_e01_e03.md` |
| Cấu hình dữ liệu | `configs/data/oulu_protocol1.yaml` |
| Cấu hình mô hình | `configs/models/*.yaml` |
| Cấu hình thí nghiệm | `configs/experiments/*.yaml` |
| Mã LBP và SVM | `src/face_spoofing/features/lbp.py`, `src/face_spoofing/models/lbp_svm.py` |
| Mã CNN | `src/face_spoofing/models/mobilenet_v2.py`, `src/face_spoofing/models/resnet18.py` |
| Mã đánh giá | `src/face_spoofing/evaluation/metrics.py`, `aggregation.py`, `threshold.py` |
| Toàn bộ artifact E01–E04 | `artifacts/runs/` |

# Phụ lục B. Cấu hình cốt lõi để tái lập

```text
Dữ liệu:    OULU-NPU Protocol 1; live=0; spoof=1; 10 khung hình/video
Vùng cắt:   MediaPipe confidence 0,5; margin=0,2; đầu ra 256×256 PNG
E01:        Xám 128; LBP riu2 P=8, R=1; lưới 8×8; LinearSVC C=1e-4
E02:        MobileNetV2 ImageNet V2; backbone khóa; học head 1.281 tham số
E03:        ResNet18 ImageNet V1; backbone khóa; học head 513 tham số
E04:        ResNet18; học layer4 với LR 1e-5 và head với LR 1e-4
CNN chung:  RGB 224; chuẩn hóa ImageNet; lật ngang 0,5 chỉ trên train; lô 16
Mất mát:    BCEWithLogits; pos_weight=0,25; Adam; weight_decay=1e-4
Chọn mô hình: ACER/APCER/F1 trên video dev; ngưỡng từ dev; test sau khi khóa
Gộp:        Trung bình cộng điểm số theo video
Hạt giống:  42
Phần cứng:  NVIDIA RTX 3060 12 GB cho CNN; CPU cho LBP-SVM
```

# Phụ lục C. Ngưỡng và siêu tham số đã chọn

| Thí nghiệm | Siêu tham số chọn trên dev | Ngưỡng khung hình | Ngưỡng video | Epoch chọn |
|---|---|---:|---:|---:|
| E01 | $C = 10^{-4}$ | $-0{,}3049388$ | $-0{,}4000959$ | — |
| E02 | epoch | — | $0{,}5125712$ | 15 |
| E03 | epoch | — | $0{,}5859636$ | 15 |
| E04 | epoch | — | $0{,}1310235$ | 6 (dừng sớm sau epoch 9) |

# Phụ lục D. Checklist trước khi nộp

- [ ] Điền đầy đủ trường, khoa, giảng viên, học viên, mã số và lớp ở trang bìa
- [ ] Sinh mục lục, danh mục hình, danh mục bảng và đánh số trang
- [ ] Kiểm tra công thức hiển thị đúng sau khi chuyển sang Word hoặc PDF
- [ ] Mọi công thức được đánh số và mọi ký hiệu được giải thích khi xuất hiện lần đầu
- [ ] Mọi bảng và hình được viện dẫn ít nhất một lần trong văn bản
- [ ] Mọi số liệu khớp với artifact — không thay bằng kết quả từ lần chạy khác
- [ ] Mọi trích dẫn slide và số trang sách đã được đối chiếu
- [ ] Giữ nguyên ghi chú minh bạch rằng nội dung CNN không có trong slide môn học
- [ ] Thống nhất dùng dấu phẩy làm dấu thập phân trong toàn báo cáo
- [ ] Phân biệt rõ kết luận thực nghiệm với giả thuyết về manh mối mô hình đã học
- [ ] Ghi rõ giới hạn một hạt giống và một protocol trong phần bảo vệ

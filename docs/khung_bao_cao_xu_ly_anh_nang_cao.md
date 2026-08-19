# BỘ KHUNG BÁO CÁO MÔN HỌC — XỬ LÝ ẢNH NÂNG CAO

## Đề tài: Phát hiện giả mạo khuôn mặt (Face Presentation Attack Detection) trên OULU-NPU Protocol 1

---

**Trường:** ..............................................................
**Khoa/Bộ môn:** .........................................................
**Học phần:** Xử lý ảnh nâng cao
**Giảng viên hướng dẫn:** ................................................
**Học viên thực hiện:** ..................................................
**Mã số học viên:** ......................................................
**Lớp:** .................................................................

**TP. Hồ Chí Minh, tháng ..... năm 2026**

---

## CÁCH DÙNG TÀI LIỆU NÀY

Đây là **bộ khung** (dàn ý thi công), không phải bản báo cáo hoàn chỉnh. Mỗi mục
được mô tả theo năm trường thống nhất:

| Trường | Ý nghĩa |
|---|---|
| **Mục tiêu** | Câu hỏi mà mục này phải trả lời cho người đọc |
| **Nội dung cần viết** | Các ý bắt buộc phải có, theo thứ tự trình bày |
| **Công thức** | Các biểu thức cần đánh số và giải thích từng ký hiệu |
| **Nguồn giáo trình** | Slide/chương sách cụ thể để trích dẫn |
| **Nối với triển khai** | File mã nguồn / config / artifact tương ứng trong dự án |

Trọng tâm môn học là **lý thuyết**, nên tỉ lệ phân bổ đề xuất là:

| Phần | Số trang gợi ý | Tỉ lệ |
|---|---:|---:|
| Chương 1 — Giới thiệu | 4–5 | 8% |
| Chương 2 — Nhân trắc học và tấn công trình diện | 6–7 | 12% |
| Chương 3 — Khung lý thuyết nhận dạng mẫu | 5–6 | 10% |
| Chương 4 — Lý thuyết xử lý ảnh trong tiền xử lý | 7–8 | 14% |
| Chương 5 — Biểu diễn đặc trưng thủ công (LBP) | 8–9 | 16% |
| Chương 6 — Phân lớp biên cực đại (SVM) | 6–7 | 12% |
| Chương 7 — Biểu diễn học sâu (CNN, transfer learning) | 7–8 | 14% |
| Chương 8 — Lý thuyết đánh giá và quyết định | 5–6 | 10% |
| Chương 9 — Thực nghiệm, kết quả và thảo luận | 8–10 | *(minh chứng)* |
| Chương 10 — Kết luận | 2–3 | 4% |

**Tổng thân bài:** khoảng 58–69 trang (chưa tính bìa, mục lục, tài liệu tham
khảo, phụ lục).

> **Nguyên tắc xuyên suốt:** mỗi khối lý thuyết đều phải khép kín theo chuỗi
> *nguyên lý → công thức → tham số cấu hình thực tế → artifact quan sát được*.
> Không trình bày mô hình như "hộp đen", và không đưa vào công thức nào mà báo
> cáo không dùng đến ở phần sau.

---

## BẢNG ĐỐI CHIẾU NGUỒN GIÁO TRÌNH

Ký hiệu viết tắt dùng trong toàn bộ khung:

| Ký hiệu | Tài liệu | Vị trí trong folder |
|---|---|---|
| **[S1]** | Slide *Nhân trắc học* — Thái Hoàng Lê, ĐH KHTN TP.HCM (58 slide) | `Bai_giang_nhan_dang/Bai1_Nhan_trac_hoc.pdf` |
| **[S2]** | Slide *Nhận dạng mẫu và ứng dụng thử nghiệm* — Lê Hoàng Thái (35 slide) | `Bai_giang_nhan_dang/Bai 2_Chu_de_2.pdf` |
| **[S3]** | Slide *Local Binary Patterns* (54 slide) | `Bai_giang_nhan_dang/Bai3_lpbslides.pdf` |
| **[S4]** | Slide *PCA — Some Mathematical Backgrounds* — A. van Erk (58 slide) | `Bai_giang_nhan_dang/Bai 4_pca_basics.pdf` |
| **[S5]** | Slide *Dimensionality Reduction Using PCA/LDA + Case Studies* (56 slide) | `Bai_giang_nhan_dang/Bai 4_5_PCA_LDA_Case_Studies_new.pdf` |
| **[S6]** | Slide *PCA and LDA for Feature Reduction* — Jieping Ye, ASU (40 slide) | `Bai_giang_nhan_dang/Bai 5_Dimensionality-Reduction.pdf` |
| **[S7]** | Slide *An Introduction of Support Vector Machine* — Jinwei Gu, 2008 (36 slide) | `Bai_giang_nhan_dang/Bai 6_svm.pdf` |
| **[S8]** | Slide *Deep Learning Tutorial* — Hung-yi Lee (109 slide) | `Bai_giang_nhan_dang/LEE.pdf` |
| **[HFR]** | *Handbook of Face Recognition*, 2nd ed., Li & Jain (eds.), Springer 2011 | `Book 2011 - Handbook of Face Recognition 2nd Edition.pdf` |
| **[HB]** | *Handbook of Biometrics*, Jain, Flynn & Ross (eds.), Springer 2008 | `Handbook of Biometrics.pdf` |

### Các mỏ neo lý thuyết đã xác minh

| Chủ đề | Nguồn chính | Vị trí chính xác |
|---|---|---|
| Định nghĩa nhân trắc học | [S1] | slide 9 |
| Ba vai trò của hệ nhân trắc học | [S1] | slide 10 |
| Lịch sử (Bertillon 1882 → IAFIS 2000) | [S1] | slide 13 |
| Các thách thức, có "công kích đối với hệ nhân trắc học" | [S1] | slide 16 |
| Sơ đồ hệ nhận dạng mặt 4 khâu | [S1] | slide 21, 28 |
| Kỹ thuật trích chọn không gian mẫu (PCA/ICA/LDA) | [S1] | slide 24 |
| Kỹ thuật phân lớp (ANN, AdaBoost, SVM) | [S1] | slide 25 |
| Mẫu, lớp mẫu, bộ phân lớp (Duda & Hart) | [S2] | slide 3 |
| Ba hướng nhận dạng (thống kê / cấu trúc / nơron) | [S2] | slide 5 |
| Feature vector, hidden state, hàm quyết định q: X→Y | [S2] | slide 6 |
| Ví dụ bộ phân lớp tuyến tính `w·x + b` | [S2] | slide 7 |
| Sơ đồ thành phần hệ nhận dạng mẫu | [S2] | slide 8 |
| Tiêu chí "đặc trưng tốt" vs "đặc trưng tồi" | [S2] | slide 9 |
| Toán tử LBP cơ bản (ví dụ LBP = 241, mẫu 11110001) | [S3] | slide 6 |
| LBP<sub>P,R</sub> lân cận tròn (P=8/R=1, P=12/R=2.5, P=16/R=4) | [S3] | slide 7 |
| Uniform patterns và ý nghĩa số bin | [S3] | slide 9 |
| Nguyên hàm kết cấu: spot, spot/flat, line end, edge, corner | [S3] | slide 10 |
| Vị trí LBP trong họ mô tả kết cấu | [S3] | slide 11 |
| Biến thể LBP (bất biến quay, đa tỉ lệ, LBP variance) | [S3] | slide 12–17 |
| PCA: mục tiêu và bảo toàn phương sai | [S5] | slide 4, 7 |
| PCA: phép chiếu `b_i = uᵢᵀ(x − x̄)` | [S5] | slide 9 |
| PCA: phổ trị riêng và chọn K | [S5] | slide 10, 13 |
| PCA: sai số do giảm chiều | [S5] | slide 14 |
| Eigenfaces (Turk & Pentland 1991) | [S5] | slide 1, 25–28 |
| LDA: scatter trong lớp / giữa lớp | [S5] | slide 37, 40 |
| Fisherfaces, bài toán trị riêng suy rộng | [S5] | slide 41 |
| PCA rồi LDA | [S5] | slide 43 |
| "LDA có luôn tốt hơn PCA?" (Martinez & Kak 2001) | [S5] | slide 53–56 |
| Định nghĩa feature reduction, có giám sát/không giám sát | [S6] | slide 3 |
| Feature reduction vs feature selection | [S6] | slide 5 |
| Curse of dimensionality | [S6] | slide 7 |
| PCA trực quan hình học từng bước | [S4] | slide 4–17 |
| SVM: nguồn gốc (Vapnik 1992) | [S7] | slide 3 |
| Hàm phân biệt tuyến tính `g(x) = wᵀx + b` | [S7] | slide 7 |
| Vô số siêu phẳng — cái nào tốt nhất? | [S7] | slide 8–11 |
| Biên cực đại, "safe zone", tính tổng quát hóa | [S7] | slide 12 |
| Dạng chuẩn tắc sau phép co giãn | [S7] | slide 13 |
| Bài toán đối ngẫu Lagrange | [S7] | slide 20 |
| Điều kiện KKT, vector hỗ trợ, `w = Σ αᵢyᵢxᵢ` | [S7] | slide 21 |
| Hàm quyết định chỉ phụ thuộc tích vô hướng | [S7] | slide 22 |
| Biến bù ξ cho dữ liệu không tách được | [S7] | slide 23 |
| Soft margin, vai trò tham số C | [S7] | slide 24 |
| Kernel trick | [S7] | slide 25–33 |
| Nơ-ron: `z = Σ wᵢaᵢ + b` và hàm kích hoạt | [S8] | slide 8 |
| Kiến trúc nhiều lớp | [S8] | slide 9 |
| Softmax ở lớp đầu ra | [S8] | slide 16–18 |
| Cost / Total cost `C(θ) = Σ Lʳ(θ)` | [S8] | slide 20–21 |
| Gradient descent | [S8] | slide 22–26 |
| Mini-batch | [S8] | slide 28–30 |
| Backpropagation | [S8] | slide 31 |
| Universality theorem | [S8] | slide 34 |
| "Fat + Short vs Thin + Tall" | [S8] | slide 35–36 |
| Modularization — vì sao cần sâu | [S8] | slide 37–40 |
| Overfitting | [S8] | slide 45–46 |
| ReLU và vanishing gradient | [S8] | slide 48–54 |
| Dropout | [S8] | slide 62–72 |
| Điều chỉnh learning rate | [S8] | slide 55–61 |
| Nhân trắc học nhập môn | [HB] | Ch.1, tr. 1–22 |
| Bảo mật hệ nhân trắc học | [HB] | Ch.19, tr. 381–402 |
| **Spoof Detection Schemes** | [HB] | **Ch.20, tr. 403–424** |
| — Spoof khuôn mặt cụ thể | [HB] | §20.2.3, tr. 411 |
| Nhận dạng mặt trong không gian con (PCA/LDA) | [HFR] | Ch.2, tr. 19–50 |
| **Biểu diễn cục bộ đặc trưng khuôn mặt** | [HFR] | **Ch.4, tr. 79–108** |
| — LBP trong miền không gian | [HFR] | §4.3.1.1, tr. 84 |
| — LBP không-thời gian (LBP-TOP) | [HFR] | §4.3.1.2, tr. 86 |
| — LBP đa tỉ lệ | [HFR] | §4.3.1.3, tr. 87 |
| — Mô tả khuôn mặt bằng LBP (chia ô, ghép histogram) | [HFR] | §4.3.2, tr. 87–90 |
| — So sánh LBP với mô tả kết cấu khác (bảng FERET) | [HFR] | tr. 91 |
| Phát hiện khuôn mặt | [HFR] | Ch.11, tr. 277–304 |
| Định vị điểm mốc khuôn mặt | [HFR] | Ch.12, tr. 305–322 |
| Phương pháp đánh giá trong nhận dạng mặt | [HFR] | Ch.21, tr. 551–574 |

> ⚠️ **Lưu ý về khoảng trống giáo trình.** Bộ slide **không có nội dung về mạng
> tích chập (CNN)**: [S8] dừng ở mạng nơ-ron truyền thẳng, gradient descent,
> ReLU và dropout. Do đó Chương 7 phải nêu rõ rằng phần tích chập, batch
> normalization, kết nối phần dư và tích chập tách theo chiều sâu được lấy từ
> tài liệu ngoài (LeCun 1998; Ioffe & Szegedy 2015; He et al. 2016; Sandler et
> al. 2018), **không** gán nhầm cho slide môn học. Đây là điểm trung thực học
> thuật mà người chấm thường kiểm tra.

---

# PHẦN MỞ ĐẦU

## Trang bìa và bìa lót
Theo mẫu của Khoa. Ghi rõ tên học phần **Xử lý ảnh nâng cao**.

## Lời cam đoan
Cam đoan số liệu trong báo cáo được đọc trực tiếp từ artifact của dự án
(`artifacts/runs/`), cấu hình và checkpoint được lưu để kiểm tra lại; kiến thức
kế thừa được trích dẫn đầy đủ.

## Tóm tắt (250–350 từ)
Cấu trúc bốn câu: *(1)* bối cảnh PAD; *(2)* bốn thí nghiệm E01–E04 trên cùng
protocol; *(3)* trọng tâm lý thuyết xử lý ảnh được vận dụng; *(4)* kết quả
ACER và giới hạn. Kết bằng 6–9 từ khóa.

## Mục lục — Danh mục hình — Danh mục bảng — Danh mục chữ viết tắt
Sinh tự động. Danh mục viết tắt tối thiểu: PAD, PAI, LBP, SVM, CNN, BN, BCE,
APCER, BPCER, ACER, EER, ROI, ROC.

---

# CHƯƠNG 1. GIỚI THIỆU
*(4–5 trang)*

## 1.1. Đặt vấn đề

**Mục tiêu.** Thuyết phục người đọc rằng nhận dạng danh tính và phát hiện sự
sống là **hai bài toán khác nhau**.

**Nội dung cần viết**
- Khuôn mặt là đặc trưng sinh trắc thuận tiện: thu nhận không tiếp xúc, bằng
  camera thông thường → dẫn từ [S1] slide 14 (bảng so sánh các đặc trưng nhân
  trắc học) và [HB] Ch.1.
- Chính sự thuận tiện tạo ra lỗ hổng: ảnh/video của người dùng dễ bị sao chép.
- Phân biệt rành mạch hai câu hỏi:
  - *"Đây có phải khuôn mặt của người A?"* → bài toán nhận dạng, đã có lời giải
    trong [S1] slide 21, 28.
  - *"Khuôn mặt này đang xuất hiện trực tiếp hay chỉ là ảnh của người A?"* →
    bài toán PAD, là trọng tâm báo cáo.
- Chỉ ra chính xác vị trí của PAD trong sơ đồ hệ thống: nó nằm ở **điểm tấn
  công số 1** (sensor) trong phân loại của [HB] Ch.19–20.

**Nguồn.** [S1] slide 14, 16, 21; [HB] Ch.1 tr. 1; [HB] Ch.20 tr. 403–405.

## 1.2. Cơ sở vật lý của bài toán

**Mục tiêu.** Giải thích *vì sao* thuật toán xử lý ảnh có thể phân biệt được
live và spoof — đây là mục quan trọng nhất của chương 1.

**Nội dung cần viết**
- Mô tả **chuỗi thu nhận kép (recapture chain)**: mặt thật → camera 1 ghi lại →
  in ra giấy hoặc hiển thị trên màn hình → camera của hệ thống chụp lại.
- Liệt kê các dấu vết vật lý mà chuỗi này để lại, mỗi dấu vết nối với một phép
  xử lý ảnh sẽ dùng ở chương sau:

  | Dấu vết vật lý | Hệ quả trên ảnh | Khai thác ở chương |
  |---|---|---|
  | Lấy mẫu lại lưới điểm ảnh | Moiré, aliasing tần số cao | Ch.4, Ch.5 |
  | Nén và lượng tử hóa hai lần | Mất chi tiết vi kết cấu | Ch.5 (LBP) |
  | Phản xạ bề mặt phẳng | Highlight bất thường, mất bóng 3D | Ch.7 (CNN) |
  | Sai lệch gam màu máy in/màn hình | Dịch chuyển phân bố màu | Ch.4 |
  | Mất nét do tái lấy nét | Giảm năng lượng cạnh | Ch.5 |

- Kết luận: PAD **không** là bài toán ngữ nghĩa mà là bài toán **kết cấu và
  tần số** — chính vì vậy một mô tả vi kết cấu như LBP là ứng viên hợp lý.

**Nguồn.** [HB] §20.2.3 tr. 411; [HFR] Ch.4 tr. 79–80.

## 1.3. Mục tiêu của báo cáo

Bốn mục tiêu, viết ở thể động từ:
1. Xây dựng pipeline tái lập được từ video thô đến quyết định ở cấp video.
2. Đối chiếu biểu diễn **thủ công** (LBP + SVM) với biểu diễn **học được**
   (MobileNetV2, ResNet18) trên cùng protocol, cùng crop, cùng evaluator.
3. Giải thích vai trò của từng nguyên lý xử lý ảnh trong pipeline thay vì mô tả
   mô hình như hộp đen.
4. Kiểm chứng tác động của học chuyển giao qua ablation head-only (E03) so với
   fine-tune `layer4` (E04).

## 1.4. Câu hỏi nghiên cứu

Giữ đúng 5 câu hỏi, sẽ được trả lời từng câu ở §9.6:

- **RQ1.** Đặc trưng vi kết cấu LBP còn hiệu quả đến đâu so với CNN pretrained?
- **RQ2.** Chỉ học classifier head có đủ để chuyển từ miền ImageNet sang miền
  face PAD không?
- **RQ3.** Fine-tune tầng cuối ResNet18 làm thay đổi sai số attack và live như
  thế nào khi mọi yếu tố khác được giữ nguyên?
- **RQ4.** Gộp trung bình điểm của 10 frame có luôn tốt hơn quyết định trên
  từng frame không?
- **RQ5.** Chỉ số F1 có đủ để đánh giá tập dữ liệu lệch lớp 80% spoof không?

## 1.5. Phạm vi và giới hạn

**Nêu thẳng những gì báo cáo KHÔNG làm** — người chấm đánh giá cao sự trung thực:
- Chỉ OULU-NPU Protocol 1 (không chạy Protocol 2–4, không cross-dataset).
- Một seed duy nhất (seed 42), không có khoảng tin cậy trên nhiều lần chạy.
- Chỉ hai loại PAI: ảnh in và video phát lại; không có mặt nạ 3D.
- Không tuyên bố SOTA.

## 1.6. Đóng góp

3–4 gạch đầu dòng, mỗi gạch nối với một artifact cụ thể có thể mở ra kiểm tra.

## 1.7. Cấu trúc báo cáo

Một đoạn văn xuôi dẫn dắt qua 10 chương. Không dùng danh sách gạch đầu dòng ở
mục này (tránh trùng lặp với mục lục).

---

# CHƯƠNG 2. NHÂN TRẮC HỌC VÀ TẤN CÔNG TRÌNH DIỆN
*(6–7 trang)* — **Chương lý thuyết nền, bám sát [S1] và [HB]**

## 2.1. Nhân trắc học: định nghĩa và vai trò

**Mục tiêu.** Đặt bài toán PAD vào đúng khung khái niệm của môn học.

**Nội dung cần viết**
- Định nghĩa: *nhận dạng người tự động dựa trên các bộ phận cơ thể riêng biệt
  (khuôn mặt, vân tay, tròng mắt, võng mạc, hình bàn tay) hoặc các đặc điểm
  hành vi (chữ ký, dáng đi)* — trích gần như nguyên văn [S1] slide 9.
- Ba vai trò theo [S1] slide 10, trình bày dưới dạng bảng:

  | Vai trò | Câu hỏi hệ thống trả lời | Ví dụ |
  |---|---|---|
  | Nhận diện *chấp nhận* (positive) | Người này có được hệ thống biết đến? | Đăng nhập |
  | Nhận diện *độ thuộc lớn* (large scale) | Người này có trong CSDL không? | Chống đăng ký trùng |
  | *Trình duyệt* (screening) | Đây có phải người cần tìm? | Danh sách theo dõi sân bay |

- **Điểm nhấn phải có:** trong cả ba vai trò, hệ thống đều ngầm giả định mẫu
  đưa vào là *thật*. PAD chính là việc gỡ bỏ giả định đó.

**Nguồn.** [S1] slide 9–10; [HB] Ch.1.

## 2.2. Bảy tiêu chí của một đặc trưng nhân trắc học

**Nội dung cần viết.** Trình bày các tiêu chí (tính phổ quát, tính phân biệt,
tính bền vững, khả năng thu nhận, hiệu năng, khả năng chấp nhận, khả năng
chống giả mạo) và **chấm điểm khuôn mặt trên từng tiêu chí**, làm rõ khuôn mặt
mạnh về khả năng thu nhận/chấp nhận nhưng yếu về **chống giả mạo** — chính là
lý do tồn tại của đề tài.

**Nguồn.** [S1] slide 14; [HB] Ch.1 tr. 1–22.

## 2.3. Lược sử và bối cảnh

Một đoạn ngắn (nửa trang), mốc theo [S1] slide 13: hệ Bertillon 1882 →
Galton/Henry 1900 → FBI 1924 → AFIS 1965 → bài báo nhận dạng mặt đầu tiên
(Goldstein et al. 1971) → IAFIS 2000. Mục đích: cho thấy PAD là mối quan tâm
**mới**, xuất hiện khi hệ nhận dạng đã đủ chính xác để trở thành mục tiêu tấn
công.

## 2.4. Các thách thức của hệ nhân trắc học

Liệt kê đủ 9 thách thức trong [S1] slide 16 và **khoanh vùng** thách thức mà báo
cáo giải quyết: *"Những công kích đối với hệ nhân trắc học"*. Các thách thức
khác (phân đoạn, nhiễu đầu vào, tính leo thang, vấn đề riêng tư) chỉ nhắc để
định vị phạm vi.

## 2.5. Phân loại tấn công và vị trí của PAD

**Mục tiêu.** Chỉ rõ PAD chống được loại tấn công nào và **không** chống được
loại nào.

**Nội dung cần viết**
- Vẽ lại sơ đồ luồng thông tin của hệ nhân trắc học ([HB] Hình 20.1, tr. 404)
  với các điểm tấn công được đánh số.
- Bảng phân định:

  | Điểm tấn công | Mô tả | PAD có xử lý? |
  |---|---|---|
  | 1 — Cảm biến | Trình diện vật giả trước camera | **Có** |
  | 2 — Kênh truyền | Chặn/thay thế dữ liệu | Không |
  | 3 — Bộ trích đặc trưng | Thay thế vector đặc trưng | Không |
  | 4 — CSDL mẫu | Sửa template | Không |
  | 5 — Bộ so khớp | Ghi đè điểm số | Không |

- Định nghĩa chuẩn hóa: **PAI** (Presentation Attack Instrument) và **PAD**.

**Nguồn.** [HB] Ch.19 tr. 381–402; Ch.20 tr. 403–406.

## 2.6. Phân loại các phương pháp PAD

**Nội dung cần viết.** Cây phân loại ba nhánh, mỗi nhánh 1–2 đoạn:

1. **Dựa trên phần cứng bổ sung** — cảm biến đa phổ, hồng ngoại, camera chiều
   sâu. Trình bày ví dụ ảnh đa phổ trong [HB] §20.3.2 tr. 415 làm minh họa
   nguyên lý (chương này dùng vân tay nhưng nguyên lý phổ áp dụng chung).
2. **Dựa trên phản ứng sống (liveness/challenge-response)** — chớp mắt, quay
   đầu, đọc chữ ngẫu nhiên. Ưu: khó giả. Nhược: cần hợp tác của người dùng,
   tăng thời gian, thua trước tấn công video phát lại.
3. **Dựa trên phân tích ảnh thụ động** — kết cấu, tần số, màu, chuyển động vi
   mô. **← Đây là nhánh của báo cáo.** Nêu rõ lý do chọn: không cần phần cứng
   thêm, không cần người dùng hợp tác, và là nhánh dùng trực tiếp kiến thức
   xử lý ảnh nâng cao.

**Nguồn.** [HB] §20.2.3 tr. 411 (spoof khuôn mặt); [HFR] Ch.4.

## 2.7. Kết luận chương

Một đoạn chốt: PAD thụ động dựa trên kết cấu là lựa chọn phù hợp cả về mặt kỹ
thuật lẫn phạm vi môn học; các chương sau xây dựng công cụ toán học cho lựa
chọn này.

---

# CHƯƠNG 3. KHUNG LÝ THUYẾT NHẬN DẠNG MẪU
*(5–6 trang)* — **Bám sát [S2], đây là "xương sống" khái niệm của cả báo cáo**

## 3.1. Các khái niệm nền tảng

**Nội dung cần viết**
- **Mẫu (pattern):** một đối tượng, quy trình hoặc sự kiện đã được gắn với một
  tên cho trước.
- **Lớp mẫu (pattern class):** tập các mẫu có chung thuộc tính, thường xuất
  phát từ cùng một nguồn.
- **Bộ phân lớp (classifier):** máy thực hiện phân loại — trích định nghĩa của
  Duda & Hart trong [S2] slide 3.
- **Vector đặc trưng** x ∈ X: vector quan sát đo lường được.
- **Trạng thái ẩn (hidden state)** y ∈ Y: không đo trực tiếp được; các mẫu cùng
  trạng thái ẩn thuộc cùng một lớp.

**Ánh xạ vào đề tài — bảng bắt buộc phải có:**

| Khái niệm [S2] | Trong bài toán PAD của báo cáo |
|---|---|
| Mẫu | Một video OULU-NPU (hoặc một frame đã crop mặt) |
| Lớp mẫu | `live` (nhãn 0) và `spoof` (nhãn 1) |
| Vector đặc trưng x | Vector LBP 640 chiều, hoặc đặc trưng CNN |
| Trạng thái ẩn y | Mặt thật hay vật giả trình diện trước camera |
| Bộ phân lớp q: X → Y | LinearSVC (E01) hoặc CNN + sigmoid (E02–E04) |

**Nguồn.** [S2] slide 3, 6.

## 3.2. Hàm quyết định

**Công thức (3.1).** Nhiệm vụ là thiết kế hàm quyết định

    q : X → Y

**Công thức (3.2).** Với bài toán hai lớp, dạng tuyến tính đơn giản nhất
([S2] slide 7):

    q(x) = { live   nếu ⟨w, x⟩ + b ≥ 0
           { spoof  nếu ⟨w, x⟩ + b < 0

**Nội dung cần viết.** Nhấn mạnh: siêu phẳng ⟨w, x⟩ + b = 0 chia không gian đặc
trưng thành hai nửa. Toàn bộ Chương 6 chỉ nhằm trả lời một câu hỏi — **chọn w
và b như thế nào cho tốt nhất**.

## 3.3. Sơ đồ thành phần của một hệ nhận dạng mẫu

**Nội dung cần viết.** Vẽ lại sơ đồ [S2] slide 8:

    Sensors & preprocessing → Feature extraction → Classifier → Class assignment
                                        ↑                ↑
                              Learning algorithm ← Teacher (nhãn)

Sau đó **ánh xạ 1–1 vào pipeline của dự án** (bảng này sẽ được nhắc lại ở §9.1):

| Khối [S2] slide 8 | Module trong dự án |
|---|---|
| Sensors & preprocessing | `data/frame_sampler.py`, `data/preprocess.py` |
| Feature extraction | `features/lbp.py` (E01) / backbone CNN (E02–E04) |
| Classifier | `models/lbp_svm.py`, `models/resnet18.py`, `models/mobilenet_v2.py` |
| Learning algorithm | `training/*_experiment.py` |
| Teacher (nhãn) | File protocol OULU-NPU, `data/oulu.py` |
| Class assignment | `evaluation/threshold.py`, `evaluation/aggregation.py` |

**Đây là bảng có giá trị điểm cao nhất trong chương** — nó chứng minh học viên
hiểu dự án của mình là hiện thân của một sơ đồ lý thuyết chuẩn.

## 3.4. Thế nào là một đặc trưng tốt?

**Nội dung cần viết.** Theo [S2] slide 9, đặc trưng tốt phải thỏa:
- các đối tượng **cùng lớp** có giá trị đặc trưng **tương tự** (phương sai
  trong lớp nhỏ);
- các đối tượng **khác lớp** có giá trị đặc trưng **khác biệt** (phương sai
  giữa lớp lớn).

**Liên hệ bắt buộc.** Chính hai tiêu chí này là hàm mục tiêu của LDA ở §5.6, và
là tiêu chí để phê phán LBP ở §9.5 (LBP tách tốt trên dev nhưng không tách được
trên test → phương sai trong lớp bị điều kiện thu nhận chi phối).

## 3.5. Ba hướng tiếp cận nhận dạng

Trình bày ngắn ba hướng của [S2] slide 5 và **định vị đề tài**:

| Hướng | Nội dung | Thí nghiệm tương ứng |
|---|---|---|
| Thống kê (statistical PR) | Mô hình thống kê trên tập mẫu | E01: LBP histogram + SVM |
| Cấu trúc/ngữ nghĩa (structural) | Văn phạm, automata, chuỗi | Không dùng — giải thích lý do |
| Mạng nơ-ron (neural) | Mạng nối kết mô phỏng nơ-ron | E02, E03, E04 |

**Lý do không dùng hướng cấu trúc:** dấu vết recapture là thống kê phân tán
trên toàn ảnh, không có cấu trúc ngữ pháp phân cấp để mô tả.

## 3.6. Trích chọn đặc trưng và các kỹ thuật kinh điển

Dẫn [S1] slide 24–25 để cho thấy bức tranh đầy đủ mà môn học đã dạy:
- Trích chọn không gian mẫu: **PCA, ICA, LDA**.
- Phân lớp mẫu: **ANN, AdaBoost, SVM**.

Nêu rõ: báo cáo dùng SVM và ANN sâu; PCA/LDA được phân tích ở §5.6 như phương
án thay thế và làm cơ sở lý luận, không đưa vào pipeline chính.

## 3.7. Kết luận chương

---

# CHƯƠNG 4. LÝ THUYẾT XỬ LÝ ẢNH TRONG GIAI ĐOẠN TIỀN XỬ LÝ
*(7–8 trang)* — **Chương "xử lý ảnh" thuần túy nhất, cần dày công thức**

## 4.1. Ảnh số và video số

**Nội dung cần viết**
- Ảnh số như hàm rời rạc I(x, y) trên lưới điểm ảnh; video là I(x, y, t).
- Ba trục lượng tử hóa: không gian, thời gian, cường độ.
- Điểm nối với đề tài: **mỗi trục lượng tử hóa là một chỗ chuỗi recapture để
  lại dấu vết** (nhắc lại bảng §1.2).

**Công thức (4.1).** Chuyển ảnh màu sang xám (chuẩn ITU-R BT.601):

    I_gray(x, y) = 0.299·R(x, y) + 0.587·G(x, y) + 0.114·B(x, y)

**Nội dung cần viết.** Giải thích tại sao trọng số của G lớn nhất (độ nhạy phổ
của mắt người) và **thảo luận đánh đổi**: E01 chuyển sang ảnh xám
(`grayscale: true` trong `configs/models/lbp_svm.yaml`) nên **mất thông tin
màu** — mà sai lệch gam màu lại là một dấu vết spoof. Đây là một giả thuyết
giải thích kết quả kém của E01 ở Chương 9.

## 4.2. Lấy mẫu khung hình

**Mục tiêu.** Biện minh cho lựa chọn 10 frame/video bằng lý thuyết lấy mẫu.

**Nội dung cần viết**
- Nhắc định lý lấy mẫu Nyquist–Shannon và **giới hạn áp dụng**: tín hiệu ở đây
  không dừng (non-stationary), nên lấy mẫu đều là heuristic chứ không phải hệ
  quả trực tiếp của định lý. *Viết đúng điều này thể hiện sự chặt chẽ.*
- Chiến lược đã dùng: lấy mẫu **đều, tất định**, có bao gồm frame đầu và frame
  cuối.
- Ba lý do: (i) phủ toàn bộ trục thời gian; (ii) tất định → tái lập được;
  (iii) giảm chi phí tính toán 10–100 lần so với dùng toàn bộ frame.
- **Đánh đổi phải nêu:** lấy mẫu thưa làm **mất hoàn toàn** thông tin động
  (chớp mắt, vi chuyển động) — vốn là một họ dấu hiệu PAD quan trọng. Dẫn
  [HFR] §4.3.1.2 tr. 86 (LBP-TOP) như hướng khắc phục, và đưa vào §10.2.

**Nối với triển khai.** `configs/data/oulu_protocol1.yaml` →
`sampling: {strategy: uniform, frames_per_video: 10, deterministic: true,
include_first_frame: true, include_last_frame: true}`;
mã: `src/face_spoofing/data/frame_sampler.py`.

## 4.3. Phát hiện khuôn mặt

**Nội dung cần viết**
- Vị trí trong sơ đồ 4 khâu của [S1] slide 21/28: *Tìm khuôn mặt → Chuẩn hóa →
  Trích chọn đặc trưng → So khớp*.
- Lý thuyết: tổng quan các họ phương pháp phát hiện mặt theo [HFR] Ch.11
  tr. 277 — dựa trên tri thức, đặc trưng bất biến, so mẫu, và **dựa trên diện
  mạo** (Viola–Jones/AdaBoost, mạng nơ-ron). [S1] slide 30 cũng nêu hướng
  AdaBoost + ANN.
- Phương pháp thực dùng: **MediaPipe** (`detector.name: mediapipe`), một bộ dò
  một giai đoạn dựa trên CNN nhẹ. Nêu tham số:
  `model_selection: 0`, `min_detection_confidence: 0.5`,
  `detection_max_side: 640`, `retry_full_resolution: true`.
- **Vì sao tỉ lệ phát hiện phải rất cao:** ngưỡng kiểm soát chất lượng của dự
  án là `minimum_face_detection_rate: 0.98`. Giải thích: nếu bộ dò thất bại
  **có hệ thống** trên ảnh spoof (vì mặt in bị mờ, lóa), thì bản thân việc
  "không phát hiện được mặt" đã rò rỉ nhãn — một dạng leakage tinh vi.

**Nguồn.** [HFR] Ch.11 tr. 277–304; [S1] slide 21, 28, 30.

## 4.4. Chuẩn hóa hình học vùng quan tâm (ROI)

**Nội dung cần viết**
- Vai trò của khâu chuẩn hóa trong [S1] slide 28 và [S1] slide 31 (ASM/AAM).
- Cách làm của dự án: lấy hộp bao khuôn mặt, **nới biên 20%** (`margin: 0.2`),
  cắt và lưu ở kích thước cố định 256×256 PNG (`face_cache.output_size: 256`,
  `format: png`).
- **Ba câu hỏi lý thuyết phải trả lời:**
  1. *Vì sao cần margin?* Ranh giới mặt–nền chứa thông tin PAD (viền giấy in,
     khung màn hình, phản xạ mép). Margin quá nhỏ thì cắt mất; quá lớn thì đưa
     nền vào và mô hình có thể học tắt theo nền.
  2. *Vì sao lưu PNG chứ không JPEG?* PNG là nén **không mất mát**. Nếu lưu
     JPEG, ta sẽ chồng thêm một lớp nén thứ ba lên chuỗi recapture, làm nhiễu
     chính tín hiệu cần đo. **Đây là một quyết định thiết kế thuần túy xử lý
     ảnh và cần được nhấn mạnh.**
  3. *Vì sao lưu 256 rồi mới resize?* Tách rời khâu tiền xử lý tốn kém khỏi
     khâu huấn luyện, đồng thời giữ một bản trung gian đủ lớn để cả LBP (128px)
     và CNN (224px) dùng chung mà không phải upsample.

**Nối với triển khai.** `data/preprocess.py`, `data/processed_validation.py`.

## 4.5. Thay đổi kích thước và nội suy

**Mục tiêu.** Đây là mục **nhiều lý thuyết xử lý ảnh nhất** — cần viết kỹ.

**Nội dung cần viết**
- Bài toán: ánh xạ lưới đích về lưới nguồn, giá trị tại tọa độ không nguyên
  phải nội suy.

**Công thức (4.2).** Nội suy song tuyến (bilinear):

    I(x, y) = (1−a)(1−b)·I₀₀ + a(1−b)·I₁₀ + (1−a)b·I₀₁ + ab·I₁₁

với a, b ∈ [0, 1) là phần lẻ của tọa độ.

**Công thức (4.3).** Nội suy vùng (area / box averaging) khi thu nhỏ theo hệ số
s:

    I_out(i, j) = (1/|Ω_ij|) · Σ_{(u,v) ∈ Ω_ij} I_in(u, v)

với Ω_ij là tập điểm ảnh nguồn rơi vào ô đích (i, j).

- **So sánh và biện minh lựa chọn của dự án** — bảng bắt buộc:

  | Phép nội suy | Bản chất | Dùng ở đâu | Lý do |
  |---|---|---|---|
  | Area | Trung bình vùng, chống aliasing đúng cách khi thu nhỏ | E01: 256 → 128 (`resize_interpolation: area`) | Thu nhỏ mạnh; area là bộ lọc thông thấp tự nhiên, tránh aliasing làm hỏng thống kê LBP |
  | Bilinear + antialias | Nội suy tuyến tính có tiền lọc | E02–E04: 256 → 224 (`interpolation: bilinear, antialias: true`) | Khớp với quy ước tiền xử lý của trọng số ImageNet |

- **Điểm lý thuyết cốt lõi phải viết rõ:** thu nhỏ ảnh **là một phép lọc thông
  thấp**. Nó xóa bớt chính thành phần tần số cao mà dấu vết recapture cư trú.
  Do đó việc chọn 128px cho LBP là một sự đánh đổi *có thể đã làm mất tín hiệu*
  — và giả thuyết này phải được kiểm lại ở §9.5.

## 4.6. Chuẩn hóa cường độ

**Công thức (4.4).** Chuẩn hóa theo thống kê ImageNet (E02–E04):

    x̂_c = (x_c − μ_c) / σ_c,   c ∈ {R, G, B}

với μ = (0.485, 0.456, 0.406), σ = (0.229, 0.224, 0.225).

**Công thức (4.5).** Chuẩn hóa đặc trưng theo z-score trước SVM (E01):

    z_j = (f_j − μ_j) / σ_j

**Nội dung cần viết**
- Vì sao E02–E04 **phải** dùng đúng μ, σ của ImageNet: trọng số pretrained được
  học trên dữ liệu đã chuẩn hóa như vậy; dùng thống kê khác sẽ đẩy phân bố đầu
  vào ra khỏi vùng làm việc của các tầng BN đầu tiên.
- Vì sao E01 cần `standardize: true`: SVM tuyến tính có chính quy hóa L2 nhạy
  với thang đo của từng chiều đặc trưng; không chuẩn hóa thì tham số C mất ý
  nghĩa nhất quán giữa các chiều.
- **Cảnh báo leakage bắt buộc phải nêu:** μ_j và σ_j chỉ được ước lượng trên
  **tập train**, sau đó áp dụng nguyên vẹn cho dev và test.

## 4.7. Kết luận chương

Chốt: sau chương này, mỗi video đã trở thành một tập 10 ảnh mặt chuẩn hóa —
đầu vào chung, công bằng cho cả bốn thí nghiệm.

---

# CHƯƠNG 5. BIỂU DIỄN ĐẶC TRƯNG THỦ CÔNG: LOCAL BINARY PATTERN
*(8–9 trang)* — **Chương lý thuyết trọng tâm, dùng [S3] và [HFR] Ch.4**

## 5.1. Vì sao chọn mô tả kết cấu?

**Nội dung cần viết**
- Nhắc lại kết luận §1.2: PAD là bài toán kết cấu, không phải ngữ nghĩa.
- Vị trí LBP trong họ các mô tả kết cấu: dẫn sơ đồ [S3] slide 11 (LBP nằm giữa
  các nhánh texture unit / texture spectrum / co-occurrence / textons).
- Ba ưu điểm khiến LBP phù hợp bài toán: bất biến với biến đổi đơn điệu của
  mức xám, chi phí tính toán thấp, không cần giai đoạn học.
- Dẫn [HFR] §4.1 tr. 79: biểu diễn tốt phải *(i)* phân biệt tốt giữa lớp trong
  khi dung thứ biến thiên nội lớp, *(ii)* trích xuất nhanh, *(iii)* nằm trong
  không gian chiều thấp. Đối chiếu từng tiêu chí với LBP.

## 5.2. Toán tử LBP cơ bản

**Công thức (5.1).** LBP gốc trên lân cận 3×3 ([S3] slide 6):

    LBP(x_c, y_c) = Σ_{p=0}^{7} s(g_p − g_c) · 2^p

**Công thức (5.2).** Hàm dấu:

    s(t) = { 1  nếu t ≥ 0
           { 0  nếu t < 0

**Nội dung cần viết**
- **Bắt buộc có ví dụ số** — chép lại ví dụ của [S3] slide 6 và tự kiểm chứng:
  cửa sổ [[6,5,2],[7,6,1],[9,8,7]] với tâm 6 → ngưỡng hóa cho mẫu nhị phân
  `11110001` → LBP = 1 + 16 + 32 + 64 + 128 = **241**.
- Giải thích **vì sao bất biến với biến đổi đơn điệu**: nếu thay g → f(g) với f
  đơn điệu tăng, dấu của hiệu g_p − g_c không đổi, nên mã LBP không đổi. Đây là
  lý do LBP chịu được thay đổi độ sáng — một tính chất rất có giá trị khi
  OULU-NPU thu ở nhiều điều kiện chiếu sáng.
- **Ghi chú triển khai quan trọng:** mã nguồn dự án dùng điều kiện
  `neighbours >= centre` (bao gồm dấu bằng) và duyệt lân cận **theo chiều kim
  đồng hồ bắt đầu từ góc trên-trái**. Biên ảnh được xử lý bằng **nhân bản mép**
  (`np.pad(..., mode="edge"`) để không tạo ra khung tối nhân tạo. Cần nêu đúng
  các chi tiết này vì chúng ảnh hưởng đến khả năng tái lập.

**Nối với triển khai.** `src/face_spoofing/features/lbp.py`, hàm
`_uniform_lbp_bins`.

## 5.3. LBP tổng quát trên lân cận tròn

**Công thức (5.3).**

    LBP_{P,R}(x_c, y_c) = Σ_{p=0}^{P−1} s(g_p − g_c) · 2^p

với P điểm lấy mẫu đều trên đường tròn bán kính R, tọa độ:

**Công thức (5.4).**

    (x_p, y_p) = (x_c + R·cos(2πp/P),  y_c − R·sin(2πp/P))

**Nội dung cần viết**
- Giá trị tại tọa độ không nguyên phải **nội suy song tuyến** → nối ngược về
  Công thức (4.2). *Đây là một liên kết đẹp giữa hai chương, nên nêu rõ.*
- Ba cấu hình minh họa của [S3] slide 7: (P=8, R=1.0), (P=12, R=2.5),
  (P=16, R=4.0). Giải thích ý nghĩa đa tỉ lệ: R lớn bắt kết cấu thô hơn.
- Ghi công: Ojala, Pietikäinen & Mäenpää, *TPAMI* 24(7), 2002.
- **Lựa chọn của dự án và lý do:** chỉ hỗ trợ P=8, R=1 (mã nguồn chủ động ném
  lỗi với cấu hình khác). Biện minh: dấu vết recapture nằm ở **tần số cao
  nhất**, tức lân cận sát nhất; đồng thời giữ số chiều đặc trưng nhỏ. Nêu thẳng
  đây cũng là **giới hạn** — LBP đa tỉ lệ ([HFR] §4.3.1.3 tr. 87) là hướng mở
  rộng ở §10.2.

## 5.4. Mẫu uniform và giảm số bin

**Định nghĩa (5.5).** Số chuyển tiếp bit vòng:

    U(LBP_{P,R}) = |s(g_{P−1} − g_c) − s(g_0 − g_c)|
                 + Σ_{p=1}^{P−1} |s(g_p − g_c) − s(g_{p−1} − g_c)|

Mẫu được gọi là **uniform** khi U ≤ 2.

**Nội dung cần viết**
- Ý nghĩa hình học: các mẫu uniform tương ứng với các **nguyên hàm kết cấu** cơ
  bản — *spot, spot/flat, line end, edge, corner* ([S3] slide 10). Nên vẽ lại
  hình này.
- **Lập luận thống kê then chốt:** với P=8 có 256 mẫu, trong đó chỉ 58 là
  uniform, nhưng chúng chiếm phần áp đảo tần suất xuất hiện trong ảnh tự nhiên.
  Gom toàn bộ mẫu không uniform vào **một** bin duy nhất giúp giảm chiều mạnh
  mà mất rất ít thông tin, đồng thời làm histogram **ổn định thống kê hơn**
  (mỗi bin nhận đủ số đếm).
- **Ánh xạ cụ thể của dự án — phải mô tả chính xác:** dùng biến thể **bất biến
  quay + uniform**, ánh xạ theo *số bit 1*:

  | Bin | Nội dung |
  |---:|---|
  | 0–8 | Mẫu uniform, đánh số theo số bit bằng 1 (0 đến 8 bit) |
  | 9 | Toàn bộ mẫu không uniform (U > 2) |

  → **đúng 10 bin**, khớp `bins: 10` trong `configs/models/lbp_svm.yaml`.

**Nguồn.** [S3] slide 9, 10; [HFR] §4.3.1.1 tr. 84.

## 5.5. Histogram không gian và mô tả khuôn mặt

**Mục tiêu.** Giải thích cách chuyển từ bản đồ mã LBP thành một vector đặc
trưng duy nhất.

**Nội dung cần viết**
- **Vấn đề:** histogram LBP trên toàn ảnh chỉ mã hóa *tần suất* các vi mẫu, mất
  hoàn toàn *vị trí* của chúng ([HFR] §4.3.2.1 tr. 87–88 nêu chính xác vấn đề
  này).
- **Giải pháp:** chia ảnh thành lưới ô, tính histogram độc lập trên từng ô, rồi
  **nối** lại. Đây chính là phương pháp Ahonen–Hadid–Pietikäinen mà [HFR]
  §4.3.2 trình bày. Vẽ lại sơ đồ chia ô.
- **Ý nghĩa với PAD (điểm phải nhấn):** dấu vết spoof **không phân bố đều** —
  vùng trán, gò má phản xạ khác vùng mắt, tóc. Lưới không gian cho phép mô hình
  gán trọng số khác nhau cho từng vùng.

**Công thức (5.6).** Chuẩn hóa L1 trên mỗi ô:

    h_c(k) = n_c(k) / |Ω_c|,   k = 0, …, 9

với n_c(k) là số điểm ảnh trong ô c rơi vào bin k, |Ω_c| là số điểm ảnh của ô.

**Công thức (5.7).** Vector đặc trưng cuối:

    f = [h_1(0), …, h_1(9), h_2(0), …, h_{64}(9)] ∈ ℝ^640

**Nội dung cần viết — phép tính chiều phải trình bày rõ:**

    grid_rows × grid_cols × bins = 8 × 8 × 10 = 640

khớp `feature_dim: 640`. Nêu rằng ảnh 128×128 chia lưới 8×8 → mỗi ô 16×16 = 256
điểm ảnh, tức trung bình 25,6 điểm/bin — **đủ để histogram có ý nghĩa thống
kê**. Đây là lập luận biện minh cho việc chọn đồng thời 128px và lưới 8×8, và
là một điểm cộng nếu viết được.

- **Vì sao chuẩn hóa L1 theo từng ô** (chứ không chuẩn hóa toàn cục): để mỗi ô
  đóng góp như nhau bất kể ô rìa có thể bị cắt lẻ; đồng thời biến số đếm thành
  phân bố xác suất, so sánh được giữa các ảnh khác kích thước.

**Nối với triển khai.** `features/lbp.py::extract_lbp`, tham số
`grid_rows: 8, grid_cols: 8, histogram_normalization: l1_per_cell`.

## 5.6. Giảm chiều: PCA và LDA như phương án thay thế

**Mục tiêu.** Đây là mục cho phép huy động toàn bộ [S4], [S5], [S6] — **không
bỏ qua dù dự án không dùng PCA trong pipeline chính**. Cách viết đúng là trình
bày như *một phân tích lựa chọn thiết kế có luận cứ*.

### 5.6.1. Bài toán giảm chiều

- Định nghĩa theo [S6] slide 3: ánh xạ dữ liệu chiều cao sang không gian chiều
  thấp, với tiêu chí khác nhau tùy bối cảnh — **không giám sát**: cực tiểu mất
  mát thông tin; **có giám sát**: cực đại khả năng tách lớp.
- Phân biệt **feature reduction** (dùng mọi đặc trưng gốc, tạo tổ hợp tuyến
  tính) và **feature selection** (chỉ chọn một tập con) — [S6] slide 5.
- **Curse of dimensionality** ([S6] slide 7): độ chính xác và hiệu quả truy vấn
  suy giảm nhanh khi số chiều tăng.

**Công thức (5.8).** Phép chiếu tuyến tính: y = Gᵀx, với G ∈ ℝ^{p×d}, d ≪ p.

### 5.6.2. PCA

- Trực giác hình học theo [S4] slide 4–17: tính trọng tâm → dịch gốc tọa độ về
  trọng tâm → tìm hướng phương sai cực đại → lặp cho các trục trực giao → chiếu
  bỏ bớt trục.

**Công thức (5.9).** Ma trận hiệp phương sai mẫu:

    Σ = (1/M) · Σ_{i=1}^{M} (x_i − x̄)(x_i − x̄)ᵀ

**Công thức (5.10).** Bài toán trị riêng: Σu_k = λ_k u_k, sắp xếp
λ_1 ≥ λ_2 ≥ … ≥ λ_N.

**Công thức (5.11).** Hệ số chiếu ([S5] slide 9): b_i = u_iᵀ(x − x̄)

**Công thức (5.12).** Tiêu chí chọn K theo tỉ lệ phương sai giữ lại
([S5] slide 13):

    (Σ_{i=1}^{K} λ_i) / (Σ_{i=1}^{N} λ_i) ≥ θ   (θ thường 0.90–0.95)

**Công thức (5.13).** Sai số trung bình do giảm chiều ([S5] slide 14):

    e = (1/2) · Σ_{i=K+1}^{N} λ_i

- Nêu tính chất: Σ đối xứng thực nên các vector riêng trực giao và tạo thành
  một cơ sở ([S5] slide 7).
- **Eigenfaces** ([S5] slide 25–28; Turk & Pentland 1991): mỗi vector riêng là
  một "khuôn mặt riêng"; nhận dạng bằng cách so khớp trong không gian hệ số.

### 5.6.3. LDA

**Công thức (5.14).** Scatter trong lớp:

    S_W = Σ_{j=1}^{C} Σ_{x ∈ ω_j} (x − μ_j)(x − μ_j)ᵀ

**Công thức (5.15).** Scatter giữa lớp:

    S_B = Σ_{j=1}^{C} N_j (μ_j − μ)(μ_j − μ)ᵀ

**Công thức (5.16).** Tiêu chuẩn Fisher ([S5] slide 40):

    W* = arg max_W  |Wᵀ S_B W| / |Wᵀ S_W W|

- Nghiệm là vector riêng của bài toán trị riêng suy rộng S_B w = λ S_W w
  ([S5] slide 41) — các trục này gọi là **Fisherfaces**.
- Vì sao thường phải chạy **PCA trước rồi LDA** ([S5] slide 43): khi số mẫu nhỏ
  hơn số chiều, S_W suy biến và không nghịch đảo được.
- **Giới hạn số chiều:** LDA cho tối đa C − 1 hướng phân biệt. Với PAD hai lớp
  (C = 2) → **chỉ 1 chiều duy nhất**. Nêu rõ điều này.

### 5.6.4. Vì sao pipeline không dùng PCA/LDA — lập luận thiết kế

Trình bày thành bảng, đây là phần cho thấy tư duy phản biện:

| Cân nhắc | Phân tích |
|---|---|
| Số chiều đã đủ nhỏ | 640 chiều với ~12 000 mẫu train là tỉ lệ lành mạnh; chưa chạm curse of dimensionality theo nghĩa của [S6] slide 7 |
| PCA cực đại phương sai, **không** cực đại khả năng tách | Phương sai lớn nhất của ảnh mặt đến từ chiếu sáng và danh tính, **không** từ dấu vết spoof — PCA có nguy cơ giữ lại nhiễu và loại bỏ tín hiệu |
| LDA hai lớp chỉ cho 1 chiều | Quá chặt; mất khả năng biểu diễn phi tuyến còn lại |
| SVM tuyến tính đã tự chính quy hóa | Chuẩn L2 trên w đã kiểm soát năng lực mô hình mà không cần giảm chiều tường minh |
| Đối chứng với [S5] slide 53–56 | Martinez & Kak (2001): LDA **không** luôn tốt hơn PCA; khi tập huấn luyện nhỏ, PCA có thể thắng. Kết luận: giảm chiều là lựa chọn theo bối cảnh, không phải bước bắt buộc |

**Kết luận mục.** Một đoạn: PCA/LDA vẫn có giá trị như đường cơ sở đối chứng và
được đưa vào §10.2 như thí nghiệm mở rộng.

## 5.7. Kết luận chương

---

# CHƯƠNG 6. PHÂN LỚP BIÊN CỰC ĐẠI: SUPPORT VECTOR MACHINE
*(6–7 trang)* — **Bám sát [S7], trình bày theo đúng mạch dẫn dắt của slide**

## 6.1. Hàm phân biệt tuyến tính

**Công thức (6.1).** g(x) = wᵀx + b ([S7] slide 7)

**Nội dung cần viết**
- Nhắc lại từ [S2] slide 6: bộ phân lớp gán x cho lớp ω_i nếu
  g_i(x) > g_j(x) ∀ j ≠ i; với hai lớp rút gọn thành xét dấu g(x).
- Ý nghĩa hình học: g(x) = 0 là siêu phẳng; **w là vector pháp tuyến**; vector
  pháp tuyến đơn vị là n = w/‖w‖ ([S7] slide 7).
- **Đặt vấn đề như slide:** với dữ liệu tách được tuyến tính có **vô số** siêu
  phẳng thỏa mãn ([S7] slide 8–11). Câu hỏi: *cái nào tốt nhất?*

## 6.2. Nguyên lý biên cực đại

**Nội dung cần viết**
- Định nghĩa **biên (margin)**: bề rộng mà ranh giới có thể nới ra trước khi
  chạm điểm dữ liệu đầu tiên — hình "safe zone" [S7] slide 12.
- Lập luận của slide: siêu phẳng biên cực đại **bền vững với ngoại lai và có
  khả năng tổng quát hóa mạnh**.
- Ghi công: Vapnik và cộng sự, 1992 ([S7] slide 3).

**Công thức (6.2).** Dạng chuẩn tắc sau phép co giãn w, b ([S7] slide 13):

    y_i(wᵀx_i + b) ≥ 1,   i = 1, …, n

**Công thức (6.3).** Bề rộng biên:

    margin = 2 / ‖w‖

→ cực đại biên **tương đương** cực tiểu ‖w‖². Cần viết rõ phép tương đương này,
vì đó là bước then chốt biến bài toán hình học thành bài toán tối ưu.

## 6.3. Bài toán tối ưu và đối ngẫu

**Công thức (6.4).** Bài toán gốc (hard margin):

    min_{w,b}  (1/2)‖w‖²
    s.t.       y_i(wᵀx_i + b) ≥ 1,  ∀i

**Công thức (6.5).** Hàm Lagrange ([S7] slide 20):

    L_p(w, b, α) = (1/2)‖w‖² − Σ_{i=1}^{n} α_i [ y_i(wᵀx_i + b) − 1 ]

**Công thức (6.6).** Bài toán đối ngẫu ([S7] slide 20):

    max_α  Σ_{i=1}^{n} α_i − (1/2) Σ_i Σ_j α_i α_j y_i y_j x_iᵀx_j
    s.t.   α_i ≥ 0,  Σ_{i=1}^{n} α_i y_i = 0

**Công thức (6.7).** Nghiệm theo điều kiện KKT ([S7] slide 21):

    w = Σ_{i=1}^{n} α_i y_i x_i = Σ_{i ∈ SV} α_i y_i x_i

**Nội dung cần viết**
- Diễn giải KKT: α_i[y_i(wᵀx_i + b) − 1] = 0, do đó **chỉ những điểm nằm đúng
  trên biên mới có α_i > 0** — đó là các **vector hỗ trợ**. Nghiệm chỉ phụ
  thuộc vào một tập con nhỏ của dữ liệu.
- Nhận xét quan trọng của [S7] slide 22: hàm quyết định chỉ phụ thuộc vào
  **tích vô hướng** giữa điểm kiểm tra và các vector hỗ trợ — đây chính là cánh
  cửa dẫn tới kernel trick.

## 6.4. Soft margin và tham số C

**Công thức (6.8).** Bài toán với biến bù ([S7] slide 23–24):

    min_{w,b,ξ}  (1/2)‖w‖² + C · Σ_{i=1}^{n} ξ_i
    s.t.         y_i(wᵀx_i + b) ≥ 1 − ξ_i,   ξ_i ≥ 0

**Nội dung cần viết**
- Vì sao cần: dữ liệu thực có nhiễu và ngoại lai, không tách được tuyến tính
  ([S7] slide 23).
- Diễn giải ξ_i: mức độ vi phạm biên của mẫu thứ i.
- **Vai trò của C** ([S7] slide 24): C là cách kiểm soát overfitting. C lớn →
  phạt nặng vi phạm → biên hẹp, dễ khớp quá mức. C nhỏ → chấp nhận vi phạm →
  biên rộng, mô hình đơn giản hơn.
- **Nối với thực nghiệm:** dự án dò C trên lưới
  {10⁻⁴, 10⁻³, 10⁻², 10⁻¹, 1, 10}, **chọn trên tập dev**, kết quả lưu tại
  `artifacts/runs/lbp_svm/.../selection/c_search.csv`. Cần trình bày bảng dò
  này ở §9.2 và bình luận theo lý thuyết vừa nêu.

## 6.5. Kernel trick

**Công thức (6.9).** Thay tích vô hướng bằng hàm nhân:

    K(x_i, x_j) = φ(x_i)ᵀφ(x_j)

- Trình bày ý tưởng ([S7] slide 25–33): ánh xạ ngầm sang không gian chiều cao
  hơn nơi dữ liệu tách được tuyến tính, mà **không cần tính φ tường minh**.
- Nêu các nhân thông dụng: đa thức, RBF (Gaussian), sigmoid.
- **Vì sao dự án dùng nhân tuyến tính** (`estimator: LinearSVC`) — ba lý do:
  *(i)* đặc trưng LBP đã là histogram chiều tương đối cao (640), thường đã đủ
  tách tuyến tính; *(ii)* giữ E01 ở vai trò **đường cơ sở tối giản**, để phép
  so sánh với CNN quy về "biểu diễn thủ công vs biểu diễn học được" chứ không
  lẫn với độ phức tạp của bộ phân lớp; *(iii)* chi phí suy luận cực thấp
  (0,163 ms/mẫu) — một luận điểm về tính thực dụng.
- SVM nhân RBF đưa vào §10.2 như thí nghiệm mở rộng.

## 6.6. Xử lý mất cân bằng lớp

**Nội dung cần viết**
- Nêu số liệu: Protocol 1 có tỉ lệ **live : spoof = 1 : 4** (train 240 : 960).
- Cơ chế `class_weight: balanced`: trọng số lớp tỉ lệ nghịch với tần suất, tức
  hàm mục tiêu trở thành

**Công thức (6.10).**

    min  (1/2)‖w‖² + C · Σ_i c_{y_i} · ξ_i,   với c_k ∝ n / (K · n_k)

- **Vì sao cần:** nếu không cân bằng, bộ phân lớp có thể đạt 80% độ chính xác
  chỉ bằng cách luôn dự đoán `spoof` — mà vẫn vô dụng. Đây cũng là lý do phải
  dùng ACER thay vì accuracy, dẫn sang Chương 8.
- Các siêu tham số còn lại cần nêu để tái lập: `penalty: l2`,
  `loss: squared_hinge`, `dual: false`, `tolerance: 1e-4`,
  `max_iterations: 20000`, `seed: 42`.

## 6.7. Kết luận chương

---

# CHƯƠNG 7. BIỂU DIỄN HỌC SÂU VÀ HỌC CHUYỂN GIAO
*(7–8 trang)*

> **Ghi chú về nguồn — bắt buộc viết ở đầu chương.** Slide [S8] cung cấp nền
> tảng mạng nơ-ron truyền thẳng (nơ-ron, hàm mất mát, gradient descent,
> backpropagation, ReLU, dropout, vì sao cần sâu) nhưng **không đề cập mạng
> tích chập**. Các mục 7.4–7.7 do đó dựa trên tài liệu ngoài và cần trích dẫn
> tương ứng. Nêu minh bạch điều này ngay trong báo cáo.

## 7.1. Từ nơ-ron đến mạng nhiều lớp

**Công thức (7.1).** Một nơ-ron ([S8] slide 8):

    z = Σ_{k=1}^{K} w_k a_k + b,    a = σ(z)

**Nội dung cần viết**
- Các thành phần: trọng số, độ lệch (bias), hàm kích hoạt.
- Mạng nhiều lớp ([S8] slide 9): lớp vào — các lớp ẩn — lớp ra; mạng là một họ
  hàm f: ℝ^N → ℝ^M có tham số.
- **Universality theorem** ([S8] slide 34): một lớp ẩn đủ rộng có thể xấp xỉ
  hàm liên tục bất kỳ.
- **Nhưng vì sao vẫn cần sâu?** — trình bày lập luận *modularization*
  ([S8] slide 37–40) và so sánh "Fat + Short vs Thin + Tall" ([S8] slide
  35–36): mạng sâu tái sử dụng các đặc trưng trung gian, đạt cùng năng lực biểu
  diễn với ít tham số hơn nhiều.
- **Liên hệ đề tài:** đây chính là biện minh lý thuyết cho việc dùng ResNet18
  18 tầng thay vì một MLP rộng.

## 7.2. Hàm mất mát và huấn luyện

**Công thức (7.2).** Tổng chi phí trên tập huấn luyện ([S8] slide 20–21):

    C(θ) = Σ_{r=1}^{R} L^r(θ)

**Công thức (7.3).** Sigmoid cho bài toán nhị phân:

    σ(z) = 1 / (1 + e^{−z})

**Công thức (7.4).** Binary cross-entropy có trọng số lớp:

    L = −(1/N) Σ_{i=1}^{N} [ w₊ · y_i log σ(z_i) + (1 − y_i) log(1 − σ(z_i)) ]

**Nội dung cần viết**
- Vì sao dùng **sigmoid + BCE** (một logit) chứ không softmax hai lớp
  ([S8] slide 16–18 trình bày softmax): với bài toán nhị phân hai cách tương
  đương về mặt biểu diễn, nhưng một logit cho **một điểm số vô hướng liên tục**
  — thuận tiện cho việc quét ngưỡng ở Chương 8. Đây là lý do thiết kế thực chất.
- Nêu cấu hình: `output_dim: 1`, `score_type: logit`,
  `loss: BCEWithLogitsLoss`.
- Vì sao dùng trọng số dương w₊: cùng lý do với `class_weight: balanced` ở §6.6.

## 7.3. Tối ưu hóa

**Công thức (7.5).** Gradient descent ([S8] slide 22–26):

    θ^{(t+1)} = θ^{(t)} − η · ∇C(θ^{(t)})

**Nội dung cần viết**
- **Mini-batch** ([S8] slide 28–30): vì sao không dùng toàn bộ tập dữ liệu mỗi
  bước — chi phí và tính ngẫu nhiên giúp thoát điểm yên ngựa.
- **Backpropagation** ([S8] slide 31): là **cách tính gradient hiệu quả** bằng
  quy tắc chuỗi, không phải một thuật toán tối ưu riêng. Nhiều báo cáo nhầm chỗ
  này — nêu đúng sẽ được đánh giá cao.
- **Learning rate** ([S8] slide 55–61): quá lớn thì phân kỳ, quá nhỏ thì chậm;
  các biến thể thích nghi (Adagrad, momentum — [S8] slide 26–27).
- **Nối với thực nghiệm:** E04 dùng **hai learning rate khác nhau**:
  head 1e-4, `layer4` 1e-5. Giải thích lý do ở §7.7.

## 7.4. Phép tích chập

> *Nguồn ngoài: LeCun et al., "Gradient-based learning applied to document
> recognition", Proc. IEEE, 1998.*

**Công thức (7.6).** Tích chập 2-D rời rạc:

    (I * K)(i, j) = Σ_m Σ_n I(i − m, j − n) · K(m, n)

**Nội dung cần viết**
- Ba tính chất và **ý nghĩa cụ thể với PAD**:

  | Tính chất | Ý nghĩa | Vì sao quan trọng cho PAD |
  |---|---|---|
  | Kết nối cục bộ | Mỗi nơ-ron chỉ nhìn một vùng nhỏ | Dấu vết recapture là hiện tượng cục bộ |
  | Chia sẻ trọng số | Cùng bộ lọc quét toàn ảnh | Dấu vết xuất hiện ở mọi vị trí, không cố định |
  | Bất biến tịnh tiến | Đáp ứng không đổi khi dịch chuyển | Mặt có thể ở vị trí bất kỳ trong crop |

- **Liên hệ lý thuyết đẹp cần nêu:** bộ lọc tích chập ở tầng đầu học ra các bộ
  dò cạnh và điểm — **cùng loại nguyên hàm kết cấu** mà LBP mã hóa thủ công
  (spot, edge, corner — [S3] slide 10). Khác biệt cốt lõi: LBP **cố định** các
  nguyên hàm này, CNN **học** chúng từ dữ liệu. Đây là câu trả lời khái niệm
  cho RQ1 và nên được viết thành một đoạn riêng.
- Trường tiếp nhận (receptive field) và pooling: vì sao mạng sâu "nhìn" được
  vùng rộng dần.

## 7.5. Batch Normalization

> *Nguồn ngoài: Ioffe & Szegedy, ICML 2015.*

**Công thức (7.7).**

    x̂ = (x − μ_B) / √(σ²_B + ε),    y = γ·x̂ + β

**Nội dung cần viết**
- Tác dụng: ổn định phân bố đầu vào mỗi tầng, cho phép learning rate lớn hơn,
  có tác dụng chính quy hóa nhẹ.
- **Vấn đề then chốt trong học chuyển giao** — phải viết kỹ vì nó ảnh hưởng
  trực tiếp đến E03/E04: khi đóng băng backbone, BN vẫn có hai chế độ. Nếu để
  BN ở chế độ huấn luyện, thống kê chạy (running statistics) sẽ **bị cập nhật
  theo dữ liệu mới ngay cả khi trọng số bị đóng băng** — làm mô hình thay đổi
  ngoài ý muốn. Cấu hình dự án ghi rõ
  `batch_norm: layer4_trainable_earlier_frozen`, tức chỉ BN trong `layer4`
  được cập nhật.

## 7.6. Kiến trúc: ResNet18 và MobileNetV2

### 7.6.1. Học phần dư (ResNet)

> *Nguồn ngoài: He et al., CVPR 2016.*

**Công thức (7.8).** Khối phần dư:

    y = F(x, {W_i}) + x

**Nội dung cần viết**
- Vấn đề suy thoái (degradation): mạng sâu hơn cho lỗi **huấn luyện** cao hơn —
  không phải overfitting mà là khó tối ưu.
- Vì sao kết nối tắt giúp: đường dẫn gradient trực tiếp, giảm vanishing
  gradient — nối với [S8] slide 48–50 (vanishing gradient) để **liên kết với
  giáo trình**.
- Cấu trúc ResNet18: stem → layer1 → layer2 → layer3 → layer4 → pooling → fc.
  Tổng ~11,18 triệu tham số.

### 7.6.2. Tích chập tách theo chiều sâu (MobileNetV2)

> *Nguồn ngoài: Sandler et al., CVPR 2018.*

**Công thức (7.9).** Tỉ lệ giảm chi phí tính toán:

    (D_K² · M · D_F² + M · N · D_F²) / (D_K² · M · N · D_F²) = 1/N + 1/D_K²

**Nội dung cần viết**
- Tách tích chập chuẩn thành **depthwise** (lọc theo từng kênh) + **pointwise**
  (1×1, trộn kênh).
- Với D_K = 3 → giảm khoảng 8–9 lần chi phí.
- Inverted residual và linear bottleneck (nêu ngắn).
- ~2,23 triệu tham số, checkpoint 9,15 MB so với 44,79 MB của ResNet18.
- **Giả thuyết cần đặt ra cho Chương 9:** mô hình nhỏ hơn có thể **thiếu năng
  lực** để mã hóa dấu vết vi kết cấu tinh vi — cần kiểm chứng bằng số liệu chứ
  không khẳng định trước.

## 7.7. Học chuyển giao

**Nội dung cần viết**
- Định nghĩa và động cơ: OULU-NPU Protocol 1 chỉ có 1200 video huấn luyện —
  quá ít để học một CNN sâu từ đầu. [S8] slide 45–46 (overfitting) là cơ sở lý
  thuyết cho lập luận này.
- Giả thiết nền: các tầng đầu học đặc trưng **tổng quát** (cạnh, màu, kết cấu),
  các tầng sau học đặc trưng **chuyên biệt theo tác vụ**.
- Ba mức chiến lược, trình bày thành bảng:

  | Chiến lược | Mô tả | Thí nghiệm |
  |---|---|---|
  | Feature extraction | Đóng băng toàn bộ backbone, chỉ học head | E02, E03 |
  | Fine-tune một phần | Mở khối cuối với LR nhỏ hơn | **E04** |
  | Fine-tune toàn bộ | Học lại mọi tầng | Không thực hiện — nêu lý do (dữ liệu ít) |

- **Khoảng cách miền (domain gap) — lập luận trọng tâm của E04:** ImageNet là
  tác vụ **ngữ nghĩa** (phân biệt chó/mèo/xe); PAD là tác vụ **kết cấu và tần
  số**. Hai tác vụ chia sẻ các tầng thấp nhưng phân kỳ ở các tầng cao. Do đó
  giả thuyết: **`layer4` — nơi đặc trưng chuyên biệt nhất — là khối cần được
  thích nghi nhất.** E04 kiểm chứng đúng giả thuyết này.
- Vì sao LR của `layer4` (1e-5) nhỏ hơn LR của head (1e-4) **10 lần**: head
  khởi tạo ngẫu nhiên nên cần học nhanh; `layer4` đã mang tri thức hữu ích, LR
  lớn sẽ **xóa** tri thức đó (catastrophic forgetting).

**Nối với triển khai.** `configs/models/resnet18_finetune_layer4.yaml`:
`frozen_stages: [stem, layer1, layer2, layer3]`,
`trainable_stages: [layer4, classifier]`.

## 7.8. Kết luận chương

---

# CHƯƠNG 8. LÝ THUYẾT ĐÁNH GIÁ VÀ RA QUYẾT ĐỊNH
*(5–6 trang)*

## 8.1. Vì sao độ chính xác không dùng được

**Nội dung cần viết**
- Protocol 1 test: 480 spoof / 120 live. Một bộ phân lớp luôn trả `spoof` đạt
  **80% accuracy** nhưng chặn 100% người dùng hợp lệ → vô dụng.
- Ma trận nhầm lẫn và bốn đại lượng TP, TN, FP, FN. Quy ước của dự án:
  `positive_class: spoof`, `positive_label: 1` — **phải nêu rõ quy ước này**,
  vì dấu của mọi chỉ số phụ thuộc vào nó.

**Công thức (8.1)–(8.3).** Precision, Recall, F1.

- Vì sao F1 **vẫn chưa đủ**: F1 tính trên lớp dương (spoof) nên **không phản
  ánh** tỉ lệ từ chối nhầm người thật. Minh chứng số sẽ có ở §9.2: E01 đạt F1
  test 90,26% trong khi từ chối nhầm **60%** người live. Đây là câu trả lời
  trực tiếp cho **RQ5** và là một trong những điểm sắc sảo nhất của báo cáo.

## 8.2. Bộ chỉ số chuẩn ISO/IEC 30107-3

**Công thức (8.4).** APCER — tỉ lệ tấn công bị phân loại nhầm thành thật:

    APCER = FN / (TP + FN)

**Công thức (8.5).** BPCER — tỉ lệ người thật bị phân loại nhầm thành tấn công:

    BPCER = FP / (TN + FP)

**Công thức (8.6).** ACER:

    ACER = (APCER + BPCER) / 2

**Nội dung cần viết**
- **Ý nghĩa an ninh bất đối xứng — mục phải viết bằng văn xuôi, không chỉ công
  thức:** APCER cao là **lỗ hổng bảo mật** (kẻ tấn công lọt qua); BPCER cao là
  **lỗi trải nghiệm** (người thật bị chặn). Trong hệ thống thanh toán, APCER
  nghiêm trọng hơn; trong hệ thống mở khóa điện thoại, BPCER lại gây khó chịu
  nhiều hơn. ACER trung bình hóa hai loại nên **giả định chúng quan trọng như
  nhau** — một giả định cần được nêu tường minh chứ không nhận mặc định.
- Đối chiếu với phương pháp đánh giá tổng quát trong [HFR] Ch.21 tr. 551–574:
  đường ROC, DET, EER.
- Nêu **EER** và vì sao dự án dùng ngưỡng dev-EER làm chính sách phụ để tương
  thích với quy ước báo cáo OULU.

## 8.3. Chọn ngưỡng

**Nội dung cần viết**
- Mô hình sinh ra **điểm số liên tục** (`decision_function` cho SVM, `logit`
  cho CNN); quyết định nhị phân đòi hỏi một ngưỡng τ.
- **Nguyên tắc bất khả xâm phạm:** τ được chọn **chỉ trên tập dev**, không bao
  giờ trên test. Cấu hình khóa điều này: `test_used_for_selection: false`.
- Mục tiêu chọn ngưỡng của dự án: cực tiểu ACER, với thứ tự phá hòa
  `[acer, apcer, threshold]` — nêu vì sao cần quy tắc phá hòa tất định (để tái
  lập được khi nhiều ngưỡng cho cùng ACER).
- Phân biệt ngưỡng **frame-level** và **video-level**, được chọn độc lập.

**Nối với triển khai.** `evaluation/threshold.py`, `threshold.json` trong mỗi
thư mục run.

## 8.4. Gộp điểm theo video

**Công thức (8.7).** Trung bình điểm số qua các frame:

    s_video = (1/N) · Σ_{k=1}^{N} s_k,   N = 10

**Nội dung cần viết**
- Cơ sở lý thuyết: nếu nhiễu trên từng frame **độc lập và không thiên lệch**,
  trung bình hóa giảm phương sai theo hệ số 1/N.
- **Vì sao giả thiết này có thể sai** — đây là điểm phân tích quan trọng: các
  frame trong cùng một video **tương quan mạnh** (cùng thiết bị, cùng ánh sáng,
  cùng PAI). Nếu sai số là **thiên lệch có hệ thống** chứ không phải nhiễu ngẫu
  nhiên, trung bình hóa **không** khử được nó, mà chỉ làm mượt. Đây là lời giải
  thích cho hiện tượng E01 có ACER video **xấu hơn** ACER frame — trả lời **RQ4**.
- Nêu các phương án khác để đối chiếu: max, median, bỏ phiếu đa số, học có
  trọng số theo thời gian.

**Nối với triển khai.** `evaluation/aggregation.py`,
`aggregation: mean_decision_score`.

## 8.5. Chống rò rỉ dữ liệu

**Nội dung cần viết.** Liệt kê các cơ chế và giải thích **vì sao mỗi cơ chế cần
thiết**, không chỉ liệt kê:
- Tách rời train / dev / test theo **định danh video và định danh chủ thể**
  (`require_disjoint_video_ids`, `require_disjoint_subjects`) — nếu cùng một
  người xuất hiện ở cả train và test, mô hình có thể nhận ra *người* thay vì
  nhận ra *dấu vết spoof*.
- Ước lượng μ, σ chuẩn hóa chỉ trên train.
- Test chỉ được đánh giá **sau khi** checkpoint và ngưỡng đã bị khóa.
- Dữ liệu thô bất biến (`raw_data_immutable: true`).
- Cố định seed (42) và lưu `environment.json`, `run_manifest.json`.

## 8.6. Kết luận chương

---

# CHƯƠNG 9. THỰC NGHIỆM, KẾT QUẢ VÀ THẢO LUẬN
*(8–10 trang)* — **Phần minh chứng: mọi con số phải đọc từ `artifacts/runs/`**

## 9.1. Bộ dữ liệu và pipeline tổng thể

- OULU-NPU Protocol 1: train 1200 video (240 live / 960 spoof), dev 900
  (180/720), test 600 (120/480). Hai PAI: ảnh in, video phát lại.
- Sơ đồ pipeline đầy đủ, **đối chiếu với sơ đồ lý thuyết [S2] slide 8** đã lập
  ở §3.3.
- Bảng kiểm kê frame: train 12 000, dev 8 999, test 6 000.
  *(Lưu ý: dev là 8 999 chứ không phải 9 000 — cần giải thích chênh lệch một
  frame này, hoặc kiểm tra lại `validation_protocol1.json`. Một sai lệch nhỏ
  được giải thích minh bạch sẽ tạo ấn tượng tốt hơn là làm tròn cho đẹp.)*

## 9.2. Bảng truy vết lý thuyết → triển khai

**Đây là bảng quan trọng nhất của toàn báo cáo cho một môn học thiên lý
thuyết.** Mỗi dòng nối một khái niệm lý thuyết với tham số và vị trí mã nguồn:

| Lý thuyết | Mục | Tham số thực tế | Mã nguồn |
|---|---|---|---|
| Lấy mẫu đều | §4.2 | `frames_per_video: 10` | `data/frame_sampler.py` |
| Phát hiện mặt | §4.3 | `mediapipe, margin 0.2` | `data/preprocess.py` |
| Nội suy area | §4.5 | `resize_interpolation: area`, 128px | `models/lbp_svm.py` |
| Nội suy bilinear | §4.5 | `bilinear, antialias, 224px` | `data/cnn_dataset.py` |
| Chuẩn hóa ImageNet | §4.6 | `mean/std` | `data/cnn_dataset.py` |
| LBP uniform | §5.2–5.4 | `radius 1, points 8, bins 10` | `features/lbp.py` |
| Histogram không gian | §5.5 | `grid 8×8 → 640-D, L1/ô` | `features/lbp.py` |
| SVM biên cực đại | §6.2–6.3 | `LinearSVC, l2, squared_hinge` | `models/lbp_svm.py` |
| Tham số C | §6.4 | lưới 6 giá trị, chọn trên dev | `selection/c_search.csv` |
| Cân bằng lớp | §6.6 | `class_weight: balanced` | `models/lbp_svm.py` |
| Học chuyển giao | §7.7 | `frozen_stages`, LR kép | `training/resnet_experiment.py` |
| Sigmoid + BCE | §7.2 | `BCEWithLogitsLoss` | `training/*_experiment.py` |
| Chọn ngưỡng | §8.3 | `select_on_dev`, min-ACER | `evaluation/threshold.py` |
| Gộp video | §8.4 | `mean_decision_score` | `evaluation/aggregation.py` |
| APCER/BPCER/ACER | §8.2 | — | `evaluation/metrics.py` |

## 9.3. Kết quả chính ở cấp video

Bảng kết quả (đọc từ artifact — số liệu hiện có):

| Mô hình | Dev ACER | Test F1 | Test APCER | Test BPCER | **Test ACER** |
|---|---:|---:|---:|---:|---:|
| E01 — LBP + SVM | 10,97% | 90,26% | 5,42% | 60,00% | **32,71%** |
| E02 — MobileNetV2 head-only | 13,75% | 85,62% | 19,38% | 30,83% | **25,10%** |
| E03 — ResNet18 head-only | 13,06% | 85,49% | 20,21% | 27,50% | **23,85%** |
| E04 — ResNet18 fine-tune `layer4` | 2,57% | 94,29% | 5,42% | 24,17% | **14,79%** |

Kèm: confusion matrix (`figures/test_confusion.png`), khoảng cách dev–test,
bảng frame-level vs video-level, kết quả theo chính sách dev-EER, và bảng chi
phí (tham số, dung lượng checkpoint, thời gian huấn luyện, độ trễ suy luận).

## 9.4. Ablation phạm vi fine-tune

E03 so E04: mọi yếu tố giữ nguyên (cùng dữ liệu, cùng crop, cùng evaluator,
cùng seed), chỉ mở `layer4`. Kết quả: **ACER test giảm 9,06 điểm phần trăm**.
Đây là thiết kế ablation sạch và cần được trình bày như vậy.

## 9.5. Thảo luận: lý thuyết giải thích kết quả như thế nào?

**Đây là mục thể hiện năng lực tổng hợp — cần viết bằng văn xuôi phân tích, mỗi
tiểu mục 3–5 đoạn.**

### 9.5.1. Vì sao E01 tốt trên dev nhưng sụp trên test?
Nối về §5.3 (chỉ một tỉ lệ R=1), §4.1 (mất thông tin màu), §4.5 (thu nhỏ về
128px là lọc thông thấp, có thể đã xóa dấu vết tần số cao) và §3.4 (đặc trưng
tốt phải có phương sai nội lớp nhỏ — LBP không đạt khi điều kiện thu nhận đổi).
Chỉ ra: BPCER test 60% nghĩa là ngưỡng chọn trên dev **không chuyển được** sang
phân bố test — đây là biểu hiện kinh điển của domain shift.

### 9.5.2. Vì sao MobileNetV2 không thắng ResNet18?
Nối về §7.6.2: kiểm chứng hay bác bỏ giả thuyết "năng lực mô hình" bằng chênh
lệch thực tế 1,25 điểm ACER — một khoảng cách **nhỏ**, nên cần thận trọng
không diễn giải quá mức từ một seed.

### 9.5.3. E04 dưới góc nhìn học chuyển giao
Nối về §7.7: xác nhận giả thuyết khoảng cách miền. Nhưng cũng phải nêu: dev–test
gap vẫn còn **12,22 điểm** — mô hình đã thích nghi tốt hơn *nhưng chưa tổng
quát hóa*.

### 9.5.4. Vai trò của cân bằng lớp và chỉ số đối xứng
Nối §6.6 và §8.1: E01 có F1 cao nhưng BPCER thảm hại — bằng chứng số cụ thể
cho luận điểm lý thuyết ở §8.1. **Trả lời RQ5.**

### 9.5.5. Vì sao trung bình theo video có thể thất bại?
Nối §8.4: sai số tương quan trong video không bị khử bởi trung bình hóa.
**Trả lời RQ4.**

## 9.6. Trả lời năm câu hỏi nghiên cứu

Năm đoạn, mỗi đoạn trả lời dứt khoát một RQ và **dẫn số liệu cụ thể** làm bằng
chứng. Nếu dữ liệu chưa đủ để kết luận, nói thẳng là chưa đủ.

## 9.7. Các đe dọa tới tính hợp lệ

- **Hợp lệ nội tại:** một seed duy nhất; không có khoảng tin cậy.
- **Hợp lệ ngoại tại:** chỉ Protocol 1; không cross-dataset; không kết luận
  được về khả năng tổng quát hóa.
- **Hợp lệ cấu trúc:** ACER giả định hai loại lỗi quan trọng như nhau — giả
  định này có thể không đúng với ứng dụng thực tế.
- **Hợp lệ kết luận:** chênh lệch 1,25 điểm giữa E02 và E03 có thể nằm trong
  dao động ngẫu nhiên giữa các seed.

---

# CHƯƠNG 10. KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN
*(2–3 trang)*

## 10.1. Kết luận

Ba đoạn: *(1)* những gì đã xây dựng và chứng minh; *(2)* kết quả định lượng
chính; *(3)* những gì **chưa** chứng minh được. Không tuyên bố vượt quá dữ liệu.

## 10.2. Hướng phát triển theo thứ tự ưu tiên

| Ưu tiên | Hướng | Cơ sở lý thuyết |
|---|---|---|
| 1 | Chạy nhiều seed, báo cáo khoảng tin cậy | §9.7 |
| 2 | LBP đa tỉ lệ (nhiều cặp P, R) | §5.3, [HFR] §4.3.1.3 |
| 3 | LBP-TOP khai thác thông tin thời gian | §4.2, [HFR] §4.3.1.2 |
| 4 | LBP trên các kênh màu thay vì ảnh xám | §4.1 |
| 5 | SVM nhân RBF | §6.5 |
| 6 | Đối chứng PCA/LDA trên đặc trưng LBP | §5.6 |
| 7 | Đánh giá cross-dataset (Replay-Attack, CASIA) | §9.7 |
| 8 | Fine-tune sâu hơn (`layer3` + `layer4`) | §7.7 |

---

# TÀI LIỆU THAM KHẢO

Đề xuất chia hai nhóm, đánh số liên tục theo IEEE.

**Nhóm A — Giáo trình và bài giảng môn học**

1. Thái Hoàng Lê, *Nhân trắc học*, Khoa CNTT, ĐH KHTN TP.HCM. [S1]
2. Lê Hoàng Thái, *Nhận dạng mẫu và ứng dụng thử nghiệm*. [S2]
3. *Local Binary Patterns* (slide bài giảng). [S3]
4. A. van Erk, *Principal Component Analysis — Some Mathematical Backgrounds*,
   BiGCaT. [S4]
5. *Dimensionality Reduction Using PCA/LDA — Case Studies*, CS 479/679 Pattern
   Recognition. [S5]
6. J. Ye, *PCA and LDA for Feature Reduction*, Arizona State University. [S6]
7. J. Gu, *An Introduction of Support Vector Machine*, 2008. [S7]
8. H.-y. Lee, *Deep Learning Tutorial*. [S8]
9. S. Z. Li, A. K. Jain (eds.), *Handbook of Face Recognition*, 2nd ed.,
   Springer, 2011. [HFR]
10. A. K. Jain, P. Flynn, A. Ross (eds.), *Handbook of Biometrics*, Springer,
    2008. [HB]

**Nhóm B — Công trình gốc được viện dẫn**

11. T. Ojala, M. Pietikäinen, D. Harwood, "A comparative study of texture
    measures with classification based on featured distributions", *Pattern
    Recognition*, 29(1), 1996.
12. T. Ojala, M. Pietikäinen, T. Mäenpää, "Multiresolution gray-scale and
    rotation invariant texture classification with local binary patterns",
    *IEEE TPAMI*, 24(7), 2002.
13. T. Ahonen, A. Hadid, M. Pietikäinen, "Face description with local binary
    patterns", *IEEE TPAMI*, 28(12), 2006.
14. C. Cortes, V. Vapnik, "Support-vector networks", *Machine Learning*, 20(3),
    1995.
15. M. Turk, A. Pentland, "Eigenfaces for recognition", *J. Cognitive
    Neuroscience*, 3(1), 1991.
16. P. Belhumeur, J. Hespanha, D. Kriegman, "Eigenfaces vs. Fisherfaces",
    *IEEE TPAMI*, 19(7), 1997.
17. A. Martinez, A. Kak, "PCA versus LDA", *IEEE TPAMI*, 23(2), 2001.
18. Y. LeCun et al., "Gradient-based learning applied to document recognition",
    *Proc. IEEE*, 86(11), 1998.
19. S. Ioffe, C. Szegedy, "Batch normalization", *ICML*, 2015.
20. K. He, X. Zhang, S. Ren, J. Sun, "Deep residual learning for image
    recognition", *CVPR*, 2016.
21. M. Sandler et al., "MobileNetV2: Inverted residuals and linear
    bottlenecks", *CVPR*, 2018.
22. Z. Boulkenafet et al., "OULU-NPU: A mobile face presentation attack
    database with real-world variations", *IEEE FG*, 2017.
23. Z. Boulkenafet, J. Komulainen, A. Hadid, "Face spoofing detection using
    colour texture analysis", *IEEE TIFS*, 11(8), 2016.
24. ISO/IEC 30107-3:2017, *Information technology — Biometric presentation
    attack detection — Part 3: Testing and reporting*.

> **Kiểm tra trước khi nộp:** mọi tài liệu trong danh sách phải thực sự được
> trích dẫn trong thân bài. Ngược lại, mọi trích dẫn trong thân bài phải có
> trong danh sách.

---

# PHỤ LỤC

**Phụ lục A — Bản đồ artifact.** Bảng ánh xạ từng bảng/hình trong báo cáo tới
đường dẫn artifact sinh ra nó, để người chấm có thể kiểm chứng.

**Phụ lục B — Cấu hình cốt lõi.** Trích các file YAML then chốt:
`configs/data/oulu_protocol1.yaml`, `configs/models/lbp_svm.yaml`,
`configs/models/resnet18_finetune_layer4.yaml`.

**Phụ lục C — Môi trường tái lập.** Nội dung `environment.json`,
`run_manifest.json`, seed, phiên bản thư viện, cấu hình phần cứng.

**Phụ lục D — Checklist trước khi nộp.**

- [ ] Điền đầy đủ thông tin trang bìa
- [ ] Mục lục, danh mục hình, danh mục bảng đã cập nhật
- [ ] Mọi công thức được đánh số và mọi ký hiệu được giải thích khi xuất hiện lần đầu
- [ ] Mọi hình/bảng được viện dẫn ít nhất một lần trong văn bản
- [ ] Mọi số liệu khớp với artifact (không có số nào gõ tay mà không kiểm tra)
- [ ] Mọi trích dẫn slide/sách đã đối chiếu đúng số slide và số trang
- [ ] Ghi chú minh bạch: phần CNN không có trong slide môn học
- [ ] Thống nhất dấu thập phân (dấu phẩy) trong toàn bộ báo cáo
- [ ] Kiểm tra chính tả và thuật ngữ tiếng Việt nhất quán
- [ ] Xuất PDF, kiểm tra không vỡ bảng và công thức

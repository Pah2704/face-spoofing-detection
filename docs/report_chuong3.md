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
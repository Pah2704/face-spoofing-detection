# Kế hoạch triển khai dự án Face Spoofing Detection trên OULU-NPU

> Nguồn yêu cầu: de_cuong_chi_tiet_face_spoofing_oulu_npu.md
> Trạng thái dữ liệu: Protocol 1 đã ingest, preprocess và kiểm tra hoàn tất
> Phạm vi chính: OULU-NPU Protocol 1, ba mô hình LBP-SVM, MobileNetV2 và ResNet18

## 1. Kết quả cần đạt

Xây dựng một pipeline tái lập được từ video OULU-NPU đến báo cáo so sánh ba mô hình:

~~~text
OULU-NPU gốc
  -> kiểm tra dữ liệu và đọc split Protocol 1
  -> tạo video manifest
  -> lấy đều 10 frame/video
  -> phát hiện và crop khuôn mặt
  -> tạo frame manifest
  -> huấn luyện LBP-SVM / MobileNetV2 / ResNet18
  -> dự đoán từng frame
  -> gộp score theo video
  -> chọn threshold trên dev
  -> đánh giá test
  -> sinh bảng, biểu đồ và phân tích trade-off
~~~

Đầu ra cuối cùng phải trả lời được ba câu hỏi:

1. Mô hình nào có ACER và F1 tốt nhất ở video-level?
2. Video-level có ổn định hơn frame-level không?
3. Mô hình nào cân bằng tốt nhất giữa chất lượng, kích thước và tốc độ?

## 2. Phạm vi đã khóa

| Hạng mục | Quyết định chính |
|---|---|
| Dataset | OULU-NPU |
| Protocol | Protocol 1 |
| Bài toán | Nhị phân: Live và Spoof |
| Quy ước nhãn | live = 0, spoof = 1 |
| Lớp dương | Spoof / Attack |
| Mô hình | LBP-SVM, MobileNetV2, ResNet18 |
| Frame sampling | 10 frame/video, lấy đều và xác định |
| Đầu vào LBP | Grayscale 128 x 128 |
| Đầu vào CNN | RGB 224 x 224, ImageNet normalization |
| Face detector mặc định | MediaPipe; tham số được cấu hình và crop được cache |
| Crop margin ban đầu | 20%, có thể chỉnh bằng dev/QC trước khi train |
| Gộp video | Trung bình score/xác suất spoof |
| Metric chính | Video-level ACER và F1 |
| Metric phụ | Accuracy, Precision, Recall, APCER, BPCER, confusion matrix |
| Model selection | Dựa trên video-level ACER của dev |
| Threshold | Chọn trên dev, khóa trước khi chạy test |
| Seed chính | 42 |

Quy tắc threshold mặc định là tối thiểu hóa ACER trên dev. Nếu nhiều threshold bằng nhau, ưu tiên APCER thấp hơn. Trước khi chốt số liệu báo cáo, evaluator phải được đối chiếu với quy ước hoặc script đánh giá chính thức đi kèm OULU-NPU; nếu khác, quy trình chính thức được ưu tiên và phải ghi rõ trong báo cáo.

## 3. Ngoài phạm vi critical path

Các mục sau chỉ thực hiện sau khi E01-E03 hoàn tất:

- Protocol 2-4.
- Dataset Replay-Attack hoặc cross-dataset.
- Attention/temporal pooling.
- Few-shot, meta-learning hoặc domain adaptation.
- CDCN/CDCN++ hay mô hình SOTA chuyên biệt.
- 3D mask và deepfake.

## 4. Kiến trúc repository mục tiêu

Đây là cấu trúc mục tiêu. Package dữ liệu, CLI, evaluator, E01 LBP-SVM và bộ
khung artifact đã được dựng; các module CNN được bổ sung ở Phase 5-6.

~~~text
.
├── README.md
├── pyproject.toml
├── configs/
│   ├── data/oulu_protocol1.yaml
│   ├── models/lbp_svm.yaml
│   ├── models/mobilenet_v2.yaml
│   ├── models/resnet18.yaml
│   └── experiments/e01_lbp_svm.yaml
├── data/
│   ├── raw/oulu_npu/              # chép dữ liệu giải nén vào đây
│   ├── interim/frames/             # frame được lấy đều, theo video_id
│   ├── processed/faces/            # crop dùng chung cho cả ba mô hình
│   ├── processed/features/lbp/     # cache đặc trưng LBP
│   ├── manifests/                  # videos.csv và frames.csv
│   └── quality_control/            # montage và báo cáo kiểm tra crop
├── src/face_spoofing/
│   ├── data/
│   │   ├── protocol.py
│   │   ├── validate.py
│   │   ├── frame_sampler.py
│   │   ├── face_cropper.py
│   │   └── dataset.py
│   ├── features/lbp.py
│   ├── models/
│   │   ├── lbp_svm.py
│   │   ├── mobilenet_v2.py
│   │   └── resnet18.py
│   ├── training/
│   ├── evaluation/
│   │   ├── aggregation.py
│   │   ├── metrics.py
│   │   ├── threshold.py
│   │   └── evaluator.py
│   └── utils/
├── scripts/
├── tests/
├── artifacts/runs/
└── reports/
    ├── figures/
    └── tables/
~~~

Không tổ chức crop chỉ bằng các thư mục train/live, train/spoof vì cách đó dễ làm mất quan hệ frame-video. Mọi crop được lưu theo video_id; split và label do manifest quản lý.

## 5. Data contract

### 5.1. Nguyên tắc

- data/raw/oulu_npu/ là bất biến: không đổi tên, không di chuyển và không ghi đè file gốc.
- Split được lấy từ Protocol 1 chính thức, không tự chia ngẫu nhiên.
- Tất cả frame của một video luôn thuộc cùng một split.
- Ba mô hình dùng cùng video manifest, frame index và face crop.
- Mọi path trong manifest là path tương đối so với project root.
- Score càng cao luôn có nghĩa là càng nghiêng về Spoof.
- Không âm thầm bỏ video/frame lỗi; lỗi phải có status và lý do.

### 5.2. Video manifest

File mục tiêu: data/manifests/videos_protocol1.csv

| Cột | Ý nghĩa |
|---|---|
| video_id | ID duy nhất, ổn định |
| video_path | Đường dẫn video gốc |
| split | train, dev hoặc test |
| label | 0 = live, 1 = spoof |
| label_name | live hoặc spoof |
| protocol | protocol_1 |
| attack_type | print/replay/unknown nếu metadata có |
| subject_id | ID chủ thể nếu metadata có |
| device_id | ID thiết bị nếu metadata có |
| readable | Video có mở được hay không |
| num_frames | Tổng số frame đọc từ video |
| fps | FPS đọc được |

### 5.3. Frame manifest

File mục tiêu: data/manifests/frames_protocol1.csv

| Cột | Ý nghĩa |
|---|---|
| frame_id | ID duy nhất |
| video_id | Khóa liên kết video |
| sample_index | Vị trí mẫu từ 0 đến 9 trong video |
| frame_index | Chỉ số frame gốc |
| timestamp_ms | Thời điểm trong video |
| split | Kế thừa từ video |
| label | Kế thừa từ video |
| source_video_path | Video nguồn; không lưu full frame để tiết kiệm ổ đĩa |
| source_frame_count/source_fps | Metadata dùng để tái lập sampling |
| face_path | Crop khuôn mặt |
| face_detected | Có phát hiện mặt hay không |
| detector_status | ok/no_face/read_error/... |
| detector_score | Confidence của MediaPipe |
| crop_bbox_x1...crop_bbox_y2 | Crop vuông sau khi thêm margin, trong tọa độ frame nguồn |
| crop_size | Kích thước PNG đầu ra, mặc định 256 |
| preprocess_version/fingerprint | Phiên bản pipeline và hash cấu hình |

Full frame không được ghi ra đĩa. Mỗi crop có thể tái tạo từ
source_video_path, frame_index và cấu hình preprocessing.

## 6. Quy tắc tái lập và chống leakage

1. Lấy frame bằng các vị trí cách đều từ đầu đến cuối video; cùng video và config phải sinh đúng cùng frame_index.
2. Không split ở cấp frame và không dùng random sampler để tạo train/dev/test.
3. Mọi tham số, hyperparameter, threshold và checkpoint chỉ được chọn bằng train/dev.
4. Test chỉ được chạy sau khi model, preprocessing và threshold đã khóa.
5. SVM scaler/feature transform chỉ fit trên train.
6. Nếu hiệu chỉnh probability cho SVM, các fold phải được group theo video_id.
7. Early stopping của CNN dùng video-level ACER trên dev.
8. Mỗi run lưu config resolved, seed, môi trường, checkpoint, threshold, prediction và metrics.

## 7. Work breakdown structure

### Phase 0 — Nền tảng kỹ thuật, chưa cần dataset

Mục tiêu: dựng project có thể cấu hình, test và báo lỗi rõ khi data chưa tồn tại.

Công việc:

- Tạo package Python, dependency file và README.
- Định nghĩa config schema, label mapping và manifest schema.
- Dựng CLI validate, prepare, train, evaluate và benchmark.
- Cài evaluation engine bằng dữ liệu giả nhỏ.
- Viết unit test cho metric, aggregation, threshold và leakage.

Nghiệm thu:

- Import package không lỗi.
- Các CLI có --help.
- Validator khi chưa có dữ liệu trả thông báo chỉ đúng data/raw/oulu_npu/, không in stack trace khó hiểu.
- Test xác nhận live = 0, spoof = 1.
- Test tính tay xác nhận APCER, BPCER và ACER.
- Test chặn video_id xuất hiện ở nhiều split.

Ước lượng: 1-1.5 ngày.

### Phase 1 — Nhận và kiểm tra OULU-NPU

Phụ thuộc: người dùng chép dữ liệu vào data/raw/oulu_npu/.

Công việc:

- Khảo sát đúng layout của bản dữ liệu đã tải.
- Xác định video và file protocol/split.
- Tạo video manifest cho Protocol 1.
- Kiểm tra file thiếu, hỏng, trùng ID và nhãn không hợp lệ.
- Sinh thống kê theo split và label.

Nghiệm thu:

- 100% video hợp lệ có video_id, path, split và label.
- Mọi path tồn tại và video được mở thử.
- Train/dev/test không giao nhau theo video_id.
- Số lượng theo split/label khớp metadata chính thức hoặc mọi sai khác có báo cáo.
- Không chỉnh sửa dữ liệu raw.

Ước lượng: 0.5-1 ngày.

### Phase 2 — Trích frame và crop mặt dùng chung

Công việc:

- Lấy đều 10 frame/video.
- Phát hiện khuôn mặt bằng MediaPipe.
- Mở rộng bounding box 20%, clip trong biên ảnh và lưu crop.
- Ghi đầy đủ trạng thái detector.
- Sinh montage QC cho cả split và nhãn.

Chính sách lỗi:

- Thử detector đúng theo cấu hình đã khóa.
- Nếu không thấy mặt, ghi no_face; không âm thầm dùng center crop.
- Video thiếu crop được đưa vào báo cáo ngoại lệ trước khi huấn luyện.
- Nếu tỷ lệ thành công thấp, điều chỉnh detector/margin trên train/dev rồi chạy lại toàn bộ cache.

Nghiệm thu:

- Chạy lại cùng config sinh cùng frame index.
- Mỗi crop truy ngược được đến video và frame nguồn.
- Ba mô hình dùng cùng crop.
- Có thống kê tỷ lệ phát hiện mặt theo split/label.
- Mục tiêu tối thiểu 98% sampled frame có crop hợp lệ; nếu thấp hơn phải xử lý và ghi rõ nguyên nhân trước khi chuyển phase.
- QC thủ công tối thiểu 100 crop phân bố đều giữa train/dev/test và live/spoof.

Ước lượng: 1-2 ngày, chưa tính thời gian máy chạy.

### Phase 3 — Evaluation engine

Công việc:

- Chuẩn hóa prediction schema ở frame-level.
- Mean aggregation theo video_id.
- Chọn threshold trên dev.
- Tính Accuracy, Precision, Recall, F1, APCER, BPCER và ACER.
- Sinh confusion matrix và prediction CSV.

Nghiệm thu:

- Metric đúng trên các ca kiểm thử tính tay, kể cả thiếu một lớp.
- Mỗi video chỉ có đúng một dòng video prediction.
- Evaluator test không có đường code tối ưu threshold trên test.
- Threshold và quy tắc chọn được lưu cùng run.
- Cách tính được đối chiếu với protocol/evaluator chính thức của OULU-NPU.

Ước lượng: 1 ngày.

### Phase 4 — E01: LBP-SVM

Trạng thái: **hoàn tất ngày 12/07/2026**. Báo cáo tại
`docs/ket_qua_e01_lbp_svm.md`; run đã khóa tại
`artifacts/runs/lbp_svm/e01_20260712_lbp_svm_seed42_verified/`.

Cấu hình chính:

- Grayscale 128 x 128.
- Uniform LBP, radius = 1, points = 8.
- Histogram chuẩn hóa.
- Linear SVM.
- Mean decision score ở video-level.

Công việc:

- [x] Cache feature theo frame.
- [x] Train trên train.
- [x] Chọn C và threshold bằng dev.
- [x] Khóa model rồi đánh giá test.

Nghiệm thu:

- [x] Model, config LBP, scaler và threshold được lưu.
- [x] Có prediction/metric frame-level và video-level cho dev/test.
- [x] Load artifact và infer lại cho kết quả nhất quán.

Kết quả video-level: dev ACER 10,97%, test ACER 32,71%. Test BPCER 60,00%
cho thấy baseline lệch mạnh sang dự đoán spoof trên live test; không tune lại
bằng test.

Ước lượng: 1 ngày.

### Phase 5 — E02: MobileNetV2

Trạng thái: **hoàn tất**. Báo cáo tại `docs/ket_qua_e02_mobilenet_v2.md`;
run chính tại `artifacts/runs/mobilenet_v2/e02_20260712_mobilenet_v2_seed42/`.

Cấu hình chính:

- ImageNet pretrained.
- RGB 224 x 224.
- Train classifier head trước, backbone freeze.
- Cross-Entropy, Adam, learning rate 1e-4.
- Batch size 8 hoặc 16 theo bộ nhớ.
- Tối đa 15 epoch, early stopping theo dev video ACER.

Công việc:

- [x] Chạy và tái lập smoke test 1 epoch.
- [x] Chạy main training 15 epoch.
- [x] Lưu best checkpoint theo dev.
- [x] Chọn threshold dev rồi đánh giá test.

Nghiệm thu:

- [x] Loss hữu hạn và checkpoint load được.
- [x] Checkpoint chứa label mapping và preprocessing config.
- [x] Không dùng test để early stop.
- [x] Prediction và metric đầy đủ ở hai cấp.

Kết quả video-level: dev ACER 13,75%, test ACER 25,10%. Best checkpoint là
epoch 15; test chỉ được dựng sau marker khóa checkpoint/threshold.

Ước lượng: 1-2 ngày, chưa tính thời gian huấn luyện.

### Phase 6 — E03: ResNet18

Trạng thái: **hoàn tất**. Báo cáo tại `docs/ket_qua_e03_resnet18.md`; run
chính tại `artifacts/runs/resnet18/e03_20260713_resnet18_seed42/`.

Cấu hình và quy trình tương tự MobileNetV2:

- ImageNet pretrained, RGB 224 x 224.
- Freeze backbone, train classifier head.
- Adam, learning rate 1e-4 cho head.
- Fine-tune block cuối với learning rate khoảng 1e-5 chỉ là thí nghiệm phụ.

Nghiệm thu:

- [x] Cùng split, crop, augmentation và evaluator với MobileNetV2.
- [x] Đủ artifact, prediction và metric.
- [x] Không dùng test cho model selection.

Kết quả video-level: dev ACER 13,06%, test ACER 23,85%. Best checkpoint epoch
15; test được dựng sau marker khóa checkpoint/threshold.

Ước lượng: 1-2 ngày, chưa tính thời gian huấn luyện.

### Phase 7 — So sánh, benchmark và thí nghiệm phụ

Trạng thái: **đã hoàn tất phần bắt buộc** gồm so sánh frame/video, benchmark
chuẩn hóa và error analysis. Ablation fine-tune block cuối đã hoàn tất ở E04;
các ablation 5/20 frame và nhiều seed được giữ làm hướng phát triển, không tune
bằng test hiện tại.

Thí nghiệm bắt buộc:

| ID | Mô hình | Frame/video | Kết quả |
|---|---|---:|---|
| E01 | LBP-SVM | 10 | Frame + video |
| E02 | MobileNetV2 | 10 | Frame + video |
| E03 | ResNet18 | 10 | Frame + video |

Thí nghiệm phụ theo thứ tự ưu tiên:

1. So sánh frame-level và video-level từ chính prediction E01-E03.
2. 5 so với 10 frame/video.
3. [x] Freeze backbone so với fine-tune block cuối — E03/E04.
4. Pure-model latency và end-to-end latency.
5. 20 frame/video.
6. Linear SVM so với RBF SVM.
7. Ba seed nếu tài nguyên cho phép.

Quy tắc benchmark:

- Cùng máy, device, batch size và chế độ inference.
- Có warm-up và nhiều lần lặp.
- Báo riêng pure-model và end-to-end, không trộn hai loại latency.
- Ghi số tham số, dung lượng model, train time và inference/video.

Nghiệm thu:

- Có bảng chính đủ ba mô hình.
- Có bảng frame-level so với video-level.
- Có bảng chi phí tính toán.
- Mọi so sánh dùng cùng tập video hợp lệ; nếu không, phải ghi rõ.

Ước lượng: 1 ngày.

### Phase 8 — Báo cáo và bàn giao

Trạng thái: **cập nhật hoàn tất ngày 14/07/2026**. Báo cáo độc lập tại
`docs/bao_cao_thuc_nghiem_face_spoofing_oulu_npu.md`.

Công việc:

- Sinh bảng metric và confusion matrix.
- Vẽ biểu đồ ACER/F1 so với latency/size.
- Phân tích video dự đoán sai và chất lượng crop.
- Hoàn thiện Results, Discussion, Limitations và Conclusion.
- Viết chuỗi lệnh tái lập từ raw data đến report.

Nghiệm thu:

- Bảng chính có Accuracy, Precision, Recall, F1, APCER, BPCER, ACER.
- Bảng tài nguyên có params, model size, train time và inference/video.
- Có error analysis đại diện cho false live và false spoof.
- Báo cáo không tuyên bố SOTA.
- README cho phép chạy lại toàn bộ pipeline bằng config đã lưu.

Ước lượng: 1-2 ngày.

## 8. Timeline đề xuất

Effort tổng ban đầu dự kiến là 9-13 ngày làm việc. Dữ liệu, ba baseline,
tổng hợp, benchmark, error analysis và báo cáo phần chính đã hoàn tất. Các
thí nghiệm mở rộng phụ thuộc CPU/GPU và không thuộc critical path.

| Mốc | Phase | Gate để đi tiếp |
|---|---|---|
| M0 | Nền tảng | CLI/test hoạt động khi chưa có data |
| M1 | Data ingest | Manifest hợp lệ, không leakage |
| M2 | Preprocessing | Crop QC đạt, lỗi có báo cáo |
| M3 | Evaluator | Metric và threshold đã kiểm chứng |
| M4 | Ba baseline | E01-E03 có đủ artifact |
| M5 | Tổng hợp | Bảng, benchmark, error analysis hoàn tất |
| M6 | E04 | Fine-tune layer4, artifact và báo cáo ablation hoàn tất |

Có thể làm Phase 0 và phần lớn Phase 3 trong khi chờ tải dữ liệu. Phase 1 là điểm bắt buộc phải chờ data thật.

## 9. Cấu trúc artifact cho mỗi run

~~~text
artifacts/runs/<experiment_id>/<run_id>/
├── config_resolved.json
├── environment.json
├── run_manifest.json
├── timing.json
├── result.json
├── model/
├── selection/
├── threshold.json
├── predictions/
│   ├── dev_frames.csv
│   ├── dev_videos.csv
│   ├── test_frames.csv
│   └── test_videos.csv
├── metrics/
│   ├── dev.json
│   ├── test.json
│   └── summary.json
└── figures/
~~~

run_id cần chứa timestamp, model và seed. Không ghi đè run cũ.

## 10. Rủi ro và cách kiểm soát

| Rủi ro | Kiểm soát |
|---|---|
| Layout bản tải khác dự kiến | Khảo sát sau khi copy; viết adapter thay vì đổi raw |
| Split leakage | Manifest theo video và test disjoint split |
| Crop quá sát làm mất dấu spoof | Margin cấu hình, montage QC, dùng chung crop |
| Detector bỏ sót không cân bằng giữa live/spoof | Báo tỷ lệ theo split/label và danh sách ngoại lệ |
| Frame tương quan làm kết quả quá lạc quan | Video-level là kết quả chính |
| Threshold bị tune trên test | API tách select-threshold(dev) và evaluate(test) |
| Augmentation phá texture | Main run chỉ dùng augmentation nhẹ; lưu config |
| CNN overfit | Freeze trước, early stopping trên dev, fine-tune là ablation |
| Benchmark không công bằng | Cùng máy/cấu hình và báo hai loại latency |
| Data/checkpoint bị commit | .gitignore đã chuẩn bị |
| Scope creep | Chỉ mở rộng sau khi E01-E03 hoàn thành |

## 11. Definition of Done

Dự án hoàn thành phần chính khi:

- [x] OULU-NPU Protocol 1 được ingest và kiểm tra.
- [x] Không có video_id trùng giữa train/dev/test.
- [x] 10 sample row/video và crop chung được tạo tái lập.
- [x] Evaluator ACER/APCER/BPCER được kiểm chứng.
- [x] E01 LBP-SVM hoàn tất.
- [x] E02 MobileNetV2 hoàn tất.
- [x] E03 ResNet18 hoàn tất.
- [x] E04 ResNet18 fine-tune layer4 hoàn tất.
- [x] Cả ba có frame-level và video-level metrics.
- [x] Threshold chỉ chọn trên dev.
- [x] Có benchmark tài nguyên công bằng.
- [x] Có bảng, confusion matrix và error analysis.
- [x] Có hướng dẫn tái lập và báo cáo kết luận.

## 12. Trạng thái hiện tại và bước kế tiếp

- [x] Đọc và chuyển đề cương thành implementation plan.
- [x] Chuẩn bị data/raw/oulu_npu/ để nhận dataset.
- [x] Chuẩn bị các thư mục generated data và quy tắc ignore.
- [x] Nhận 5 archive OULU-NPU và giữ nguyên bản gốc.
- [x] Giải nén chọn lọc 2.700 video của Protocol 1.
- [x] Full probe toàn bộ 2.700 video, không có lỗi.
- [x] Tạo video manifest 2.700 dòng.
- [x] Tạo frame manifest 27.000 dòng và 26.999 crop PNG hợp lệ.
- [x] Decode/kiểm tra toàn bộ crop, không leakage, duplicate hay orphan.
- [x] Tạo montage QC cân bằng 120 crop.
- [x] Hoàn tất evaluation engine và unit test nền tảng.
- [x] Triển khai và chạy E01 LBP-SVM.
- [x] Cache 26.999 feature LBP 640 chiều theo content fingerprint.
- [x] Chọn C và threshold trên dev; khóa model trước khi chạy test.
- [x] Lưu model, prediction, metric, confusion matrix và checksum E01.
- [x] Load lại model và xác nhận score dev/test nhất quán.
- [x] Triển khai và chạy E02 MobileNetV2.
- [x] Hai smoke run E02 tái lập byte-for-byte checkpoint/prediction.
- [x] Khóa checkpoint/threshold E02 trước khi dựng test dataset.
- [x] Lưu đủ 24 artifact và source snapshot E02.
- [x] Triển khai và chạy E03 ResNet18.
- [x] Hai smoke run E03 tái lập byte-for-byte checkpoint/prediction.
- [x] Lưu đủ 24 artifact và source snapshot E03.
- [x] Triển khai E04 với hai optimizer group khóa trước.
- [x] Hai smoke run E04 tái lập checkpoint/prediction/metric byte-for-byte.
- [x] Khóa checkpoint epoch 6 và threshold trước khi đánh giá test E04.
- [x] Lưu đủ 24 artifact, checksum và source snapshot E04.
- [x] So sánh E03 head-only với E04 fine-tune layer4.
- [x] Tạo bảng tổng hợp E01-E03 ở hai policy threshold.
- [x] Benchmark cùng 600 crop, batch 16, 4 worker và 3 lần lặp.
- [x] Error analysis theo model, phone, attack instrument và crop metadata.
- [x] Tối ưu threshold sweep lên O(n log n) và chứng minh tương đương exhaustive.
- [x] Hoàn thiện báo cáo Results, Discussion, Limitations và Conclusion.

Ghi chú preprocessing: video dev spoof 3_1_28_4 không có mặt ở frame 0;
metadata mắt chính thức cũng báo thất bại ở đoạn đầu. Row này được giữ với
status no_face, không thay bằng frame gần trùng sample kế tiếp. Tỷ lệ phát
hiện cuối cùng là 26.999/27.000 = 99,9963%, vượt gate 98%.

Phần chính đã hoàn tất. Bước tiếp theo, nếu mở rộng phạm vi, là chạy nhiều seed,
mở Protocol 2-4 hoặc đánh giá trên thiết bị đích. Không mở thêm tuning trên test
Protocol 1 hiện tại.

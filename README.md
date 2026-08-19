# Face Spoofing Detection trên OULU-NPU

Pipeline tái lập cho bài toán phát hiện giả mạo khuôn mặt trên OULU-NPU Protocol 1. Phạm vi baseline gồm LBP-SVM, MobileNetV2 và ResNet18; kết quả chính được đánh giá ở video-level với `live = 0`, `spoof = 1`.

## Trạng thái dữ liệu

Bản dữ liệu hiện có được giữ nguyên ở dạng archive trong:

~~~text
data/raw/oulu_npu/
├── Train_files.tar
├── Dev_files.tar
├── Test_files.tar
├── Protocols.tar
├── Baseline.tar
└── Readme.pdf
~~~

Các file Protocol 1 nằm tại `data/raw/oulu_npu/Protocols/Protocol_1/`. Số video được chỉ định bởi protocol là:

| Split | Live | Spoof | Tổng |
|---|---:|---:|---:|
| Train | 240 | 960 | 1200 |
| Dev | 180 | 720 | 900 |
| Test | 120 | 480 | 600 |

Milestone dữ liệu hiện đã hoàn tất: full-probe 2.700/2.700 video đạt; frame
manifest có 27.000 row; 26.999 crop PNG đã decode và kiểm tra đầy đủ. Một
sample dev không có mặt ở frame đầu được giữ với status `no_face`, đưa tỷ lệ
phát hiện cuối cùng về 99,9963%.

Cả ba baseline đã hoàn tất. Video ACER test lần lượt là 32,71% cho LBP-SVM,
25,10% cho MobileNetV2 và 23,85% cho ResNet18. Mọi threshold đều được khóa từ
dev, không hậu chỉnh bằng test. Kết quả tổng hợp nằm trong
`docs/ket_qua_tong_hop_e01_e03.md`; báo cáo thực nghiệm hoàn chỉnh tại
`docs/bao_cao_thuc_nghiem_face_spoofing_oulu_npu.md`.

Báo cáo môn **Xử lý ảnh nâng cao**, tập trung vào cơ sở lý thuyết và bảng truy
vết lý thuyết → mã nguồn → thực nghiệm E01–E04, nằm tại
`docs/bao_cao_mon_xu_ly_anh_nang_cao_face_spoofing.md`.

Ablation E04 fine-tune `layer4` của ResNet18 đã giảm test video ACER từ
23,85% xuống 14,79%, với cấu hình khóa trước và test chỉ chạy sau frozen
marker. Chi tiết tại `docs/ket_qua_e04_resnet18_finetune_layer4.md`.

`data/raw/` là dữ liệu gốc bất biến. Không đổi tên, ghi đè hoặc xóa các file `.tar` sau khi giải nén. Các thư mục giải nén và mọi artifact phía sau phải có thể tạo lại từ archive cùng config.

Protocol 1 đã được giải nén chọn lọc vào `Train_files/`, `Dev_files/` và
`Test_files/`. Toàn bộ archive gốc vẫn được giữ nguyên.

## Khởi tạo cho milestone dữ liệu

Các lệnh ingest/validation hiện không cần dependency ngoài Python và
`ffprobe`. Trên máy hiện tại có thể dùng Conda environment `ai_env` để chạy
milestone này mà không thay đổi các package ML đang có:

~~~bash
conda activate ai_env
python --version
python -m pip install -e . --no-deps
face-spoofing --help
~~~

E01/E02/E03 đã được chạy bằng Conda environment `ai_env`; môi trường chính xác và
source snapshot được lưu cùng từng run. Trước khi bàn giao nên tạo một
environment Python 3.10 sạch và khóa
dependency. Không cài đồng thời `opencv-python` và
`opencv-contrib-python`; project dùng gói `opencv-contrib-python`. PyTorch
CUDA được khóa riêng theo GPU/driver của máy. Luồng chuẩn bị dữ liệu không phụ
thuộc GPU.

## Luồng chuẩn bị dữ liệu

Interface CLI nằm trong nhóm lệnh `data` dưới đây. Có thể chạy bằng module
`python -m face_spoofing` hoặc executable `face-spoofing`:

~~~bash
# 1. Kiểm kê archive, protocol và layout hiện tại; không ghi dữ liệu
python -m face_spoofing data inspect \
  --raw-root data/raw/oulu_npu \
  --protocol 1

# 2a. Xem trước danh sách thành viên Protocol 1 sẽ được giải nén
python -m face_spoofing data extract \
  --raw-root data/raw/oulu_npu \
  --protocol 1 \
  --dry-run

# 2b. Giải nén chọn lọc Protocol 1 dưới raw root; không xóa archive
python -m face_spoofing data extract \
  --raw-root data/raw/oulu_npu \
  --protocol 1

# 3. Đọc Protocol 1 và tạo video manifest
python -m face_spoofing data build-manifest \
  --raw-root data/raw/oulu_npu \
  --protocol 1 \
  --output data/manifests/videos_protocol1.csv

# 4. Kiểm tra count, label, leakage và thử đọc video theo từng nhóm
python -m face_spoofing data validate \
  --raw-root data/raw/oulu_npu \
  --protocol 1 \
  --report data/manifests/validation_protocol1.json \
  --probe-per-group 1
~~~

## Tiền xử lý khuôn mặt

Smoke test cân bằng trên từng nhóm split/label:

~~~bash
PYTHONPATH=src conda run -n ai_env python -m face_spoofing data preprocess \
  --raw-root data/raw/oulu_npu \
  --output-root data/processed/faces_smoke \
  --frame-manifest data/manifests/frames_protocol1_smoke.csv \
  --summary data/manifests/preprocess_protocol1_smoke_summary.json \
  --qc-output data/quality_control/protocol1_faces_smoke_montage.jpg \
  --workers 2 \
  --limit-per-group 1
~~~

Chạy toàn bộ Protocol 1 và kiểm tra output:

~~~bash
PYTHONPATH=src conda run -n ai_env python -m face_spoofing data preprocess \
  --raw-root data/raw/oulu_npu \
  --workers 4

PYTHONPATH=src conda run -n ai_env python -m face_spoofing data validate-processed \
  --raw-root data/raw/oulu_npu
~~~

Mỗi video có metadata cache riêng nên lệnh có thể chạy lại an toàn. Cờ
`--force` chỉ dùng khi chủ động thay config hoặc muốn tạo lại crop.

Có thể thay `python -m face_spoofing` bằng `face-spoofing` trong từng lệnh. Config chuẩn tại `configs/data/oulu_protocol1.yaml` khóa data contract và tham số cho các phase tiếp theo.

`inspect` nên được chạy trước `extract`; luôn xem `--dry-run` trước lần giải nén thật. `extract` chỉ chọn các thành viên thuộc Protocol 1, không xóa archive, không giải nén ra ngoài raw root và không âm thầm ghi đè file khác nội dung. Chỉ các video được liệt kê trong Protocol 1 mới đi vào manifest.

Sau khi manifest hợp lệ, pipeline sẽ lấy đều 10 frame mỗi video, phát hiện mặt bằng MediaPipe, thêm margin 20% và lưu crop dùng chung cho cả ba baseline. Threshold chỉ được chọn trên dev; test không được dùng để chọn preprocessing, model hoặc threshold.

## Baseline E01 LBP-SVM

E01 dùng grayscale 128 x 128, uniform LBP 8-neighbour trên grid 8 x 8 và
LinearSVC. Feature cache có địa chỉ theo nội dung; scaler chỉ fit train. C và
threshold được chọn trên dev, rồi model mới được đánh giá một lần trên test.

| Split | Cấp | F1 | APCER | BPCER | ACER |
|---|---|---:|---:|---:|---:|
| Dev | Frame | 90,35% | 15,63% | 9,61% | 12,62% |
| Dev | Video | 92,91% | 10,83% | 11,11% | **10,97%** |
| Test | Frame | 89,66% | 7,92% | 53,25% | 30,58% |
| Test | Video | 90,26% | 5,42% | 60,00% | **32,71%** |

Run đã khóa: `artifacts/runs/lbp_svm/e01_20260712_lbp_svm_seed42_verified/`.

~~~bash
env OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1 \
    PYTHONPATH=src \
conda run --no-capture-output -n ai_env \
python -m face_spoofing train lbp-svm \
  --frame-manifest data/manifests/frames_protocol1.csv \
  --feature-cache-root data/processed/features/lbp \
  --run-root artifacts/runs/lbp_svm \
  --project-root . \
  --run-id <run_id_moi> \
  --feature-workers 6 \
  --seed 42 \
  --c-values 0.0001 0.001 0.01 0.1 1.0 10.0
~~~

Pipeline không ghi đè run cũ. Dùng một `run_id` mới khi tái lập.

## Baseline E02 MobileNetV2

| Split | Cấp | F1 | APCER | BPCER | ACER |
|---|---|---:|---:|---:|---:|
| Dev | Frame | 87,70% | 20,11% | 9,17% | 14,64% |
| Dev | Video | 88,38% | 19,17% | 8,33% | **13,75%** |
| Test | Frame | 84,78% | 20,79% | 30,58% | 25,69% |
| Test | Video | 85,62% | 19,38% | 30,83% | **25,10%** |

Run đã khóa:
`artifacts/runs/mobilenet_v2/e02_20260712_mobilenet_v2_seed42/`.
Xem lệnh tái lập và phân tích đầy đủ tại `docs/ket_qua_e02_mobilenet_v2.md`.

## Baseline E03 ResNet18

| Split | Cấp | F1 | APCER | BPCER | ACER |
|---|---|---:|---:|---:|---:|
| Dev | Frame | 90,80% | 13,67% | 15,28% | 14,47% |
| Dev | Video | 91,04% | 13,89% | 12,22% | **13,06%** |
| Test | Frame | 86,10% | 18,90% | 29,17% | 24,03% |
| Test | Video | 85,49% | 20,21% | 27,50% | **23,85%** |

Run đã khóa: `artifacts/runs/resnet18/e03_20260713_resnet18_seed42/`.
Chi tiết tại `docs/ket_qua_e03_resnet18.md`.

## Ablation E04 ResNet18 fine-tune layer4

E04 giữ nguyên E03 nhưng mở `layer4`; LR layer4/head lần lượt là `1e-5` và
`1e-4`. Best checkpoint epoch 6, early stopping ở epoch 9.

| Split | Cấp | F1 | APCER | BPCER | ACER |
|---|---|---:|---:|---:|---:|
| Dev | Frame | 98,31% | 2,38% | 3,89% | 3,13% |
| Dev | Video | 98,89% | 1,25% | 3,89% | **2,57%** |
| Test | Frame | 94,25% | 6,31% | 20,50% | **13,41%** |
| Test | Video | 94,29% | 5,42% | 24,17% | **14,79%** |

Run đã khóa:
`artifacts/runs/resnet18_finetune/e04_20260714_resnet18_finetune_layer4_seed42/`.
Lệnh tái lập và kiểm chứng artifact nằm trong
`docs/ket_qua_e04_resnet18_finetune_layer4.md`.

## Thư mục chính

~~~text
configs/data/oulu_protocol1.yaml   # data contract và tham số tiền xử lý
configs/models/lbp_svm.yaml        # đặc trưng và LinearSVC E01
configs/experiments/e01_lbp_svm.yaml
configs/models/mobilenet_v2.yaml   # kiến trúc/score contract E02
configs/experiments/e02_mobilenet_v2.yaml
configs/models/resnet18.yaml        # kiến trúc/score contract E03
configs/experiments/e03_resnet18.yaml
configs/models/resnet18_finetune_layer4.yaml
configs/experiments/e04_resnet18_finetune_layer4.yaml
data/raw/oulu_npu/                 # archive và dữ liệu giải nén, không commit
data/interim/frames/               # 10 frame/video
data/processed/faces/              # face crop dùng chung
data/processed/features/lbp/       # cache feature E01, không commit
data/manifests/                    # video/frame manifest
data/quality_control/              # báo cáo và montage QC
src/face_spoofing/                 # package Python theo src layout
artifacts/runs/lbp_svm/             # model, prediction và metric E01
artifacts/runs/mobilenet_v2/         # checkpoint và kết quả E02
artifacts/runs/resnet18/              # checkpoint và kết quả E03
artifacts/runs/resnet18_finetune/     # smoke/main run E04
tests/                             # unit test
~~~

Kế hoạch và tiêu chí nghiệm thu đầy đủ ở
`docs/ke_hoach_trien_khai_face_spoofing_oulu_npu.md`; kết quả E01 ở
`docs/ket_qua_e01_lbp_svm.md`, `docs/ket_qua_e02_mobilenet_v2.md` và
`docs/ket_qua_e03_resnet18.md`; kết quả E04 tại
`docs/ket_qua_e04_resnet18_finetune_layer4.md`. Benchmark và error analysis nằm tại
`docs/benchmark_tai_nguyen_e01_e03.md` và `docs/error_analysis_e01_e03.md`.
Bản báo cáo độc lập theo cấu trúc sáu chương nằm tại
`docs/bao_cao_thuc_nghiem_face_spoofing_oulu_npu.md`.

## Kiểm thử

Chạy toàn bộ unit test bằng thư viện chuẩn:

~~~bash
PYTHONPATH=src conda run --no-capture-output -n ai_env \
python -m unittest discover -s tests -p "test_*.py" -v
~~~

Hiện có 100 unit test. Các test bảo vệ mapping nhãn, count P1, ID duy nhất,
split không giao nhau, frame sampling, processed-data contract, LBP cache,
CNN dataset/model/checkpoint, source snapshot, score orientation và evaluator.

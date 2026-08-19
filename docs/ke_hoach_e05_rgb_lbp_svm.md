# Kế hoạch thực nghiệm E05 — RGB-LBP-SVM

## 1. Mục tiêu

E05 kiểm tra một câu hỏi duy nhất: **giữ nguyên toàn bộ pipeline E01, việc giữ
thông tin màu bằng LBP độc lập trên ba kênh RGB có cải thiện khả năng phát hiện
giả mạo so với LBP ảnh xám hay không?**

Đây là ablation xử lý ảnh, không phải tìm kiếm một pipeline hoàn toàn mới. Kết
quả chính được so trực tiếp với run E01 đã khóa:
`artifacts/runs/lbp_svm/e01_20260712_lbp_svm_seed42_verified/`.

## 2. Giả thuyết và biểu diễn

- **H5:** sai khác màu do máy in, màn hình, camera và quá trình recapture cung
  cấp tín hiệu bổ sung cho texture mức xám, nên RGB-LBP có thể giảm ACER.
- Ảnh crop được đọc ở BGR bằng OpenCV, đổi chính xác sang RGB.
- Tính cùng $LBP^{riu2}_{8,1}$ và histogram lưới $8\times8$ độc lập trên R, G,
  B.
- Thứ tự vector được khóa là
  $[LBP(R), LBP(G), LBP(B)]$.
- Mỗi kênh có $8\times8\times10=640$ chiều; vector cuối có 1.920 chiều.
- Histogram vẫn chuẩn hóa L1 theo từng cell của từng kênh. `StandardScaler`
  chỉ fit trên train trước `LinearSVC`.

RGB-LBP ở đây không phải opponent-color LBP, không ghép cặp chéo kênh và không
dùng HSV/YCbCr. Giới hạn này giữ phép so sánh E01/E05 dễ diễn giải.

## 3. Các yếu tố được giữ nguyên

| Thành phần | E01 và E05 |
|---|---|
| Dữ liệu | OULU-NPU Protocol 1, cùng manifest/crop |
| Sampling | 10 frame/video |
| Kích thước feature input | 128×128 |
| LBP | riu2, $P=8$, $R=1$, 10 bin, grid 8×8 |
| Classifier | `StandardScaler + LinearSVC` |
| SVM | L2, squared hinge, `dual=False`, balanced class |
| Lưới C | $10^{-4},10^{-3},10^{-2},10^{-1},1,10$ |
| Seed | 42 |
| Selection | C và threshold chỉ chọn trên dev |
| Video score | Trung bình decision score của frame |
| Metric | F1, APCER, BPCER, ACER; spoof là lớp dương |

Yếu tố duy nhất thay đổi là grayscale 640D thành ba kênh RGB 1.920D.

## 4. Quy trình triển khai

1. Mở rộng primitive LBP để nhận RGB và ghép feature theo thứ tự khóa.
2. Mở rộng content-addressed cache với `color_mode=rgb`; cache E01 cũ không
   bị thay đổi vì màu là một phần fingerprint.
3. Tạo command riêng `train rgb-lbp-svm`, config E05 và run root riêng.
4. Bổ sung unit test cho contract RGB, thứ tự kênh, số chiều và cache address.
5. Chạy smoke/unit test; xác nhận output 1.920D hữu hạn, L1-normalized.
6. Tạo full cache 26.999 frame.
7. Fit sáu giá trị C trên train, chọn C và ngưỡng frame/video bằng dev.
8. Chỉ sau khi selection hoàn tất mới lấy test feature và đánh giá một lần.
9. Lưu config, môi trường, model, dự đoán, metric, hình confusion và checksum.
10. So sánh E05 với E01 ở dev/test, frame/video, attack type và tài nguyên.

## 5. Tiêu chí nghiệm thu

- E01 grayscale vẫn tái sử dụng được cache/model cũ và toàn bộ unit test cũ
  tiếp tục pass.
- RGB feature có dtype `float32`, đúng 1.920 chiều, không NaN/Inf.
- Coverage đúng train/dev/test = 12.000/8.999/6.000 frame và 900/600 video.
- Scaler chỉ fit 12.000 train frame; score cao hơn luôn là spoof.
- Không có convergence warning trong sáu trial C.
- C, threshold và mọi lựa chọn model không đọc test.
- Model reload cho score dev/test khớp với trước khi lưu ở tolerance `1e-12`.
- Run hoàn chỉnh có checksum manifest và tài liệu kết quả.

## 6. Cách diễn giải kết quả

- Chỉ kết luận màu **có/không có ích trong cấu hình RGB-LBP này**; không suy
  rộng sang mọi color-texture descriptor.
- Nếu dev tăng nhưng test giảm, ưu tiên kết luận về domain shift/calibration,
  không chọn lại kênh hoặc C bằng test.
- Báo APCER và BPCER bên cạnh F1/ACER vì test có 80% spoof.
- Chênh lệch E01/E05 là một run seed 42, chưa phải kiểm định thống kê nhiều
  seed.

## 7. Lệnh main run dự kiến

```bash
env OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1 \
    PYTHONPATH=src \
conda run --no-capture-output -n ai_env \
python -m face_spoofing train rgb-lbp-svm \
  --frame-manifest data/manifests/frames_protocol1.csv \
  --feature-cache-root data/processed/features/rgb_lbp \
  --run-root artifacts/runs/rgb_lbp_svm \
  --project-root . \
  --run-id e05_<yyyymmdd>_rgb_lbp_svm_seed42 \
  --feature-workers 6 \
  --seed 42 \
  --c-values 0.0001 0.001 0.01 0.1 1.0 10.0
```

## 8. Trạng thái hoàn thành

- [x] Primitive RGB-LBP và contract `[R,G,B]` 1.920D.
- [x] Cache, CLI, config model/experiment và artifact runner riêng.
- [x] 106/106 unit test pass; smoke crop thật đúng dtype/shape/L1.
- [x] Main run `e05_20260721_rgb_lbp_svm_seed42` hoàn tất.
- [x] Repro run cho 13 artifact ổn định giống byte-for-byte.
- [x] 17/17 checksum main artifact hợp lệ.
- [x] Kết quả được phân tích tại `docs/ket_qua_e05_rgb_lbp_svm.md`.

Kết quả chính: selected `C=1e-4`; dev/test video ACER lần lượt 2,71%/14,17%.
E05 giảm test ACER 18,54 điểm so với E01, chủ yếu nhờ BPCER giảm 41,67 điểm;
APCER tăng 4,58 điểm. Không thay config theo test.

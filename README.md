# 📈 Tài chính hành vi Việt Nam - [Website phân tích của dự án](https://vietnam-behavioral-finance.streamlit.app/)

Bảng điều khiển phân tích thực nghiệm cho nghiên cứu:

> **"Hành vi bầy đàn có phải là cơ chế tạo ra hiệu ứng đảo ngược? Bằng chứng từ thị trường chứng khoán Việt Nam giai đoạn 2006–2025"**

## Tính năng

| Phân hệ | Mô tả |
|---|---|
| 🚨 Hệ thống cảnh báo & lọc cổ phiếu | Phát hiện tín hiệu đảo chiều, phân tán CSAD, lọc cổ phiếu theo quy mô & thanh khoản |
| 🌐 Chế độ thị trường & bầy đàn ngành | Hệ số bầy đàn β₂ theo ngành, phân phối CSAD theo chế độ thị trường |
| 🔄 Kiểm thử & mô phỏng chiến thuật | Backtest danh mục Long-Short đảo chiều hàng tuần / tháng, Sharpe, max drawdown |

## Chạy ứng dụng

```bash
pip install -r requirements.txt

# Tiếng Việt
streamlit run vn_app.py

# English
streamlit run app.py
```

## Dữ liệu

- **Giai đoạn:** 2006–2025 (19 năm, HOSE & HNX)
- **Nguồn:** vnstock — giá, khối lượng, vốn hóa, Amihud illiquidity
- **Chỉ số:** CSAD (Cross-Sectional Absolute Deviation), VNINDEX

## Cấu trúc thư mục

```
├── vn_app.py                        # Ứng dụng chính (tiếng Việt)
├── app.py                           # Ứng dụng phụ (tiếng Anh)
├── requirements.txt
├── data/processed/
│   ├── csad_daily.parquet           # CSAD toàn thị trường (2006–2025)
│   ├── firm_panel_app.parquet       # Dữ liệu cổ phiếu tối ưu hóa
│   └── macro_monthly.parquet        # Chế độ thị trường & vĩ mô tháng
└── output/tables/                   # Kết quả hồi quy thực nghiệm
```

## Triển khai

Ứng dụng được triển khai công khai tại **Streamlit Community Cloud**.

---

*Nghiên cứu học thuật — Dữ liệu cập nhật đến 31/12/2025.*

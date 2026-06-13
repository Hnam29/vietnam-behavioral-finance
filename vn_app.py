"""
Bảng điều khiển tài chính hành vi Việt Nam
=====================================
Đề tài: "Hành vi bầy đàn có phải là cơ chế tạo ra hiệu ứng đảo ngược?
        Bằng chứng từ thị trường chứng khoán Việt Nam giai đoạn 2006-2025"

Các phân hệ:
  1. 🚨 Hệ thống cảnh báo đảo chiều & lọc cổ phiếu
  2. 🌐 Chế độ thị trường & bản đồ bầy đàn ngành
  3. 🔄 Kiểm thử & mô phỏng chiến thuật đảo chiều

Sử dụng:
  streamlit run vn_app.py

Yêu cầu:
  pip install streamlit plotly pandas pyarrow numpy scipy statsmodels
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import scipy.stats as stats

# ── 1. PAGE CONFIGURATION & THEME ─────────────────────────────────────────────
st.set_page_config(
    page_title="Tài chính hành vi - Việt Nam",
    page_icon="🇻🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Tùy chỉnh CSS giao diện tối (dark-mode)
st.markdown("""
    <style>
    .reportview-container {
        background: #0b0f19;
    }
    div[data-testid="stMetricValue"] {
        font-size: 26px;
        font-weight: bold;
        color: #38bdf8;
    }
    div[data-testid="stMetricDelta"] {
        font-size: 14px;
    }
    .card {
        background-color: #1e293b;
        border-radius: 8px;
        padding: 15px;
        border: 1px solid #334155;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# ── 2. DATA LOADERS (CACHED) ───────────────────────────────────────────────────
DATA_PROCESSED = Path("data/processed")
OUTPUT_TABLES  = Path("output/tables")

@st.cache_data
def load_datasets():
    """Tải trước các tập dữ liệu parquet và bảng kết quả hồi quy."""
    data = {}

    # ── Các tệp Parquet ──
    try:
        data["csad"]       = pd.read_parquet(DATA_PROCESSED / "csad_daily.parquet")
        data["firm_panel"] = pd.read_parquet(DATA_PROCESSED / "firm_panel_app.parquet")

        # Chuẩn hóa ngày tháng
        data["csad"]["date"]       = pd.to_datetime(data["csad"]["date"])
        data["firm_panel"]["date"] = pd.to_datetime(data["firm_panel"]["date"])

        # Tích hợp động nhãn chế độ thị trường (market_regime) từ macro_monthly.parquet vào csad
        macro_m = pd.read_parquet(DATA_PROCESSED / "macro_monthly.parquet")
        data["csad"]["month"] = data["csad"]["date"].dt.to_period("M").astype(str)
        data["csad"] = data["csad"].merge(
            macro_m[["month", "market_regime"]],
            on="month",
            how="left"
        ).drop(columns=["month"])
    except Exception as e:
        st.error(
            f"⚠️ Lỗi khi tải dữ liệu parquet: {e}\n\n"
            "Vui lòng đảm bảo `run_research_analysis.py` đã được chạy và "
            "thư mục `data/processed/` chứa các tệp `.parquet` cần thiết."
        )
        st.stop()

    # ── Các bảng kết quả CSV ──
    try:
        data["t2a"]       = pd.read_csv(OUTPUT_TABLES / "T2a_Port_Weekly.csv")
        data["t5_sector"] = pd.read_csv(OUTPUT_TABLES / "T5_Sector_CSAD.csv")
        data["t7a_regime"]= pd.read_csv(OUTPUT_TABLES / "T7a_Regime_Reversal.csv")
    except Exception as e:
        st.warning(f"⚠️ Một số bảng kết quả phân tích bị thiếu: {e}. Một số biểu đồ có thể không hiển thị.")

    return data

data = load_datasets()

# ── 3. SIDEBAR NAVIGATION ──────────────────────────────────────────────────────
st.sidebar.title("🇻🇳 Vietnam Behavioral Sentinel")
st.sidebar.markdown("*Không gian phân tích thực nghiệm*")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Tính năng",
    [
        "Hệ thống cảnh báo & lọc cổ phiếu đảo chiều",
        "Chế độ thị trường & bản đồ bầy đàn ngành",
        "Kiểm thử & mô phỏng chiến thuật đảo chiều",
    ]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **Giai đoạn nghiên cứu: 2006–2025**\n\n"
    "Bảng điều khiển này trực quan hóa các kết quả nghiên cứu thực nghiệm đã được tính toán sẵn "
    "kết hợp với bộ lọc cổ phiếu động từ tập dữ liệu `firm_panel_daily.parquet`."
)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — REVERSAL SENTINEL & SCREENER
# ══════════════════════════════════════════════════════════════════════════════
if page == "Hệ thống cảnh báo & lọc cổ phiếu đảo chiều":
    st.title("🚨 Hệ thống cảnh báo - lọc cổ phiếu đảo chiều")
    st.markdown(
        "Phát hiện sự phản ứng thái quá cực đoan (tín hiệu đảo chiều) và lập bản đồ "
        "sự hội tụ / hoảng loạn trên toàn thị trường thông qua chỉ số phân tán CSAD."
    )

    # ── Khối Chỉ số (Metric) ──
    col1, col2, col3, col4 = st.columns(4)
    latest_row     = data["csad"].sort_values("date").iloc[-1]
    avg_csad       = data["csad"]["csad"].mean()
    csad_percentile= (data["csad"]["csad"] < latest_row["csad"]).mean() * 100

    with col1:
        st.metric(
            "CSAD mới nhất",
            f"{latest_row['csad']:.4%}",
            delta=f"{(latest_row['csad'] - avg_csad):.3%} so với trung bình"
        )
    with col2:
        st.metric(
            "Phần trăm phân tán",
            f"{csad_percentile:.1f}%",
            help="Phần trăm thấp (< 10%) biểu thị khả năng hội tụ bầy đàn / hoảng loạn."
        )
    with col3:
        st.metric(
            "Biến động thực tế (20 ngày)",
            f"{latest_row['realized_vol_20d']:.2%}"
        )
    with col4:
        st.metric("Dữ liệu cập nhật đến", latest_row["date"].strftime("%Y-%m-%d"))

    # ── Đồng hồ Đo Hoảng loạn CSAD ──
    st.subheader("🐑 Chỉ số đo lường hoảng loạn / phân tán thị trường (CSAD)")

    fig_gauge = go.Figure(go.Indicator(
        mode   = "gauge+number",
        value  = csad_percentile,
        domain = {"x": [0, 1], "y": [0, 1]},
        title  = {"text": "Phần trăm phân tán lợi suất CSAD (Thấp = bầy đàn cực hạn / hoảng loạn)"},
        gauge  = {
            "axis": {"range": [0, 100]},
            "steps": [
                {"range": [0,  15],  "color": "#ef4444"},   # Hoảng loạn / Bầy đàn
                {"range": [15, 85],  "color": "#334155"},   # Bình thường
                {"range": [85, 100], "color": "#10b981"},   # Phân tán tăng
            ],
            "threshold": {
                "line":      {"color": "white", "width": 4},
                "thickness": 0.75,
                "value":     csad_percentile,
            },
        },
    ))
    fig_gauge.update_layout(
        height   = 280,
        template = "plotly_dark",
        margin   = dict(t=50, b=0, l=0, r=0)
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

    # ── Biểu đồ Chuỗi Thời gian CSAD ──
    st.subheader("📈 Lịch sử biến động CSAD (2006–2025)")
    fig_ts = go.Figure()
    fig_ts.add_trace(go.Scatter(
        x=data["csad"]["date"], y=data["csad"]["csad"],
        mode="lines", name="CSAD hàng ngày",
        line=dict(color="#38bdf8", width=0.8)
    ))
    fig_ts.update_layout(
        template   = "plotly_dark",
        height     = 320,
        xaxis_title= "Ngày",
        yaxis_title= "CSAD",
        margin     = dict(t=30, b=30)
    )
    st.plotly_chart(fig_ts, use_container_width=True)

    # ── Hệ thống Lọc Cổ phiếu Đảo chiều Hàng tuần ──
    st.subheader("🔍 Hệ thống lọc cổ phiếu đảo chiều hàng tuần")
    st.markdown(
        "Lọc các cổ phiếu niêm yết đang hoạt động dựa trên quy mô (vốn hóa) và tính thanh khoản kém "
        "(Amihud) để tìm ra các ứng viên có xác suất đảo chiều cao."
    )

    exchange_sel = st.multiselect("Lọc sàn giao dịch", ["HOSE", "HNX"], default=["HOSE"])
    min_volume   = st.number_input(
        "Khối lượng giao dịch tuần tối thiểu (cổ phiếu)", min_value=0, value=50_000, step=10_000
    )

    # Bản đồ hóa HOSE sang HSX để khớp với nhãn trong tệp parquet
    exchange_mapped = [ex.replace("HOSE", "HSX") for ex in exchange_sel]

    screener_base = data["firm_panel"][
        (data["firm_panel"]["exchange"].isin(exchange_mapped)) &
        (data["firm_panel"]["status"] == "listed") &
        (data["firm_panel"]["return_w"].notnull())
    ].copy()

    if len(screener_base) > 0:
        latest_panel_date = screener_base["date"].max()
        latest_panel      = screener_base[
            (screener_base["date"] == latest_panel_date) &
            (screener_base["volume"] >= min_volume)
        ].copy()
    else:
        latest_panel = pd.DataFrame()

    if len(latest_panel) > 0:
        try:
            latest_panel["size_q"] = pd.qcut(
                latest_panel["market_cap"], 5,
                labels=["S1 (Nhỏ)", "S2", "S3", "S4", "S5 (Lớn)"]
            )
            latest_panel["liq_q"] = pd.qcut(
                latest_panel["amihud_d"], 5,
                labels=["I1 (Thanh khoản tốt)", "I2", "I3", "I4", "I5 (Kém thanh khoản)"]
            )
        except Exception:
            latest_panel["size_q"] = "N/A"
            latest_panel["liq_q"]  = "N/A"

        col_l, col_r = st.columns(2)

        with col_l:
            st.success("🟢 **Danh mục MUA — Vốn hóa nhỏ + thanh khoản kém + giảm sâu**")
            buy_candidates = latest_panel[
                (latest_panel["size_q"].isin(["S1 (Nhỏ)", "S2"])) &
                (latest_panel["liq_q"].isin(["I4", "I5 (Kém thanh khoản)"]))
            ].sort_values("return_w").head(12)
            
            # Đổi tên cột hiển thị sang tiếng Việt (chữ hoa đầu dòng)
            buy_display = buy_candidates[["ticker", "size_q", "liq_q", "return_w", "market_cap"]].rename(
                columns={
                    "ticker": "Mã CP",
                    "size_q": "Nhóm quy mô",
                    "liq_q": "Nhóm thanh khoản",
                    "return_w": "Lợi suất tuần",
                    "market_cap": "Vốn hóa (tỷ)"
                }
            )
            st.dataframe(
                buy_display.style.format({"Lợi suất tuần": "{:.2%}", "Vốn hóa (tỷ)": "{:,.2f}B"}),
                use_container_width=True
            )

        with col_r:
            st.warning("🔴 **Danh mục BÁN / TRÁNH — Vốn hóa lớn + thanh khoản tốt + tăng mạnh**")
            sell_candidates = latest_panel[
                (latest_panel["size_q"].isin(["S4", "S5 (Lớn)"])) &
                (latest_panel["liq_q"].isin(["I1 (Thanh khoản tốt)", "I2"]))
            ].sort_values("return_w", ascending=False).head(12)
            
            sell_display = sell_candidates[["ticker", "size_q", "liq_q", "return_w", "market_cap"]].rename(
                columns={
                    "ticker": "Mã CP",
                    "size_q": "Nhóm quy mô",
                    "liq_q": "Nhóm thanh khoản",
                    "return_w": "Lợi suất tuần",
                    "market_cap": "Vốn hóa (tỷ)"
                }
            )
            st.dataframe(
                sell_display.style.format({"Lợi suất tuần": "{:.2%}", "Vốn hóa (tỷ)": "{:,.2f}B"}),
                use_container_width=True
            )
    else:
        st.info("Không tìm thấy dữ liệu cổ phiếu khả dụng cho mốc thời gian mới nhất.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — MARKET REGIME & SECTOR NAVIGATOR
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Chế độ thị trường & bản đồ bầy đàn ngành":
    st.title("🌐 Chế độ thị trường - Hiệu ứng bầy đàn theo ngành")
    st.markdown(
        "Phân tích cường độ bầy đàn động theo ngành và so sánh hiệu suất "
        "chiến thuật đảo chiều qua các chế độ thị trường (Tăng / Giảm / Đi ngang)."
    )

    tab1, tab2 = st.tabs([
        "🏢 Phân tích bầy đàn theo ngành",
        "📈 Hành vi theo chế độ & đồng biến động lăn",
    ])

    # ── Tab 1: Sector Herding ──
    with tab1:
        st.subheader("Cường độ hành vi bầy đàn theo ngành")
        st.markdown(
            r"Hệ số bầy đàn thực nghiệm ($\beta_2$) ước tính sự hội tụ lợi suất. "
            "**Hệ số âm và có ý nghĩa thống kê xác nhận có hành vi bầy đàn.**"
        )

        if "t5_sector" in data:
            sector_df = (
                data["t5_sector"]
                .rename(columns={"Unnamed: 0": "Sector"})
                .sort_values("beta2")
            )
            
            # Dịch nghĩa cột bầy đàn sang tiếng Việt để vẽ đồ thị
            sector_df["Bầy đàn"] = sector_df["herding"].map({"Yes": "Có", "No": "Không"})

            fig_sec = px.bar(
                sector_df,
                x     = "Sector",
                y     = "beta2",
                color = "Bầy đàn",
                title = "Hệ số bầy đàn thực nghiệm (β₂) theo ngành (2006–2025)",
                color_discrete_map = {"Có": "#ef4444", "Không": "#10b981"},
                labels = {"Sector": "Ngành", "beta2": "Hệ số beta 2", "Bầy đàn": "Có ý nghĩa"},
            )
            fig_sec.update_layout(template="plotly_dark", height=450)
            st.plotly_chart(fig_sec, use_container_width=True)

            sector_display = sector_df.rename(
                columns={
                    "Sector": "Ngành",
                    "beta2": "Hệ số beta 2",
                    "t_stat": "Thống kê t",
                    "p_value": "Giá trị p",
                    "Bầy đàn": "Bầy đàn (có ý nghĩa)"
                }
            )
            st.dataframe(
                sector_display[["Ngành", "Hệ số beta 2", "Thống kê t", "Giá trị p", "Bầy đàn (có ý nghĩa)"]].style.format({
                    "Hệ số beta 2":   "{:.6f}",
                    "Thống kê t":  "{:.2f}",
                    "Giá trị p": "{:.4f}",
                }),
                use_container_width=True,
            )
        else:
            st.error("Không tìm thấy tệp dữ liệu ngành `output/tables/T5_Sector_CSAD.csv`.")

    # ── Tab 2: Regime Behaviour ──
    with tab2:
        st.subheader("Hiệu suất chiến thuật qua các chế độ thị trường")

        col_reg_l, col_reg_r = st.columns([2, 1.5])

        with col_reg_l:
            if "t7a_regime" in data:
                st.write("**Chênh lệch đảo chiều thực nghiệm theo trạng thái thị trường**")
                
                # Dịch nghĩa Chế độ
                regime_display = data["t7a_regime"].copy()
                regime_display["Regime"] = regime_display["Regime"].map({"Bull": "Thị trường tăng", "Bear": "Thị trường giảm", "Sideways": "Đi ngang"})
                
                st.table(
                    regime_display.rename(
                        columns={
                            "Regime": "Chế độ",
                            "Mean Reversal Spread": "Chênh lệch đảo chiều TB",
                            "t-stat": "Thống kê t",
                            "p-value": "Giá trị p",
                            "Obs": "Số mẫu"
                        }
                    ).style.format({
                        "Chênh lệch đảo chiều TB": "{:.4%}",
                        "Thống kê t":  "{:.2f}",
                        "Giá trị p": "{:.4f}",
                    })
                )
            else:
                st.write("Thiếu dữ liệu chế độ thị trường (`T7a_Regime_Reversal.csv`).")

        with col_reg_r:
            st.write("**Mối quan hệ giữa bầy đàn lăn & chênh lệch đảo chiều**")
            st.info(
                "Phân tích cửa sổ lăn (rolling window) cho thấy mối tương quan cao giữa cường độ bầy đàn lăn "
                "và chênh lệch đảo chiều tiếp theo. "
                "Xem đồ thị đầy đủ tại biểu đồ **Figure 4** trong thư mục `output/figures/`."
            )
            st.markdown(
                "> **Kết luận chính (Khối D):** Lợi nhuận của chiến thuật đảo chiều tăng vọt một cách "
                "đột biến trong và ngay sau các giai đoạn biến động cực hạn, thị trường gấu, hoặc "
                "khủng hoảng hệ thống do phản ứng thái quá về mặt tâm lý của các nhà đầu tư."
            )

        # ── Biểu đồ hộp phân phối CSAD theo chế độ ──
        if "t7a_regime" in data and "csad" in data:
            st.subheader("Xem trước phân phối CSAD")
            fig_box = go.Figure()
            if "market_regime" in data["csad"].columns:
                for regime, vn_regime, colour in [
                    ("Bull",     "Thị trường tăng", "#10b981"),
                    ("Bear",     "Thị trường giảm", "#ef4444"),
                    ("Sideways", "Đi ngang",        "#f59e0b"),
                ]:
                    sub = data["csad"][data["csad"]["market_regime"] == regime]["csad"].dropna()
                    if len(sub):
                        fig_box.add_trace(go.Box(
                            y    = sub,
                            name = vn_regime,
                            marker_color = colour,
                        ))
                fig_box.update_layout(
                    template   = "plotly_dark",
                    height     = 400,
                    yaxis_title= "CSAD",
                    title      = "Phân phối CSAD theo chế độ thị trường",
                )
                st.plotly_chart(fig_box, use_container_width=True)
            else:
                st.info(
                    "Không tìm thấy cột `market_regime` trong `csad_daily.parquet`. "
                    "Hãy thêm nhãn chế độ từ `macro_monthly.parquet` để bật biểu đồ này."
                )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — STRATEGY BACKTESTER & SIMULATOR
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Kiểm thử & mô phỏng chiến thuật đảo chiều":
    st.title("🔄 Mô phỏng & kiểm thử chiến thuật đảo chiều")
    st.markdown(
        "Mô phỏng hiệu suất danh mục mua-bán đảo chiều định kỳ hàng tuần hoặc hàng tháng. "
        "Tùy chỉnh các thông số lọc để kiểm chứng tính bền vững của lợi nhuận."
    )

    # ── Thiết lập tham số ──
    st.subheader("⚙️ Thiết lập mô phỏng")
    col_c1, col_c2, col_c3 = st.columns(3)

    with col_c1:
        quantiles = st.slider(
            "Số lượng nhóm phân loại (quantiles)", min_value=3, max_value=10, value=5
        )
        exchange_filter = st.multiselect(
            "Sàn giao dịch áp dụng", ["HOSE", "HNX"],
            default=["HOSE", "HNX"], key="backtest_ex"
        )
    with col_c2:
        transaction_cost = st.slider(
            "Chi phí giao dịch một chiều (%)",
            min_value=0.0, max_value=1.0, value=0.15, step=0.05
        )
        size_filter = st.selectbox(
            "Ràng buộc quy mô cổ phiếu",
            [
                "Tất cả cổ phiếu", 
                "Loại bỏ 20% quy mô nhỏ nhất (vốn hóa siêu nhỏ)", 
                "Loại bỏ 20% quy mô lớn nhất (vốn hóa siêu lớn)"
            ]
        )
    with col_c3:
        holding_horizon = st.selectbox(
            "Chu kỳ hình thành / nắm giữ", ["1 tuần", "1 tháng"]
        )
        min_stock_limit = st.number_input(
            "Số cổ phiếu tối thiểu mỗi ngày hình thành", min_value=10, value=50
        )

    # ── Tính toán Mô phỏng ──
    st.subheader("📊 Kết quả kiểm thử (backtest)")

    with st.spinner("Đang chạy mô phỏng kiểm thử danh mục…"):
        # Ánh xạ HOSE -> HSX
        exchange_mapped = [ex.replace("HOSE", "HSX") for ex in exchange_filter]
        full_df = data["firm_panel"][
            data["firm_panel"]["exchange"].isin(exchange_mapped)
        ].copy()

        # Áp dụng bộ lọc quy mô
        if size_filter == "Loại bỏ 20% quy mô nhỏ nhất (vốn hóa siêu nhỏ)":
            q20 = full_df.groupby("date")["market_cap"].transform(lambda x: x.quantile(0.20))
            full_df = full_df[full_df["market_cap"] > q20]
        elif size_filter == "Loại bỏ 20% quy mô lớn nhất (vốn hóa siêu lớn)":
            q80 = full_df.groupby("date")["market_cap"].transform(lambda x: x.quantile(0.80))
            full_df = full_df[full_df["market_cap"] < q80]

        form_col = "return_w" if holding_horizon == "1 tuần" else "return_m"
        
        # Loại bỏ các hàng trống trước khi dịch chuyển chu kỳ để dịch chuyển đúng bước thời gian
        full_df = full_df.dropna(subset=[form_col]).copy()
        full_df["lag_ret"] = full_df.groupby("ticker")[form_col].shift(1)
        clean_df = full_df.dropna(subset=["lag_ret", form_col]).copy()

        # Vòng lặp sắp xếp và phân nhóm danh mục
        port_returns = []
        for date, group in clean_df.groupby("date"):
            if len(group) < min_stock_limit:
                continue
            try:
                group = group.copy()
                group["q"] = pd.qcut(
                    group["lag_ret"], quantiles, labels=False, duplicates="drop"
                )
            except Exception:
                continue

            low_q  = group["q"].min()
            high_q = group["q"].max()
            if low_q == high_q:
                continue

            q1_ret = group[group["q"] == low_q][form_col].mean()
            qN_ret = group[group["q"] == high_q][form_col].mean()

            port_returns.append({
                "date":        date,
                "Q1 (Loser)":  q1_ret,
                "Q5 (Winner)": qN_ret,
                "L-S Spread":  q1_ret - qN_ret,
            })

        sim_df = pd.DataFrame(port_returns)

        if len(sim_df) > 0:
            sim_df["date"] = pd.to_datetime(sim_df["date"])
            sim_df = sim_df.sort_values("date").reset_index(drop=True)

            # Tính toán chênh lệch sau khi trừ phí giao dịch
            sim_df["Adj Spread"] = sim_df["L-S Spread"] - 2 * (transaction_cost / 100)

            # Lợi nhuận tích lũy
            sim_df["cum_q1"]    = (1 + sim_df["Q1 (Loser)"]).cumprod() - 1
            sim_df["cum_q5"]    = (1 + sim_df["Q5 (Winner)"]).cumprod() - 1
            sim_df["cum_spread"]= (1 + sim_df["Adj Spread"]).cumprod() - 1

            # Thống kê tổng hợp
            mean_ret = sim_df["Adj Spread"].mean()
            std_ret  = sim_df["Adj Spread"].std()
            ann_factor = 52 if holding_horizon == "1 tuần" else 12
            sharpe   = (mean_ret / std_ret) * np.sqrt(ann_factor) if std_ret > 0 else 0
            win_rate = (sim_df["Adj Spread"] > 0).mean()
            max_dd   = (
                sim_df["cum_spread"] -
                sim_df["cum_spread"].cummax()
            ).min()

            # Khối thẻ chỉ số kết quả
            stat_c1, stat_c2, stat_c3, stat_c4 = st.columns(4)
            with stat_c1:
                st.metric("Tỷ suất lợi nhuận TB", f"{mean_ret:.3%}")
            with stat_c2:
                st.metric("Hệ số Sharpe hàng năm", f"{sharpe:.2f}")
            with stat_c3:
                st.metric("Tỷ lệ thắng (win rate)", f"{win_rate:.2%}")
            with stat_c4:
                st.metric("Sụt giảm lớn nhất (max DD)", f"{max_dd:.2%}")

            # Đồ thị hiệu suất tích lũy
            fig_perf = go.Figure()
            fig_perf.add_trace(go.Scatter(
                x=sim_df["date"], y=sim_df["cum_q1"] * 100,
                name="Danh mục Q1 (thua cuộc/giảm sâu)",
                line=dict(color="#10b981")
            ))
            fig_perf.add_trace(go.Scatter(
                x=sim_df["date"], y=sim_df["cum_q5"] * 100,
                name="Danh mục QN (chiến thắng/tăng mạnh)",
                line=dict(color="#ef4444")
            ))
            fig_perf.add_trace(go.Scatter(
                x=sim_df["date"], y=sim_df["cum_spread"] * 100,
                name="Chênh lệch L-S ròng (trừ chi phí)",
                line=dict(color="#38bdf8", width=3)
            ))
            fig_perf.update_layout(
                title       = "Mô phỏng đảo chiều động — lợi nhuận tích lũy (%)",
                xaxis_title = "Ngày",
                yaxis_title = "Lợi nhuận tích lũy (%)",
                template    = "plotly_dark",
                height      = 500,
                legend      = dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
            )
            st.plotly_chart(fig_perf, use_container_width=True)

            # Phân phối chênh lệch định kỳ
            st.subheader("Phân phối lợi nhuận định kỳ")
            fig_hist = px.histogram(
                sim_df, x="Adj Spread",
                nbins       = 50,
                title       = "Phân phối lợi nhuận chênh lệch L-S định kỳ (đã trừ chi phí)",
                labels      = {"Adj Spread": "Lợi suất chênh lệch L-S"},
                color_discrete_sequence = ["#38bdf8"],
                template    = "plotly_dark",
            )
            fig_hist.add_vline(x=0, line_dash="dash", line_color="white")
            fig_hist.add_vline(
                x=mean_ret, line_dash="dot", line_color="#10b981",
                annotation_text=f"Trung bình={mean_ret:.3%}", annotation_position="top right"
            )
            st.plotly_chart(fig_hist, use_container_width=True)

        else:
            st.warning(
                "Không có chu kỳ danh mục nào được thiết lập thành công với các cài đặt hiện tại. "
                "Hãy thử giảm số lượng cổ phiếu tối thiểu hoặc mở rộng sàn giao dịch."
            )

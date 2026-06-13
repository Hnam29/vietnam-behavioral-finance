"""
Vietnam Behavioral Finance Dashboard
=====================================
Topic: "Hành vi bầy đàn có phải là cơ chế tạo ra hiệu ứng đảo ngược?
        Bằng chứng từ thị trường chứng khoán Việt Nam giai đoạn 2006-2025"

Dashboard Modules:
  Reversal Sentinel & Behavioral Screener
  Market Regime & Sector Herding Navigator
  Strategy Backtester & Simulator

Usage:
  streamlit run app.py

Prerequisites:
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
    page_title="Vietnam Behavioral Finance Dashboard",
    page_icon="🇻🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom dark-mode CSS
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
    """Load preprocessed parquets and regression output tables."""
    data = {}

    # ── Parquet files ──
    try:
        data["csad"]       = pd.read_parquet(DATA_PROCESSED / "csad_daily.parquet")
        data["firm_panel"] = pd.read_parquet(DATA_PROCESSED / "firm_panel_app.parquet")

        # Standardize dates
        data["csad"]["date"]       = pd.to_datetime(data["csad"]["date"])
        data["firm_panel"]["date"] = pd.to_datetime(data["firm_panel"]["date"])

        # Dynamically merge market_regime from macro_monthly.parquet into csad
        macro_m = pd.read_parquet(DATA_PROCESSED / "macro_monthly.parquet")
        data["csad"]["month"] = data["csad"]["date"].dt.to_period("M").astype(str)
        data["csad"] = data["csad"].merge(
            macro_m[["month", "market_regime"]],
            on="month",
            how="left"
        ).drop(columns=["month"])
    except Exception as e:
        st.error(
            f"⚠️ Error loading parquet data: {e}\n\n"
            "Ensure `run_research_analysis.py` has been executed and "
            "`data/processed/` contains the required `.parquet` files."
        )
        st.stop()

    # ── CSV output tables ──
    try:
        data["t2a"]       = pd.read_csv(OUTPUT_TABLES / "T2a_Port_Weekly.csv")
        data["t5_sector"] = pd.read_csv(OUTPUT_TABLES / "T5_Sector_CSAD.csv")
        data["t7a_regime"]= pd.read_csv(OUTPUT_TABLES / "T7a_Regime_Reversal.csv")
    except Exception as e:
        st.warning(f"⚠️ Some output tables are missing: {e}. Certain charts may not render.")

    return data

data = load_datasets()

# ── 3. SIDEBAR NAVIGATION ──────────────────────────────────────────────────────
st.sidebar.title("🇻🇳 Vietnam Behavioral Sentinel")
st.sidebar.markdown("*Empirical Analysis Workspace*")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Select Analysis Workspace",
    [
        "Reversal Sentinel & Screener",
        "Market Regime & Sector Navigator",
        "Strategy Backtester & Simulator",
    ]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **Research Period: 2006–2025**\n\n"
    "This dashboard visualises preprocessed research outputs combined "
    "with live ticker sorting from `firm_panel_daily.parquet`."
)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — REVERSAL SENTINEL & SCREENER
# ══════════════════════════════════════════════════════════════════════════════
if page == "Reversal Sentinel & Screener":
    st.title("Reversal Sentinel & Behavioral Screener")
    st.markdown(
        "Detects extreme overreaction (reversal signals) and maps market-wide "
        "convergence / panic via CSAD dispersion indices."
    )

    # ── Metric block ──
    col1, col2, col3, col4 = st.columns(4)
    latest_row     = data["csad"].sort_values("date").iloc[-1]
    avg_csad       = data["csad"]["csad"].mean()
    csad_percentile= (data["csad"]["csad"] < latest_row["csad"]).mean() * 100

    with col1:
        st.metric(
            "Latest CSAD",
            f"{latest_row['csad']:.4%}",
            delta=f"{(latest_row['csad'] - avg_csad):.3%} vs mean"
        )
    with col2:
        st.metric(
            "Dispersion Percentile",
            f"{csad_percentile:.1f}%",
            help="Low percentile (< 10%) indicates potential herding convergence."
        )
    with col3:
        st.metric(
            "Realised Volatility (20d)",
            f"{latest_row['realized_vol_20d']:.2%}"
        )
    with col4:
        st.metric("Data Up-To-Date", latest_row["date"].strftime("%Y-%m-%d"))

    # ── CSAD Panic Gauge ──
    st.subheader("🐑 Market Dispersion (CSAD) Panic Meter")

    fig_gauge = go.Figure(go.Indicator(
        mode   = "gauge+number",
        value  = csad_percentile,
        domain = {"x": [0, 1], "y": [0, 1]},
        title  = {"text": "CSAD Return Dispersion Percentile  (Low = Extreme Herding / Panic)"},
        gauge  = {
            "axis": {"range": [0, 100]},
            "steps": [
                {"range": [0,  15],  "color": "#ef4444"},   # Panic / herding
                {"range": [15, 85],  "color": "#334155"},   # Normal
                {"range": [85, 100], "color": "#10b981"},   # Divergent
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

    # ── Full CSAD time-series chart ──
    st.subheader("📈 CSAD History (2006–2025)")
    fig_ts = go.Figure()
    fig_ts.add_trace(go.Scatter(
        x=data["csad"]["date"], y=data["csad"]["csad"],
        mode="lines", name="Daily CSAD",
        line=dict(color="#38bdf8", width=0.8)
    ))
    fig_ts.update_layout(
        template   = "plotly_dark",
        height     = 320,
        xaxis_title= "Date",
        yaxis_title= "CSAD",
        margin     = dict(t=30, b=30)
    )
    st.plotly_chart(fig_ts, use_container_width=True)

    # ── Weekly Reversal Screener ──
    st.subheader("🔍 Weekly Reversal Screener")
    st.markdown(
        "Filters active listed equities based on size (market cap) and illiquidity "
        "(Amihud) to surface high-probability reversal candidates."
    )

    exchange_sel = st.multiselect("Filter Exchanges", ["HOSE", "HNX"], default=["HOSE"])
    min_volume   = st.number_input(
        "Minimum Weekly Volume (shares)", min_value=0, value=50_000, step=10_000
    )

    # Map HOSE to HSX to match exchange labels in parquet file
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
                labels=["S1 (Small)", "S2", "S3", "S4", "S5 (Large)"]
            )
            latest_panel["liq_q"] = pd.qcut(
                latest_panel["amihud_d"], 5,
                labels=["I1 (Liquid)", "I2", "I3", "I4", "I5 (Illiquid)"]
            )
        except Exception:
            latest_panel["size_q"] = "N/A"
            latest_panel["liq_q"]  = "N/A"

        col_l, col_r = st.columns(2)

        with col_l:
            st.success("🟢 **BUY Screener — Small-Cap + Illiquid Losers**")
            buy_candidates = latest_panel[
                (latest_panel["size_q"].isin(["S1 (Small)", "S2"])) &
                (latest_panel["liq_q"].isin(["I4", "I5 (Illiquid)"]))
            ].sort_values("return_w").head(12)
            st.dataframe(
                buy_candidates[["ticker", "size_q", "liq_q", "return_w", "market_cap"]]
                .style.format({"return_w": "{:.2%}", "market_cap": "{:,.2f}B"}),
                use_container_width=True
            )

        with col_r:
            st.warning("🔴 **SELL / AVOID Screener — Large-Cap + Liquid Winners**")
            sell_candidates = latest_panel[
                (latest_panel["size_q"].isin(["S4", "S5 (Large)"])) &
                (latest_panel["liq_q"].isin(["I1 (Liquid)", "I2"]))
            ].sort_values("return_w", ascending=False).head(12)
            st.dataframe(
                sell_candidates[["ticker", "size_q", "liq_q", "return_w", "market_cap"]]
                .style.format({"return_w": "{:.2%}", "market_cap": "{:,.2f}B"}),
                use_container_width=True
            )
    else:
        st.info("No active stock records found for the latest timestamp.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — MARKET REGIME & SECTOR NAVIGATOR
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Market Regime & Sector Navigator":
    st.title("Market Regime & Sector Herding Navigator")
    st.markdown(
        "Analyses dynamic sector herding patterns and compares reversal strategy "
        "behaviour across market regimes (Bull / Bear / Sideways)."
    )

    tab1, tab2 = st.tabs([
        "🏢 Sector Herding Analysis",
        "📈 Regime Behaviour & Rolling Co-movement",
    ])

    # ── Tab 1: Sector Herding ──
    with tab1:
        st.subheader("Sector-Specific Herding Intensity")
        st.markdown(
            r"The herding coefficient ($\beta_2$) estimates return convergence. "
            "**Negative coefficients confirm herding.**"
        )

        if "t5_sector" in data:
            sector_df = (
                data["t5_sector"]
                .rename(columns={"Unnamed: 0": "Sector"})
                .sort_values("beta2")
            )

            fig_sec = px.bar(
                sector_df,
                x     = "Sector",
                y     = "beta2",
                color = "herding",
                title = "Empirical Herding Coefficient (β₂) by Sector (2006–2025)",
                color_discrete_map = {"Yes": "#ef4444", "No": "#10b981"},
                labels = {"beta2": "Beta 2 Coefficient", "herding": "Significant Herding"},
            )
            fig_sec.update_layout(template="plotly_dark", height=450)
            st.plotly_chart(fig_sec, use_container_width=True)

            st.dataframe(
                sector_df.style.format({
                    "beta2":   "{:.6f}",
                    "t_stat":  "{:.2f}",
                    "p_value": "{:.4f}",
                }),
                use_container_width=True,
            )
        else:
            st.error("Sector output file `output/tables/T5_Sector_CSAD.csv` not found.")

    # ── Tab 2: Regime Behaviour ──
    with tab2:
        st.subheader("Performance Across Market Regimes")

        col_reg_l, col_reg_r = st.columns([1, 2])

        with col_reg_l:
            if "t7a_regime" in data:
                st.write("**Empirical Reversal Spreads by Market State**")
                st.table(
                    data["t7a_regime"].style.format({
                        "Mean Reversal Spread": "{:.4%}",
                        "t-stat":  "{:.2f}",
                        "p-value": "{:.4f}",
                    })
                )
            else:
                st.write("Regime data (`T7a_Regime_Reversal.csv`) is missing.")

        with col_reg_r:
            st.write("**Rolling Herding vs. Reversal Spreads**")
            st.info(
                "Rolling window regressions show a high correlation between rolling "
                "herding intensity and subsequent reversal spreads. "
                "See **Figure 4** in `output/figures/` for the full time-series overlay."
            )
            st.markdown(
                "> **Key Finding (Block D):** Reversal profitability spikes dramatically "
                "during and immediately following high-volatility, bear-market, or systemic "
                "crisis periods due to extreme cognitive overreaction."
            )

        # ── CSAD distribution by regime ──
        if "t7a_regime" in data and "csad" in data:
            st.subheader("CSAD Distribution Preview")
            fig_box = go.Figure()
            if "market_regime" in data["csad"].columns:
                for regime, colour in [
                    ("Bull",     "#10b981"),
                    ("Bear",     "#ef4444"),
                    ("Sideways", "#f59e0b"),
                ]:
                    sub = data["csad"][data["csad"]["market_regime"] == regime]["csad"].dropna()
                    if len(sub):
                        fig_box.add_trace(go.Box(
                            y    = sub,
                            name = regime,
                            marker_color = colour,
                        ))
                fig_box.update_layout(
                    template   = "plotly_dark",
                    height     = 400,
                    yaxis_title= "CSAD",
                    title      = "CSAD Distribution by Market Regime",
                )
                st.plotly_chart(fig_box, use_container_width=True)
            else:
                st.info(
                    "`market_regime` column not found in `csad_daily.parquet`. "
                    "Add regime labels from `macro_monthly.parquet` to enable this chart."
                )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — STRATEGY BACKTESTER & SIMULATOR
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Strategy Backtester & Simulator":
    st.title("Reversal Portfolio Backtester & Simulator")
    st.markdown(
        "Simulate customised weekly / monthly long-short portfolios. "
        "Adjust filtering parameters to validate robust reversal returns."
    )

    # ── Controls ──
    st.subheader("⚙️ Simulation Settings")
    col_c1, col_c2, col_c3 = st.columns(3)

    with col_c1:
        quantiles = st.slider(
            "Number of Sorting Quantiles", min_value=3, max_value=10, value=5
        )
        exchange_filter = st.multiselect(
            "Exchanges to Include", ["HOSE", "HNX"],
            default=["HOSE", "HNX"], key="backtest_ex"
        )
    with col_c2:
        transaction_cost = st.slider(
            "Single-Leg Transaction Cost (%)",
            min_value=0.0, max_value=1.0, value=0.15, step=0.05
        )
        size_filter = st.selectbox(
            "Stock Size Constraint",
            ["All Stocks", "Exclude Bottom 20% (Micro Cap)", "Exclude Top 20% (Mega Cap)"]
        )
    with col_c3:
        holding_horizon = st.selectbox(
            "Formation / Holding Horizon", ["1 Week", "1 Month"]
        )
        min_stock_limit = st.number_input(
            "Min Stocks per Formation Date", min_value=10, value=50
        )

    # ── Backtest computation ──
    st.subheader("📊 Backtest Results")

    with st.spinner("Simulating portfolio paths…"):
        # Map HOSE to HSX
        exchange_mapped = [ex.replace("HOSE", "HSX") for ex in exchange_filter]
        full_df = data["firm_panel"][
            data["firm_panel"]["exchange"].isin(exchange_mapped)
        ].copy()

        # Size filters
        if size_filter == "Exclude Bottom 20% (Micro Cap)":
            q20 = full_df.groupby("date")["market_cap"].transform(lambda x: x.quantile(0.20))
            full_df = full_df[full_df["market_cap"] > q20]
        elif size_filter == "Exclude Top 20% (Mega Cap)":
            q80 = full_df.groupby("date")["market_cap"].transform(lambda x: x.quantile(0.80))
            full_df = full_df[full_df["market_cap"] < q80]

        form_col = "return_w" if holding_horizon == "1 Week" else "return_m"
        # Drop rows where form_col is NaN before grouping/shifting
        full_df = full_df.dropna(subset=[form_col]).copy()
        full_df["lag_ret"] = full_df.groupby("ticker")[form_col].shift(1)
        clean_df = full_df.dropna(subset=["lag_ret", form_col]).copy()

        # Portfolio sorting loop
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

            # Cost-adjust spread
            sim_df["Adj Spread"] = sim_df["L-S Spread"] - 2 * (transaction_cost / 100)

            # Cumulative returns
            sim_df["cum_q1"]    = (1 + sim_df["Q1 (Loser)"]).cumprod() - 1
            sim_df["cum_q5"]    = (1 + sim_df["Q5 (Winner)"]).cumprod() - 1
            sim_df["cum_spread"]= (1 + sim_df["Adj Spread"]).cumprod() - 1

            # Summary stats
            mean_ret = sim_df["Adj Spread"].mean()
            std_ret  = sim_df["Adj Spread"].std()
            ann_factor = 52 if holding_horizon == "1 Week" else 12
            sharpe   = (mean_ret / std_ret) * np.sqrt(ann_factor) if std_ret > 0 else 0
            win_rate = (sim_df["Adj Spread"] > 0).mean()
            max_dd   = (
                sim_df["cum_spread"] -
                sim_df["cum_spread"].cummax()
            ).min()

            # Stat cards
            stat_c1, stat_c2, stat_c3, stat_c4 = st.columns(4)
            with stat_c1:
                st.metric("Avg Portfolio Return", f"{mean_ret:.3%}")
            with stat_c2:
                st.metric("Annualised Sharpe", f"{sharpe:.2f}")
            with stat_c3:
                st.metric("Win Rate", f"{win_rate:.2%}")
            with stat_c4:
                st.metric("Max Drawdown", f"{max_dd:.2%}")

            # Cumulative performance chart
            fig_perf = go.Figure()
            fig_perf.add_trace(go.Scatter(
                x=sim_df["date"], y=sim_df["cum_q1"] * 100,
                name="Q1 (Losers) Portfolio",
                line=dict(color="#10b981")
            ))
            fig_perf.add_trace(go.Scatter(
                x=sim_df["date"], y=sim_df["cum_q5"] * 100,
                name="QN (Winners) Portfolio",
                line=dict(color="#ef4444")
            ))
            fig_perf.add_trace(go.Scatter(
                x=sim_df["date"], y=sim_df["cum_spread"] * 100,
                name="Net L-S Spread (Cost-Adj.)",
                line=dict(color="#38bdf8", width=3)
            ))
            fig_perf.update_layout(
                title       = "Dynamic Reversal Simulation — Cumulative Return (%)",
                xaxis_title = "Date",
                yaxis_title = "Cumulative Return (%)",
                template    = "plotly_dark",
                height      = 500,
                legend      = dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
            )
            st.plotly_chart(fig_perf, use_container_width=True)

            # Period spread distribution
            st.subheader("Periodic Spread Distribution")
            fig_hist = px.histogram(
                sim_df, x="Adj Spread",
                nbins       = 50,
                title       = "Distribution of Period L-S Spread Returns (Cost-Adjusted)",
                labels      = {"Adj Spread": "L-S Spread Return"},
                color_discrete_sequence = ["#38bdf8"],
                template    = "plotly_dark",
            )
            fig_hist.add_vline(x=0, line_dash="dash", line_color="white")
            fig_hist.add_vline(
                x=mean_ret, line_dash="dot", line_color="#10b981",
                annotation_text=f"Mean={mean_ret:.3%}", annotation_position="top right"
            )
            st.plotly_chart(fig_hist, use_container_width=True)

        else:
            st.warning(
                "No portfolio periods were constructed with the current settings. "
                "Try relaxing size, exchange, or minimum-stock filters."
            )
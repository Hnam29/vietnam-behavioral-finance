# Guide: How to Implement the Behavioral Finance & Reversal Dashboard

This guide outlines the steps and provides the complete code to build a unified **Streamlit** dashboard implementing all three behavioral finance solutions:
1. **Behavioral Reversal Sentinel** (Active Screener & CSAD Panic Gauge)
2. **Market State & Herding Regime Navigator** (Regime Split Analysis & Sector Heatmaps)
3. **Behavioral Portfolio Backtester & Simulator** (Dynamic Backtesting with Parameter Sliders)

These solutions are structured as individual tabs/pages controlled by a modern, interactive sidebar navigation system.

---

## 📁 1. Project Directory Structure

Your Streamlit application should reside in the same project directory as your research code to access the preprocessed data folders instantly:

```text
behavior/
├── data/
│   ├── raw/
│   └── processed/
│       ├── csad_daily.parquet
│       ├── returns_daily.parquet
│       └── firm_panel_daily.parquet
├── output/
│   ├── tables/
│   │   ├── T2a_Port_Weekly.csv
│   │   ├── T5_Sector_CSAD.csv
│   │   └── T7a_Regime_Reversal.csv
│   └── figures/
├── app.py                <-- [NEW] The main Streamlit Dashboard script
└── how_to_implement.md   <-- This guide
```

---

## ⚙️ 2. Prerequisites & Environment Setup

Since you are in a **Bronze Tier License** environment, make sure to activate your virtual environment before installing packages and running the app.

### Step A: Activate Environment
```bash
# On macOS / Linux:
source ~/.venv/bin/activate
```

### Step B: Install Required Packages
Install Streamlit, Plotly, and PyArrow (for reading `.parquet` files):
```bash
pip install streamlit plotly pandas pyarrow numpy scipy statsmodels
```

---

## 💻 3. The Dashboard Code (`app.py`)

Create a file named `app.py` in your workspace and copy the code below. It contains:
- Consolidated data loading with `@st.cache_data` to ensure near-instantaneous page reloads.
- Premium dark-themed UI components matching your research figures.
- Separate navigation routes for each of the three solutions.

```python
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import scipy.stats as stats

# ── 1. PAGE CONFIGURATION & THEME ──────────────────────────────────────────
st.set_page_config(
    page_title="Vietnam Behavioral Finance Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Sleek CSS for Dark-Mode and Premium Aesthetics
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

# ── 2. DATA LOADERS (CACHED) ────────────────────────────────────────────────
DATA_PROCESSED = Path("data/processed")
OUTPUT_TABLES = Path("output/tables")

@st.cache_data
def load_datasets():
    """Load preprocessed parquets and regression output tables."""
    data = {}
    try:
        data["csad"] = pd.read_parquet(DATA_PROCESSED / "csad_daily.parquet")
        data["returns"] = pd.read_parquet(DATA_PROCESSED / "returns_daily.parquet")
        data["firm_panel"] = pd.read_parquet(DATA_PROCESSED / "firm_panel_daily.parquet")
        
        # Standardize dates
        data["csad"]["date"] = pd.to_datetime(data["csad"]["date"])
        data["firm_panel"]["date"] = pd.to_datetime(data["firm_panel"]["date"])
    except Exception as e:
        st.error(f"⚠️ Error loading parquet data: {e}. Ensure 'run_research_analysis.py' was run.")
        st.stop()
        
    # Load Table outputs
    try:
        data["t2a"] = pd.read_csv(OUTPUT_TABLES / "T2a_Port_Weekly.csv")
        data["t5_sector"] = pd.read_csv(OUTPUT_TABLES / "T5_Sector_CSAD.csv")
        data["t7a_regime"] = pd.read_csv(OUTPUT_TABLES / "T7a_Regime_Reversal.csv")
    except Exception as e:
        st.warning(f"⚠️ Table outputs missing: {e}. Static charts may not load correctly.")
        
    return data

data = load_datasets()

# ── 3. SIDEBAR NAVIGATION ──────────────────────────────────────────────────
st.sidebar.title("📊 VN Behavioral Sentinel")
st.sidebar.markdown("*Empirical Analysis Workspace*")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Select Analysis Workspace",
    [
        "🚨 1. Reversal Sentinel & Screener",
        "🌐 2. Market Regime & Sector Navigator",
        "🔄 3. Strategy Backtester & Simulator"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **Bronze Tier Active**\n\n"
    "This dashboard utilizes preprocessed 2006–2025 research outputs combined with active ticker sorting."
)

# ══════════════════════════════════════════════════════════════════════════
# PAGE 1: REVERSAL SENTINEL & SCREENER
# ══════════════════════════════════════════════════════════════════════════
if page == "🚨 1. Reversal Sentinel & Screener":
    st.title("🚨 Reversal Sentinel & Behavioral Screener")
    st.markdown(
        "Detects extreme overreaction (reversal signals) and maps market-wide convergence/panic via CSAD dispersion indices."
    )
    
    # ── METRIC BLOCK ──
    col1, col2, col3, col4 = st.columns(4)
    latest_row = data["csad"].sort_values("date").iloc[-1]
    avg_csad = data["csad"]["csad"].mean()
    csad_percentile = (data["csad"]["csad"] < latest_row["csad"]).mean() * 100
    
    with col1:
        st.metric("Latest CSAD", f"{latest_row['csad']:.4%}", 
                  delta=f"{(latest_row['csad'] - avg_csad):.3%} vs mean")
    with col2:
        st.metric("Dispersion Percentile", f"{csad_percentile:.1f}%", 
                  help="Low percentile (< 10%) shows potential herding convergence.")
    with col3:
        st.metric("Market State Volatility", f"{latest_row['realized_vol_20d']:.2%}")
    with col4:
        st.metric("Data Up-To-Date", latest_row["date"].strftime("%Y-%m-%d"))

    # ── CSAD PANIC GAUGE CHART ──
    st.subheader("🐑 Market Dispersion (CSAD) Panic Meter")
    
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = csad_percentile,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "CSAD Return Dispersion Percentile (Low = Extreme Herding/Panic)"},
        gauge = {
            'axis': {'range': [0, 100]},
            'steps': [
                {'range': [0, 15], 'color': "#ef4444"},   # Extreme herding / Panic
                {'range': [15, 85], 'color': "#334155"},  # Normal regime
                {'range': [85, 100], 'color': "#10b981"}  # Divergent regime
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': csad_percentile
            }
        }
    ))
    fig_gauge.update_layout(height=280, template="plotly_dark", margin=dict(t=50, b=0, l=0, r=0))
    st.plotly_chart(fig_gauge, use_container_width=True)

    # ── WEEKLY DOUBLE-SORT SCREENER ──
    st.subheader("🔍 Weekly Reversal Screener")
    st.markdown("Filters active listed equities based on size (Cap) and illiquidity (Amihud) to target high-probability reversal components.")

    # User inputs for screening
    exchange_sel = st.multiselect("Filter Exchanges", ["HOSE", "HNX"], default=["HOSE"])
    min_volume = st.number_input("Minimum Weekly Volume (shares)", min_value=0, value=50000, step=10000)
    
    # Filter the panel
    screener_base = data["firm_panel"][
        (data["firm_panel"]["exchange"].isin(exchange_sel)) & 
        (data["firm_panel"]["status"] == "listed")
    ].copy()
    
    # Get latest date in firm_panel
    latest_panel_date = screener_base["date"].max()
    latest_panel = screener_base[screener_base["date"] == latest_panel_date].copy()
    
    if len(latest_panel) > 0:
        # Form quintiles
        try:
            latest_panel["size_q"] = pd.qcut(latest_panel["market_cap"], 5, labels=["S1 (Small)", "S2", "S3", "S4", "S5 (Large)"])
            latest_panel["liq_q"] = pd.qcut(latest_panel["amihud_d"], 5, labels=["I1 (Liquid)", "I2", "I3", "I4", "I5 (Illiquid)"])
        except Exception:
            latest_panel["size_q"] = "N/A"
            latest_panel["liq_q"] = "N/A"
            
        # Display screens side-by-side
        col_l, col_r = st.columns(2)
        
        with col_l:
            st.success("🟢 **Reversal BUY Screener (Small-Cap + Illiquid Losers)**")
            buy_candidates = latest_panel[
                (latest_panel["size_q"].isin(["S1 (Small)", "S2"])) &
                (latest_panel["liq_q"].isin(["I4", "I5 (Illiquid)"]))
            ].sort_values("return_w").head(12)
            
            st.dataframe(buy_candidates[["ticker", "size_q", "liq_q", "return_w", "market_cap"]].style.format({
                "return_w": "{:.2%}",
                "market_cap": "{:,.2f}B"
            }), use_container_width=True)
            
        with col_r:
            st.warning("🔴 **Reversal SELL/AVOID Screener (Large-Cap + Liquid Winners)**")
            sell_candidates = latest_panel[
                (latest_panel["size_q"].isin(["S4", "S5 (Large)"])) &
                (latest_panel["liq_q"].isin(["I1 (Liquid)", "I2"]))
            ].sort_values("return_w", ascending=False).head(12)
            
            st.dataframe(sell_candidates[["ticker", "size_q", "liq_q", "return_w", "market_cap"]].style.format({
                "return_w": "{:.2%}",
                "market_cap": "{:,.2f}B"
            }), use_container_width=True)
    else:
        st.write("No active stock records found for the latest timestamp.")

# ══════════════════════════════════════════════════════════════════════════
# PAGE 2: MARKET REGIME & SECTOR NAVIGATOR
# ══════════════════════════════════════════════════════════════════════════
elif page == "🌐 2. Market Regime & Sector Navigator":
    st.title("🌐 Market Regime & Sector Herding Navigator")
    st.markdown(
        "Analyzes dynamic sector herding patterns and compares reversal strategy behavior across market regimes (Bull/Bear/Sideways)."
    )

    # ── TAB CONTAINER ──
    tab1, tab2 = st.tabs(["🏢 Sector Herding Analysis", "📈 Regime Behavior & Rolling Co-movement"])
    
    with tab1:
        st.subheader("Sector-Specific Herding Intensity")
        st.markdown(
            "The herding coefficient ($\beta_2$) estimates return convergence. **Negative coefficients confirm herding.**"
        )
        
        if "t5_sector" in data:
            # Clean sector dataset columns
            sector_df = data["t5_sector"].rename(columns={"Unnamed: 0": "Sector"}).sort_values("beta2")
            
            fig_sec = px.bar(
                sector_df,
                x="Sector",
                y="beta2",
                color="herding",
                title="Empirical Herding Coefficient (β2) by Sector (2006–2025)",
                color_discrete_map={"Yes": "#ef4444", "No": "#10b981"},
                labels={"beta2": "Beta 2 Coefficient", "herding": "Significant Herding"}
            )
            fig_sec.update_layout(template="plotly_dark", height=450)
            st.plotly_chart(fig_sec, use_container_width=True)
            
            # Display Raw Table
            st.dataframe(sector_df.style.format({
                "beta2": "{:.6f}",
                "t_stat": "{:.2f}",
                "p_value": "{:.4f}"
            }))
        else:
            st.error("Sector output file output/tables/T5_Sector_CSAD.csv not found.")

    with tab2:
        st.subheader("Performance Across Regimes")
        
        col_reg_l, col_reg_r = st.columns([1, 2])
        
        with col_reg_l:
            if "t7a_regime" in data:
                st.write("**Empirical Reversal Spreads by Market State**")
                st.table(data["t7a_regime"].style.format({
                    "Mean Reversal Spread": "{:.4%}",
                    "t-stat": "{:.2f}",
                    "p-value": "{:.4f}"
                }))
            else:
                st.write("Regime data missing.")
                
        with col_reg_r:
            st.write("**Rolling Herding vs. Reversal Spreads**")
            st.info(
                "Rolling window regressions show a high correlation between rolling herding intensity "
                "and subsequent reversal spreads. Check **Figure 4** in the output directory for details."
            )
            # Recreate interactive preview of rolling correlations if available
            st.markdown(
                "> **Key Finding (Block D):** Reversal profitability spikes dramatically during and "
                "immediately following high-volatility, bear-market, or systemic crisis periods due to "
                "extreme cognitive overreaction."
            )

# ══════════════════════════════════════════════════════════════════════════
# PAGE 3: STRATEGY BACKTESTER & SIMULATOR
# ══════════════════════════════════════════════════════════════════════════
elif page == "🔄 3. Strategy Backtester & Simulator":
    st.title("🔄 Reversal Portfolio Backtester & Simulator")
    st.markdown(
        "Simulate customized weekly/monthly long-short portfolios. Select filtering parameters to validate robust returns."
    )

    # ── CONTROLS PANEL ──
    st.subheader("⚙️ Simulation Settings")
    col_c1, col_c2, col_c3 = st.columns(3)
    
    with col_c1:
        quantiles = st.slider("Number of Sorting Quantiles", min_value=3, max_value=10, value=5)
        exchange_filter = st.multiselect("Exchanges to Include", ["HOSE", "HNX"], default=["HOSE", "HNX"], key="backtest_ex")
    with col_c2:
        transaction_cost = st.slider("Single-Leg Transaction Cost (%)", min_value=0.0, max_value=1.0, value=0.15, step=0.05)
        size_filter = st.selectbox("Stock Size Constraint", ["All Stocks", "Exclude Bottom 20% (Micro Cap)", "Exclude Top 20% (Mega Cap)"])
    with col_c3:
        holding_horizon = st.selectbox("Formation/Holding Horizon", ["1 Week", "1 Month"])
        min_stock_limit = st.number_input("Min Stocks per Formation Date", min_value=10, value=50)

    # ── LIVE BACKTEST COMPUTATION ──
    st.subheader("📊 Backtest Results")
    
    with st.spinner("Simulating portfolio paths..."):
        # Select active datasets
        full_df = data["firm_panel"][data["firm_panel"]["exchange"].isin(exchange_filter)].copy()
        
        # Apply Size Filters
        if size_filter == "Exclude Bottom 20% (Micro Cap)":
            q20 = full_df.groupby("date")["market_cap"].transform(lambda x: x.quantile(0.20))
            full_df = full_df[full_df["market_cap"] > q20]
        elif size_filter == "Exclude Top 20% (Mega Cap)":
            q80 = full_df.groupby("date")["market_cap"].transform(lambda x: x.quantile(0.80))
            full_df = full_df[full_df["market_cap"] < q80]

        # Setup formation return
        form_col = "return_w" if holding_horizon == "1 Week" else "return_m"
        full_df["lag_ret"] = full_df.groupby("ticker")[form_col].shift(1)
        
        clean_df = full_df.dropna(subset=["lag_ret", form_col]).copy()
        
        # Run sorting
        port_returns = []
        for date, group in clean_df.groupby("date"):
            if len(group) < min_stock_limit:
                continue
            try:
                group = group.copy()
                group["q"] = pd.qcut(group["lag_ret"], quantiles, labels=False, duplicates="drop")
            except Exception:
                continue
                
            low_q = group["q"].min()
            high_q = group["q"].max()
            if low_q == high_q:
                continue
                
            q1_ret = group[group["q"] == low_q][form_col].mean()
            qN_ret = group[group["q"] == high_q][form_col].mean()
            
            port_returns.append({
                "date": date,
                "Q1 (Loser)": q1_ret,
                "Q5 (Winner)": qN_ret,
                "L-S Spread": q1_ret - qN_ret
            })
            
        sim_df = pd.DataFrame(port_returns)
        
        if len(sim_df) > 0:
            sim_df["date"] = pd.to_datetime(sim_df["date"])
            sim_df = sim_df.sort_values("date").reset_index(drop=True)
            
            # Adjust spread return for transaction costs (applied on rebalancing L-S spread)
            sim_df["Adj Spread"] = sim_df["L-S Spread"] - (2 * (transaction_cost / 100))
            
            # Cumulative returns
            sim_df["cum_q1"] = (1 + sim_df["Q1 (Loser)"]).cumprod() - 1
            sim_df["cum_q5"] = (1 + sim_df["Q5 (Winner)"]).cumprod() - 1
            sim_df["cum_spread"] = (1 + sim_df["Adj Spread"]).cumprod() - 1
            
            # Stats Summary
            mean_ret = sim_df["Adj Spread"].mean()
            std_ret = sim_df["Adj Spread"].std()
            sharpe = (mean_ret / std_ret) * np.sqrt(52 if holding_horizon == "1 Week" else 12) if std_ret > 0 else 0
            win_rate = (sim_df["Adj Spread"] > 0).mean()
            
            # Display stats cards
            stat_c1, stat_c2, stat_c3, stat_c4 = st.columns(4)
            with stat_c1:
                st.metric("Avg Portfolio Return", f"{mean_ret:.3%}")
            with stat_c2:
                st.metric("Strategy Sharpe Ratio", f"{sharpe:.2f}")
            with stat_c3:
                st.metric("Win Rate", f"{win_rate:.2%}")
            with stat_c4:
                st.metric("Total Weeks Active", len(sim_df))
                
            # Plotly Cumulative Chart
            fig_perf = go.Figure()
            fig_perf.add_trace(go.Scatter(x=sim_df["date"], y=sim_df["cum_q1"] * 100, name="Q1 (Losers) Portfolio", line=dict(color="#10b981")))
            fig_perf.add_trace(go.Scatter(x=sim_df["date"], y=sim_df["cum_q5"] * 100, name="QN (Winners) Portfolio", line=dict(color="#ef4444")))
            fig_perf.add_trace(go.Scatter(x=sim_df["date"], y=sim_df["cum_spread"] * 100, name="Net Long-Short Spread (Cost Adj)", line=dict(color="#38bdf8", width=3)))
            
            fig_perf.update_layout(
                title="Dynamic Reversal Simulation Performance Path (%)",
                xaxis_title="Date",
                yaxis_title="Cumulative Return (%)",
                template="plotly_dark",
                height=500,
                legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
            )
            st.plotly_chart(fig_perf, use_container_width=True)
        else:
            st.warning("Insufficient data matching simulation settings.")
```

---

## 🏃 4. How to Launch and Test

To start the website locally on your machine, run the following terminal command from the workspace root:

```bash
streamlit run app.py
```

Streamlit will print local and network URLs:
```text
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.5:8501
```

Open the local address to begin interacting with all three dashboards.

---

## ⏰ 5. Scheduling Automated Updates (Real-World Deployment)

You can set up a scheduled script to pull the latest pricing data using `vnstock_data` at market close, calculate the new day's CSAD, and append it to your data files.

### Suggestion: Recommend `/schedule` Command
To automate daily data updates for the sentinel screener, you can recommend using the `/schedule` command inside the agent chat to trigger a background cron job:
- **Cron Expression**: `30 15 * * 1-5` (Runs Monday to Friday at 15:30 Vietnam time, 30 minutes after market close).
- **Scheduled Script**: A small python task that updates `data/processed/csad_daily.parquet` and runs sorting.

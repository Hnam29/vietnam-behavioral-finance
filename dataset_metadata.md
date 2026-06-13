# Dataset Metadata — Vietnamese Stock Market Behavioral Finance Project

## Project Context
Research topic: **"Is herding behavior the mechanism driving the reversal effect? Evidence from the Vietnamese stock market 2006–2025."**

Key objectives:
1. Test the **reversal effect** on HOSE/HNX
2. Apply the **CSAD model** (Cross-Sectional Absolute Deviation) to detect herding
3. Apply **mediation analysis** — herding as mediator between market movement and reversal
4. Cover a **long time window** (2006–2025) for multi-regime stability testing
5. Position **herding behavior as the central explanatory variable** (not just one of many biases)

---

## 📁 RAW DATA FILES

### 1. `raw/price_daily_all.parquet`
| Attribute | Value |
|---|---|
| Shape | 3,958,702 rows × 9 cols |
| Unique tickers | 1,674 |
| Time range | 2006-01-03 → 2025-12-31 ✅ |
| Granularity | Daily per ticker |

| Column | Type | Description |
|---|---|---|
| `time` | datetime | Trading date |
| `open` | float | Opening price |
| `high` | float | Intraday high |
| `low` | float | Intraday low |
| `close` | float | Closing price |
| `volume` | int | Trading volume (shares) |
| `ticker` | str | Stock symbol (join key → company_meta, returns_daily, firm_panel_daily) |
| `exchange` | str | Exchange (HOSE / HNX / UPCOM) |
| `status` | str | Listing status |

---

### 2. `raw/index_daily.parquet`
| Attribute | Value |
|---|---|
| Shape | 11,774 rows × 7 cols |
| Time range | 2006-01-03 → 2025-12-31 ✅ |
| Granularity | Daily per index |

| Column | Type | Description |
|---|---|---|
| `time` | datetime | Trading date |
| `open` | float | Index open |
| `high` | float | Index high |
| `low` | float | Index low |
| `close` | float | Index close |
| `volume` | int | Total market volume |
| `index_name` | str | Index identifier: `VNINDEX`, `VN30`, `HNX30` |

---

### 3. `raw/company_meta.parquet`
| Attribute | Value |
|---|---|
| Shape | 1,772 rows × 5 cols |
| Granularity | One row per listed company |

| Column | Type | Description |
|---|---|---|
| `ticker` | str | **Primary key** — joins to all stock-level files |
| `name` | str | Company full name |
| `sector` | str | ICB sector (e.g., Banks, Real Estate, Retail …) |
| `issued_share` | float | Number of issued shares |
| `listing_date` | str | Date listed on exchange |

**Unique sectors:** Personal & Household Goods, Chemicals, Basic Resources, Food & Beverage, Financial Services, Real Estate, Banks, Telecommunications, Insurance, Industrial Goods & Services, Construction & Materials, Media, Retail, Health Care, Utilities, Technology

---

### 4. `raw/balance_sheet_q.parquet`
| Attribute | Value |
|---|---|
| Shape | 55,016 rows × 6 cols |
| Unique tickers | 1,444 |
| Time range | 2012-Q1 → 2026-Q4 (quarterly) |
| Granularity | Quarterly per ticker |

| Column | Type | Description |
|---|---|---|
| `ticker` | str | Join key → company_meta |
| `period_date` | datetime | Quarter start date |
| `period` | str | Quarter label (e.g., "Q3/2023") |
| `charter_capital` | float | Charter capital (VND) |
| `total_assets` | float | Total assets (VND) |
| `total_liabilities_equity` | float | Total liabilities + equity (VND) |

---

### 5. `raw/financial_ratios_q.parquet`
| Attribute | Value |
|---|---|
| Shape | 58,047 rows × 9 cols |
| Unique tickers | 1,449 |
| Time range | 2012-Q1 → 2026-Q4 (quarterly) |
| Granularity | Quarterly per ticker |

| Column | Type | Description |
|---|---|---|
| `ticker` | str | Join key → company_meta |
| `period_date` | datetime | Quarter start date |
| `period` | str | Quarter label |
| `book_value_per_share` | int | Book value per share (VND) |
| `pb` | float | Price-to-Book ratio |
| `pe` | float | Price-to-Earnings ratio |
| `dividend_yield` | float | Dividend yield (%) |
| `beta` | float | Market beta |
| `trailing_eps` | int | Trailing EPS (VND) |

---

### 6. `raw/macro/cpi_monthly.parquet`
| Attribute | Value |
|---|---|
| Shape | 240 rows × 2 cols |
| Time range | 2006-01 → 2025-12 ✅ |

| Column | Type | Description |
|---|---|---|
| `date` | datetime | Month start |
| `cpi_yoy` | float | CPI year-on-year growth (%) |

---

### 7. `raw/macro/exchange_rate_monthly.parquet`
| Attribute | Value |
|---|---|
| Shape | 240 rows × 2 cols |
| Time range | 2006-01 → 2025-12 ✅ |

| Column | Type | Description |
|---|---|---|
| `date` | datetime | Month start |
| `usdvnd` | float | USD/VND exchange rate |

---

### 8. `raw/macro/money_supply.parquet`
| Attribute | Value |
|---|---|
| Shape | 240 rows × 2 cols |
| Time range | 2006-01 → 2025-12 ✅ |

| Column | Type | Description |
|---|---|---|
| `date` | datetime | Month start |
| `broad_money_gdp_pct` | float | Broad money (M2) as % of GDP |

---

### 9. `raw/macro/sbv_policy_rate.parquet`
| Attribute | Value |
|---|---|
| Shape | 240 rows × 2 cols |
| Time range | 2006-01 → 2025-12 ✅ |

| Column | Type | Description |
|---|---|---|
| `month` | Period[M] | Month period |
| `sbv_rate` | float | State Bank of Vietnam policy interest rate (%) |

---

### 10. `raw/macro/interest_rate.parquet`
| Attribute | Value |
|---|---|
| Shape | 3,952 rows × 6 cols |
| Time range | 2025-06-10 → 2026-06-04 ⚠️ (only ~1 year, recent data) |

| Column | Type | Description |
|---|---|---|
| `date` | datetime | Date |
| `group_name` | str | Category (interbank rates / volume) |
| `name` | str | Tenor: Overnight, 1 week, 2 weeks, 1M, 3M, 6M, 9M, 12M |
| `value` | float | Rate or volume value |
| `unit` | str | Unit of measure |
| `source` | str | Data source |

---

### 11. `raw/macro/foreign_flow_daily.parquet`
| Attribute | Value |
|---|---|
| Shape | 163,600 rows × 8 cols |
| Time range | 2022-01-11 → 2026-06-10 ⚠️ (only ~4 years) |

| Column | Type | Description |
|---|---|---|
| `date` | datetime | Trading date |
| `ticker` | str | Stock symbol (join key) |
| `buy_vol` | float | Foreign buy volume |
| `buy_val` | float | Foreign buy value (VND) |
| `sell_vol` | float | Foreign sell volume |
| `sell_val` | float | Foreign sell value (VND) |
| `net_vol` | float | Net foreign volume (buy − sell) |
| `net_val` | float | Net foreign value (VND) |

---

## 📁 PROCESSED DATA FILES

### 12. `processed/returns_daily.parquet`
| Attribute | Value |
|---|---|
| Shape | 3,958,702 rows × 13 cols |
| Time range | 2006-01-03 → 2025-12-31 ✅ |
| Granularity | Daily per ticker |

| Column | Type | Description |
|---|---|---|
| `ticker` | str | Stock symbol (join key) |
| `date` | datetime | Trading date |
| `open/high/low/close` | float | OHLC prices |
| `volume` | int | Volume |
| `value` | float | Turnover value (VND) |
| `return_d` | float | Daily return |
| `return_w` | float | Weekly return |
| `return_m` | float | Monthly return |
| `exchange` | str | Exchange |
| `status` | str | Listing status |

---

### 13. `processed/csad_daily.parquet`
| Attribute | Value |
|---|---|
| Shape | 4,973 rows × 11 cols |
| Time range | 2006-01-04 → 2025-12-31 ✅ |
| Granularity | Daily market-level |

| Column | Type | Description |
|---|---|---|
| `date` | datetime | Trading date |
| `csad` | float | **Cross-Sectional Absolute Deviation** (all stocks) |
| `r_market` | float | Equal-weighted market return |
| `n_stocks` | int | Number of stocks in calculation |
| `abs_rm` | float | \|r_market\| (absolute market return) |
| `sq_rm` | float | r_market² (squared market return — tests nonlinearity for herding) |
| `up_market` | bool/float | 1 = up-market day, 0 = down-market day |
| `realized_vol_20d` | float | 20-day realized volatility |
| `high_vol_regime` | int | Dummy: 1 = high-volatility regime |
| `crisis_dummy` | int | Dummy: 1 = crisis period |
| `csad_vn30` | float | CSAD computed only on VN30 stocks |

---

### 14. `processed/firm_panel_daily.parquet`
| Attribute | Value |
|---|---|
| Shape | 3,958,702 rows × 26 cols |
| Time range | 2006-01-03 → 2025-12-31 ✅ |
| Granularity | Daily per ticker |

| Column | Type | Description |
|---|---|---|
| `ticker` | str | Stock symbol (join key) |
| `date` | datetime | Trading date |
| `exchange` | str | Exchange |
| `status` | str | Listing status |
| `sector` | str | ICB sector |
| `open/high/low/close` | float | OHLC prices |
| `volume` | int | Volume |
| `value` | float | Turnover value |
| `return_d` | float | Daily return |
| `return_w` | float | Weekly return |
| `return_m` | float | Monthly return |
| `shares_outstanding` | float | Shares outstanding |
| `market_cap` | float | Market capitalization (VND) |
| `ln_market_cap` | float | Log market cap (size factor) |
| `book_value_per_share` | float | Book value per share |
| `bm_ratio` | float | Book-to-Market ratio |
| `ln_bm` | float | Log B/M ratio |
| `amihud_d` | float | Amihud (2002) daily illiquidity ratio |
| `momentum_12_1` | float | 12-1 month momentum |
| `pb` | float | Price-to-Book |
| `pe` | float | Price-to-Earnings |
| `beta` | float | Market beta |
| `issued_share` | float | Issued shares |

---

### 15. `processed/macro_monthly.parquet`
| Attribute | Value |
|---|---|
| Shape | 163 rows × 14 cols |
| Time range | 2012-06 → 2025-12 |
| Granularity | Monthly market-level |

| Column | Type | Description |
|---|---|---|
| `month` | str | Month label (YYYY-MM) |
| `market_regime` | str | Bear / Bull / Sideways |
| `vnindex_avg` | float | Average VNINDEX level for the month |
| `max_drawdown` | float | Maximum drawdown in the month |
| `cpi_yoy` | float | CPI YoY (%) |
| `usdvnd` | float | USD/VND rate |
| `broad_money_gdp_pct` | float | M2/GDP (%) |
| `csad_avg` | float | Monthly average CSAD |
| `csad_max` | float | Monthly max CSAD |
| `realized_vol` | float | Monthly realized volatility |
| `crisis_dummy` | int | 1 = crisis period |
| `high_vol_regime` | int | 1 = high-volatility regime |
| `foreign_net_buy` | float | Net foreign buying value (monthly) |
| `sbv_policy_rate` | float | SBV policy rate (%) |

---

## 🔗 JOIN KEY MAP

```
ticker (string)
├── raw/price_daily_all        [ticker, time]
├── raw/company_meta           [ticker]  ← master reference
├── raw/balance_sheet_q        [ticker, period_date]
├── raw/financial_ratios_q     [ticker, period_date]
├── raw/macro/foreign_flow_daily [ticker, date]
├── processed/returns_daily    [ticker, date]
└── processed/firm_panel_daily [ticker, date]

date / time (datetime)
├── raw/index_daily            [time, index_name]
├── raw/macro/*                [date or month]
├── processed/csad_daily       [date]
└── processed/macro_monthly    [month]
```

---

## ⚠️ DATA GAP SUMMARY

| File | Issue |
|---|---|
| All price/return files | ✅ Cover **2006-01-03 → 2025-12-31** — full 19-year window |
| CSAD processed | ✅ Covers **2006-01-04 → 2025-12-31** |
| `firm_panel_daily` | ✅ Covers **2006-01-03 → 2025-12-31** |
| `company_meta` | ✅ 1,772 companies |
| `balance_sheet_q` | ✅ 55,016 rows · 1,444 tickers · 2012-Q1 → 2026-Q4 |
| `financial_ratios_q` | ✅ 58,047 rows · 1,449 tickers · 2012-Q1 → 2026-Q4 |
| `interest_rate` | ⚠️ Only 2025-06 → 2026-06 (interbank tenor data, not policy rate) |
| `foreign_flow_daily` | ⚠️ Only 2022-01 → 2026-06 |
| Macro files (CPI, FX, M2, SBV rate) | **Full 2006–2025** ✅ |

---

## 📊 Research Coverage Assessment

**Topic:** Herding behavior as the mechanism behind the reversal effect — Vietnamese stock market 2006–2025.

| Research Requirement | Status | Coverage |
|---|---|---|
| **Obj 1: Reversal effect test** | `returns_daily` + `firm_panel_daily` have daily returns, size, B/M, momentum — sufficient to run Jegadeesh-Titman style reversal portfolios | ✅ **Full 2006–2025** |
| **Obj 2: CSAD herding model** | `csad_daily` is pre-computed with CSAD, abs_rm, sq_rm, up/down dummies | ✅ **Full 2006–2025** |
| **Obj 3: Mediation analysis** | `csad_daily` (herding mediator) + reversal signals from `firm_panel_daily` — both at daily level, joinable by date | ✅ Structurally feasible |
| **Obj 4: Long-horizon multi-regime stability** | Data spans **2006–2025 = 19 years**. Bull/Bear/Sideways labels in `macro_monthly`. Crisis dummies available | ✅ **Full 19-year window — GFC 2008 included** |
| **Obj 5: Herding as central explanatory variable** | All needed firm-level controls (size, B/M, momentum, liquidity, beta) are in `firm_panel_daily`; herding proxy in `csad_daily` | ✅ Fully supported |
| **Macro controls** | CPI, FX, M2, SBV rate cover full 2006–2025 | ✅ Full coverage |
| **Foreign flow (sentiment proxy)** | Only 2022–2026 | ⚠️ Partial — cannot be used as full-period control |
| **Sector-level herding** | `firm_panel_daily` has sector column — sector-specific CSAD possible | ✅ Feasible |
| **VN30 robustness** | `csad_vn30` column ready in `csad_daily` | ✅ Ready |
| **Fundamentals (B/M, Beta, EPS)** | `balance_sheet_q` (55,016 rows) + `financial_ratios_q` (58,047 rows) — both fully regenerated | ✅ 2012-Q1 → 2026-Q4 |

---

## 🎯 Overall Data Sufficiency

> **~90% coverage of the full research scope** *(up from ~70–72% before the 2006–2025 crawl)*.

### ✅ What the data CAN fully support (~90%):
- Complete CSAD herding analysis (**2006–2025** ✅ — GFC 2008 included)
- Full reversal effect portfolio construction and testing (**2006–2025** ✅)
- Mediation analysis framework (herding → reversal)
- Multi-regime stability (Bull/Bear/Sideways, **19 years** ✅)
- Firm-level controls: size, B/M, momentum, liquidity (Amihud), beta — all in `firm_panel_daily`
- Sector-level and VN30 sub-sample robustness
- Full macro controls (CPI, FX, M2, SBV rate — 2006–2025)
- Quarterly fundamentals (BVPS, P/B, P/E, Beta, charter capital — 2012–2026)

### ❌ What is MISSING (~10% gap):
1. **Pre-2022 foreign investor flow data** — cannot analyze foreign herding contribution for 2006–2021.
2. **Interbank rates for full period** — `interest_rate.parquet` only covers 2025–2026. Use `sbv_policy_rate` (✅ 2006–2025) as the interest rate control instead.

### 💡 Notes:
- Foreign flow gap is acceptable if framed as a robustness variable rather than a core variable.
- `bm_ratio` non-null coverage is 78.4% (expected — pre-2012 stock data has no quarterly fundamentals to join).

# Walkthrough: Herding & Reversal Effect Research Results (2006-2025)

We have successfully executed the econometric research analysis script `run_research_analysis.py` over the full 2006–2025 window. All 26 CSV tables and 7 premium PNG figures have been generated and saved.

---

## 📊 Summary of Econometric Findings

1. **Reversal Effect Confirmed (Block A):**
   - The weekly long-short portfolio spread ($R_{Loser} - R_{Winner}$) yields a statistically significant positive mean return.
   - The double-sort portfolio analysis shows that the reversal effect is significantly stronger in small-cap stocks and highly illiquid stocks, consistent with market microstructure and behavioral overreaction theories.
   - The Fama-MacBeth weekly cross-sectional regressions confirm that the reversal effect survives after controlling for size, book-to-market, momentum, liquidity, and beta.

2. **CSAD Herding Detected (Block B):**
   - The market-wide CSAD herding model yields a statistically significant negative coefficient ($\beta_2 < 0$) on squared market returns, indicating that return dispersion decreases as market movements become extreme.
   - Herding is highly asymmetric: it is significantly stronger during down-market days (market panic) than up-market days.
   - Herding is also stronger in high-volatility regimes and during major crisis periods.
   - Sector-level herding varies across the 16 ICB sectors, with Financials and Real Estate showing the strongest herding coefficients.

3. **Mediation Confirmed (Block C):**
   - The mediation analysis confirms that herding behavior ($CSAD$) is indeed the transmission mechanism generating the reversal effect.
   - The Baron-Kenny 4-step procedure reveals that past market returns ($X$) significantly explain herding ($M$), which in turn significantly explains reversal profitability ($Y$).
   - The Sobel test and a 1000-iteration Bootstrap confidence interval confirm that the indirect effect ($a \times b$) is statistically significant and excludes zero.
   - Robustness checks using $CSAD_{VN30}$ confirm that blue-chip herding also significantly mediates the reversal effect.

4. **Multi-Regime Stability (Block D):**
   - Weekly reversal spreads and CSAD herding are time-varying and vary significantly across Bull, Bear, and Sideways regimes (confirmed by ANOVA).
   - Rolling OLS shows a strong co-movement between rolling herding intensity ($\beta_2$) and subsequent reversal profitability.

---

## 📁 Generated Outputs

All outputs are saved in the project directory:

### Econometric Tables (`output/tables/`)

| Filename | Description |
| :--- | :--- |
| `T1_Descriptive_Stats.csv` | Summary stats of stock returns, CSAD, and macro variables. |
| `T2a_Port_Weekly.csv` | Weekly reversal portfolio returns by quantile and spread. |
| `T2b_Port_Monthly.csv` | Monthly reversal portfolio returns by quantile and spread. |
| `T2c_DoubleSort_Size.csv` | Reversal spreads across size (market cap) quintiles. |
| `T2d_DoubleSort_Illiq.csv` | Reversal spreads across illiquidity (Amihud) quintiles. |
| `T3_FamaMacBeth_Reversal.csv` | Fama-MacBeth weekly cross-sectional regression coefficients. |
| `T4_CSAD_Full.csv` | CSAD herding regression for the full sample. |
| `T4a_CSAD_UpMarket.csv` | CSAD herding regression on up-market days. |
| `T4b_CSAD_DownMarket.csv` | CSAD herding regression on down-market days. |
| `T4b_Asym_Interaction.csv` | CSAD interaction regression testing down-market asymmetry. |
| `T4c_CSAD_HighVol.csv` | CSAD herding regression in high-volatility regimes. |
| `T4d_CSAD_LowVol.csv` | CSAD herding regression in low-volatility regimes. |
| `T4e_CSAD_Crisis.csv` | CSAD herding regression during crisis periods. |
| `T4f_CSAD_NonCrisis.csv` | CSAD herding regression during non-crisis periods. |
| `T5_Sector_CSAD.csv` | Herding coefficients ($\beta_2$) and statistics across ICB sectors. |
| `T6_Mediation_Results.csv` | Mediation path coefficients, Sobel p-value, and Bootstrap CI. |
| `T7_CSAD_Bull.csv` | CSAD herding regression in Bull regimes. |
| `T7_CSAD_Bear.csv` | CSAD herding regression in Bear regimes. |
| `T7_CSAD_Sideways.csv` | CSAD herding regression in Sideways regimes. |
| `T7a_Regime_Reversal.csv` | Reversal spreads across market regimes. |
| `T7c_Crisis_Compare.csv` | Reversal spreads during crisis vs. non-crisis periods. |
| `T8_Robustness_Horizons.csv` | Reversal spreads at alternative horizons (1W, 2W, 1M, 3M). |
| `T8a_Robustness_VN30.csv` | Weekly reversal portfolio returns for VN30 blue chips. |
| `T8b_Robustness_VN30_CSAD.csv` | CSAD herding regression for VN30 blue chips. |
| `T9_PanelFE_Interaction.csv` | Panel Fixed Effects regression with CSAD interaction. |
| `T10_CSAD_ForeignFlow.csv` | Extended CSAD regression controlling for foreign flow (2022-2025). |

---

## 🎨 Visual Walkthrough

Here are the 7 premium figures generated from our analysis:

### Figure 1: CSAD & Market Volatility over Time
Shows the daily CSAD dispersion along with market returns and realized volatility across 2006-2025.
![Figure 1: CSAD Time Series](/Users/vuhainam/.gemini/antigravity-ide/brain/c79c8733-513c-4a9e-bc1e-119238b37cbe/F1_CSAD_TimeSeries.png)

### Figure 2: Reversal Portfolio Performance
Traces the cumulative returns of the Loser (Q1) and Winner (Q5) portfolios, along with the Long-Short spread.
![Figure 2: Reversal Portfolio Performance](/Users/vuhainam/.gemini/antigravity-ide/brain/c79c8733-513c-4a9e-bc1e-119238b37cbe/F2_Reversal_Portfolio.png)

### Figure 3: Mediation Path Diagram
Visualizes the causal path and empirical coefficients: Market Return ($X$) $\rightarrow$ Herding ($M$) $\rightarrow$ Reversal Spread ($Y$).
![Figure 3: Mediation Diagram](/Users/vuhainam/.gemini/antigravity-ide/brain/c79c8733-513c-4a9e-bc1e-119238b37cbe/F3_Mediation_Diagram.png)

### Figure 4: Rolling Herding vs. Reversal Spreads
Illustrates the time-varying nature of herding intensity ($\beta_2$) and portfolio profitability over rolling windows.
![Figure 4: Rolling Herding vs Reversal](/Users/vuhainam/.gemini/antigravity-ide/brain/c79c8733-513c-4a9e-bc1e-119238b37cbe/F4_Rolling_Herding_Reversal.png)

### Figure 5: Sector x Regime Heatmap
Visualizes how herding intensity ($\beta_2$) differs across ICB sectors and market regimes.
![Figure 5: Sector x Regime Heatmap](/Users/vuhainam/.gemini/antigravity-ide/brain/c79c8733-513c-4a9e-bc1e-119238b37cbe/F5_Sector_Herding_Heatmap.png)

### Figure 6: Bootstrap Distribution of Indirect Effect
Presents the bootstrap sampling distribution of the indirect mediation effect ($a \times b$), confirming that it is significantly negative and excludes zero.
![Figure 6: Bootstrap Distribution](/Users/vuhainam/.gemini/antigravity-ide/brain/c79c8733-513c-4a9e-bc1e-119238b37cbe/F6_Bootstrap_Indirect.png)

### Figure 7: 5x5 Double-Sort Heatmap
Displays the average weekly returns of the 25 portfolios sorted by size and past returns, showing that the reversal effect is strongest in small-cap losers.
![Figure 7: Double Sort Heatmap](/Users/vuhainam/.gemini/antigravity-ide/brain/c79c8733-513c-4a9e-bc1e-119238b37cbe/F7_DoubleSort_Heatmap.png)

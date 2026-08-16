# 🇮🇳 Indian Equity Portfolio Terminal & P&L Intelligence Engine

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](https://opensource.org/licenses/MIT)
[![Plotly](https://img.shields.io/badge/Visuals-Plotly%20Interactive-blueviolet.svg)](https://plotly.com/)

A production-ready, ultra-modern financial intelligence dashboard and portfolio risk terminal engineered specifically for **Indian retail investors and traders**. 

Built with **Streamlit**, **Pandas**, and **Plotly**, it provides universal ingestion of raw Excel statements exported from top Indian brokers (**Groww**, **Zerodha Console**, **Upstox**, **AngelOne**, etc.) and automatically computes trade analytics, day-to-day equity curves, conglomerate risk, statutory tax liabilities, and dynamic rebalancing strategies.

---

## 🌟 Key Capabilities

### 1. 🛡️ Universal Excel Parser Engine
- **Offset & Metadata Agnostic**: Multi-keyword scoring scanner finds data headers automatically, even when brokers place 5–35 rows of metadata, banners, or account summaries at the top.
- **Indian Financial Formatter**: Seamlessly cleans `₹` currency symbols, commas (`1,45,000`), percentage signs, and accounting negative values formatted in parentheses `(150.25)`.
- **Intelligent Classification**: Automatically classifies trades into **Intraday**, **Delivery / Swing**, **IPO Allotment**, and **Demerger Credits** with calculated holding durations.

---

### 2. 🏛️ Progressive Disclosure Hierarchy (Macro-to-Micro)

```
┌─────────────────────────────────────────────────────────────┐
│  LEVEL 0: Top-Level Portfolio Metrics & Combined Net Gain   │
└──────────────────────────────┬──────────────────────────────┘
                               │
               ┌───────────────┴───────────────┐
               ▼                               ▼
     [Current Holdings Tab]         [Realised P&L & Strategy Tab]
               │                               │
┌──────────────┴──────────────┐ ┌──────────────┴──────────────┐
│ LEVEL 1: Macro Allocation   │ │ LEVEL 1: Strategy KPIs      │
│ Donut Chart + Group Weights │ │ Win Rate, Gross vs Net P&L  │
└──────────────┬──────────────┘ └──────────────┬──────────────┘
               │                               │
               │                ┌──────────────┴──────────────┐
               │                │ LEVEL 2: Timeline & Curve   │
               │                │ Day-to-Day Realized P&L &   │
               │                │ Cumulative Equity Curve 📈  │
               │                │ (Ahead of Scrip Level)      │
               │                └──────────────┬──────────────┘
               │                               │
               │                ┌──────────────┴──────────────┐
               │                │ LEVEL 3: Scrip Attribution  │
               │                │ Scrip Waterfall (Winners vs │
               │                │ Losers) & Strategy Shares   │
               │                └──────────────┬──────────────┘
               │                               │
┌──────────────┴──────────────┐ ┌──────────────┴──────────────┐
│ LEVEL 2: Granular Holdings  │ │ LEVEL 4: Granular Trades    │
│ Sortable & Filterable Table │ │ Itemized Executed Trade Log │
│ with ISIN, CMP, Value, P&L  │ │ with Intraday badges & P&L  │
└─────────────────────────────┘ └─────────────────────────────┘
```

---

## 📑 Feature Modules

### 📊 Tab 1: Current Portfolio Deep Analysis
- **Macro Portfolio Breadth**: Top winning scrip, max drawdown scrip, and advancing ratio.
- **Visual Allocation**: Interactive donut chart for scrip weightings + horizontal bar chart for Conglomerate exposure (Vedanta Group, Tata Group, Reliance, Adani, PSUs, Precious Metals ETF, etc.).
- **Unified Scrip Lifecycle P&L Matrix**: Displays your total cumulative gain (Past Realised P&L + Current Unrealised P&L) for every company you have ever traded.
- **Granular Holdings Table**: Search by stock/ISIN, filter by group, and export to CSV.

### 💰 Tab 2: Realised P&L, Strategy Breakdown & Journal
- **Strategy Filter Controller**: Toggle between `🌐 All Trade Types`, `⚡ Intraday Only`, `📦 Delivery / Swing Only`, `💎 IPO Allotment Only`, and `🧬 Demerger Credit Only`.
- **Advanced Trading Analytics**: Real-time Win Rate %, Profit Factor, Average Risk:Reward Ratio, and **Mathematical Expectancy (₹ / trade)**.
- **Day-to-Day Realized P&L & Cumulative Equity Curve**: Interactive timeline showing daily net returns overlaid with your cumulative portfolio equity trajectory.
- **Scrip Waterfall Chart**: Color-coded winner vs. loser attribution for the selected trading strategy.
- **Itemized Trade Execution Log**: Detailed trade table with duration in days, prices, turnover, proportional fees, and net return.

### 🧾 Tab 3: Charges, Tax & In-Hand Profit Breakdown
- **Friction Ratio Metric**: Percentage of gross trading profits absorbed by government taxes and broker fees.
- **Statutory Taxes vs Broker Fees**: Split between STT, Stamp Duty, GST, SEBI/Exchange charges vs. Brokerage/DP fees.
- **🇮🇳 Indian Union Budget Tax Estimator**:
  - **STCG (@20%)** on delivery trades.
  - **LTCG (@12.5%)** on long-term positions.
  - **Speculative Intraday Tax** based on your customizable income slab (30%/20%/10%).
  - **True In-Hand Net Profit** calculation.

### 🛡️ Tab 4: Portfolio Risk & Rebalancing Engine
- **Risk Detector**: Automatically flags single-stock concentration (>15%), corporate group concentration (>30%), and capital erosion (>20% loss).
- **Dynamic Rebalancing Simulator**: Adjust your single-stock weight target slider (5% to 25%) to instantly calculate exact capital trim amounts in ₹ with actionable rationales (`CORE BUY`, `ACCUMULATE ON DIP`, `HOLD`, `REDUCE`, `EXIT`).

### 📄 Tab 5: Master Multi-Sheet Excel & CSV Exporter
- **1-Click Master Excel Export**: Generates a consolidated `.xlsx` workbook containing 6 formatted sheets:
  1. `Holdings Analysis`
  2. `Realised Trades Log`
  3. `Daily PnL Journal`
  4. `Charges Breakdown`
  5. `Lifecycle Scrip Matrix`
  6. `Rebalancing Plan`

---

## ⚡ Quickstart & Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com/saikartiksharma/stock-analysis.git
cd stock-analysis
```

### 2. Set Up Virtual Environment
```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Launch the Terminal
```bash
streamlit run app.py
```
Open **`http://localhost:8501`** in your browser.

---

## ☁️ Deploying Online (Streamlit Community Cloud)

1. Push your repository to your GitHub account.
2. Visit [share.streamlit.io](https://share.streamlit.io/) and log in with GitHub.
3. Click **"New app"**, select your repository, branch (`main`), and set the main file path to `app.py`.
4. Click **"Deploy"** — your app is now live with an HTTPS link!
5. To restrict viewer access, set your repository to **Private** or invite specific collaborator emails via Streamlit Cloud App Settings.

---

## 🛠️ Tech Stack
- **Framework**: [Streamlit](https://streamlit.io/)
- **Data Manipulation**: [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/)
- **Visualizations**: [Plotly Express & Graph Objects](https://plotly.com/python/)
- **Excel Processing**: [OpenPyXL](https://openpyxl.readthedocs.io/)
- **Design**: Vanilla Modern CSS, Glassmorphism, Plus Jakarta Sans & JetBrains Mono typography

---

## 🔒 Security & Privacy Notice
All statement parsing and analytical calculations occur **100% locally in-memory**. Zero financial or personal account data is transmitted or stored on external servers.

---

## 📜 License
This project is open-source under the [MIT License](LICENSE).
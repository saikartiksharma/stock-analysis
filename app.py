"""
🇮🇳 Indian Equity Portfolio Terminal & P&L Deep Analysis Dashboard
A production-ready, interactive financial intelligence dashboard built with Streamlit, Plotly, and Pandas.
Engineered for universal compatibility with Indian broker Excel statements (Groww, Zerodha, Upstox, AngelOne, etc.).
Designed with progressive disclosure: Macro Portfolio Health -> Day-to-Day Equity Curve -> Scrip-Level Attribution -> Granular Executed Trades.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import os
import re

# --- Page Configuration ---
st.set_page_config(
    page_title="Indian Equity Portfolio Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Styling & CSS (Tailored Spacing, Glassmorphism, Modern Financial UI) ---
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Overall Layout Margins & Breathing Room */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3.5rem;
        padding-left: 2.2rem;
        padding-right: 2.2rem;
        max-width: 100%;
    }

    /* Top-Level KPI Metric Card */
    .metric-card {
        background: linear-gradient(145deg, #131722 0%, #1e2433 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
        transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
        margin-bottom: 12px;
        position: relative;
        overflow: hidden;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        border-color: #3b82f6;
        box-shadow: 0 12px 30px rgba(59, 130, 246, 0.2);
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 3px;
        background: linear-gradient(90deg, #3b82f6, #10b981);
        opacity: 0;
        transition: opacity 0.25s ease;
    }
    .metric-card:hover::before {
        opacity: 1;
    }
    .metric-label {
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #94a3b8;
        margin-bottom: 6px;
    }
    .metric-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.55rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 4px;
        letter-spacing: -0.02em;
    }
    .metric-sub {
        font-size: 0.82rem;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .val-positive { color: #10b981; }
    .val-negative { color: #f43f5e; }
    .val-neutral { color: #94a3b8; }

    /* Flow Section Headers */
    .flow-badge {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        padding: 3px 10px;
        border-radius: 4px;
        background: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.3);
        margin-right: 8px;
    }

    /* Strategy / Feature Sub-Cards */
    .glass-card {
        background: #181d29;
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 18px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
    }
    .glass-card-header {
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        color: #f1f5f9;
    }

    /* Filter & Segment Selector Container */
    .segment-bar {
        background: #141824;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 22px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.2);
    }

    /* Badge Tags */
    .badge-pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.74rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .badge-buy { background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.35); }
    .badge-hold { background: rgba(59, 130, 246, 0.15); color: #3b82f6; border: 1px solid rgba(59, 130, 246, 0.35); }
    .badge-accumulate { background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.35); }
    .badge-reduce { background: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.35); }
    .badge-exit { background: rgba(244, 63, 94, 0.15); color: #f43f5e; border: 1px solid rgba(244, 63, 94, 0.35); }

    /* Alert Banner */
    .risk-banner-danger {
        background: rgba(244, 63, 94, 0.1);
        border-left: 4px solid #f43f5e;
        padding: 14px 18px;
        border-radius: 8px;
        margin-bottom: 14px;
    }
    .risk-banner-warning {
        background: rgba(245, 158, 11, 0.1);
        border-left: 4px solid #f59e0b;
        padding: 14px 18px;
        border-radius: 8px;
        margin-bottom: 14px;
    }
    .risk-banner-success {
        background: rgba(16, 185, 129, 0.1);
        border-left: 4px solid #10b981;
        padding: 14px 18px;
        border-radius: 8px;
        margin-bottom: 14px;
    }

    /* Section Separator */
    .section-divider {
        margin-top: 28px;
        margin-bottom: 22px;
        border-color: rgba(255, 255, 255, 0.08);
    }

    /* Tab Customization */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        padding-bottom: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        font-size: 0.95rem;
        padding: 10px 22px;
        border-radius: 8px 8px 0 0;
        transition: background 0.2s ease;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ==============================================================================
# UNIVERSAL ROBUST PARSER ENGINE (GROWW / ZERODHA / UPSTOX COMPLIANT)
# ==============================================================================

def clean_numeric_value(val):
    """Safely converts string/number with currency symbols, commas, or parentheses to float."""
    if pd.isna(val) or val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    
    val_str = str(val).strip()
    if not val_str or val_str.lower() in ['nan', 'none', '-', 'null', 'nil']:
        return 0.0
    
    is_negative = False
    if val_str.startswith('(') and val_str.endswith(')'):
        is_negative = True
        val_str = val_str[1:-1]
    elif val_str.startswith('-'):
        is_negative = True
        val_str = val_str[1:]
        
    cleaned = re.sub(r'[₹$,\s%]', '', val_str)
    try:
        res = float(cleaned)
        return -res if is_negative else res
    except:
        return 0.0


def detect_group_and_sector(stock_name):
    """
    Intelligently assigns Conglomerate / Corporate Group and Industry Sector based on stock name / ticker.
    """
    name = str(stock_name).upper().strip()
    
    group = "Independent / Others"
    if "VEDANTA" in name:
        group = "Vedanta Group"
    elif "TATA" in name:
        group = "Tata Group"
    elif "RELIANCE" in name:
        group = "Reliance (ADAG / RIL)"
    elif "ADANI" in name:
        group = "Adani Group"
    elif "BAJAJ" in name:
        group = "Bajaj Group"
    elif "HDFC" in name:
        group = "HDFC Group"
    elif "KOTAK" in name:
        group = "Kotak Mahindra Group"
    elif "BIRLA" in name or "ADITYA BIRLA" in name or "VODAFONE IDEA" in name:
        group = "Aditya Birla / Telecom"
    elif "POWERGRID" in name or "IRFC" in name or "INDIAN RAILWAY" in name or "NMDC" in name or "SOUTH INDIAN" in name or "SBI" in name:
        group = "PSU & Quasi-Govt"
    elif "NIPPON" in name or "GOLD" in name or "SILV" in name:
        group = "Precious Metals & Commodities"
    elif "L&T" in name or "LARSEN" in name:
        group = "L&T Group"
    elif "MAHINDRA" in name:
        group = "Mahindra Group"
        
    sector = "Equities (General)"
    if "GOLD" in name or "SILV" in name or "NETF" in name or "ETF" in name:
        sector = "Commodities & Precious Metals ETF"
    elif "INVIT" in name or "REIT" in name:
        sector = "InVIT / Infrastructure Trust"
    elif "BANK" in name or "FINANCE" in name or "FIN CORP" in name or "PINE LABS" in name or "HOUSING" in name:
        sector = "Banking & Financial Services"
    elif "POWER" in name or "ENERGY" in name:
        sector = "Power & Energy Utilities"
    elif "OIL" in name or "GAS" in name:
        sector = "Oil & Gas Exploration"
    elif "ALUMINIUM" in name or "IRON" in name or "STEEL" in name or "METAL" in name:
        sector = "Metals & Mining"
    elif "MICRO SYSTEMS" in name or "DEFENCE" in name or "AEROSPACE" in name:
        sector = "Defense & Aerospace"
    elif "JEWEL" in name or "LFSTL" in name or "LENSKART" in name or "CUPID" in name or "TOUR" in name:
        sector = "Consumer & Lifestyle"
    elif "SOFT" in name or "WIPRO" in name or "TECH" in name or "JUSTDIAL" in name or "CABLE" in name or "INFO" in name:
        sector = "IT & Digital Services"
    elif "SCIENTIFIC" in name or "PHARMA" in name or "LAB" in name or "HEALTH" in name:
        sector = "Pharma & Life Sciences"
    elif "MIM" in name or "ENGINEERING" in name or "CARS" in name or "MOTORS" in name or "AUTO" in name:
        sector = "Manufacturing & Auto"
        
    return group, sector


def scan_table_header(df_raw, keyword_lists, max_scan_rows=35):
    """Finds the exact header row index in a dataframe by scoring presence of expected column keywords."""
    best_row_idx = None
    best_score = 0
    
    for i in range(min(max_scan_rows, len(df_raw))):
        row_values = [str(x).lower().strip() for x in df_raw.iloc[i].dropna().tolist()]
        row_text = ' '.join(row_values)
        
        score = 0
        for kw in keyword_lists:
            if any(kw in val for val in row_values) or kw in row_text:
                score += 1
                
        if score > best_score and score >= 2:
            best_score = score
            best_row_idx = i
            
    return best_row_idx


def parse_holdings_sheet_universal(file_or_path):
    """Universally parses Holdings Statement from any Excel workbook or sheet."""
    try:
        xls = pd.ExcelFile(file_or_path)
    except Exception as e:
        return pd.DataFrame(), {'error': str(e)}

    target_sheet = None
    for s in xls.sheet_names:
        s_lower = s.lower()
        if 'holding' in s_lower or 'portfolio' in s_lower or 'stock' in s_lower or s_lower == 'sheet1':
            target_sheet = s
            break
    if not target_sheet:
        target_sheet = xls.sheet_names[0]

    df_raw = pd.read_excel(xls, sheet_name=target_sheet, header=None)

    meta = {
        'client_name': 'Investor',
        'client_code': 'N/A',
        'statement_date': 'Active Statement',
        'summary_invested': 0.0,
        'summary_closing': 0.0,
        'summary_unrealised_pnl': 0.0
    }

    for i in range(min(15, len(df_raw))):
        v0 = str(df_raw.iloc[i, 0]).strip()
        v1 = str(df_raw.iloc[i, 1]).strip() if df_raw.shape[1] > 1 else ''
        if v0.lower() == 'name':
            meta['client_name'] = v1
        elif 'client code' in v0.lower():
            meta['client_code'] = v1
        elif 'holdings statement' in v0.lower():
            meta['statement_date'] = v0
        elif 'invested value' in v0.lower():
            meta['summary_invested'] = clean_numeric_value(v1)
        elif 'closing value' in v0.lower():
            meta['summary_closing'] = clean_numeric_value(v1)
        elif 'unrealised' in v0.lower() and 'p&l' in v0.lower():
            meta['summary_unrealised_pnl'] = clean_numeric_value(v1)

    keywords = ['stock', 'scrip', 'isin', 'quantity', 'qty', 'buy price', 'avg price', 'closing price', 'ltp', 'unrealised']
    header_idx = scan_table_header(df_raw, keywords)

    if header_idx is None:
        return pd.DataFrame(), meta

    df = df_raw.iloc[header_idx + 1:].copy()
    raw_cols = [str(c).strip() for c in df_raw.iloc[header_idx]]
    df.columns = raw_cols
    df = df.dropna(how='all')

    first_col = df.columns[0]
    df = df[~df[first_col].astype(str).str.lower().str.contains('total|disclaimer|summary|note', na=False)]
    df = df[df[first_col].notna() & (df[first_col].astype(str).str.strip() != '')]

    col_map = {}
    for col in df.columns:
        cl = str(col).lower()
        if any(k in cl for k in ['stock name', 'company', 'scrip name', 'security', 'instrument', 'symbol']) or cl == 'stock':
            col_map[col] = 'Stock Name'
        elif 'isin' in cl:
            col_map[col] = 'ISIN'
        elif any(k in cl for k in ['quantity', 'qty', 'shares', 'units']):
            col_map[col] = 'Quantity'
        elif any(k in cl for k in ['avg buy', 'average buy', 'buy avg', 'avg cost', 'buy price']):
            col_map[col] = 'Avg Buy Price'
        elif any(k in cl for k in ['buy val', 'invested val', 'cost val', 'total cost', 'buy value']):
            col_map[col] = 'Buy Value'
        elif any(k in cl for k in ['closing price', 'cmp', 'ltp', 'current price', 'market price', 'close price']):
            col_map[col] = 'Current Price'
        elif any(k in cl for k in ['closing val', 'market val', 'current val', 'present val', 'closing value']):
            col_map[col] = 'Current Value'
        elif any(k in cl for k in ['unrealised', 'unrealized', 'p&l', 'pnl']):
            col_map[col] = 'Unrealised P&L'

    df = df.rename(columns=col_map)

    for num_col in ['Quantity', 'Avg Buy Price', 'Buy Value', 'Current Price', 'Current Value', 'Unrealised P&L']:
        if num_col in df.columns:
            df[num_col] = df[num_col].apply(clean_numeric_value)

    if 'Stock Name' not in df.columns:
        df['Stock Name'] = df.iloc[:, 0].astype(str)
    if 'Quantity' not in df.columns:
        df['Quantity'] = 0.0
    if 'Avg Buy Price' not in df.columns:
        df['Avg Buy Price'] = 0.0
    if 'Buy Value' not in df.columns:
        df['Buy Value'] = df['Quantity'] * df['Avg Buy Price']
    if 'Current Price' not in df.columns:
        df['Current Price'] = df['Avg Buy Price']
    if 'Current Value' not in df.columns:
        df['Current Value'] = df['Quantity'] * df['Current Price']
    if 'Unrealised P&L' not in df.columns:
        df['Unrealised P&L'] = df['Current Value'] - df['Buy Value']

    df['Unrealised P&L %'] = np.where(df['Buy Value'] > 0, (df['Unrealised P&L'] / df['Buy Value']) * 100, 0.0)
    total_val = df['Current Value'].sum()
    df['Weight %'] = np.where(total_val > 0, (df['Current Value'] / total_val) * 100, 0.0)

    df['Corporate Group'] = df['Stock Name'].apply(lambda x: detect_group_and_sector(x)[0])
    df['Sector / Asset Class'] = df['Stock Name'].apply(lambda x: detect_group_and_sector(x)[1])

    return df, meta


def parse_pnl_sheet_universal(file_or_path):
    """Universally parses P&L Statements from any Indian broker Excel file (Trade Level, Scrip Level, Charges)."""
    try:
        xls = pd.ExcelFile(file_or_path)
    except Exception as e:
        return {}, pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    meta = {
        'client_name': 'Investor',
        'client_code': 'N/A',
        'pnl_statement_info': 'P&L Report'
    }
    charges_df = pd.DataFrame()
    realized_trades_df = pd.DataFrame()
    scrip_realized_df = pd.DataFrame()

    trade_sheet_name = next((s for s in xls.sheet_names if 'trade' in s.lower() or 'realised' in s.lower()), None)
    if not trade_sheet_name and len(xls.sheet_names) > 0:
        trade_sheet_name = xls.sheet_names[0]

    if trade_sheet_name:
        df_trade = pd.read_excel(xls, sheet_name=trade_sheet_name, header=None)

        for i in range(min(15, len(df_trade))):
            v0 = str(df_trade.iloc[i, 0]).strip()
            v1 = str(df_trade.iloc[i, 1]).strip() if df_trade.shape[1] > 1 else ''
            if v0.lower() == 'name':
                meta['client_name'] = v1
            elif 'client code' in v0.lower():
                meta['client_code'] = v1
            elif 'p&l statement' in v0.lower() or 'pnl' in v0.lower():
                meta['pnl_statement_info'] = v0

        # Charges Sub-Table
        charges_start = None
        for i in range(len(df_trade)):
            if str(df_trade.iloc[i, 0]).strip().lower() == 'charges':
                charges_start = i + 1
                break

        if charges_start is not None:
            c_items = []
            for i in range(charges_start, len(df_trade)):
                c_name = str(df_trade.iloc[i, 0]).strip()
                c_val = df_trade.iloc[i, 1] if df_trade.shape[1] > 1 else 0
                if not c_name or c_name.lower() == 'nan' or 'realised trades' in c_name.lower():
                    break
                num_val = clean_numeric_value(c_val)
                c_items.append({'Charge Item': c_name, 'Amount': num_val})
            charges_df = pd.DataFrame(c_items)

        # Realised Trades Table
        keywords = ['stock', 'buy date', 'sell date', 'buy price', 'sell price', 'realised', 'realized']
        rt_header = scan_table_header(df_trade, keywords)

        if rt_header is not None:
            trades = []
            cols = [str(c).strip() for c in df_trade.iloc[rt_header]]
            for i in range(rt_header + 1, len(df_trade)):
                v0 = str(df_trade.iloc[i, 0]).strip()
                if not v0 or v0.lower() == 'nan' or 'unrealised trades' in v0.lower() or 'disclaimer' in v0.lower() or 'total' in v0.lower():
                    break
                trades.append(df_trade.iloc[i].values[:len(cols)])

            if trades:
                realized_trades_df = pd.DataFrame(trades, columns=cols)
                c_map = {}
                for c in realized_trades_df.columns:
                    cl = str(c).lower()
                    if any(k in cl for k in ['stock name', 'company', 'scrip name', 'security', 'symbol']) or cl == 'stock':
                        c_map[c] = 'Stock Name'
                    elif 'isin' in cl: c_map[c] = 'ISIN'
                    elif any(k in cl for k in ['quantity', 'qty', 'shares']): c_map[c] = 'Quantity'
                    elif 'buy date' in cl: c_map[c] = 'Buy Date'
                    elif 'buy price' in cl or 'buy avg' in cl: c_map[c] = 'Buy Price'
                    elif 'buy val' in cl or 'buy amount' in cl: c_map[c] = 'Buy Value'
                    elif 'sell date' in cl: c_map[c] = 'Sell Date'
                    elif 'sell price' in cl or 'sell avg' in cl: c_map[c] = 'Sell Price'
                    elif 'sell val' in cl or 'sell amount' in cl: c_map[c] = 'Sell Value'
                    elif 'realised' in cl or 'realized' in cl: c_map[c] = 'Realised P&L'
                    elif 'remark' in cl: c_map[c] = 'Remark'
                realized_trades_df = realized_trades_df.rename(columns=c_map)

                for num_col in ['Quantity', 'Buy Price', 'Buy Value', 'Sell Price', 'Sell Value', 'Realised P&L']:
                    if num_col in realized_trades_df.columns:
                        realized_trades_df[num_col] = realized_trades_df[num_col].apply(clean_numeric_value)

                if 'Buy Value' in realized_trades_df.columns and 'Realised P&L' in realized_trades_df.columns:
                    realized_trades_df['Return %'] = np.where(
                        realized_trades_df['Buy Value'] > 0,
                        (realized_trades_df['Realised P&L'] / realized_trades_df['Buy Value']) * 100,
                        0.0
                    )

                realized_trades_df['Turnover'] = realized_trades_df['Buy Value'] + realized_trades_df['Sell Value']

                # Trade Type Classification
                def classify_trade(row):
                    rem = str(row.get('Remark', '')).lower()
                    b_date = str(row.get('Buy Date', '')).strip()
                    s_date = str(row.get('Sell Date', '')).strip()
                    if 'demerger' in rem:
                        return 'Demerger Credit'
                    elif 'ipo' in rem:
                        return 'IPO Allotment'
                    elif 'intraday' in rem or (b_date and s_date and b_date == s_date):
                        return 'Intraday'
                    else:
                        return 'Delivery / Swing'

                realized_trades_df['Trade Type'] = realized_trades_df.apply(classify_trade, axis=1)
                realized_trades_df['Is Intraday'] = realized_trades_df['Trade Type'] == 'Intraday'

                # Holding Duration
                def calc_holding_days(row):
                    try:
                        b_dt = pd.to_datetime(row.get('Buy Date', ''), format='%d-%m-%Y', errors='coerce')
                        s_dt = pd.to_datetime(row.get('Sell Date', ''), format='%d-%m-%Y', errors='coerce')
                        if pd.notna(b_dt) and pd.notna(s_dt):
                            return max(0, (s_dt - b_dt).days)
                    except:
                        pass
                    return 0

                realized_trades_df['Holding Days'] = realized_trades_df.apply(calc_holding_days, axis=1)

                # Duration Bucket
                def duration_bucket(days):
                    if days == 0: return '0d (Intraday)'
                    elif days <= 7: return '1-7d (Quick Swing)'
                    elif days <= 30: return '8-30d (Positional)'
                    else: return '>30d (Long Term)'
                
                realized_trades_df['Duration Bucket'] = realized_trades_df['Holding Days'].apply(duration_bucket)

                # Brokerage Allocation per trade
                total_charges_val = 0.0
                if not charges_df.empty and 'Amount' in charges_df.columns:
                    total_charges_val = charges_df[~charges_df['Charge Item'].str.lower().isin(['total'])]['Amount'].sum()
                
                tot_turnover = realized_trades_df['Turnover'].sum()
                if tot_turnover > 0:
                    realized_trades_df['Est Charges (₹)'] = (realized_trades_df['Turnover'] / tot_turnover) * total_charges_val
                else:
                    realized_trades_df['Est Charges (₹)'] = 0.0

                realized_trades_df['Net P&L (₹)'] = realized_trades_df['Realised P&L'] - realized_trades_df['Est Charges (₹)']

    # 2. Parse Scrip Level sheet
    scrip_sheet_name = next((s for s in xls.sheet_names if 'scrip' in s.lower()), None)
    if scrip_sheet_name:
        df_scrip = pd.read_excel(xls, sheet_name=scrip_sheet_name, header=None)
        sr_header = scan_table_header(df_scrip, ['stock', 'isin', 'realised', 'avg buy'])

        if sr_header is not None:
            sr_rows = []
            cols = [str(c).strip() for c in df_scrip.iloc[sr_header]]
            for i in range(sr_header + 1, len(df_scrip)):
                v0 = str(df_scrip.iloc[i, 0]).strip()
                if not v0 or v0.lower() == 'nan' or 'total' in v0.lower() or 'unrealised' in v0.lower():
                    break
                sr_rows.append(df_scrip.iloc[i].values[:len(cols)])

            if sr_rows:
                scrip_realized_df = pd.DataFrame(sr_rows, columns=cols)
                c_map = {}
                for c in scrip_realized_df.columns:
                    cl = str(c).lower()
                    if any(k in cl for k in ['stock name', 'company', 'scrip name', 'security']) or cl == 'stock':
                        c_map[c] = 'Stock Name'
                    elif 'isin' in cl: c_map[c] = 'ISIN'
                    elif any(k in cl for k in ['quantity', 'qty']): c_map[c] = 'Quantity'
                    elif 'avg buy' in cl: c_map[c] = 'Avg Buy Price'
                    elif 'buy val' in cl: c_map[c] = 'Buy Value'
                    elif 'avg sell' in cl: c_map[c] = 'Avg Sell Price'
                    elif 'sell val' in cl: c_map[c] = 'Sell Value'
                    elif 'p&l %' in cl or 'pnl %' in cl: c_map[c] = 'Realised P&L %'
                    elif 'p&l' in cl or 'pnl' in cl: c_map[c] = 'Realised P&L'
                scrip_realized_df = scrip_realized_df.rename(columns=c_map)

                for num_col in ['Quantity', 'Avg Buy Price', 'Buy Value', 'Avg Sell Price', 'Sell Value', 'Realised P&L', 'Realised P&L %']:
                    if num_col in scrip_realized_df.columns:
                        scrip_realized_df[num_col] = scrip_realized_df[num_col].apply(clean_numeric_value)

    return meta, charges_df, realized_trades_df, scrip_realized_df


def format_inr(val, decimals=2):
    """Formats numeric values into Indian Rupee style with ₹ symbol."""
    if pd.isna(val) or val is None:
        return "₹0.00"
    is_neg = val < 0
    abs_val = abs(val)
    if decimals == 0:
        s = f"{abs_val:,.0f}"
    else:
        s = f"{abs_val:,.{decimals}f}"
    formatted = f"₹{s}"
    return f"-{formatted}" if is_neg else formatted


def compute_daily_pnl(trades_df, total_charges):
    """
    Computes day-to-day Realized P&L, daily trade counts, intraday vs delivery split,
    proportional charges, net daily returns, and cumulative P&L equity curve.
    """
    if trades_df.empty or 'Sell Date' not in trades_df.columns:
        return pd.DataFrame()

    df = trades_df.copy()
    df['Sell Date DT'] = pd.to_datetime(df['Sell Date'], format='%d-%m-%Y', errors='coerce')
    df = df.dropna(subset=['Sell Date DT'])

    tot_turnover = df['Turnover'].sum()

    daily = df.groupby('Sell Date DT').agg(
        Sell_Date=('Sell Date', 'first'),
        Total_Trades=('Realised P&L', 'count'),
        Intraday_Trades=('Is Intraday', lambda x: x.sum()),
        Delivery_Trades=('Is Intraday', lambda x: (~x).sum()),
        Gross_PnL=('Realised P&L', 'sum'),
        Turnover=('Turnover', 'sum'),
        Wins=('Realised P&L', lambda x: (x > 0).sum()),
        Losses=('Realised P&L', lambda x: (x < 0).sum())
    ).reset_index().sort_values(by='Sell Date DT')

    daily['Day of Week'] = daily['Sell Date DT'].dt.strftime('%A')
    daily['Win Rate %'] = np.where(daily['Total_Trades'] > 0, (daily['Wins'] / daily['Total_Trades']) * 100, 0.0)
    
    if tot_turnover > 0:
        daily['Est_Charges'] = (daily['Turnover'] / tot_turnover) * total_charges
    else:
        daily['Est_Charges'] = 0.0

    daily['Net_PnL'] = daily['Gross_PnL'] - daily['Est_Charges']
    daily['Cumulative_Gross_PnL'] = daily['Gross_PnL'].cumsum()
    daily['Cumulative_Net_PnL'] = daily['Net_PnL'].cumsum()

    return daily


def evaluate_portfolio_risks(holdings_df, max_target_weight=10.0):
    """
    Evaluates concentration risk, capital impairment, group exposure,
    and assigns actionable buckets with dynamic target weight allocation.
    """
    if holdings_df.empty:
        return pd.DataFrame(), []

    total_val = holdings_df['Current Value'].sum()
    alerts = []

    group_totals = holdings_df.groupby('Corporate Group')['Current Value'].sum()
    group_weights = (group_totals / total_val) * 100 if total_val > 0 else group_totals * 0

    for grp, wt in group_weights.items():
        if grp != "Independent / Others" and wt > 30.0:
            alerts.append({
                'level': 'danger',
                'title': f'Excessive Corporate Group Exposure: {grp} ({wt:.1f}%)',
                'desc': f'Your portfolio holds {wt:.1f}% exposure to {grp} companies. This exceeds the recommended 30% single-group ceiling and amplifies governance and sector-specific drawdowns.'
            })

    rebal_rows = []
    for _, row in holdings_df.iterrows():
        stock = row['Stock Name']
        weight = row['Weight %']
        pnl_pct = row['Unrealised P&L %']
        curr_val = row['Current Value']
        unrealised_pnl = row['Unrealised P&L']
        grp = row['Corporate Group']

        flags = []
        if weight > 15.0:
            flags.append("High Concentration (>15%)")
            if weight > 25.0:
                alerts.append({
                    'level': 'warning',
                    'title': f'Single-Stock Over-Weight: {stock} ({weight:.1f}%)',
                    'desc': f'{stock} constitutes {weight:.1f}% of your portfolio (₹{curr_val:,.2f}). Any sharp pullback will disproportionately hit your entire NAV.'
                })

        if pnl_pct < -20.0:
            flags.append("Capital Impairment (Loss >20%)")
            if pnl_pct < -40.0:
                alerts.append({
                    'level': 'danger',
                    'title': f'Severe Capital Erosion: {stock} ({pnl_pct:.1f}%)',
                    'desc': f'{stock} is down {abs(pnl_pct):.1f}% with unrealized loss of ₹{abs(unrealised_pnl):,.2f}. Reassess underlying business fundamentals.'
                })

        action = "HOLD"
        badge_class = "badge-hold"
        rationale = ""
        suggested_trim_val = 0.0

        if weight > max_target_weight:
            action = "REDUCE"
            badge_class = "badge-reduce"
            target_val = total_val * (max_target_weight / 100.0)
            suggested_trim_val = max(0.0, curr_val - target_val)
            rationale = f"Trim {weight:.1f}% weight down to {max_target_weight:.0f}% target. Reallocate ₹{suggested_trim_val:,.2f} to diversify risk."
        elif pnl_pct < -25.0 and weight < 5.0:
            action = "EXIT"
            badge_class = "badge-exit"
            suggested_trim_val = curr_val
            rationale = f"Deep drawdown ({pnl_pct:.1f}%) on minor position. Liquidate ₹{curr_val:,.2f} to harvest tax loss & stop bleeding."
        elif pnl_pct < -20.0 and weight >= 5.0:
            action = "REDUCE"
            badge_class = "badge-reduce"
            target_val = total_val * 0.05
            suggested_trim_val = max(0.0, curr_val - target_val)
            rationale = f"Loss >20% ({pnl_pct:.1f}%). De-risk position by ₹{suggested_trim_val:,.2f} to contain portfolio drawdown."
        elif pnl_pct >= -10.0 and pnl_pct <= 5.0 and weight < 12.0:
            if "ETF" in row['Sector / Asset Class'] or "GOLD" in stock or "SILV" in stock:
                action = "CORE BUY"
                badge_class = "badge-buy"
                rationale = "Strategic commodity / hedging asset. Safe compounder for long-term portfolio stability."
            else:
                action = "ACCUMULATE ON DIP"
                badge_class = "badge-accumulate"
                rationale = f"Position is in a healthy range ({weight:.1f}% weight, {pnl_pct:+.1f}% P&L). Suitable for gradual accumulation."
        elif pnl_pct > 5.0 and weight <= 15.0:
            action = "HOLD"
            badge_class = "badge-hold"
            rationale = f"Profitable position (+{pnl_pct:.1f}%) with healthy weight. Let winners run with a trailing stop loss."
        else:
            action = "HOLD"
            badge_class = "badge-hold"
            rationale = "Allocation is balanced. Maintain current stance and monitor earnings."

        rebal_rows.append({
            'Stock Name': stock,
            'Group': grp,
            'Current Value': curr_val,
            'Weight %': weight,
            'Unrealised P&L %': pnl_pct,
            'Action': action,
            'Badge Class': badge_class,
            'Risk Flags': ", ".join(flags) if flags else "Normal",
            'Suggested Trim / Rebalance (₹)': suggested_trim_val,
            'Rationale': rationale
        })

    return pd.DataFrame(rebal_rows), alerts


# ==============================================================================
# SIDEBAR & DATA INGESTION
# ==============================================================================

DEFAULT_HOLDINGS_FILE = "Stocks_Holdings_Statement_6124873955_15-08-2026.xlsx"
DEFAULT_PNL_FILE = "Stocks_PnL_6124873955_01-01-2026_15-08-2026_report.xlsx"

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135679.png", width=56)
    st.title("Equity Terminal")
    st.caption("Universal Indian Portfolio & P&L Intelligence Engine")
    st.markdown("<hr style='margin: 12px 0; border-color: rgba(255,255,255,0.08);'>", unsafe_allow_html=True)

    st.subheader("📂 Upload Broker Statements")
    holdings_upload = st.file_uploader(
        "1. Holdings Statement Excel",
        type=["xlsx", "xls"],
        help="Upload standard broker Holdings Statement (Groww, Zerodha, Upstox, AngelOne, etc.)"
    )
    pnl_upload = st.file_uploader(
        "2. P&L Statement Excel",
        type=["xlsx", "xls"],
        help="Upload P&L Statement with 'Trade Level' and 'Scrip Level' sheets"
    )

    use_sample_data = False
    if holdings_upload is None and pnl_upload is None:
        if os.path.exists(DEFAULT_HOLDINGS_FILE) and os.path.exists(DEFAULT_PNL_FILE):
            use_sample_data = True
            st.info("💡 Preloaded sample statements from workspace. Upload your own files above anytime!")

    st.markdown("<hr style='margin: 12px 0; border-color: rgba(255,255,255,0.08);'>", unsafe_allow_html=True)
    st.markdown("### ⚙️ Terminal Settings")
    show_zero_trades = st.checkbox("Show Break-even Trades", value=True)
    max_pos_target = st.slider("Target Max Single-Stock Weight (%)", min_value=5.0, max_value=25.0, value=10.0, step=1.0)
    tax_slab_rate = st.selectbox("Your Income Tax Slab (for Intraday)", options=["30% (Highest Slab)", "20% (Mid Slab)", "10% (Low Slab)", "0% (Nil)"], index=0)
    
    st.markdown("<hr style='margin: 12px 0; border-color: rgba(255,255,255,0.08);'>", unsafe_allow_html=True)
    st.caption("🔒 **Security**: All computations run locally in-memory. Zero financial data is sent to external servers.")


# --- Ingestion Execution ---

holdings_df = pd.DataFrame()
holdings_meta = {}
pnl_meta = {}
charges_df = pd.DataFrame()
realized_trades_df = pd.DataFrame()
scrip_realized_df = pd.DataFrame()

if holdings_upload is not None:
    holdings_df, holdings_meta = parse_holdings_sheet_universal(holdings_upload)
elif use_sample_data and os.path.exists(DEFAULT_HOLDINGS_FILE):
    holdings_df, holdings_meta = parse_holdings_sheet_universal(DEFAULT_HOLDINGS_FILE)

if pnl_upload is not None:
    pnl_meta, charges_df, realized_trades_df, scrip_realized_df = parse_pnl_sheet_universal(pnl_upload)
elif use_sample_data and os.path.exists(DEFAULT_PNL_FILE):
    pnl_meta, charges_df, realized_trades_df, scrip_realized_df = parse_pnl_sheet_universal(DEFAULT_PNL_FILE)

client_name = holdings_meta.get('client_name') or pnl_meta.get('client_name') or "Investor"
client_code = holdings_meta.get('client_code') or pnl_meta.get('client_code') or "N/A"
statement_date = holdings_meta.get('statement_date') or pnl_meta.get('pnl_statement_info') or "August 2026"

if holdings_df.empty and scrip_realized_df.empty:
    st.warning("⚠️ Please upload your Holdings Statement and P&L Statement Excel files via the sidebar to begin analysis.")
    st.stop()


# --- KPI Summary Calculations ---

total_invested = holdings_df['Buy Value'].sum() if not holdings_df.empty else 0.0
total_current_val = holdings_df['Current Value'].sum() if not holdings_df.empty else 0.0
total_unrealised_pnl = holdings_df['Unrealised P&L'].sum() if not holdings_df.empty else 0.0
unrealised_pnl_pct = (total_unrealised_pnl / total_invested * 100) if total_invested > 0 else 0.0

gross_realised_pnl = 0.0
if not scrip_realized_df.empty and 'Realised P&L' in scrip_realized_df.columns:
    gross_realised_pnl = scrip_realized_df['Realised P&L'].sum()
elif not realized_trades_df.empty and 'Realised P&L' in realized_trades_df.columns:
    gross_realised_pnl = realized_trades_df['Realised P&L'].sum()

total_charges = 0.0
if not charges_df.empty and 'Amount' in charges_df.columns:
    c_sub = charges_df[~charges_df['Charge Item'].str.lower().isin(['total'])]
    total_charges = c_sub['Amount'].sum()

net_realised_pnl = gross_realised_pnl - total_charges
friction_ratio = (total_charges / gross_realised_pnl * 100) if gross_realised_pnl > 0 else 0.0
total_net_portfolio_return = net_realised_pnl + total_unrealised_pnl

daily_pnl_df = compute_daily_pnl(realized_trades_df, total_charges)


# --- Build Unified Lifecycle Scrip P&L Matrix ---
all_scrips_set = sorted(list(set(
    (holdings_df['Stock Name'].tolist() if not holdings_df.empty else []) + 
    (scrip_realized_df['Stock Name'].tolist() if not scrip_realized_df.empty else [])
)))
lifecycle_rows = []
for scrip in all_scrips_set:
    h_sub = holdings_df[holdings_df['Stock Name'] == scrip] if not holdings_df.empty else pd.DataFrame()
    s_sub = scrip_realized_df[scrip_realized_df['Stock Name'] == scrip] if not scrip_realized_df.empty else pd.DataFrame()
    t_sub = realized_trades_df[realized_trades_df['Stock Name'] == scrip] if not realized_trades_df.empty else pd.DataFrame()
    
    unreal_pnl = h_sub['Unrealised P&L'].values[0] if not h_sub.empty else 0.0
    curr_val = h_sub['Current Value'].values[0] if not h_sub.empty else 0.0
    buy_val = h_sub['Buy Value'].values[0] if not h_sub.empty else 0.0
    is_holding = not h_sub.empty
    
    real_pnl = s_sub['Realised P&L'].values[0] if not s_sub.empty else 0.0
    trades_cnt = len(t_sub)
    
    tot_pnl = unreal_pnl + real_pnl
    lifecycle_rows.append({
        'Stock Name': scrip,
        'Active Holding': 'Active Holding' if is_holding else 'Position Closed',
        'Current Holding Value': curr_val,
        'Realised P&L': real_pnl,
        'Unrealised P&L': unreal_pnl,
        'Total Lifecycle Gain': tot_pnl,
        'Closed Trades Count': trades_cnt
    })
lifecycle_df = pd.DataFrame(lifecycle_rows).sort_values(by='Total Lifecycle Gain', ascending=False) if lifecycle_rows else pd.DataFrame()


# ==============================================================================
# HEADER SECTION
# ==============================================================================

col_title1, col_title2 = st.columns([3, 1])
with col_title1:
    st.title("🇮🇳 Indian Equity Portfolio Terminal")
    st.markdown(f"**Account**: `{client_name}` | **UCC**: `{client_code}` | **Statement**: `{statement_date}`")
with col_title2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="text-align: right; background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.35); border-radius: 10px; padding: 10px 16px;">
            <span style="color: #94a3b8; font-size: 0.78rem; font-weight: 600; text-transform: uppercase;">COMBINED NET GAIN</span><br>
            <span style="font-family: 'JetBrains Mono'; font-size: 1.35rem; font-weight: 700; color: {'#10b981' if total_net_portfolio_return >= 0 else '#f43f5e'};">
                {format_inr(total_net_portfolio_return)}
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<div style='margin-bottom: 22px;'></div>", unsafe_allow_html=True)


# ==============================================================================
# TOP-LEVEL KPI METRIC CARDS (MACRO LEVEL 0)
# ==============================================================================

kpi_c1, kpi_c2, kpi_c3, kpi_c4, kpi_c5, kpi_c6 = st.columns(6)

with kpi_c1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Invested Capital</div>
            <div class="metric-value">{format_inr(total_invested)}</div>
            <div class="metric-sub val-neutral">Cost Basis</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with kpi_c2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Current Value</div>
            <div class="metric-value">{format_inr(total_current_val)}</div>
            <div class="metric-sub {'val-positive' if total_current_val >= total_invested else 'val-negative'}">
                {len(holdings_df)} Active Scrips
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with kpi_c3:
    unreal_cls = "val-positive" if total_unrealised_pnl >= 0 else "val-negative"
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Unrealised P&L</div>
            <div class="metric-value {unreal_cls}">{format_inr(total_unrealised_pnl)}</div>
            <div class="metric-sub {unreal_cls}">{unrealised_pnl_pct:+.2f}% ROI</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with kpi_c4:
    real_cls = "val-positive" if gross_realised_pnl >= 0 else "val-negative"
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Gross Realised P&L</div>
            <div class="metric-value {real_cls}">{format_inr(gross_realised_pnl)}</div>
            <div class="metric-sub val-neutral">{len(realized_trades_df)} Closed Trades</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with kpi_c5:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Charges & Taxes</div>
            <div class="metric-value val-negative">{format_inr(total_charges)}</div>
            <div class="metric-sub val-neutral">Friction: {friction_ratio:.1f}%</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with kpi_c6:
    net_real_cls = "val-positive" if net_realised_pnl >= 0 else "val-negative"
    st.markdown(
        f"""
        <div class="metric-card" style="border-color: rgba(16, 185, 129, 0.45);">
            <div class="metric-label">Net Realised Profit</div>
            <div class="metric-value {net_real_cls}">{format_inr(net_realised_pnl)}</div>
            <div class="metric-sub {net_real_cls}">Post Brokerage & Tax</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<div style='margin-bottom: 26px;'></div>", unsafe_allow_html=True)


# ==============================================================================
# PROGRESSIVE DISCLOSURE TABS
# ==============================================================================

tab_portfolio, tab_realised, tab_charges, tab_risk, tab_export = st.tabs([
    "📊 Current Portfolio Deep Analysis",
    "💰 Realised P&L, Strategy & Journal",
    "🧾 Charges, Tax & In-Hand Profit",
    "🛡️ Portfolio Risk & Rebalancing Engine",
    "📄 Master Multi-Sheet Excel & CSV Export"
])


# ==============================================================================
# TAB 1: CURRENT PORTFOLIO DEEP ANALYSIS (MACRO -> INTERMEDIATE -> MICRO)
# ==============================================================================
with tab_portfolio:
    if holdings_df.empty:
        st.info("No active holdings found in statement.")
    else:
        # LEVEL 1: MACRO PORTFOLIO HEALTH & ALLOCATION
        st.markdown("<span class='flow-badge'>LEVEL 1: MACRO ALLOCATION & HEALTH</span>", unsafe_allow_html=True)
        st.markdown("### Portfolio Breadth & Macro Exposure")

        h_gainers = holdings_df[holdings_df['Unrealised P&L'] > 0].sort_values(by='Unrealised P&L', ascending=False)
        h_losers = holdings_df[holdings_df['Unrealised P&L'] < 0].sort_values(by='Unrealised P&L', ascending=True)

        col_g1, col_g2, col_g3 = st.columns(3)
        with col_g1:
            st.markdown(
                f"""
                <div class="glass-card" style="padding: 14px 18px; margin-bottom: 16px;">
                    <div style="color: #94a3b8; font-size: 0.78rem; font-weight: 600; text-transform: uppercase;">Top Winning Scrip</div>
                    <div style="font-weight: 700; font-size: 1.1rem; color: #f1f5f9; margin-top: 4px;">
                        {h_gainers.iloc[0]['Stock Name'] if not h_gainers.empty else 'None'}
                    </div>
                    <div style="color: #10b981; font-weight: 700; font-family: 'JetBrains Mono'; font-size: 0.95rem;">
                        {format_inr(h_gainers.iloc[0]['Unrealised P&L']) if not h_gainers.empty else '₹0.00'}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col_g2:
            st.markdown(
                f"""
                <div class="glass-card" style="padding: 14px 18px; margin-bottom: 16px;">
                    <div style="color: #94a3b8; font-size: 0.78rem; font-weight: 600; text-transform: uppercase;">Max Drawdown Scrip</div>
                    <div style="font-weight: 700; font-size: 1.1rem; color: #f1f5f9; margin-top: 4px;">
                        {h_losers.iloc[0]['Stock Name'] if not h_losers.empty else 'None'}
                    </div>
                    <div style="color: #f43f5e; font-weight: 700; font-family: 'JetBrains Mono'; font-size: 0.95rem;">
                        {format_inr(h_losers.iloc[0]['Unrealised P&L']) if not h_losers.empty else '₹0.00'}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col_g3:
            st.markdown(
                f"""
                <div class="glass-card" style="padding: 14px 18px; margin-bottom: 16px;">
                    <div style="color: #94a3b8; font-size: 0.78rem; font-weight: 600; text-transform: uppercase;">Portfolio Breadth</div>
                    <div style="font-weight: 700; font-size: 1.1rem; color: #f1f5f9; margin-top: 4px;">
                        {len(h_gainers)} Green / {len(h_losers)} Red
                    </div>
                    <div style="color: #3b82f6; font-weight: 600; font-size: 0.95rem;">
                        {(len(h_gainers)/len(holdings_df)*100):.1f}% Advancing
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        col_pie, col_group = st.columns([1, 1])
        with col_pie:
            st.markdown("#### 🎯 Asset Allocation by Scrip Value")
            fig_pie = px.pie(
                holdings_df,
                values='Current Value',
                names='Stock Name',
                hole=0.55,
                color_discrete_sequence=px.colors.qualitative.Prism,
                custom_data=['Weight %', 'Unrealised P&L', 'Unrealised P&L %']
            )
            fig_pie.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate="<b>%{label}</b><br>Value: ₹%{value:,.2f}<br>Weight: %{customdata[0]:.2f}%<br>Unrealised P&L: ₹%{customdata[1]:,.2f} (%{customdata[2]:+.2f}%)<extra></extra>"
            )
            fig_pie.update_layout(
                margin=dict(t=20, b=20, l=10, r=10),
                showlegend=False,
                height=370,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_group:
            st.markdown("#### 🏢 Conglomerate & Sector Weightings")
            grp_df = holdings_df.groupby('Corporate Group').agg({
                'Current Value': 'sum',
                'Buy Value': 'sum',
                'Unrealised P&L': 'sum'
            }).reset_index()
            grp_df['Weight %'] = (grp_df['Current Value'] / grp_df['Current Value'].sum()) * 100
            grp_df = grp_df.sort_values(by='Current Value', ascending=True)

            fig_grp = px.bar(
                grp_df,
                x='Current Value',
                y='Corporate Group',
                orientation='h',
                color='Weight %',
                color_continuous_scale='Tealgrn',
                text=grp_df['Weight %'].apply(lambda x: f"{x:.1f}%")
            )
            fig_grp.update_traces(
                textposition='outside',
                hovertemplate="<b>%{y}</b><br>Current Value: ₹%{x:,.2f}<br>Weight: %{text}<extra></extra>"
            )
            fig_grp.update_layout(
                margin=dict(t=20, b=20, l=10, r=30),
                height=370,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(title="Total Value (₹)", gridcolor="#2a2e39"),
                yaxis=dict(title="", gridcolor="#2a2e39"),
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_grp, use_container_width=True)

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

        # LEVEL 2: INTERMEDIATE UNIFIED LIFECYCLE SCRIP MATRIX
        if not lifecycle_df.empty:
            st.markdown("<span class='flow-badge'>LEVEL 2: UNIFIED LIFECYCLE SCRIP MATRIX</span>", unsafe_allow_html=True)
            st.markdown("### Total Scrip Lifetime Performance (Realized + Unrealized Combined)")
            st.caption("Combines past realized gains with current unrealized holdings for every company you have traded.")
            
            st.dataframe(
                lifecycle_df.style.format({
                    'Current Holding Value': '₹{:,.2f}',
                    'Realised P&L': '₹{:,.2f}',
                    'Unrealised P&L': '₹{:,.2f}',
                    'Total Lifecycle Gain': '₹{:,.2f}',
                    'Closed Trades Count': '{:,.0f}'
                }).map(
                    lambda val: 'color: #10b981; font-weight: 600;' if isinstance(val, (int, float)) and val > 0 else ('color: #f43f5e; font-weight: 600;' if isinstance(val, (int, float)) and val < 0 else ''),
                    subset=['Realised P&L', 'Unrealised P&L', 'Total Lifecycle Gain']
                ),
                use_container_width=True,
                height=320
            )

            st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

        # LEVEL 3: MICRO HOLDINGS INSPECTION TABLE
        st.markdown("<span class='flow-badge'>LEVEL 3: GRANULAR HOLDINGS MATRIX</span>", unsafe_allow_html=True)
        st.markdown("### Itemized Holdings Inspection")

        col_f1, col_f2 = st.columns([2, 1])
        with col_f1:
            search_holding = st.text_input("🔍 Search Holdings by Name / ISIN", placeholder="e.g. Vedanta, HDFC, Gold...")
        with col_f2:
            group_filter = st.multiselect("Filter by Corporate Group", options=sorted(holdings_df['Corporate Group'].unique()))

        filtered_holdings = holdings_df.copy()
        if search_holding:
            filtered_holdings = filtered_holdings[
                filtered_holdings['Stock Name'].str.contains(search_holding, case=False, na=False) |
                filtered_holdings['ISIN'].str.contains(search_holding, case=False, na=False)
            ]
        if group_filter:
            filtered_holdings = filtered_holdings[filtered_holdings['Corporate Group'].isin(group_filter)]

        display_holdings = filtered_holdings[[
            'Stock Name', 'ISIN', 'Corporate Group', 'Quantity', 'Avg Buy Price',
            'Current Price', 'Buy Value', 'Current Value', 'Unrealised P&L', 'Unrealised P&L %', 'Weight %'
        ]].copy()

        st.dataframe(
            display_holdings.style.format({
                'Quantity': '{:,.0f}',
                'Avg Buy Price': '₹{:,.2f}',
                'Current Price': '₹{:,.2f}',
                'Buy Value': '₹{:,.2f}',
                'Current Value': '₹{:,.2f}',
                'Unrealised P&L': '₹{:,.2f}',
                'Unrealised P&L %': '{:+.2f}%',
                'Weight %': '{:.2f}%'
            }).map(
                lambda val: 'color: #10b981; font-weight: 600;' if isinstance(val, (int, float)) and val > 0 else ('color: #f43f5e; font-weight: 600;' if isinstance(val, (int, float)) and val < 0 else ''),
                subset=['Unrealised P&L', 'Unrealised P&L %']
            ),
            use_container_width=True,
            height=420
        )

        csv_buffer = io.StringIO()
        display_holdings.to_csv(csv_buffer, index=False)
        st.download_button(
            label="📥 Export Active Holdings Data to CSV",
            data=csv_buffer.getvalue(),
            file_name=f"Portfolio_Holdings_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )


# ==============================================================================
# TAB 2: REALISED P&L, STRATEGY & JOURNAL (PROGRESSIVE MACRO -> TIMELINE -> SCRIP -> MICRO TRADES)
# ==============================================================================
with tab_realised:
    if scrip_realized_df.empty and realized_trades_df.empty:
        st.info("No realized trades data found in statement.")
    else:
        # --- PROGRESSIVE LEVEL 1: STRATEGY SEGMENT CONTROLLER & HIGH-LEVEL KPIS ---
        all_trade_types = ["🌐 All Trade Types"]
        if not realized_trades_df.empty and 'Trade Type' in realized_trades_df.columns:
            available_types = sorted(realized_trades_df['Trade Type'].dropna().unique().tolist())
            type_labels = {
                'Intraday': '⚡ Intraday Only',
                'Delivery / Swing': '📦 Delivery / Swing Only',
                'IPO Allotment': '💎 IPO Allotment Only',
                'Demerger Credit': '🧬 Demerger Credit Only'
            }
            formatted_types = [type_labels.get(t, t) for t in available_types]
            all_trade_types.extend(formatted_types)

        st.markdown(
            """
            <div class="segment-bar">
                <span style="color: #94a3b8; font-size: 0.82rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">
                    🎯 Active Strategy View:
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

        selected_type_view = st.radio(
            "Select Strategy Filter for Analytics",
            options=all_trade_types,
            index=0,
            horizontal=True,
            label_visibility="collapsed"
        )

        active_trades = realized_trades_df.copy() if not realized_trades_df.empty else pd.DataFrame()

        if selected_type_view != "🌐 All Trade Types" and not active_trades.empty:
            if "Intraday" in selected_type_view:
                active_trades = active_trades[active_trades['Trade Type'] == 'Intraday']
            elif "Delivery" in selected_type_view:
                active_trades = active_trades[active_trades['Trade Type'] == 'Delivery / Swing']
            elif "IPO" in selected_type_view:
                active_trades = active_trades[active_trades['Trade Type'] == 'IPO Allotment']
            elif "Demerger" in selected_type_view:
                active_trades = active_trades[active_trades['Trade Type'] == 'Demerger Credit']

        pnl_col = 'Realised P&L'
        total_active_trades = len(active_trades)
        winning_trades = active_trades[active_trades[pnl_col] > 0] if not active_trades.empty else pd.DataFrame()
        losing_trades = active_trades[active_trades[pnl_col] < 0] if not active_trades.empty else pd.DataFrame()

        win_count = len(winning_trades)
        loss_count = len(losing_trades)
        win_rate = (win_count / total_active_trades * 100) if total_active_trades > 0 else 0.0

        total_gains = winning_trades[pnl_col].sum() if not winning_trades.empty else 0.0
        total_losses = abs(losing_trades[pnl_col].sum()) if not losing_trades.empty else 0.0
        profit_factor = (total_gains / total_losses) if total_losses > 0 else (total_gains if total_gains > 0 else 1.0)

        active_gross_pnl = active_trades[pnl_col].sum() if not active_trades.empty else 0.0
        active_charges = active_trades['Est Charges (₹)'].sum() if ('Est Charges (₹)' in active_trades.columns and not active_trades.empty) else 0.0
        active_net_pnl = active_gross_pnl - active_charges
        active_turnover = active_trades['Turnover'].sum() if ('Turnover' in active_trades.columns and not active_trades.empty) else 0.0

        # Advanced Statistical Calculations: Expectancy & Risk/Reward
        avg_win_val = winning_trades[pnl_col].mean() if win_count > 0 else 0.0
        avg_loss_val = abs(losing_trades[pnl_col].mean()) if loss_count > 0 else 0.0
        rr_ratio = (avg_win_val / avg_loss_val) if avg_loss_val > 0 else (avg_win_val if avg_win_val > 0 else 1.0)
        expectancy_val = ((win_rate / 100.0) * avg_win_val) - (((100.0 - win_rate) / 100.0) * avg_loss_val)

        st.markdown("<span class='flow-badge'>LEVEL 1: STRATEGY KPIS & EXPECTANCY</span>", unsafe_allow_html=True)
        st.markdown(f"### Performance Metrics ({selected_type_view})")
        t_col1, t_col2, t_col3, t_col4, t_col5, t_col6 = st.columns(6)
        with t_col1:
            st.metric("Win Rate", f"{win_rate:.1f}%", f"{win_count}W / {loss_count}L")
        with t_col2:
            st.metric("Profit Factor", f"{profit_factor:.2f}x", f"R:R {rr_ratio:.2f}x")
        with t_col3:
            st.metric("Gross P&L", format_inr(active_gross_pnl), f"{total_active_trades} Trades", delta_color="normal" if active_gross_pnl >= 0 else "inverse")
        with t_col4:
            st.metric("Est. Charges & Tax", format_inr(active_charges), f"Turnover: {format_inr(active_turnover, 0)}", delta_color="inverse")
        with t_col5:
            net_delta_color = "normal" if active_net_pnl >= 0 else "inverse"
            st.metric("Net Realised Return", format_inr(active_net_pnl), "Post Friction", delta_color=net_delta_color)
        with t_col6:
            st.metric("Trading Expectancy", format_inr(expectancy_val), "Expected ₹ / Trade", delta_color="normal" if expectancy_val >= 0 else "inverse")

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

        # --- PROGRESSIVE LEVEL 2: DAY-TO-DAY REALIZED P&L TIMELINE & EQUITY CURVE (PLACED AHEAD OF SCRIP LEVEL!) ---
        st.markdown("<span class='flow-badge'>LEVEL 2: TIMELINE & EQUITY CURVE (MACRO)</span>", unsafe_allow_html=True)
        st.markdown(f"### Day-to-Day Realized P&L & Cumulative Equity Curve ({selected_type_view})")

        daily_type_pnl = compute_daily_pnl(active_trades, active_charges)

        if not daily_type_pnl.empty:
            best_day_val = daily_type_pnl['Net_PnL'].max()
            worst_day_val = daily_type_pnl['Net_PnL'].min()
            win_days = (daily_type_pnl['Net_PnL'] > 0).sum()
            loss_days = (daily_type_pnl['Net_PnL'] < 0).sum()
            total_days = len(daily_type_pnl)
            sess_win_rate = (win_days / total_days * 100) if total_days > 0 else 0.0

            d_c1, d_c2, d_c3, d_c4 = st.columns(4)
            with d_c1:
                st.metric("Active Sessions", f"{total_days} Days", f"{win_days} Green / {loss_days} Red")
            with d_c2:
                st.metric("Session Win Rate", f"{sess_win_rate:.1f}%", "Profitable Days")
            with d_c3:
                st.metric("Best Day", format_inr(best_day_val), "Peak Daily Session", delta_color="normal")
            with d_c4:
                st.metric("Worst Day", format_inr(worst_day_val), "Max Daily Drawdown", delta_color="inverse")

            # Daily Bar Chart + Cumulative Net Curve
            fig_daily_dyn = go.Figure()
            bar_colors = daily_type_pnl['Net_PnL'].apply(lambda x: '#10b981' if x >= 0 else '#f43f5e')
            
            fig_daily_dyn.add_trace(go.Bar(
                x=daily_type_pnl['Sell_Date'],
                y=daily_type_pnl['Net_PnL'],
                name='Daily Net P&L (₹)',
                marker=dict(color=bar_colors),
                hovertemplate="<b>%{x} (%{text})</b><br>Net P&L: ₹%{y:,.2f}<extra></extra>",
                text=daily_type_pnl['Day of Week'],
                yaxis='y1'
            ))

            fig_daily_dyn.add_trace(go.Scatter(
                x=daily_type_pnl['Sell_Date'],
                y=daily_type_pnl['Cumulative_Net_PnL'],
                name='Cumulative Equity Curve (₹)',
                mode='lines+markers',
                line=dict(color='#3b82f6', width=3.5),
                marker=dict(size=6, color='#60a5fa'),
                hovertemplate="<b>%{x}</b><br>Cumulative Net: ₹%{y:,.2f}<extra></extra>",
                yaxis='y2'
            ))

            fig_daily_dyn.update_layout(
                margin=dict(t=30, b=20, l=10, r=20),
                height=420,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis=dict(title="Trade Close Date", gridcolor="#2a2e39", type='category'),
                yaxis=dict(title="Daily Net Realised P&L (₹)", gridcolor="#2a2e39", zerolinecolor="#475569"),
                yaxis2=dict(
                    title="Cumulative Equity Curve (₹)",
                    overlaying='y',
                    side='right',
                    gridcolor="rgba(0,0,0,0)",
                    zerolinecolor="#475569"
                )
            )
            st.plotly_chart(fig_daily_dyn, use_container_width=True)

        # Strategy Breakdown Bar/Donut (Shown when All is selected)
        if selected_type_view == "🌐 All Trade Types" and not realized_trades_df.empty:
            strat_summary = realized_trades_df.groupby('Trade Type').agg(
                Trades=('Realised P&L', 'count'),
                Wins=('Realised P&L', lambda x: (x > 0).sum()),
                Losses=('Realised P&L', lambda x: (x < 0).sum()),
                Gross_PnL=('Realised P&L', 'sum'),
                Est_Charges=('Est Charges (₹)', 'sum'),
                Net_PnL=('Net P&L (₹)', 'sum'),
                Turnover=('Turnover', 'sum')
            ).reset_index()

            col_s1, col_s2 = st.columns([1, 1])
            with col_s1:
                st.markdown("#### ⚖️ Strategy Return Comparison")
                fig_strat_bar = go.Figure()
                fig_strat_bar.add_trace(go.Bar(
                    x=strat_summary['Trade Type'],
                    y=strat_summary['Gross_PnL'],
                    name='Gross P&L (₹)',
                    marker_color='#3b82f6',
                    hovertemplate="<b>%{x}</b><br>Gross P&L: ₹%{y:,.2f}<extra></extra>"
                ))
                fig_strat_bar.add_trace(go.Bar(
                    x=strat_summary['Trade Type'],
                    y=strat_summary['Est_Charges'],
                    name='Brokerage & Taxes (₹)',
                    marker_color='#f43f5e',
                    hovertemplate="<b>%{x}</b><br>Charges: ₹%{y:,.2f}<extra></extra>"
                ))
                fig_strat_bar.add_trace(go.Bar(
                    x=strat_summary['Trade Type'],
                    y=strat_summary['Net_PnL'],
                    name='Net P&L (₹)',
                    marker_color='#10b981',
                    hovertemplate="<b>%{x}</b><br>Net P&L: ₹%{y:,.2f}<extra></extra>"
                ))
                fig_strat_bar.update_layout(
                    barmode='group',
                    margin=dict(t=30, b=20, l=10, r=10),
                    height=320,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    xaxis=dict(title="", gridcolor="#2a2e39"),
                    yaxis=dict(title="Amount (₹)", gridcolor="#2a2e39")
                )
                st.plotly_chart(fig_strat_bar, use_container_width=True)

            with col_s2:
                st.markdown("#### 🔄 Volume & Turnover Distribution")
                fig_strat_turn = px.pie(
                    strat_summary,
                    values='Turnover',
                    names='Trade Type',
                    hole=0.5,
                    color='Trade Type',
                    color_discrete_map={
                        'Intraday': '#3b82f6',
                        'Delivery / Swing': '#10b981',
                        'IPO Allotment': '#a78bfa',
                        'Demerger Credit': '#f59e0b'
                    },
                    custom_data=['Trades', 'Net_PnL']
                )
                fig_strat_turn.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    hovertemplate="<b>%{label}</b><br>Turnover: ₹%{value:,.2f}<br>Trades: %{customdata[0]}<br>Net P&L: ₹%{customdata[1]:,.2f}<extra></extra>"
                )
                fig_strat_turn.update_layout(
                    margin=dict(t=30, b=20, l=10, r=10),
                    height=320,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_strat_turn, use_container_width=True)

        # Holding Duration vs Return Breakdown
        if not active_trades.empty and 'Duration Bucket' in active_trades.columns:
            dur_df = active_trades.groupby('Duration Bucket').agg(
                Trades=('Realised P&L', 'count'),
                Net_PnL=('Net P&L (₹)', 'sum'),
                Win_Rate=('Realised P&L', lambda x: (x > 0).sum() / len(x) * 100)
            ).reset_index()

            st.markdown("#### ⏱️ Holding Duration vs Profitability")
            fig_dur = px.bar(
                dur_df,
                x='Duration Bucket',
                y='Net_PnL',
                color='Net_PnL',
                color_continuous_scale=['#f43f5e', '#3b82f6', '#10b981'],
                text=dur_df.apply(lambda r: f"₹{r['Net_PnL']:,.0f} ({r['Win_Rate']:.0f}% W)", axis=1)
            )
            fig_dur.update_traces(textposition='outside')
            fig_dur.update_layout(
                margin=dict(t=20, b=20, l=10, r=10),
                height=280,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(title="Holding Duration", gridcolor="#2a2e39"),
                yaxis=dict(title="Net Realised P&L (₹)", gridcolor="#2a2e39"),
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_dur, use_container_width=True)

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

        # --- PROGRESSIVE LEVEL 3: SCRIP-LEVEL WATERFALL / BAR (INTERMEDIATE SPECIFICITY) ---
        st.markdown("<span class='flow-badge'>LEVEL 3: SCRIP-LEVEL ATTRIBUTION</span>", unsafe_allow_html=True)
        st.markdown(f"### Scrip-Level Realised P&L Waterfall ({selected_type_view})")

        if not active_trades.empty:
            scrip_type_df = active_trades.groupby('Stock Name').agg(
                Gross_PnL=('Realised P&L', 'sum'),
                Est_Charges=('Est Charges (₹)', 'sum'),
                Net_PnL=('Net P&L (₹)', 'sum'),
                Trades=('Realised P&L', 'count')
            ).reset_index().sort_values(by='Net_PnL', ascending=True)

            scrip_type_df['Color'] = scrip_type_df['Net_PnL'].apply(lambda x: '#10b981' if x >= 0 else '#f43f5e')

            fig_scrip_dyn = go.Figure()
            fig_scrip_dyn.add_trace(go.Bar(
                x=scrip_type_df['Net_PnL'],
                y=scrip_type_df['Stock Name'],
                orientation='h',
                marker=dict(color=scrip_type_df['Color']),
                customdata=scrip_type_df[['Gross_PnL', 'Est_Charges', 'Trades']],
                hovertemplate="<b>%{y}</b><br>Net P&L: ₹%{x:,.2f}<br>Gross P&L: ₹%{customdata[0]:,.2f}<br>Est. Charges: ₹%{customdata[1]:,.2f}<br>Trades: %{customdata[2]}<extra></extra>"
            ))
            fig_scrip_dyn.update_layout(
                margin=dict(t=20, b=20, l=10, r=20),
                height=max(360, len(scrip_type_df) * 24),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(title="Net Realised P&L after Charges (₹)", gridcolor="#2a2e39", zerolinecolor="#475569"),
                yaxis=dict(title="", gridcolor="#2a2e39")
            )
            st.plotly_chart(fig_scrip_dyn, use_container_width=True)

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

        # --- PROGRESSIVE LEVEL 4: MICRO EXECUTED TRADES LOG TABLE (MOST SPECIFIC) ---
        st.markdown("<span class='flow-badge'>LEVEL 4: GRANULAR EXECUTED TRADES LOG</span>", unsafe_allow_html=True)
        st.markdown(f"### Itemized Trade Execution Records ({selected_type_view})")

        col_tr1, col_tr2 = st.columns([2, 1])
        with col_tr1:
            search_trade = st.text_input("🔍 Filter Trades by Stock Name / ISIN", placeholder="e.g. Cupid, Kalyan, Saksoft...")
        with col_tr2:
            pnl_outcome = st.selectbox("Filter by Trade Outcome", options=["All Trades", "Winning Trades Only", "Losing Trades Only"])

        filtered_table_trades = active_trades.copy()
        if search_trade:
            filtered_table_trades = filtered_table_trades[
                filtered_table_trades['Stock Name'].str.contains(search_trade, case=False, na=False) |
                filtered_table_trades['ISIN'].str.contains(search_trade, case=False, na=False)
            ]
        if pnl_outcome == "Winning Trades Only":
            filtered_table_trades = filtered_table_trades[filtered_table_trades['Realised P&L'] > 0]
        elif pnl_outcome == "Losing Trades Only":
            filtered_table_trades = filtered_table_trades[filtered_table_trades['Realised P&L'] < 0]
        if not show_zero_trades:
            filtered_table_trades = filtered_table_trades[filtered_table_trades['Realised P&L'] != 0]

        display_trades = filtered_table_trades[[
            'Stock Name', 'Trade Type', 'Holding Days', 'Quantity',
            'Buy Date', 'Buy Price', 'Sell Date', 'Sell Price',
            'Buy Value', 'Sell Value', 'Realised P&L', 'Est Charges (₹)', 'Net P&L (₹)', 'Return %', 'Remark'
        ]].copy()

        trade_format_dict = {
            'Quantity': '{:,.0f}',
            'Holding Days': '{:,.0f}d',
            'Buy Price': '₹{:,.2f}',
            'Buy Value': '₹{:,.2f}',
            'Sell Price': '₹{:,.2f}',
            'Sell Value': '₹{:,.2f}',
            'Realised P&L': '₹{:,.2f}',
            'Est Charges (₹)': '₹{:,.2f}',
            'Net P&L (₹)': '₹{:,.2f}',
            'Return %': '{:+.2f}%'
        }

        st.dataframe(
            display_trades.style.format(trade_format_dict).map(
                lambda val: 'color: #10b981; font-weight: 600;' if isinstance(val, (int, float)) and val > 0 else ('color: #f43f5e; font-weight: 600;' if isinstance(val, (int, float)) and val < 0 else ''),
                subset=['Realised P&L', 'Net P&L (₹)', 'Return %']
            ),
            use_container_width=True,
            height=420
        )

        csv_trades_buffer = io.StringIO()
        display_trades.to_csv(csv_trades_buffer, index=False)
        st.download_button(
            label=f"📥 Export {selected_type_view} Trade Log to CSV",
            data=csv_trades_buffer.getvalue(),
            file_name=f"Trade_Log_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )


# ==============================================================================
# TAB 3: CHARGES, TAX & IN-HAND NET PROFIT (MACRO -> TAX ESTIMATOR -> MICRO)
# ==============================================================================
with tab_charges:
    if charges_df.empty:
        st.info("No charges breakdown data found in statement.")
    else:
        charges_items = charges_df[~charges_df['Charge Item'].str.lower().isin(['total'])].copy()
        charges_items = charges_items[charges_items['Amount'] > 0]
        charges_items['Share %'] = (charges_items['Amount'] / charges_items['Amount'].sum()) * 100

        # LEVEL 1: MACRO FRICTION & STATUTORY SPLIT
        st.markdown("<span class='flow-badge'>LEVEL 1: MACRO FRICTION & STATUTORY SPLIT</span>", unsafe_allow_html=True)
        st.markdown("### Fee Efficiency & Capital Drag")

        col_ch1, col_ch2 = st.columns([1, 1])
        with col_ch1:
            st.markdown(
                f"""
                <div style="background: #181d29; border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 22px; margin-bottom: 18px;">
                    <div style="color: #94a3b8; font-size: 0.82rem; font-weight: 600; text-transform: uppercase;">Brokerage & Tax Friction Ratio</div>
                    <div style="font-family: 'JetBrains Mono'; font-size: 2.1rem; font-weight: 700; color: {'#10b981' if friction_ratio < 15 else ('#f59e0b' if friction_ratio < 25 else '#f43f5e')}; margin-top: 4px;">
                        {friction_ratio:.2f}%
                    </div>
                    <div style="color: #cbd5e1; font-size: 0.92rem; margin-top: 8px; line-height: 1.5;">
                        You paid <b>{format_inr(total_charges)}</b> in statutory taxes and broker fees on gross realized returns of <b>{format_inr(gross_realised_pnl)}</b>.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            statutory_items = ['stt', 'stamp duty', 'sebi charges', 'ipft charges', 'total gst', 'exchange transaction charges']
            statutory_sum = charges_items[charges_items['Charge Item'].str.lower().isin(statutory_items)]['Amount'].sum()
            broker_sum = charges_items[~charges_items['Charge Item'].str.lower().isin(statutory_items)]['Amount'].sum()

            col_sub1, col_sub2 = st.columns(2)
            with col_sub1:
                st.metric("Govt & Statutory Taxes", format_inr(statutory_sum), f"{(statutory_sum/total_charges*100):.1f}% of fees")
            with col_sub2:
                st.metric("Broker & DP Fees", format_inr(broker_sum), f"{(broker_sum/total_charges*100):.1f}% of fees")

        with col_ch2:
            st.markdown("#### 🥧 Fee Category Distribution")
            fig_charges = px.pie(
                charges_items,
                values='Amount',
                names='Charge Item',
                hole=0.5,
                color_discrete_sequence=px.colors.sequential.Plasma_r,
                custom_data=['Share %']
            )
            fig_charges.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate="<b>%{label}</b><br>Amount: ₹%{value:,.2f}<br>Share of Fees: %{customdata[0]:.1f}%<extra></extra>"
            )
            fig_charges.update_layout(
                margin=dict(t=20, b=20, l=10, r=10),
                height=320,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_charges, use_container_width=True)

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

        # LEVEL 2: INDIAN INCOME TAX & IN-HAND PROFIT ESTIMATOR (UNION BUDGET RULES)
        st.markdown("<span class='flow-badge'>LEVEL 2: INDIAN TAX LIABILITY & IN-HAND PROFIT</span>", unsafe_allow_html=True)
        st.markdown("### Estimated Income Tax Liability & In-Hand Profit")
        st.caption("Applies current Indian Union Budget capital gains tax rules: STCG on equity @ 20%, LTCG @ 12.5%, Intraday Speculative Income at your income slab.")

        # Tax calculations
        slab_pct = 0.30 if "30%" in tax_slab_rate else (0.20 if "20%" in tax_slab_rate else (0.10 if "10%" in tax_slab_rate else 0.0))
        
        intra_trades_list = realized_trades_df[realized_trades_df['Trade Type'] == 'Intraday'] if not realized_trades_df.empty else pd.DataFrame()
        deliv_trades_list = realized_trades_df[realized_trades_df['Trade Type'] != 'Intraday'] if not realized_trades_df.empty else pd.DataFrame()

        intra_gross_taxable = intra_trades_list['Realised P&L'].sum() if not intra_trades_list.empty else 0.0
        deliv_stcg_taxable = deliv_trades_list['Realised P&L'].sum() if not deliv_trades_list.empty else 0.0

        est_intra_tax = max(0.0, intra_gross_taxable * slab_pct)
        est_stcg_tax = max(0.0, deliv_stcg_taxable * 0.20) # Budget 2024 STCG 20%
        total_est_tax = est_intra_tax + est_stcg_tax
        true_in_hand_profit = net_realised_pnl - total_est_tax

        tax_c1, tax_c2, tax_c3, tax_c4 = st.columns(4)
        with tax_c1:
            st.metric("STCG Tax Liability (@20%)", format_inr(est_stcg_tax), f"On {format_inr(deliv_stcg_taxable)} Delivery/IPO Gains")
        with tax_c2:
            st.metric(f"Intraday Slab Tax (@{int(slab_pct*100)}%)", format_inr(est_intra_tax), f"On {format_inr(intra_gross_taxable)} Speculative Gain")
        with tax_c3:
            st.metric("Total Estimated Income Tax", format_inr(total_est_tax), "Payable in ITR", delta_color="inverse")
        with tax_c4:
            in_hand_delta = "normal" if true_in_hand_profit >= 0 else "inverse"
            st.metric("True In-Hand Net Profit", format_inr(true_in_hand_profit), "Post-Tax & Post-Brokerage", delta_color=in_hand_delta)

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

        # LEVEL 3: MICRO ITEMIZED CHARGES
        st.markdown("<span class='flow-badge'>LEVEL 3: ITEMIZED CHARGE PARTICULARS</span>", unsafe_allow_html=True)
        st.markdown("### Statutory & Broker Fee Table")
        st.dataframe(
            charges_items.style.format({
                'Amount': '₹{:,.2f}',
                'Share %': '{:.2f}%'
            }),
            use_container_width=True
        )


# ==============================================================================
# TAB 4: PORTFOLIO RISK & REBALANCING ENGINE (MACRO -> DIVERSIFICATION -> MICRO)
# ==============================================================================
with tab_risk:
    if holdings_df.empty:
        st.info("Upload holdings to run the Risk & Rebalancing Engine.")
    else:
        rebal_df, risk_alerts = evaluate_portfolio_risks(holdings_df, max_target_weight=max_pos_target)

        # LEVEL 1: MACRO RISK ALERTS & ACTION BUCKET COUNTS
        st.markdown("<span class='flow-badge'>LEVEL 1: MACRO RISK SAFEGUARDS</span>", unsafe_allow_html=True)
        st.markdown("### Capital Preservation & Safeguard Alerts")

        if risk_alerts:
            for alert in risk_alerts:
                banner_class = f"risk-banner-{alert['level']}"
                icon = "⚠️" if alert['level'] == 'warning' else "🚨"
                st.markdown(
                    f"""
                    <div class="{banner_class}">
                        <b>{icon} {alert['title']}</b><br>
                        <span style="color: #cbd5e1; font-size: 0.9rem;">{alert['desc']}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                """
                <div class="risk-banner-success">
                    <b>✅ Clean Portfolio Health</b><br>
                    <span style="color: #cbd5e1; font-size: 0.9rem;">No severe concentration (>15%) or deep impairment (>20%) flags detected.</span>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

        action_counts = rebal_df['Action'].value_counts().to_dict()
        b_c1, b_c2, b_c3, b_c4, b_c5 = st.columns(5)
        with b_c1:
            st.markdown(
                f"""
                <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 10px; padding: 14px; text-align: center;">
                    <div style="color: #10b981; font-weight: 700; font-size: 1.3rem;">{action_counts.get('CORE BUY', 0)}</div>
                    <div style="color: #94a3b8; font-size: 0.8rem; font-weight: 600;">CORE BUY</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with b_c2:
            st.markdown(
                f"""
                <div style="background: rgba(168, 85, 247, 0.1); border: 1px solid rgba(168, 85, 247, 0.35); border-radius: 10px; padding: 14px; text-align: center;">
                    <div style="color: #c084fc; font-weight: 700; font-size: 1.3rem;">{action_counts.get('ACCUMULATE ON DIP', 0)}</div>
                    <div style="color: #94a3b8; font-size: 0.8rem; font-weight: 600;">ACCUMULATE</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with b_c3:
            st.markdown(
                f"""
                <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.35); border-radius: 10px; padding: 14px; text-align: center;">
                    <div style="color: #3b82f6; font-weight: 700; font-size: 1.3rem;">{action_counts.get('HOLD', 0)}</div>
                    <div style="color: #94a3b8; font-size: 0.8rem; font-weight: 600;">HOLD</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with b_c4:
            st.markdown(
                f"""
                <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.35); border-radius: 10px; padding: 14px; text-align: center;">
                    <div style="color: #f59e0b; font-weight: 700; font-size: 1.3rem;">{action_counts.get('REDUCE', 0)}</div>
                    <div style="color: #94a3b8; font-size: 0.8rem; font-weight: 600;">REDUCE</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with b_c5:
            st.markdown(
                f"""
                <div style="background: rgba(244, 63, 94, 0.1); border: 1px solid rgba(244, 63, 94, 0.35); border-radius: 10px; padding: 14px; text-align: center;">
                    <div style="color: #f43f5e; font-weight: 700; font-size: 1.3rem;">{action_counts.get('EXIT', 0)}</div>
                    <div style="color: #94a3b8; font-size: 0.8rem; font-weight: 600;">EXIT</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

        # LEVEL 2: MICRO REBALANCING MATRIX TABLE
        st.markdown("<span class='flow-badge'>LEVEL 2: ACTION MATRIX & TARGET REALLOCATION</span>", unsafe_allow_html=True)
        st.markdown(f"### Stock-by-Stock Action Matrix (Target Max Weight: {max_pos_target:.0f}%)")

        display_rebal = rebal_df[[
            'Stock Name', 'Group', 'Weight %', 'Unrealised P&L %', 'Action',
            'Risk Flags', 'Suggested Trim / Rebalance (₹)', 'Rationale'
        ]].copy()

        st.dataframe(
            display_rebal.style.format({
                'Weight %': '{:.2f}%',
                'Unrealised P&L %': '{:+.2f}%',
                'Suggested Trim / Rebalance (₹)': '₹{:,.2f}'
            }).map(
                lambda val: (
                    'color: #10b981; font-weight: 700;' if val == 'CORE BUY' else
                    ('color: #c084fc; font-weight: 700;' if val == 'ACCUMULATE ON DIP' else
                    ('color: #3b82f6; font-weight: 700;' if val == 'HOLD' else
                    ('color: #f59e0b; font-weight: 700;' if val == 'REDUCE' else
                    ('color: #f43f5e; font-weight: 700;' if val == 'EXIT' else ''))))
                ),
                subset=['Action']
            ).map(
                lambda val: 'color: #f43f5e; font-weight: 600;' if isinstance(val, (int, float)) and val < -20 else ('color: #10b981; font-weight: 600;' if isinstance(val, (int, float)) and val > 0 else ''),
                subset=['Unrealised P&L %']
            ),
            use_container_width=True,
            height=450
        )


# ==============================================================================
# TAB 5: MASTER MULTI-SHEET EXCEL & CSV EXPORT
# ==============================================================================
with tab_export:
    st.markdown("<span class='flow-badge'>LEVEL 1: MASTER EXPORT</span>", unsafe_allow_html=True)
    st.markdown("### Master Portfolio & P&L Intelligence Export")
    st.markdown("Generate and download a single consolidated **Master Excel Workbook** containing all 6 processed analytical sheets.")

    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        if not holdings_df.empty:
            holdings_df.to_excel(writer, sheet_name='Holdings Analysis', index=False)
        if not realized_trades_df.empty:
            realized_trades_df.to_excel(writer, sheet_name='Realised Trades Log', index=False)
        if not daily_pnl_df.empty:
            daily_pnl_df.to_excel(writer, sheet_name='Daily PnL Journal', index=False)
        if not charges_df.empty:
            charges_df.to_excel(writer, sheet_name='Charges Breakdown', index=False)
        if not lifecycle_df.empty:
            lifecycle_df.to_excel(writer, sheet_name='Lifecycle Scrip Matrix', index=False)
        if not holdings_df.empty:
            rebal_export_df, _ = evaluate_portfolio_risks(holdings_df, max_target_weight=max_pos_target)
            rebal_export_df.to_excel(writer, sheet_name='Rebalancing Plan', index=False)

    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        st.markdown(
            """
            <div class="glass-card">
                <div class="glass-card-header">
                    <span>📑 Master Multi-Sheet Excel Workbook</span>
                    <span class="badge-pill badge-buy">6 Sheets</span>
                </div>
                <p style="color: #94a3b8; font-size: 0.88rem;">
                    Includes 6 formatted tabs: <b>Holdings Analysis, Realised Trades Log, Daily P&L Journal, Charges Breakdown, Lifecycle Scrip Matrix, and Rebalancing Action Plan</b>.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.download_button(
            label="📥 Download Master Portfolio Workbook (.xlsx)",
            data=excel_buffer.getvalue(),
            file_name=f"Equity_Portfolio_Master_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with col_exp2:
        st.markdown(
            """
            <div class="glass-card">
                <div class="glass-card-header">
                    <span>⚡ Quick CSV Datasets</span>
                    <span class="badge-pill badge-hold">Modular Data</span>
                </div>
                <p style="color: #94a3b8; font-size: 0.88rem;">
                    Download individual modular datasets for direct integration into Python, Excel, or custom trading backtesters.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        sub_c1, sub_c2 = st.columns(2)
        with sub_c1:
            if not holdings_df.empty:
                h_buf = io.StringIO()
                holdings_df.to_csv(h_buf, index=False)
                st.download_button("📥 Holdings (CSV)", data=h_buf.getvalue(), file_name="Holdings.csv", mime="text/csv")
        with sub_c2:
            if not daily_pnl_df.empty:
                d_buf = io.StringIO()
                daily_pnl_df.to_csv(d_buf, index=False)
                st.download_button("📥 Daily Journal (CSV)", data=d_buf.getvalue(), file_name="Daily_Journal.csv", mime="text/csv")

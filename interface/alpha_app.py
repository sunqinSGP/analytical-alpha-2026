"""
Analytical Alpha — 2026 Strategic Growth Investment Framework
Professional-grade stock analysis applying the dual-quadrant approach.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from stock_analyzer.alpha_engine import alpha_analysis, THEMES_2026, NoB_TYPES

# Page config
st.set_page_config(
    page_title="Analytical Alpha 2026",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# FinancialPlanner-style CSS — high contrast + bold emphasis
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@300;400;500;600;700;800;900&display=swap');

    /* === ROOT & RESET === */
    * { box-sizing: border-box; }
    html, body, [class*="css"] {
        font-size: 13px;
        font-family: 'Segoe UI', Arial, sans-serif;
        line-height: 1.5;
        color: #111827;
        background: #ebeef2;
    }

    section[data-testid="stSidebar"] { display: none; }
    .stApp { margin-top: -2rem; background: #ebeef2; }
    div[data-testid="stVerticalBlock"] { gap: 0.3rem; }

    /* === TYPOGRAPHY === */
    h1 { font-size: 1.3rem !important; font-weight: 800 !important; color: #0d1b3e; margin: 0 !important; letter-spacing: -0.02em; }
    h2 { font-size: 1.1rem !important; font-weight: 800 !important; color: #0d1b3e; margin: 18px 0 10px 0 !important; }
    h3 { font-size: 0.95rem !important; font-weight: 700 !important; color: #1e3a6b; margin: 14px 0 8px 0 !important; }

    /* === NAVY HEADER === */
    .stApp > header { background: linear-gradient(135deg, #0d1b3e 0%, #1a3a6b 100%) !important; }

    /* === TABS === */
    .stTabs [data-baseweb="tab-list"] { gap: 2px; border-bottom: 2px solid #d0d5dc; background: transparent; padding: 0 4px; }
    .stTabs [data-baseweb="tab"] {
        font-size: 0.73rem !important; padding: 10px 18px !important;
        font-weight: 600; color: #666; border-radius: 6px 6px 0 0 !important;
        border-bottom: 3px solid transparent !important; margin-right: 2px;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #0d1b3e; font-weight: 700; background: #fff;
        border-bottom: 3px solid #1a3a6b !important;
    }

    /* === KPI CARDS (top bar) === */
    .kpi {
        background: #fff; border-radius: 10px; padding: 14px 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06); border-left: 5px solid #1a3a6b;
        transition: transform 0.15s;
    }
    .kpi:hover { transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,0.1); }
    .kpi .kpi-label { font-size: 0.6rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; color: #777; margin-bottom: 5px; }
    .kpi .kpi-value { font-size: 1.35rem; font-weight: 800; color: #0d1b3e; line-height: 1.1; }
    .kpi .kpi-sub { font-size: 0.65rem; font-weight: 600; color: #999; margin-top: 3px; }
    .kpi.green { border-left-color: #0d8a3e; }
    .kpi.green .kpi-value { color: #0d8a3e; }
    .kpi.red { border-left-color: #c62828; }
    .kpi.red .kpi-value { color: #c62828; }
    .kpi.purple { border-left-color: #6a1b9a; }
    .kpi.purple .kpi-value { color: #6a1b9a; }
    .kpi.teal { border-left-color: #00695c; }
    .kpi.teal .kpi-value { color: #00695c; }

    /* === VERDICT BANNERS === */
    .verdict { padding: 16px 22px; border-radius: 10px; margin: 14px 0; font-size: 0.88rem; font-weight: 600; }
    .verdict.conviction-high { background: #c8f7d5; border-left: 5px solid #0d8a3e; color: #074a1f; }
    .verdict.conviction-moderate { background: #d0dff7; border-left: 5px solid #1a3a6b; color: #0d1b3e; }
    .verdict.conviction-selective { background: #ffe0b2; border-left: 5px solid #e65100; color: #7a2e00; }
    .verdict.conviction-opportunistic { background: #fff9c4; border-left: 5px solid #f9a825; color: #5d3f00; }
    .verdict.conviction-pass { background: #ffcdd2; border-left: 5px solid #c62828; color: #5f0000; }

    /* === TAGS === */
    .tag { display: inline-block; padding: 3px 10px; border-radius: 14px; font-size: 0.62rem; font-weight: 700; }
    .tag.green { background: #c8f7d5; color: #0d8a3e; }
    .tag.red { background: #ffcdd2; color: #c62828; }
    .tag.amber { background: #ffe0b2; color: #e65100; }
    .tag.blue { background: #d0dff7; color: #1a3a6b; }
    .tag.purple { background: #e1bee7; color: #6a1b9a; }
    .tag.gray { background: #e0e0e0; color: #444; }

    /* === DIVIDERS === */
    hr { margin: 0.75rem 0; border: none; border-top: 2px solid #d0d5dc; }

    /* === DATAFRAMES (Streamlit native) === */
    .stDataFrame {
        font-size: 12px !important; border: none; border-radius: 10px;
        margin: 8px 0 14px 0; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .stDataFrame th {
        font-size: 0.65rem !important; padding: 10px 14px !important;
        background: #0d1b3e !important; color: #fff !important;
        font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; border: none !important;
    }
    .stDataFrame td {
        font-size: 0.78rem !important; padding: 8px 14px !important;
        color: #111827; border-bottom: 1px solid #e0e4ea;
    }
    .stDataFrame tr:nth-child(even) td { background: #f5f6f9; }

    /* === HTML TABLES (our custom ones) === */
    table { width: 100%; border-collapse: collapse; font-size: 0.78rem; }
    th {
        background: #0d1b3e; color: #fff; padding: 10px 14px;
        text-align: left; font-weight: 700; font-size: 0.66rem;
        text-transform: uppercase; letter-spacing: 0.6px; white-space: nowrap;
    }
    td { padding: 8px 14px; border-bottom: 1px solid #e0e4ea; vertical-align: middle; font-weight: 500; }
    tr:nth-child(even) td { background: #f5f6f9; }
    td b, td strong { font-weight: 800; color: #0d1b3e; }

    /* === LINKS === */
    a { color: #1a3a6b; text-decoration: none; font-weight: 700; }
    a:hover { text-decoration: underline; }

    /* === INPUTS === */
    input, select, .stTextInput>div>div>input {
        border-radius: 8px !important; border: 2px solid #c8ccd4 !important;
        font-size: 0.82rem !important; padding: 9px 14px !important;
        background: #fff !important; font-weight: 500 !important;
    }
    input:focus, select:focus {
        border-color: #1a3a6b !important; outline: none !important;
        box-shadow: 0 0 0 3px rgba(26,58,107,0.12) !important;
    }

    /* === BUTTONS === */
    button { border-radius: 8px !important; font-weight: 700 !important; font-size: 0.82rem !important; }
    button[kind="primary"] { background: #0d1b3e !important; color: #fff !important; border: none !important; }
    button[kind="primary"]:hover { background: #1a3a6b !important; }

    /* === FACTOR ATTRIBUTION === */
    .factor-row {
        display: flex; align-items: center; gap: 14px;
        padding: 8px 16px; margin: 3px 0;
        background: #fff; border: 2px solid #e8edf3; border-radius: 8px;
        font-weight: 600;
    }
    .factor-row:hover { background: #f0f3f8; border-color: #c8d0db; }

    /* === SCROLLBAR === */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #ebeef2; }
    ::-webkit-scrollbar-thumb { background: #b0b8c4; border-radius: 3px; }

    /* === NOB BANNER === */
    .nob-banner {
        padding: 14px 20px; border-radius: 10px; margin: 12px 0;
        font-size: 0.86rem; display: flex; align-items: center; gap: 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }

    /* === THEME ACCENTS === */
    .theme-ai { border-left: 4px solid #6a1b9a; padding-left: 14px; }
    .theme-energy { border-left: 4px solid #e65100; padding-left: 14px; }
    .theme-health { border-left: 4px solid #0d8a3e; padding-left: 14px; }
    .theme-software { border-left: 4px solid #1a3a6b; padding-left: 14px; }

    /* === SPACING === */
    .stMarkdown { margin-bottom: 2px !important; }
    .stCaption { margin-top: 2px !important; margin-bottom: 6px !important; font-size: 0.75rem !important; color: #777 !important; font-weight: 500; }
    p { margin-bottom: 3px !important; }
    div[data-testid="column"] { padding: 0 3px; }
    div[data-testid="stTabs"] { margin-top: 6px; }
    div[data-baseweb="tab-panel"] { padding-top: 8px !important; }
</style>
""", unsafe_allow_html=True)


# ===========================================================================
# Currency helpers
# ===========================================================================
def detect_currency(ticker):
    currency_map = {'.SI': 'SGD', '.HK': 'HKD', '.T': 'JPY', '.L': 'GBP', '.DE': 'EUR'}
    for suffix, curr in currency_map.items():
        if ticker.endswith(suffix):
            return curr
    return 'USD'


CURRENCY_SYMBOLS = {'USD': '$', 'SGD': 'S$', 'HKD': 'HK$', 'JPY': '¥', 'GBP': '£', 'EUR': '€'}


# ===========================================================================
# Helper components
# ===========================================================================
def metric_card(label, value, sub=None, color=None):
    style = f"color:{color};" if color else ""
    sub_html = f'<div class="sub">{sub}</div>' if sub else ''
    return f'<div class="alpha-card"><div class="label">{label}</div><div class="value" style="{style}">{value}</div>{sub_html}</div>'


def tag(label, style="gray"):
    return f'<span class="tag {style}">{label}</span>'


def moat_bar(rating):
    if rating >= 8:
        color = "#16a34a"
    elif rating >= 6:
        color = "#ea580c"
    elif rating >= 4:
        color = "#ca8a04"
    else:
        color = "#dc2626"
    return f'<div class="moat-gauge"><div class="moat-bar"><div class="moat-fill" style="width:{rating*10}%;background:{color};"></div></div><b style="font-size:1.3rem;color:{color};">{rating}/10</b></div>'


# ===========================================================================
# HEADER
# ===========================================================================
# ===========================================================================
# HEADER — FinancialPlanner navy gradient style
# ===========================================================================
st.markdown("""
<div style="background: linear-gradient(135deg, #0d1b3e 0%, #1a3a6b 100%); margin: -2rem -4rem 0 -4rem; padding: 14px 4rem 14px 4rem; box-shadow: 0 3px 16px rgba(0,0,0,0.35);">
    <div style="display: flex; align-items: center; justify-content: space-between;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 18px; font-weight: 800; color: #fff; letter-spacing: 0.3px;">Analytical Alpha</span>
            <span style="color: #64b5f6; font-size: 0.65rem; font-weight: 600; letter-spacing: 0.8px; text-transform: uppercase; background: rgba(255,255,255,0.1); padding: 3px 10px; border-radius: 4px;">2026</span>
        </div>
        <span style="font-size: 0.7rem; color: rgba(255,255,255,0.5); font-weight: 500;">Strategic Growth Investment Framework</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Input row
col1, col2, col3, col4 = st.columns([0.4, 0.22, 0.22, 0.16])
with col1:
    ticker = st.text_input(
        "Ticker",
        placeholder="AAPL  QLYS  3323.HK  D05.SI  NVDA",
        label_visibility="collapsed"
    ).upper().strip()
with col2:
    framework_options = ['Auto-Detect'] + [v['name'] for v in NoB_TYPES.values()]
    framework_choice = st.selectbox(
        "Framework",
        framework_options,
        index=0,
        label_visibility="collapsed"
    )
with col3:
    weight_pct = st.number_input("Position %", 0.0, 100.0, 0.0, 0.5, label_visibility="collapsed", placeholder="Position weight %")
with col4:
    st.markdown('<div style="padding-top:4px;"></div>', unsafe_allow_html=True)

if not ticker:
    st.markdown("<br>", unsafe_allow_html=True)

    # Hero section
    st.markdown("""
    <div style="text-align:center; padding: 20px 0 10px 0;">
        <h2 style="font-size:1.5rem !important; font-weight:700; color:#0f172a; margin-bottom:6px;">
            Strategic Growth Investment Framework
        </h2>
        <p style="font-size:0.9rem; color:#64748b; max-width:700px; margin:0 auto;">
            Nature-of-Business classification with six specialized valuation frameworks,
            Circumvention Delta moat architecture, and three Master Forward-Looking Indicators.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Feature cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("""
        <div class="alpha-card" style="text-align:center; min-height:130px;">
            <span style="font-size:1.5rem;"></span>
            <div class="label" style="margin-top:6px;">NoB Classification</div>
            <div style="font-size:0.78rem;color:#475569;margin-top:4px;">
            Auto-detects business model: SaaS, Semiconductor, Energy, Biopharma, Value, or Growth
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="alpha-card" style="text-align:center; min-height:130px;">
            <span style="font-size:1.5rem;"></span>
            <div class="label" style="margin-top:6px;">Circumvention Delta</div>
            <div style="font-size:0.78rem;color:#475569;margin-top:4px;">
            Quantifies competitive moat: Time + Capital + Performance Loss = total competitor burden
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="alpha-card" style="text-align:center; min-height:130px;">
            <span style="font-size:1.5rem;"></span>
            <div class="label" style="margin-top:6px;">Forward-Looking</div>
            <div style="font-size:0.78rem;color:#475569;margin-top:4px;">
            RPO divergence, NRR installed growth, and Forward Rule of 40 inflection detection
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown("""
        <div class="alpha-card" style="text-align:center; min-height:130px;">
            <span style="font-size:1.5rem;"></span>
            <div class="label" style="margin-top:6px;">2026 Macro Context</div>
            <div style="font-size:0.78rem;color:#475569;margin-top:4px;">
            K-shaped economy, value rotation, S&P 7,500 target, and barbell portfolio strategy
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Framework quick reference
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Available Valuation Frameworks")
    fw_cols = st.columns(6)
    for i, (key, fw) in enumerate(NoB_TYPES.items()):
        with fw_cols[i]:
            st.markdown(f"""
            <div class="alpha-card" style="text-align:center; border-top:3px solid {fw['color']};">
                <div class="label">{fw['icon']} {fw['name']}</div>
                <div style="font-size:0.72rem;color:#64748b;margin-top:4px;line-height:1.4;">{fw['metrics_focus']}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.info("Enter a ticker above to begin. Try **QLYS** (High-Growth SaaS), **3323.HK** (Traditional Value), **NVDA** (AI Infra), or **BE** (Energy). Use the Framework dropdown to override auto-detection.")
    st.stop()


# ===========================================================================
# RUN ANALYSIS
# ===========================================================================

# Map framework choice back to NoB key
FRAMEWORK_MAP = {v['name']: k for k, v in NoB_TYPES.items()}
framework_override = None
if framework_choice != 'Auto-Detect':
    framework_override = FRAMEWORK_MAP.get(framework_choice)

with st.spinner(f"Running 2026 Alpha Analysis on {ticker}..."):
    import inspect
    params = inspect.signature(alpha_analysis).parameters
    if 'framework' in params:
        result = alpha_analysis(ticker, current_weight_pct=weight_pct, framework=framework_override)
    else:
        result = alpha_analysis(ticker, current_weight_pct=weight_pct)

if 'error' in result:
    st.error(result['error'])
    st.stop()

data = result['data']
info = data['info']
quant = result['quantitative']
qual = result['qualitative']
thematic = result['thematic']
risk_mgmt = result['risk_management']
portfolio = result['portfolio']
thesis = result['thesis']
perf = result['price_performance']

currency = detect_currency(ticker)
cs = CURRENCY_SYMBOLS.get(currency, '$')

price = data['price'] or 0
mcap = info.get('marketCap')
name = data['name']

# ===========================================================================
# TOP BAR — 8 key metrics
# ===========================================================================
moat = qual['moat']
r40 = quant['rule_of_40']
gm_data = quant['gross_margin']
momentum = quant['momentum']
arr = quant['arr_growth']
risk_factors = risk_mgmt['risk_factors']

c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(8)
with c1:
    st.markdown(f'<div class="kpi"><div class="kpi-label">Price</div><div class="kpi-value">{cs}{price:.2f}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="kpi"><div class="kpi-label">Market Cap</div><div class="kpi-value">{cs}{mcap/1e9:.1f}B</div></div>' if mcap else '<div class="kpi"><div class="kpi-label">Market Cap</div><div class="kpi-value">N/A</div></div>', unsafe_allow_html=True)
with c3:
    r40_val = r40.get('rule_40_fcf')
    c3_class = 'kpi green' if (r40_val and r40_val >= 50) else ('kpi' if (r40_val and r40_val >= 40) else 'kpi red')
    st.markdown(f'<div class="{c3_class}"><div class="kpi-label">Rule of 40</div><div class="kpi-value">{f"{r40_val:.0f}" if r40_val is not None else "N/A"}</div><div class="kpi-sub">{"FCF basis" if r40_val is not None else ""}</div></div>', unsafe_allow_html=True)
with c4:
    gm_val = gm_data.get('gross_margin_pct')
    c4_class = 'kpi green' if (gm_val and gm_val >= 75) else ('kpi' if (gm_val and gm_val >= 40) else 'kpi red')
    st.markdown(f'<div class="{c4_class}"><div class="kpi-label">Gross Margin</div><div class="kpi-value">{f"{gm_val:.0f}%" if gm_val is not None else "N/A"}</div></div>', unsafe_allow_html=True)
with c5:
    nrr = quant['net_revenue_retention']
    nrr_val = nrr.get('estimated_nrr_pct')
    c5_class = 'kpi green' if (nrr_val and nrr_val >= 120) else ('kpi teal' if (nrr_val and nrr_val >= 106) else 'kpi')
    nrr_sub_kpi = "Installed growth" if (nrr_val and nrr_val >= 120) else ("Above benchmark" if (nrr_val and nrr_val >= 106) else "")
    st.markdown(f'<div class="{c5_class}"><div class="kpi-label">Est. NRR</div><div class="kpi-value">{f"{nrr_val:.0f}%" if nrr_val is not None else "N/A"}</div><div class="kpi-sub">{nrr_sub_kpi}</div></div>', unsafe_allow_html=True)
with c6:
    moat_val = moat['moat_rating']
    c6_class = 'kpi green' if moat_val >= 7 else ('kpi purple' if moat_val >= 5 else 'kpi red')
    st.markdown(f'<div class="{c6_class}"><div class="kpi-label">Moat Rating</div><div class="kpi-value">{moat_val}/10</div><div class="kpi-sub">{moat["moat_label"].split(chr(8212))[0].strip() if chr(8212) in moat["moat_label"] else moat["moat_label"][:20]}</div></div>', unsafe_allow_html=True)
with c7:
    rank_label = momentum.get('rank_label', 'N/A')
    c7_class = 'kpi green' if momentum.get('zacks_rank') in [1, 2] else ('kpi purple' if momentum.get('zacks_rank') == 3 else 'kpi red')
    st.markdown(f'<div class="{c7_class}"><div class="kpi-label">Momentum</div><div class="kpi-value">{rank_label}</div></div>', unsafe_allow_html=True)
with c8:
    risk_level = risk_factors.get('risk_level', 'N/A')
    c8_class = 'kpi green' if risk_level == 'Low' else ('kpi' if risk_level == 'Medium' else 'kpi red')
    st.markdown(f'<div class="{c8_class}"><div class="kpi-label">Risk Level</div><div class="kpi-value">{risk_level}</div></div>', unsafe_allow_html=True)

st.markdown(f'<small><b>{name}</b> | {data["sector"]} | {data["industry"]} | {data.get("country", "")} | Currency: {currency} | Employees: {data.get("employees", "N/A"):,}</small>', unsafe_allow_html=True)

# ===========================================================================
# NoB BUSINESS MODEL BANNER
# ===========================================================================
nob_type = result['nob_type']
nob = result['nob']
st.markdown(f"""
<div class="nob-banner" style="background: {nob['color']}10; border-left: 4px solid {nob['color']}; background: #fff;">
    <span style="font-size:1.4rem;">{nob['icon']}</span>
    <div>
        <div style="font-weight:700; font-size:0.85rem; color:{nob['color']};">{nob['name']}</div>
        <div style="font-size:0.7rem; color:#888;">{nob['description']}</div>
    </div>
    <div style="margin-left:auto; font-size:0.65rem; color:#888; background:#f7f9fb; padding:4px 10px; border-radius:12px;">
        {nob['metrics_focus']}
    </div>
</div>
""", unsafe_allow_html=True)

# ===========================================================================
# MAIN TAB BAR
# ===========================================================================
st.markdown("---")
t1, t2, t3, t4, t5, t6, t7, t8 = st.tabs([
    "1. Overview", "2. Quantitative", "3. Qualitative Moat",
    "4. 2026 Themes", "5. Risk Management", "6. Portfolio Context", "7. Conviction",
    "8. Screener"
])

# ===== TAB 1: OVERVIEW =====
with t1:
    # =========================================================================
    # CONVICTION SPECTRUM — compact table
    # =========================================================================
    conv = thesis['conviction']
    conviction_levels = [
        {'level': 'HIGH CONVICTION', 'detail': 'Wide moat + installed growth + clean risk',
         'color': '#059669', 'bg': '#ecfdf5'},
        {'level': 'MODERATE CONVICTION', 'detail': 'Solid fundamentals, manageable risk',
         'color': '#2563eb', 'bg': '#eff6ff'},
        {'level': 'SELECTIVE', 'detail': 'Good moat but elevated risk — reduce size',
         'color': '#ea580c', 'bg': '#fff7ed'},
        {'level': 'OPPORTUNISTIC', 'detail': 'Limited moat, favorable risk/reward — trade',
         'color': '#ca8a04', 'bg': '#fefce8'},
        {'level': 'PASS', 'detail': 'Better opportunities elsewhere in 2026',
         'color': '#dc2626', 'bg': '#fef2f2'},
    ]

    rows_html = []
    for cl in conviction_levels:
        is_active = cl['level'] == conv
        color = cl['color']
        bg = cl['bg']
        level = cl['level']
        detail = cl['detail']

        if is_active:
            rows_html.append(
                '<tr style="background:' + bg + '; font-weight:800; border-left:4px solid ' + color + ';">'
                '<td style="padding:5px 12px; font-size:0.78rem; color:' + color + '; font-weight:800;">' + level + '</td>'
                '<td style="padding:5px 12px; font-size:0.75rem; color:#0d1b3e; font-weight:700;">' + detail + '</td>'
                '<td style="padding:5px 12px; text-align:right;">'
                '<span style="background:' + color + '; color:#fff; padding:2px 10px; border-radius:4px; font-size:0.65rem; font-weight:800;">ACTIVE</span>'
                '</td></tr>'
            )
        else:
            rows_html.append(
                '<tr style="opacity:0.35; border-left:4px solid transparent;">'
                '<td style="padding:5px 12px; font-size:0.7rem; color:#999;">' + level + '</td>'
                '<td style="padding:5px 12px; font-size:0.7rem; color:#999;">' + detail + '</td>'
                '<td style="padding:5px 12px;"></td></tr>'
            )

    table_html = (
        '<table style="width:100%; border-collapse:collapse; font-family:Inter,sans-serif;">'
        '<thead><tr style="border-bottom:2px solid #e2e8f0;">'
        '<th style="padding:4px 10px; font-size:0.62rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.06em; text-align:left; width:160px;">Conviction Level</th>'
        '<th style="padding:4px 10px; font-size:0.62rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.06em; text-align:left;">Criteria</th>'
        '<th style="padding:4px 10px; text-align:right; width:60px;"></th>'
        '</tr></thead><tbody>'
        + '\n'.join(rows_html) +
        '</tbody></table>'
    )
    st.markdown(table_html, unsafe_allow_html=True)

    # Thesis paragraph
    st.markdown("### Investment Thesis")
    st.markdown(f'<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:16px 20px;font-size:0.88rem;line-height:1.7;color:#334155;">{thesis["thesis"]}</div>', unsafe_allow_html=True)

    # Framework summary — compact table
    def fmt_pct(v):
        return f"{v:.0f}%" if v is not None else "N/A"
    def fmt_num(v):
        return f"{v:.0f}" if v is not None else "N/A"

    fwd_r40_overview = quant['forward_rule_of_40']
    fwd_r40_val_ov = fwd_r40_overview.get('forward_rule_40')
    fwd_inflection_ov = fwd_r40_overview.get('inflection_signal', '')
    rpo_signal_ov = quant['rpo'].get('leading_indicator_signal', 'N/A')

    # Build NoB-specific metric strings
    q_metrics = []
    if nob_type == 'high_growth_saas':
        saas = quant.get('saas_filter', {})
        q_metrics = [
            'R40(FCF) ' + fmt_num(r40_val),
            'LTV:CAC ' + (f"{saas.get('ltv_cac_ratio')}:1" if saas.get('ltv_cac_ratio') is not None else 'N/A'),
            'CAC ' + (f"{saas.get('cac_payback_months'):.0f}mo" if saas.get('cac_payback_months') else 'N/A'),
            'GM ' + fmt_pct(gm_val),
            'NRR ' + fmt_pct(nrr_val),
        ]
    elif nob_type == 'ai_infra_semiconductor':
        ind = quant.get('industrial_filter', {})
        q_metrics = [
            'Rev ' + fmt_pct(ind.get('revenue_growth_pct')),
            'Backlog ' + fmt_pct(ind.get('backlog_growth_pct')),
            'Conv ' + (f"{ind.get('conversion_velocity'):.2f}x" if ind.get('conversion_velocity') is not None else 'N/A'),
            'EPS ' + (ind.get('revision_led_eps', {}).get('rank', 'N/A')[:20]),
        ]
    elif nob_type == 'energy_industrial':
        ind = quant.get('industrial_filter', {})
        q_metrics = [
            'Rev ' + fmt_pct(ind.get('revenue_growth_pct')),
            'Backlog ' + fmt_pct(ind.get('backlog_growth_pct')),
            'Pipeline ' + ('GW' if ind.get('power_pipeline_note') else 'N/A'),
        ]
    elif nob_type == 'biopharma':
        bio = quant.get('biopharma_filter', {})
        q_metrics = [
            'Stage ' + bio.get('clinical_stage', 'N/A'),
            'rNPV ' + fmt_pct(bio.get('discount_rate_pct')),
            'AI ' + ('Yes' if bio.get('ai_attrition_premium') else 'No'),
            'Rev ' + fmt_pct(bio.get('revenue_growth_pct')),
        ]
    elif nob_type == 'traditional_value':
        val = quant.get('value_filter', {})
        tpe = val.get('trailing_pe')
        q_metrics = [
            'P/E ' + (f"{tpe:.1f}x" if tpe and tpe > 0 else 'N/A'),
            'P/B ' + (f"{val.get('price_to_book'):.2f}x" if val.get('price_to_book') is not None else 'N/A'),
            'Div ' + (f"{val.get('dividend_yield_pct'):.1f}%" if val.get('dividend_yield_pct') is not None else 'N/A'),
            'Score ' + (f"{val.get('value_score')}/10" if val.get('value_score') is not None else 'N/A'),
        ]
    elif nob_type == 'high_growth_general':
        gf = quant.get('growth_filter', {})
        runway = gf.get('cash_runway_years')
        q_metrics = [
            'Rev ' + fmt_pct(gf.get('revenue_growth_pct')),
            'Runway ' + (f"{runway:.0f}yrs" if runway is not None else 'N/A'),
            'Score ' + (f"{gf.get('growth_score')}/10" if gf.get('growth_score') is not None else 'N/A'),
        ]
    else:
        q_metrics = [
            'R40 ' + fmt_num(r40_val),
            'GM ' + fmt_pct(gm_val),
            'NRR ' + fmt_pct(nrr_val),
        ]

    # Moat metrics
    temporal = moat['temporal_width']; efficiency = moat['efficiency_width']; trust = moat['trust_width']
    perf_sig = qual.get('moat_performance', {}).get('performance', '')

    # Thematic
    primary_name = thematic.get('primary_name', 'None')
    primary_conviction = thematic.get('primary_conviction', 0)
    secondary_themes = ', '.join(t['name'] for t in thematic.get('secondary_themes', []))

    # Risk
    risk_max = risk_factors.get('max_suggested_position', 10)
    position = risk_mgmt['position_sizing']
    barbell = risk_mgmt['barbell_check']

    # Build compact table
    summary_html = (
        '<table style="width:100%; border-collapse:collapse; font-family:Inter,sans-serif; margin:8px 0;">'
        '<colgroup><col style="width:28%"><col style="width:24%"><col style="width:24%"><col style="width:24%"></colgroup>'
        '<thead><tr style="border-bottom:2px solid #e2e8f0;">'
        '<th style="padding:5px 10px; font-size:0.62rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.06em; text-align:left;">'
        'Quantitative &mdash; ' + nob['name'] + '</th>'
        '<th style="padding:5px 10px; font-size:0.62rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.06em; text-align:left;">'
        'Moat Architecture</th>'
        '<th style="padding:5px 10px; font-size:0.62rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.06em; text-align:left;">'
        '2026 Thematic</th>'
        '<th style="padding:5px 10px; font-size:0.62rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.06em; text-align:left;">'
        'Risk Framework</th>'
        '</tr></thead><tbody><tr style="vertical-align:top;">'

        # Quantitative column
        + '<td style="padding:5px 10px; font-size:0.7rem; line-height:1.5;">'
        + '<br>'.join(q_metrics)
        + '<br><span style="font-size:0.63rem; color:#888;">Fwd R40 ' + (f'{fwd_r40_val_ov:.0f}' if fwd_r40_val_ov is not None else 'N/A') + ' &mdash; ' + fwd_inflection_ov + '</span>'
        + '<br><span style="font-size:0.63rem; color:#888;">RPO: ' + rpo_signal_ov + '</span>'
        + '</td>'

        # Moat column
        + '<td style="padding:5px 10px; font-size:0.7rem; line-height:1.5;">'
        + f'Temporal: <b>{temporal["score"]}/5</b><br>'
        + f'Efficiency: <b>{efficiency["score"]}/5</b><br>'
        + f'Trust: <b>{trust["score"]}/5</b><br>'
        + f'<b>Composite: {moat_val}/10</b><br>'
        + f'<span style="font-size:0.63rem; color:#888;">{moat["moat_label"]}</span><br>'
        + f'<span style="font-size:0.63rem; color:#888;">Trend: {perf_sig}</span>'
        + '</td>'

        # Thematic column — with secondary themes
        + '<td style="padding:5px 10px; font-size:0.7rem; line-height:1.5;">'
        + f'Primary: <b>{primary_name}</b> ({primary_conviction}/10)<br>'
        + (f'Secondary: <b>{secondary_themes}</b><br>' if secondary_themes else '')
        + f'<span style="font-size:0.63rem; color:#888;">{thematic.get("primary_catalyst", "")}</span>'
        + '</td>'

        # Risk column — with stop-loss + barbell
        + '<td style="padding:5px 10px; font-size:0.7rem; line-height:1.5;">'
        + f'Risk: <b>{risk_level}</b> ({risk_factors.get("risk_score", 0)})<br>'
        + f'Max: <b>{risk_max}% NAV</b><br>'
        + f'<span style="font-size:0.63rem; color:#888;">{position["action"]}</span><br>'
        + f'<span style="font-size:0.63rem; color:#888;">Barbell: {barbell.get("message", "")}</span>'
        + '</td>'

        + '</tr></tbody></table>'
    )
    st.markdown(summary_html, unsafe_allow_html=True)

    # Price performance — compact row
    if perf:
        perf_items = []
        for lbl in ['1m', '3m', '6m', '1y']:
            if lbl in perf:
                v = perf[lbl]
                c = '#059669' if v >= 0 else '#dc2626'
                perf_items.append(f'<span style="font-weight:600; font-size:0.72rem;">{lbl}</span> <span style="color:{c}; font-weight:700; font-size:0.75rem;">{v:+.1f}%</span>')
        if '52w_high' in perf:
            perf_items.append(f'<span style="font-weight:600; font-size:0.72rem;">52W</span> <span style="color:#64748b; font-size:0.72rem;">{cs}{perf["52w_low"]:.0f}&ndash;{cs}{perf["52w_high"]:.0f}</span>')
        st.markdown(
            '<div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:6px 14px; margin:6px 0; display:flex; gap:20px; align-items:center;">'
            + '  '.join(perf_items) +
            '</div>',
            unsafe_allow_html=True
        )

# ===== TAB 2: QUANTITATIVE QUADRANT =====
with t2:
    st.markdown("### The 2026 Efficiency Filter")
    st.caption("Beyond simple revenue growth — capital efficiency, unit economics, and earnings momentum.")

    # ===========================================================================
    # 3 MASTER FORWARD-LOOKING INDICATORS (prominent section)
    # ===========================================================================
    fwd_r40 = quant['forward_rule_of_40']
    rpo_data = quant['rpo']

    st.markdown("---")
    st.markdown("####  3 Master Forward-Looking Indicators")
    st.caption('"The market prices stocks on future cash flows. These indicators reveal what is coming before the market notices."')

    fi1, fi2, fi3 = st.columns(3)

    # ---- RPO Indicator ----
    rpo_signal = rpo_data.get('leading_indicator_signal')
    rpo_growth = rpo_data.get('rpo_growth_pct')
    if rpo_signal == 'STRONG LEAD': rpo_color = '#0d8a3e'; rpo_bg = '#c8f7d5'
    elif rpo_signal == 'LAGGING': rpo_color = '#c62828'; rpo_bg = '#ffcdd2'
    elif rpo_signal == 'MODEST LEAD': rpo_color = '#1a3a6b'; rpo_bg = '#d0dff7'
    else: rpo_color = '#6a1b9a'; rpo_bg = '#e1bee7'
    rev_growth_pct = rpo_data.get('revenue_growth_pct')
    rpo_icon = '' if rpo_signal == 'STRONG LEAD' else ('' if rpo_signal == 'LAGGING' else '')
    rpo_sig_str = rpo_signal if rpo_signal else 'N/A'

    with fi1:
        st.markdown(
            '<div class="kpi" style="border-left:5px solid ' + rpo_color + '; padding:16px 18px; min-height:220px;">'
            '<div style="display:flex; align-items:center; gap:8px; margin-bottom:10px;">'
            '<span style="font-size:1.4rem;">' + rpo_icon + '</span>'
            '<span class="kpi-label" style="margin:0;">Remaining Performance Obligations</span>'
            '</div>'
            '<div style="display:flex; align-items:baseline; gap:10px; margin-bottom:6px;">'
            '<span class="kpi-value" style="color:' + rpo_color + ';">' + fmt_pct(rpo_growth) + '</span>'
            '<span style="font-size:0.7rem; color:#888; font-weight:600;">RPO Growth</span>'
            '</div>'
            '<div style="display:flex; align-items:baseline; gap:10px; margin-bottom:10px;">'
            '<span style="font-size:1rem; font-weight:700; color:#444;">' + fmt_pct(rev_growth_pct) + '</span>'
            '<span style="font-size:0.68rem; color:#888;">vs Revenue Growth</span>'
            '</div>'
            '<span style="background:' + rpo_bg + '; color:' + rpo_color + '; padding:4px 12px; border-radius:14px; font-size:0.7rem; font-weight:700;">'
            + rpo_icon + ' ' + rpo_sig_str +
            '</span>'
            '<div style="font-size:0.65rem; color:#999; margin-top:8px;">RPO &gt; Revenue = acceleration ahead</div>'
            '</div>',
            unsafe_allow_html=True
        )
        if rpo_data.get('signal_detail'):
            st.caption(rpo_data['signal_detail'])

    # ---- NRR Indicator ----
    nrr_growth = nrr.get('estimated_nrr_pct')
    if nrr_growth is not None and nrr_growth >= 120: nrr_color = '#0d8a3e'; nrr_bg = '#c8f7d5'; nrr_icon = ''
    elif nrr_growth is not None and nrr_growth >= 106: nrr_color = '#1a3a6b'; nrr_bg = '#d0dff7'; nrr_icon = ''
    elif nrr_growth is not None and nrr_growth >= 100: nrr_color = '#e65100'; nrr_bg = '#ffe0b2'; nrr_icon = ''
    else: nrr_color = '#c62828'; nrr_bg = '#ffcdd2'; nrr_icon = ''
    nrr_val = f'{nrr_growth:.0f}%' if nrr_growth is not None else 'N/A'
    if nrr_growth is not None and nrr_growth >= 100:
        nrr_impact = f'Grows {nrr_growth - 100:.0f}% with zero new customers'
    else:
        nrr_impact = 'Existing base is shrinking'

    with fi2:
        st.markdown(
            '<div class="kpi" style="border-left:5px solid ' + nrr_color + '; padding:16px 18px; min-height:220px;">'
            '<div style="display:flex; align-items:center; gap:8px; margin-bottom:10px;">'
            '<span style="font-size:1.4rem;">' + nrr_icon + '</span>'
            '<span class="kpi-label" style="margin:0;">Net Retention Rate</span>'
            '</div>'
            '<div style="display:flex; align-items:baseline; gap:10px; margin-bottom:6px;">'
            '<span class="kpi-value" style="color:' + nrr_color + ';">' + nrr_val + '</span>'
            '<span style="font-size:0.7rem; color:#888; font-weight:600;">NRR</span>'
            '</div>'
            '<div style="margin-bottom:10px;">'
            '<span style="background:' + nrr_bg + '; color:' + nrr_color + '; padding:4px 12px; border-radius:14px; font-size:0.7rem; font-weight:700;">'
            + nrr_icon + ' ' + (nrr.get('assessment', 'N/A')[:30] if nrr.get('assessment') else 'N/A') +
            '</span>'
            '</div>'
            '<div style="font-size:0.68rem; color:#555; font-weight:600; line-height:1.4;">' + nrr_impact + '</div>'
            '<div style="font-size:0.63rem; color:#999; margin-top:6px;">Benchmark &ge;106% | Installed growth &ge;120%</div>'
            '</div>',
            unsafe_allow_html=True
        )

    # ---- Forward Rule of 40 Indicator ----
    fwd_r40_val = fwd_r40.get('forward_rule_40')
    trail_r40_val = fwd_r40.get('trailing_rule_40')
    inflection = fwd_r40.get('inflection_signal', '')
    if inflection in ('MASSIVE INFLECTION', 'POSITIVE INFLECTION', 'BENCHMARK CROSSOVER'):
        fwd_color = '#0d8a3e'; fwd_bg = '#c8f7d5'; fwd_icon = ''
    elif inflection in ('NEGATIVE INFLECTION', 'SEVERE DECLINE'):
        fwd_color = '#c62828'; fwd_bg = '#ffcdd2'; fwd_icon = ''
    elif inflection == 'TRAILING ONLY':
        fwd_color = '#6a1b9a'; fwd_bg = '#e1bee7'; fwd_icon = ''
    else:
        fwd_color = '#1a3a6b'; fwd_bg = '#d0dff7'; fwd_icon = ''
    fwd_val = f'{fwd_r40_val:.0f}' if fwd_r40_val is not None else 'N/A'
    if trail_r40_val is not None and fwd_r40_val is not None:
        gap = fwd_r40_val - trail_r40_val
        fwd_subtitle = ('+' if gap > 0 else '') + f'{gap:.0f} vs trailing'
    else:
        fwd_subtitle = ''

    with fi3:
        st.markdown(
            '<div class="kpi" style="border-left:5px solid ' + fwd_color + '; padding:16px 18px; min-height:220px;">'
            '<div style="display:flex; align-items:center; gap:8px; margin-bottom:10px;">'
            '<span style="font-size:1.4rem;">' + fwd_icon + '</span>'
            '<span class="kpi-label" style="margin:0;">Forward Rule of 40</span>'
            '</div>'
            '<div style="display:flex; align-items:baseline; gap:10px; margin-bottom:4px;">'
            '<span class="kpi-value" style="color:' + fwd_color + ';">' + fwd_val + '</span>'
            '<span style="font-size:0.7rem; color:#888; font-weight:600;">Forward R40</span>'
            '</div>'
            + ('<div style="font-size:0.8rem; font-weight:700; color:#555; margin-bottom:8px;">' + fwd_subtitle + '</div>' if fwd_subtitle else '') +
            '<div style="margin-bottom:10px;">'
            '<span style="background:' + fwd_bg + '; color:' + fwd_color + '; padding:4px 12px; border-radius:14px; font-size:0.7rem; font-weight:700;">'
            + fwd_icon + ' ' + (inflection if inflection else 'N/A') +
            '</span>'
            '</div>'
            '<div style="font-size:0.68rem; color:#555; font-weight:600; line-height:1.4;">Fwd Rev: ' + fmt_pct(fwd_r40.get('forward_rev_growth_pct')) +
            ' | FCF Mgn: ' + fmt_pct(fwd_r40.get('forward_fcf_margin_pct')) + '</div>'
            '<div style="font-size:0.63rem; color:#999; margin-top:6px;">Trailing &lt;40 + Forward &ge;40 = buy signal</div>'
            '</div>',
            unsafe_allow_html=True
        )

    # Show the "why this matters" logic
    with st.expander("  Why These Matter — The Forward-Looking Logic"):
        st.markdown("""
        **The market prices stocks on future cash flows, not past ones.** These three indicators bridge the gap between reported financials and what's actually coming:

        | Indicator | What It Reveals | Key Signal |
        |---|---|---|
        | **RPO** (Remaining Performance Obligations) | Revenue already contracted but not yet recognized on the income statement | RPO growth > Revenue growth = revenue about to **accelerate** |
        | **NRR** (Net Retention Rate) | Whether existing customers are expanding or shrinking — the 'installed growth' | NRR > 120% = business grows 20%+ even with **zero new customers** |
        | **Forward Rule of 40** | What the Rule of 40 looks like using **next year's estimates** | Trailing < 40 but Forward ≥ 40 = **inflection point** to buy before the market notices |

        **How to use them together:**
        - Strong RPO + High NRR + Forward R40 crossing 40 = the trifecta — maximum conviction
        - Weak RPO + Low NRR + Forward R40 declining = thesis is breaking — consider exiting even if trailing numbers look OK
        - Mixed signals = dig deeper into the specifics of the business model
        """)

    st.markdown("---")
    st.markdown("#### Core Metrics & Momentum")
    r40_ebitda = r40.get('rule_40_ebitda')
    r40_fcf = r40.get('rule_40_fcf')
    r40_assess = r40.get('assessment', 'N/A')
    arr_growth = arr.get('estimated_arr_growth_pct')
    nrr_pct = nrr.get('estimated_nrr_pct')
    gm_pct = gm_data.get('gross_margin_pct')
    mom_score = momentum.get('momentum_score', 0)
    mom_rank = momentum.get('rank_label', 'N/A')
    mom_signals = ', '.join(momentum.get('signals', [])[:3])

    core_rows = [
        '<tr><td>Rule of 40 (EBITDA)</td><td>' + (f'{r40_ebitda:.0f}' if r40_ebitda is not None else 'N/A') + '</td><td>Rule of 40 (FCF)</td><td>' + (f'{r40_fcf:.0f}' if r40_fcf is not None else 'N/A') + '</td></tr>',
        '<tr><td>Gross Margin</td><td>' + fmt_pct(gm_pct) + '</td><td>ARR Growth</td><td>' + fmt_pct(arr_growth) + '</td></tr>',
        '<tr><td>Est. NRR</td><td>' + fmt_pct(nrr_pct) + '</td><td>Momentum</td><td>' + mom_rank + ' (' + f'{mom_score:+.0f}' + ')</td></tr>',
        '<tr><td colspan="4" style="font-size:0.65rem; color:#64748b;">' + r40_assess + ' | ' + mom_signals + '</td></tr>',
    ]
    core_table = (
        '<table style="width:100%; border-collapse:collapse; font-family:Inter,sans-serif; font-size:0.72rem; margin:8px 0;">'
        '<colgroup><col style="width:22%"><col style="width:28%"><col style="width:22%"><col style="width:28%"></colgroup>'
        '<thead><tr style="border-bottom:2px solid #e2e8f0;">'
        '<th style="padding:4px 10px; font-size:0.62rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.06em; text-align:left;">Metric</th>'
        '<th style="padding:4px 10px; font-size:0.62rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.06em; text-align:left;">Value</th>'
        '<th style="padding:4px 10px; font-size:0.62rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.06em; text-align:left;">Metric</th>'
        '<th style="padding:4px 10px; font-size:0.62rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.06em; text-align:left;">Value</th>'
        '</tr></thead><tbody>' + '\n'.join(core_rows) + '</tbody></table>'
    )
    st.markdown(core_table, unsafe_allow_html=True)

    # ---- NoB-Specific Filter ----
    st.markdown("---")
    st.markdown(f"#### {nob['name']}-Specific Metrics")
    st.caption({
        'saas_cloud': 'SaaS & Cloud companies are evaluated on efficiency, unit economics, and retention velocity.',
        'ai_infra_industrial': 'Industrial/AI Infra companies are evaluated on throughput, backlog conversion, and revision-led EPS.',
        'biopharma_life_sciences': 'Biopharma companies are evaluated on milestone alpha — rNPV, clinical stage, and AI-enabled reduced attrition.',
        'general': 'General companies are evaluated on the full dual-quadrant framework.',
    }.get(nob_type, ''))

    if nob_type == 'high_growth_saas':
        saas = quant.get('saas_filter', {})
        sb1, sb2, sb3 = st.columns(3)
        with sb1:
            ltv = saas.get('ltv_cac_ratio')
            ltv_color = "#16a34a" if (ltv and ltv >= 5) else ("#16a34a" if (ltv and ltv >= 3) else "#dc2626")
            st.markdown(metric_card("LTV:CAC Ratio", f"{ltv}:1" if ltv else "N/A", sub=str(saas.get('ltv_cac_assessment', ''))[:40], color=ltv_color), unsafe_allow_html=True)
        with sb2:
            cac = saas.get('cac_payback_months')
            cac_color = "#16a34a" if (cac and cac <= 12) else ("#ea580c" if (cac and cac <= 18) else "#dc2626")
            st.markdown(metric_card("CAC Payback", f"{cac:.0f} mo" if cac else "N/A", sub=str(saas.get('cac_payback_assessment', ''))[:40], color=cac_color), unsafe_allow_html=True)
        with sb3:
            r40_fcf_saas = saas.get('rule_40_fcf')
            st.markdown(metric_card("Rule of 40 (FCF)", f"{r40_fcf_saas:.0f}" if r40_fcf_saas else "N/A", sub=saas.get('rule_40_assessment', ''), color="#16a34a" if (r40_fcf_saas and r40_fcf_saas >= 40) else "#ea580c"), unsafe_allow_html=True)
        st.caption("**SaaS Benchmarks:** R40(FCF) &ge;40 | LTV:CAC &ge;3:1 | CAC Payback &le;12mo | NRR >106% | Gross Margin &ge;75%")
        if saas.get('ltv_cac_assessment') and '5:1' in str(saas.get('ltv_cac_assessment')):
            st.warning("LTV:CAC >5:1 may indicate under-investment in growth.")

    elif nob_type == 'ai_infra_semiconductor':
        ind = quant.get('industrial_filter', {})
        rev = ind.get('revision_led_eps', {})
        ib1, ib2, ib3 = st.columns(3)
        with ib1:
            backlog = ind.get('backlog_growth_pct')
            bk_color = "#16a34a" if (backlog and backlog > 50) else ("#ea580c" if (backlog and backlog > 20) else "#dc2626")
            st.markdown(metric_card("Backlog Growth", f"{backlog:.0f}%" if backlog else "N/A", sub=str(ind.get('backlog_assessment', ''))[:40] if ind.get('backlog_assessment') else None, color=bk_color), unsafe_allow_html=True)
        with ib2:
            conv = ind.get('conversion_velocity')
            st.markdown(metric_card("Conv. Velocity", f"{conv:.2f}x" if conv else "N/A", sub=ind.get('conversion_assessment', ''), color="#16a34a" if (conv and 0.8 <= conv <= 1.2) else "#ea580c"), unsafe_allow_html=True)
        with ib3:
            st.markdown(metric_card("EPS Revision", rev.get('rank', 'N/A'), sub="Revision-led" if rev.get('is_revision_led') else "", color="#16a34a" if rev.get('is_revision_led') else "#ea580c"), unsafe_allow_html=True)
        st.caption("**Semiconductor Benchmarks:** Backlog >20% YoY | Conv. Velocity 0.8-1.2x | Zacks #1 (Strong Buy)")
        if rev.get('signals'):
            for sig in rev['signals'][:3]:
                st.markdown(f"<small> {sig}</small>", unsafe_allow_html=True)

    elif nob_type == 'energy_industrial':
        ind = quant.get('industrial_filter', {})
        ib1, ib2, ib3 = st.columns(3)
        with ib1:
            backlog = ind.get('backlog_growth_pct')
            bk_color = "#16a34a" if (backlog and backlog > 50) else ("#ea580c" if (backlog and backlog > 20) else "#dc2626")
            st.markdown(metric_card("Backlog Growth", f"{backlog:.0f}%" if backlog else "N/A", color=bk_color), unsafe_allow_html=True)
        with ib2:
            st.markdown(metric_card("Revenue Growth", f"{ind.get('revenue_growth_pct', 0):.0f}%" if ind.get('revenue_growth_pct') else "N/A"), unsafe_allow_html=True)
        with ib3:
            st.markdown(metric_card("Power Pipeline", "GW scale" if ind.get('power_pipeline_note') else "N/A"), unsafe_allow_html=True)
        if ind.get('power_pipeline_note'):
            st.info(ind['power_pipeline_note'])

    elif nob_type == 'biopharma':
        bio = quant.get('biopharma_filter', {})
        bb1, bb2, bb3 = st.columns(3)
        with bb1:
            st.markdown(metric_card("Clinical Stage", bio.get('clinical_stage', 'Unknown'), color="#8b5cf6"), unsafe_allow_html=True)
        with bb2:
            dr = bio.get('discount_rate_pct')
            st.markdown(metric_card("rNPV Disc. Rate", f"{dr:.0f}%" if dr else "N/A", sub="Probability-weighted", color="#ea580c" if (dr and dr > 25) else "#16a34a"), unsafe_allow_html=True)
        with bb3:
            ai_prem = bio.get('ai_attrition_premium', False)
            st.markdown(metric_card("AI Attrition Premium", "YES" if ai_prem else "No", sub="Reduced trial failure risk" if ai_prem else "Standard attrition", color="#16a34a" if ai_prem else "#6b7280"), unsafe_allow_html=True)
        st.caption("**Biopharma Benchmarks:** rNPV | Discount: 40% preclinical &rarr; 15% Phase 3 | AI-enabled = higher success rates")
        if bio.get('rnpv_note'):
            st.info(bio['rnpv_note'])

    elif nob_type == 'traditional_value':
        val = quant.get('value_filter', {})
        vb1, vb2, vb3 = st.columns(3)
        with vb1:
            tpe = val.get('trailing_pe')
            st.markdown(metric_card("Trailing P/E", f"{tpe:.1f}x" if tpe and tpe > 0 else "N/A", sub="<15 = value" if tpe and 0 < tpe < 15 else "", color="#16a34a" if (tpe and 0 < tpe < 15) else "#ea580c"), unsafe_allow_html=True)
        with vb2:
            pb = val.get('price_to_book')
            st.markdown(metric_card("Price/Book", f"{pb:.2f}x" if pb is not None else "N/A", sub="<1.5 = good value" if pb and pb < 1.5 else "", color="#16a34a" if (pb and pb < 1.5) else "#ea580c"), unsafe_allow_html=True)
        with vb3:
            div = val.get('dividend_yield_pct')
            st.markdown(metric_card("Dividend Yield", f"{div:.1f}%" if div is not None else "N/A", sub=">3% attractive" if div and div > 3 else "", color="#16a34a" if (div and div > 3) else "#ea580c"), unsafe_allow_html=True)
        st.caption(f"**Value Score: {val.get('value_score', 'N/A')}/10** — {val.get('value_label', '')}")
        st.caption("**Value Benchmarks:** P/E <15x | P/B <1.5x | Dividend >3% | D/E <50x")
        if val.get('signals'):
            with st.expander("Value Signals"):
                for s in val['signals']:
                    st.markdown(f"<small>+ {s}</small>", unsafe_allow_html=True)
        if val.get('concerns'):
            with st.expander("Concerns"):
                for c in val['concerns']:
                    st.markdown(f"<small>- {c}</small>", unsafe_allow_html=True)

    elif nob_type == 'high_growth_general':
        gf = quant.get('growth_filter', {})
        gb1, gb2, gb3 = st.columns(3)
        with gb1:
            st.markdown(metric_card("Revenue Growth", f"{gf.get('revenue_growth_pct', 0):.0f}%" if gf.get('revenue_growth_pct') is not None else "N/A", color="#16a34a" if (gf.get('revenue_growth_pct') and gf['revenue_growth_pct'] > 20) else "#ea580c"), unsafe_allow_html=True)
        with gb2:
            runway = gf.get('cash_runway_years')
            st.markdown(metric_card("Cash Runway", f"{runway:.0f} yrs" if runway is not None else "N/A", sub=">3yrs = ample" if runway and runway > 3 else "", color="#16a34a" if (runway and runway > 3) else "#dc2626"), unsafe_allow_html=True)
        with gb3:
            st.markdown(metric_card("Growth Score", f"{gf.get('growth_score', 'N/A')}/10", sub="Decelerating" if gf.get('growth_decelerating') else "Stable", color="#16a34a" if not gf.get('growth_decelerating') else "#ea580c"), unsafe_allow_html=True)
        if gf.get('signals'):
            for s in gf['signals']:
                st.markdown(f"<small>+ {s}</small>", unsafe_allow_html=True)
        if gf.get('concerns'):
            for c in gf['concerns']:
                st.markdown(f"<small>- {c}</small>", unsafe_allow_html=True)

    else:
        st.info("Cross-model analysis — key metrics span efficiency, moat strength, and thematic alignment.")

# ===== TAB 3: QUALITATIVE MOAT =====
with t3:
    st.markdown("### Technical Moat Architecture")

    circumvention = moat.get('circumvention_delta', 0)
    circumvention_pct = moat.get('circumvention_delta_pct', 0)
    cd_formula = moat.get('circumvention_delta_formula', '')
    cd_color = "#059669" if circumvention >= 9 else ("#ea580c" if circumvention >= 6 else "#dc2626")
    perf = qual.get('moat_performance', {})
    perf_signal = perf.get('performance', 'N/A')
    perf_color = perf.get('performance_color', '#6b7280')
    temporal = moat['temporal_width']
    efficiency = moat['efficiency_width']
    trust = moat['trust_width']
    ai_depth = qual.get('ai_integration_depth', 0)
    ai_depth_labels = {3: 'Deep — AI Infra', 2: 'Significant — AI Models', 1: 'Moderate — AI Apps', 0: 'Limited'}
    ai_color = "#8b5cf6" if ai_depth >= 3 else ("#3b82f6" if ai_depth >= 2 else ("#10b981" if ai_depth >= 1 else "#94a3b8"))

    # Moat summary row
    moat_summary = (
        '<div style="display:flex; gap:16px; align-items:center; margin:8px 0;">'
        '<span style="font-weight:700; font-size:1rem; color:' + moat['moat_color'] + ';">Moat ' + str(moat_val) + '/10</span>'
        '<span style="font-size:0.72rem; color:#64748b;">' + moat['moat_label'] + '</span>'
        '<span style="font-size:0.68rem; color:#94a3b8;">|</span>'
        '<span style="font-weight:600; font-size:0.72rem; color:' + cd_color + ';">Circ.Delta ' + str(circumvention) + '/13</span>'
        '<span style="font-size:0.68rem; color:#94a3b8;">|</span>'
        '<span style="font-weight:600; font-size:0.72rem; color:' + perf_color + ';">' + perf_signal + '</span>'
        '<span style="font-size:0.68rem; color:#94a3b8;">|</span>'
        '<span style="font-weight:600; font-size:0.72rem; color:' + ai_color + ';">AI: ' + ai_depth_labels.get(ai_depth, 'None') + '</span>'
        '</div>'
    )
    st.markdown(moat_summary, unsafe_allow_html=True)

    # Compact moat dimensions table
    t_c = "#059669" if temporal['score'] >= 4 else ("#ea580c" if temporal['score'] >= 3 else "#dc2626")
    e_c = "#059669" if efficiency['score'] >= 5 else ("#ea580c" if efficiency['score'] >= 3 else "#dc2626")
    tr_c = "#059669" if trust['score'] >= 4 else ("#ea580c" if trust['score'] >= 3 else "#dc2626")
    moat_table = (
        '<table style="width:100%; border-collapse:collapse; font-family:Inter,sans-serif; font-size:0.7rem; margin:6px 0;">'
        '<colgroup><col style="width:20%"><col style="width:8%"><col style="width:39%"><col style="width:33%"></colgroup>'
        '<thead><tr style="border-bottom:2px solid #e2e8f0;">'
        '<th style="padding:3px 8px; font-size:0.6rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.05em; text-align:left;">Dimension</th>'
        '<th style="padding:3px 8px; font-size:0.6rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.05em; text-align:center;">Score</th>'
        '<th style="padding:3px 8px; font-size:0.6rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.05em; text-align:left;">Assessment</th>'
        '<th style="padding:3px 8px; font-size:0.6rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.05em; text-align:left;">Signals</th>'
        '</tr></thead><tbody>'
        '<tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:3px 8px; font-weight:600;">Temporal Width</td>'
        '<td style="padding:3px 8px; text-align:center; font-weight:700; color:' + t_c + ';">' + str(temporal['score']) + '/5</td>'
        '<td style="padding:3px 8px; font-size:0.65rem;">' + temporal['rating'] + '</td>'
        '<td style="padding:3px 8px; font-size:0.63rem; color:#64748b;">' + ', '.join(temporal.get('signals', [])[:2]) + '</td></tr>'
        '<tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:3px 8px; font-weight:600;">Efficiency Width</td>'
        '<td style="padding:3px 8px; text-align:center; font-weight:700; color:' + e_c + ';">' + str(efficiency['score']) + '/5</td>'
        '<td style="padding:3px 8px; font-size:0.65rem;">' + efficiency['rating'] + '</td>'
        '<td style="padding:3px 8px; font-size:0.63rem; color:#64748b;">' + ', '.join(efficiency.get('signals', [])[:2]) + '</td></tr>'
        '<tr><td style="padding:3px 8px; font-weight:600;">Trust Width</td>'
        '<td style="padding:3px 8px; text-align:center; font-weight:700; color:' + tr_c + ';">' + str(trust['score']) + '/5</td>'
        '<td style="padding:3px 8px; font-size:0.65rem;">' + trust['rating'] + '</td>'
        '<td style="padding:3px 8px; font-size:0.63rem; color:#64748b;">' + ', '.join(trust.get('signals', [])[:2]) + '</td></tr>'
        '</tbody></table>'
    )
    st.markdown(moat_table, unsafe_allow_html=True)
    st.caption('Circumvention Delta = ' + cd_formula + ' | ' + moat.get('benchmark', '') + ' | ' + moat.get('wide_moat_annual_return', ''))

    # Moat signals expander
    if perf.get('compound_signals') or perf.get('decay_signals'):
        with st.expander("Moat Signal Details"):
            if perf.get('compound_signals'):
                for s in perf['compound_signals']:
                    st.markdown('<small style="color:#059669;">+ ' + s + '</small>', unsafe_allow_html=True)
            if perf.get('decay_signals'):
                for s in perf['decay_signals']:
                    st.markdown('<small style="color:#dc2626;">- ' + s + '</small>', unsafe_allow_html=True)

# ===== TAB 4: 2026 THEMES =====
with t4:
    st.markdown("### 2026 Investment Themes")
    st.caption("Thematic classification based on the 2026 Chief Strategist framework. Scores reflect keyword density, sector alignment, and direct top-pick status.")

    # Primary theme highlight
    primary_key = thematic.get('primary_theme')
    if primary_key and primary_key in THEMES_2026:
        theme = THEMES_2026[primary_key]
        st.markdown(f"""
        <div class="verdict conviction-high">
            <b>Primary Theme: {theme['name']}</b> — Conviction Score: {thematic.get('primary_conviction', 0)}/10<br>
            <small>{theme['description']}</small><br>
            <small><b>Catalyst:</b> {thematic.get('primary_catalyst', theme['catalyst'])}</small><br>
            <small><b>Target P/E Range:</b> {thematic.get('primary_pe_target', theme['forward_pe_target'])}</small>
        </div>
        """, unsafe_allow_html=True)

    # All theme scores
    st.markdown("#### Theme Alignment Scores")
    all_scores = thematic.get('all_scores', {})
    if all_scores:
        theme_rows = []
        for key, score in sorted(all_scores.items(), key=lambda x: x[1], reverse=True):
            t = THEMES_2026.get(key, {})
            theme_rows.append({
                'Theme': t.get('name', key),
                'Score': f"{score}/10",
                'Description': t.get('description', ''),
                'Top Picks': ', '.join(t.get('top_picks', [])[:5]),
            })
        st.dataframe(pd.DataFrame(theme_rows), width='stretch', hide_index=True,
                     column_config={
                         'Theme': st.column_config.TextColumn(width='medium'),
                         'Score': st.column_config.TextColumn(width='small'),
                         'Description': st.column_config.TextColumn(width='large'),
                         'Top Picks': st.column_config.TextColumn(width='medium'),
                     })

    # Secondary themes
    secondary = thematic.get('secondary_themes', [])
    if secondary:
        st.markdown("#### Secondary Theme Exposure")
        for s in secondary:
            st.markdown(f'<div style="margin:4px 0;"><span class="tag blue">{s["name"]}</span> <small>Score: {s["score"]}/10</small></div>', unsafe_allow_html=True)

    # Theme keyword matches
    st.markdown("---")
    st.markdown("#### Keyword Match Detail")
    all_matches = thematic.get('all_matches', {})
    if all_matches:
        for theme_key, matches in all_matches.items():
            if matches:
                theme_name = THEMES_2026.get(theme_key, {}).get('name', theme_key)
                st.markdown(f'<small><b>{theme_name}:</b> {", ".join(matches[:5])}</small>', unsafe_allow_html=True)

    # 2026 Market Context
    st.markdown("---")
    st.markdown("#### 2026 Macro Context")
    mc1, mc2, mc3, mc4 = st.columns(4)
    with mc1:
        st.metric("S&P 500 Target", "7,500-7,800", "~12-14% from early 2026")
    with mc2:
        st.metric("US GDP Growth", "2.6%", "Leads developed markets")
    with mc3:
        st.metric("Trailing P/E", "~26x", "Historically elevated")
    with mc4:
        st.metric("Shiller CAPE", "~39", "Among highest on record")

    # "K-shaped" economy context
    st.markdown("---")
    st.markdown("#### The 'K-Shaped' Economy & 2026 Style Rotation")
    kc1, kc2 = st.columns(2)
    with kc1:
        st.warning("""
        **'K-Shaped' Divergence:**
        - Higher-income spending remains resilient
        - Total job creation outside healthcare turns **negative** for first time in 25 years
        - Consumer staples & energy leading as technology names falter
        - "Real economy" stocks gaining favor over narrative-driven growth
        """)
    with kc2:
        st.info("""
        **Style Rotation (Early 2026):**
        - Value stocks outperformed growth by **11%+** in opening weeks
        - Valuation discipline regaining prominence
        - Investors' tolerance for earnings misses is **declining**
        - "Barbell" construction: balance high-growth AI infra + quality value/energy
        """)

# ===== TAB 5: RISK MANAGEMENT =====
with t5:
    st.markdown("### 2026 Risk Management")

    position = risk_mgmt['position_sizing']
    ms = risk_mgmt['mental_stop_loss']
    max_pos = risk_factors.get('max_suggested_position', 10)
    rs = risk_factors.get('risk_score', 0)
    urgency = position['urgency']
    u_color = "#dc2626" if urgency == 'High' else ("#ea580c" if urgency == 'Medium' else "#059669")

    # Compact risk summary table
    risk_rows = [
        '<tr><td style="font-weight:600;">Risk Level</td><td style="font-weight:700; color:' + ('#059669' if risk_level == 'Low' else ('#ea580c' if risk_level == 'Medium' else '#dc2626')) + ';">' + risk_level + '</td><td style="font-weight:600;">Risk Score</td><td>' + str(rs) + '/10</td></tr>',
        '<tr><td style="font-weight:600;">Max Position</td><td style="font-weight:700;">' + str(max_pos) + '% NAV</td><td style="font-weight:600;">Current</td><td>' + str(position['current_weight_pct']) + '%</td></tr>',
        '<tr><td style="font-weight:600;">Position Status</td><td style="font-weight:600; color:' + u_color + ';">' + position['action'] + '</td><td style="font-weight:600;">Stop-Loss</td><td style="font-size:0.65rem;">' + ms['thesis_break_threshold'][:80] + '</td></tr>',
    ]
    risk_table = (
        '<table style="width:100%; border-collapse:collapse; font-family:Inter,sans-serif; font-size:0.7rem; margin:6px 0;">'
        '<colgroup><col style="width:16%"><col style="width:34%"><col style="width:16%"><col style="width:34%"></colgroup>'
        '<thead><tr style="border-bottom:2px solid #e2e8f0;">'
        '<th style="padding:3px 8px; font-size:0.6rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.05em; text-align:left;">Parameter</th>'
        '<th style="padding:3px 8px; font-size:0.6rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.05em; text-align:left;">Value</th>'
        '<th style="padding:3px 8px; font-size:0.6rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.05em; text-align:left;">Parameter</th>'
        '<th style="padding:3px 8px; font-size:0.6rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.05em; text-align:left;">Value</th>'
        '</tr></thead><tbody>' + '\n'.join(risk_rows) + '</tbody></table>'
    )
    st.markdown(risk_table, unsafe_allow_html=True)

    # Risk factors as compact table
    risk_factor_rows = []
    for rf in risk_factors.get('risks', []):
        sev = rf.get('severity', 'Low')
        sev_c = {'High': '#dc2626', 'Medium': '#ea580c', 'Low': '#059669'}.get(sev, '#6b7280')
        risk_factor_rows.append(
            '<tr><td style="font-weight:600;">' + rf['factor'] + '</td>'
            '<td><span style="font-size:0.6rem; font-weight:600; color:' + sev_c + ';">' + sev + '</span></td>'
            '<td style="font-size:0.65rem;">' + rf['detail'] + '</td>'
            '<td style="font-size:0.63rem; color:#64748b;">' + rf['mitigation'] + '</td></tr>'
        )
    risk_factors_table = (
        '<table style="width:100%; border-collapse:collapse; font-family:Inter,sans-serif; font-size:0.7rem; margin:6px 0;">'
        '<colgroup><col style="width:18%"><col style="width:8%"><col style="width:38%"><col style="width:36%"></colgroup>'
        '<thead><tr style="border-bottom:2px solid #e2e8f0;">'
        '<th style="padding:3px 8px; font-size:0.6rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.05em; text-align:left;">Risk Factor</th>'
        '<th style="padding:3px 8px; font-size:0.6rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.05em; text-align:left;">Sev</th>'
        '<th style="padding:3px 8px; font-size:0.6rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.05em; text-align:left;">Detail</th>'
        '<th style="padding:3px 8px; font-size:0.6rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.05em; text-align:left;">Mitigation</th>'
        '</tr></thead><tbody>' + '\n'.join(risk_factor_rows) + '</tbody></table>'
    )
    st.markdown(risk_factors_table, unsafe_allow_html=True)

    # Framework thresholds expander
    with st.expander("Framework Stop-Loss Thresholds"):
        for t, th in {'AAPL': 'Exit if iPhone unit growth turns negative 2 quarters', 'AMZN': 'Exit if AWS growth <14%', 'MSFT': 'Exit if Azure growth <28%', 'NVDA': 'Exit if data center growth <50%'}.items():
            st.markdown('<small><b>' + t + ':</b> ' + th + '</small>', unsafe_allow_html=True)

    # Barbell + Portfolio compact
    barbell = risk_mgmt['barbell_check']
    segments = barbell.get('segments', {})
    info = data['info']
    fwd_pe = info.get('forwardPE'); tpe = info.get('trailingPE')
    ps = info.get('priceToSales'); ev_ebitda = info.get('enterpriseToEbitda')
    fcf_val = info.get('freeCashflow'); mcap_val = info.get('marketCap')
    fcf_yield_val = (fcf_val / mcap_val * 100) if (fcf_val and mcap_val and mcap_val > 0) else None

    barbell_portfolio_table = (
        '<table style="width:100%; border-collapse:collapse; font-family:Inter,sans-serif; font-size:0.7rem; margin:6px 0;">'
        '<colgroup><col style="width:18%"><col style="width:32%"><col style="width:18%"><col style="width:32%"></colgroup>'
        '<thead><tr style="border-bottom:2px solid #e2e8f0;">'
        '<th style="padding:3px 8px; font-size:0.6rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.05em; text-align:left;">Barbell</th>'
        '<th style="padding:3px 8px; font-size:0.6rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.05em; text-align:left;">Allocation</th>'
        '<th style="padding:3px 8px; font-size:0.6rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.05em; text-align:left;">Valuation</th>'
        '<th style="padding:3px 8px; font-size:0.6rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.05em; text-align:left;">Value</th>'
        '</tr></thead><tbody>'
        '<tr><td>High-Growth</td><td>' + str(segments.get('high_growth_pct', 0)) + '%</td>'
        '<td>Forward P/E</td><td style="font-weight:600;">' + (f'{fwd_pe:.1f}x' if fwd_pe and fwd_pe > 0 else 'N/A') + '</td></tr>'
        '<tr><td>Quality Value</td><td>' + str(segments.get('quality_value_pct', 0)) + '%</td>'
        '<td>Trailing P/E</td><td style="font-weight:600;">' + (f'{tpe:.1f}x' if tpe and tpe > 0 else 'N/A') + '</td></tr>'
        '<tr><td>Other</td><td>' + str(segments.get('other_pct', 0)) + '%</td>'
        '<td>FCF Yield</td><td style="font-weight:600;">' + (f'{fcf_yield_val:.1f}%' if fcf_yield_val is not None else 'N/A') + '</td></tr>'
        '<tr><td colspan="2" style="font-size:0.63rem; color:#64748b;">' + barbell.get('message', '') + '</td>'
        '<td>P/S</td><td>' + (f'{ps:.1f}x' if ps else 'N/A') + '</td></tr>'
        '</tbody></table>'
    )
    st.markdown(barbell_portfolio_table, unsafe_allow_html=True)

# ===== TAB 6: PORTFOLIO CONTEXT =====
with t6:
    st.markdown("### Portfolio Strategy")

    # Portfolio recommendations table
    port_rows = []
    for p in portfolio:
        port_rows.append('<tr><td style="font-weight:600;">' + p['rule'] + '</td><td>' + p['recommendation'] + '</td><td style="font-size:0.65rem; color:#64748b;">' + p['detail'] + '</td></tr>')
    port_table = (
        '<table style="width:100%; border-collapse:collapse; font-family:Inter,sans-serif; font-size:0.7rem; margin:6px 0;">'
        '<colgroup><col style="width:16%"><col style="width:44%"><col style="width:40%"></colgroup>'
        '<thead><tr style="border-bottom:2px solid #e2e8f0;">'
        '<th style="padding:3px 8px; font-size:0.6rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.05em; text-align:left;">Rule</th>'
        '<th style="padding:3px 8px; font-size:0.6rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.05em; text-align:left;">Recommendation</th>'
        '<th style="padding:3px 8px; font-size:0.6rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.05em; text-align:left;">Detail</th>'
        '</tr></thead><tbody>' + '\n'.join(port_rows) + '</tbody></table>'
    )
    st.markdown(port_table, unsafe_allow_html=True)
    st.caption("Standard 2026 Approach: Deploy 50% base position + 50% dry powder for -10% dips. Hard cap at risk-adjusted limit. Review quarterly.")

# ===== TAB 7: CONVICTION =====
with t7:
    st.markdown("### Investment Conviction & Thesis")

    # Conviction spectrum — compact table
    conv = thesis['conviction']
    conviction_levels = [
        {'level': 'HIGH CONVICTION', 'detail': 'Wide moat + installed growth + clean risk', 'color': '#059669', 'bg': '#ecfdf5'},
        {'level': 'MODERATE CONVICTION', 'detail': 'Solid fundamentals, manageable risk', 'color': '#2563eb', 'bg': '#eff6ff'},
        {'level': 'SELECTIVE', 'detail': 'Good moat but elevated risk', 'color': '#ea580c', 'bg': '#fff7ed'},
        {'level': 'OPPORTUNISTIC', 'detail': 'Limited moat, favorable risk/reward', 'color': '#ca8a04', 'bg': '#fefce8'},
        {'level': 'PASS', 'detail': 'Better opportunities elsewhere', 'color': '#dc2626', 'bg': '#fef2f2'},
    ]
    rows_t7 = []
    for cl in conviction_levels:
        is_active = cl['level'] == conv
        color = cl['color']
        bg = cl['bg']
        if is_active:
            rows_t7.append(
                '<tr style="background:' + bg + '; font-weight:800; border-left:4px solid ' + color + ';">'
                '<td style="padding:4px 10px; font-size:0.75rem; color:' + color + '; font-weight:800;">' + cl['level'] + '</td>'
                '<td style="padding:4px 10px; font-size:0.72rem; color:#0d1b3e; font-weight:700;">' + cl['detail'] + '</td>'
                '<td style="padding:4px 10px; text-align:right;">'
                '<span style="background:' + color + '; color:#fff; padding:2px 9px; border-radius:4px; font-size:0.62rem; font-weight:800;">ACTIVE</span>'
                '</td></tr>'
            )
        else:
            rows_t7.append(
                '<tr style="opacity:0.3;">'
                '<td style="padding:4px 10px; font-size:0.68rem; color:#999;">' + cl['level'] + '</td>'
                '<td style="padding:4px 10px; font-size:0.68rem; color:#999;">' + cl['detail'] + '</td>'
                '<td style="padding:4px 10px;"></td></tr>'
            )
    table_t7 = (
        '<table style="width:100%; border-collapse:collapse; font-family:Inter,sans-serif; margin-bottom:12px;">'
        '<thead><tr style="border-bottom:2px solid #e2e8f0;">'
        '<th style="padding:3px 8px; font-size:0.6rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.06em; text-align:left;">Conviction</th>'
        '<th style="padding:3px 8px; font-size:0.6rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.06em; text-align:left;">Criteria</th>'
        '<th style="padding:3px 8px; text-align:right; width:55px;"></th>'
        '</tr></thead><tbody>' + '\n'.join(rows_t7) + '</tbody></table>'
    )
    st.markdown(table_t7, unsafe_allow_html=True)

    # Full thesis
    st.markdown("#### One-Paragraph Thesis")
    st.markdown(f'<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:6px;padding:16px 20px;font-size:0.9rem;line-height:1.6;color:#334155;">{thesis["thesis"]}</div>', unsafe_allow_html=True)

    # Factor attribution (SHAP-style simplified)
    st.markdown("---")
    st.markdown("#### Factor Attribution (SHAP-Style)")
    st.caption("Which factors drove the conviction assessment? Simplified feature importance for transparency.")

    # Build attribution
    factors = []
    # Rule of 40 impact
    r40_fcf = r40.get('rule_40_fcf')
    if r40_fcf is not None:
        if r40_fcf >= 50:
            factors.append({'Factor': 'Rule of 40 (Elite)', 'Impact': '+2.5', 'Direction': 'Bullish', 'Detail': f'FCF Rule of 40 = {r40_fcf:.0f}'})
        elif r40_fcf >= 40:
            factors.append({'Factor': 'Rule of 40 (Strong)', 'Impact': '+1.5', 'Direction': 'Bullish', 'Detail': f'FCF Rule of 40 = {r40_fcf:.0f}'})
        elif r40_fcf < 20:
            factors.append({'Factor': 'Rule of 40 (Weak)', 'Impact': '-1.5', 'Direction': 'Bearish', 'Detail': f'FCF Rule of 40 = {r40_fcf:.0f}'})

    # Gross margin impact
    gm_pct = gm_data.get('gross_margin_pct')
    if gm_pct is not None:
        if gm_pct >= 75:
            factors.append({'Factor': 'Gross Margin (Excellent)', 'Impact': '+1.5', 'Direction': 'Bullish', 'Detail': f'{gm_pct:.0f}% gross margin'})
        elif gm_pct < 20:
            factors.append({'Factor': 'Gross Margin (Thin)', 'Impact': '-1.5', 'Direction': 'Bearish', 'Detail': f'{gm_pct:.0f}% gross margin'})

    # Moat impact
    if moat_val >= 8:
        factors.append({'Factor': 'Moat Rating (Wide)', 'Impact': '+2.0', 'Direction': 'Bullish', 'Detail': f'Moat = {moat_val}/10'})
    elif moat_val >= 6:
        factors.append({'Factor': 'Moat Rating (Moderate)', 'Impact': '+1.0', 'Direction': 'Bullish', 'Detail': f'Moat = {moat_val}/10'})
    elif moat_val <= 3:
        factors.append({'Factor': 'Moat Rating (None)', 'Impact': '-1.5', 'Direction': 'Bearish', 'Detail': f'Moat = {moat_val}/10'})

    # Momentum
    mom_rank = momentum.get('zacks_rank', 3)
    if mom_rank == 1:
        factors.append({'Factor': 'Momentum (Strong Buy)', 'Impact': '+1.5', 'Direction': 'Bullish', 'Detail': momentum.get('rank_label', '')})
    elif mom_rank >= 4:
        factors.append({'Factor': 'Momentum (Negative)', 'Impact': '-1.0', 'Direction': 'Bearish', 'Detail': momentum.get('rank_label', '')})

    # Thematic fit
    theme_score = thematic.get('primary_conviction', 0)
    if theme_score >= 7:
        factors.append({'Factor': 'Thematic Alignment (Strong)', 'Impact': '+1.5', 'Direction': 'Bullish', 'Detail': f'Primary: {thematic.get("primary_name", "")}'})
    elif theme_score <= 2:
        factors.append({'Factor': 'Thematic Alignment (Weak)', 'Impact': '-0.5', 'Direction': 'Bearish', 'Detail': 'No strong 2026 theme fit'})

    # Risk factors
    rs = risk_factors.get('risk_score', 0)
    if rs >= 6:
        factors.append({'Factor': 'Risk Profile (Elevated)', 'Impact': '-2.0', 'Direction': 'Bearish', 'Detail': f'Risk score = {rs}'})
    elif rs <= 2:
        factors.append({'Factor': 'Risk Profile (Clean)', 'Impact': '+1.0', 'Direction': 'Bullish', 'Detail': f'Risk score = {rs}'})

    # NRR impact (enhanced with installed growth logic)
    nrr_pct = nrr.get('estimated_nrr_pct')
    if nrr_pct is not None:
        if nrr_pct >= 120:
            factors.append({'Factor': 'NRR — Installed Growth Engine', 'Impact': '+2.0', 'Direction': 'Bullish', 'Detail': f'NRR = {nrr_pct:.0f}% — grows {nrr_pct - 100:.0f}% even with zero new customers'})
        elif nrr_pct >= 106:
            factors.append({'Factor': 'NRR (Expanding)', 'Impact': '+1.0', 'Direction': 'Bullish', 'Detail': f'Est. NRR = {nrr_pct:.0f}%'})
        elif nrr_pct < 100:
            factors.append({'Factor': 'NRR (Contracting)', 'Impact': '-1.5', 'Direction': 'Bearish', 'Detail': f'Est. NRR = {nrr_pct:.0f}% — existing customer base is shrinking'})

    # RPO impact
    rpo_signal = rpo_data.get('leading_indicator_signal')
    if rpo_signal == 'STRONG LEAD':
        factors.append({'Factor': 'RPO — Revenue Acceleration Ahead', 'Impact': '+1.5', 'Direction': 'Bullish', 'Detail': rpo_data.get('signal_detail', 'Contracted backlog growing faster than revenue')})
    elif rpo_signal == 'LAGGING':
        factors.append({'Factor': 'RPO — Backlog Depleting', 'Impact': '-1.0', 'Direction': 'Bearish', 'Detail': rpo_data.get('signal_detail', 'RPO growth trailing revenue')})

    # Forward Rule of 40 inflection
    fwd_r40_val = fwd_r40.get('forward_rule_40')
    fwd_inflection = fwd_r40.get('inflection_signal', '')
    if fwd_inflection in ('MASSIVE INFLECTION', 'POSITIVE INFLECTION', 'BENCHMARK CROSSOVER'):
        factors.append({'Factor': 'Forward Rule of 40 — Inflection Point', 'Impact': '+2.0', 'Direction': 'Bullish', 'Detail': fwd_r40.get('inflection_detail', 'Forward estimates show improvement')})
    elif fwd_inflection in ('NEGATIVE INFLECTION', 'SEVERE DECLINE'):
        factors.append({'Factor': 'Forward Rule of 40 — Deteriorating', 'Impact': '-1.5', 'Direction': 'Bearish', 'Detail': fwd_r40.get('inflection_detail', 'Forward estimates show decline')})

    # Moat Performance attribution
    perf_attr = qual.get('moat_performance', {})
    perf_signal_attr = perf_attr.get('performance', '')
    if perf_signal_attr == 'COMPOUNDING':
        factors.append({'Factor': 'Moat Trajectory — Compounding', 'Impact': '+1.5', 'Direction': 'Bullish', 'Detail': 'Moat strengthening — declining CAC, rising premiums, expanding share'})
    elif perf_signal_attr == 'DECAYING':
        factors.append({'Factor': 'Moat Trajectory — Decaying', 'Impact': '-2.0', 'Direction': 'Bearish', 'Detail': 'Moat eroding — competitors closing gaps, pricing power weakening'})
    elif perf_signal_attr == 'DEFENDING':
        factors.append({'Factor': 'Moat Trajectory — Defending', 'Impact': '+0.5', 'Direction': 'Neutral', 'Detail': 'Moat stable — maintaining position without significant change'})

    # Circumvention Delta
    cd = moat.get('circumvention_delta', 0)
    if cd >= 10:
        factors.append({'Factor': 'Circumvention Delta (Formidable)', 'Impact': '+2.0', 'Direction': 'Bullish', 'Detail': f'Delta = {cd}/13 — {moat.get("circumvention_delta_formula", "")}'})
    elif cd >= 7:
        factors.append({'Factor': 'Circumvention Delta (Strong)', 'Impact': '+1.0', 'Direction': 'Bullish', 'Detail': f'Delta = {cd}/13'})
    elif cd <= 3:
        factors.append({'Factor': 'Circumvention Delta (Weak)', 'Impact': '-1.0', 'Direction': 'Bearish', 'Detail': f'Delta = {cd}/13 — low barrier to competition'})

    if factors:
        for f in factors:
            dir_color = "#0d8a3e" if f['Direction'] == 'Bullish' else ("#555" if f['Direction'] == 'Neutral' else "#c62828")
            st.markdown(f"""
            <div class="factor-row">
                <span style="font-weight:800;color:{dir_color};min-width:55px;font-size:0.9rem;">{f['Impact']}</span>
                <span style="font-weight:700;font-size:0.82rem;color:#0d1b3e;min-width:180px;">{f['Factor']}</span>
                <span style="font-size:0.76rem;color:#555;flex:1;font-weight:600;">{f['Detail']}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Insufficient data to decompose factor attribution.")

    # Thesis re-test reminder
    st.markdown("---")
    st.markdown("#### Thesis Re-Test Protocol")
    st.warning("""
    **After every earnings print, ask:**
    1. Can I rewrite the one-paragraph thesis using the new data (guidance, capex, segment mix)?
    2. Has any thesis-break threshold been triggered?
    3. Has the moat widened or narrowed?
    4. Does the position still fit within my barbell allocation?

    If you cannot answer #1 with conviction → liquidate or reduce the position.
    """)

    st.markdown("---")
# ===== TAB 8: SCREENER =====
with t8:
    st.markdown("### High Conviction Stock Screener")
    st.caption("Screen 114 stocks across US, SGX, HKEX, and EU markets for Platinum, Gold, and Silver conviction tiers.")

    # Watchlist
    WATCHLIST = [
        # US Tech - SaaS/Cloud
        'MSFT','CRM','ADBE','NOW','SNOW','DDOG','CRWD','PANW','ZS','QLYS','NET','MDB','HUBS','TEAM','WDAY','INTU','ADSK','PLTR',
        # US Tech - Semis/AI Infra
        'NVDA','AMD','AVGO','MU','MRVL','AMAT','LRCX','KLAC','TXN','QCOM','INTC','SMCI','ANET','DELL','STX','WDC',
        # US Mega Cap
        'AAPL','GOOGL','AMZN','META','TSLA',
        # Energy/Industrial
        'BE','NEE','GEV','FSLR','CEG','VST','XOM','CVX','COP','CAT','GE','HON','EMR','ETN',
        # Healthcare/Biopharma
        'LLY','NVO','BMY','ALGN','CNC','UNH','JNJ','ABBV','MRK','PFE','REGN','VRTX','SDGR','MRNA',
        # Financials
        'JPM','BAC','WFC','GS','MS','BLK','V','MA','AXP',
        # Consumer/Retail
        'WMT','COST','HD','LOW','NKE','SBUX','MCD','TGT',
        # SGX
        'D05.SI','O39.SI','U11.SI','Z74.SI','C52.SI','BN4.SI','S68.SI','C09.SI','F34.SI','S63.SI',
        # HKEX
        '0700.HK','9988.HK','3690.HK','9618.HK','1299.HK','0005.HK','0388.HK','2318.HK','0941.HK','0016.HK',
        # EU/Global
        'SAP','ASML','AZN','HSBC','BHP','RIO','BP','SHEL',
    ]

    if st.button("Run Screener (114 stocks, ~30s)", type="primary", use_container_width=True):
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import time

        progress = st.progress(0)
        status = st.empty()

        results = []
        errors = []
        start_time = time.time()
        total = len(WATCHLIST)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {executor.submit(alpha_analysis, t): t for t in WATCHLIST}
            for i, future in enumerate(as_completed(futures)):
                ticker_scan = futures[future]
                res = future.result()
                if 'error' in res:
                    errors.append({'ticker': ticker_scan, 'error': res['error']})
                else:
                    results.append({
                        'ticker': ticker_scan,
                        'name': res['data']['name'],
                        'nob': res['nob']['name'],
                        'moat': res['qualitative']['moat']['moat_rating'],
                        'circ_delta': res['qualitative']['moat'].get('circumvention_delta', 0),
                        'moat_trend': res['qualitative']['moat_performance']['performance'],
                        'risk': res['risk_management']['risk_factors']['risk_score'],
                        'nrr': res['quantitative']['net_revenue_retention'].get('estimated_nrr_pct'),
                        'fwd_inflection': res['quantitative']['forward_rule_of_40'].get('inflection_signal', ''),
                        'conviction': res['thesis']['conviction'],
                        'price': res['data']['price'],
                        'sector': res['data']['sector'],
                        'fwdr40': res['quantitative']['forward_rule_of_40'].get('forward_rule_40'),
                    })
                progress.progress((i + 1) / total)
                elapsed = time.time() - start_time
                status.text(f"Scanning: {i+1}/{total} | {ticker_scan} | {elapsed:.0f}s")

        progress.empty()
        status.empty()

        if not results:
            st.warning("No results. Check network connection.")
            st.stop()

        df = pd.DataFrame(results)

        # ---- Tier filters ----
        platinum = df[
            (df['moat'] >= 6) & (df['risk'] <= 1) & (df['moat_trend'] == 'COMPOUNDING') &
            ((df['nrr'].notna() & (df['nrr'] >= 120)) | (df['fwd_inflection'].isin(['MASSIVE INFLECTION', 'POSITIVE INFLECTION', 'BENCHMARK CROSSOVER'])))
        ].sort_values('moat', ascending=False)

        gold = df[
            (df['moat'] >= 5) & (df['risk'] <= 2) &
            ((df['nrr'].notna() & (df['nrr'] >= 120)) | (df['fwd_inflection'].isin(['MASSIVE INFLECTION', 'POSITIVE INFLECTION', 'BENCHMARK CROSSOVER'])))
        ].sort_values('moat', ascending=False)

        silver = df[
            (df['moat'] >= 4) & (df['risk'] <= 4) & (df['circ_delta'] >= 4)
        ].sort_values('moat', ascending=False)

        # ---- Display tiers ----
        def show_tier(subset, label, color, emoji):
            if len(subset) == 0:
                return
            st.markdown(f"### {emoji} {label} — {len(subset)} stocks")
            st.caption({
                'PLATINUM': 'Moat >= 6 | Risk <= 1 | Compounding | Growth signal',
                'GOLD': 'Moat >= 5 | Risk <= 2 | Growth signal',
                'SILVER': 'Moat >= 4 | Risk <= 4 | Circ.Delta >= 4',
            }.get(label, ''))

            display = subset[['ticker','name','nob','moat','circ_delta','moat_trend','risk','nrr','fwd_inflection','price','sector']].copy()
            display['moat'] = display['moat'].apply(lambda x: f"{x:.1f}")
            display['nrr'] = display['nrr'].apply(lambda x: f"{x:.0f}%" if pd.notna(x) else 'N/A')
            display['price'] = display['price'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else 'N/A')
            display.columns = ['Ticker','Name','NoB','Moat','Circ.D','Trend','Risk','NRR','Fwd Inflection','Price','Sector']

            st.dataframe(display, width='stretch', hide_index=True,
                column_config={
                    'Ticker': st.column_config.TextColumn(width='small'),
                    'Name': st.column_config.TextColumn(width='medium'),
                    'Moat': st.column_config.TextColumn(width='small'),
                    'Circ.D': st.column_config.TextColumn(width='small'),
                    'Trend': st.column_config.TextColumn(width='small'),
                    'Risk': st.column_config.TextColumn(width='small'),
                    'NRR': st.column_config.TextColumn(width='small'),
                    'Fwd Inflection': st.column_config.TextColumn(width='medium'),
                    'Price': st.column_config.TextColumn(width='small'),
                })

        show_tier(platinum, 'PLATINUM', '#059669', '')
        show_tier(gold, 'GOLD', '#d97706', '')
        show_tier(silver, 'SILVER', '#6b7280', '')

        # ---- Summary stats ----
        st.markdown("---")
        st.markdown("#### Screening Summary")
        sm1, sm2, sm3, sm4, sm5 = st.columns(5)
        with sm1: st.metric("Total Scanned", len(WATCHLIST))
        with sm2: st.metric("PLATINUM", len(platinum))
        with sm3: st.metric("GOLD", len(gold))
        with sm4: st.metric("SILVER", len(silver))
        with sm5: st.metric("Time", f"{time.time() - start_time:.0f}s")

        # Conviction distribution
        st.caption("Conviction Distribution")
        dist_cols = st.columns(5)
        for i, level in enumerate(['HIGH CONVICTION', 'MODERATE CONVICTION', 'SELECTIVE', 'OPPORTUNISTIC', 'PASS']):
            count = len(df[df['conviction'] == level])
            with dist_cols[i]:
                st.metric(level, count)

        if errors:
            st.warning(f"{len(errors)} errors: {', '.join(e['ticker'] for e in errors[:5])}")

    else:
        st.info("Click **Run Screener** to scan 114 stocks across US, Singapore, Hong Kong, and European markets. Screening takes ~30 seconds using multi-threaded analysis.")
        st.caption("The screener applies the full Analytical Alpha framework to each stock, then filters by moat strength, risk profile, and forward-looking growth signals.")

st.caption(f"Not financial advice. Public data via Yahoo Finance. Analysis generated {datetime.now().strftime('%Y-%m-%d %H:%M')} — 2026 Strategic Growth Investment Framework")

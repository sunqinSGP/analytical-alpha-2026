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

# Professional CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,400;14..32,500;14..32,600;14..32,700;14..32,800&display=swap');

    /* === ROOT & RESET === */
    html, body, [class*="css"] {
        font-size: 14px;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        line-height: 1.5;
        color: #1e293b;
        background: #f1f5f9;
    }

    /* === HIDE SIDEBAR & ADJUST APP === */
    section[data-testid="stSidebar"] { display: none; }
    .stApp { margin-top: -2rem; background: #f1f5f9; }
    div[data-testid="stVerticalBlock"] { gap: 0.25rem; }
    div[data-testid="stMetricValue"] { font-size: 1rem !important; }
    div[data-testid="stMetricLabel"] { font-size: 0.7rem !important; }

    /* === TYPOGRAPHY === */
    h1 { font-size: 1.3rem !important; font-weight: 700 !important; letter-spacing: -0.015em; color: #0f172a; margin: 0 !important; }
    h2 { font-size: 1.05rem !important; font-weight: 600 !important; color: #1e293b; margin-top: 0.4rem !important; margin-bottom: 0.25rem !important; }
    h3 { font-size: 0.9rem !important; font-weight: 600 !important; color: #334155; margin-top: 0.3rem !important; margin-bottom: 0.15rem !important; }
    .dim { color: #94a3b8; font-size: 0.7rem; }

    /* === TABS === */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        border-bottom: 1px solid #e2e8f0;
        background: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 0.75rem !important;
        padding: 8px 18px !important;
        font-weight: 500;
        color: #64748b;
        border-radius: 6px 6px 0 0 !important;
        margin-right: 2px;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #0f172a;
        font-weight: 600;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-bottom: 2px solid #ffffff;
    }

    /* === METRIC CARDS === */
    .alpha-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 12px 14px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
        transition: all 0.2s ease;
        height: 100%;
    }
    .alpha-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.06);
        border-color: #cbd5e1;
        transform: translateY(-1px);
    }
    .alpha-card .label {
        font-size: 0.6rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .alpha-card .value {
        font-size: 1.2rem;
        font-weight: 700;
        color: #0f172a;
        line-height: 1.2;
    }
    .alpha-card .sub {
        font-size: 0.65rem;
        color: #64748b;
        margin-top: 3px;
    }

    /* === VERDICT BANNERS === */
    .verdict {
        padding: 16px 22px;
        border-radius: 8px;
        margin: 14px 0;
        font-size: 0.88rem;
        line-height: 1.5;
    }
    .verdict.conviction-high {
        background: linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%);
        border: 1px solid #a7f3d0;
        border-left: 4px solid #059669;
    }
    .verdict.conviction-moderate {
        background: linear-gradient(135deg, #eff6ff 0%, #f0f9ff 100%);
        border: 1px solid #bfdbfe;
        border-left: 4px solid #2563eb;
    }
    .verdict.conviction-selective {
        background: linear-gradient(135deg, #fff7ed 0%, #fffbf5 100%);
        border: 1px solid #fed7aa;
        border-left: 4px solid #ea580c;
    }
    .verdict.conviction-opportunistic {
        background: linear-gradient(135deg, #fefce8 0%, #fffbeb 100%);
        border: 1px solid #fde68a;
        border-left: 4px solid #ca8a04;
    }
    .verdict.conviction-pass {
        background: linear-gradient(135deg, #fef2f2 0%, #fff5f5 100%);
        border: 1px solid #fecaca;
        border-left: 4px solid #dc2626;
    }

    /* === TAGS === */
    .tag {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 0.65rem;
        font-weight: 600;
        letter-spacing: 0.03em;
    }
    .tag.green { background: #dcfce7; color: #166534; }
    .tag.red { background: #fee2e2; color: #991b1b; }
    .tag.amber { background: #ffedd5; color: #9a3412; }
    .tag.blue { background: #dbeafe; color: #1e40af; }
    .tag.purple { background: #f3e8ff; color: #6b21a8; }
    .tag.gray { background: #f1f5f9; color: #475569; }

    /* === MOAT GAUGE === */
    .moat-gauge {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 6px 0;
    }
    .moat-bar {
        height: 12px;
        border-radius: 6px;
        background: #e2e8f0;
        flex: 1;
        overflow: hidden;
    }
    .moat-fill {
        height: 100%;
        border-radius: 6px;
        transition: width 0.5s ease;
    }

    /* === DIVIDERS === */
    hr { margin: 0.75rem 0; border: none; border-top: 1px solid #e2e8f0; }

    /* === DATAFRAMES === */
    .stDataFrame {
        font-size: 12px !important;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        margin: 8px 0 14px 0;
        overflow: hidden;
    }
    .stDataFrame th {
        font-size: 0.68rem !important;
        padding: 9px 14px !important;
        background: #f8fafc;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        border-bottom: 1px solid #e2e8f0;
    }
    .stDataFrame td {
        font-size: 0.78rem !important;
        padding: 8px 14px !important;
        color: #334155;
    }

    /* === LINKS === */
    a { color: #2563eb; text-decoration: none; font-weight: 500; }
    a:hover { text-decoration: underline; }

    /* === INPUTS === */
    input, select, .stTextInput>div>div>input {
        border-radius: 6px !important;
        border: 1px solid #e2e8f0 !important;
        font-size: 0.82rem !important;
        padding: 8px 12px !important;
    }
    input:focus, select:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37,99,235,0.1) !important;
    }

    /* === BUTTONS === */
    button {
        border-radius: 6px !important;
        font-weight: 500 !important;
    }

    /* === MOAT DIMENSION CARDS === */
    .moat-dim-card {
        background: #ffffff;
        border-radius: 8px;
        padding: 16px 18px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
        height: 100%;
    }

    /* === THEME ACCENTS === */
    .theme-ai { border-left: 3px solid #7c3aed; padding-left: 12px; }
    .theme-energy { border-left: 3px solid #d97706; padding-left: 12px; }
    .theme-health { border-left: 3px solid #059669; padding-left: 12px; }
    .theme-software { border-left: 3px solid #2563eb; padding-left: 12px; }

    /* === FACTOR ATTRIBUTION ROW === */
    .factor-row {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 9px 14px;
        margin: 3px 0;
        background: #ffffff;
        border: 1px solid #f1f5f9;
        border-radius: 6px;
        transition: background 0.15s;
    }
    .factor-row:hover { background: #f8fafc; }

    /* === SCROLLBAR === */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #f1f5f9; }
    ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }

    /* === NOB BANNER === */
    .nob-banner {
        padding: 10px 18px;
        border-radius: 8px;
        margin: 10px 0;
        font-size: 0.85rem;
        display: flex;
        align-items: center;
        gap: 12px;
    }
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
# HEADER — dark bar with logo, inputs
# ===========================================================================
st.markdown("""
<div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); margin: -2rem -4rem 0 -4rem; padding: 16px 4rem 14px 4rem;">
    <div style="display: flex; align-items: center; justify-content: space-between;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 1.5rem;"></span>
            <span style="font-size: 1.2rem; font-weight: 700; color: #f8fafc; letter-spacing: -0.02em;">Analytical Alpha</span>
            <span style="font-size: 0.7rem; font-weight: 500; color: #94a3b8; background: #334155; padding: 3px 10px; border-radius: 4px;">2026</span>
        </div>
        <span style="font-size: 0.7rem; color: #64748b;">Strategic Growth Investment Framework</span>
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
    st.markdown(metric_card("Price", f"{cs}{price:.2f}"), unsafe_allow_html=True)
with c2:
    st.markdown(metric_card("Market Cap", f"{cs}{mcap/1e9:.1f}B" if mcap else "N/A"), unsafe_allow_html=True)
with c3:
    r40_val = r40.get('rule_40_fcf')
    r40_color = "#16a34a" if (r40_val and r40_val >= 50) else ("#ea580c" if (r40_val and r40_val >= 40) else ("#dc2626" if (r40_val and r40_val < 30) else "#6b7280"))
    r40_display = f"{r40_val:.0f}" if r40_val is not None else "N/A"
    st.markdown(metric_card("Rule of 40", r40_display, sub="FCF basis" if r40_val is not None else None, color=r40_color), unsafe_allow_html=True)
with c4:
    gm_val = gm_data.get('gross_margin_pct')
    gm_color = "#16a34a" if (gm_val and gm_val >= 75) else ("#ea580c" if (gm_val and gm_val >= 40) else ("#dc2626" if (gm_val and gm_val is not None and gm_val < 20) else "#6b7280"))
    st.markdown(metric_card("Gross Margin", f"{gm_val:.0f}%" if gm_val is not None else "N/A", color=gm_color), unsafe_allow_html=True)
with c5:
    nrr = quant['net_revenue_retention']
    nrr_val = nrr.get('estimated_nrr_pct')
    nrr_color = "#16a34a" if (nrr_val and nrr_val >= 120) else ("#16a34a" if (nrr_val and nrr_val >= 106) else ("#ea580c" if (nrr_val and nrr_val >= 100) else "#dc2626"))
    nrr_sub = "Installed growth!" if (nrr_val and nrr_val >= 120) else ("≥106% target" if nrr_val is not None else None)
    st.markdown(metric_card("Est. NRR", f"{nrr_val:.0f}%" if nrr_val is not None else "N/A", sub=nrr_sub, color=nrr_color), unsafe_allow_html=True)
with c6:
    moat_val = moat['moat_rating']
    moat_color = moat['moat_color']
    st.markdown(metric_card("Moat Rating", f"{moat_val}/10", sub=moat['moat_label'].split('—')[0].strip(), color=moat_color), unsafe_allow_html=True)
with c7:
    rank_label = momentum.get('rank_label', 'N/A')
    rank_color = "#16a34a" if momentum.get('zacks_rank') in [1, 2] else ("#ea580c" if momentum.get('zacks_rank') == 3 else "#dc2626")
    st.markdown(metric_card("Momentum", rank_label, color=rank_color), unsafe_allow_html=True)
with c8:
    risk_level = risk_factors.get('risk_level', 'N/A')
    risk_color = "#16a34a" if risk_level == 'Low' else ("#ea580c" if risk_level == 'Medium' else "#dc2626")
    st.markdown(metric_card("Risk Level", risk_level, color=risk_color), unsafe_allow_html=True)

st.markdown(f'<small><b>{name}</b> | {data["sector"]} | {data["industry"]} | {data.get("country", "")} | Currency: {currency} | Employees: {data.get("employees", "N/A"):,}</small>', unsafe_allow_html=True)

# ===========================================================================
# NoB BUSINESS MODEL BANNER
# ===========================================================================
nob_type = result['nob_type']
nob = result['nob']
st.markdown(f"""
<div class="nob-banner" style="background: {nob['color']}08; border: 1px solid {nob['color']}30;">
    <span style="font-size:1.3rem;">{nob['icon']}</span>
    <div>
        <div style="font-weight:700; font-size:0.9rem; color:{nob['color']};">{nob['name']}</div>
        <div style="font-size:0.73rem; color:#64748b;">{nob['description']}</div>
    </div>
    <div style="margin-left:auto; font-size:0.68rem; color:#94a3b8; background:#f8fafc; padding:4px 10px; border-radius:4px;">
        {nob['metrics_focus']}
    </div>
</div>
""", unsafe_allow_html=True)

# ===========================================================================
# MAIN TAB BAR
# ===========================================================================
st.markdown("---")
t1, t2, t3, t4, t5, t6, t7 = st.tabs([
    "1. Overview", "2. Quantitative", "3. Qualitative Moat",
    "4. 2026 Themes", "5. Risk Management", "6. Portfolio Context", "7. Conviction"
])

# ===== TAB 1: OVERVIEW =====
with t1:
    # Conviction banner
    conv = thesis['conviction']
    conv_class = {
        'HIGH CONVICTION': 'conviction-high',
        'MODERATE CONVICTION': 'conviction-moderate',
        'SELECTIVE': 'conviction-selective',
        'OPPORTUNISTIC': 'conviction-opportunistic',
        'PASS': 'conviction-pass',
    }.get(conv, '')
    st.markdown(f'<div class="verdict {conv_class}"><b>{conv}</b><br><small>{thesis["conviction_detail"]}</small></div>', unsafe_allow_html=True)

    # Thesis paragraph
    st.markdown("### Investment Thesis")
    st.markdown(f'<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:6px;padding:16px 20px;font-size:0.9rem;line-height:1.6;color:#334155;">{thesis["thesis"]}</div>', unsafe_allow_html=True)

    # Framework summary grid
    st.markdown("### Framework Summary")
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        fwd_r40_overview = quant['forward_rule_of_40']
        fwd_r40_val_ov = fwd_r40_overview.get('forward_rule_40')
        fwd_inflection_ov = fwd_r40_overview.get('inflection_signal', '')
        rpo_ov = quant['rpo']
        rpo_signal_ov = rpo_ov.get('leading_indicator_signal', 'N/A')

        # NoB-specific metrics (built with simple concatenation, no nested f-strings)
        def fmt_pct(v):
            return f"{v:.0f}%" if v is not None else "N/A"

        def fmt_num(v, unit=""):
            return f"{v:.0f}{unit}" if v is not None else "N/A"

        lines = []
        lines.append('<div class="alpha-card">')
        lines.append(f'<div class="label">Quantitative Scorecard &mdash; {nob["name"]}</div>')
        lines.append('<div style="margin-top:8px;font-size:0.82rem;line-height:1.6;">')

        if nob_type == 'high_growth_saas':
            saas = quant.get('saas_filter', {})
            ltv = saas.get('ltv_cac_ratio')
            cac = saas.get('cac_payback_months')
            lines.append('<b>SaaS Efficiency Metrics</b><br>')
            lines.append(f'Rule of 40 (FCF): <b>{fmt_num(r40_val)}</b> (benchmark &ge;40)<br>')
            lines.append(f'LTV:CAC Ratio: <b>{f"{ltv}:1" if ltv is not None else "N/A"}</b> (min 3:1)<br>')
            lines.append(f'CAC Payback: <b>{f"{cac:.1f}mo" if cac is not None else "N/A"}</b> (&le;12mo best)<br>')
            lines.append(f'Gross Margin: <b>{fmt_pct(gm_val)}</b> (&ge;75% for SaaS)<br>')
            nrr_str = fmt_pct(nrr_val)
            if nrr.get('nrr_capped'): nrr_str += ' (proxy cap)'
            lines.append(f'Est. NRR: <b>{nrr_str}</b> (&ge;106% retention)<br>')
        elif nob_type == 'ai_infra_semiconductor':
            ind = quant.get('industrial_filter', {})
            rev = ind.get('revision_led_eps', {})
            lines.append('<b>Semiconductor Throughput</b><br>')
            lines.append(f'Revenue Growth: <b>{fmt_pct(ind.get("revenue_growth_pct"))}</b><br>')
            lines.append(f'Backlog Growth: <b>{fmt_pct(ind.get("backlog_growth_pct"))}</b> (&ge;20% target)<br>')
            conv = ind.get('conversion_velocity')
            lines.append(f'Conversion Velocity: <b>{f"{conv:.2f}x" if conv is not None else "N/A"}</b><br>')
            lines.append(f'Revision-Led EPS: <b>{rev.get("rank", "N/A")}</b><br>')
        elif nob_type == 'energy_industrial':
            ind = quant.get('industrial_filter', {})
            lines.append('<b>Energy &amp; Industrial Throughput</b><br>')
            lines.append(f'Revenue Growth: <b>{fmt_pct(ind.get("revenue_growth_pct"))}</b><br>')
            lines.append(f'Backlog Growth: <b>{fmt_pct(ind.get("backlog_growth_pct"))}</b><br>')
            if ind.get('power_pipeline_note'):
                lines.append('Power Pipeline: <b>Monitor GW capacity</b><br>')
        elif nob_type == 'biopharma':
            bio = quant.get('biopharma_filter', {})
            lines.append('<b>Biopharma Milestone Metrics</b><br>')
            lines.append(f'Clinical Stage: <b>{bio.get("clinical_stage", "N/A")}</b><br>')
            lines.append(f'rNPV Discount Rate: <b>{fmt_pct(bio.get("discount_rate_pct"))}</b><br>')
            lines.append(f'AI Attrition Premium: <b>{"YES" if bio.get("ai_attrition_premium") else "No"}</b><br>')
            lines.append(f'Revenue Growth: <b>{fmt_pct(bio.get("revenue_growth_pct"))}</b><br>')
            lines.append(f'Price/Revenue: <b>{bio.get("price_to_revenue", "N/A")}</b><br>')
        elif nob_type == 'traditional_value':
            val = quant.get('value_filter', {})
            lines.append('<b>Traditional Value Metrics</b><br>')
            tpe = val.get('trailing_pe')
            lines.append(f'Trailing P/E: <b>{f"{tpe:.1f}x" if tpe and tpe > 0 else "N/A"}</b><br>')
            pb = val.get('price_to_book')
            lines.append(f'Price/Book: <b>{f"{pb:.2f}x" if pb is not None else "N/A"}</b><br>')
            div = val.get('dividend_yield_pct')
            lines.append(f'Dividend Yield: <b>{f"{div:.1f}%" if div is not None else "N/A"}</b><br>')
            lines.append(f'Value Score: <b>{val.get("value_score", "N/A")}/10</b> — {val.get("value_label", "")}<br>')
            dte = val.get('debt_to_equity')
            lines.append(f'Debt/Equity: <b>{f"{dte:.0f}" if dte is not None else "N/A"}</b><br>')
        elif nob_type == 'high_growth_general':
            gf = quant.get('growth_filter', {})
            lines.append('<b>High-Growth Metrics</b><br>')
            lines.append(f'Revenue Growth: <b>{fmt_pct(gf.get("revenue_growth_pct"))}</b><br>')
            runway = gf.get('cash_runway_years')
            lines.append(f'Cash Runway: <b>{f"{runway:.0f}yrs" if runway is not None else "N/A"}</b><br>')
            lines.append(f'Growth Score: <b>{gf.get("growth_score", "N/A")}/10</b><br>')
            lines.append(f'Growth Decelerating: <b>{"Yes" if gf.get("growth_decelerating") else "No"}</b><br>')
        else:
            arr_val = arr.get('estimated_arr_growth_pct')
            lines.append('<b>General Metrics</b><br>')
            lines.append(f'Rule of 40 (FCF): <b>{fmt_num(r40_val)}</b><br>')
            lines.append(f'Gross Margin: <b>{fmt_pct(gm_val)}</b><br>')
            lines.append(f'Est. ARR Growth: <b>{fmt_pct(arr_val)}</b><br>')
            nrr_str = fmt_pct(nrr_val)
            if nrr.get('nrr_capped'): nrr_str += ' (capped)'
            lines.append(f'Est. NRR: <b>{nrr_str}</b><br>')
            lines.append(f'Momentum: <b>{momentum.get("rank_label", "N/A")}</b><br>')

        # Forward-looking
        fwd_r40_str = fmt_num(fwd_r40_val_ov) if fwd_r40_val_ov is not None else "N/A"
        lines.append('<b>Forward-Looking</b><br>')
        lines.append(f'Forward R40: <b>{fwd_r40_str}</b> &mdash; {fwd_inflection_ov}<br>')
        lines.append(f'RPO Signal: <b>{rpo_signal_ov}</b><br>')
        lines.append('</div>')
        lines.append('</div>')

        scorecard_html = '\n'.join(lines)
        st.markdown(scorecard_html, unsafe_allow_html=True)
    with f2:
        temporal = moat['temporal_width']
        efficiency = moat['efficiency_width']
        trust = moat['trust_width']
        st.markdown(f"""
        <div class="alpha-card">
            <div class="label">Moat Architecture</div>
            <div style="margin-top:8px;font-size:0.82rem;line-height:1.6;">
            Temporal (R&D Lag): <b>{temporal['score']}/5</b><br>
            Efficiency (Performance): <b>{efficiency['score']}/5</b><br>
            Trust (Validation): <b>{trust['score']}/5</b><br>
            <b>Composite: {moat_val}/10 — {moat['moat_label']}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with f3:
        primary_name = thematic.get('primary_name', 'None')
        primary_conviction = thematic.get('primary_conviction', 0)
        secondary = ', '.join(t['name'] for t in thematic.get('secondary_themes', [])) or 'None'
        st.markdown(f"""
        <div class="alpha-card">
            <div class="label">2026 Thematic Alignment</div>
            <div style="margin-top:8px;font-size:0.82rem;line-height:1.6;">
            Primary: <b>{primary_name}</b> (score: {primary_conviction}/10)<br>
            Secondary: <b>{secondary}</b><br>
            Catalyst: <small>{thematic.get('primary_catalyst', 'N/A')}</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with f4:
        risk_max = risk_factors.get('max_suggested_position', 10)
        ms = risk_mgmt['mental_stop_loss']
        position = risk_mgmt['position_sizing']
        barbell = risk_mgmt['barbell_check']
        st.markdown(f"""
        <div class="alpha-card">
            <div class="label">Risk Framework</div>
            <div style="margin-top:8px;font-size:0.82rem;line-height:1.6;">
            Risk Level: <b>{risk_level}</b><br>
            Max Position: <b>{risk_max}% NAV</b><br>
            Stop-Loss: {position['action']}<br>
            Barbell: {'✓' if barbell.get('valid') else '⚠'} {barbell.get('message', '')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Price performance
    if perf:
        st.markdown("### Price Performance")
        pc1, pc2, pc3, pc4, pc5, pc6 = st.columns(6)
        for i, (label, col) in enumerate([
            ('1m', pc1), ('3m', pc2), ('6m', pc3), ('1y', pc4)
        ]):
            if label in perf:
                with col:
                    val = perf[label]
                    c = "#16a34a" if val >= 0 else "#dc2626"
                    st.markdown(f'<div class="alpha-card" style="text-align:center;"><div class="label">{label}</div><div class="value" style="color:{c};">{val:+.1f}%</div></div>', unsafe_allow_html=True)
        with pc5:
            if '52w_high' in perf:
                st.markdown(f'<div class="alpha-card" style="text-align:center;"><div class="label">52W High</div><div class="value" style="font-size:1rem;">{cs}{perf["52w_high"]:.2f}</div></div>', unsafe_allow_html=True)
        with pc6:
            if '52w_low' in perf:
                st.markdown(f'<div class="alpha-card" style="text-align:center;"><div class="label">52W Low</div><div class="value" style="font-size:1rem;">{cs}{perf["52w_low"]:.2f}</div></div>', unsafe_allow_html=True)

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
    st.caption('"The market prices stocks based on future cash flows. These three indicators help you see what\'s coming before the rest of the market."')

    fi1, fi2, fi3 = st.columns(3)

    with fi1:
        # RPO Indicator
        rpo_signal = rpo_data.get('leading_indicator_signal')
        rpo_growth = rpo_data.get('rpo_growth_pct')
        rpo_color = "#16a34a" if rpo_signal == "STRONG LEAD" else ("#ea580c" if rpo_signal == "LAGGING" else "#3b82f6")
        rpo_icon = "" if rpo_signal == "STRONG LEAD" else ("" if rpo_signal == "LAGGING" else "")
        rev_growth_pct = rpo_data.get('revenue_growth_pct')

        rpo_lines = [
            f'<div class="alpha-card" style="border-top:3px solid {rpo_color};">',
            '<div class="label"> Remaining Performance Obligations</div>',
            '<div style="font-size:0.78rem;color:#64748b;margin:4px 0;">Deferred revenue + contracted backlog</div>',
            f'<div class="value" style="color:{rpo_color};font-size:1.1rem;">{rpo_icon} {rpo_signal if rpo_signal else "N/A"}</div>',
            '<div style="font-size:0.75rem;color:#475569;margin-top:2px;">',
            f'RPO Growth: <b>{fmt_pct(rpo_growth)}</b><br>',
            f'vs Rev Growth: <b>{fmt_pct(rev_growth_pct)}</b>',
            '</div>',
            '<div style="font-size:0.68rem;color:#94a3b8;margin-top:4px;">RPO growth > revenue growth = revenue will accelerate</div>',
            '</div>',
        ]
        st.markdown('\n'.join(rpo_lines), unsafe_allow_html=True)
        if rpo_data.get('signal_detail'):
            st.caption(rpo_data['signal_detail'])

    with fi2:
        # NRR with Installed Growth
        nrr_growth = nrr.get('estimated_nrr_pct')
        if nrr_growth is not None and nrr_growth >= 120:
            nrr_color_fi = "#16a34a"; nrr_icon_fi = ""
        elif nrr_growth is not None and nrr_growth >= 106:
            nrr_color_fi = "#16a34a"; nrr_icon_fi = ""
        elif nrr_growth is not None and nrr_growth >= 100:
            nrr_color_fi = "#ea580c"; nrr_icon_fi = ""
        else:
            nrr_color_fi = "#dc2626"; nrr_icon_fi = ""

        nrr_val_str = f'{nrr_growth:.0f}%' if nrr_growth is not None else 'N/A'
        if nrr_growth is not None and nrr_growth >= 100:
            growth_detail = f"At {nrr_growth:.0f}% NRR, the business grows {nrr_growth - 100:.0f}% even with ZERO new customers"
        else:
            growth_detail = "NRR below 100% means the existing base is shrinking"

        nrr_lines = [
            f'<div class="alpha-card" style="border-top:3px solid {nrr_color_fi};">',
            '<div class="label"> Net Retention Rate</div>',
            '<div style="font-size:0.78rem;color:#64748b;margin:4px 0;">Existing customer expansion &mdash; installed growth</div>',
            f'<div class="value" style="color:{nrr_color_fi};font-size:1.1rem;">{nrr_icon_fi} {nrr_val_str}</div>',
            '<div style="font-size:0.75rem;color:#475569;margin-top:2px;">Benchmark: <b>&ge;106%</b> | Installed Growth: <b>&ge;120%</b></div>',
            f'<div style="font-size:0.68rem;color:#94a3b8;margin-top:4px;">{growth_detail}</div>',
            '</div>',
        ]
        st.markdown('\n'.join(nrr_lines), unsafe_allow_html=True)
        if nrr.get('installed_growth_note'):
            st.caption(nrr['installed_growth_note'])

    with fi3:
        # Forward Rule of 40
        fwd_r40_val = fwd_r40.get('forward_rule_40')
        trail_r40_val = fwd_r40.get('trailing_rule_40')
        inflection = fwd_r40.get('inflection_signal', '')

        if inflection in ('MASSIVE INFLECTION', 'POSITIVE INFLECTION', 'BENCHMARK CROSSOVER'):
            fwd_color = "#16a34a"; fwd_icon = ""
        elif inflection in ('NEGATIVE INFLECTION', 'SEVERE DECLINE'):
            fwd_color = "#dc2626"; fwd_icon = ""
        else:
            fwd_color = "#3b82f6"; fwd_icon = ""

        fwd_val_str = f'{fwd_r40_val:.0f}' if fwd_r40_val is not None else 'N/A'
        if trail_r40_val is not None:
            fwd_val_str += f' vs trailing {trail_r40_val:.0f}'
        fwd_rev_str = fmt_pct(fwd_r40.get('forward_rev_growth_pct'))
        fwd_fcf_str = fmt_pct(fwd_r40.get('forward_fcf_margin_pct'))

        fwd_lines = [
            f'<div class="alpha-card" style="border-top:3px solid {fwd_color};">',
            '<div class="label"> Forward Rule of 40</div>',
            '<div style="font-size:0.78rem;color:#64748b;margin:4px 0;">Using analyst estimates for next year</div>',
            f'<div class="value" style="color:{fwd_color};font-size:1.1rem;">{fwd_icon} {fwd_val_str}</div>',
            '<div style="font-size:0.75rem;color:#475569;margin-top:2px;">',
            f'Forward Rev Growth: <b>{fwd_rev_str}</b><br>',
            f'Forward FCF Margin: <b>{fwd_fcf_str}</b>',
            '</div>',
            f'<div style="font-size:0.68rem;color:#94a3b8;margin-top:4px;">{inflection if inflection else "Forward estimates unavailable"}</div>',
            '</div>',
        ]
        st.markdown('\n'.join(fwd_lines), unsafe_allow_html=True)
        if fwd_r40.get('inflection_detail'):
            st.caption(fwd_r40['inflection_detail'])

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
    st.markdown("#### Standard Quantitative Metrics")

    q1, q2 = st.columns([1, 1])
    with q1:
        st.markdown("#### Rule of 40 (SaaS Efficiency Standard)")
        r40_ebitda = r40.get('rule_40_ebitda')
        r40_fcf = r40.get('rule_40_fcf')
        r40_assess = r40.get('assessment', 'N/A')

        rc1, rc2 = st.columns(2)
        with rc1:
            ebitda_display = f"{r40_ebitda:.0f}" if r40_ebitda is not None else "N/A"
            st.metric("EBITDA Basis", ebitda_display)
            st.caption("Revenue Growth % + EBITDA Margin %")
        with rc2:
            fcf_display = f"{r40_fcf:.0f}" if r40_fcf is not None else "N/A"
            st.metric("FCF Basis (2026 Refined)", fcf_display)
            st.caption("Adds back SBC — often ~16pp higher")

        assess_color = "#16a34a" if "Elite" in str(r40_assess) or "Strong" in str(r40_assess) else ("#ea580c" if "Adequate" in str(r40_assess) else "#dc2626")
        st.markdown(f'<span style="color:{assess_color};font-weight:600;">{r40_assess}</span>', unsafe_allow_html=True)
        st.caption(f"Benchmark: {r40.get('benchmark', '')}")
        if r40_fcf is not None and r40_ebitda is not None:
            gap = r40_fcf - r40_ebitda
            st.caption(f"FCF-EBITDA gap: {gap:+.0f}pp — {'typical for companies with significant SBC' if gap > 5 else 'minimal SBC adjustment'}")

        st.markdown("---")
        st.markdown("#### Gross Margin Efficiency")
        gm_pct = gm_data.get('gross_margin_pct')
        gm_assess = gm_data.get('assessment', '')
        if gm_pct is not None:
            st.metric("Gross Margin", f"{gm_pct:.1f}%")
            gm_assess_color = "#16a34a" if "Excellent" in str(gm_assess) or "Good" in str(gm_assess) else ("#ea580c" if "Adequate" in str(gm_assess) else "#dc2626")
            st.markdown(f'<span style="color:{gm_assess_color};font-weight:600;">{gm_assess}</span>', unsafe_allow_html=True)
            st.caption(f"Benchmark: {gm_data.get('benchmark', '')}")

    with q2:
        st.markdown("#### ARR Growth Estimate")
        arr_growth = arr.get('estimated_arr_growth_pct')
        is_sub = arr.get('is_subscription_business', False)
        arr_assess = arr.get('assessment', '')

        if arr_growth is not None:
            st.metric("Est. ARR Growth (TTM)", f"{arr_growth:.1f}%")
            arr_color = "#16a34a" if arr_growth >= 25 else ("#ea580c" if arr_growth >= 15 else "#dc2626")
            st.markdown(f'<span style="color:{arr_color};font-weight:600;">{arr_assess}</span>', unsafe_allow_html=True)
            st.caption(f"Benchmark: {arr.get('benchmark', '')}")
            if is_sub:
                st.caption(" Subscription/Recurring revenue model detected")
        else:
            st.info("ARR growth cannot be estimated — insufficient quarterly data")
            st.caption(f"Benchmark: {arr.get('benchmark', '')}")
            if is_sub:
                st.caption(" Subscription/Recurring revenue model detected")

        st.markdown("---")
        st.markdown("#### Net Revenue Retention (Estimate)")
        nrr_pct = nrr.get('estimated_nrr_pct')
        nrr_assess = nrr.get('assessment', '')

        if nrr_pct is not None:
            st.metric("Est. NRR", f"{nrr_pct:.0f}%")
            nrr_color = "#16a34a" if nrr_pct >= 106 else ("#ea580c" if nrr_pct >= 100 else "#dc2626")
            st.markdown(f'<span style="color:{nrr_color};font-weight:600;">{nrr_assess}</span>', unsafe_allow_html=True)
            st.caption(f"Benchmark: {nrr.get('benchmark', '')}")
            st.caption("Measured via Revenue Per Share trend (proxy for expansion within existing customers)")
        else:
            st.info("NRR cannot be estimated — requires quarterly revenue + share count data")
            st.caption(f"Benchmark: {nrr.get('benchmark', '')}")
            st.caption("NRR > 106% indicates expansion within existing customer base")

    st.markdown("---")
    st.markdown("#### Earnings Momentum (Zacks-Style Rank)")
    ms1, ms2, ms3 = st.columns([0.3, 0.4, 0.3])
    with ms1:
        st.metric("Momentum Score", f"{momentum.get('momentum_score', 0):+.0f}")
        st.metric("Rank", momentum.get('rank_label', 'N/A'))
        if momentum.get('is_revision_led'):
            st.success("Revision-led momentum — price supported by rising EPS estimates")
    with ms2:
        st.markdown("**Signals**")
        for sig in momentum.get('signals', []):
            st.markdown(f'<small> {sig}</small>', unsafe_allow_html=True)
    with ms3:
        st.markdown("**Momentum Interpretation**")
        rank = momentum.get('zacks_rank', 3)
        if rank == 1:
            st.success("Strong Buy — favorable estimate revisions + price momentum")
        elif rank == 2:
            st.info("Buy — positive momentum signals")
        elif rank == 3:
            st.warning("Hold — mixed or neutral momentum")
        elif rank == 4:
            st.error("Underperform — negative revision trend")
        else:
            st.error("Strong Sell — deteriorating fundamentals")

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
    st.caption("Evaluating the 'Circumvention Delta' — what a competitor must spend to replicate the value proposition.")

    # Main moat rating
    m1, m2 = st.columns([0.6, 0.4])
    with m1:
        st.markdown(f"#### Composite Moat Rating")
        st.markdown(moat_bar(moat_val), unsafe_allow_html=True)
        st.markdown(f"<b>{moat['moat_label']}</b> — {moat.get('benchmark', '')}", unsafe_allow_html=True)
        st.caption("Wide-moat stocks have delivered 11.5% annualized returns since 2007 vs. 8.99% for the broad market.")
    with m2:
        st.markdown("#### AI Integration Depth")
        ai_depth = qual.get('ai_integration_depth', 0)
        ai_depth_labels = {3: 'Deep — Core AI Infrastructure', 2: 'Significant — AI Platform/Models', 1: 'Moderate — AI Applications', 0: 'Limited — Not directly AI-exposed'}
        ai_color = "#8b5cf6" if ai_depth >= 3 else ("#3b82f6" if ai_depth >= 2 else ("#10b981" if ai_depth >= 1 else "#94a3b8"))
        st.markdown(f'<span style="font-size:1.4rem;font-weight:700;color:{ai_color};">{ai_depth_labels.get(ai_depth, "None")}</span>', unsafe_allow_html=True)
        st.caption("Based on business description and industry classification")
        for sig in qual.get('ai_signals', []):
            st.markdown(f'<small> {sig}</small>', unsafe_allow_html=True)

    # ---- Circumvention Delta (formula display) ----
    st.markdown("---")
    st.markdown("#### Circumvention Delta (Moat Architecture)")
    st.caption("The total burden a competitor must take on to match a value proposition: **Time + Capital + Performance Loss**")

    circumvention = moat.get('circumvention_delta', 0)
    circumvention_pct = moat.get('circumvention_delta_pct', 0)
    cd_formula = moat.get('circumvention_delta_formula', '')
    cd_color = "#16a34a" if circumvention >= 9 else ("#ea580c" if circumvention >= 6 else "#dc2626")

    cdx1, cdx2 = st.columns([0.6, 0.4])
    with cdx1:
        st.markdown(f"""
        <div class="alpha-card" style="border-top:3px solid {cd_color};">
            <div class="label">Circumvention Delta Formula</div>
            <div style="font-size:1.1rem;font-weight:700;color:{cd_color};margin-top:6px;">{cd_formula}</div>
            <div class="moat-gauge" style="margin-top:8px;">
                <div class="moat-bar" style="height:12px;">
                    <div class="moat-fill" style="width:{circumvention_pct}%;background:{cd_color};"></div>
                </div>
                <b style="font-size:1.1rem;color:{cd_color};">{circumvention}/{circumvention + (13 - circumvention) if circumvention < 13 else 13}</b>
            </div>
            <div style="font-size:0.72rem;color:#64748b;margin-top:4px;">Maximum defensibility at 13 — measures Time(R&D lag) + Capital(efficiency) + Performance Loss(trust barrier)</div>
        </div>
        """, unsafe_allow_html=True)
    with cdx2:
        # Moat Performance Signal
        perf = qual.get('moat_performance', {})
        perf_signal = perf.get('performance', 'INSUFFICIENT DATA')
        perf_color = perf.get('performance_color', '#6b7280')
        perf_label = perf.get('performance_label', '')

        st.markdown(f"""
        <div class="alpha-card" style="border-top:3px solid {perf_color};">
            <div class="label">Moat Trajectory</div>
            <div style="font-size:1.3rem;font-weight:800;color:{perf_color};margin-top:4px;">{perf_signal}</div>
            <div style="font-size:0.78rem;color:#475569;margin-top:4px;">{perf_label}</div>
        </div>
        """, unsafe_allow_html=True)

        # Moat signal details
        if perf.get('compound_signals'):
            with st.expander(" Compounding Signals"):
                for s in perf['compound_signals']:
                    st.markdown(f"<small>+ {s}</small>", unsafe_allow_html=True)
        if perf.get('decay_signals'):
            with st.expander(" Decaying Signals"):
                for s in perf['decay_signals']:
                    st.markdown(f"<small>- {s}</small>", unsafe_allow_html=True)

    # Three dimensions
    st.markdown("---")
    st.markdown("#### Three Dimensions of Technical Defense")

    d1, d2, d3 = st.columns(3)

    with d1:
        temporal = moat['temporal_width']
        t_color = "#16a34a" if temporal['score'] >= 4 else ("#ea580c" if temporal['score'] >= 3 else ("#ca8a04" if temporal['score'] >= 2 else "#dc2626"))
        st.markdown(f"""
        <div class="alpha-card" style="border-top:3px solid {t_color};">
            <div class="label">Temporal Width</div>
            <div class="value" style="color:{t_color};">{temporal['score']}/5</div>
            <div style="font-size:0.8rem;color:#475569;margin-top:4px;">{temporal['rating']}</div>
            <div style="margin-top:6px;font-size:0.75rem;color:#64748b;">
        """, unsafe_allow_html=True)
        for sig in temporal.get('signals', []):
            st.markdown(f'<small style="display:block;"> {sig}</small>', unsafe_allow_html=True)
        st.markdown('<small style="color:#94a3b8;">R&D time-lag a competitor cannot bridge with capital alone</small></div>', unsafe_allow_html=True)

    with d2:
        efficiency = moat['efficiency_width']
        e_color = "#16a34a" if efficiency['score'] >= 5 else ("#ea580c" if efficiency['score'] >= 3 else ("#ca8a04" if efficiency['score'] >= 1 else "#dc2626"))
        st.markdown(f"""
        <div class="alpha-card" style="border-top:3px solid {e_color};">
            <div class="label">Efficiency Width</div>
            <div class="value" style="color:{e_color};">{efficiency['score']}/5</div>
            <div style="font-size:0.8rem;color:#475569;margin-top:4px;">{efficiency['rating']}</div>
            <div style="margin-top:6px;font-size:0.75rem;color:#64748b;">
        """, unsafe_allow_html=True)
        for sig in efficiency.get('signals', []):
            st.markdown(f'<small style="display:block;"> {sig}</small>', unsafe_allow_html=True)
        st.markdown('<small style="color:#94a3b8;">Performance penalty for competitors using alternative architectures</small></div>', unsafe_allow_html=True)

    with d3:
        trust = moat['trust_width']
        tr_color = "#16a34a" if trust['score'] >= 4 else ("#ea580c" if trust['score'] >= 3 else ("#ca8a04" if trust['score'] >= 2 else "#dc2626"))
        st.markdown(f"""
        <div class="alpha-card" style="border-top:3px solid {tr_color};">
            <div class="label">Trust Width</div>
            <div class="value" style="color:{tr_color};">{trust['score']}/5</div>
            <div style="font-size:0.8rem;color:#475569;margin-top:4px;">{trust['rating']}</div>
            <div style="margin-top:6px;font-size:0.75rem;color:#64748b;">
        """, unsafe_allow_html=True)
        for sig in trust.get('signals', []):
            st.markdown(f'<small style="display:block;"> {sig}</small>', unsafe_allow_html=True)
        st.markdown('<small style="color:#94a3b8;">B2B validation barrier — switching costs + proven standard</small></div>', unsafe_allow_html=True)

    # Technology sovereignty
    st.markdown("---")
    st.markdown("#### Technology Sovereignty")
    for s in qual.get('technology_sovereignty', []):
        st.markdown(f'<small> {s}</small>', unsafe_allow_html=True)

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
    st.markdown("### 2026 Risk Management Playbook")
    st.caption("'Risk management is the differentiator between terminal success and catastrophic drawdown.' — Chief Strategist 2026")

    r1, r2 = st.columns([1, 1])

    with r1:
        st.markdown("#### Position Sizing — 10% NAV Rule")
        position = risk_mgmt['position_sizing']
        action = position['action']
        urgency = position['urgency']

        urgency_color = "#dc2626" if urgency == 'High' else ("#ea580c" if urgency == 'Medium' else "#16a34a")
        st.markdown(f"""
        <div class="alpha-card">
            <div class="label">Current Position Status</div>
            <div style="margin-top:6px;font-size:0.85rem;font-weight:600;color:{urgency_color};">{action}</div>
            <div style="margin-top:4px;font-size:0.75rem;color:#64748b;">Max: {position['max_weight_pct']}% NAV | Current: {position['current_weight_pct']}%</div>
        </div>
        """, unsafe_allow_html=True)

        if position.get('note'):
            st.warning(position['note'])

        st.markdown("#### Mental Stop-Loss")
        ms = risk_mgmt['mental_stop_loss']
        st.markdown(f"""
        <div class="alpha-card">
            <div class="label">Thesis-Break Threshold</div>
            <div style="margin-top:6px;font-size:0.85rem;color:#334155;">{ms['thesis_break_threshold']}</div>
            <div style="margin-top:6px;font-size:0.72rem;color:#94a3b8;">{'Generated from sector rules' if ms.get('is_custom_generated') else 'Framework-specified threshold'}</div>
        </div>
        """, unsafe_allow_html=True)
        st.caption(ms.get('rule', ''))

        # Well-known thresholds for context
        with st.expander("Framework Thresholds for Reference"):
            for t, threshold in {
                'AAPL': 'Exit if iPhone unit growth turns negative for two consecutive quarters',
                'AMZN': 'Exit if AWS growth drops below 14%',
                'MSFT': 'Exit if Azure growth falls below 28%',
                'NVDA': 'Exit if data center growth drops below 50%',
            }.items():
                st.markdown(f"<small><b>{t}:</b> {threshold}</small>", unsafe_allow_html=True)

    with r2:
        st.markdown("#### Risk Factor Assessment")
        for rf in risk_factors.get('risks', []):
            sev_color = {
                'High': '#dc2626', 'Medium': '#ea580c', 'Low': '#16a34a'
            }.get(rf.get('severity', ''), '#6b7280')
            st.markdown(f"""
            <div class="alpha-card" style="margin-bottom:8px;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <b style="font-size:0.82rem;">{rf['factor']}</b>
                    <span class="tag" style="background:{sev_color}20;color:{sev_color};">{rf['severity']}</span>
                </div>
                <div style="font-size:0.78rem;color:#475569;margin-top:4px;">{rf['detail']}</div>
                <div style="font-size:0.72rem;color:#64748b;margin-top:3px;">Mitigation: {rf['mitigation']}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### Risk-Adjusted Position Guidance")
        max_pos = risk_factors.get('max_suggested_position', 10)
        rs = risk_factors.get('risk_score', 0)
        st.markdown(f"""
        <div class="alpha-card">
            <div class="label">Maximum Suggested Position</div>
            <div style="font-size:1.3rem;font-weight:700;color:{'#dc2626' if max_pos <= 3 else ('#ea580c' if max_pos <= 7 else '#16a34a')};">{max_pos}% of NAV</div>
            <div style="font-size:0.75rem;color:#64748b;">Based on risk score: {rs} | Level: {risk_level}</div>
        </div>
        """, unsafe_allow_html=True)

    # Barbell check
    st.markdown("---")
    st.markdown("#### Barbell Portfolio Structure")
    barbell = risk_mgmt['barbell_check']
    bc1, bc2 = st.columns([0.7, 0.3])
    with bc1:
        valid = barbell.get('valid', True)
        bc_color = "#16a34a" if valid else "#ea580c"
        st.markdown(f'<b style="color:{bc_color};">{"✓" if valid else "⚠"} {barbell.get("message", "")}</b>', unsafe_allow_html=True)
        st.caption(barbell.get('target', ''))
    with bc2:
        segments = barbell.get('segments', {})
        if segments:
            st.markdown(f"""
            <small>
            High-Growth: {segments.get('high_growth_pct', 0)}%<br>
            Quality Value: {segments.get('quality_value_pct', 0)}%<br>
            Other: {segments.get('other_pct', 0)}%
            </small>
            """, unsafe_allow_html=True)

# ===== TAB 6: PORTFOLIO CONTEXT =====
with t6:
    st.markdown("### Portfolio Optimization Context")
    st.caption("AI/MPT-style position sizing suggestions based on conviction, correlation, and risk budget.")

    for p in portfolio:
        st.markdown(f"""
        <div class="alpha-card" style="margin-bottom:10px;">
            <div class="label">{p['rule']}</div>
            <div style="font-size:0.85rem;font-weight:600;color:#0f172a;margin-top:4px;">{p['recommendation']}</div>
            <div style="font-size:0.78rem;color:#64748b;margin-top:2px;">{p['detail']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Valuation Context (2026 Benchmarks)")
    info = data['info']
    fwd_pe = info.get('forwardPE')
    tpe = info.get('trailingPE')
    ps = info.get('priceToSales')
    ev_ebitda = info.get('enterpriseToEbitda')
    fcf_yield_val = None
    fcf_val = info.get('freeCashflow')
    mcap_val = info.get('marketCap')
    if fcf_val and mcap_val and mcap_val > 0:
        fcf_yield_val = (fcf_val / mcap_val) * 100

    v1, v2, v3, v4, v5 = st.columns(5)
    with v1:
        fpe_display = f"{fwd_pe:.1f}x" if fwd_pe and fwd_pe > 0 else ("Neg" if fwd_pe and fwd_pe < 0 else "N/A")
        fpe_color = "#16a34a" if (fwd_pe and 0 < fwd_pe < 20) else ("#ea580c" if (fwd_pe and 20 <= fwd_pe < 35) else "#dc2626")
        st.markdown(metric_card("Forward P/E", fpe_display, sub="2026 avg ~22x", color=fpe_color), unsafe_allow_html=True)
    with v2:
        tpe_display = f"{tpe:.1f}x" if tpe and tpe > 0 else ("Neg" if tpe and tpe < 0 else "N/A")
        st.markdown(metric_card("Trailing P/E", tpe_display, sub="2026 avg ~26x"), unsafe_allow_html=True)
    with v3:
        ps_display = f"{ps:.1f}x" if ps else "N/A"
        st.markdown(metric_card("Price/Sales", ps_display), unsafe_allow_html=True)
    with v4:
        ev_ebitda_display = f"{ev_ebitda:.1f}x" if ev_ebitda and ev_ebitda > 0 else "N/A"
        st.markdown(metric_card("EV/EBITDA", ev_ebitda_display), unsafe_allow_html=True)
    with v5:
        fy_display = f"{fcf_yield_val:.1f}%" if fcf_yield_val is not None else "N/A"
        fy_color = "#16a34a" if (fcf_yield_val and fcf_yield_val > 5) else ("#ea580c" if (fcf_yield_val and fcf_yield_val > 0) else "#dc2626")
        st.markdown(metric_card("FCF Yield", fy_display, sub=">5% = attractive", color=fy_color), unsafe_allow_html=True)

    # Deployment strategy
    st.markdown("---")
    st.markdown("#### Suggested Deployment")
    st.info("""
    **Standard 2026 Approach:**
    - Deploy 50% of intended capital as base position at current price
    - Keep 50% as dry powder for -10% dips only
    - Hard cap at the risk-adjusted position limit
    - Review thesis quarterly after every earnings print
    - If the position exceeds the 10% NAV limit: trim, don't hesitate — even Magnificent 7 names gap down
    """)

# ===== TAB 7: CONVICTION =====
with t7:
    st.markdown("### Investment Conviction & Thesis")

    # Conviction banner
    st.markdown(f'<div class="verdict {conv_class}"><h2 style="margin:0;">{conv}</h2><p style="margin:4px 0 0 0;">{thesis["conviction_detail"]}</p></div>', unsafe_allow_html=True)

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
            dir_color = "#059669" if f['Direction'] == 'Bullish' else ("#64748b" if f['Direction'] == 'Neutral' else "#dc2626")
            st.markdown(f"""
            <div class="factor-row">
                <span style="font-weight:700;color:{dir_color};min-width:55px;font-size:0.85rem;">{f['Impact']}</span>
                <span style="font-weight:600;font-size:0.8rem;color:#1e293b;min-width:180px;">{f['Factor']}</span>
                <span style="font-size:0.75rem;color:#64748b;flex:1;">{f['Detail']}</span>
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
    st.caption(f"Not financial advice. Public data via Yahoo Finance. Analysis generated {datetime.now().strftime('%Y-%m-%d %H:%M')} — 2026 Strategic Growth Investment Framework")

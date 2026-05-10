"""
Analytical Alpha Engine — 2026 Strategic Growth Investment Framework
Implements Nature-of-Business (NoB) filters, dual-quadrant analysis,
Circumvention Delta moat architecture, and the 3 Master Forward-Looking Indicators.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import math

# ---------------------------------------------------------------------------
# Core utilities
# ---------------------------------------------------------------------------

def safe_get(func, default=None):
    try:
        return func()
    except Exception:
        return default


def fetch_alpha_data(ticker):
    tkr = yf.Ticker(ticker)
    info = safe_get(lambda: tkr.info, {})

    data = {
        'ticker': ticker.upper(),
        'info': info,
        'price': info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose'),
        'name': info.get('longName') or info.get('shortName', ticker),
        'sector': info.get('sector', 'N/A'),
        'industry': info.get('industry', 'N/A'),
        'description': info.get('longBusinessSummary', 'N/A'),
        'country': info.get('country', 'N/A'),
        'employees': info.get('fullTimeEmployees', 'N/A'),
    }

    data['income_annual'] = safe_get(lambda: tkr.financials)
    data['income_quarterly'] = safe_get(lambda: tkr.quarterly_income_stmt)
    data['balance_sheet'] = safe_get(lambda: tkr.balance_sheet)
    data['cashflow'] = safe_get(lambda: tkr.cashflow)
    price_data = safe_get(lambda: tkr.history(period='5y'))
    data['price_data'] = price_data if (price_data is not None and not price_data.empty) else None

    return data


# ===========================================================================
# NATURE-OF-BUSINESS (NoB) CLASSIFICATION
# ===========================================================================

NoB_TYPES = {
    'high_growth_saas': {
        'name': 'High-Growth SaaS',
        'description': 'Subscription software — Rule of 40, LTV:CAC, CAC payback, NRR retention velocity',
        'icon': '',
        'color': '#3b82f6',
        'metrics_focus': 'Efficiency & compounding — can it scale profitably?',
    },
    'ai_infra_semiconductor': {
        'name': 'AI Infra / Semiconductor',
        'description': 'Chip makers, data center hardware — backlog conversion, revision-led EPS, compute demand',
        'icon': '',
        'color': '#8b5cf6',
        'metrics_focus': 'Throughput & capacity — is compute demand outstripping supply?',
    },
    'energy_industrial': {
        'name': 'Energy & Industrial',
        'description': 'Power, utilities, manufacturing — power pipeline (GW), backlog conversion, CapEx efficiency',
        'icon': '',
        'color': '#f59e0b',
        'metrics_focus': 'Physical capacity & CapEx returns — are assets delivering?',
    },
    'biopharma': {
        'name': 'Biopharma',
        'description': 'Drug development — rNPV, clinical stage, AI-enabled reduced attrition, milestone catalysts',
        'icon': '',
        'color': '#10b981',
        'metrics_focus': 'Milestone alpha — scientific catalysts & probability-weighted value',
    },
    'traditional_value': {
        'name': 'Traditional / Value',
        'description': 'Cyclicals, industrials, materials, financials — P/E, P/B, dividend yield, earnings stability',
        'icon': '',
        'color': '#64748b',
        'metrics_focus': 'Margin of safety — is the price below intrinsic value?',
    },
    'high_growth_general': {
        'name': 'High-Growth (General)',
        'description': 'Revenue growth >15%, may be unprofitable — growth sustainability, TAM, cash runway',
        'icon': '',
        'color': '#2563eb',
        'metrics_focus': 'Growth durability — can it sustain the trajectory?',
    },
}

# Map for sectors that are inherently traditional/cyclical
TRADITIONAL_SECTORS = {
    'basic-materials', 'industrials', 'energy', 'utilities',
    'real-estate', 'consumer-defensive', 'communication-services',
}
TRADITIONAL_INDUSTRIES = {
    'building-materials', 'construction', 'chemicals', 'steel', 'mining',
    'oil-&-gas', 'utilities', 'insurance', 'banks', 'capital-markets',
    'real-estate', 'shipping', 'transportation', 'automotive', 'paper',
    'metals', 'agriculture', 'textile', 'packaging', 'containers',
    'building-products', 'engineering-&-construction', 'infrastructure',
    'cement', 'concrete', 'lumber', 'industrial-distribution',
}
HIGH_GROWTH_INDUSTRIES = {
    'software-infrastructure', 'software-application', 'internet-content-&-information',
    'cloud-computing', 'cybersecurity', 'artificial-intelligence',
    'semiconductors', 'semiconductor-equipment-&-materials',
    'biotechnology', 'drug-manufacturers', 'renewable-energy-technology',
    'electric-vehicles', 'fintech', 'digital-payments', 'e-commerce',
}


def classify_business_model(ticker, info):
    """Classify a company into its Nature-of-Business (NoB) type.
    Uses industry classification + financial profile (growth, margins) to determine
    the right valuation framework."""
    ticker_upper = ticker.upper()
    desc = (info.get('longBusinessSummary') or '').lower()
    industry_raw = (info.get('industry') or '')
    industry = industry_raw.lower().replace(' - ', '-').replace(' ', '-')
    sector = (info.get('sector') or '').lower().replace(' ', '-')

    # Financial profile signals
    rev_growth = info.get('revenueGrowth')  # decimal, e.g. 0.25 = 25%
    gm = info.get('grossMargins')  # decimal, e.g. 0.75 = 75%
    fwd_pe = info.get('forwardPE')
    tpe = info.get('trailingPE')
    ps = info.get('priceToSales')
    fcf = info.get('freeCashflow')
    beta = info.get('beta')
    div_yield = info.get('dividendYield')

    is_high_growth = (rev_growth is not None and rev_growth > 0.15)
    is_high_margin = (gm is not None and gm > 0.60)
    is_low_margin = (gm is not None and gm < 0.30)
    is_unprofitable = (tpe is not None and tpe < 0) or (fcf is not None and fcf < 0)
    is_high_ps = (ps is not None and ps > 10)
    is_low_ps = (ps is not None and ps < 2)

    # ---- Biopharma ----
    if industry in ('biotechnology', 'drug-manufacturers', 'pharmaceutical',
                    'medical-devices', 'diagnostics', 'life-sciences'):
        return 'biopharma'
    if sector == 'healthcare':
        bio_kw = ['biotechnology', 'pharmaceutical', 'drug', 'therapy', 'gene',
                  'clinical-trial', 'antibody', 'biopharma', 'biologic']
        if any(kw in desc for kw in bio_kw):
            return 'biopharma'

    # ---- High-Growth SaaS / Software (industry-first) ----
    if industry in ('software-infrastructure', 'software-application',
                    'information-technology-services', 'software',
                    'cybersecurity', 'internet-content-&-information'):
        return 'high_growth_saas'

    # ---- AI Infra / Semiconductor (industry-first) ----
    if industry in ('semiconductors', 'semiconductor-equipment-&-materials',
                    'computer-hardware', 'electronic-components',
                    'hardware-storage-&-peripherals'):
        return 'ai_infra_semiconductor'

    # ---- Energy & Industrial (check BEFORE Traditional) ----
    if sector in ('energy', 'utilities'):
        return 'energy_industrial'
    energy_industries = ('electrical-equipment-&-parts', 'renewable-energy',
                         'renewable-energy-technology', 'solar', 'nuclear',
                         'utilities-renewable', 'utilities-regulated-electric',
                         'utilities-regulated-gas', 'utilities-diversified',
                         'specialty-industrial-machinery',
                         'oil-&-gas', 'oil-&-gas-equipment', 'oil-&-gas-integrated',
                         'oil-&-gas-e&p', 'oil-&-gas-midstream',
                         'energy', 'independent-power-producers')
    if industry in energy_industries:
        return 'energy_industrial'
    # Also check: companies in Industrials sector that are energy-related
    if sector == 'industrials':
        energy_kw = ['energy', 'power', 'fuel-cell', 'solar', 'wind', 'nuclear',
                     'turbine', 'grid', 'renewable', 'generator', 'generation',
                     'data-center-power', 'electrification', 'electricity',
                     'hydrogen', 'battery', 'storage']
        if any(kw in desc for kw in energy_kw):
            return 'energy_industrial'

    # ---- Traditional / Value (industry-first, then financials) ----
    if industry in TRADITIONAL_INDUSTRIES or sector in TRADITIONAL_SECTORS:
        # High growth with decent margins → growth company, not traditional
        if is_high_growth and (is_high_margin or (gm is not None and gm > 0.15)):
            return 'high_growth_general'
        # Unprofitable high-growth (EVs, biotech, etc.)
        if is_high_growth and is_unprofitable:
            return 'high_growth_general'
        return 'traditional_value'

    # ---- Financial / Banks → Traditional ----
    if sector == 'financial-services' or industry in ('banks', 'banks-diversified',
                                                      'insurance', 'capital-markets',
                                                      'credit-services', 'mortgage',
                                                      'asset-management'):
        return 'traditional_value'

    # ---- Tech sector companies not in specific industries ----
    if sector == 'technology':
        # Count signals
        growth_signals = 0
        value_signals = 0
        if is_high_growth: growth_signals += 1
        if is_high_margin: growth_signals += 1
        if is_high_ps: growth_signals += 1
        if is_unprofitable: growth_signals += 1  # unprofitable growth = typical young tech
        if is_low_margin: value_signals += 1
        if is_low_ps: value_signals += 1
        if div_yield and div_yield > 0.02: value_signals += 1
        if tpe and 0 < tpe < 15: value_signals += 1

        # Check description for SaaS/cloud signals
        saas_kw = ['software', 'saas', 'subscription', 'recurring', 'cloud', 'platform',
                   'cybersecurity', 'security', 'network-security', 'endpoint']
        if any(kw in desc for kw in saas_kw) and is_high_margin:
            return 'high_growth_saas'

        hard_kw = ['semiconductor', 'chip', 'gpu', 'processor', 'memory', 'server',
                   'data-center', 'networking', 'hpc', 'accelerator']
        if any(kw in desc for kw in hard_kw):
            return 'ai_infra_semiconductor'

        if growth_signals > value_signals:
            return 'high_growth_general'
        return 'traditional_value'

    # ---- Catch-all: use financial profile ----
    if is_high_growth:
        # Any company growing >15% gets the growth framework
        if is_high_margin or is_unprofitable:
            tech_kw = ['software', 'subscription', 'saas', 'cloud', 'ai', 'platform',
                       'digital', 'app', 'online', 'tech', 'data']
            if any(kw in desc for kw in tech_kw):
                return 'high_growth_saas' if is_high_margin else 'high_growth_general'
            return 'high_growth_general'
        # Moderate-margin high growth (e.g., TSLA, EV companies)
        return 'high_growth_general'

    if is_low_margin and not is_high_growth:
        return 'traditional_value'

    return 'traditional_value'


# ===========================================================================
# NoB-SPECIFIC FILTERS
# ===========================================================================

def saas_efficiency_filter(data):
    """SaaS & Cloud Model: Efficiency & Compounding.
    Evaluates Rule of 40 (FCF), LTV:CAC, CAC Payback, and Retention Velocity."""
    info = data['info']
    inc = data['income_annual']
    cf = data['cashflow']

    # --- Rule of 40 (FCF basis) ---
    rev_growth = info.get('revenueGrowth')
    rg_pct = (rev_growth * 100) if rev_growth is not None else None
    fcf = info.get('freeCashflow')
    rev_ttm = None
    if inc is not None and not inc.empty:
        for row in ['Total Revenue', 'Operating Revenue']:
            if row in inc.index and len(inc.columns) > 0:
                rev_ttm = inc.loc[row, inc.columns[0]]
                if pd.notna(rev_ttm) and rev_ttm > 0:
                    break
    fcf_margin_pct = (fcf / rev_ttm * 100) if (fcf and rev_ttm and rev_ttm > 0) else None
    rule_40_fcf = (rg_pct + fcf_margin_pct) if (rg_pct is not None and fcf_margin_pct is not None) else None

    # R40 assessment
    r40_assessment = None
    if rule_40_fcf is not None:
        if rule_40_fcf >= 50:
            r40_assessment = "Elite — premium SaaS valuation fully warranted"
        elif rule_40_fcf >= 40:
            r40_assessment = "Strong — meets the 2026 SaaS benchmark"
        elif rule_40_fcf >= 30:
            r40_assessment = "Adequate — borderline for SaaS growth premium"
        else:
            r40_assessment = "Below standard — growth not justifying cash consumption"

    # --- LTV:CAC Ratio Estimation ---
    # LTV ≈ (Gross Margin × ARPU) / Churn Rate
    # CAC ≈ Sales & Marketing / New Customers
    # We use gross margin as proxy for LTV quality and S&M/Revenue as proxy for CAC efficiency
    gm = info.get('grossMargins')
    gm_pct = (gm * 100) if gm is not None else None

    # Estimate S&M as % of revenue
    sga = info.get('sellingGeneralAndAdministrative')
    total_opex = None
    if inc is not None and not inc.empty:
        for row in ['Selling General And Administration', 'Selling General Administrative']:
            if row in inc.index and len(inc.columns) > 0:
                total_opex = inc.loc[row, inc.columns[0]]
                break
    opex_ratio = (total_opex / rev_ttm) if (total_opex and rev_ttm and rev_ttm > 0) else None

    # LTV:CAC estimate — simplified: (GM / implied churn) / (S&M ratio / customers)
    # Rule of thumb: high GM + low S&M spend relative to growth = good LTV:CAC
    ltv_cac_estimate = None
    ltv_cac_detail = None
    if gm_pct is not None and rg_pct is not None:
        # Crude proxy: GM% relative to revenue growth efficiency
        if opex_ratio is not None and opex_ratio > 0:
            efficiency = (rg_pct / (opex_ratio * 100)) if opex_ratio > 0 else 0
            if gm_pct > 70:
                ltv_cac_estimate = min(15, 3 + efficiency * 3) if efficiency > 0 else None
            elif gm_pct > 50:
                ltv_cac_estimate = min(10, 2 + efficiency * 2) if efficiency > 0 else None
            else:
                ltv_cac_estimate = max(0.5, efficiency * 1.5) if efficiency > 0 else None
            ltv_cac_detail = "Estimated from gross margin efficiency and S&M spend ratio — approximate proxy"

    ltv_cac_assessment = None
    if ltv_cac_estimate is not None:
        if ltv_cac_estimate >= 5:
            ltv_cac_assessment = ">5:1 — possible under-investment in growth (consider increasing S&M)"
        elif ltv_cac_estimate >= 3:
            ltv_cac_assessment = "≥3:1 — scalable economics, healthy efficiency"
        elif ltv_cac_estimate >= 2:
            ltv_cac_assessment = "2-3:1 — marginal, high-friction customer acquisition"
        else:
            ltv_cac_assessment = "<2:1 — unsustainable economics"

    # --- CAC Payback Period Estimation ---
    cac_payback_months = None
    cac_payback_detail = None
    if opex_ratio is not None and gm is not None and gm > 0:
        # CAC Payback ≈ S&M spend ratio / monthly gross margin per dollar
        # S&M % of revenue ÷ (gross margin / 12) = months to recoup
        implied_payback = (opex_ratio * 12) / gm
        cac_payback_months = round(min(60, max(2, implied_payback)), 1) if implied_payback > 0 else None
        cac_payback_detail = "Estimated from S&M ratio and gross margin — proxy only"

    cac_assessment = None
    if cac_payback_months is not None:
        if cac_payback_months <= 12:
            cac_assessment = f"≤12 months — high capital efficiency, best-in-class"
        elif cac_payback_months <= 18:
            cac_assessment = f"12-18 months — meets 2026 industry median"
        elif cac_payback_months <= 24:
            cac_assessment = f"18-24 months — above median, moderate efficiency"
        else:
            cac_assessment = f">24 months — concerning, capital-intensive customer acquisition"

    # --- Retention Velocity (NRR > 106%) ---
    # (handled by the shared NRR function, referenced below)

    # --- Gross Margin benchmark ---
    gm_benchmark = None
    if gm_pct is not None:
        if gm_pct >= 75:
            gm_benchmark = "Excellent — exceeds SaaS 75% benchmark"
        elif gm_pct >= 60:
            gm_benchmark = "Good — above average for SaaS"
        elif gm_pct >= 40:
            gm_benchmark = "Adequate — room for improvement"
        else:
            gm_benchmark = "Below SaaS standard"

    return {
        'business_model': 'SaaS & Cloud',
        'rule_40_fcf': rule_40_fcf,
        'rule_40_assessment': r40_assessment,
        'gross_margin_pct': gm_pct,
        'gm_benchmark': gm_benchmark,
        'ltv_cac_ratio': round(ltv_cac_estimate, 1) if ltv_cac_estimate is not None else None,
        'ltv_cac_detail': ltv_cac_detail,
        'ltv_cac_assessment': ltv_cac_assessment,
        'cac_payback_months': round(cac_payback_months, 1) if cac_payback_months is not None else None,
        'cac_payback_detail': cac_payback_detail,
        'cac_payback_assessment': cac_assessment,
        'saas_benchmarks': {
            'rule_of_40': '≥40 (FCF basis)',
            'ltv_cac': '≥3:1 (minimum for scalable economics)',
            'cac_payback': '≤12 months (best-in-class), ≤18 months (median)',
            'nrr': '>106% (platform stickiness signal)',
            'gross_margin': '≥75% (efficient service delivery)',
        },
    }


def industrial_throughput_filter(data):
    """AI Infrastructure & Industrials: Throughput & Capacity.
    Evaluates backlog conversion velocity, revision-led EPS growth, and power pipeline."""
    info = data['info']
    bs = data['balance_sheet']
    inc = data['income_annual']
    inc_q = data['income_quarterly']

    # --- Revenue growth (throughput proxy) ---
    rev_growth = info.get('revenueGrowth')
    rg_pct = (rev_growth * 100) if rev_growth is not None else None

    # --- Backlog Conversion Velocity ---
    # We use RPO growth as proxy for backlog
    rpo_data = rpo_analysis(data)
    backlog_growth = rpo_data.get('rpo_growth_pct')
    backlog_signal = rpo_data.get('leading_indicator_signal')

    backlog_assessment = None
    if backlog_growth is not None:
        if backlog_growth > 50:
            backlog_assessment = f"Explosive — backlog growing {backlog_growth:.0f}% YoY, data center equipment backlogs up 100%+ in 2026"
        elif backlog_growth > 20:
            backlog_assessment = f"Strong — backlog growing at {backlog_growth:.0f}%, healthy pipeline"
        elif backlog_growth > 0:
            backlog_assessment = f"Moderate — backlog growing, conversion rate is key"
        else:
            backlog_assessment = "Concerning — backlog may be depleting"

    # Conversion velocity: revenue growth vs backlog growth
    conversion_velocity = None
    conversion_assessment = None
    if rg_pct is not None and backlog_growth is not None and backlog_growth > 0:
        conversion_velocity = rg_pct / backlog_growth
        if 0.8 <= conversion_velocity <= 1.2:
            conversion_assessment = "Balanced — converting backlog in line with new bookings"
        elif conversion_velocity > 1.2:
            conversion_assessment = "Accelerating — converting backlog faster than new bookings (watch depletion)"
        else:
            conversion_assessment = "Building — accumulating backlog faster than converting (future revenue acceleration)"

    # --- Revision-Led EPS Growth ---
    eps_trailing = info.get('trailingEps')
    eps_forward = info.get('forwardEps')
    eps_growth = info.get('earningsGrowth')
    fwd_pe = info.get('forwardPE')
    price = data.get('price')
    target_mean = info.get('targetMeanPrice')
    recommendation = info.get('recommendationKey', '')

    revision_score = 0
    revision_signals = []

    if eps_forward and eps_trailing and eps_trailing > 0:
        eps_fwd_growth = ((eps_forward / eps_trailing) - 1) * 100
        if eps_fwd_growth > 30:
            revision_score += 3
            revision_signals.append(f"Forward EPS growth +{eps_fwd_growth:.0f}% — strong upward revisions")
        elif eps_fwd_growth > 15:
            revision_score += 2
            revision_signals.append(f"Forward EPS growth +{eps_fwd_growth:.0f}%")
        elif eps_fwd_growth > 0:
            revision_score += 1
        elif eps_fwd_growth < 0:
            revision_score -= 1
            revision_signals.append("EPS estimates declining")

    if eps_growth is not None:
        if eps_growth > 0.30:
            revision_score += 2
            revision_signals.append(f"Historical EPS growth strong ({eps_growth*100:.0f}%)")
        elif eps_growth < -0.10:
            revision_score -= 1

    rec_map = {'strong_buy': 3, 'buy': 2, 'hold': 0, 'underperform': -2, 'sell': -3}
    if recommendation in rec_map:
        revision_score += rec_map[recommendation]

    if target_mean and price and price > 0:
        upside = ((target_mean / price) - 1) * 100
        if upside > 20:
            revision_score += 2
        elif upside > 5:
            revision_score += 1

    revision_rank = None
    if revision_score >= 6:
        revision_rank = "#1 Strong Buy — price appreciation driven by upward analyst revisions"
    elif revision_score >= 3:
        revision_rank = "#2 Buy — revision-led momentum"
    elif revision_score >= 0:
        revision_rank = "#3 Hold"
    else:
        revision_rank = "#4/5 — negative revision trend"

    is_revision_led = revision_score >= 4 and eps_forward is not None and eps_trailing is not None and eps_forward > eps_trailing

    # --- Power Pipeline / Capacity ---
    power_pipeline_note = None
    desc = (info.get('longBusinessSummary') or '').lower()
    industry_norm = (info.get('industry') or '').lower().replace(' - ', '-').replace(' ', '-')
    is_energy_sector = any(kw in industry_norm for kw in ['energy', 'utility', 'renewable', 'solar', 'nuclear', 'electrical'])
    is_semiconductor = 'semiconductor' in industry_norm
    if is_energy_sector or (any(kw in desc for kw in ['fuel cell', 'power plant', 'grid operator', 'electric utility',
                                                       'energy generation', 'power generation']) and not is_semiconductor):
        mcap = info.get('marketCap')
        if mcap and mcap > 50e9:
            power_pipeline_note = 'Large-cap energy infrastructure — monitor GW pipeline announcements. Top-tier providers maintain 21+ GW pipelines.'
        elif mcap:
            power_pipeline_note = 'Energy/industrial play — key metric is power pipeline capacity (GW). NextEra benchmark: 21 GW pipeline, 33 GW project backlog.'

    return {
        'business_model': 'AI Infrastructure & Industrials',
        'revenue_growth_pct': rg_pct,
        'backlog_growth_pct': backlog_growth,
        'backlog_signal': backlog_signal,
        'backlog_assessment': backlog_assessment,
        'conversion_velocity': round(conversion_velocity, 2) if conversion_velocity is not None else None,
        'conversion_assessment': conversion_assessment,
        'revision_led_eps': {
            'score': revision_score,
            'rank': revision_rank,
            'is_revision_led': is_revision_led,
            'signals': revision_signals,
        },
        'power_pipeline_note': power_pipeline_note,
        'industrial_benchmarks': {
            'backlog_growth': '>20% YoY (data center equipment: 100%+ in 2026)',
            'conversion_velocity': '0.8-1.2x (balanced conversion)',
            'eps_revision': 'Zacks Rank #1 (Strong Buy) — revision-led',
            'power_pipeline': '>21 GW for top-tier energy providers',
        },
    }


def biopharma_milestone_filter(data):
    """Biopharma & Life Sciences: Milestone Alpha.
    Evaluates rNPV framework, clinical stage, and AI-enabled reduced attrition."""
    info = data['info']
    desc = (info.get('longBusinessSummary') or '').lower()

    # --- Pipeline Stage Assessment ---
    clinical_stage = 'Unknown'
    stage_indicators = {
        'preclinical': ['preclinical', 'pre-clinical', 'discovery', 'lead optimization'],
        'phase_1': ['phase 1', 'phase i ', 'phase 1/2', 'first-in-human', 'safety study'],
        'phase_2': ['phase 2', 'phase ii ', 'phase 2/3', 'proof-of-concept', 'dose-finding'],
        'phase_3': ['phase 3', 'phase iii ', 'pivotal', 'registrational', 'registration'],
        'commercial': ['commercial', 'approved', 'marketed', 'fda approved', 'regulatory approval'],
    }
    for stage, indicators in stage_indicators.items():
        for kw in indicators:
            if kw in desc:
                clinical_stage = stage
                break
        if clinical_stage != 'Unknown':
            break

    # --- Discount Rate Estimation (rNPV framework) ---
    discount_rate = None
    stage_discount_rates = {
        'preclinical': 0.40,
        'phase_1': 0.35,
        'phase_2': 0.25,
        'phase_3': 0.15,
        'commercial': 0.10,
        'Unknown': 0.30,
    }
    discount_rate = stage_discount_rates.get(clinical_stage, 0.30)

    # --- AI-Enabled Reduced Attrition ---
    ai_biopharma_signals = []
    ai_attrition_premium = False
    ai_kw_list = [
        'artificial intelligence', 'machine learning', 'ai-driven', 'ai-enabled',
        'computational', 'in silico', 'molecular dynamics', 'deep learning',
        'ai platform', 'schrodinger', 'recursion', 'atomwise', 'benevolentai',
        'ai/m', 'digital', 'data-driven', 'predictive model',
    ]
    for kw in ai_kw_list:
        if kw in desc:
            ai_biopharma_signals.append(f"AI integration: {kw}")
            ai_attrition_premium = True
            break

    # Known AI-native biopharma companies
    ticker_upper = data['ticker'].upper()
    ai_native_biopharma = ['SDGR', 'RXRX', 'ABCL', 'ROIV', 'DNA', 'EXAI', 'ABSI']
    if ticker_upper in ai_native_biopharma:
        ai_attrition_premium = True
        ai_biopharma_signals.append("AI-native drug discovery platform")

    if not ai_biopharma_signals:
        ai_biopharma_signals.append("No AI integration detected — standard attrition risk applies")

    # --- Revenue / Pipeline value ---
    rev_growth = info.get('revenueGrowth')
    rg_pct = (rev_growth * 100) if rev_growth is not None else None

    mcap = info.get('marketCap')
    rev_ttm = None
    inc = data['income_annual']
    if inc is not None and not inc.empty:
        for row in ['Total Revenue', 'Operating Revenue']:
            if row in inc.index and len(inc.columns) > 0:
                rev_ttm = inc.loc[row, inc.columns[0]]
                break

    # rNPV note
    rnpv_note = (
        f"rNPV framework: apply ~{discount_rate*100:.0f}% discount rate for {clinical_stage.replace('_', ' ').title()} stage. "
        f"{'AI integration may reduce effective discount rate by 5-10pp due to higher success rates.' if ai_attrition_premium else ''}"
    )

    # Revenue vs market cap
    price_to_pipeline = None
    if mcap and rev_ttm and rev_ttm > 0:
        price_to_pipeline = mcap / rev_ttm

    return {
        'business_model': 'Biopharma & Life Sciences',
        'clinical_stage': clinical_stage.replace('_', ' ').title(),
        'discount_rate_pct': discount_rate * 100,
        'rnpv_note': rnpv_note,
        'ai_attrition_premium': ai_attrition_premium,
        'ai_biopharma_signals': ai_biopharma_signals,
        'revenue_growth_pct': rg_pct,
        'price_to_revenue': round(price_to_pipeline, 1) if price_to_pipeline is not None else None,
        'biopharma_benchmarks': {
            'rnpv': 'Risk-Adjusted NPV — probability-weighted cash flows based on trial phase',
            'discount_rate': f'{clinical_stage.replace("_", " ").title()}: ~{discount_rate*100:.0f}% (40% preclinical → 15% Phase 3)',
            'ai_premium': 'AI-enabled programs show materially higher success rates in 2026',
            'catalyst': 'Upcoming clinical readouts, FDA decisions, partnership announcements',
        },
    }


def gross_margin_efficiency(data):
    """Standard gross margin evaluation (used by all NoB types)."""
    info = data['info']
    gm = info.get('grossMargins')
    assessment = None
    if gm is not None:
        gm_pct = gm * 100
        if gm_pct >= 75:
            assessment = "Excellent — efficient service delivery, strong pricing power"
        elif gm_pct >= 60:
            assessment = "Good — above-average efficiency"
        elif gm_pct >= 40:
            assessment = "Adequate — room for improvement"
        elif gm_pct >= 20:
            assessment = "Thin — vulnerable to cost pressure"
        elif gm_pct > 0:
            assessment = "Very thin — commodity-like economics"
        else:
            assessment = "Unsustainable — negative unit economics"
    return {
        'gross_margin_pct': gm * 100 if gm is not None else None,
        'benchmark': '≥75% (software), ≥40% (general)',
        'assessment': assessment,
    }


def arr_growth_estimate(data):
    """Estimate ARR growth from quarterly revenue trends."""
    info = data['info']
    inc_q = data['income_quarterly']
    desc = (info.get('longBusinessSummary') or '').lower()
    is_subscription = any(kw in desc for kw in [
        'subscription', 'recurring revenue', 'arr', 'annual recurring',
        'saas', 'software-as-a-service', 'cloud', 'platform'
    ])
    arr_growth = None
    quarterly_growth_rates = []
    if inc_q is not None and not inc_q.empty:
        for row in ['Total Revenue', 'Operating Revenue']:
            if row in inc_q.index:
                revs = []
                for col in inc_q.columns[:8]:
                    val = inc_q.loc[row, col]
                    if pd.notna(val) and val > 0:
                        revs.append(val)
                if len(revs) >= 4:
                    ttm_current = sum(revs[:4])
                    ttm_prior = sum(revs[4:8]) if len(revs) >= 8 else sum(revs[4:])
                    if ttm_prior > 0:
                        arr_growth = ((ttm_current / ttm_prior) - 1) * 100
                if len(revs) >= 2:
                    for i in range(len(revs) - 1):
                        if revs[i + 1] > 0:
                            quarterly_growth_rates.append(((revs[i] / revs[i + 1]) - 1) * 100)
                break
    # Cap at 200% — quarterly revenue trends can overshoot for hyper-growth
    if arr_growth is not None and arr_growth > 200:
        arr_growth = 200.0

    assessment = None
    if arr_growth is not None:
        if arr_growth >= 30:
            assessment = "Hyper-growth — typical of top-quartile VC-backed SaaS"
        elif arr_growth >= 25:
            assessment = "Strong growth — at the 2026 VC-backed benchmark"
        elif arr_growth >= 15:
            assessment = "Healthy growth — scaling sustainably"
        elif arr_growth >= 5:
            assessment = "Moderate growth — may be maturing"
        elif arr_growth >= 0:
            assessment = "Flat — no organic expansion"
        else:
            assessment = "Declining — losing customers or pricing power"
    return {
        'is_subscription_business': is_subscription,
        'estimated_arr_growth_pct': arr_growth,
        'quarterly_growth_rates': quarterly_growth_rates,
        'benchmark': '≥25-30% (VC-backed), ≥15% (public)',
        'assessment': assessment,
    }


# ===========================================================================
# 3 MASTER FORWARD-LOOKING INDICATORS (shared across all NoB types)
# ===========================================================================

MASTER_INDICATORS_DESCRIPTION = {
    'rpo': {
        'name': 'Remaining Performance Obligations (RPO)',
        'summary': 'Contracted revenue not yet on the income statement — deferred revenue + backlog.',
        'forward_logic': 'If RPO growth > revenue growth, it acts as a leading indicator that revenue will accelerate in the coming quarters.',
        'key_threshold': 'RPO growth exceeding revenue growth by 5%+',
    },
    'nrr': {
        'name': 'Net Retention Rate (NRR)',
        'summary': 'How much existing customers spent this year vs. last year.',
        'forward_logic': 'High NRR (>120%) means "installed growth" — even with zero new customers, the business grows 20% next year from current clients expanding.',
        'key_threshold': '≥120% = installed growth engine, ≥106% = benchmark',
    },
    'forward_rule_of_40': {
        'name': 'Forward Rule of 40',
        'summary': 'Using analyst estimates for next year\'s revenue growth and FCF margins.',
        'forward_logic': 'The market prices stocks on future cash flows. A company with a failing Trailing Rule of 40 today could have a passing Forward Rule of 40 — the inflection point to buy before the market notices.',
        'key_threshold': 'Forward Rule of 40 ≥ 40, especially when Trailing < 40',
    },
}


def rpo_analysis(data):
    """Calculate Remaining Performance Obligations (RPO) — deferred revenue + backlog."""
    info = data['info']
    bs = data['balance_sheet']
    inc = data['income_annual']

    deferred_rev_current = None
    deferred_rev_noncurrent = None
    deferred_rev_labels = [
        'Deferred Revenue', 'Deferred Revenue Current',
        'Current Deferred Revenue', 'Current Accrued Expenses',
        'Unearned Revenue', 'Contract Liabilities',
        'Customer Advances', 'Deferred Income'
    ]
    if bs is not None and not bs.empty:
        bs_lower = {k.lower(): k for k in bs.index}
        for label in deferred_rev_labels:
            if label.lower() in bs_lower:
                actual_key = bs_lower[label.lower()]
                if len(bs.columns) >= 1:
                    val = bs.loc[actual_key, bs.columns[0]]
                    if pd.notna(val) and val > 0:
                        deferred_rev_current = val
                        break
        noncurrent_labels = [
            'Deferred Revenue Non Current', 'Non Current Deferred Revenue',
            'Deferred Revenue Long Term', 'Long Term Deferred Revenue',
            'Contract Liabilities Non Current'
        ]
        for label in noncurrent_labels:
            if label.lower() in bs_lower:
                actual_key = bs_lower[label.lower()]
                if len(bs.columns) >= 1:
                    val = bs.loc[actual_key, bs.columns[0]]
                    if pd.notna(val) and val > 0:
                        deferred_rev_noncurrent = val
                        break

    total_rpo = None
    if deferred_rev_current is not None:
        total_rpo = deferred_rev_current
        if deferred_rev_noncurrent is not None:
            total_rpo += deferred_rev_noncurrent

    rpo_prior = None
    rpo_growth_pct = None
    if bs is not None and not bs.empty and deferred_rev_current is not None:
        bs_lower = {k.lower(): k for k in bs.index}
        for label in deferred_rev_labels:
            if label.lower() in bs_lower:
                actual_key = bs_lower[label.lower()]
                if len(bs.columns) >= 2:
                    prior_val = bs.loc[actual_key, bs.columns[1]]
                    if pd.notna(prior_val) and prior_val > 0:
                        rpo_prior = prior_val
                        for nl in ['Deferred Revenue Non Current', 'Non Current Deferred Revenue',
                                     'Deferred Revenue Long Term', 'Long Term Deferred Revenue']:
                            if nl.lower() in bs_lower:
                                nk = bs_lower[nl.lower()]
                                prior_nc = bs.loc[nk, bs.columns[1]]
                                if pd.notna(prior_nc) and prior_nc > 0:
                                    rpo_prior += prior_nc
                        rpo_growth_pct = ((total_rpo / rpo_prior) - 1) * 100
                break

    rev_growth = info.get('revenueGrowth')
    rev_growth_pct = (rev_growth * 100) if rev_growth is not None else None

    signal = None
    signal_detail = None
    if rpo_growth_pct is not None and rev_growth_pct is not None:
        if rpo_growth_pct > rev_growth_pct + 5:
            signal = "STRONG LEAD"
            signal_detail = f"RPO growing at {rpo_growth_pct:.0f}% vs revenue at {rev_growth_pct:.0f}% — contracted backlog suggests revenue acceleration ahead"
        elif rpo_growth_pct > rev_growth_pct:
            signal = "MODEST LEAD"
            signal_detail = f"RPO growing at {rpo_growth_pct:.0f}% vs revenue at {rev_growth_pct:.0f}% — slight leading edge"
        elif rpo_growth_pct < rev_growth_pct - 5:
            signal = "LAGGING"
            signal_detail = f"RPO growth ({rpo_growth_pct:.0f}%) trailing revenue growth ({rev_growth_pct:.0f}%) — backlog may be depleting"
        else:
            signal = "ALIGNED"
            signal_detail = "RPO and revenue growth roughly aligned"

    return {
        'deferred_revenue_current': deferred_rev_current,
        'deferred_revenue_noncurrent': deferred_rev_noncurrent,
        'total_rpo_estimate': total_rpo,
        'rpo_prior_year': rpo_prior,
        'rpo_growth_pct': rpo_growth_pct,
        'revenue_growth_pct': rev_growth_pct,
        'leading_indicator_signal': signal,
        'signal_detail': signal_detail,
        'benchmark': 'RPO growth > revenue growth = leading indicator of acceleration',
    }


def net_revenue_retention_estimate(data):
    """Calculate NRR via Revenue Per Share trend (proxy).
    High NRR (>120%) = 'installed growth' — business grows even with zero new customers."""
    info = data['info']
    inc_q = data['income_quarterly']
    nrr_estimate = None
    revenue_per_share_trend = []

    shares = None
    if inc_q is not None and not inc_q.empty:
        for row in ['Diluted Average Shares', 'Basic Average Shares']:
            if row in inc_q.index and len(inc_q.columns) >= 2:
                shares = [inc_q.loc[row, col] for col in inc_q.columns[:8] if pd.notna(inc_q.loc[row, col])]
                break

    if shares and len(shares) >= 4:
        revs = None
        if inc_q is not None:
            for row in ['Total Revenue', 'Operating Revenue']:
                if row in inc_q.index:
                    revs = [inc_q.loc[row, col] for col in inc_q.columns[:min(8, len(inc_q.columns))]
                            if pd.notna(inc_q.loc[row, col])]
                    break
        if revs and len(revs) >= 4:
            min_len = min(len(revs), len(shares))
            for i in range(min_len):
                if shares[i] > 0:
                    rps = revs[i] / shares[i]
                    revenue_per_share_trend.append(rps)
            if len(revenue_per_share_trend) >= 4:
                ttm_rps_current = sum(revenue_per_share_trend[:4])
                ttm_rps_prior = sum(revenue_per_share_trend[4:8]) if len(revenue_per_share_trend) >= 8 else sum(revenue_per_share_trend[4:])
                if ttm_rps_prior > 0:
                    nrr_estimate = (ttm_rps_current / ttm_rps_prior) * 100

    # Cap at 200% — revenue-per-share proxy can overshoot for hyper-growth companies
    nrr_capped = False
    if nrr_estimate is not None and nrr_estimate > 200:
        nrr_estimate = 200.0
        nrr_capped = True

    assessment = None
    installed_growth_note = None
    if nrr_estimate is not None:
        if nrr_estimate >= 130:
            assessment = "World-class — massive expansion within existing customers"
            installed_growth_note = "Even with ZERO new customers, revenue grows 30%+ next year from existing clients expanding"
        elif nrr_estimate >= 120:
            assessment = "Exceptional — 'installed growth' engine: 20%+ organic expansion guaranteed"
            installed_growth_note = "Even with ZERO new customers, revenue grows ~20% next year from existing clients expanding"
        elif nrr_estimate >= 106:
            assessment = "Healthy — above the 2026 benchmark of 106%"
            installed_growth_note = "Existing customers are expanding — organic growth is built in"
        elif nrr_estimate >= 100:
            assessment = "Stable — maintaining existing revenue, no expansion"
            installed_growth_note = "No organic expansion from existing base — growth depends entirely on new customers"
        elif nrr_estimate >= 90:
            assessment = "Concerning — shrinking within existing accounts"
            installed_growth_note = "Existing customers are contracting — new customer acquisition must overcome the leakage"
        else:
            assessment = "Critical — significant customer contraction"
            installed_growth_note = "Severe churn/contraction — business may be structurally declining"

    return {
        'estimated_nrr_pct': nrr_estimate,
        'nrr_capped': nrr_capped,
        'revenue_per_share_trend': revenue_per_share_trend,
        'benchmark': '≥106% (standard), ≥120% (installed growth engine)',
        'assessment': assessment,
        'installed_growth_note': installed_growth_note,
        'why_forward_looking': "High NRR means 'installed growth' — the company grows even without new customers. It's the most predictable form of future revenue.",
    }


def forward_rule_of_40(data):
    """Calculate Forward Rule of 40 using analyst estimates for next year.
    Uses forward P/E + forward EPS to derive forward revenue growth and margins.
    Identifies inflection points where Forward R40 crosses key benchmarks vs trailing."""
    info = data['info']
    inc = data['income_annual']

    # --- Derive forward revenue growth from analyst estimates ---
    fwd_eps = info.get('forwardEps')
    trailing_eps = info.get('trailingEps')
    fwd_pe = info.get('forwardPE')
    price = data.get('price')
    shares_out = info.get('sharesOutstanding')
    trailing_ni = None
    if inc is not None and not inc.empty:
        for row in ['Net Income', 'Net Income Common Stockholders']:
            if row in inc.index and len(inc.columns) > 0:
                trailing_ni = inc.loc[row, inc.columns[0]]
                if pd.notna(trailing_ni):
                    break

    forward_ni = None
    if fwd_eps and shares_out and shares_out > 0:
        forward_ni = fwd_eps * shares_out

    # Forward revenue growth: from forward NI / trailing net margin, or EPS growth
    fwd_rev_growth_pct = None
    fwd_rev_growth_source = None
    trailing_net_margin = info.get('profitMargins')
    rev_ttm = None
    if inc is not None and not inc.empty:
        for row in ['Total Revenue', 'Operating Revenue']:
            if row in inc.index and len(inc.columns) > 0:
                rev_ttm = inc.loc[row, inc.columns[0]]
                if pd.notna(rev_ttm) and rev_ttm > 0:
                    break

    # Method 1: Forward NI / trailing net margin → forward revenue → growth
    if forward_ni and trailing_net_margin and trailing_net_margin > 0 and rev_ttm and rev_ttm > 0:
        fwd_rev_est = forward_ni / trailing_net_margin
        fwd_rev_growth_pct = ((fwd_rev_est / rev_ttm) - 1) * 100
        fwd_rev_growth_source = 'Derived from forward EPS + trailing net margin'

    # Method 2: EPS growth as proxy for revenue growth
    if fwd_rev_growth_pct is None and fwd_eps and trailing_eps and trailing_eps > 0:
        eps_growth = ((fwd_eps / trailing_eps) - 1) * 100
        fwd_rev_growth_pct = eps_growth
        fwd_rev_growth_source = 'Forward EPS growth (proxy for revenue growth)'

    # Method 3: Trailing growth (fallback)
    if fwd_rev_growth_pct is None:
        rev_growth = info.get('revenueGrowth')
        if rev_growth is not None:
            fwd_rev_growth_pct = rev_growth * 100
            fwd_rev_growth_source = 'Trailing growth (no forward estimate available)'

    # --- Forward FCF Margin ---
    trailing_fcf = info.get('freeCashflow')
    fcf_conversion = (trailing_fcf / trailing_ni) if (trailing_fcf and trailing_ni and trailing_ni > 0) else None

    fwd_fcf_margin_pct = None
    fwd_fcf_margin_source = None

    # Method A: Forward FCF = forward NI × FCF conversion → margin
    if forward_ni and fcf_conversion and fcf_conversion > 0 and rev_ttm and rev_ttm > 0:
        # Estimate forward revenue first
        if trailing_net_margin and trailing_net_margin > 0:
            fwd_rev_est = forward_ni / trailing_net_margin
            fwd_fcf_est = forward_ni * fcf_conversion
            fwd_fcf_margin_pct = (fwd_fcf_est / fwd_rev_est) * 100
        else:
            fwd_fcf_est = forward_ni * fcf_conversion
            fwd_fcf_margin_pct = (fwd_fcf_est / rev_ttm) * 100
        fwd_fcf_margin_source = 'Forward NI × historical FCF conversion'

    # Method B: Assume margin improvement if EPS growing faster than revenue
    if fwd_fcf_margin_pct is None and trailing_fcf and rev_ttm and rev_ttm > 0:
        trailing_fcf_margin = (trailing_fcf / rev_ttm) * 100
        # If forward EPS growth > trailing rev growth, margin likely expanding
        if fwd_eps and trailing_eps and trailing_eps > 0:
            eps_growth = ((fwd_eps / trailing_eps) - 1) * 100
            rev_growth = info.get('revenueGrowth', 0) * 100
            margin_expansion = eps_growth - rev_growth
            fwd_fcf_margin_pct = trailing_fcf_margin + (margin_expansion * 0.3)  # partial pass-through
            fwd_fcf_margin_source = 'Trailing FCF margin + estimated margin expansion from EPS growth'
        else:
            fwd_fcf_margin_pct = trailing_fcf_margin
            fwd_fcf_margin_source = 'Trailing FCF margin (no forward margin data)'

    # --- Forward R40 ---
    forward_rule_40_val = None
    if fwd_rev_growth_pct is not None and fwd_fcf_margin_pct is not None:
        forward_rule_40_val = fwd_rev_growth_pct + fwd_fcf_margin_pct
        # Sanity cap at 200 — above this, estimation noise dominates
        if forward_rule_40_val > 200:
            forward_rule_40_val = 200.0
        if forward_rule_40_val < -50:
            forward_rule_40_val = -50.0

    # --- Trailing R40 ---
    trailing_r40 = None
    rev_growth_trailing = info.get('revenueGrowth')
    if rev_growth_trailing is not None and trailing_fcf and rev_ttm and rev_ttm > 0:
        trailing_fcf_margin = (trailing_fcf / rev_ttm) * 100
        trailing_r40 = (rev_growth_trailing * 100) + trailing_fcf_margin

    # --- Inflection detection ---
    inflection_signal = None
    inflection_detail = None
    has_forward_estimate = fwd_rev_growth_source and 'Trailing' not in fwd_rev_growth_source

    if trailing_r40 is not None and forward_rule_40_val is not None:
        gap = forward_rule_40_val - trailing_r40
        if abs(gap) < 3 and not has_forward_estimate:
            inflection_signal = "TRAILING ONLY"
            inflection_detail = "Forward estimates unavailable — showing trailing data. No inflection signal possible."
        elif gap >= 20:
            inflection_signal = "MASSIVE INFLECTION"
            inflection_detail = f"Forward R40 ({forward_rule_40_val:.0f}) is {gap:.0f} pts above trailing ({trailing_r40:.0f}) — potential turnaround or new product cycle"
        elif gap >= 10:
            inflection_signal = "POSITIVE INFLECTION"
            inflection_detail = f"Forward R40 ({forward_rule_40_val:.0f}) is {gap:.0f} pts above trailing ({trailing_r40:.0f}) — improvement ahead"
        elif gap >= 3:
            inflection_signal = "MODEST IMPROVEMENT"
            inflection_detail = f"Forward R40 ({forward_rule_40_val:.0f}) slightly above trailing ({trailing_r40:.0f})"
        elif gap <= -20:
            inflection_signal = "SEVERE DECLINE"
            inflection_detail = f"Forward R40 ({forward_rule_40_val:.0f}) is {abs(gap):.0f} pts BELOW trailing ({trailing_r40:.0f}) — significant deterioration expected"
        elif gap <= -10:
            inflection_signal = "NEGATIVE INFLECTION"
            inflection_detail = f"Forward R40 ({forward_rule_40_val:.0f}) declining vs trailing ({trailing_r40:.0f})"
        elif gap <= -3:
            inflection_signal = "MODEST DECLINE"
            inflection_detail = "Forward R40 slightly below trailing"
        else:
            inflection_signal = "STABLE"
            inflection_detail = "Forward R40 in line with trailing"

        if trailing_r40 < 40 and forward_rule_40_val >= 40:
            inflection_signal = "BENCHMARK CROSSOVER"
            inflection_detail += " — CROSSING the 40 benchmark. This is the inflection point to buy before the market notices."

    assessment = None
    if forward_rule_40_val is not None:
        if forward_rule_40_val >= 50:
            assessment = "Elite (Forward) — premium multiple justified on future cash flows"
        elif forward_rule_40_val >= 40:
            assessment = "Strong (Forward) — meets 2026 benchmark on forward estimates"
        elif forward_rule_40_val >= 30:
            assessment = "Adequate (Forward)"
        elif forward_rule_40_val >= 20:
            assessment = "Below standard (Forward)"
        else:
            assessment = "Weak (Forward)"

    return {
        'forward_rev_growth_pct': fwd_rev_growth_pct,
        'forward_rev_growth_source': fwd_rev_growth_source,
        'forward_fcf_margin_pct': fwd_fcf_margin_pct,
        'forward_fcf_margin_source': fwd_fcf_margin_source,
        'forward_rule_40': forward_rule_40_val,
        'trailing_rule_40': trailing_r40,
        'has_forward_estimate': has_forward_estimate,
        'inflection_signal': inflection_signal,
        'inflection_detail': inflection_detail,
        'assessment': assessment,
        'benchmark': '>=40 (Forward), inflection when trailing <40 and forward >=40',
        'why_forward_looking': "The market prices stocks on future cash flows. A company can have a failing Trailing Rule of 40 today but a passing Forward Rule of 40 as new data centers or products come online.",
    }


def zacks_style_momentum(data):
    """Estimate earnings momentum from revisions and price trend."""
    info = data['info']
    price_data = data.get('price_data')
    eps_current = info.get('trailingEps')
    eps_forward = info.get('forwardEps')
    eps_growth = info.get('earningsGrowth')
    target_mean = info.get('targetMeanPrice')
    recommendation = info.get('recommendationKey', '')

    signals = []
    score = 0

    if eps_forward and eps_current and eps_current > 0:
        eps_fwd_growth = ((eps_forward / eps_current) - 1) * 100
        if eps_fwd_growth > 20:
            score += 3
            signals.append(f"Strong forward EPS growth (+{eps_fwd_growth:.0f}%)")
        elif eps_fwd_growth > 10:
            score += 2
            signals.append(f"Solid forward EPS growth (+{eps_fwd_growth:.0f}%)")
        elif eps_fwd_growth > 0:
            score += 1
        elif eps_fwd_growth < -10:
            score -= 2
            signals.append(f"Earnings contraction expected ({eps_fwd_growth:.0f}%)")

    if eps_growth is not None:
        if eps_growth > 0.30:
            score += 2
            signals.append(f"Historical EPS growth strong ({eps_growth*100:.0f}%)")
        elif eps_growth < -0.10:
            score -= 1

    if price_data is not None and not price_data.empty:
        closes = price_data['Close'].values.flatten()
        if len(closes) >= 252:
            current = closes[-1]
            for days, weight in [(63, 1), (126, 1), (252, 2)]:
                if len(closes) > days:
                    ret = ((current / closes[-days]) - 1) * 100
                    if ret > 20:
                        score += weight
                        signals.append(f"{days//21}mo return +{ret:.0f}% — strong momentum")
                    elif ret > 5:
                        score += 0.5 * weight
                    elif ret < -20:
                        score -= weight
                        signals.append(f"{days//21}mo return {ret:.0f}% — negative momentum")

    rec_map = {'strong_buy': 3, 'buy': 2, 'hold': 0, 'underperform': -2, 'sell': -3}
    if recommendation in rec_map:
        score += rec_map[recommendation]
        signals.append(f"Consensus: {recommendation.replace('_', ' ').title()}")

    price = data.get('price')
    if target_mean and price and price > 0:
        upside = ((target_mean / price) - 1) * 100
        if upside > 20:
            score += 2
            signals.append(f"Analyst target upside {upside:.0f}%")
        elif upside > 5:
            score += 1

    if score >= 8:
        rank, rank_label = 1, "#1 Strong Buy"
    elif score >= 4:
        rank, rank_label = 2, "#2 Buy"
    elif score >= 0:
        rank, rank_label = 3, "#3 Hold"
    elif score >= -4:
        rank, rank_label = 4, "#4 Underperform"
    else:
        rank, rank_label = 5, "#5 Strong Sell"

    return {
        'momentum_score': score,
        'zacks_rank': rank,
        'rank_label': rank_label,
        'signals': signals,
        'is_revision_led': score >= 4 and eps_forward is not None and eps_current is not None and eps_forward > eps_current,
    }


# ===========================================================================
# QUALITATIVE QUADRANT — Circumvention Delta Moat Architecture
# ===========================================================================

def moat_analysis(info, gm=None):
    """Evaluate competitive moat using the Circumvention Delta formula:
    Circumvention Delta = Time + Capital + Performance Loss"""

    desc = (info.get('longBusinessSummary') or '').lower()
    industry = (info.get('industry') or '').lower()
    sector = (info.get('sector') or '').lower()
    if gm is None:
        gm = info.get('grossMargins')

    # ---- Temporal Width (R&D Time-Lag): 2-3 cycle lead ----
    temporal_score = 0
    temporal_signals = []
    rnd_keywords = {
        'patent': 3, 'proprietary': 3, 'semiconductor': 3, 'chip': 3, 'processor': 3, 'gpu': 3,
        'biotechnology': 3, 'pharmaceutical': 3, 'drug': 3, 'gene therapy': 4,
        'algorithm': 2, 'machine learning': 2, 'ai model': 2,
        'aerospace': 3, 'defense': 4, 'nuclear': 4, 'quantum': 4,
        'fda': 3, 'clinical trial': 3, 'regulatory approval': 3,
        'manufacturing process': 2, 'fabrication': 3, 'foundry': 3,
    }
    for kw, pts in rnd_keywords.items():
        if kw in desc or kw in industry:
            temporal_score = max(temporal_score, pts)
            temporal_signals.append(kw.title())

    high_rnd_industries = {
        'semiconductors': 3, 'semiconductor equipment': 3, 'biotechnology': 4,
        'drug manufacturers': 3, 'software-infrastructure': 2, 'aerospace & defense': 4,
        'medical devices': 2, 'scientific instruments': 3,
    }
    for ind, pts in high_rnd_industries.items():
        if ind in industry:
            temporal_score = max(temporal_score, pts)

    if temporal_score >= 4:
        temporal_rating = "2-3 cycle lead — cannot be bridged by capital alone"
    elif temporal_score >= 3:
        temporal_rating = "Significant R&D moat — 1-2 cycle advantage"
    elif temporal_score >= 2:
        temporal_rating = "Moderate lead — replicable with time and investment"
    else:
        temporal_rating = "Limited temporal advantage — easily replicated"

    # ---- Efficiency Width (Performance Penalty) ----
    efficiency_score = 0
    efficiency_signals = []
    if gm is not None:
        if gm > 0.80:
            efficiency_score += 3
            efficiency_signals.append("80%+ gross margin — extreme pricing power")
        elif gm > 0.60:
            efficiency_score += 2
        elif gm > 0.40:
            efficiency_score += 1

    network_kw = ['network effect', 'marketplace', 'platform', 'two-sided', 'ecosystem', 'social network']
    for kw in network_kw:
        if kw in desc:
            efficiency_score += 2
            efficiency_signals.append("Network effects")
            break

    scale_kw = ['largest', 'leading', 'scale', 'global infrastructure', 'distribution network',
                'supply chain', 'volume', 'manufacturing scale']
    for kw in scale_kw:
        if kw in desc:
            efficiency_score += 1
            efficiency_signals.append("Scale advantage")
            break

    data_kw = ['proprietary data', 'data advantage', 'training data', 'unique dataset']
    for kw in data_kw:
        if kw in desc:
            efficiency_score += 2
            efficiency_signals.append("Data moat")
            break

    if efficiency_score >= 5:
        eff_rating = "Formidable — competitors face 20%+ performance penalty"
    elif efficiency_score >= 3:
        eff_rating = "Strong — meaningful cost/performance advantage"
    elif efficiency_score >= 1:
        eff_rating = "Moderate — replicable with effort"
    else:
        eff_rating = "Limited — no clear efficiency barrier"

    # ---- Trust Width (Validation Barrier) ----
    trust_score = 0
    trust_signals = []
    trust_kw = {
        'enterprise': 1, 'government': 2, 'federal': 3, 'military': 3,
        'healthcare': 2, 'hospital': 3, 'banking': 2, 'financial institution': 2,
        'compliance': 2, 'regulatory': 2, 'security': 2, 'certified': 2,
        'mission-critical': 3, 'infrastructure': 2, 'standard': 1,
        'trusted by': 2, 'used by': 1, 'deployed in': 1,
    }
    for kw, pts in trust_kw.items():
        if kw in desc:
            trust_score = max(trust_score, pts)
            trust_signals.append(kw.title())

    trust_industries = {
        'aerospace & defense': 4, 'banks-diversified': 3, 'insurance': 3,
        'healthcare plans': 3, 'drug manufacturers': 3, 'telecom services': 3,
        'software-infrastructure': 2, 'information technology services': 2,
    }
    for ind, pts in trust_industries.items():
        if ind in industry:
            trust_score = max(trust_score, pts)

    b2b_kw = ['enterprise', 'business', 'organization', 'corporate']
    b2c_kw = ['consumer', 'individual', 'personal', 'household']
    if any(kw in desc for kw in b2b_kw) and not any(kw in desc for kw in b2c_kw):
        trust_score += 1

    if trust_score >= 4:
        trust_rating = "Extreme — entrenched B2B standard, validation barrier immense"
    elif trust_score >= 3:
        trust_rating = "High — significant switching costs and trust requirements"
    elif trust_score >= 2:
        trust_rating = "Moderate — some barriers but competitors can qualify"
    else:
        trust_rating = "Low — minimal trust/validation barriers"

    # ---- Circumvention Delta (composite) ----
    circumvention_delta = temporal_score + efficiency_score + trust_score
    max_delta = 13
    delta_pct = (circumvention_delta / max_delta) * 100

    # ---- Composite Moat Rating (1-10) ----
    moat_score = (temporal_score + efficiency_score + trust_score) / 3
    moat_score = max(1.0, min(10.0, moat_score * 1.5 + 1))

    if moat_score >= 8:
        moat_label = "Wide Moat — Exceptional Resilience"
        moat_color = "#16a34a"
    elif moat_score >= 6:
        moat_label = "Moderate Moat — Defensible Position"
        moat_color = "#ea580c"
    elif moat_score >= 4:
        moat_label = "Narrow Moat — Some Protection"
        moat_color = "#ca8a04"
    else:
        moat_label = "No Moat — Vulnerable to Competition"
        moat_color = "#dc2626"

    return {
        'temporal_width': {'score': temporal_score, 'rating': temporal_rating, 'signals': temporal_signals},
        'efficiency_width': {'score': efficiency_score, 'rating': eff_rating, 'signals': efficiency_signals},
        'trust_width': {'score': trust_score, 'rating': trust_rating, 'signals': trust_signals},
        'circumvention_delta': circumvention_delta,
        'circumvention_delta_pct': round(delta_pct, 1),
        'circumvention_delta_formula': f"Time({temporal_score}) + Capital({efficiency_score}) + Performance Loss({trust_score}) = {circumvention_delta}",
        'moat_rating': round(moat_score, 1),
        'moat_label': moat_label,
        'moat_color': moat_color,
        'benchmark': '≥7 = Wide Moat, 4-6 = Narrow Moat, <4 = No Moat',
        'wide_moat_annual_return': '11.5% annualized since 2007 vs 8.99% broad market',
    }


def moat_performance_signals(info, data):
    """Determine if the moat is Compounding, Defending, or Decaying.
    - Compounding: declining CAC, rising price premiums
    - Defending: stable market share
    - Decaying: multi-homing increasing, competitors closing cost gaps"""

    desc = (info.get('longBusinessSummary') or '').lower()

    # Check for moat deterioration signals
    decay_signals = []
    compound_signals = []
    defend_signals = []

    # Revenue growth trajectory
    rev_growth = info.get('revenueGrowth')
    if rev_growth is not None:
        if rev_growth > 0.25:
            compound_signals.append("Strong revenue momentum — moat likely expanding")
        elif rev_growth < -0.05:
            decay_signals.append("Revenue declining — moat may be eroding")

    # Gross margin trajectory
    gm = info.get('grossMargins')
    if gm is not None:
        if gm > 0.70:
            compound_signals.append("High gross margins sustained — pricing power intact")
        elif gm < 0.15:
            decay_signals.append("Thin margins — limited pricing power")

    # Competitive language in description
    competition_kw = ['competitive', 'competition', 'intense competition', 'price pressure',
                      'commoditization', 'substitute', 'alternative']
    for kw in competition_kw:
        if kw in desc:
            decay_signals.append(f"Competitive pressure acknowledged: '{kw}'")
            break

    innovation_kw = ['innovation', 'breakthrough', 'first-to-market', 'industry-leading',
                     'disruptive', 'revolutionary', 'best-in-class']
    for kw in innovation_kw:
        if kw in desc:
            compound_signals.append(f"Innovation advantage: '{kw}'")
            break

    # Determine overall state
    total_signals = len(compound_signals) + len(defend_signals) + len(decay_signals)
    if total_signals == 0:
        performance = "INSUFFICIENT DATA"
        performance_label = "Cannot determine moat trajectory from available data"
        performance_color = "#6b7280"
    elif len(compound_signals) >= len(decay_signals) + 2:
        performance = "COMPOUNDING"
        performance_label = "Moat is strengthening — declining CAC, rising price premiums, expanding market share"
        performance_color = "#16a34a"
    elif len(decay_signals) > len(compound_signals):
        performance = "DECAYING"
        performance_label = "Moat is eroding — competitors closing gaps, multi-homing increasing, pricing power weakening"
        performance_color = "#dc2626"
    else:
        performance = "DEFENDING"
        performance_label = "Moat is stable — maintaining share, steady pricing, no significant erosion or expansion"
        performance_color = "#ea580c"

    return {
        'performance': performance,
        'performance_label': performance_label,
        'performance_color': performance_color,
        'compound_signals': compound_signals,
        'defend_signals': defend_signals,
        'decay_signals': decay_signals,
    }


def qualitative_quadrant(data):
    """Full qualitative analysis — moat architecture + performance signals."""
    info = data['info']
    gm = info.get('grossMargins')
    moat = moat_analysis(info, gm)
    perf = moat_performance_signals(info, data)

    desc = (info.get('longBusinessSummary') or '').lower()

    # Technology sovereignty
    sovereignty_signals = []
    if any(kw in desc for kw in ['domestic manufacturing', 'onshore', 'made in usa', 'american']):
        sovereignty_signals.append("Domestic manufacturing advantage")
    if any(kw in desc for kw in ['export control', 'national security', 'defense']):
        sovereignty_signals.append("National security relevance — export control protection")
    if not sovereignty_signals:
        sovereignty_signals.append("No specific sovereignty advantage")

    # AI integration depth
    ai_depth = 0
    ai_signals = []
    ai_layer1_kw = ['gpu', 'chip', 'semiconductor', 'data center', 'hbm', 'high-bandwidth memory',
                     'networking', 'infrastructure', 'cooling', 'power management']
    ai_layer2_kw = ['foundation model', 'large language model', 'ai platform', 'machine learning',
                     'training', 'inference', 'neural network', 'deep learning']
    ai_layer3_kw = ['ai-powered', 'ai assistant', 'copilot', 'autonomous', 'computer vision',
                     'generative ai', 'ai integration']
    for kw in ai_layer1_kw:
        if kw in desc:
            ai_depth = max(ai_depth, 3)
            ai_signals.append("AI Infrastructure exposure")
    for kw in ai_layer2_kw:
        if kw in desc:
            ai_depth = max(ai_depth, 2)
            ai_signals.append("AI Platform/Model exposure")
    for kw in ai_layer3_kw:
        if kw in desc:
            ai_depth = max(ai_depth, 1)
            ai_signals.append("AI Application exposure")
    if not ai_signals:
        ai_signals.append("No direct AI exposure detected")

    return {
        'moat': moat,
        'moat_performance': perf,
        'technology_sovereignty': sovereignty_signals,
        'ai_integration_depth': ai_depth,
        'ai_signals': ai_signals,
    }


# ===========================================================================
# THEMATIC ANALYSIS
# ===========================================================================

THEMES_2026 = {
    'ai_semiconductor': {
        'name': 'AI Semiconductor Leadership',
        'description': 'Compute Demand > Supply — HBM, AI accelerators, networking',
        'keywords': ['gpu', 'semiconductor', 'chip', 'hbm', 'dram', 'nand', 'asic', 'fpga',
                     'networking', 'data center', 'ai accelerator', 'processor', 'memory', 'storage'],
        'top_picks': ['NVDA', 'MU', 'AVGO', 'STX', 'TER', 'TXN', 'AMD', 'MRVL', 'AMAT', 'KLAC'],
        'catalyst': 'AI buildout continues — compute demand outstrips supply',
        'forward_pe_target': '15-40x depending on growth trajectory',
    },
    'energy_renaissance': {
        'name': 'Energy Renaissance',
        'description': 'Powering the Intelligence Era — data center energy, nuclear, gas',
        'keywords': ['energy', 'power', 'nuclear', 'natural gas', 'renewable', 'solar',
                     'fuel cell', 'grid', 'utility', 'storage', 'turbine', 'generation', 'electricity'],
        'top_picks': ['BE', 'NEE', 'GEV', 'FSLR', 'CEG', 'VST', 'SMR', 'OKLO'],
        'catalyst': 'Data center energy consumption growing 10%+ annually',
        'forward_pe_target': '20-60x for high-growth energy tech',
    },
    'healthcare_innovation': {
        'name': 'Healthcare & Biotech Innovation',
        'description': 'GLP-1 ecosystem, gene therapy, AI drug discovery, diabesity',
        'keywords': ['biotechnology', 'pharmaceutical', 'drug', 'therapy', 'gene',
                     'clinical trial', 'antibody', 'diabetes', 'obesity', 'glp-1',
                     'longevity', 'medical device', 'diagnostic', 'healthcare'],
        'top_picks': ['LLY', 'NVO', 'ALGN', 'CNC', 'BMY', 'SDGR'],
        'catalyst': 'Product innovation cycle + AI accelerating drug discovery',
        'forward_pe_target': '15-35x for established, higher for biotech',
    },
    'software_diffusion': {
        'name': 'AI Software Diffusion',
        'description': 'AI monetization — margin expansion through labor cost savings',
        'keywords': ['software', 'saas', 'cloud', 'enterprise software', 'automation',
                     'workflow', 'productivity', 'copilot', 'subscription',
                     'digital transformation', 'cybersecurity'],
        'top_picks': ['MSFT', 'CRM', 'NOW', 'ADBE', 'SNOW', 'DDOG', 'CRWD', 'PANW'],
        'catalyst': '$1.2T annual corporate labor cost savings from AI',
        'forward_pe_target': '25-50x with Rule of 40 validation',
    },
    'smallcap_recovery': {
        'name': 'Small-Cap Value Recovery',
        'description': 'Undervalued small-caps trading at 15% discount to fair value',
        'keywords': ['small cap', 'regional', 'community', 'local'],
        'top_picks': [],
        'catalyst': 'Rate normalization + domestic manufacturing policy',
        'forward_pe_target': '10-20x with earnings recovery',
    },
}


def thematic_classification(ticker, info):
    ticker = ticker.upper()
    desc = (info.get('longBusinessSummary') or '').lower()
    industry = (info.get('industry') or '').lower()
    sector = (info.get('sector') or '').lower()
    name = (info.get('shortName') or info.get('longName') or '').lower()

    theme_scores = {}
    for theme_key, theme in THEMES_2026.items():
        score = 0
        matches = []
        if ticker in theme['top_picks']:
            score += 5
            matches.append('Top pick in 2026 framework')
        for kw in theme['keywords']:
            if kw in desc or kw in industry or kw in name:
                score += 1
                matches.append(f"Keyword: {kw}")
        sector_map = {
            'ai_semiconductor': ['technology', 'semiconductor', 'hardware'],
            'energy_renaissance': ['energy', 'utilities', 'renewable'],
            'healthcare_innovation': ['healthcare', 'biotechnology', 'pharmaceutical'],
            'software_diffusion': ['software', 'technology', 'information technology'],
            'smallcap_recovery': [],
        }
        for kw in sector_map.get(theme_key, []):
            if kw in sector or kw in industry:
                score += 2
                matches.append(f"Sector: {kw}")
                break
        theme_scores[theme_key] = {'score': min(10, score), 'matches': matches[:5]}

    ranked = sorted(theme_scores.items(), key=lambda x: x[1]['score'], reverse=True)
    primary_theme = ranked[0] if ranked else (None, None)
    secondary_themes = [t for t in ranked[1:3] if t[1]['score'] >= 2]

    return {
        'all_scores': {k: v['score'] for k, v in theme_scores.items()},
        'primary_theme': primary_theme[0] if primary_theme[0] else None,
        'primary_name': THEMES_2026[primary_theme[0]]['name'] if primary_theme[0] in THEMES_2026 else None,
        'primary_conviction': primary_theme[1]['score'] if primary_theme[1] else 0,
        'primary_catalyst': THEMES_2026[primary_theme[0]]['catalyst'] if primary_theme[0] in THEMES_2026 else None,
        'primary_pe_target': THEMES_2026[primary_theme[0]]['forward_pe_target'] if primary_theme[0] in THEMES_2026 else None,
        'secondary_themes': [
            {'key': k, 'name': THEMES_2026[k]['name'], 'score': v['score']}
            for k, v in secondary_themes
        ],
        'all_matches': {k: v['matches'] for k, v in theme_scores.items() if v['matches']},
    }


# ===========================================================================
# RISK MANAGEMENT
# ===========================================================================

MENTAL_STOP_LOSSES = {
    'AAPL': 'Exit if iPhone unit growth turns negative for two consecutive quarters',
    'AMZN': 'Exit if AWS growth drops below 14%',
    'MSFT': 'Exit if Azure growth falls below 28%',
    'NVDA': 'Exit if data center growth drops below 50%',
    'GOOGL': 'Exit if advertising revenue growth turns negative',
    'META': 'Exit if DAU growth stalls for two consecutive quarters',
    'TSLA': 'Exit if automotive gross margin (ex-credits) falls below 15%',
}


def position_sizing_check(ticker, current_weight_pct, max_weight=10.0):
    ticker = ticker.upper()
    is_magnificent_7 = ticker in ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA']
    if current_weight_pct > max_weight:
        action = f"TRIM — reduce from {current_weight_pct:.1f}% to {max_weight}% NAV"
        urgency = "High" if current_weight_pct > 15 else "Medium"
    elif current_weight_pct > max_weight * 0.8:
        action = f"WATCH — at {current_weight_pct:.1f}%, approaching {max_weight}% limit"
        urgency = "Low"
    else:
        action = f"OK — {current_weight_pct:.1f}% within {max_weight}% limit"
        urgency = "None"
    note = 'Even Magnificent 7 names can gap down 15%+ overnight on earnings' if is_magnificent_7 else None
    return {
        'current_weight_pct': current_weight_pct, 'max_weight_pct': max_weight,
        'is_magnificent_7': is_magnificent_7, 'action': action, 'urgency': urgency, 'note': note,
    }


def mental_stop_loss(ticker, info):
    ticker = ticker.upper()
    if ticker in MENTAL_STOP_LOSSES:
        threshold = MENTAL_STOP_LOSSES[ticker]
        is_custom = False
    else:
        sector = (info.get('sector') or '').lower()
        if 'technology' in sector or 'software' in (info.get('industry') or '').lower():
            rev_growth = info.get('revenueGrowth')
            if rev_growth is not None and rev_growth > 0.20:
                threshold = f"Exit if revenue growth drops below {max(10, rev_growth * 100 * 0.5):.0f}%"
            else:
                threshold = "Exit if revenue growth turns negative for two consecutive quarters"
        elif 'financial' in sector:
            threshold = "Exit if net interest margin contracts below 2% or loan loss provisions double"
        elif 'healthcare' in sector:
            threshold = "Exit if key pipeline drug fails Phase 3 or revenue growth turns negative"
        elif 'energy' in sector:
            threshold = "Exit if crude oil (WTI) sustains below $50 or production guidance cut"
        else:
            threshold = "Exit if revenue growth turns negative for two consecutive quarters OR operating margin halves"
        is_custom = True
    return {
        'ticker': ticker, 'thesis_break_threshold': threshold, 'is_custom_generated': is_custom,
        'rule': 'Re-test thesis after every earnings print.',
    }


def barbell_allocation_check(positions):
    if not positions:
        return {'valid': True, 'message': 'No positions to check', 'segments': {}}
    growth_themes = {'ai_semiconductor', 'software_diffusion'}
    value_themes = {'energy_renaissance', 'healthcare_innovation', 'smallcap_recovery'}
    growth_weight = sum(p.get('weight', 0) for p in positions if any(t in growth_themes for t in p.get('themes', [])))
    value_weight = sum(p.get('weight', 0) for p in positions if any(t in value_themes for t in p.get('themes', [])))
    other_weight = sum(p.get('weight', 0) for p in positions if not any(t in growth_themes | value_themes for t in p.get('themes', [])))
    total = growth_weight + value_weight + other_weight
    if total == 0:
        return {'valid': True, 'message': 'No weights assigned', 'segments': {}}
    growth_pct = growth_weight / total * 100
    value_pct = value_weight / total * 100
    if growth_pct > 80:
        valid = False
        message = "Portfolio too concentrated in growth — add quality value/energy for the barbell"
    elif value_pct > 80:
        valid = False
        message = "Portfolio too conservative — add AI/semiconductor growth"
    elif growth_pct > 25 and value_pct > 25:
        valid = True
        message = "Barbell structure validated — balanced growth and value"
    else:
        valid = True
        message = "Barbell emerging — consider increasing the underweight segment"
    return {
        'valid': valid, 'message': message,
        'segments': {
            'high_growth_pct': round(growth_pct, 1),
            'quality_value_pct': round(value_pct, 1),
            'other_pct': round(other_weight / total * 100, 1) if total > 0 else 0,
        },
        'target': 'Aim for 35-50% growth, 35-50% value, 10-20% alternatives',
    }


def risk_factor_analysis(data):
    info = data['info']
    risks = []
    risk_score = 0
    fwd_pe = info.get('forwardPE')
    tpe = info.get('trailingPE')
    ps = info.get('priceToSales')
    if fwd_pe and fwd_pe > 40:
        risks.append({'factor': 'Extended Valuation', 'detail': f'Forward P/E of {fwd_pe:.1f}x', 'severity': 'High',
                      'mitigation': 'Size position conservatively, use mental stop-losses'})
        risk_score += 3
    elif fwd_pe and fwd_pe > 25:
        risks.append({'factor': 'Above-Average Valuation', 'detail': f'Forward P/E of {fwd_pe:.1f}x', 'severity': 'Medium',
                      'mitigation': 'Require above-benchmark Rule of 40 to justify'})
        risk_score += 1
    if ps and ps > 15:
        risks.append({'factor': 'High Price/Sales', 'detail': f'P/S of {ps:.1f}x', 'severity': 'Medium',
                      'mitigation': 'Validate with ARR growth and NRR metrics'})
        risk_score += 1
    dte = info.get('debtToEquity')
    if dte and dte > 150:
        risks.append({'factor': 'Excessive Leverage', 'detail': f'D/E ratio of {dte:.0f}', 'severity': 'High',
                      'mitigation': 'Ensure interest coverage > 3x'})
        risk_score += 2
    desc = (info.get('longBusinessSummary') or '').lower()
    if any(kw in desc for kw in ['single customer', 'concentrated', 'largest customer']):
        risks.append({'factor': 'Customer Concentration', 'detail': 'Revenue concentrated in few customers', 'severity': 'High',
                      'mitigation': 'Verify no single customer > 20% of revenue'})
        risk_score += 2
    beta = info.get('beta')
    if beta and beta > 2:
        risks.append({'factor': 'Extreme Volatility', 'detail': f'Beta of {beta:.1f}', 'severity': 'Medium',
                      'mitigation': 'Use mental stop-losses instead of hard stops'})
        risk_score += 1
    fcf = info.get('freeCashflow')
    if fcf and fcf < -100e6:
        risks.append({'factor': 'Cash Burn', 'detail': f'FCF of ${fcf/1e6:.0f}M', 'severity': 'Medium',
                      'mitigation': 'Verify cash runway > 2 years'})
        risk_score += 1
    if not risks:
        risks.append({'factor': 'No Critical Flags', 'detail': 'No major 2026-specific risk factors identified',
                      'severity': 'Low', 'mitigation': 'Standard position sizing and thesis monitoring'})
    risk_level = 'High' if risk_score >= 6 else ('Medium' if risk_score >= 3 else 'Low')
    return {
        'risks': risks, 'risk_score': risk_score, 'risk_level': risk_level,
        'max_suggested_position': 3 if risk_score >= 6 else (7 if risk_score >= 3 else 10),
    }


def risk_management_module(ticker, data, current_weight_pct=0, positions=None):
    info = data['info']
    return {
        'position_sizing': position_sizing_check(ticker, current_weight_pct),
        'mental_stop_loss': mental_stop_loss(ticker, info),
        'barbell_check': barbell_allocation_check(positions or []),
        'risk_factors': risk_factor_analysis(data),
    }


# ===========================================================================
# PORTFOLIO OPTIMIZATION
# ===========================================================================

def estimate_correlation(ticker_a, ticker_b, data_a=None, data_b=None):
    try:
        closes_a = data_a['price_data']['Close'] if (data_a and data_a.get('price_data') is not None) else safe_get(lambda: yf.Ticker(ticker_a).history(period='1y')['Close'])
        closes_b = data_b['price_data']['Close'] if (data_b and data_b.get('price_data') is not None) else safe_get(lambda: yf.Ticker(ticker_b).history(period='1y')['Close'])
        if closes_a is None or closes_b is None or closes_a.empty or closes_b.empty:
            return None
        common_dates = closes_a.index.intersection(closes_b.index)
        if len(common_dates) < 60:
            return None
        return closes_a.loc[common_dates].pct_change().dropna().corr(closes_b.loc[common_dates].pct_change().dropna())
    except Exception:
        return None


def portfolio_optimization_suggestions(ticker, data, existing_positions):
    risk = risk_factor_analysis(data)
    max_weight = risk['max_suggested_position']
    suggestions = [{
        'rule': '10% NAV Cap',
        'recommendation': f'Maximum {max_weight}% of portfolio NAV',
        'detail': f'Based on risk level: {risk["risk_level"]}',
    }]
    if existing_positions and len(existing_positions) > 0:
        high_corr = []
        for pos in existing_positions:
            corr = estimate_correlation(ticker, pos, data, existing_positions.get(pos, {}))
            if corr and corr > 0.7:
                high_corr.append((pos, corr))
        if high_corr:
            suggestions.append({
                'rule': 'Correlation Risk',
                'recommendation': 'Reduce size — highly correlated with existing positions',
                'detail': ', '.join(f'{t} (r={c:.2f})' for t, c in high_corr),
            })
    suggestions.append({
        'rule': 'Deployment Strategy',
        'recommendation': 'Deploy 50% now as base position, keep 50% dry powder for -10% dips',
        'detail': 'Review thesis quarterly — trim if position exceeds 10% NAV',
    })
    return suggestions


# ===========================================================================
# INVESTMENT THESIS GENERATOR
# ===========================================================================

def generate_thesis(ticker, data, quantitative, qualitative, thematic, risk, nob_type):
    info = data['info']
    name = data.get('name', ticker)
    nob = NoB_TYPES.get(nob_type, NoB_TYPES['traditional_value'])
    parts = [f"{name} ({ticker}) — {nob['name']}"]

    r40 = quantitative.get('rule_of_40', {})
    fwd_r40 = quantitative.get('forward_rule_of_40', {})
    nrr_data = quantitative.get('net_revenue_retention', {})
    rpo_data = quantitative.get('rpo', {})
    gm_data = quantitative.get('gross_margin', {})
    moat = qualitative['moat']
    risk_factors = risk['risk_factors']

    # NoB-specific thesis logic
    if nob_type == 'high_growth_saas':
        saas = quantitative.get('saas_filter', {})
        ltv_cac = saas.get('ltv_cac_ratio')
        cac_payback = saas.get('cac_payback_months')
        if r40.get('rule_40_fcf') is not None:
            parts.append(f"Rule of 40 (FCF): {r40['rule_40_fcf']:.0f}")
        if ltv_cac is not None:
            parts.append(f"LTV:CAC ~{ltv_cac}:1")
        if cac_payback is not None:
            parts.append(f"CAC payback ~{cac_payback:.0f} months")
    elif nob_type in ('ai_infra_semiconductor', 'energy_industrial'):
        ind = quantitative.get('industrial_filter', {})
        if ind.get('revision_led_eps', {}).get('is_revision_led'):
            parts.append("Revision-led EPS momentum")
        if ind.get('backlog_assessment'):
            parts.append(ind['backlog_assessment'][:80])
    elif nob_type == 'biopharma':
        bio = quantitative.get('biopharma_filter', {})
        parts.append(f"Stage: {bio.get('clinical_stage', 'Unknown')}")
        if bio.get('ai_attrition_premium'):
            parts.append("AI-enabled reduced attrition premium")
    elif nob_type == 'traditional_value':
        val = quantitative.get('value_filter', {})
        if val.get('value_score') is not None:
            parts.append(f"Value Score: {val['value_score']}/10 — {val.get('value_label', '')}")
        if val.get('trailing_pe') is not None and val['trailing_pe'] > 0:
            parts.append(f"P/E: {val['trailing_pe']:.1f}x")
        if val.get('dividend_yield_pct') is not None and val['dividend_yield_pct'] > 0:
            parts.append(f"Dividend: {val['dividend_yield_pct']:.1f}%")
    elif nob_type == 'high_growth_general':
        gf = quantitative.get('growth_filter', {})
        if gf.get('revenue_growth_pct') is not None:
            parts.append(f"Revenue growth: {gf['revenue_growth_pct']:.0f}%")
        if gf.get('cash_runway_years') is not None:
            parts.append(f"Cash runway: {gf['cash_runway_years']:.0f}yrs")
        if gf.get('growth_decelerating'):
            parts.append("Growth decelerating — monitor")

    # Forward Rule of 40 inflection
    if fwd_r40.get('inflection_signal') in ('MASSIVE INFLECTION', 'POSITIVE INFLECTION', 'BENCHMARK CROSSOVER'):
        parts.append(f"Forward Rule of 40: {fwd_r40.get('inflection_signal')}")

    # NRR installed growth
    nrr_pct = nrr_data.get('estimated_nrr_pct')
    if nrr_pct is not None and nrr_pct >= 120:
        parts.append(f"NRR {nrr_pct:.0f}% — installed growth engine")

    # RPO leading indicator
    if rpo_data.get('leading_indicator_signal') == 'STRONG LEAD':
        parts.append("RPO leading — contracted backlog signals revenue acceleration")

    # Moat
    parts.append(f"Moat: {moat['moat_rating']}/10 — {moat['moat_label']}")

    # Moat performance
    perf = qualitative.get('moat_performance', {})
    if perf.get('performance'):
        parts.append(f"Moat trajectory: {perf['performance']}")

    primary_name = thematic.get('primary_name')
    if primary_name:
        parts.append(f"Theme: {primary_name}")

    risk_level = risk_factors.get('risk_level', 'N/A')
    parts.append(f"Risk: {risk_level}")

    thesis_text = '. '.join(parts) + '.'

    # Conviction
    moat_rating = moat['moat_rating']
    risk_score = risk_factors.get('risk_score', 5)
    fwd_inflection = fwd_r40.get('inflection_signal', '')
    nrr_high = nrr_pct is not None and nrr_pct >= 120

    if moat_rating >= 7 and risk_score <= 2 and nrr_high:
        conviction = "HIGH CONVICTION"
        conviction_detail = "Wide moat + installed growth engine + clean risk profile. Core portfolio position subject to 10% NAV cap."
    elif moat_rating >= 5 and risk_score <= 4:
        conviction = "MODERATE CONVICTION"
        conviction_detail = "Solid fundamentals with manageable risks. Consider barbell pairing."
    elif moat_rating >= 5:
        conviction = "SELECTIVE"
        conviction_detail = "Good moat but elevated risk — reduce position size, tighten mental stop-losses."
    elif risk_score <= 3:
        conviction = "OPPORTUNISTIC"
        conviction_detail = "Limited moat but favorable risk/reward — trade, don't marry."
    else:
        conviction = "PASS"
        conviction_detail = "Neither strong moat nor clean risk profile. Better opportunities exist."

    return {
        'thesis': thesis_text,
        'conviction': conviction,
        'conviction_detail': conviction_detail,
    }


# ===========================================================================
# QUANTITATIVE QUADRANT (routes to NoB-specific filter)
# ===========================================================================

def quantitative_quadrant(data, nob_type):
    """Full quantitative analysis with NoB-specific routing."""
    base = {
        'gross_margin': gross_margin_efficiency(data),
        'arr_growth': arr_growth_estimate(data),
        'rpo': rpo_analysis(data),
        'net_revenue_retention': net_revenue_retention_estimate(data),
        'forward_rule_of_40': forward_rule_of_40(data),
        'momentum': zacks_style_momentum(data),
        'rule_of_40': {
            'rule_40_fcf': None,
            'rule_40_ebitda': None,
            'assessment': None,
            'benchmark': '≥40 (2026 standard)',
        },
    }

    # Shared Rule of 40 (used by all types)
    info = data['info']
    inc = data['income_annual']
    cf = data['cashflow']
    rev_growth = info.get('revenueGrowth')
    rg_pct = (rev_growth * 100) if rev_growth is not None else None
    ebitda_margin = info.get('ebitdaMargins')
    ebitda_pct = (ebitda_margin * 100) if ebitda_margin is not None else None
    rule_40_ebitda = (rg_pct + ebitda_pct) if (rg_pct is not None and ebitda_pct is not None) else None
    fcf = info.get('freeCashflow')
    rev_ttm = None
    if inc is not None and not inc.empty:
        for row in ['Total Revenue', 'Operating Revenue']:
            if row in inc.index and len(inc.columns) > 0:
                rev_ttm = inc.loc[row, inc.columns[0]]
                if pd.notna(rev_ttm) and rev_ttm > 0:
                    break
    fcf_margin_pct = (fcf / rev_ttm * 100) if (fcf and rev_ttm and rev_ttm > 0) else None
    rule_40_fcf = (rg_pct + fcf_margin_pct) if (rg_pct is not None and fcf_margin_pct is not None) else None
    assessment = None
    if rule_40_fcf is not None:
        if rule_40_fcf >= 50:
            assessment = "Elite — premium valuation warranted"
        elif rule_40_fcf >= 40:
            assessment = "Strong — meets 2026 benchmark"
        elif rule_40_fcf >= 30:
            assessment = "Adequate"
        elif rule_40_fcf >= 20:
            assessment = "Below standard"
        else:
            assessment = "Weak"
    base['rule_of_40'] = {
        'revenue_growth_pct': rg_pct, 'ebitda_margin_pct': ebitda_pct,
        'fcf_margin_pct': fcf_margin_pct, 'rule_40_ebitda': rule_40_ebitda,
        'rule_40_fcf': rule_40_fcf, 'assessment': assessment,
        'benchmark': '≥40 (2026 standard), ≥50 for premium',
    }

    # Route to NoB-specific filter
    if nob_type == 'high_growth_saas':
        base['saas_filter'] = saas_efficiency_filter(data)
    elif nob_type == 'ai_infra_semiconductor':
        base['industrial_filter'] = industrial_throughput_filter(data)
    elif nob_type == 'energy_industrial':
        base['industrial_filter'] = industrial_throughput_filter(data)
    elif nob_type == 'biopharma':
        base['biopharma_filter'] = biopharma_milestone_filter(data)
    elif nob_type == 'traditional_value':
        base['value_filter'] = traditional_value_filter(data)
    elif nob_type == 'high_growth_general':
        base['growth_filter'] = high_growth_general_filter(data)

    return base


# ===========================================================================
# TRADITIONAL / VALUE FILTER
# ===========================================================================

def traditional_value_filter(data):
    """Traditional value companies evaluated on margin of safety:
    P/E, P/B, dividend yield, earnings stability, debt levels."""
    info = data['info']
    inc = data['income_annual']

    tpe = info.get('trailingPE')
    fwd_pe = info.get('forwardPE')
    pb = info.get('priceToBook')
    ps = info.get('priceToSales')
    div_yield = info.get('dividendYield')
    dte = info.get('debtToEquity')
    roe = info.get('returnOnEquity')
    beta = info.get('beta')
    ev_ebitda = info.get('enterpriseToEbitda')
    current_ratio = info.get('currentRatio')
    earnings_growth = info.get('earningsGrowth')
    rev_growth = info.get('revenueGrowth')

    # Earnings stability (from income trends)
    ni_trend = []
    if inc is not None and not inc.empty:
        for row in ['Net Income', 'Net Income Common Stockholders']:
            if row in inc.index:
                for col in inc.columns[:5]:
                    val = inc.loc[row, col]
                    if pd.notna(val):
                        ni_trend.append(val)
                break

    earnings_volatility = None
    if len(ni_trend) >= 3:
        ni_changes = [(ni_trend[i] / ni_trend[i+1] - 1) if ni_trend[i+1] != 0 else 0
                      for i in range(len(ni_trend)-1)]
        earnings_volatility = float(np.std(ni_changes)) if ni_changes else None

    # Margin of safety assessment
    signals = []
    concerns = []

    # P/E analysis
    if tpe is not None:
        if 0 < tpe < 10:
            signals.append(f"Deep value — trailing P/E of {tpe:.1f}x")
        elif 10 <= tpe < 15:
            signals.append(f"Value territory — trailing P/E of {tpe:.1f}x")
        elif 15 <= tpe < 20:
            signals.append(f"Fair value — trailing P/E of {tpe:.1f}x")
        elif tpe > 30:
            concerns.append(f"Expensive for traditional company — P/E of {tpe:.1f}x")
        elif tpe < 0:
            concerns.append("Currently unprofitable — P/E negative")

    if fwd_pe is not None and fwd_pe > 0:
        if fwd_pe < tpe if tpe and tpe > 0 else False:
            signals.append(f"Earnings expected to grow — forward P/E {fwd_pe:.1f}x vs trailing {tpe:.1f}x")

    # Price/Book
    if pb is not None:
        if pb < 1:
            signals.append(f"Below book value — P/B of {pb:.2f}x")
        elif pb < 1.5:
            signals.append(f"Near book value — P/B of {pb:.2f}x")
        elif pb > 5:
            concerns.append(f"High P/B of {pb:.1f}x — paying significant premium to book")

    # Dividend
    if div_yield is not None:
        div_pct = div_yield * 100 if div_yield < 1 else div_yield
        if div_pct > 4:
            signals.append(f"Strong dividend yield — {div_pct:.1f}%")
        elif div_pct > 2:
            signals.append(f"Moderate dividend yield — {div_pct:.1f}%")

    # Debt
    if dte is not None:
        if dte < 30:
            signals.append(f"Conservative leverage — D/E {dte:.0f}")
        elif dte > 150:
            concerns.append(f"High leverage — D/E {dte:.0f}")

    # Earnings stability
    if earnings_volatility is not None:
        if earnings_volatility < 0.15:
            signals.append("Stable earnings — low volatility")
        elif earnings_volatility > 0.5:
            concerns.append("Highly volatile earnings — cyclical risk")

    # Growth
    if rev_growth is not None:
        if rev_growth > 0.10:
            signals.append(f"Above-average growth for value — revenue +{rev_growth*100:.0f}%")
        elif rev_growth < -0.05:
            concerns.append(f"Revenue declining — {rev_growth*100:.0f}%")

    if not signals:
        signals.append("No strong value signals identified from available data")
    if not concerns:
        concerns.append("No major red flags")

    # Composite value score (0-10)
    value_score = 5
    if tpe is not None and 0 < tpe < 15: value_score += 1
    if pb is not None and pb < 2: value_score += 1
    if div_yield is not None and div_yield > 0.03: value_score += 1
    if dte is not None and dte < 50: value_score += 1
    if earnings_volatility is not None and earnings_volatility < 0.2: value_score += 1
    if rev_growth is not None and rev_growth > 0: value_score += 1
    value_score = max(0, min(10, value_score))

    if value_score >= 8:
        value_label = "Deep Value — significant margin of safety"
    elif value_score >= 6:
        value_label = "Good Value — reasonable price for quality"
    elif value_score >= 4:
        value_label = "Fair Value — adequately priced"
    else:
        value_label = "Expensive — limited margin of safety"

    return {
        'business_model': 'Traditional / Value',
        'trailing_pe': tpe,
        'forward_pe': fwd_pe,
        'price_to_book': pb,
        'price_to_sales': ps,
        'dividend_yield_pct': (div_yield * 100 if div_yield and div_yield < 1 else div_yield),
        'debt_to_equity': dte,
        'return_on_equity': (roe * 100) if roe is not None else None,
        'earnings_volatility': round(earnings_volatility, 3) if earnings_volatility is not None else None,
        'beta': beta,
        'ev_to_ebitda': ev_ebitda,
        'current_ratio': current_ratio,
        'signals': signals,
        'concerns': concerns,
        'value_score': value_score,
        'value_label': value_label,
        'benchmarks': {
            'pe': '<15x = value, 15-20x = fair, >25x = expensive',
            'pb': '<1.5x = good value, >3x = premium',
            'dividend': '>3% = attractive, >5% = deep value signal',
            'debt': '<50 D/E = conservative, >100 = elevated',
        },
    }


def high_growth_general_filter(data):
    """High-growth general companies: growth durability, TAM, cash runway."""
    info = data['info']
    inc = data['income_annual']

    rev_growth = info.get('revenueGrowth')
    earnings_growth = info.get('earningsGrowth')
    gm = info.get('grossMargins')
    fcf = info.get('freeCashflow')
    cash = info.get('totalCash', 0) or 0
    mcap = info.get('marketCap')
    beta = info.get('beta')

    rg_pct = (rev_growth * 100) if rev_growth is not None else None
    gm_pct = (gm * 100) if gm is not None else None

    # Cash runway
    cash_runway_years = None
    if fcf is not None and fcf < 0 and cash > 0:
        cash_runway_years = cash / abs(fcf)

    # Growth sustainability check
    rev_ttm = None
    inc_q = data['income_quarterly']
    quarterly_trend = []
    if inc_q is not None and not inc_q.empty:
        for row in ['Total Revenue', 'Operating Revenue']:
            if row in inc_q.index:
                for col in inc_q.columns[:8]:
                    val = inc_q.loc[row, col]
                    if pd.notna(val) and val > 0:
                        quarterly_trend.append(val)
                break

    growth_decelerating = False
    if len(quarterly_trend) >= 4:
        recent_qoq = ((quarterly_trend[0] / quarterly_trend[1]) - 1) if quarterly_trend[1] > 0 else 0
        prior_qoq = ((quarterly_trend[2] / quarterly_trend[3]) - 1) if len(quarterly_trend) >= 4 and quarterly_trend[3] > 0 else 0
        if recent_qoq < prior_qoq:
            growth_decelerating = True

    # Signals
    signals = []
    concerns = []

    if rg_pct is not None:
        if rg_pct > 30:
            signals.append(f"Hyper-growth — revenue +{rg_pct:.0f}%")
        elif rg_pct > 15:
            signals.append(f"Strong growth — revenue +{rg_pct:.0f}%")
        else:
            concerns.append(f"Growth may not justify 'high-growth' classification — only +{rg_pct:.0f}%")

    if gm_pct is not None:
        if gm_pct > 60:
            signals.append(f"High gross margin ({gm_pct:.0f}%) — scalable unit economics")
        elif gm_pct < 20:
            concerns.append(f"Low gross margin ({gm_pct:.0f}%) — may never achieve profitability")

    if cash_runway_years is not None:
        if cash_runway_years > 3:
            signals.append(f"Cash runway: {cash_runway_years:.0f} years — ample time")
        elif cash_runway_years < 1:
            concerns.append(f"Cash runway: {cash_runway_years*12:.0f} months — urgent financing needed")

    if growth_decelerating:
        concerns.append("Growth rate decelerating — monitor trajectory")

    if beta is not None and beta > 2:
        concerns.append(f"Extreme volatility — beta {beta:.1f}")

    growth_score = 5
    if rg_pct is not None and rg_pct > 30: growth_score += 2
    elif rg_pct is not None and rg_pct > 15: growth_score += 1
    if gm_pct is not None and gm_pct > 60: growth_score += 1
    if cash_runway_years is not None and cash_runway_years > 2: growth_score += 1
    if not growth_decelerating: growth_score += 1
    growth_score = max(0, min(10, growth_score))

    return {
        'business_model': 'High-Growth (General)',
        'revenue_growth_pct': rg_pct,
        'earnings_growth_pct': (earnings_growth * 100) if earnings_growth is not None else None,
        'gross_margin_pct': gm_pct,
        'cash_runway_years': round(cash_runway_years, 1) if cash_runway_years is not None else None,
        'growth_decelerating': growth_decelerating,
        'beta': beta,
        'signals': signals,
        'concerns': concerns,
        'growth_score': growth_score,
    }


# ===========================================================================
# MASTER ALPHA ANALYSIS
# ===========================================================================

def alpha_analysis(ticker, existing_positions=None, current_weight_pct=0, framework=None):
    """Run the complete 2026 Strategic Growth Investment Framework analysis.
    Pass framework='high_growth_saas', 'traditional_value', etc. to override auto-detection."""
    ticker = ticker.upper().strip()
    data = fetch_alpha_data(ticker)
    info = data['info']

    if not info or info.get('marketCap') is None:
        return {'error': f"Could not fetch data for {ticker}. Check the ticker symbol."}

    # Step 1: Classify business model (or use override)
    if framework and framework in NoB_TYPES:
        nob_type = framework
    else:
        nob_type = classify_business_model(ticker, info)
    nob = NoB_TYPES.get(nob_type, NoB_TYPES['traditional_value'])

    # Step 2: Quantitative (NoB-routed)
    quantitative = quantitative_quadrant(data, nob_type)

    # Step 3: Qualitative (moat + performance signals)
    qualitative = qualitative_quadrant(data)

    # Step 4: Thematic
    thematic = thematic_classification(ticker, info)

    # Step 5: Risk management
    risk = risk_management_module(ticker, data, current_weight_pct, existing_positions)

    # Step 6: Portfolio context
    portfolio = portfolio_optimization_suggestions(ticker, data, existing_positions)

    # Step 7: Thesis
    thesis = generate_thesis(ticker, data, quantitative, qualitative, thematic, risk, nob_type)

    # Price performance
    price_data = data.get('price_data')
    price_perf = {}
    if price_data is not None and not price_data.empty:
        closes = price_data['Close'].values.flatten()
        current = closes[-1] if len(closes) > 0 else 0
        for days, label in [(21, '1m'), (63, '3m'), (126, '6m'), (252, '1y')]:
            if len(closes) > days:
                prev = closes[-days]
                if prev > 0:
                    price_perf[label] = ((current / prev) - 1) * 100
        if len(closes) >= 252:
            price_perf['52w_high'] = float(np.max(closes[-252:]))
            price_perf['52w_low'] = float(np.min(closes[-252:]))

    return {
        'ticker': ticker,
        'data': data,
        'nob_type': nob_type,
        'nob': nob,
        'quantitative': quantitative,
        'qualitative': qualitative,
        'thematic': thematic,
        'risk_management': risk,
        'portfolio': portfolio,
        'thesis': thesis,
        'price_performance': price_perf,
        'analysis_timestamp': datetime.now().isoformat(),
    }

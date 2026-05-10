"""
Stock Analysis Engine - 4-Layer Investment Framework
Analyzes any stock ticker through the lens of business quality, financial health,
competitive position, and valuation.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

# ---------------------------------------------------------------------------
# Competitor mappings (curated for major stocks, falls back to industry peers)
# ---------------------------------------------------------------------------
COMPETITOR_MAP = {
    'MSFT': ['AAPL', 'GOOGL', 'AMZN', 'ORCL', 'CRM'],
    'AAPL': ['MSFT', 'GOOGL', 'SAMSUNG', 'DELL'],
    'GOOGL': ['MSFT', 'AAPL', 'AMZN', 'META', 'BIDU'],
    'AMZN': ['MSFT', 'GOOGL', 'WMT', 'ORCL'],
    'META': ['GOOGL', 'SNAP', 'PINS', 'TWLO'],
    'NVDA': ['AMD', 'INTC', 'AVGO', 'QCOM', 'TSM'],
    'AMD': ['NVDA', 'INTC', 'QCOM'],
    'INTC': ['NVDA', 'AMD', 'TSM', 'QCOM'],
    'CRM': ['MSFT', 'ORCL', 'ADBE', 'NOW', 'HUBS'],
    'NOW': ['CRM', 'WDAY', 'TEAM', 'HUBS'],
    'ADBE': ['MSFT', 'CRM', 'INTU', 'ADSK'],
    'QLYS': ['CRWD', 'ZS', 'PANW', 'CHKP', 'TENB', 'RPD', 'OKTA'],
    'TENB': ['QLYS', 'CRWD', 'ZS', 'RPD', 'VRNS'],
    'OKTA': ['CRWD', 'ZS', 'PANW', 'MSFT', 'RPD'],
    'RPD': ['QLYS', 'CRWD', 'ZS', 'TENB'],
    'CRWD': ['PANW', 'ZS', 'S', 'QLYS', 'NET'],
    'ZS': ['CRWD', 'PANW', 'NET', 'CHKP', 'QLYS'],
    'PANW': ['CRWD', 'ZS', 'CHKP', 'FTNT', 'CSCO'],
    'CHKP': ['PANW', 'FTNT', 'CSCO', 'QLYS'],
    'APLD': ['EQIX', 'DLR', 'CORZ', 'IREN', 'HUT'],
    'FCEL': ['PLUG', 'BLDP', 'BE', 'HYSR'],
    # Singapore (SGX)
    'D05.SI': ['O39.SI', 'U11.SI', '0005.HK'],
    'O39.SI': ['D05.SI', 'U11.SI', '0005.HK'],
    'U11.SI': ['D05.SI', 'O39.SI', '0005.HK'],
    'Z74.SI': ['ST', 'VOD', 'T'],
    'C52.SI': ['SIA', 'CPA', 'CATHAY'],
    'BN4.SI': ['KT', 'KEP', 'SIE'],
    # Hong Kong (HKEX)
    '0700.HK': ['9988.HK', '3690.HK', 'BIDU', 'NTES', '9618.HK'],
    '9988.HK': ['0700.HK', '3690.HK', 'JD', 'PDD', '9618.HK'],
    '3690.HK': ['0700.HK', '9988.HK', 'BIDU'],
    '9618.HK': ['9988.HK', 'BIDU', 'JD', 'PDD'],
    '1299.HK': ['0005.HK', '3988.HK', '2628.HK', 'PRU'],
    '0005.HK': ['1299.HK', '3988.HK', '2888.HK', 'D05.SI'],
    'TSLA': ['BYD', 'RIVN', 'LCID', 'GM', 'F', 'NIO'],
    'JPM': ['BAC', 'WFC', 'C', 'GS', 'MS'],
    'WMT': ['AMZN', 'TGT', 'COST', 'KR'],
    'COST': ['WMT', 'TGT', 'BJ'],
    'XOM': ['CVX', 'COP', 'BP', 'SHEL'],
    'JNJ': ['PFE', 'MRK', 'ABBV', 'BMY'],
    'PG': ['UL', 'CL', 'KMB', 'CHD'],
    'DIS': ['NFLX', 'CMCSA', 'PARA', 'WBD'],
    'NFLX': ['DIS', 'AMZN', 'AAPL', 'PARA', 'WBD'],
}

# AI layer classification rules
# Layer 1: Infrastructure (chips, data centers, networking, cloud)
# Layer 2: Platforms & Models (foundation models, ML platforms, AI tools)
# Layer 3: Applications (AI-powered products for end users)
# Layer 4: AI-Adjacent (beneficiary but not core AI)
# Layer 0: Not AI-related

AI_LAYER_MAP = {
    # Layer 1 - Infrastructure
    'NVDA': 1, 'AMD': 1, 'INTC': 1, 'AVGO': 1, 'TSM': 1, 'QCOM': 1,
    'MRVL': 1, 'AMAT': 1, 'LRCX': 1, 'KLAC': 1, 'MU': 1,
    'APLD': 1, 'EQIX': 1, 'DLR': 1, 'SMFT': 1, 'CORZ': 1,
    'ANET': 1, 'CSCO': 1, 'JNPR': 1, 'SMCI': 1, 'DELL': 1,
    'HPE': 1, 'VRT': 1, 'PSTG': 1, 'NTAP': 1, 'WDC': 1, 'STX': 1,
    # Layer 2 - Platforms & Models
    'MSFT': 2, 'GOOGL': 2, 'AMZN': 2, 'META': 2, 'IBM': 2,
    'CRM': 2, 'NOW': 2, 'SNOW': 2, 'MDB': 2, 'DDOG': 2,
    'PLTR': 2, 'PATH': 2, 'AI': 2, 'CFLT': 2, 'ESTC': 2,
    'GTLB': 2, 'NET': 2, 'ADBE': 2, 'ORCL': 2, 'SAP': 2,
    # Layer 3 - Applications
    'ADSK': 3, 'ANSS': 3, 'PTC': 3, 'TYL': 3, 'MANH': 3,
    'ZM': 3, 'DOCU': 3, 'SHOP': 3, 'SQ': 3, 'TEAM': 3,
    'HUBS': 3, 'WDAY': 3, 'INTU': 3, 'NOW': 2,
    # Layer 4 - Adjacent (cybersecurity benefits from AI arms race)
    'QLYS': 4, 'CRWD': 4, 'ZS': 4, 'PANW': 4, 'CHKP': 4, 'TENB': 4, 'RPD': 4, 'OKTA': 4,
    'VRNS': 4, 'S': 4, 'FTNT': 4, 'NET': 4, 'CYBR': 4,
    # Layer 4 - Other adjacent
    'FCEL': 4, 'BE': 4, 'PLUG': 4, 'TSLA': 4, 'RIVN': 4,
    # SG / HK stocks
    'D05.SI': 0, 'O39.SI': 0, 'U11.SI': 0, 'Z74.SI': 0,  # financials/telecom
    '0700.HK': 2, '9988.HK': 2, '3690.HK': 2, '9618.HK': 2,  # Chinese tech platforms
    '1299.HK': 0, '0005.HK': 0,  # insurance/banking
    # Layer 0 - Not AI
    'KO': 0, 'PEP': 0, 'PG': 0, 'JNJ': 0, 'WMT': 0, 'COST': 0,
    'XOM': 0, 'CVX': 0, 'JPM': 0, 'BAC': 0, 'V': 0, 'MA': 0,
}

AI_LAYER_LABELS = {
    1: "AI Infrastructure (chips, data centers, networking)",
    2: "AI Platforms & Models (foundation models, ML tools)",
    3: "AI Applications (AI-powered end-user products)",
    4: "AI-Adjacent (benefits from AI but not core)",
    0: "Not AI-related",
}

# Industry stickiness ratings (1-10)
INDUSTRY_STICKINESS = {
    'software-infrastructure': 9,
    'software-application': 8,
    'information technology services': 7,
    'semiconductors': 6,
    'semiconductor equipment & materials': 7,
    'internet content & information': 5,
    'internet retail': 4,
    'telecom services': 8,
    'drug manufacturers': 9,
    'healthcare plans': 9,
    'medical devices': 8,
    'banks-diversified': 7,
    'credit services': 8,
    'insurance': 8,
    'aerospace & defense': 10,
    'electrical equipment & parts': 6,
    'renewable energy': 5,
    'oil & gas': 4,
    'retail': 3,
    'restaurants': 5,
    'consumer packaged goods': 8,
    'beverages': 9,
    'tobacco': 10,
    'entertainment': 3,
    'media': 4,
    'automotive': 3,
}


def safe_get(func, default=None):
    """Safely execute a function, returning default on failure."""
    try:
        return func()
    except Exception:
        return default


def fetch_financials(ticker):
    """Gather all financial data for a ticker."""
    tkr = yf.Ticker(ticker)
    info = safe_get(lambda: tkr.info, {})

    data = {
        'ticker': ticker.upper(),
        'info': info,
        'price': info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose'),
        'name': info.get('longName') or info.get('shortName', ticker),
        'sector': info.get('sector', 'N/A'),
        'industry': info.get('industry', 'N/A'),
        'website': info.get('website', 'N/A'),
        'description': info.get('longBusinessSummary', 'N/A'),
        'country': info.get('country', 'N/A'),
        'employees': info.get('fullTimeEmployees', 'N/A'),
    }

    # Financial statements
    data['income_annual'] = safe_get(lambda: tkr.financials)
    data['income_quarterly'] = safe_get(lambda: tkr.quarterly_income_stmt)
    data['balance_sheet'] = safe_get(lambda: tkr.balance_sheet)
    data['cashflow'] = safe_get(lambda: tkr.cashflow)

    # Price data — use history() for better international ticker support
    price_data = safe_get(lambda: tkr.history(period='5y'))
    data['price_data'] = price_data if (price_data is not None and not price_data.empty) else None

    return data


# ---------------------------------------------------------------------------
# LAYER 1: Can the business support itself?
# ---------------------------------------------------------------------------
def layer1_analysis(data):
    info = data['info']
    inc = data['income_annual']

    analysis = {
        'gross_margin': info.get('grossMargins'),
        'operating_margin': info.get('operatingMargins'),
        'net_margin': info.get('profitMargins'),
        'ebitda_margin': info.get('ebitdaMargins'),
        'revenue_growth': info.get('revenueGrowth'),
        'earnings_growth': info.get('earningsGrowth'),
        'roe': info.get('returnOnEquity'),
        'roa': info.get('returnOnAssets'),
    }

    # Revenue trend
    revenue_trend = []
    if inc is not None and not inc.empty:
        for row in ['Total Revenue', 'Operating Revenue']:
            if row in inc.index:
                for col in inc.columns[:5]:
                    val = inc.loc[row, col]
                    if pd.notna(val) and val > 0:
                        revenue_trend.append({
                            'date': col.strftime('%Y-%m-%d'),
                            'revenue': val
                        })
                if revenue_trend:
                    break

    analysis['revenue_trend'] = revenue_trend

    # Income trend
    income_trend = []
    if inc is not None and not inc.empty:
        for row in ['Net Income', 'Net Income Common Stockholders']:
            if row in inc.index:
                for col in inc.columns[:5]:
                    val = inc.loc[row, col]
                    if pd.notna(val):
                        income_trend.append({
                            'date': col.strftime('%Y-%m-%d'),
                            'net_income': val
                        })
                if income_trend:
                    break

    analysis['income_trend'] = income_trend

    # Assessment
    gm = analysis['gross_margin']
    om = analysis['operating_margin']
    rg = analysis['revenue_growth']

    issues = []
    positives = []

    if gm is not None:
        if gm > 0.40:
            positives.append(f"Strong gross margin ({gm*100:.1f}%) — significant pricing power")
        elif gm > 0.20:
            positives.append(f"Healthy gross margin ({gm*100:.1f}%)")
        elif gm > 0:
            positives.append(f"Positive but thin gross margin ({gm*100:.1f}%)")
        elif gm < 0:
            issues.append(f"CRITICAL: Negative gross margin ({gm*100:.1f}%) — loses money on every unit sold")

    if om is not None:
        if om > 0.15:
            positives.append(f"Strong operating margin ({om*100:.1f}%) — business funds itself comfortably")
        elif om > 0:
            positives.append(f"Positive operating margin ({om*100:.1f}%) — operationally break-even or better")
        elif om < -0.20:
            issues.append(f"Deep operating losses ({om*100:.1f}%) — far from self-sufficiency")
        elif om < 0:
            issues.append(f"Operating at a loss ({om*100:.1f}%)")

    if rg is not None:
        if rg > 0.30:
            positives.append(f"High revenue growth ({rg*100:.1f}%) — strong demand")
        elif rg > 0.10:
            positives.append(f"Moderate revenue growth ({rg*100:.1f}%)")
        elif rg < 0:
            issues.append(f"Revenue declining ({rg*100:.1f}%) — shrinking business")

    # Score: 0-10
    score = 5
    if gm is not None:
        if gm > 0.50: score += 2
        elif gm > 0.30: score += 1.5
        elif gm > 0.10: score += 0.5
        elif gm < 0: score -= 3

    if om is not None:
        if om > 0.20: score += 2
        elif om > 0.10: score += 1
        elif om > 0: score += 0.5
        elif om < -0.30: score -= 2

    if rg is not None:
        if rg > 0.30: score += 1
        elif rg < 0: score -= 1

    score = max(0, min(10, score))

    analysis['verdict'] = 'PASS' if gm is not None and gm > 0 else 'FAIL'
    analysis['score'] = score
    analysis['issues'] = issues
    analysis['positives'] = positives
    analysis['summary'] = (
        "The core business model works — the product sells for more than it costs to produce."
        if analysis['verdict'] == 'PASS'
        else "The core business model is broken — the product costs more to make than customers pay."
    )

    return analysis


# ---------------------------------------------------------------------------
# LAYER 2: How is it staying alive?
# ---------------------------------------------------------------------------
def layer2_analysis(data):
    info = data['info']
    cf = data['cashflow']
    bs = data['balance_sheet']
    inc_q = data['income_quarterly']

    analysis = {
        'total_cash': info.get('totalCash'),
        'total_debt': info.get('totalDebt'),
        'debt_to_equity': info.get('debtToEquity'),
        'current_ratio': info.get('currentRatio'),
        'operating_cf': info.get('operatingCashflow'),
        'free_cashflow': info.get('freeCashflow'),
    }

    # Cash flow trends
    cf_trends = {}
    if cf is not None and not cf.empty:
        for row in ['Free Cash Flow', 'Operating Cash Flow', 'Capital Expenditure',
                    'Common Stock Issuance', 'Net Common Stock Issuance',
                    'Issuance Of Debt', 'Net Long Term Debt Issuance']:
            if row in cf.index:
                vals = []
                for col in cf.columns[:5]:
                    val = cf.loc[row, col]
                    if pd.notna(val):
                        vals.append({'date': col.strftime('%Y-%m-%d'), 'value': val})
                if vals:
                    cf_trends[row] = vals

    analysis['cf_trends'] = cf_trends

    # Share dilution
    shares_trend = []
    if inc_q is not None and not inc_q.empty:
        for row in ['Diluted Average Shares', 'Basic Average Shares']:
            if row in inc_q.index:
                for col in inc_q.columns[:10]:
                    val = inc_q.loc[row, col]
                    if pd.notna(val) and val > 0:
                        shares_trend.append({
                            'date': col.strftime('%Y-%m-%d'),
                            'shares': val
                        })
                if shares_trend:
                    break

    analysis['shares_trend'] = shares_trend

    # Balance sheet trends
    bs_trends = {}
    if bs is not None and not bs.empty:
        for row in ['Total Assets', 'Total Debt', 'Cash And Cash Equivalents',
                    'Stockholders Equity', 'Working Capital']:
            if row in bs.index:
                vals = []
                for col in bs.columns[:5]:
                    val = bs.loc[row, col]
                    if pd.notna(val):
                        vals.append({'date': col.strftime('%Y-%m-%d'), 'value': val})
                if vals:
                    bs_trends[row] = vals

    analysis['bs_trends'] = bs_trends

    # Assessment
    issues = []
    positives = []

    ocf = analysis['operating_cf']
    fcf = analysis['free_cashflow']

    if ocf is not None:
        if ocf > 0:
            positives.append(f"Positive operating cash flow (${ocf/1e6:.0f}M) — operations generate cash")
        else:
            issues.append(f"Negative operating cash flow (${ocf/1e6:.0f}M) — operations consume cash")

    if fcf is not None:
        if fcf > 0:
            positives.append(f"Positive free cash flow (${fcf/1e6:.0f}M) — self-funding after CapEx")
        else:
            issues.append(f"Negative free cash flow (${fcf/1e6:.0f}M) — needs external funding")

    # Check for dilution
    if len(shares_trend) >= 2:
        old_shares = shares_trend[-1]['shares']
        new_shares = shares_trend[0]['shares']
        dilution_pct = ((new_shares / old_shares) - 1) * 100
        if dilution_pct > 50:
            issues.append(f"Severe dilution: shares up {dilution_pct:.0f}% — shareholders being heavily diluted")
        elif dilution_pct > 20:
            issues.append(f"Moderate dilution: shares up {dilution_pct:.0f}%")
        elif dilution_pct < -10:
            positives.append(f"Share count declining ({dilution_pct:.0f}%) — company buying back stock")
        analysis['dilution_pct'] = dilution_pct

    # Check for stock issuance
    total_issuance = 0
    if 'Common Stock Issuance' in cf_trends or 'Net Common Stock Issuance' in cf_trends:
        key = 'Common Stock Issuance' if 'Common Stock Issuance' in cf_trends else 'Net Common Stock Issuance'
        for item in cf_trends[key]:
            if item['value'] > 0:
                total_issuance += item['value']

    analysis['total_stock_issuance'] = total_issuance

    # Check debt trend
    if 'Total Debt' in bs_trends and len(bs_trends['Total Debt']) >= 2:
        old_debt = bs_trends['Total Debt'][-1]['value']
        new_debt = bs_trends['Total Debt'][0]['value']
        if new_debt > old_debt * 3:
            issues.append(f"Debt explosion: debt up {(new_debt/old_debt - 1)*100:.0f}% — leverage increasing rapidly")
        elif new_debt > old_debt * 1.5:
            issues.append(f"Debt growing faster than equity")

    # Survival method
    if ocf is not None and ocf > 0:
        survival = "Self-funded from operations"
    elif total_issuance > 100e6:
        survival = "Funded by selling shares (heavy dilution)"
    elif total_issuance > 0:
        survival = "Funded by selling shares (moderate dilution)"
    elif analysis['total_debt'] and analysis['total_debt'] > 1e9:
        survival = "Funded by debt"
    else:
        survival = "Burning cash reserves"

    analysis['survival_method'] = survival
    analysis['issues'] = issues
    analysis['positives'] = positives

    return analysis


# ---------------------------------------------------------------------------
# LAYER 3: Is there a turnaround thesis?
# ---------------------------------------------------------------------------
def layer3_analysis(data):
    info = data['info']
    inc = data['income_annual']
    inc_q = data['income_quarterly']

    analysis = {}

    # Revenue trajectory from annual data
    rev_growth_rates = []
    if inc is not None and not inc.empty:
        rev_row = 'Total Revenue' if 'Total Revenue' in inc.index else 'Operating Revenue'
        if rev_row in inc.index:
            revs = []
            for col in inc.columns[:5]:
                val = inc.loc[rev_row, col]
                if pd.notna(val) and val > 0:
                    revs.append(val)
            for i in range(1, len(revs)):
                if revs[i-1] > 0:
                    rev_growth_rates.append((revs[i] / revs[i-1] - 1) * 100)

    analysis['rev_growth_rates'] = rev_growth_rates

    # Gross margin trend from annual data
    gm_trend = []
    if inc is not None and not inc.empty:
        if 'Gross Profit' in inc.index:
            rev_row = 'Total Revenue' if 'Total Revenue' in inc.index else 'Operating Revenue'
            if rev_row in inc.index:
                for col in inc.columns[:5]:
                    gp = inc.loc['Gross Profit', col]
                    rev = inc.loc[rev_row, col]
                    if pd.notna(gp) and pd.notna(rev) and rev > 0:
                        gm_trend.append({
                            'date': col.strftime('%Y-%m-%d'),
                            'gross_margin': (gp / rev) * 100
                        })

    analysis['gm_trend'] = gm_trend

    # Quarterly trend
    q_rev_trend = []
    if inc_q is not None and not inc_q.empty:
        rev_row = None
        for candidate in ['Total Revenue', 'Operating Revenue']:
            if candidate in inc_q.index:
                rev_row = candidate
                break
        gp_row = 'Gross Profit' if 'Gross Profit' in inc_q.index else None
        ni_row = 'Net Income' if 'Net Income' in inc_q.index else None
        if rev_row:
            for col in inc_q.columns[:8]:
                entry = {'date': col.strftime('%Y-%m-%d')}
                rv = inc_q.loc[rev_row, col]
                if pd.notna(rv):
                    entry['revenue'] = rv
                if gp_row:
                    gpv = inc_q.loc[gp_row, col]
                    if pd.notna(gpv):
                        entry['gross_profit'] = gpv
                if ni_row:
                    niv = inc_q.loc[ni_row, col]
                    if pd.notna(niv):
                        entry['net_income'] = niv
                if 'revenue' in entry:
                    q_rev_trend.append(entry)

    analysis['quarterly_revenue'] = q_rev_trend

    # Bull and bear cases
    bulls = []
    bears = []

    gm = info.get('grossMargins')
    rg = info.get('revenueGrowth')
    om = info.get('operatingMargins')

    if gm is not None and gm > 0.30 and len(gm_trend) >= 2:
        if gm_trend[0]['gross_margin'] > gm_trend[-1]['gross_margin']:
            bulls.append("Gross margins are expanding — operating leverage building")
        elif gm_trend[0]['gross_margin'] < gm_trend[-1]['gross_margin']:
            bears.append("Gross margins are declining — pricing power eroding")

    if rg is not None and rg > 0.20:
        bulls.append(f"Revenue growing at {rg*100:.0f}% — strong demand tailwind")
    elif rg is not None and rg < 0:
        bears.append("Revenue shrinking — market may be in structural decline")

    if om is not None and om < -0.10:
        bears.append(f"Deep operating losses ({om*100:.0f}%) — path to profitability unclear")
    elif om is not None and om > 0.15:
        bulls.append("Already profitable with margin buffer — thesis is about durability, not survival")

    # Debt concern
    dte = info.get('debtToEquity')
    if dte is not None and dte > 100:
        bears.append(f"Debt/Equity of {dte:.0f} — high leverage limits strategic flexibility")

    # Cash runway
    cash = info.get('totalCash', 0) or 0
    fcf = info.get('freeCashflow', 0) or 0
    if fcf < 0 and cash > 0:
        runway = cash / abs(fcf)
        if runway < 2:
            bears.append(f"Cash runway under 2 years at current burn rate")
        elif runway > 5:
            bulls.append(f"Cash runway of {runway:.0f} years — ample time to execute")

    analysis['bull_case'] = bulls
    analysis['bear_case'] = bears
    analysis['verdict'] = 'PLAUSIBLE' if len(bulls) >= len(bears) else 'NARROW' if len(bulls) > 0 else 'UNLIKELY'

    return analysis


# ---------------------------------------------------------------------------
# LAYER 4: What are you actually buying?
# ---------------------------------------------------------------------------
def layer4_analysis(data):
    info = data['info']

    mcap = info.get('marketCap')
    ev = info.get('enterpriseValue')
    price = data['price']
    shares = info.get('sharesOutstanding') or (mcap / price if price and mcap else None)

    analysis = {
        'market_cap': mcap,
        'enterprise_value': ev,
        'trailing_pe': info.get('trailingPE'),
        'forward_pe': info.get('forwardPE'),
        'price_to_book': info.get('priceToBook'),
        'price_to_sales': info.get('priceToSales'),
        'ev_to_revenue': info.get('enterpriseToRevenue'),
        'ev_to_ebitda': info.get('enterpriseToEbitda'),
        'fcf_yield': None,
        'fcf_ex_capex_yield': None,
        'beta': info.get('beta'),
        'short_pct': info.get('shortPercentOfFloat'),
    }

    fcf_v = info.get('freeCashflow')
    ocf_v = info.get('operatingCashflow')
    if fcf_v and mcap and mcap > 0:
        analysis['fcf_yield'] = (fcf_v / mcap) * 100
    if ocf_v and mcap and mcap > 0:
        analysis['fcf_ex_capex_yield'] = (ocf_v / mcap) * 100

    # Valuation assessment
    issues = []
    positives = []

    fpe = analysis['forward_pe']
    tpe = analysis['trailing_pe']
    ps = analysis['price_to_sales']
    fcf_y = analysis['fcf_yield']

    if tpe is not None:
        if tpe < 0:
            issues.append("Unprofitable — P/E ratio meaningless; you're buying potential, not earnings")
        elif tpe < 15:
            positives.append(f"Trailing P/E of {tpe:.1f}x — cheap on current earnings")
        elif tpe < 25:
            positives.append(f"Trailing P/E of {tpe:.1f}x — reasonable valuation")
        elif tpe > 50:
            issues.append(f"Trailing P/E of {tpe:.1f}x — very expensive on current earnings")

    if fcf_y is not None:
        if fcf_y > 8:
            positives.append(f"FCF yield of {fcf_y:.1f}% — strong cash returns at current price")
        elif fcf_y > 5:
            positives.append(f"FCF yield of {fcf_y:.1f}% — decent cash generation relative to price")
        elif fcf_y < 0:
            issues.append("Negative FCF yield — burning cash, not generating it")

    if ps is not None:
        if ps > 20:
            issues.append(f"Price/Sales of {ps:.1f}x — pricing in years of growth")
        elif ps < 2:
            positives.append(f"Price/Sales of {ps:.1f}x — inexpensive on revenue basis")

    beta = analysis['beta']
    if beta is not None:
        if beta > 2:
            issues.append(f"Beta of {beta:.1f} — extremely volatile, will move 2x+ the market")
        elif beta > 1.5:
            issues.append(f"Beta of {beta:.1f} — high volatility")

    analysis['issues'] = issues
    analysis['positives'] = positives

    # Summary
    net_good = len(positives) - len(issues)
    if net_good >= 2:
        analysis['summary'] = "Reasonable valuation with multiple positive signals. The price appears to offer value relative to fundamentals."
    elif net_good >= 0:
        analysis['summary'] = "Mixed valuation picture. Some metrics look reasonable, others expensive."
    else:
        analysis['summary'] = "Expensive on most metrics. You're paying a premium and betting on significant future growth to justify the price."

    return analysis


# ---------------------------------------------------------------------------
# COMPETITOR ANALYSIS
# ---------------------------------------------------------------------------
def get_competitors(ticker, info):
    """Get competitors from curated map or industry peers."""
    ticker = ticker.upper()
    if ticker in COMPETITOR_MAP:
        return COMPETITOR_MAP[ticker]

    # Fallback: try to find peers by industry
    industry = (info.get('industry') or '').lower()
    sector = (info.get('sector') or '').lower()

    # Return empty — we'll tell the user no competitors found
    return []


def analyze_competitors(ticker, competitors, data):
    """Compare company against competitors on key metrics."""
    all_tickers = [ticker] + competitors
    results = {}

    def fetch_one(t):
        try:
            tkr = yf.Ticker(t)
            info = tkr.info
            hist = safe_get(lambda: tkr.history(period='2y'))

            # Revenue trend
            inc = safe_get(lambda: tkr.financials)
            rev_trend = []
            if inc is not None and not inc.empty:
                for row in ['Total Revenue', 'Operating Revenue']:
                    if row in inc.index:
                        for col in inc.columns[:4]:
                            val = inc.loc[row, col]
                            if pd.notna(val) and val > 0:
                                rev_trend.append({'date': col.strftime('%Y-%m-%d'), 'revenue': val})
                        if rev_trend:
                            break

            # Stock return
            ret_1y = None
            if hist is not None and not hist.empty and len(hist) >= 252:
                ret_1y = ((hist['Close'].iloc[-1] / hist['Close'].iloc[-252]) - 1) * 100

            return {
                'ticker': t,
                'name': info.get('shortName', t),
                'market_cap': info.get('marketCap'),
                'revenue_growth': info.get('revenueGrowth'),
                'earnings_growth': info.get('earningsGrowth'),
                'gross_margin': info.get('grossMargins'),
                'profit_margin': info.get('profitMargins'),
                'trailing_pe': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'price_to_book': info.get('priceToBook'),
                'price_to_sales': info.get('priceToSales'),
                'ev_to_revenue': info.get('enterpriseToRevenue'),
                'ev_to_ebitda': info.get('enterpriseToEbitda'),
                'debt_to_equity': info.get('debtToEquity'),
                'return_1y': ret_1y,
                'revenue_trend': rev_trend,
                'recommendation': info.get('recommendationKey'),
            }
        except Exception as e:
            return {'ticker': t, 'error': str(e)}

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(fetch_one, t): t for t in all_tickers}
        for future in as_completed(futures):
            result = future.result()
            results[result['ticker']] = result

    return results


# ---------------------------------------------------------------------------
# AI LAYER CLASSIFICATION
# ---------------------------------------------------------------------------
def classify_ai_layer(ticker, info):
    """Classify company's relationship to AI development."""
    ticker = ticker.upper()
    if ticker in AI_LAYER_MAP:
        return AI_LAYER_MAP[ticker], AI_LAYER_LABELS[AI_LAYER_MAP[ticker]]

    # Heuristic classification based on industry/sector/description
    industry = (info.get('industry') or '').lower()
    sector = (info.get('sector') or '').lower()
    desc = (info.get('longBusinessSummary') or '').lower()

    ai_keywords_layer1 = ['chip', 'semiconductor', 'processor', 'gpu', 'data center', 'networking',
                          'infrastructure', 'memory', 'server', 'cloud computing', 'fiber',
                          'cooling', 'power management', 'circuit']
    ai_keywords_layer2 = ['artificial intelligence', 'machine learning', 'deep learning', 'foundation model',
                          'language model', 'ai platform', 'ml platform', 'neural network',
                          'training', 'inference', 'large language']
    ai_keywords_layer3 = ['ai-powered', 'ai assistant', 'copilot', 'autonomous', 'computer vision',
                          'natural language processing', 'speech recognition', 'generative ai']

    score = 0
    for kw in ai_keywords_layer1:
        if kw in desc or kw in industry:
            score = 1
            break
    if score == 0:
        for kw in ai_keywords_layer2:
            if kw in desc:
                score = 2
                break
    if score == 0:
        for kw in ai_keywords_layer3:
            if kw in desc:
                score = 3
                break

    # Check if it's a beneficiary but not core
    if score == 0:
        if any(kw in desc for kw in ['energy', 'power', 'battery', 'electric vehicle',
                                       'automation', 'robotics', 'data', 'digital']):
            score = 4

    return score, AI_LAYER_LABELS.get(score, 'Not AI-related')


# ---------------------------------------------------------------------------
# BUSINESS STICKINESS
# ---------------------------------------------------------------------------
def analyze_stickiness(data, info):
    """Assess how sticky the business is — how hard for customers to leave."""
    industry = (info.get('industry') or '').lower()
    sector = (info.get('sector') or '').lower()
    desc = (info.get('longBusinessSummary') or '').lower()
    gm = info.get('grossMargins')

    # Base score from industry
    base_score = 5
    for key, score in INDUSTRY_STICKINESS.items():
        if key in industry or key in sector:
            base_score = score
            break

    # Adjust based on gross margin (higher = more pricing power = stickier)
    gm_adjust = 0
    if gm is not None:
        if gm > 0.80: gm_adjust = 2
        elif gm > 0.60: gm_adjust = 1.5
        elif gm > 0.40: gm_adjust = 1
        elif gm > 0.20: gm_adjust = 0
        elif gm > 0: gm_adjust = -1
        elif gm < 0: gm_adjust = -2

    # Revenue growth stability
    rg = info.get('revenueGrowth')
    rg_adjust = 0
    if rg is not None:
        if rg > 0.20: rg_adjust = 1  # growing = customers staying and expanding
        elif rg < -0.10: rg_adjust = -2  # shrinking = customers leaving

    # Qualitative factors from description
    qual_score = 0
    stickiness_keywords = {
        'subscription': 2, 'recurring': 2, 'contract': 1, 'enterprise': 1,
        'mission-critical': 3, 'compliance': 2, 'regulatory': 2, 'infrastructure': 2,
        'platform': 1, 'integrated': 1, 'ecosystem': 1, 'database': 2,
        'payroll': 3, 'accounting': 3, 'security': 2, 'banking': 3,
        'healthcare': 2, 'insurance': 2, 'telecom': 2, 'utility': 3,
    }
    for kw, pts in stickiness_keywords.items():
        if kw in desc or kw in industry:
            qual_score = max(qual_score, pts)

    total = base_score + gm_adjust + rg_adjust + qual_score
    total = max(0, min(10, total))

    # Interpretation
    if total >= 8:
        label = "Very High — customers face extreme switching costs"
    elif total >= 6:
        label = "High — significant friction to leave"
    elif total >= 4:
        label = "Moderate — some switching costs but not locked in"
    elif total >= 2:
        label = "Low — customers can easily switch"
    else:
        label = "Very Low — commodity-like, no customer lock-in"

    return {
        'score': total,
        'label': label,
        'factors': {
            'industry_base': base_score,
            'gross_margin_adj': gm_adjust,
            'growth_adj': rg_adjust,
            'qualitative': qual_score,
        }
    }


# ---------------------------------------------------------------------------
# CUSTOMER ANALYSIS
# ---------------------------------------------------------------------------
def analyze_company_profile(info, news_articles=None):
    """Extract company overview: management, ownership, geography, deals."""
    profile = {}

    # --- Management ---
    officers = info.get('companyOfficers', [])
    mgmt = []
    for o in officers[:6]:
        name = o.get('name', '')
        title = o.get('title', '')
        age = o.get('age')
        total_pay = o.get('totalPay')
        exercised = o.get('exercisedValue', 0) or 0
        mgmt.append({
            'name': name,
            'title': title,
            'age': age,
            'total_pay': total_pay,
            'exercised_value': exercised,
        })
    profile['management'] = mgmt

    # --- Ownership ---
    insider_pct = info.get('heldPercentInsiders')
    inst_pct = info.get('heldPercentInstitutions')
    profile['insider_ownership'] = insider_pct * 100 if insider_pct else None
    profile['institutional_ownership'] = inst_pct * 100 if inst_pct else None

    # --- Geography ---
    geo = {
        'country': info.get('country', ''),
        'state': info.get('state', ''),
        'city': info.get('city', ''),
        'address': f"{info.get('address1', '')}, {info.get('city', '')}, {info.get('state', '')}".strip(', '),
        'employees': info.get('fullTimeEmployees'),
    }
    profile['geography'] = geo

    # Extract geographic mentions from business summary
    desc = (info.get('longBusinessSummary') or '').lower()
    regions = []
    geo_keywords = {
        'united states': 'US', 'north america': 'North America', 'europe': 'Europe',
        'asia pacific': 'Asia-Pacific', 'asia': 'Asia', 'latin america': 'Latin America',
        'middle east': 'Middle East', 'africa': 'Africa', 'china': 'China',
        'japan': 'Japan', 'india': 'India', 'southeast asia': 'SE Asia',
        'australia': 'Australia', 'canada': 'Canada', 'uk': 'UK',
        'germany': 'Germany', 'france': 'France', 'singapore': 'Singapore',
        'internationally': 'International',
    }
    for kw, label in geo_keywords.items():
        if kw in desc:
            regions.append(label)
    profile['regions'] = list(dict.fromkeys(regions))  # dedupe preserve order

    # --- Main clients ---
    client_kw = {
        'fortune 500': 'Fortune 500', 'fortune 100': 'Fortune 100', 'fortune 1000': 'Fortune 1000',
        'enterprise': 'Enterprise', 'government': 'Government', 'federal': 'Federal Government',
        'healthcare': 'Healthcare', 'financial services': 'Financial Services',
        'bank': 'Banking', 'insurance': 'Insurance', 'retail': 'Retail',
        'telecom': 'Telecom', 'energy': 'Energy', 'manufacturing': 'Manufacturing',
        'small business': 'SMB', 'mid-market': 'Mid-Market', 'consumer': 'Consumer',
        'education': 'Education', 'technology': 'Technology',
    }
    clients = []
    for kw, label in client_kw.items():
        if kw in desc:
            clients.append(label)
    profile['client_types'] = clients if clients else ['Not specified']

    # --- Recent deals from news ---
    deals = []
    if news_articles:
        deal_keywords = ['deal', 'partnership', 'contract', 'acquisition', 'acquire',
                         'merger', 'launch', 'expansion', 'collaboration', 'agreement',
                         'selected by', 'wins', 'won', 'signs', 'announced']
        for a in news_articles[:15]:
            title = (a.get('title', '')).lower()
            if any(kw in title for kw in deal_keywords):
                deals.append(a.get('title', '')[:120])
        profile['recent_deals'] = deals[:5]

    return profile


def analyze_customers(info):
    """Identify likely main customers based on industry and business description."""
    desc = (info.get('longBusinessSummary') or '').lower()
    industry = (info.get('industry') or '').lower()
    sector = (info.get('sector') or '').lower()

    customer_profile = {
        'type': 'Unknown',
        'examples': [],
        'concentration_risk': 'Unknown',
    }

    # Enterprise/B2B indicators
    enterprise_kw = ['enterprise', 'business', 'organization', 'government', 'federal',
                     'fortune', 'corporate', 'companies', 'financial institution']
    consumer_kw = ['consumer', 'individual', 'household', 'personal', 'user', 'family']
    smb_kw = ['small business', 'medium business', 'startup', 'developer']

    if any(kw in desc for kw in enterprise_kw):
        customer_profile['type'] = 'Enterprise / Large Organizations'
        customer_profile['concentration_risk'] = 'Medium — likely has a few large customers'
    elif any(kw in desc for kw in consumer_kw):
        customer_profile['type'] = 'Consumers / Individuals'
        customer_profile['concentration_risk'] = 'Low — highly diversified customer base'
    elif any(kw in desc for kw in smb_kw):
        customer_profile['type'] = 'SMBs / Developers'
        customer_profile['concentration_risk'] = 'Low-Medium — broad base of smaller customers'
    else:
        customer_profile['type'] = 'Mixed / Industry-specific'

    # Customer concentration from info
    # Some companies report this, but yfinance may not have it

    return customer_profile


# ---------------------------------------------------------------------------
# NEWS SENTIMENT
# ---------------------------------------------------------------------------
def analyze_news(ticker):
    """Fetch recent news and compute basic sentiment."""
    try:
        tkr = yf.Ticker(ticker)
        news = safe_get(lambda: tkr.news, [])
    except Exception:
        return {'articles': [], 'sentiment': 'No data', 'count': 0}

    articles = []
    positive_words = ['beat', 'raise', 'upgrade', 'growth', 'profit', 'gain', 'surge', 'strong',
                      'positive', 'outperform', 'buy', 'opportunity', 'momentum', 'record']
    negative_words = ['miss', 'cut', 'downgrade', 'loss', 'decline', 'drop', 'weak', 'negative',
                      'underperform', 'sell', 'risk', 'concern', 'layoff', 'investigation', 'lawsuit']

    pos_count = 0
    neg_count = 0

    for item in news[:20]:
        content = item.get('content', {}) or {}
        title = item.get('title', '') or content.get('title', '')
        summary = item.get('summary', '') or content.get('summary', '')
        text = (title + ' ' + summary).lower()

        pos = sum(1 for w in positive_words if w in text)
        neg = sum(1 for w in negative_words if w in text)

        if pos > neg:
            pos_count += 1
            sentiment = 'Positive'
        elif neg > pos:
            neg_count += 1
            sentiment = 'Negative'
        else:
            sentiment = 'Neutral'

        link = ''
        raw_link = (item.get('link') or
                    content.get('canonicalUrl') or
                    content.get('clickThroughUrl') or '')
        if isinstance(raw_link, dict):
            link = raw_link.get('url', '')
        elif isinstance(raw_link, str):
            link = raw_link

        articles.append({
            'title': title[:120],
            'publisher': item.get('publisher', ''),
            'date': datetime.fromtimestamp(item.get('providerPublishTime', 0)).strftime('%Y-%m-%d') if item.get('providerPublishTime') else '',
            'sentiment': sentiment,
            'link': link,
        })

    if pos_count > neg_count:
        overall = 'Bullish'
    elif neg_count > pos_count:
        overall = 'Bearish'
    else:
        overall = 'Neutral'

    return {
        'articles': articles[:10],
        'positive': pos_count,
        'negative': neg_count,
        'sentiment': overall,
        'count': len(articles),
    }


# ---------------------------------------------------------------------------
# RISK FACTORS
# ---------------------------------------------------------------------------
def analyze_risks(data, info):
    """Identify key risk factors."""
    risks = []

    # Financial risks
    dte = info.get('debtToEquity')
    if dte and dte > 100:
        risks.append("High financial leverage — vulnerable to rate increases or credit tightening")

    cr = info.get('currentRatio')
    if cr and cr < 1:
        risks.append("Current ratio below 1 — potential liquidity issues")

    fcf = info.get('freeCashflow')
    if fcf and fcf < 0:
        risks.append("Negative free cash flow — dependent on external financing")

    # Business risks
    gm = info.get('grossMargins')
    if gm is not None and gm < 0.10:
        risks.append("Thin gross margins — vulnerable to cost inflation or price competition")

    rg = info.get('revenueGrowth')
    if rg is not None and rg < 0:
        risks.append("Declining revenue — may indicate structural market decline or competitive displacement")

    # Volatility
    beta = info.get('beta')
    if beta and beta > 2:
        risks.append(f"Extreme volatility (Beta={beta:.1f}) — stock may swing wildly on market moves")

    # Short interest
    short = info.get('shortPercentOfFloat')
    if short and short > 0.15:
        risks.append(f"High short interest ({short*100:.0f}% of float) — potential for short squeeze or indicates bearish sentiment")

    # Concentration
    desc = (info.get('longBusinessSummary') or '')
    if 'single customer' in desc.lower() or 'concentrated' in desc.lower():
        risks.append("Customer concentration risk — loss of one customer could significantly impact revenue")

    if not risks:
        risks.append("No major red flags identified from available data")

    return risks


# ---------------------------------------------------------------------------
# MASTER ANALYSIS FUNCTION
# ---------------------------------------------------------------------------
def full_analysis(ticker):
    """Run the complete 4-layer analysis on a ticker."""
    ticker = ticker.upper().strip()

    # Fetch data
    data = fetch_financials(ticker)
    info = data['info']

    if not info or info.get('marketCap') is None:
        return {'error': f"Could not fetch data for {ticker}. Check the ticker symbol."}

    # Run all analyses
    l1 = layer1_analysis(data)
    l2 = layer2_analysis(data)
    l3 = layer3_analysis(data)
    l4 = layer4_analysis(data)

    # Stickiness
    stickiness = analyze_stickiness(data, info)

    # Competitors
    competitors = get_competitors(ticker, info)
    comp_data = analyze_competitors(ticker, competitors, data) if competitors else {}

    # AI Layer
    ai_layer, ai_label = classify_ai_layer(ticker, info)

    # Customers
    customers = analyze_customers(info)

    # News
    news = analyze_news(ticker)

    # Company Profile
    company_profile = analyze_company_profile(info, news.get('articles', []))

    # Risks
    risks = analyze_risks(data, info)

    # Price performance
    price_data = data.get('price_data')
    price_perf = {}
    if price_data is not None and not price_data.empty:
        closes = price_data['Close'].values.flatten()
        current = closes[-1]
        for days, label in [(21, '1m'), (63, '3m'), (126, '6m'), (252, '1y')]:
            if len(closes) > days:
                prev = closes[-days]
                price_perf[label] = ((current/prev) - 1) * 100

        if len(closes) >= 252:
            price_perf['52w_high'] = np.max(closes[-252:])
            price_perf['52w_low'] = np.min(closes[-252:])

    return {
        'ticker': ticker,
        'data': data,
        'layer1': l1,
        'layer2': l2,
        'layer3': l3,
        'layer4': l4,
        'stickiness': stickiness,
        'competitors': comp_data,
        'competitor_list': competitors,
        'ai_layer': ai_layer,
        'ai_label': ai_label,
        'customers': customers,
        'company_profile': company_profile,
        'news': news,
        'risks': risks,
        'price_performance': price_perf,
    }

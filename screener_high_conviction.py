"""
High Conviction Stock Screener — 2026 Framework
Scans a curated watchlist for stocks meeting HIGH CONVICTION criteria:
  - Moat Rating >= 7
  - Risk Score <= 2
  - NRR (installed growth) >= 120% OR strong Forward R40 inflection
Also surfaces MODERATE CONVICTION candidates as a secondary tier.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stock_analyzer.alpha_engine import alpha_analysis
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# ===========================================================================
# CURATED WATCHLIST — ~120 stocks across all sectors & markets
# ===========================================================================
WATCHLIST = [
    # US Tech — SaaS / Cloud
    'MSFT', 'CRM', 'ADBE', 'NOW', 'SNOW', 'DDOG', 'CRWD', 'PANW', 'ZS',
    'QLYS', 'NET', 'MDB', 'HUBS', 'TEAM', 'WDAY', 'INTU', 'ADSK', 'PLTR',
    # US Tech — Semiconductors / AI Infra
    'NVDA', 'AMD', 'AVGO', 'MU', 'MRVL', 'AMAT', 'LRCX', 'KLAC', 'TXN',
    'QCOM', 'INTC', 'SMCI', 'ANET', 'DELL', 'STX', 'WDC',
    # US Tech — Mega Cap
    'AAPL', 'GOOGL', 'AMZN', 'META', 'TSLA',
    # Energy / Industrial
    'BE', 'NEE', 'GEV', 'FSLR', 'CEG', 'VST', 'XOM', 'CVX', 'COP',
    'CAT', 'GE', 'HON', 'EMR', 'ETN',
    # Healthcare / Biopharma
    'LLY', 'NVO', 'BMY', 'ALGN', 'CNC', 'UNH', 'JNJ', 'ABBV', 'MRK',
    'PFE', 'REGN', 'VRTX', 'SDGR', 'MRNA',
    # Financials
    'JPM', 'BAC', 'WFC', 'GS', 'MS', 'BLK', 'V', 'MA', 'AXP',
    # Consumer / Retail
    'WMT', 'COST', 'AMZN', 'HD', 'LOW', 'NKE', 'SBUX', 'MCD', 'TGT',
    # Singapore (SGX)
    'D05.SI', 'O39.SI', 'U11.SI', 'Z74.SI', 'C52.SI', 'BN4.SI',
    'S68.SI', 'C09.SI', 'F34.SI', 'S63.SI',
    # Hong Kong (HKEX)
    '0700.HK', '9988.HK', '3690.HK', '9618.HK', '1299.HK', '0005.HK',
    '0388.HK', '2318.HK', '0941.HK', '0016.HK',
    # European / Global
    'SAP', 'ASML', 'NVO', 'AZN', 'HSBC', 'BHP', 'RIO', 'BP', 'SHEL',
]

# ===========================================================================
# SCREENING LOGIC
# ===========================================================================

def screen_stock(ticker):
    """Run alpha analysis and return screening results."""
    try:
        r = alpha_analysis(ticker)
        if 'error' in r:
            return {'ticker': ticker, 'error': r['error']}

        moat = r['qualitative']['moat']
        risk = r['risk_management']['risk_factors']
        quant = r['quantitative']
        fwd = quant['forward_rule_of_40']
        nrr = quant['net_revenue_retention']
        nob = r['nob']
        perf = r['qualitative']['moat_performance']
        thesis = r['thesis']

        return {
            'ticker': ticker,
            'name': r['data']['name'],
            'nob': nob['name'],
            'moat_rating': moat['moat_rating'],
            'moat_label': moat['moat_label'],
            'circumvention_delta': moat.get('circumvention_delta', 0),
            'moat_performance': perf['performance'],
            'risk_score': risk['risk_score'],
            'risk_level': risk['risk_level'],
            'nrr_pct': nrr.get('estimated_nrr_pct'),
            'nrr_installed_growth': nrr.get('estimated_nrr_pct', 0) is not None and nrr['estimated_nrr_pct'] >= 120,
            'fwd_r40': fwd.get('forward_rule_40'),
            'trailing_r40': fwd.get('trailing_rule_40'),
            'fwd_inflection': fwd.get('inflection_signal', ''),
            'conviction': thesis['conviction'],
            'thesis_short': thesis['thesis'][:120],
            'price': r['data']['price'],
            'market_cap': r['data']['info'].get('marketCap'),
            'sector': r['data']['sector'],
            'industry': r['data']['industry'],
            'error': None,
        }
    except Exception as e:
        return {'ticker': ticker, 'error': str(e)}


# ===========================================================================
# MAIN
# ===========================================================================

def main():
    print("=" * 90)
    print("  HIGH CONVICTION STOCK SCREENER — 2026 Strategic Growth Framework")
    print(f"  Scanning {len(WATCHLIST)} stocks across US, SGX, HKEX, EU markets")
    print("=" * 90)
    print()

    results = []
    errors = []
    start = time.time()

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(screen_stock, t): t for t in WATCHLIST}
        for i, future in enumerate(as_completed(futures)):
            ticker = futures[future]
            result = future.result()
            if result.get('error'):
                errors.append(result)
            else:
                results.append(result)
            elapsed = time.time() - start
            print(f"\r  [{i+1}/{len(WATCHLIST)}] Scanned {ticker:<10} | {i+1-len(errors)} passed | {len(errors)} errors | {elapsed:.0f}s", end='', flush=True)

    print("\n")

    if not results:
        print("No results. Check network connection.")
        return

    df = pd.DataFrame(results)

    # ---- PLATINUM (Highest Quality) ----
    # Rare: wide moat + clean risk + growth signal + compounding moat
    platinum = df[
        (df['moat_rating'] >= 6) &
        (df['risk_score'] <= 1) &
        (df['moat_performance'] == 'COMPOUNDING') &
        ((df['nrr_installed_growth'] == True) | (df['fwd_inflection'].isin(['MASSIVE INFLECTION', 'POSITIVE INFLECTION', 'BENCHMARK CROSSOVER'])))
    ].sort_values('moat_rating', ascending=False)

    # ---- GOLD (High Conviction) ----
    # Strong: moderate moat + clean risk + growth catalyst
    high_conviction = df[
        (df['moat_rating'] >= 5) &
        (df['risk_score'] <= 2) &
        ((df['nrr_installed_growth'] == True) | (df['fwd_inflection'].isin(['MASSIVE INFLECTION', 'POSITIVE INFLECTION', 'BENCHMARK CROSSOVER'])))
    ].sort_values('moat_rating', ascending=False)

    # ---- SILVER (Moderate Conviction) ----
    # Decent: some moat + manageable risk
    moderate_conviction = df[
        (df['moat_rating'] >= 4) &
        (df['risk_score'] <= 4) &
        (df['circumvention_delta'] >= 4)
    ].sort_values('moat_rating', ascending=False)

    # ---- DISPLAY ----
    display_cols = ['ticker', 'name', 'nob', 'moat_rating', 'circumvention_delta',
                    'moat_performance', 'risk_score', 'nrr_pct', 'fwd_inflection',
                    'price', 'sector']

    def format_display(subset, label, criteria):
        print("=" * 100)
        print(f"  {label} — {len(subset)} stocks found")
        print(f"  Criteria: {criteria}")
        print("=" * 100)
        print()
        if len(subset) > 0:
            disp = subset[display_cols].copy()
            disp['price'] = disp['price'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else 'N/A')
            disp['nrr_pct'] = disp['nrr_pct'].apply(lambda x: f"{x:.0f}%" if pd.notna(x) else 'N/A')
            disp['moat_rating'] = disp['moat_rating'].apply(lambda x: f"{x:.1f}/10")
            disp.columns = ['Ticker', 'Name', 'NoB', 'Moat', 'Circ.Delta', 'Trend', 'Risk', 'NRR', 'Fwd R40', 'Price', 'Sector']
            print(disp.to_string(index=False))
        else:
            print("  No stocks in this tier.")
        print()

    format_display(platinum, 'PLATINUM — Highest Quality',
                   'Moat >= 6 | Risk <= 1 | Moat COMPOUNDING | NRR >= 120% or Fwd R40 Inflection')
    format_display(high_conviction, 'GOLD — High Conviction',
                   'Moat >= 5 | Risk <= 2 | NRR >= 120% or Fwd R40 Inflection')
    format_display(moderate_conviction, 'SILVER — Moderate Conviction',
                   'Moat >= 4 | Risk <= 4 | Circumvention Delta >= 4')

    # ---- SUMMARY STATS ----
    print()
    print("=" * 100)
    print(f"  SCREENING SUMMARY — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 100)
    print(f"  Total scanned:     {len(WATCHLIST)}")
    print(f"  Successful:        {len(results)}")
    print(f"  Errors:            {len(errors)}")
    print(f"  PLATINUM:          {len(platinum)}  (Moat>=6, Risk<=1, Compounding, Growth signal)")
    print(f"  GOLD:              {len(high_conviction)}  (Moat>=5, Risk<=2, Growth signal)")
    print(f"  SILVER:            {len(moderate_conviction)}  (Moat>=4, Risk<=4, Circ.Delta>=4)")
    print(f"  Time elapsed:      {time.time() - start:.0f}s")
    print()

    # Conviction distribution
    print("  Conviction Distribution:")
    for level in ['HIGH CONVICTION', 'MODERATE CONVICTION', 'SELECTIVE', 'OPPORTUNISTIC', 'PASS']:
        count = len(df[df['conviction'] == level])
        bar = '#' * (count // 2) if count > 0 else ''
        print(f"    {level:<22} {count:>3}  {bar}")

    # Moat distribution
    print()
    print("  Moat Rating Distribution:")
    for lo, hi, label in [(0, 3, 'No Moat (0-3)'), (3, 5, 'Narrow (3-5)'), (5, 7, 'Moderate (5-7)'), (7, 11, 'Wide (7-10)')]:
        count = len(df[(df['moat_rating'] >= lo) & (df['moat_rating'] < hi)])
        bar = '#' * (count // 2) if count > 0 else ''
        print(f"    {label:<22} {count:>3}  {bar}")

    if errors:
        print(f"\n  Errors ({len(errors)}):")
        for e in errors[:10]:
            print(f"    {e['ticker']}: {e['error']}")
        if len(errors) > 10:
            print(f"    ... and {len(errors)-10} more")


if __name__ == '__main__':
    main()

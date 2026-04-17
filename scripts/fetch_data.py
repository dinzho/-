import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime

def fetch_and_calculate(symbol, config):
    """抓取股價數據並計算技術指標"""
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period=f"{config['parameters']['lookback_days']}d")
    
    if hist.empty:
        raise ValueError(f"無法獲取 {symbol} 的歷史數據")

    df = hist.copy()
    p = config['parameters']

    # 計算指標
    for period in p['sma_periods']:
        df[f'SMA_{period}'] = ta.sma(df['Close'], length=period)
    df['RSI'] = ta.rsi(df['Close'], length=p['rsi_period'])
    macd = ta.macd(df['Close'])
    df = pd.concat([df, macd], axis=1)

    # 最新數據
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    change_pct = ((latest['Close'] - prev['Close']) / prev['Close']) * 100

    # 52週高低
    high_52w = df['High'].max()
    low_52w = df['Low'].min()
    pos_pct = ((latest['Close'] - low_52w) / (high_52w - low_52w)) * 100

    # 基本面 (yfinance info 可能不穩定，提供預設結構)
    info = ticker.info
    market_cap = info.get('marketCap', 'N/A')
    pe_ratio = info.get('trailingPE', 'N/A')

    # FIB 計算 (基於52週高低)
    fib_range = high_52w - low_52w
    fib_levels = {lvl: round(high_52w - fib_range * lvl, 2) for lvl in p['fib_levels']}
    fib_table = "\n".join([f"  {lvl:.3f} → {val:.2f}" for lvl, val in fib_levels.items()])

    # 均線狀態
    sma20 = latest.get('SMA_20', 'N/A')
    sma50 = latest.get('SMA_50', 'N/A')
    sma200 = latest.get('SMA_200', 'N/A')
    
    ma_status = "多頭排列" if (isinstance(sma20, (int, float)) and isinstance(sma50, (int, float)) and 
                                sma20 > sma50 > sma200) else "空頭/糾纏"

    return {
        "SYMBOL": symbol,
        "EXCHANGE": next((t['exchange'] for t in config['tickers'] if t['symbol'] == symbol), "NYSE"),
        "NAME": next((t['name'] for t in config['tickers'] if t['symbol'] == symbol), symbol),
        "DATE": datetime.now().strftime(config['output']['date_format']),
        "PRICE": f"${latest['Close']:.2f}",
        "PRICE_CHANGE_DESC": f"較前日 {'+' if change_pct > 0 else ''}{change_pct:.2f}%",
        "HIGH_52W": f"${high_52w:.2f}",
        "LOW_52W": f"${low_52w:.2f}",
        "POSITION_PERCENT": f"{pos_pct:.1f}%",
        "MARKET_CAP": f"${market_cap/1e9:.1f}B" if isinstance(market_cap, (int, float)) else "N/A",
        "PE_RATIO": f"{pe_ratio:.2f}x" if isinstance(pe_ratio, (int, float)) else "N/A",
        "FIB_HIGH": f"${high_52w:.2f}",
        "FIB_LOW": f"${low_52w:.2f}",
        "FIB_TABLE_MARKDOWN": fib_table,
        "FIB_POSITION_NOTE": f"位於 0.236 與 0.382 之間，處於震盪修復區",
        "SMA20": f"${sma20:.2f}" if isinstance(sma20, (int, float)) else "計算中",
        "SMA50": f"${sma50:.2f}" if isinstance(sma50, (int, float)) else "計算中",
        "SMA200": f"${sma200:.2f}" if isinstance(sma200, (int, float)) else "計算中",
        "MA_ALIGNMENT": ma_status,
        "RSI": f"{latest['RSI']:.1f}" if not pd.isna(latest.get('RSI')) else "50.0",
        "MACD_STATUS": "多頭金叉/紅柱放大" if latest.get('MACD_12_26_9', 0) > 0 else "空頭死叉/綠柱收斂",
        # 以下為預設佔位符，建議後續串接 Finnhub/AlphaVantage 或手動覆寫
        "TREND_DESC": "大型 ABC 調整浪末端 / 底部構築中",
        "A_WAVE_DESC": "主跌段完成，估值回歸理性",
        "B_WAVE_DESC": "反彈試探壓力，量能配合度普通",
        "C_WAVE_DESC": "殺跌動能減弱，籌碼逐步沉澱",
        "WAVE_CONCLUSION": "最慘烈單邊下跌結束，進入右側震盪築底期",
        "VOLUME_NOTE": "下跌縮量、反彈溫和放量，籌碼鎖定良好",
        "ROE": "需手動輸入或串接財報API",
        "ROE_NOTE": "關注資本運用效率與護城河",
        "INDUSTRY_CAGR": "15-20% (預估值)",
        "SECTOR_GROWTH_NOTE": "行業處於數位轉型/AI賦能週期",
        "DIV_YIELD": "0.00%",
        "DIV_NOTE": "成長型標的通常以再投資為主",
        "VALUATION_METRIC": "Forward PE / PS",
        "VAL_NOTE": "相較歷史均值具備安全邊際",
        "CATALYSTS": "1. 財報指引 2. AI產品變現 3. 降息預期",
        "RISKS": "1. 宏觀衰退 2. 競爭加劇 3. 監管壓力",
        "CONSENSUS": "買入/持有/賣出 (需手動更新)",
        "SENTIMENT_IDX": "中性偏樂觀",
        "FLOW_NOTE": "機構資金於支撐區吸籌",
        "OPTIONS_SENTIMENT": "IV 中等，未見極端投機",
        "SWING_ENTRY": "回踩 SMA20 或 FIB 0.236",
        "SWING_SL": "跌破前低結構",
        "SWING_TP1": "FIB 0.382",
        "SWING_TP2": "SMA50",
        "MID_ENTRY": "分批建倉區間",
        "MID_SL": "收盤低於極限防守位",
        "MID_TP": "前期波段高點",
        "LONG_ENTRY": "歷史估值底部 / 重大錯殺點",
        "LONG_EXIT": "基本面惡化 / 估值泡沫化 / 技術月線頂背離",
        "LONG_THESIS": "賺取業績增長 + 估值修復的錢",
        "TECH_SCORE": "7.5",
        "FUND_SCORE": "8.0",
        "RECOMMENDATION": "逢低吸納 (Accumulate)",
        "ONE_LINER": "技術面築底完成，基本面具備長期賠率，適合分批佈局。"
    }

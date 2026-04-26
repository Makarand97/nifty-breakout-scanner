import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import pytz
import warnings

warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Swing Breakout Scanner",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #0a0e1a; color: #e0e6f0; }
.header-block {
    background: linear-gradient(135deg, #0d1b3e 0%, #112244 50%, #0a1628 100%);
    border: 1px solid #1e3a5f; border-radius: 12px; padding: 24px 32px; margin-bottom: 20px;
}
.header-title { font-family: 'Space Mono', monospace; font-size: 24px; font-weight: 700;
    color: #4fc3f7; letter-spacing: -0.5px; margin: 0; }
.header-sub { color: #7a9abf; font-size: 13px; margin-top: 4px; }
.metric-card { background: #0d1b3e; border: 1px solid #1e3a5f; border-radius: 10px;
    padding: 16px 20px; text-align: center; }
.metric-val { font-size: 26px; font-weight: 700; color: #4fc3f7; font-family: 'Space Mono', monospace; }
.metric-lbl { font-size: 11px; color: #7a9abf; margin-top: 2px; }
div[data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }
.stButton > button { background: #1565c0 !important; color: white !important;
    border: none !important; border-radius: 8px !important; font-weight: 600 !important; padding: 10px 20px !important; }
.stButton > button:hover { background: #1976d2 !important; }
div[data-testid="stSidebar"] { background: #06111f !important; border-right: 1px solid #1e3a5f; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# NSE STOCK UNIVERSE
# ─────────────────────────────────────────────────────────────────────────────
ALL_STOCKS = [
    "RELIANCE","TCS","HDFCBANK","INFY","ICICIBANK","KOTAKBANK","HINDUNILVR",
    "ITC","SBIN","BAJFINANCE","BHARTIARTL","ASIANPAINT","MARUTI","AXISBANK",
    "LT","SUNPHARMA","TITAN","ULTRACEMCO","NESTLEIND","WIPRO","HCLTECH",
    "ADANIENT","ADANIPORTS","ONGC","NTPC","POWERGRID","COALINDIA","BPCL",
    "JSWSTEEL","TATASTEEL","TATAMOTORS","TECHM","BAJAJFINSV","BAJAJ-AUTO",
    "HDFCLIFE","SBILIFE","BRITANNIA","DRREDDY","CIPLA","DIVISLAB","EICHERMOT",
    "GRASIM","HEROMOTOCO","HINDALCO","INDUSINDBK","M&M","APOLLOHOSP",
    "TATACONSUM","IOC","UPL","ADANIGREEN","SIEMENS","ABB","HAVELLS","PIDILITIND",
    "BERGEPAINT","MARICO","COLPAL","DABUR","GODREJCP","MCDOWELL-N","BANDHANBNK",
    "FEDERALBNK","IDFCFIRSTB","PNB","BANKBARODA","CANBK","UNIONBANK","MUTHOOTFIN",
    "CHOLAFIN","LICHSGFIN","RECLTD","PFC","IRCTC","DLF","LODHA","AMBUJACEM",
    "TRENT","ZOMATO","NYKAA","PERSISTENT","LTIM","COFORGE","MPHASIS","OFSS",
    "LTTS","TATAPOWER","TORNTPHARM","LUPIN","AUROPHARMA","ZYDUSLIFE","PAGEIND",
    "POLYCAB","GAIL","INDHOTEL","TATACOMM","MAXHEALTH","NAUKRI","GODREJPROP",
    "PRESTIGE","ABCAPITAL","ABFRL","ALKEM","AMBER","ASTRAL","ATUL","BALKRISIND",
    "BLUESTARCO","CESC","CENTURYPLY","CROMPTON","CUMMINSIND","CYIENT","DALBHARAT",
    "DEEPAKNTR","DIXON","EMAMILTD","ESCORTS","EXIDEIND","FINEORG","GNFC",
    "GODREJIND","GRANULES","GRINDWELL","HAPPSTMNDS","IPCALAB","JBCHEPHARM",
    "JKCEMENT","JUBLPHARMA","KALPATPOWR","KEI","MANAPPURAM","METROPOLIS",
    "MOTILALOSW","MRF","NATCOPHARM","NAVINFLUOR","NLCINDIA","OLECTRA","PFIZER",
    "PIIND","RADICO","RAMCOCEM","RITES","RVNL","SRF","STARHEALTH","SUNDARMFIN",
    "SUPREMEIND","SYNGENE","TATACHEM","TATAELXSI","THERMAX","TIMKEN","TORNTPOWER",
    "TVSMOTOR","VGUARD","VOLTAS","ZEEL","SAIL","NMDC","MOIL","NATIONALUM",
    "HINDCOPPER","VEDL","HINDZINC","GMRAIRPORT","ADANIPOWER","ADANITRANS",
    "NHPC","SJVN","IREDA","HUDCO","IRFC","RAILTEL","BEML","BEL","HAL","BHEL",
    "MIDHANI","GRSE","COCHINSHIP","MAZAGONDOCK","KARURVYSYA","SOUTHBANK",
    "DCBBANK","CITYUNIONBANK","EQUITASBNK","UJJIVANSFB","AUBANK","RBLBANK",
    "MFSL","NIACL","GICRE","ICICIGI","HDFCAMC","ABSLAMC","360ONE","ANGELONE",
    "IIFL","RATEGAIN","CARTRADE","EASEMYTRIP","IXIGO","NAZARA","INFOEDGE",
    "JUSTDIAL","MATRIMONY","INDIAMART","AFFLE","TANLA","ROUTE","KFINTECH",
    "CAMS","CDSL","BSE","MCX","DEEPAKFERT","GSPL","MGL","IGL","ATGL",
    "GUJGASLTD","PETRONET","AEGISCHEM","NOCIL","AAVAS","HOMEFIRST","APTUS",
    "CREDITACC","SPANDANA","UJJIVAN","SHRIRAMFIN","BAJAJHFL","CANFINHOME",
    "REPCO","APAR","CUPID","SHREEPUSHKAR","HFCL","STLTECH","TEJASNET",
    "DATAMATICS","MASTEK","KPITTECH","BIRLASOFT","ZENSAR","RELAXO","BATA",
    "CAMPUS","DMART","SHOPERSTOP","JYOTHYLAB","HATSUN","PGHH","GILLETTE",
    "COLGATE","AJANTPHARM","GLENMARK","WOCKPHARMA","ABBOTINDIA","SANOFI",
    "BIOCON","LAURUSLABS","STRIDES","SEQUENT","SUDARSCHEM","AARTI","VINATI",
    "LAXMICHEM","HEIDELBERG","ORIENTCEM","JKPAPER","TNPL","TIINDIA","CRAFTSMAN",
    "SANSERA","ENDURANCE","MOTHERSON","BOSCHLTD","SCHAEFFLER","SKFINDIA",
    "SUPRAJIT","SUNDRMFAST","FIEMIND","MINDA","SUBROS","GABRIEL","ROLEXRINGS",
    "RATNAMANI","WELCORP","JINDALSAW","JSWISPL","APLAPOLLO","HIKAL","SUVEN",
    "GALAXYSURF","VINATIORGA","BAJAJCON","EMAMIPAP","KSCL","MAHINDCIE",
    "LUMAXIND","IIFLWAM","MANINFRA","GAYAPROJ","NBCC","NCC","PNCINFRA",
    "KNRCON","HGINFRA","GPPL","JPPOWER","RPOWER","KPRMILL","RUPA","DOLLAR",
    "LOVABLE","NIITLTD","APTECH","CRISIL","ICRA","CARERATING","ACCELYA",
    "FSL","SPENCERS","VMART","NUVAMA","EDELWEISS","POONAWALLA","MUTHOOTCAP",
    "CHOLAHLDNG","BAJAJHLDNG","GODREJAGRO","JUBLINGSCI","SUVENPHAR",
    "LALPATHLAB","THYROCARE","KRSNAA","VIJAYA","ASTERDM","FORTIS",
    "NARAYANAHEALTH","RAINBOW","DRPATH","VIMTALABS","YESBANK","JMFINANCIL",
    "POLICYBZR","PAYTM","DELHIVERY","MAPMYINDIA","INTELLECT","NUCLEUS",
    "SONATA","MSTC","CONCOR","BLUEDART","TCI","ALLCARGO","MAHLOG",
    "ORIENTHOTEL","LEMONTREE","TAJGVK","CHALET","SAMHI","EIHOTEL","WONDERLA",
    "MAHINDRAHOLIDAY","TATATECH","MEDPLUS","ERIS","CAPLIPOST","JBPHARMA",
    "FDC","INDOCO","MANKIND","ALEMBICPHARM","ORCHPHARMA","DHANUKA","BAYER",
    "EXCEL","GHCL","DCMSHRIRAM","CHAMBAL","COROMANDEL","GSFC","RALLIS",
    "SUMITCHEM","AARTIDRUGS","CENTURYPLY","GREENPANEL","TRIDENT","VARDHMAN",
    "NITIN","BANSWRAS","DONEAR","RAYMOND","ARVIND","WELSPUN","MAFATLAL",
    "MANDHANA","KITEX","GARWARE","WPIL","HLE","ELGIEQUIP","ISGEC","TEXMACO",
    "TITAGARH","GREAVESCOT","GREAVES","KIRLOSKAR","KOEL","LAKSHMIELET",
    "ELECON","SUZLON","INOXWIND","POWERMECH","KEC","GEPIL","PRAJ",
    "CASTROLIND","GULFOILLUB","UFLEX","POLYPLEX","NILKAMAL","GREENLAM",
    "CERA","KAJARIA","SOMANYCER","AKZOINDIA","KANSAINER","PCJEWELLER",
    "RAJESHEXPO","THANGAMAYL","GOLDIAM","SENCO","KALYAN","ETHOS","VAIBHAVGBL",
    "KALYANKJIL","SWARAJENG","MAHSEAMLES","BIRLACORPN","NUVOCO","SANGHI",
    "KAKATCEM","STARCEMENT","JKCEMENT","RAMCOCEM","DALBHARAT","ULTRACEMCO",
    "AMBUJACEM","ACC","SHREECEM","TORNTPOWER","GESHIP","ESABINDIA","JTEKTINDIA",
    "FAGBEARINGS","NRBBEARING","TINPLATE","TATAMETALIK","JSPL","INDIANB","TMB",
    "SURYODAY","OBEROIRLTY","BRIGADE","SOBHA","PURVANKARA","KOLTEPATIL",
    "MAHLIFE","SUNTECK","PHOENIXLTD","MACROTECH","ASHOKLEY","HINDMOTORS",
    "PRICOL","VSTTILLERS","FORCEMOT","SMLISUZU","TVSSRICHAK","BALRAMCHIN",
    "DHAMPURSUG","TRIVENI","EID","NITCO","MURUDCERA","ORIENTBELL","INDIGO",
    "SPICEJET","THOMASCOOK","GICRE","NIACL","LICIHFL","LINDEINDIA","IGARASHI",
    "FIVESTAR","FEDBANK","ESAFSFB","UTKARSH","JKIL","GPIL","KIOCL","SBFC",
    "UGROCAP","YATHARTH","NETWEB","UPDATER","BRAINBEES","DOMS","GTPL",
    "HBLPOWER","SSWL","SANDHAR","CEAT","APOLLOTYRE","JKTYRE","KRBL","GREENPLY",
    "PARAS","VSTIND","GODFRYPHLP","UNITDSPR","JUBLFOOD","WESTLIFE","DEVYANI",
    "SAPPHIRE","KAYNES","SYRMA","AVALON","ELIN","VOLTAMP","SKIPPER",
    "STERLITEPOWER","VINDHYATEL","HINDPETRO","MRPL","CHENNPETRO","DEEPAKFERT",
]

seen = set()
STOCKS = []
for s in ALL_STOCKS:
    if s not in seen:
        seen.add(s)
        STOCKS.append(s)

# ─────────────────────────────────────────────────────────────────────────────
# INDICATOR HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def ema_series(series, span):
    return series.ewm(span=span, adjust=False).mean()

# ─────────────────────────────────────────────────────────────────────────────
# SCREEN ONE STOCK
# ─────────────────────────────────────────────────────────────────────────────

def screen_stock(sym, w_df, d_df):
    try:
        if w_df is None or d_df is None:
            return None
        if len(w_df) < 52 or len(d_df) < 60:
            return None

        wc = w_df["Close"].dropna()
        wh = w_df["High"].dropna().reindex(wc.index).ffill().bfill()
        wl = w_df["Low"].dropna().reindex(wc.index).ffill().bfill()
        wv = w_df["Volume"].dropna().reindex(wc.index).fillna(0)
        dc = d_df["Close"].dropna()

        if len(wc) < 52 or len(dc) < 50:
            return None

        cur = float(dc.iloc[-1])

        def pct(n):
            try:
                return round((float(dc.iloc[-1]) / float(dc.iloc[-n]) - 1) * 100, 2) \
                    if len(dc) > n else None
            except Exception:
                return None

        ch1d = pct(2)
        ch1w = pct(6)
        ch1m = pct(22)
        ch3m = pct(66)
        ch6m = pct(132)
        ch1y = pct(252)

        # C1: Uptrend — higher highs AND higher lows over last 12 weeks
        if len(wh) >= 12 and len(wl) >= 12:
            fh = float(wh.iloc[-12:-6].max())
            sh = float(wh.iloc[-6:].max())
            fl = float(wl.iloc[-12:-6].min())
            sl = float(wl.iloc[-6:].min())
            c1 = bool(sh > fh and sl > fl)
        else:
            c1 = False

        # C2: Not overextended — 3M gain < 100%
        c2 = bool(ch3m is not None and ch3m < 100.0)

        # C3: Range contraction — last 4 weekly candle ranges narrowing
        if len(wh) >= 6 and len(wl) >= 6:
            ranges = [float(wh.iloc[-i]) - float(wl.iloc[-i]) for i in range(1, 6)]
            narrowing = sum(1 for i in range(len(ranges)-1) if ranges[i] < ranges[i+1])
            c3 = bool(narrowing >= 3)
        else:
            c3 = False

        # C4: Volume dry-up — recent 4W volume below 10W avg and declining
        if len(wv) >= 10:
            vol10_avg   = float(wv.iloc[-10:].mean())
            vol4_recent = float(wv.iloc[-4:].mean())
            vol4_prior  = float(wv.iloc[-8:-4].mean())
            c4 = bool(vol4_recent < vol10_avg and vol4_recent < vol4_prior)
        else:
            c4 = False

        # C5: Price above 20-week EMA
        ema20w = ema_series(wc, 20)
        c5 = bool(cur > float(ema20w.iloc[-1]))

        # C6: Near breakout — within 5% of 12W high
        high12w = float(wh.iloc[-12:].max())
        c6 = bool(high12w > 0 and cur >= high12w * 0.95)

        # C7: Volume surge — latest week >= 1.5x the prior 10-week average
        if len(wv) >= 11:
            base_vol   = float(wv.iloc[-11:-1].mean())
            latest_vol = float(wv.iloc[-1])
            c7 = bool(base_vol > 0 and latest_vol >= base_vol * 1.5)
        else:
            c7 = False

        # C8: Second leg — prior expansion visible in weeks 26-12
        if len(wv) >= 26 and len(wc) >= 26:
            prior_v    = wv.iloc[-26:-12]
            avg_v      = float(wv.iloc[-26:].mean())
            had_surge  = bool((prior_v >= avg_v * 2.0).any())
            prior_lo   = float(wc.iloc[-26:-12].min())
            prior_hi   = float(wc.iloc[-26:-12].max())
            had_move   = bool(prior_lo > 0 and (prior_hi / prior_lo - 1) >= 0.15)
            c8 = bool(had_surge and had_move)
        else:
            c8 = False

        score = sum([c1, c2, c3, c4, c5, c6, c7, c8])

        entry     = round(high12w, 1)
        stop_loss = round(entry * 0.975, 1)
        target1   = round(entry * 1.20, 1)
        target2   = round(entry * 1.50, 1)

        return {
            "Symbol":           sym,
            "Price (INR)":      round(cur, 1),
            "Entry Level":      entry,
            "Stop Loss":        stop_loss,
            "Target 1 (+20%)":  target1,
            "Target 2 (+50%)":  target2,
            "1D %": ch1d, "1W %": ch1w, "1M %": ch1m,
            "3M %": ch3m, "6M %": ch6m, "1Y %": ch1y,
            "C1 Uptrend":            c1,
            "C2 Not Overextended":   c2,
            "C3 Range Contraction":  c3,
            "C4 Volume Dry-Up":      c4,
            "C5 Above 20W EMA":      c5,
            "C6 Near Breakout":      c6,
            "C7 Volume Surge":       c7,
            "C8 Second Leg":         c8,
            "Score": score,
        }
    except Exception:
        return None

# ─────────────────────────────────────────────────────────────────────────────
# STAGE CLASSIFIER
# ─────────────────────────────────────────────────────────────────────────────

def classify_stage(row):
    c1 = row["C1 Uptrend"]
    c2 = row["C2 Not Overextended"]
    c3 = row["C3 Range Contraction"]
    c4 = row["C4 Volume Dry-Up"]
    c5 = row["C5 Above 20W EMA"]
    c6 = row["C6 Near Breakout"]
    c7 = row["C7 Volume Surge"]
    if c1 and c2 and c6 and c7 and (c3 or c4):
        return "🚀 Breaking Out"
    elif c1 and c2 and c3 and c4 and c5 and c6:
        return "🟢 Ready"
    elif c1 and c2 and c3 and c5:
        return "🟠 Approaching"
    elif c1 and c3:
        return "🟡 Coiling"
    else:
        return "⚪ Watching"

STAGE_ORDER = {
    "🚀 Breaking Out": 0,
    "🟢 Ready":        1,
    "🟠 Approaching":  2,
    "🟡 Coiling":      3,
    "⚪ Watching":     4,
}

# ─────────────────────────────────────────────────────────────────────────────
# DATA FETCH
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=3600 * 8, show_spinner=False)
def fetch_batch(symbols_tuple, interval, period):
    symbols = list(symbols_tuple)
    tickers = [f"{s}.NS" for s in symbols]
    try:
        raw = yf.download(
            tickers, period=period, interval=interval,
            group_by="ticker", auto_adjust=True, progress=False,
        )
    except Exception:
        return {}
    result = {}
    is_multi = isinstance(raw.columns, pd.MultiIndex)
    for sym, tkr in zip(symbols, tickers):
        try:
            if len(tickers) == 1 and not is_multi:
                df = raw.dropna(how="all")
            elif is_multi:
                if tkr in raw.columns.get_level_values(0):
                    df = raw[tkr].dropna(how="all")
                elif tkr in raw.columns.get_level_values(1):
                    df = raw.xs(tkr, axis=1, level=1).dropna(how="all")
                else:
                    result[sym] = None
                    continue
            else:
                df = raw[tkr].dropna(how="all") if tkr in raw.columns else None
                if df is None:
                    result[sym] = None
                    continue
            result[sym] = df if (df is not None and not df.empty) else None
        except Exception:
            result[sym] = None
    return result

def fetch_all(symbols, progress_bar):
    chunk_size = 100
    chunks = [symbols[i:i+chunk_size] for i in range(0, len(symbols), chunk_size)]
    weekly_data, daily_data = {}, {}
    for idx, chunk in enumerate(chunks):
        pct = (idx + 0.5) / len(chunks)
        progress_bar.progress(pct, text=f"📥 Batch {idx+1}/{len(chunks)} — {len(chunk)} stocks…")
        weekly_data.update(fetch_batch(tuple(chunk), "1wk", "2y"))
        daily_data.update(fetch_batch(tuple(chunk), "1d",  "18mo"))
    return weekly_data, daily_data


# ─────────────────────────────────────────────────────────────────────────────
# MAIN UI
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="header-block">
  <div class="header-title">📈 NSE SWING BREAKOUT SCANNER — Range Contraction &amp; Expansion Strategy</div>
  <div class="header-sub">
    Identifies stocks in range contraction approaching an expansion breakout &nbsp;|&nbsp;
    ~640 NSE stocks &nbsp;|&nbsp; Weekly data via Yahoo Finance &nbsp;|&nbsp; Prices in INR
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:#0d1b3e;border:1px solid #1e3a5f;border-radius:12px;padding:18px 24px;margin-bottom:18px;">
  <div style="color:#4fc3f7;font-family:'Space Mono',monospace;font-size:13px;font-weight:700;margin-bottom:12px;">
    📌 CRITERIA — Range Contraction &amp; Expansion (Swing Strategy)
  </div>
  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;">
    <div style="background:#06111f;border:1px solid #1e3a5f;border-radius:8px;padding:10px 12px;">
      <div style="color:#4fc3f7;font-weight:700;font-size:12px;margin-bottom:4px;">C1 — Uptrend</div>
      <div style="color:#a0b8d0;font-size:11px;line-height:1.5;">Higher highs AND higher lows over last 12 weeks. Only trade in the direction of trend.</div>
    </div>
    <div style="background:#06111f;border:1px solid #1e3a5f;border-radius:8px;padding:10px 12px;">
      <div style="color:#4fc3f7;font-weight:700;font-size:12px;margin-bottom:4px;">C2 — Not Overextended</div>
      <div style="color:#a0b8d0;font-size:11px;line-height:1.5;">3-month gain below 100%. Stocks after 100%+ moves consolidate 8–12 weeks — avoid them.</div>
    </div>
    <div style="background:#06111f;border:1px solid #1e3a5f;border-radius:8px;padding:10px 12px;">
      <div style="color:#4fc3f7;font-weight:700;font-size:12px;margin-bottom:4px;">C3 — Range Contraction</div>
      <div style="color:#a0b8d0;font-size:11px;line-height:1.5;">Last 4 weekly candle ranges (H−L) are progressively narrowing. Price compressing — energy coiling.</div>
    </div>
    <div style="background:#06111f;border:1px solid #1e3a5f;border-radius:8px;padding:10px 12px;">
      <div style="color:#4fc3f7;font-weight:700;font-size:12px;margin-bottom:4px;">C4 — Volume Dry-Up</div>
      <div style="color:#a0b8d0;font-size:11px;line-height:1.5;">Volume last 4 weeks below 10-week avg and declining. No distribution — quiet accumulation.</div>
    </div>
    <div style="background:#06111f;border:1px solid #1e3a5f;border-radius:8px;padding:10px 12px;">
      <div style="color:#4fc3f7;font-weight:700;font-size:12px;margin-bottom:4px;">C5 — Above 20W EMA</div>
      <div style="color:#a0b8d0;font-size:11px;line-height:1.5;">Price above the 20-week EMA. Confirms the broader trend is supportive.</div>
    </div>
    <div style="background:#06111f;border:1px solid #1e3a5f;border-radius:8px;padding:10px 12px;">
      <div style="color:#4fc3f7;font-weight:700;font-size:12px;margin-bottom:4px;">C6 — Near Breakout</div>
      <div style="color:#a0b8d0;font-size:11px;line-height:1.5;">Within 5% of the 12-week high. Stock at the doorstep of expansion. Set GTT at Entry Level.</div>
    </div>
    <div style="background:#06111f;border:1px solid #1e3a5f;border-radius:8px;padding:10px 12px;">
      <div style="color:#4fc3f7;font-weight:700;font-size:12px;margin-bottom:4px;">C7 — Volume Surge ★</div>
      <div style="color:#a0b8d0;font-size:11px;line-height:1.5;">Latest week volume 1.5x+ the 10-week average. Institutional entry — the fuel for the expansion.</div>
    </div>
    <div style="background:#06111f;border:1px solid #1e3a5f;border-radius:8px;padding:10px 12px;">
      <div style="color:#69f0ae;font-weight:700;font-size:12px;margin-bottom:4px;">C8 — Second Leg ★</div>
      <div style="color:#a0b8d0;font-size:11px;line-height:1.5;">Prior expansion-contraction cycle visible (weeks 26–12). Second leg breakouts have higher success rates.</div>
    </div>
  </div>
  <div style="margin-top:14px;background:#06111f;border:1px solid #1e3a5f;border-radius:8px;padding:12px 16px;">
    <div style="color:#4fc3f7;font-weight:700;font-size:12px;margin-bottom:8px;">🏷️ STAGE CLASSIFICATION</div>
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;">
      <div style="padding:8px 10px;background:#0d1b3e;border-radius:6px;border-left:3px solid #ffd600;">
        <div style="color:#ffd600;font-weight:700;font-size:11px;">🟡 COILING</div>
        <div style="color:#a0b8d0;font-size:10px;margin-top:3px;">C1 + C3. Uptrend and contraction confirmed. Add to watchlist — check back weekly.</div>
      </div>
      <div style="padding:8px 10px;background:#0d1b3e;border-radius:6px;border-left:3px solid #ff9800;">
        <div style="color:#ff9800;font-weight:700;font-size:11px;">🟠 APPROACHING</div>
        <div style="color:#a0b8d0;font-size:10px;margin-top:3px;">C1+C2+C3+C5. Structure forming. Set GTT just above the 12-week high (Entry Level).</div>
      </div>
      <div style="padding:8px 10px;background:#0d1b3e;border-radius:6px;border-left:3px solid #00e676;">
        <div style="color:#00e676;font-weight:700;font-size:11px;">🟢 READY</div>
        <div style="color:#a0b8d0;font-size:10px;margin-top:3px;">C1+C2+C3+C4+C5+C6. All base signals confirmed. High priority — place GTT at Entry Level now.</div>
      </div>
      <div style="padding:8px 10px;background:#0d1b3e;border-radius:6px;border-left:3px solid #4fc3f7;">
        <div style="color:#4fc3f7;font-weight:700;font-size:11px;">🚀 BREAKING OUT</div>
        <div style="color:#a0b8d0;font-size:10px;margin-top:3px;">C1+C2+C6+C7+contraction. Volume surge at the level. Buy on close or next open. SL = 2.5% below.</div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ──
with st.sidebar:
    st.markdown("### ⚙️ Filters")
    min_score = st.slider("Minimum Score", 0, 8, 3)
    st.markdown("---")
    st.markdown("### 📐 Trade Rules (Ankur Strategy)")
    st.markdown("""
**Entry:** GTT at 12-week high = Entry Level column

**Stop Loss:** 2.5% below entry — hard order, not mental

**Target 1:** Sell 40–50% of position at +20%

**Target 2:** Trail remainder on daily 10/20 EMA

**Position size:**
- Beginner: 10% of capital per trade
- Experienced: up to 20%

**Max trades:** 3–4 simultaneously

**Exit rule:** Close below 20W EMA = full exit
""")
    st.markdown("---")
    st.caption(
        "**Stages:** 🚀 Act now → 🟢 Place GTT → 🟠 Set alert → 🟡 Watchlist\n\n"
        "C8 (Second Leg) ✅ = higher conviction setup\n\n"
        "⏱ First load: ~8–12 mins | Cache: 8 hours"
    )

# ── Clock + Refresh ──
ist_now = datetime.now(pytz.timezone("Asia/Kolkata"))
market_open = (9 <= ist_now.hour < 15) or (ist_now.hour == 15 and ist_now.minute <= 30)
market_status = "🟢 Market Open" if market_open else "🔴 Market Closed"

col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.markdown(
        f'<div style="color:#7a9abf;font-size:13px;padding-top:6px;">'
        f'{market_status} &nbsp;|&nbsp; IST: {ist_now.strftime("%d %b %Y, %I:%M %p")}'
        f'</div>', unsafe_allow_html=True)
with col2:
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.session_state["last_refresh"] = ist_now.strftime("%d %b %Y, %I:%M %p")
        st.rerun()
with col3:
    if "last_refresh" in st.session_state:
        st.markdown(
            f'<div style="color:#7a9abf;font-size:11px;padding-top:8px;">'
            f'Last: {st.session_state["last_refresh"]}</div>',
            unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Run scan ──
prog = st.progress(0, text="Starting data download…")
weekly_data, daily_data = fetch_all(STOCKS, prog)

rows = []
total = len(STOCKS)
for i, sym in enumerate(STOCKS):
    prog.progress(0.5 + (i + 1) / total * 0.5,
                  text=f"🔍 Screening {sym} ({i+1}/{total})…")
    rec = screen_stock(sym, weekly_data.get(sym), daily_data.get(sym))
    if rec:
        rows.append(rec)
prog.empty()

if not rows:
    st.error("No data returned. Check your internet connection and click Refresh.")
    st.stop()

df = pd.DataFrame(rows)
df["Stage"] = df.apply(classify_stage, axis=1)
df["Stage Order"] = df["Stage"].map(STAGE_ORDER).fillna(5)
df_filtered = (
    df[df["Score"] >= min_score]
    .sort_values(["Stage Order", "Score"], ascending=[True, False])
    .reset_index(drop=True)
)

# ── Metric cards ──
m1, m2, m3, m4, m5, m6 = st.columns(6)
for col, val, lbl in [
    (m1, len(STOCKS),                                   "Universe"),
    (m2, len(df),                                       "Data Available"),
    (m3, len(df[df["Stage"] == "🚀 Breaking Out"]),     "🚀 Breaking Out"),
    (m4, len(df[df["Stage"] == "🟢 Ready"]),            "🟢 Ready"),
    (m5, len(df[df["Stage"] == "🟠 Approaching"]),      "🟠 Approaching"),
    (m6, len(df[df["Stage"] == "🟡 Coiling"]),          "🟡 Coiling"),
]:
    with col:
        st.markdown(
            f'<div class="metric-card"><div class="metric-val">{val}</div>'
            f'<div class="metric-lbl">{lbl}</div></div>',
            unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Table ──
crit_cols = [
    "C1 Uptrend","C2 Not Overextended","C3 Range Contraction",
    "C4 Volume Dry-Up","C5 Above 20W EMA","C6 Near Breakout",
    "C7 Volume Surge","C8 Second Leg",
]

display_df = df_filtered[[
    "Symbol","Stage","Price (INR)",
    "Entry Level","Stop Loss","Target 1 (+20%)","Target 2 (+50%)",
    "1D %","1W %","1M %","3M %","6M %","1Y %",
] + crit_cols + ["Score"]].copy()

for c in crit_cols:
    display_df[c] = display_df[c].map(lambda x: "✅" if x else "❌")

display_df.rename(columns={
    "C1 Uptrend":           "C1",
    "C2 Not Overextended":  "C2",
    "C3 Range Contraction": "C3",
    "C4 Volume Dry-Up":     "C4",
    "C5 Above 20W EMA":     "C5",
    "C6 Near Breakout":     "C6",
    "C7 Volume Surge":      "C7",
    "C8 Second Leg":        "C8",
}, inplace=True)

st.markdown(
    f"### 📊 Swing Breakout Candidates — Score ≥ {min_score} "
    f"&nbsp;|&nbsp; {len(df_filtered)} stocks &nbsp;|&nbsp; Sorted by Stage → Score"
)

st.dataframe(
    display_df,
    use_container_width=True,
    height=min(700, max(300, len(display_df) * 38 + 50)),
    column_config={
        "Symbol":          st.column_config.TextColumn("Symbol",      width="small"),
        "Stage":           st.column_config.TextColumn("Stage",       width="medium"),
        "Price (INR)":     st.column_config.NumberColumn("Price ₹",  format="₹%.1f", width="small"),
        "Entry Level":     st.column_config.NumberColumn("Entry ₹",  format="₹%.1f", width="small"),
        "Stop Loss":       st.column_config.NumberColumn("Stop ₹",   format="₹%.1f", width="small"),
        "Target 1 (+20%)": st.column_config.NumberColumn("T1 +20%",  format="₹%.1f", width="small"),
        "Target 2 (+50%)": st.column_config.NumberColumn("T2 +50%",  format="₹%.1f", width="small"),
        "1D %":  st.column_config.NumberColumn("1D %",  format="%.1f%%", width="small"),
        "1W %":  st.column_config.NumberColumn("1W %",  format="%.1f%%", width="small"),
        "1M %":  st.column_config.NumberColumn("1M %",  format="%.1f%%", width="small"),
        "3M %":  st.column_config.NumberColumn("3M %",  format="%.1f%%", width="small"),
        "6M %":  st.column_config.NumberColumn("6M %",  format="%.1f%%", width="small"),
        "1Y %":  st.column_config.NumberColumn("1Y %",  format="%.1f%%", width="small"),
        "C1": st.column_config.TextColumn("C1", width="small"),
        "C2": st.column_config.TextColumn("C2", width="small"),
        "C3": st.column_config.TextColumn("C3", width="small"),
        "C4": st.column_config.TextColumn("C4", width="small"),
        "C5": st.column_config.TextColumn("C5", width="small"),
        "C6": st.column_config.TextColumn("C6", width="small"),
        "C7": st.column_config.TextColumn("C7", width="small"),
        "C8": st.column_config.TextColumn("C8", width="small"),
        "Score": st.column_config.ProgressColumn(
            "Score", min_value=0, max_value=8, format="%d/8", width="small"),
    },
    hide_index=True,
)

st.caption(
    "💡 Click any column header to sort. "
    "Entry Level = 12-week high — place GTT here. "
    "Stop Loss = 2.5% below entry. T1 = +20% (book 40–50%). T2 = +50% (trail). "
    "Verify on chart before acting. This is a scanner, not a buy recommendation."
)

st.markdown("---")
st.markdown(
    '<div style="color:#3a5a7a;font-size:11px;text-align:center;">'
    'Data sourced from Yahoo Finance via yfinance. Not financial advice. '
    'Past performance does not guarantee future results. '
    'Always conduct your own due diligence before investing.'
    '</div>', unsafe_allow_html=True)

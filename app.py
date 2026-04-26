import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import pytz
import warnings

warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Nifty 750 Breakout Scanner",
    page_icon="🚀",
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
    border: 1px solid #1e3a5f; border-radius: 12px;
    padding: 24px 32px; margin-bottom: 20px;
}
.header-title { font-family: 'Space Mono', monospace; font-size: 26px; font-weight: 700; color: #4fc3f7; letter-spacing: -0.5px; margin: 0; }
.header-sub { color: #7a9abf; font-size: 13px; margin-top: 4px; }
.metric-card { background: #0d1b3e; border: 1px solid #1e3a5f; border-radius: 10px; padding: 16px 20px; text-align: center; }
.metric-val { font-size: 28px; font-weight: 700; color: #4fc3f7; font-family: 'Space Mono', monospace; }
.metric-lbl { font-size: 12px; color: #7a9abf; margin-top: 2px; }
div[data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }
.stButton > button { background: #1565c0 !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; padding: 10px 20px !important; }
.stButton > button:hover { background: #1976d2 !important; }
div[data-testid="stSidebar"] { background: #06111f !important; border-right: 1px solid #1e3a5f; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# NIFTY TOP ~750 SYMBOLS (NSE)
# ─────────────────────────────────────────────────────────────────────────────
ALL_STOCKS = [
    # ── NIFTY 50 ──
    "RELIANCE","TCS","HDFCBANK","INFY","ICICIBANK","KOTAKBANK","HINDUNILVR",
    "ITC","SBIN","BAJFINANCE","BHARTIARTL","ASIANPAINT","MARUTI","AXISBANK",
    "LT","SUNPHARMA","TITAN","ULTRACEMCO","NESTLEIND","WIPRO","HCLTECH",
    "ADANIENT","ADANIPORTS","ONGC","NTPC","POWERGRID","COALINDIA","BPCL",
    "JSWSTEEL","TATASTEEL","TATAMOTORS","TECHM","BAJAJFINSV","BAJAJ-AUTO",
    "HDFCLIFE","SBILIFE","BRITANNIA","DRREDDY","CIPLA","DIVISLAB","EICHERMOT",
    "GRASIM","HEROMOTOCO","HINDALCO","INDUSINDBK","M&M","APOLLOHOSP",
    "TATACONSUM","IOC","UPL",
    # ── NIFTY NEXT 50 ──
    "ADANIGREEN","SIEMENS","ABB","HAVELLS","PIDILITIND","BERGEPAINT","MARICO",
    "COLPAL","DABUR","GODREJCP","MCDOWELL-N","BANDHANBNK","FEDERALBNK",
    "IDFCFIRSTB","PNB","BANKBARODA","CANBK","UNIONBANK","MUTHOOTFIN",
    "CHOLAFIN","LICHSGFIN","RECLTD","PFC","IRCTC","DLF","LODHA","AMBUJACEM",
    "TRENT","ZOMATO","NYKAA","PERSISTENT","LTIM","COFORGE","MPHASIS",
    "OFSS","LTTS","TATAPOWER","TORNTPHARM","LUPIN","AUROPHARMA","ZYDUSLIFE",
    "PAGEIND","POLYCAB","GAIL","INDHOTEL","TATACOMM","MAXHEALTH","NAUKRI",
    "GODREJPROP","PRESTIGE",
    # ── NIFTY MIDCAP 150 ──
    "ABCAPITAL","ABFRL","ALKEM","AMBER","ASTRAL","ATUL","BALKRISIND",
    "BLUESTARCO","CESC","CENTURYPLY","CROMPTON","CUMMINSIND","CYIENT",
    "DALBHARAT","DEEPAKNTR","DIXON","EMAMILTD","ESCORTS","EXIDEIND",
    "FINEORG","GNFC","GODREJIND","GRANULES","GRINDWELL","HAPPSTMNDS",
    "IPCALAB","JBCHEPHARM","JKCEMENT","JUBLPHARMA","KALPATPOWR","KEI",
    "MANAPPURAM","METROPOLIS","MRF","NATCOPHARM","NAVINFLUOR",
    "NLCINDIA","OLECTRA","PFIZER","RADICO","RAMCOCEM",
    "RITES","RVNL","SRF","STARHEALTH","SUNDARMFIN","SUPREMEIND","SYNGENE",
    "TATACHEM","TATAELXSI","THERMAX","TIMKEN","TORNTPOWER","TVSMOTOR",
    "VGUARD","VOLTAS","ZEEL","SAIL","NMDC","MOIL","NATIONALUM","HINDCOPPER",
    "VEDL","HINDZINC","GMRAIRPORT","ADANIPOWER","ADANITRANS","NHPC","SJVN",
    "IREDA","HUDCO","IRFC","RAILTEL","BEML","BEL","HAL","BHEL","MIDHANI",
    "GRSE","COCHINSHIP","MAZAGONDOCK","KARURVYSYA","SOUTHBANK","DCBBANK",
    "CITYUNIONBANK","EQUITASBNK","UJJIVANSFB","AUBANK","RBLBANK",
    # ── NIFTY SMALLCAP 250 + OTHERS ──
    "MFSL","NIACL","GICRE","ICICIGI","HDFCAMC","ABSLAMC","360ONE",
    "ANGELONE","IIFL","RATEGAIN","CARTRADE","EASEMYTRIP","IXIGO","NAZARA",
    "INFOEDGE","JUSTDIAL","MATRIMONY","INDIAMART","AFFLE","TANLA","ROUTE",
    "KFINTECH","CAMS","CDSL","BSE","MCX","DEEPAKFERT","GSPL","MGL","IGL",
    "ATGL","GUJGASLTD","PETRONET","AEGISCHEM","NOCIL","AAVAS","HOMEFIRST",
    "APTUS","CREDITACC","SPANDANA","UJJIVAN","SHRIRAMFIN","BAJAJHFL",
    "CANFINHOME","REPCO","APAR","CUPID","SHREEPUSHKAR","HFCL","STLTECH","TEJASNET","DATAMATICS",
    "MASTEK","KPITTECH","BIRLASOFT","ZENSAR","RELAXO","BATA","CAMPUS",
    "DMART","SHOPERSTOP","JYOTHYLAB","HATSUN","PGHH","GILLETTE","COLGATE",
    "AJANTPHARM","GLENMARK","WOCKPHARMA","ABBOTINDIA","SANOFI","BIOCON",
    "LAURUSLABS","STRIDES","SEQUENT","SUDARSCHEM","AARTI","VINATI","LAXMICHEM",
    "HEIDELBERG","ORIENTCEM","JKPAPER","TNPL","PUDUMJEE","ANDHRAPET",
    "VSTIND","GODFRYPHLP","UNITDSPR","TIINDIA","CRAFTSMAN","SANSERA",
    "ENDURANCE","MOTHERSON","BOSCHLTD","SCHAEFFLER","SKFINDIA","SUPRAJIT",
    "SUNDRMFAST","FIEMIND","MINDA","SUBROS","RACL","GABRIEL",
    "SETCO","ROLEXRINGS","RATNAMANI","WELCORP","JINDALSAW","JSWISPL",
    "APLAPOLLO","HIKAL","SUVEN","SEQUENT","GALAXYSURF","VINATIORGA","BAJAJCON","EMAMIPAP","KSCL",
    "MAHINDCIE","LUMAXIND","MUTHOOTFIN","IIFLWAM","MANINFRA","GAYAPROJ",
    "NBCC","NCC","PNCINFRA","KNRCON","HGINFRA","GPPL","JPPOWER","CESC",
    "RPOWER","NHPC","SJVN","KPRMILL","RUPA","DOLLAR","LOVABLE",
    "NIITLTD","APTECH","CRISIL","ICRA","CARERATING","ACCELYA","TANLA",
    "FSL","SPENCERS","VMART","NUVAMA","EDELWEISS","POONAWALLA","MUTHOOTCAP","CHOLAHLDNG","BAJAJHLDNG","GODREJAGRO","JUBLINGSCI",
    "SUVENPHAR","LALPATHLAB","THYROCARE","KRSNAA","VIJAYA","ASTERDM",
    "FORTIS","NARAYANAHEALTH","RAINBOW","DRREDDYS","IPCALAB","PFIZER",
    "NATPHARM","GRANULES","SUVEN","GLAND","BIOCON","STRIDES","LAURUSLABS",
    "SOLARA","MARKSANS","IRABMW","WINDLAS","GUFICBIO",
    "SHILPAMED","POLY","NUVOCO","TRONOX","INDORAMA","SUMITCHEM","RALLIS",
    "PIIND","DHANUKA","BAYER","EXCEL","GHCL","DCMSHRIRAM","CHAMBAL",
    "COROMANDEL","GSFC","MADRASFERT","PARADEEP","SPIC","DHARAMSI",
    "TATACHEMLS","AARTIDRUGS","MEDPLUS","ERIS","SOLARA","CAPLIPOINT",
    "GLENMARK","WOCKPHARMA","JBPHARMA","FDC","INDOCO","SUNPHARMA","ALKEM",
    "NATCOPHARM","TORNTPHARM","IPCALAB","CIPLA","DRREDDY","LUPIN","AUROPHARMA",
    "MANKIND","TIRUPATI","NAVNETEDU","PCJEWELLER","TITAN","RAJESHEXPO",
    "THANGAMAYL","GOLDIAM","SENCO","KALYAN","JOYALUKKAS","MALABAR",
    "UNIPARTS","ELECON","GREAVES","KIRLOSKAR","KOEL","LAKSHMIELET",
    "SUZLON","INOXWIND","POWERMECH","KEC","KALPATPOWR","TRIL","GEPIL",
    "ISGEC","TEXMACO","TITAGARH","REXNORD","SCHAEFFLER","SKFINDIA",
    "TIMKEN","GREAVESCOT","GREENPANEL","CENTURYPLY","KITEX","TRIDENT",
    "VARDHMAN","NITIN","BANSWRAS","DONEAR","RPGLIFE","SHREYANS",
    "SURYAROSNI","FINOLEX","POLYPLEX","UFLEX","HUHTAMAKI","MOLD-TEK","SUPREMEIND","NILKAMAL","VINYLINDIA","DCAL","GULFOILLUB",
    "CASTROLIND","BPCL","IOC","HINDPETRO","MRPL","CHENNPETRO",
    "IOCL","BPCL","HPL","PRAJ","GREENLAM","LLOYD","HAVELLS","VGUARD",
    "ORIENTELEC","KAYNES","SYRMA","AVALON","ELIN","LISI","AMBER",
    "VOLTAMP","SKIPPER","STERLITEPOWER","FINOLEX","VINDHYATEL",
    "GSPL","GAIL","PETRONET","IGL","MGL","ATGL","GUJGASLTD","ADANIGAS",
    "METROPOLIS","THYROCARE","LALPATHLAB","DRPATH","VIJAYALAB",
    "KRSNAA","VIJAYA","VIMTALABS","ACUITAS","AGAMATRIX",
    "ZOMATO","SWIGGY","NYKAA","CARTRADE","EASEMYTRIP","IXIGO","MAPMYINDIA",
    "PAYTM","POLICYBAAZAR","DELHIVERY","BRAINBEES","DOMS","UPDATER",
    "NETWEB","RATEGAIN","NAZARA","ONMOBILE","AFFLE","TANLA","ROUTE",
    "DATAMATICS","MASTEK","NIITLTD","APTECH","ZENSAR","BIRLASOFT",
    "HAPPSTMNDS","CYIENT","LTTS","COFORGE","MPHASIS","OFSS","PERSISTENT",
    "KPITTECH","TATAELXSI","TATATECH","SONATA","INTELLECT","NUCLEUS",
    "MSTC","SCI","CONCOR","BLUEDART","DTDC","TCI","GATI",
    "ALLCARGO","MAHLOG","MAHINDRA","GPPL","ADANIPORTS","APSEZ",
    "ORIENTHOTEL","LEMONTREE","MAHINDRAHOLIDAY","CHALET","SAMHI",
    "EIHOTEL","TAJGVK","SOTL","WONDERLA","IMAGICAA",
    "ISGEC","TEXMACO","TITAGARH","REXNORD","WPIL","HLE","ELGIEQUIP",
    "THERMAX","BHEL","BEL","HAL","GRSE","BEML","MIDHANI","COCHINSHIP",
    "MAZAGONDOCK","PARAS","GARWARE","MAFATLAL","MANDHANA","RUPA",
    "LOVABLE","DOLLAR","RAYMOND","ARVIND","WELSPUN","TRIDENT","VARDHMAN",
    "SWARAJENG","MAHSEAMLES","MANGLMCMT","HEIDELBERG","JKCEMENT","DALBHARAT",
    "RAMCOCEM","ULTRACEMCO","AMBUJACEM","ACC","SHREECEM","STARCEMENT",
    "BIRLACORPN","NUVOCO","SAURASHTRA","SANGHI","KAKATCEM","BURNPUR",
    "JKLAKSHMI","KESORAMIND","HICEM","PRISM",
    "GESHIP","ESABINDIA","GRINDWELL","SUNDRMBRAK","JTEKTINDIA","FAGBEARINGS",
    "NRBBEARING","ROLLCON","PRECISION","REXNORD","TINPLATE","TATAMETALIK",
    "JSPL","MTNL","BSNL","ONMOBILE","TANLA","ROUTE",
    "MINDACORP","MINDA","LUMAX","FIEM","SUPRAJIT","GABRIEL","SUBROS",
    "UCALFUEL","ROCI","BADVE","SETCO","ANPAS","RASOI","ANMOL",
    # ── Extended Nifty Midcap & Smallcap universe ──
    "IDFCFIRSTB","YESBANK","JMFINANCIL","EDELWEISS","MOTILALOSW","IIFLWAM",
    "NUVAMA","POLICYBZR","PAYTM","DELHIVERY","MAPMYINDIA","NAZARA",
    "INTELLECT","NUCLEUS","SONATA","MSTC","CONCOR","BLUEDART","TCI",
    "ALLCARGO","MAHLOG","ORIENTHOTEL","LEMONTREE","TAJGVK","CHALET",
    "SAMHI","EIHOTEL","WONDERLA","IMAGICAA","MAHINDRAHOLIDAY","TATATECH",
    "RATEGAIN","DATAMATICS","MASTEK","NIITLTD","APTECH","ZENSAR",
    "MEDPLUS","ERIS","CAPLIPOINT","WOCKPHARMA","JBPHARMA","FDC",
    "INDOCO","MANKIND","ALEMBICPHARM","ORCHPHARMA",
    "PIIND","DHANUKA","BAYER","EXCEL","GHCL","DCMSHRIRAM","CHAMBAL",
    "COROMANDEL","GSFC","RALLIS","SUMITCHEM","KSCL","AARTIDRUGS",
    "JKPAPER","TNPL","EMAMIPAP","GREENPANEL","TRIDENT",
    "VARDHMAN","NITIN","BANSWRAS","DONEAR","RAYMOND","ARVIND","WELSPUN",
    "MAFATLAL","MANDHANA","KPRMILL","KITEX","GARWARE","TIINDIA",
    "CRAFTSMAN","SANSERA","ENDURANCE","MOTHERSON","BOSCHLTD",
    "SUNDRMFAST","FIEMIND","SUBROS","GABRIEL",
    "ROLEXRINGS","RATNAMANI","WELCORP","JINDALSAW","JSWISPL","APLAPOLLO",
    "WPIL","HLE","ELGIEQUIP","ISGEC","TEXMACO","TITAGARH",
    "GREAVESCOT","GREAVES","KIRLOSKAR","KOEL","LAKSHMIELET","ELECON",
    "SUZLON","INOXWIND","POWERMECH","KEC","GEPIL","NBCC",
    "NCC","PNCINFRA","KNRCON","HGINFRA","JPPOWER","RPOWER",
    "MANINFRA","GAYAPROJ","SPENCERS","VMART","SHOPERSTOP",
    "VSTIND","GODFRYPHLP","UNITDSPR","JUBLFOOD","WESTLIFE","DEVYANI",
    "KAYNES","SYRMA","AVALON","ELIN","VOLTAMP","SKIPPER",
    "STERLITEPOWER","VINDHYATEL","ORIENTELEC",
    "PRAJ","CASTROLIND","GULFOILLUB","UFLEX",
    "POLYPLEX","NILKAMAL","GREENLAM","CERA","KAJARIA",
    "SOMANYCER","AKZOINDIA","KANSAINER","VINATIORGA",
    "GALAXYSURF","HIKAL","PCJEWELLER","RAJESHEXPO","THANGAMAYL",
    "GOLDIAM","SENCO","KALYAN","ETHOS","VAIBHAVGBL",
    "HEIDELBERG","JKLAKSHMI","PRISM","BIRLACORPN","NUVOCO","SANGHI",
    "STARCEMENT","ADANIGREEN","TORNTPOWER",
    "GESHIP","ESABINDIA","JTEKTINDIA","FAGBEARINGS","NRBBEARING",
    "TINPLATE","TATAMETALIK","JSPL","INDIANB","TMB","SURYODAY",
    "OBEROIRLTY","BRIGADE","SOBHA","PURVANKARA","KOLTEPATIL",
    "MAHLIFE","SUNTECK","PHOENIXLTD","MACROTECH",
    "ASHOKLEY","HINDMOTORS","PRICOL","VSTTILLERS",
    "FORCEMOT","SMLISUZU","TVSSRICHAK","BAJAJHIND",
    "BALRAMCHIN","DHAMPURSUG","TRIVENI","EID",
    "ORIENTBELL","NITCO","MURUDCERA",
    "INDIGO","SPICEJET","TCIEXP","GATI","DTDC","SCI",
    "IRCTC","RAILTEL","BEML","IRFC","HUDCO","IREDA",
    "THOMASCOOK","MHRIL","VRLLOG","GICRE","NIACL",
    "STARHEALTH","HDFCAMC","ABSLAMC",
    "POONAWALLA","MUTHOOTCAP","CHOLAHLDNG",
    "BAJAJHLDNG","GODREJAGRO","SUVENPHAR",
    "LALPATHLAB","THYROCARE","KRSNAA","ASTERDM",
    "FORTIS","NARAYANAHEALTH","RAINBOW","VIMTALABS",
    "SWARAJENG","MAHSEAMLES","SAURASHTRA","KAKATCEM",
    "PCJEWELLER","KALYANKJIL","ATGL","GUJGASLTD","PETRONET",
    "HINDPETRO","MRPL","CHENNPETRO","MOLD-TEK","HUHTAMAKI",
    # ── Final batch to reach 750 ──
    "ICRA","CRISIL","CARERATING","ACCELYA","TANLA","FSL",
    "BAJAJCON","MARICO","COLPAL","DABUR","GODREJCP","EMAMILTD",
    "JYOTHYLAB","HATSUN","PGHH","GILLETTE","COLGATE","HERITAGE",
    "TATACONSUM","NESTLEIND","BRITANNIA","ITC","HINDUNILVR",
    "RELAXO","BATA","CAMPUS","METRO","LIBERTY","ACTION",
    "PAGEIND","MANYAVAR","VEDANT","GOKEX","DMART","TRENT",
    "VMART","SHOPERSTOP","SPENCERS","WESTLIFE","JUBLFOOD",
    "BURGERKING","DEVYANI","SAPPHIRE","BARBEQUE",
    "ZYDUSLIFE","MANKIND","GLENMARK","WOCKPHARMA","AJANTPHARM",
    "IPCALAB","ALKEM","TORNTPHARM","DRREDDY","SUNPHARMA",
    "CIPLA","AUROPHARMA","LUPIN","DIVISLAB","BIOCON","STRIDES",
    "LAURUSLABS","GRANULES","NATCOPHARM","PFIZER","ABBOTINDIA",
    "SANOFI","NOVARTIS","SUVENPHAR","JUBLPHARMA",
    "BLISSGVS","SOLARA","MARKSANS","CAPLIPOINT","GLAND",
    "WINDLAS","GUFICBIO","SHILPAMED","SEQUENT",
    "NEULANDLAB","HIKAL","SUVEN","RPGLIFE",
    "AAVAS","HOMEFIRST","APTUS","CREDITACC","SPANDANA","UJJIVAN",
    "SHRIRAMFIN","BAJAJHFL","CANFINHOME","REPCO","MUTHOOTFIN",
    "LICHSGFIN","CHOLAFIN","M&MFIN","BAJAJFINSV","BAJFINANCE",
    "HDFCLIFE","SBILIFE","STARHEALTH","MAXHEALTH","NIACL","GICRE",
    "ICICIGI","HDFCAMC","ABSLAMC","360ONE","ANGELONE","IIFL",
    "NUVAMA","MOTILALOSW","KFINTECH","CAMS","CDSL","BSE","MCX",
    "RECLTD","PFC","IRFC","HUDCO","IREDA","RAILTEL","RVNL",
    "NHPC","SJVN","NTPC","POWERGRID","TATAPOWER","ADANIGREEN",
    "TORNTPOWER","CESC","RPOWER","JPPOWER","ADANIPOWER",
    "ADANITRANS","SUZLON","INOXWIND","SWANENERGY",
    "COALINDIA","NMDC","MOIL","NATIONALUM","HINDCOPPER","VEDL",
    "HINDZINC","JSPL","TATASTEEL","JSWSTEEL","SAIL","HINDALCO",
    "GMRAIRPORT","ADANIPORTS","CONCOR","SCI","IRCTC","BLUEDART",
    "TCI","ALLCARGO","MAHLOG","GATI","DTDC","VRLLOG","TCIEXP",
    "INDIGO","SPICEJET","INTERGLOBE","THOMASCOOK","MHRIL",
    "INDHOTEL","EIHOTEL","TAJGVK","CHALET","SAMHI","LEMONTREE",
    "ORIENTHOTEL","WONDERLA","MAHINDRAHOLIDAY","IMAGICAA",
    "DLF","LODHA","PRESTIGE","GODREJPROP","SOBHA","BRIGADE",
    "OBEROIRLTY","KOLTEPATIL","MAHLIFE","SUNTECK","PHOENIXLTD",
    "PURVANKARA","MACROTECH","INDIABULLS","RBLBANK","AUBANK",
    # ── Nifty 500 completions ──
    "JAIBALAJI","LLOYDSME","HBLPOWER","DLINKINDIA","GTLINFRA",
    "GTPL","YATHARTH","NETWEB","UPDATER","BRAINBEES","DOMS",
    "SBFC","UGROCAP","FIVESTAR","FEDBANK","ESAFSFB","UTKARSH",
    "JKIL","GPIL","KIOCL","MIDHANI","GRSE","COCHINSHIP",
    "MAZAGONDOCK","BEML","BEL","HAL","BHEL","MIDHANI",
    "AARTIPHARM","IOLCP","SUDARSCHEM","ANDHRAPET","DEEPIND",
    "ORIENTBELL","NITCO","MURUDCERA","SOMANYCERA","CERA",
    "KAJARIA","GREENLAM","GREENPLY",
    "HINDWAREAP","HSIL","CEAT","MRF","APOLLOTYRE","BALKRISIND",
    "JKTYRE","TVSSRICHAK","PARAS",
    "KRBL","LT","LTIM","COFORGE","MPHASIS","OFSS","PERSISTENT",
    "KPITTECH","TATAELXSI","TATATECH","CYIENT","LTTS","BIRLASOFT",
    "HAPPSTMNDS","ZENSAR","MASTEK","NIITLTD","DATAMATICS",
    "TANLA","ROUTE","AFFLE","INTELLECT","NUCLEUS","SONATA",
    "NAZARA","INFOEDGE","JUSTDIAL","MATRIMONY","INDIAMART",
    "NAUKRI","MAPMYINDIA","RATEGAIN","IXIGO","EASEMYTRIP",
    "CARTRADE","POLICYBZR","PAYTM","ZOMATO","NYKAA",
    "DELHIVERY","SWIGGY","BRAINBEES","DOMS","UPDATER","NETWEB",
    "VAIBHAVGBL","ETHOS","SENCO","KALYAN","GOLDIAM","THANGAMAYL",
    "RAJESHEXPO","PCJEWELLER","TITAN","KALYANKJIL",
    "SSWL","SANDHAR","MINDA","LUMAXIND","LUMAX","FIEM",
    "PRICOL","VSTTILLERS","FORCEMOT","SMLISUZU","ASHOKLEY",
    "TATAMOTORS","MARUTI","M&M","BAJAJ-AUTO","HEROMOTOCO",
    "EICHERMOT","TVSMOTOR","ESCORTS","MAHINDCIE","ENDURANCE",
    "MOTHERSON","BOSCHLTD","SCHAEFFLER","SKFINDIA","TIMKEN",
    "GRINDWELL","SUNDRMBRAK","GABRIEL","SUBROS","SUPRAJIT",
    "SUNDRMFAST","FIEMIND","JTEKTINDIA","NRBBEARING","FAGBEARINGS",
    "ROLLCON","WPIL","HLE","ELGIEQUIP","KIRLOSKAR","KOEL",
    "ELECON","GREAVES","GREAVESCOT","THERMAX","ISGEC",
    "TEXMACO","TITAGARH","RATNAMANI","WELCORP","JINDALSAW",
    "JSWISPL","APLAPOLLO","TINPLATE","TATAMETALIK","JSPL",
    "MOIL","NMDC","NATIONALUM","HINDCOPPER","SAIL","HINDALCO",
    "DEEPAKNTR","ATUL","FINEORG","NAVINFLUOR","SRF","GNFC",
    "AARTIDRUGS","AARTI","VINATI","LAXMICHEM","NOCIL","SUDARSCHEM",
    "KSCL","PIIND","DHANUKA","BAYER","EXCEL","GHCL","DCMSHRIRAM",
    "CHAMBAL","COROMANDEL","GSFC","RALLIS","SUMITCHEM",
    "DEEPAKFERT","GSPL","TATACHEM","VINATIORGA","GALAXYSURF",
    "HIKAL","SEQUENT","SOLARA","MARKSANS","CAPLIPOINT",
    "NATCOPHARM","GRANULES","AJANTPHARM","GLENMARK","WOCKPHARMA",
    "JBPHARMA","FDC","INDOCO","MANKIND","ALEMBICPHARM","ORCHPHARMA",
    "NEULANDLAB","BLISSGVS","GUFICBIO","SHILPAMED","WINDLAS",
    "RPGLIFE","IOLCP","AARTIPHARM","SUVEN","HIKAL",
    "KARURVYSYA","SOUTHBANK","DCBBANK","CITYUNIONBANK","TMB",
    "EQUITASBNK","UJJIVANSFB","SURYODAY","IDFC","YESBANK",
    "BANDHANBNK","FEDERALBNK","PNB","BANKBARODA","CANBK","UNIONBANK",
    "INDIANB","SBIN","ICICIBANK","HDFCBANK","AXISBANK","KOTAKBANK",
    "INDUSINDBK","IDFCFIRSTB","JMFINANCIL","EDELWEISS","MOTILALOSW",
    # ── Nifty Smallcap 250 additions ──
    "HBLPOWER","GTLINFRA","GTPL","YATHARTH","SBFC","UGROCAP",
    "FIVESTAR","FEDBANK","ESAFSFB","UTKARSH","JKIL","GPIL","KIOCL",
    "SSWL","SANDHAR","LUMAXIND","LUMAX","CEAT","APOLLOTYRE",
    "BALKRISIND","JKTYRE","KRBL","LINDEINDIA",
    "IGARASHI","PNBHOUSING","REPCO","CANFINHOME","BAJAJHFL",
    "CREDITACC","SPANDANA","UJJIVAN","SHRIRAMFIN","M&MFIN",
    "CHOLAFIN","MANAPPURAM","AAVAS","HOMEFIRST","APTUS",
    "MUTHOOTCAP","POONAWALLA","JMFINANCIL",
    "NUVAMA","IIFLWAM","MOTILALOSW","ANGELONE","KFINTECH",
    "CAMS","CDSL","BSE","MCX","ICRA","CRISIL","CARERATING",
    "POLICYBZR","PAYTM","DELHIVERY","MAPMYINDIA","NAUKRI",
    "INFOEDGE","JUSTDIAL","MATRIMONY","INDIAMART",
    "AFFLE","TANLA","ROUTE","INTELLECT","NUCLEUS","SONATA","DATAMATICS","MASTEK","APTECH","NIITLTD",
    "ZENSAR","BIRLASOFT","HAPPSTMNDS","CYIENT",
    "KAYNES","SYRMA","AVALON","ELIN","AMBER","DIXON",
    "VOLTAMP","SKIPPER","STERLITEPOWER","VINDHYATEL","ORIENTELEC",
    "KEI","FINOLEX","POLYCAB","HAVELLS","VGUARD",
    "HFCL","STLTECH","TEJASNET",
    "IRCTC","CONCOR","SCI","GESHIP","TCIEXP","VRLLOG",
    "ALLCARGO","MAHLOG","TCI","GATI","DTDC","BLUEDART","MAHINDRAHOLIDAY",
    "WONDERLA","IMAGICAA","EIHOTEL","TAJGVK","CHALET","SAMHI",
    "LEMONTREE","ORIENTHOTEL","INDHOTEL",
    "OBEROIRLTY","BRIGADE","SOBHA","PURVANKARA","KOLTEPATIL",
    "MAHLIFE","SUNTECK","PHOENIXLTD","MACROTECH","GODREJPROP",
    "DLF","LODHA","PRESTIGE","INDIABULLS",
    "TORNTPOWER","CESC","RPOWER","JPPOWER","ADANIPOWER",
    "ADANITRANS","SUZLON","INOXWIND","SWANENERGY","ADANIGREEN",
    "TATAPOWER","NHPC","SJVN","NTPC","POWERGRID","COALINDIA",
    "PETRONET","IGL","MGL","ATGL","GUJGASLTD","GSPL","GAIL",
    "HINDPETRO","MRPL","CHENNPETRO","BPCL","IOC","ONGC",
    "CASTROLIND","GULFOILLUB","PRAJ",
    "HEIDELBERG","JKLAKSHMI","PRISM","BIRLACORPN","NUVOCO",
    "SAURASHTRA","SANGHI","KAKATCEM","STARCEMENT",
    "JKCEMENT","RAMCOCEM","DALBHARAT","ULTRACEMCO","AMBUJACEM","ACC","SHREECEM",
    "RELAXO","BATA","CAMPUS","METRO","LIBERTY","ACTION",
    "PAGEIND","MANYAVAR","DMART","TRENT","VMART","SHOPERSTOP",
    "SPENCERS","WESTLIFE","JUBLFOOD","DEVYANI","SAPPHIRE","BARBEQUE",
    "VSTIND","GODFRYPHLP","UNITDSPR","RADICO","MCDOWELL-N",
    "BAJAJCON","MARICO","COLPAL","DABUR","GODREJCP","EMAMILTD",
    "JYOTHYLAB","HATSUN","PGHH","GILLETTE","COLGATE","HERITAGE",
    "INDIACEM",
]

# Deduplicate preserving order
seen = set()
STOCKS = []
for s in ALL_STOCKS:
    if s not in seen:
        seen.add(s)
        STOCKS.append(s)

# ─────────────────────────────────────────────────────────────────────────────
# INDICATOR FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def compute_rsi(close, period=14):
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return (100 - (100 / (1 + rs))).fillna(50)

def compute_macd(close, fast=12, slow=26, signal=9):
    ema_f = close.ewm(span=fast, adjust=False).mean()
    ema_s = close.ewm(span=slow, adjust=False).mean()
    macd = ema_f - ema_s
    sig = macd.ewm(span=signal, adjust=False).mean()
    return macd, sig

def compute_adx(high, low, close, period=14):
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs()
    ], axis=1).max(axis=1)
    up = high.diff()
    down = -low.diff()
    plus_dm = pd.Series(np.where((up > down) & (up > 0), up, 0.0), index=close.index)
    minus_dm = pd.Series(np.where((down > up) & (down > 0), down, 0.0), index=close.index)
    atr = tr.ewm(alpha=1/period, adjust=False).mean()
    plus_di = 100 * plus_dm.ewm(alpha=1/period, adjust=False).mean() / atr.replace(0, np.nan)
    minus_di = 100 * minus_dm.ewm(alpha=1/period, adjust=False).mean() / atr.replace(0, np.nan)
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    adx = dx.ewm(alpha=1/period, adjust=False).mean()
    return adx.fillna(0), plus_di.fillna(0), minus_di.fillna(0)

def compute_obv(close, volume):
    direction = np.sign(close.diff()).fillna(0)
    return (volume * direction).cumsum()

# ─────────────────────────────────────────────────────────────────────────────
# SCREEN ONE STOCK
# ─────────────────────────────────────────────────────────────────────────────

def screen_stock(sym, w_df, d_df):
    try:
        if w_df is None or d_df is None or len(w_df) < 52 or len(d_df) < 60:
            return None

        wc = w_df["Close"].dropna()
        wh = w_df["High"].dropna()
        wl = w_df["Low"].dropna()
        wv = w_df["Volume"].dropna()
        dc = d_df["Close"].dropna()

        if len(wc) < 52 or len(dc) < 50:
            return None

        cur = float(dc.iloc[-1])

        def pct(n):
            try:
                return round((float(dc.iloc[-1]) / float(dc.iloc[-n]) - 1) * 100, 2) if len(dc) > n else None
            except Exception:
                return None

        # Price changes
        ch1d = pct(2)
        ch1w = pct(6)
        ch1m = pct(22)
        ch3m = pct(66)
        ch6m = pct(132)
        ch1y = pct(252)

        # 52W high (use weekly HIGH for accurate resistance) / low (weekly LOW)
        wh_aligned = wh.reindex(wc.index).ffill().bfill()
        wl_aligned = wl.reindex(wc.index).ffill().bfill()
        h52 = float(wh_aligned.rolling(52).max().iloc[-1])
        l52 = float(wl_aligned.rolling(52).min().iloc[-1])
        rng = (h52 - l52) / l52 if l52 > 0 else 999

        # C1: Consolidation — price range ≤35% over last 36 weeks (≈9 months)
        # Uses 36W box only; the 52W rng is kept for C2's h52 reference only.
        last36 = wc.iloc[-36:]
        box_max = float(last36.max())
        box_min = float(last36.min())
        box_width = (box_max - box_min) / box_min if box_min > 0 else 999
        c1 = bool(box_width <= 0.35)

        # C2: Near breakout — within 10% of 52W high
        c2 = bool(cur >= h52 * 0.90)

        # C3: RSI 55–78 on weekly
        wrsi = compute_rsi(wc)
        rsi_val = float(wrsi.iloc[-1])
        c3 = bool(55 <= rsi_val <= 78)

        # C4: MACD bullish (weekly)
        macd_line, macd_sig = compute_macd(wc)
        c4 = bool(macd_line.iloc[-1] > macd_sig.iloc[-1])

        # C5: Price > 50W SMA and SMA rising
        sma50w = wc.rolling(50).mean()
        c5 = bool(
            len(sma50w.dropna()) >= 5 and
            cur > float(sma50w.iloc[-1]) and
            float(sma50w.iloc[-1]) > float(sma50w.iloc[-5])
        )

        # C6: OBV in top 30% of 52W range
        # Align volume to close index to prevent NaN misalignment
        wv_aligned = wv.reindex(wc.index).fillna(0)
        obv = compute_obv(wc, wv_aligned)
        obv_max = float(obv.rolling(52).max().iloc[-1])
        obv_min = float(obv.rolling(52).min().iloc[-1])
        obv_range = obv_max - obv_min
        obv_pos = (float(obv.iloc[-1]) - obv_min) / obv_range if obv_range != 0 else 0.5
        c6 = bool(obv_pos >= 0.70)

        # C7: ADX 20–45 rising, +DI > -DI
        # Reuse wh_aligned / wl_aligned (already ffill+bfill'd above)
        adx, pdi, mdi = compute_adx(wh_aligned, wl_aligned, wc)
        adx_val = float(adx.iloc[-1])
        adx_rising = len(adx) > 4 and float(adx.iloc[-1]) > float(adx.iloc[-4])
        c7 = bool(20 <= adx_val <= 45 and adx_rising and float(pdi.iloc[-1]) > float(mdi.iloc[-1]))

        # C8: Bollinger Band Squeeze — bands at their tightest + price near/above upper band
        bb_period = 20
        bb_sma = wc.rolling(bb_period).mean()
        bb_std = wc.rolling(bb_period).std()
        bb_upper = bb_sma + 2 * bb_std
        bb_lower = bb_sma - 2 * bb_std
        bbw = ((bb_upper - bb_lower) / bb_sma).replace([np.inf, -np.inf], np.nan).dropna()
        if len(bbw) >= 52:
            bbw_52 = bbw.iloc[-52:]
            bbw_min52 = float(bbw_52.min())
            bbw_max52 = float(bbw_52.max())
            bbw_cur = float(bbw.iloc[-1])
            bbw_range = bbw_max52 - bbw_min52
            # Squeeze = BBW in bottom 25% of its 52W range
            bbw_pct = (bbw_cur - bbw_min52) / bbw_range if bbw_range > 0 else 0.5
            squeeze = bool(bbw_pct <= 0.25)
            # Expansion = price at or above upper BB (breakout from squeeze)
            price_above_upper = bool(len(bb_upper.dropna()) > 0 and cur >= float(bb_upper.dropna().iloc[-1]) * 0.99)
            c8 = bool(squeeze or price_above_upper)
        else:
            c8 = False

        score = sum([c1, c2, c3, c4, c5, c6, c7, c8])

        return {
            "Symbol": sym,
            "Price (INR)": round(cur, 1),
            "1D %": ch1d,
            "1W %": ch1w,
            "1M %": ch1m,
            "3M %": ch3m,
            "6M %": ch6m,
            "1Y %": ch1y,
            "C1 Consolidation": c1,
            "C2 Near Breakout": c2,
            "C3 RSI Bullish":   c3,
            "C4 MACD Bullish":  c4,
            "C5 MA Aligned":    c5,
            "C6 OBV Strong":    c6,
            "C7 ADX Rising":    c7,
            "C8 BB Squeeze":    c8,
            "Score": score,
        }
    except Exception as e:
        # Uncomment below line for debugging individual stock failures:
        # st.sidebar.warning(f"{sym}: {e}")
        return None

# ─────────────────────────────────────────────────────────────────────────────
# STAGE CLASSIFIER
# ─────────────────────────────────────────────────────────────────────────────

def classify_stage(row):
    c1 = row["C1 Consolidation"]
    c2 = row["C2 Near Breakout"]
    c8 = row["C8 BB Squeeze"]
    confirmatory = sum([
        row["C3 RSI Bullish"], row["C4 MACD Bullish"],
        row["C5 MA Aligned"],  row["C6 OBV Strong"], row["C7 ADX Rising"]
    ])
    if c1 and c8 and c2 and confirmatory >= 4:
        return "🚀 Breaking Out"
    elif c1 and c8 and c2 and confirmatory >= 2:
        return "🟢 Ready"
    elif c1 and c8 and c2:
        return "🟠 Approaching"
    elif c1 and c8:
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
# BATCH DATA FETCH — splits 750 stocks into chunks of 100 to stay reliable
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=3600 * 8, show_spinner=False)
def fetch_batch(symbols_tuple, interval, period):
    """Fetch a batch of symbols; returns dict sym -> DataFrame."""
    symbols = list(symbols_tuple)
    tickers = [f"{s}.NS" for s in symbols]
    try:
        raw = yf.download(
            tickers,
            period=period,
            interval=interval,
            group_by="ticker",
            auto_adjust=True,
            progress=False,
        )
    except Exception:
        return {}

    result = {}
    is_multi = isinstance(raw.columns, pd.MultiIndex)
    for sym, tkr in zip(symbols, tickers):
        try:
            if len(tickers) == 1 and not is_multi:
                # Single ticker: flat columns
                df = raw.dropna(how="all")
            elif is_multi:
                # Multi-ticker: MultiIndex columns — try both axis orderings
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
    total_chunks = len(chunks)

    weekly_data = {}
    daily_data  = {}

    for idx, chunk in enumerate(chunks):
        pct = (idx + 0.5) / total_chunks
        progress_bar.progress(pct, text=f"📥 Downloading data batch {idx+1}/{total_chunks} ({len(chunk)} stocks)…")
        w = fetch_batch(tuple(chunk), "1wk", "2y")
        d = fetch_batch(tuple(chunk), "1d",  "18mo")
        weekly_data.update(w)
        daily_data.update(d)

    return weekly_data, daily_data

# ─────────────────────────────────────────────────────────────────────────────
# MAIN UI
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="header-block">
  <div class="header-title">🚀 NIFTY TOP 750 — CONSOLIDATION BREAKOUT SCANNER</div>
  <div class="header-sub">
    Multi-month/year base breakout identification across ~750 NSE stocks &nbsp;|&nbsp;
    8-criteria technical framework &nbsp;|&nbsp; Data via Yahoo Finance (yfinance) &nbsp;|&nbsp; Prices in INR
  </div>
</div>
""", unsafe_allow_html=True)

# ── Criteria Summary Panel ──
st.markdown("""
<div style="background:#0d1b3e;border:1px solid #1e3a5f;border-radius:12px;padding:18px 24px;margin-bottom:18px;">
  <div style="color:#4fc3f7;font-family:'Space Mono',monospace;font-size:13px;font-weight:700;margin-bottom:12px;letter-spacing:0.5px;">
    📌 CRITERIA QUICK REFERENCE
  </div>
  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;">
    <div style="background:#06111f;border:1px solid #1e3a5f;border-radius:8px;padding:10px 12px;">
      <div style="color:#4fc3f7;font-weight:700;font-size:12px;margin-bottom:4px;">C1 — Consolidation</div>
      <div style="color:#a0b8d0;font-size:11px;line-height:1.5;">Price range ≤35% over last 9 months. Stock has been building a base — the coiling spring phase.</div>
    </div>
    <div style="background:#06111f;border:1px solid #1e3a5f;border-radius:8px;padding:10px 12px;">
      <div style="color:#4fc3f7;font-weight:700;font-size:12px;margin-bottom:4px;">C2 — Near Breakout</div>
      <div style="color:#a0b8d0;font-size:11px;line-height:1.5;">Price within 10% of its 52-week high. Stock is approaching the top of its consolidation box.</div>
    </div>
    <div style="background:#06111f;border:1px solid #1e3a5f;border-radius:8px;padding:10px 12px;">
      <div style="color:#4fc3f7;font-weight:700;font-size:12px;margin-bottom:4px;">C3 — RSI Bullish</div>
      <div style="color:#a0b8d0;font-size:11px;line-height:1.5;">Weekly RSI between 55–78. Momentum is building but not yet overbought — the breakout sweet spot.</div>
    </div>
    <div style="background:#06111f;border:1px solid #1e3a5f;border-radius:8px;padding:10px 12px;">
      <div style="color:#4fc3f7;font-weight:700;font-size:12px;margin-bottom:4px;">C4 — MACD Bullish</div>
      <div style="color:#a0b8d0;font-size:11px;line-height:1.5;">MACD line above Signal line on weekly chart. Short-term momentum crossing above long-term trend.</div>
    </div>
    <div style="background:#06111f;border:1px solid #1e3a5f;border-radius:8px;padding:10px 12px;">
      <div style="color:#4fc3f7;font-weight:700;font-size:12px;margin-bottom:4px;">C5 — MA Aligned</div>
      <div style="color:#a0b8d0;font-size:11px;line-height:1.5;">Price above rising 50-week SMA. The long-term trend structure is positive and strengthening.</div>
    </div>
    <div style="background:#06111f;border:1px solid #1e3a5f;border-radius:8px;padding:10px 12px;">
      <div style="color:#4fc3f7;font-weight:700;font-size:12px;margin-bottom:4px;">C6 — OBV Strong</div>
      <div style="color:#a0b8d0;font-size:11px;line-height:1.5;">On-Balance Volume in top 30% of its 52W range. Institutions quietly accumulating while price is flat.</div>
    </div>
    <div style="background:#06111f;border:1px solid #1e3a5f;border-radius:8px;padding:10px 12px;">
      <div style="color:#4fc3f7;font-weight:700;font-size:12px;margin-bottom:4px;">C7 — ADX Rising</div>
      <div style="color:#a0b8d0;font-size:11px;line-height:1.5;">ADX between 20–45 and trending up, +DI above -DI. A new directional trend is being born.</div>
    </div>
    <div style="background:#06111f;border:1px solid #1e3a5f;border-radius:8px;padding:10px 12px;">
      <div style="color:#69f0ae;font-weight:700;font-size:12px;margin-bottom:4px;">C8 — BB Squeeze ★</div>
      <div style="color:#a0b8d0;font-size:11px;line-height:1.5;">Bollinger Bands at their tightest in months (bottom 25% of 52W width). Maximum energy compression before an explosive move.</div>
    </div>
  </div>
  <div style="margin-top:14px;background:#06111f;border:1px solid #1e3a5f;border-radius:8px;padding:12px 16px;">
    <div style="color:#4fc3f7;font-weight:700;font-size:12px;margin-bottom:8px;">🏷️ BREAKOUT STAGE CLASSIFICATION — What the Stage column means</div>
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;">
      <div style="padding:8px 10px;background:#0d1b3e;border-radius:6px;border-left:3px solid #ffd600;">
        <div style="color:#ffd600;font-weight:700;font-size:11px;">🟡 COILING</div>
        <div style="color:#a0b8d0;font-size:10px;margin-top:3px;">C1 + C8 both met. Valid base exists and Bollinger Bands are compressed. Energy is building — put on watchlist.</div>
      </div>
      <div style="padding:8px 10px;background:#0d1b3e;border-radius:6px;border-left:3px solid #ff9800;">
        <div style="color:#ff9800;font-weight:700;font-size:11px;">🟠 APPROACHING</div>
        <div style="color:#a0b8d0;font-size:10px;margin-top:3px;">C1 + C8 + C2 all met. Stock is now within 10% of its breakout level. Set a price alert.</div>
      </div>
      <div style="padding:8px 10px;background:#0d1b3e;border-radius:6px;border-left:3px solid #00e676;">
        <div style="color:#00e676;font-weight:700;font-size:11px;">🟢 READY</div>
        <div style="color:#a0b8d0;font-size:10px;margin-top:3px;">C1 + C8 + C2 + at least 2 of 5 confirmatory signals met. Momentum is aligning. High priority — review chart now.</div>
      </div>
      <div style="padding:8px 10px;background:#0d1b3e;border-radius:6px;border-left:3px solid #4fc3f7;">
        <div style="color:#4fc3f7;font-weight:700;font-size:11px;">🚀 BREAKING OUT</div>
        <div style="color:#a0b8d0;font-size:10px;margin-top:3px;">C1 + C8 + C2 + 4 or more confirmatory signals. All systems go. Verify on chart and apply entry rules.</div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ──
with st.sidebar:
    st.markdown("### ⚙️ Filters")
    min_score = st.slider("Minimum Breakout Score", 0, 8, 3)

    st.markdown("---")
    st.markdown("### 📋 Criteria Reference")
    criteria_info = {
        "C1": "Consolidation — Price range ≤35% over last 9 months",
        "C2": "Near Breakout — Within 10% of 52-week high",
        "C3": "RSI Bullish — Weekly RSI between 55 and 78",
        "C4": "MACD Bullish — MACD line above Signal line (weekly)",
        "C5": "MA Aligned — Price above 50W SMA; SMA rising",
        "C6": "OBV Strong — OBV in top 30% of its 52W range",
        "C7": "ADX Rising — ADX 20–45, trending up, +DI > -DI",
        "C8": "BB Squeeze — Bollinger Bands at tightest in months",
    }
    for k, v in criteria_info.items():
        st.markdown(f"**{k}** — {v}")

    st.markdown("---")
    st.caption(
        "**Stages:** 🚀 Act now → 🟢 High priority → 🟠 Set alert → 🟡 Watchlist\n\n"
        "**Score** = total of all 8 criteria met (C1–C8)\n\n"
        "🟡 Coiling stocks score 2 — set filter to 2 to see them\n\n"
        "⏱ First load: ~8–12 mins | Cache: 8 hours"
    )

# ── Refresh row ──
ist_now = datetime.now(pytz.timezone("Asia/Kolkata"))
market_open = (9 <= ist_now.hour < 15) or (ist_now.hour == 15 and ist_now.minute <= 30)
market_status = "🟢 Market Open" if market_open else "🔴 Market Closed"

col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.markdown(
        f'<div style="color:#7a9abf;font-size:13px;padding-top:6px;">'
        f'{market_status} &nbsp;|&nbsp; IST: {ist_now.strftime("%d %b %Y, %I:%M %p")}'
        f'</div>', unsafe_allow_html=True
    )
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
            unsafe_allow_html=True
        )

st.markdown("<br>", unsafe_allow_html=True)

# ── Download + Screen ──
prog = st.progress(0, text="Starting data download…")

weekly_data, daily_data = fetch_all(STOCKS, prog)

rows = []
total = len(STOCKS)
for i, sym in enumerate(STOCKS):
    prog.progress(0.5 + (i + 1) / total * 0.5, text=f"🔍 Screening {sym} ({i+1}/{total})…")
    rec = screen_stock(sym, weekly_data.get(sym), daily_data.get(sym))
    if rec:
        rows.append(rec)

prog.empty()

if not rows:
    st.error("No data returned. Check your internet connection and try Refresh.")
    st.stop()

df = pd.DataFrame(rows)
df["Stage"] = df.apply(classify_stage, axis=1)
df["Stage Order"] = df["Stage"].map(STAGE_ORDER).fillna(5)
df_filtered = (
    df[df["Score"] >= min_score]
    .sort_values(["Stage Order", "Score"], ascending=[True, False])
    .reset_index(drop=True)
)

# ── Summary metrics ──
m1, m2, m3, m4, m5, m6 = st.columns(6)
for col, val, lbl in [
    (m1, len(STOCKS),                                          "Universe"),
    (m2, len(df),                                              "Data Available"),
    (m3, len(df[df["Stage"] == "🚀 Breaking Out"]),            "🚀 Breaking Out"),
    (m4, len(df[df["Stage"] == "🟢 Ready"]),                   "🟢 Ready"),
    (m5, len(df[df["Stage"] == "🟠 Approaching"]),             "🟠 Approaching"),
    (m6, len(df[df["Stage"] == "🟡 Coiling"]),                 "🟡 Coiling"),
]:
    with col:
        st.markdown(
            f'<div class="metric-card"><div class="metric-val">{val}</div>'
            f'<div class="metric-lbl">{lbl}</div></div>',
            unsafe_allow_html=True
        )

st.markdown("<br>", unsafe_allow_html=True)

# ── Build display table ──
crit_cols = [
    "C1 Consolidation","C2 Near Breakout","C3 RSI Bullish",
    "C4 MACD Bullish","C5 MA Aligned","C6 OBV Strong",
    "C7 ADX Rising","C8 BB Squeeze",
]

display_df = df_filtered[[
    "Symbol","Stage","Price (INR)",
    "1D %","1W %","1M %","3M %","6M %","1Y %",
] + crit_cols + ["Score"]].copy()

for c in crit_cols:
    display_df[c] = display_df[c].map(lambda x: "✅" if x else "❌")

display_df.rename(columns={
    "C1 Consolidation": "C1",
    "C2 Near Breakout": "C2",
    "C3 RSI Bullish":   "C3",
    "C4 MACD Bullish":  "C4",
    "C5 MA Aligned":    "C5",
    "C6 OBV Strong":    "C6",
    "C7 ADX Rising":    "C7",
    "C8 BB Squeeze":    "C8",
}, inplace=True)

st.markdown(f"### 📊 Breakout Candidates — Score ≥ {min_score} &nbsp;|&nbsp; {len(df_filtered)} stocks &nbsp;|&nbsp; Sorted by Stage then Score")

st.dataframe(
    display_df,
    use_container_width=True,
    height=min(700, max(300, len(display_df) * 38 + 50)),
    column_config={
        "Symbol":       st.column_config.TextColumn("Symbol",    width="small"),
        "Stage":        st.column_config.TextColumn("Stage",     width="medium"),
        "Price (INR)":  st.column_config.NumberColumn("Price ₹", format="₹%.1f", width="small"),
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
            "Score", min_value=0, max_value=8, format="%d/8", width="small"
        ),
    },
    hide_index=True,
)

st.caption(
    "💡 Click any column header to sort high→low or low→high. "
    "All criteria should be verified manually on a chart before taking a position. "
    "This is a scanner, not a buy recommendation."
)

st.markdown("---")
st.markdown(
    '<div style="color:#3a5a7a;font-size:11px;text-align:center;">'
    'Data sourced from Yahoo Finance via yfinance. Not financial advice. '
    'Past performance does not guarantee future results. '
    'Always conduct your own due diligence before investing.'
    '</div>',
    unsafe_allow_html=True
)

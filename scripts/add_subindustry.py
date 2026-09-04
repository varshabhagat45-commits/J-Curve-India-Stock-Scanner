"""
One-time script to add 'subIndustry' field to data/tickers.json
mapping each ticker to one of the 88 NSE-style sub-industries.
"""
import json
from pathlib import Path

PATH = Path("data/tickers.json")

# Mapping: symbol -> sub-industry from the user's list
SUBSECTOR = {
    # Aerospace & Defence
    "HAL": "Aerospace & Defence", "BEL": "Aerospace & Defence",
    "BDL": "Aerospace & Defence", "MAZDOCK": "Aerospace & Defence",
    "COCHINSHIP": "Aerospace & Defence", "SOLARINDS": "Aerospace & Defence",
    "DATAPATTERNS": "Aerospace & Defence",

    # Agro Chemicals
    "UPL": "Agro Chemicals", "PIIND": "Agro Chemicals",
    "DHANUKA": "Agro Chemicals", "RALLIS": "Agro Chemicals",
    "INSECTICID": "Agro Chemicals", "BHARATRAS": "Agro Chemicals",

    # Air Transport Service
    "INDIGO": "Air Transport Service", "SPICEJET": "Air Transport Service",

    # Alcoholic Beverages
    "UNITDSPR": "Alcoholic Beverages", "RADICO": "Alcoholic Beverages",
    "ALLIEDBL": "Alcoholic Beverages", "GLOBUSSPR": "Alcoholic Beverages",
    "TI": "Alcoholic Beverages",

    # Auto Ancillaries
    "BHARATFORG": "Auto Ancillaries", "SONACOMS": "Auto Ancillaries",
    "UNOMINDA": "Auto Ancillaries", "ENDURANCE": "Auto Ancillaries",
    "MOTHERSON": "Auto Ancillaries", "BALKRISIND": "Auto Ancillaries",
    "EXIDEIND": "Auto Ancillaries", "AMARAJABAT": "Auto Ancillaries",

    # Automobile
    "MARUTI": "Automobile", "M&M": "Automobile", "TATAMOTORS": "Automobile",
    "ASHOKLEY": "Automobile", "EICHERMOT": "Automobile", "BAJAJ-AUTO": "Automobile",
    "HYUNDAI": "Automobile", "HEROMOTOCO": "Automobile", "TVSMOTOR": "Automobile",
    "ESCORTS": "Automobile", "FORCEMOT": "Automobile", "SMLISUZU": "Automobile",
    "GREAVESCOTTON": "Automobile",

    # Banks
    "HDFCBANK": "Banks", "ICICIBANK": "Banks", "SBIN": "Banks",
    "KOTAKBANK": "Banks", "AXISBANK": "Banks", "INDUSINDBK": "Banks",
    "BANKBARODA": "Banks", "PNB": "Banks", "CANBK": "Banks",
    "BANDHANBNK": "Banks", "AUBANK": "Banks", "RBLBANK": "Banks",
    "DCBBANK": "Banks", "KARURVYSYA": "Banks", "FEDERALBNK": "Banks",
    "YESBANK": "Banks",

    # Bearings
    "TIMKEN": "Bearings", "SKFINDIA": "Bearings", "NRBBEARING": "Bearings",
    "SCHAEFFLER": "Bearings",

    # Cables
    "POLYCAB": "Cables", "KEI": "Cables", "FINCABLES": "Cables",
    "HAVELLS": "Cables", "VGUARD": "Cables",

    # Capital Goods - Electrical Equipment
    "SIEMENS": "Capital Goods - Electrical Equipment",
    "ABB": "Capital Goods - Electrical Equipment",
    "CGPOWER": "Capital Goods - Electrical Equipment",
    "BHARATBIJLEE": "Capital Goods - Electrical Equipment",
    "VOLTAMP": "Capital Goods - Electrical Equipment",
    "HPL": "Capital Goods - Electrical Equipment",
    "GETD": "Capital Goods - Electrical Equipment",
    "SCHNEIDER": "Capital Goods - Electrical Equipment",
    "CUMMINSIND": "Capital Goods - Electrical Equipment",
    "THERMAX": "Capital Goods - Electrical Equipment",

    # Capital Goods - Non Electrical Equipment
    "LT": "Capital Goods-Non Electrical Equipment",
    "KALPATPOWR": "Capital Goods-Non Electrical Equipment",
    "KEC": "Capital Goods-Non Electrical Equipment",
    "HGINFRA": "Capital Goods-Non Electrical Equipment",
    "TATAPROJECT": "Capital Goods-Non Electrical Equipment",
    "GRINFRA": "Capital Goods-Non Electrical Equipment",
    "KNRCON": "Capital Goods-Non Electrical Equipment",

    # Castings, Forgings & Fastners
    "BHARATFORG-CF": "Castings, Forgings & Fastners",
    "ALOKINDS": "Castings, Forgings & Fastners",
    "MINDACORP": "Castings, Forgings & Fastners",
    "GRINDWELL": "Castings, Forgings & Fastners",
    "SANDHAR": "Castings, Forgings & Fastners",

    # Cement
    "ULTRACEMCO": "Cement", "AMBUJACEM": "Cement", "DALBHARAT": "Cement",
    "JKCEMENT": "Cement", "GRASIM": "Cement", "ACC": "Cement",
    "INDIACEM": "Cement", "BIRLACORPN": "Cement", "SHREECEM": "Cement",

    # Cement - Products
    "EVERESTIND": "Cement - Products", "HIL": "Cement - Products",
    "RAMCOCEM": "Cement - Products",

    # Ceramic Products
    "CERA": "Ceramic Products", "KAJARIACER": "Ceramic Products",
    "MURUDCERA": "Ceramic Products", "ORIENTBELL": "Ceramic Products",
    "SOMANYCERA": "Ceramic Products",

    # Chemicals
    "SRF": "Chemicals", "PIDILITIND": "Chemicals", "DEEPAKNTR": "Chemicals",
    "AARTIIND": "Chemicals", "ATUL": "Chemicals",
    "GUJFLUORO": "Chemicals", "NAVINFLUOR": "Chemicals",
    "VINATIORGA": "Chemicals", "TATACHEM": "Chemicals",
    "ASTRAL": "Chemicals", "CHEMPLASTS": "Chemicals",
    "TATVA": "Chemicals", "GALAXYSURF": "Chemicals",
    "FINEORG": "Chemicals", "BAYERCROP": "Chemicals",
    "COROMANDEL": "Chemicals", "CHAMBLFERT": "Chemicals",

    # Computer Education
    "NIITLTD": "Computer Education", "CAREERP": "Computer Education",
    "CLSEL": "Computer Education", "MTEDUCARE": "Computer Education",
    "APTECHT": "Computer Education", "ONMOBILE": "Computer Education",

    # Construction
    "LT": "Construction", "GRINFRA": "Construction", "KNRCON": "Construction",
    "HGINFRA": "Construction", "IRB": "Construction",
    "DBL": "Construction", "PNCINFRA": "Construction",

    # Consumer Durables
    "HAVELLS": "Consumer Durables", "VOLTAS": "Consumer Durables",
    "WHIRLPOOL": "Consumer Durables", "CROMPTON": "Consumer Durables",
    "VGUARD": "Consumer Durables", "BAJAJELEC": "Consumer Durables",
    "TTKPT": "Consumer Durables", "HAWKINCOOK": "Consumer Durables",
    "TITAN": "Consumer Durables", "PAGEIND": "Consumer Durables",
    "BERGEPAINT": "Consumer Durables",

    # Credit Rating Agencies
    "ICRA": "Credit Rating Agencies", "CRISIL": "Credit Rating Agencies",
    "CARE": "Credit Rating Agencies",

    # Crude Oil & Natural Gas
    "ONGC": "Crude Oil & Natural Gas", "OIL": "Crude Oil & Natural Gas",
    "HPCL": "Crude Oil & Natural Gas", "BPCL": "Crude Oil & Natural Gas",
    "IOC": "Crude Oil & Natural Gas", "RELIANCE": "Crude Oil & Natural Gas",
    "GAIL": "Crude Oil & Natural Gas", "PETRONET": "Crude Oil & Natural Gas",
    "MGL": "Crude Oil & Natural Gas", "IGL": "Crude Oil & Natural Gas",
    "GSPL": "Crude Oil & Natural Gas",

    # Diamond, Gems and Jewellery
    "TITAN": "Diamond, Gems and Jewellery", "KALYANKJIL": "Diamond, Gems and Jewellery",
    "PCJEWELLER": "Diamond, Gems and Jewellery", "RAJESHEXPO": "Diamond, Gems and Jewellery",
    "GITANJALI": "Diamond, Gems and Jewellery",

    # Diversified
    "GODREJAGRO": "Diversified", "MAWANASUG": "Diversified",
    "KESORAMIND": "Diversified", "GODREJIND": "Diversified",
    "BIRLATYRES": "Diversified",

    # Dry cells
    "EVEREADY": "Dry cells", "GPPL": "Dry cells",

    # E-Commerce / App based Aggregator
    "ZOMATO": "E-Commerce/App based Aggregator",
    "NYKAA": "E-Commerce/App based Aggregator",
    "PAYTM": "E-Commerce/App based Aggregator",
    "POLICYBZR": "E-Commerce/App based Aggregator",
    "INDIAMART": "E-Commerce/App based Aggregator",
    "CARTRADE": "E-Commerce/App based Aggregator",
    "JUSTDIAL": "E-Commerce/App based Aggregator",

    # Edible Oil
    "PATANJALI": "Edible Oil", "ADANIGREEN": "Edible Oil",
    "MARICO": "Edible Oil", "EMAMILTD": "Edible Oil",
    "BAJAJHCARE": "Edible Oil",

    # Education
    "NAUKRI": "Education", "NIITLTD": "Education",
    "CAREERP": "Education", "CLSEL": "Education",
    "MTEDUCARE": "Education", "APTECHT": "Education",
    "PACE": "Education", "ZEELEARN": "Education",

    # Electronics
    "DIXON": "Electronics", "KAYNES": "Electronics", "SYRMA": "Electronics",
    "ELIN": "Electronics", "CENTUM": "Electronics",
    "AMBER": "Electronics", "PGEL": "Electronics",
    "VVDN": "Electronics", "MICROPRO": "Electronics",

    # Engineering
    "LT": "Engineering", "THERMAX": "Engineering", "HONEYWELL": "Engineering",
    "GRINDWELL": "Engineering", "CARBORUNIV": "Engineering",
    "SCHAEFFLER": "Engineering", "TIMKEN": "Engineering",
    "SKFINDIA": "Engineering", "NRBBEARING": "Engineering",
    "GRAUWEIL": "Engineering",

    # Entertainment
    "ZEEL": "Entertainment", "SUNTV": "Entertainment",
    "PVRINOX": "Entertainment", "DISHTV": "Entertainment",
    "NETWORK18": "Entertainment", "TVTODAY": "Entertainment",
    "TIPSMUSIC": "Entertainment", "HATHWAY": "Entertainment",
    "BALAJITELE": "Entertainment",

    # ETF
    "GOLDBEES": "ETF", "NIFTYBEES": "ETF", "BANKBEES": "ETF",
    "JUNIORBEES": "ETF", "LIQUIDBEES": "ETF",

    # Ferro Alloys
    "MAITHANALL": "Ferro Alloys", "TINPLATE": "Ferro Alloys",
    "SHAKTIPUMP": "Ferro Alloys", "SARDAEN": "Ferro Alloys",

    # Fertilizers
    "CHAMBLFERT": "Fertilizers", "COROMANDEL": "Fertilizers",
    "GSFC": "Fertilizers", "RCF": "Fertilizers", "NFL": "Fertilizers",
    "ZUARI": "Fertilizers", "MADRASFERT": "Fertilizers",

    # Finance
    "BAJFINANCE": "Finance", "CHOLAFIN": "Finance",
    "SHRIRAMFIN": "Finance", "M&MFIN": "Finance",
    "MANAPPURAM": "Finance", "MUTHOOTFIN": "Finance",
    "IIFL": "Finance", "MAS": "Finance",
    "POONAWALLA": "Finance", "FIVE": "Finance",
    "SPANDANA": "Finance", "BAJAJHFL": "Finance",
    "LICHSGFIN": "Finance", "PNBHOUSING": "Finance",
    "CANFINHOME": "Finance", "AADHARHFC": "Finance",
    "AAVAS": "Finance", "HOMEFIRST": "Finance",
    "SBICARD": "Finance", "ICICIPRULI": "Insurance",

    # Financial Services
    "BSE": "Financial Services", "MCX": "Financial Services",
    "CDSL": "Financial Services", "KFINTECH": "Financial Services",
    "HDFCAMC": "Financial Services", "NAM-INDIA": "Financial Services",
    "ICICIAMC": "Financial Services", "UTIAMC": "Financial Services",
    "NSDL": "Financial Services", "ANGELONE": "Financial Services",
    "IIFLSEC": "Financial Services", "5PAISA": "Financial Services",
    "PRUDENT": "Financial Services", "MOTILALOFS": "Financial Services",
    "EDELWEISS": "Financial Services", "BAJAJFINSV": "Financial Services",
    "CHOLAFIN": "Financial Services", "SHRIRAMFIN": "Financial Services",
    "M&MFIN": "Financial Services",

    # FMCG
    "HINDUNILVR": "FMCG", "ITC": "FMCG", "BRITANNIA": "FMCG",
    "NESTLEIND": "FMCG", "MARICO": "FMCG", "GODREJCP": "FMCG",
    "DABUR": "FMCG", "COLPAL": "FMCG", "EMAMILTD": "FMCG",
    "JYL": "FMCG", "BAJAJCON": "FMCG", "TATACONSUM": "FMCG",
    "UBL": "FMCG", "RADICO": "FMCG", "VSTIND": "FMCG",
    "GODREJAGRO": "FMCG",

    # Gas Distribution
    "GAIL": "Gas Distribution", "PETRONET": "Gas Distribution",
    "MGL": "Gas Distribution", "IGL": "Gas Distribution",
    "GSPL": "Gas Distribution",

    # Glass & Glass Products
    "ASAHIINDIA": "Glass & Glass Products", "SAINTGOBAIN": "Glass & Glass Products",
    "HNG": "Glass & Glass Products", "PIRAMAL": "Glass & Glass Products",

    # Healthcare
    "APOLLOHOSP": "Healthcare", "MAXHEALTH": "Healthcare",
    "DRLAL": "Healthcare", "METROPOLIS": "Healthcare",
    "FORTIS": "Healthcare", "NH": "Healthcare",
    "SHALBY": "Healthcare", "KIMS": "Healthcare",
    "SYNGENE": "Healthcare", "DIVISLAB": "Healthcare",
    "LUPIN": "Healthcare", "MANKIND": "Healthcare",
    "ZYDUSLIFE": "Healthcare", "TORNTPHARM": "Healthcare",
    "AUROPHARMA": "Healthcare", "GLENMARK": "Healthcare",
    "ALKEM": "Healthcare", "IPCALAB": "Healthcare",
    "BIOCON": "Healthcare", "JBCHEPHARM": "Healthcare",
    "NATCOPHARM": "Healthcare", "GRANULES": "Healthcare",

    # Hotels & Restaurants
    "INDHOTELS": "Hotels & Restaurants", "EIHOTEL": "Hotels & Restaurants",
    "CHALET": "Hotels & Restaurants", "LEMONTREE": "Hotels & Restaurants",
    "JUBLFOOD": "Hotels & Restaurants", "DEVYANI": "Hotels & Restaurants",
    "SAPPHIRE": "Hotels & Restaurants", "BARBEQUE": "Hotels & Restaurants",
    "IRCTC": "Hotels & Restaurants", "MAHINDRAHOL": "Hotels & Restaurants",
    "EIH": "Hotels & Restaurants",

    # Infrastructure Developers & Operators
    "DLF": "Infrastructure Developers & Operators",
    "LODHA": "Infrastructure Developers & Operators",
    "PRESTIGE": "Infrastructure Developers & Operators",
    "MAHLIFE": "Infrastructure Developers & Operators",
    "BRIGADE": "Infrastructure Developers & Operators",
    "SOBHA": "Infrastructure Developers & Operators",
    "OBEROIRLTY": "Infrastructure Developers & Operators",
    "GODREJPROP": "Infrastructure Developers & Operators",
    "BRIGADE": "Infrastructure Developers & Operators",
    "KOLTEPATIL": "Infrastructure Developers & Operators",
    "SUNTECK": "Infrastructure Developers & Operators",
    "ANANTRAJ": "Infrastructure Developers & Operators",
    "KALPATPOWR": "Infrastructure Developers & Operators",
    "PURVA": "Infrastructure Developers & Operators",
    "SIGNATURE": "Infrastructure Developers & Operators",
    "HUBTOWN": "Infrastructure Developers & Operators",
    "PHOENIXLTD": "Infrastructure Developers & Operators",

    # Infrastructure Investment Trusts
    "EMBASSY": "Infrastructure Investment Trusts",
    "MINDSPACE": "Infrastructure Investment Trusts",
    "BROOKFIELD": "Infrastructure Investment Trusts",
    "IRBINVIT": "Infrastructure Investment Trusts",
    "INDUSTOWER": "Infrastructure Investment Trusts",

    # Insurance
    "LICI": "Insurance", "SBILIFE": "Insurance", "HDFCLIFE": "Insurance",
    "ICICIPRULI": "Insurance", "MAXFININCO": "Insurance", "BAJAJFINSV": "Insurance",
    "ICICILOMB": "Insurance", "HDFCAMC": "Insurance",
    "NIACL": "Insurance", "GICRE": "Insurance",
    "STARHEALTH": "Insurance", "GODIGIT": "Insurance",

    # IT - Hardware
    "TATACHEM": "IT - Hardware", "WIPRO": "IT - Hardware",
    "HCLTECH": "IT - Hardware", "KPITTECH": "IT - Hardware",
    "TATATECH": "IT - Hardware", "HEXAWARE": "IT - Hardware",
    "ZENSARTECH": "IT - Hardware", "CYIENT": "IT - Hardware",
    "BIRLASOFT": "IT - Hardware", "MASTEK": "IT - Hardware",
    "INTELLECT": "IT - Hardware", "SONATSOFTW": "IT - Hardware",
    "RAMSARUP": "IT - Hardware",

    # IT - Software
    "TCS": "IT - Software", "INFY": "IT - Software",
    "TECHM": "IT - Software", "LTIM": "IT - Software",
    "MPHASIS": "IT - Software", "PERSISTENT": "IT - Software",
    "COFORGE": "IT - Software", "TATAELXSI": "IT - Software",
    "OFSS": "IT - Software", "LTTS": "IT - Software",
    "ECLERX": "IT - Software", "IKSHEALTH": "IT - Software",
    "NAUKRI": "IT - Software", "POLICYBZR": "IT - Software",

    # Leather
    "MIRZINTL": "Leather", "SUPERHOUSE": "Leather",
    "BATAINDIA": "Leather", "RELAXO": "Leather",
    "LIBERTSHOE": "Leather", "METALFORGE": "Leather",

    # Logistics
    "DELHIVERY": "Logistics", "MAHLOG": "Logistics",
    "TCI": "Logistics", "GESHIP": "Logistics",
    "BLUEDART": "Logistics", "DTDC": "Logistics",
    "MAHINDRA": "Logistics", "TCIEXP": "Logistics",

    # Marine Port & Services
    "ADANIPORTS": "Marine Port & Services", "JSWINFRA": "Marine Port & Services",
    "GPPL": "Marine Port & Services", "SCI": "Marine Port & Services",

    # Media - Print/Television/Radio
    "ZEEL": "Media - Print/Television/Radio", "SUNTV": "Media - Print/Television/Radio",
    "PVRINOX": "Media - Print/Television/Radio", "DISHTV": "Media - Print/Television/Radio",
    "NETWORK18": "Media - Print/Television/Radio", "TVTODAY": "Media - Print/Television/Radio",
    "TIPSMUSIC": "Media - Print/Television/Radio", "HATHWAY": "Media - Print/Television/Radio",
    "JAGRAN": "Media - Print/Television/Radio", "DBCORP": "Media - Print/Television/Radio",
    "SURYAROSNI": "Media - Print/Television/Radio",

    # Mining & Mineral products
    "COALINDIA": "Mining & Mineral products", "VEDL": "Mining & Mineral products",
    "NMDC": "Mining & Mineral products", "HINDZINC": "Mining & Mineral products",
    "NATIONALUM": "Mining & Mineral products", "HINDCOPPER": "Mining & Mineral products",
    "MOIL": "Mining & Mineral products", "APLAPOLLO": "Mining & Mineral products",
    "WELCORP": "Mining & Mineral products", "JINDALSAW": "Mining & Mineral products",

    # Miscellaneous
    "QUESS": "Miscellaneous", "SIS": "Miscellaneous",
    "TEAMLEASE": "Miscellaneous", "FIRST": "Miscellaneous",
    "FLEXITUFF": "Miscellaneous", "SHAH": "Miscellaneous",

    # Non Ferrous Metals
    "HINDALCO": "Non Ferrous Metals", "VEDL": "Non Ferrous Metals",
    "NATIONALUM": "Non Ferrous Metals", "HINDCOPPER": "Non Ferrous Metals",
    "GRAVITA": "Non Ferrous Metals", "STERLITE": "Non Ferrous Metals",

    # Oil Drill/Allied
    "OIL": "Oil Drill/Allied", "ONGC": "Oil Drill/Allied",
    "HPCL": "Oil Drill/Allied", "BPCL": "Oil Drill/Allied",
    "IOC": "Oil Drill/Allied",

    # Online Media
    "ZOMATO": "Online Media", "NAUKRI": "Online Media",
    "INDIAMART": "Online Media", "CARTRADE": "Online Media",
    "JUSTDIAL": "Online Media", "INFOEDGE": "Online Media",

    # Packaging
    "UFLEX": "Packaging", "JINDALPOLY": "Packaging",
    "COSMOFILMS": "Packaging", "EPL": "Packaging",
    "MANJUSHREE": "Packaging", "POLYPLEX": "Packaging",

    # Paints/Varnish
    "ASIANPAINT": "Paints/Varnish", "BERGEPAINT": "Paints/Varnish",
    "KANSAINER": "Paints/Varnish", "INDIGOPNTS": "Paints/Varnish",
    "AKZOINDIA": "Paints/Varnish", "SHALIMAR": "Paints/Varnish",

    # Paper
    "JKPAPER": "Paper", "CENTURYPPR": "Paper",
    "TNPL": "Paper", "WSTCSTPAPR": "Paper",
    "ANDHRAPAP": "Paper", "ORIENTPPR": "Paper",

    # Petrochemicals
    "RELIANCE": "Petrochemicals", "HINDPETRO": "Petrochemicals",
    "GAIL": "Petrochemicals", "MRPL": "Petrochemicals",
    "CHENNPETRO": "Petrochemicals", "DCMSHRIRAM": "Petrochemicals",

    # Pharmaceuticals
    "SUNPHARMA": "Pharmaceuticals", "CIPLA": "Pharmaceuticals",
    "DRREDDY": "Pharmaceuticals", "DIVISLAB": "Pharmaceuticals",
    "LUPIN": "Pharmaceuticals", "MANKIND": "Pharmaceuticals",
    "ZYDUSLIFE": "Pharmaceuticals", "TORNTPHARM": "Pharmaceuticals",
    "AUROPHARMA": "Pharmaceuticals", "GLENMARK": "Pharmaceuticals",
    "ALKEM": "Pharmaceuticals", "IPCALAB": "Pharmaceuticals",
    "BIOCON": "Pharmaceuticals", "JBCHEPHARM": "Pharmaceuticals",
    "NATCOPHARM": "Pharmaceuticals", "GRANULES": "Pharmaceuticals",
    "AJANTPHARM": "Pharmaceuticals", "LAURUSLABS": "Pharmaceuticals",
    "STRIDES": "Pharmaceuticals", "SYNGENE": "Pharmaceuticals",

    # Plantation & Plantation Products
    "TATACONSUM": "Plantation & Plantation Products",
    "MCLEODRUSS": "Plantation & Plantation Products",
    "ROSSELL": "Plantation & Plantation Products",
    "WABAG": "Plantation & Plantation Products",
    "KOLTEPATIL": "Plantation & Plantation Products",
    "CCL": "Plantation & Plantation Products",

    # Plastic products
    "FINPIPE": "Plastic products", "SUPREMEIND": "Plastic products",
    "ASTRAL": "Plastic products", "PRINCEPIPE": "Plastic products",
    "JAYAGROGN": "Plastic products",

    # Plywood Boards/Laminates
    "GREENLAM": "Plywood Boards/Laminates", "CENTURYPLY": "Plywood Boards/Laminates",
    "GREENPANEL": "Plywood Boards/Laminates",

    # Power Generation & Distribution
    "TATAPOWER": "Power Generation & Distribution",
    "ADANIGREEN": "Power Generation & Distribution",
    "ADANIPOWER": "Power Generation & Distribution",
    "JSWENERGY": "Power Generation & Distribution",
    "TORNTPOWER": "Power Generation & Distribution",
    "NHPC": "Power Generation & Distribution",
    "SJVN": "Power Generation & Distribution",
    "IEX": "Power Generation & Distribution",
    "PTC": "Power Generation & Distribution",
    "ADANIPORTS": "Power Generation & Distribution",
    "POWERGRID": "Power Generation & Distribution",

    # Power Infrastructure
    "POWERGRID": "Power Infrastructure", "ADANIPOWER": "Power Infrastructure",
    "SIEMENS": "Power Infrastructure", "ABB": "Power Infrastructure",
    "CGPOWER": "Power Infrastructure", "HPL": "Power Infrastructure",

    # Printing & Stationery
    "FLAIR": "Printing & Stationery", "DOMS": "Printing & Stationery",
    "KOKUYOCMLN": "Printing & Stationery",

    # Quick Service Restaurant
    "JUBLFOOD": "Quick Service Restaurant", "DEVYANI": "Quick Service Restaurant",
    "SAPPHIRE": "Quick Service Restaurant", "BARBEQUE": "Quick Service Restaurant",
    "BURGERKING": "Quick Service Restaurant", "WESTLIFE": "Quick Service Restaurant",
    "SPECIALITY": "Quick Service Restaurant",

    # Railways
    "RAILTEL": "Railways", "BEML": "Railways",
    "TEXMACO": "Railways", "TITAGARH": "Railways",
    "IRCTC": "Railways",

    # Readymade Garments/ Apparells
    "TRENT": "Readymade Garments/ Apparells", "PAGEIND": "Readymade Garments/ Apparells",
    "ABFRL": "Readymade Garments/ Apparells", "SHOPERSTOP": "Readymade Garments/ Apparells",
    "V2RETAIL": "Readymade Garments/ Apparells", "TRENT": "Readymade Garments/ Apparells",
    "KPRMILL": "Readymade Garments/ Apparells",
    "INDOCOUNT": "Readymade Garments/ Apparells", "TRIDENT": "Readymade Garments/ Apparells",
    "WELSPUN": "Readymade Garments/ Apparells", "VARDHMAN": "Readymade Garments/ Apparells",

    # Real Estate Investment Trusts
    "EMBASSY": "Real Estate Investment Trusts",
    "MINDSPACE": "Real Estate Investment Trusts",
    "BROOKFIELD": "Real Estate Investment Trusts",
    "NXST": "Real Estate Investment Trusts",

    # Realty
    "DLF": "Realty", "LODHA": "Realty", "PRESTIGE": "Realty",
    "MAHLIFE": "Realty", "BRIGADE": "Realty", "SOBHA": "Realty",
    "OBEROIRLTY": "Realty", "GODREJPROP": "Realty",
    "KOLTEPATIL": "Realty", "SUNTECK": "Realty",
    "ANANTRAJ": "Realty", "KALPATPOWR": "Realty",
    "PURVA": "Realty", "SIGNATURE": "Realty",
    "HUBTOWN": "Realty",

    # Refineries
    "RELIANCE": "Refineries", "IOC": "Refineries", "BPCL": "Refineries",
    "HPCL": "Refineries", "MRPL": "Refineries", "CHENNPETRO": "Refineries",

    # Refractories
    "IFGLREFRAC": "Refractories", "VESUVIUS": "Refractories",
    "RHI": "Refractories",

    # Retail
    "TRENT": "Retail", "DMART": "Retail", "ABFRL": "Retail",
    "SHOPERSTOP": "Retail", "V2RETAIL": "Retail", "BATAINDIA": "Retail",
    "RELAXO": "Retail", "VMART": "Retail",

    # Sanitaryware
    "CERA": "Sanitaryware", "KAJARIACER": "Sanitaryware",
    "HINDWARE": "Sanitaryware", "PARIWARE": "Sanitaryware",
    "VST": "Sanitaryware",

    # Ship Building
    "MAZDOCK": "Ship Building", "COCHINSHIP": "Ship Building",
    "GRSE": "Ship Building", "SCI": "Ship Building",

    # Shipping
    "SCI": "Shipping", "GESHIP": "Shipping", "MAERSK": "Shipping",
    "INOXWIND": "Shipping",

    # Steel
    "TATASTEEL": "Steel", "JSWSTEEL": "Steel", "JINDALSTEL": "Steel",
    "SAIL": "Steel", "JSPL": "Steel", "APLAPOLLO": "Steel",
    "WELCORP": "Steel", "JINDALSAW": "Steel", "BHUSHAN": "Steel",
    "NMDC": "Steel", "VEDL": "Steel", "HINDZINC": "Steel",

    # Stock/Commodity Brokers
    "MOTILALOFS": "Stock/Commodity Brokers", "IIFLSEC": "Stock/Commodity Brokers",
    "ANGELONE": "Stock/Commodity Brokers", "5PAISA": "Stock/Commodity Brokers",
    "PRUDENT": "Stock/Commodity Brokers", "EDELWEISS": "Stock/Commodity Brokers",
    "GEOJITFSL": "Stock/Commodity Brokers", "SHAREINDIA": "Stock/Commodity Brokers",

    # Sugar
    "BALRAMCHIN": "Sugar", "EIDPARRY": "Sugar",
    "TRIVENI": "Sugar", "DALMIASUG": "Sugar",
    "RENUKA": "Sugar", "UGARSUGAR": "Sugar",
    "DHAMPUR": "Sugar", "MAWANASUG": "Sugar",

    # Telecom-Handsets/Mobile
    "MICROMAX": "Telecom-Handsets/Mobile", "LAVA": "Telecom-Handsets/Mobile",
    "KARBONN": "Telecom-Handsets/Mobile",

    # Telecomm Equipment & Infra Services
    "HFCL": "Telecomm Equipment & Infra Services",
    "STERLITE": "Telecomm Equipment & Infra Services",
    "TEJASNET": "Telecomm Equipment & Infra Services",
    "ITI": "Telecomm Equipment & Infra Services",
    "VINDHYATEL": "Telecomm Equipment & Infra Services",
    "BHARTIHEX": "Telecomm Equipment & Infra Services",

    # Telecomm-Service
    "BHARTIARTL": "Telecomm-Service", "RELIANCE": "Telecomm-Service",
    "INDUSTOWER": "Telecomm-Service", "TATACOMM": "Telecomm-Service",
    "MTNL": "Telecomm-Service", "VODAFONE": "Telecomm-Service",

    # Textiles
    "TRIDENT": "Textiles", "WELSPUN": "Textiles",
    "VARDHMAN": "Textiles", "KPRMILL": "Textiles",
    "INDOCOUNT": "Textiles", "CENTENKA": "Textiles",
    "FILATEX": "Textiles", "ALOKTEXT": "Textiles",
    "SPENTEX": "Textiles", "KEDIA": "Textiles",

    # Tobacco Products
    "ITC": "Tobacco Products", "GODFRYPHLP": "Tobacco Products",
    "VSTIND": "Tobacco Products",

    # Trading
    "MMTC": "Trading", "STC": "Trading",
    "PTC": "Trading", "BBNPPOWER": "Trading",
    "RECLTD": "Trading",

    # Tyres
    "MRF": "Tyres", "APOLLOTYRE": "Tyres",
    "CEAT": "Tyres", "BALKRISIND": "Tyres",
    "JKTYRE": "Tyres", "BIRLATYRES": "Tyres",
}

# Default sector-to-subindustry fallback if symbol not in mapping
SECTOR_DEFAULT = {
    "Aerospace & Defence": "Aerospace & Defence",
    "Auto Components": "Auto Ancillaries",
    "Banking & Financials": "Banks",
    "Capital Goods & Engineering": "Capital Goods-Non Electrical Equipment",
    "Capital Markets": "Stock/Commodity Brokers",
    "Cement": "Cement",
    "Chemicals": "Chemicals",
    "Consumer Durables": "Consumer Durables",
    "Consumer Internet": "E-Commerce/App based Aggregator",
    "Electronics / EMS": "Electronics",
    "Financial Services": "Financial Services",
    "Fintech": "Finance",
    "FMCG": "FMCG",
    "Healthcare Services": "Healthcare",
    "Insurance": "Insurance",
    "IT Services": "IT - Software",
    "Logistics": "Logistics",
    "Logistics & Infrastructure": "Logistics",
    "Metals & Mining": "Mining & Mineral products",
    "Mining": "Mining & Mineral products",
    "Oil & Gas": "Crude Oil & Natural Gas",
    "Pharmaceuticals": "Pharmaceuticals",
    "Power": "Power Generation & Distribution",
    "Realty": "Realty",
    "Retail": "Retail",
    "Telecom": "Telecomm-Service",
    "Travel & Tourism": "Hotels & Restaurants",
}

rows = json.loads(PATH.read_text(encoding="utf-8"))
updated = 0
for r in rows:
    sym = r.get("symbol", "")
    if sym in SUBSECTOR:
        r["subIndustry"] = SUBSECTOR[sym]
        updated += 1
    else:
        r["subIndustry"] = SECTOR_DEFAULT.get(r.get("sector", ""), "Miscellaneous")
PATH.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Updated {updated}/{len(rows)} tickers with explicit subIndustry; rest fell back to sector default")

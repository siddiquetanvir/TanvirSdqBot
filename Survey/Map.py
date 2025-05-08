import requests, re, pandas as pd, numpy as np, math
from IPython.display import display, Markdown
from collections import defaultdict
from itertools import permutations
from concurrent.futures import ThreadPoolExecutor, as_completed
import plotly.express as px

EVENT_MAP = {
    'wlf': 'Folklore',
    'wle': 'Earth',
    'wlm': 'Monuments',
    'wlb': 'Bangla'
}

COUNTRY_MAP = {
    'bd': 'Bangladesh',
    'in': 'India',
    'pk': 'Pakistan',
    'np': 'Nepal',
    'ng': 'Nigeria',
    'za': 'South Africa',
    'ke': 'Kenya',
    'id': 'Indonesia',
    'ph': 'Philippines',
    'my': 'Malaysia',
    'tr': 'Turkey',
    'eg': 'Egypt',
    'ua': 'Ukraine',
    'ru': 'Russia',
    'de': 'Germany',
    'it': 'Italy',
    'fr': 'France',
    'uk': 'United Kingdom',
    'us': 'United States',
    'ca': 'Canada',
    'nl': 'Netherlands',
    'pl': 'Poland',
    'br': 'Brazil',
    'mx': 'Mexico',
    'es': 'Spain',
    'pt': 'Portugal',
    'be': 'Belgium',
    'at': 'Austria',
    'ch': 'Switzerland',
    'no': 'Norway',
    'se': 'Sweden',
    'fi': 'Finland',
    'ar': 'Argentina',
    'cl': 'Chile',
    'co': 'Colombia',
    'jp': 'Japan',
    'kr': 'South Korea',
    'sg': 'Singapore',
    'th': 'Thailand',
    'vn': 'Vietnam'
}

def get_participants(code):
    try:
        code = re.sub(r'\s+', '', code).lower()
        event, cc, yr = re.match(r'(wlf|wle|wlm)([a-z]{0,2})(\d{2})', code).groups()
        category = f"Images_from_Wiki_Loves_{EVENT_MAP[event]}_{2000 + int(yr)}"
        if cc:
            category += f"_in_{COUNTRY_MAP.get(cc, '')}"
        participants, url = set(), "https://commons.wikimedia.org/w/api.php"
        params = {
            "action": "query",
            "generator": "categorymembers",
            "gcmtitle": f"Category:{category}",
            "gcmnamespace": 6,
            "gcmtype": "file",
            "prop": "imageinfo",
            "iiprop": "user",
            "format": "json",
            "gcmlimit": "max"
        }
        while True:
            data = requests.get(url, params=params, timeout=15).json()
            pages = data.get('query', {}).get('pages', {})
            participants.update(p['imageinfo'][0]['user'] for p in pages.values() if p.get('imageinfo'))
            if 'continue' in data and 'gcmcontinue' in data['continue']:
                params['gcmcontinue'] = data['continue']['gcmcontinue']
            else:
                break
        return participants
    except Exception as e:
        display(Markdown(f"**Error processing {code}:** {str(e)}"))
        return set()

def fetch_all_participants(codes):
    results = {}
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_code = {executor.submit(get_participants, code): code for code in codes}
        for future in as_completed(future_to_code):
            code = future_to_code[future]
            results[code] = future.result()
    return results

def compute_average_retention(codes):
    valid = [c for c in (re.sub(r'\s+', '', cd).lower() for cd in codes)
             if re.match(r'(wlf|wle|wlm)([a-z]{0,2})(\d{2})', c)]
    part_dict = fetch_all_participants(valid)
    country_events = defaultdict(dict)
    for code in valid:
        event, cc, yr = re.match(r'(wlf|wle|wlm)([a-z]{0,2})(\d{2})', code).groups()
        if cc in COUNTRY_MAP:
            country_events[cc][code] = part_dict.get(code, set())
    avg_retention = {}
    for country_code, events in country_events.items():
        if len(events) < 3:  # Only include countries with at least one event in each of the 3 main events
            continue
        # Check that each of the 3 categories is represented
        categories = set()
        for code in events.keys():
            cat, _, _ = re.match(r'(wlf|wle|wlm)([a-z]{0,2})(\d{2})', code).groups()
            categories.add(cat)
        if not all(c in categories for c in ['wlf','wle','wlm']):
            continue
        pairs = list(permutations(events.keys(), 2))
        percentages = []
        for source, target in pairs:
            source_users = events[source]
            if not source_users:
                continue
            overlap = len(source_users & events[target])
            retention = (overlap / len(source_users)) * 100
            percentages.append(retention)
        if percentages:
            avg_retention[COUNTRY_MAP[country_code]] = np.mean(percentages)
    return avg_retention

# Optimized updated input list (space separated)
input_codes = """wlfbd21 wlfbd22 wlfbd23 wlfbd24  
wlebd21 wlebd22 wlebd23 wlebd24  
wlmbd21 wlmbd22 wlmbd23 wlmbd24  

wlfin21 wlfin22 wlfin23 wlfin24  
wlein21 wlein22 wlein23 wlein24  
wlmin21 wlmin22 wlmin23 wlmin24  

wlfde21 wlfde22 wlfde23 wlfde24  
wlede21 wlede22 wlede23 wlede24  
wlmde21 wlmde22 wlmde23 wlmde24  

wlfit21 wlfit22 wlfit23 wlfit24  
wleit21 wleit22 wleit23 wleit24  
wlmit21 wlmit22 wlmit23 wlmit24  

wlffr21 wlffr22 wlffr23 wlffr24  
wlefr21 wlefr22 wlefr23 wlefr24  
wlmfr21 wlmfr22 wlmfr23 wlmfr24  

wlfus21 wlfus22 wlfus23 wlfus24  
wleus21 wleus22 wleus23 wleus24  
wlmus21 wlmus22 wlmus23 wlmus24  

wlfca21 wlfca22 wlfca23 wlfca24  
wleca21 wleca22 wleca23 wleca24  
wlmca21 wlmca22 wlmca23 wlmca24  

wlfuk21 wlfuk22 wlfuk23 wlfuk24  
wleuk21 wleuk22 wleuk23 wleuk24  
wlmuk21 wlmuk22 wlmuk23 wlmuk24  

wlfnl21 wlfnl22 wlfnl23 wlfnl24  
wlenl21 wlenl22 wlenl23 wlenl24  
wlmnl21 wlmnl22 wlmnl23 wlmnl24  

wlfpl21 wlfpl22 wlfpl23 wlfpl24  
wlepl21 wlepl22 wlepl23 wlepl24  
wlmpl21 wlmpl22 wlmpl23 wlmpl24  

wlfbr21 wlfbr22 wlfbr23 wlfbr24  
wlebr21 wlebr22 wlebr23 wlebr24  
wlmbr21 wlmbr22 wlmbr23 wlmbr24  

wlfmx21 wlfmx22 wlfmx23 wlfmx24  
wlemx21 wlemx22 wlemx23 wlemx24  
wlmmx21 wlmmx22 wlmmx23 wlmmx24  

wlfes21 wlfes22 wlfes23 wlfes24  
wlees21 wlees22 wlees23 wlees24  
wlmes21 wlmes22 wlmes23 wlmes24  

wlfpt21 wlfpt22 wlfpt23 wlfpt24  
wlept21 wlept22 wlept23 wlept24  
wlmpt21 wlmpt22 wlmpt23 wlmpt24  

wlfpk21 wlfpk22 wlfpk23 wlfpk24  
wlepk21 wlepk22 wlepk23 wlepk24  
wlmpk21 wlmpk22 wlmpk23 wlmpk24  

wlfnp21 wlfnp22 wlfnp23 wlfnp24  
wlenp21 wlenp22 wlenp23 wlenp24  
wlmnp21 wlmnp22 wlmnp23 wlmnp24  

wlfng21 wlfng22 wlfng23 wlfng24  
wleng21 wleng22 wleng23 wleng24  
wlmng21 wlmng22 wlmng23 wlmng24  

wlfza21 wlfza22 wlfza23 wlfza24  
wleza21 wleza22 wleza23 wleza24  
wlmza21 wlmza22 wlmza23 wlmza24  

wlfke21 wlfke22 wlfke23 wlfke24  
wleke21 wleke22 wleke23 wleke24  
wlmke21 wlmke22 wlmke23 wlmke24  

wlfid21 wlfid22 wlfid23 wlfid24  
wleid21 wleid22 wleid23 wleid24  
wlmid21 wlmid22 wlmid23 wlmid24  

wlfph21 wlfph22 wlfph23 wlfph24  
wleph21 wleph22 wleph23 wleph24  
wlmph21 wlmph22 wlmph23 wlmph24  

wlfmy21 wlfmy22 wlfmy23 wlfmy24  
wlemy21 wlemy22 wlemy23 wlemy24  
wlmmy21 wlmmy22 wlmmy23 wlmmy24  

wlftr21 wlftr22 wlftr23 wlftr24  
wletr21 wletr22 wletr23 wletr24  
wlmtr21 wlmtr22 wlmtr23 wlmtr24  

wlfeg21 wlfeg22 wlfeg23 wlfeg24  
wleeg21 wleeg22 wleeg23 wleeg24  
wlmeg21 wlmeg22 wlmeg23 wlmeg24  

wlfua21 wlfua22 wlfua23 wlfua24  
wleua21 wleua22 wleua23 wleua24  
wlmua21 wlmua22 wlmua23 wlmua24  

wlfru21 wlfru22 wlfru23 wlfru24  
wleru21 wleru22 wleru23 wleru24  
wlmru21 wlmru22 wlmru23 wlmru24  

wlfch21 wlfch22 wlfch23 wlfch24  
wlech21 wlech22 wlech23 wlech24  
wlmch21 wlmch22 wlmch23 wlmch24  

wlfse21 wlfse22 wlfse23 wlfse24  
wlese21 wlese22 wlese23 wlese24  
wlmse21 wlmse22 wlmse23 wlmse24  

wlfno21 wlfno22 wlfno23 wlfno24  
wleno21 wleno22 wleno23 wleno24  
wlmno21 wlmno22 wlmno23 wlmno24  

wlffi21 wlffi22 wlffi23 wlffi24  
wlefi21 wlefi22 wlefi23 wlefi24  
wlmfi21 wlmfi22 wlmfi23 wlmfi24  

wlfbe21 wlfbe22 wlfbe23 wlfbe24  
wlebe21 wlebe22 wlebe23 wlebe24  
wlmbe21 wlmbe22 wlmbe23 wlmbe24  

wlfat21 wlfat22 wlfat23 wlfat24  
wleat21 wleat22 wleat23 wleat24  
wlmat21 wlmat22 wlmat23 wlmat24  

wlfar21 wlfar22 wlfar23 wlfar24  
wlear21 wlear22 wlear23 wlear24  
wlmar21 wlmar22 wlmar23 wlmar24  

wlfcl21 wlfcl22 wlfcl23 wlfcl24  
wlecl21 wlecl22 wlecl23 wlecl24  
wlmcl21 wlmcl22 wlmcl23 wlmcl24  

wlfco21 wlfco22 wlfco23 wlfco24  
wleco21 wleco22 wleco23 wleco24  
wlmco21 wlmco22 wlmco23 wlmco24
"""

# Split the updated input list into codes
codes = input_codes.split()
avg_retention_dict = compute_average_retention(codes)
if avg_retention_dict:
    df = pd.DataFrame(list(avg_retention_dict.items()), columns=["Country", "AverageRetention"])
    fig = px.choropleth(
        df,
        locations="Country",
        locationmode="country names",
        color="AverageRetention",
        color_continuous_scale="Viridis",
        title="Average Retention by Country",
        labels={"AverageRetention": "Avg Retention (%)"}
    )
    fig.show()
else:
    display(Markdown("**No valid multi-event country data found**"))

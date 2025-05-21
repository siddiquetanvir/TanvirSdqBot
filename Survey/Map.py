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
    'bd': 'Bangladesh', 'in': 'India', 'pk': 'Pakistan', 'np': 'Nepal',
    'ng': 'Nigeria', 'ke': 'Kenya', 'id': 'Indonesia',
    'ph': 'Philippines', 'my': 'Malaysia', 'tr': 'Turkey', 'eg': 'Egypt',
    'ua': 'Ukraine', 'ru': 'Russia', 'de': 'Germany', 'it': 'Italy',
    'fr': 'France', 'uk': 'United Kingdom', 'us': 'United States', 'ca': 'Canada',
    'nl': 'Netherlands', 'pl': 'Poland', 'br': 'Brazil', 'mx': 'Mexico',
    'es': 'Spain', 'pt': 'Portugal', 'be': 'Belgium', 'at': 'Austria',
    'ch': 'Switzerland', 'no': 'Norway', 'se': 'Sweden', 'fi': 'Finland',
    'ar': 'Argentina', 'co': 'Colombia', 'jp': 'Japan',
    'kr': 'South Korea', 'sg': 'Singapore', 'th': 'Thailand', 'vn': 'Vietnam'
}

def get_participants(code):
    try:
        code = re.sub(r'\s+', '', code).lower()
        match = re.match(r'(wlf|wle|wlm|wlb)([a-z]{0,2})(\d{2})', code)
        if not match:
            return set()
        event, cc, yr = match.groups()
        category = f"Images_from_Wiki_Loves_{EVENT_MAP.get(event, '')}_{2000 + int(yr)}"
        if cc and cc in COUNTRY_MAP:
            category += f"_in_{COUNTRY_MAP[cc]}"
        participants, url = set(), "https://commons.wikimedia.org/w/api.php"
        params = {
            "action": "query", "generator": "categorymembers",
            "gcmtitle": f"Category:{category}", "gcmnamespace": 6,
            "gcmtype": "file", "prop": "imageinfo", "iiprop": "user",
            "format": "json", "gcmlimit": "max"
        }
        while True:
            data = requests.get(url, params=params, timeout=15).json()
            pages = data.get('query', {}).get('pages', {})
            participants.update(p['imageinfo'][0]['user'] 
                for p in pages.values() if p.get('imageinfo'))
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
             if re.match(r'(wlf|wle|wlm|wlb)([a-z]{0,2})(\d{2})', c)]
    
    if not valid:
        display(Markdown("**No valid event codes found**"))
        return {}

    part_dict = fetch_all_participants(valid)
    country_events = defaultdict(dict)

    for code in valid:
        match = re.match(r'(wlf|wle|wlm|wlb)([a-z]{0,2})(\d{2})', code)
        if not match:
            continue
        event, cc, yr = match.groups()
        if cc in COUNTRY_MAP:
            country_events[cc][code] = part_dict.get(code, set())

    avg_retention = {}
    for country_code, events in country_events.items():
        if len(events) < 3:
            continue
        categories = set()
        for code in events.keys():
            cat = re.match(r'(wlf|wle|wlm|wlb)', code).group(1)
            categories.add(cat)
        if not {'wlf','wle','wlm'}.issubset(categories):
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
            avg_retention[COUNTRY_MAP[country_code]] = np.nanmean(percentages)

    return avg_retention

# User interaction and visualization
user_input = input("Enter event codes (space-separated): ").strip()
codes = user_input.split()

if not codes:
    display(Markdown("**No input provided**"))
else:
    retention_data = compute_average_retention(codes)
    
    if retention_data:
        df = pd.DataFrame(list(retention_data.items()), 
                         columns=["Country", "AverageRetention"])
        
        # Dynamic color scaling based on data distribution
        max_retention = df['AverageRetention'].max()
        min_retention = df['AverageRetention'].min()
        color_max = max(15, max_retention * 1.1)  # Ensures minimum range up to 15%
        color_min = max(0, min_retention * 0.9)

        fig = px.choropleth(
            df,
            locations="Country",
            locationmode="country names",
            color="AverageRetention",
            color_continuous_scale="Reds",
            range_color=(color_min, color_max),
            title="Average Participant Retention Between Events",
            labels={"AverageRetention": "Retention Rate (%)"},
            hover_name="Country",
            hover_data={"AverageRetention": ":.1f%"},
            projection="natural earth"
        )

        fig.update_layout(
            geo=dict(showcountries=True, countrycolor="lightgray"),
            coloraxis_colorbar=dict(
                title="Retention %",
                ticksuffix="%",
                dtick=5 if color_max <= 30 else 10
            ),
            margin={"r":0,"t":40,"l":0,"b":0}
        )
        fig.show()
    else:
        display(Markdown("**No countries with complete event trilogy found**"))
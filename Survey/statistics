import requests, re, numpy as np, pandas as pd
from IPython.display import display, Markdown

COUNTRY_MAP = {
    'bd': 'Bangladesh',
    'in': 'India',
    'de': 'Germany',
    'it': 'Italy',
    'fr': 'France',
    'us': 'United_States',
    'ca': 'Canada',
    'uk': 'United_Kingdom',
    'nl': 'Netherlands',
    'pl': 'Poland',
    'br': 'Brazil',
    'mx': 'Mexico',
    'es': 'Spain',
    'pt': 'Portugal',
    'pk': 'Pakistan',
    'np': 'Nepal',
    'ng': 'Nigeria',
    'za': 'South_Africa',
    'ke': 'Kenya',
    'id': 'Indonesia',
    'ph': 'Philippines',
    'my': 'Malaysia',
    'tr': 'Turkey',
    'eg': 'Egypt',
    'ua': 'Ukraine',
    'ru': 'Russia',
    'ch': 'Switzerland',
    'se': 'Sweden',
    'no': 'Norway',
    'fi': 'Finland',
    'be': 'Belgium',
    'at': 'Austria',
    'ar': 'Argentina',
    'cl': 'Chile',
    'co': 'Colombia'
}

EVENT_MAP = {
    'wlf': 'Folklore',
    'wle': 'Earth',
    'wlm': 'Monuments'
}

def get_participants(code):
    try:
        cd = re.sub(r'\s+', '', code).lower()
        event, cc, yr = re.match(r'(wlf|wle|wlm)([a-z]{2})(\d{2})', cd).groups()
        category = f"Images_from_Wiki_Loves_{EVENT_MAP[event]}_{2000+int(yr)}"
        country = COUNTRY_MAP.get(cc, '')
        if country:
            category += f"_in_{country}"
        parts = set()
        url = "https://commons.wikimedia.org/w/api.php"
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
            parts.update(p['imageinfo'][0]['user'] for p in pages.values() if p.get('imageinfo'))
            if 'continue' in data and 'gcmcontinue' in data['continue']:
                params['gcmcontinue'] = data['continue']['gcmcontinue']
            else:
                break
        return parts
    except Exception as e:
        display(Markdown(f"**Error processing {code}:** {str(e)}"))
        return set()

def generate_country_trend_tables(codes):
    groups = {}
    for cd in codes:
        cd_clean = re.sub(r'\s+', '', cd).lower()
        m = re.match(r'(wlf|wle|wlm)([a-z]{2})(\d{2})', cd_clean)
        if m:
            comp, country, yr = m.groups()
            groups.setdefault(country, {}).setdefault(comp, []).append((cd_clean, int(yr)))
    participant_cache = {}
    country_tables = {}
    for country, comp_dict in groups.items():
        rows = []
        for comp, events in comp_dict.items():
            events.sort(key=lambda x: x[1])
            if len(events) < 2:
                row = {
                    "Competition": EVENT_MAP[comp],
                    "Event Count": len(events),
                    "Min Retention": "N/A",
                    "25th Percentile": "N/A",
                    "Median": "N/A",
                    "75th Percentile": "N/A",
                    "Max Retention": "N/A",
                    "Event Pairs": "Only one event"
                }
                rows.append(row)
            else:
                retentions = []
                event_pairs = []
                for i in range(len(events) - 1):
                    code_prev, yr_prev = events[i]
                    code_next, yr_next = events[i+1]
                    if code_prev not in participant_cache:
                        participant_cache[code_prev] = get_participants(code_prev)
                    if code_next not in participant_cache:
                        participant_cache[code_next] = get_participants(code_next)
                    parts_prev = participant_cache[code_prev]
                    parts_next = participant_cache[code_next]
                    if parts_prev:
                        rate = len(parts_prev & parts_next) / len(parts_prev) * 100
                        retentions.append(rate)
                        event_pairs.append(f"{yr_prev}-{yr_next}")
                if retentions:
                    row = {
                        "Competition": EVENT_MAP[comp],
                        "Event Count": len(events),
                        "Min Retention": np.min(retentions),
                        "25th Percentile": np.percentile(retentions, 25),
                        "Median": np.median(retentions),
                        "75th Percentile": np.percentile(retentions, 75),
                        "Max Retention": np.max(retentions),
                        "Event Pairs": ", ".join(event_pairs)
                    }
                    rows.append(row)
        if rows:
            df = pd.DataFrame(rows)
            country_name = COUNTRY_MAP.get(country, country)
            country_tables[country_name] = df
    return country_tables

codes = input("Enter event codes: ").split()
tables = generate_country_trend_tables(codes)
if tables:
    for country, df in tables.items():
        display(Markdown(f"### Trend Table for {country}"))
        display(df)
else:
    display(Markdown("**No sufficient data to generate trend tables.**"))

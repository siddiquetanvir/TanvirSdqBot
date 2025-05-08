import requests, re, pandas as pd, numpy as np
from IPython.display import display, Markdown
from collections import defaultdict
from itertools import permutations
import math

EVENT_MAP = {'wlf': 'Folklore', 'wle': 'Earth', 'wlm': 'Monuments', 'wlb': 'Bangla'}
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

def get_participants(code):
    try:
        code = re.sub(r'\s+', '', code).lower()
        event, cc, yr = re.match(r'(wlf|wle|wlm)([a-z]{0,2})(\d{2})', code).groups()
        category = f"Images_from_Wiki_Loves_{EVENT_MAP[event]}_{2000 + int(yr)}"
        if cc:
            category += f"_in_{COUNTRY_MAP.get(cc, '')}"
        participants, url, params = set(), "https://commons.wikimedia.org/w/api.php", {
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

def find_peak_and_deviation(values):
    if not values:
        return (0.0, 0.0)
    freq = {}
    for v in values:
        r = round(v, 1)
        freq[r] = freq.get(r, 0) + 1
    peak_rounded = max(freq, key=freq.get)
    diffs = [(v - peak_rounded)**2 for v in values]
    var = sum(diffs) / (len(diffs) - 1) if len(diffs) > 1 else 0
    return (peak_rounded, math.sqrt(var))

def analyze_country_overlaps(codes):
    valid = [c for c in (re.sub(r'\s+', '', cd).lower() for cd in codes) if re.match(r'(wlb|wlf|wle|wlm)([a-z]{0,2})(\d{2})', c)]
    country_events = defaultdict(dict)
    for code in valid:
        event, cc, yr = re.match(r'(wlb|wlf|wle|wlm)([a-z]{0,2})(\d{2})', code).groups()
        if cc in COUNTRY_MAP:
            country_events[cc][code] = get_participants(code)
    trend_reports = []
    for country_code, events in country_events.items():
        if len(events) < 2:
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
        if not percentages:
            continue
        peak_val, peak_dev = find_peak_and_deviation(percentages)
        range_lower = max(0, peak_val - peak_dev)
        range_upper = min(100, peak_val + peak_dev)
        trend_reports.append({
            'Country': COUNTRY_MAP[country_code],
            'Events': len(events),
            'Max': f"{np.max(percentages):.1f}%",
            'Median': f"{np.median(percentages):.1f}%",
            'Average': f"{np.mean(percentages):.1f}%",
            'Peak Range': f"{range_lower:.1f}% - {range_upper:.1f}%",
            'Std Dev': f"{np.std(percentages, ddof=1):.1f}%"
        })
    if trend_reports:
        df = pd.DataFrame(trend_reports)
        df.index = df.index + 1
        display(Markdown("**Cross-Event Retention Analysis**"))
        display(df[['Country', 'Events', 'Max', 'Median', 'Average', 'Peak Range', 'Std Dev']])
    else:
        display(Markdown("**No valid multi-event country data found**"))

analyze_country_overlaps(input("Enter event codes (space-separated): ").split())

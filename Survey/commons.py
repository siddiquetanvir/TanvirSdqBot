import requests
import re
from IPython.display import display, Markdown

EVENT_MAP = {
    'wlf': 'Folklore',
    'wle': 'Earth',
    'wlm': 'Monuments',
    'wlb': 'Bangla'
}

COUNTRY_MAP = {
    'bd': 'Bangladesh',
    'in': 'India', 'pk': 'Pakistan', 'np': 'Nepal', 'ng': 'Nigeria',
    'za': 'South Africa', 'ke': 'Kenya', 'id': 'Indonesia', 'ph': 'Philippines',
    'my': 'Malaysia', 'tr': 'Turkey', 'eg': 'Egypt', 'ua': 'Ukraine',
    'ru': 'Russia', 'de': 'Germany', 'it': 'Italy', 'fr': 'France',
    'uk': 'United Kingdom', 'us': 'United States', 'ca': 'Canada',
    'nl': 'Netherlands', 'pl': 'Poland', 'br': 'Brazil', 'mx': 'Mexico',
    'es': 'Spain', 'pt': 'Portugal', 'be': 'Belgium', 'at': 'Austria',
    'ch': 'Switzerland', 'no': 'Norway', 'se': 'Sweden', 'fi': 'Finland',
    'ar': 'Argentina', 'cl': 'Chile', 'co': 'Colombia', 'jp': 'Japan',
    'kr': 'South Korea', 'sg': 'Singapore', 'th': 'Thailand', 'vn': 'Vietnam'
}

def get_participants(code):
    try:
        code = re.sub(r'\s+', '', code).lower()
        match = re.match(r'(wlf|wle|wlm|wlb)([a-z]{0,2})(\d{2})', code)
        event, cc, yr = match.groups()
        category = f"Images_from_Wiki_Loves_{EVENT_MAP[event]}_{2000 + int(yr)}"
        if cc in COUNTRY_MAP:
            category += f"_in_{COUNTRY_MAP[cc]}"
        participants = set()
        url = "https://commons.wikimedia.org/w/api.php"
        params = {
            "action": "query", "generator": "categorymembers",
            "gcmtitle": f"Category:{category}", "gcmnamespace": 6,
            "gcmtype": "file", "prop": "imageinfo", "iiprop": "user",
            "format": "json", "gcmlimit": "max"
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
import requests, re, pandas as pd, numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display, Markdown

EVENT_MAP = {
    'wlf': 'Folklore', 'wle': 'Earth',
    'wlm': 'Monuments', 'wlb': 'Bangla'
}

COUNTRY_MAP = {
    'bd': 'Bangladesh', 'in': 'India', 'pk': 'Pakistan', 'np': 'Nepal',
    'ng': 'Nigeria', 'ke': 'Kenya', 'id': 'Indonesia',
    'ph': 'Philippines', 'my': 'Malaysia', 'tr': 'Turkey', 'eg': 'Egypt',
    'ua': 'Ukraine', 'ru': 'Russia', 'de': 'Germany', 'it': 'Italy',
    'fr': 'France', 'uk': 'UK', 'us': 'USA', 'ca': 'Canada', 'nl': 'Netherlands',
    'pl': 'Poland', 'br': 'Brazil', 'mx': 'Mexico', 'es': 'Spain', 'pt': 'Portugal',
    'be': 'Belgium', 'at': 'Austria', 'ch': 'Switzerland', 'no': 'Norway',
    'se': 'Sweden', 'fi': 'Finland', 'ar': 'Argentina',
    'co': 'Colombia', 'jp': 'Japan', 'kr': 'Korea', 'sg': 'Singapore',
    'th': 'Thailand', 'vn': 'Vietnam'
}

def get_participants(code):
    try:
        code = re.sub(r'\s+', '', code).lower()
        match = re.match(r'(wlb|wlf|wle|wlm)([a-z]{0,2})(\d{2})', code)
        event, cc, yr = match.groups()
        category = f"Images_from_Wiki_Loves_{EVENT_MAP[event]}_{2000+int(yr)}"
        if cc and cc in COUNTRY_MAP:
            category += f"_in_{COUNTRY_MAP[cc]}"
        parts, url, params = set(), "https://commons.wikimedia.org/w/api.php", {
            "action": "query", "generator": "categorymembers", 
            "gcmtitle": f"Category:{category}", "gcmnamespace": 6, 
            "gcmtype": "file", "prop": "imageinfo", "iiprop": "user",
            "format": "json", "gcmlimit": "max"
        }
        while True:
            data = requests.get(url, params=params, timeout=15).json()
            if 'query' in data and 'pages' in data['query']:
                parts.update(p['imageinfo'][0]['user'] 
                           for p in data['query']['pages'].values() 
                           if 'imageinfo' in p)
            if 'continue' in data and 'gcmcontinue' in data['continue']:
                params['gcmcontinue'] = data['continue']['gcmcontinue']
            else: break
        return parts
    except Exception as e:
        display(Markdown(f"**Error processing {code}:** {str(e)}"))
        return set()

def create_matrices(codes):
    valid = [re.sub(r'\s+', '', cd).lower() for cd in codes 
            if re.match(r'(wlb|wlf|wle|wlm)([a-z]{0,2})(\d{2})', cd)]
    
    if len(valid) < 2:
        return display(Markdown("**Need ≥2 valid codes**"))
    
    participants = {code: get_participants(code) for code in valid}
    codes = [f"{cd[:3]}{cd[3:5]}{cd[5:]}" for cd in valid]
    
    # Percentage Matrix
    perc_data = []
    for i, (code, parts) in enumerate(participants.items()):
        row = []
        for j in range(len(valid)):
            if i == j:
                row.append(np.nan)  
            else:
                total = len(parts)
                overlap = len(parts & participants[valid[j]])
                row.append((overlap / total * 100) if total > 0 else np.nan)
        perc_data.append(row)
    
    perc_df = pd.DataFrame(perc_data, index=codes, columns=codes)
    
    # Heatmap Visualization
    plt.figure(figsize=(14, 10))
    sns.heatmap(
        perc_df, 
        annot=True, 
        fmt=".1f", 
        cmap='Reds', 
        linewidths=.5, 
        annot_kws={'size': 8},
        cbar_kws={'label': 'Retention Percentage (%)'},
        mask=perc_df.isnull()  
    )
    plt.title('Participant Retention Matrix', pad=20, fontsize=14)
    plt.xticks(rotation=45, ha='right', fontsize=9)
    plt.yticks(rotation=0, fontsize=9)
    plt.tight_layout()
    plt.savefig('retention_matrix_bd.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Display styled matrix
    display(Markdown("### Retention Percentage Matrix"))
    display(perc_df.style.format("{:.1f}%", na_rep="-")
              .background_gradient(cmap='Reds', axis=None)
              .set_table_styles([{
                  'selector': 'td',
                  'props': [('min-width', '100px')]
              }]))

create_matrices(input("Enter event codes (space-separated): ").split())
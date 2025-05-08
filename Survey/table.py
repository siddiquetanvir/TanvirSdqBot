from commons import get_participants, COUNTRY_MAP, EVENT_MAP
import re
import pandas as pd
import numpy as np
from IPython.display import display, Markdown

def generate_country_trend_tables(codes):
    groups = {}
    for cd in codes:
        cd_clean = re.sub(r'\s+', '', cd).lower()
        m = re.match(r'(wlf|wle|wlm)([a-z]{2})(\d{2})', cd_clean)
        if m:
            comp, country, yr = m.groups()
            groups.setdefault(country, {}).setdefault(comp, []).append((cd_clean, int(yr)))
    
    country_tables = {}
    for country, comp_dict in groups.items():
        rows = []
        for comp, events in comp_dict.items():
            events.sort(key=lambda x: x[1])
            if len(events) < 2:
                rows.append({
                    "Competition": EVENT_MAP[comp],
                    "Event Count": len(events),
                    "Min": "N/A",
                    "Median": "N/A",
                    "Max": "N/A",
                    "Event Pairs": "Insufficient data"
                })
                continue
                
            retentions = []
            event_pairs = []
            for i in range(len(events)-1):
                prev = get_participants(events[i][0])
                next_ = get_participants(events[i+1][0])
                if prev:
                    rate = len(prev & next_) / len(prev) * 100
                    retentions.append(rate)
                    event_pairs.append(f"{events[i][1]}-{events[i+1][1]}")
            
            if retentions:
                rows.append({
                    "Competition": EVENT_MAP[comp],
                    "Event Count": len(events),
                    "Min": f"{np.min(retentions):.1f}%",
                    "Median": f"{np.median(retentions):.1f}%",
                    "Max": f"{np.max(retentions):.1f}%",
                    "Event Pairs": ", ".join(event_pairs)
                })
        
        if rows:
            country_name = COUNTRY_MAP.get(country, country.upper())
            country_tables[country_name] = pd.DataFrame(rows)
    
    return country_tables

if __name__ == "__main__":
    codes = input("Enter event codes: ").split()
    tables = generate_country_trend_tables(codes)
    for country, df in tables.items():
        display(Markdown(f"### {country} Trends"))
        display(df.style.format({'Min': '{:.1f}%', 'Median': '{:.1f}%', 'Max': '{:.1f}%'}))
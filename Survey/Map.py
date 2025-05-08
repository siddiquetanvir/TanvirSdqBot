from commons import get_participants, COUNTRY_MAP
import re
import numpy as np
import pandas as pd
import plotly.express as px
from itertools import permutations
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from IPython.display import display, Markdown

def compute_average_retention(codes):
    valid = [c for c in (re.sub(r'\s+', '', cd).lower() for cd in codes) 
             if re.match(r'(wlf|wle|wlm|wlb)([a-z]{0,2})(\d{2})', c)]
    
    part_dict = {}
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_code = {executor.submit(get_participants, code): code for code in valid}
        for future in as_completed(future_to_code):
            part_dict[future_to_code[future]] = future.result()

    country_events = defaultdict(dict)
    for code, participants in part_dict.items():
        event, cc, yr = re.match(r'(wlf|wle|wlm|wlb)([a-z]{0,2})(\d{2})', code).groups()
        if cc in COUNTRY_MAP:
            country_events[cc][code] = participants

    avg_retention = {}
    for country_code, events in country_events.items():
        if len(events) < 3: continue
        categories = {re.match(r'(wlf|wle|wlm|wlb)', code).group(1) for code in events}
        if not {'wlf','wle','wlm'}.issubset(categories): continue
        
        pairs = list(permutations(events.keys(), 2))
        percentages = []
        for src, tgt in pairs:
            if events[src]:
                overlap = len(events[src] & events[tgt])
                percentages.append((overlap / len(events[src])) * 100)
        
        if percentages:
            avg_retention[COUNTRY_MAP[country_code]] = np.mean(percentages)
    
    return avg_retention

def generate_retention_map(input_codes):
    codes = input_codes.split()
    avg_retention_dict = compute_average_retention(codes)
    
    if avg_retention_dict:
        df = pd.DataFrame(list(avg_retention_dict.items()), 
                         columns=["Country", "AverageRetention"])
        
        fig = px.choropleth(
            df,
            locations="Country",
            locationmode="country names",
            color="AverageRetention",
            color_continuous_scale="Viridis",
            title="Average Retention by Country",
            labels={"AverageRetention": "Avg Retention (%)"},
            range_color=(0, 100)
        )
        fig.update_layout(geo=dict(showframe=False, showcoastlines=False))
        fig.show()
    else:
        display(Markdown("**No valid multi-event country data found**"))

if __name__ == "__main__":
    input_codes = input("Enter event codes (space-separated): ")
    generate_retention_map(input_codes)
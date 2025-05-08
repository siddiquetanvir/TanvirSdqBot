from commons import get_participants, COUNTRY_MAP
import re
import pandas as pd
import numpy as np
import math
from IPython.display import display, Markdown

def analyze_country_overlaps(codes):
    valid = [c for c in (re.sub(r'\s+', '', cd).lower() for cd in codes)
             if re.match(r'(wlb|wlf|wle|wlm)([a-z]{0,2})(\d{2})', c)]
    
    country_events = defaultdict(dict)
    for code in valid:
        event, cc, yr = re.match(r'(wlb|wlf|wle|wlm)([a-z]{0,2})(\d{2})', code).groups()
        if cc in COUNTRY_MAP:
            country_events[cc][code] = get_participants(code)

    trend_reports = []
    for country_code, events in country_events.items():
        if len(events) < 2: continue
        
        pairs = list(permutations(events.keys(), 2))
        percentages = []
        for src, tgt in pairs:
            if events[src]:
                overlap = len(events[src] & events[tgt])
                percentages.append((overlap / len(events[src])) * 100)
        
        if percentages:
            peak = max(set([round(p, 1) for p in percentages]), key=lambda x: percentages.count(x))
            std = np.std(percentages)
            trend_reports.append({
                'Country': COUNTRY_MAP[country_code],
                'Events': len(events),
                'Max Retention': f"{max(percentages):.1f}%",
                'Median': f"{np.median(percentages):.1f}%",
                'Average': f"{np.mean(percentages):.1f}%",
                'Peak (±SD)': f"{peak:.1f}% ± {std:.1f}%"
            })

    if trend_reports:
        df = pd.DataFrame(trend_reports)
        display(Markdown("### Cross-Event Retention Analysis"))
        display(df)
    else:
        display(Markdown("**No valid data found**"))

if __name__ == "__main__":
    codes = input("Enter event codes: ").split()
    analyze_country_overlaps(codes)
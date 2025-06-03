import requests, re, pandas as pd, numpy as np
import matplotlib.pyplot as plt
from IPython.display import display, Markdown
from collections import defaultdict
from itertools import permutations
import math
from matplotlib import rcParams

EVENT_MAP = {'wlf': 'Folklore', 'wle': 'Earth', 'wlm': 'Monuments', 'wlb': 'Bangla'}
COUNTRY_MAP = {
    'bd': 'Bangladesh', 'in': 'India', 'de': 'Germany', 'it': 'Italy',
    'fr': 'France', 'us': 'United_States', 'ca': 'Canada', 'uk': 'United_Kingdom',
    'nl': 'Netherlands', 'pl': 'Poland', 'br': 'Brazil', 'mx': 'Mexico',
    'es': 'Spain', 'pt': 'Portugal', 'pk': 'Pakistan', 'np': 'Nepal',
    'ng': 'Nigeria', 'ke': 'Kenya', 'id': 'Indonesia',
    'ph': 'Philippines', 'my': 'Malaysia', 'tr': 'Turkey', 'eg': 'Egypt',
    'ua': 'Ukraine', 'ru': 'Russia', 'ch': 'Switzerland', 'se': 'Sweden',
    'no': 'Norway', 'fi': 'Finland', 'be': 'Belgium', 'at': 'Austria',
    'ar': 'Argentina', 'co': 'Colombia'
}

def get_participants_2(code):
    try:
        code = re.sub(r'\s+', '', code).lower()
        event, cc, yr = re.match(r'(wlf|wle|wlm)([a-z]{0,2})(\d{2})', code).groups()
        cat = f"Images_from_Wiki_Loves_{EVENT_MAP[event]}_{2000 + int(yr)}"
        if cc: cat += f"_in_{COUNTRY_MAP.get(cc, '')}"
        response = requests.get('https://ptools.toolforge.org/uploadersincat.php?category='+cat)
        for uincattxt in response.content.decode("UTF-8").split('fieldset'):
            if '<legend>List</legend>' in uincattxt: break
        splt = list(uincattxt.split('>'))
        users = set()

        for s in splt:
            if "User:" in s and "href" not in s:
                users.add(s.replace("User:","").replace("</a",""))
        return users
    except Exception as e:
        print(f"**Error processing {code}:** {str(e)}")
        return set()

def get_participants(code):
    try:
        code = re.sub(r'\s+', '', code).lower()
        event, cc, yr = re.match(r'(wlf|wle|wlm)([a-z]{0,2})(\d{2})', code).groups()
        category = f"Images_from_Wiki_Loves_{EVENT_MAP[event]}_{2000 + int(yr)}"
        if cc:
            category += f"_in_{COUNTRY_MAP.get(cc, '')}"
        participants, url, params = set(), "https://commons.wikimedia.org/w/api.php", {
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
            else: break
        return participants
    except Exception as e:
        display(Markdown(f"**Error processing {code}:** {str(e)}"))
        return set()

def find_peak_and_deviation(values):
    if not values: return (0.0, 0.0)
    freq = {}
    for v in values:
        r = round(v, 1)
        freq[r] = freq.get(r, 0) + 1
    peak_rounded = max(freq, key=freq.get)
    diffs = [(v - peak_rounded)**2 for v in values]
    var = sum(diffs) / (len(diffs) - 1) if len(diffs) > 1 else 0
    return (peak_rounded, math.sqrt(var))

def analyze_country_overlaps(codes):
    valid = [c for c in (re.sub(r'\s+', '', cd).lower() for cd in codes) 
            if re.match(r'(wlf|wle|wlm)([a-z]{0,2})(\d{2})', c)]
    
    country_events = defaultdict(dict)
    for code in valid:
        event, cc, yr = re.match(r'(wlf|wle|wlm)([a-z]{0,2})(\d{2})', code).groups()
        participants = get_participants_2(code)
        if cc in COUNTRY_MAP and participants:
            country_events[cc][code] = participants
            print(valid.index(code) + 1, code, len(participants))
    
    trend_reports = []
    for country_code, events in country_events.items():
        if len(events) < 2: continue
        
        pairs = list(permutations(events.keys(), 2))
        percentages = []
        for source, target in pairs:
            source_users = events[source]
            if not source_users: continue
            overlap = len(source_users & events[target])
            retention = (overlap / len(source_users)) * 100
            percentages.append(retention)
        
        if not percentages: continue
        
        peak_val, peak_dev = find_peak_and_deviation(percentages)
        range_lower = max(0, peak_val - peak_dev)
        range_upper = min(100, peak_val + peak_dev)
        
        IQR_range = f"{np.percentile(percentages, 75):.1f}% - {np.percentile(percentages, 25):.1f}%"

        trend_reports.append({
            'Country': COUNTRY_MAP[country_code],
            'Events': len(events),
            'Max': f"{np.max(percentages):.1f}%",
            'Median': f"{np.median(percentages):.1f}%",
            'Average': f"{np.mean(percentages):.1f}%",
            #'Peak Range': f"{range_lower:.1f}% - {range_upper:.1f}%",
            'IQR Range': f"{IQR_range}",
            'Std Dev': f"{np.std(percentages, ddof=1):.1f}%"
        })
    
    if trend_reports:
        df = pd.DataFrame(trend_reports)
        df.index = df.index + 1
        #save CSV
        df.to_csv(Filename+".csv",index=False)

        # Save high-res table image
        plt.figure(figsize=(12, 6), dpi=300)
        ax = plt.subplot(frame_on=False)
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)
        
        table = pd.plotting.table(ax, df, loc='center', cellLoc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1.2, 1.5)
        plt.tight_layout()
        plt.savefig(Filename+'.png', dpi=600, bbox_inches='tight')
        plt.close()
        
        # Display in notebook
        display(Markdown("**Cross-Event Retention Analysis**"))
        display(df[['Country', 'Events', 'Max', 'Median', 'Average', 'IQR Range', 'Std Dev']])
    else:
        display(Markdown("**No valid multi-event country data found**"))


Filename = input("Enter output file-title (default: 'retention_analysis_highres'): ") or "retention_analysis_highres"

#analyze_country_overlaps(input("Enter event codes (space-separated): ").split())


#Li = ['wlfbd20', 'wlfbd21', 'wlfbd22', 'wlfbd23', 'wlfbd24', 'wlfin20', 'wlfin21', 'wlfin22', 'wlfin23', 'wlfin24', 'wlfde20', 'wlfde21', 'wlfde22', 'wlfde23', 'wlfde24', 'wlfit20', 'wlfit21', 'wlfit22', 'wlfit23', 'wlfit24', 'wlffr20', 'wlffr21', 'wlffr22', 'wlffr23', 'wlffr24', 'wlfus20', 'wlfus21', 'wlfus22', 'wlfus23', 'wlfus24', 'wlfca20', 'wlfca21', 'wlfca22', 'wlfca23', 'wlfca24', 'wlfuk20', 'wlfuk21', 'wlfuk22', 'wlfuk23', 'wlfuk24', 'wlfnl20', 'wlfnl21', 'wlfnl22', 'wlfnl23', 'wlfnl24', 'wlfpl20', 'wlfpl21', 'wlfpl22', 'wlfpl23', 'wlfpl24', 'wlfbr20', 'wlfbr21', 'wlfbr22', 'wlfbr23', 'wlfbr24', 'wlfmx20', 'wlfmx21', 'wlfmx22', 'wlfmx23', 'wlfmx24', 'wlfes20', 'wlfes21', 'wlfes22', 'wlfes23', 'wlfes24', 'wlfpt20', 'wlfpt21', 'wlfpt22', 'wlfpt23', 'wlfpt24', 'wlfpk20', 'wlfpk21', 'wlfpk22', 'wlfpk23', 'wlfpk24', 'wlfnp20', 'wlfnp21', 'wlfnp22', 'wlfnp23', 'wlfnp24', 'wlfng20', 'wlfng21', 'wlfng22', 'wlfng23', 'wlfng24', 'wlfke20', 'wlfke21', 'wlfke22', 'wlfke23', 'wlfke24', 'wlfid20', 'wlfid21', 'wlfid22', 'wlfid23', 'wlfid24', 'wlfph20', 'wlfph21', 'wlfph22', 'wlfph23', 'wlfph24', 'wlfmy20', 'wlfmy21', 'wlfmy22', 'wlfmy23', 'wlfmy24', 'wlftr20', 'wlftr21', 'wlftr22', 'wlftr23', 'wlftr24', 'wlfeg20', 'wlfeg21', 'wlfeg22', 'wlfeg23', 'wlfeg24', 'wlfua20', 'wlfua21', 'wlfua22', 'wlfua23', 'wlfua24', 'wlfru20', 'wlfru21', 'wlfru22', 'wlfru23', 'wlfru24', 'wlfch20', 'wlfch21', 'wlfch22', 'wlfch23', 'wlfch24', 'wlfse20', 'wlfse21', 'wlfse22', 'wlfse23', 'wlfse24', 'wlfno20', 'wlfno21', 'wlfno22', 'wlfno23', 'wlfno24', 'wlffi20', 'wlffi21', 'wlffi22', 'wlffi23', 'wlffi24', 'wlfbe20', 'wlfbe21', 'wlfbe22', 'wlfbe23', 'wlfbe24', 'wlfat20', 'wlfat21', 'wlfat22', 'wlfat23', 'wlfat24', 'wlfar20', 'wlfar21', 'wlfar22', 'wlfar23', 'wlfar24', 'wlfco20', 'wlfco21', 'wlfco22', 'wlfco23', 'wlfco24', 'wlebd20', 'wlebd21', 'wlebd22', 'wlebd23', 'wlebd24', 'wlein20', 'wlein21', 'wlein22', 'wlein23', 'wlein24', 'wlede20', 'wlede21', 'wlede22', 'wlede23', 'wlede24', 'wleit20', 'wleit21', 'wleit22', 'wleit23', 'wleit24', 'wlefr20', 'wlefr21', 'wlefr22', 'wlefr23', 'wlefr24', 'wleus20', 'wleus21', 'wleus22', 'wleus23', 'wleus24', 'wleca20', 'wleca21', 'wleca22', 'wleca23', 'wleca24', 'wleuk20', 'wleuk21', 'wleuk22', 'wleuk23', 'wleuk24', 'wlenl20', 'wlenl21', 'wlenl22', 'wlenl23', 'wlenl24', 'wlepl20', 'wlepl21', 'wlepl22', 'wlepl23', 'wlepl24', 'wlebr20', 'wlebr21', 'wlebr22', 'wlebr23', 'wlebr24', 'wlemx20', 'wlemx21', 'wlemx22', 'wlemx23', 'wlemx24', 'wlees20', 'wlees21', 'wlees22', 'wlees23', 'wlees24', 'wlept20', 'wlept21', 'wlept22', 'wlept23', 'wlept24', 'wlepk20', 'wlepk21', 'wlepk22', 'wlepk23', 'wlepk24', 'wlenp20', 'wlenp21', 'wlenp22', 'wlenp23', 'wlenp24', 'wleng20', 'wleng21', 'wleng22', 'wleng23', 'wleng24', 'wleke20', 'wleke21', 'wleke22', 'wleke23', 'wleke24', 'wleid20', 'wleid21', 'wleid22', 'wleid23', 'wleid24', 'wleph20', 'wleph21', 'wleph22', 'wleph23', 'wleph24', 'wlemy20', 'wlemy21', 'wlemy22', 'wlemy23', 'wlemy24', 'wletr20', 'wletr21', 'wletr22', 'wletr23', 'wletr24', 'wleeg20', 'wleeg21', 'wleeg22', 'wleeg23', 'wleeg24', 'wleua20', 'wleua21', 'wleua22', 'wleua23', 'wleua24', 'wleru20', 'wleru21', 'wleru22', 'wleru23', 'wleru24', 'wlech20', 'wlech21', 'wlech22', 'wlech23', 'wlech24', 'wlese20', 'wlese21', 'wlese22', 'wlese23', 'wlese24', 'wleno20', 'wleno21', 'wleno22', 'wleno23', 'wleno24', 'wlefi20', 'wlefi21', 'wlefi22', 'wlefi23', 'wlefi24', 'wlebe20', 'wlebe21', 'wlebe22', 'wlebe23', 'wlebe24', 'wleat20', 'wleat21', 'wleat22', 'wleat23', 'wleat24', 'wlear20', 'wlear21', 'wlear22', 'wlear23', 'wlear24', 'wleco20', 'wleco21', 'wleco22', 'wleco23', 'wleco24', 'wlmbd20', 'wlmbd21', 'wlmbd22', 'wlmbd23', 'wlmbd24', 'wlmin20', 'wlmin21', 'wlmin22', 'wlmin23', 'wlmin24', 'wlmde20', 'wlmde21', 'wlmde22', 'wlmde23', 'wlmde24', 'wlmit20', 'wlmit21', 'wlmit22', 'wlmit23', 'wlmit24', 'wlmfr20', 'wlmfr21', 'wlmfr22', 'wlmfr23', 'wlmfr24', 'wlmus20', 'wlmus21', 'wlmus22', 'wlmus23', 'wlmus24', 'wlmca20', 'wlmca21', 'wlmca22', 'wlmca23', 'wlmca24', 'wlmuk20', 'wlmuk21', 'wlmuk22', 'wlmuk23', 'wlmuk24', 'wlmnl20', 'wlmnl21', 'wlmnl22', 'wlmnl23', 'wlmnl24', 'wlmpl20', 'wlmpl21', 'wlmpl22', 'wlmpl23', 'wlmpl24', 'wlmbr20', 'wlmbr21', 'wlmbr22', 'wlmbr23', 'wlmbr24', 'wlmmx20', 'wlmmx21', 'wlmmx22', 'wlmmx23', 'wlmmx24', 'wlmes20', 'wlmes21', 'wlmes22', 'wlmes23', 'wlmes24', 'wlmpt20', 'wlmpt21', 'wlmpt22', 'wlmpt23', 'wlmpt24', 'wlmpk20', 'wlmpk21', 'wlmpk22', 'wlmpk23', 'wlmpk24', 'wlmnp20', 'wlmnp21', 'wlmnp22', 'wlmnp23', 'wlmnp24', 'wlmng20', 'wlmng21', 'wlmng22', 'wlmng23', 'wlmng24', 'wlmke20', 'wlmke21', 'wlmke22', 'wlmke23', 'wlmke24', 'wlmid20', 'wlmid21', 'wlmid22', 'wlmid23', 'wlmid24', 'wlmph20', 'wlmph21', 'wlmph22', 'wlmph23', 'wlmph24', 'wlmmy20', 'wlmmy21', 'wlmmy22', 'wlmmy23', 'wlmmy24', 'wlmtr20', 'wlmtr21', 'wlmtr22', 'wlmtr23', 'wlmtr24', 'wlmeg20', 'wlmeg21', 'wlmeg22', 'wlmeg23', 'wlmeg24', 'wlmua20', 'wlmua21', 'wlmua22', 'wlmua23', 'wlmua24', 'wlmru20', 'wlmru21', 'wlmru22', 'wlmru23', 'wlmru24', 'wlmch20', 'wlmch21', 'wlmch22', 'wlmch23', 'wlmch24', 'wlmse20', 'wlmse21', 'wlmse22', 'wlmse23', 'wlmse24', 'wlmno20', 'wlmno21', 'wlmno22', 'wlmno23', 'wlmno24', 'wlmfi20', 'wlmfi21', 'wlmfi22', 'wlmfi23', 'wlmfi24', 'wlmbe20', 'wlmbe21', 'wlmbe22', 'wlmbe23', 'wlmbe24', 'wlmat20', 'wlmat21', 'wlmat22', 'wlmat23', 'wlmat24', 'wlmar20', 'wlmar21', 'wlmar22', 'wlmar23', 'wlmar24', 'wlmco20', 'wlmco21', 'wlmco22', 'wlmco23', 'wlmco24']
#Li = ['wlebd15', 'wlebd16', 'wlebd17', 'wlebd18', 'wlebd19', 'wlein15', 'wlein16', 'wlein17', 'wlein18', 'wlein19', 'wlede15', 'wlede16', 'wlede17', 'wlede18', 'wlede19', 'wleit15', 'wleit16', 'wleit17', 'wleit18', 'wleit19', 'wlefr15', 'wlefr16', 'wlefr17', 'wlefr18', 'wlefr19', 'wleus15', 'wleus16', 'wleus17', 'wleus18', 'wleus19', 'wleca15', 'wleca16', 'wleca17', 'wleca18', 'wleca19', 'wleuk15', 'wleuk16', 'wleuk17', 'wleuk18', 'wleuk19', 'wlenl15', 'wlenl16', 'wlenl17', 'wlenl18', 'wlenl19', 'wlepl15', 'wlepl16', 'wlepl17', 'wlepl18', 'wlepl19', 'wlebr15', 'wlebr16', 'wlebr17', 'wlebr18', 'wlebr19', 'wlemx15', 'wlemx16', 'wlemx17', 'wlemx18', 'wlemx19', 'wlees15', 'wlees16', 'wlees17', 'wlees18', 'wlees19', 'wlept15', 'wlept16', 'wlept17', 'wlept18', 'wlept19', 'wlepk15', 'wlepk16', 'wlepk17', 'wlepk18', 'wlepk19', 'wlenp15', 'wlenp16', 'wlenp17', 'wlenp18', 'wlenp19', 'wleng15', 'wleng16', 'wleng17', 'wleng18', 'wleng19', 'wleke15', 'wleke16', 'wleke17', 'wleke18', 'wleke19', 'wleid15', 'wleid16', 'wleid17', 'wleid18', 'wleid19', 'wleph15', 'wleph16', 'wleph17', 'wleph18', 'wleph19', 'wlemy15', 'wlemy16', 'wlemy17', 'wlemy18', 'wlemy19', 'wletr15', 'wletr16', 'wletr17', 'wletr18', 'wletr19', 'wleeg15', 'wleeg16', 'wleeg17', 'wleeg18', 'wleeg19', 'wleua15', 'wleua16', 'wleua17', 'wleua18', 'wleua19', 'wleru15', 'wleru16', 'wleru17', 'wleru18', 'wleru19', 'wlech15', 'wlech16', 'wlech17', 'wlech18', 'wlech19', 'wlese15', 'wlese16', 'wlese17', 'wlese18', 'wlese19', 'wleno15', 'wleno16', 'wleno17', 'wleno18', 'wleno19', 'wlefi15', 'wlefi16', 'wlefi17', 'wlefi18', 'wlefi19', 'wlebe15', 'wlebe16', 'wlebe17', 'wlebe18', 'wlebe19', 'wleat15', 'wleat16', 'wleat17', 'wleat18', 'wleat19', 'wlear15', 'wlear16', 'wlear17', 'wlear18', 'wlear19', 'wleco15', 'wleco16', 'wleco17', 'wleco18', 'wleco19', 'wlmbd15', 'wlmbd16', 'wlmbd17', 'wlmbd18', 'wlmbd19', 'wlmin15', 'wlmin16', 'wlmin17', 'wlmin18', 'wlmin19', 'wlmde15', 'wlmde16', 'wlmde17', 'wlmde18', 'wlmde19', 'wlmit15', 'wlmit16', 'wlmit17', 'wlmit18', 'wlmit19', 'wlmfr15', 'wlmfr16', 'wlmfr17', 'wlmfr18', 'wlmfr19', 'wlmus15', 'wlmus16', 'wlmus17', 'wlmus18', 'wlmus19', 'wlmca15', 'wlmca16', 'wlmca17', 'wlmca18', 'wlmca19', 'wlmuk15', 'wlmuk16', 'wlmuk17', 'wlmuk18', 'wlmuk19', 'wlmnl15', 'wlmnl16', 'wlmnl17', 'wlmnl18', 'wlmnl19', 'wlmpl15', 'wlmpl16', 'wlmpl17', 'wlmpl18', 'wlmpl19', 'wlmbr15', 'wlmbr16', 'wlmbr17', 'wlmbr18', 'wlmbr19', 'wlmmx15', 'wlmmx16', 'wlmmx17', 'wlmmx18', 'wlmmx19', 'wlmes15', 'wlmes16', 'wlmes17', 'wlmes18', 'wlmes19', 'wlmpt15', 'wlmpt16', 'wlmpt17', 'wlmpt18', 'wlmpt19', 'wlmpk15', 'wlmpk16', 'wlmpk17', 'wlmpk18', 'wlmpk19', 'wlmnp15', 'wlmnp16', 'wlmnp17', 'wlmnp18', 'wlmnp19', 'wlmng15', 'wlmng16', 'wlmng17', 'wlmng18', 'wlmng19', 'wlmke15', 'wlmke16', 'wlmke17', 'wlmke18', 'wlmke19', 'wlmid15', 'wlmid16', 'wlmid17', 'wlmid18', 'wlmid19', 'wlmph15', 'wlmph16', 'wlmph17', 'wlmph18', 'wlmph19', 'wlmmy15', 'wlmmy16', 'wlmmy17', 'wlmmy18', 'wlmmy19', 'wlmtr15', 'wlmtr16', 'wlmtr17', 'wlmtr18', 'wlmtr19', 'wlmeg15', 'wlmeg16', 'wlmeg17', 'wlmeg18', 'wlmeg19', 'wlmua15', 'wlmua16', 'wlmua17', 'wlmua18', 'wlmua19', 'wlmru15', 'wlmru16', 'wlmru17', 'wlmru18', 'wlmru19', 'wlmch15', 'wlmch16', 'wlmch17', 'wlmch18', 'wlmch19', 'wlmse15', 'wlmse16', 'wlmse17', 'wlmse18', 'wlmse19', 'wlmno15', 'wlmno16', 'wlmno17', 'wlmno18', 'wlmno19', 'wlmfi15', 'wlmfi16', 'wlmfi17', 'wlmfi18', 'wlmfi19', 'wlmbe15', 'wlmbe16', 'wlmbe17', 'wlmbe18', 'wlmbe19', 'wlmat15', 'wlmat16', 'wlmat17', 'wlmat18', 'wlmat19', 'wlmar15', 'wlmar16', 'wlmar17', 'wlmar18', 'wlmar19', 'wlmco15', 'wlmco16', 'wlmco17', 'wlmco18', 'wlmco19']
Li = ['wlfbd21', 'wlfbd22', 'wlfbd23', 'wlfbd24', 'wlfbd25', 'wlfin21', 'wlfin22', 'wlfin23', 'wlfin24', 'wlfin25', 'wlfde21', 'wlfde22', 'wlfde23', 'wlfde24', 'wlfde25', 'wlfit21', 'wlfit22', 'wlfit23', 'wlfit24', 'wlfit25', 'wlffr21', 'wlffr22', 'wlffr23', 'wlffr24', 'wlffr25', 'wlfus21', 'wlfus22', 'wlfus23', 'wlfus24', 'wlfus25', 'wlfca21', 'wlfca22', 'wlfca23', 'wlfca24', 'wlfca25', 'wlfuk21', 'wlfuk22', 'wlfuk23', 'wlfuk24', 'wlfuk25', 'wlfnl21', 'wlfnl22', 'wlfnl23', 'wlfnl24', 'wlfnl25', 'wlfpl21', 'wlfpl22', 'wlfpl23', 'wlfpl24', 'wlfpl25', 'wlfbr21', 'wlfbr22', 'wlfbr23', 'wlfbr24', 'wlfbr25', 'wlfmx21', 'wlfmx22', 'wlfmx23', 'wlfmx24', 'wlfmx25', 'wlfes21', 'wlfes22', 'wlfes23', 'wlfes24', 'wlfes25', 'wlfpt21', 'wlfpt22', 'wlfpt23', 'wlfpt24', 'wlfpt25', 'wlfpk21', 'wlfpk22', 'wlfpk23', 'wlfpk24', 'wlfpk25', 'wlfnp21', 'wlfnp22', 'wlfnp23', 'wlfnp24', 'wlfnp25', 'wlfng21', 'wlfng22', 'wlfng23', 'wlfng24', 'wlfng25', 'wlfke21', 'wlfke22', 'wlfke23', 'wlfke24', 'wlfke25', 'wlfid21', 'wlfid22', 'wlfid23', 'wlfid24', 'wlfid25', 'wlfph21', 'wlfph22', 'wlfph23', 'wlfph24', 'wlfph25', 'wlfmy21', 'wlfmy22', 'wlfmy23', 'wlfmy24', 'wlfmy25', 'wlftr21', 'wlftr22', 'wlftr23', 'wlftr24', 'wlftr25', 'wlfeg21', 'wlfeg22', 'wlfeg23', 'wlfeg24', 'wlfeg25', 'wlfua21', 'wlfua22', 'wlfua23', 'wlfua24', 'wlfua25', 'wlfru21', 'wlfru22', 'wlfru23', 'wlfru24', 'wlfru25', 'wlfch21', 'wlfch22', 'wlfch23', 'wlfch24', 'wlfch25', 'wlfse21', 'wlfse22', 'wlfse23', 'wlfse24', 'wlfse25', 'wlfno21', 'wlfno22', 'wlfno23', 'wlfno24', 'wlfno25', 'wlffi21', 'wlffi22', 'wlffi23', 'wlffi24', 'wlffi25', 'wlfbe21', 'wlfbe22', 'wlfbe23', 'wlfbe24', 'wlfbe25', 'wlfat21', 'wlfat22', 'wlfat23', 'wlfat24', 'wlfat25', 'wlfar21', 'wlfar22', 'wlfar23', 'wlfar24', 'wlfar25', 'wlfco21', 'wlfco22', 'wlfco23', 'wlfco24', 'wlfco25', 'wlebd21', 'wlebd22', 'wlebd23', 'wlebd24', 'wlein21', 'wlein22', 'wlein23', 'wlein24', 'wlede21', 'wlede22', 'wlede23', 'wlede24', 'wleit21', 'wleit22', 'wleit23', 'wleit24', 'wlefr21', 'wlefr22', 'wlefr23', 'wlefr24', 'wleus21', 'wleus22', 'wleus23', 'wleus24', 'wleca21', 'wleca22', 'wleca23', 'wleca24', 'wleuk21', 'wleuk22', 'wleuk23', 'wleuk24', 'wlenl21', 'wlenl22', 'wlenl23', 'wlenl24', 'wlepl21', 'wlepl22', 'wlepl23', 'wlepl24', 'wlebr21', 'wlebr22', 'wlebr23', 'wlebr24', 'wlemx21', 'wlemx22', 'wlemx23', 'wlemx24', 'wlees21', 'wlees22', 'wlees23', 'wlees24', 'wlept21', 'wlept22', 'wlept23', 'wlept24', 'wlepk21', 'wlepk22', 'wlepk23', 'wlepk24', 'wlenp21', 'wlenp22', 'wlenp23', 'wlenp24', 'wleng21', 'wleng22', 'wleng23', 'wleng24', 'wleke21', 'wleke22', 'wleke23', 'wleke24', 'wleid21', 'wleid22', 'wleid23', 'wleid24', 'wleph21', 'wleph22', 'wleph23', 'wleph24', 'wlemy21', 'wlemy22', 'wlemy23', 'wlemy24', 'wletr21', 'wletr22', 'wletr23', 'wletr24', 'wleeg21', 'wleeg22', 'wleeg23', 'wleeg24', 'wleua21', 'wleua22', 'wleua23', 'wleua24', 'wleru21', 'wleru22', 'wleru23', 'wleru24', 'wlech21', 'wlech22', 'wlech23', 'wlech24', 'wlese21', 'wlese22', 'wlese23', 'wlese24', 'wleno21', 'wleno22', 'wleno23', 'wleno24', 'wlefi21', 'wlefi22', 'wlefi23', 'wlefi24', 'wlebe21', 'wlebe22', 'wlebe23', 'wlebe24', 'wleat21', 'wleat22', 'wleat23', 'wleat24', 'wlear21', 'wlear22', 'wlear23', 'wlear24', 'wleco21', 'wleco22', 'wleco23', 'wleco24', 'wlmbd21', 'wlmbd22', 'wlmbd23', 'wlmbd24', 'wlmin21', 'wlmin22', 'wlmin23', 'wlmin24', 'wlmde21', 'wlmde22', 'wlmde23', 'wlmde24', 'wlmit21', 'wlmit22', 'wlmit23', 'wlmit24', 'wlmfr21', 'wlmfr22', 'wlmfr23', 'wlmfr24', 'wlmus21', 'wlmus22', 'wlmus23', 'wlmus24', 'wlmca21', 'wlmca22', 'wlmca23', 'wlmca24', 'wlmuk21', 'wlmuk22', 'wlmuk23', 'wlmuk24', 'wlmnl21', 'wlmnl22', 'wlmnl23', 'wlmnl24', 'wlmpl21', 'wlmpl22', 'wlmpl23', 'wlmpl24', 'wlmbr21', 'wlmbr22', 'wlmbr23', 'wlmbr24', 'wlmmx21', 'wlmmx22', 'wlmmx23', 'wlmmx24', 'wlmes21', 'wlmes22', 'wlmes23', 'wlmes24', 'wlmpt21', 'wlmpt22', 'wlmpt23', 'wlmpt24', 'wlmpk21', 'wlmpk22', 'wlmpk23', 'wlmpk24', 'wlmnp21', 'wlmnp22', 'wlmnp23', 'wlmnp24', 'wlmng21', 'wlmng22', 'wlmng23', 'wlmng24', 'wlmke21', 'wlmke22', 'wlmke23', 'wlmke24', 'wlmid21', 'wlmid22', 'wlmid23', 'wlmid24', 'wlmph21', 'wlmph22', 'wlmph23', 'wlmph24', 'wlmmy21', 'wlmmy22', 'wlmmy23', 'wlmmy24', 'wlmtr21', 'wlmtr22', 'wlmtr23', 'wlmtr24', 'wlmeg21', 'wlmeg22', 'wlmeg23', 'wlmeg24', 'wlmua21', 'wlmua22', 'wlmua23', 'wlmua24', 'wlmru21', 'wlmru22', 'wlmru23', 'wlmru24', 'wlmch21', 'wlmch22', 'wlmch23', 'wlmch24', 'wlmse21', 'wlmse22', 'wlmse23', 'wlmse24', 'wlmno21', 'wlmno22', 'wlmno23', 'wlmno24', 'wlmfi21', 'wlmfi22', 'wlmfi23', 'wlmfi24', 'wlmbe21', 'wlmbe22', 'wlmbe23', 'wlmbe24', 'wlmat21', 'wlmat22', 'wlmat23', 'wlmat24', 'wlmar21', 'wlmar22', 'wlmar23', 'wlmar24', 'wlmco21', 'wlmco22', 'wlmco23', 'wlmco24']
#Li = ['wlfbd20', 'wlfin20', 'wlfde20', 'wlfit20', 'wlffr20', 'wlfus20', 'wlfca20', 'wlfuk20', 'wlfnl20', 'wlfpl20', 'wlfbr20', 'wlfmx20', 'wlfes20', 'wlfpt20', 'wlfpk20', 'wlfnp20', 'wlfng20', 'wlfke20', 'wlfid20', 'wlfph20', 'wlfmy20', 'wlftr20', 'wlfeg20', 'wlfua20', 'wlfru20', 'wlfch20', 'wlfse20', 'wlfno20', 'wlffi20', 'wlfbe20', 'wlfat20', 'wlfar20', 'wlfco20', 'wlebd15', 'wlebd16', 'wlebd17', 'wlebd18', 'wlebd19', 'wlebd20', 'wlein15', 'wlein16', 'wlein17', 'wlein18', 'wlein19', 'wlein20', 'wlede15', 'wlede16', 'wlede17', 'wlede18', 'wlede19', 'wlede20', 'wleit15', 'wleit16', 'wleit17', 'wleit18', 'wleit19', 'wleit20', 'wlefr15', 'wlefr16', 'wlefr17', 'wlefr18', 'wlefr19', 'wlefr20', 'wleus15', 'wleus16', 'wleus17', 'wleus18', 'wleus19', 'wleus20', 'wleca15', 'wleca16', 'wleca17', 'wleca18', 'wleca19', 'wleca20', 'wleuk15', 'wleuk16', 'wleuk17', 'wleuk18', 'wleuk19', 'wleuk20', 'wlenl15', 'wlenl16', 'wlenl17', 'wlenl18', 'wlenl19', 'wlenl20', 'wlepl15', 'wlepl16', 'wlepl17', 'wlepl18', 'wlepl19', 'wlepl20', 'wlebr15', 'wlebr16', 'wlebr17', 'wlebr18', 'wlebr19', 'wlebr20', 'wlemx15', 'wlemx16', 'wlemx17', 'wlemx18', 'wlemx19', 'wlemx20', 'wlees15', 'wlees16', 'wlees17', 'wlees18', 'wlees19', 'wlees20', 'wlept15', 'wlept16', 'wlept17', 'wlept18', 'wlept19', 'wlept20', 'wlepk15', 'wlepk16', 'wlepk17', 'wlepk18', 'wlepk19', 'wlepk20', 'wlenp15', 'wlenp16', 'wlenp17', 'wlenp18', 'wlenp19', 'wlenp20', 'wleng15', 'wleng16', 'wleng17', 'wleng18', 'wleng19', 'wleng20', 'wleke15', 'wleke16', 'wleke17', 'wleke18', 'wleke19', 'wleke20', 'wleid15', 'wleid16', 'wleid17', 'wleid18', 'wleid19', 'wleid20', 'wleph15', 'wleph16', 'wleph17', 'wleph18', 'wleph19', 'wleph20', 'wlemy15', 'wlemy16', 'wlemy17', 'wlemy18', 'wlemy19', 'wlemy20', 'wletr15', 'wletr16', 'wletr17', 'wletr18', 'wletr19', 'wletr20', 'wleeg15', 'wleeg16', 'wleeg17', 'wleeg18', 'wleeg19', 'wleeg20', 'wleua15', 'wleua16', 'wleua17', 'wleua18', 'wleua19', 'wleua20', 'wleru15', 'wleru16', 'wleru17', 'wleru18', 'wleru19', 'wleru20', 'wlech15', 'wlech16', 'wlech17', 'wlech18', 'wlech19', 'wlech20', 'wlese15', 'wlese16', 'wlese17', 'wlese18', 'wlese19', 'wlese20', 'wleno15', 'wleno16', 'wleno17', 'wleno18', 'wleno19', 'wleno20', 'wlefi15', 'wlefi16', 'wlefi17', 'wlefi18', 'wlefi19', 'wlefi20', 'wlebe15', 'wlebe16', 'wlebe17', 'wlebe18', 'wlebe19', 'wlebe20', 'wleat15', 'wleat16', 'wleat17', 'wleat18', 'wleat19', 'wleat20', 'wlear15', 'wlear16', 'wlear17', 'wlear18', 'wlear19', 'wlear20', 'wleco15', 'wleco16', 'wleco17', 'wleco18', 'wleco19', 'wleco20', 'wlmbd15', 'wlmbd16', 'wlmbd17', 'wlmbd18', 'wlmbd19', 'wlmbd20', 'wlmin15', 'wlmin16', 'wlmin17', 'wlmin18', 'wlmin19', 'wlmin20', 'wlmde15', 'wlmde16', 'wlmde17', 'wlmde18', 'wlmde19', 'wlmde20', 'wlmit15', 'wlmit16', 'wlmit17', 'wlmit18', 'wlmit19', 'wlmit20', 'wlmfr15', 'wlmfr16', 'wlmfr17', 'wlmfr18', 'wlmfr19', 'wlmfr20', 'wlmus15', 'wlmus16', 'wlmus17', 'wlmus18', 'wlmus19', 'wlmus20', 'wlmca15', 'wlmca16', 'wlmca17', 'wlmca18', 'wlmca19', 'wlmca20', 'wlmuk15', 'wlmuk16', 'wlmuk17', 'wlmuk18', 'wlmuk19', 'wlmuk20', 'wlmnl15', 'wlmnl16', 'wlmnl17', 'wlmnl18', 'wlmnl19', 'wlmnl20', 'wlmpl15', 'wlmpl16', 'wlmpl17', 'wlmpl18', 'wlmpl19', 'wlmpl20', 'wlmbr15', 'wlmbr16', 'wlmbr17', 'wlmbr18', 'wlmbr19', 'wlmbr20', 'wlmmx15', 'wlmmx16', 'wlmmx17', 'wlmmx18', 'wlmmx19', 'wlmmx20', 'wlmes15', 'wlmes16', 'wlmes17', 'wlmes18', 'wlmes19', 'wlmes20', 'wlmpt15', 'wlmpt16', 'wlmpt17', 'wlmpt18', 'wlmpt19', 'wlmpt20', 'wlmpk15', 'wlmpk16', 'wlmpk17', 'wlmpk18', 'wlmpk19', 'wlmpk20', 'wlmnp15', 'wlmnp16', 'wlmnp17', 'wlmnp18', 'wlmnp19', 'wlmnp20', 'wlmng15', 'wlmng16', 'wlmng17', 'wlmng18', 'wlmng19', 'wlmng20', 'wlmke15', 'wlmke16', 'wlmke17', 'wlmke18', 'wlmke19', 'wlmke20', 'wlmid15', 'wlmid16', 'wlmid17', 'wlmid18', 'wlmid19', 'wlmid20', 'wlmph15', 'wlmph16', 'wlmph17', 'wlmph18', 'wlmph19', 'wlmph20', 'wlmmy15', 'wlmmy16', 'wlmmy17', 'wlmmy18', 'wlmmy19', 'wlmmy20', 'wlmtr15', 'wlmtr16', 'wlmtr17', 'wlmtr18', 'wlmtr19', 'wlmtr20', 'wlmeg15', 'wlmeg16', 'wlmeg17', 'wlmeg18', 'wlmeg19', 'wlmeg20', 'wlmua15', 'wlmua16', 'wlmua17', 'wlmua18', 'wlmua19', 'wlmua20', 'wlmru15', 'wlmru16', 'wlmru17', 'wlmru18', 'wlmru19', 'wlmru20', 'wlmch15', 'wlmch16', 'wlmch17', 'wlmch18', 'wlmch19', 'wlmch20', 'wlmse15', 'wlmse16', 'wlmse17', 'wlmse18', 'wlmse19', 'wlmse20', 'wlmno15', 'wlmno16', 'wlmno17', 'wlmno18', 'wlmno19', 'wlmno20', 'wlmfi15', 'wlmfi16', 'wlmfi17', 'wlmfi18', 'wlmfi19', 'wlmfi20', 'wlmbe15', 'wlmbe16', 'wlmbe17', 'wlmbe18', 'wlmbe19', 'wlmbe20', 'wlmat15', 'wlmat16', 'wlmat17', 'wlmat18', 'wlmat19', 'wlmat20', 'wlmar15', 'wlmar16', 'wlmar17', 'wlmar18', 'wlmar19', 'wlmar20', 'wlmco15', 'wlmco16', 'wlmco17', 'wlmco18', 'wlmco19', 'wlmco20', 'wlbbd15', 'wlbbd16', 'wlbbd17', 'wlbbd18', 'wlbbd19', 'wlbbd20', 'wlbin15', 'wlbin16', 'wlbin17', 'wlbin18', 'wlbin19', 'wlbin20', 'wlbde15', 'wlbde16', 'wlbde17', 'wlbde18', 'wlbde19', 'wlbde20', 'wlbit15', 'wlbit16', 'wlbit17', 'wlbit18', 'wlbit19', 'wlbit20', 'wlbfr15', 'wlbfr16', 'wlbfr17', 'wlbfr18', 'wlbfr19', 'wlbfr20', 'wlbus15', 'wlbus16', 'wlbus17', 'wlbus18', 'wlbus19', 'wlbus20', 'wlbca15', 'wlbca16', 'wlbca17', 'wlbca18', 'wlbca19', 'wlbca20', 'wlbuk15', 'wlbuk16', 'wlbuk17', 'wlbuk18', 'wlbuk19', 'wlbuk20', 'wlbnl15', 'wlbnl16', 'wlbnl17', 'wlbnl18', 'wlbnl19', 'wlbnl20', 'wlbpl15', 'wlbpl16', 'wlbpl17', 'wlbpl18', 'wlbpl19', 'wlbpl20', 'wlbbr15', 'wlbbr16', 'wlbbr17', 'wlbbr18', 'wlbbr19', 'wlbbr20', 'wlbmx15', 'wlbmx16', 'wlbmx17', 'wlbmx18', 'wlbmx19', 'wlbmx20', 'wlbes15', 'wlbes16', 'wlbes17', 'wlbes18', 'wlbes19', 'wlbes20', 'wlbpt15', 'wlbpt16', 'wlbpt17', 'wlbpt18', 'wlbpt19', 'wlbpt20', 'wlbpk15', 'wlbpk16', 'wlbpk17', 'wlbpk18', 'wlbpk19', 'wlbpk20', 'wlbnp15', 'wlbnp16', 'wlbnp17', 'wlbnp18', 'wlbnp19', 'wlbnp20', 'wlbng15', 'wlbng16', 'wlbng17', 'wlbng18', 'wlbng19', 'wlbng20', 'wlbke15', 'wlbke16', 'wlbke17', 'wlbke18', 'wlbke19', 'wlbke20', 'wlbid15', 'wlbid16', 'wlbid17', 'wlbid18', 'wlbid19', 'wlbid20', 'wlbph15', 'wlbph16', 'wlbph17', 'wlbph18', 'wlbph19', 'wlbph20', 'wlbmy15', 'wlbmy16', 'wlbmy17', 'wlbmy18', 'wlbmy19', 'wlbmy20', 'wlbtr15', 'wlbtr16', 'wlbtr17', 'wlbtr18', 'wlbtr19', 'wlbtr20', 'wlbeg15', 'wlbeg16', 'wlbeg17', 'wlbeg18', 'wlbeg19', 'wlbeg20', 'wlbua15', 'wlbua16', 'wlbua17', 'wlbua18', 'wlbua19', 'wlbua20', 'wlbru15', 'wlbru16', 'wlbru17', 'wlbru18', 'wlbru19', 'wlbru20', 'wlbch15', 'wlbch16', 'wlbch17', 'wlbch18', 'wlbch19', 'wlbch20', 'wlbse15', 'wlbse16', 'wlbse17', 'wlbse18', 'wlbse19', 'wlbse20', 'wlbno15', 'wlbno16', 'wlbno17', 'wlbno18', 'wlbno19', 'wlbno20', 'wlbfi15', 'wlbfi16', 'wlbfi17', 'wlbfi18', 'wlbfi19', 'wlbfi20', 'wlbbe15', 'wlbbe16', 'wlbbe17', 'wlbbe18', 'wlbbe19', 'wlbbe20', 'wlbat15', 'wlbat16', 'wlbat17', 'wlbat18', 'wlbat19', 'wlbat20', 'wlbar15', 'wlbar16', 'wlbar17', 'wlbar18', 'wlbar19', 'wlbar20', 'wlbco15', 'wlbco16', 'wlbco17', 'wlbco18', 'wlbco19', 'wlbco20']
analyze_country_overlaps(Li)
import pandas as pd

filename = 'survey 21-25(f) (copy).csv'

img_resolution = 1080
cellheight = 30
cellwidth = [90, 60, 60, 60, 60, 100, 60, 0]	# width for every column. set value to 0 to skip a column
txt_lpad = [17, 25, 14, 16, 16, 16, 14]     # left padding for text in every column
head_lpad = [17, 12, 19, 11, 9, 19, 9]      # left padding for header text in every column
txt_tpad = 19						# top padding including font height
font_size = 10.4
cell_border_width = 0.45
cell_head_color = "#fff"
head_fontcolor = "#000"
font_family = "Roboto"


df = pd.read_csv(filename)
SVGfile = ""
xdis = [sum(cellwidth[0:i]) for i in range(len(cellwidth))]

for i, key in enumerate(df.keys()):
        y = 0
        x = xdis[i]
        width = cellwidth[i]
        if not width: continue
        label = key       
        SVGfile += f"""
    <rect id="{label + "_cell"}" x="{x}" y="{y}" width="{width}" height="{cellheight}" fill="{cell_head_color}" stroke='#000' stroke-width="{cell_border_width}"/>
    <text id="{label + "_value"}" x="{x + head_lpad[i]}" y="{y + txt_tpad}" font-family="{font_family}" font-size="{font_size}" fill="{head_fontcolor}">{key}</text>
"""
        
for index, row in df.iterrows():
    for  i, v in enumerate(row):
        y = (index+1) * 30
        x = xdis[i]
        width = cellwidth[i]
        if not width: continue
        label = df['Country'][index]+"_"+row.keys()[i]
        SVGfile += f"""
    <rect id="{label + "_cell"}" x="{x}" y="{y}" width="{width}" height="{cellheight}" fill="#fff" stroke='#000' stroke-width="{cell_border_width}"/>
    <text id="{label + "_value"}" x="{x + txt_lpad[i]}" y="{y + txt_tpad}" font-family="{font_family}" font-size="{font_size}" fill="#000">{v}</text>
"""
SVGfile = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {sum(cellwidth)} {(len(df)+1)*cellheight}"  width="{img_resolution}" height="{(len(df)+1)*cellheight/sum(cellwidth)*img_resolution}">
""" + SVGfile + "</svg>"
        
with open(filename.replace('.csv','')+'.svg', 'w') as f:
    f.write(SVGfile)
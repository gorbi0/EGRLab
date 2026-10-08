# Development preview of placement.py (M1_BOXES dump -> routing/boxes.svg; svg2png.mjs rasterizes it in Docker).
import json,sys
d=json.load(open('routing/boxes.json'))
s=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="-2 -2 154 84" width="1540" height="840"><rect x="0" y="0" width="150" height="80" fill="#f8f8f0" stroke="black" stroke-width=".2"/>']
for side,z in d['reserved']:
    s.append(f'<rect x="{z[0]}" y="{z[1]}" width="{z[2]-z[0]}" height="{z[3]-z[1]}" fill="{"#fdd" if side=="F" else "none"}" stroke="red" stroke-width=".1"/>')
for r,b in d['boxes'].items():
    c='#36c' if d['side'][r]=='F' else '#c63'
    s.append(f'<rect x="{b[0]}" y="{b[1]}" width="{b[2]-b[0]}" height="{b[3]-b[1]}" fill="none" stroke="{c}" stroke-width=".15"/><text x="{(b[0]+b[2])/2}" y="{(b[1]+b[3])/2}" font-size="1.6" text-anchor="middle" fill="{c}">{r}</text>')
for r,pp in d['pads'].items():
    for n,(x,y) in pp.items(): s.append(f'<circle cx="{x}" cy="{y}" r=".3" fill="#999"/>')
for x,y in d['holes']: s.append(f'<circle cx="{x}" cy="{y}" r="3.5" fill="none" stroke="green" stroke-width=".2"/>')
open('routing/boxes.svg','w').write(''.join(s)+'</svg>')

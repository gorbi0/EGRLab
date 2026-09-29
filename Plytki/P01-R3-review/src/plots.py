"""Small vector plots of retained traces; all acceptance metrics use full traces."""
from pathlib import Path
import numpy as np,html
P=Path(__file__).resolve().parents[1]
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="840" viewBox="0 0 1200 840"><rect width="1200" height="840" fill="white"/><style>text{font:14px Arial;fill:#263444}.title{font-size:22px;font-weight:bold}.head{font-size:17px;font-weight:bold}</style><text x="40" y="36" class="title">P01 R3 — symulacja bloku bramki</text><text x="40" y="62">Model przybliżony; wykresy nie są pomiarami. R1 zachowane jako próba regresji.</text>']
def panel(x,y,title,series,tmin,tmax,ymin,ymax,unit):
 w,h=480,220
 svg.append(f'<text x="{x}" y="{y-18}" class="head">{title}</text>')
 for j in range(6):
  px=x+j*w/5;py=y+j*h/5
  svg.extend([f'<path d="M{px},{y} V{y+h} M{x},{py} H{x+w}" stroke="#e0e6eb" fill="none"/>',f'<text x="{px}" y="{y+h+20}" text-anchor="middle">{tmin+(tmax-tmin)*j/5:.0f}</text>',f'<text x="{x-8}" y="{py+5}" text-anchor="end">{ymax-(ymax-ymin)*j/5:.1f}</text>'])
 svg.append(f'<text x="{x+w/2}" y="{y+h+42}" text-anchor="middle">czas [{unit}]</text>')
 for k,(file,col,scale,color,label) in enumerate(series):
  a=np.genfromtxt(P/'simulation/results'/f'{file}.csv',delimiter=',',names=True)
  t=a['t_s']*scale;v=a['VS_V']-a['GATE_V'] if col=='VSG' else a[col]
  mask=(t>=tmin)&(t<=tmax);pts=' '.join(f'{x+(tt-tmin)/(tmax-tmin)*w:.2f},{y+(ymax-vv)/(ymax-ymin)*h:.2f}' for tt,vv in zip(t[mask],v[mask]))
  svg.append(f'<polyline points="{pts}" stroke="{color}" stroke-width="2" fill="none"/>')
  svg.append(f'<text x="{x+k*240}" y="{y+h+67}" style="fill:{color}">{html.escape(label)}</text>')
panel(75,115,'Hotplug 24 V / 1 µs: VSG [V]',[('regression_R1_hot24','VSG',1e6,'#c23b35','R1 — wykryty błąd'),('hot_24_1e-06_0','VSG',1e6,'#007f84','R3 — nominał')],0,100,0,10,'µs')
panel(690,115,'Hotplug 48 V / 1 µs: VSG [V]',[('hot_48_1e-06_1','VSG',1e6,'#007f84','R3 — C5+, C6−, Cgd=2nF')],0,100,0,.8,'µs')
panel(75,505,'Wyłączenie: VSG [V]',[('off_0','VSG',1e6,'#5167a8','R3 nominał'),('off_1','VSG',1e6,'#007f84','R3 wolniejszy wariant')],40,150,0,16,'µs')
panel(690,505,'Start 17 V, 1,5 A: prąd Q1 [A]',[('start_fast_corner','Q1_channel_A',1e3,'#007f84','R3 — szybszy wariant')],0,30,0,5,'ms')
svg.append('<text x="40" y="825">Pełne dane, parametry i limity: verification/dynamics.json, docs/ANALIZA.md</text></svg>')
(P/'simulation/przebiegi.svg').write_text(''.join(svg),encoding='utf-8')

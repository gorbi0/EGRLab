"""Assembly concept drawings, explicitly not fabrication/layout files."""
from pathlib import Path
import csv,json,html,textwrap
D=Path(__file__).resolve().parents[1];O=D/'montaz';O.mkdir(exist_ok=True)
interfaces=list(csv.DictReader((D/'interfejsy.csv').open(encoding='utf-8-sig'),delimiter=';'))
modules=json.loads((D/'hardware/modules.json').read_text())
def begin(title,height=650):return [f'<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="{height}" viewBox="0 0 1100 {height}"><rect width="100%" height="100%" fill="#fff"/><g font-family="Arial" font-size="18"><text x="35" y="42" font-size="26" font-weight="bold">{html.escape(title)}</text>']
def label(s,x,y,text,size=18):s.append(f'<text x="{x}" y="{y}" font-size="{size}">{html.escape(text)}</text>')
def rect(s,x,y,w,h,fill):s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{fill}" stroke="#476173"/>')
def end(name,s):s.append('</g></svg>');(O/name).write_text(''.join(s),encoding='utf-8')
s=begin('V6 — pigtail modułu: PTH + kotwa 10–15 mm')
rect(s,50,110,700,350,'#eef4f0');label(s,70,143,'PCB modułu — widok od strony przewodów')
rect(s,240,185,650,190,'#dae1e6')
for y in range(200,370,24):
 s.append(f'<path d="M 265 {y} H 925" stroke="#8b9aa5" stroke-width="10"/><circle cx="265" cy="{y}" r="9" fill="#d7b96e" stroke="#664c12"/><circle cx="265" cy="{y}" r="3" fill="#fff"/>')
rect(s,460,166,24,230,'#7297a1')
for y in [174,389]:s.append(f'<circle cx="472" cy="{y}" r="9" fill="#fff" stroke="#123"/>')
rect(s,925,179,112,206,'#364e61');label(s,932,275,'IDC',22);label(s,913,425,'jedyny wtyk')
label(s,140,405,'metalizowane otwory');label(s,410,435,'opaska na izolacji')
s.append('<path d="M 265 485 H 472 M 265 475 V 495 M 472 475 V 495" stroke="#174969" stroke-width="2"/>');label(s,295,515,'10–15 mm')
label(s,50,560,'Dwa otwory kotwy po bokach taśmy. Miękka przekładka, niewielki luz przy lutach.')
label(s,50,595,'Schemat zasady mocowania — nie jest szablonem wiercenia ani rysunkiem w skali.',16)
end('kotwa.svg',s)
s=begin('V6 — CORE–DAQ: bezpośrednie złącze płytka–płytka')
rect(s,65,205,500,30,'#89b9a1');label(s,90,192,'P03 CORE — połączenie z P05 bez kabla')
rect(s,490,355,510,30,'#89b9a1');label(s,670,420,'P05 DAQ — analog poza CORE')
rect(s,495,235,50,120,'#334d60');label(s,620,277,'SSW-108-01-G-D / TSW-108-07-G-D',17)
label(s,620,310,'2 × 8; pozycja 2 usunięta i zaślepiona',17)
for x in [450,585]:rect(s,x,140,16,300,'#d9dfe5')
label(s,85,465,'Oddzielne podpory obu PCB; złącze nie przenosi obciążeń mechanicznych.')
label(s,85,500,'Asymetryczna prowadnica blokuje obrót i przesunięcie złącza.')
label(s,85,535,'Rozstaw podpór i wysokość ustalić z rzeczywistym złączem przed layoutem.')
label(s,85,570,'Widok zasady z boku, bez skali. 3V3_CORE i 3V3_IO pozostają rozdzielone.',16)
end('core-daq.svg',s)
for m in modules:
 b=m['id'];s=begin(f'V6 / {b} {m["function"]} — plan stref montażowych',730)
 label(s,35,75,'Rezerwa miejsca: '+' × '.join(map(str,m['envelope_mm']))+' mm; '+m['assembly'])
 for x in range(40,1040,20):
  for y in range(105,370,20):s.append(f'<circle cx="{x}" cy="{y}" r="1" fill="#bec7cd"/>')
 rect(s,65,135,290,175,'#eef4f7');rect(s,405,135,290,175,'#edf5e9');rect(s,745,135,290,175,'#fff2dc')
 for x,lines in [(85,['KRAWĘDŹ / INTERFEJSY','PTH oraz kotwy 10–15 mm','Bufory blisko wejść','Gniazda pewnie mocowane']), (425,['OBWODY LOKALNE','Podstawki / układy','Odsprzęganie przy pinach','Krótki powrót GND']), (765,['ZASILANIE / POMIARY','Szyny i punkty pomiarowe','Oddzielny tor dużego prądu','Dostęp do sond'])]:
  for j,t in enumerate(lines):label(s,x,168+33*j,t,17)
 label(s,45,352,'Na uniwersalnej raster 2,54 mm; tu siatka poglądowa, nie współrzędne elementów.',16)
 related=[r for r in interfaces if b in [r['koniec_A'].split('/')[0],r['koniec_B'].split('/')[0]]]
 y=405
 for r in related:
  label(s,45,y,f'{r["lacze"]}: {r["dlugosc_mm"]} mm, {r["rodzina"]}; koniec lutowany: '+(r['koniec_B'] if r['kotwa_mm'] else 'brak przewodów / wyjątek'),16);y+=22
 label(s,45,680,'Układ stref — bez gotowego rozmieszczenia wszystkich części i bez ścieżek.',16)
 label(s,45,708,'Pinout i kolejność montażu: netlist.csv, karty modułów, docs/10-montaz-wiazek.md.',16)
 end(b+'-strefy.svg',s)
files=['kotwa.svg','core-daq.svg']+[m['id']+'-strefy.svg' for m in modules]
(O/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>EGRLab V6 — montaż</title><style>body{font:17px system-ui;max-width:1100px;margin:30px auto}img{width:100%;border:1px solid #ddd;margin-bottom:30px}</style><h1>EGRLab V6 — wskazówki montażowe</h1><p>Rysunki zasad i stref. Nie są plikami produkcyjnymi ani szczegółowym rozmieszczeniem elementów.</p>'+''.join(f'<h2>{f}</h2><img src="{f}" alt="{f}">' for f in files),encoding='utf-8')
print(len(files),'assembly drawings')

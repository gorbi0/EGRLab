from pathlib import Path
import csv,json,html,re,math,collections
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor

ROOT=Path(__file__).resolve().parents[1]
C=json.loads((ROOT/'hardware/components.json').read_text(encoding='utf-8'))
W,H=1190.55,841.89
pdfmetrics.registerFont(TTFont('Text','C:/Windows/Fonts/segoeui.ttf'))
pdfmetrics.registerFont(TTFont('Bold','C:/Windows/Fonts/segoeuib.ttf'))
pdf=canvas.Canvas(str(ROOT/'EGRLab-PWR-THT-v1.pdf'),pagesize=(W,H))
pdf.setTitle('EGRLab PWR-THT v1 - schemat i dokumentacja')
pdf.setAuthor('EGRLab / projekt przygotowany z Codex')
page_count=0;covered=set();manifest=[];overflows=[]

def wrap(s,width,size=10,font='Text'):
    result=[]
    for para in s.split('\n'):
        words=para.split();line=''
        for word in words:
            candidate=(line+' '+word).strip()
            if pdfmetrics.stringWidth(candidate,font,size)<=width:line=candidate;continue
            if line:result.append(line);line=''
            while pdfmetrics.stringWidth(word,font,size)>width:
                k=max(1,int(len(word)*width/pdfmetrics.stringWidth(word,font,size)))
                while pdfmetrics.stringWidth(word[:k],font,size)>width:k-=1
                result.append(word[:k]);word=word[k:]
            line=word
        if line:result.append(line)
        if not words:result.append('')
    return result

class Page:
    def __init__(self,title,sub=''):
        global page_count
        page_count+=1;self.i=page_count;self.title=title;self.svg=[]
        self.rect(0,0,W,H,fill='#ffffff',stroke='#ffffff')
        self.text(32,32,'EGRLab  /  PWR-THT v1',11,True,'#007d77')
        self.text(32,66,title,24,True)
        self.text(32,87,sub,10,False,'#516473')
        self.line([(32,104),(W-32,104)],'#bccbd4')
    def text(self,x,y,s,size=10,bold=False,color='#173242',anchor='start'):
        font='Bold' if bold else 'Text';s=str(s).replace('≤','<=').replace('≥','>=')
        sw=pdfmetrics.stringWidth(s,font,size)
        lx=x if anchor=='start' else x-sw/2 if anchor=='middle' else x-sw
        if lx<16 or lx+sw>W-16 or y>H-30:overflows.append((self.i,lx,y,s))
        pdf.setFont(font,size);pdf.setFillColor(HexColor(color));pdf.drawString(lx,H-y,s)
        self.svg.append(f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" font-family="Segoe UI,Arial,sans-serif" font-weight="{700 if bold else 400}" fill="{color}" text-anchor="{anchor}">{html.escape(s)}</text>')
    def line(self,pts,color='#18704b',width=1):
        pdf.setStrokeColor(HexColor(color));pdf.setLineWidth(width)
        p=pdf.beginPath();p.moveTo(pts[0][0],H-pts[0][1])
        for x,y in pts[1:]:p.lineTo(x,H-y)
        pdf.drawPath(p)
        self.svg.append(f'<polyline points="{" ".join(f"{x:.2f},{y:.2f}" for x,y in pts)}" fill="none" stroke="{color}" stroke-width="{width}"/>')
    def rect(self,x,y,w,h,fill='#ffffff',stroke='#8ba4b0'):
        pdf.setFillColor(HexColor(fill));pdf.setStrokeColor(HexColor(stroke));pdf.setLineWidth(.6)
        pdf.rect(x,H-y-h,w,h,fill=1,stroke=1)
        self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width=".6"/>')
    def circle(self,x,y,r=2,color='#18704b'):
        pdf.setFillColor(HexColor(color));pdf.circle(x,H-y,r,fill=1,stroke=0)
        self.svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>')
    def para(self,x,y,s,width=530,size=10,bold=False,color='#173242',leading=None):
        leading=leading or size*1.45
        for line in wrap(s,width,size,'Bold' if bold else 'Text'):
            self.text(x,y,line,size,bold,color);y+=leading
        return y
    def card(self,ref,x,y,w=350,h=90):
        c=C[ref];covered.add(ref)
        self.rect(x,y,w,h,fill='#f7fafb',stroke='#d7e1e6')
        value=c['value']
        if c['kind']=='C':value+=' / '+re.search(r'\d+ V',c['note']).group(0)
        if c['kind']=='R':
            rv=c['rating'];value=f'{rv/1000:g} kΩ' if rv>=1000 else f'{rv:g} Ω'
        self.text(x+9,y+17,ref+'  '+value,10,True)
        pins=list(c['pins'].items());pitch=14
        if len(pins)<=2:
            mid=x+w/2;cy=y+46
            left,p1=pins[0][1],pins[0][0];right,p2=pins[1][1],pins[1][0]
            self.line([(x+12,cy),(mid-22,cy)]);self.line([(mid+22,cy),(x+w-12,cy)])
            if c['kind']=='R':self.rect(mid-22,cy-6,44,12)
            elif c['kind']=='C':
                self.line([(mid-22,cy),(mid-4,cy)]);self.line([(mid+4,cy),(mid+22,cy)])
                self.line([(mid-4,cy-10),(mid-4,cy+10)]);self.line([(mid+4,cy-10),(mid+4,cy+10)])
            elif c['kind']=='D':
                self.line([(mid-22,cy),(mid-9,cy),(mid-9,cy-9),(mid+9,cy),(mid-9,cy+9),(mid-9,cy)])
                self.line([(mid+9,cy-10),(mid+9,cy+10)]);self.line([(mid+9,cy),(mid+22,cy)])
            else:self.rect(mid-22,cy-7,44,14)
            self.text(x+12,cy-8,p1+(' +' if c['kind']=='C' and 'plus' in c['note'] else ''),8);self.text(x+w-12,cy-8,p2,8,anchor='end')
            self.text(x+12,cy+18,left,8.2);self.text(x+w-12,cy+18,right,8.2,anchor='end')
        else:
            for j,(pin,net) in enumerate(pins):
                cy=y+34+j*pitch
                self.line([(x+14,cy-3),(x+40,cy-3)])
                self.text(x+15,cy-6,pin,7)
                label=pinname(ref,pin)
                self.text(x+46,cy,f'{label}  ->  {net}',9)
        # pin labels and net names are electrical; positions within card are not footprint positions.
    def end(self):
        self.line([(32,H-49),(W-32,H-49)],'#bccbd4')
        self.text(32,H-30,'PROJEKT PROTOTYPU | 22.09.2026 | brak pomiarów sprzętowych / brak kwalifikacji ISO',9,False,'#647681')
        self.text(W-32,H-30,f'{self.i:02d}',10,True,anchor='end')
        (ROOT/'svg'/f'{self.i:02d}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">\n'+'\n'.join(self.svg)+'</svg>',encoding='utf-8')
        manifest.append({'page':self.i,'title':self.title});pdf.showPage()

def pinname(ref,p):
    maps={
    'U1':{'1':'OUT','2':'GND','3':'IN'},'U2':{'1':'OUT1 OC','2':'IN1 -','3':'IN1 +','4':'GND','5':'IN2 +','6':'IN2 -','7':'OUT2 OC','8':'VCC'},
    'U3':{'1':'K','2':'A','3':'REF'},'U4':{'1':'RESET OC','2':'VDD','3':'VSS'},
    'Q1':{'1':'G','2':'D + TAB','3':'S'},'D2':{'1':'A1','2':'K + TAB','3':'A2'},'RV1':{'1':'koniec + suwak','2':'suwak + pin 1','3':'drugi koniec'}}
    if ref.startswith('Q') and ref!='Q1':return {'1':'E','2':'B','3':'C'}[p]
    return maps.get(ref,{}).get(p,'pin '+p)

def grid(page,refs,y=125,pitch=101,cols=3):
    width=(W-64-20*(cols-1))/cols
    for i,ref in enumerate(refs):
        h=max(90,39+14*len(C[ref]['pins']))
        page.card(ref,32+(i%cols)*(width+20),y+(i//cols)*pitch,width,h)

p=Page('01 / Tor mocy','Oznaczenia lokalne PG.*. Identyczne nazwy sieci oznaczają połączenie elektryczne na wszystkich arkuszach.')
# Connected functional power drawing with physical pin numbers.
for x,w,title,body in [(40,150,'J1 / wejście','1 BAT_FUSED\n2 GND'),(285,180,'D2 / Schottky','STPS20100CT\n1+3 A -> 2 K'),(565,230,'Q1 / P-MOSFET','SUP53P06-20-E3\n3 S -> 2 D; 1 G'),(910,230,'J2 / wyjście','1 VPROT\n2 GND')]:
    p.rect(x,140,w,95,fill='#eaf4f2');p.text(x+12,164,title,12,True);p.para(x+12,187,body,w-24,10)
p.line([(190,184),(285,184)],width=2);p.line([(465,184),(565,184)],width=2);p.line([(795,184),(910,184)],width=2)
p.text(494,172,'VS',10,True);p.text(813,172,'VPROT',10,True)
p.line([(235,184),(235,253),(92,253),(92,286)]);p.circle(235,184)
p.rect(40,286,160,48);p.text(50,305,'D1 15KPA24CA',10,True);p.text(50,321,'dwukierunkowy -> GND',9)
p.line([(850,184),(850,286)]);p.circle(850,184);p.rect(769,286,163,48);p.text(780,305,'D3 5KP18A',10,True);p.text(780,321,'K=VPROT; A=GND',9)
p.line([(680,235),(680,305)]);p.text(692,258,'GATE -> arkusz 04',10)
p.para(275,277,'Q1: dioda strukturalna przewodzi od VPROT do VS.\nD2 blokuje powrót energii do B+.\nPrzed J1 wymagany istniejący F1 5 A.',430,11)
covered.update(['J1','J2','D1','D2','Q1','D3'])
grid(p,['D4','C1','C2','C3','C4','C5','C6','R22','R28','LED1','R29'],y=375,pitch=97)
p.end()

p=Page('02 / Zasilanie pomocnicze, wzorzec i reset','Sterowanie jest zasilane z VS przed odłącznikiem. AUX5 jest odrębną siecią od 5V_SYS EGRLab.')
grid(p,['U1','U3','U4'],y=130,pitch=100)
grid(p,['R1','D5','C7','C8','R2','C9','R3','R4','C10','C11'],y=243,pitch=103)
p.para(32,677,'U1 TO-92: 1=OUT, 2=GND, 3=IN. U3 TI LP: 1=K, 2=A, 3=REF. U4: wyłącznie bondout D.',1125,11,True)
p.para(32,711,'C9 + R2 zapewniają wymagany ESR regulatora. Nie dodawać przypadkowego kondensatora na REF. U4 ściąga OK do masy podczas startu i brownout; typowe opóźnienie startu 350 ms.',1125,11)
p.end()

p=Page('03 / Okno napięciowe i histereza','OVP 18,00 V po kalibracji; powrót około 16,66 V. UVLO nominalnie 9,37 V / start 9,85 V.')
p.card('U2',32,125,350,161)
p.para(413,146,'LM2903P: OUT1 (pin 1) i OUT2 (pin 7) są połączone z OK. OUT1 ściąga OK przy OV_SENSE > OV_REF. OUT2 ściąga OK przy UV_SENSE < REF.',720,12)
p.para(413,214,'D6 mierzy BAT_FUSED przed diodą mocy i blokuje napięcie ujemne. Jej spadek wchodzi do kalibracji RV1. RV1: pin 2 zwarty z pinem 1; przed uruchomieniem ustawić 0 Ω między (1+2) i 3.',720,11)
grid(p,['D6','R5','RV1','R6','R7','R8','R9','R10','R11','R12','R13','J3','C12','C13'],y=305,pitch=92)
p.end()

p=Page('04 / Driver bramki - osobne tory ON i OFF','OFF: Q3/Q5 wyłączone, Q4 wyłączony, Q2 podciąga GATE do VS. ON: Q3/Q5/Q4 włączone, Q2 wyłączony.')
grid(p,['Q2','Q3','Q4','Q5','Q6','R14','D7','D8','R15','R16','R17','R18','R19','R20','R21','R23','R24','R25','R26','R27'],y=120,pitch=91)
p.end()

p=Page('05 / Sygnał błędu i połączenie z EGRLab','J4 jest wymagane. Krótki błąd rozbraja zatrzask ARM także przy podtrzymanym 3V3_IO.')
grid(p,['Q7','Q8','J4','R30','R31','R32','R33'],y=130,pitch=101)
p.para(32,459,'J4.1 -> 3V3_IO istniejącej płyty\nJ4.2 -> SAFE_N = U9 SN74HC74N pin 1 istniejącej płyty\nJ4.3 -> GND_STAR',540,13,True)
p.para(622,459,'Przy ENABLE=0 tranzystor Q7 przewodzi i zwiera SAFE_N do masy. Przy ENABLE=1 Q8 blokuje Q7. Kolektor Q7 nie ma lokalnego pull-up i nie wprowadza 5 V na SAFE_N.',535,12)
p.para(32,558,'M5.J1/J3 zastępują J1.1/J1.2, a M5.J2/J4 zastępują J2.1/J2.2. Stary wejściowy SM8S24CA zastępuje PG.D1 15KPA24CA. F1, F2/F3/F4, KPWR, C_BULK i SMCJ18A przy VMOTOR pozostają.',1125,12)
p.para(32,631,'Wszystkie oznaczenia na arkuszach 01-05 dotyczą nowego modułu. Nie utożsamiaj PG.Q8 ani PG.U4 z Q8/U4 istniejącej płyty. Napięcie ADC CH7 nadal pobierane jest z VPROT; firmware i pinout ESP32 nie wymagają zmiany.',1125,12)
p.para(32,708,'Powrót napięcia przywraca VPROT. Ruch silnika wymaga nowego naciśnięcia ARM. Nie łączyć OK/AUX5 bezpośrednio z SAFE_N.',1125,12,True)
p.end()

assert covered==set(C),('Missing components',set(C)-covered)

# Grouped procurement list. Function-specific comments remain in full BOM.
groups=collections.OrderedDict()
for ref,c in C.items():
    if c['kind']=='R':desc=c['value']+'; rezystor THT; '+c['note'].split(';')[0:2][0]+'; '+(';'.join(c['note'].split(';')[1:2])).strip()
    elif c['kind']=='C':
        voltage=re.search(r'\d+ V',c['note']).group(0)
        tech='elektrolit 105°C' if 'plus' in c['note'] else 'C0G/NP0' if 'C0G' in c['note'] else 'foliowy' if 'film' in c['note'] else 'X7R'
        desc=f'{c["value"]} / {voltage}; {tech}; THT'
        if ref=='C9':desc+='; ESR C9+1 Ω: 0,3-8 Ω'
    elif c['kind']=='J':desc=c['package']+(' / INHIBIT' if ref=='J3' else ' / FAULT' if ref=='J4' else '')
    else:desc=c['value']+'; '+c['package']
    groups.setdefault(desc,[]).append(ref)
materials=[('Radiator do D2, <=5 K/W w docelowej obudowie',1),('Radiator do Q1, <=10 K/W w docelowej obudowie',1),('Zestaw izolacyjny TO-220: podkładka + tulejka + śruba',2),('Podstawka precyzyjna DIP-8',1),('Płytka uniwersalna FR4 około 100 x 160 mm',1),('Zworka 2,54 mm do J3, tylko do prób INHIBIT',1)]
shopping=[(desc,len(refs),', '.join(refs)) for desc,refs in groups.items()]+[(desc,qty,'montaż') for desc,qty in materials]
with (ROOT/'hardware/do-zamowienia.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f,delimiter=';');w.writerow(['Nazwa','Ilosc szt.']);w.writerows((d,q) for d,q,r in shopping)
lines=['# Lista zakupów PWR-THT v1','','Pozycje wyłącznie nowego modułu. F1 i oprawa są już w EGRLab. Nie uwzględniono zapasowych sztuk.','','| Nazwa | Ilość szt. | Oznaczenia |','|---|---:|---|']
lines += [f'| {d} | {q} | {r} |' for d,q,r in shopping]
lines += ['','Dodatkowo przewód miedziany 1,5-2,5 mm², cienkie przewody sygnałowe, pasta termiczna, dystanse i materiały izolacyjne według wykonanej obudowy. Radiatory i elementy mocy należy mechanicznie umocować.','', 'Lista pełnych wymagań oraz pinoutów: hardware/BOM.csv. Q1 wyłącznie Vishay SUP53P06-20-E3 dla tej rewizji; zamiennik wymaga ponownej oceny VGS, SOA i strat.']
(ROOT/'ZAKUPY.md').write_text('\n'.join(lines),encoding='utf-8')

# Full text appendix on A3, in two columns, with measured line wrapping.
def render_md(path,title):
    raw=(ROOT/path).read_text(encoding='utf-8');p=Page(title,'Dokumentacja montażowa i wymagania odbiorcze. Wyniki sprzętowe nie zostały jeszcze uzyskane.')
    x=32;y=132;col=0;cw=544;code=False
    for rawline in raw.splitlines():
        if rawline.startswith('```'):
            code=not code
            if code and path=='README.md':
                p.text(x,y,'Schemat toru mocy: arkusz 01. Sterowanie: arkusze 02-05.',9.5);y+=20
            continue
        if code and path=='README.md':continue
        if re.match(r'^\|[- :|]+\|$',rawline):continue
        if not rawline.strip():y+=7;continue
        level=len(rawline)-len(rawline.lstrip('#'))
        if level==1:continue
        bold=level>0
        line=rawline.lstrip('# ').replace('**','').replace('`','').replace('—','-').replace('–','-')
        size=12 if bold else 9.5
        if line.startswith('|'):line=' | '.join(c.strip() for c in line.strip('|').split('|'));size=9
        lines=wrap(line,cw,size,'Bold' if bold else 'Text')
        leading=14 if not bold else 18
        if bold:y+=8
        for s in lines:
            if y>H-74:
                if col==0:col=1;x=615;y=132
                else:p.end();p=Page(title+' / cd.','Dokumentacja montażowa i wymagania odbiorcze.');col=0;x=32;y=132
            p.text(x,y,s,size,bold);y+=leading
    p.end()

render_md('README.md','06 / Założenia i integracja')
p=Page('07 / Wykaz elementów do zamówienia','Nowy moduł: 72 elementy elektryczne; ilości bez zapasowych sztuk. Istniejący F1 i jego oprawa pozostają.')
for column in range(2):
    x=32+column*583;y=130
    p.rect(x,y,543,25,fill='#eaf4f2');p.text(x+8,y+17,'Nazwa / wymagania',10,True);p.text(x+360,y+17,'Szt.',10,True);p.text(x+398,y+17,'Oznaczenia',10,True)
    y+=25
    split=(len(shopping)+1)//2
    for desc,qty,refs in shopping[column*split:(column+1)*split]:
        if 'ohm; rezystor' in desc:
            rv=float(desc.split(' ohm')[0]);desc=(f'{rv/1000:g} kΩ' if rv>=1000 else f'{rv:g} Ω')+desc[desc.index(';'):]
        ds=wrap(desc,340,9);rs=wrap(refs,135,8.5);h=max(len(ds),len(rs))*12+9
        p.rect(x,y,543,h,fill='#ffffff',stroke='#d7e1e6')
        for j,s in enumerate(ds):p.text(x+8,y+14+j*12,s,9)
        p.text(x+367,y+14,str(qty),9,True)
        for j,s in enumerate(rs):p.text(x+398,y+14+j*12,s,8.5)
        y+=h
    assert y<755,('BOM overflow',y)
p.para(32,770,'Dodatkowo: przewody 1,5-2,5 mm² i sygnałowe, pasta termiczna, dystanse. Pełne wymagania: hardware/BOM.csv.',1125,9)
p.end()
render_md('PROJEKT.md','08 / Obliczenia, zakres ochrony i źródła')
render_md('URUCHOMIENIE.md','09 / Uruchomienie i protokół odbioru')
pdf.save()
report={'pages':page_count,'components_drawn':len(covered),'all_components_drawn':covered==set(C),'layout_overflows':overflows,'manifest':manifest,'shopping_rows':len(shopping),'shopping_component_quantity':sum(len(v) for v in groups.values())}
(ROOT/'verification/document.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
assert not overflows,overflows
print(json.dumps(report,ensure_ascii=True,indent=2))

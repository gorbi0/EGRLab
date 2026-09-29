from pathlib import Path
import csv,json,re,hashlib,math,html,textwrap,collections
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor

import argparse
parser=argparse.ArgumentParser(description='Generator schematu EGRLab v4 S1')
parser.add_argument('--source',type=Path,default=Path(__file__).resolve().parent/'wejscie')
parser.add_argument('--out',type=Path,default=Path(__file__).resolve().parent.parent)
args=parser.parse_args()
SOURCE=args.source
OUT=args.out; OUT.mkdir(exist_ok=True,parents=True)
(OUT/'svg').mkdir(exist_ok=True);(OUT/'dane').mkdir(exist_ok=True)
W,H=1190.551,841.89
pdfmetrics.registerFont(TTFont('Segoe','C:/Windows/Fonts/segoeui.ttf'))
pdfmetrics.registerFont(TTFont('SegoeBold','C:/Windows/Fonts/segoeuib.ttf'))

def read(name):
    with (SOURCE/'hardware'/name).open(encoding='utf-8-sig') as f:return list(csv.DictReader(f,delimiter=';'))
edges=read('connections.csv');pins=read('ic-pins.csv');gpio=read('pinout.csv');connectors=read('connectors.csv')
components={}; parents={}; names=collections.defaultdict(set); covered=set(); drawn=[]
def root(x):
    parents.setdefault(x,x)
    if parents[x]!=x:parents[x]=root(parents[x])
    return parents[x]
def join(a,b):
    if a=='NC' or b=='NC':return
    parents[root(a)]=root(b)
def add(ref,value,terminals,kind='ic',note=''):
    assert ref not in components,ref
    components[ref]={'ref':ref,'value':value,'pins':dict(terminals),'kind':kind,'note':note}
    for pin,net in terminals:
        if net!='NC':join(ref+'.'+str(pin),net)
    return ref
for e in edges:join(e['from'],e['to'])
for p in pins:join(p['ref']+'.'+p['pin'],p['net'])
for p in connectors:join(p['connector']+'.'+p['contact'],p['signal'])

# Use physical device terminal numbers for ICs and labelled module contacts.
for ref,rows in __import__('itertools').groupby(sorted(pins,key=lambda x:x['ref']),lambda x:x['ref']):
    rows=list(rows);add(ref,rows[0]['part_package'],[(p['pin'],p['net']) for p in rows], 'mos' if ref.startswith('Q') else 'ic')
    components[ref]['functions']={p['pin']:p['function'] for p in rows}

passives={}
for e in edges:
    for end in ('from','to'):
        terminal=e[end];m=re.match(r'^((?:R_|C_|RM|RS|RA|RB|RV|RC|RO|CF|CI|Q\d+_PD)[\w]*?)\.([12])$',terminal)
        if m and not m[1].startswith('RSH'):
            p=m[1];passives.setdefault(p,{'value':'','ends':{}})
            passives[p]['ends'][m[2]]=e['to' if end=='from' else 'from']
            if e['note']:passives[p]['value']=e['note']
for ref,p in passives.items():
    assert set(p['ends'])=={'1','2'},ref
    add(ref,p['value'],list(p['ends'].items()),'cap' if ref.startswith(('C_','CF','CI')) else 'res')

def near(terminal):
    options=[]
    for e in edges:
        if e['from']==terminal:options.append(e['to'])
        if e['to']==terminal:options.append(e['from'])
    return next((x for x in options if '.' not in x),options[0] if options else 'NC')
for ref in ('F1','F2','F3','F4'):add(ref,'5 A' if ref in ('F1','F4') else '1 A',[(p,near(ref+'.'+p)) for p in ('IN','OUT')],'fuse')
add('D1','SM8S24CA',[(p,near('D1.'+p)) for p in ('A','B')],'tvsbi')
add('D2','SMCJ18A',[(p,near('D2.'+p)) for p in ('A','K')],'zener')
for n in range(4,9):add(f'D{n}','1N4148',[(p,near(f'D{n}.'+p)) for p in ('A','K')],'diode')
add('D11','1N4007',[(p,near('D11.'+p)) for p in ('A','K')],'diode')
add('D12','Zener 18 V / >=1 W',[(p,near('D12.'+p)) for p in ('A','K')],'zener')
add('D3','PESD2CAN / SOT-23',[(str(n),near('D3.'+str(n))) for n in (1,2,3)])
components['D3']['functions']={'1':'CAN1','2':'CAN2','3':'COMMON'}
for ref in ('M3','M4'):
    add(ref,'TSR 2-2450' if ref=='M3' else 'TSR 2-2433',[(p,near(ref+'.'+p)) for p in ('VIN','GND','VOUT')],note='Piny wg nazw modułu; zweryfikuj obudowę.')
add('M5','LM74800EVM-CD',[(p,near('M5.'+p)) for p in ('J1','J3','J2','J4')],note='Gotowy moduł TI. J6: 2-3. Szczegóły OV na arkuszu zasilania.')
add('M2','Pololu 1451 / VNH5019',[(p,near('M2.'+p)) for p in ('VIN','GND','VDD','PWM','INA','INB','ENA','ENB','OUTA','OUTB')]+[('CS','NC')],note='Nazwy pól nośnika; CS nieużyte. Mostek jako kompletny moduł.')
add('M1','Waveshare ESP32-S3 N32R16V',[('5V','5V_SYS'),('GND','DGND')]+[(p['GPIO'],p['signal']) for p in gpio if p['direction']!='reserved'],note='Numery GPIO, nie numery kolejnych pól goldpin. 3V3 płytki nie łączyć z 3V3_IO.')
components['M1']['functions']={p['GPIO']:'GPIO'+p['GPIO'] for p in gpio if p['direction']!='reserved'}|{'5V':'5V','GND':'GND'}
for ref in ('RSH_T','RSH_L'):add(ref,'5 mΩ / 2 W / Kelvin',[(p,near(ref+'.'+p)) for p in ('P1','P2','K1','K2')],'shunt')
for ref in ('KMEAS1','KMEAS2','KMEAS3','KCUR','KSENSOR'):
    add(ref,'G6K-2F-Y DC5',[(p,near(ref+'.'+p)) for p in ('COIL_PLUS','COIL_MINUS','COM_A','NC_A','NO_A','COM_B','NC_B','NO_B')],'relay')
    components[ref]['numbers']={'COIL_PLUS':'1','COIL_MINUS':'8','COM_A':'3','NC_A':'2','NO_A':'4','COM_B':'6','NC_B':'7','NO_B':'5'}
add('KPWR','NO >=20 A; cewka 12 V <=150 mA',[(p,near('KPWR.'+p)) for p in ('86','85','30','87')],'relaypower',note='Przekaźnik bez wbudowanej diody. Finalny SKU wymaga doboru mechanicznego.')

for ref,ps,value in [('SW_MODE',['COM','TEST_NO'],'Kluczyk TEST / NO'),('SW_LOG1',['COM_A','NC_A','COM_B','NC_B'],'Gniazdo L1 / dwa NC'),('SW_LOG2',['COM_A','NC_A','COM_B','NC_B'],'Gniazdo L2 / dwa NC'),('SW_TEST',['COM','NO'],'Gniazdo T / NO'),('SW_STOP',['COM_NC','NC','COM_NO','NO'],'STOP 1NC+1NO sprzężone'),('SW_ARM',['COM','NO'],'ARM / chwilowy NO'),('SW_MARK',['COM','NO'],'MARK / chwilowy NO')]:
    add(ref,value,[(p,near(ref+'.'+p)) for p in ps],'switch')
add('JP_AUX','DPDT HI / LO',[(p,near('JP_AUX.'+p)) for p in ('COM_A','HI_A','LO_A','COM_B','HI_B','LO_B')],'switch')
add('J_BYPASS','Zwora >=5 A / bypass 1',[(p,near('J_BYPASS.'+p)) for p in ('1','2')],'jumper')
for ref in ('J_TEST','J_L1','J_L2'):
    rows=[p for p in connectors if p['connector']==ref]
    add(ref,'Panel 12p / klucz '+ref,[(p['contact'],p['signal']) for p in rows],'connector')
for ref,ps,val in [('J_PWR',['1','2'],'Wejście B+ / B-'),('J_SCOPE',['HOT','SHELL'],'BNC: wyjście trigger'),('J_AUX',['HOT','SHELL'],'BNC: wejście pomiarowe'),('J_OBD',['6','14','4','5','16'],'OBD-II; pozostałe styki NC')]:
    add(ref,val,[(p,near(ref+'.'+p)) for p in ps],'connector')
for ref in ('TC1','TC2'):add(ref,'Moduł MAX31856 / 3,3 V',[(p,near(ref+'.'+p)) for p in ('VIN','GND','SCK','SDI','SDO','CS','T+','T-')],note='Kompletny moduł z filtrami wejść; termopara K izolowana.')
add('SD1','microSD SPI / 3,3 V',[(p,near('SD1.'+p)) for p in ('VDD','GND','CLK','DI','DO','CS')])

# Explicit completion of connections described in V4 prose.
for n in (4,5,6):add('JP'+str(n),'1x3; tylko DWIE zwory łącznie',[('1','5V_SENSOR'),('2',f'T.OEM{n}'),('3','AGND_SENSOR')],'connector')
join('J_TEST.1','T.OEM1');join('J_TEST.2','T.OEM3')
add('JT_LOOP','Mostek tylko w adapterze T',[('10','LOOP_OUT'),('11','INTERLOCK')],'jumper')
join('J_L1.2','L1.OEM1');join('J_L1.1','ECU_P1')
for n in (3,4,5,6):join(f'L1.OEM{n}',f'ECU_P{n}')
join('SHIELD','AGND')
for adapter in ('T','L1','L2'):
    for n in (1,3,4,5,6):join(f'{adapter}.OEM{n}',f'{adapter}_EGR_P{n}')
    add('OEM_'+adapter,'Zawór / sondy '+adapter,[(str(n),f'{adapter}.OEM{n}') for n in (1,3,4,5,6)],'connector')
add('OEM_ECU','Wiązka fabryczna w L1',[(str(n),f'ECU_P{n}') for n in (1,3,4,5,6)],'connector')
add('M5_R8','9,10 kΩ / 0,1%',[('1','BAT_FUSED'),('2','M5_VIN_MON')],'res')
add('M5_R3','38,3 kΩ / 0,1%',[('1','M5_VIN_MON'),('2','M5_OV')],'res')
add('M5_R4','3,48 kΩ / 0,1%',[('1','M5_OV'),('2','AGND')],'res')
add('C_MOTOR_HF','100 nF / 50 V',[('1','VMOTOR'),('2','PGND')],'cap')
add('C_MOTOR_MF','1 µF / 50 V',[('1','VMOTOR'),('2','PGND')],'cap')
add('R_LED','1 kΩ',[('1','STATUS_LED'),('2','LED_A')],'res')
add('LED1','Zielona / status',[('A','LED_A'),('K','DGND')],'led')
add('C_CAN_VIO','100 nF',[('1','3V3_IO'),('2','AGND')],'cap')
for rail in ('5V_SYS','3V3_IO'):
    for typ,val in [('IN','10 µF / 50 V'),('OUT','22 µF / 10 V')]:
        add('C_DCDC_'+rail+'_'+typ,val,[('1',('M3.VIN' if rail=='5V_SYS' else 'M4.VIN') if typ=='IN' else rail),('2','GND_STAR')],'cap')
for term,label in {'RSH_T.P1':'HBR_OUT_A','RSH_T.K1':'TEST_K1','RSH_T.K2':'TEST_K2','RSH_L.K1':'LOGGER_K1','RSH_L.K2':'LOGGER_K2','KCUR.NO_A':'I_TEST_SER','KCUR.NC_A':'I_LOG_SER','R_PWM.2':'PWM_DRV','R_INA.2':'INA_DRV','R_INB.2':'INB_DRV','M3.VIN':'VIN_DC5','M4.VIN':'VIN_DC33','SW_ARM.NO':'ARM_CONTACT','SW_STOP.NC':'STOP_NC_OUT','SW_LOG1.NC_A':'ILK_L1_L2','SW_LOG1.NC_B':'DIAG_L1_L2'}.items():join(term,label)

# Net name normalization: preserve user-facing rail/signal names, avoid naked pin aliases.
for n in list(parents):
    if '.' not in n:names[root(n)].add(n)
preferred=['GND_STAR','5V_SYS','3V3_IO','5V_A','VMOTOR','VPROT','BAT_FUSED','SAFE_N','SUP_N','INTERLOCK','5V_SENSOR','AGND_SENSOR']
canon={}
for n in list(parents):
    rt=root(n)
    if rt in canon:continue
    options=names.get(rt,set())
    canon[rt]=next((x for x in preferred if x in options),sorted(options,key=lambda x:(x.endswith('_OUT'),len(x),x))[0] if options else 'N_'+re.sub(r'\W','_',n))
def net(terminal):
    if terminal=='NC':return 'NC'
    return canon[root(terminal)]
def pn(ref,p):
    raw=components[ref]['pins'][str(p)]
    if raw=='NC':return 'NC'
    if raw in ('AGND','DGND','PGND'):return raw
    return net(ref+'.'+str(p))
for ref,c in components.items():
    c['resolved']={p:pn(ref,p) for p in c['pins']}

class Drawing:
    def __init__(self,pdf,index,title,subtitle=''):
        self.pdf=pdf;self.index=index;self.title=title;self.svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="420mm" height="297mm" viewBox="0 0 {W} {H}"><rect width="100%" height="100%" fill="white"/>'];self.refs=[]
        self.text(28,27,'EGRLab v4',18,True);self.text(168,27,title,17,True)
        self.text(28,49,subtitle or 'Schemat elektryczny modułowy | Kia Sportage 1.7 CRDi 2013 | rewizja rysunkowa S1',9)
        self.line([(25,62),(W-25,62)],'#153b51',1.5)
    def text(self,x,y,s,size=9,bold=False,color='#183743',anchor='start'):
        s=str(s).replace('∧','&').replace('→','->').replace('–','-').replace('—','-')
        self.pdf.setFillColor(HexColor(color));self.pdf.setFont('SegoeBold' if bold else 'Segoe',size)
        width=pdfmetrics.stringWidth(s,'SegoeBold' if bold else 'Segoe',size)
        px=x if anchor=='start' else x-width/2 if anchor=='middle' else x-width
        assert px>=8 and px+width<W-8,(self.index,s,px,width)
        self.pdf.drawString(px,H-y,s)
        self.svg.append(f'<text x="{x:.2f}" y="{y:.2f}" font-family="Segoe UI,Arial,sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" text-anchor="{anchor}" fill="{color}">{html.escape(s)}</text>')
    def line(self,pts,color='#267146',width=.85):
        self.pdf.setStrokeColor(HexColor(color));self.pdf.setLineWidth(width)
        p=self.pdf.beginPath();p.moveTo(pts[0][0],H-pts[0][1])
        for x,y in pts[1:]:p.lineTo(x,H-y)
        self.pdf.drawPath(p)
        self.svg.append('<polyline points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in pts)+f'" stroke="{color}" stroke-width="{width}" fill="none"/>')
    def rect(self,x,y,w,h,color='#172f3d',fill='#ffffff',lw=.9):
        self.pdf.setStrokeColor(HexColor(color));self.pdf.setFillColor(HexColor(fill));self.pdf.setLineWidth(lw);self.pdf.rect(x,H-y-h,w,h,stroke=1,fill=1)
        self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" stroke="{color}" stroke-width="{lw}" fill="{fill}"/>')
    def dot(self,x,y,r=2):
        self.pdf.setFillColor(HexColor('#267146'));self.pdf.circle(x,H-y,r,stroke=0,fill=1);self.svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#267146"/>')
    def circle(self,x,y,r):
        self.pdf.setStrokeColor(HexColor('#172f3d'));self.pdf.setLineWidth(.8);self.pdf.circle(x,H-y,r,stroke=1,fill=0);self.svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" stroke="#172f3d" stroke-width=".8" fill="none"/>')
    def label(self,x,y,label,side='left',size=8):
        if label=='NC':self.line([(x-3,y-3),(x+3,y+3)],'#888');self.line([(x-3,y+3),(x+3,y-3)],'#888');return
        self.text(x,y-4,label,size,False,'#15538b','end' if side=='left' else 'start')
    def note(self,x,y,s,w=100,size=9,color='#183743'):
        for i,line in enumerate(textwrap.wrap(s,w,break_long_words=False)):self.text(x,y+i*13,line,size,color=color)
    def section(self,x,y,s,w=535):
        self.text(x,y,s,11,True);self.line([(x,y+7),(x+w,y+7)],'#c2cdd3',.65)
    def mark(self,ref):
        if ref not in self.refs:self.refs.append(ref)
        drawn.append((self.index,ref));covered.add(ref)
    def two(self,ref,x,y,w=340):
        c=components[ref];ps=list(c['pins']);assert len(ps)==2,(ref,ps)
        self.mark(ref);a,b=[pn(ref,p) for p in ps];mid=x+w/2;ends=(mid-38,mid+38)
        # Net labels are set above the ends, keeping wire runs distinct.
        self.text(x,y-12,a,8,False,'#15538b');self.text(x+w,y-12,b,8,False,'#15538b','end')
        self.line([(x,y),(mid-16,y)]);self.line([(mid+16,y),(x+w,y)])
        k=c['kind']
        if k in ('res','fuse','jumper'):
            self.rect(mid-16,y-5,32,10)
            if k=='fuse':self.line([(mid-16,y),(mid+16,y)],'#172f3d')
            if k=='jumper':self.line([(mid-15,y-3),(mid+15,y+3)],'#172f3d')
        elif k=='cap':
            self.line([(mid-16,y),(mid-3,y)],'#172f3d');self.line([(mid+3,y),(mid+16,y)],'#172f3d');self.line([(mid-3,y-9),(mid-3,y+9)],'#172f3d',1.4);self.line([(mid+3,y-9),(mid+3,y+9)],'#172f3d',1.4)
        elif k=='tvsbi':
            self.line([(mid-16,y),(mid-12,y)],'#172f3d');self.line([(mid-12,y-7),(mid-12,y+7),(mid-3,y),(mid-12,y-7)],'#172f3d');self.line([(mid-3,y-8),(mid-3,y+8)],'#172f3d')
            self.line([(mid+12,y-7),(mid+12,y+7),(mid+3,y),(mid+12,y-7)],'#172f3d');self.line([(mid+3,y-8),(mid+3,y+8)],'#172f3d');self.line([(mid-3,y),(mid+3,y)],'#172f3d');self.line([(mid+12,y),(mid+16,y)],'#172f3d')
        else:
            self.line([(mid-16,y),(mid-7,y)],'#172f3d');self.line([(mid-7,y-8),(mid-7,y+8),(mid+7,y),(mid-7,y-8)],'#172f3d');self.line([(mid+7,y-9),(mid+7,y+9)],'#172f3d',1.2);self.line([(mid+7,y),(mid+16,y)],'#172f3d')
            if k=='zener':self.line([(mid+4,y-11),(mid+7,y-9),(mid+7,y+9),(mid+10,y+11)],'#172f3d')
            if k=='led':
                for dx in (0,7):
                    self.line([(mid+dx-2,y-10),(mid+dx+5,y-17)],'#172f3d');self.line([(mid+dx+1,y-17),(mid+dx+5,y-17),(mid+dx+5,y-13)],'#172f3d')
        self.text(mid,y-24,ref,8.4,True,anchor='middle');self.text(mid,y+23,c['value'],8,anchor='middle')
        self.text(mid-21,y+12,ps[0],6.5,anchor='end');self.text(mid+21,y+12,ps[1],6.5)
    def chip(self,ref,x,y,w=500,pitch=16,pin_subset=None,suffix=''):
        if components[ref]['kind']=='mos':return self.mos(ref,x,y,w)
        if components[ref]['kind']=='shunt':return self.shunt(ref,x,y,w)
        if components[ref]['kind'] in ('relay','relaypower'):return self.relay(ref,x,y,w)
        if components[ref]['kind']=='switch':return self.switch(ref,x,y,w)
        c=components[ref];self.mark(ref);ps=list(pin_subset or c['pins']);N=math.ceil(len(ps)/2);left=ps[:N];right=ps[N:];bodyw=max(110,w-284);bodyx=x+(w-bodyw)/2;bodyy=y+30;height=max(45,N*pitch+20)
        self.text(x+w/2,y,ref+suffix+'  '+c['value'],10,True,anchor='middle');self.rect(bodyx,bodyy,bodyw,height)
        for side,arr in [('left',left),('right',right)]:
            for i,p in enumerate(arr):
                yy=bodyy+16+i*pitch;func=c.get('functions',{}).get(p,p);label=pn(ref,p)
                bx=bodyx if side=='left' else bodyx+bodyw;tx=bx-9 if side=='left' else bx+9;end=bx-20 if side=='left' else bx+20
                self.line([(bx,yy),(end,yy)]);self.label(end,yy,label,side,7.5)
                self.text(bx+(5 if side=='left' else -5),yy+3,func,7.7,anchor='start' if side=='left' else 'end')
                number=c.get('numbers',{}).get(p,str(p))
                if number.isdigit():self.text(tx,yy-3,number,6.4,anchor='middle')
                if label=='NC':self.label(end,yy,label,side)
        return bodyy+height
    def contact(self,ref,x,y,w,com,nc,no=None,closed=True):
        cx=x+w/2;left=x+18;right=x+w-18
        self.line([(left,y),(cx-26,y)]);self.circle(cx-26,y,2)
        if pn(ref,com)=='NC':self.label(left,y,'NC')
        else:self.text(left,y-10,pn(ref,com),7.5,color='#15538b')
        pc=components[ref].get('numbers',{}).get(com,com);self.text(cx-42,y+14,pc,7,anchor='end')
        if no is None:
            self.circle(cx+26,y,2);self.line([(cx+28,y),(right,y)])
            self.line([(cx-24,y),(cx+23,y if closed else y-16)],'#172f3d',1.2)
            self.text(right,y-10,pn(ref,nc),7.5,color='#15538b',anchor='end');self.text(cx+43,y+14,components[ref].get('numbers',{}).get(nc,nc),7)
        else:
            self.line([(cx-24,y),(cx+23,y-16 if closed else y+16)],'#172f3d',1.2)
            for pin,dy in ((nc,-18),(no,18)):
                self.circle(cx+26,y+dy,2);self.line([(cx+28,y+dy),(right,y+dy)])
                nn=pn(ref,pin)
                if nn=='NC':self.label(right,y+dy,'NC')
                else:self.text(right,y+dy-5,nn,7.5,color='#15538b',anchor='end')
                self.text(cx+43,y+dy+12,components[ref].get('numbers',{}).get(pin,pin),7)
    def coil(self,ref,x,y,w,plus,minus):
        cx=x+w/2
        self.line([(x+18,y),(cx-24,y)]);self.rect(cx-24,y-9,48,18)
        for dx in (-15,-5,5,15):self.line([(cx+dx-3,y+7),(cx+dx+3,y-7)],'#172f3d')
        self.line([(cx+24,y),(x+w-18,y)])
        self.text(x+18,y-12,pn(ref,plus),7.5,color='#15538b');self.text(x+w-18,y-12,pn(ref,minus),7.5,color='#15538b',anchor='end')
        nums=components[ref].get('numbers',{});self.text(cx-37,y+16,nums.get(plus,plus)+' +',7,anchor='end');self.text(cx+37,y+16,nums.get(minus,minus)+' -',7)
    def relay(self,ref,x,y,w):
        self.mark(ref);self.text(x+w/2,y,ref+'  '+components[ref]['value'],10,True,anchor='middle')
        if ref=='KPWR':
            self.coil(ref,x,y+50,w,'86','85');self.contact(ref,x,y+119,w,'30','87',closed=False);return y+150
        self.coil(ref,x,y+45,w,'COIL_PLUS','COIL_MINUS')
        self.contact(ref,x,y+112,w,'COM_A','NC_A','NO_A')
        self.contact(ref,x,y+192,w,'COM_B','NC_B','NO_B')
        return y+228
    def switch(self,ref,x,y,w):
        self.mark(ref);self.text(x+w/2,y,ref+'  '+components[ref]['value'],10,True,anchor='middle')
        if ref=='JP_AUX':
            self.contact(ref,x,y+63,w,'COM_A','HI_A','LO_A');self.contact(ref,x,y+150,w,'COM_B','HI_B','LO_B');return y+190
        if ref in ('SW_LOG1','SW_LOG2'):
            self.contact(ref,x,y+57,w,'COM_A','NC_A');self.contact(ref,x,y+124,w,'COM_B','NC_B');return y+150
        if ref=='SW_STOP':
            self.contact(ref,x,y+47,w,'COM_NC','NC');self.contact(ref,x,y+108,w,'COM_NO','NO',closed=False);return y+125
        self.contact(ref,x,y+60,w,'COM','TEST_NO' if ref=='SW_MODE' else 'NO',closed=False);return y+90
    def mos(self,ref,x,y,w):
        self.mark(ref);cx=x+w/2;cy=y+78
        self.text(cx,y,ref+'  2N7002 / SOT-23',10,True,anchor='middle')
        self.line([(cx-15,cy-16),(cx-15,cy+16)],'#172f3d',1.3)
        self.line([(cx-9,cy-19),(cx-9,cy-8)],'#172f3d',1.3);self.line([(cx-9,cy-5),(cx-9,cy+5)],'#172f3d',1.3);self.line([(cx-9,cy+8),(cx-9,cy+19)],'#172f3d',1.3)
        self.line([(cx-9,cy-14),(cx+15,cy-14),(cx+15,cy-36)],'#172f3d');self.line([(cx-9,cy+14),(cx+15,cy+14),(cx+15,cy+36)],'#172f3d')
        self.line([(cx-75,cy),(cx-15,cy)]);self.label(cx-75,cy,pn(ref,'1'),'left');self.text(cx-39,cy-4,'1 G',7)
        self.line([(cx+15,cy-36),(cx+73,cy-36)]);self.label(cx+73,cy-36,pn(ref,'3'),'right');self.text(cx+20,cy-40,'3 D',7)
        self.line([(cx+15,cy+36),(cx+73,cy+36)]);self.label(cx+73,cy+36,pn(ref,'2'),'right');self.text(cx+20,cy+32,'2 S',7)
        return cy+40
    def shunt(self,ref,x,y,w):
        self.mark(ref);cx=x+w/2;cy=y+69
        self.text(cx,y,ref+'  '+components[ref]['value'],10,True,anchor='middle')
        self.rect(cx-19,cy-7,38,14);self.line([(cx-100,cy),(cx-19,cy)]);self.line([(cx+19,cy),(cx+100,cy)])
        self.label(cx-100,cy,pn(ref,'P1'),'left');self.label(cx+100,cy,pn(ref,'P2'),'right');self.text(cx-53,cy-5,'P1',7);self.text(cx+44,cy-5,'P2',7)
        self.line([(cx-19,cy),(cx-19,cy+37),(cx-100,cy+37)]);self.line([(cx+19,cy),(cx+19,cy+37),(cx+100,cy+37)])
        self.dot(cx-19,cy);self.dot(cx+19,cy);self.label(cx-100,cy+37,pn(ref,'K1'),'left');self.label(cx+100,cy+37,pn(ref,'K2'),'right');self.text(cx-53,cy+33,'K1',7);self.text(cx+44,cy+33,'K2',7)
        return cy+45
    def finish(self,total):
        self.line([(25,778),(W-25,778)],'#153b51',1)
        self.text(28,795,'EGRLab v4 / S1 | 22.09.2026 | A3 poziomo | identyczne etykiety = połączenie elektryczne',8)
        self.text(28,812,'Moduły kupne pokazano przez ich zaciski. Widok pinów IC od góry. Odbiór sprzętu wg V4 nadal wymagany.',8)
        self.text(W-28,808,f'{self.index:02d} / {total:02d}',12,True,anchor='end')
        self.svg.append('</svg>');(OUT/'svg'/f'{self.index:02d}.svg').write_text(''.join(self.svg),encoding='utf-8');self.pdf.showPage()

pages=[]
def page(title,fn,sub=''):pages.append((title,fn,sub))
def grid(d,refs,y=130,cols=3,row=72):
    gap=32;w=(W-80-gap*(cols-1))/cols
    for i,ref in enumerate(refs):d.two(ref,40+(i%cols)*(w+gap),y+(i//cols)*row,w)
def chips(d,refs,y=110):
    for i,ref in enumerate(refs):d.chip(ref,40+(i%2)*570,y+(i//2)*250,530)

def intro(d):
    d.text(40,112,'Pełny schemat połączeń urządzenia w architekturze modułowej V4',21,True)
    d.note(40,146,'Rysunki obejmują zasilanie, interlock, watchdog, bramki, przekaźniki, motor, pomiary, ADC, ESP32, CAN, temperatury, SD oraz trzy adaptery. Węzły łączy się po etykietach również pomiędzy arkuszami.',155,11)
    y=217
    for i,(title,_,_) in enumerate(pages[1:],2):
        col=0 if i<=11 else 1;rowi=i-2 if col==0 else i-12
        d.text(45+col*565,y+rowi*30,f'{i:02d}  {title}',10)
    d.section(40,574,'Jak czytać schemat',1100)
    d.note(40,603,'Zielona linia: przewód. Niebieska etykieta: nazwa sieci. Kropka: połączenie. Krzyżyk: pin celowo niepodłączony. AGND / DGND / PGND łączą się wyłącznie w GND_STAR na arkuszu 02. NC nigdy nie jest wspólną siecią.',160)
    d.note(40,648,'G6K: styki pokazane bez zasilania cewki. M1/M2/M3/M4/M5, TC1/TC2 i SD1 są gotowymi modułami - zaciski oznaczono nazwami na płytkach. Ich elektroniki fabrycznej nie buduje się ponownie według tych arkuszy.',160)
    d.note(40,693,'S1 doprecyzowuje zapisy V4: dodaje pominięte w CSV kondensatory VMOTOR, pola zworek, LED i jednoznaczne zakończenia. Szczegóły oraz otwarte punkty montażowe: UWAGI-S1.md. To schemat, nie projekt PCB ani potwierdzenie działania egzemplarza.',160)
page('Spis arkuszy i legenda',intro)

def power(d):
    d.section(40,95,'Wejście 12 V i odcięcie przepięcia',1080)
    d.chip('J_PWR',45,126,440);d.chip('M5',595,126,535)
    grid(d,['F1','D1','F2','F3'],y=301,cols=2,row=76)
    d.chip('M3',45,427,475);d.chip('M4',615,427,475)
    grid(d,['R_FILT','C_A'],y=610,cols=2)
    d.note(40,660,'M5: J1=wejście +, J3=masa wejścia, J2=wyjście +, J4=masa wyjścia. J6 2-3 = input cutoff. Dzielnik OVP ma TRZY rezystory: R8=9,10 kΩ, R3=38,3 kΩ, R4=3,48 kΩ. Szczegóły modyfikacji fabrycznego EVM: arkusz 23.',156)
    d.note(40,706,'OVP nominalnie 18,00 V; pomiar odbiorczy 17,5-18,5 V. F1=5 A dla bazowego EVM. AGND, DGND i PGND prowadź osobnymi powrotami do GND_STAR = J_PWR.2 = B- akumulatora. OBD 4/5/16 pozostają NC.',156)
page('Zasilanie: wejście, OVP i przetwornice',power)

def interlock(d):
    d.section(40,95,'Fizyczna pętla interlock i niezależne styki diagnostyczne',1080)
    chips(d,['SW_MODE','SW_LOG1','SW_LOG2','SW_TEST'],y=132)
    d.chip('SW_STOP',40,620,530)
    d.note(660,620,'Łańcuch: 3V3_IO -> SW_MODE -> LOG1.A NC -> LOG2.A NC -> T.10 -> mostek w adapterze -> T.11 -> INTERLOCK. Wyjęcie T albo włożenie L1/L2 rozłącza sprzętowe zezwolenie.',64)
    d.note(660,701,'B4 LOGGER_CLEAR=1 oznacza oba gniazda LOGGER puste. Styki A/B nie są elektrycznie połączone. Pull-downy wejść: arkusz rezystorów pomocniczych.',64)
page('Interlock oraz STOP',interlock)

def watchdog(d):
    d.chip('U5',40,105,530);d.chip('U7',610,105,530)
    d.chip('U8',40,364,530)
    d.chip('U9',610,364,530)
    grid(d,['R_SUP_PU','R_WD','C_WD','R_ARM_PU','C_ARM','R_ARM_SER'],y=644,row=72)
page('Supervisor, watchdog i zatrzask ARM',watchdog)

def permits(d):
    chips(d,['U10','U12'],y=112)
    for j,ref in enumerate(('Q8','Q9','Q10')):d.chip(ref,28+j*389,355,365)
    grid(d,['R_SAFE_PU','R_SAFE_PD','Q8_PD','Q9_PD','Q10_PD'],y=530,row=75)
    d.note(40,700,'MOTOR_PERMIT = HW_ARMED & MCU_ARM & INTERLOCK. PWM_OUT = PWM & MOTOR_PERMIT. SENSOR_PERMIT = SENSOR_ENABLE & TEST_KEY & INTERLOCK & SAFE_N. SAFE_N: wyłącznie wyjścia open collector / otwarte dreny.',160)
    d.note(40,741,'SUP_N jest odrębną siecią. CT U5 jest NC (nom. 20 ms). Po błędzie wymagane nowe naciśnięcie ARM.',160)
page('Bramki zezwolenia i otwarte dreny SAFE_N',permits)

def comparators(d):
    chips(d,['U4','U6'],y=110)
    d.chip('U13',40,315,530)
    grid(d,['R_OC_LT','R_OC_LB','R_OC_HT','R_OC_HB','R_RAIL_T','R_RAIL_B','R_RAIL_LT','R_RAIL_LB','R_RAIL_HT','R_RAIL_HB'],y=501,row=66)
    d.note(625,323,'U4: okno prądu nominalnie ±4 A przy RSH=5 mΩ i INA gain=50. U6: okno 5V_A 4,75-5,25 V. U6 i ADR4525 zasilane z 5V_SYS, niezależnie od nadzorowanej 5V_A.',64)
page('Komparatory prądu i napięcia',comparators)

def relay_driver(d):
    d.chip('U18',40,110,535)
    d.chip('KPWR',620,110,500)
    grid(d,['D4','D5','D6','D7','D8','D11','D12'],y=398,row=81)
    d.note(40,680,'U18 COM (10) pozostaje NC. Wszystkie cewki sygnałowe: plus do 5V_SYS; osobne diody D4-D8 katodą do plusa. KMEAS1-3 mają wspólne wyjście O1. KCUR: O2; KSENSOR: O3. O4 steruje cewką KPWR.',156)
    d.note(40,723,'KPWR: 86 do VPROT; 85 do O4. D11: A na 85, K do K D12; D12 Zener 18 V: A do 86. Nie zastępuj tego zwykłą diodą równoległą. Cewka bez wbudowanej diody.',156)
page('Sterownik i gaszenie cewek',relay_driver)

def hbridge(d):
    d.chip('M2',40,110,590);d.chip('RSH_T',665,110,465)
    grid(d,['F4','C_BULK','R_BLEED','D2','C_MOTOR_HF','C_MOTOR_MF','R_PWM','R_INA','R_INB','R_PWM_PD','R_INA_PD','R_INB_PD'],y=382,row=84)
    d.note(40,727,'KPWR.30 z F4; KPWR.87=VMOTOR. VDD nośnika M2 z MOTOR_PERMIT. Motor: OUTA -> RSH_T -> T.1 -> EGR1; OUTB -> T.2 -> EGR3. Nie łącz wyjść M2 z ECU.',155)
page('Mostek H i zasilanie motoru TEST',hbridge)

def current(d):
    chips(d,['U2','U3'],y=110)
    d.chip('RSH_L',40,319,530);d.chip('KCUR',610,319,530)
    grid(d,['RC1','RC2','RC3','RC4','RO1','RO2','CI_ADC'],y=585,row=72)
    d.note(660,725,'I=(Vout-Vzero)/0,25 V/A. Kelvin K1 przy P1, K2 przy P2; osobne ścieżki pomiarowe.',65)
page('Pomiary prądu TEST / LOGGER',current)

def sensor(d):
    chips(d,['U11','KSENSOR'],y=110)
    grid(d,['R_ILIM','C_SIN','C_SOUT','R_PU_SENSOR_FAULT_N'],y=385,cols=2,row=83)
    for j,ref in enumerate(('JP4','JP5','JP6')):d.chip(ref,28+j*389,567,365)
    d.note(40,730,'TPS2553: ok. 0,1 A przy 232 kΩ - nie 20 mA. Dwie zwory: supply 1-2; GND 2-3; feedback bez zwory. Zworki przekładaj bez zasilania. Mapowanie po pasywnym IDENTIFY.',158)
page('Zasilanie sensora i zworki TEST',sensor)

def front(d):
    for j,ref in enumerate(('KMEAS1','KMEAS2','KMEAS3')):d.chip(ref,25+j*389,112,367)
    grid(d,['CF1','CF2','CF3','CF4','CF5','RB1','RB2'],y=391,row=87)
    d.note(40,702,'Styki NO: TAP_P1/3/4/5/6. COM: ADC_CH1...CH5. Wszystkie NC i nieużyty drugi biegun KMEAS3 pozostają NC. Cewki KMEAS wspólne: MEAS_COIL_LOW / 5V_SYS. Przełącza się wyłącznie odczepy, nigdy obwody ECU.',153)
page('Odczepy EGR i KMEAS',front)

def aux(d):
    chips(d,['JP_AUX','J_AUX'],y=111)
    grid(d,['RA1','RA2','RA3','RA4','RB4','CF7','RV1','RV2','RB3','CF6'],y=362,row=88)
    d.note(40,728,'AUX LO: drugi biegun odłącza dolny koniec RB4. LO nie jest zakresem dla 12 V. Ekran J_AUX do AGND; mierzoną masę sensora podłączaj wyłącznie do HOT przez rezystory wejściowe.',155)
page('AUX HI/LO i pomiar VPROT',aux)

def adc(d):
    d.chip('U1',40,107,700,pitch=17)
    for i,ref in enumerate(('C_REGCAP_A','C_REGCAP_D','C_ADC_REF','C_REFCAP')):d.two(ref,805,192+i*104,335)
    d.note(823,640,'Podstawowa konfiguracja: OS[2:0]=111, PAR/SER=1, STBY=1, RANGE=1, WR=1; REFSEL=1. SW mode: SPI mode 2.',43)
    d.note(823,710,'REGCAP_A i REGCAP_D: osobne 1 µF. REFCAPA/B wspólne. Wszystkie VxGND do AGND.',43)
page('AD7606B: wszystkie 64 piny',adc)

def mcu(d):
    chips(d,['M1','U17'],y=111)
    grid(d,['R_PU_I2C_SDA','R_PU_I2C_SCL','R_LED','LED1'],y=488,cols=2,row=88)
    d.note(40,667,'M1: zasilanie przez 5V, masa DGND. Nie zwieraj 3V3 płytki Waveshare z 3V3_IO. Przed podłączeniem potwierdź sekwencję szyn oraz brak zasilania pasożytniczego przez GPIO. USB VBUS odłączone przy zasilaniu zewnętrznym.',154)
    d.note(40,719,'GPIO19/20 i 43/44 pozostają na płytce dla USB / CH343. GPIO38 wymaga odłączenia DIN pokładowego RGB. MCP: adres 0x20; A7/B7 jako wyjścia. Pozostałe nieużywane piny NC.',154)
page('ESP32-S3 i ekspander MCP23017',mcu)

def peripherals(d):
    chips(d,['TC1','TC2','SD1','U16'],y=111)
    d.chip('D3',40,609,470);d.chip('J_OBD',610,609,530)
    d.note(40,747,'CAN: S=3V3_IO, TWAI listen-only. Brak 120 Ω. OBD 4/5/16 NC; odniesienie przez J_PWR.2. TC jako kompletne moduły z filtrami wejść.',156)
page('Termopary, SD oraz CAN/OBD',peripherals)

def panel(d):
    for j,ref in enumerate(('J_TEST','J_L1','J_L2')):d.chip(ref,25+j*389,111,367,pitch=24)
    d.chip('J_SCOPE',40,414,480);d.chip('SW_MARK',620,414,480)
    d.chip('SW_ARM',40,604,480);d.chip('J_BYPASS',620,604,480)
page('Złącza panelowe i przyciski',panel)

def adapter_page(which):
    def body(d):
        idx={'T':0,'L1':1,'L2':2}[which]
        for j,op in enumerate((1,3,4,5,6)):
            ref='RM' if j<2 else 'RS';n=idx*(4 if j<2 else 6)+(j*2 if j<2 else (j-2)*2)+1
            for k in range(2):d.two(ref+str(n+k),40+k*570,170+j*107,530)
        if which=='T':
            d.two('JT_LOOP',40,672,530)
            msg='Adapter T: OEM1/3 z motoru; OEM4/5/6 do środkowych pinów JP4/5/6. T.10-T.11 zwarte tylko we wtyku. T.12 NC. Rezystory montuj bezpośrednio przy EGR, przed długim przewodem. T musi mieć inny klucz niż L1/L2.'
        elif which=='L1':msg='Adapter L1: ECU1 -> panel L1.1 -> RSH_L -> panel L1.2 -> EGR1. ECU3/4/5/6 bezpośrednio do tych samych pinów EGR. Odczepy po stronie EGR. Sygnały sensorowe pozostają zasilane tylko z ECU. L1.12 ekran po stronie urządzenia; bez kontaktu przy EGR.'
        else:msg='Adapter L2: pięć sond back-probe na 1/3/4/5/6 bez rozpinania złącza. Brak własnego zasilania sensora i brak przewodów mocy. Ustaw bypass 1. L2.12 ekran po stronie urządzenia. Jednocześnie tylko jeden adapter T/L1/L2.'
        d.note(40,724,msg,156)
    return body
for which in ('T','L1','L2'):page('Adapter '+which+': rezystory przy EGR',adapter_page(which))

assigned={ref for ref in components if ref.startswith(('C_DEC_','C_DCDC_'))}
# The lists below intentionally expose every passive, including the small pull-downs.
auxrefs=['R_PD_TEST_KEY','R_PD_INTERLOCK','R_PD_LOGGER_CLEAR','R_PD_TEST_PRESENT','R_PD_STOP_PRESSED','R_MCU_PD','R_HW_PD','R_HEART_PD','R_DEFAULT_MEAS_EN','R_DEFAULT_MEAS_BANK','R_DEFAULT_SENSOR_PERMIT','R_DEFAULT_MOTOR_PERMIT','R_DEFAULT_SENSOR_ENABLE','R_DEFAULT_MOTOR_INA','R_DEFAULT_MOTOR_INB','R_PU_ADC_CS','R_PU_SD_CS','R_PU_TC1_CS','R_PU_TC2_CS','R_SCOPE','R_MARK','C_MARK']
page('Rezystory pomocnicze i stany domyślne',lambda d:grid(d,auxrefs,y=133,row=78))
filters=['R_IFILT','C_IFILT','C_OC_LOW','C_OC_HIGH','C_RAIL_LOW','C_RAIL_HIGH','C_REF_IN','C_REF_OUT','C_CAN_VIO']
page('Filtry okien i odniesienia',lambda d:(grid(d,filters,y=160,row=122),d.note(40,650,'I_FILT jest pobierane zawsze z INA TEST (I_T_OUT), przed KCUR. Komparator prądu nie zależy od banku ADC. Wyjścia komparatorów są połączone bezpośrednio z SAFE_N.',154)))
decouplers=sorted(assigned)
page('Odsprzęganie układów i modułów',lambda d:(grid(d,decouplers,y=130,row=76),d.note(40,750,'100 nF przy danym pinie zasilania, krótki powrót do właściwej masy. Kondensatory wejść DC/DC przy module; napięcia znamionowe zgodne z BOM.',155)))

def completion(d):
    grid(d,['M5_R8','M5_R3','M5_R4'],y=148,row=85)
    d.note(40,209,'M5_R8/R3/R4 oznaczają elementy WEWNĄTRZ modułu TI. W rewizji SLVUBU3A fabrycznie: R8=9,1 kΩ, R3=91 kΩ, R4=3,48 kΩ. Górna gałąź to R8+R3. S1: R3=38,3 kΩ; R8 i R4 pozostają nominalnie jak wyżej (zalecana tolerancja 0,1%).',154)
    d.note(40,263,'M5_OV -> pin 5 (OV) układu U1 na EVM. M5_VIN_MON to istniejący węzeł pomiędzy R8 i R3. J6 2-3 wybiera napięcie wejściowe. Nie dodawaj drugiego dzielnika obok istniejącego. Vtrip=1,231*(1+(9,1+38,3)/3,48)=17,998 V. Ostateczny próg ustaw pomiarem.',154)
    chips(d,['OEM_T','OEM_L1','OEM_L2','OEM_ECU'],y=366)
    d.note(40,756,'Numery OEM dotyczą oznaczeń obudowy złącza, nie lustrzanego widoku wiązki. Ustal 5V/GND przez IDENTIFY przed TEST.',157)
page('Doprecyzowanie OVP i złącza OEM',completion)

pdf=canvas.Canvas(str(OUT/'EGRLab-v4-schemat-S1.pdf'),pagesize=(W,H),pageCompression=1)
pdf.setTitle('EGRLab v4 - schemat elektryczny S1');pdf.setAuthor('Projekt EGRLab')
for i,(title,fn,sub) in enumerate(pages,1):
    pdf.bookmarkPage('sheet'+str(i));pdf.addOutlineEntry(f'{i:02d} {title}','sheet'+str(i),level=0)
    d=Drawing(pdf,i,title,sub);fn(d);d.finish(len(pages))
pdf.save()
missing=set(components)-covered
assert not missing,sorted(missing)
(OUT/'dane/components.json').write_text(json.dumps(components,ensure_ascii=False,indent=2),encoding='utf-8')
with (OUT/'dane/piny-sieci.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f,delimiter=';');w.writerow(['ref','value','pin','terminal_name','function','net','sheet'])
    for ref,c in components.items():
        for p,n in c['resolved'].items():w.writerow([ref,c['value'],c.get('numbers',{}).get(p,p),p,c.get('functions',{}).get(p,p),n,','.join(str(i) for i,rr in drawn if rr==ref)])
with (OUT/'dane/indeks-elementow.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f,delimiter=';');w.writerow(['ref','value','sheet']);w.writerows((ref,c['value'],','.join(str(i) for i,rr in drawn if rr==ref)) for ref,c in components.items())
(OUT/'dane/pokrycie.json').write_text(json.dumps(dict(sheets=len(pages),components=len(components),pins=sum(len(c['pins']) for c in components.values()),all_components_drawn=not missing,missing=list(missing)),indent=2),encoding='utf-8')
(OUT/'dane/zrodla-sha256.json').write_text(json.dumps({str(p.relative_to(SOURCE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [SOURCE/'hardware'/n for n in ('connections.csv','ic-pins.csv','pinout.csv','connectors.csv','BOM.csv')]},indent=2),encoding='utf-8')
with (OUT/'dane/aliasy-sieci.csv').open('w',encoding='utf-8-sig',newline='') as f:
    wr=csv.writer(f,delimiter=';');wr.writerow(['nazwa_wejsciowa','siec_wspolna'])
    for group,labels in sorted(names.items()):
        for label in sorted(labels):wr.writerow([label,canon[group]])
print(f'{len(pages)} sheets, {len(components)} components, {sum(len(c["pins"]) for c in components.values())} terminals; coverage complete.')

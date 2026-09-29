"""One-time migration to editable KiCad schematics, separate project per PCB.
Not a PCB layout. Pin roles are independent of project net names. Preserve reports
and migration map; never silently regenerate over manually edited schematics.
"""
import argparse, collections, csv, json, math, re, uuid, functools, shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1]
q=lambda s:json.dumps(str(s),ensure_ascii=False)
u=lambda s:str(uuid.uuid5(uuid.NAMESPACE_URL,'egrlab-6.1/'+s))
font='(effects (font (size 1 1)))'
def forms(text):
    toks=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',text);idx=0
    def parse():
        nonlocal idx
        t=toks[idx];idx+=1
        if t=='(':
            a=[]
            while toks[idx]!=')':a.append(parse())
            idx+=1;return a
        return json.loads(t) if t.startswith('"') else t
    return parse()
def sub(x,name):return [y for y in x if isinstance(y,list) and y and y[0]==name]
def one(x,name):return next(y for y in x if isinstance(y,list) and y and y[0]==name)
@functools.lru_cache(maxsize=None)
def official(libroot,lib,name):
    tree=forms((libroot/(lib+'.kicad_sym')).read_text(encoding='utf-8'))
    by={x[1]:x for x in sub(tree,'symbol')}
    def get(n):
        x=by[n];p={}
        if sub(x,'extends'):p.update(get(one(x,'extends')[1]))
        for unit in sub(x,'symbol'):
            for pin in sub(unit,'pin'):
                p[one(pin,'number')[1]]=(one(pin,'name')[1],pin[1])
        return p
    return get(name)

def roles(c,library):
    v=c['value'];pins=c['pins'];part={p:(p,'passive') for p in pins};src='Passive/contact/module boundary; see review limitations'
    for word,lib,name in [('74LVC125','74xx','74LVC125'),('SN74HC08','74xx','74HC00'),('SN74HC14','74xx','74HC14'),('SN74HC74','74xx','74HC74'),('SN74HC139','74xx','74LS139'),('CD74HC123','74xx','74HC123'),('MCP120','Power_Supervisor','MCP120-xxxDxTO'),('LM2903','Comparator','LM2903'),('LM2936','Regulator_Linear','LM2936-5.0_TO92'),('TL431','Reference_Voltage','TL431LP'),('MCP3201','Analog_ADC','MCP3201'),('MCP1525','Reference_Voltage','MCP1525-TO'),('INA240','Amplifier_Current','INA240A2D'),('MCP6022','Amplifier_Operational','MCP6022'),('ADR4525','Reference_Voltage','ADR4525'),('TPS3808','Power_Supervisor','TPS3808DBV')]:
        if word in v:
            p=official(library,lib,name);part.update({n:p[n] for n in pins if n in p});src=f'KiCad 10.0.6 {lib}:{name}'
            if word=='SN74HC08':src+=' (HC00 pin roles, same gate pin numbering; function remains AND)'
            break
    def define(names,typ):
        for n,label in names.items():
            if str(n) in pins:part[str(n)]=(label,typ)
    if 'AD7606B' in v:
        src='ADI AD7606B Rev B, table 6'
        define({n:'AGND' for n in [2,26,30,31,32,33,35,40,41,43,46,47,50,52,54,56,58,60,62,64]},'power_in')
        define({1:'AVCC',37:'AVCC',38:'AVCC',48:'AVCC',23:'VDRIVE'},'power_in')
        define({3:'OS0',4:'OS1',5:'OS2',6:'PAR_SER',7:'RANGE',8:'STBY_N',9:'CONVST',10:'WR_N',11:'RESET',12:'RD_SCLK',13:'CS_N',29:'DB11_SDI',34:'REFSELECT',49:'V1',51:'V2',53:'V3',55:'V4',57:'V5',59:'V6',61:'V7',63:'V8'},'input')
        define({14:'BUSY'},'output');define({15:'FRSTDATA',24:'DB7_DOUTA',25:'DB8_DOUTB',27:'DB9_DOUTC',28:'DB10_DOUTD'},'tri_state')
        define({n:'DB'+str(n-16)+'_unused_serial' for n in range(16,23)},'input')
        define({30:'DB12_unused_serial',31:'DB13_unused_serial',32:'DB14_unused_serial',33:'DB15_unused_serial'},'input')
        define({36:'REGCAP',39:'REGCAP'},'power_out')
        define({42:'REFIN_OUT',44:'REFCAP',45:'REFCAP'},'passive')
    if 'TPS2553' in v:
        src='TI TPS2553 SLVS841F pin functions'
        define({1:'IN',2:'GND'},'power_in');define({3:'EN',5:'ILIM'},'input');define({4:'FAULT_N'},'open_collector');define({6:'OUT'},'power_out')
    if 'TBD62083' in v:
        define({n:'IN'+str(n) for n in range(1,9)},'input');define({n:'OUT'+str(19-n) for n in range(11,19)},'open_collector');define({9:'GND'},'power_in');define({10:'COM'},'passive');src='Toshiba TBD62083APG pin numbering'
    if 'MCP1702' in v:define({1:'GND',2:'VIN'},'power_in');define({3:'VOUT'},'power_out');src='Microchip MCP1702 TO92 DS22008E'
    if 'TSR 2-' in v:define({1:'VIN',2:'GND','VIN':'VIN','GND':'GND'},'power_in');define({3:'VOUT','VOUT':'VOUT'},'power_out');src='Traco TSR2 pin convention'
    if 'MCP23017' in v:
        define({9:'VDD',10:'VSS'},'power_in');define({11:'NC',14:'NC'},'no_connect')
        define({12:'SCL',15:'A0',16:'A1',17:'A2',18:'RESET_N'},'input');define({13:'SDA'},'bidirectional');define({19:'INTB',20:'INTA'},'open_collector')
        define({n:'GPIO' for n in [1,2,3,4,5,6,7,8,21,22,23,24,25,26,27,28]},'bidirectional');src='Microchip MCP23017 SPDIP28'
    if 'Waveshare' in v:define({'3V3':'3V3'},'power_out')
    if 'TCAN1051' in v:
        define({1:'TXD',5:'VIO',8:'S'},'input');define({2:'GND',3:'VCC'},'power_in');define({4:'RXD'},'output');define({6:'CANL',7:'CANH'},'bidirectional');src='TI TCAN1051VDRQ1 pin functions'
    if 'TLV1702' in v:
        define({1:'OUT1',7:'OUT2'},'open_collector');define({2:'IN1-',3:'IN1+',5:'IN2+',6:'IN2-'},'input');define({4:'VEE',8:'VCC'},'power_in');src='TI TLV1702 DGK'
    return part,src

def footprint(c):
    v=c['value'];b=c['board'];r=c['ref']
    if b!='P01':return ''
    if r in ['U1','U3','U4'] or r.startswith('Q') and r!='Q1':return 'Package_TO_SOT_THT:TO-92_Inline_Wide'
    if r in ['Q1','D2']:return 'Package_TO_SOT_THT:TO-220-3_Vertical'
    if r=='U2':return 'Package_DIP:DIP-8_W7.62mm'
    if r=='RV1':return 'Potentiometer_THT:Potentiometer_Bourns_3296W_Vertical'
    if c['kind']=='R':return 'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal' if r not in ['R1','R23'] else ''
    if v=='1N4148':return 'Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal'
    if r=='LED1':return 'LED_THT:LED_D3.0mm'
    return ''

def generate(library):
    out=R/'eda';out.mkdir(exist_ok=True)
    assert not list(out.glob('P*/*.kicad_sch')),'EDA exists: use a new import directory or review manual changes first'
    C=json.loads((R/'hardware/components.json').read_text(encoding='utf-8'));mapping=[];coverage=[];all_lib=[]
    # Explicit source declarations at module boundary or AFTER a reviewed filter.
    # These do not establish any inter-board connection; checks.py does that.
    flag_sources={'P01':{'GND':'BAT return','P01_AUX_IN':'D2 -> R1, filtered input'},'P02':{'GND':'SUPPLY','VIN_DC5':'SUPPLY -> F2','VIN_DC33':'SUPPLY -> F3'},'P03':{'GND':'LV03','5V_SYS':'LV03'},'P04':{'GND':'LV04','3V3_IO':'LV04'},'P05':{'GND':'LV05','3V3_IO':'LV05','5V_SYS':'LV05','5VA_P05':'LV05 -> R_FILT 1R'},'P06':{'GND':'LV06','3V3_IO':'LV06','5VA_P06':'LV06 -> R_AF 1R'},'P07':{'GND':'LV07','3V3_IO':'LV07','5VA_P07':'LV07 -> R_AF 1R'},'P08':{'GND':'LV08','3V3_IO':'LV08','5V_SYS':'LV08'},'P09':{'GND':'LV09','3V3_IO':'LV09'},'P10':{'GND':'LV10','3V3_IO':'LV10','5V_SYS':'LV10'}}
    (out/'power-source-declarations.json').write_text(json.dumps(flag_sources,indent=2),encoding='utf-8')
    for b in sorted({c['board'] for c in C.values()}):
        dest=out/b;dest.mkdir(exist_ok=True);root=u(b);lib=[];symbols=[];labels=[]
        # One expandable sheet per board: no cross-project/global net aliasing.
        items=sorted(((key,c) for key,c in C.items() if c['board']==b),key=lambda t:t[0]);cols=4;heights=[25.4]*cols;max_width=609.6
        for index,(key,c) in enumerate(items):
            pinmeta,source=roles(c,library);coverage.append(dict(component=key,roles_source=source,footprint=footprint(c)))
            logical=list(c['pins']);count=len(logical);rows=math.ceil(count/2);height=max(25.4,rows*2.54+20.32)
            col=min(range(cols),key=lambda i:heights[i]);x=76.2+col*152.4;y=heights[col]+10.16;heights[col]+=height
            # Keep original reference as a visible property; legal, stable EDA ref.
            prefix='U' if c['kind'].lower()=='ic' else 'R' if c['kind'].lower() in ['r','res'] else 'C' if c['kind'].lower() in ['c','cap'] else 'J' if c['kind'] in ['connector','termination','testpad','J'] else 'X'
            ref=prefix+str(index+1);name=key;sid=u(key);fp=footprint(c)
            padmap={p:('2' if p=='A' else '1' if p=='K' else p) for p in logical}
            # Certain symbols use numeric physical pads; the map is checked on export.
            mapping.append(dict(component=key,board=b,eda_ref=ref,pads=padmap))
            h=(rows+1)*2.54
            properties=f'(property "Reference" {q(ref)} (at 0 5.08 0) {font}) (property "Value" {q(c["value"])} (at 0 2.54 0) (effects (font (size 0.8 0.8)))) (property "Footprint" {q(fp)} (at 0 0 0) (effects (font (size 1 1)) hide))'
            body=f'(rectangle (start -17.78 0) (end 17.78 {-h}) (stroke (width 0.254) (type default)) (fill (type background)))'
            pins=[];pinst=[]
            for idx,p in enumerate(logical):
                side=idx//rows;j=idx%rows;px=-20.32 if side==0 else 20.32;py=-(j+1)*2.54;angle=0 if side==0 else 180;nm,typ=pinmeta[p]
                pins.append(f'(pin {typ} line (at {px} {py} {angle}) (length 2.54) (name {q(nm)} (effects (font (size 0.8 0.8)))) (number {q(padmap[p])} (effects (font (size 0.8 0.8)))))')
                pinst.append(f'(pin {q(padmap[p])} (uuid {u(key+"/pin/"+p)}))')
                ax=round(x+px,4);ay=round(y-py,4);net=c['pins'][p]
                if net=='NC':labels.append(f'(no_connect (at {ax} {ay}) (uuid {u(key+"/nc/"+p)}))')
                else:
                    end=round(ax+(-5.08 if side==0 else 5.08),4)
                    labels.append(f'(wire (pts (xy {ax} {ay}) (xy {end} {ay})) (stroke (width 0) (type default)) (uuid {u(key+"/wire/"+p)}))')
                    labels.append(f'(label {q(net)} (at {end} {ay} 0) (effects (font (size 0.9 0.9)) (justify {"right" if side==0 else "left"} bottom)) (uuid {u(key+"/label/"+p)}))')
            lib.append(f'(symbol {q("EGRLab:"+name)} (pin_names (offset 0.5)) (in_bom yes) (on_board yes) {properties} (symbol {q(name+"_0_1")} {body}) (symbol {q(name+"_1_1")} {"".join(pins)}))')
            symbols.append(f'(symbol (lib_id {q("EGRLab:"+name)}) (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid {sid}) (property "Reference" {q(ref)} (at {x} {y-7.62} 0) {font}) (property "Value" {q(c["value"])} (at {x} {y-5.08} 0) (effects (font (size 0.8 0.8)) hide)) (property "Footprint" {q(fp)} (at {x} {y} 0) (effects (font (size 1 1)) hide)) (property "SourceRef" {q(c["ref"])} (at {x} {y-5.08} 0) {font}) {"".join(pinst)} (instances (project {q(b)} (path {q("/"+root)} (reference {q(ref)}) (unit 1)))))')
            labels.append(f'(text {q(c["value"][:65])} (at {x} {y-2.54} 0) (effects (font (size 0.8 0.8))) (uuid {u(key+"/value")}))')
        for fi,(net,why) in enumerate(flag_sources.get(b,{}).items()):
            name=b+'_PWR_'+str(fi);ref='#FLG'+str(fi+1);sid=u(name);x=25.4+fi*76.2;y=max(heights)+5.08
            lib.append(f'(symbol {q("EGRLab:"+name)} (pin_names (offset 0)) (in_bom no) (on_board no) (property "Reference" {q(ref)} (at 0 0 0) {font}) (property "Value" "PWR_FLAG" (at 0 2.54 0) {font}) (symbol {q(name+"_1_1")} (pin power_out line (at 0 0 90) (length 0) (name "source" {font}) (number "1" {font}))))')
            labels.append(f'(label {q(net)} (at {x} {y} 0) (effects (font (size 1 1)) (justify left bottom)) (uuid {u(name+"/label")}))')
            symbols.append(f'(symbol (lib_id {q("EGRLab:"+name)}) (at {x} {y} 0) (unit 1) (in_bom no) (on_board no) (dnp no) (uuid {sid}) (property "Reference" {q(ref)} (at {x} {y} 0) (effects (font (size 1 1)) hide)) (property "Value" "PWR_FLAG" (at {x} {y+2.54} 0) {font}) (pin "1" (uuid {u(name+"/pin")})) (instances (project {q(b)} (path {q("/"+root)} (reference {q(ref)}) (unit 1)))))')
        ymax=math.ceil((max(heights)+30)/25.4)*25.4
        header=f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {root}) (paper "User" {max_width} {ymax}) (title_block (title {q("EGRLab 6.1-rc1 / "+b+" / MIGRATION FOR REVIEW")}) (rev "6.1-rc1"))'
        (dest/(b+'.kicad_sch')).write_text(header+'(lib_symbols '+''.join(lib)+')'+''.join(labels)+''.join(symbols)+')',encoding='utf-8')
        (dest/(b+'.kicad_pro')).write_text('{}',encoding='utf-8')
        (dest/'sym-lib-table').write_text('(sym_lib_table (lib (name "EGRLab") (type "KiCad") (uri "${KIPRJMOD}/../libraries/EGRLab.kicad_sym") (options "") (descr "Pinned migration symbols")))',encoding='utf-8')
        all_lib.extend(s.replace('(symbol "EGRLab:','(symbol "',1) for s in lib)
    vend=out/'libraries';vend.mkdir(exist_ok=True)
    (vend/'EGRLab.kicad_sym').write_text('(kicad_symbol_lib (version 20231120) (generator "kicad_symbol_editor")'+''.join(all_lib)+')',encoding='utf-8')
    fps={x['footprint'] for x in coverage if x['footprint']};flibs=set()
    for fp in fps:
        lib,name=fp.split(':');src=library.parent/'footprints'/(lib+'.pretty')/(name+'.kicad_mod');assert src.exists(),src
        target=vend/(lib+'.pretty');target.mkdir(exist_ok=True);shutil.copy2(src,target/src.name);flibs.add(lib)
    table='(fp_lib_table '+''.join(f'(lib (name {q(n)}) (type "KiCad") (uri "${{KIPRJMOD}}/../libraries/{n}.pretty") (options "") (descr "KiCad 10.0.6 footprint, candidate"))' for n in sorted(flibs))+')'
    for b in {c['board'] for c in C.values()}:(out/b/'fp-lib-table').write_text(table,encoding='utf-8')
    (out/'migration-map.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'pin-role-coverage.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Generated',len(C),'symbols in',len({c['board'] for c in C.values()}),'separate board projects')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--library',type=Path,required=True);a=p.parse_args();generate(a.library)



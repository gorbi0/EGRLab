"""Native KiCad PCB from frozen R3 XML. Placement and critical routes explicit.
Run with KiCad's Python (pcbnew). Never modifies the R3 package.
"""
from pathlib import Path
import pcbnew as p,json,re,math,xml.etree.ElementTree as ET
P=Path(__file__).resolve().parents[1];E=P/'eda'
mm=p.FromMM
def xy(x,y):return p.VECTOR2I(mm(x),mm(y))
def layers(*ids):
    ls=p.LSET()
    for n in ids:ls.AddLayer(n)
    return ls
parts=json.loads((P/'reference/R3-docs/parts.json').read_text())
root=ET.parse(P/'reference/R3-P01.xml').getroot()
b=p.BOARD();b.SetFileName(str(E/'P01.kicad_pcb'));b.SetCopperLayerCount(2)
s=b.GetDesignSettings();s.SetBoardThickness(mm(1.6));s.m_MinClearance=mm(.25);s.m_TrackMinWidth=mm(.3)
s.m_CopperEdgeClearance=mm(.5);s.m_HoleToHoleMin=mm(.3);s.m_HoleClearance=mm(.25)
s.m_ViasMinSize=mm(.8);s.m_MinThroughDrill=mm(.4);s.m_ViasMinAnnularWidth=mm(.2)
s.m_SilkClearance=mm(.15);s.m_MinSilkTextHeight=mm(.8);s.m_MinSilkTextThickness=mm(.12)
s.m_SolderMaskMinWidth=mm(.1);s.m_MinResolvedSpokes=2
net={};pin={}
for n in root.findall('./nets/net'):
    v=p.NETINFO_ITEM(b,n.get('name'),int(n.get('code')));b.Add(v)
    net[n.get('name').split('/')[-1]]=v
    for q in n.findall('node'):pin[q.get('ref'),q.get('pin')]=v
pos={
 'HS1':(55,18,0),'D2':(52.46,22.30,0),'HS2':(108,18,0),'Q1':(105.46,22.30,0),
 'J7':(15,25,0),'J1':(11,43,0),'D1':(14,36,0),'C1':(68,39,0),'C2':(74,39,0),
 'TP1':(113,24.5,0),'TP2':(103,26,0),'LK1':(126,36,0),'J6':(151,32,90),
 'D3':(130,48,0),'C3':(132,57,0),'C4':(144,56,0),'J2':(155,62,90),
 'R28':(130,65,0),'R29':(130,72,0),'LED1':(150,72,0),
 'C6':(100,40,0),'D4':(100,49,0),'C5':(115,42,0),'R27':(90,51,90),
 'Q2':(87.46,57,0),'Q4':(108,57,0),'D9':(101,65,0),'R24':(110,51,0),
 'R25':(110,73,90),'R23':(121,73,90),'R26':(99,73,0),'Q5':(99,79,0),
 'R19':(99,86,0),'R20':(99,94,0),'R22':(94,31,0),
 'Q3':(119,81,0),'R21':(119,60,270),'R17':(116,94,90),'R18':(125,94,90),
 'R1':(8,59,0),'D5':(8,67,0),'C7':(29,67,0),'C8':(30,58,0),'U1':(34,73,180),
 'R2':(8,82,0),'C9':(29,84,0),'C10':(36,83,90),'TP3':(26,53,0),'TP4':(39,86,0),'TP10':(39,94,0),
 'D6':(8,50,0),'R12':(8,91,0),
 'R3':(45,66,270),'U3':(51,88,0),'R4':(50,95,0),'TP5':(50,82,0),'R7':(55,79,0),
 'U2':(78,68,0),'C11':(89.5,68,270),'U4':(70,88,0),'R13':(94,94,90),
 'R5':(50,52,0),'RV1':(70,55,0),'R6':(53,60,0),'C12':(72,66,90),'TP8':(76,61,0),
 'R8':(75,50,270),'R9':(51,68,0),'R10':(55,87,0),'R11':(80,94,90),'C13':(85,84,90),'TP9':(86,90,0),
 'R14':(34,49,0),'D7':(36,40,0),'D8':(41,33,0),'Q6':(42,25,0),
 'R15':(31,34,90),'R16':(34,41,270),'TP6':(45,44,0),'TP7':(34,30,0),'J3':(63,46,0),
 'Q7':(147,85,90),'Q8':(152,94,90),'R30':(134,61,90),'R31':(140,61,90),
 'R32':(149,81,180),'R33':(150,96,180),'J4':(155,76,90),'J5':(143,95,90),
 'J8':(126,88,90),'R34':(130,94,90),
}
over=P/'src/placement.json'
if over.exists():pos.update({k:tuple(v) for k,v in json.loads(over.read_text()).items()})
fmap={}
schroot=re.search(r'\(uuid "?([0-9a-f-]+)',(E/'P01.kicad_sch').read_text()).group(1)
for c in root.findall('./components/comp'):
    ref=c.get('ref');lib,name=c.findtext('footprint').split(':')
    f=p.FootprintLoad(str(E/'libraries'/(lib+'.pretty')),name);assert f,ref
    f.SetReference(ref);f.SetValue(c.findtext('value'));f.SetFPIDAsString(c.findtext('footprint'))
    path='/'+schroot+c.find('sheetpath').get('tstamps')+c.findtext('tstamps').split()[0]
    f.SetPath(p.KIID_PATH(path))
    f.GetField(p.FIELD_T_DATASHEET).SetText(c.findtext('datasheet') or '')
    for field in c.findall('./fields/field'):
        name=field.get('name')
        if name in ['MPN','BaselineRef']:
            ff=p.PCB_FIELD(f,p.FIELD_T_USER,name);ff.SetText(field.text or '');ff.SetVisible(False);f.Add(ff)
    for pad in f.Pads():
        if pad.GetNumber():pad.SetNet(pin[ref,pad.GetNumber()])
    b.Add(f);fmap[ref]=f
for ref in ['HS1','HS2']:
    f=p.FootprintLoad(str(E/'libraries/P01.pretty'),'HS_Fischer_SK129_63.5_STS_D2.8')
    f.SetReference(ref);f.SetValue('SK129-63STS');f.SetFPIDAsString('P01:HS_Fischer_SK129_63.5_STS_D2.8')
    f.SetAttributes(p.FP_THROUGH_HOLE|p.FP_BOARD_ONLY|p.FP_EXCLUDE_FROM_POS_FILES)
    b.Add(f);fmap[ref]=f
for ref,f in fmap.items():
    x,y,ang=pos[ref];f.SetPosition(xy(x,y));f.SetOrientationDegrees(ang)
    f.Value().SetVisible(False);f.Reference().SetTextSize(xy(1,1));f.Reference().SetTextThickness(mm(.15))
    f.Reference().SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T))
    # Readable external labels, refined with placement/silkscreen checks.
    bb=f.GetLayerBoundingBox(layers(p.F_CrtYd))
    f.Reference().SetPosition(xy((p.ToMM(bb.GetLeft())+p.ToMM(bb.GetRight()))/2,p.ToMM(bb.GetTop())-1.1))
for i,(x,y) in enumerate([(5,5),(155,5),(5,115),(155,115)],1):
    f=p.FOOTPRINT(b);f.SetReference('H'+str(i));f.SetValue('M3 NPTH');f.SetAttributes(p.FP_BOARD_ONLY|p.FP_EXCLUDE_FROM_BOM|p.FP_EXCLUDE_FROM_POS_FILES)
    pad=p.PAD(f);pad.SetAttribute(p.PAD_ATTRIB_NPTH);pad.SetShape(p.PAD_SHAPE_CIRCLE);pad.SetSize(xy(3.2,3.2));pad.SetDrillSize(xy(3.2,3.2));pad.SetLayerSet(p.LSET.AllCuMask());f.Add(pad)
    f.SetPosition(xy(x,y));f.Reference().SetVisible(False);f.Value().SetVisible(False);f.SetAllowMissingCourtyard(True);b.Add(f)
    # Full keepout for M3 head/washer, radius 4 mm on both sides.
    z=p.ZONE(b);z.SetIsRuleArea(True);z.SetLayerSet(layers(p.F_Cu,p.B_Cu));z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowZoneFills(True);z.SetDoNotAllowPads(False);z.SetDoNotAllowFootprints(False)
    o=z.Outline();o.NewOutline()
    for k in range(48):o.Append(mm(x+4*math.cos(k*math.tau/48)),mm(y+4*math.sin(k*math.tau/48)))
    b.Add(z)
for a,c in [((0,0),(160,0)),((160,0),(160,120)),((160,120),(0,120)),((0,120),(0,0))]:
    line=p.PCB_SHAPE();line.SetShape(p.SHAPE_T_SEGMENT);line.SetStart(xy(*a));line.SetEnd(xy(*c));line.SetWidth(mm(.05));line.SetLayer(p.Edge_Cuts);b.Add(line)
def txt(t,x,y,size=1,layer=p.F_SilkS):
    a=p.PCB_TEXT(b);a.SetText(t);a.SetPosition(xy(x,y));a.SetTextSize(xy(size,size));a.SetTextThickness(mm(.15));a.SetLayer(layer);b.Add(a)
txt('EGRLab P01 / PCB R1',81,5,1.1)
txt('Cu 70um / 2L / 1.6mm',79,117,1,p.Dwgs_User)
tb=p.TITLE_BLOCK();tb.SetTitle('EGRLab P01 PROTECT / PCB R1');tb.SetRevision('PCB-R1 / SCH-R3');tb.SetDate('2026-09-23');tb.SetComment(0,'Review / physical fit and bench acceptance pending');b.SetTitleBlock(tb)
b.BuildConnectivity();p.SaveBoard(str(E/'P01.kicad_pcb'),b)
# Current placement is versioned independently of electrical R3.
summary=[]
for ref,f in fmap.items():
    bb=f.GetLayerBoundingBox(layers(p.F_CrtYd))
    summary.append({'ref':ref,'x':p.ToMM(f.GetPosition().x),'y':p.ToMM(f.GetPosition().y),'deg':f.GetOrientationDegrees(),
      'courtyard':[p.ToMM(bb.GetLeft()),p.ToMM(bb.GetTop()),p.ToMM(bb.GetRight()),p.ToMM(bb.GetBottom())],
      'pads':[{'n':pad.GetNumber(),'xy':[p.ToMM(pad.GetPosition().x),p.ToMM(pad.GetPosition().y)],'net':pad.GetNetname()} for pad in f.Pads()]})
(P/'verification/placement.json').write_text(json.dumps(summary,indent=2))
print('Created board',len(fmap),'electrical/mechanical footprints, 4 M3 holes.')

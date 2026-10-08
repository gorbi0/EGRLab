from pathlib import Path
import hashlib,json,zipfile,re
import pcbnew as p
E=Path(__file__).resolve().parent; R=E.parent
S=Path(json.loads((E/'source-snapshot.json').read_text())['source'])
sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
before=json.loads((E/'source-snapshot.json').read_text())['files']
now={x.relative_to(S).as_posix():sha(x) for x in S.rglob('*') if x.is_file()}
changed=[k for k,v in before.items() if now.get(k)!=v]
extra=sorted(set(now)-set(before))
(E/'source-integrity-final.json').write_text(json.dumps({'pass':not changed and not extra,'files_before':len(before),'files_after':len(now),'changed_or_missing':changed,'new':extra},indent=2))
P=S/'Plytki/M1-PCB-R1-zamowienie'
with zipfile.ZipFile(P/'DO-ZAMOWIENIA_M1-PCB-R1.zip') as z:
    entries=z.namelist(); zbad=z.testzip()
    mismatch=[n for n in entries if z.read(n)!=(P/'gerber'/n).read_bytes()]
    extras=sorted(set(x.name for x in (P/'gerber').iterdir() if x.is_file())-set(entries))
(E/'original-zip-check.json').write_text(json.dumps({'crc_error':zbad,'files':len(entries),'different':mismatch,'not_in_zip':extras,'sha256':sha(P/'DO-ZAMOWIENIA_M1-PCB-R1.zip')},indent=2))
def canonical(b):
    xy=lambda v:(v.x,v.y)
    tracks=[]
    for t in b.GetTracks():
        if t.GetClass()=='PCB_VIA':tracks.append(('via',t.GetNetname(),xy(t.GetPosition()),t.GetWidth(p.F_Cu),t.GetDrill(),t.TopLayer(),t.BottomLayer()))
        else:tracks.append(('track',t.GetNetname(),t.GetLayer(),t.GetWidth(),tuple(sorted([xy(t.GetStart()),xy(t.GetEnd())]))))
    fps=[]
    for f in b.GetFootprints():
        pads=sorted((q.GetNumber(),q.GetNetname(),xy(q.GetPosition()),xy(q.GetSize()),xy(q.GetDrillSize()),q.GetAttribute(),q.GetShape(),q.GetOrientationDegrees(),tuple(q.GetLayerSet().Seq())) for q in f.Pads())
        fps.append((f.GetReference(),f.GetValue(),xy(f.GetPosition()),f.GetOrientationDegrees(),f.GetLayer(),pads))
    zones=[]
    for z in b.Zones():
        poly=z.Outline()
        outlines=[]
        for i in range(poly.OutlineCount()):
            line=poly.COutline(i);outlines.append(tuple(xy(line.CPoint(j)) for j in range(line.PointCount())))
        zones.append((z.GetNetname(),tuple(z.GetLayerSet().Seq()),z.GetIsRuleArea(),tuple(outlines)))
    return {'tracks_vias':sorted(tracks),'footprints_pads':sorted(fps),'zone_boundaries':sorted(zones),'copper_layers':b.GetCopperLayerCount()}
a=canonical(p.LoadBoard(str(S/'Plytki/M1-R1-review/eda/M1.kicad_pcb')))
b=canonical(p.LoadBoard(str(R/'regen/eda/M1.kicad_pcb')))
checks={k:a[k]==b[k] for k in a}
(E/'rebuild-geometry-comparison.json').write_text(json.dumps({'scope':'Footprints/pads, tracks/vias, zone boundaries, layer count; not a filled-copper polygon XOR or byte identity.','checks':checks,'counts_source':{k:len(v) for k,v in a.items() if isinstance(v,list)},'counts_rebuild':{k:len(v) for k,v in b.items() if isinstance(v,list)}},indent=2))
fresh=R/'work/Plytki/M1-PCB-R1-zamowienie'
d0=json.loads((E/'original-board-fabrication-data.json').read_text())
d1=json.loads((fresh/'verification/board-fabrication-data.json').read_text())
(E/'fresh-fabrication-data-comparison.json').write_text(json.dumps({'equal':d0==d1,'different_keys':[k for k in set(d0)|set(d1) if d0.get(k)!=d1.get(k)]},indent=2))
def normalise(s):
    return '\n'.join(l for l in s.splitlines() if not any(t in l for t in ['TF.CreationDate','TF.MD5','Created by KiCad','Creation date']))
camdiff=[]
for f in (P/'gerber').iterdir():
    if f.is_file():
        if normalise(f.read_text())!=normalise((fresh/'gerber'/f.name).read_text()):camdiff.append(f.name)
(E/'fresh-cam-comparison.json').write_text(json.dumps({'different_after_ignoring_timestamp_and_md5':camdiff},indent=2))
print('source unchanged',not changed and not extra,'ZIP differences',mismatch,'rebuild',checks,'CAM diff',camdiff,'fab equal',d0==d1)

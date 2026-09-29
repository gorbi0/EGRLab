"""EGRLab log reader/exporter. Python 3.10+, standard library only."""
import argparse
import csv
import json
import math
from pathlib import Path
import statistics
import struct
import zlib

HEADER = struct.Struct('<8sHHIIIQ')
BLOCK = struct.Struct('<4sIII')
RECORD = struct.Struct('<QI8hHH')
DEFAULT_META = dict(gain=[4.06,4.06,1.01996,1.01996,1.01996,1,1,6.0796],
                    offset=[0]*8, current_zero=[2.5,2.5], current_volts_per_amp=.25,
                    supply_pin=5, closed=.15, open=.85)

class LogError(ValueError):
    pass

def read_header(stream):
    data = stream.read(HEADER.size)
    if len(data) != HEADER.size:
        raise LogError('Truncated file header')
    magic, version, size, rate, record, flags, session = HEADER.unpack(data)
    if magic != b'EGRLOG1\0' or version != 1 or size != 32 or record != 32 or not rate:
        raise LogError('Unsupported or invalid header')
    return dict(version=version, sample_rate=rate, record_bytes=record,
                synthetic=bool(flags & 1), session=session)

def records(stream, *, recovery=False, warnings=None):
    """Read after read_header. Recovery discards only a truncated final block."""
    warnings = warnings if warnings is not None else []
    while True:
        offset = stream.tell()
        raw = stream.read(BLOCK.size)
        if not raw:
            return
        if len(raw) != BLOCK.size:
            if recovery:
                warnings.append(f'truncated block header at {offset}')
                return
            raise LogError(f'Truncated block header at {offset}')
        magic, count, length, crc = BLOCK.unpack(raw)
        if magic != b'BLK1' or not 1 <= count <= 256 or length != count * 32:
            raise LogError(f'Invalid block at {offset}')
        payload = stream.read(length)
        if len(payload) != length:
            if recovery:
                warnings.append(f'truncated final block at {offset}')
                return
            raise LogError(f'Truncated block at {offset}')
        if zlib.crc32(payload) != crc:
            raise LogError(f'CRC mismatch at {offset}')
        yield from RECORD.iter_unpack(payload)

def physical(record, meta):
    t, seq, *rest = record
    raw, flags = rest[:8], rest[8]
    gain = meta['gain']
    offset = meta['offset']
    if len(gain) != 8 or len(offset) != 8:
        raise LogError('Calibration must have eight gains and offsets')
    v = [n * 10 / 32768 * g + o for n,g,o in zip(raw,gain,offset)]
    supply = meta.get('supply_pin')
    ref = ratio = position = math.nan
    if supply in (5,6):
        s,g = (3,4) if supply == 5 else (4,3)
        ref = v[s]-v[g]
        if 4.0 <= ref <= 6.0:
            ratio = (v[2]-v[g])/ref
            rc,ro=meta.get('closed'),meta.get('open')
            if rc is not None and ro is not None and abs(ro-rc)>.2:
                position=(ratio-rc)/(ro-rc)
    zero=meta.get('current_zero',[2.5,2.5]);scale=meta.get('current_volts_per_amp',.25)
    if not scale:
        raise LogError('Zero current scale')
    return [t,seq,flags,*raw,*v,v[0]-v[1],(v[5]-zero[0])/scale,
            (v[6]-zero[1])/scale,ref,ratio,position]

def inspect(path, recovery=False):
    warnings=[]; intervals=[]; count=gaps=sequence_gaps=0;last=None
    with open(path,'rb') as stream:
        header=read_header(stream)
        for row in records(stream,recovery=recovery,warnings=warnings):
            if last is not None:
                if row[0] <= last[0]:
                    raise LogError('Non-monotonic timestamps')
                intervals.append(row[0]-last[0])
                if row[1] != (last[1]+1)&0xffffffff:
                    sequence_gaps+=1
            if row[-2]&1:gaps+=1
            count+=1;last=row
    return dict(**header,records=count,gap_flags=gaps,sequence_discontinuities=sequence_gaps,
                min_dt_us=min(intervals) if intervals else None,
                max_dt_us=max(intervals) if intervals else None,
                median_dt_us=statistics.median(intervals) if intervals else None,warnings=warnings)

def export(path, metadata, target, recovery=False):
    meta=json.loads(Path(metadata).read_text(encoding='utf-8'))
    columns=['t_us','sequence','flags']+[f'raw_ch{i}' for i in range(1,9)]+[
        'motor_a_v','motor_b_v','pin4_v','pin5_v','pin6_v','itest_out_v','ilog_out_v','vprot_v',
        'motor_diff_v','itest_a','ilog_a','sensor_ref_v','sensor_ratio','position']
    warnings=[]
    changes=[]
    events=Path(path).parent/'events.ndjson'
    if events.exists():
        for number,line in enumerate(events.read_text(encoding='utf-8').splitlines(),1):
            try:
                event=json.loads(line)
            except json.JSONDecodeError:
                warnings.append(f'invalid NDJSON line {number}')
                continue
            if event.get('type')=='profile':changes.append(event)
        changes.sort(key=lambda e:e['t_us'])
    change_index=0
    with open(path,'rb') as stream,open(target,'w',newline='',encoding='utf-8') as output:
        read_header(stream);writer=csv.writer(output);writer.writerow(columns)
        for row in records(stream,recovery=recovery,warnings=warnings):
            while change_index<len(changes) and changes[change_index]['t_us']<=row[0]:
                meta.update({k:v for k,v in changes[change_index].items() if k in ('supply_pin','closed','open')})
                change_index+=1
            vals=physical(row,meta)
            writer.writerow(['' if isinstance(v,float) and not math.isfinite(v) else v for v in vals])
    return warnings

def write_log(path, rows, rate=2000, synthetic=True):
    with open(path,'wb') as stream:
        stream.write(HEADER.pack(b'EGRLOG1\0',1,32,rate,32,int(synthetic),1))
        for start in range(0,len(rows),64):
            part=rows[start:start+64];payload=b''.join(RECORD.pack(*r) for r in part)
            stream.write(BLOCK.pack(b'BLK1',len(part),len(payload),zlib.crc32(payload)))
            stream.write(payload)

def synth(path, seconds=2):
    meta=dict(DEFAULT_META,synthetic=True,description='Generated bench fixture, NOT vehicle data',
              vehicle='Kia Sportage 1.7 CRDi 2013',sample_rate=2000)
    rows=[]
    for n in range(seconds*2000):
        t=n/2000
        fb=2.5+.8*math.sin(2*math.pi*t)
        if .995<t<1.005:fb=.05
        real=[12 if n%2 else 0,0,fb,5,.025,2.5,2.5+.15*math.sin(2*math.pi*t),13.9]
        raw=[max(-32768,min(32767,round(v/g*32768/10))) for v,g in zip(real,meta['gain'])]
        rows.append((n*500+1,n,*raw,0,0))
    write_log(path,rows)
    Path(path).with_suffix('.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    for name in ('inspect','export','synth'):
        q=sub.add_parser(name);q.add_argument('file',type=Path)
        if name!='synth':q.add_argument('--recover',action='store_true')
        if name=='export':q.add_argument('--meta',required=True);q.add_argument('--csv',required=True)
    a=p.parse_args()
    try:
        if a.command=='synth':synth(a.file)
        elif a.command=='inspect':print(json.dumps(inspect(a.file,a.recover),indent=2))
        else:print(json.dumps({'warnings':export(a.file,a.meta,a.csv,a.recover)}))
    except (OSError,ValueError,KeyError) as e:p.exit(2,f'{e}\n')

if __name__=='__main__':main()

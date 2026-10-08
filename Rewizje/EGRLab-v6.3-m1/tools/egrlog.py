"""EGRLab v5 — czytnik i eksporter logow 1–5. Python 3.10+, biblioteka standardowa.

Podkomendy:
  inspect <plik.egr>                        integralnosc, odstepy, GAP, config_id
  scan    <events.ndjson>                   konfiguracje, triggery, MARK, HOT-SOAK, ekstrema 1 Hz
  export  <plik.egr> --csv o.csv [--meta m.json]
  report  <plik.egr> --html o.html [--meta m.json]
  synth   <plik.egr>                        syntetyczny plik testowy

Formaty 3–5 niosa w kazdym rekordzie `config_id`: numer migawki konfiguracji
zapisanej w events.ndjson jako zdarzenie `config`. Dzieki temu zmiana zakresu,
banku, zera pradu albo mapowania pinow w trakcie sesji nie psuje przeliczenia
wczesniejszych probek. Pliki 1 i 2 czytaja sie po staremu, z metadanych.
"""
import argparse
import html
from collections import Counter
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
RECORD_V5 = struct.Struct('<QI8h6H')

# Kanaly w wersjach 2-4: 0 pin1, 1 pin3, 2 pin4, 3 pin5, 4 pin6,
# 5 prad aktywnego banku, 6 VBAT, 7 AUX.
NAMES_V2 = ['motor_a_v', 'motor_b_v', 'pin4_v', 'pin5_v', 'pin6_v',
            'current_out_v', 'vbat_v', 'aux_v']
NAMES_V1 = ['motor_a_v', 'motor_b_v', 'pin4_v', 'pin5_v', 'pin6_v',
            'itest_out_v', 'ilog_out_v', 'vprot_v']

NOMINAL_GAIN = [4.06, 4.06, 1.01996, 1.01996, 1.01996, 1, 6.0796, 4.06]

DEFAULT_META = dict(
    gain=list(NOMINAL_GAIN),
    offset=[0] * 8,
    full_scale=[10, 10, 5, 5, 2.5, 5, 10, 10],
    current_zero=2.5, current_volts_per_amp=.25, current_valid=True,
    ch_supply=2, ch_ground=4, ch_feedback=3,   # fixture / legacy fallback, not a verified OEM pinout
    closed=.15, open=.85, learned=True, adc_config_ok=True)


class LogError(ValueError):
    pass


def read_header(stream):
    data = stream.read(HEADER.size)
    if len(data) != HEADER.size:
        raise LogError('Truncated file header')
    magic, version, size, rate, record, flags, session = HEADER.unpack(data)
    if magic != b'EGRLOG1\0' or version not in (1, 2, 3, 4, 5) or size != 32 or record != (40 if version==5 else 32) or not rate:
        raise LogError('Unsupported or invalid header')
    return dict(version=version, sample_rate=rate, record_bytes=record,
                synthetic=bool(flags & 1), session=session)


def records(stream, *, recovery=False, warnings=None, version=4):
    """Czytaj po read_header. Recovery odrzuca wylacznie urwany ostatni blok."""
    warnings = warnings if warnings is not None else []
    fmt=RECORD_V5 if version==5 else RECORD
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
        if magic != b'BLK1' or not 1 <= count <= 256 or length != count * fmt.size:
            raise LogError(f'Invalid block at {offset}')
        payload = stream.read(length)
        if len(payload) != length:
            if recovery:
                warnings.append(f'truncated final block at {offset}')
                return
            raise LogError(f'Truncated block at {offset}')
        if zlib.crc32(payload) != crc:
            raise LogError(f'CRC mismatch at {offset}')
        yield from fmt.iter_unpack(payload)


def channels(cfg):
    """Zwraca (zasilanie, masa, sygnal) jako indeksy v[] albo (None, None, None)."""
    keys = ('ch_supply', 'ch_ground', 'ch_feedback')
    if all(cfg.get(k) is not None for k in keys):
        triple = tuple(cfg[k] for k in keys)
        if all(isinstance(c, int) and 0 <= c < 8 for c in triple) and len(set(triple)) == 3:
            return triple
        return (None, None, None)
    supply = cfg.get('supply_pin')          # zgodnosc z plikami v1
    if supply == 5:
        return (3, 4, 2)
    if supply == 6:
        return (4, 3, 2)
    return (None, None, None)


def normalise_config(raw, warnings=None, source='metadane'):
    """Uzupelnia konfiguracje; brak potwierdzenia pomiaru pozostaje niewazny."""
    cfg = dict(raw)
    if warnings is not None:
        if cfg.get('local_current'):
            if cfg.get('voltage_calibrated') is not True:
                warnings.append(f'{source}: kalibracja napiec niezaakceptowana - fizyczne napiecia pominiete')
            for field in ('current_adc_gain','current_adc_offset','current_calibrated'):
                if field not in cfg:warnings.append(f'{source}: brak {field} - lokalny prad nie moze byc zatwierdzony')
        for field, effect in (
            ('adc_config_ok', 'wielkosci fizyczne pominiete'),
            ('current_valid', 'prad pominiety'),
            ('learned', 'pozycja pominieta; ratio nie wymaga LEARN'),
        ):
            if field not in cfg:
                warnings.append(f'{source}: brak {field} - {effect}')
    cfg.setdefault('full_scale', [10] * 8)
    cfg.setdefault('gain', list(NOMINAL_GAIN))
    cfg.setdefault('offset', [0] * 8)
    cfg.setdefault('current_volts_per_amp', .25)
    cfg.setdefault('current_valid', False)
    cfg.setdefault('learned', False)
    cfg.setdefault('adc_config_ok', False)
    zero = cfg.get('current_zero', 2.5)
    cfg['current_zero'] = zero[0] if isinstance(zero, list) else zero
    for key in ('gain', 'offset', 'full_scale'):
        if not isinstance(cfg[key], (list, tuple)) or len(cfg[key]) != 8:
            raise LogError(f'{key}: oczekiwano osmiu wartosci')
    return cfg


def physical(record, cfg):
    """Zamienia rekord na wielkosci fizyczne wedlug PODANEJ konfiguracji."""
    cfg = normalise_config(cfg)
    t, seq, *rest = record
    raw, flags, config_id = rest[:8], rest[-2], rest[-1]
    def value(n,f,g,o):
        if not cfg['adc_config_ok'] or (len(record)==16 and not cfg.get('voltage_calibrated')) or flags & 128 or abs(n)>=32760:
            return math.nan
        if not all(isinstance(x,(int,float)) and math.isfinite(x) for x in (f,g,o)) or f<=0:
            return math.nan
        return n*f/32768*g+o
    v = [value(n,f,g,o) for n,f,g,o in zip(raw,cfg['full_scale'],cfg['gain'],cfg['offset'])]
    # 6.3.1-m1 (recenzja M1-10): pola MCP3201 rekordu v5 zastepuja CH6 tylko w sesjach z lokalnym przetwornikiem
    # (local_current=true, S1). M1 zapisuje prad w raw[5] (CH6 AD7606B) i ma local_current=false - v[5] zostaje.
    if len(record)==16 and cfg.get('local_current') is True:
        n,begin,end,status=record[10:14]
        g_adc=cfg.get('current_adc_gain');o_adc=cfg.get('current_adc_offset')
        v[5]=n*g_adc+o_adc if (status==1 and 4<=n<=4091 and not flags&128 and
            0<=begin<=end<=400 and end-begin<=100 and all(isinstance(x,(int,float)) and math.isfinite(x) for x in (g_adc,o_adc))) else math.nan
    s, g, f = channels(cfg)
    ref = ratio = position = math.nan
    if s is not None:
        ref = v[s] - v[g]
        if 4.0 <= ref <= 6.0:
            ratio = (v[f] - v[g]) / ref
            rc, ro = cfg.get('closed'), cfg.get('open')
            if cfg['learned'] and rc is not None and ro is not None and abs(ro - rc) > .2:
                position = (ratio - rc) / (ro - rc)
    per_amp = cfg['current_volts_per_amp']
    if not isinstance(per_amp,(int,float)) or not math.isfinite(per_amp) or per_amp<=0:
        raise LogError('Zero current scale')
    # Prad bez waznej informacji (mostek bocznikujacy, sondy back-probe) to
    # pusta wartosc, a nie liczba, ktora wyglada jak pomiar.
    current = (v[5] - cfg['current_zero']) / per_amp if cfg['current_valid'] and (len(record)!=16 or cfg.get('current_calibrated')) else math.nan
    return [t, seq, flags, config_id, *raw, *v, v[0] - v[1], current, ref, ratio, position]


def columns(version, sens5v=False):
    names = list(NAMES_V2 if version >= 2 else NAMES_V1)
    if sens5v and version >= 2:
        names[7] = 'sens_5v_v'   # M1: CH8 = SENS_5V (config ch8), nie AUX z S1
    return (['t_us', 'sequence', 'flags', 'config_id'] + [f'raw_ch{i}' for i in range(1, 9)]
            + names + ['motor_diff_v', 'current_a', 'sensor_ref_v', 'sensor_ratio', 'position']
            + (['current_raw','current_begin_us','current_end_us','current_status'] if version==5 else []))


def sample_paths(path):
    path=Path(path)
    files=sorted(path.glob('samples*.egr')) if path.is_dir() else [path]
    if not files: raise LogError('brak plikow samples*.egr')
    return files


def iter_session(path,recovery=False,warnings=None):
    first=None
    for file in sample_paths(path):
        with file.open('rb') as stream:
            header=read_header(stream)
            if first and any(header[k]!=first[k] for k in ('session','version','sample_rate')):
                raise LogError('Niezgodne naglowki segmentow sesji')
            first=header
            for row in records(stream,recovery=recovery,warnings=warnings,version=header["version"]): yield header,row


def inspect(path,recovery=False):
    warnings=[]; counts=Counter(); histogram=Counter(); last=None
    count=gaps=triggers=sequence_gaps=0; minimum=maximum=None; header=None
    for header,row in iter_session(path,recovery,warnings):
        if last is not None:
            dt=row[0]-last[0]
            if dt<=0: raise LogError('Non-monotonic timestamps')
            minimum=dt if minimum is None else min(minimum,dt)
            maximum=dt if maximum is None else max(maximum,dt)
            histogram[min(dt,10001)]+=1
            if row[1]!=(last[1]+1)&0xffffffff: sequence_gaps+=1
        gaps+=bool(row[-2]&1); triggers+=bool(row[-2]&32)
        counts[row[-1]]+=1; count+=1; last=row
    if header is None:
        with sample_paths(path)[0].open('rb') as stream: header=read_header(stream)
    mid=None; accumulated=0
    for dt,n in sorted(histogram.items()):
        accumulated+=n
        if accumulated>=max(1,(count-1+1)//2): mid=dt; break
    return dict(**header,records=count,gap_flags=gaps,trigger_flags=triggers,
                sequence_discontinuities=sequence_gaps,config_ids=dict(sorted(counts.items())),
                min_dt_us=minimum,max_dt_us=maximum,median_dt_us=mid,
                median_capped_at_us=10001,warnings=warnings)


def event_paths(path):
    path=Path(path)
    if path.is_dir():
        return sorted(path.glob('events*.ndjson'))
    if path.name=='events.ndjson' and not path.exists():
        return sorted(path.parent.glob('events_*.ndjson'))
    return [path] if path.exists() else []


def iter_events(path, warnings):
    def reject_constant(x):
        raise ValueError('non-standard JSON constant '+x)
    for file in event_paths(path):
        with file.open(encoding='utf-8') as stream:
            for number,line in enumerate(stream,1):
                if not line.strip(): continue
                try:
                    event=json.loads(line,parse_constant=reject_constant)
                    if not isinstance(event,dict): raise ValueError('expected object')
                    yield event
                except (ValueError,TypeError):
                    if len(warnings)<100: warnings.append(f'invalid NDJSON {file.name} line {number}')


def load_events(path):
    warnings=[]
    return list(iter_events(path,warnings)),warnings


def load_configs(events, warnings=None):
    """Mapa config_id -> konfiguracja, ze zdarzen `config`."""
    out = {}
    for e in events:
        if e.get('type') != 'config' or e.get('config_id') is None:
            continue
        out[int(e['config_id'])] = normalise_config(e, warnings, f"config_id={e['config_id']}")
    return out


def resolve_configs(path, meta_path, warnings):
    """Zwraca (mapa_konfiguracji, konfiguracja_zapasowa)."""
    # Keep only metadata and a bounded event digest; raw CAN never fills RAM.
    events=[]; clipped=False
    for e in iter_events(Path(path) if Path(path).is_dir() else Path(path).parent, warnings):
        if e.get('type')=='config': events.append(e)
        elif e.get('type') in ('mark','trigger','hotsoak_point'):
            if len(events)<10000: events.append(e)
            else: clipped=True
    if clipped: warnings.append('tabela zdarzen ograniczona do 10000; pelne dane w NDJSON')
    configs = load_configs(events, warnings)
    fallback = None
    if meta_path:
        fallback = normalise_config(json.loads(Path(meta_path).read_text(encoding='utf-8')),
                                    warnings, f'--meta {Path(meta_path).name}')
    elif configs:
        fallback = configs[min(configs)]
    else:
        fallback = normalise_config(DEFAULT_META)
        warnings.append('brak metadanych: nominalne skale tylko dla historycznego formatu 1/2; format 3/4 pozostaje niewazny')
    return configs, fallback, events


def config_for(configs, fallback, config_id, warnings, seen):
    cfg = configs.get(int(config_id))
    if cfg is None:
        if config_id not in seen:
            seen.add(config_id)
            warnings.append(f'brak zdarzenia config dla config_id={config_id}')
        return normalise_config(dict(full_scale=[None]*8, adc_config_ok=False, current_valid=False))
    return cfg


def scan(path):
    warnings=[]; counts=Counter(); first={}; marks=[]; soak=[]; configs=[]; problems=[]
    n=seconds=0; extremes={}
    for e in iter_events(path,warnings):
        n+=1; kind=e.get('type')
        if kind=='trigger':
            k=e.get('name','?'); counts[k]+=1; first.setdefault(k,e.get('t_us'))
        elif kind=='mark' and len(marks)<10000: marks.append(e.get('t_us'))
        elif kind=='hotsoak_point' and len(soak)<10000: soak.append(e)
        elif kind=='config': configs.append(e)
        elif kind in ('adc_error','adc_config_error','summary_dropped','can_drop') and len(problems)<10000: problems.append(e)
        elif kind=='summary':
            seconds+=1
            for i,values in enumerate(e.get('ch',[])[:8]):
                if len(values)!=3: continue
                good=[v for v in (values[0],values[2]) if isinstance(v,(int,float)) and math.isfinite(v)]
                if not good: continue
                key=NAMES_V2[i]; magnitude=max(abs(v) for v in good)
                if key not in extremes or magnitude>extremes[key]['magnitude']:
                    extremes[key]=dict(t_us=e.get('t_us'),min=values[0],mean=values[1],max=values[2],magnitude=magnitude)
    if any(e.get('adc_config_ok') is False for e in configs):
        warnings.append('konfiguracja z niepotwierdzonym ADC: wielkosci fizyczne niewazne')
    return dict(events=n,warnings=warnings,configs=configs,problems=problems,triggers=dict(counts),
                first_trigger_us=first,marks_us=marks,hotsoak_points=soak,seconds=seconds,extremes=extremes)


def export(path,target,meta_path=None,recovery=False,start=None,end=None):
    warnings=[]; configs,fallback,_=resolve_configs(path,meta_path,warnings); seen=set()
    with open(target,'w',newline='',encoding='utf-8') as output:
        writer=csv.writer(output); wrote=False
        for header,row in iter_session(path,recovery,warnings):
            if not wrote:
                writer.writerow(columns(header['version'],any(c.get('ch8')=='SENS_5V' for c in configs.values()))); wrote=True
            if start is not None and row[0]<start*1e6: continue
            if end is not None and row[0]>end*1e6: continue
            cfg=fallback if header['version']<3 else config_for(configs,fallback,row[-1],warnings,seen)
            values=physical(row,cfg)
            if header['version']==5: values.extend(row[10:14])
            writer.writerow(['' if isinstance(v,float) and not math.isfinite(v) else v for v in values])
    return warnings


def report(path,target,meta_path=None,recovery=False,points=3000,start=None,end=None,full=False):
    warnings=[]; configs,fallback,events=resolve_configs(path,meta_path,warnings); seen=set()
    count=0; lo=hi=None; header=None
    for header,row in iter_session(path,recovery,warnings):
        t=row[0]/1e6
        if (start is not None and t<start) or (end is not None and t>end): continue
        if lo is None: lo=t
        hi=t; count+=1
    if not count: raise LogError('Brak probek w wybranym oknie')
    if full and count>200000: raise LogError('--full: za duze okno; wybierz <=200000 probek przez --from/--to')
    points=max(1,min(int(points),10000)); width=max((hi-lo)/points,1e-9)
    keys=('ratio','position','ground','ref','current','vbat','aux')
    buckets=[{k:[None,None] for k in keys} for _ in range(count if full else points)]
    times=[]; quality=set(); index=0
    for h,row in iter_session(path,recovery,warnings):
        t=row[0]/1e6
        if t<lo or t>hi: continue
        cfg=fallback if h['version']<3 else config_for(configs,fallback,row[-1],warnings,seen)
        vals=physical(row,cfg); v=vals[12:20]; _,g,_=channels(cfg)
        values=(vals[-2],vals[-1],v[g] if g is not None else math.nan,vals[-3],vals[-4],v[6],v[7])
        idx=index if full else min(points-1,int((t-lo)/width)); bucket=buckets[idx]
        if full: times.append(t)
        if row[-2]&193 or not cfg['adc_config_ok']: quality.add(idx)
        for k,value in zip(keys,values):
            if math.isfinite(value):
                x=bucket[k]; x[0]=value if x[0] is None else min(x[0],value); x[1]=value if x[1] is None else max(x[1],value)
        index+=1
    data=dict(series={k:[b[k] for b in buckets] for k in keys},lo=lo,hi=hi,
              quality=sorted(quality),times=times,full=full)
    table='<table><tr><th>config_id</th><th>bank</th><th>ADC OK</th><th>learned</th></tr>'
    for c in configs.values():
        table+='<tr>'+''.join('<td>'+html.escape(str(c.get(k)))+'</td>' for k in ('config_id','bank','adc_config_ok','learned'))+'</tr>'
    table+='</table>'
    note=f'Format {header["version"]}; {count} rekordow; czas {lo:.6f}–{hi:.6f} s. '
    note+=('Pelna rozdzielczosc.' if full else 'Obwiednia min/max kazdego przedzialu; wszystkie probki uczestnicza w agregacji. Nie wyznaczaj czasu impulsu z pomniejszonego widoku.')
    if any(c.get('ch8')=='SENS_5V' for c in configs.values()): note+=' Seria aux = CH8 SENS_5V (M1); vbat = CH7 wedlug ch7_source w config.'
    if header['synthetic']: note+=' DANE SYNTETYCZNE'
    document=HTML.replace('__TITLE__',html.escape(Path(path).name)).replace('__NOTE__',html.escape(note))
    document=document.replace('__TABLE__',table).replace('__WARN__','<br>'.join(html.escape(x) for x in warnings))
    document=document.replace('__DATA__',json.dumps(data,allow_nan=False,separators=(',',':')))
    Path(target).write_text(document,encoding='utf-8'); return warnings


HTML = r"""<!doctype html><html lang="pl"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>EGRLab — __TITLE__</title><style>body{font:15px system-ui;background:#101923;color:#e6eff8;margin:24px}h1{font-size:24px}canvas{width:100%;height:190px;background:#172433;margin-bottom:20px}table{border-collapse:collapse}td,th{border:1px solid #607080;padding:5px}aside{color:#f6ba66}</style>
<h1>EGRLab — __TITLE__</h1><p>__NOTE__</p><p>Pomarańczowy pasek: GAP, nasycenie lub nieważny ADC. Jednostki: ratio/position bezwymiarowe, ground/ref/vbat/aux V, current A.</p>__TABLE__<aside>__WARN__</aside><div id="plots"></div>
<script id="data" type="application/json">__DATA__</script><script>
const D=JSON.parse(document.getElementById('data').textContent);
for(const [key,arr] of Object.entries(D.series)) {
const label=document.createElement('h2');label.textContent=key;plots.appendChild(label);
const cv=document.createElement('canvas');cv.width=1500;cv.height=210;plots.appendChild(cv);
const c=cv.getContext('2d');let low=Infinity,high=-Infinity;
for(const a of arr)if(a[0]!==null){low=Math.min(low,a[0]);high=Math.max(high,a[1]);}
if(!Number.isFinite(low)){c.fillStyle='#ccc';c.fillText('Brak waznych pomiarow',20,70);continue;}
if(low===high){low-=.01;high+=.01;}const pad=(high-low)*.05;low-=pad;high+=pad;
const x=i=>70+1410*(D.full?(D.times[i]-D.lo)/Math.max(1e-9,D.hi-D.lo):i/Math.max(1,arr.length-1)),y=v=>175-(v-low)*150/(high-low);
c.strokeStyle='#34495d';for(let j=0;j<5;j++){let yy=25+j*150/4;c.beginPath();c.moveTo(70,yy);c.lineTo(1480,yy);c.stroke();c.fillStyle='#ccc';c.fillText((high-j*(high-low)/4).toPrecision(4),2,yy);}
c.strokeStyle='#62dcc7';c.lineWidth=1;
let prev=null;for(let i=0;i<arr.length;i++){let a=arr[i];if(a[0]===null){prev=null;continue;}c.beginPath();c.moveTo(x(i),y(a[0]));c.lineTo(x(i),y(a[1]));c.stroke();if(D.full&&prev!==null){c.beginPath();c.moveTo(x(i-1),y(prev));c.lineTo(x(i),y(a[0]));c.stroke();}prev=a[0];}
c.fillStyle='#f4a344';for(const i of D.quality)c.fillRect(x(i),181,Math.max(1,1410/arr.length),4);
c.fillStyle='#ddd';c.fillText(D.lo.toFixed(6)+' s',70,203);c.fillText(D.hi.toFixed(6)+' s',1350,203);
cv.title='Pelne surowe dane: egrlog export katalog --csv okno.csv --from t0 --to t1';
}
</script></html>"""


def write_log(path, rows, rate=2000, synthetic=True, version=4):
    fmt=RECORD_V5 if version==5 else RECORD
    with open(path, 'wb') as stream:
        stream.write(HEADER.pack(b'EGRLOG1\0', version, 32, rate, fmt.size, int(synthetic), 1))
        for start in range(0, len(rows), 64):
            part = rows[start:start + 64]
            payload = b''.join(fmt.pack(*r) for r in part)
            stream.write(BLOCK.pack(b'BLK1', len(part), len(payload), zlib.crc32(payload)))
            stream.write(payload)


def config_event(config_id, **overrides):
    cfg = dict(DEFAULT_META, type='config', config_id=config_id, t_us=0, bank=0,
               learned=True, opening_sign=1, adc_software_mode=True, adc_config_ok=True,
               aux_position='HI')
    cfg.update(overrides)
    return cfg


def synth(path, seconds=2):
    """Plik testowy ze ZMIANA konfiguracji w polowie sesji.

    Pierwsza sekunda: kanal masy na +-10 V. Druga: ten sam sygnal fizyczny na
    +-2,5 V, czyli inne kody surowe. Poprawny czytnik da w obu identyczne
    napiecie — na tym polega roznica miedzy v2 a v3.
    """
    path = Path(path)
    cfg_a = config_event(1, full_scale=[10, 10, 10, 10, 10, 5, 10, 10])
    cfg_b = config_event(2, full_scale=[10, 10, 10, 5, 2.5, 5, 10, 10], current_zero=2.55)
    rows = []
    for n in range(seconds * 2000):
        t = n / 2000
        feedback = 2.5 + .8 * math.sin(2 * math.pi * t)
        ground = .025
        if .995 < t < 1.005:          # zasymulowany krotki zanik sygnalu
            feedback = .05
        if 1.40 < t < 1.55:           # zasymulowany skok masy pod obciazeniem
            ground = .42
        cfg = cfg_a if t < 1.0 else cfg_b
        zero = cfg['current_zero']
        real = [12 if n % 2 else 0, 0, 5.0, feedback, ground,
                zero + .15 * math.sin(2 * math.pi * t), 13.9, 1.2]
        raw = [max(-32768, min(32767, round(value / gain * 32768 / fs)))
               for value, gain, fs in zip(real, cfg['gain'], cfg['full_scale'])]
        rows.append((n * 500 + 1, n, *raw, 0, cfg['config_id']))
    write_log(path, rows)
    events = path.parent / 'events.ndjson'
    lines = [json.dumps(cfg_a), json.dumps(dict(cfg_b, t_us=1000000))]
    lines.append(json.dumps({'type': 'mark', 't_us': 1500000}))
    events.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    meta = {'schema': 4, 'firmware': 'EGRLab-v4', 'synthetic': True, 'sample_rate': 2000,
            'vehicle': 'Kia Sportage 1.7 CRDi 2013',
            'note': 'Syntetyczny plik testowy; kalibracja w events.ndjson.'}
    path.with_suffix('.json').write_text(json.dumps(meta, indent=2), encoding='utf-8')


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='command', required=True)
    for name in ('inspect', 'scan', 'export', 'report', 'synth'):
        q = sub.add_parser(name)
        q.add_argument('file', type=Path)
        if name in ('inspect', 'export', 'report'):
            q.add_argument('--recover', action='store_true')
        if name in ('export', 'report'):
            q.add_argument('--meta', default=None,
                           help='konfiguracja zapasowa dla plikow bez zdarzen config')
        if name in ('export','report'):
            q.add_argument('--from',dest='start',type=float)
            q.add_argument('--to',dest='end',type=float)
        if name == 'export':
            q.add_argument('--csv', required=True)
        if name == 'report':
            q.add_argument('--html', required=True)
            q.add_argument('--full',action='store_true')
    a = p.parse_args()
    try:
        if a.command == 'synth':
            synth(a.file)
        elif a.command == 'inspect':
            print(json.dumps(inspect(a.file, a.recover), indent=2))
        elif a.command == 'scan':
            print(json.dumps(scan(a.file), indent=2))
        elif a.command == 'export':
            print(json.dumps({'warnings': export(a.file, a.csv, a.meta, a.recover,a.start,a.end)}))
        else:
            print(json.dumps({'warnings': report(a.file, a.html, a.meta, a.recover,start=a.start,end=a.end,full=a.full)}))
    except (OSError, ValueError, KeyError) as e:
        p.exit(2, f'{e}\n')


if __name__ == '__main__':
    main()

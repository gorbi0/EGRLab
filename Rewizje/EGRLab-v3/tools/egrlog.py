"""EGRLab v3 — czytnik i eksporter logow. Python 3.10+, tylko biblioteka standardowa.

Podkomendy:
  inspect <plik.egr>                        integralnosc, odstepy, GAP, config_id
  scan    <events.ndjson>                   konfiguracje, triggery, MARK, HOT-SOAK, ekstrema 1 Hz
  export  <plik.egr> --csv o.csv [--meta m.json]
  report  <plik.egr> --html o.html [--meta m.json]
  synth   <plik.egr>                        syntetyczny plik testowy

Format 3 niesie w kazdym rekordzie `config_id`: numer migawki konfiguracji
zapisanej w events.ndjson jako zdarzenie `config`. Dzieki temu zmiana zakresu,
banku, zera pradu albo mapowania pinow w trakcie sesji nie psuje przeliczenia
wczesniejszych probek. Pliki 1 i 2 czytaja sie po staremu, z metadanych.
"""
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

# Kanaly w wersji 2 i 3: 0 pin1, 1 pin3, 2 pin4, 3 pin5, 4 pin6,
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
    ch_supply=2, ch_ground=4, ch_feedback=3,   # pinout ze schematu Monolith
    closed=.15, open=.85)


class LogError(ValueError):
    pass


def read_header(stream):
    data = stream.read(HEADER.size)
    if len(data) != HEADER.size:
        raise LogError('Truncated file header')
    magic, version, size, rate, record, flags, session = HEADER.unpack(data)
    if magic != b'EGRLOG1\0' or version not in (1, 2, 3) or size != 32 or record != 32 or not rate:
        raise LogError('Unsupported or invalid header')
    return dict(version=version, sample_rate=rate, record_bytes=record,
                synthetic=bool(flags & 1), session=session)


def records(stream, *, recovery=False, warnings=None):
    """Czytaj po read_header. Recovery odrzuca wylacznie urwany ostatni blok."""
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


def normalise_config(raw):
    """Uzupelnia brakujace pola konfiguracji wartosciami zgodnymi wstecz."""
    cfg = dict(raw)
    cfg.setdefault('full_scale', [10] * 8)
    cfg.setdefault('gain', list(NOMINAL_GAIN))
    cfg.setdefault('offset', [0] * 8)
    cfg.setdefault('current_volts_per_amp', .25)
    cfg.setdefault('current_valid', True)
    zero = cfg.get('current_zero', 2.5)
    cfg['current_zero'] = zero[0] if isinstance(zero, list) else zero
    for key in ('gain', 'offset', 'full_scale'):
        if len(cfg[key]) != 8:
            raise LogError(f'{key}: oczekiwano osmiu wartosci')
    return cfg


def physical(record, cfg):
    """Zamienia rekord na wielkosci fizyczne wedlug PODANEJ konfiguracji."""
    cfg = normalise_config(cfg)
    t, seq, *rest = record
    raw, flags, config_id = rest[:8], rest[8], rest[9]
    v = [n * f / 32768 * g + o
         for n, f, g, o in zip(raw, cfg['full_scale'], cfg['gain'], cfg['offset'])]
    s, g, f = channels(cfg)
    ref = ratio = position = math.nan
    if s is not None:
        ref = v[s] - v[g]
        if 4.0 <= ref <= 6.0:
            ratio = (v[f] - v[g]) / ref
            rc, ro = cfg.get('closed'), cfg.get('open')
            if rc is not None and ro is not None and abs(ro - rc) > .2:
                position = (ratio - rc) / (ro - rc)
    per_amp = cfg['current_volts_per_amp']
    if not per_amp:
        raise LogError('Zero current scale')
    # Prad bez waznej informacji (mostek bocznikujacy, sondy back-probe) to
    # pusta wartosc, a nie liczba, ktora wyglada jak pomiar.
    current = (v[5] - cfg['current_zero']) / per_amp if cfg['current_valid'] else math.nan
    return [t, seq, flags, config_id, *raw, *v, v[0] - v[1], current, ref, ratio, position]


def columns(version):
    names = NAMES_V2 if version >= 2 else NAMES_V1
    return (['t_us', 'sequence', 'flags', 'config_id'] + [f'raw_ch{i}' for i in range(1, 9)]
            + names + ['motor_diff_v', 'current_a', 'sensor_ref_v', 'sensor_ratio', 'position'])


def inspect(path, recovery=False):
    warnings = []
    intervals = []
    count = gaps = triggers = sequence_gaps = 0
    configs = {}
    last = None
    with open(path, 'rb') as stream:
        header = read_header(stream)
        for row in records(stream, recovery=recovery, warnings=warnings):
            if last is not None:
                if row[0] <= last[0]:
                    raise LogError('Non-monotonic timestamps')
                intervals.append(row[0] - last[0])
                if row[1] != (last[1] + 1) & 0xffffffff:
                    sequence_gaps += 1
            flags = row[-2]
            if flags & 1:
                gaps += 1
            if flags & 32:
                triggers += 1
            configs[row[-1]] = configs.get(row[-1], 0) + 1
            count += 1
            last = row
    return dict(**header, records=count, gap_flags=gaps, trigger_flags=triggers,
                sequence_discontinuities=sequence_gaps,
                config_ids={int(k): v for k, v in sorted(configs.items())},
                min_dt_us=min(intervals) if intervals else None,
                max_dt_us=max(intervals) if intervals else None,
                median_dt_us=statistics.median(intervals) if intervals else None,
                warnings=warnings)


def load_events(path):
    """Czyta NDJSON; uszkodzone linie trafiaja do ostrzezen, nie wysadzaja odczytu."""
    events, warnings = [], []
    path = Path(path)
    if not path.exists():
        return events, warnings
    for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            warnings.append(f'invalid NDJSON line {number}')
    return events, warnings


def load_configs(events):
    """Mapa config_id -> konfiguracja, ze zdarzen `config`."""
    out = {}
    for e in events:
        if e.get('type') != 'config' or e.get('config_id') is None:
            continue
        out[int(e['config_id'])] = normalise_config(e)
    return out


def resolve_configs(path, meta_path, warnings):
    """Zwraca (mapa_konfiguracji, konfiguracja_zapasowa)."""
    events, event_warnings = load_events(Path(path).parent / 'events.ndjson')
    warnings.extend(event_warnings)
    configs = load_configs(events)
    fallback = None
    if meta_path:
        fallback = normalise_config(json.loads(Path(meta_path).read_text(encoding='utf-8')))
    elif configs:
        fallback = configs[min(configs)]
    else:
        fallback = normalise_config(DEFAULT_META)
        warnings.append('brak zdarzen config i pliku --meta: uzyto wartosci nominalnych')
    return configs, fallback, events


def config_for(configs, fallback, config_id, warnings, seen):
    if not configs:
        return fallback
    cfg = configs.get(int(config_id))
    if cfg is None:
        if config_id not in seen:
            seen.add(config_id)
            warnings.append(f'brak zdarzenia config dla config_id={config_id}')
        return fallback
    return cfg


def scan(path):
    events, warnings = load_events(path)
    triggers, marks, soak, summaries, configs, problems = {}, [], [], [], [], []
    for e in events:
        kind = e.get('type')
        if kind == 'trigger':
            triggers.setdefault(e.get('name', '?'), []).append(e)
        elif kind == 'mark':
            marks.append(e.get('t_us'))
        elif kind == 'hotsoak_point':
            soak.append(e)
        elif kind == 'summary':
            summaries.append(e)
        elif kind == 'config':
            configs.append({k: e.get(k) for k in
                            ('config_id', 'bank', 'ch_supply', 'ch_ground', 'ch_feedback',
                             'full_scale', 'current_zero', 'current_valid',
                             'adc_software_mode', 'adc_config_ok', 'aux_position')})
        elif kind in ('adc_error', 'adc_config_error', 'summary_dropped', 'can_drop'):
            problems.append(e)
    out = {'events': len(events), 'warnings': warnings, 'configs': configs,
           'problems': problems,
           'triggers': {k: len(v) for k, v in sorted(triggers.items())},
           'first_trigger_us': {k: v[0].get('t_us') for k, v in sorted(triggers.items())},
           'marks_us': marks, 'hotsoak_points': soak}
    bad = [c for c in configs if c.get('adc_config_ok') is False]
    if bad:
        out['warnings'] = warnings + [
            f'{len(bad)} konfiguracji z niepotwierdzonym ADC — skala napiec niepewna']
    if summaries:
        def worst(index):
            best = max(summaries, key=lambda s: abs(s['ch'][index][2]) if s.get('ch') else 0)
            return {'t_us': best.get('t_us'), 'min': best['ch'][index][0],
                    'mean': best['ch'][index][1], 'max': best['ch'][index][2]}
        out['seconds'] = len(summaries)
        out['extremes'] = {NAMES_V2[i]: worst(i) for i in range(8) if summaries[0].get('ch')}
    return out


def export(path, target, meta_path=None, recovery=False):
    warnings = []
    configs, fallback, _ = resolve_configs(path, meta_path, warnings)
    seen = set()
    with open(path, 'rb') as stream, open(target, 'w', newline='', encoding='utf-8') as output:
        header = read_header(stream)
        writer = csv.writer(output)
        writer.writerow(columns(header['version']))
        for row in records(stream, recovery=recovery, warnings=warnings):
            cfg = fallback if header['version'] < 3 else config_for(
                configs, fallback, row[-1], warnings, seen)
            values = physical(row, cfg)
            writer.writerow(['' if isinstance(v, float) and not math.isfinite(v) else v
                             for v in values])
    return warnings


HTML = """<!doctype html><meta charset="utf-8"><title>EGRLab - %(title)s</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>body{font:14px system-ui;margin:16px;background:#111;color:#eee}
h1{font-size:18px}canvas{background:#181818;border-radius:8px;margin-bottom:18px}
table{border-collapse:collapse;margin:8px 0}td,th{border:1px solid #333;padding:4px 8px}
.warn{color:#fb4}</style>
<h1>%(title)s</h1><p>%(note)s</p>%(tables)s
<canvas id="c1" height="120"></canvas><canvas id="c2" height="120"></canvas>
<canvas id="c3" height="120"></canvas>
<script>const D=%(data)s;
const opt=t=>({responsive:true,animation:false,plugins:{title:{display:true,text:t,color:'#eee'},
legend:{labels:{color:'#bbb'}}},scales:{x:{ticks:{color:'#888'},grid:{color:'#222'}},
y:{ticks:{color:'#888'},grid:{color:'#222'}}}});
const mk=(id,keys,t)=>new Chart(document.getElementById(id),{type:'line',
data:{labels:D.t,datasets:keys.map((k,i)=>({label:k,data:D[k],borderWidth:1,pointRadius:0,
borderColor:['#4ea','#e84','#6af','#fd5','#f6a'][i%%5]}))},options:opt(t)});
mk('c1',['ratio','position'],'Pozycja i ratio');
mk('c2',['ground','ref'],'Masa czujnika i referencja 5 V');
mk('c3',['current','vbat','aux'],'Prad, VBAT, AUX');</script>"""


def report(path, target, meta_path=None, recovery=False, points=3000):
    warnings = []
    configs, fallback, events = resolve_configs(path, meta_path, warnings)
    seen = set()
    with open(path, 'rb') as stream:
        header = read_header(stream)
        rows = list(records(stream, recovery=recovery, warnings=warnings))
    step = max(1, len(rows) // points)
    series = {k: [] for k in ('t', 'ratio', 'position', 'ground', 'ref', 'current', 'vbat', 'aux')}
    clean = lambda x: None if not isinstance(x, float) or not math.isfinite(x) else round(x, 5)
    for row in rows[::step]:
        cfg = fallback if header['version'] < 3 else config_for(
            configs, fallback, row[-1], warnings, seen)
        vals = physical(row, cfg)
        v = vals[12:20]
        _, g, _ = channels(normalise_config(cfg))
        series['t'].append(round(row[0] / 1e6, 3))
        series['ratio'].append(clean(vals[-2]))
        series['position'].append(clean(vals[-1]))
        series['ground'].append(clean(v[g]) if g is not None else None)
        series['ref'].append(clean(vals[-3]))
        series['current'].append(clean(vals[-4]))
        series['vbat'].append(clean(v[6]))
        series['aux'].append(clean(v[7]))
    counts, soak, config_rows = {}, [], []
    for e in events:
        if e.get('type') == 'trigger':
            counts[e.get('name', '?')] = counts.get(e.get('name', '?'), 0) + 1
        elif e.get('type') == 'hotsoak_point':
            soak.append(e)
        elif e.get('type') == 'config':
            config_rows.append(e)
    tables = ''
    if config_rows:
        head = ['config_id', 'bank', 'ch_supply', 'ch_ground', 'ch_feedback',
                'current_zero', 'current_valid', 'adc_config_ok']
        tables += '<table><tr>' + ''.join(f'<th>{h}</th>' for h in head) + '</tr>' + ''.join(
            '<tr>' + ''.join(f'<td>{c.get(h, "")}</td>' for h in head) + '</tr>'
            for c in config_rows) + '</table>'
    if counts:
        tables += '<table><tr><th>trigger</th><th>liczba</th></tr>' + ''.join(
            f'<tr><td>{k}</td><td>{v}</td></tr>' for k, v in sorted(counts.items())) + '</table>'
    if soak:
        head = ['index', 'tc1', 'tc2', 'i_break_open', 'i_break_close', 'ms_10_90', 'ms_90_10']
        tables += '<table><tr>' + ''.join(f'<th>{h}</th>' for h in head) + '</tr>' + ''.join(
            '<tr>' + ''.join(f'<td>{p.get(h, "")}</td>' for h in head) + '</tr>'
            for p in soak) + '</table>'
    if warnings:
        tables += '<p class="warn">' + '<br>'.join(warnings) + '</p>'
    note = (f'wersja formatu {header["version"]}, {len(rows)} rekordow, '
            f'{header["sample_rate"]} Hz, co {step}. probka'
            + (' - DANE SYNTETYCZNE' if header['synthetic'] else ''))
    Path(target).write_text(HTML % dict(title=Path(path).parent.name or Path(path).name,
                                        note=note, tables=tables,
                                        data=json.dumps(series)), encoding='utf-8')
    return warnings


def write_log(path, rows, rate=2000, synthetic=True, version=3):
    with open(path, 'wb') as stream:
        stream.write(HEADER.pack(b'EGRLOG1\0', version, 32, rate, 32, int(synthetic), 1))
        for start in range(0, len(rows), 64):
            part = rows[start:start + 64]
            payload = b''.join(RECORD.pack(*r) for r in part)
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
    cfg_b = config_event(2, full_scale=[10, 10, 5, 5, 2.5, 5, 10, 10], current_zero=2.55)
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
    meta = {'schema': 3, 'firmware': 'EGRLab-v3', 'synthetic': True, 'sample_rate': 2000,
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
        if name == 'export':
            q.add_argument('--csv', required=True)
        if name == 'report':
            q.add_argument('--html', required=True)
    a = p.parse_args()
    try:
        if a.command == 'synth':
            synth(a.file)
        elif a.command == 'inspect':
            print(json.dumps(inspect(a.file, a.recover), indent=2))
        elif a.command == 'scan':
            print(json.dumps(scan(a.file), indent=2))
        elif a.command == 'export':
            print(json.dumps({'warnings': export(a.file, a.csv, a.meta, a.recover)}))
        else:
            print(json.dumps({'warnings': report(a.file, a.html, a.meta, a.recover)}))
    except (OSError, ValueError, KeyError) as e:
        p.exit(2, f'{e}\n')


if __name__ == '__main__':
    main()

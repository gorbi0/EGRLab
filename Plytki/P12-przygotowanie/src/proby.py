"""Próby ujemne src/kontrakty.py: kopie zrodla.json z jedną wstrzykniętą wadą (i próba zerowa bez zmian).
Każda wadliwa kopia musi skończyć się kodem 1 i dodać komunikat o swojej wadzie, którego nie ma w przebiegu bazowym; zerowa ma dać wynik bazowy. Kopie i wyniki tylko w katalogu tymczasowym.
uruchomienie: python3 Plytki/P12-przygotowanie/src/proby.py
"""
import copy, json, subprocess, sys, tempfile
from pathlib import Path

P = Path(__file__).resolve().parents[1]; BAZA = json.loads((P / 'zrodla.json').read_text(encoding='utf-8'))


def plan(cfg):
    return next(p for p in cfg['plytki'] if p['plytka'] == 'P05 R3')['zrodlo']['piny']


def nazwa_sieci(cfg):                  # ADC_SCLK na P05 przemianowane: P03 kieruje ADC_SCLK do P05, który już ma pinout
    plan(cfg)['J_BP2']['2'][0] = 'ADC_SCK'


def brak_nadajnika(cfg):               # ADC_BUSY na P05 jako wejście: na sieci same wejścia
    plan(cfg)['J_BP2']['12'][1] = 'in'


def dwa_nadajniki(cfg):                # VBAT_SENSE na P05 jako wyjście: nadają P02 i P05
    plan(cfg)['J_BP1']['10'][1] = 'out'


def prad_ponad_styki(cfg):             # P10 pobiera 2,5 A przez dwa piny 5V_SYS
    next(p for p in cfg['plytki'] if p['plytka'] == 'P10 R2')['prad_5V_mA'] = 2500


def dziura_w_numeracji(cfg):           # J_BP1 P05 bez pinu 9
    del plan(cfg)['J_BP1']['9']


def opis_w_specyfikacji(cfg, tmp):     # stary nagłówek S1 §8 (x = 80,0 mm dla J_BP P02 R4 w slocie S3)
    spec = P.parents[1] / cfg['opisy_w_specyfikacji'][0]['plik']; kopia = tmp / 'spec.md'
    kopia.write_text(spec.read_text(encoding='utf-8').replace('slot S3, środek x = 133,5 mm', 'slot S3, środek x = 80,0 mm'), encoding='utf-8')
    cfg['opisy_w_specyfikacji'][0]['plik'] = str(kopia)


PROBY = [(None, None), (nazwa_sieci, 'brak na P05'), (brak_nadajnika, 'brak nadajnika'), (dwa_nadajniki, 'więcej niż jeden nadajnik'),
         (prad_ponad_styki, 'na 2 pinach'), (dziura_w_numeracji, 'dziury w numeracji'), (opis_w_specyfikacji, 'slot S3 ma środek')]
wyniki = []
with tempfile.TemporaryDirectory() as t:
    tmp = Path(t)
    baza = subprocess.run([sys.executable, str(P / 'src/kontrakty.py'), str(P / 'zrodla.json'), str(tmp / 'baza')], capture_output=True, text=True).stdout
    for fn, oczek in PROBY:
        cfg = copy.deepcopy(BAZA); nazwa = fn.__name__ if fn else 'proba_zerowa'
        if fn is opis_w_specyfikacji:
            fn(cfg, tmp)
        elif fn:
            fn(cfg)
        c = tmp / f'{nazwa}.json'; c.write_text(json.dumps(cfg, ensure_ascii=False), encoding='utf-8')
        r = subprocess.run([sys.executable, str(P / 'src/kontrakty.py'), str(c), str(tmp / nazwa)], capture_output=True, text=True)
        # zerowa: wynik jak w przebiegu bazowym (baza może mieć prawdziwe błędy, np. pojemność 5 V); wada: nowy komunikat, którego baza nie ma
        ok = (r.stdout == baza) if oczek is None else (r.returncode == 1 and oczek in r.stdout and oczek not in baza)
        wyniki.append({'proba': nazwa, 'oczekiwane': oczek or 'brak błędów', 'wykryta': ok, 'wyjscie': r.stdout.strip().splitlines()[:4]})
        print('OK ' if ok else 'ZLE', nazwa, '->', r.stdout.strip().splitlines()[:2])
(P / 'wyniki/proby.json').write_text(json.dumps(wyniki, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
print(sum(w['wykryta'] for w in wyniki), '/', len(wyniki), 'prób (z zerową)')
sys.exit(0 if all(w['wykryta'] for w in wyniki) else 1)

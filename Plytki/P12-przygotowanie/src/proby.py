"""Próby ujemne src/kontrakty.py: kopie zrodla.json z jedną wstrzykniętą wadą (i próba zerowa bez zmian).
Każda wadliwa kopia musi skończyć się kodem 1 i dodać komunikat o swojej wadzie, którego nie ma w przebiegu bazowym; zerowa ma dać wynik bazowy. Kopie i wyniki tylko w katalogu tymczasowym.
uruchomienie: python3 Plytki/P12-przygotowanie/src/proby.py
"""
import copy, json, subprocess, sys, tempfile
from pathlib import Path

P = Path(__file__).resolve().parents[1]; BAZA = json.loads((P / 'zrodla.json').read_text(encoding='utf-8'))


def plan(cfg):
    """1.10: P05 czyta schemat z chmury (csv); wady wstrzykujemy do kopii jego pinoutu jako planu (ten sam pinout, sprawdzone)."""
    z = next(p for p in cfg['plytki'] if p['plytka'] == 'P05 R3')['zrodlo']
    if z['typ'] != 'plan':
        z.update(typ='plan', piny=z.pop('plan_piny'), ref='origin/main', plik=z['plan_plik']); z.pop('pcb_checks', None)   # 1.10: raport PCB jest na gałęzi płytki
    return z['piny']


def pojemnosc_bez_decyzji(cfg):        # P06 C3 z powrotem 470 µF (stan sprzed decyzji 1.10): razem ponad 600 µF
    next(p for p in cfg['pojemnosc_5V']['plytki'] if p['plytka'].startswith('P06'))['zamiany'] = {'C3': '470u / 16V'}


def schemat_inny_niz_plan(cfg):        # plan z zadania mówi PFAIL_N na J_BP2.16 P05, schemat ma tam GND
    next(p for p in cfg['plytki'] if p['plytka'] == 'P05 R3')['zrodlo']['plan_piny']['J_BP2']['16'][0] = 'PFAIL_N'


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


def budzet_pelny_ryzyko(cfg):          # 5.10: P07 z 900 mA (np. bez decyzji o cewce) — stos ponad 1,8 A z 2 A przetwornicy (uwaga ryzyka, kod 0)
    next(p for p in cfg['plytki'] if p['plytka'] == 'P07 S1')['prad_5V_mA'] = 900


def bez_P07(cfg):                      # 5.10: P07 bez pinoutu — jego sieci wracają do stanu „czeka” (kod 0, ale nie 0 czeka)
    pl = next(p for p in cfg['plytki'] if p['plytka'] == 'P07 S1'); pl.pop('zrodlo'); pl['zlacza'] = {}
    cfg['pojemnosc_5V']['plytki'] = [p for p in cfg['pojemnosc_5V']['plytki'] if not p['plytka'].startswith('P07')]


BEZ_BLEDU = {'budzet_pelny_ryzyko', 'bez_P07'}   # wada sygnalizowana uwagą albo stanem „czeka”, nie błędem
PROBY = [(None, None), (nazwa_sieci, 'brak na P05'), (brak_nadajnika, 'brak nadajnika'), (dwa_nadajniki, 'więcej niż jeden nadajnik'),
         (prad_ponad_styki, 'na 2 pinach'), (dziura_w_numeracji, 'dziury w numeracji'), (opis_w_specyfikacji, 'slot S3 ma środek'),
         (schemat_inny_niz_plan, 'plan z zadania PFAIL_N'), (pojemnosc_bez_decyzji, 'pojemność na szynach 5 V'),
         (budzet_pelny_ryzyko, 'ryzyko: suma budżetów 5V_SYS wariantu pełnego'), (bez_P07, 'czeka 12')]
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
        ok = (r.stdout == baza) if oczek is None else (r.returncode == (0 if nazwa in BEZ_BLEDU else 1) and oczek in r.stdout and oczek not in baza)
        wyniki.append({'proba': nazwa, 'oczekiwane': oczek or 'brak błędów', 'wykryta': ok, 'wyjscie': r.stdout.strip().splitlines()[:4]})
        print('OK ' if ok else 'ZLE', nazwa, '->', r.stdout.strip().splitlines()[:2])
(P / 'wyniki/proby.json').write_text(json.dumps(wyniki, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
print(sum(w['wykryta'] for w in wyniki), '/', len(wyniki), 'prób (z zerową)')
sys.exit(0 if all(w['wykryta'] for w in wyniki) else 1)

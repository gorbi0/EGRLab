"""P12 R1 (wariant LOGGER) — płytka połączeń krawędzi A formatu S1. Części z kontraktu pinowego docs/kontrakt-P12.json (src/kontrakt.py):
J1..J9 — proste obudowane gniazda IDC (wtyk w stronę stosu) dla złączy krawędzi A płytek LOGGER, J10 — IDC 2x10 dla taśmy z P11 (panel);
TP1..TP4 — pola pomiarowe GND / 5V_SYS / 3V3_IO / GND. Bez elementów aktywnych i biernych.
Każdy pin dostaje sieć z kontraktu (GND jawnie); łączenie wyłącznie po nazwie sieci (README, „Elektryka”). Piny sieci, których drugi
koniec jest na płytce wariantu pełnego (P04 / P07 / P08, docs/NIEPODLACZONE.csv), mają znacznik „nie podłączać” i opis z nazwą sieci
(pole nc_nets) — etykieta przy jednym pinie to ostrzeżenie ERC isolated_pin_label."""
from cadlib import *
import csv, shutil
PARTS = {}
exec((P / 'src/helpers.txt').read_text(encoding='utf-8'))
K12 = json.loads((P / 'docs/kontrakt-P12.json').read_text(encoding='utf-8'))
assert not K12['bledy'], K12['bledy']
TP = copyfp('TestPoint', 'TestPoint_THTPad_D2.0mm_Drill1.0mm')
IDC = {n: copyfp('Connector_IDC', f'IDC-Header_2x{n:02d}_P2.54mm_Vertical') for n in (5, 8, 10)}
MPN = {5: 'Amphenol FCI T821110A1S100CEU', 8: 'Amphenol FCI T821116A1S100CEU', 10: 'Amphenol FCI T821120A1S100CEU'}


def add(r, src, sym, fp, value, mpn, pins, sheet, url='', note='', zrodlo='nowe', **extra):
    PARTS[r] = dict(ref=r, source_ref=src, symbol=sym, footprint=fp, display=value, value=value, mpn=mpn, pins={str(k): v for k, v in pins.items()},
                    sheet=sheet, url=url, note=note, qty=1, on_board=True, zrodlo=zrodlo, **extra)


NIEP = {q['pin']: q['siec'] for q in K12['niepodlaczone']}   # 'J1.15' -> 'P04_3V3': drugi koniec na płytce wariantu pełnego
for z in K12['zlacza']:
    n = z['n'] // 2
    assert z['footprint'] == IDC[n], (z['ref'], z['footprint'])
    gdzie = f"poziom {z['poziom']}, {z['slot']}" if z['poziom'] != 'panel' else 'panel, taśma z P11'
    add(z['ref'], f"{z['plytka']} {z['zlacze']}", symbol('Connector_Generic', f'Conn_02x{n:02d}_Odd_Even'), IDC[n],
        f"{z['plytka'].split()[0]} {z['zlacze']} / IDC 2x{n} proste", f"{MPN[n]} (IDC 2x{n} proste obudowane, Au) lub odpowiednik",
        {k: ('NC' if f"{z['ref']}.{k}" in NIEP else s) for k, s in z['piny'].items()}, 'P12', note=f"Do {z['plytka']} {z['zlacze']} ({gdzie}); środek x = {z['x_mm']} mm, z = {z['z_osi_mm']} mm (docs/GEOMETRIA.csv); "
                              'pin 1 od mniejszego x, rząd nieparzysty niżej (taśma prosta, README).',
        plytka=z['plytka'], zlacze=z['zlacze'], typ=z['typ'], nc_nets={k: s for k, s in z['piny'].items() if f"{z['ref']}.{k}" in NIEP})
for k, (net, opis) in enumerate([('GND', 'masa'), ('5V_SYS', 'zasilanie 5V_SYS z P02'), ('3V3_IO', 'zasilanie 3V3_IO z P02'), ('GND', 'masa (druga sonda)')], 1):
    add(f'TP{k}', 'P12_R1', symbol('Connector', 'TestPoint'), TP, net, 'pole pomiarowe THT D2,0 / otwór 1,0 (bez elementu)', {1: net}, 'P12', note=opis, in_bom=False)
if __name__ == '__main__':
    write_tables(); print(len(PARTS), 'parts')

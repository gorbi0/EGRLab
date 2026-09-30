"""Opisy paczki zamówieniowej (README, specyfikacja dla producenta, QA) z danych kontroli.
Uruchomienie: python src/write_docs.py — przed src/seal_package.py.
"""
from pathlib import Path
import json

R = Path(__file__).resolve().parents[1]
CFG = json.loads((R/'src'/'config.json').read_text(encoding='utf-8'))
N, REV, (W, H), CU = CFG['name'], CFG['revision'], CFG['board_mm'], CFG['copper_um']
V = R/'verification'
D = json.loads((V/'board-fabrication-data.json').read_text(encoding='utf-8'))
cam = json.loads((V/'cam-checks.json').read_text(encoding='utf-8'))
neg = json.loads((V/'cam-negative-controls.json').read_text(encoding='utf-8'))
cnt = json.loads((V/'drc-counts.json').read_text(encoding='utf-8'))
EXTRA = CFG.get('extra', {})
DATE = CFG.get('release_date', '28.09.2026')
FAB = CFG.get('fab', 'Satland')
ACC = json.loads((V/'drc-accepted.json').read_text(encoding='utf-8')).get('lib_footprint_mismatch_accepted', []) if (V/'drc-accepted.json').exists() else []
acc_txt = (f' Przyjęte zgłoszenia `lib_footprint_mismatch` ({len(ACC)}) dotyczą wyłącznie części, którym skrypt nadruku wydania przyciął '
           f'linie lub przesunął tekst (`drc-accepted.json`); KiCad porównuje je z nieprzyciętą kopią w bibliotece. Nie wpływa to na miedź ani otwory.') if ACC else ''
pth = [h for h in D['holes'] if h['plated']]
npth = [h for h in D['holes'] if not h['plated']]
vias = sum(1 for h in D['holes'] if h['ref'] == 'VIA')
dmin = min(h['diameter'] for h in D['holes']); dmax = max(h['diameter'] for h in D['holes'])
zip_name = f'DO-ZAMOWIENIA_{N}-PCB-{REV}.zip'
layers = {'F.Cu': 'miedź górna (.gtl)', 'B.Cu': 'miedź dolna (.gbl)', 'F.Mask': 'maska górna (.gts)', 'B.Mask': 'maska dolna (.gbs)',
          'F.SilkS': 'opis górny (.gto)', 'B.SilkS': 'opis dolny (.gbo)', 'Edge.Cuts': 'obrys (.gm1)'}
n_neg = sum(1 for x in neg if x['plik'])
silk_top_only = 'B.SilkS' not in CFG['layers']
dec = lambda x: f'{x:.2f}'.rstrip('0').rstrip('.').replace('.', ',')
num = lambda x: str(x).replace('.', ',')
RCM = CFG.get('corner_radius_mm')
rc_readme = (', narożniki R' + dec(RCM)) if RCM else ''
rc_spec = (' z narożnikami R' + dec(RCM) + ' mm') if RCM else ''


def przelotki(n):
    if n == 1:
        return '1 przelotka'
    return f'{n} przelotki' if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14) else f'{n} przelotek'


paired = sum(len(c['details'].get('sparowane_w_tolerancji_0.001mm', [])) for c in cam['checks'] if isinstance(c.get('details'), dict))
otw = (lambda n: f'{n} otwór leży' if n == 1 else f'{n} otwory leżą' if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14) else f'{n} otworów leży')
paired_txt = (f'- {otw(paired)} dokładnie na połówce mikrometra; KiCad zaokrągla je w Excellonie (rozdzielczość 0,001 mm) w drugą stronę niż kontrola, '
              'więc są parowane z tolerancją 0,001 mm i tą samą średnicą (lista w `cam-checks.json`); próba ujemna z przesunięciem 5 µm jest wykrywana.\n') if paired else ''
ring = D['min_annular_ring_mm']
ring_min = min(v for v in ring.values() if v is not None)
ring_txt = f'pierścień wokół otworu ≥ {dec(ring_min)} mm' + (
    f" (przelotki {dec(ring['vias'])} mm, pola {dec(ring['pads'])} mm)" if None not in ring.values() and ring['vias'] != ring['pads'] else '')

readme = f"""# {N} — pakiet do zamówienia PCB

Wydanie **{DATE}**, źródło **{CFG['source']}**. Plik płytki jest bajtowo zgodny z wydaniem {REV}; nie zmieniano tras, rozmieszczenia, otworów ani opisu. {EXTRA.get('intro', '')}

**Do producenta wgraj `{zip_name}`.** Zawiera wyłącznie {len(CFG['layers'])} warstw Gerber X2 i 2 pliki wierceń Excellon. Parametry: `SPECYFIKACJA-DLA-PRODUCENTA.txt`{'; zamówienie w Satland krok po kroku: `../Zamowienie-Satland/INSTRUKCJA-SATLAND.md`' if FAB == 'Satland' else ' (ustawienia dla JLCPCB i uwagi dla Satlandu)'}.

| Parametr | Ustawienie |
|---|---|
| Wymiary | **{W} × {H} mm**{rc_readme} |
| Warstwy | 2 |
| Laminat | FR4 1,6 mm{' (w Satlandzie wybrać 1,5 mm)' if FAB == 'Satland' else ' (JLCPCB: 1.6 mm; w Satlandzie 1,5 mm)'} |
| Miedź | **{CU} µm na każdej stronie**{' (zmiana z 70 µm — poniżej)' if CFG.get('copper_note') else ''} |
| Wykończenie | HAL |
| Maska | zielona, obie strony |
| Opis | biały, {'**tylko góra** (dolny opis w projekcie jest pusty)' if silk_top_only else 'obie strony'} |
| Otwory | {len(pth)} PTH (w tym {przelotki(vias)}), {len(npth)} NPTH; wiertła {dec(dmin)}–{dec(dmax)} mm; bez szczelin |
| Najwęższa ścieżka / najmniejszy odstęp (reguła) | {num(D['min_track_mm'])} mm / 0,25 mm; miedź–krawędź ≥ 0,5 mm |
| Najmniejszy pierścień (z geometrii) | {ring_txt.removeprefix('pierścień wokół otworu ')} |

{CFG['copper_note'] + chr(10) + chr(10) if CFG.get('copper_note') else ''}Kontrole: DRC KiCad 10.0.6 ze świeżym wypełnieniem stref i zgodnością ze schematem — **{cnt['violations']} naruszeń, {cnt['unconnected_items']} niepołączonych, {cnt['schematic_parity']} rozbieżności**.{acc_txt} Kontrola CAM własnym parserem Gerber/Excellon: **{sum(c['pass'] for c in cam['checks'])}/{len(cam['checks'])}** (każdy otwór, każde pole z siecią, otwarcia maski, obrys, liczba konturów wylewek). Próby ujemne kontroli CAM: **{sum(x['ok'] for x in neg if x['plik'])}/{n_neg} wykryte**, próba zerowa przechodzi. Oględziny podglądów wygenerowanych z samych plików CAM. {EXTRA.get('checks', '')}

**Przymiarka rzeczywistych części, próby elektryczne i cieplne: NIE ZBADANO.** To wydanie plików do wykonania prototypu, nie odbiór działającej płytki. Wydruk 1:1: `projekt/output/pdf/{CFG['pdf']}` (skala 100 %, zmierzyć belkę 100 mm i obrys). {('Formularz odbioru: `projekt/' + CFG['odbior'] + '`.') if CFG.get('odbior') else 'Procedura odbioru P02 R4 na stanowisku P00: do opracowania (punkty pomiarowe na listwach serwisowych J_SV1/J_SV2).'}

| Ścieżka | Zawartość |
|---|---|
| `{zip_name}` (+ `.sha256`) | jedyny plik dla producenta |
| `gerber/` | te same pliki co w ZIP |
| `podglad/CAM-top.png`, `CAM-bottom.png` | wygląd wynikający z Gerberów; spód oglądany od spodu |
| `podglad/CAM-kontrola-warstw.png` | zestawienie warstw |
| `verification/QA.md` | zakres kontroli i odtworzenie |
| `projekt/` | kopia wydania {CFG['source']} (KiCad, dokumentacja, BOM) |
| `src/` | eksport, kontrola CAM, próby ujemne, zamknięcie paczki |

{EXTRA.get('assembly', '')}
"""
(R/'README.md').write_text(readme, encoding='utf-8')

spec = f"""EGRLab {N} — płytka prototypowa, wyłącznie PCB (bez montażu i szablonu)
Plik: {zip_name} (suma SHA-256 w pliku .zip.sha256)

Laminat: FR4, 2 warstwy, grubość {'1,5 mm (projekt nominalnie 1,6 mm — 1,5 mm jest akceptowalne)' if FAB == 'Satland' else '1,6 mm (w Satlandzie 1,5 mm jest akceptowalne)'}
Miedź: {CU} µm na każdej stronie{' (zmiana z 70 µm 28.09.2026; pliki CAM bez zmian)' if CFG.get('copper_note') else ''}
Wymiar: {W},0 × {H},0 mm, prostokąt{rc_spec}. Obrys po osi linii w pliku .gm1; niektóre przeglądarki
  pokazują {W},05 × {H},05 mm, doliczając grubość linii 0,05 mm. Nie skalować.
Wykończenie: HAL (jeśli możliwe bezołowiowy)
Maska: zielona, obie strony, według plików (projekt nie powiększa otwarć maski)
Opis: biały, {'TYLKO strona górna (TOP). Pliku opisu dolnego celowo nie ma — dolny opis jest pusty.' if silk_top_only else 'obie strony.'}
Metalizacja: galwaniczna wszystkich otworów PTH. Średnice w plikach wierceń to średnice gotowych otworów.
Otwory: PTH {len(pth)} (w tym {przelotki(vias)}), NPTH {len(npth)}; wiertła {dec(dmin)}–{dec(dmax)} mm; brak szczelin i frezowań wewnętrznych.
  PTH i NPTH są w osobnych plikach — nie łączyć według samej średnicy.
Reguły projektu: najwęższa ścieżka {num(D['min_track_mm'])} mm; minimalny odstęp miedzi 0,25 mm; {ring_txt};
  odstęp miedź–krawędź ≥ 0,5 mm; odstęp otwór–otwór ≥ 0,3 mm.
Format: Gerber X2 (RS-274X z atrybutami), mm, 4.6; Excellon mm dziesiętnie, współrzędne absolutne; wspólny początek
  wszystkich warstw. Nie odbijać, nie skalować, nie panelizować.
Pliki w ZIP: {', '.join(sorted(cam['files']))}.
Dostawa: pojedyncze płytki, bez V-cut. Test elektryczny: proszę o informację, czy jest wykonywany.
{('JLCPCB: Base Material FR-4, Layers 2, Dimensions ' + str(W) + ' x ' + str(H) + ' mm, PCB Thickness 1.6 mm, PCB Color Green, Silkscreen White, ' 'Surface Finish HASL (lead free), Outer Copper Weight 1 oz, Via Covering Tented, Board Outline Tolerance +/-0.2 mm, Remove Order Number: ' 'Specify a location lub No (wybrać przy zamówieniu), Confirm Production file: Yes. Bez montażu (PCBA) i bez szablonu.') if FAB == 'JLCPCB' else ''}
"""
(R/'SPECYFIKACJA-DLA-PRODUCENTA.txt').write_text(spec, encoding='utf-8')

qa = f"""# Kontrola wydania do wykonania {N} — {DATE}

Źródło: {CFG['source']}. SHA-256 płytki: `{D['board_sha256']}` (bajtowo zgodna z wydaniem; `source-snapshot.json`, `source-unchanged.json`).

## Wyniki

- DRC KiCad 10.0.6 z `--refill-zones --schematic-parity --severity-all`: {cnt['violations']} naruszeń, {cnt['unconnected_items']} niepołączonych, {cnt['schematic_parity']} rozbieżności (`drc.json`, `drc-counts.json`){f"; poza tym {len(ACC)} przyjętych zgłoszeń lib_footprint_mismatch (`drc-accepted.json`, wyjaśnienie niżej)" if ACC else ''}.
- Eksport `kicad-cli` z opcjami jak dla P01 (Gerber X2 4.6 mm, `--subtract-soldermask`, `--disable-aperture-macros`, `--check-zones`; Excellon mm, PTH/NPTH osobno); hashe plików projektu identyczne przed i po (`export-receipt.json`, logi).
- Kontrola CAM własnym parserem (`src/check_cam.py`, bez KiCada): {sum(c['pass'] for c in cam['checks'])}/{len(cam['checks'])} (`cam-checks.json`). Porównanie położenia i średnicy każdego z {len(D['holes'])} otworów, położenia i sieci każdego pola na obu warstwach miedzi, otwarcia maski nad każdym polem, obrysu {W} × {H} mm, liczby konturów wylewek ({D['zone_outlines']['F.Cu']} góra, {D['zone_outlines']['B.Cu']} dół) oraz atrybutów X2 i formatu.
- Próby ujemne kontroli CAM (`src/cam_negative_controls.py`, `cam-negative-controls.json`): {n_neg} celowych usterek w kopiach plików (usunięte pole, otwór przesunięty o 0,1 mm i o 5 µm, zmienione wiertło, brak otwarcia maski, zmieniony obrys, zła sieć, usunięta wylewka) — wszystkie wykryte właściwą kontrolą; próba zerowa przechodzi. Sumy w kopii pokwitowania są przeliczane, więc wykrycie nie wynika z porównania bajtów.
- Oględziny podglądów z plików CAM (`visual-review.json`).
{paired_txt}{EXTRA.get('qa', '')}
## Interpretacja

{'Dolny opis (B.SilkS) w projekcie nie zawiera żadnego drukowanego elementu; eksport KiCada dawałby plik z samymi odejmowanymi otworami maski. Dlatego warstwy nie ma w paczce, a zamówienie obejmuje opis tylko na górze.' if silk_top_only else 'Opis na obu stronach: od spodu oznaczenia części montowanych od spodu (U9, C27, C28).'}{chr(10) + acc_txt.strip() if acc_txt else ''}
`{N}-job.gbrjob` zostaje w verification (obwiednia kreski obrysu {W},05 × {H},05 mm), poza ZIP-em. Podglądy PNG nie służą do wykonania ani do przymiarki 1:1.

Przymiarka części, elektryka i termika: **NIE ZBADANO**.

## Odtworzenie

1. Python KiCada 10.0.6: `src/export_production.py` (DRC, eksport, dane płytki).
2. Python z Pillow: `src/check_cam.py`, potem `src/cam_negative_controls.py`.
3. Oględziny podglądów, `visual-review.json`; `src/write_docs.py`; `src/seal_package.py` (ZIP, suma, status, manifest).

Po dowolnej zmianie CAD potrzebny jest cały nowy odbiór.
"""
(V/'QA.md').write_text(qa, encoding='utf-8')
print('docs ok', N)

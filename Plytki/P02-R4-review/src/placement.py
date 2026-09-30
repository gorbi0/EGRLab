"""P02 R4 placement (format S1, class L: the 2/3 pilot layout with the power block moved 53.5 mm towards the input wall). Writes src/placement.json: ref -> [x, y, rotation]; origin = footprint origin
(pad 1 for THT library parts, centre for SMD). Board: x 0..106.5 (106.5 = input wall), y 0..100 (0 = edge A, 100 = edge B).
Fixed by S1: J_BP (edge A, centre x = 80.0), J_SV1/J_SV2 (edge B, x 10..43 in each slot), J1/J2/J15 at the input wall.
Power chain J1 -> Q9 -> SW_COM -> Q1 -> VSW -> F1 -> J2 runs down the right third; control on the left.
"""
import json
from pathlib import Path
P = Path(__file__).resolve().parents[1]
L = {}


def put(ref, x, y, r=0, side='F'):
    L[ref] = [round(x, 3), round(y, 3), r] + (['B'] if side == 'B' else [])


# ---- S1 connectors ----
put('J_BP', 68.57, 13.32, 90)            # pins 1..19 at y 13.32, 2..20 at y 10.78; pin 1 at x 68.57, centre 80.0
put('J_SV1', 41.74, 95.96, 270)          # pin 1 at x 41.74 ... pin 13 at x 11.26; body front at y = 100
put('J_SV2', 95.24, 95.96, 270)
# ---- input wall ----
put('J1', 90, 24, 270)                   # BAT_IN (90,24), GND (90,31.62); anchors at x = 102.5
put('J2', 96.5, 76, 90)                  # VMOTOR (96.5,76), GND (96.5,68.38), NC (96.5,60.76); face at x = 106.5
put('J15', 99, 2.5, 0)                   # VBAT_CAR pad, top corner at the input wall (no anchor)
put('R38', 99, 6.5, 270)                 # VBAT_CAR (99,5.04) - VBAT_SENSE (99,7.96)
put('D13', 104.3, 8.6, 90)               # VBAT_SENSE (104.3,8.6), GND (104.3,3.52)
put('R59', 96, 16.8, 0)                  # service VBAT_SENSE
put('R34', 86.5, 16.3, 0)                # PG_SEND-PG_LINK wire link under J_BP pins 17/18
# ---- power column: Q9 (tab right = BAT_IN), Q1 (tab left = VSW); sources meet at SW_COM between them ----
put('Q9', 74, 21.46, 270)                # G (74,21.46) D (74,24) S (74,26.54)
put('Q1', 74, 39.58, 90)                 # S (74,34.5) D (74,37.04) G (74,39.58)
put('R61', 81.5, 17.5, 90)                  # service BAT_IN, inside the BAT_IN pour
put('R35', 71.08, 16.3, 180)             # REV_G (71.08,16.3) - GND (66,16.3)
put('C1', 65.5, 21.3, 0)                 # SW_COM reservoir
put('D10', 66, 26.5, 0)                  # SW_COM (66,26.5) - REV_G (71.08,26.5)
R5_XY = (12.0, 77.5, 90)                   # klasa L: przy D11 (SW_COM), zob. koniec pliku
put('R62', 62.4, 25.5, 180)                # service SW_COM
put('C2', 77.3, 31.2, 0)                 # 100 nF B32529 at the sources
# gate of Q1 (right of Q1, under J1)
put('C6', 81, 40, 90)                    # GATE (81,40) - SW_COM (81,35)
put('R22', 86.7, 39.3, 0)                # GATE - SW_COM
put('C5', 80, 44.3, 180)                 # GATE (80,44.3) - VSW (75,44.3)
put('R21', 83.3, 44.2, 0)                # GATE - ON_COL
put('D4', 91.5, 47.5, 90)                # K SW_COM (91.5,47.5) - A GATE (91.5,42.42)
put('R63', 96, 39.2, 0)                 # service GATE
put('R27', 87.5, 50.4, 180)              # OFF_D (87.5,50.4) - GATE (69.72,50.4), lying
put('Q2', 83, 57, 0)                   # Q_OFF: G (83,55.3) D (85.54,55.3) S (88.08,55.3); tab up
put('R64', 72.5, 54.8, 180)                   # service OFF_G
put('R23', 77.5, 54.8, 0)                 # OFF_G - GND (SMD)
# VSW, F1, D3
put('C3', 60, 37, 0)                     # 47 uF VSW
put('C4', 67.8, 40.8, 90)                # 100 nF at Q1 drain
put('R65', 60.6, 55.8, 180)                    # service VSW
put('F1', 75, 61, 0)                   # VSW (75,58.5/61.9) - VMOTOR (84.92,58.5/61.9)
put('D3', 65, 60, 270)                   # VSW (65,60) - GND (65,80.32), lying
put('R66', 83.9, 71.2, 180)                   # service VMOTOR
put('R29', 72, 69.5, 0)                  # LED PWR from VSW
put('LED1', 90.5, 83, 0)
# hold-up: R40, D2 (charge), D1 (OR), C_H at the left edge
put('R40', 45, 33.5, 270)                  # VSW (45,36) - CH_A (45,53.78), lying
put('D1', 55, 43, 270)                   # VSW (55,43) VLOG (55,45.54) HOLD_C (55,48.08); tab right
put('D2', 50, 41, 270)                   # CH_A (50,51) HOLD_C (50,53.54) CH_A (50,56.08); tab right
put('C12', 37, 55.3, 0)                   # C_H lying along the left edge: HOLD_C (5,55.3), GND (12.5,55.3)
put('R41', 40.7, 49.5, 90)                 # C_H bleeder
put('R67', 49.3, 51.2, 270)                    # service HOLD_C
put('C20', 56, 54.3, 180)                  # VLOG bus
put('R68', 59.8, 50.5, 90)                   # service VLOG
# ---- LV (edge A, left of J_BP) ----
put('F3', 9, 2.5, 0)                     # VLOG - VIN_DC33
put('F2', 26, 2.5, 0)                    # VLOG - VIN_DC5
put('U5', 44.5, 5, 90)                   # VIN (44.5,5) GND (47.04,5) 5V (49.58,5)
put('C21', 40, 13, 0)
put('C22', 56.8, 3.3, 0)
put('R69', 57.3, 8.9, 0)                 # service 5V_SYS
put('U6', 23, 22, 90)
put('C23', 18.5, 13, 0)
put('C24', 29, 30, 0)
put('R70', 77.2, 16.2, 0)                 # service 3V3_IO
# ---- PSU_OK ----
put('U10', 37.5, 29.5, 90)
put('C29', 38.8, 18.8, 0)
put('U9', 41, 66, 90, 'B')                # S1-2: SOIC on the bottom under the lying C_H (no THT pads there); GND pins on the B.Cu plane
put('C27', 34.0, 62.5, 90, 'B')
put('C28', 34.0, 67.4, 90, 'B')
put('U7', 2, 20.5, 0)
put('U8', 2, 27, 0)
put('C25', 11, 24, 90)
put('C26', 14.7, 29.3, 90)
put('R42', 3, 36, 90)
put('R43', 7, 36, 90)
put('R44', 21.5, 36, 0)                    # PSU_OK to GND
put('R71', 31, 35.5, 0)                    # service PSU_OK
put('R60', 39, 35, 0)                    # service SUP5_N
# ---- control (STER) ----
put('J14', 10.2, 47.8, 90)                 # PWR_A (10,47.8), PWR_B (10,43.99); anchors at x = 3
put('R9', 15, 44, 0)
put('R10', 19.5, 44, 0)
put('C13', 15, 47.3, 180)
put('R12', 19.5, 47.3, 0)
put('R52', 15, 50.6, 0)                  # service UV_DIV
put('R11', 29, 47.3, 180)
put('R53', 29, 44, 0)                    # service UV_CMP
put('U2', 30, 58, 180)
put('C11', 19.3, 60, 90)
put('R6', 33.0, 47.12, 270)
put('R7', 35.8, 48.5, 90)
put('R13', 10.5, 56.5, 0)
put('U4', 2, 57, 0)
put('R54', 26, 62, 0)                    # service OK
put('U3', 22, 66, 0)
put('R3', 19, 70, 90)
put('R4', 22.2, 70, 0)
put('R51', 15, 66.5, 0)                    # service REF
put('U1', 20, 75, 0)
put('C10', 19.5, 79.5, 0)
put('R2', 9, 82, 0)
put('C9', 7.5, 72, 180)
put('C8', 28.5, 78, 90)
put('C7', 13, 72, 0)
put('R1', 13, 77.5, 0)
put('D11', 3, 79, 0)
put('D12', 39, 85, 0)
put('R50', 24, 87, 0)                    # service AUX5
put('R14', 58.1, 74.5, 90)
put('D7', 58.3, 59.2, 270)
put('D8', 55.5, 64.3, 90)
put('R15', 51.9, 66.9, 270)
put('Q6', 52.1, 63.5, 90)
put('R16', 55.0, 75, 90)
put('R55', 52, 79.5, 90)                   # service ENABLE
put('R36', 4, 62, 0)
put('R37', 10, 62, 0)
put('R56', 15, 62, 0)               # service PFAIL_N
put('Q7', 35.65, 39.5, 0)
put('R30', 24.5, 10, 0)
put('R31', 24.5, 14.5, 0)
put('Q8', 13.05, 39.5, 0)
put('R32', 20.72, 39.5, 0)
put('R33', 28.43, 39.5, 0)
put('R57', 38.4, 44.5, 270)   # 29.09: przeniesiony obok R7 (nakładanie z R33 w pilocie)                    # service SAFE_N
put('R58', 33, 14.5, 0)                    # service P04_3V3
put('Q3', 96.5, 47.5, 90)
put('R17', 100.2, 50.5, 90)
put('R18', 97, 53.8, 0)
put('Q4', 71.5, 73.5, 0)
put('R24', 81, 74.1, 0)
put('D9', 72, 78.5, 0)
put('R25', 81, 78.5, 0)
put('R26', 72, 83, 0)
put('Q5', 81, 83, 0)
put('R19', 72, 87.2, 0)
put('R20', 81, 87.2, 0)
# ---- klasa L (decyzja użytkownika 29.09, opcja 1): w klasie 2/3 trasowanie się nie domykało. Blok mocy, złącza ściany
# wejść, J_BP i J_SV2 przesunięte o jeden slot (53,5 mm) do x = 160; blok sterowania i J_SV1 (slot S1) bez zmian.
# Odległości wewnątrz bloków zostają, między blokami otwiera się pas ok. 30 mm na ścieżki. route_critical.py przesuwa
# wylewki, pasy, korytarz i ścieżki tym samym DX.
DX = 53.5
RIGID = ['J_BP', 'J_SV2', 'J1', 'J2', 'J15', 'R38', 'D13', 'R59', 'R34', 'Q9', 'Q1', 'R61', 'R35', 'C1', 'D10', 'R62', 'C2', 'C6', 'R22', 'C5', 'R21', 'D4', 'R63', 'R27', 'Q2', 'R64', 'R23', 'C3', 'C4', 'R65', 'F1', 'D3', 'R66', 'R29', 'LED1', 'R40', 'D1', 'D2', 'C12', 'R41', 'R67', 'C20', 'R68', 'Q3', 'R17', 'R18', 'Q4', 'R24', 'D9', 'R25', 'R26', 'Q5', 'R19', 'R20']
assert set(RIGID) <= set(L), sorted(set(RIGID) - set(L))
for ref in RIGID:
    L[ref][0] = round(L[ref][0] + DX, 3)
# ---- klasa L, rozsunięcie bloku sterowania (29.09, lokalnie) ----
# Po przesunięciu bloku mocy blok sterowania został gęsty jak w pilocie 2/3 (x 0..61), a pas x ≈ 61..86 pusty. Router
# i planer dokańczania zostawiały 2-5 połączeń; PWR_A nie miała drogi do J14 (pierścień ścieżek na obu warstwach).
# Współrzędne x części sterowania mnożone przez KX od lewej krawędzi (strona panelu): układ i sąsiedztwa zostają, odstępy
# rosną o 35 %. Bez zmian: blok mocy (RIGID), złącza S1 (J_SV1; J_BP i J_SV2 są w RIGID), R70 (położony już w pasie).
KX = 1.35
KEEP = set(RIGID) | {'J_SV1', 'R70'}
for ref in L:
    if ref not in KEEP:
        L[ref][0] = round(L[ref][0] * KX, 3)
# R5 (1 kΩ, początek dzielnika UVLO) z bloku mocy obok D11, do którego i tak dochodzi miedź SW_COM (zasilanie V_CTRL).
# PWR_A (R5.2 → J14.1 → włącznik na panelu) skraca się ze 100 mm przez całą płytkę do odcinka w bloku sterowania,
# a rezystor nadal stoi przy źródle SW_COM, więc zwarcie w przewodach panelu ogranicza do ok. 17 mA.
# Po rozsunięciu cztery części wpadły w strefy dystansów M3 (D7), a siedem kondensatorów odsprzęgających odjechało od
# pinów dalej niż 8 mm (verify_pcb.py §8). Położenia poniżej znalazł skrypt: wolne miejsce (obrysy, strefy M3, na spodzie
# >= 1 mm od pól THT) najbliżej pinu zasilania układu.
put('R58', 43.05, 14.5, 0)
put('D12', 52.65, 81.0, 0)
put('C29', 47.25, 22.5, 270)                # C29.1 - U10.14: 3,4 mm
put('C21', 53.08, 5.0, 180)                 # C21.1 - U5.1: 7,0 mm
put('C22', 64.66, 11.5, 270)                # C22.1 - U5.3: 6,5 mm
put('C23', 31.55, 28.5, 270)                # C23.1 - U6.1: 6,5 mm
put('C24', 37.13, 28.5, 270)                # C24.1 - U6.3: 6,6 mm
put('C25', 9.99, 20.5, 0)                   # C25.1 - U7.2: 4,8 mm
put('C26', 9.99, 27.0, 0)                   # C26.1 - U8.2: 4,8 mm
put('C27', 49.54, 66.72, 270, 'B')          # C27.1 - U9.14: 2,0 mm (obrót przed odbiciem na spód; po odbiciu 90)
# Rezystory listwy serwisowej przy węźle (verify_pcb.py: <= 10 mm od pola sieci węzła): najmniejsze przesunięcie
# do odległości <= 8 mm.
put('R69', 74.11, 7.65, 0)                  # 5V_SYS: 7,9 mm od U5 (było 11,4 mm)
put('R70', 59.70, 19.45, 0)                 # 3V3_IO: 8,0 mm od U10 (było 25,7 mm; położony w pasie przy pierwszym przebiegu klasy L)
put('R71', 38.35, 35.5, 0)                  # PSU_OK: 7,9 mm od R44 (było 11,4 mm)
put('R5', *R5_XY)
# ---- 30.09 (użytkownik, wydruk 1:1): rozsunięcie obu bloków w stronę wolnego pola ----
# Po równym ×1,35 zostało puste pole między blokami (ok. 15 cm²: x 70–95 / y 5–25 i x 45–65 / y 55–75), a oba brzegi były
# ciasne (zajętość obrysami w pasach 20 mm: 49 / 60 / 36 / 24 / 29 / 34 / 76 / 68 %). Blok sterowania rozsuwa się jeszcze raz
# w osi x od strony panelu: górna połowa (y ≤ Y_SPLIT) ×SX_TOP, dolna ×SX_BOT. Układy jadą sztywno ze swoimi kondensatorami
# odsprzęgającymi i rezystorami serwisowymi (CLUSTERS), więc odległości z verify_pcb.py §4 i §8 się nie zmieniają.
# Grupa podtrzymania (HOLD) przesuwa się o DH w lewo; route_critical.py przesuwa o DH jej wylewki VLOG i HOLD_C, ścieżki
# kotwic i przedłużenia VSW do R40/D1. Grupa ENABLE ustępuje miejsca C12. U9, C27, C28 (od spodu) zostają: nad nimi nie może
# stanąć pin THT.
SX_TOP, SX_BOT, Y_SPLIT = 1.25, 1.12, 58.0
DH, HOLD = -8.0, ['C12', 'D1', 'D2', 'R40', 'R41', 'R67', 'C20', 'R68']
DEN, ENABLE = -4.0, ['Q6', 'D7', 'D8', 'R14', 'R15', 'R16', 'R55']
BOTTOM = {'U9', 'C27', 'C28'}
CLUSTERS = {'U5': ['C21', 'C22', 'R69'], 'U6': ['C23', 'C24'], 'U7': ['C25'], 'U8': ['C26'], 'U10': ['C29', 'R70', 'R60'],
            'U2': ['C11', 'R54'], 'U1': ['C8', 'C10', 'R50'], 'R12': ['C13', 'R52'], 'R44': ['R71'], 'R11': ['R53'],
            'R3': ['R51'], 'R37': ['R56'], 'Q7': ['R57'], 'R30': ['R58']}
member = {m: a for a, ms in CLUSTERS.items() for m in ms}
for ref in HOLD:
    L[ref][0] = round(L[ref][0] + DH, 3)
for ref in ENABLE:
    L[ref][0] = round(L[ref][0] + DEN, 3)
shift = {}
for ref, v in L.items():
    if ref in RIGID or ref in HOLD or ref in ENABLE or ref in BOTTOM or ref in member or ref == 'J_SV1':
        continue
    shift[ref] = v[0] * ((SX_TOP if v[1] <= Y_SPLIT else SX_BOT) - 1)
for m, a in member.items():
    shift[m] = shift[a]
for ref, d in shift.items():
    L[ref][0] = round(L[ref][0] + d, 3)
# po rozsunięciu: R30, R31, R58 w strefie dystansu otworu H3, D12 na R55 - najbliższe wolne położenia (skrypt)
put('R30', 40.844, 9.5, 0)
put('R31', 39.094, 14.5, 0)
put('R58', 38.094, 10.5, 90)                # P04_3V3: 3,7 mm od R30.1 (poza strefą H3)
put('D12', 58.718, 81.0, 0)
(P / 'src/placement.json').write_text(json.dumps(L, indent=1) + '\n')
print(len(L), 'placed')

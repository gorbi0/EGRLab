import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1]
ns = {}
for f in ('items.py', 'items2.py', 'tme.py', 'other.py'):
    exec(open(os.path.join(HERE, f), encoding='utf-8').read(), ns)
TME, KAMAMI, WIRES, WIRES_NOTE, SUPP, OPEN, HOLD, OPTIONAL = (ns[k] for k in ('TME', 'KAMAMI', 'WIRES', 'WIRES_NOTE', 'SUPP', 'OPEN', 'HOLD', 'OPTIONAL'))

def zl(x): return f'{x:,.2f}'.replace(',', ' ').replace('.', ',')
def cena(x): return (f'{x:.4f}'.rstrip('0').rstrip('.') if x < 1 else f'{x:.2f}').replace('.', ',')
tme_total = sum(q * p for _, q, p, *_ in TME)
kam_total = sum(q * p for _, _, q, p, *_ in KAMAMI)
wires_total = sum(q * p for _, q, p, *_ in WIRES) + 94.97
far = [x for x in SUPP if x[5] == 'F']
mou = [x for x in SUPP if x[5] == 'M']
far_total = sum(x[3][1] * x[3][2] for x in far)
mou_total = sum(x[1] * x[4][1] for x in mou)
mou_backorder = [x for x in mou if str(x[4][2]).startswith('0 ')]
mou_instock = mou_total - sum(x[1] * x[4][1] for x in mou_backorder)

_starts = [('Układy i półprzewodniki', 'TLC555CP'), ('Rezystory 1 %', 'MF0207FTE-10K'), ('Rezystory 0,1 %', 'MBB0207VD1002BC100'),
 ('Kondensatory THT', 'K104K15X7RF5TH5'), ('Kondensatory SMD', 'GRM21BR71H104KA01L'), ('Złącza na płytkach, bezpieczniki, przełączniki', 'MKDS1.5/2-5.08'),
 ('Wiązki: wtyki, styki, przewód CAN', 'MX-5557-04R'), ('Mechanika', 'TFF-M3X10/DR185')]
_sym = [t[0] for t in TME]
_idx = [_sym.index(s0) for _, s0 in _starts] + [len(TME)]
GROUPS = [(t, _idx[i], _idx[i + 1]) for i, (t, _) in enumerate(_starts)]
assert _idx == sorted(_idx)

L = []
a = L.append
a('# Lista zakupowa 2 — P00, P02–P06, P08–P11')
a('')
a('*28.09.2026. Ceny i stany sprawdzone tego dnia w TME, Kamami, Farnellu, Mouserze i DigiKey. Lista nie jest zamówieniem: po złożeniu zamówienia dopisać pozycje do `Zamowione/ZAMOWIONE.md` i `zamowione.csv`.*')
a('')
a('Zakres: wszystkie płytki z co najmniej pierwszą rewizją, bez P01 (kompletna 24.09) i bez P07 (wstrzymana), bez PCB. Źródła ilości: najnowsze pakiety P00-R3, P02-R3, P03-R5, P04-R2.2, P05-R1, P06/P08/P09/P10/P11-R1 (BOM, ZAKUPY, wiązki); P03-R5 i P04-R2.2 z 28.09 zmieniają względem R4/R2.1 tylko U4 (SN74LVC1G37 zamiast 1G07) i R17 (10k zamiast 100k). Ilości są netto: odjęte zamówienia z 24.09 i zapas P01 (tabela „Pokryte z zapasu” na końcu). P05 ma wartości z recenzji: R5 6,04k, R7 5,11k, R13 47k, opcjonalna 1N5817. Moduły ESP32-S3 i AD7606B są posiadane; MAX31856 XU ×2 kupione na Allegro (wg `P09-R1-review/docs/MODUL-KWALIFIKACJA.md`) — w `ZAMOWIONE.md` wciąż figurują jako brak.')
a('')
a('**Korekta `P00-R3-review/docs/ZAKUPY-P00.md` (mój błąd w R3).** Wiązka stanowiskowa do P04 ma tam dla J2 „gniazdo IDC16” i dla J1 „obudowę żeńską Mini-Fit 4p”. Tymczasem H_SAFE i H_LV04 są przylutowane do P04 i kończą się złączami żeńskimi, a P04 `P00-P04.md` wymaga męskiego IDC16 z usuniętym pinem 4. Ta lista kupuje więc dla P00 męski T821-1-16-S1 (druga sztuka z minimum 2) i męskie gniazdo Mini-Fit 39-29-6048 (dziesiąta sztuka z Farnella), bez żeńskiego IDC16 i bez obudowy 4p ze stykami. J3–J8 bez zmian.')
a('')
a('## Podsumowanie')
a('')
a('| Dostawca | Plik | Pozycji | Wartość | Uwagi |')
a('|---|---|---:|---:|---|')
a(f'| TME — części | `TME-wklej.txt` | {len(TME)} | {zl(tme_total)} zł netto | format „SYMBOL ilość”, do okna szybkiego dodawania TME |')
a(f'| TME — przewody i taśma | `TME-przewody-wklej.txt` | {len(WIRES) + 1} | {zl(wires_total)} zł netto | szpule 10–25 m i rolka 30,5 m taśmy; potrzeba kilkanaście metrów — do decyzji (TME albo zakup lokalny) |')
a(f'| Kamami | tabela niżej | {len(KAMAMI)} | {zl(kam_total)} zł brutto | + wysyłka 8,90–14,90 zł |')
a(f'| Farnell | `FARNELL-wklej.txt` | {len(far)} | {zl(far_total)} zł netto | powyżej 200 zł wysyłka gratis; format „kod,ilość” (LTC4412 wpisany numerem producenta) |')
a(f'| Mouser | `MOUSER-wklej.txt` | {len(mou)} | {zl(mou_total)} zł netto | wszystko na stanie; powyżej 300 zł wysyłka gratis |')
a(f'| Do decyzji | — | {len(OPEN)} | — | bocznik PBV (tylko DigiKey, 163,30 zł), przyciski EAO (panel P11, poza PCB) |')
a('')
a('Każda pozycja poza TME i Kamami ma przypisanego jednego dostawcę (kolumna „Kupić w” w tabeli „Uzupełnienie”); Obie paczki przekraczają progi darmowej wysyłki (Farnell 200 zł, Mouser 300 zł), a każda pozycja jest dziś na stanie. Mouser nie sprzedaje do Polski TBD62083APG i ADR4525BRZ, a LTC4412 ma tam status „ograniczona dostępność”, stąd podział na dwa sklepy.')
a('')
a('## Zamienniki względem BOM')
a('')
a('W TME nie było dokładnego MPN z BOM (brak, zero na stanie albo minimum setki sztuk). Każdy zamiennik ma tę samą funkcję, obudowę i raster; różnice są w kolumnie „Uwagi” tabel TME. Wymagają akceptacji:')
a('')
a('| BOM | Kupowane | Co się zmienia |')
a('|---|---|---|')
for r in [
 ('SN74HC14N', 'CD74HC14E', 'nic poza oznaczeniem (TI HC14, DIP14)'),
 ('TLV1702AQDGKRQ1', 'TLV1702AIDGKR', 'wersja przemysłowa zamiast AEC-Q100, ta sama VSSOP-8'),
 ('BAT85,133 (Nexperia)', 'BAT85S-TAP (Vishay)', 'producent'),
 ('K104K15X7RF53H5 / K103 / K102 / K471', 'K104K15X7RF5TH5, Murata RDER/RDE5', 'kod wyprowadzeń/opakowania i producent; raster 5 mm bez zmian'),
 ('EEUFR1C220, EEUFR1E220', 'EEUFR1H220', '50 V zamiast 16/25 V, ten sam korpus D5×11'),
 ('EEUFR1H4R7', 'EEUEB1H4R7SH', 'seria EB zamiast FR, D5×11'),
 ('C3225X7R1E226M250AB, GRM31CR71E105KA12L, GRM31CR71H104KA01L', 'CL32B226KAJNNNE, C3216X7R1H105KAB, C1206C104K5RAC', 'producent; 1u 1206 ma 50 V zamiast 25 V'),
 ('MF0207 330R, 33R, 560R', 'MBB0207 330R/33R, TE LR1F560R', 'producent'),
 ('232k 1 % (P08 R1)', 'YR1B232KCC 0,1 % (Farnell)', 'lepsza tolerancja; 1 % nie ma nigdzie w detalu'),
 ('SN74LVC1G37DBVR (P03-R5 U4)', 'SN74LVC1G37DBVRQ1 (Mouser)', 'wersja AEC-Q100 tego samego układu; DBVR nigdzie na stanie'),
 ('ADR4525BRZ (P05 U2)', 'REF5025AIDR (Mouser)', 'ten sam pinout SOIC-8; 0,05 % zamiast 0,02 %; zasila tylko okno DAQ_OK (analiza okna zakładała 0,1 %)'),
 ('5,1k 0,1 % (P06 R3, R4)', 'YR1B5K11CC ×2', 'dzielnik zostaje 1:2; wzmocnienie i tak kalibrowane'),
 ('Molex 39-29-9129 (P11 J7)', '39-29-6128 (Mouser)', 'wersja bez kołków, złocona; otwory na kołki zostają puste'),
 ('MBB0207 300k 0,1 % (P05 R33)', 'Vishay Dale RN55E3003BB14', 'producent i seria; 25 ppm/K wg oznaczenia E'),
 ('1R 1 W metalizowany (P05 R1, P06 R6)', 'KNP01U-1R (drutowy, 3×9 mm)', 'technologia drutowa; energii impulsu ≥ 10 mJ / 0,5 ms z karty nie sprawdzałem'),
 ('PR02 1k 2 W (P02 R20)', 'PMR2S-1K', 'producent, korpus 4×11 mm'),
 ('TE HSA2547RJ (poza PCB)', 'Arcol HS25-47RF', 'producent, ta sama obudowa 25 W'),
 ('Würth IDC 612…21621 / 612…23021', 'Amphenol FCI T821 (złocone) / T812 (gold flash, wariant A101)', 'TME nie prowadzi Würtha; obrys nagłówków sprawdzić przy wydruku 1:1, odciążkę T812 przy odbiorze'),
 ('Mini-Fit 39-29-6088 (P03 J9)', 'bez zmian (Mouser); w TME tylko cynowy MX-5566-08A', 'cynowy nagłówek ze złoconymi stykami wtyku — decyzja'),
]: a('| ' + ' | '.join(r) + ' |')
a('')
a('## TME — części (`TME-wklej.txt`)')
a('')
a('Ceny netto przy podanej ilości, stan z 28.09.')
for title, i0, i1 in GROUPS:
    a('')
    a(f'### {title}')
    a('')
    a('| Symbol TME | Szt. | zł/szt | Stan | Płytki | Uwagi |')
    a('|---|---:|---:|---:|---|---|')
    for s, q, p, st, b, u in TME[i0:i1]:
        a(f'| {s} | {q} | {cena(p)} | {st} | {b} | {u} |')
a('')
a(f'**Razem TME — części: {zl(tme_total)} zł netto.**')
a('')
a('## Przewody i taśma IDC (`TME-przewody-wklej.txt`, do decyzji)')
a('')
a('Potrzeba netto: AWG22 ok. 12,4 m, 0,5 mm² ok. 3,6 m, 1,5 mm² 0,6 m, taśma 1,27 mm ok. 1,6 m (16, 10, 8 i 6 żył). TME sprzedaje tylko szpule, stąd koszt. Silikonowe linki w Kamami (22/24/20/16 AWG) są dziś „w oczekiwaniu na dostawę”.')
a('')
a('| Symbol TME | Ilość | zł/j. | Stan | Zastosowanie | Uwagi |')
a('|---|---:|---:|---:|---|---|')
for s, q, p, st, b, u in WIRES:
    a(f'| {s} | {q} m | {cena(p)} | {st} m | {b} | {u} |')
a('| DS1057-16A282R | 1 rolka | 94,97 | 258 | wszystkie taśmy IDC | 30,5 m 16× AWG28; taśmę dzieli się na 10/8/6 żył |')
a('')
a(f'Razem {zl(wires_total)} zł netto. {WIRES_NOTE} 2,5 mm² (P02 SUPPLY, P06 ISERIES/SW1-A, łącznie 0,9 m): w planie P01 jest już zakup lokalny przewodu 2,5 mm² czerwonego i czarnego — dopisać długość (w TME: LGY2.5/10-RD i -BK po 133,50 zł za 10 m).')
a('')
a('## Kamami')
a('')
a('Ceny brutto ze strony produktu, dostępność z karty produktu 28.09.')
a('')
a('| Indeks | Produkt | Szt. | zł/szt brutto | Dostępność | Płytki | Uwagi |')
a('|---|---|---:|---:|---|---|---|')
for i, n, q, p, st, b, u in KAMAMI:
    a(f'| {i} | {n} | {q} | {cena(p)} | {st} | {b} | {u} |')
a('')
a(f'Razem {zl(kam_total)} zł brutto + wysyłka. Goldpinów i zworek nie trzeba: P09 JP1/JP2 i wybierak HB w P00 wychodzą z zapasu (listwa 1×40 z Kamami, ZL201-02G i JUMPER-KPL z TME).')
a('')
a('## Uzupełnienie — Farnell i Mouser')
a('')
a('Pozycje, których TME i Kamami nie mają w detalu. „—” = brak u tego dostawcy (powód w Uwagach). Stany z 28.09.')
a('')
a('| Pozycja | Szt. | Płytki | Kupić w | Farnell: kod, zł/szt, kup, stan | Mouser: nr, zł/szt, stan | Uwagi |')
a('|---|---:|---|---|---|---|---|')
for s, q, b, f, m, d, u in SUPP:
    fs = f'{f[0]}, {cena(f[1])}, {f[2]} szt., {f[3]}' if f else '—'
    ms = f'{m[0]}, {cena(m[1])}, {m[2]}' if m else '—'
    a(f'| {s} | {q} | {b} | {"Farnell" if d == "F" else "Mouser"} | {fs} | {ms} | {u} |')
a('')
a(f'Farnell (`FARNELL-wklej.txt`): {len(far)} pozycji, {zl(far_total)} zł netto. Mouser (`MOUSER-wklej.txt`): {len(mou)} pozycji, {zl(mou_total)} zł netto. Rezystory YR1B są w Mouserze, bo tam minimum to 1 szt. (w Farnellu 5). Części dostępne tylko u jednego dostawcy albo w małej ilości — G6K 5 V (Farnell; TME i Mouser dopiero w 2027), TBD62083APG i LTC4412 (Farnell), C&K 7201SYCBE (Mouser, 10 szt.), 39-29-9069 (Farnell, 23 szt.), TPS2553DBVR (TME, 5 szt.), styki DEUTSCH (TME, 25 szt.) — zamówić bez zwłoki.')
a('')
a('## Do decyzji')
a('')
a('| Pozycja | Szt. | Płytki | Stan sprawdzenia |')
a('|---|---:|---|---|')
for s, q, b, u in OPEN:
    a(f'| {s} | {q} | {b} | {u} |')
a('')
a('Na płytkach nie zostaje żadna część z terminem dostawy dłuższym niż kilka dni, o ile przyjmiesz zamienniki z tabeli „Zamienniki”. Bocznik PBV jest na stanie tylko w DigiKey (trzeci dostawca, wysyłka gratis od 300 zł). Przyciski EAO są na panelu, nie na PCB — zamiennik dobierzemy przy P11 R2.')
a('')
a('## Wstrzymane i opcjonalne')
a('')
a('| Symbol | Szt. | Płytki | Stan / cena | Dlaczego nie ma w plikach |')
a('|---|---:|---|---|---|')
for s, q, b, st, u in HOLD:
    a(f'| {s} | {q} | {b} | {st} | {u} |')
for s, q, b, u in OPTIONAL:
    a(f'| {s} | {q} | {b} | — | {u} |')
a('| DEUTSCH: uchwyty detektorów, przesłona portów, nasadki EAO | — | P11 | — | elementy mechaniczne do wykonania albo dobrania razem z EAO |')
a('| Zaślepka klucza w gnieździe IDC | — | P04 H_SAFE i pozostałe | — | brak osobnej części; zaślepić pozycję ręcznie |')
a('')
a('## Pokryte z zapasu i zamówień z 24.09')
a('')
a('| Pozycja | Potrzeba | Pokrycie |')
a('|---|---:|---|')
for r in [
 ('74LVC125AD,118', '22', 'Mouser 25 szt. (zostają 3)'),
 ('SN74HC08N', '8', 'Mouser 8 szt.'),
 ('MCP120-450DI/TO', '4', 'Mouser 3 + TME 1'),
 ('MCP120-300DI/TO', '5', 'Mouser 4; piąta w uzupełnieniu'),
 ('SN74HC139N', '2', 'Mouser 1 (P03); druga w TME'),
 ('STPS20100CT', '2', 'zapas TME 1; druga w uzupełnieniu'),
 ('LM2903P, TL431BILP', '1 + 1', 'zapas TME / Mouser'),
 ('TSR 2-2450, TSR 2-2433, MCP23017, TPS3808 + PA0085, INA240, MCP3201, MCP6022, MCP1525, MCP1702', 'po 1', 'Mouser 24.09'),
 ('1N4148', '4', 'Kamami 10 + TME 2'),
 ('Adaptery SO14 Kamami', '11 (P02 1, P03 7, P04 3)', '18 kupionych; P05, P06, P08–P10 mają SOIC lutowane wprost, więc 7 zostaje'),
 ('Podstawki DIP14 / DIP16 / DIP-8P', 'P02–P06, P08 / P03, P04 / P06', 'Kamami 24.09; dokupione tylko 2× DIP14 dla P04 U2/U3, DIP8 dla P00, opcjonalna DIP16 dla P09'),
 ('Rezystory 10k, 100k, 4k7, 47k', '—', 'zapas TME po 2 szt. odjęty'),
 ('1R (P00 R6), 6k8 (P08 R16)', '1 + 1', 'zapas TME MF0207FTE-1R i MF0204FTE52-6K8'),
 ('EEUFR1H220, L-934GD', '—', 'zapas TME po 1 szt. odjęty'),
 ('Styki Mini-Fit Au', '72', 'zapas 4 szt. MX-5556GSL7F odjęty'),
 ('Dystanse M3×10', '41', 'zapas 6 szt. odjęty; śruby M3×6 (92), podkładki poliamidowe (98), opaski 2,5 mm (99) i tulejki WAGO 216-206 (2) z zapasu'),
 ('Goldpiny 1×2, zworki', '9 + kilka', 'ZL201-02G (49) i JUMPER-KPL (19)'),
 ('RG174', '0,15 m', 'posiadany przewód'),
]: a('| ' + ' | '.join(r) + ' |')
a('')
a('## Do sprawdzenia przy odbiorze')
a('')
a('Wtyki T812 w wariancie A101: czy mają odciążkę. Nagłówki T821 zamiast Würtha: obrys na wydruku 1:1 P03/P04. Przełącznik 611-7201-054 w Mouserze: czy to wersja 7201SYCBE do druku. RN55E3003BB14: TCR 25 ppm/K w karcie. REF5025AIDR: pinout (2 VIN, 4 GND, 6 VOUT) z kartą TI przed lutowaniem. Farnell zapisuje G6K-2P-Y jako „G6K-2PY DC5”: sprawdzić, że to wersja przewlekana, nie -2F-Y. SN74LVC1G37DBVRQ1: pinout jak w wersji bez Q1. KNP01U-1R: dopuszczalna energia impulsu. Kondensatory 0805 po uwzględnieniu DC bias: P08 C1/C2/C9 ≥ 0,47 µF, P09/P10 C4/C5 ≥ 2,2 µF (wymagania z ZAKUPY tych płytek). Styki DEUTSCH 0460-202-1631: TME ma dokładnie 25 szt., bez zapasu na pomyłkę przy zaciskaniu.')
a('')
with open(os.path.join(OUT, 'ZAKUPY-2.md'), 'w', encoding='utf-8', newline='\r\n') as fh:
    fh.write('\n'.join(L))
print('doc ok', len(L))

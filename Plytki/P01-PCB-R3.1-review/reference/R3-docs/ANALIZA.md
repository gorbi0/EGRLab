# R3 — obliczenia i granice

C5=10nF±5%, C6=1µF±5%, R21=100k, R22=470k, R27=10Ω/2W. C6 WIMA ma takie same
wartość i tolerancję jak poprzednia TDK; obrys nowej części jest 7,2×7,2mm.
Nie zatwierdzono automatycznie zamienników ±10%. Źródła: reference/WIMA_MKS2.pdf,
reference/sources.json. WIMA podaje 15V/µs dla tej pojemności/napięcia; w próbach
ocenić dV/dt na samym C6, nie utożsamiać go ze zboczem VS.

Rachunek podłączenia przy założonym Cgd≤2nF daje VSG≤0,6234V przy 48V.
Cgd to obwiednia inżynierska do weryfikacji, nie gwarantowane maksimum producenta.
LK1 ma w modelu 0,2mΩ; jego rzeczywisty opór i indukcyjność wynikną z wykonania.
Prąd kanału Q1 w modelu i prąd całej gałęzi zmierzony na LK1 są różnymi wielkościami.

| Scenariusz | VSG peak [V] | I kanału peak [A] | wyłączenie [µs] |
|---|---:|---:|---:|
| hot_14_1e-06_0 | 0.143 | 0.000 | — |
| hot_14_1e-06_1 | 0.183 | 0.000 | — |
| hot_14_0.001_0 | 0.013 | 0.000 | — |
| hot_14_0.001_1 | 0.017 | 0.000 | — |
| hot_24_1e-06_0 | 0.238 | 0.000 | — |
| hot_24_1e-06_1 | 0.309 | 0.000 | — |
| hot_24_0.001_0 | 0.015 | 0.000 | — |
| hot_24_0.001_1 | 0.021 | 0.000 | — |
| hot_48_1e-06_0 | 0.453 | 0.000 | — |
| hot_48_1e-06_1 | 0.595 | 0.001 | — |
| hot_48_0.001_0 | 0.019 | 0.000 | — |
| hot_48_0.001_1 | 0.028 | 0.000 | — |
| start_9_0 | 7.406 | 0.659 | — |
| start_9_1.5 | 7.344 | 2.283 | — |
| start_14_0 | 11.529 | 1.208 | — |
| start_14_1.5 | 11.467 | 2.847 | — |
| start_17_0 | 14.002 | 1.555 | — |
| start_17_1.5 | 13.940 | 3.194 | — |
| start_slow_corner | 7.290 | 1.933 | — |
| start_fast_corner | 13.959 | 3.696 | — |
| off_0 | 13.941 | 1.501 | 42.93 |
| off_1 | 13.905 | 1.501 | 64.23 |
| off_step_18_48 | 0.328 | 0.000 | — |
| off_precharged_18_48 | 0.328 | 0.000 | — |
| hot_bounce_24 | 0.297 | 0.000 | — |
| ovp_17_24_delay20us | 13.908 | 96.431 | 77.97 |

## Powrót i obciążenie stałej mocy

Model odbiornika odłącza pobór poniżej 6,5V. Nie modeluje wewnętrznego UVLO,
zapasów regulatora ESP ani pracy karty SD. Przypadki powrotu z HOLD zaczynają
się z naładowaną rezerwą; oddzielny hold_cold_start sprawdza start z0V i ładowanie
przy C+20%/R+5%. Pojemność bezpośrednio widziana przez P01:198µF+22µF=220µF.

| Scenariusz | minimum szyny odbiorników [V] | spadek poniżej 7V |
|---|---:|---|
| recovery_bare_vt1 | 7.658 | NIE |
| recovery_bare_vt2 | 6.496 | TAK |
| recovery_bare_vt3 | 6.496 | TAK |
| recovery_hold_1e-05 | 10.472 | NIE |
| recovery_hold_5e-05 | 8.845 | NIE |
| recovery_hold_0.001 | 8.511 | NIE |
| recovery_burst_bare | 6.493 | TAK |
| recovery_burst_hold | 8.084 | NIE |
| recovery_exhausted_hold | 6.484 | TAK |
| hold_cold_start | 0.002 | TAK |

HOLD ma jawny budżet: 6W na wejściu przetwornic, Ceff≥52,8mF, początek≥9,5V,
łączny spadek gałęzi≤1,2V, szyna≥7V. Rachunek daje około85ms wobec wymogu50ms.
To warunkowy zapas obliczeniowy. Minimalne Ceff, spadek, upływ i pobór podlegają
odbiorowi w0/25/50°C. Czas nie oznacza gwarantowanego dokończenia zapisu SD.

## OVP, SOA, temperatura

Duży prąd w talii OVP pochodzi ze sztywnego źródła i ładowania220µF.
Modele bramki nie zawierają pełnej charakterystyki TVS i źródła samochodowego.
Nie uznajemy wyniku energii modelu za zamknięcie SOA. D3=5KP18A: VBR20–22,1V
przy5mA, VC max29,2V przy174,7A; nie zakładamy idealnego ograniczenia do21V.
Oceniać jednocześnie ID, VDS, czas, temperaturę, D2, D3 i impedancję źródła.
Źródło: https://www.littelfuse.com/assetdocs/littelfuse_tvs_diode_5kp_datasheet.pdf?assetguid=b1ddd6a2-fccb-4327-bea1-7d77c0793479

Rth radiatora4,5K/W odnosi się do warunków producenta. Dla Q1 przy5A i przyjętym
gorącym RDS≤50mΩ moc≤1,25W. D2 liczymy zachowawczo do5W; przy otoczeniu50°C
sam radiator wzrósłby o22,5°C. Dodać izolator, przejście złącze-obudowa i wpływ
obudowy. Pomiar wymagany: Tc<85°C, oszacowane Tj<110°C. Radiatory nie dowodzą
dopuszczalności zwarcia ani liniowej pracy Q1 podczas narastania.

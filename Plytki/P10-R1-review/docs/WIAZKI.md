# Wiązki P10-R1

Właścicielem W1, W2 i W3 jest BOM P10. Każdy koniec przy P10 lutowany do otworów
metalizowanych; trzy kotwy z dwoma otworami Ø3,2 mm. Kotwa 12 mm od osi pierwszego
rzędu lutów; dla drugiego rzędu J2 odległość14,54 mm. Nie lutować do pól SMD.
Zostawić mały łuk przewodu, opaskę zacisnąć na izolacji, bez przecinania jej krawędzią PCB.
Łby opasek i żyły nie mogą ocierać o elementy; dystanse PCB≥10 mm, obejma przy OBD.

| W1 LV10: J1 P10 | Sygnał | P02-R3/J10 |
|---:|---|---:|
| 1 | 5V_SYS | 1 |
| 2 | GND | 2 |
| 3 | 3V3_IO | 3 |
| 4 | GND | 4 |

200 mm, 4×AWG22. P10 J1 od lewej1–4 patrząc na stronę elementów, górna krawędź PCB
przy napisach LV10/CORE. Drugi koniec żeński Mini-Fit Jr4p Au. Nie zwierać szyn5/3,3 V.

| W2: J2 P10 | Sygnał | P03-R2/J8 |
|---:|---|---:|
| 1 | CAN_TX — tylko TP6 | 1 |
| 2 | GND | 2 |
| 3 | CAN_RX | 3 |
| 4 | NC, żyła zaizolowana | KEY4 |
| 5 | NC, żyła zaizolowana | 5 NC |
| 6 | NC, żyła zaizolowana | 6 NC |

150 mm, taśma6×AWG28 raster1,27 mm, IDC2×3 raster2,54 mm Au z odciążką i zaślepką4.
Na P10 rząd górny1/3/5, dolny2/4/6. Czerwony pasek żyły1. Pola4/5/6 NC są obecne
dla czytelnej numeracji, żyły pozostają odizolowane. Kabel sprawdzić miernikiem względem
numerów styków, a nie orientacji fotografii. CAN_TX nie łączy się z transceiverem.

| W3: J3 P10 | Sygnał | OBD męski TypeA |
|---:|---|---:|
| 1, pole kwadratowe po prawej | CAN_H | 6 |
| 2, pole okrągłe po lewej | CAN_L | 14 |

300 mm **całkowitej długości od lutów do styków wtyku**; para CAN o impedancji120 Ω,
2×AWG24. Rozplot przy obu końcach≤10 mm. Skrętka jest odgałęzieniem istniejącej magistrali;
ten limit długości wymaga potwierdzenia na stanowisku przy500 kbit/s. Nie przedłużać
niekwalifikowanym przewodem. Nie dodawać terminacji do P10 ani wtyku.

Wtyk ma 16 pozycji, elektrycznie obsadzone tylko6/14. Styki4,5,16 i wszystkie inne NC;
ekran, jeśli obecny, zaizolowany. GND EGRLab połączona z masą pojazdu przez P01/P02,
przed dołączeniem W3. Zasilacz laboratoryjny pływający bez tego odniesienia nie jest
równoważnym sposobem podłączenia. W3 odpinać przed odłączaniem masy zasilania.
Nie prowadzić W3 równolegle do przewodów mostka/silnika. Obudowa P10 blisko gniazda OBD.

Na stanowisku masa generatora CAN i P10 jest wspólna przez zasilanie/wiązki testowe.
Do badania ACK potrzebne dwa aktywne węzły; sam P10 z generatorem to nie taka para.

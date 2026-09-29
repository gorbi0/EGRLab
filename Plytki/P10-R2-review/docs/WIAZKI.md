# Wiązki P10-R2

W R2 zostaje jedna wiązka: **W3 OBD CAN** (J3). W1 LV10 i W2 CORE CAN z R1 zastępuje złącze J_BP do płytki połączeń P12 (`docs/J_BP.csv`; zasilanie i CAN_TX/CAN_RX z P02 R4 i P03 przez P12). Właścicielem W3 jest BOM P10. Koniec przy P10 lutowany do otworów metalizowanych; kotwa z dwoma otworami Ø3,2 mm, 12 mm od osi rzędu lutów. Nie lutować do pól SMD. Zostawić mały łuk przewodu, opaskę zacisnąć na izolacji, bez przecinania jej krawędzią PCB; łby opasek i żyły nie mogą ocierać o elementy.

Uwaga do layoutu: J3 nie leży na krawędzi A ani B, tylko na jednej z krótkich (przy ścianie wejść lub panelu), bo kabel do gniazda OBD wychodzi z obudowy inną drogą niż taśmy P12 i strona serwisowa.

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

# 02 — Wnioski i narzędzia

## Kluczowe wnioski
- GDS (i40 VF 2013, D4FD): P0404 = aktuator EGR całkowicie otwarty lub zamknięty >4 s (diagnoza 4,4 s); progi: wysoka temperatura silnika aktuatora lub silnik zablokowany; przyczyna wg GDS: obwód silnika aktuatora. Źródło: gds-manuals.ru/data/hme/vf12/2013/dtc/10619683-10619797-10619723-10619835-10619842-10619708-10619764.html (warunki wykrycia, specyfikacja aktuatora, przebiegi wzorcowe).
- Zaślepienie kołnierza EGR nie rusza P0404 — to nie usterka przepływu.
- Niepowodzenie adaptacji EGR poprzedza P0404; są powiązane, ale P0404 nie jest blokadą adaptacji — prawdziwa blokada nieznana.
- Po CAN dostępny **tylko jeden PID EGR** — brak pary desired/actual. Logi OBD nie wystarczą do izolacji usterki → potrzebny oscyloskop. PID EGR traktować jako kanał korelacyjny (znacznik czasu), nie pomiar pozycji.
- **Aktywna regeneracja DPF tłumi EGR**; kilka logów testowych było zafałszowanych przez regenerację (rozpoznanie: ciągłe kanały post-injection Pol1/Pol2).
- Kompresor AC: **Denso 6SE14**, zmienna wydajność, zewnętrzny ECV (nr 977012Y100). Wcześniejsza usterka AC: przerwana żyła w wiązce ECV (nie czynnik, nie ECU, nie czujnik).
- Wspólny mianownik: integralność wiązki — naprawa AC/ECV, połamane mocowania, luźna masa silnika — wszystko po wymianie rozrządu.
- Próbkowanie logów XML Car Scanner/MaxiECU: ~1,8–4,6 Hz zależnie od liczby kanałów → maks. 3–4 kanały na sesję.
- Zawory zdejmowane z tego auta konsekwentnie bez istotnego nagaru — hipotezy nagarowe mało prawdopodobne.
- **Pinout pinów 4/5/6 CUD87 nie jest potwierdzony.** Tabela niżej pochodzi ze schematu Monolith; przy projektowaniu EGRLab v1 funkcjonowało sprzeczne z nią założenie (pin 4 jako wiper). Przed pierwszym wpięciem potwierdź multimetrem, który pin ma 5 V przy zapłonie. Szczegóły i skutki: `01-overview.md`.
- Przy 2 kS/s ciągły zapis ośmiu kanałów mieści się w limicie 4 GiB FAT32 przez 18,6 h — do tej usterki nie potrzeba ani wysokiego próbkowania, ani pretriggera. Kształt i zbocza PWM to nadal robota dla skopu.
- Rejestrator i oscyloskop mają rozłączne słabości: skop ma pasmo, ale nie wie, kiedy patrzeć; rejestrator wie kiedy, ale nie ma pasma. Stąd wyjście wyzwalające z EGRLaba do DHO804.
- Pomiar prądu przez INA240 z odniesieniem na połowie szyny 5 V: **zero trzeba zmierzyć, nie zakładać**. Błąd szyny ±2 % to ±0,2 A przy skalowaniu 0,25 V/A.

## Metoda pracy
- Wielohipotezowa: log → systematyczna eliminacja → zawężenie przed wymianą części.
- Parsowanie logów XML MaxiECU/Car Scanner w Pythonie; wizualizacje wielokanałowe (Chart.js).
- Checklisty i plany testów jako pliki markdown, aktualizowane między sesjami.
- Samodzielna diagnoza i naprawa; bez warsztatów w Hiszpanii.

## Narzędzia
| Kategoria | Sprzęt / zasób |
|---|---|
| Interfejs 1 | **MaxiECU 3** z modułem Kia (konto platformowe): inicjalizacja EGR, adaptacja przepustnicy, kodowanie wtryskiwaczy, cylinder balance, wymuszona regeneracja DPF |
| Interfejs 2 | **Vgate vLinker MC+ 4.0 BLE** + **Car Scanner Pro** (Android, Samsung Galaxy M35), profil Hyundai/Kia extended PID |
| Multimetr | **MS2115A** (cęgowy) |
| Oscyloskop | **Rigol DHO804** (4 kan., 70 MHz, 12 bit, zasilanie USB-C PD 15 V/3 A lub 12 V/4 A; power bank ≥45 W). 4 kanały = korelacja EGR vs AC/ECV w jednym przechwyceniu |
| Przewody pomiarowe | 4× RG174 z BNC (~4 m), komora silnika → kabina, zbudowane i przetestowane; ekrany do wspólnego węzła → jeden przewód na minus akumulatora; probe ratio 1X |
| Sondy zapasowe | Hantek PP-150 (Kamami.pl), zestaw Cleqee (Amazon.pl) |
| Przyrząd własny | **EGRLab v3** (`EGRLab-v3/`) — ESP32-S3 + AD7606B: 8 kanałów jednocześnie (piny 1/3/4/5/6, prąd uzwojenia, VBAT, AUX), termopary K, CAN listen-only, zapis na SD, wyjście wyzwalające do DHO804; tryb TEST steruje zaworem przy zgaszonym silniku. Projekt gotowy, sprzęt do zbudowania |
| Schematy | Monolith, Kia Sportage od 2010 (PDF ~74 s., RU, krutilvertel.com), obejmuje 1.7D |

## Schematy — lokalizacja stron
| Sekcja | Strony książki | Strony PDF |
|---|---|---|
| Sterowanie silnikiem 1.7D, obwód EGR | 449–452 | 56–59 |
| Mapa punktów masowych D4FD | 429–430 | 36–37 |
| Klimatyzacja automatyczna (FATC) | 462–463 | 69–70 |

## Pinout złącza EGR — CUD87 (6-pin, szare)
| Pin | Funkcja | Kolor | ECM CUD-K |
|---|---|---|---|
| 1 | Napęd silnika (H-bridge) | pomarańczowy | 5 |
| 3 | Napęd silnika (H-bridge) | żółty | 20 |
| 4 | Zasilanie potencjometru 5 V | biały | 39 |
| 5 | Wiper / sygnał pozycji | czerwony | 31 |
| 6 | Masa potencjometru (→ GUD09) | niebieski | 23 |

*Zweryfikować względem schematu dla VIN przed pierwszym wpięciem.* **Sporne:** przy projektowaniu EGRLab v1 przyjęto inne mapowanie trójki 4/5/6 (pin 4 jako wiper). Powyższa wersja ze schematu jest wiarygodniejsza, bo jest zmapowana na piny ECM, ale rozstrzyga dopiero pomiar. EGRLab v3 rozpoznaje tę trójkę sam, sprawdzając sześć permutacji; procedura v3 ma ją wpisaną wprost i przy pomyłce wprowadzi w błąd.

## Źródła niedostępne (żeby nie szukać ponownie)
- Portal Kia euro5 GSW (kia-hotline.com/euro5) — blokada: polski NIP niezarejestrowany w VIES.
- ASO odmawiają udostępnienia danych (licencje).
- Krążące PDF-y manuala Sportage SL obejmują tylko benzyny 2.0/2.4, nie 1.7 CRDi.

# P00-R2 - wiązka stanowiskowa do P04

Mapa pochodzi z rzeczywistej netlisty P04 v6.1-rc1; jej odczyt zapisano w `reference/P04-v6.1-contract.json`. Przed pierwszym podłączeniem porównać z finalnym schematem PCB P04: oznaczenia J13-J20 mogą się zmienić, dlatego podano także nazwy funkcjonalne. Kierować się numerami pinów producenta, a nie położeniem lewo/prawo oglądanego wtyku.

## Wykonanie

Przewody sygnałowe AWG24-26 do 20 cm, opisane na obu końcach; po stronie P00 żeńskie Dupont 2,54 mm. Jn.1 jest sygnałem, Jn.2 masą. Masę połączyć z GND P04 przed sygnałami. Dla HB prowadzić sygnał razem z przewodem GND, np. jako skręconą parę. Używać oprawionych wtyków/adapterów do IDC, Mini-Fit i końcówki wiązki H_SAFE. Dupont nie pasuje bezpośrednio do wszystkich złączy P04.

P00 i P04 zasilić z ich właściwych zasilaczy. **Nie łączyć równolegle 3V3 obu płytek.** P00 nie zasila P04. Do odbioru P04 odłączyć CORE, DAQ, DRIVE, SENSOR oraz wiązki auta; przyrząd zastępuje ich wejścia. Pozostawić wyjścia P04 dostępne do pomiaru.

## Podstawowe przypisanie

| Kanał P00 | Wejście P04 | Złącze funkcjonalne / pin | Ref w netliście v6.1 |
|---|---|---|---|
| J1.1 / SW1 | PSU_OK | J_PSUOKA.1 | J18.1 |
| J2.1 / SW2 | DAQ_OK | J_DAQOKA.1 | J13.1 |
| J3.1 / SW3 | DRIVE_OK | J_DRIVEA.7 | J14.7 |
| J4.1 / SW4 | SENSOR_OK | J_SENSORA.3 | J20.3 |
| J5.1 / SW5 | CORE_LINK | J_SAFEB.13 | J19.13 |
| J6.1 / SW6 | PG_LINK | J_PGA.5 | J17.5 |
| J7.1 / SW7 | TEST_KEY | J_PANELSAFEA.3 | J16.3 |
| J8.1 / SW8 | MECH_OK | J_PANELSAFEA.4 | J16.4 |
| J9.1 / SW9 | HEARTBEAT | J_SAFEB.3 | J19.3 |

Wspólna masa P04 jest dostępna m.in. na J16.2/10, J19.2/6/8/10/12/14/16. Nie używać pozycji klucza J19.4. Dokładna liczba równoległych przewodów GND może odpowiadać liczbie złączy w adapterze; wszystkie należą do tej samej masy.

## Dodatkowe trzy odgałęzienia adaptera

Źródłem poniższych H jest **3V3 samego P04, J16.1**. Każde odgałęzienie ma własny rezystor 1 kΩ / 1% / 0,25 W, izolowany termokurczem, oraz rozłączalną zworkę. Te trzy rezystory nie są elementami PCB P00.

| Nazwa | Połączenie | Użycie |
|---|---|---|
| H_SUP | P04 3V3 → 1 kΩ → zworka → J19.15 SUP_N | Ustalony H dla próby ARM/watchdog; rozłączenie bada reset niezależny |
| H_MCU | P04 3V3 → 1 kΩ → zworka → J19.5 MCU_ARM | Żądanie zezwolenia MCU; jego brak musi być osobno zbadany |
| H_HB | P04 3V3 → 1 kΩ → zworka → J19.3 HEARTBEAT | Wyłącznie próba heartbeat zablokowanego w H, po odłączeniu J9.1 P00 |

Podłączenie H_HB i J9.1 jest wzajemnie wykluczające. Złącze rozłączne ma fizycznie uniemożliwiać ich równoczesne wpięcie w ten sam pin. Nie uzyskiwać H przez zwieranie J9 do 3V3. Pozostałe wejścia PWM (J19.1) i SENSOR_ENABLE (J19.11) na początku pozostają w swoim stanie L; w próbach ich torów użyć pożyczonego kanału lub odgałęzienia przez 1 kΩ, po zapisaniu nowej mapy danej próby.

ARM: chwilowy styk NO między J16.9 ARM_CONTACT i J16.10 GND. STOP: styk NC między J16.1 3V3 a J16.7 STOP_NC_OUT. Nie sterować wyjściowego SAFE_N z P00. W mapie szczególnie odróżnić J14.7 DRIVE_OK od J14.1 MOTOR_PERMIT i J14.9 SAFE_N (wyjścia P04).

## Przebieg próby

1. Bez zasilania potwierdzić ciągłość i brak połączenia między szynami 3V3. P00 wszystkie L/STOP, zworki H_SUP/H_MCU/H_HB otwarte. P04 bez połączenia z pozostałymi modułami i bez aktuatora.
2. Połączyć GND, zasilić P04, potem P00. Sprawdzić napięcia. Włączać wejścia kolejno i mierzyć H/L na P04, nie tylko obserwować LED. Główne wejścia buforowane są 74LVC125A; MECH_OK ma dwa pulldowny 10 kΩ równolegle i daje większy spadek.
3. Dla próby uzbrajania ustalić wymaganą kombinację wejść zgodnie z kartą P04, H_SUP/H_MCU oraz zamknięty STOP. RUN heartbeat. Dopiero potem nacisnąć i puścić fizyczny ARM. Zmiana READY na poprawne nie może sama ponownie uzbroić zatrzasku.
4. Testy watchdog osobno: przejście RUN→STOP (stałe L), odpięcie przewodu J9.1 oraz odpięcie J9.1 i dołączenie H_HB (stałe H). Pozostałe wejścia utrzymać bez zmian, aby test nie był rozbrojeniem przez inny warunek. Mierzyć czas od **ostatniego zbocza heartbeat** do zaniku WD_Q/MOTOR_PERMIT. Cel P04 v6.1: 50-150 ms. Po każdej próbie przywrócenie heartbeat nie może zastąpić nowego ARM.
5. Osobno zbadać SUP_N, STOP i każde wymagane wejście, a następnie kombinacje oraz fizyczne styki obecności LOGGER według schematu P04. P00 nie zastępuje mechanicznej próby styków złączy LOGGER.
6. Przed wyłączeniem P04 ustawić źródła P00 w L/STOP i odpiąć wymuszenia. Po odbiorze usunąć wszystkie zworki i wiązkę P00 przed integracją systemu.

Nie ma potrzeby dodawania kolejnych przełączników na PCB P00. Sposób zmiany mapy i stan każdego pomocniczego wejścia trzeba jednak zapisać przy wyniku próby.

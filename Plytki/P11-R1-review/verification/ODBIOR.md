# Odbiór stanowiskowy P11-R1

Wszystkie pozycje początkowo **NIE ZBADANO**. Data/operator/numery PCB:________.
Przyrządy i kalibracja:________. Użyte MPN kontaktów i pary zacisków:________.

| Krok | Kryterium | Wynik / pomiar |
|---|---|---|
| 1. Przymiarka | J1/J7 poprawna geometria,kołki,pozycja1,miejsce na zatrzask;druk1:1 | NIE ZBADANO |
| 2. PCB bez wiązek | Brak zwarć,miedź≥3 mm w czterech torach,brak połączenia TEST/LOGGER i AGND_SENSOR/GND | NIE ZBADANO |
| 3. Każda żyła | Pomiar wg lista-przewodow.csv;zgodność widoku wtyku,polaNC bez żył | NIE ZBADANO |
| 4. Kotwy | LutPTH bez naprężeń,lekki łuk,opaski10–15 mm,próba pociągnięcia bez ruchu lutu | NIE ZBADANO |
| 5. Suche kontakty | Identyfikacja rzeczywistych COM/NC/NO,brak wspólnegoCOM obu sekcjiL1/L2 | NIE ZBADANO |
| 6. Logika bez mocy | Test64 stanów lub komplet przypadków opisany poniżej;MECH_OK tylko pełna pętla | NIE ZBADANO |
| 7. Zasilanie | P04 przy3,18/3,3/3,42 V,pełny P03/P08;SAFE_N≥2,7 V,brak lamp naPANEL_3V3 | NIE ZBADANO |
| 8. STOP | RozwarcieNC wymusza MOTOR_PERMIT/PWM_OUT=0,odtworzenieNC nie uruchamia ruchu bezARM | NIE ZBADANO |
| 9. Rozpięcie | PrzerwanieW1,KEY,każdego NC_A i pętliAT zatrzymuje;wtyczki wewnętrzne przy wyłączonym zasilaniu | NIE ZBADANO |
| 10. Detektory | Wsunąć/wyjąć100 razy,powoli/szybko/przekoszone;zmierzyć momentNC,stykDT,PERMIT | NIE ZBADANO |
| 11. TESTNO | Obecność dopiero przy osadzeniu;przerwany przewód nie daje fałszywegoTEST_PRESENT | NIE ZBADANO |
| 12. Porty | Tylko jeden dostępny/używany port;dwa adaptery niedopuszczone także wLOGGER | NIE ZBADANO |
| 13. Sensor | P08OFF/ON:AGND_SENSOR nie ma obejścia przezPCB,panel,BNC,osprzęt | NIE ZBADANO |
| 14. SCOPE | Poprawny impuls na1 MΩ,amplituda/ringing;nie używać50 Ω | NIE ZBADANO |
| 15. Moc | Obciążenie2/5/10 A,30 min,wpisaneΔT i spadki;bezEGR/ECU | NIE ZBADANO |
| 16. TAP | Znane napięcia5 kanałów,ciągłość0,5 mm²,brak zmieszania sygnałów;przesłuchPWM | NIE ZBADANO |
| 17. Temperatura | PowtórzenieSTOP/ARM/MECH i napięć po nagrzaniu wnętrza | NIE ZBADANO |
| 18. P07 | PozostajeHOLD;powtórzyć7–10 po zatwierdzeniuP07 i finalnego obciążeniaSAFE_N | HOLD |

Przy pustych L1/L2,KEY=TEST,AT zwiera10–11 na odległym końcu:MECH_OK=HIGH.
Każde z osobna:KEYOFF,L1obecny,L2obecny,przerwana pętlaAT →MECH_OK=LOW.
LOGGER_CLEAR=HIGH tylko obaL1/L2puste;nie zależy od kluczyka.
STOP wciśnięty →STOP_NC_OUT pozbawiony zasilania;P04 rozbraja zatrzask.
Przywrócenie trybu/aktywacji po przerwie wymaga ponownegoARM.

P07 niewpięty podczas odbioru użyć wskaźnika/obciążenia logicznego PERMIT/PWM.
Nie zwierać wejść SAFE żeby przejść test. Brak zamkniętego odbioru mechaniki
wyklucza aktywny TEST z samochodową wiązką w sąsiednim porcie.

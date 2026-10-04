# Integracja z CORE i logami

Bez zmian pinów:GPIO17 CAN_TX→P03 J8.1, na P10 R2 przez J_BP pin 6 tylko do kołka serwisowego (R1: TP6), GPIO18 CAN_RX←J8.3.
P03-R2:U11D buforuje RX do MCU, R30=10k podciąga zewnętrzną CAN_RX do3V3_CORE.
Dlatego U2 na P10 ma Ioff i oddziela TCAN.RXD od tego podciągania, gdy P10 nie jest
zasilana. To właściwość układu74LVC125AD Nexperia, nie każdej kostki z napisem125.

Bazowy `reference/board.c`: TWAI_MODE_LISTEN_ONLY, RX kolejka128, TX kolejka0,
timing500 kbit/s, filtr ACCEPT_ALL. Utrzymać listen-only również mimo sprzętowego
S=HIGH/TXD=HIGH. Nie dodawać aktywnego OBD na tej płytce. Szybkość pojazdu potwierdzić;
500 kbit/s jest ustawieniem startowym. ESP32-S3 TWAI obsługuje Classical CAN, nie ramki
CAN FD; możliwości transceivera nie rozszerzają kontrolera MCU.

`reference/app_main.c` zapisuje zdarzenie `can` z t_us,id,ext,rtr,datahex.
t_us jest czasem obsługi odebranej ramki, a nie znacznikiem sprzętowym początku ramki.
Odczyt CAN współdzieli wolniejszą pętlę z temperaturami i podsumowaniami. Kolejka128
może się przepełnić; bez testu obciążenia nie deklarować pełnego zapisu magistrali.

Przed integracją kompletnego firmware:

- Uruchomić odbiór CAN w osobnym zadaniu opróżniającym kolejkę; SD i temperatury
  nie mogą zatrzymywać odbioru. Zliczać przepełnienia RX/kolejki zdarzeń i błędy CAN,
  zapisywać w logach wraz z czasem. Zdefiniować limit ruchu, który zestaw zapisuje bez strat.
- Sesja musi zawierać bitrate, tryb listen-only, źródło czasu i profil interpretacji CAN.
  Dla korelacji szarpnięcia priorytet ma ciągłość DAQ; przeciążenie CAN oznaczyć jawną stratą,
  a nie gubić po cichu próbek EGR.
- RPM: bazowy dekoder akceptuje odpowiedź Mode01 PID0C o ID0x7E8–0x7EF, AB/4.
  P10 nie wysyła pytania. Sama obecność odbiornika nie powoduje tych odpowiedzi.
  Użyć oddzielnego interfejsu diagnostycznego z poprawnym odgałęzieniem albo potwierdzić
  fabryczną ramkę RPM na podstawie pomiaru. Zapisywać ID ECU i profil dekodera.
- Sprawdzić zgodność deklarowanej długości ISO-TP Single Frame z rzeczywistym DLC,
  utratę/nieaktualność RPM, wybór jednego ECU i rozróżnienie braku danych od0 rpm.
  Bazowy fragment dekodera nie sprawdza wszystkich tych warunków.
- Zmierzyć opóźnienie kolejki względem DAQ, przy maksymalnym przewidywanym ruchu i zapisie SD.
  Weryfikować obroty oraz temperaturę odniesienia na postoju przed interpretacją1500–1700 rpm.

Nie zmieniano wspólnego firmware ani nie deklarowano jego pełnej kompilacji w tym pakiecie.
To wymagania na integrację P05/P08/P09/P10. Do P10 nie jest potrzebny nowy sterownik
transceivera; HW silent jest wymuszone fizycznie. Test statyczny kontraktu w
`verify_electrical.py` nie symuluje propagacji, UVLO ani brownoutu.

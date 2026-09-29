# Zamrożone wymagania P10-R1

| ID | Kryterium | Dowód |
|---|---|---|
| E1 | Pinout TCAN1051V, PESD2CAN i LVC125AD zgodny z producentem | XML i niezależny kontrakt pinów |
| E2 | S i TXD staleVIO; CAN_TX tylko J2.1/TP6 | XML, test rzeczywistych sieci i mutacje; test oscyloskopem |
| E3 | RX przez Ioff,100R; pullup10k do lokalnego3,3 V przed buforem | XML, pomiar z wyłączoną P10/CORE na USB |
| E4 | LV10 P02-R3/J10 i CORE P03-R2/J8 zgodne pin w pin | Porównanie z niezależnymi snapshotami |
| E5 | CAN tylko U1/D1/J3, bez terminacji120 Ω | XML oraz pomiar odłączonej płytki |
| P1 |80×70 mm,2Cu,1,6 mm; M3 zgodnie z rysunkiem | Kontrola geometrii i wydruk1:1 |
| P2 | PTH i odciążenie trzech wiązek10–15 mm od lutów | Geometria, oględziny gotowej wiązki |
| P3 | H/L naF.Cu, bez przelotek, <15 mm każda; TVS przy wejściu | Kontrola finalnych ścieżek; oscyloskop |
| P4 | C1/C2/C3 blisko zasilania, przelotkaTVS GND<1,5 mm | Geometria plus wizualna pętla powrotu |
| P5 |0 DRC/unconnected/parity, brak wyłączeń pojedynczych błędów | Świeży raport ze skrótami źródeł |
| Q1 | Kontrole negatywne wykrywają celowe błędy | Raporty elektr./PCB; nie zastępują recenzji |
| Q2 | Czysta regeneracja schematu i PCB z zapisanejSES | Raport odtworzenia i odcisk geometrii |
| Q3 | Wszystkie strony PDF czytelne, wydruk1:1 | Oględziny renderów i rozmiarówPDF |
| H1 | P10 nie wprowadza dominacji ani ACK przy dowolnymCAN_TX | Stanowisko z oscyloskopem; ODBIOR |
| H2 | Brak niedozwolonego zasilania przez RX przy różnych kolejnościach szyn | Stanowisko; ODBIOR |
| H3 | Liczba ramek/opóźnienia/straty zmierzone pod obciążeniem | Integracja firmware i stanowisko |

Gdy kryterium dotyczy sprzętu, status początkowy jest NIE ZBADANO. Sama zgodna topologia
Ioff nie dowodzi poprawnego zachowania podczas wolnego brownoutu. Uzupełnienie ODBIOR
jest wymagane przed użyciem w aucie. Rewizja schematu/PCB nie nadaje automatycznie PASS.

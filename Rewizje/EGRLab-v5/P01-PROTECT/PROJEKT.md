# Obliczenia i uzasadnienie

## Tor mocy i sterowanie

Obie anody STPS20100CT (D2.1 i D2.3) łączą się z BAT_FUSED, wspólna katoda D2.2 z VS. Q1 ma źródło na VS i dren na VPROT. Dioda strukturalna Q1 przewodzi z VPROT do VS; odwrotna orientacja tranzystora ominęłaby odcięcie OVP. D2 zatrzymuje przepływ z VS do akumulatora, także gdy energia wraca przez diodę Q1.

Zasilanie U1 pochodzi z VS, przed Q1. R1=150 Ω i D5 ograniczają obciążenie wejścia regulatora podczas przepięcia. D5 to **1.5KE18A**, z VWM=15,3 V i VC=25,2 V przy katalogowym impulsie. Nie mylić go z 5KP18A, którego VWM wynosi 18 V. C7 ma 35 V. Przy 24 V na wejściu D5 może się nagrzewać również przy odłączonym wyjściu.

LM2936 ma wymaganie stabilności: główny kondensator wyjścia co najmniej 10 uF, ESR 0,3-8 Ω. Dlatego C9=47 uF ma szeregowy R2=1 Ω. Dobierz C9 o ESR poniżej 7 Ω również na zimno; nie usuwaj R2 po zamianie kondensatora na bardzo niskoimpedancyjny. Lokalne 100 nF przy układach pozostają.

TL431BILP pracuje jako wzorzec około 2,495 V. Przy AUX5=4,85 V i wysokiej wartości REF prąd przez R3=820 Ω pozostaje powyżej 2,8 mA przed odjęciem małych obciążeń, z zapasem wobec 1 mA wymaganego do regulacji. Na REF nie ma kondensatora: przypadkowo dobrana pojemność mogłaby wprowadzić niestabilność TL431.

MCP120 trzyma OK nisko podczas startu i spadku AUX5. U2.1/U2.7/U4.1 są otwartymi wyjściami i wolno je połączyć. R13 jest ich jedynym pull-up. Maksymalny statyczny prąd ściągania jest mniejszy niż 2,5 mA. D7/D8 oddzielają niski stan OK, który dla LM2903 może osiągać 0,7 V, od bazy bufora Q6.

| Stan | Q3/Q5 | Q4 | Q2 | Q1 |
|---|---|---|---|---|
| Brak AUX5 lub błąd | wyłączone | wyłączony | włączony, jeżeli istnieje VS | wyłączony |
| OK po zakończeniu POR | włączone | włączony | wyłączony | włączony |
| INHIBIT zwarty | wyłączone | wyłączony | włączony | wyłączony |

Q2 ma stałą polaryzację bazy przez R23 i nie potrzebuje ESP32 ani AUX5, aby podciągać GATE do SOURCE. Q4 podczas prawidłowej pracy blokuje Q2. R21 kształtuje włączanie, natomiast Q2/R27 zapewniają oddzielny, mocniejszy tor wyłączania. R22 pozostaje pasywnym powrotem GATE do SOURCE. D4 ogranicza ujemne VGS; dodatnie ogranicza przewodzeniem wprost.

To nie jest architektura odporna na każdą pojedynczą awarię elementu. Na przykład zwarcie D-S Q1 usuwa aktywne odcięcie. F1 chroni przewody i skutki zwarć, a nie gwarantuje przetrwania MOSFET-a przy każdym zwarciu wyjścia.

## Progi

Osobna D6 pozwala mierzyć napięcie przed diodą **mocy**, bez doprowadzania ujemnego napięcia do wejść U2. Jej spadek nie zależy bezpośrednio od prądu silnika, ale zależy od temperatury. Kalibracja uwzględnia D6.

Niech VD będzie spadkiem D6, VL/VH niskim/wysokim napięciem OK, a RT=R5+RV1. Pomijając prądy polaryzacji i offset:

```
OV_REF = (VREF/R7 + VOK/R8) / (1/R7 + 1/R8)
VIN_OV = VD + OV_REF * (1 + RT/R6)

VIN_UV = VD + VREF * (1 + R9/R10 + R9/R11) - VOK * R9/R11
```

OVP wykorzystuje VH przy wyłączaniu i VL przy powrocie. UVLO wykorzystuje VL przy załączaniu i VH przy wyłączaniu. Ponieważ oba wyjścia dzielą OK, poniżej okna UV i powyżej okna OV sprzężenia są wspólne; okna nie nakładają się i nie powoduje to oscylacji w modelu DC.

Model z rzeczywistymi wartościami rezystorów, obciążeniem OK=80 uA, VD=0,60 V i prądem wejść 25 nA daje RV1 około **2,143 kΩ**, OVP **18,00/16,66 V**, UVLO **9,85/9,37 V**. RV1 należy ustawić pomiarem, nie samą liczbą obrotów śruby.

Kontrola 5000 zestawów parametrów daje orientacyjną wrażliwość OVP około 17,52-18,54 V i UVLO około 9,01-9,77 V przy opadaniu. To nie gwarantowane granice: przyjęto m.in. VD=0,4-0,85 V, obciążenie OK=20-150 uA, tolerancję wzorca z dryftem, offset U2 do ±15 mV i prądy wejść do 500 nA. Kalibracja pokojowa usuwa część rozrzutu, lecz nie cały dryft termiczny.

W pobliżu progów OVP wejścia U2 są około 2,5 V, wewnątrz zakresu przy AUX5=5 V. Przy silnym przepięciu wejście pomiarowe może przekroczyć AUX5. Dla **klasycznego TI LM2903P** producent dopuszcza poprawny stan wyjścia, jeżeli drugie wejście jest we właściwym zakresie; wejście pomiarowe nadal pozostaje daleko poniżej maksymalnej wartości 36 V. Nie zakładać tej własności dla dowolnego innego komparatora. D6 blokuje wejście ujemne.

## Straty i radiatory

Dla dwóch równolegle obciążonych sekcji D2 użyto producentowego przybliżenia strat przewodzenia. Dla Q1 przyjęto budżet RDS(on)=50 mΩ na gorąco: dwukrotność katalogowych 25 mΩ przy VGS=-4,5 V. Mnożnik temperaturowy jest założeniem projektowym wymagającym pomiaru.

| Prąd | D2, oszacowanie | Q1, budżet gorący | Suma | Spadek sumaryczny |
|---:|---:|---:|---:|---:|
| 1 A | 0,56 W | 0,05 W | 0,61 W | 0,61 V |
| 3,5 A | 2,02 W | 0,61 W | 2,63 W | 0,75 V |
| 5 A | 2,94 W | 1,25 W | 4,19 W | 0,84 V |

Do wymiarowania radiatora D2 przyjmij bardziej zachowawczo **4,75 W** (5 A razy 0,95 V). Wymagaj radiatora D2 <=5 K/W oraz Q1 <=10 K/W, z uwzględnieniem rzeczywistej wentylacji obudowy. Przy otoczeniu 50°C i styku termicznym 1 K/W daje to około 79°C obudowy diody i 64°C obudowy MOSFET-a. Docelowo wymagamy obudów obu elementów poniżej 85°C i oszacowanego Tj poniżej 110°C.

Blaszka D2 ma potencjał VS, blaszka Q1 ma VPROT. Wspólny nieizolowany radiator zwarłby odłącznik. Zastosuj dwa radiatory lub podkładki i tulejki izolacyjne, a izolację sprawdź omomierzem po dokręceniu. Rth izolacji wlicz do bilansu.

## Start, szybkie odcięcie i przepięcia

C5=220 nF wprowadza sprzężenie Millera, a R21=4,7 kΩ ogranicza prąd bramki. Orientacyjny prąd podczas plateau wynosi 1-3 mA, co daje narastanie około 5-14 V/ms. To oszacowanie, nie specyfikacja czasu ani limit prądu. C6 i rzeczywiste pojemności Q1 wpływają na przebieg.

Limit sumy pojemności bezpośrednio na VPROT wynosi 220 uF. Energia ładowania przy 17 V to około 32 mJ. Sama energia nie wystarcza do oceny MOSFET-a: zmierz jednocześnie VDS i ID, a przebieg porównaj z SOA SUP53P06-20, uwzględniając temperaturę obudowy i powtarzalność. Nie wolno uruchamiać tego modułu z już zasilanym silnikiem albo zwartym wyjściem.

Q2 ma prąd bazy około 5 mA przy VS=12 V i może szybko przeładować bramkę przez 47 Ω. Ładunek dodatkowego C5 przy zmianie 15 V to 3,3 uC; wraz z C6 i Q1 jest to kilka uC. Przy prądzie rzędu 50-100 mA czas jest rzędu dziesiątek mikrosekund. **100 us od przekroczenia 18,5 V do |VGS|<0,5 V to cel odbiorczy, nie wynik pomiaru ani gwarancja.** Uwzględnij magazynowanie ładunku w Q4/Q5 i przewody montażowe.

D1 15KPA24CA ma w katalogowym impulsie VC=40,7 V przy 371 A i 25°C; D3 5KP18A ma VC=29,2 V. Ich zachowanie zależy od impulsu, temperatury i indukcyjności montażu. Przyjmujemy do odbioru: VS <=48 V i VPROT <=32 V w zdefiniowanych próbach impulsowych. Pozostaje zapas do 60 V Q1 oraz 36 V przetwornic TSR. To nie oznacza, że EGR może być długo zasilany 32 V: J4 musi od razu rozbroić SAFE_N/KPWR.

Nie ma potwierdzonej odporności na pełny, nieograniczony load dump. Przykładowe 100 V przez 400 ms i 2 Ω źródła oznaczałyby setki dżuli do rozproszenia; oznaczenie 15 kW transila nie uzasadnia takiej zdolności. Wymagania dla testu samochodowego muszą wynikać z wybranego przebiegu i energii, a nie z samej nazwy elementu. Próbę wykonuje się odpowiednim generatorem; nie odłącza się akumulatora podczas pracy silnika.

## Układ mechaniczny

Zaprojektowano montaż ręczny, bez WSON/QFN. Płytka uniwersalna FR4 około 100 x 160 mm może służyć prototypowi; to nie projekt gotowego PCB. Tor 5 A wykonaj przewodem miedzianym 1,5-2,5 mm², bez prowadzenia go ścieżkami płytki stykowej. Mocowania złączy i dużych transili muszą przenosić obciążenia mechaniczne.

D1 umieść przy wejściu, D3 przy Q1/J2. Pętle transili do masy mają być możliwie krótkie i szerokie. Masę U2/U3 poprowadź osobno do GND_STAR, z dala od prądu impulsowego D1/D3. Q2, R27, D4, C5 i C6 umieść przy Q1. R1, R23, radiatory i transile odsuń od TL431/D6 oraz dzielników progowych. Nie dokładaj filtrów RC na OVP bez pomiaru czasu odcięcia.

## Źródła producentów

Weryfikowane 22.09.2026. Dane elementów nie są wynikami pomiaru kompletnego modułu.

1. Vishay SUP53P06-20, doc. 68633: https://www.vishay.com/docs/68633/sup53p06-20.pdf
2. ST STPS20100CT: https://www.st.com/resource/en/datasheet/stps20100.pdf
3. TI LM2903/LM393, SLCS005AH, zwłaszcza tablice 5.10 i 5.11: https://www.ti.com/lit/ds/symlink/lm393.pdf
4. TI LM2936, SNOSC48O, pinout i sekcja 8.2: https://www.ti.com/lit/ds/symlink/lm2936.pdf
5. TI TL431, SLVS543S, obudowa LP: https://www.ti.com/lit/ds/symlink/tl431.pdf
6. Microchip MCP120/130, DS11184D: https://ww1.microchip.com/downloads/en/devicedoc/11184d.pdf
7. Littelfuse 15KPA: https://www.littelfuse.com/assetdocs/tvs-diodes-15kpa-datasheet?assetguid=5152edba-6eab-4c4a-9bef-2c97b144328e
8. Littelfuse 5KP: https://www.littelfuse.com/~/media/electronics/datasheets/tvs_diodes/littelfuse_tvs_diode_5kp_datasheet.pdf.pdf
9. Vishay 1.5KE, doc. 88301: https://www.vishay.com/docs/88301/15ke.pdf
10. Vishay BZX55, doc. 85604: https://www.vishay.com/docs/85604/bzx55.pdf
11. onsemi 2N5551: https://www.onsemi.com/download/data-sheet/pdf/2n5550-d.pdf
12. onsemi 2N5401: https://www.onsemi.com/download/data-sheet/pdf/2n5401-d.pdf
13. Bourns 3296: https://www.bourns.com/docs/product-datasheets/3296.pdf

Nie dołączono kopii kart katalogowych do paczki; powyższe odnośniki identyfikują źródła do kontroli przed zakupem.

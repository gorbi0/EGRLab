# Montaż i uruchomienie

PCB:80×70 mm,2 warstwy,FR4 1,6 mm,Cu35 µm. Ścieżki≥0,30 mm,odstęp≥0,25 mm,
przelotki0,8/0,4 mm. Cztery M3:(5,5),(75,5),(5,65),(75,65) mm; podkładki OD≤8 mm.
Brak elementów pod spodem. Maskować przelotki po obu stronach. Wymagany producent PCB
wykonujący metalizację otworów i soldermaskę. Jest to płytka do ręcznego lutowania,
bez QFN/BGA:SOIC8,SO14,SOT23,0805 i dwa rezystory przewlekane DIN0207.

1. Wydruk montażowy100% i belka100 mm. Przymierzyć obudowę, dystanse i trzy wiązki.
2. U1/U2/D1: sprawdzić oznaczenia i pin1 względem F.Fab, nie względem obrotu napisu.
   U1 na PCB obrócony270°, piny1–4 w górnym rzędzie od prawej; U2 pin1 w lewym górnym rogu.
   D1:1=CAN_L,2=CAN_H,3=GND. Dwa dolne wyprowadzenia D1 są liniami, górne wspólne GND.
3. Wlutować SMD, potem R1/R2, na końcu wiązki PTH z opaskami. Umyć topnik przy układach.
4. Bez zasilania zmierzyć ciągłość wszystkich żył, brak zwarć szyn i H/L.
   P10 nie może wnosić terminacji120 Ω. Pomiar rezystancji przez układy półprzewodnikowe
   zależy od polaryzacji miernika — porównać oba kierunki, nie wymagać idealnej nieskończoności.
5. Zasilanie bez magistrali, limit początkowy20 mA na każdej szynie. TP1 około5 V,
   TP2 około3,3 V; U1.1 i U1.8 mają3,3 V. Sprawdzić TP4/TP5 w stanie recesywnym.
6. Stanowisko CAN: dwa sprawne aktywne węzły i dwa terminatory120 Ω na końcach magistrali,
   P10 jako krótki odczep300 mm. Wspólna masa przez zasilanie. Początkowo500 kbit/s.
7. Wykonać i zapisać wszystkie próby w ODBIOR.md, w tym zaniki5/3,3 V i CORE na USB.
8. Dopiero po kwalifikacji stanowiskowej podłączyć zmontowany logger do samochodu.
   Najpierw sesja na postoju i porównanie z interfejsem odniesienia.

Rezerwa w bilansie P02:10 mA dla5V_SYS i10 mA dla3V3_IO. To budżet projektowy,
nie wynik pomiaru. TCAN w silent pobiera wg tabeli maks.2,5 mA z VCC, VIO maks.300 µA
bez obciążenia zewnętrznego; bufor, rezystor i przełączanie zwiększają pobór.
Wartość25 V na kondensatorach nie dopuszcza podania12 V na J1.

Ochrona D1 dotyczy krótkich przepięć linii CAN. P10 korzysta z ochrony zasilania P01
i stabilizacji P02. Nie ma dowodu kwalifikacji całego układu wg ISO7637/ISO10605/EMC,
ani separacji galwanicznej. Przypadkowe stałe zwarcie CAN do źródła energii nie jest
zastępowane przez znamionowanie TVS.

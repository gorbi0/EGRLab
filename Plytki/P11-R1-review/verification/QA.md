# QA P11-R1 - 27.09.2026

Status: CAD do recenzji. Sprzęt,mechanika,wiązki i próby termiczne NIE ZBADANO.

| Kontrola | Wynik |
|---|---|
| Native ERC KiCad10.0.6 | 0 naruszeń,4 arkusze |
| Netlista vs części | 22 części,159/159 pinów |
| Kontrakty elektryczne | 38/38 PASS;P03/P04/P05/P06/P08 oraz baseline portów |
| Stany kontaktów | 64/64 zgodnych;model grafu prawdziwej netlisty |
| Geometria PCB i stackup | 36/36 PASS |
| Celowe błędy obwodu/PCB | 17/17 +13/13 wykrytych |
| Native DRC / brakujące / parity | 0 /0 /0 |
| Wyłączenia pojedynczych naruszeń | Brak |
| Reguły DSN | 0,30/0,25 mm;via0,8/0,4 mm |
| Miedź mocy | Cztery ścieżki3 mm/70 µm;13,8/10,8 mm;bez przelotek |
| GND,niezależny graf geometrii | Jeden połączony obszar |
| Czysta odbudowa | Identyczna geometria i4 pliki schematu;ponownie kontrole PASS |
| PDF | 4×A3 schemat +4×A4 PCB;wszystkie strony wyrenderowane i obejrzane |

PDF montażowy sprawdzono pod kątem numeracji pól,rast­rów,kołków złączy,kotew,
M3 i czytelności. Widok dolnej warstwy to prześwietlenie z góry,bez lustra.
J1 odsunięto od ogonka L1 o4 mm dla opisów. Importowana sesja zawiera to samo
rozmieszczenie co końcowa PCB. Sesja została sprawdzona przez świeże DRC po
adaptacji; nie uznajemy wyniku autoroutera za zatwierdzenie. Końcowa PCB ma67
przelotek,322 odcinki/przelotki łącznie,11 footprintów obwodu i4 mocowania.

Raporty w verification wiążą się z aktualnym CAD. Pliki routing są pośrednie;
część opisów drukowanych powstaje po trasowaniu. Domyślnie pomijane klasy KiCad
są jawne w drc.json/ignored_checks. Nie deklarujemy,że program sprawdza każdą
możliwą regułę. Skrypty dodatkowe sprawdzają rzeczywiste otwory,kotwy,kołki,
zgodność padów,oddzielenie sensorGND i warunki czterech torów mocy.

Otwarte odbiory:przymiarka zakupionych J1/J7;komplet nasadek kontaktów;
geometria i sekwencja detektorów DT;SAFE_N przy pełnym obciążeniu i temperaturze;
rezystancja i termika całej wiązki;przesłuchy TAP. Budżet upływności przy granicy
3,18 V nie jest potwierdzony dla nieznanego P07. Wspólnego firmware nie zmieniono.
P07 nadal HOLD. Brak Gerberów zatwierdzonych do produkcji i brak prób w aucie.

Nie zmieniono wcześniejszych płytek. Kopie referencji mają własne SHA256;
manifest obejmuje cały dostarczony pakiet. Czystą odbudowę można wykonać wg
docs/ODTWORZENIE.md. Recenzję rozpocząć od docs/DLA-RECENZENTA.md.

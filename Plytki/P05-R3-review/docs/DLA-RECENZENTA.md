# Zakres niezależnej recenzji P05-R1

**R3 (1.10.2026, format S1):** recenzji podlega schemat R3: złącza J_BP1/J_BP2, listwy serwisowe, typy części (SMD 1206, posiadane THT, rezystory precyzyjne 1206), SW1 JS202011AQN i budżet okna DAQ_OK — szczegóły w `README.md`. B2B P03/P05 i mating z tekstu niżej już nie obowiązują. Dowody: `verification/QA.md` (`verify_s1.py` i `verify_electrical.py`).

**R2 (29.09.2026):** recenzji podlega tylko schemat R2 (zmiany w `README.md`). PCB nie ma — layout powstanie w formacie S1; `wip-layout-obrys-R1/` to tylko wzór odsprzęgania przy U1. Poniższy tekst pochodzi z R1.

Proszę oceniać tę paczkę, nie tylko tekst ogólnej v6.1. Schemat, PCB i skrypty są edytowalne. Netlista ma pochodzić z eksportu KiCad, a kontrola DRC musi być świeża i powiązana z hashami plików.

## Najpierw sprawy elektryczne

1. Wszystkie64 piny AD7606B według wariantuB, zwłaszcza CONVST9,WR10,VDRIVE23,SDI29,REF_SELECT34, osobneREGCAP36/39 i wspólneREFCAP44/45. Nie podstawiać symbolu staregoAD7606 bez porównania.
2. Zasilanie lokalne3V3 zAVCC: normalna kolejność, zaniki, ładowanie/rozładowanie pojemności i graniceVDRIVE względemAVCC. Ocenić, czy potrzebna jest dodatkowa ograniczająca różnicę dioda/układ — nie dodawać jej bez bilansu prądu i napięcia przy uszkodzeniu.
3. Niezależne źródłoADR dla okna i model tolerancji. Przesunięcie progów do wnętrza zakresu jest celowe. Ocenić zakłócenia przy progu oraz wydłużenie odpadania przekaźników przez diody.
4. MISO rzeczywiście trójstanowe przyCS=H; BUSY i wszystkie drogi przez bufory mająIoff. Oba przypadki braku zasilania modułu sprawdzić w integracji.
5. Wspólne zwolnienie trzech cewek i poprawna numeracja G6K/TBD62083. Zwrócić uwagę naCOM, polaryzację diod i to, żeMEAS nie wymagaARM silnika.
6. Wpływ rezystancji wejściowej ADC, offsetu, filtrów i dryftu na diagnozę. Kalibracja całego toru z adapterem; AUXLO odłącza shunt100k. CH6 jest zerem, nie prądem.

## PCB i montaż

Sprawdzić miedź, nie tylko render3D. Płaszczyzna pod analogiem, ścieżki referencji, odsprzęganie i powroty masy wymagają oceny człowieka. DRC nie symuluje szumu ani odporności na zakłócenia. Sprawdzić rzeczywistą dostępność do lutowaniaU1/U3 oraz sondowaniaTP.

**Mechanicznie otwarty punkt:** mating kątowy P03/P05 i przyporządkowanie poziomów styków. Jest tabela testu1:1; fizycznie jej nie wykonano. Nie uznawać zgodnego logicznego pinoutu za wykonany test mechaniczny. Podobnie SW1: wariant terminaliC i korpus, a nie dowolny7201.

Sprawdzić realnyCeff C12/C13; w BOM jest kandydat22µF25V1210, a nie deklaracja zmierzonej pojemności pod napięciem. Ogólne rezystory pasywne dobierać według podanej tolerancji, TCR, mocy i rozmiaru; specjalnie nie wymyślono numerów katalogowych części, których konkretnego wariantu nie zweryfikowano.

## Dowody i ich granice

`verify_electrical.py` odczytuje fizyczne piny zXML i porównuje z niezależnymi regułami. TablicaREADY jest wyliczana z rzeczywistych pinówHC08, a nie z samej oczekiwanej formuły. Dziewięć mutacji musi zostać wykrytych. `verify_pcb.py` uruchamia natywneDRC, porównuje każdy pad zXML, sprawdza geometrię i pięć mutacji. `verify_schematic.py` sprawdza spójność generatora i schematu — nie zastępuje recenzji układu.

Automatyczne kontrole **nie dowodzą** poprawnej pracy analogowej, zgodnościEMC, jakości lutowania, matingu zakupionych złączy ani skuteczności diagnozyP0404. FormularzODBIOR pozostaje niewypełniony do czasu prób.

Przed wydaniem do produkcji: zamknięta recenzja, mechanikaB2B/SW1, kwalifikacja kondensatorów, uzgodniona zmiana sekwencji startowej firmware, ponowne kontrole po każdej korekcie i dopiero eksportGerberów/Excellon. P07 pozostajeHOLD.

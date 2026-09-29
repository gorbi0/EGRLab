# Źródła P00-R2

Źródła producentów sprawdzone 25.09.2026. Historyczne materiały R1 są zachowane oddzielnie; poniższa lista dotyczy bieżącego doboru.

- TI LM2937-2.5/-3.3, **SNVS015F**, strony 4-5 i 11-12: https://www.mouser.com/datasheet/2/405/lm2937-3.3-484674.pdf . To dokument TI w kopii dystrybutora. Nie przenosić tabeli innego wariantu LM2937. Granice i ich zastosowanie zapisano w requirements/electrical.json.
- Panasonic EEUFR1H220: https://industrial.panasonic.com/ww/products/pt/aluminum-cap-lead/models/EEUFR1H220 . 22 µF / 50 V, D5 x L11, raster 2 mm.
- Panasonic FR-A, tabela 50 V: https://industrial.panasonic.com/cdbs/www-data/pdf/RDF0000/ABA0000C1259.pdf . Dla C6 Zmax = 0,340 Ω przy 100 kHz / 20°C. Karta serii jest źródłem jednostki Ω; na stronie WWW jednostka tabeli jest niespójna.
- Yageo MFR, kwiecień 2024, strony 2-3: https://yageogroup.com/content/Resource%20Library/Datasheet/YAGEO-MFR_DATASHEET.pdf . Rodzina MFR-25, 0,25 W, normalny korpus 6,3 x 2,4 mm, zakres od 1 Ω; składnia MFR-25FRF52-.... Nie używać miniaturowego MFR25S jako podstawy wymiarów.
- TI TLC555: https://www.ti.com/lit/ds/symlink/tlc555.pdf . Układ astabilny i działanie RESET; wyjście obciążone podlega pomiarowi.
- Würth 450301014042: https://www.we-online.com/en/components/products/datasheet/450301014042.pdf . COM na środkowym pinie 1, połączenie z kontaktem przeciwnym do położenia suwaka.
- Kingbright L-934YD, dokument producenta w kopii: https://www.activecomponents.com/dbdocument/1208518/K491106-DS.pdf . Dotyczy LED9.
- Kingbright L-934ID, dokument producenta w kopii: https://asset.conrad.com/media10/add/160267/c1/-/gl/812265765DS00/datenblatt-2888735-kingbright-l-934id-led-bedrahtet-rot-rund-3-mm-20-mcd-40-30-ma-2-v.pdf . Dotyczy LED10; wersja bez wbudowanego rezystora.
- Vishay 1N5819: https://www.vishay.com/docs/88525/1n5817.pdf . Dioda szeregowa D1. Budżet 0,6 V przyjęto do obliczeń projektu; TP3 podlega pomiarowi.
- Phoenix 1715721: https://www.phoenixcontact.com/en-pl/products/pcb-terminal-block-mkds-15-2-508-1715721 . J10.
- P00/P04 v6.1-rc1: kopie importu P00 i mapy P04 w reference/. Mapa wiązki wymaga ponownego potwierdzenia przy zatwierdzeniu finalnej PCB P04.

Pliki PDF zewnętrznych producentów nie są warunkiem wykonania generatora. Wartości wymagań zapisano jawnie, a strony i linki pozwalają je niezależnie sprawdzić.

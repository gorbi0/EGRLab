# Zakupy i wykonanie

`hardware/BOM.csv`: każdy element z oznaczeniem i płytką. `hardware/zakupy.csv`: nazwa i ilość sztuk, zgrupowane dla całego obwodu. Złącza w tej tabeli to rodziny z wymaganą liczbą styków i obciążalnością; przed zamówieniem samych PCB dopasuj konkretną serię/footprint i kodowanie do fizycznie kupionych korpusów. Standardowe rezystory/kondensatory kup z zapasem 20–30%, układy kluczowe po jednym zapasowym egzemplarzu. Tych zapasów nie doliczono automatycznie do BOM.

Nie kupuj LM74800EVM-CD. P01-PROTECT zastępuje go w tej rewizji. Nie sumuj osobno BOM P01 z główną tabelą: P01 jest już ujęty. Zasilanie, adaptery i styki mocy przewymiarowano obciążalnością; bezpieczniki i limity zaworu zostają niższe.

Kolejność zamówień:

1. P01, P02, radiatory, podstawowe materiały P00, przewody i mierzalne obciążenie.
2. CORE/SD, DAQ, adapter L2, TEMP — pierwszy użyteczny zapis gorącego auta.
3. I-LOGGER, L1, CAN — prąd i kontekst obrotów/sterowania.
4. SAFE, DRIVE, SENSOR, adapter T — pełny tester, po odbiorze samych blokad.

P01 to większość elementów przewlekanych. MCP3201, MCP6022 i logiczne 74HC są DIP; referencje/LDO/nadzory dostępne w TO92. INA240 i bufory Ioff SOIC/SO14 można montować na adapterach. AD7606B nadal wymaga nośnika LQFP64: kup gotowy właściwy moduł lub zleć jego montaż. Moduł z podobnym napisem AD7606 nie zastępuje bez sprawdzenia AD7606B — połączenia i rejestry różnią się. Przy gotowych nośnikach nie dubluj na ślepo ich elementów; audytuj schemat i dopasuj zgodność z połączeniami P05.

Materiały poza elementami elektrycznymi: karta microSD FAT32 jakości przemysłowej lub trwała karta markowa, podstawki DIP, adaptery SOIC/SO14/LQFP, dystanse M3, izolatory radiatorów, tulejki zaciskowe, termokurcz, opisy przewodów, osłony styków mocy, przewód termoparowy właściwego typu, dwa komplety oryginalnych pasujących złączy EGR i przewody adapterów. Rodzaj PCB/nośnika i długości przewodów zależą od wykonanej mechaniki; nie są sztucznie liczone jako „1 układ”.

Na wszystkich płytkach pozostaw punkty: wejście i wyjście każdej szyny, GND przy sygnale, READY, CS, SCLK, MISO. DRIVE dodatkowo INA OUT, REF25, OC_LOW/HIGH, OC_LOCAL_N, LOCAL_CLEAR_N, OC_GOOD, LOCAL_PERMIT, PWM i zaciski Kelvin. DAQ: CONVST, BUSY, RESET, REFCAP, oba REGCAP; nie łącz kondensatorów REGCAP_A i REGCAP_D.

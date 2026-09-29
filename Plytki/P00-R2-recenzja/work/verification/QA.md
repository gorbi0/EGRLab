# P00-R2 - kontrole wydania

Pakiet wykonuje następujące kontrole:

| Kontrola | Oczekiwany wynik finalnego wydania |
|---|---|
| ERC | 0 naruszeń według reguł projektu |
| Netlista | 66 elementów, 37 sieci, 145 pinów, 0 rozbieżności |
| Natywny DRC, wszystkie poziomy, zgodność schematu | 0 / 0 / 0 |
| Kontrole gotowej PCB | 24/24 |
| Mutacje PCB | 10/10 wykrytych przez wskazaną kontrolę |
| Warunki pracy odczytane z eksportu i BOM | 11/11 |
| Mutacje warunków pracy | 6/6 |
| Czysta regeneracja bez P02 | Sukces całego pipeline; zgodna geometria PCB |
| Fizyczna przymiarka i pomiary | NIEWYKONANE |

Aktualne wyniki i liczby są w `schematic-check.json`, `pcb-checks.json`, `negative-controls.json`, `electrical-checks.json` i `electrical-negative-controls.json`. `clean-rebuild.json` jest osobnym potwierdzeniem próby z czystego katalogu. Same oczekiwane liczby z tej tabeli nie stanowią wyniku testu.

Mutacje PCB obejmują osiem prób przejętych z R1 oraz błędną wartość R5 i obejście R6. Każda musi oblać oczekiwany test szczegółowy, a nie tylko dowolny DRC. Mutacje elektryczne obejmują 5 V na J10, otwarte R5, R5 100 kΩ, błędny MPN C6, ominięty powrót R6 oraz R6 = 0 Ω. Nie zmieniają plików finalnej płytki.

DRC wiązany jest hashami z aktualną PCB, schematem, bibliotekami, źródłami generatora, wymaganiami, netlistą i wejściami routingu. Pakowanie odmawia użycia raportów dla zmienionych wejść. Hashe manifestu i zawartość ZIP sprawdzane są po utworzeniu archiwum.

Źródłem reguł elektrycznych jest `requirements/electrical.json`; kontroler nie importuje `parts.py`. Uwzględnia tolerancje i TCR R5, budżet D1, COUT oraz dobór C6. Ograniczenia: obliczenia ESR dotyczą wskazanych warunków katalogowych, bilans cieplny jest oszacowaniem; pomiary opisuje `docs/ODBIOR-P00-R2.md`.

Przed przekazaniem obejrzeć rzeczywiście wyrenderowany schemat PDF oraz wszystkie cztery strony dokumentu PCB. Wydruk montażowy zawiera belkę 100 mm; fizyczne dopasowanie sprawdzić z częściami.

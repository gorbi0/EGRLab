# Odbiór cyfrowy PCB-R3 (wydanie R3.1)

Wynik maszynowy: `release-status.json` i `pcb-checks.json`. Właściwy projekt jest
w `eda`. W tej rewizji odbiór obejmuje **31 kontroli**, w tym świeży natywny DRC
i zgodność schematu, oraz **5 celowych usterek**. Liczba kontroli nie zastępuje
przeglądu funkcjonalnego ani przymiarki.

## Jedno polecenie

Uruchomić Pythonem dołączonym do KiCad 10.0.6, z katalogu pakietu:

```text
python src/run_release.py --docs-python <Python-z-reportlab> --node <node.exe> --sharp-module <katalog-modulu-sharp>
```

Opcja `--rebuild` odtwarza lokalne zmiany z zamrożonej R2, modele gabarytowe i BOM
montażowy A1. Bez niej sprawdzany i eksportowany jest aktualny plik PCB.
`verify_pcb.py` także sam zawsze wykonuje nowy DRC. Błąd narzędzia, brak JSON,
naruszenia albo zmiana wejść w trakcie kontroli uniemożliwiają PASS.

Kolejność: ewentualna generacja -> kontrola PCB + świeży DRC -> próby błędów ->
natywne eksporty KiCad -> PDF i świeże podglądy jego stron -> sprawdzenie, że wejścia się nie zmieniły ->
zapis identyfikacji wyników. Oględziny wyrenderowanego PDF są oddzielnym etapem.

## Co kontrolujemy

- Elementy, sieci, geometria padów oraz niezmienione schematy R3.
- Format i miedź, otwory, mocowania, zakazy miedzi radiatorów i wypełnione strefy.
- Zachowanie tras krytycznych, Kelvin LK1, odcinki sondowania i termiki J7.
- Reguły CAD, brak wyłączeń DRC, oznaczenia TO-220 i pól pomiarowych.
- Sąsiedztwo funkcjonalne, limity wrażliwych sieci, droga J5 aż do krawędzi.
- Lokalną drogę D4 do G/S <=8 mm, nominalny prześwit D4-C6 >=1 mm, dostęp od
  spodu i obecność modeli krytycznych części.
- Świeżość wyniku: PCB, schemat, projekt/reguły, biblioteki, modele, źródła i skrypty.
- R3.1: BOM A1 - każda część kupowana ma źródło w rejestrze zakupów, uwagi montażowe BOM R3
  (wyprowadzenia, polaryzacja) są zachowane, a pola AssemblyMPN
  i AssemblyValue w PCB zgadzają się z `docs/BOM-MONTAZOWY-A1.csv`. Kontrola otworów
  montażowych nie zależy od liczby stref radiatorów.

Kontrola sąsiedztwa kondensatora jest filtrem błędnego rozmieszczenia, nie analizą
impedancji pełnej pętli. Długość sieci nie jest pomiarem EMC. Modele są gabarytowe.

## Próby ujemne

1. Usunięcie ścieżki do TP2: wykrycie przerwy także w natywnym DRC.
2. Poszerzenie SAFE_N do 12 mm przy pozostawionym czystym raporcie: stary wynik
   odrzucony, świeży DRC wykrywa zwarcia.
3. Usunięcie zakazu miedzi HS2: wykrycie brakującego obszaru reguł.
4. Usunięcie znacznika taba Q2: wykrycie utraty informacji montażowej.
5. Odsunięcie D4 bez korekty ścieżek: wykrycie niespełnionej drogi i połączeń.

Pliki usterek są tylko w `verification/negative-controls`. Nie zmieniają oryginału.
Raporty JSON i logi przechowują konkretne przyczyny odrzucenia, nie sam licznik.

## Ograniczenia i wydanie

Przymiarka, izolacja rzeczywistych części, lutowanie i próby elektryczne NIE ZBADANE.
Gerber/Excellon po przymiarce. Manifest końcowego pakietu obejmuje źródła i wyniki;
archiwalne ścieżki absolutne w logach wskazują środowisko wykonania, nie zależność
layoutu od tego komputera. Do ponownej oceny po przeniesieniu użyć nowego przebiegu.

# 03 — Chronologia kampanii (skrót rozmów z projektu claude.ai)

| Kiedy | Wątek | Wynik |
|---|---|---|
| czerwiec 2026 | Szarpanie 1600–1800 obr. przy lekkim gazie po serii napraw (rozrząd, przepustnica, EGR, solenoid VGT; wcześniej turbina i regeneracja wtryskiwaczy). Auto przejechało Warszawa → Camposol. | Solenoid VGT mało prawdopodobny (brak P0299/P2262/P2263). Wybór interfejsu: Vgate vLinker MC+ + Car Scanner Pro (odradzone klony ELM327). |
| lipiec 2026 (do 23.07) | Przerywany brak klimatyzacji, bez kodów. Analiza logów FATC i silnika z MaxiECU. | **Przyczyna: przerwana żyła ECV** między FATC a kompresorem. Naprawa obejściem. Znalezione połamane mocowania wiązki i luźna masa silnika po wymianie rozrządu. Szczegóły: `04-klimatyzacja-ECV.md`. |
| lipiec 2026 (do 25.07) | Wielohipotezowa diagnostyka szarpania z logami XML (Python + Chart.js). | Wykluczone: powietrze w paliwie, IQA wtryskiwaczy, adaptacja przepustnicy. Regeneracja DPF maskowała objaw. EGR głównym podejrzanym. Pojawia się **P0404**, potem tryb awaryjny. Szczegóły: `05-szarpanie-historia.md`. |
| od 21.07 | Adaptacja EGR w MaxiECU | „Initialization EGR” zawsze błąd warunku wyzwolenia; „EGR Replacement” OK. |
| sierpień 2026 (do 15.08) | Powrót do PL z aktywnym P0404 (kasowanie co 10–20 km). Zaszyfrowany log MaxiECU. Poszukiwanie schematów. | Log nieczytelny (klucz MaxiECU, tryb ECB). Ticket eskalowany. Hipoteza wspólnej przyczyny P0404 i usterki ECV (przetarcie / wspólna masa). Zakupiony PDF Monolith, wyciągnięty pinout CUD87. Auto zostało na lotnisku w Alicante do połowy września. |
| 03.09.2026 | Zaślepienie EGR | Odrzucone (patrz decyzje w `01-overview.md`). |
| sierpień–wrzesień 2026 | Wybór oscyloskopu (DHO804 / DHO802 / handheldy / PicoScope 4425A), logistyka (Ryanair, InPost), przewody RG174, power bank, pętle masy. | Kupiony **DHO804** w cenie DHO802. Przewody zbudowane i przetestowane. Procedura v1 → v2 (recenzja innego modelu: przyjęte Math CH2−CH3, powtarzalność 3–5×, podkategorie FAIL w Kroku 5, zastrzeżenie o pamięci; odrzucone: sondy ×10 na pinach 4/5/6, usunięcie progów liczbowych, osłabienie Window trigger) → **v3** (limity DHO804 z datasheetu, H7, test AC na początku, ścieżka B). |
| wrzesień 2026 | 7 dni w Camposol, goście, brak pomiarów. | Jedno P0404 w najcieplejszy dzień (~35°C). Obserwacje wpisane do v3. |
| ~20.09.2026 | Manual GDS dla D4FD | Definicja P0404 wskazuje na obwód silnika aktuatora / temperaturę silnika aktuatora — do uwzględnienia w v4. |

## Wyciągnięte lekcje o współpracy
- Błąd metodyczny z lipca: zaproponowany test AC on/off, choć log z 24.07 (AC zawsze włączona) już podważał jego założenie. Zawsze najpierw sprawdzić istniejące dane.
- Przy wyborze oscyloskopu była prośba o restart poszukiwań bez zakotwiczenia na pierwszej rekomendacji — nie trzymać się pierwszego pomysłu.

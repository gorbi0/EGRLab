---
name: tme-mouser-lookup
description: "How to read TME/Mouser/Farnell/Kamami stock in the built-in browser, bot-block limits, PL shipping thresholds (Mouser 105 zł below 300 zł) — learned 2026-09-24, extended 2026-09-28"
metadata:
  node_type: memory
  type: reference
  originSessionId: 1bdb3685-394a-4886-bbc7-14b9957d5ea4
  modified: 2026-09-28T13:38:08.663Z
---

TME: w karcie tme.eu (po przejściu Cloudflare przez użytkownika; 28.09 trzeba było dwa razy, bo ajax dostawał 403 aż do przeładowania strony) stan i ceny czytać zapytaniem z kontekstu strony: `POST /ajax/common/product/data` z JSON `{isFactoredPrice:false,isGrossPrice:'false',items:[{symbol:'SYMBOL_TME',amount:N}],scope:['prices','stock','delivery_confirmed']}` (w `deliveries` jest termin dostawy, np. tydzień/rok). Wyszukiwanie: `POST /ajax/common/catalog/search?dataScope=products` z `{queryPhrase, page, onlyInStock:'0'|'1'}` → `productList.products[]` (symbol, manufacturerSymbol, minimumQuantity, multiples, unit, description). Parametry (np. „Pokrycie styku”) z `fetch('/pl/details/<symbol>/')` + DOMParser. Frazy polskie trafiają słabo — lepiej symbol/prefiks albo wartość („330Ω”) i filtr po opisie.

Asortyment TME (09.2026): brak Würth Elektronik (IDC → Amphenol FCI T821 złocone / T812 gold flash, A101), brak Adafruit, brak Isabellenhütte PBV; Mini-Fit Au (39-29-60x8/9xx9) tylko po 10–32 szt., cynowe 39-28-1xx3 po 1 szt.; linki tylko szpule 10–250 m; rezystory 0,1 % w detalu tylko nieliczne (MBB0207 10k/20k/100k, MRA0207-30K1); wiele MF0207FTE ma 0 szt. — zamiennik MBB02070C…FCT00.

Pułapki: „null w magazynie TME” to NIEZAŁADOWANY stan, nie zero. Nawigacje co <5 s wywołują Cloudflare — nie obchodzić, zwolnić. Skrypt w javascript_tool ma limit 45 s — maks. 3–4 zapytania do Farnella/Mousera na wywołanie.

Mouser: URL `/pl/ProductDetail/<nr>` z „/” zamienionym na „-” (np. 579-MCP120-300DI-TO) albo `/c/?q=<MPN>` (przekierowuje na kartę); w tekście liczby mają `&#160;` („Na stanie magazynowym: 5 730”). Mouser NIE sprzedaje do PL ADR4525BRZ ani TBD62083APG („nie sprzedaje tego produktu w Twoim regionie”); LTC4412 ma „ograniczoną dostępność”. Po ok. 15 szybkich zapytaniach: 403 „Access to this page has been denied”; po przerwie i w tempie 1 zapytanie / 10–20 s (maks. 2 na wywołanie javascript_tool) przeszło ok. 25 zapytań bez blokady. Zabezpieczeń nie obchodzić (zasada — także gdy użytkownik prosi); zamiast tego zwolnić albo poprosić użytkownika o wyzwanie w panelu.

DigiKey PL: `digikey.pl/pl/products/result?keywords=<MPN>` → karta; w tekście „W magazynie: N”, „Standardowy czas realizacji”; wysyłka gratis od 300 zł. Ma PBV-R005-F1-0.5 (163,30 zł). Farnell PL: `pl.farnell.com/search?st=<MPN>` przekierowuje na kartę; tekst po zdjęciu tagów: „N W Magazynie”, „Minimum: x Wiele: y”, progi „1 + 12,410 zł”. Szybkie zamówienie: `kod_Farnell,ilość`. Po ok. 15 zapytaniach: 403 „security software” — nie czyścić ciasteczek, żeby to obejść. Rezystory TE YR1B (0,1 %, 15 ppm) są w Farnellu (min. 5), ale bez wartości E24 (300k, 5k1) i bez 6k04 (ten jest w Mouserze 279-YR1B6K04CC).

Koszty wysyłki do PL (2026-09): **Mouser** — darmowo od 300 zł, poniżej ok. 105 zł; **Farnell** — 29,99 zł poniżej 200 zł, od 200 zł darmowo, magazyn USA +110 zł; **DigiKey** — 80 zł poniżej 300 zł. RS PL nie ma 15KPA24CA.

Kamami: wyszukiwarka `kamami.pl/szukaj?controller=search&s=<fraza>`; `fetch` + DOMParser na `article.js-product-miniature`. Ceny brutto (`.current-price-value[content]`). Dostępność czytać z `#product-availability` i `.product-stock-k-dlg` na karcie produktu — pierwsze „Dostępna ilość” w HTML może należeć do boksu polecanych (tak błędnie uznałem silikonowe linki za dostępne; 28.09 czekały na dostawę). Stan 09.2026: adaptery SO14 0,6", SOIC8 0,3", SOT23 3-pin; podstawki precyzyjne DIP14 (648) 0,98 zł, DIP16 (649) 0,80 zł, DIP-8P złota (1207058) 5,02 zł; zestaw OBD2 12 V ZOBD SET ABS (1191911); brak Adafruit 4682, 74HC14/74/123 DIP, TLC555, TBD62083. Wysyłka 8,90–14,90 zł.

Listy: P01 `Plytki/P01-zakupy/`; lista 2 `Plytki/Zakupy-2/` ([[egrlab-purchasing-state]]).

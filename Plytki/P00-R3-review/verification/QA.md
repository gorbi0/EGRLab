# Kontrola plików P00-R3

27.09.2026 · Claude. KiCad 10.0.6. Status: **rewizja zamykająca po recenzji R2; miedź = R2**. Sprzęt, przymiarka i odbiór elektryczny: **NIE ZBADANO**. Zmiany względem R2: `docs/ZMIANY-R3.md`.

| Kontrola | Wynik i dowód |
|---|---|
| ERC, wszystkie ważności | 0; `erc.json` |
| Netlista a jawny kontrakt części | 145/145 pinów, 66 części, 37 sieci, 0 rozbieżności; `schematic-check.json` |
| DRC, wszystkie ważności, zgodność ze schematem | 0 naruszeń / 0 niepołączonych / 0 rozbieżności; `drc.json` z `drc.provenance.json` |
| Kontrole gotowej PCB | 25/25 (R2: 24 + nowa: napis +VIN przy J10, TP3 „ZA D1”); `pcb-checks.json` |
| Warunki pracy z netlisty | 14/14 (R2: 11 + topologia obciążeń, budżet ≥ maksimum z netlisty, poziom H heartbeat); `electrical-checks.json` |
| Wiązka P00 → P04-R2.1 | 10/10 na zamrożonej netliście P04-R2.1: sieci, jeden pulldown, wyłącznie wejścia, H ≥ VIH + 0,2 V, źródło gałęzi TP1 = 3V3_IO, styki, wyjścia tylko do pomiaru, masy, klucze, zgodność tabel dokumentu; `harness-checks.json` |
| Zakres R2 → R3 | 10/10: te same części, piny, wartości, MPN i footprinty; uwagi zmienione tylko w R6, RL9 i TP3; identyczne rozmieszczenie, pady, wiercenia, miedź (149 elementów), strefy, pola wylewek i obrys; na nadruku zmienione tylko +VIN, TP3 i tytuł; pakiet R2 nienaruszony; `revision-checks.json` |
| Próby ujemne na PCB | Próba zerowa: 25/25 i czysty DRC kopii. 11/11 wad wykrytych przez wskazaną kontrolę, w tym nowa „napis +VIN przy TP3”; `negative-controls.json` |
| Próby ujemne warunków pracy | 9/9 (R2: 6 + R5 220 Ω, RL9 220 Ω, RL9 za R3); `electrical-negative-controls.json` |
| Próby ujemne wiązki | 12/12 (m.in. DRIVE na MOTOR_PERMIT, HB na HW_ARMED, podwójny pulldown MECH, gałęzie z PANEL_3V3, STOP na TEST_KEY, stara numeracja w dokumencie); `harness-negative-controls.json` |
| Czysta regeneracja | PASS w osobnym katalogu, tylko ze źródeł: odcisk geometrii `ba543c4b…` identyczny; Gerbery semantycznie identyczne (`src/gerber_equiv.py`, z autotestem), wiercenia identyczne; `clean-rebuild.json` |
| Gerbery a R2 | Miedź, maski, obrys i wiercenia identyczne z R2; różni się tylko F.Silkscreen; `clean-rebuild.json` |
| Kontrola wzrokowa | Wszystkie strony obu końcowych PDF (1 + 4); `pdf-visual-review.json` z SHA256 |

## Model elektryczny

| Wielkość | Wynik |
|---|---|
| VIN na U2 przy 6 V na J10 (budżet D1 0,6 V) | 5,4 V (wymagane ≥ 4,75 V) |
| R5: minimalny prąd / maksymalna moc | 5,54 mA / 21,6 mW |
| Gałąź C6 + R6 (100 kHz, 20 °C) | 0,99–1,35 Ω (okno 0,01–3 Ω) |
| Maksymalny pobór z netlisty (wszystkie zwarcia i LED) | 57,1 mA; budżet 65 mA |
| TJ przy budżecie (15 V, 65 mA, IG 20 mA, 40 °C) | 123,4 °C; przy maksimum z netlisty ok. 116 °C, typowo ok. 84 °C |
| Kanał H na wejściu 74LVC125A P04 | ≥ 2,85 V (VIH 2,0 V) |
| KEY/MECH na bramce HC08 | ≥ 2,61 V (ok. 2,36 V) |
| Heartbeat H na wejściu P04 | typowo ≥ 2,45 V; narożnik minimalnego VOH 1,87 V — rozstrzyga pomiar na J9 (ODBIOR) |
| Częstotliwość HB | 102,3 Hz nominalnie |

Liczby LM2937 pochodzą z SNVS015F według R2 (w R3 karta u dystrybutora nie odpowiadała). TLC555 i 74LVC125A sprawdzone w kartach TI SLFS043K i Nexperia Rev. 12 (`reference/ZRODLA.md`). Nie wykonano symulacji SPICE ani pomiarów.

## Otwarte przed zamówieniem i odbiorem

Przymiarka 1:1 z częściami. Zakup (części P00 nie są zamówione; zapasy z P01 w `docs/ZAKUPY-P00.md`). Odbiór według `docs/ODBIOR-P00-R2.md`, w tym H heartbeat na J9 i temperatura przy 15 V. Te pozycje nie mają wyniku PASS.

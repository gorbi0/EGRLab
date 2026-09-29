---
name: egrlab-review-rules
description: How the user wants EGRLab hardware reviews done (scope, constraints, verification)
metadata:
  type: feedback
---

Przy recenzjach EGRLab: nie oceniać zasadności projektu ani kosztów „życiowo”; oceniać architekturę, poprawność elektryczną i kodu. Ograniczenia: montaż amatorski (bez BGA/QFN, bez lutowania na fali), PCB z fabryki, maks. 2 warstwy, maksymalna modułowość. Drogie moduły scalone zastępowalne dyskretnymi — źle widziane.

**Why:** Użytkownik wprost się na to zirytował (wcześniejsze „porady życiowe”, moduł za 70% ceny urządzenia). Recenzje ERC/netlist nie łapią błędów dynamicznych — P01-R1 miał taki błąd mimo czystych kontroli ([[p01-r1-gate-coupling]]).

**How to apply:** Każdą proponowaną poprawkę obwodu sprawdź liczbowo (prosty model/symulacja) zanim ją podasz — pierwsza intuicyjna poprawka dla P01 (R szeregowo z C5) była błędna. Podawaj pin/sieć/warunek i dowód.

Przy recenzji lub projekcie layoutu sprawdzaj też uwagi o położeniu w kolumnie note BOM (np. „C10 przy U2”, „C11 przy U4”) i wytyczne z MECHANIKA R3 (korytarz mocy ≥5 mm, „C5/C6/D4 lokalnie”, pętla Q2 „krótka”) — recenzja PCB R1 przeoczyła C10/C11. Przed oddaniem dokumentu porównaj każde liczbowe twierdzenie ze źródłem (raport kontroli, BOM, rejestr zamówień): szkic ZMIANY-R2 miał 3 fałszywe zdania.

Przy BOM montażowym (wariant zakupowy) sprawdzać, czy nie gubi uwag z BOM nominalnego (wyprowadzenia, polaryzacja, zalecenia montażu) — w R3 A1 znikały w 70/89 wierszach, a moja recenzja R3 tego nie wyłapała; wyszło dopiero przy wdrażaniu poprawek.

---
name: p04-r1-review
description: "Recenzja P04 SAFE R1 Astry (26.09.2026): bez blokera; R4-01 próg MCP100, R4-02 watchdog tylko przez Q1, R4-03 3V3_IO bez ograniczenia; wniosek dla mojego P03"
metadata:
  node_type: memory
  type: project
  originSessionId: 1bdb3685-394a-4886-bbc7-14b9957d5ea4
  modified: 2026-09-26T08:08:28.288Z
---

`Plytki/P04-R1-recenzja/RECENZJA-P04-R1.md` (+ `skrypty/`). Logika z netlisty zgodna z PROJEKT, pinouty OK (HC123 C1 15–14, MCP100 wariant D = RST/VDD/VSS jak w DS11184), DRC odtworzony 0/0/0, interfejsy z P01 R3.1, P02 R2, P03 R1 i P05 R1 zgodne.

Uwagi: R4-01 MCP100-315 przy TSR 2-2433 (min 3,18 V DC) ma w najgorszym przypadku zapas −15 mV do zwolnienia resetu → MCP100-300 (+135 mV; P02 R2 i P05 R1 mają -300). R4-02 watchdog działa tylko przez Q1 → wolna U7D: SAFE_WD = SAFE_OK & WD_Q na CLR U3 i zgody + próba okresowa w firmware. R4-03 3V3_IO wychodzi bez ograniczenia (R38 0R PG_SEND, J7.1, J8.1) → 1 k / 1 k / 100–220 Ω. Drobne: R5 (pulldown SAFE_N) 74 mm od reszty sieci, KEY tylko w nazwie złącza, 2 przelotki GND, TEST_KEY/MECH_OK bez rezystora szeregowego. Dla P07: ARM_CLK ma impuls 4–13 ms przy włączeniu P04; EN mostka bramkować też SAFE_N.

**Why:** ta sama wada (0 Ω z szyny na żyłę taśmy między GND) jest w moim P03: CORE_LINK przez R14 0R — obiecałem 1 k w P03 R2 (i rozważyć 100–330 Ω na PWM/HEARTBEAT/MCU_ARM z GPIO).
**How to apply:** przy P04 R2 sprawdzić wdrożenie R4-01…03 liczbowo; przy P03 R2 wdrożyć R14 1 k. Recenzja Astry mojego P03 leży w `Plytki/P03-R1-recenzja-Codex/` — do przerobienia. Zob. [[p03-r1-state]], [[egrlab-review-rules]].

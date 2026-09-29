"""PCB3-01: dostęp wkrętakiem do śruby Q1 od przodu (strona Q1) po wlutowaniu C6.
Uruchomić Pythonem z KiCad 10 z argumentem: ścieżka do P01.kicad_pcb (PCB-R3 albo R2).
Stałe z src/add_models.py pakietu R3 (modele gabarytowe) i z dokumentacji R3:
otwór TO-220/SK129 na wysokości 13,5 mm, tył taba na lokalnym y=-3,15, tab 1,27 mm,
C6 WIMA MKS2 7,2 x 7,2 x 13 mm. Podkładka izolacyjna 0,25 mm, tulejka z kołnierzem ~1 mm,
łeb M3 ~2,5 mm - to założenia, nie pomiar.
"""
import pcbnew as p, sys
b = p.LoadBoard(sys.argv[1]); mm = p.ToMM
F = {f.GetReference(): f for f in b.GetFootprints()}
q1y = mm(F['Q1'].GetPosition().y); c6y = mm(F['C6'].GetPosition().y); d4y = mm(F['D4'].GetPosition().y)
tab_back = q1y - 3.15; tab_front = tab_back + 1.27
head_front = tab_front + 1.0 + 2.5          # kołnierz tulejki + łeb M3
c6_front = c6y - 3.6; c6_top = 13.0; axis_z = 13.5
print(f'Q1 y={q1y:.2f}  tab front y={tab_front:.2f}  czoło łba śruby y~{head_front:.2f}')
print(f'C6 y={c6y:.2f}  korpus od y={c6_front:.2f}, wysokość {c6_top} mm; oś śruby z={axis_z} mm')
print(f'wolne miejsce przed łbem do C6: {c6_front - head_front:.2f} mm; C6 kończy się {axis_z - c6_top:.2f} mm pod osią śruby')
print('wniosek: trzonek wkrętaka (promień >=1,5 mm) na osi z=13,5 zahacza o C6 -> brak dostępu od przodu' if axis_z - c6_top < 1.5 else 'wkrętak przechodzi nad C6')
print(f'D4 y={d4y:.2f}, korpus do z~{0.5 + 1.85:.2f} mm - nie przeszkadza')

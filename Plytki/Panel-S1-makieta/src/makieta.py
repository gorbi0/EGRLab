"""Makieta panelu S1 (wariant LOGGER) — PDF A4 do druku w skali 1:1 i widoki stosu 1:2.
Uruchomienie (Python z matplotlib): python3 Plytki/Panel-S1-makieta/src/makieta.py
Wynik: Plytki/Panel-S1-makieta/MAKIETA-PANELU-S1.pdf

Geometria stosu z Plytki/Format-S1/format-s1.json (S1-3); położenia SW1 / J4 / J6 (P05 R3) i J3 / J4 / J5 (P06 R2)
odczytane z plików PCB wydań 4.10.2026; wymiary SW1 z karty E-Switch 100 (s. 6 i 11). Otwory i obrysy elementów panelu
są typowe dla klasy części (kody wybiera zadanie Zakupy-4) — przed wierceniem sprawdzić z kartą wybranego MPN.
"""
from pathlib import Path
import json
import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch

R = Path(__file__).resolve().parents[1]
F = json.loads((R.parents[1]/'Plytki/Format-S1/format-s1.json').read_text(encoding='utf-8'))
POZ = F['poziomy']
T = F['obrys']['grubosc_pcb']
A4 = (297, 210)
MM = 1 / 25.4

# --- stos LOGGER: wysokość dolnej powierzchni płytek ---
z_dno = POZ['dystans_od_dna_obudowy']
z = [z_dno]
for d in (25.0, 20.0, 20.0):
    z.append(z[-1] + T + d)
Z_TOP = z[3] + T + POZ['wys_max_gora_standard']       # najwyższe elementy poziomu 4
WEW_Z = round(Z_TOP + 3.0)                              # jak w S1 §7 (ok. 99 mm)

# --- założenia makiety (do potwierdzenia) ---
STREFA = 50.0            # głębokość strefy panelu przed krawędzią x = 0 stosu (P11, przyciski, kanał przewodów)
Y_A, Y_B = -30.0, 110.0  # ściana A (za P12 ok. 18 mm od krawędzi A) i zdejmowana ściana B (kołki serwisowe do 106 mm)
SC = 3.0                 # grubość ścianki obudowy przyjęta do obrysu płyty
W_PAN = Y_B - Y_A        # szerokość wewnętrzna panelu (wzdłuż y)
H_PAN = WEW_Z            # wysokość wewnętrzna panelu (wzdłuż z)

# SW1 P05 (E-Switch 100 M6 kątowy): oś tulei y = 66,52 (z PCB), z = góra P05 + 6,35 (środek korpusu 12,7 mm, karta s. 11)
SW1_Y, SW1_Z = 66.52, z[2] + T + 6.35
SW1_ZA_KRAWEDZ = 20.3 - 16.62    # tuleja (do lokalnego x = 20,3) wystaje za krawędź P05 o tyle mm

# elementy panelu: (oznaczenie, u, v, obrys: ('o', średnica) | ('p', szer, wys), otwór, opis)
# u — od lewej krawędzi wewnętrznej patrząc na panel z zewnątrz (lewa = strona serwisowa B, prawa = strona P12 / krawędź A)
ELEM = [
    ('TEST', 26, 80, ('p', 34, 26), 'wg karty AT04-12PC', 'port TEST — AT04-12, klucz C'),
    ('L2', 70, 80, ('p', 34, 26), 'wg karty AT04-12PB', 'port L2 — AT04-12, klucz B'),
    ('L1', 114, 80, ('p', 34, 26), 'wg karty AT04-12PA', 'port L1 — AT04-12, klucz A'),
    ('STOP', 26, 45, ('o', 40), 'Ø22,3', 'STOP zatrzaskowy, grzybek Ø40, styk NC złocony'),
    ('KLUCZ', 64, 45, ('o', 30), 'Ø22,3', 'stacyjka TEST (kluczyk), styki złocone'),
    ('ARM', 94, 45, ('o', 30), 'Ø22,3', 'ARM — przycisk, styki złocone'),
    ('MARK', 124, 45, ('o', 26), 'Ø19,2', 'MARK — przycisk, styki złocone'),
    ('AUX', 14, 14, ('o', 16), 'Ø9,7 (D)', 'BNC AUX izolowane (P05 J6, RG174)'),
    ('SCOPE', 36, 14, ('o', 16), 'Ø9,7 (D)', 'BNC SCOPE izolowane (P03 N_J_SCOPE_HOT)'),
    ('HI/LO', 58, 14, ('o', 14), 'Ø6,4', 'SW1 P05 AUX HI/LO — wariant: przełącznik na panelu'),
    ('BYPASS', 82, 14, ('o', 20), 'Ø12,2', 'BYPASS P06 — DPDT ON-ON ≥ 10 A DC'),
    ('PWR', 106, 14, ('o', 18), 'Ø12,2', 'PWR P02 (J14)'),
    ('LED', 124, 14, ('o', 10), 'Ø8', 'LED PWR P02 w oprawce'),
]


def page(pdf, draw):
    fig = plt.figure(figsize=(A4[0] * MM, A4[1] * MM))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, A4[0]); ax.set_ylim(0, A4[1]); ax.set_aspect('equal'); ax.axis('off')
    draw(ax)
    pdf.savefig(fig); plt.close(fig)


def belka(ax, x, y, dl, opis):
    ax.add_patch(Rectangle((x, y), dl, 2, fc='k'))
    for i in range(0, int(dl) + 1, 10):
        ax.plot([x + i, x + i], [y, y + 4 if i % 50 == 0 else y + 3], 'k', lw=.4)
    ax.text(x, y - 4, opis, fontsize=6)


def panel_1_1(ax):
    ox, oy = (A4[0] - W_PAN) / 2, 40
    ax.text(10, 200, 'EGRLab — makieta panelu S1 (LOGGER), widok od zewnątrz, SKALA 1:1', fontsize=10, weight='bold')
    ax.text(10, 194, 'Drukować 100 %, bez dopasowania. Sprawdzić belkę 100 mm. Obrysy elementów i otwory są typowe — przed wierceniem z karty wybranego MPN.', fontsize=6.5)
    ax.add_patch(Rectangle((ox - SC, oy - SC), W_PAN + 2 * SC, H_PAN + 2 * SC, fill=False, lw=.8))
    ax.add_patch(Rectangle((ox, oy), W_PAN, H_PAN, fill=False, lw=.3, ls='--'))
    ax.text(ox, oy + H_PAN + SC + 2, f'płyta {W_PAN + 2 * SC:.0f} × {H_PAN + 2 * SC:.0f} mm (wnętrze {W_PAN:.0f} × {H_PAN:.0f}, ścianki {SC:g} mm)', fontsize=6)
    ax.text(ox - SC, oy - SC - 5, '← strona serwisowa (krawędź B)', fontsize=6)
    ax.text(ox + W_PAN + SC, oy - SC - 5, 'strona P12 (krawędź A) →', fontsize=6, ha='right')
    # rzut stosu (cienko): płytki poziomów 1–4, krawędź x = 0
    for i, zz in enumerate(z):
        u0, u1 = Y_B - 100.0, Y_B - 0.0
        ax.add_patch(Rectangle((ox + u0, oy + zz), u1 - u0, T, fc='0.85', ec='0.6', lw=.2))
        ax.text(ox + u0 + 1, oy + zz + T + .5, f'poziom {i + 1}', fontsize=4, color='0.5')
    # SW1 P05 — gdyby tuleja szła przez panel
    u = Y_B - SW1_Y
    ax.add_patch(Circle((ox + u, oy + SW1_Z), 3.2, fill=False, ec='r', lw=.4, ls=':'))
    ax.text(ox + u + 4, oy + SW1_Z - 1, 'oś SW1 na P05 (tuleja 1/4") — patrz str. 3', fontsize=4.5, color='r')
    for ref, uu, vv, ob, otw, op in ELEM:
        cx, cy = ox + uu, oy + vv
        if ob[0] == 'o':
            ax.add_patch(Circle((cx, cy), ob[1] / 2, fill=False, lw=.5))
        else:
            ax.add_patch(FancyBboxPatch((cx - ob[1] / 2, cy - ob[2] / 2), ob[1], ob[2], boxstyle='round,pad=0,rounding_size=2', fill=False, lw=.5))
        ax.plot([cx - 2, cx + 2], [cy, cy], 'k', lw=.3); ax.plot([cx, cx], [cy - 2, cy + 2], 'k', lw=.3)
        ax.text(cx, cy + 2.5, ref, fontsize=5.5, ha='center', weight='bold')
        ax.text(cx, cy - 4.5, otw, fontsize=4.5, ha='center')
    belka(ax, 10, 18, 100, 'belka kontrolna 100 mm (krok 10 mm)')
    ax.text(150, 22, 'Obrys = miejsce zajęte na panelu (kołnierz, nakrętka, grzybek); krzyżyk = środek otworu.', fontsize=5.5)
    ax.text(150, 17, 'Za panelem strefa 50 mm: P11 poziomo na dnie, przyciski, porty i kanał przewodów (str. 2).', fontsize=5.5)
    ax.text(150, 12, 'Przed portami zostawić ok. 70 mm na wtyki z przewodami.', fontsize=5.5)


def widoki(ax):
    s = .5
    ax.text(10, 200, 'Widoki stosu S1 (LOGGER) ze strefą panelu — SKALA 1:2', fontsize=10, weight='bold')
    # widok z góry (x w prawo, y w dół): stos 160 × 100 w x 0..160, y 0..100
    gx, gy = 30, 185

    def P(x, y):
        return gx + (x + STREFA) * s, gy - (y - Y_A) * s
    x0, y0 = P(-STREFA, Y_A); x1, y1 = P(160 + 10, Y_B)
    ax.add_patch(Rectangle((x0, y1), x1 - x0, y0 - y1, fill=False, lw=.6))
    ax.text(x0, y0 + 2, 'widok z góry: wnętrze obudowy (ściana wejść x > 160 — do ustalenia)', fontsize=6)
    a, b = P(0, 100); c, d = P(160, 0)
    ax.add_patch(Rectangle((a, b), c - a, d - b, fc='0.9', ec='0.4', lw=.4)); ax.text((a + c) / 2, (b + d) / 2, 'stos P02 / P03 / P05+P09 / P06+P10\n160 × 100', fontsize=6, ha='center', va='center')
    a, b = P(0, -18); c, _ = P(160, -18)
    ax.plot([a, c], [b, b], 'b', lw=1.2); ax.text(a + 2, b + 1.5, 'P12 (ok. 18 mm od krawędzi A)', fontsize=5, color='b')
    a, b = P(-STREFA, Y_B); c, d = P(0, Y_A)
    ax.add_patch(Rectangle((a, b), c - a, d - b, fc='#fff3d6', ec='0.4', lw=.4)); ax.text((a + c) / 2, (b + d) / 2, f'strefa panelu\n{STREFA:.0f} mm\nP11 na dnie', fontsize=5.5, ha='center', va='center')
    for nm, yy, col in (('J4 TAPS', 33, 'g'), ('J6 AUX', 52.6, 'g'), ('SW1', SW1_Y, 'r'), ('P06 J3', 27, 'm'), ('P06 J4', 48.8, 'm'), ('P06 J5', 70, 'm')):
        a, b = P(15, yy); c, _ = P(0, yy)
        ax.annotate('', (c - 4, b), (a, b), arrowprops=dict(arrowstyle='->', color=col, lw=.6))
        ax.text(a + 1, b - .8, nm, fontsize=4.5, color=col)
    # widok z boku (x w prawo, z w górę)
    hx, hy = 30, 40

    def Q(x, zz):
        return hx + (x + STREFA) * s, hy + zz * s
    a, b = Q(-STREFA, 0); c, d = Q(170, WEW_Z)
    ax.add_patch(Rectangle((a, b), c - a, d - b, fill=False, lw=.6)); ax.text(a, d + 2, f'widok z boku: wysokość wewnętrzna ok. {WEW_Z} mm (S1 §7)', fontsize=6)
    for i, zz in enumerate(z):
        a, b = Q(0, zz); c, _ = Q(160, zz)
        ax.add_patch(Rectangle((a, b), c - a, T * s, fc='0.5'))
        ax.text(c + 1, b, ['P02 (L)', 'P03 (L)', 'P05 + P09', 'P06 + P10'][i], fontsize=5)
    a, b = Q(-STREFA, 0); c, d = Q(-STREFA + 2, WEW_Z)
    ax.add_patch(Rectangle((a - 1.5, b), 1.5, d - b, fc='k'))
    a, b = Q(-SW1_ZA_KRAWEDZ, SW1_Z); c, _ = Q(3.4, SW1_Z)
    ax.plot([a, c], [b, b], 'r', lw=1.5); ax.text(a - 1, b + 2, f'tuleja SW1 wystaje tylko {SW1_ZA_KRAWEDZ:.1f} mm za krawędź P05 — panel jest {STREFA:.0f} mm dalej'.replace('.', ','), fontsize=4.5, color='r', ha='right')
    belka(ax, 200, 20, 50, 'belka 100 mm w skali 1:2')


def uwagi(ax):
    L = [
        ('Wniosek z makiety — SW1 P05 a panel', True),
        (f'Tuleja SW1 (E-Switch 100 M6, B3/B4 7,1 mm) wystaje za krawędź P05 tylko {SW1_ZA_KRAWEDZ:.1f} mm, a dźwignia kończy się ok. 15,9 mm za krawędzią.'.replace('3.7', '3,7'), False),
        ('Panel musiałby stać prawie przy krawędzi stosu (≤ 1 mm). Wtedy:', False),
        ('  • za panelem nie ma miejsca na przyciski, porty AT04, stację kluczyka ani P11 (głębokość 25–45 mm) — trzeba by je dać nad stos (+ ok. 50 mm wysokości obudowy);', False),
        ('  • przewody z P05 J4 / J6 i P06 J3 / J4 / J5 nie mają kanału między krawędzią płytek a panelem;', False),
        ('  • tuleja B3 nie ma długości na nakrętkę: przy panelu 2 mm wystaje ok. 1,2 mm (nakrętka 1/4-40 ma ok. 2,4 mm).', False),
        ('Rekomendacja: SW1 jako przełącznik na panelu (E-Switch 100 z oczkami, ten sam obwód DPDT ON-ON), połączony 5 przewodami', False),
        ('z otworami footprintu SW1 na P05: 1, 2, 3 (biegun A), 5 i 4 = GND (biegun B; pin 6 wolny). Płytka P05 bez zmian, zamówienie bez zmian.', False),
        ('Panel 50 mm przed stosem: strefa na P11, przyciski i kanał przewodów (jak w kasecie R1: 51 mm).', False),
        ('', False),
        ('Założenia', True),
        (f'Stos LOGGER: płytki na z = {" / ".join(f"{v:.1f}".replace(".", ",") for v in z)} mm (dno 8, dystanse 25 / 20 / 20, PCB 1,6); wnętrze ok. {WEW_Z} mm.', False),
        (f'Szerokość wnętrza {W_PAN:.0f} mm: ściana A {abs(Y_A):.0f} mm przed krawędzią A (P12 ok. 18 mm + taśmy), ściana B 10 mm za krawędzią B (kołki serwisowe 6 mm).', False),
        ('Elementy: AT04-12 z kołnierzem — obrys 34 × 26 mm; przyciski 22 mm (MARK 19 mm); BNC izolowane z otworem D; przełączniki 12 mm (BYPASS, PWR).', False),
        ('Kody części: zadanie dla chmury Zakupy-4 (kandydaci) — po wyborze podmienić otwory i obrysy w src/makieta.py.', False),
        ('NIE ZBADANO: przymiarka z częściami, długości wiązek w nowej kasecie, odprowadzenie ciepła.', False),
    ]
    y = 195
    for t, bold in L:
        ax.text(12, y, t, fontsize=8 if bold else 6.5, weight='bold' if bold else 'normal'); y -= 9 if bold else 7


with PdfPages(R/'MAKIETA-PANELU-S1.pdf', metadata={'Title': 'EGRLab makieta panelu S1', 'Author': 'EGRLab'}) as pdf:
    page(pdf, panel_1_1); page(pdf, widoki); page(pdf, uwagi)
print('z poziomów', [round(v, 1) for v in z], 'wnętrze z', WEW_Z, 'SW1 z', round(SW1_Z, 1), 'za krawędzią', round(SW1_ZA_KRAWEDZ, 2))

# Dobór i analiza R2

## Części i obliczenia

Q1/Q2 [Vishay SUP53P06-20-E3](https://www.vishay.com/docs/68633/sup53p06-20.pdf):
TO-220 GDS, VDS60V, |VGS|20V, RDS(on) określone również przy4,5V. Napięcie progowe
nie jest napięciem pełnego otwarcia. Ciss3500pF zawiera Crss290pF (wartości typowe).

C5 [TDK B32529C1103J000](https://www.tdk-electronics.tdk.com/inf/20/20/db/fc_2009/B32520_529.pdf):
10nF/100V ±5%, P5mm, obrys7,3×2,5mm, H6,5mm. C6 B32529D1105J000:
1µF/100V ±5%, P5mm, obrys7,8×7,8mm, H13mm. Nie zamieniać bez analizy na MLCC.
R27 [PR02000201009FR500](https://www.vishay.com/docs/28729/pr010203.pdf):10Ω/2W±1%.

Szybki skok VS przy stałym wyjściu daje:
`ΔVSG≈ΔVS·(C5+Cgd)/(C5+Cgd+C6+Cgs)`.
Dla48V, C5+5%, C6−5%, założonego Cgd≤2nF i konserwatywnie pominiętej Cgs:
**VSG≤0,623V**. Cgd2nF jest założeniem do sprawdzenia, nie gwarancją producenta.
Rachunek nie obejmuje dzwonienia indukcyjnego. Cel0,8V dotyczy odbioru prototypu
0…50°C, nie dowolnej temperatury złącza. Rzeczywiste przewodzenie też mierzymy.

DC z niskim wejściem8,9V, spadkami0,95/0,3V i R±1% daje **VSG≈6,29V**.
R22 zwiększono wraz z R21, aby zachować zapas sterowania przy niskim napięciu.
Energia pojemności przy18V około0,173mJ; początkowa moc R27≤32,8W, krótki impuls.
Wykres PR02 str.9 ma zapas dla dziesiątek µs i okres/czas≥100. Odbiór wymaga
zmierzenia impulsu i jego powtarzalności; automatyczne próby zasilania najwyżej1Hz.
R23 przy VS48V i clampie15V: około0,495W, D9 około0,223W. Nie oznacza to dopuszczenia
ciągłego48V dla P01. SOA startu Q1 nie wolno oceniać na podstawie EAS avalanche.

## Zakres modelu

Model czyta z XML połączenia/wartości R17–R27,C5/C6,Q1–Q5,D4/D9. C1=10µF,
Cload=220µF i Rsource=50mΩ są parametrami stanowiska. To nie model instalacji auta.
ENABLE jest sterowane źródłem; w OVP narzucono około20µs opóźnienia detekcji.
Nie symulowano pełnego LM2903/D6/AUX/Q6 ani tłumienia TVS/D2. Odniesienie18,5V
w talii jest źródłem przed Rsource, nie fizycznym pomiarem J1.

Ogólne modele VDMOS/BJT ngspice **nie są modelami producentów wybranych części**.
Badane wartości: Vth0,8…3V,Kp4…20,Cgd0,1…2nF,Cgs2…3,21nF; Q2 Cgs10/20nF,
Cgd3/6nF; BJT BF30…100,TR1/3µs. Są to warianty wrażliwości, nie gwarantowane
granice procesu/temperatury ani pełny iloczyn wszystkich skrajności.
Minimalne wewnętrzne C modeli VDMOS1pF stabilizują solver; raportowany prąd gałęzi
Q1 zawiera ich śladowy składnik. Nie interpretować wyniku bliskiego0 jako zerowego
rzeczywistego upływu. KCL uwzględnia zewnętrzne prądy C5/C6.

Badamy C±5%, zmienione R±1%, oba kierunki kompromisu start/stop, precharge,
bounce,1µs i1ms. Osobny szybki start ma obie C−5%, małe Cgd i duże Kp.
Dla trzech prób zmniejszenie kroku2× zmienia wybrane metryki o<3%.
To kontrola błędu numerycznego, nie weryfikacja fizycznego modelu tranzystora.

## Wyniki modelu

| Próba | VSG szczyt [V] | gałąź Q1 szczyt [A] | wyłączenie [µs] |
|---|---:|---:|---:|
| hot_14_1e-06_0 | 0.143 | 0.000 | — |
| hot_14_1e-06_1 | 0.183 | 0.000 | — |
| hot_14_0.001_0 | 0.013 | 0.000 | — |
| hot_14_0.001_1 | 0.017 | 0.000 | — |
| hot_24_1e-06_0 | 0.238 | 0.000 | — |
| hot_24_1e-06_1 | 0.309 | 0.000 | — |
| hot_24_0.001_0 | 0.015 | 0.000 | — |
| hot_24_0.001_1 | 0.021 | 0.000 | — |
| hot_48_1e-06_0 | 0.453 | 0.000 | — |
| hot_48_1e-06_1 | 0.595 | 0.001 | — |
| hot_48_0.001_0 | 0.019 | 0.000 | — |
| hot_48_0.001_1 | 0.028 | 0.000 | — |
| start_9_0 | 7.406 | 0.659 | — |
| start_9_1.5 | 7.344 | 2.283 | — |
| start_14_0 | 11.529 | 1.208 | — |
| start_14_1.5 | 11.467 | 2.847 | — |
| start_17_0 | 14.002 | 1.555 | — |
| start_17_1.5 | 13.940 | 3.194 | — |
| start_slow_corner | 7.290 | 1.933 | — |
| start_fast_corner | 13.959 | 3.697 | — |
| off_0 | 13.941 | 1.501 | 42.93 |
| off_1 | 13.905 | 1.501 | 64.23 |
| off_step_18_48 | 0.328 | 0.000 | — |
| off_precharged_18_48 | 0.328 | 0.000 | — |
| hot_bounce_24 | 0.297 | 0.000 | — |
| ovp_17_24_delay20us | 13.908 | 96.698 | 77.97 |

Wiersze start dotyczą ON, więc wysokie VSG jest prawidłowe. OFF0/OFF1 liczą
od ENABLE do VSG<0,5V, OVP od źródłowego18,5V z narzuconym opóźnieniem.
Budżet:20µs detektor/bufor +80µs blok bramki =100µs. Te20µs jest wymaganiem
do pomiaru, nie gwarantowanym czasem LM2903. Najwolniejszy badany start osiąga
95%VS w około74.3ms po ENABLE.

Regresja R1 przy24V daje w tym modelu VSG8.45V
i ładunek około2078µC — znany błąd
zostaje wykryty. Nie wymagamy zgodności prądu z uproszczonym modelem Opusa.

**OVP przy już otwartym Q1 daje duży prąd:**17→24V to około
97A w tym modelu. PASS czasu nie oznacza
PASS tego impulsu. P01 nie ma aktywnego limitu5A. W odbiorze ocenić trajektorię
VDS/ID względem SOA z temperaturą, D2, TVS, ścieżki i bezpiecznik. Model nie
kwalifikuje zwarcia, reverse recovery, termiki ani load dump. Wszystkie pomiary
sprzętowe pozostają NIE ZBADANO. Pełny impuls wymaga opisu amplitudy, czasu,
impedancji i energii, nie samego hasła „48V”.

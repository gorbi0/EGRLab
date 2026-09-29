"""V6 electrical deltas and assembly contract. Called by build_hardware.py.
The source reference is immutable; outputs always describe the final V6 circuit.
"""
import csv,json,collections,re,html

FAB={'P01','P05','P07'}
NAMES={'P00':'FIXTURE','P01':'PROTECT','P02':'PSU','P03':'CORE','P04':'SAFE','P05':'DAQ','P06':'I-LOGGER','P07':'DRIVE','P08':'SENSOR','P09':'TEMP','P10':'CAN','P11':'PANEL','AT':'TEST adapter','AL1':'LOGGER L1 adapter','AL2':'LOGGER L2 adapter','EXT':'Zasilanie zewnętrzne'}

def writecsv(p,rows,fields=None):
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fields or list(rows[0]),delimiter=';');w.writeheader();w.writerows(rows)

def apply_changes(C,W,K,mods):
    # The original standalone P01 J4 pin 1 is supplied by PG pin 1 in the integrated unit.
    # V5's hierarchy prefix left that bias rail electrically isolated.
    for c in C.values():
        if c['board']=='P01':
            c['pins']={p:('3V3_IO' if n=='P01_BOARD_3V3' else n) for p,n in c['pins'].items()}
    for ref in ['J1','J2','J4','J_PRES']:
        c=C['P01_'+ref];c['kind']='testpad';c['value']='Pola kontrolne PTH '+ref+' (bez osobnego złącza)'
        c['note']='V6: połączenie robocze przez BAT/SUPPLY/PG; pozostały dostęp pomiarowy. Nie dokupować gniazda.'
    for c in C.values():
        c['value']=c['value'].replace('AD7606BSTZ','AD7606BBSTZ').replace('TLV1702QDGKRQ1','TLV1702AQDGKRQ1 VSSOP8 DGK').replace(' + adapter (Ioff)',' (Ioff)')
    for key in ['P06_RO2','P07_RO1']:del C[key]
    c=C['P11_SW_STOP'];c['pins']={p:('NC' if n=='STOP_PRESSED' else n) for p,n in c['pins'].items()};c['note']='Pomocniczy NO niepodłączony; styki NC zachowują sprzętowy STOP.'
    C['P07_U_GATE']['pins'].update({'4':'GND','5':'GND','6':'NC'})
    for b in ['P06','P07']:
        C[b+'_C_REF']['value']='4.7uF X7R 10V'
        C[b+'_C_REF_HF']=dict(board=b,ref='C_REF_HF',value='100nF X7R 50V',pins={'1':b+'_REF25','2':'GND'},kind='cap',note='Równolegle z C_REF, przy VREF ADC; bez rezystora szeregowego.')
    # Collapse only true series pairs: no other component or wire uses the midpoint.
    merges=[]
    pairs=[]
    for board,startm,starts in [('AT',1,1),('AL1',5,7),('AL2',9,13)]:
        pairs += [(board,'RM'+str(i),'RM'+str(i+1),300000) for i in [startm,startm+2]]
        pairs += [(board,'RS'+str(i),'RS'+str(i+1),100000) for i in [starts,starts+2,starts+4]]
    pairs += [('P05','RV1','RV2',499000),('P05','RA1','RA2',300000),('P05','RA3','RA4',100000)]
    for b,r1,r2,ohms in pairs:
        a,z=C[b+'_'+r1],C[b+'_'+r2];middle=set(a['pins'].values())&set(z['pins'].values());assert len(middle)==1
        mid=middle.pop()
        assert sum(mid in c['pins'].values() for c in C.values())==2,mid
        assert all(w['net']!=mid for w in W)
        ends=[n for c in [a,z] for n in c['pins'].values() if n!=mid]
        merges.append(dict(module=b,old_refs=r1+' + '+r2,old_values=a['value']+' + '+z['value'],new_ref=r1,ohms=ohms,removed_midpoint=mid,new_value=f'{ohms//1000}k 0.1% 25ppm MBB/SMA0207 0.40W 350V THT'))
        a.update(value=merges[-1]['new_value'],pins={'1':ends[0],'2':ends[1]},note='V6: jeden większy rezystor zamiast pary. Nie zachowuje redundancji dwóch elementów; patrz docs/09-zmiany-v6.md.')
        del C[b+'_'+r2]
    interfaces=[]
    for k in K:
        rows=[w for w in W if w['cable']==k['cable']];a,b=k['ends'].split('/');name=k['cable'];sample=rows[0]
        ends=[C[sample[s+'_board']+'_'+sample[s+'_ref']] for s in ['from','to']]
        n=k['positions'];length=int(sample['max_cm'])*10
        rec=dict(lacze=name,koniec_A=a+'/'+ends[0]['ref'],koniec_B=b+'/'+ends[1]['ref'],rodzina=k['family'],pozycje=n,klucz=k['key_pin'],koniec_lutowany='',wlasciciel_wiazki=b,dlugosc_mm=length,przewod='',typ_wtyku='',kotwa_mm='',zakonczenie='',wersja='M2')
        if name=='DAQ':
            k.update(family='B2B 2.54',blocking='Pin 2 usunięty / otwór 2 zaślepiony + asymetryczny uchwyt',compatible_group='DAQ_M2')
            ends[0]['value']='Samtec SSW-108-01-G-D gniazdo PTH 2x8 Au';ends[1]['value']='Samtec TSW-108-07-G-D wtyk PTH 2x8 Au'
            rec.update(rodzina=k['family'],koniec_lutowany='BRAK przewodów; oba złącza lutowane do PCB',wlasciciel_wiazki='BRAK',dlugosc_mm=0,przewod='BRAK',typ_wtyku='TSW-108-07-G-D / SSW-108-01-G-D',zakonczenie='Płytka–płytka; klucz 2; osobne mocowanie obu PCB')
        elif name.startswith('EXT_'):
            rec.update(koniec_lutowany='BRAK: zaciskane styki DEUTSCH na obu końcach',przewod='2x1.5mm2 moc + 0.35mm2 sygnały; ekran odczepów wg docs/10',typ_wtyku='DEUTSCH DT06-12S'+str(k['key_pin'])+' + DT04-12P'+str(k['key_pin']),zakonczenie='Adapter zewnętrzny; bez zmiany standardu')
        else:
            # All internal harnesses have only one detachable end (A).
            ends[1]['kind']='termination';ends[1]['value']=f'PTH lutowane H_{name}, {n} pozycji (nie kupować złącza)'
            rec.update(koniec_lutowany=rec['koniec_B'],kotwa_mm='10–15',zakonczenie='Przewody do PTH; 2 otwory kotwy + opaska; bez pól SMD')
            if k['family']=='IDC':
                rec.update(przewod=f'taśma {n} żył AWG28, raster 1.27mm',typ_wtyku=f'IDC żeński {n}p Au z odciążką, KEY {k["key_pin"]}')
                ends[0]['value']=f'IDC box header {n}p 2.54mm Au, KEY {k["key_pin"]}'
            elif 'MicroFit' in k['family'] or 'Micro-Fit' in k['family'] or name=='TAPS':
                if name=='TAPS':
                    # Signal-ground interleave; includes no ties to the sensor ground wires.
                    nets=['TAP_P1','GND','TAP_P3','GND','TAP_P4','GND','TAP_P5','GND','TAP_P6','GND','NC','NC']
                    n=12;k['positions']=12;rec['pozycje']=12
                    for end in ends:end['pins']={str(i):net for i,net in enumerate(nets,1)}
                    W[:]=[w for w in W if w['cable']!=name]
                    rows=[]
                    for i,net in enumerate(nets,1):
                        row=sample.copy();row.update(from_pin=str(i),to_pin=str(i),net=net);W.append(row);rows.append(row)
                    rec['przewod']='5 par sygnał/GND AWG24; 2 pozycje NC; długość całkowita 50mm'
                else:rec['przewod']='wiązka AWG22 (0.34mm2), oddzielna od taśm SPI'
                k['family']='Mini-Fit Jr 4.2';rec.update(rodzina=k['family'],typ_wtyku=f'Mini-Fit Jr żeński {n}p, styki Au, klucz {name}')
                ends[0]['value']=f'Mini-Fit Jr stałe gniazdo męskie {n}p Au, KEY {name}; korpus + styki + ogonki PTH'
                ends[1]['value']=f'PTH lutowane H_{name}, {n} pozycji (nie kupować złącza)'
                k['blocking']='Zatrzask + dedykowana osłona mechaniczna '+name+'; LV03..LV10 elektrycznie wspólne'
            else:
                k['family']='MSTB 5.08 power';rec.update(rodzina=k['family'],przewod='miedź linka 2.5mm2; osobne żyły, nie taśma IDC',typ_wtyku=f'MSTB 5.08 {n}p >=12A z tulejkami, KEY {name}')
                ends[0]['value']=f'MSTB 5.08 gniazdo {n}p >=12A, KEY {name}'
        for w in rows:w['connector']=rec['rodzina'];w['max_cm']=rec['dlugosc_mm']/10
        interfaces.append(rec)
    for m in mods:m.update(interface='M2',hw_rev='6.0',assembly=('PCB 2L' if m['id'] in FAB else 'uniwersalna lutowana / nośnik'),status='no_routed_layout_hardware_acceptance_pending')
    return dict(merges=merges,interfaces=interfaces)

def extra_outputs(D,C,W,K,mods,data):
    H=D/'hardware';interfaces=data['interfaces']
    for path in [D/'interfejsy.csv',H/'interfejsy.csv']:writecsv(path,interfaces)
    writecsv(H/'rezystory-zamiany.csv',data['merges'])
    def package(c):
        s=c['value']
        for a,b in [('LQFP64','LQFP64 0.5mm'),('VSSOP8','VSSOP8 DGK 0.65mm'),('125AD','SO14 1.27mm'),('INA240','SOIC8 1.27mm'),('TCAN1051','SOIC8 1.27mm'),('ADR4525','SOIC8 1.27mm'),('TPS2553','SOT23-6 0.95mm'),('TPS3808','SOT23-6 0.95mm'),('PESD2','SOT23'),('0207','axial THT 0207'),('MCP23017','SPDIP28'),('TO92','TO92'),('DIP','DIP')]:
            if a in s:return b
        if c['kind']=='res':return 'THT / zgodnie z mocą i tolerancją w nazwie'
        return 'wg elementu; zweryfikować rysunek zakupionego typu'
    adapters=[];bom=[]
    for key,c in C.items():
        if c['kind'] in ['termination','testpad']:continue
        pkg=package(c);b=c['board'];adapter=''
        if b not in FAB and pkg.startswith(('SO14','SOIC8','SOT23')):
            adapter=pkg.split()[0]+' → DIP 2.54mm'
            adapters.append(dict(module=b,ref='ADP_'+c['ref'],name='Adapter '+adapter,quantity=1,for_ref=c['ref']))
        mpn=c['value'].split()[0] if c['kind']=='ic' and not c['ref'].startswith(('M','TC','SD')) else ''
        if 'MBB/SMA0207' in c['value']:
            code={'100k':'1003','300k':'3003','499k':'4993'}[c['value'].split()[0]];mpn='MBB0207VD'+code+'BC100'
        bom.append(dict(module=b,ref=c['ref'],name=c['value'],quantity=1,unit='szt.',mpn=mpn,package=pkg,assembly=('bezpośrednio PCB 2L' if b in FAB else ('adapter + uniwersalna' if adapter else 'montaż lutowany / mechaniczny')),adapter=adapter,length_mm='',plug_type='',category='element',note=c['note']))
    for x in adapters:bom.append(dict(module=x['module'],ref=x['ref'],name=x['name'],quantity=1,unit='szt.',mpn='',package='adapter',assembly='uniwersalna',adapter='',length_mm='',plug_type='',category='adapter',note='Dla '+x['for_ref']))
    # A harness is one BOM assembly; constituent parts below are an alternative shopping view, never added twice.
    parts=[]
    for r in interfaces:
        if r['wlasciciel_wiazki']=='BRAK':continue
        name=r['lacze'];b=r['wlasciciel_wiazki'];n=int(r['pozycje'])
        bom.append(dict(module=b,ref='H_'+name,name='Wiązka '+name,quantity=1,unit='kpl.',mpn='',package='wiązka',assembly=r['koniec_lutowany'],adapter='',length_mm=r['dlugosc_mm'],plug_type=r['typ_wtyku'],category='wiązka',note=r['przewod']+'; kotwa '+str(r['kotwa_mm'])+' mm. Rozbicie: wiazki-czesci.csv'))
        def add(nam,q,unit='szt.'):parts.append(dict(module=b,wiazka=name,nazwa=nam,ilosc=q,jednostka=unit))
        used=sum(w['net']!='NC' for w in W if w['cable']==name)
        if r['rodzina']=='IDC':
            add(r['typ_wtyku'],1);add(r['przewod'],round((r['dlugosc_mm']+30)/1000,3),'m');add('Zaślepka kluczująca IDC',1);add('Opaska 2.5mm + miękka przekładka',1)
        elif r['rodzina'].startswith('Mini-Fit'):
            add(f'Mini-Fit Jr korpus żeński {n}p 4.2mm',1);add('Mini-Fit Jr styk żeński Au do użytego AWG',used);add(r['przewod'].split(';')[0],round(used*(r['dlugosc_mm']+20)/1000,3),'m żyły');add('Opaska 2.5mm + miękka przekładka',1)
        elif r['rodzina'].startswith('MSTB'):
            add(r['typ_wtyku'],1);add('Przewód Cu elastyczny 2.5mm2',round(used*(r['dlugosc_mm']+20)/1000,3),'m');add('Tulejka do 2.5mm2',used);add('Opaska 3.6mm + miękka przekładka',1)
        else:
            # DT connectors and contacts are part of the existing adapter component assemblies.
            add('Kabel zewnętrzny mieszany 2x1.5mm2 + sygnały 0.35mm2; wg pinów adaptera',r['dlugosc_mm']/1000,'m');add('Osłona / odciążka adaptera DEUTSCH',2)
    writecsv(H/'adaptery.csv',adapters);writecsv(H/'wiazki-czesci.csv',parts)
    writecsv(H/'BOM.csv',bom)
    # Board mounting material belongs to the same full shopping list.
    materials=[]
    for b in sorted(NAMES):
        if b=='EXT':continue
        typ='PCB 2L do zaprojektowania' if b in FAB else ('nośnik / obudowa adaptera' if b.startswith('A') else 'płytka uniwersalna PTH raster 2.54mm')
        materials += [dict(module=b,nazwa=typ,ilosc=1,jednostka='szt.',uwagi='Wymiary: karta modułu; brak Gerberów'),dict(module=b,nazwa='Dystans M3 + śruba + podkładka',ilosc=4,jednostka='kpl.',uwagi='Długość dobrać do obudowy i złącza B2B')]
    writecsv(H/'materialy.csv',materials)
    shopping=collections.Counter()
    for r in bom:
        if r['category']!='wiązka':shopping[(r['name'],r['unit'])]+=r['quantity']
    for r in parts+materials:shopping[(r['nazwa'],r['jednostka'])]+=float(r['ilosc'])
    writecsv(H/'zakupy.csv',[dict(nazwa=n,ilosc=round(q,3),jednostka=u) for (n,u),q in sorted(shopping.items())])
    cards=['# Karty modułów V6 / HW6.0 / interfejs M2\n\nBOM-y zawierają pozycje „Wiązka”; ich części są rozpisane w wiazki-czesci.csv. Zakupy.csv liczy części wiązek zamiast całych wiązek, bez podwajania. Długość jest długością gotową od PTH do czoła wtyku; zapas cięcia podano tylko w częściach.\n']
    stages={'P01':'TVS/bezpiecznik → sterowanie ochroną → MOSFET-y i radiatory → obciążenie sztuczne.','P02':'Przewody mocy → TSR → pomiar obu szyn → sygnał PSU_OK.','P03':'Podstawki MCU/SD → zasilanie → bufory i rezystory → B2B DAQ → wgrywanie CORE.','P04':'Masa/100nF → bramki i nadzór → watchdog → latch/ARM → próby P00.','P05':'ADC i kondensatory lokalne → referencja → analog/dzielniki → bufory/B2B → pomiar znanych napięć.','P06':'Bocznik i Kelvin → INA/REF → MCP3201 → bufory → zero i oba znaki prądu.','P07':'Zasilanie/OC bez mostka → latch → nośnik VNH5019 → obciążenie sztuczne.','P08':'Stabilne 5V → ogranicznik TPS → przekaźnik → SENSOR_OK.','P09':'Podstawki MAX31856 → bufory → próby dwóch termopar.','P10':'Transceiver/ESD → odbiór CAN na stanowisku → listen-only w aucie.','P11':'Złącza i mikrowyłączniki → wiązki mocy → sygnały → test braku pomyłek.'}
    for b in sorted(NAMES):
        rows=[r for r in bom if r['module']==b];writecsv(H/(b+'-BOM.csv'),rows or [dict.fromkeys(bom[0],'')],list(bom[0]))
        related=[r for r in interfaces if r['koniec_A'].split('/')[0]==b or r['koniec_B'].split('/')[0]==b]
        m=next((m for m in mods if m['id']==b),None)
        cards += [f'\n## {b} {NAMES[b]}\n',f'Wykonanie: **{"PCB dwuwarstwowa zamawiana" if b in FAB else "trwały montaż lutowany / nośnik / panel"}**. BOM: [hardware/{b}-BOM.csv](../hardware/{b}-BOM.csv).\n']
        if m:cards += [f'Rezerwa obrysu {m["envelope_mm"][0]} × {m["envelope_mm"][1]} mm. Otwory z modules.json są założeniem do rozmieszczenia.\n']
        cards += ['| Wiązka / łącze | Długość gotowa | Wtyk | Lutowany koniec / właściciel |\n|---|---:|---|---|\n']
        for r in related:cards += [f'| {r["lacze"]} | {r["dlugosc_mm"]} mm | {r["typ_wtyku"]} | {r["koniec_lutowany"]}; BOM {r["wlasciciel_wiazki"]} |\n']
        if not related:cards += ['| Brak stałej wiązki między PCB | — | przewody stanowiskowe | nie dotyczy |\n']
        cards += ['\nMontaż: '+stages.get(b,'Sprawdzić mapę styków; lutować odczepy przez rezystory, odizolować i odciążyć mechanicznie.')+'\n']
        if b in ['P07','P09']:cards += ['Gotowe VNH5019 / MAX31856 zachowują listwy i gniazda na swoim nośniku; nie lutować taśmy do gotowego modułu.\n']
        cards += ['Odbiór: oględziny obu stron, ciągłość pin–pin, brak zwarć sąsiednich żył, identyfikacja kluczy; następnie próby z ODBIOR.csv. Odłączać wyłącznie bez zasilania.\n']
    (D/'docs/PCB.md').write_text(''.join(cards),encoding='utf-8')
    writecsv(H/'wykonanie-modulow.csv',[dict(module=m['id'],wykonanie=m['assembly'],warstwy=2 if m['id'] in FAB else '',miedz_um=70 if m['id'] in ['P01','P07'] else 35 if m['id']=='P05' else '',status=m['status']) for m in mods])
    print(f'V6: {len(interfaces)} interfaces; {len(data["merges"])} resistor pairs collapsed; {len(adapters)} SMD adapters; {len(bom)} BOM rows')

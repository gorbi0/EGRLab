"""Small ordered electrical fixes; each patch records its actual model diff."""
import copy, json, difflib, importlib.util

def apply(C,W,K,mods,data,D):
    spec=importlib.util.spec_from_file_location('stabilization_contract',D/'stabilizacja/checks.py')
    checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
    def capture():return json.dumps(dict(components=C,wiring=W,connectors=K,interfaces=data['interfaces']),indent=2,ensure_ascii=False,sort_keys=True).splitlines(True)
    def record(id,before):
        (D/'stabilizacja/patches'/f'{id}.diff').write_text(''.join(difflib.unified_diff(before,capture(),fromfile=id+'-before',tofile=id+'-after')),encoding='utf-8')
        rows=[dict(w,from_pin=str(w['from_pin']),to_pin=str(w['to_pin'])) for w in W]
        failure=checker.check(C,rows,K)
        expected={'F01':{'F02','F03','F04','T02'},'F02':{'F03','F04','T02'},'F03':{'F04','T02'},'F04':{'T02'},'F07':set()}[id]
        assert set(failure)==expected,(id,failure,expected)
        (D/'stabilizacja/evidence'/f'{id}-stage-check.json').write_text(json.dumps(dict(after_patch=id,remaining_known_failures=failure,no_new_contract_failures=True),indent=2,ensure_ascii=False),encoding='utf-8')
    def interface(name):return next(i for i in data['interfaces'] if i['lacze']==name)
    def connector(name):return next(i for i in K if i['cable']==name)
    before=capture()
    # A dedicated low-current branch. Fuse is on the source board, before wire.
    C['P02_F_VSENSE']=dict(board='P02',ref='F_VSENSE',value='Bezpiecznik F 100mA 5x20mm >=32V DC + oprawka PTH',pins={'1':'VPROT','2':'VPROT_SENSE'},kind='fuse',note='Przy odgałęzieniu VPROT, przed wiązką. Spadek na bezpieczniku objęty kalibracją całego toru VBAT.')
    nets={str(i):('VPROT_SENSE' if i==1 else 'GND' if i==2 else 'NC') for i in range(1,15)}
    C['P02_J_VSENSEA']=dict(board='P02',ref='J_VSENSEA',value='Mini-Fit Jr stałe gniazdo męskie 14p Au, VSENSE',pins=copy.copy(nets),kind='connector',note='VSENSE; dedykowany korpus 14p, niezgodny z LV 4p; tylko piny 1/2 obsadzone')
    C['P05_J_VSENSEB']=dict(board='P05',ref='J_VSENSEB',value='PTH lutowane H_VSENSE, 14 pozycji (nie kupować złącza)',pins=copy.copy(nets),kind='termination',note='Para AWG22, 150mm; kotwa 10–15mm od lutów; piny 3..14 NC bez przewodów')
    C['P05_RV1']['pins']['1']='VPROT_SENSE'
    for p,n in nets.items():W.append(dict(cable='VSENSE',from_board='P02',from_ref='J_VSENSEA',from_pin=p,to_board='P05',to_ref='J_VSENSEB',to_pin=p,net=n,connector='Mini-Fit Jr 4.2',max_cm=15))
    K.append(dict(cable='VSENSE',ends='P02/P05',family='Mini-Fit Jr 4.2',positions=14,key_pin='',blocking='Dedykowany pełny korpus 14p z zatrzaskiem; LV ma 4p',compatible_group='VSENSE'))
    data['interfaces'].append(dict(lacze='VSENSE',koniec_A='P02/J_VSENSEA',koniec_B='P05/J_VSENSEB',rodzina='Mini-Fit Jr 4.2',pozycje=14,klucz='',koniec_lutowany='P05/J_VSENSEB',wlasciciel_wiazki='P05',dlugosc_mm=150,przewod='para AWG22: VPROT_SENSE/GND; tylko 2 styki Au; NC bez żył',typ_wtyku='Mini-Fit Jr żeński 14p Au VSENSE; bez zamienności z LV',kotwa_mm='10–15',zakonczenie='PTH lutowane; kotwa + opaska; zabezpieczenie 100mA na P02',wersja='M2.1'))
    record('F01',before)
    before=capture()
    # The raw open-drain output and its pull-up remain LOCAL to P08.
    for c in C.values():
        for p,n in list(c['pins'].items()):
            if n=='SENSOR_FAULT_N':c['pins'][p]='SENSOR_HEALTHY'
            elif n=='SENSOR_FAULT_N_CORE':c['pins'][p]='SENSOR_HEALTHY_CORE'
    for w in W:
        if w['net']=='SENSOR_FAULT_N':w['net']='SENSOR_HEALTHY'
    C['P08_U11']['pins']['4']='SENSOR_FAULT_LOCAL_N'
    C['P08_R_FAULT_PU']['pins']={'1':'SENSOR_FAULT_LOCAL_N','2':'3V3_IO'}
    C['P08_U_READY']['pins'].update({'9':'SENSOR_OK','10':'SENSOR_FAULT_LOCAL_N','8':'SENSOR_HEALTH_LOCAL'})
    C['P08_U_RX1']['pins'].update({'4':'GND','5':'SENSOR_HEALTH_LOCAL','6':'SENSOR_HEALTHY'})
    c=C.pop('P03_R_PU_SENSOR_FAULT_N');c.update(ref='R_PD_SENSOR_HEALTHY',pins={'1':'SENSOR_HEALTHY','2':'GND'},note='Odbiorczy pull-down: kabel przerwany lub nadajnik bez zasilania = awaria')
    C['P03_R_PD_SENSOR_HEALTHY']=c
    interface('SFAULT')['wersja']='M2.1'
    record('F02',before)
    before=capture()
    for key in ['P04_J_PANELSAFEA','P11_J_PANELSAFEB']:C[key]['pins'].update({'5':'NC','6':'NC'})
    for w in W:
        if w['cable']=='PANELSAFE' and str(w['from_pin']) in ['5','6']:w['net']='NC'
    record('F03',before)
    before=capture()
    # Different mating geometry, not just a label/color. Still screw termination.
    connector('VMOTOR').update(family='COMBICON PC4 7.62 power',blocking='PC4 raster 7.62mm; SUPPLY MSTB ma 5.08mm',compatible_group='VMOTOR')
    C['P02_J_VMOTORA']['value']='Phoenix Contact PC 4/3-G-7,62 1804807 PTH 20A'
    interface('VMOTOR').update(rodzina='COMBICON PC4 7.62 power',typ_wtyku='Phoenix Contact PC 4/3-ST-7,62 1804917, 20A; tulejki 2.5mm2',wersja='M2.1')
    for w in W:
        if w['cable']=='VMOTOR':w['connector']='COMBICON PC4 7.62 power'
    record('F04',before)
    before=capture()
    # Same dead-copy problem as PANELSAFE; actual status LED stays on CORE.
    for key in ['P03_J_PANELCOREA','P11_J_PANELCOREB']:C[key]['pins']['6']='NC'
    for w in W:
        if w['cable']=='PANELCORE' and str(w['from_pin'])=='6':w['net']='NC'
    record('F07',before)
    for m in mods:m.update(interface='M2.1',hw_rev='6.1-rc1',status='SCHEMATIC_REVIEW_PENDING; NO_PRODUCTION_RELEASE')

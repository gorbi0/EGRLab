import csv,json,re,unittest,collections,sys,subprocess,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
HW=R.parent/'EGRLab-v6.1-rc1'   # 6.2-s1: zamkniety model sprzetu v6.1 (M2.1); firmware, profile i narzedzia z tej rewizji
sys.path.insert(0,str(R/'tools'))
import profile_v6

def rows(name):
    with (HW/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter=';'))   # tabele sprzetu v6.1

class V6Assembly(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=json.loads((HW/'hardware/components.json').read_text(encoding='utf-8'))
        cls.i=rows('interfejsy.csv');cls.bom=rows('hardware/BOM.csv');cls.w=rows('hardware/wiring.csv')

    def test_errata_order_codes_and_pinout(self):
        self.assertIn('AD7606BBSTZ',self.c['P05_U1']['value'])
        self.assertEqual(self.c['P05_U1']['pins']['9'],'ADC_CONVST_P05')
        self.assertEqual(self.c['P05_U1']['pins']['10'],'3V3_IO')
        self.assertEqual(self.c['P05_U1']['pins']['23'],'3V3_IO')
        for k in ['P05_U6','P07_U4']:self.assertIn('TLV1702AQDGKRQ1',self.c[k]['value'])

    def test_removed_dead_nets_and_tied_spare_gate(self):
        nets={n for c in self.c.values() for n in c['pins'].values()}
        self.assertTrue(nets.isdisjoint(['STOP_PRESSED','I_LOG_SER','I_TEST_SER','LOCAL_ARM_CLK']))
        self.assertEqual({k:self.c['P07_U_GATE']['pins'][k] for k in ['4','5','6']},{'4':'GND','5':'GND','6':'NC'})
        self.assertEqual(self.c['P07_U_OC_LATCH']['pins']['3'],'ARM_CLK_P07')
        self.assertEqual(self.c['P07_U_OC_LATCH']['pins']['2'],'PERMIT_N')

    def test_p01_fault_transistor_bias_is_actually_supplied_by_pg(self):
        pg=self.c['P01_J_PGB']['pins']
        bias=self.c['P01_R30']['pins']
        self.assertEqual(pg['1'],'3V3_IO')
        self.assertEqual(bias['1'],pg['1'])
        self.assertEqual(bias['2'],self.c['P01_Q7']['pins']['2'])
        self.assertEqual(self.c['P01_Q7']['pins']['3'],'SAFE_N')
        nets={n for c in self.c.values() for n in c['pins'].values()}
        self.assertNotIn('P01_BOARD_3V3',nets)
        for ref in ['J1','J2','J4','J_PRES']:
            self.assertEqual(self.c['P01_'+ref]['kind'],'testpad')
            self.assertFalse(any(x['module']=='P01' and x['ref']==ref for x in self.bom))

    def test_reference_caps_parallel_to_adc_and_not_series(self):
        for b in ['P06','P07']:
            ref=self.c[b+'_U_ADC']['pins']['1']
            self.assertEqual(self.c[b+'_U_REF']['pins']['2'],ref)
            for r in ['C_REF','C_REF_HF']:self.assertEqual(set(self.c[b+'_'+r]['pins'].values()),{ref,'GND'})
            self.assertTrue(self.c[b+'_C_REF']['value'].startswith('4.7uF'))

    def test_pigtail_is_exactly_one_pth_end_and_one_receiver(self):
        for r in self.i:
            if r['lacze']=='DAQ' or r['lacze'].startswith('EXT_'):continue
            a=self.c[r['koniec_A'].replace('/','_')];b=self.c[r['koniec_B'].replace('/','_')]
            self.assertEqual(a['kind'],'connector')
            self.assertEqual(b['kind'],'termination')
            self.assertEqual(r['koniec_lutowany'],r['koniec_B'])
            self.assertEqual(r['kotwa_mm'],'10–15')
            self.assertIn('PTH',r['zakonczenie']);self.assertGreater(int(r['dlugosc_mm']),0)
            pins={w['to_pin'] for w in self.w if w['cable']==r['lacze']}
            self.assertEqual(pins,set(b['pins']))
            self.assertFalse(any(x['module']==b['board'] and x['ref']==b['ref'] for x in self.bom))

    def test_daq_direct_connection_has_no_harness_or_power_alias(self):
        r=next(x for x in self.i if x['lacze']=='DAQ')
        self.assertEqual(r['rodzina'],'B2B 2.54');self.assertEqual(int(r['dlugosc_mm']),0)
        self.assertFalse(any(x['ref']=='H_DAQ' for x in self.bom))
        for key in ['P03_J_DAQA','P05_J_DAQB']:
            c=self.c[key];self.assertEqual(c['kind'],'connector');self.assertNotIn('2',c['pins']);self.assertEqual(len(c['pins']),15)
            self.assertTrue(set(c['pins'].values()).isdisjoint(['3V3_IO','3V3_CORE','5V_SYS']))
        self.assertEqual(self.c['P03_J_DAQA']['pins'],self.c['P05_J_DAQB']['pins'])

    def test_every_harness_is_in_owner_bom_with_length_and_plug(self):
        for r in self.i:
            if r['wlasciciel_wiazki']=='BRAK':continue
            owner=r['wlasciciel_wiazki'];local=rows('hardware/'+owner+'-BOM.csv')
            found=[x for x in local if x['ref']=='H_'+r['lacze']]
            self.assertEqual(len(found),1)
            self.assertEqual(found[0]['length_mm'],r['dlugosc_mm'])
            self.assertEqual(found[0]['plug_type'],r['typ_wtyku'])
            self.assertEqual(found[0]['category'],'wiązka')

    def test_bought_boards_keep_their_original_pins(self):
        base=json.loads((HW/'reference/purchased-module-pins-v5.json').read_text(encoding='utf-8'))
        expected={'P07_M2':'Pololu 1451 / VNH5019','P09_TC1':'MAX31856','P09_TC2':'MAX31856'}
        for key,part in expected.items():
            self.assertIn(part,self.c[key]['value'])
            self.assertEqual(self.c[key]['pins'],base[key]['pins'])
            self.assertNotEqual(self.c[key]['kind'],'termination')

    def test_adc_lvc_and_other_adapters_follow_assembly_method(self):
        a=rows('hardware/adaptery.csv')
        self.assertEqual(sum('SO14' in x['name'] for x in a),18)
        self.assertTrue(all(x['module'] not in ['P01','P05','P07'] for x in a))
        self.assertEqual(sum('74LVC125AD' in c['value'] for c in self.c.values()),26)
        for x in a:self.assertIn(x['module']+'_'+x['for_ref'],self.c)

    def test_all_series_pairs_collapsed_without_dangling_midpoints(self):
        merged=rows('hardware/rezystory-zamiany.csv');self.assertEqual(len(merged),18)
        nets=collections.defaultdict(list)
        for key,c in self.c.items():
            for n in c['pins'].values():nets[n].append(c)
        for r in merged:
            self.assertNotIn(r['removed_midpoint'],nets)
            self.assertIn('0207',self.c[r['module']+'_'+r['new_ref']]['value'])
            self.assertNotIn(r['module']+'_'+r['old_refs'].split(' + ')[1],self.c)
        remaining=[n for n,cs in nets.items() if n!='NC' and len(cs)==2 and all(c['kind'] in ['res','R'] for c in cs)]
        self.assertEqual(remaining,[])

    def test_firmware_gains_follow_real_resistor_nominals(self):
        def ohms(k):
            value=self.c[k]['value'].split()[0]
            return float(value.rstrip('k'))*1000 if value.endswith('k') else float(value)
        code=(R/'firmware/main/control.c').read_text(encoding='utf-8')
        gains=[float(v.strip().rstrip('f')) for v in re.search(r'const float nominal\[8\] = \{([^}]+)',code)[1].split(',')]
        parallel=1/(1/100000+1/5000000)
        self.assertAlmostEqual(gains[0],1+ohms('AT_RM1')/parallel,places=5)
        self.assertAlmostEqual(gains[2],1+ohms('AT_RS1')/5000000,places=5)
        self.assertAlmostEqual(gains[6],1+ohms('P05_RV1')/parallel,places=5)

    def test_taps_sensor_pins_not_grounded_and_local_kelvin(self):
        p=self.c['P05_J_TAPSB']['pins']
        self.assertEqual(p['7'],'TAP_P5');self.assertEqual(p['9'],'TAP_P6')
        self.assertEqual(len(p),12)
        self.assertTrue(all(p[str(i)]=='GND' for i in [2,4,6,8,10]))
        self.assertFalse(any(w['net'].startswith(('INA_L_','INA_T_')) for w in self.w))

    def test_interfaces_copies_and_card_references(self):
        self.assertEqual((HW/'interfejsy.csv').read_bytes(),(HW/'hardware/interfejsy.csv').read_bytes())
        docs=(HW/'docs/PCB.md').read_text(encoding='utf-8')
        for r in self.i:self.assertIn('| '+r['lacze']+' |',docs)

    def test_procurement_sum_does_not_buy_pth_pads_or_duplicate_harnesses(self):
        expected=collections.Counter()
        for x in self.bom:
            if x['category']!='wiązka':expected[(x['name'],x['unit'])]+=float(x['quantity'])
        for filename in ['wiazki-czesci.csv','materialy.csv']:
            for x in rows('hardware/'+filename):expected[(x['nazwa'],x['jednostka'])]+=float(x['ilosc'])
        actual={(x['nazwa'],x['jednostka']):float(x['ilosc']) for x in rows('hardware/zakupy.csv')}
        self.assertEqual(actual,{k:round(v,3) for k,v in expected.items()})
        harness_names={x['name'] for x in self.bom if x['category']=='wiązka'}
        self.assertFalse(any('PTH lutowane' in key[0] or key[0] in harness_names for key in actual))

    def test_v5_profile_rejected_and_commissioning_stays_disabled(self):
        objects=[json.loads((R/'profiles'/f'{x}.json').read_text()) for x in ['hardware','valve','session']]
        # 6.3-m1 (M-13): sprzet M1-R1 ma schema 7, zawor i sesja zostaja na 6.
        self.assertEqual([o['schema'] for o in objects],[7,6,6])
        objects[0]['schema']=5
        with self.assertRaisesRegex(ValueError,'schema 6'):profile_v6.commands(*objects)
        self.assertIn('#define EGR_HARDWARE_ACCEPTED 0',(R/'firmware/main/commissioning.h').read_text())
        header=(R/'firmware/main/control.h').read_text();self.assertIn('0x36524745u',header);self.assertIn('EGR_PROFILE_VERSION 7',header)

    def test_configurable_clocks_are_used_and_timing_limit_retained(self):
        code=(R/'firmware/main/board.c').read_text(encoding='utf-8')
        self.assertIn('.clock_speed_hz = CONFIG_EGR_ADC_SPI_HZ',code)
        self.assertIn('host.max_freq_khz = CONFIG_EGR_SD_KHZ',code)
        k=(R/'firmware/main/Kconfig.projbuild').read_text()
        self.assertRegex(k,r'config EGR_ADC_SPI_HZ[\s\S]*?default 1000000')
        self.assertRegex(k,r'config EGR_SD_KHZ[\s\S]*?default 4000')
        self.assertNotIn('.clock_speed_hz=500000',code)   # 6.3-m1: bez MCP3201 (M-01)
        self.assertIn('pdMS_TO_TICKS(100)',code)

if __name__=='__main__':unittest.main()

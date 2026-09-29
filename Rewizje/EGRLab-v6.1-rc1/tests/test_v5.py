import csv,itertools,json,math,sys,tempfile,unittest,collections,copy
from pathlib import Path
R=Path(__file__).parents[1];sys.path.insert(0,str(R/'tools'))
import egrlog as log
import profile_v6 as profiles

class V5Logs(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.d=Path(self.tmp.name)
        self.cfg=log.config_event(1,local_current=True,current_adc_gain=5/4096,current_adc_offset=0,
            current_calibrated=True,voltage_calibrated=True,daq_module='DAQ_A',current_module='IL_A')
    def row(self,raw=2253,status=1,begin=60,end=98):return (1,0,0,0,16000,8000,0,0,20000,0,raw,begin,end,status,0,1)
    def test_local_scaling_and_legacy_are_independent(self):
        values=log.physical(self.row(),self.cfg)
        self.assertAlmostEqual(values[-4],(2253*5/4096-2.5)/.25)
        self.assertEqual(values[9],0) # original AD raw[5] retained
        self.assertGreater(values[17],2.5) # semantic current-output voltage
    def test_missing_current_never_becomes_zero_amps(self):
        for status in [0,2,4,8,16]:self.assertTrue(math.isnan(log.physical(self.row(status=status),self.cfg)[-4]))
    def test_current_bad_time_or_unqualified_is_blank(self):
        for row in [self.row(begin=98,end=60),self.row(end=450),self.row(begin=1,end=102)]:
            self.assertTrue(math.isnan(log.physical(row,self.cfg)[-4]))
        self.cfg['current_calibrated']=False
        self.assertTrue(math.isnan(log.physical(self.row(),self.cfg)[-4]))
    def test_unqualified_voltage_preserves_raw_and_current(self):
        self.cfg['voltage_calibrated']=False;v=log.physical(self.row(),self.cfg)
        self.assertEqual(v[6],16000);self.assertTrue(math.isnan(v[14]));self.assertTrue(math.isfinite(v[-4]))
    def test_v5_header_crc_csv_preserves_local_raw(self):
        path=self.d/'samples_000.egr';log.write_log(path,[self.row()],version=5)
        (self.d/'events_000.ndjson').write_text(json.dumps(self.cfg)+'\n')
        self.assertEqual(log.inspect(path)['record_bytes'],40)
        out=self.d/'o.csv';log.export(path,out)
        with out.open() as f:r=next(csv.DictReader(f))
        self.assertEqual(r['current_raw'],'2253');self.assertEqual(r['current_end_us'],'98')
        raw=bytearray(path.read_bytes());raw[-5]^=1;path.write_bytes(raw)
        with self.assertRaises(log.LogError):log.inspect(path)
    def test_wrong_record_size_rejected(self):
        import io
        data=log.HEADER.pack(b'EGRLOG1\0',5,32,2000,32,0,1)
        with self.assertRaises(log.LogError):log.read_header(io.BytesIO(data))

class V5Hardware(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=json.loads((R/'hardware/components.json').read_text(encoding='utf-8'))
        cls.w=list(csv.DictReader((R/'hardware/wiring.csv').open(encoding='utf-8-sig'),delimiter=';'))
    def test_every_wire_matches_both_actual_connector_pins(self):
        for w in self.w:
            for side in ['from','to']:
                c=self.c[w[side+'_board']+'_'+w[side+'_ref']]
                self.assertEqual(c['pins'][w[side+'_pin']],w['net'])
    def test_cross_board_nets_have_complete_wire_paths(self):
        used=collections.defaultdict(set);cables={w['cable'] for w in self.w}
        for c in self.c.values():
            if c['kind']=='connector' and c['note'] in cables:continue
            for n in c['pins'].values():
                if n!='NC':used[n].add(c['board'])
        for net,boards in used.items():
            if len(boards)<2:continue
            pairs=[(w['from_board'],w['to_board']) for w in self.w if w['net']==net]
            known={next(iter(boards))}
            while True:
                before=set(known)
                for a,b in pairs:
                    if a in known or b in known:known.update([a,b])
                if before==known:break
            self.assertTrue(boards<=known,(net,boards-known))
    def test_no_18volt_gpio_or_b7_input(self):
        m=self.c['P03_M1']['pins'];self.assertFalse({'47','48','35','36','37'}&set(m))
        self.assertEqual(self.c['P03_U17']['pins']['25'],'LOGGER_CURRENT_OK_CORE')
        self.assertEqual(self.c['P03_U17']['pins']['8'],'NC')
        code=(R/'firmware/main/board.c').read_text(encoding='utf-8')
        self.assertIn('mcp_write(0x00, 0x10)',code);self.assertIn('mcp_write(0x01, 0x7f)',code)
    def test_idc_mechanical_keys_remove_only_the_specified_position(self):
        rows=list(csv.DictReader((R/'hardware/connectors.csv').open(encoding='utf-8-sig'),delimiter=';'))
        seen={}
        for r in rows:
            if r['family']!='IDC':continue
            key=(r['positions'],r['key_pin']);self.assertNotIn(key,seen);seen[key]=r['cable']
            a,b=r['ends'].split('/')
            for board,end in [(a,'A'),(b,'B')]:
                pins=self.c[board+'_J_'+r['cable']+end]['pins']
                self.assertNotIn(r['key_pin'],pins)
                self.assertEqual(len(pins),int(r['positions'])-1)
    def test_reference_regulator_adc_and_inamp_pins(self):
        for b,u in [('P06','U3'),('P07','U2')]:
            self.assertEqual(self.c[b+'_U_REF']['pins'],{'1':'GND','2':b+'_REF25','3':b+'_3V3'})
            self.assertEqual(self.c[b+'_U_LDO']['pins'],{'1':'GND','2':'5VA_'+b,'3':b+'_3V3'})
            a=self.c[b+'_U_ADC']['pins'];self.assertEqual(a['1'],b+'_REF25');self.assertEqual(a['3'],'GND')
            for pin in ['3','7']:self.assertEqual(self.c[b+'_'+u]['pins'][pin],b+'_REF_BUF')
    def test_interlock_entire_truth_table_from_gate_pins(self):
        names=['PSU_OK_P04','DAQ_OK_P04','DRIVE_OK_P04','SENSOR_OK_P04','CORE_LINK_P04','PG_LINK_P04','MECH_OK']
        for bits in itertools.product([False,True],repeat=len(names)):
            state=dict(zip(names,bits));state['GND']=False
            for ref in ['P04_U_LINK','P04_U_LINK2']:
                pins=self.c[ref]['pins']
                for a,b,y in [('1','2','3'),('4','5','6'),('9','10','8'),('12','13','11')]:
                    if pins[y]!='NC':state[pins[y]]=state[pins[a]] and state[pins[b]]
            self.assertEqual(state['INTERLOCK'],all(bits))
    def test_local_permit_requires_latch_and_power(self):
        pins=self.c['P07_U_GATE']['pins']
        for permit,good,rails in itertools.product([0,1],repeat=3):
            n={'MOTOR_PERMIT_P07':permit,'OC_GOOD':good,'P07_RAILS_OK':rails}
            n[pins['8']]=n[pins['9']] and n[pins['10']]
            n[pins['11']]=n[pins['12']] and n[pins['13']]
            self.assertEqual(n['LOCAL_PERMIT'],permit and good and rails)
        latch=self.c['P07_U_OC_LATCH']['pins']
        self.assertEqual(latch['1'],'LOCAL_CLEAR_N');self.assertEqual(latch['3'],'ARM_CLK_P07')
        self.assertEqual(self.c['P07_M2']['pins']['VDD'],'LOCAL_PERMIT')
    def test_supervisor_has_no_parallel_push_pull_driver(self):
        self.assertEqual(self.c['P03_U5']['pins']['1'],'SUP_N')
        self.assertEqual(self.c['P03_U5']['pins']['6'],'3V3_CORE')
        self.assertNotIn('P04_U5',self.c)
        # Bus interfaces explicitly select a manufacturer whose part has Ioff.
        for c in self.c.values():
            if '125A' in c['value']:self.assertIn('Nexperia',c['value'])
    def test_no_abandoned_parallel_oc_dividers_or_current_relay(self):
        for r in ['R_OC_LT','R_OC_LB','R_OC_HT','R_OC_HB']:self.assertNotIn('P07_'+r,self.c)
        self.assertNotIn('P05_KCUR',self.c);self.assertNotIn('P06_J_BYPASS',self.c)

class V5Profiles(unittest.TestCase):
    def setUp(self):
        self.hw,self.valve,self.session=[json.loads((R/'profiles'/f'{name}.json').read_text()) for name in ['hardware','valve','session']]
    def measured_fixture(self):
        for v in self.hw['voltage']:v.update(accepted=True,gain=[1]*8,offset=[0]*8)
        for a in self.hw['aux']:a.update(gain=1,offset=0)
        for c in self.hw['current']:c.update(accepted=True,adc_gain=5/4096,adc_offset=0,volts_per_amp=.25,zero=2.5)
    def test_templates_cannot_commission_hardware(self):
        with self.assertRaises(ValueError):profiles.commands(self.hw,self.valve,self.session)
    def test_complete_profile_emits_no_arm_test_or_qualify(self):
        self.measured_fixture();s=profiles.commands(self.hw,self.valve,self.session)
        self.assertTrue(s.startswith('stop\nbind '));self.assertNotIn('qualify',s)
        self.assertTrue({'arm','test'}.isdisjoint(line.split()[0] for line in s.splitlines()))
        self.assertLess(s.index('auxcal 1'),s.index('vcalok 0'))
    def test_module_identity_mismatch_and_nan_rejected(self):
        self.measured_fixture();self.hw['modules']['P06']['serial']='DIFFERENT'
        with self.assertRaises(ValueError):profiles.commands(self.hw,self.valve,self.session)
        self.hw['modules']['P06']['serial']=self.hw['current'][0]['module_id']
        self.hw['current'][0]['adc_gain']=float('nan')
        with self.assertRaises(ValueError):profiles.commands(self.hw,self.valve,self.session)
    def test_synthetic_or_other_drive_class_rejected(self):
        self.measured_fixture();self.session['synthetic']=True
        with self.assertRaises(ValueError):profiles.commands(self.hw,self.valve,self.session)
        self.session['synthetic']=False;self.valve['drive_class']='smart_can'
        with self.assertRaises(ValueError):profiles.commands(self.hw,self.valve,self.session)

if __name__=='__main__':unittest.main()

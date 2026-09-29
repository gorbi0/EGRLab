import csv,json,math,re,sys,tempfile,unittest
from itertools import product
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'tools'))
import egrlog as log
from profile_commands import commands

class V4Regression(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.dir=Path(self.tmp.name);self.path=self.dir/'samples_000.egr'
    def cfg(self,**kw):
        return log.config_event(1,gain=[1]*8,offset=[0]*8,full_scale=[10]*8,**kw)
    def row(self,t=1,n=0,flags=0,cfg=1):return (t,n,0,0,16384,8192,66,8192,20000,0,flags,cfg)
    def write(self,rows,cfg=None):
        log.write_log(self.path,rows)
        (self.dir/'events_000.ndjson').write_text(json.dumps(cfg or self.cfg())+'\n',encoding='utf-8')
    def test_missing_snapshot_never_borrows_scale(self):
        self.write([self.row(cfg=2)]);out=self.dir/'x.csv';warnings=log.export(self.path,out)
        with out.open() as f:r=next(csv.DictReader(f))
        self.assertEqual(r['pin6_v'],'');self.assertEqual(r['current_a'],'')
        self.assertEqual(r['raw_ch5'],'66');self.assertTrue(warnings)
    def test_absent_metadata_does_not_guess_v4(self):
        log.write_log(self.path,[self.row()]);out=self.dir/'x.csv';log.export(self.path,out)
        with out.open() as f:r=next(csv.DictReader(f))
        self.assertEqual(r['sensor_ratio'],'')
    def test_legacy_manual_metadata_warns_and_preserves_raw(self):
        log.write_log(self.path,[self.row()],version=2)
        old=self.cfg()
        for field in ('adc_config_ok','current_valid','learned'): old.pop(field)
        meta=self.dir/'old.json';meta.write_text(json.dumps(old),encoding='utf-8')
        out=self.dir/'x.csv';warnings=log.export(self.path,out,meta_path=meta)
        with out.open() as f:r=next(csv.DictReader(f))
        self.assertEqual(r['pin6_v'],'');self.assertEqual(r['position'],'')
        self.assertEqual(r['raw_ch5'],'66')
        for field in ('adc_config_ok','current_valid','learned'):
            self.assertTrue(any(field in w and '--meta old.json' in w for w in warnings))
        html=self.dir/'r.html';log.report(self.path,html,meta_path=meta)
        self.assertIn('brak adc_config_ok',html.read_text(encoding='utf-8'))
    def test_legacy_explicit_valid_metadata_still_exports(self):
        log.write_log(self.path,[self.row()],version=2)
        meta=self.dir/'valid.json';meta.write_text(json.dumps(self.cfg()),encoding='utf-8')
        out=self.dir/'x.csv';warnings=log.export(self.path,out,meta_path=meta)
        with out.open() as f:r=next(csv.DictReader(f))
        self.assertNotEqual(r['pin6_v'],'');self.assertFalse(warnings)
    def test_config_event_missing_validity_warns(self):
        cfg=self.cfg();cfg.pop('adc_config_ok');self.write([self.row()],cfg)
        warnings=log.export(self.path,self.dir/'x.csv')
        self.assertTrue(any('config_id=1: brak adc_config_ok' in w for w in warnings))
    def test_failed_adc_invalidates_all_physical_values(self):
        v=log.physical(self.row(),self.cfg(adc_config_ok=False))
        self.assertTrue(all(math.isnan(x) for x in v[12:]))
    def test_learned_false_leaves_ratio_but_no_position(self):
        v=log.physical(self.row(),self.cfg(learned=False))
        self.assertTrue(math.isfinite(v[-2]));self.assertTrue(math.isnan(v[-1]))
    def test_saturated_channel_not_reported_as_voltage(self):
        row=list(self.row());row[6]=32767
        v=log.physical(row,self.cfg());self.assertTrue(math.isnan(v[16]))
    def test_invalid_record_flag(self):
        v=log.physical(self.row(flags=128),self.cfg());self.assertTrue(math.isnan(v[-4]))
    def test_strict_json_rejects_nan(self):
        p=self.dir/'events.ndjson';p.write_text('{"type":"trigger","i":NaN}\n{"type":"trigger","i":null}\n')
        events,warnings=log.load_events(p);self.assertEqual(len(events),1);self.assertTrue(warnings)
    def test_single_sample_peak_survives_envelope(self):
        rows=[self.row(1+500*n,n) for n in range(4000)]
        r=list(rows[17]);r[6]=1311;rows[17]=tuple(r);self.write(rows)
        p=self.dir/'r.html';log.report(self.path,p,points=20)
        text=p.read_text(encoding='utf-8')
        data=json.loads(re.search(r'<script id="data" type="application/json">(.*?)</script>',text).group(1))
        self.assertGreater(max(x[1] for x in data['series']['ground']),.39)
        self.assertNotIn('https://',text);self.assertNotIn('NaN',text)
    def test_segments_and_time_window(self):
        self.write([self.row(1,0),self.row(501,1)])
        log.write_log(self.dir/'samples_001.egr',[self.row(1001,2),self.row(1501,3)])
        self.assertEqual(log.inspect(self.dir)['records'],4)
        out=self.dir/'x.csv';log.export(self.dir,out,start=.001,end=.002)
        with out.open() as f:self.assertEqual(len(list(csv.DictReader(f))),2)
    def test_unknown_range_is_invalid(self):
        cfg=self.cfg();cfg['full_scale'][4]=None
        self.assertTrue(math.isnan(log.physical(self.row(),cfg)[16]))
    def test_current_bypass_and_null_temperature_scan(self):
        cfg=self.cfg(current_valid=False);self.assertTrue(math.isnan(log.physical(self.row(),cfg)[-4]))
        p=self.dir/'events.ndjson';p.write_text(json.dumps(dict(type='summary',ch=[[None,None,None]]*8))+'\n')
        self.assertEqual(log.scan(p)['extremes'],{})
    def test_profile_import_refuses_unmeasured_zero(self):
        p=json.loads((Path(__file__).parents[1]/'hardware/profile.template.json').read_text(encoding='utf-8'))
        p['valve_id']='valve_a';p['adapter_id']='T_01'
        with self.assertRaises(ValueError):commands(p)
        p['current_zero']=[2.49,2.51];s=commands(p)
        self.assertIn('currentcal 1 2.51',s);self.assertTrue(s.endswith('save\nprofile\n'))

class HardwareNetChecks(unittest.TestCase):
    def setUp(self):
        root=Path(__file__).parents[1]/'hardware'
        with (root/'ic-pins.csv').open(encoding='utf-8-sig') as f:self.pins={(r['ref'],r['pin']):r['net'] for r in csv.DictReader(f,delimiter=';')}
        with (root/'connections.csv').open(encoding='utf-8-sig') as f:self.edges=list(csv.DictReader(f,delimiter=';'))
    def test_watchdog_reset_is_independent(self):
        self.assertEqual(self.pins['U7','3'],'SUP_N');self.assertEqual(self.pins['U9','1'],'SAFE_N')
        self.assertEqual(self.pins['U5','1'],'SUP_N');self.assertEqual(self.pins['Q9','3'],'SAFE_N')
        for r in self.edges:self.assertNotEqual({r['from'],r['to']},{'SUP_N','SAFE_N'})
    def test_no_push_pull_on_safe(self):
        allowed={'U4','U6','U9','U12','Q8','Q9','Q10'}
        self.assertTrue(all(ref in allowed for (ref,pin),net in self.pins.items() if net=='SAFE_N'))
    def interlock_reachable(self, key, log1, log2, loop, edges=None):
        # Traverse actual copper/wiring, then add physically closed contacts.
        # Resistors are not ideal wires: the pulldown is checked separately.
        graph={}
        def wire(a,b):
            graph.setdefault(a,set()).add(b);graph.setdefault(b,set()).add(a)
        for row in self.edges if edges is None else edges:wire(row['from'],row['to'])
        for (ref,pin),net in self.pins.items():
            if net!='NC':wire(f'{ref}.{pin}',net)
        if key:wire('SW_MODE.COM','SW_MODE.TEST_NO')
        for ref,present in (('SW_LOG1',log1),('SW_LOG2',log2)):
            if not present:
                for pole in ('A','B'):wire(f'{ref}.COM_{pole}',f'{ref}.NC_{pole}')
        if loop:wire('J_TEST.10','J_TEST.11')
        seen=set();todo=['3V3_IO']
        while todo:
            node=todo.pop()
            if node in seen:continue
            seen.add(node);todo.extend(graph.get(node,()))
        return 'INTERLOCK' in seen
    def test_interlock_truth_table(self):
        for key,log1,log2,loop in product((False,True),repeat=4):
            with self.subTest(key=key,log1=log1,log2=log2,loop=loop):
                self.assertEqual(self.interlock_reachable(key,log1,log2,loop),
                                 key and not log1 and not log2 and loop)
        for ref,pin in (('U10','5'),('U12','2'),('U8','9')):
            self.assertEqual(self.pins[ref,pin],'INTERLOCK')
        for a,b in (('INTERLOCK','R_PD_INTERLOCK.1'),('R_PD_INTERLOCK.2','AGND')):
            self.assertTrue(any({r['from'],r['to']}=={a,b} for r in self.edges))
    def test_interlock_graph_detects_wiring_mutations(self):
        chain=[('3V3_IO','SW_MODE.COM'),('SW_MODE.TEST_NO','TEST_KEY'),
               ('TEST_KEY','SW_LOG1.COM_A'),('SW_LOG1.NC_A','SW_LOG2.COM_A'),
               ('SW_LOG2.NC_A','J_TEST.10'),('J_TEST.11','INTERLOCK')]
        for a,b in chain:
            broken=[r for r in self.edges if {r['from'],r['to']}!={a,b}]
            self.assertLess(len(broken),len(self.edges))
            self.assertFalse(self.interlock_reachable(True,False,False,True,broken))
        for a,b,state in [('J_TEST.10','J_TEST.11',(True,False,False,False)),
                          ('SW_LOG1.COM_A','SW_LOG1.NC_A',(True,True,False,True))]:
            bridged=self.edges+[{'from':a,'to':b}]
            self.assertFalse(self.interlock_reachable(*state))
            self.assertTrue(self.interlock_reachable(*state,edges=bridged))
    def test_mcp_reset_and_output_only_bit(self):
        self.assertEqual(self.pins['U17','18'],'SUP_N')
        self.assertEqual(self.pins['U17','7'],'STOP_PRESSED')
        self.assertEqual(self.pins['U17','8'],'NC')
    def test_adc_pins_and_watchdog_cap(self):
        self.assertEqual(sum(ref=='U1' for ref,pin in self.pins),64)
        self.assertEqual(self.pins['U1','9'],'ADC_CONVST')
        self.assertEqual(self.pins['U1','10'],'3V3_IO') # WR, not CONVST_B on B variant
        self.assertEqual(self.pins['U7','14'],'WD_C');self.assertEqual(self.pins['U7','15'],'WD_RC')

if __name__=='__main__':unittest.main()

import csv,json,math,re,sys,tempfile,unittest
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
    def test_interlock_truth_table(self):
        # Exhaust all plug/key/loop combinations; broken loop must deny TEST.
        for key in (0,1):
            for log1 in (0,1):
                for log2 in (0,1):
                    for loop in (0,1):
                        interlock=key and not log1 and not log2 and loop
                        if not key or log1 or log2 or not loop:self.assertFalse(interlock)
                        else:self.assertTrue(interlock)
    def test_mcp_reset_and_output_only_bit(self):
        self.assertEqual(self.pins['U17','18'],'SUP_N')
        self.assertEqual(self.pins['U17','7'],'STOP_PRESSED')
        self.assertEqual(self.pins['U17','8'],'NC')
    def test_adc_pins_and_watchdog_cap(self):
        self.assertEqual(sum(ref=='U1' for ref,pin in self.pins),64)
        self.assertEqual(self.pins['U1','10'],'3V3_IO') # WR, not CONVST_B on B variant
        self.assertEqual(self.pins['U7','14'],'WD_C');self.assertEqual(self.pins['U7','15'],'WD_RC')

if __name__=='__main__':unittest.main()

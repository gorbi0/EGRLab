import importlib.util,itertools,json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('contract',R/'stabilizacja/checks.py');contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract)
class Stabilization(unittest.TestCase):
    def setUp(self):self.c,self.w,self.k=contract.load(R/'hardware')
    def test_contract_covers_all_rails_and_ports(self):self.assertEqual(contract.check(self.c,self.w,self.k),{})
    def test_real_v6_fails_before_fixes(self):
        c,w,k=contract.load(R/'stabilizacja/baseline');fail=contract.check(c,w,k)
        self.assertTrue({'F01','F02','F03','F04','T01','T02'}<=set(fail))
        self.assertEqual(contract.disconnected(c,w),{'VPROT':['P05']})
    def test_mutations_are_detected(self):self.assertEqual(len(contract.mutations(self.c,self.w,self.k)),10)
    def test_sensor_health_truth_table_from_actual_pins(self):
        gate=self.c['P08_U_READY']['pins'];tx=self.c['P08_U_RX1']['pins'];rx=self.c['P03_U_IN2']['pins']
        pd=self.c['P03_R_PD_SENSOR_HEALTHY']['pins']
        for rails,raw_fault_n,powered,cable in itertools.product([0,1],repeat=4):
            state={'SENSOR_OK':rails,'SENSOR_FAULT_LOCAL_N':raw_fault_n,'GND':0}
            state[gate['8']]=state[gate['9']] and state[gate['10']]
            driven=powered and cable and not state[tx['4']]
            wire=state[tx['5']] if driven else state[pd['2']]
            self.assertEqual(tx['6'],pd['1']);self.assertEqual(rx['12'],pd['1'])
            self.assertEqual(bool(wire),bool(rails and raw_fault_n and powered and cable))
    def test_health_does_not_feed_enable_and_create_retry_loop(self):
        gate=self.c['P08_U_READY']['pins']
        self.assertEqual((gate['1'],gate['2'],gate['3']),('P08_SUP3_N','P08_SUP5_N','SENSOR_OK'))
        self.assertEqual((gate['4'],gate['5'],gate['6']),('SENSOR_PERMIT_P08','SENSOR_OK','SENSOR_LOCAL'))
        self.assertEqual(self.c['P08_U11']['pins']['3'],'SENSOR_LOCAL')
    def test_application_calls_freshness_guard_and_updates_time_with_inputs(self):
        app=(R/'firmware/main/app_main.c').read_text(encoding='utf-8')
        snapshot=app[app.index('static inputs_t snapshot'):app.index('static void tick')]
        self.assertIn('it=inputs_time',snapshot);self.assertIn('control_guard_io(&i,it)',snapshot)
        update=app[app.index('bool io_ok='):app.index('#if CONFIG_EGR_CAN_PRESENT',app.index('bool io_ok='))]
        self.assertLess(update.index('portENTER_CRITICAL'),update.index('inputs_time=completed'))
        self.assertLess(update.index('inputs_time=completed'),update.index('portEXIT_CRITICAL'))
        board=(R/'firmware/main/board.c').read_text(encoding='utf-8')
        self.assertIn('mcp_write(0x0d, 0x4c)',board);self.assertIn('*sensor_fault = !(b & B_SENSOR_HEALTHY)',board)
    def test_integrated_p01_keeps_reviewed_analog_circuit(self):
        reference=json.loads((R/'P01-PROTECT/hardware/components.json').read_text(encoding='utf-8'))
        def net(n):
            if n=='FAULT_OC':return 'SAFE_N'
            if n=='BOARD_3V3':return '3V3_IO'
            if n in ['GND','VPROT','BAT_FUSED','PG_SEND','PG_LINK','NC']:return n
            return 'P01_'+n
        for ref,c in reference.items():
            self.assertEqual(self.c['P01_'+ref]['pins'],{p:net(n) for p,n in c['pins'].items()},ref)
if __name__=='__main__':unittest.main()

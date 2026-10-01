"""6.2-s1: statyczne kontrole zmian z Plytki/Format-S1/zadania/ZADANIE-FIRMWARE-S1.md (F-01...F-09, decyzje D-1...D-3).
Czytaja zrodla tej rewizji; nie zastepuja odbioru na sprzecie (ODBIOR P02 R4 O-05, P05 kroki 8-17, P10 \"Ruch ciagly\")."""
import json,re,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];HW=R.parent/'EGRLab-v6.1-rc1';M=R/'firmware/main'
def src(name):return (M/name).read_text(encoding='utf-8')
def body(text,signature):
    start=text.index(signature);i=text.index('{',start)+1;depth=1
    while depth:depth+=(text[i]=='{')-(text[i]=='}');i+=1
    return text[start:i]
class S1Firmware(unittest.TestCase):
    def test_f01_pfail_input_without_internal_pulls_and_falling_edge(self):
        init=body(src('board.c'),'void board_pfail_init(')
        self.assertIn('1ULL << PFAIL_N',init);self.assertIn('GPIO_PULLUP_DISABLE',init);self.assertIn('GPIO_PULLDOWN_DISABLE',init)
        self.assertIn('GPIO_INTR_NEGEDGE',init);self.assertIn('PFAIL_N = 3',src('board.c'))
    def test_d3_drive_stops_before_files_close(self):
        pf=body(src('app_main.c'),'static void power_fail(')
        self.assertLess(pf.index('board_power_fail_stop()'),pf.index('esp_timer_stop(timer)'))
        self.assertLess(pf.index('esp_timer_stop(timer)'),pf.index('storage_power_fail('))
        self.assertIn('powerfail ||',body(src('board.c'),'void board_drive('))   # PWM nie wraca po PFAIL
        close=body(src('storage.c'),'bool storage_power_fail(')
        self.assertIn('\\"reason\\":\\"UVLO\\"',close);self.assertIn('fclose(samples)',close);self.assertIn('fclose(eventfile)',close)
    def test_d2_bench_mode_from_low_pfail_for_100_ms(self):
        app=body(src('app_main.c'),'void app_main(')
        self.assertIn('k<=20',app);self.assertIn('vTaskDelay(pdMS_TO_TICKS(5))',app)   # 21 odczytow co 5 ms = 100 ms
        self.assertIn('storage_init_bench(',app);self.assertIn('if(!bench_mode) { session++;',app)
        self.assertIn('if(bench_mode && !strcmp(cmd,"test")) return false;',src('app_main.c'))
        self.assertLess(app.index('board_pfail_init()'),app.index('nvs_flash_init()'))
    def test_f04_adc_startup_and_meas_enable_order(self):
        b=src('board.c')
        self.assertRegex(b,r'vTaskDelay\(pdMS_TO_TICKS\(10\)\);\s*ESP_ERROR_CHECK\(porta_set\(A_ADC_RESET, true\)\)')
        self.assertIn('ESP_ERROR_CHECK(porta_set(A_ADC_RESET, false)); vTaskDelay(pdMS_TO_TICKS(2100));',b)
        self.assertIn('vTaskDelay(pdMS_TO_TICKS(2100));',body(b,'static esp_err_t adc_full_reset('))
        self.assertIn('adc_reset_needed = true',body(b,'esp_err_t board_adc('))
        self.assertIn('vTaskDelay(pdMS_TO_TICKS(25))',body(b,'esp_err_t board_mode('))
        commit=body(src('app_main.c'),'static bool commit_locked(')
        self.assertLess(commit.index('board_adc_ranges('),commit.index('board_mode(ctrl.test_bank,ctrl.sensor_on)'))
        self.assertIn('board_meas_off()',commit)
    def test_f05_rate_range_counters_and_window(self):
        k=(R/'firmware/main/Kconfig.projbuild').read_text(encoding='utf-8')
        self.assertRegex(k,r'config EGR_SAMPLE_HZ\r?\n(?:.*\n){0,2}\s*range 1000 10000')
        self.assertIn('#define CURRENT_WINDOW_N 256',src('measure.h'));self.assertIn('daq_stats',src('app_main.c'))
    def test_f06_logger_current_chain_in_config(self):
        j=src('jsonlog.c');self.assertIn('P06R2 WSK2512 5mOhm INA240A2 G50 div1:2',j);self.assertIn('current_chain',j)
    def test_f07_p09_patch_applied(self):
        ref=(R.parents[1]/'Plytki/P09-R1-review/firmware/board.c').read_text(encoding='utf-8')
        mine=body(src('board.c'),'esp_err_t board_temperature(').replace('\r','')
        self.assertEqual(mine,body(ref,'esp_err_t board_temperature(').replace('\r',''))
        self.assertIn('.cs_ena_pretrans = 2, .cs_ena_posttrans = 2',src('board.c'))
    def test_f08_can_has_own_task_and_soft_events(self):
        app=src('app_main.c');aux=body(app,'static void auxiliary(');can=body(app,'static void can_rx(')
        self.assertNotIn('twai_receive',aux);self.assertIn('twai_receive',can);self.assertIn('storage_event_soft',can)
        self.assertIn('rx_overrun_count',can);self.assertIn('obd_rpm_frame',can);self.assertIn('TWAI_MODE_LISTEN_ONLY',src('board.c'))
        self.assertIn('"obd.c"',(R/'firmware/main/CMakeLists.txt').read_text(encoding='utf-8'))
    def test_f09_profile_s1_revisions_without_calibration_change(self):
        new=json.loads((R/'profiles/hardware.json').read_text(encoding='utf-8'));old=json.loads((HW/'profiles/hardware.json').read_text(encoding='utf-8'))
        want={'P02':'R4','P03':'R6','P05':'R3','P06':'R2','P09':'R2','P10':'R2'}
        for k,rev in want.items():self.assertEqual((new['modules'][k]['hardware_revision'],new['modules'][k]['interface']),(rev,'S1'))
        self.assertEqual(new['schema'],6)
        for key in old:
            if key!='modules':self.assertEqual(new[key],old[key],key)   # kalibracja i tozsamosci bez zmian
        for k in old['modules']:self.assertEqual(new['modules'][k]['serial'],old['modules'][k]['serial'])
    def test_version(self):
        self.assertIn('set(PROJECT_VER "6.2-s1")',(R/'firmware/CMakeLists.txt').read_text(encoding='utf-8'))
        self.assertIn('EGRLab-6.2-s1',src('storage.c'))
if __name__=='__main__':unittest.main()

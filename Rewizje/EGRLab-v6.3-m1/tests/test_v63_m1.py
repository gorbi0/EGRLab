"""6.3-m1: statyczne kontrole zmian M-01...M-13 z Plytki/M1-specyfikacja/zadania/ZADANIE-M1-KROK8-FIRMWARE.md.
Zrodla prawdy o sprzecie: Plytki/M1-R1-review/docs/GPIO.csv (mapa GPIO z netlisty) i docs/parts.json (wartosci czesci).
Kontrole czytaja zrodla tej rewizji; nie zastepuja odbioru na sprzecie (README, "Odbior na sprzecie")."""
import csv,json,re,sys,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];M=R/'firmware/main';HWM1=R.parents[1]/'Plytki/M1-R1-review/docs'
sys.path.insert(0,str(R/'tools'))
import profile_v6
def src(name):return (M/name).read_text(encoding='utf-8').replace('\r','')
def code(name):
    """Zrodlo bez komentarzy i literalow tekstowych - do sprawdzania, ze cos NIE wystepuje w kodzie."""
    t=re.sub(r'/\*.*?\*/','',src(name),flags=re.S);t=re.sub(r'//[^\n]*','',t)
    return re.sub(r'"(?:\\.|[^"\\])*"','""',t)
def body(text,signature):
    start=text.index(signature);i=text.index('{',start)+1;depth=1
    while depth:depth+=(text[i]=='{')-(text[i]=='}');i+=1
    return text[start:i]
def gpio_csv():
    with (HWM1/'GPIO.csv').open(encoding='utf-8-sig',newline='') as f:return {int(r['gpio']):r['siec'] for r in csv.DictReader(f,delimiter=';')}
def parts():return json.loads((HWM1/'parts.json').read_text(encoding='utf-8-sig'))
def board_enum():
    return {k:int(v) for k,v in re.findall(r'(GPIO_[A-Z0-9_]+)\s*=\s*(\d+)',src('board.h'))}
# Siec z GPIO.csv -> nazwa w board.h. GPIO17 (TWAI TX) i GPIO38 (dioda RGB modulu) sa w netliscie NC - patrz testy.
NET={'RPWM':'GPIO_RPWM','LPWM':'GPIO_LPWM','DRIVE_EN':'GPIO_DRIVE_EN','SENS_EN':'GPIO_SENS_EN','SENS_FAULT_N':'GPIO_SENS_FAULT_N',
     'ADC_SDI':'GPIO_ADC_SDI','ADC_SCLK':'GPIO_ADC_SCLK','ADC_DOUTA':'GPIO_ADC_DOUTA','ADC_CS':'GPIO_ADC_CS','ADC_RESET':'GPIO_ADC_RESET',
     'ADC_CONVST':'GPIO_ADC_CONVST','ADC_BUSY':'GPIO_ADC_BUSY','SPI3_SCK':'GPIO_SPI3_SCK','SPI3_MOSI':'GPIO_SPI3_MOSI',
     'SPI3_MISO':'GPIO_SPI3_MISO','SD_CS':'GPIO_SD_CS','TC1_CS':'GPIO_TC1_CS','TC2_CS':'GPIO_TC2_CS','CAN_RXD':'GPIO_CAN_RX',
     'BTN':'GPIO_BTN','SCOPE_TRIG':'GPIO_SCOPE','GPIO3_TP':'GPIO_TP3'}
FORBIDDEN={0,45,46,19,20,33,34,35,36,37,43,44,47,48}   # SPECYFIKACJA M1 sekcja 3 (jak P03 R6)

class M1Firmware(unittest.TestCase):
    def test_m01_removed_hardware_has_no_code(self):
        for name in sorted(p.name for p in M.glob('*.[ch]')):
            c=code(name)
            for word in ['mcp_write','mcp_read','i2c_param_config','i2c_driver_install','porta_set','current_adc','current_read',
                         'PFAIL_N','board_pfail_init','board_pfail_level','power_fail','A_MEAS_EN','A_MEAS_BANK','board_meas_off',
                         'board_interlock','board_armed','B_TEST_PRESENT','log_present','test_present','hw_armed','HEART','CURRENT_CS']:
                self.assertIsNone(re.search(r'\b'+word+r'\b',c),(name,word))   # slowo, nie fragment (current_adc_gain zostaje w profilu)
        k=(M/'Kconfig.projbuild').read_text(encoding='utf-8')
        for opt in ['EGR_PFAIL_PRESENT','EGR_LOG_CURRENT_PRESENT','EGR_TEST_CURRENT_PRESENT']:self.assertNotIn(opt,k)
        for f in (R/'firmware').glob('sdkconfig.*.defaults'):self.assertNotIn('CURRENT_PRESENT',f.read_text(encoding='utf-8'),f.name)
    def test_m01_gpio_map_matches_netlist(self):
        net=gpio_csv();enum=board_enum()
        used={NET[n]:g for g,n in net.items() if n in NET}
        self.assertEqual(len(used),len(NET),set(NET)-set(net.values()))   # kazda siec z tabeli jest w netliscie
        for name,g in used.items():self.assertEqual(enum.get(name),g,name)
        # Wszystko z board.h, co nie jest w netliscie: tylko TWAI TX (niepodlaczony, M-09) i dioda modulu (M-12).
        extra={k:v for k,v in enum.items() if k not in used}
        self.assertEqual(extra,{'GPIO_CAN_TX':17,'GPIO_LED_RGB':38})
        self.assertEqual((net[17],net[38]),('NC','NC'))
        self.assertFalse(FORBIDDEN & set(enum.values()))
        self.assertEqual(len(set(enum.values())),len(enum))                # zadnego pinu dwa razy
    def test_m01_peripherals_use_named_pins(self):
        b=src('board.c')
        for frag in ['.mosi_io_num = GPIO_ADC_SDI, .miso_io_num = GPIO_ADC_DOUTA, .sclk_io_num = GPIO_ADC_SCLK',
                     '.spics_io_num = GPIO_ADC_CS','.mosi_io_num = GPIO_SPI3_MOSI, .miso_io_num = GPIO_SPI3_MISO, .sclk_io_num = GPIO_SPI3_SCK',
                     '.spics_io_num = i ? GPIO_TC2_CS : GPIO_TC1_CS','slot.gpio_cs = GPIO_SD_CS',
                     'TWAI_GENERAL_CONFIG_DEFAULT(GPIO_CAN_TX, GPIO_CAN_RX, TWAI_MODE_LISTEN_ONLY)',
                     '.gpio_num = GPIO_RPWM','.gpio_num = GPIO_LPWM','.gpio_num = GPIO_LED_RGB']:self.assertIn(frag,b)
        self.assertNotRegex(code('board.c'),r'gpio_(set|get)_level\(\s*\d')                    # bez golych numerow
    def test_m02_adc_reset_from_gpio10_and_startup_times(self):
        b=src('board.c');init=body(b,'esp_err_t board_init(')
        self.assertRegex(init,r'vTaskDelay\(pdMS_TO_TICKS\(10\)\);\s*adc_reset_pulse\(\); vTaskDelay\(pdMS_TO_TICKS\(2100\)\);')
        pulse=body(b,'static void adc_reset_pulse(')
        self.assertRegex(pulse,r'gpio_set_level\(GPIO_ADC_RESET, 1\); esp_rom_delay_us\(20\); gpio_set_level\(GPIO_ADC_RESET, 0\);')
        self.assertIn('vTaskDelay(pdMS_TO_TICKS(2100));',body(b,'static esp_err_t adc_full_reset('))
        self.assertIn('adc_reset_needed = true',body(b,'esp_err_t board_adc('))
        self.assertIn('GPIO_ADC_RESET',init[:init.index('gpio_config(&out)')])                     # nisko przed wyjsciem
        self.assertEqual(parts()['R9']['pins'],{'1':'ADC_RESET','2':'GND'})
        commit=body(src('app_main.c'),'static bool commit_locked(')
        self.assertLess(commit.index('board_adc_ranges('),commit.index('board_mode(ctrl.test_bank,ctrl.sensor_on)'))
        u=parts()['U3']['pins'];self.assertEqual((u['11'],u['13'],u['14'],u['9'],u['12'],u['29']),
            ('ADC_RESET','ADC_CS','ADC_BUSY','ADC_CONVST','ADC_SCLK','ADC_SDI'))
        self.assertIn('ADC_OVERSAMPLE_X8 0x03',b);self.assertIn('default y',re.search(r'config EGR_ADC_SOFTWARE_MODE[\s\S]*?help',src('Kconfig.projbuild')).group(0))
    def test_m03_m04_channel_scales_from_parts(self):
        p=parts();rin=5e6;par=lambda a,b:a*b/(a+b);val=lambda r:float(p[r]['value'].upper().replace('K','e3').replace('R',''))
        def chain(series,bottom=None):
            low=par(val(bottom),rin) if bottom else rin
            return (val(series)+low)/low
        want=[chain('R11','R12'),chain('R13','R14'),chain('R15'),chain('R16'),chain('R17'),chain('R21'),chain('R18','R19'),chain('R20')]
        nets=[('R11','P1_EGR','ADC_CH1'),('R13','P3','ADC_CH2'),('R15','P4','ADC_CH3'),('R16','P5','ADC_CH4'),('R17','P6','ADC_CH5'),
              ('R21','I_MOT','ADC_CH6'),('R18','VBAT_CAR','ADC_CH7'),('R20','SENS_5V','ADC_CH8')]
        for r,a,b in nets:self.assertEqual(p[r]['pins'],{'1':a,'2':b},r)
        for c,ch,v in [('C16','ADC_CH1','220p'),('C17','ADC_CH2','220p'),('C18','ADC_CH3','220p'),('C19','ADC_CH4','220p'),
                       ('C20','ADC_CH5','220p'),('C21','ADC_CH7','220p'),('C22','ADC_CH8','220p'),('C23','ADC_CH6','1n')]:
            self.assertEqual((p[c]['pins']['1'],p[c]['value']),(ch,v),c)
        nominal=[float(x.rstrip('f')) for x in re.search(r'const float nominal\[8\] = \{([^}]*)\}',src('control.c')).group(1).split(',')]
        for j,(n,w) in enumerate(zip(nominal,want)):self.assertAlmostEqual(n,w,delta=5e-4*w,msg=f'CH{j+1}')
        # M-04: INA240A2 (x50) na boczniku 5 mOhm -> 0,25 V/A; zero VS/2 mierzone, nie stala.
        self.assertEqual(p['U4']['value'],'INA240A2');self.assertTrue(p['RSH1']['value'].startswith('5m'))
        self.assertEqual((p['U4']['pins']['5'],p['U4']['pins']['6'],p['U4']['pins']['7']),('I_MOT','5V','5V'))   # OUT, VS, REF1
        self.assertEqual(p['U4']['pins']['3'],'GND')                                                             # REF2
        self.assertAlmostEqual(0.005*50,float(re.search(r'current_volts_per_amp\[bank\] = ([.\d]+)f',src('control.c')).group(1)))
        meta=src('storage.c')
        for frag in ['CH1 P1_EGR 300k/100k','CH6 I_MOT INA240A2 x50 5mOhm VS/2+0.25V/A 1k/1n','CH7 499k/100k: LOGGER akumulator auta (X1.13), TEST VMOTOR','CH8 SENS_5V 100k',
                     'input_impedance_ohm','filter_pf']:self.assertIn(frag,meta)
    def test_m04_current_sampled_with_voltages(self):
        acq=body(src('app_main.c'),'static void acquisition(')
        self.assertIn('board_adc(raw,&sample_time)',acq);self.assertNotIn('cur.',acq)
        self.assertIn('s.current_raw=65535',acq);self.assertIn('s.current_status=2',acq)
        self.assertIn('current_window_add(&window,s.t_us,amps',acq)
        self.assertIn('out->local_current = false',src('control.c'))
        self.assertIn('CHAIN_M1',src('jsonlog.c'));self.assertIn('\\"synchronous\\":true',src('jsonlog.c'))
        zero=body(src('app_main.c'),'static bool zero_locked(')
        self.assertIn('control_zero_ok(s.mean,s.min,s.max)',zero);self.assertIn('board_inhibit(true)',zero)
        self.assertIn('ctrl.profile.current_zero[bank]=s.mean[5]',zero)
        self.assertIn('p->range[CH_CURRENT] = RANGE_5V',src('control.c'))
    def test_m05_bridge_pins_pwm_and_safe_start(self):
        k=src('Kconfig.projbuild');self.assertRegex(k,r'config EGR_PWM_HZ[\s\S]*?range 100 25000')
        b=src('board.c');init=body(b,'esp_err_t board_init(')
        self.assertIn('.freq_hz = CONFIG_EGR_PWM_HZ',init)
        low=init[:init.index('gpio_config(&out)')]
        for pin in ['GPIO_DRIVE_EN','GPIO_SENS_EN','GPIO_RPWM','GPIO_LPWM']:self.assertIn(pin,low)
        self.assertLess(init.index('gpio_config(&out)'),init.index('ledc_channel_config(&lr)'))
        after=init[init.index('gpio_config(&out)'):]   # po wlaczeniu wyjsc: ponownie nisko, nigdzie wysoko w board_init
        self.assertIn('for (unsigned k = 0; k < sizeof low / sizeof low[0]; k++) gpio_set_level(low[k], 0);',after)
        self.assertNotRegex(init,r'gpio_set_level\(GPIO_(DRIVE_EN|SENS_EN|RPWM|LPWM), *1\)')
        kill=body(b,'void board_kill(');self.assertLess(kill.index('GPIO_DRIVE_EN, 0'),kill.index('pwm_set(0, 0)'))
        drive=body(b,'void board_drive(');self.assertIn('reverse_until = now + 5000',drive)
        self.assertIn('pwm_set(current_sign > 0 ? d : 0, current_sign < 0 ? d : 0)',drive);self.assertIn('fminf(fabsf(duty), .9f)',drive)
        p=parts()
        # R2 4,7 k (GPIO39 = MTCK: wewnetrzne podciaganie ok. 45 k po resecie, karta ESP32-S3 v2.2 tab. 2-1 przyp. 7), reszta 100 k
        for r,net,val in [('R2','DRIVE_EN','4.7K'),('R3','RPWM','100K'),('R4','LPWM','100K'),('R5','SENS_EN','100K')]:
            self.assertEqual((p[r]['value'],p[r]['pins']),(val,{'1':net,'2':'GND'}),r)
        u=p['U7']['pins'];self.assertEqual((u['2'],u['5'],u['9'],u['12']),('RPWM','LPWM','DRIVE_EN','DRIVE_EN'))
        self.assertEqual((u['3'],u['6'],u['8'],u['11']),('IBT_RPWM','IBT_LPWM','IBT_REN','IBT_LEN'))
    def test_m06_software_current_limit_and_watchdogs(self):
        k=src('Kconfig.projbuild')
        self.assertRegex(k,r'config EGR_SW_CURRENT_LIMIT\n\s*bool[^\n]*\n\s*default y')
        self.assertRegex(k,r'config EGR_SW_CURRENT_LIMIT_MA[\s\S]*?range 1000 9000\n\s*default 8000')
        acq=body(src('app_main.c'),'static void acquisition(')
        self.assertLess(acq.index('overcurrent_sample('),acq.index('trigger_sample('))
        self.assertLess(acq.index('overcurrent_sample('),acq.index('storage_push('))
        self.assertIn('board_overcurrent_trip()',acq);self.assertIn('#if CONFIG_EGR_SW_CURRENT_LIMIT',acq)
        self.assertIn('if (!in->drive_ok)     { fail(c, "OVERCURRENT"); return; }',src('control.c'))
        safety=body(src('app_main.c'),'static void safety(')
        self.assertLess(safety.index('board_watchdogs_start()'),safety.index('while(true)'))
        # 6.3.1-m1 (recenzja M1-08): karmienie po ocenie sterowania i granicy czasu, tylko przy postepie albo bez napedu;
        # zachowanie sprawdza probe_review_m1.py (rzeczywista petla safety), tu tylko kolejnosc w zrodle
        loop=safety[safety.index('while(true)'):];self.assertLess(loop.index('control_step('),loop.index('board_watchdogs_feed()'))
        self.assertIn('if(evaluated || !run_permission) board_watchdogs_feed();',loop)
        self.assertLess(loop.index('CONTROL_STALE_US'),loop.index('board_watchdogs_feed()'))
        b=src('board.c');wrap=body(b,'void IRAM_ATTR __wrap_esp_panic_handler(')
        self.assertLess(wrap.index('GPIO_DRIVE_EN, 0'),wrap.index('__real_esp_panic_handler(info)'))
        self.assertIn('GPIO_SENS_EN, 0',wrap)
        self.assertIn('-Wl,--wrap=esp_panic_handler',(M/'CMakeLists.txt').read_text(encoding='utf-8'))
        st=body(b,'esp_err_t board_watchdogs_start(')
        self.assertIn('.trigger_panic = true',st);self.assertIn('WDT_STAGE_ACTION_RESET_SYSTEM',st)
        self.assertIn('esp_register_shutdown_handler(board_shutdown)',b)
    def test_m07_sensor_supply_only_in_test(self):
        b=src('board.c');mode=body(b,'esp_err_t board_mode(')
        self.assertLess(mode.index('if (sensor && !test)'),mode.index('GPIO_SENS_EN, 1'))
        safety=body(src('app_main.c'),'static void safety(')
        self.assertIn('if(!ctrl.test_bank && board_sensor_enabled()) board_sensor_off();',safety)
        ex=body(src('app_main.c'),'static bool execute_locked(')
        self.assertLess(ex.index('control_test_wiring(&in)'),ex.index('control_command(&ctrl,cmd'))
        self.assertIn('sens5v_ok(c, in)',body(src('control.c'),'static bool sensor_valid('))
        p=parts();u=p['U8'];self.assertEqual((u['pins']['3'],u['pins']['4'],u['pins']['6']),('SENS_EN','SENS_FAULT_N','SENS_5V'))
        self.assertEqual(p['R32']['pins'],{'1':'SENS_FAULT_N','2':'3V3'})
        self.assertIn('return !gpio_get_level(GPIO_SENS_FAULT_N)',b)
    def test_m08_f07_max31856_patch_and_direct_cs(self):
        ref=(R/'tests/fixtures/P09-R1-board.c').read_text(encoding='utf-8')   # M1-07: fixture
        mine=body(src('board.c'),'esp_err_t board_temperature(')
        self.assertEqual(mine,body(ref,'esp_err_t board_temperature(').replace('\r',''))
        self.assertIn('.cs_ena_pretrans = 2, .cs_ena_posttrans = 2',src('board.c'))
        self.assertNotIn('HC139',code('board.c'))
    def test_m09_can_listen_only_rx18(self):
        self.assertEqual(board_enum()['GPIO_CAN_RX'],18);self.assertIn('TWAI_MODE_LISTEN_ONLY',src('board.c'))
        can=body(src('app_main.c'),'static void can_rx(');self.assertIn('storage_event_soft',can);self.assertIn('twai_receive',can)
        u=parts()['U6']['pins'];self.assertEqual((u['1'],u['8'],u['4']),('3V3','3V3','CAN_RX_U'))   # TXD i S na 3V3
    def test_m10_no_power_fail_path_and_sync_period(self):
        self.assertNotIn('storage_power_fail',code('storage.c')+code('storage.h')+code('app_main.c'))
        self.assertIn('\\"power_fail\\":{\\"input\\":null',src('storage.c'))
        self.assertRegex(src('Kconfig.projbuild'),r'config EGR_SD_SYNC_MS\n[^\n]*\n\s*range 250 2000\n\s*default 1000\n')
        self.assertIn('(uint64_t)CONFIG_EGR_SD_SYNC_MS * 1000',body(src('storage.c'),'void storage_writer('))
        self.assertIn('fsync',(R/'docs/04-firmware-logi.md').read_text(encoding='utf-8'))
    def test_m11_missing_sd_or_adc_does_not_hang(self):
        app=body(src('app_main.c'),'void app_main(')
        self.assertNotRegex(app,r'ESP_ERROR_CHECK\((board_sd_mount\(\)|sd)\)');self.assertIn('bench_mode=sd!=ESP_OK',app)
        self.assertIn('storage_init_bench(',app);self.assertIn('if(!bench_mode) { session++;',app)
        self.assertIn('if(bench_mode && !strcmp(cmd,"test")) return false;',src('app_main.c'))
        acq=body(src('app_main.c'),'static void acquisition(');self.assertIn('if(!adc_failing) storage_event(',acq)
        self.assertIn('adc_reset_needed = true;      /* M-11',body(src('board.c'),'esp_err_t board_adc_ranges('))
    def test_m12_button_led_scope(self):
        e=board_enum();self.assertEqual((e['GPIO_BTN'],e['GPIO_LED_RGB'],e['GPIO_SCOPE']),(15,38,41))
        b=src('board.c');self.assertIn('rmt_new_bytes_encoder',b);self.assertIn('return !gpio_get_level(GPIO_BTN)',b)
        btn=body(src('app_main.c'),'static void button_tick(')
        self.assertLess(btn.index('if(test_states)'),btn.index('request_stop()'))   # w TEST nacisniecie = STOP od razu
        self.assertIn('now-changed>=20000',btn)
        p=parts();self.assertEqual((p['R6']['pins'],p['C4']['value']),({'1':'BTN','2':'3V3'},'100n'))
    def test_m13_profile_m1(self):
        hw,valve,session=[json.loads((R/'profiles'/f'{x}.json').read_text(encoding='utf-8')) for x in ['hardware','valve','session']]
        self.assertEqual((hw['schema'],hw['configuration'],hw['configuration_version']),(7,'M1-R1',1))
        self.assertEqual(hw['current_driver'],'ad7606b_ch6_ina240');self.assertNotIn('aux',hw)
        old=json.loads((R/'tests/fixtures/v6.2-s1-hardware.json').read_text(encoding='utf-8'))   # M1-07: fixture
        self.assertEqual(hw['daq_module'],old['daq_module'])                                   # tozsamosci jak w 6.2-s1
        self.assertEqual(hw['current'][0]['module_id'],old['current'][0]['module_id'])
        self.assertEqual(hw['current'][1]['module_id'],hw['current'][0]['module_id'])          # D-M1-7: jeden tor
        self.assertEqual(hw['temperature']['probes'],old['temperature']['probes'])
        self.assertEqual(hw['modules']['IBT2']['serial'],old['modules']['P07']['serial'])
        with self.assertRaises(ValueError):profile_v6.commands(hw,valve,session)                 # szablon nie uruchamia sprzetu
        for v in hw['voltage']:v.update(accepted=True,gain=[1]*8,offset=[0]*8)
        for c in hw['current']:c.update(accepted=True,volts_per_amp=.25,zero=2.5)
        out=profile_v6.commands(hw,valve,session);first={l.split()[0] for l in out.splitlines()}
        self.assertTrue({'auxcal','iscal','qualify','test','arm'}.isdisjoint(first));self.assertIn('ivpa',first)
        self.assertLess(out.index('cal 1 7'),out.index('vcalok 0'))
        hw['current'][1]['module_id']='OTHER_01'
        with self.assertRaises(ValueError):profile_v6.commands(hw,valve,session)
        h=src('control.h');self.assertIn('EGR_PROFILE_VERSION 7',h)
        app=src('app_main.c');self.assertEqual(app.count('"profile_m1"'),2);self.assertNotIn('"profile5"',app)
        self.assertIn('#define EGR_HARDWARE_ACCEPTED 0',src('commissioning.h'))
    def test_version(self):
        self.assertIn('set(PROJECT_VER "6.3.1-m1")',(R/'firmware/CMakeLists.txt').read_text(encoding='utf-8'))
        self.assertIn('EGRLab-6.3.1-m1',src('storage.c'));self.assertIn('\\"firmware\\":\\"6.3.1-m1\\"',src('jsonlog.c'))
        self.assertNotIn('6.2-s1"',code('app_main.c'))
if __name__=='__main__':unittest.main()

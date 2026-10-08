"""6.3-m1: proby mutacyjne nowych kontroli (tests/test_v63_m1.py, tests/test_control.c, tests/test_runtime.c,
tests/probe_drive.py) - kopia rewizji z jedna celowa wada; kazda musi oblac co najmniej jedna kontrole. Proba zerowa
(kopia bez zmian) musi przejsc wszystkie.
python tests/probe_v63_mutations.py --cc gcc  (wynik: verification/v63-mutations.json)"""
import argparse,json,shutil,subprocess,sys,tempfile
from pathlib import Path
R=Path(__file__).resolve().parents[1]
MUT=[  # (nazwa, plik wzgledem R, stary tekst, nowy tekst)
 ('m01_mcp_back','firmware/main/board.c','static void board_shutdown(void)','static int mcp_write(int r,int v){(void)r;(void)v;return 0;}\nstatic void board_shutdown(void)'),
 ('m01_gpio_lpwm_wrong','firmware/main/board.h','GPIO_LPWM = 21','GPIO_LPWM = 38'),
 ('m01_forbidden_pin','firmware/main/board.h','GPIO_SENS_FAULT_N = 42','GPIO_SENS_FAULT_N = 47'),
 ('m02_reset_wait_10ms','firmware/main/board.c','adc_reset_pulse(); vTaskDelay(pdMS_TO_TICKS(2100));','adc_reset_pulse(); vTaskDelay(pdMS_TO_TICKS(10));'),
 ('m02_reset_pulse_short','firmware/main/board.c','gpio_set_level(GPIO_ADC_RESET, 1); esp_rom_delay_us(20);','gpio_set_level(GPIO_ADC_RESET, 1); esp_rom_delay_us(1);'),
 ('m03_vbat_gain','firmware/main/control.c','1.0002f, 6.0898f, 1.02f}','1.0002f, 6.0f, 1.02f}'),
 ('m03_sens5v_gain_aux','firmware/main/control.c','1.0002f, 6.0898f, 1.02f}','1.0002f, 6.0898f, 4.06f}'),
 ('m04_current_from_mcp','firmware/main/control.c','out->local_current = false;','out->local_current = true;'),
 ('m04_zero_ignores_motor','firmware/main/control.c','fabsf(min[j]) > .5f || fabsf(max[j]) > .5f) return false;','fabsf(min[j]) > 50 || fabsf(max[j]) > 50) return false;'),
 ('m05_both_pwm','firmware/main/board.c','pwm_set(current_sign > 0 ? d : 0, current_sign < 0 ? d : 0);','pwm_set(d, current_sign < 0 ? d : 0);'),
 ('m05_no_reverse_gap','firmware/main/board.c','board_kill(); current_sign = sign; reverse_until = now + 5000;','board_kill(); current_sign = sign; reverse_until = now;'),
 ('m05_en_before_low','firmware/main/board.c','    gpio_config_t out = {.pin_bit_mask = mask, .mode = GPIO_MODE_OUTPUT};\n    ESP_ERROR_CHECK(gpio_config(&out));\n    for (unsigned k = 0; k < sizeof low / sizeof low[0]; k++) gpio_set_level(low[k], 0);',
  '    gpio_config_t out = {.pin_bit_mask = mask, .mode = GPIO_MODE_OUTPUT};\n    ESP_ERROR_CHECK(gpio_config(&out));\n    gpio_set_level(GPIO_DRIVE_EN, 1);'),
 ('m05_pwm_over_25k','firmware/main/Kconfig.projbuild','range 100 25000','range 100 40000'),
 ('m06_limit_off_default','firmware/main/Kconfig.projbuild','bool "Programowe ograniczenie pradu silnika z CH6 (M-06, do potwierdzenia)"\n    default y','bool "Programowe ograniczenie pradu silnika z CH6 (M-06, do potwierdzenia)"\n    default n'),
 ('m06_trip_ignored','firmware/main/control.c','if (!in->drive_ok)     { fail(c, "OVERCURRENT"); return; }','(void)0;'),
 ('m06_latch_cleared','firmware/main/board.c','void board_overcurrent_trip(void) { drive_ok = false; board_emergency_stop(); }','void board_overcurrent_trip(void) { board_emergency_stop(); }'),
 ('m06_single_sample_nan_ok','firmware/main/measure.c','    if (isfinite(amps) && fabsf(amps) <= limit_a) { o->over = 0; return false; }','    if (!isfinite(amps) || fabsf(amps) <= limit_a) { o->over = 0; return false; }'),
 ('m06_panic_wrap_removed','firmware/main/CMakeLists.txt','target_link_libraries(${COMPONENT_LIB} INTERFACE "-Wl,--wrap=esp_panic_handler")','# brak'),
 ('m06_no_feed','firmware/main/app_main.c','        if(evaluated || !run_permission) board_watchdogs_feed();\n','\n'),
 ('m07_sensor_in_logger','firmware/main/board.c','    if (sensor && !test) { board_sensor_off(); return ESP_ERR_INVALID_STATE; }\n','\n'),
 ('m07_wiring_skips_sensor','firmware/main/control.c','if (fabsf(in->v[j]) > .5f) return "SENSOR_LINES_LIVE";','if (fabsf(in->v[j]) > 50) return "SENSOR_LINES_LIVE";'),
 ('m07_sens5v_not_checked','firmware/main/control.c','(!in->sensor_fault && sens5v_ok(c, in))','(!in->sensor_fault)'),
 # 6.3.1-m1: cofniecie kazdej poprawki z recenzji M1-R1 musi wykryc tests/probe_review_m1.py (w run_host.py)
 ('r_m102_test_supply_16v5','firmware/main/control.c','in->v[CH_VBAT] > 17.3f','in->v[CH_VBAT] > 16.5f'),
 ('r_m103_release_ignores_wdt','firmware/main/board.c','bool ok=token==gate_epoch && watchdogs_ok;','bool ok=token==gate_epoch;'),
 ('r_m108_no_stale_stop','firmware/main/app_main.c','if(run_permission && !evaluated && i.now-last_eval>CONTROL_STALE_US) {','if(false) {'),
 ('r_m108_button_skipped','firmware/main/app_main.c','        button_tick(i.now,(state_t)shown_state);\n','\n'),
 ('r_m109_snapshot_validity','firmware/main/app_main.c','bool cfg_ok=c.adc_config_ok && board_adc_config_ok();','bool cfg_ok=c.adc_config_ok;'),
 ('r_m110_mcp3201_overwrite','tools/egrlog.py',"if len(record)==16 and cfg.get('local_current') is True:","if len(record)==16:"),
 ('r_m111_ch6_cal_keeps_current','firmware/main/profile.c','if (j==5) {n.current_calibrated[b]=false;n.current_window_qualified=false;}','(void)j;'),
 ('r_m112_nan_ref','firmware/main/trigger.c','if (fire(0, isfinite(ref) && !(ref','if (fire(0, !(ref'),
 ('m07_test_without_wiring_check','firmware/main/app_main.c','const char *why=control_test_wiring(&in);','const char *why=NULL; (void)in;'),
 ('m10_sync_2s','firmware/main/Kconfig.projbuild','range 250 2000\n    default 1000','range 250 2000\n    default 2000'),
 ('m11_sd_required','firmware/main/app_main.c','esp_err_t sd=board_sd_mount(); bench_mode=sd!=ESP_OK;','esp_err_t sd=board_sd_mount(); ESP_ERROR_CHECK(sd); bench_mode=sd!=ESP_OK;'),
 ('m11_bench_allows_test','firmware/main/app_main.c','    if(bench_mode && !strcmp(cmd,"test")) return false;','    (void)bench_mode;'),
 ('m12_button_no_stop_in_test','firmware/main/app_main.c','                long_done=true; request_stop();','                long_done=true;'),
 ('m13_profile_v6','firmware/main/control.h','#define EGR_PROFILE_VERSION 7','#define EGR_PROFILE_VERSION 6'),
 ('m13_auxcal_back','firmware/main/profile.c','    else if (!strcmp(cmd,"limits")','    else if (!strcmp(cmd,"auxcal") && sscanf(line,"%*s %d %f %f %c",&b,&a,&z,&extra)==3 && b>=0 && b<2) { n.aux_gain[b]=a; n.aux_offset[b]=z; }\n    else if (!strcmp(cmd,"limits")'),
 ('m13_identity_bank1','profiles/hardware.json','"module_id": "IL_001",\r\n      "accepted": false,\r\n      "volts_per_amp": null,\r\n      "zero": null,\r\n      "calibration_date": null\r\n    }\r\n  ]','"module_id": "DR_001",\r\n      "accepted": false,\r\n      "volts_per_amp": null,\r\n      "zero": null,\r\n      "calibration_date": null\r\n    }\r\n  ]'),
]
def check(copy,cc):
    """Wszystkie kontrole, ktore moga zlapac mutacje: unittest test_v63_m1 i testy hosta C (run_host.py)."""
    fails=[]
    r=subprocess.run([sys.executable,'-m','unittest','test_v63_m1'],cwd=copy/'tests',capture_output=True,text=True)
    if r.returncode:fails+=[l for l in r.stderr.splitlines() if l.startswith(('FAIL:','ERROR:'))] or ['unittest']
    r=subprocess.run([sys.executable,str(copy/'tests/run_host.py'),'--cc',cc],cwd=copy,capture_output=True,text=True)
    if r.returncode:fails.append('run_host: '+(r.stdout+r.stderr).strip().splitlines()[-1][:120] if (r.stdout+r.stderr).strip() else 'run_host')
    return fails
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cc',default='gcc');a=p.parse_args()
    results=[]
    with tempfile.TemporaryDirectory() as t:
        base=Path(t);(base/'Rewizje').mkdir()
        for name in ['EGRLab-v6.1-rc1','EGRLab-v6.2-s1']:(base/'Rewizje'/name).symlink_to(R.parent/name)
        (base/'Plytki').symlink_to(R.parents[1]/'Plytki')
        for name,rel,old,new in [('zerowa',None,None,None)]+MUT:
            copy=base/'Rewizje/EGRLab-v6.3-m1'
            if copy.exists():shutil.rmtree(copy)
            shutil.copytree(R,copy,ignore=shutil.ignore_patterns('verification','__pycache__','*.exe','build-*','sdkconfig.core','sdkconfig.logger','sdkconfig.minimal','sdkconfig.test','sdkconfig.wifi','prebuilt'))
            shutil.copytree(R/'verification/host-tcc-include',copy/'verification/host-tcc-include')
            if rel:
                f=copy/rel;s=f.read_bytes().decode('utf-8')
                for eol in ['\n','\r\n']:   # wzorce pisane z LF albo CRLF; plik moze miec dowolne
                    if s.count(old)!=1:old,new=old.replace('\r\n','\n').replace('\n',eol),new.replace('\r\n','\n').replace('\n',eol)
                assert s.count(old)==1,(name,s.count(old));f.write_bytes(s.replace(old,new).encode('utf-8'))
            fails=check(copy,a.cc);ok=not fails if rel is None else bool(fails)
            results.append({'mutation':name,'detected' if rel else 'clean':ok,'failed':fails[:4]});print('OK ' if ok else 'ZLE',name,fails[:2])
    (R/'verification').mkdir(exist_ok=True)
    (R/'verification/v63-mutations.json').write_text(json.dumps(results,indent=1,ensure_ascii=False)+'\n',encoding='utf-8')
    good=sum(1 for x in results if x.get('detected',x.get('clean')));print(f'{good}/{len(results)} (z proba zerowa)');sys.exit(0 if good==len(results) else 1)

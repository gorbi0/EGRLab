"""6.2-s1: proby mutacyjne kontroli tests/test_v62_s1.py - kopia rewizji z jedna celowa wada; kazda musi oblac test.
python tests/probe_v62_mutations.py  (wynik: verification/v62-mutations.json)"""
import json,shutil,subprocess,sys,tempfile
from pathlib import Path
R=Path(__file__).resolve().parents[1]
MUT=[  # (nazwa, plik wzgledem R, stary tekst, nowy tekst)
 ('d3_order_swapped','firmware/main/app_main.c','        board_power_fail_stop(); power_failed=true;','        storage_power_fail(0,0); board_power_fail_stop(); power_failed=true;'),
 ('pfail_internal_pulldown','firmware/main/board.c','.pull_down_en = GPIO_PULLDOWN_DISABLE','.pull_down_en = GPIO_PULLDOWN_ENABLE'),
 ('adc_reset_wait_10ms','firmware/main/board.c','ESP_ERROR_CHECK(porta_set(A_ADC_RESET, false)); vTaskDelay(pdMS_TO_TICKS(2100));','ESP_ERROR_CHECK(porta_set(A_ADC_RESET, false)); vTaskDelay(pdMS_TO_TICKS(10));'),
 ('meas_en_before_adc_config','firmware/main/app_main.c','    bool adc_ok=board_adc_ranges(ctrl.profile.range,applied)==ESP_OK && board_adc_config_ok();\r\n    bool ok=adc_ok && board_mode(ctrl.test_bank,ctrl.sensor_on)==ESP_OK;',
  '    bool ok=board_mode(ctrl.test_bank,ctrl.sensor_on)==ESP_OK;\r\n    bool adc_ok=board_adc_ranges(ctrl.profile.range,applied)==ESP_OK && board_adc_config_ok();\r\n    ok=ok && adc_ok;'),
 ('relay_wait_removed','firmware/main/board.c','        if (e == ESP_OK) vTaskDelay(pdMS_TO_TICKS(25));','        (void)0;'),
 ('can_back_in_aux','firmware/main/app_main.c','        vTaskDelay(pdMS_TO_TICKS(2));\r\n        if(now-last_stats','        { twai_message_t m; twai_receive(&m,pdMS_TO_TICKS(2)); }\r\n        if(now-last_stats'),
 ('bench_allows_test','firmware/main/app_main.c','    if(bench_mode && !strcmp(cmd,"test")) return false;','    (void)bench_mode;'),
 ('profile_p06_m2','profiles/hardware.json','"serial": "IL_001",\r\n      "hardware_revision": "R2",\r\n      "interface": "S1"','"serial": "IL_001",\r\n      "hardware_revision": "R2",\r\n      "interface": "M2"'),
 ('profile_calibration_changed','profiles/hardware.json','"current_window_accepted": false','"current_window_accepted": true'),
 ('p09_patch_partly_reverted','firmware/main/board.c','.cs_ena_pretrans = 2, .cs_ena_posttrans = 2','.cs_ena_pretrans = 2, .cs_ena_posttrans = 1'),
]
results=[]
with tempfile.TemporaryDirectory() as t:
    base=Path(t);(base/'Rewizje').mkdir();(base/'Rewizje/EGRLab-v6.1-rc1').symlink_to(R.parent/'EGRLab-v6.1-rc1')
    (base/'Plytki').symlink_to(R.parents[1]/'Plytki')
    def run(copy):
        r=subprocess.run([sys.executable,'-m','unittest','test_v62_s1'],cwd=copy/'tests',capture_output=True,text=True)
        return r.returncode,[l for l in r.stderr.splitlines() if l.startswith(('FAIL:','ERROR:'))]
    for name,rel,old,new in [('zerowa',None,None,None)]+MUT:
        copy=base/'Rewizje/EGRLab-v6.2-s1'
        if copy.exists():shutil.rmtree(copy)
        shutil.copytree(R,copy,ignore=shutil.ignore_patterns('verification','__pycache__','*.exe'))
        if rel:
            f=copy/rel;s=f.read_bytes().decode('utf-8');assert s.count(old)==1,(name,s.count(old));f.write_bytes(s.replace(old,new).encode('utf-8'))
        code,fails=run(copy);ok=(code==0) if rel is None else (code!=0)
        results.append({'mutation':name,'detected' if rel else 'clean':ok,'failed':fails});print('OK ' if ok else 'ZLE',name,fails[:2])
(R/'verification').mkdir(exist_ok=True)
(R/'verification/v62-mutations.json').write_text(json.dumps(results,indent=1,ensure_ascii=False)+'\n',encoding='utf-8')
good=sum(1 for x in results if x.get('detected',x.get('clean')));print(f'{good}/{len(results)} (z proba zerowa)');sys.exit(0 if good==len(results) else 1)

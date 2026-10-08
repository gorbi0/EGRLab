"""Review-only fault injection. Extract unmodified M1 board functions.
HAL/scheduler are stubs; this is a C logic test, not an ESP or motor test.
The post-error sequence is the successful configuration/release path in app_main.c.
"""
from pathlib import Path
import sys, subprocess, re
E=Path(__file__).resolve().parent
F=E.parent/'work/Rewizje/EGRLab-v6.3-m1'
sys.path.insert(0,str(F/'tests'))
from probe_drive import PRE
from probe_storage import function
board=(F/'firmware/main/board.c').read_text(encoding='utf-8')
app=(F/'firmware/main/app_main.c').read_text(encoding='utf-8')
start_branch=re.search(r'if\(board_watchdogs_start\(\)!=ESP_OK\) \{[^\n]+\}',app).group(0)
release_branch=re.search(r'if\(stop_epoch==epoch && !stop_pending && acquisition_healthy && storage_ok\(\) && ctrl.state!=FAULT\)\s+board_release\(gate\);',app).group(0)
stubs=r'''
#define ESP_LOGE(...) ((void)0)
#define CONFIG_EGR_DRIVE_WDT_MS 200
#define CONFIG_EGR_RTC_WDT_MS 1000
typedef struct {int timeout_ms,idle_core_mask;bool trigger_panic;} esp_task_wdt_config_t;
static int fail_case, rtc_calls, rtc_wdt; static bool rtc_wdt_on;
enum {WDT_STAGE0=0,WDT_STAGE_ACTION_RESET_SYSTEM=1,FAULT=9};
static int esp_task_wdt_reconfigure(const esp_task_wdt_config_t *c){(void)c;return fail_case==1?3:(fail_case==2?ESP_ERR_INVALID_STATE:ESP_OK);}
static int esp_task_wdt_init(const esp_task_wdt_config_t *c){(void)c;return fail_case==2?3:ESP_OK;}
static int esp_task_wdt_add(void *p){(void)p;return fail_case==3?3:ESP_OK;}
static int rtc_clk_slow_freq_get_hz(void){return 32768;}
static void wdt_hal_write_protect_disable(int *p){(void)p;rtc_calls++;}
static void wdt_hal_write_protect_enable(int *p){(void)p;rtc_calls++;}
static void wdt_hal_config_stage(int *p,int s,uint32_t t,int a){(void)p;(void)s;(void)t;(void)a;rtc_calls++;}
static void wdt_hal_enable(int *p){(void)p;rtc_calls++;}
static bool storage_ok(void){return true;}
'''
sigs=['static void pwm_set(','void board_inhibit(','uint32_t board_stop_token(',
      'void board_emergency_stop(','bool board_release(','void board_kill(',
      'void board_overcurrent_trip(','void board_drive(','esp_err_t board_mode(',
      'esp_err_t board_sensor_off(','esp_err_t board_watchdogs_start(']
main=r'''
int main(void) {
  for(fail_case=1;fail_case<=3;fail_case++) {
    rtc_calls=0;rtc_wdt_on=false;inhibited=true;gate_epoch=0;now_us=0;
    current_sign=0;reverse_until=0;drive_ok=true;
    /* Exact branch from safety(), including the emergency stop. */
    START_BRANCH
    int inhibited_after_error=inhibited;
    /* The next normal commit captures the current epoch, not the old one. */
    uint32_t gate=board_stop_token();
    unsigned stop_epoch=0,epoch=0;bool stop_pending=false,acquisition_healthy=true;
    struct {int state;} ctrl={0};
    board_inhibit(true);board_kill();
    if(board_mode(true,false)!=ESP_OK)return 2;
    /* Exact final predicate from successful commit_locked(). */
    RELEASE_BRANCH
    board_drive(.2f,true); now_us+=5000; board_drive(.2f,true);
    printf("WDT_FAILURE_CASE=%d inhibited_after_error=%d RTC_STARTED=%d RTC_CALLS=%d AFTER_COMMIT_EN=%d RPWM=%u LPWM=%u\n",
      fail_case,inhibited_after_error,rtc_wdt_on,rtc_calls,level[GPIO_DRIVE_EN],duty_out[0],duty_out[1]);
    if(!level[GPIO_DRIVE_EN] || !duty_out[0] || rtc_wdt_on)return 3;
  }
  return 0;
}
'''.replace('START_BRANCH',start_branch).replace('RELEASE_BRANCH',release_branch)
source=PRE+stubs+''.join(function(board,s) for s in sigs)+main
c=E/'watchdog_probe.c';c.write_text(source,encoding='utf-8')
exe=E/'watchdog_probe.exe'
subprocess.run([str(E/'tcc-review.cmd'),'-std=c11',str(c),'-o',str(exe)],check=True)
r=subprocess.run([str(exe)],text=True,capture_output=True,check=True)
(E/'watchdog-probe.txt').write_text(r.stdout,encoding='utf-8'); print(r.stdout)

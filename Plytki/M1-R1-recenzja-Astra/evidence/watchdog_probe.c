
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <math.h>
typedef int esp_err_t;
enum {ESP_OK=0,ESP_ERR_INVALID_STATE=2};
enum {GPIO_RPWM=1,GPIO_LPWM=21,GPIO_DRIVE_EN=39,GPIO_SENS_EN=40};
enum {LEDC_LOW_SPEED_MODE=0,LEDC_CHANNEL_0=0,LEDC_CHANNEL_1=1};
typedef int portMUX_TYPE;
#define portENTER_CRITICAL(m) ((void)(m),critical++)
#define portEXIT_CRITICAL(m) ((void)(m),critical--)
#define pdMS_TO_TICKS(x) (x)
static int critical,level[64],violations;static uint32_t duty_set[2],duty_out[2];static uint64_t now_us;
static int gpio_set_level(int pin,int v){level[pin]=v;return 0;}
static int ledc_set_duty(int mode,int ch,uint32_t d){(void)mode;duty_set[ch]=d;return 0;}
static int ledc_update_duty(int mode,int ch){(void)mode;duty_out[ch]=duty_set[ch];return 0;}
static uint64_t esp_timer_get_time(void){return now_us;}
static void vTaskDelay(int t){now_us+=1000ull*t;}
static portMUX_TYPE gate_mux;static bool inhibited=true;static uint32_t gate_epoch;
static bool drive_ok=true,sens_on,acquisition_running;static int current_sign;static uint64_t reverse_until;
void board_kill(void);esp_err_t board_sensor_off(void);
/* Niezmiennik M-05: nigdy oba PWM naraz; DRIVE_EN wysoki tylko przy jednym aktywnym kierunku albo postoju. */
static void invariant(void){if(duty_out[0] && duty_out[1])violations++;}

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
static void pwm_set(uint32_t r, uint32_t l) {
    ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, r); ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
    ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_1, l); ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_1);
}void board_inhibit(bool stop) {
    portENTER_CRITICAL(&gate_mux);
    inhibited = stop;
    if (stop) gpio_set_level(GPIO_DRIVE_EN, 0);
    portEXIT_CRITICAL(&gate_mux);
}uint32_t board_stop_token(void) {
    portENTER_CRITICAL(&gate_mux); uint32_t v=gate_epoch; portEXIT_CRITICAL(&gate_mux); return v;
}void board_emergency_stop(void) {
    portENTER_CRITICAL(&gate_mux); gate_epoch++; inhibited=true; gpio_set_level(GPIO_DRIVE_EN,0); portEXIT_CRITICAL(&gate_mux);
    board_kill();
}bool board_release(uint32_t token) {
    portENTER_CRITICAL(&gate_mux); bool ok=token==gate_epoch;
    if(ok) inhibited=false;
    portEXIT_CRITICAL(&gate_mux); return ok;
}void board_kill(void) {
    portENTER_CRITICAL(&gate_mux);
    gpio_set_level(GPIO_DRIVE_EN, 0);
    portEXIT_CRITICAL(&gate_mux);
    pwm_set(0, 0);
}void board_overcurrent_trip(void) { drive_ok = false; board_emergency_stop(); }void board_drive(float duty, bool permit) {
    if (!drive_ok || !permit || !isfinite(duty)) { board_kill(); return; }
    int sign = duty > 0 ? 1 : duty < 0 ? -1 : 0;
    uint64_t now = esp_timer_get_time();
    if (sign && sign != current_sign) {
        board_kill(); current_sign = sign; reverse_until = now + 5000;
        return;                       /* pelne 5 ms przerwy */
    }
    if (now < reverse_until) { board_kill(); return; }
    /* Zezwolenie utrzymujemy w postoju przy duty 0 (oba PWM nisko = hamowanie); STOP zdejmuje DRIVE_EN. */
    portENTER_CRITICAL(&gate_mux);
    bool blocked = inhibited;
    if (!blocked) gpio_set_level(GPIO_DRIVE_EN, 1);
    portEXIT_CRITICAL(&gate_mux);
    if (blocked) { board_kill(); return; }
    uint32_t d = (uint32_t)(fminf(fabsf(duty), .9f) * 1023);
    pwm_set(current_sign > 0 ? d : 0, current_sign < 0 ? d : 0);
}esp_err_t board_mode(bool test, bool sensor) {
    if (acquisition_running) return ESP_ERR_INVALID_STATE;
    if (sensor && !test) { board_sensor_off(); return ESP_ERR_INVALID_STATE; }
    board_kill();
    current_sign = 0; reverse_until = 0; drive_ok = true;
    if (!sensor) return board_sensor_off();
    if (!sens_on) { vTaskDelay(pdMS_TO_TICKS(100)); gpio_set_level(GPIO_SENS_EN, 1); sens_on = true; }
    return ESP_OK;
}esp_err_t board_sensor_off(void) {
    gpio_set_level(GPIO_SENS_EN, 0); sens_on = false;
    return ESP_OK;
}esp_err_t board_watchdogs_start(void) {
    esp_task_wdt_config_t c = {.timeout_ms = CONFIG_EGR_DRIVE_WDT_MS, .idle_core_mask = 0, .trigger_panic = true};
    esp_err_t e = esp_task_wdt_reconfigure(&c);
    if (e == ESP_ERR_INVALID_STATE) e = esp_task_wdt_init(&c);
    if (e == ESP_OK) e = esp_task_wdt_add(NULL);
    if (e != ESP_OK) return e;
    uint32_t ticks = (uint32_t)((uint64_t)CONFIG_EGR_RTC_WDT_MS * rtc_clk_slow_freq_get_hz() / 1000);
    wdt_hal_write_protect_disable(&rtc_wdt);
    wdt_hal_config_stage(&rtc_wdt, WDT_STAGE0, ticks, WDT_STAGE_ACTION_RESET_SYSTEM);
    wdt_hal_enable(&rtc_wdt);
    wdt_hal_write_protect_enable(&rtc_wdt);
    rtc_wdt_on = true;
    return ESP_OK;
}
int main(void) {
  for(fail_case=1;fail_case<=3;fail_case++) {
    rtc_calls=0;rtc_wdt_on=false;inhibited=true;gate_epoch=0;now_us=0;
    current_sign=0;reverse_until=0;drive_ok=true;
    /* Exact branch from safety(), including the emergency stop. */
    if(board_watchdogs_start()!=ESP_OK) { ESP_LOGE(TAG,"watchdog: start nieudany - TEST zablokowany"); board_emergency_stop(); }
    int inhibited_after_error=inhibited;
    /* The next normal commit captures the current epoch, not the old one. */
    uint32_t gate=board_stop_token();
    unsigned stop_epoch=0,epoch=0;bool stop_pending=false,acquisition_healthy=true;
    struct {int state;} ctrl={0};
    board_inhibit(true);board_kill();
    if(board_mode(true,false)!=ESP_OK)return 2;
    /* Exact final predicate from successful commit_locked(). */
    if(stop_epoch==epoch && !stop_pending && acquisition_healthy && storage_ok() && ctrl.state!=FAULT)
        board_release(gate);
    board_drive(.2f,true); now_us+=5000; board_drive(.2f,true);
    printf("WDT_FAILURE_CASE=%d inhibited_after_error=%d RTC_STARTED=%d RTC_CALLS=%d AFTER_COMMIT_EN=%d RPWM=%u LPWM=%u\n",
      fail_case,inhibited_after_error,rtc_wdt_on,rtc_calls,level[GPIO_DRIVE_EN],duty_out[0],duty_out[1]);
    if(!level[GPIO_DRIVE_EN] || !duty_out[0] || rtc_wdt_on)return 3;
  }
  return 0;
}

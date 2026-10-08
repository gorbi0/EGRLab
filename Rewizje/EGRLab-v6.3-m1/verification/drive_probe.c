
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
}
#define CHECK(x) do{checks++;invariant();if(!(x)){printf("FAIL %d: %s\n",__LINE__,#x);return 1;}}while(0)
int main(void){int checks=0;
CHECK(!level[GPIO_DRIVE_EN] && !duty_out[0] && !duty_out[1]);
board_drive(.3f,true);CHECK(!level[GPIO_DRIVE_EN]);                        /* inhibited po starcie */
CHECK(board_release(board_stop_token()));
board_drive(.3f,false);CHECK(!level[GPIO_DRIVE_EN] && !duty_out[0] && !duty_out[1]);   /* brak zezwolenia */
board_drive(.3f,true);CHECK(!level[GPIO_DRIVE_EN] && !duty_out[0]);         /* pierwszy kierunek: 5 ms przerwy */
now_us+=4999;board_drive(.3f,true);CHECK(!level[GPIO_DRIVE_EN] && !duty_out[0]);
now_us+=1;board_drive(.3f,true);CHECK(level[GPIO_DRIVE_EN] && duty_out[0]==306 && duty_out[1]==0);
board_drive(.95f,true);CHECK(duty_out[0]==920 && !duty_out[1]);             /* wypelnienie <= 90 % */
board_drive(0,true);CHECK(level[GPIO_DRIVE_EN] && !duty_out[0] && !duty_out[1]);  /* postoj: hamowanie */
board_drive(-.2f,true);CHECK(!level[GPIO_DRIVE_EN] && !duty_out[0] && !duty_out[1]); /* zmiana kierunku */
now_us+=2000;board_drive(-.2f,true);CHECK(!level[GPIO_DRIVE_EN] && !duty_out[1]);
now_us+=3000;board_drive(-.2f,true);CHECK(level[GPIO_DRIVE_EN] && duty_out[1]==204 && !duty_out[0]);
board_drive(NAN,true);CHECK(!level[GPIO_DRIVE_EN] && !duty_out[0] && !duty_out[1]);
board_drive(-.2f,true);CHECK(level[GPIO_DRIVE_EN] && duty_out[1]==204);
board_inhibit(true);CHECK(!level[GPIO_DRIVE_EN]);board_drive(-.2f,true);CHECK(!level[GPIO_DRIVE_EN] && !duty_out[1]);
uint32_t tok=board_stop_token();CHECK(board_release(tok));board_drive(-.2f,true);CHECK(level[GPIO_DRIVE_EN]);
tok=board_stop_token();board_emergency_stop();CHECK(!level[GPIO_DRIVE_EN] && !duty_out[1]);
CHECK(!board_release(tok));board_drive(-.2f,true);CHECK(!level[GPIO_DRIVE_EN]);  /* stary token nie zwalnia */
CHECK(board_release(board_stop_token()));board_drive(-.2f,true);CHECK(level[GPIO_DRIVE_EN]);
/* M-06: zadzialanie ograniczenia pradu - zatrzask do nastepnego board_mode, nawet po zwolnieniu bramki. */
board_overcurrent_trip();CHECK(!level[GPIO_DRIVE_EN] && !duty_out[1] && !drive_ok);
CHECK(board_release(board_stop_token()));board_drive(-.2f,true);CHECK(!level[GPIO_DRIVE_EN] && !duty_out[1]);
/* M-07: SENS_EN tylko z bankiem TEST; LOGGER zawsze wylacza. */
CHECK(board_mode(false,true)==ESP_ERR_INVALID_STATE);CHECK(!level[GPIO_SENS_EN] && !sens_on);
CHECK(board_mode(true,true)==ESP_OK);CHECK(level[GPIO_SENS_EN] && sens_on && drive_ok);
CHECK(!level[GPIO_DRIVE_EN] && !duty_out[0] && !duty_out[1]);              /* zmiana trybu = mostek w dol */
CHECK(board_mode(false,true)==ESP_ERR_INVALID_STATE);CHECK(!level[GPIO_SENS_EN] && !sens_on);  /* odmowa tez wylacza */
CHECK(board_mode(true,true)==ESP_OK && level[GPIO_SENS_EN]);
CHECK(board_mode(false,false)==ESP_OK);CHECK(!level[GPIO_SENS_EN]);
CHECK(board_mode(true,true)==ESP_OK && level[GPIO_SENS_EN]);
CHECK(board_mode(true,false)==ESP_OK);CHECK(!level[GPIO_SENS_EN]);
acquisition_running=true;CHECK(board_mode(true,true)==ESP_ERR_INVALID_STATE);CHECK(!level[GPIO_SENS_EN]);acquisition_running=false;
/* Po board_mode kierunek liczy sie od nowa: znow 5 ms przerwy. */
board_drive(.3f,true);CHECK(!level[GPIO_DRIVE_EN]);now_us+=5000;board_drive(.3f,true);CHECK(level[GPIO_DRIVE_EN] && duty_out[0]==306);
CHECK(critical==0);CHECK(violations==0);
printf("Drive / SENS_EN safe states: %d assertions OK\n",checks);return 0;}

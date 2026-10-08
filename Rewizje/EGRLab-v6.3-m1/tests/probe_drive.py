"""6.3-m1 (M-05, M-06, M-07): compile the actual bridge / sensor-supply functions of board.c with stubbed GPIO,
LEDC and timer, and check the safe states of the IBT-2 drive and of SENS_EN. No electronics are simulated.
python tests/probe_drive.py --cc gcc --out verification
"""
import argparse,subprocess
from pathlib import Path
from probe_storage import function

PRE=r'''
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
'''
POST=r'''
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
'''

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cc',default='gcc');p.add_argument('--out',type=Path,default=Path('verification'));a=p.parse_args()
    root=Path(__file__).parents[1];a.out.mkdir(parents=True,exist_ok=True)
    board=(root/'firmware/main/board.c').read_text(encoding='utf-8')
    source=PRE+''.join(function(board,sig) for sig in ['static void pwm_set(','void board_inhibit(','uint32_t board_stop_token(',
        'void board_emergency_stop(','bool board_release(','void board_kill(','void board_overcurrent_trip(','void board_drive(',
        'esp_err_t board_mode(','esp_err_t board_sensor_off('])+POST
    c=a.out/'drive_probe.c';c.write_text(source,encoding='utf-8')
    exe=a.out/'drive_probe.exe';subprocess.run([a.cc,'-std=c11',str(c),'-lm','-o',str(exe)],check=True)
    result=subprocess.run([str(exe.resolve())],check=True,capture_output=True,text=True)
    (a.out/'drive-results.txt').write_text(result.stdout,encoding='utf-8');print(result.stdout,end='')

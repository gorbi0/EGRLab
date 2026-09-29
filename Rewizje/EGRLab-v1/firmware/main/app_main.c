#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <inttypes.h>
#include "sdkconfig.h"
#include "board.h"
#include "control.h"
#include "storage.h"
#include "commissioning.h"
#include "esp_timer.h"
#include "esp_psram.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "nvs.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"

static control_t ctrl;
static inputs_t latest;
static sample_t raw_latest;
static portMUX_TYPE data_mux=portMUX_INITIALIZER_UNLOCKED;
static SemaphoreHandle_t control_mutex;
static TaskHandle_t acquisition_handle;
static esp_timer_handle_t timer;
static volatile bool test_bank,run_permission;
static volatile bool acquisition_healthy=true;
static volatile uint32_t lost_ticks;
static bool tc_valid;
static uint64_t tc_time;
static nvs_handle_t nvs;
static const char *TAG="EGRLab";

static inputs_t snapshot(void){
    portENTER_CRITICAL(&data_mux);inputs_t i=latest;portEXIT_CRITICAL(&data_mux);
    i.now=esp_timer_get_time();i.interlock=board_interlock();i.hw_armed=board_armed();
    i.storage_ok=storage_ok()&&acquisition_healthy;
    portENTER_CRITICAL(&data_mux);i.tc_ok=tc_valid&&i.now-tc_time<1000000;portEXIT_CRITICAL(&data_mux);
    return i;
}
static void tick(void *arg){(void)arg;xTaskNotifyGive(acquisition_handle);}
static void acquisition(void *arg){
    (void)arg;uint32_t seq=0;
    while(true){
        uint32_t ticks=ulTaskNotifyTake(pdTRUE,portMAX_DELAY);
        sample_t s={.sequence=seq++};
        if(ticks>1){s.flags|=1;lost_ticks+=ticks-1;acquisition_healthy=false;board_kill();}
        esp_err_t e=board_adc(s.raw,&s.t_us);
        if(e!=ESP_OK){acquisition_healthy=false;board_kill();
            storage_event("{\"type\":\"adc_error\",\"code\":%d}",e);continue;}
        if(test_bank)s.flags|=2;if(run_permission)s.flags|=8;
        /* Calibration is fixed during each session, no NVS writes while acquiring. */
        portENTER_CRITICAL(&data_mux);
        latest.sample_time=s.t_us;raw_latest=s;
        for(int j=0;j<8;j++)latest.v[j]=s.raw[j]*(10.0f/32768)*ctrl.profile.gain[j]+ctrl.profile.offset[j];
        portEXIT_CRITICAL(&data_mux);
        storage_push(&s);
    }
}
static void safety(void *arg){
    (void)arg;TickType_t wake=xTaskGetTickCount();uint64_t last_beat=0,last_io=0;
    bool sensor_fault=false,was_mark=false;state_t prior=SAFE;
    while(true){
        inputs_t i=snapshot();
        if(i.now-last_io>=20000){
            if(board_inputs(&sensor_fault)!=ESP_OK)sensor_fault=true;last_io=i.now;
        }
        i.sensor_fault=sensor_fault;
        if(xSemaphoreTake(control_mutex,pdMS_TO_TICKS(2))==pdTRUE){
            control_step(&ctrl,&i);
            bool moving=control_moving(&ctrl);
#if !CONFIG_EGR_ACTIVE_TEST
            moving=false;
#endif
            run_permission=moving;
            board_drive(ctrl.duty,moving);
            bool entered_fault=ctrl.state==FAULT && prior!=FAULT;
            if(ctrl.state!=prior){
                storage_event("{\"type\":\"state\",\"t_us\":%"PRIu64",\"state\":\"%s\",\"fault\":\"%s\"}",
                    i.now,control_name(ctrl.state),ctrl.fault?ctrl.fault:"");prior=ctrl.state;
                storage_event("{\"type\":\"profile\",\"t_us\":%"PRIu64",\"supply_pin\":%ld,\"closed\":%.7g,\"open\":%.7g,\"sign\":%ld}",
                    i.now,(long)ctrl.profile.supply_pin,ctrl.profile.closed,ctrl.profile.open,(long)ctrl.profile.opening_sign);
            }
            bool beat=ctrl.state!=FAULT&&i.now-i.sample_time<10000&&acquisition_healthy;
            if(i.now-last_beat>=10000){board_heartbeat(beat);last_beat=i.now;}
            if(entered_fault){board_kill();board_mode(ctrl.test_bank,false,ctrl.profile.supply_pin);}
            xSemaphoreGive(control_mutex);
        }else {board_kill();run_permission=false;}
        bool mark=board_mark();if(mark&&!was_mark)storage_mark(i.now);was_mark=mark;
        vTaskDelayUntil(&wake,pdMS_TO_TICKS(1));
    }
}
static void auxiliary(void *arg){
    (void)arg;uint64_t last_tc=0;
    while(true){
        twai_message_t m;
        if(twai_receive(&m,pdMS_TO_TICKS(5))==ESP_OK){
            uint64_t now=esp_timer_get_time();char hex[17]={0};
            unsigned len=m.data_length_code>8?8:m.data_length_code;
            for(unsigned j=0;j<len;j++)snprintf(hex+j*2,3,"%02x",m.data[j]);
            storage_event("{\"type\":\"can\",\"t_us\":%"PRIu64",\"id\":%"PRIu32",\"ext\":%d,\"rtr\":%d,\"data\":\"%s\"}",
                now,m.identifier,m.extd,m.rtr,hex);
            if(!m.extd&&!m.rtr&&m.identifier>=0x7e8&&m.identifier<=0x7ef&&len>=5&&
                    m.data[0]>=4&&m.data[0]<=7&&m.data[1]==0x41&&m.data[2]==0x0c){
                float rpm=((unsigned)m.data[3]*256+m.data[4])/4.0f;
                storage_event("{\"type\":\"rpm_obd\",\"t_us\":%"PRIu64",\"rpm\":%.2f}",now,rpm);
            }
        }
        uint64_t now=esp_timer_get_time();
        if(now-last_tc>=200000){
            float t[2]={NAN,NAN};uint8_t fault[2]={255,255};
            for(int j=0;j<2;j++)if(board_temperature(j,&t[j],&fault[j])!=ESP_OK){fault[j]=255;t[j]=NAN;}
            portENTER_CRITICAL(&data_mux);
            latest.t1=t[0];latest.t2=t[1];tc_valid=!fault[0];tc_time=now;
            portEXIT_CRITICAL(&data_mux);
            for(int j=0;j<2;j++){
                char value[32];if(isfinite(t[j]))snprintf(value,sizeof value,"%.4f",t[j]);else strcpy(value,"null");
                storage_event("{\"type\":\"temperature\",\"t_us\":%"PRIu64",\"channel\":%d,\"celsius\":%s,\"fault\":%u}",now,j+1,value,fault[j]);
            }last_tc=now;
            twai_status_info_t info;if(twai_get_status_info(&info)==ESP_OK&&info.rx_missed_count){
                storage_event("{\"type\":\"can_drop\",\"count\":%"PRIu32"}",info.rx_missed_count);
            }
        }
    }
}
static bool valid_id(const char *s){
    if(!*s)return false;
    for(;*s;s++)if(!((*s>='a'&&*s<='z')||(*s>='A'&&*s<='Z')||(*s>='0'&&*s<='9')||*s=='_'||*s=='-'))return false;
    return true;
}
static void console(void *arg){
    (void)arg;char line[160],cmd[32];
    puts("EGRLab: status logger identify bind test learn manual goto sweep friction cycle thermal mark stop save");
    while(true){
        if(!fgets(line,sizeof line,stdin)){vTaskDelay(pdMS_TO_TICKS(20));continue;}
        float a=0,bf=0;int b=0;cmd[0]=0;int fields=sscanf(line,"%31s %f %f",cmd,&a,&bf);
        if((fields>=2&&(!isfinite(a)||fabsf(a)>10000))||(fields>=3&&(!isfinite(bf)||fabsf(bf)>10000))){puts("INVALID NUMBER");continue;}
        b=(int)bf;
        if(!strcmp(cmd,"stop"))board_kill();
        if(!strcmp(cmd,"mark")){storage_mark(esp_timer_get_time());continue;}
        if(xSemaphoreTake(control_mutex,pdMS_TO_TICKS(50))!=pdTRUE){puts("BUSY");continue;}
        inputs_t i=snapshot();bool ok=false;
        if(!strcmp(cmd,"status")){
            printf("%s pin5V=%ld V4=%.4f V5=%.4f V6=%.4f I=%.3f ratio=%.4f pos=%.4f T=%.2f drops=%"PRIu32" qualified=%d\n",
                control_name(ctrl.state),(long)ctrl.profile.supply_pin,i.v[2],i.v[3],i.v[4],
                (i.v[5]-2.5f)/.25f,control_ratio(&ctrl,&i),control_position(&ctrl,&i),i.t1,lost_ticks,ctrl.profile.qualified);ok=true;
        }else if(!strcmp(cmd,"bind")&&ctrl.state==SAFE){
            char v[32]={0},h[32]={0};if(sscanf(line,"%*s %31s %31s",v,h)==2&&valid_id(v)&&valid_id(h)){
                /* A different physical valve invalidates all learned parameters. */
                if(strcmp(v,ctrl.profile.valve)||strcmp(h,ctrl.profile.adapter)){
                    ctrl.profile.supply_pin=0;ctrl.profile.learned=false;
                }strcpy(ctrl.profile.valve,v);strcpy(ctrl.profile.adapter,h);ok=true;
            }
        }else if(!strcmp(cmd,"learn")&&ctrl.state==READY){
            float rc,ro;int sign;
            if(sscanf(line,"%*s %f %f %d",&rc,&ro,&sign)==3&&isfinite(rc)&&isfinite(ro)&&
                    rc>.02f&&rc<.98f&&ro>.02f&&ro<.98f&&fabsf(ro-rc)>.2f&&(sign==1||sign==-1)){
                ctrl.profile.closed=rc;ctrl.profile.open=ro;ctrl.profile.opening_sign=sign;
                ctrl.profile.learned=true;ok=true;
            }
        }else if(!strcmp(cmd,"save")&&ctrl.state==SAFE&&valid_id(ctrl.profile.valve)&&valid_id(ctrl.profile.adapter)){
            /* Stop timer and park acquisition before flash writes. */
            esp_timer_stop(timer);vTaskDelay(pdMS_TO_TICKS(20));
            esp_err_t e=nvs_set_blob(nvs,"profile",&ctrl.profile,sizeof ctrl.profile);
            if(e==ESP_OK)e=nvs_commit(nvs);ok=e==ESP_OK;
            esp_timer_start_periodic(timer,1000000/CONFIG_EGR_SAMPLE_HZ);
        }else{
#if !CONFIG_EGR_ACTIVE_TEST
            bool active=strcmp(cmd,"logger")&&strcmp(cmd,"identify")&&strcmp(cmd,"stop");
            if(active){puts("ACTIVE_TEST disabled in menuconfig");xSemaphoreGive(control_mutex);continue;}
#endif
            if(!strcmp(cmd,"cycle")||!strcmp(cmd,"friction"))b=(int)a;
            ok=control_command(&ctrl,cmd,a,b,i.now);
            if(ok&&(!strcmp(cmd,"test")||!strcmp(cmd,"logger")||!strcmp(cmd,"stop"))){
                board_kill();test_bank=ctrl.test_bank;
                if(board_mode(ctrl.test_bank,ctrl.sensor_on,ctrl.profile.supply_pin)!=ESP_OK){
                    control_stop(&ctrl);ok=false;
                }
            }
        }
        if(ok){
            storage_event("{\"type\":\"command\",\"t_us\":%"PRIu64",\"command\":\"%s\",\"a\":%.7g,\"b\":%d}",i.now,cmd,a,b);
            storage_event("{\"type\":\"profile\",\"t_us\":%"PRIu64",\"supply_pin\":%ld,\"closed\":%.7g,\"open\":%.7g,\"sign\":%ld}",
                i.now,(long)ctrl.profile.supply_pin,ctrl.profile.closed,ctrl.profile.open,(long)ctrl.profile.opening_sign);
        }
        xSemaphoreGive(control_mutex);puts(ok?"OK":"REJECTED (state/profile/limits)");
    }
}
void app_main(void){
    ESP_ERROR_CHECK(nvs_flash_init());ESP_ERROR_CHECK(nvs_open("egrlab",NVS_READWRITE,&nvs));
    control_init(&ctrl);size_t bytes=sizeof(profile_t);profile_t saved;
    if(nvs_get_blob(nvs,"profile",&saved,&bytes)==ESP_OK&&bytes==sizeof saved&&saved.magic==0x45475231){
        ctrl.profile=saved;
    }
    ctrl.profile.qualified=EGR_HARDWARE_ACCEPTED;
    /* Set qualified=true ONLY after the documented electrical acceptance/calibration,
       with a reviewed profile. No auto-qualification from a pin voltage is allowed. */
    uint32_t session=0;nvs_get_u32(nvs,"session",&session);session++;
    ESP_ERROR_CHECK(nvs_set_u32(nvs,"session",session));ESP_ERROR_CHECK(nvs_commit(nvs));
    ESP_LOGI(TAG,"PSRAM=%u bytes; hardware TEST default locked",(unsigned)esp_psram_get_size());
    ESP_ERROR_CHECK(board_init());ESP_ERROR_CHECK(board_sd_mount());
    if(!storage_init(session,&ctrl.profile)){board_kill();ESP_LOGE(TAG,"Storage initialization failed");return;}
    control_mutex=xSemaphoreCreateMutex();configASSERT(control_mutex);
    latest.t1=NAN;latest.t2=NAN;
    ESP_ERROR_CHECK(board_mode(false,false,ctrl.profile.supply_pin));
    configASSERT(xTaskCreatePinnedToCore(acquisition,"adc",4096,NULL,23,&acquisition_handle,1)==pdPASS);
    configASSERT(xTaskCreatePinnedToCore(storage_writer,"writer",8192,NULL,8,NULL,0)==pdPASS);
    configASSERT(xTaskCreatePinnedToCore(safety,"safety",4096,NULL,20,NULL,0)==pdPASS);
    configASSERT(xTaskCreatePinnedToCore(auxiliary,"aux",4096,NULL,5,NULL,0)==pdPASS);
    esp_timer_create_args_t ta={.callback=tick,.dispatch_method=ESP_TIMER_TASK,.name="sample"};
    ESP_ERROR_CHECK(esp_timer_create(&ta,&timer));
    ESP_ERROR_CHECK(esp_timer_start_periodic(timer,1000000/CONFIG_EGR_SAMPLE_HZ));
    configASSERT(xTaskCreatePinnedToCore(console,"console",6144,NULL,3,NULL,0)==pdPASS);
}

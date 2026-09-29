#include "board.h"
#include <math.h>
#include "driver/gpio.h"
#include "driver/spi_master.h"
#include "driver/i2c.h"
#include "driver/ledc.h"
#include "driver/sdspi_host.h"
#include "esp_timer.h"
#include "esp_rom_sys.h"
#include "esp_vfs_fat.h"
#include "sdmmc_cmd.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"

enum {PWM=1,INA=2,INB=38,ARM=39,HW_ARM=40,MARK=41,INTERLOCK=42,HEART=21};
static spi_device_handle_t adc,tc[2];
static SemaphoreHandle_t io_lock;
static uint8_t porta;
static int current_sign;
static uint64_t reverse_until;
static bool prev_sensor,prev_test;
static int prev_pin;
static esp_err_t mcp_write(uint8_t reg,uint8_t value){
    uint8_t tx[]={reg,value};
    return i2c_master_write_to_device(I2C_NUM_0,0x20,tx,2,pdMS_TO_TICKS(5));
}
static esp_err_t mcp_read(uint8_t reg,uint8_t *value){
    return i2c_master_write_read_device(I2C_NUM_0,0x20,&reg,1,value,1,pdMS_TO_TICKS(5));
}
void board_kill(void){
    gpio_set_level(ARM,0);
    ledc_set_duty(LEDC_LOW_SPEED_MODE,LEDC_CHANNEL_0,0);
    ledc_update_duty(LEDC_LOW_SPEED_MODE,LEDC_CHANNEL_0);
}
bool board_interlock(void){return gpio_get_level(INTERLOCK);}
bool board_armed(void){return gpio_get_level(HW_ARM);}
bool board_mark(void){return !gpio_get_level(MARK);}
void board_heartbeat(bool enabled){
    static bool level;
    level=enabled?!level:false;gpio_set_level(HEART,level);
}
void board_drive(float duty,bool permit){
    if(!permit||!isfinite(duty)||!board_interlock()||!board_armed()){
        board_kill();return;
    }
    int sign=duty>0?1:duty<0?-1:0;
    uint64_t now=esp_timer_get_time();
    if(sign&&sign!=current_sign){
        board_kill();current_sign=sign;reverse_until=now+5000;
        gpio_set_level(INA,sign>0);gpio_set_level(INB,sign<0);
    }
    if(now<reverse_until){board_kill();return;}
    /* Maintain power permission during zero-duty dwell; STOP deasserts both EN pins. */
    gpio_set_level(ARM,1);
    ledc_set_duty(LEDC_LOW_SPEED_MODE,LEDC_CHANNEL_0,(uint32_t)(fminf(fabsf(duty),.9f)*1023));
    ledc_update_duty(LEDC_LOW_SPEED_MODE,LEDC_CHANNEL_0);
}
static esp_err_t tc_write(spi_device_handle_t dev,uint8_t reg,uint8_t val){
    spi_transaction_t t={.length=16,.flags=SPI_TRANS_USE_TXDATA};
    t.tx_data[0]=reg|0x80;t.tx_data[1]=val;return spi_device_polling_transmit(dev,&t);
}
esp_err_t board_init(void){
    gpio_config_t out={.pin_bit_mask=(1ULL<<INA)|(1ULL<<INB)|(1ULL<<ARM)|(1ULL<<HEART)|(1ULL<<13),
        .mode=GPIO_MODE_OUTPUT};
    ESP_ERROR_CHECK(gpio_config(&out));
    gpio_set_level(ARM,0);gpio_set_level(HEART,0);gpio_set_level(13,0);
    gpio_config_t inp={.pin_bit_mask=(1ULL<<HW_ARM)|(1ULL<<INTERLOCK)|(1ULL<<14),.mode=GPIO_MODE_INPUT};
    ESP_ERROR_CHECK(gpio_config(&inp));
    inp.pin_bit_mask=1ULL<<MARK;inp.pull_up_en=GPIO_PULLUP_ENABLE;ESP_ERROR_CHECK(gpio_config(&inp));
    ledc_timer_config_t lt={.speed_mode=LEDC_LOW_SPEED_MODE,.duty_resolution=LEDC_TIMER_10_BIT,
        .timer_num=LEDC_TIMER_0,.freq_hz=1000,.clk_cfg=LEDC_AUTO_CLK};
    ESP_ERROR_CHECK(ledc_timer_config(&lt));
    ledc_channel_config_t lc={.gpio_num=PWM,.speed_mode=LEDC_LOW_SPEED_MODE,.channel=LEDC_CHANNEL_0,
        .timer_sel=LEDC_TIMER_0,.duty=0};ESP_ERROR_CHECK(ledc_channel_config(&lc));
    io_lock=xSemaphoreCreateMutex();if(!io_lock)return ESP_ERR_NO_MEM;
    i2c_config_t ic={.mode=I2C_MODE_MASTER,.sda_io_num=10,.scl_io_num=15,
        .sda_pullup_en=true,.scl_pullup_en=true,.master.clk_speed=400000};
    ESP_ERROR_CHECK(i2c_param_config(I2C_NUM_0,&ic));
    ESP_ERROR_CHECK(i2c_driver_install(I2C_NUM_0,I2C_MODE_MASTER,0,0,0));
    /* Set latches before switching port A to outputs. */
    ESP_ERROR_CHECK(mcp_write(0x14,0));ESP_ERROR_CHECK(mcp_write(0x00,0));
    ESP_ERROR_CHECK(mcp_write(0x01,0xff));ESP_ERROR_CHECK(mcp_write(0x0d,0xff));
    ESP_ERROR_CHECK(mcp_write(0x14,1));esp_rom_delay_us(20);
    ESP_ERROR_CHECK(mcp_write(0x14,0));vTaskDelay(pdMS_TO_TICKS(10));
    spi_bus_config_t ab={.mosi_io_num=-1,.miso_io_num=11,.sclk_io_num=9,
        .quadwp_io_num=-1,.quadhd_io_num=-1,.max_transfer_sz=32};
    ESP_ERROR_CHECK(spi_bus_initialize(SPI2_HOST,&ab,SPI_DMA_CH_AUTO));
    spi_device_interface_config_t ad={.clock_speed_hz=8000000,.mode=2,.spics_io_num=12,
        .queue_size=1,.cs_ena_pretrans=2,.cs_ena_posttrans=1};
    ESP_ERROR_CHECK(spi_bus_add_device(SPI2_HOST,&ad,&adc));
    spi_bus_config_t sb={.mosi_io_num=5,.miso_io_num=6,.sclk_io_num=4,
        .quadwp_io_num=-1,.quadhd_io_num=-1,.max_transfer_sz=8192};
    ESP_ERROR_CHECK(spi_bus_initialize(SPI3_HOST,&sb,SPI_DMA_CH_AUTO));
    for(int i=0;i<2;i++){
        spi_device_interface_config_t t={.clock_speed_hz=1000000,.mode=1,
            .spics_io_num=i?16:8,.queue_size=1};
        ESP_ERROR_CHECK(spi_bus_add_device(SPI3_HOST,&t,&tc[i]));
        ESP_ERROR_CHECK(tc_write(tc[i],1,0x03)); /* K, one-sample averaging */
        ESP_ERROR_CHECK(tc_write(tc[i],0,0x91)); /* continuous, OC detection, 50 Hz */
    }
    twai_general_config_t tg=TWAI_GENERAL_CONFIG_DEFAULT(17,18,TWAI_MODE_LISTEN_ONLY);
    tg.rx_queue_len=128;tg.tx_queue_len=0;
    twai_timing_config_t tt=TWAI_TIMING_CONFIG_500KBITS();
    twai_filter_config_t tf=TWAI_FILTER_CONFIG_ACCEPT_ALL();
    ESP_ERROR_CHECK(twai_driver_install(&tg,&tt,&tf));ESP_ERROR_CHECK(twai_start());
    return ESP_OK;
}
esp_err_t board_sd_mount(void){
    sdmmc_host_t host=SDSPI_HOST_DEFAULT();host.slot=SPI3_HOST;host.max_freq_khz=10000;
    sdspi_device_config_t slot=SDSPI_DEVICE_CONFIG_DEFAULT();slot.gpio_cs=7;slot.host_id=SPI3_HOST;
    esp_vfs_fat_sdmmc_mount_config_t mount={.format_if_mount_failed=false,.max_files=8,.allocation_unit_size=32768};
    sdmmc_card_t *card=NULL;
    return esp_vfs_fat_sdspi_mount("/sd",&host,&slot,&mount,&card);
}
esp_err_t board_adc(int16_t values[8],uint64_t *t_us){
    *t_us=esp_timer_get_time();gpio_set_level(13,1);esp_rom_delay_us(1);gpio_set_level(13,0);
    uint64_t until=*t_us+100;
    while(gpio_get_level(14)){if((uint64_t)esp_timer_get_time()>until)return ESP_ERR_TIMEOUT;}
    for(int i=0;i<8;i++){
        spi_transaction_t t={.length=16,.flags=SPI_TRANS_USE_RXDATA};
        esp_err_t e=spi_device_polling_transmit(adc,&t);if(e!=ESP_OK)return e;
        values[i]=(int16_t)(((uint16_t)t.rx_data[0]<<8)|t.rx_data[1]);
    }return ESP_OK;
}
esp_err_t board_mode(bool test,bool sensor,int supply_pin){
    if(sensor&&(!test||!board_interlock()||(supply_pin!=5&&supply_pin!=6)))return ESP_ERR_INVALID_STATE;
    if(test==prev_test&&sensor==prev_sensor&&supply_pin==prev_pin&&porta)return ESP_OK;
    board_kill();
    if(xSemaphoreTake(io_lock,pdMS_TO_TICKS(10))!=pdTRUE)return ESP_ERR_TIMEOUT;
    porta=0;esp_err_t e=mcp_write(0x14,porta); /* both banks and sensor OFF */
    if(e==ESP_OK){vTaskDelay(pdMS_TO_TICKS(100));
        porta=(test?4:2)|((test&&supply_pin==6)?16:0);
        e=mcp_write(0x14,porta);
    }
    if(e==ESP_OK&&sensor){vTaskDelay(pdMS_TO_TICKS(100));porta|=8|32;e=mcp_write(0x14,porta);}
    xSemaphoreGive(io_lock);
    if(e==ESP_OK){prev_test=test;prev_sensor=sensor;prev_pin=supply_pin;}
    else {porta=0;board_kill();}
    return e;
}
esp_err_t board_inputs(bool *sensor_fault){
    if(xSemaphoreTake(io_lock,pdMS_TO_TICKS(5))!=pdTRUE)return ESP_ERR_TIMEOUT;
    uint8_t b=0;esp_err_t e=mcp_read(0x13,&b);xSemaphoreGive(io_lock);
    *sensor_fault=(e!=ESP_OK)||!(b&2);return e;
}
esp_err_t board_temperature(int ch,float *value,uint8_t *fault){
    if(ch<0||ch>1)return ESP_ERR_INVALID_ARG;
    uint8_t tx[6]={0x0a,0,0,0,0,0},rx[6]={0};
    spi_transaction_t t={.length=48,.tx_buffer=tx,.rx_buffer=rx};
    esp_err_t e=spi_device_polling_transmit(tc[ch],&t);if(e!=ESP_OK)return e;
    /* Registers 0A CJTL, 0B LTCBH, 0C LTCBM, 0D LTCBL, 0E SR. */
    int32_t raw=((int32_t)rx[2]<<16)|((int32_t)rx[3]<<8)|rx[4];
    if(raw&0x800000)raw|=(int32_t)0xff000000;
    *fault=rx[5];*value=*fault?NAN:(float)(raw>>5)/128.0f;
    return ESP_OK;
}

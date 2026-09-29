
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
typedef int esp_err_t;
enum {ESP_OK=0,SPI_TRANS_USE_RXDATA=1};
enum {CURRENT_OK=1,CURRENT_ABSENT=2,CURRENT_BUS_ERROR=4,CURRENT_SATURATED=8,CURRENT_TIMING=16};
typedef struct {uint16_t raw,begin_us,end_us,status;} local_current_t;
typedef struct {int length,flags;uint8_t rx_data[4];} spi_transaction_t;
static int current_adc,spi_error,spi_calls,timer_calls;
static bool prev_test,present;
static uint16_t frame;
static uint64_t begin_stamp,end_stamp;
static bool board_local_current_present(bool test){(void)test;return present;}
static uint64_t esp_timer_get_time(void){return timer_calls++%2?end_stamp:begin_stamp;}
static int spi_device_polling_transmit(int device,spi_transaction_t *t){
 (void)device;spi_calls++;t->rx_data[0]=frame>>8;t->rx_data[1]=frame;return spi_error;}
static void current_read(uint64_t origin, local_current_t *out) {
    *out=(local_current_t){.raw=65535,.status=CURRENT_ABSENT};
    if(!board_local_current_present(prev_test)) return;
    uint64_t begin=esp_timer_get_time();
    spi_transaction_t t={.length=16,.flags=SPI_TRANS_USE_RXDATA};
    esp_err_t e=spi_device_polling_transmit(current_adc,&t);
    uint64_t end=esp_timer_get_time();
    if(e!=ESP_OK) {out->status=CURRENT_BUS_ERROR;return;}
    uint16_t word=((uint16_t)t.rx_data[0]<<8)|t.rx_data[1];
    out->raw=(word>>1)&0x0fff;
    if(begin<origin || end<begin || end-origin>400 || end-begin>100) {out->status=CURRENT_TIMING;return;}
    out->begin_us=(uint16_t)(begin-origin);out->end_us=(uint16_t)(end-origin);
    if(word&0x2000) out->status=CURRENT_BUS_ERROR; /* NULL bit must be zero */
    else if(out->raw<4 || out->raw>4091) out->status=CURRENT_SATURATED;
    else out->status=CURRENT_OK;
}
#define CHECK(x) do{checks++;if(!(x)){printf("FAIL %d: %s\n",__LINE__,#x);return 1;}}while(0)
int main(void){int checks=0;local_current_t out;
present=false;current_read(1000,&out);CHECK(out.status==CURRENT_ABSENT);CHECK(out.raw==65535);CHECK(spi_calls==0);
present=true;begin_stamp=1060;end_stamp=1098;frame=2253<<1;
current_read(1000,&out);CHECK(out.status==CURRENT_OK);CHECK(out.raw==2253);CHECK(out.begin_us==60 && out.end_us==98);
spi_error=1;current_read(1000,&out);CHECK(out.status==CURRENT_BUS_ERROR);spi_error=0;
frame=(2253<<1)|0x2000;current_read(1000,&out);CHECK(out.status==CURRENT_BUS_ERROR);
frame=0;current_read(1000,&out);CHECK(out.status==CURRENT_SATURATED);
frame=4095<<1;current_read(1000,&out);CHECK(out.status==CURRENT_SATURATED);
frame=2048<<1;begin_stamp=999;end_stamp=1098;current_read(1000,&out);CHECK(out.status==CURRENT_TIMING);
begin_stamp=1080;end_stamp=1070;current_read(1000,&out);CHECK(out.status==CURRENT_TIMING);
begin_stamp=1060;end_stamp=1161;current_read(1000,&out);CHECK(out.status==CURRENT_TIMING);
begin_stamp=1365;end_stamp=1401;current_read(1000,&out);CHECK(out.status==CURRENT_TIMING);
begin_stamp=1362;end_stamp=1400;current_read(1000,&out);CHECK(out.status==CURRENT_OK);
printf("Current ADC fault injection: %d assertions OK\n",checks);return 0;}

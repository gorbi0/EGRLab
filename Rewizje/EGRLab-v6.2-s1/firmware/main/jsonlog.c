#include "jsonlog.h"
#include <stdarg.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <inttypes.h>
/* 6.2-s1 F-06 (P06 R1 docs/FIRMWARE.md, P06 R2 po rewizji S1): tor pradu banku LOGGER w metadanych kazdej konfiguracji. */
#define CHAIN_LOGGER "P06R2 WSK2512 5mOhm INA240A2 G50 div1:2 tau1.20ms MCP3201"
#define CHAIN_TEST "P07 pre-S1"
void json_init(json_buf_t *b,char *p,size_t cap) { *b=(json_buf_t){p,cap,0,cap>0}; if(cap) *p=0; }
void json_add(json_buf_t *b,const char *fmt,...) {
    if(!b->ok) return;
    va_list a; va_start(a,fmt); int n=vsnprintf(b->p+b->used,b->cap-b->used,fmt,a); va_end(a);
    if(n<0 || (size_t)n>=b->cap-b->used) { b->ok=false; return; }
    b->used+=(size_t)n;
}
const char *json_number(char out[32],double x) {
    if(!isfinite(x)) strcpy(out,"null"); else snprintf(out,32,"%.9g",x);
    return out;
}
bool json_config(char *out,size_t cap,const session_config_t *c,uint64_t t) {
    json_buf_t b; json_init(&b,out,cap);
    json_add(&b,"{\"type\":\"config\",\"t_us\":%" PRIu64 ",\"config_id\":%u,\"bank\":%d,"
        "\"ch_supply\":%d,\"ch_ground\":%d,\"ch_feedback\":%d",t,c->id,c->bank,c->ch_supply,c->ch_ground,c->ch_feedback);
    const char *keys[]={"full_scale","gain","offset"};
    for(int k=0;k<3;k++) {
        json_add(&b,",\"%s\":[",keys[k]);
        for(int j=0;j<8;j++) { char n[32]; float v=k==0?control_full_scale(c->range[j]):k==1?c->gain[j]:c->offset[j];
            json_add(&b,"%s%s",j?",":"",json_number(n,v)); }
        json_add(&b,"]");
    }
    json_add(&b,",\"daq_module\":\"%s\",\"voltage_calibrated\":%s",c->daq_module,c->voltage_calibrated?"true":"false");
    json_add(&b,",\"local_current\":true,\"current_adc_gain\":%.9g,\"current_adc_offset\":%.9g,"
        "\"current_calibrated\":%s,\"current_module\":\"%s\",\"valve_id\":\"%s\",\"adapter_id\":\"%s\","
        "\"vehicle_id\":\"%s\",\"session_note\":\"%s\",\"current_time\":\"spi_interval_us\",\"synchronous\":false",
        c->current_adc_gain,c->current_adc_offset,c->current_calibrated?"true":"false",c->current_module,c->valve,c->adapter,c->vehicle_id,c->session_note);
    char z[32],closed[32],open[32];
    json_add(&b,",\"current_zero\":%s,\"current_volts_per_amp\":%.9g,\"current_valid\":%s,"
        "\"closed\":%s,\"open\":%s,\"opening_sign\":%d,\"learned\":%s,\"aux_position\":\"%s\","
        "\"adc_software_mode\":%s,\"adc_config_ok\":%s,\"current_window_qualified\":%s,"
        "\"current_metric\":\"sample_mean_20ms\",\"current_chain\":\"%s\",\"firmware\":\"6.2-s1\"}",json_number(z,c->current_zero),c->current_volts_per_amp,c->current_valid?"true":"false",
        json_number(closed,c->closed),json_number(open,c->open),c->opening_sign,c->learned?"true":"false",
        c->aux_position?"LO":"HI",c->adc_software_mode?"true":"false",c->adc_config_ok?"true":"false",
        c->current_window_qualified?"true":"false",c->bank==0?CHAIN_LOGGER:CHAIN_TEST);
    return b.ok;
}

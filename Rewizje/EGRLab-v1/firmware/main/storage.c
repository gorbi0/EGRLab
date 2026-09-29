#include "storage.h"
#include <stdio.h>
#include <stdarg.h>
#include <string.h>
#include <inttypes.h>
#include <sys/stat.h>
#include "sdkconfig.h"
#include "esp_heap_caps.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"

#define RING_COUNT (8*1024*1024/sizeof(sample_t))
#define BLOCK_COUNT 64
static sample_t *ring;
static uint64_t head,mark_at,mark_time;
static bool mark_pending,healthy;
static portMUX_TYPE mux=portMUX_INITIALIZER_UNLOCKED;
static QueueHandle_t events;
static FILE *samples,*eventfile;
static char directory[96];
static uint32_t crc_table[256];
static void crc_init(void){
    for(unsigned i=0;i<256;i++){uint32_t c=i;
        for(unsigned j=0;j<8;j++)c=(c>>1)^((c&1)?0xedb88320:0);crc_table[i]=c;}
}
uint32_t egr_crc32(const void *data,unsigned length){
    const uint8_t *p=data;uint32_t c=0xffffffff;
    for(unsigned i=0;i<length;i++)c=crc_table[(c^p[i])&255]^(c>>8);
    return c^0xffffffff;
}
static bool header(FILE *f,uint32_t session){
    struct __attribute__((packed)) {char magic[8];uint16_t version,bytes;
        uint32_t rate,record,flags;uint64_t session;} h={"EGRLOG1",1,32,CONFIG_EGR_SAMPLE_HZ,32,0,session};
    return fwrite(&h,1,sizeof h,f)==sizeof h;
}
static void unhealthy(void){portENTER_CRITICAL(&mux);healthy=false;portEXIT_CRITICAL(&mux);}
bool storage_ok(void){portENTER_CRITICAL(&mux);bool h=healthy;portEXIT_CRITICAL(&mux);return h;}
bool storage_init(uint32_t session,const profile_t *p){
    crc_init();ring=heap_caps_malloc(RING_COUNT*sizeof(sample_t),MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT);
    events=xQueueCreate(128,256);if(!ring||!events)return false;
    snprintf(directory,sizeof directory,"/sd/session_%"PRIu32,session);
    /* Never overwrite an existing session, even if NVS was restored. */
    if(mkdir(directory,0777)!=0)return false;
    char path[160];snprintf(path,sizeof path,"%s/samples.egr",directory);samples=fopen(path,"wb");
    snprintf(path,sizeof path,"%s/events.ndjson",directory);eventfile=fopen(path,"w");
    if(!samples||!eventfile||!header(samples,session))return false;
    snprintf(path,sizeof path,"%s/meta.json",directory);FILE *meta=fopen(path,"w");
    if(!meta)return false;
    fprintf(meta,"{\n\"schema\":1,\"firmware\":\"EGRLab-v1-A\",\"synthetic\":false,\"utc\":null,\n"
        "\"vehicle\":\"Kia Sportage 1.7 CRDi 2013\",\"valve_part\":\"28410-2A850\",\n"
        "\"sample_rate\":%d,\"supply_pin\":%d,\"adc_range\":10,\"shunt_bypass\":\"verify\",\n"
        "\"gain\":[",CONFIG_EGR_SAMPLE_HZ,(int)p->supply_pin);
    for(int i=0;i<8;i++)fprintf(meta,"%s%.9g",i?",":"",p->gain[i]);
    fprintf(meta,"],\"offset\":[");for(int i=0;i<8;i++)fprintf(meta,"%s%.9g",i?",":"",p->offset[i]);
    fprintf(meta,"],\"current_zero\":[2.5,2.5],\"current_volts_per_amp\":0.25,"
        "\"closed\":%.9g,\"open\":%.9g,\"qualified\":%s}\n",p->closed,p->open,p->qualified?"true":"false");
    bool good=!ferror(meta);if(fclose(meta)!=0)good=false;healthy=good;return good;
}
void storage_push(const sample_t *s){
    portENTER_CRITICAL(&mux);ring[head%RING_COUNT]=*s;head++;portEXIT_CRITICAL(&mux);
}
void storage_mark(uint64_t t){
    portENTER_CRITICAL(&mux);
    if(!mark_pending){mark_at=head;mark_time=t;mark_pending=true;}
    portEXIT_CRITICAL(&mux);
}
void storage_event(const char *format,...){
    if(!events)return;char line[256];va_list args;va_start(args,format);
    int n=vsnprintf(line,sizeof line,format,args);va_end(args);
    if(n<0||n>=(int)sizeof line||xQueueSend(events,line,0)!=pdTRUE)unhealthy();
}
static unsigned copy_records(uint64_t *cursor,sample_t *out,unsigned maximum,uint64_t ceiling){
    uint64_t dropped=0;
    portENTER_CRITICAL(&mux);
    uint64_t oldest=head>RING_COUNT?head-RING_COUNT:0;
    if(*cursor<oldest){dropped=oldest-*cursor;*cursor=oldest;healthy=false;}
    uint64_t end=head<ceiling?head:ceiling;
    unsigned n=end>*cursor?(unsigned)(end-*cursor):0;if(n>maximum)n=maximum;
    for(unsigned i=0;i<n;i++)out[i]=ring[(*cursor+i)%RING_COUNT];
    *cursor+=n;portEXIT_CRITICAL(&mux);
    if(dropped)storage_event("{\"type\":\"gap\",\"lost\":%"PRIu64"}",dropped);
    if(dropped&&n)out[0].flags|=1;return n;
}
static bool block(FILE *f,sample_t *data,unsigned n){
    struct __attribute__((packed)){char magic[4];uint32_t count,bytes,crc;} h={
        {'B','L','K','1'},n,n*sizeof(sample_t),egr_crc32(data,n*sizeof(sample_t))};
    return fwrite(&h,1,sizeof h,f)==sizeof h&&fwrite(data,sizeof(sample_t),n,f)==n;
}
void storage_writer(void *arg){
    (void)arg;sample_t buf[BLOCK_COUNT];char line[256];uint64_t cursor=0,eventcursor=0,eventend=0;
    uint64_t last_flush=0;FILE *capture=NULL;
    while(true){
        unsigned n=copy_records(&cursor,buf,BLOCK_COUNT,UINT64_MAX);
        if(n&&!block(samples,buf,n))unhealthy();
        portENTER_CRITICAL(&mux);
        bool pending=mark_pending;uint64_t at=mark_at,t=mark_time;
        if(pending&&!capture)mark_pending=false;
        portEXIT_CRITICAL(&mux);
        if(pending&&!capture){
            uint64_t pre=(uint64_t)CONFIG_EGR_SAMPLE_HZ*10;
            if(pre>RING_COUNT/2)pre=RING_COUNT/2;
            eventcursor=at>pre?at-pre:0;eventend=at+(uint64_t)CONFIG_EGR_SAMPLE_HZ*10;
            char path[160];snprintf(path,sizeof path,"%s/mark_%"PRIu64".egr",directory,t);
            capture=fopen(path,"wb");
            if(!capture||!header(capture,(uint32_t)t))unhealthy();
            storage_event("{\"type\":\"mark\",\"t_us\":%"PRIu64",\"pre_records\":%"PRIu64"}",t,at-eventcursor);
        }
        if(capture){
            unsigned m=copy_records(&eventcursor,buf,BLOCK_COUNT,eventend);
            if(m&&!block(capture,buf,m))unhealthy();
            if(eventcursor>=eventend){if(fclose(capture)!=0)unhealthy();capture=NULL;}
        }
        for(unsigned i=0;i<16&&xQueueReceive(events,line,0)==pdTRUE;i++){
            if(fprintf(eventfile,"%s\n",line)<0)unhealthy();
        }
        uint64_t now=esp_timer_get_time();
        if(now-last_flush>1000000){
            if(fflush(samples)||fflush(eventfile))unhealthy();
            if(capture&&fflush(capture))unhealthy();last_flush=now;
        }
        if(!n)vTaskDelay(pdMS_TO_TICKS(1));
    }
}

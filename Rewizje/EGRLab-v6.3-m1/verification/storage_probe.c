
#if defined(__TINYC__)
/* Older TinyCC lacks C11 _Static_assert: preserve the actual size check. */
#define _Static_assert(c,m) typedef char host_record_size_assert[(c)?1:-1]
#endif
#include "storage.h"
#include "trigger.h"
#include <stdio.h>
#include <string.h>
#include <stdarg.h>
#include <inttypes.h>
#include <float.h>
#include <math.h>
#define pdTRUE 1
static int events=1,healthy=1,lost_events,send_ok=1,write_ok=1;
static int sends,returned,writes;
static size_t sent_bytes,receive_bytes;
static char sent[4096];
static char *pending;
static control_t ctrl;
static session_config_t active_cfg;
static uint64_t esp_timer_get_time(void){return UINT64_MAX;}
static void unhealthy(void){healthy=0;}
static int xRingbufferSend(int handle,const void *p,size_t n,int ticks){
    (void)handle;(void)ticks;sends++;sent_bytes=n;memcpy(sent,p,n);return send_ok;
}
static void *xRingbufferReceive(int handle,size_t *n,int ticks){
    (void)handle;(void)ticks;char *p=pending;pending=NULL;*n=receive_bytes;return p;
}
static void vRingbufferReturnItem(int handle,void *p){(void)handle;(void)p;returned++;}
static bool write_event(const char *p){(void)p;writes++;return write_ok;}
/* Tryb bez karty (sink, 6.3-m1 M-11) w drain_events i zdarzenia miekkie CAN (F-08); bez PFAIL_N (M-10) nie ma closing. */
static bool sink;static unsigned soft_drops;
bool storage_event(const char *fmt, ...) {
    if (!events) return false;
    char line[STORAGE_EVENT_MAX];
    va_list args; va_start(args, fmt);
    int n = vsnprintf(line, sizeof line, fmt, args);
    va_end(args);
    /* Obciecie dawaloby niepoprawna linie NDJSON, ktora czytnik odrzuci jako
     * uszkodzona â€” a zapis raportowalby zdrowie. Zglaszamy blad. */
    if (n < 0 || n >= (int)sizeof line) { lost_events++; unhealthy(); return false; }
    if (xRingbufferSend(events, line, (size_t)n + 1, 0) != pdTRUE) {
        lost_events++; unhealthy(); return false;
    }
    return true;
}bool storage_event_soft(const char *fmt, ...) {
    if (!events) { soft_drops++; return false; }
    char line[STORAGE_EVENT_MAX];
    va_list args; va_start(args, fmt);
    int n = vsnprintf(line, sizeof line, fmt, args);
    va_end(args);
    if (n < 0 || n >= (int)sizeof line || xRingbufferSend(events, line, (size_t)n + 1, 0) != pdTRUE) {
        soft_drops++; return false;
    }
    return true;
}static bool drain_events(unsigned limit) {
    for (unsigned n = 0; n < limit; n++) {
        size_t bytes = 0;
        char *item = xRingbufferReceive(events, &bytes, 0);
        if (!item) break;
        bool ok = bytes > 0 && bytes <= STORAGE_EVENT_MAX && item[bytes - 1] == 0;
        if (ok && !sink) ok = write_event(item);
        vRingbufferReturnItem(events, item);
        if (!ok) { unhealthy(); return false; }
    }
    return true;
}static void log_summary(const summary_t *s) {
    char line[JSON_EVENT_MAX]; json_buf_t b; json_init(&b,line,sizeof line);
    json_add(&b,"{\"type\":\"summary\",\"t_us\":%" PRIu64 ",\"config_id\":%u,\"bank\":%d,\"n\":%u,\"ch\":[",
        s->t_us,s->config_id,s->bank,(unsigned)s->count);
    for(int j=0;j<8;j++) { char a[32],m[32],z[32];
        json_add(&b,"%s[%s,%s,%s]",j?",":"",json_number(a,s->min[j]),json_number(m,s->mean[j]),json_number(z,s->max[j])); }
    json_add(&b,"]}"); if(b.ok) storage_event("%s",line);
}static void log_campaign_locked(void) {
    campaign_t *p=&ctrl.soak; if(!p->point_ready) return;
    char n[7][32];
    storage_event("{\"type\":\"hotsoak_point\",\"t_us\":%" PRIu64 ",\"index\":%d,\"config_id\":%u,"
        "\"tc1\":%s,\"tc2\":%s,\"vbat\":%s,\"vbat_source\":\"vmotor_x1_3\",\"i_break_open\":%s,\"i_break_close\":%s,"
        "\"ms_10_90\":%s,\"ms_90_10\":%s,\"current_metric\":\"sample_mean_20ms\",\"metric_qualified\":%s}",
        (uint64_t)esp_timer_get_time(),p->done,active_cfg.id,json_number(n[0],p->t1),json_number(n[1],p->t2),
        json_number(n[2],p->vbat),json_number(n[3],p->i_break_open),json_number(n[4],p->i_break_close),
        json_number(n[5],p->ms_open),json_number(n[6],p->ms_close),ctrl.profile.current_window_qualified?"true":"false");
    p->point_ready=false;
}
#define CHECK(x) do{checks++;if(!(x)){printf("FAIL %d: %s\n",__LINE__,#x);return 1;}}while(0)
int main(void){int checks=0;
CHECK(storage_event("%s","{\"type\":\"mark\"}"));
CHECK(sent_bytes==strlen(sent)+1);CHECK(sent_bytes<256);CHECK(healthy);
char limit[STORAGE_EVENT_MAX+1];memset(limit,'x',sizeof limit);limit[STORAGE_EVENT_MAX-1]=0;
CHECK(storage_event("%s",limit));CHECK(sent_bytes==STORAGE_EVENT_MAX);
int before=sends;limit[STORAGE_EVENT_MAX-1]='x';limit[STORAGE_EVENT_MAX]=0;
CHECK(!storage_event("%s",limit));CHECK(sends==before);CHECK(lost_events==1 && !healthy);
healthy=1;send_ok=0;CHECK(!storage_event("{}"));CHECK(lost_events==2 && !healthy);send_ok=1;
healthy=1;summary_t s={0};s.t_us=UINT64_MAX;s.config_id=UINT16_MAX;s.bank=1;s.count=UINT32_MAX;
for(int j=0;j<8;j++){s.min[j]=-FLT_MAX;s.mean[j]=1.23456789e-30f;s.max[j]=FLT_MAX;}
log_summary(&s);CHECK(healthy);CHECK(sent_bytes>256 && sent_bytes<=STORAGE_EVENT_MAX);
printf("SUMMARY_JSON %s\n",sent);
ctrl.soak=(campaign_t){.point_ready=true,.done=200,.t1=59.987654f,.t2=120.12345f,.vbat=13.987654f,
    .i_break_open=3.1234567f,.i_break_close=2.1234567f,.ms_open=1234.5678f,.ms_close=1234.5678f};
active_cfg.id=UINT16_MAX;log_campaign_locked();CHECK(!ctrl.soak.point_ready);
CHECK(healthy);CHECK(sent_bytes>256 && sent_bytes<=STORAGE_EVENT_MAX);printf("HOTSOAK_JSON %s\n",sent);
s.mean[0]=NAN;log_summary(&s);CHECK(strstr(sent,"null")!=NULL);printf("NULL_JSON %s\n",sent);
pending=sent;receive_bytes=sent_bytes;CHECK(drain_events(16));CHECK(returned==1 && writes==1);
CHECK(drain_events(16));CHECK(returned==1 && writes==1);
pending=sent;receive_bytes=sent_bytes;write_ok=0;
CHECK(!drain_events(16));CHECK(returned==2 && writes==2 && !healthy);
write_ok=1;healthy=1;pending=sent;receive_bytes=0;
CHECK(!drain_events(16));CHECK(returned==3 && writes==2 && !healthy);
healthy=1;pending=sent;receive_bytes=STORAGE_EVENT_MAX+1;
CHECK(!drain_events(16));CHECK(returned==4 && writes==2 && !healthy);
healthy=1;pending=sent;receive_bytes=1;sent[0]='x';
CHECK(!drain_events(16));CHECK(returned==5 && writes==2 && !healthy);
healthy=1;sink=true;pending=sent;receive_bytes=sent_bytes;sent[0]='{';
CHECK(drain_events(16));CHECK(returned==6 && writes==2 && healthy);sink=false;
before=sends;CHECK(storage_event_soft("{\"type\":\"can\"}"));CHECK(sends==before+1 && soft_drops==0 && healthy);
send_ok=0;CHECK(!storage_event_soft("{}"));CHECK(soft_drops==1);CHECK(healthy);CHECK(lost_events==2);send_ok=1;
limit[STORAGE_EVENT_MAX-1]='x';limit[STORAGE_EVENT_MAX]=0;before=sends;
CHECK(!storage_event_soft("%s",limit));CHECK(sends==before && soft_drops==2 && healthy);
printf("Storage contracts: %d assertions OK\n",checks);return 0;}

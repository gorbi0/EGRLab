"""Compile actual storage send/drain and summary/hotsoak serializers with stubs.
Tests API contracts/error paths, not the FreeRTOS scheduler or SD hardware.
python tests/probe_storage.py --cc gcc --out verification
"""
import argparse,json,subprocess
from pathlib import Path

def function(text, signature):
    start=text.index(signature);begin=text.index('{',start);depth=1;i=begin+1
    while depth:
        depth+=(text[i]=='{')-(text[i]=='}');i+=1
    return text[start:i]

PRE=r'''
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
'''
POST=r'''
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
'''

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cc',default='gcc')
    p.add_argument('--out',type=Path,default=Path('verification'));a=p.parse_args()
    root=Path(__file__).parents[1];main=root/'firmware/main';a.out.mkdir(exist_ok=True,parents=True)
    storage=(main/'storage.c').read_text(encoding='utf-8');app=(main/'app_main.c').read_text(encoding='utf-8')
    source=PRE+function(storage,'bool storage_event(')+function(storage,'bool storage_event_soft(')+function(storage,'static bool drain_events(')
    source+=function(app,'static void log_summary(')+function(app,'static void log_campaign_locked(')+POST
    c=a.out/'storage_probe.c';c.write_text(source,encoding='utf-8');exe=a.out/'storage_probe.exe'
    tiny='tcc' in Path(a.cc).name
    extra=['-I',str(root/'verification/host-tcc-include')] if tiny else []
    cmd=[a.cc,'-std=c11',*extra,'-I',str(main),str(c),str(main/'jsonlog.c'),str(main/'control.c')]
    subprocess.run(cmd+([] if tiny else ['-lm'])+['-o',str(exe)],check=True)
    result=subprocess.run([str(exe.resolve())],check=True,capture_output=True,text=True)
    lengths={}
    for line in result.stdout.splitlines():
        if '_JSON ' in line:
            kind,body=line.split(' ',1);json.loads(body,parse_constant=lambda x:(_ for _ in ()).throw(ValueError(x)))
            lengths[kind]=len(body.encode())
    (a.out/'storage-results.txt').write_text(result.stdout+'JSON bytes: '+json.dumps(lengths)+'\n',encoding='utf-8')
    print(result.stdout,end='');print('JSON bytes:',lengths)

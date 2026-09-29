"""Compile the actual patched board_temperature with a register-bus mock and independent byte vectors."""
from pathlib import Path
import subprocess,os,json,sys
P=Path(__file__).resolve().parents[1];tmp=P/'output/host-tests';tmp.mkdir(parents=True,exist_ok=True)
s=(P/'firmware/board.c').read_text();a=s.index('esp_err_t board_temperature(');z=s.index('\n}',a)+2;fn=s[a:z]
head=r'''
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#define NAN (0.0f/0.0f)
static float fabsf(float x){return x<0?-x:x;}
static void esp_rom_delay_us(unsigned x){(void)x;}
#include <assert.h>
#include <stdlib.h>
#undef assert
#define assert(x) do { if (!(x)) { fprintf(stderr,"check failed at line %d\n",__LINE__); exit(2); } } while (0)
typedef int esp_err_t;
#define ESP_OK 0
#define ESP_ERR_INVALID_ARG 1
#define ESP_ERR_NOT_FOUND 2
#define ESP_ERR_INVALID_RESPONSE 3
typedef struct {int length; const void *tx_buffer;void *rx_buffer;} spi_transaction_t;
static int tc[2]={1,2}, fail_at=0,calls=0;
static uint8_t cfg0=0x91,cfg1=3,data[4]={1,0x90,0,0};
int spi_device_polling_transmit(int device,spi_transaction_t *t){
 const uint8_t *tx=t->tx_buffer;uint8_t *rx=t->rx_buffer;
 assert(device==1||device==2);calls++;
 if(calls==fail_at)return 99;
 if(t->length==24){assert(tx[0]==0x00);rx[1]=cfg0;rx[2]=cfg1;}
 else {assert(t->length==40);assert(tx[0]==0x0c);memcpy(rx+1,data,4);}
 return 0;
}
'''
tail=r'''
static int tests=0;
static void check(int ch,int expected,float temp,int flt){
 float value=123;uint8_t fault=88;calls=0;
 int rc=board_temperature(ch,&value,&fault);
 assert(rc==expected);assert(fault==flt);
 if(flt || rc)assert(value!=value);else assert(fabsf(value-temp)<0.00001f);
 tests++;
}
int main(void){
 check(0,0,25,0);check(1,0,25,0);
 data[0]=0xff;data[1]=0x58;data[2]=0;check(0,0,-10.5f,0);
 data[0]=0;data[1]=0;data[2]=0;check(0,0,0,0);
 data[2]=0x20;check(0,0,0.0078125f,0);
 data[0]=0x7f;data[1]=0xff;data[2]=0xe0;check(0,0,2047.9921875f,0);
 data[0]=0x80;data[1]=0;data[2]=0;check(0,0,-2048,0);
 data[0]=1;data[1]=0x90;data[2]=0;
 for(int i=0;i<8;i++){data[3]=(uint8_t)(1u<<i);check(0,0,0,data[3]);}
 data[3]=0;cfg0=0;cfg1=0;check(0,3,0,255);
 cfg0=0xff;cfg1=0xff;check(0,3,0,255);
 cfg0=0;cfg1=3;check(0,3,0,255);
 cfg0=0x91;cfg1=2;check(0,3,0,255);cfg1=3;
 data[2]=1;check(0,3,0,255);data[2]=0;
 fail_at=1;check(0,99,0,255);fail_at=2;check(0,99,0,255);fail_at=0;
 check(-1,1,0,255);check(2,1,0,255);tc[1]=0;check(1,2,0,255);
 uint8_t f;float v;assert(board_temperature(0,0,&f)==1);assert(board_temperature(0,&v,0)==1);tests+=2;
 printf("PASS %d actual-function cases\n",tests);return 0;
}
'''
cc=os.environ.get('EGRLAB_TCC','tcc')
results=[]
for label,body,expected in [('final',fn,True),('wrong-start-address',fn.replace('{0x0c,','{0x0b,'),False),('wrong-fault-byte',fn.replace('*fault = rx[4]','*fault = rx[3]'),False),('accept-floating-zero',fn.replace('if (cfg_rx[1] != 0x91 || cfg_rx[2] != 0x03) return ESP_ERR_INVALID_RESPONSE;',''),False)]:
 c=tmp/(label+'.c');exe=tmp/(label+'.exe');c.write_text(head+body+tail)
 subprocess.run([cc,str(c),'-o',str(exe)],check=True,capture_output=True)
 r=subprocess.run([str(exe)],capture_output=True,text=True)
 ok=r.returncode==0;assert r.returncode==(0 if expected else 2),(label,r.returncode,r.stdout,r.stderr)
 results.append({'case':label,'pass':ok if expected else not ok,'expected':'PASS' if expected else 'detected regression','output':r.stdout.strip()})
 try:exe.unlink()
 except PermissionError:pass # Windows scanner may retain the just-closed EXE; not a test failure.
assert '.cs_ena_pretrans = 2, .cs_ena_posttrans = 2' in s and 'vTaskDelay(pdMS_TO_TICKS(300))' in s
(P/'verification/temperature-tests.json').write_text(json.dumps({'results':results,'compiled_actual_function':True,'full_esp_idf_build':False,'hardware_tested':False},indent=2))
print(json.dumps(results,indent=2))


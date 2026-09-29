/* Host C11 test: cc -std=c11 -Wall -Wextra -I firmware/main
   tests/test_control.c firmware/main/control.c -lm -o test_control */
#include "control.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
static inputs_t good(uint64_t now){
    inputs_t i={.now=now,.sample_time=now,.interlock=true,.hw_armed=true,
        .storage_ok=true,.tc_ok=true,.t1=25};
    i.v[2]=2.5;i.v[3]=5;i.v[4]=0;i.v[5]=2.5;i.v[7]=12;return i;
}
int main(void){
    control_t c;control_init(&c);assert(c.state==SAFE);
    assert(!control_command(&c,"manual",.1f,50,0));
    assert(control_command(&c,"logger",0,0,0));
    assert(control_command(&c,"identify",0,0,0));
    for(uint64_t t=1;t<=2100001;t+=1000){inputs_t i=good(t);control_step(&c,&i);}
    assert(c.profile.supply_pin==5&&c.state==LOGGER);
    control_stop(&c);assert(!control_command(&c,"test",0,0,3000000));
    c.profile.qualified=true;assert(control_command(&c,"test",0,0,3000000));
    for(uint64_t t=3000001;t<3300000;t+=1000){inputs_t i=good(t);control_step(&c,&i);}
    assert(c.state==READY);
    assert(control_command(&c,"manual",.1f,50,3300000));
    inputs_t i=good(3310000);control_step(&c,&i);assert(c.duty>.09f);
    i.interlock=false;control_step(&c,&i);assert(c.state==FAULT&&c.duty==0);
    i.interlock=true;control_step(&c,&i);assert(c.state==FAULT);
    control_stop(&c);c.state=READY;assert(control_command(&c,"manual",.1f,50,4000000));
    i=good(4001000);i.v[5]=3;control_step(&c,&i);assert(c.state==FAULT);
    control_stop(&c);c.state=READY;assert(!control_command(&c,"manual",NAN,50,0));
    assert(!control_command(&c,"manual",.1f,251,0));
    c.state=READY;assert(control_command(&c,"manual",.1f,50,5000000));
    i=good(5100000);control_step(&c,&i);assert(c.state==READY&&c.duty==0);
    control_stop(&c);c.state=LOGGER;assert(control_command(&c,"identify",0,0,6000000));
    for(uint64_t t=6000001;t<8200000;t+=1000){i=good(t);i.v[3]=0;i.v[4]=5;control_step(&c,&i);}
    assert(c.profile.supply_pin==6);
    puts("control tests passed");return 0;
}

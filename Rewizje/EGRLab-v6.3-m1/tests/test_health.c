#include "control.h"
#include <stdio.h>
#include <string.h>
static int checks,failures;
#define CHECK(x) do { checks++; if(!(x)) { failures++; printf("FAIL line %d: %s\n",__LINE__,#x); } } while(0)
static inputs_t input(void) {
    inputs_t i={0};i.now=i.sample_time=1000000;
    i.storage_ok=i.adc_ok=i.drive_ok=i.tc_ok=true;   /* 6.3-m1: bez interlock / ARM / adapterow */
    i.v[CH_VBAT]=13.5f;i.v[CH_CURRENT]=2.5f;
    i.v[2]=5;i.v[3]=2.5f;i.v[4]=0;i.v[CH_SENS5V]=5;i.t1=i.t2=25;
    return i;
}
int main(void) {
    state_t states[]={SENSOR_CHECK,READY,MANUAL,GOTO,SWEEP,FRICTION,CYCLE};
    for(unsigned j=0;j<sizeof states/sizeof states[0];j++) {
        control_t c;control_init(&c);c.state=states[j];c.test_bank=c.sensor_on=true;
        c.profile.ch_supply=2;c.profile.ch_ground=4;c.profile.ch_feedback=3;
        c.profile.qualified=c.profile.learned=true;c.profile.closed=.1f;c.profile.open=.9f;
        c.deadline=3000000;c.duty=.1f;
        inputs_t i=input();i.sensor_fault=true;control_step(&c,&i);
        CHECK(c.state==FAULT);CHECK(c.duty==0);CHECK(!c.sensor_on);
        i.sensor_fault=false;i.now+=1000;i.sample_time=i.now;control_step(&c,&i);
        CHECK(c.state==FAULT);CHECK(!control_command(&c,"manual",.1f,50,i.now));
        CHECK(!control_command(&c,"test",0,0,i.now));
    }
#ifdef HAS_IO_GUARD
    uint64_t stamps[]={0,899999,1000001}; /* never read, stale, future */
    for(unsigned j=0;j<3;j++) {
        inputs_t i=input();control_guard_io(&i,stamps[j]);
        CHECK(i.sensor_fault);CHECK(i.io_stale);
        control_t c;control_init(&c);c.state=READY;c.test_bank=c.sensor_on=true;
        control_step(&c,&i);CHECK(c.state==FAULT);CHECK(!strcmp(c.fault,"INPUTS_STALE"));CHECK(!c.sensor_on);
    }
    inputs_t i=input();control_guard_io(&i,900000);
    CHECK(!i.sensor_fault && !i.io_stale);
#endif
    printf("health: %d assertions, %d failed\n",checks,failures);return failures!=0;
}

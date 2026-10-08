#include "control.h"
#include "measure.h"
#include <stdio.h>
#include <math.h>

/* Links the delivered control.c and measure.c unchanged. */
static void supply_case(float vbat) {
    control_t c; control_init(&c);
    c.profile.ch_supply=2; c.profile.ch_ground=4; c.profile.ch_feedback=3;
    c.profile.qualified=true;
    inputs_t in={0}; in.now=in.sample_time=1000000;
    in.adc_ok=in.storage_ok=in.drive_ok=in.tc_ok=true;
    in.t1=30; in.v[CH_CURRENT]=2.5; in.v[CH_VBAT]=vbat;
    printf("VBAT=%.2f wiring=%s ",vbat,control_test_wiring(&in) ? "reject" : "OK");
    int accepted=control_command(&c,"test",0,0,in.now);
    in.v[2]=in.v[7]=5; in.v[3]=2.5;
    control_step(&c,&in);
    in.now=in.sample_time=1250000; control_step(&c,&in);
    printf("test=%d state=%s fault=%s\n",accepted,control_name(c.state),c.fault?c.fault:"none");
}
int main(void) {
    supply_case(0); supply_case(13.5); supply_case(16.8);
    printf("RING_SECONDS_AT_2KSPS=%.5f\n", (double)((8*1024*1024)/40)/2000);
    overcurrent_t oc={0}; int trips=0;
    for(int j=0;j<2000;j++) if(overcurrent_sample(&oc,(j&1)?7.9f:8.1f,8,2)) trips++;
    printf("OC_ALTERNATING_8_1_7_9_2000_SAMPLES_TRIPS=%d\n",trips);
    return 0;
}

#include <stdio.h>
#include <string.h>
#include <math.h>
#include "control.h"
#include "jsonlog.h"
#include "measure.h"
#include "trigger.h"
#define CHECK(x) do { assertions++; if(!(x)) {printf("FAIL line %d: %s\n",__LINE__,#x);return 1;} } while(0)
int main(void) {
    int assertions=0; control_t c; control_init(&c);
    CHECK(profile_valid(&c.profile)); profile_t before=c.profile;
    CHECK(!profile_command(&c.profile,"cal 0 0 nan 1"));
    CHECK(!memcmp(&before,&c.profile,sizeof before));
    CHECK(!profile_command(&c.profile,"cal 0 8 1 0"));
    CHECK(!profile_command(&c.profile,"limits .2 5 60"));
    CHECK(!profile_command(&c.profile,"limits .2 1 100"));
    CHECK(!profile_command(&c.profile,"metric 1 garbage"));
    CHECK(profile_command(&c.profile,"cal 1 4 1.012345 0.0234567"));
    CHECK(profile_command(&c.profile,"currentcal 1 2.54321"));
    CHECK(!profile_command(&c.profile,"auxcal 1 1.01995 -0.003"));   /* 6.3-m1: M1 bez kanalu AUX */
    CHECK(profile_command(&c.profile,"limits .1 .5 60"));
    CHECK(profile_command(&c.profile,"metric 1"));
    CHECK(!profile_command(&c.profile,"icalok 0 1"));
    CHECK(!profile_command(&c.profile,"vcalok 0 1"));
    strcpy(c.profile.current_module[0],"IL_001");strcpy(c.profile.daq_module,"DAQ_001");
    CHECK(profile_command(&c.profile,"icalok 0 1"));CHECK(c.profile.current_calibrated[0]);
    CHECK(!profile_command(&c.profile,"iscal 0 .001220703125 0 .25"));  /* 6.3-m1: bez MCP3201 */
    CHECK(c.profile.current_calibrated[0]);
    CHECK(!profile_command(&c.profile,"ivpa 0 0"));CHECK(!profile_command(&c.profile,"ivpa 2 .25"));
    CHECK(profile_command(&c.profile,"ivpa 0 .2501"));
    CHECK(!c.profile.current_calibrated[0] && !c.profile.current_window_qualified && c.profile.current_volts_per_amp[0]==.2501f);
    CHECK(profile_command(&c.profile,"vcalok 0 1"));CHECK(c.profile.voltage_calibrated[0]);
    CHECK(profile_command(&c.profile,"cal 0 0 1 0"));CHECK(!c.profile.voltage_calibrated[0]);
    c.profile.ch_supply=3;c.profile.ch_ground=4;c.profile.ch_feedback=2;
    control_apply_ranges(&c.profile,true);
    CHECK(c.profile.range[3]==RANGE_10V);
    CHECK(c.profile.range[4]==RANGE_2V5);
    CHECK(c.profile.range[2]==RANGE_5V);
    session_config_t cfg; c.test_bank=true;
    control_build_config(&c,&cfg,65535,c.profile.range,true,true);
    for(int j=0;j<8;j++) {cfg.gain[j]=19.987654f;cfg.offset[j]=-1.987654f;}
    cfg.closed=NAN;cfg.open=NAN;
    memset(cfg.current_module,'M',sizeof cfg.current_module-1);cfg.current_module[sizeof cfg.current_module-1]=0;
    memset(cfg.daq_module,'D',sizeof cfg.daq_module-1);cfg.daq_module[sizeof cfg.daq_module-1]=0;
    memset(cfg.valve,'V',sizeof cfg.valve-1);cfg.valve[sizeof cfg.valve-1]=0;
    memset(cfg.adapter,'A',sizeof cfg.adapter-1);cfg.adapter[sizeof cfg.adapter-1]=0;
    memset(cfg.vehicle_id,'C',sizeof cfg.vehicle_id-1);cfg.vehicle_id[sizeof cfg.vehicle_id-1]=0;
    memset(cfg.session_note,'S',sizeof cfg.session_note-1);cfg.session_note[sizeof cfg.session_note-1]=0;
    char json[JSON_EVENT_MAX]; CHECK(json_config(json,sizeof json,&cfg,18446744073709551615ULL));
    CHECK(strlen(json)>512);CHECK(strstr(json,"nan")==NULL);CHECK(strstr(json,"null")!=NULL);
    char small[64];CHECK(!json_config(small,sizeof small,&cfg,0));
    puts(json); /* Python runner parses actual serializer output strictly. */
    cfg.range[0]=RANGE_UNKNOWN;CHECK(json_config(json,sizeof json,&cfg,1));
    CHECK(strstr(json,"\"full_scale\":[null")!=NULL);
    int16_t raw[8]={0,32760,0,0,-32768,0,0,0};CHECK(measurement_saturation(raw)==0x12);
    current_window_t window;current_window_reset(&window);float mean,rms;bool valid=false;
    for(int j=0;j<=40;j++) valid=current_window_add(&window,1+500*j,(j%2)?1:-1,&mean,&rms);
    CHECK(valid);CHECK(fabsf(mean)<.025f);CHECK(fabsf(rms-1)<.001f);
    CHECK(!current_window_add(&window,24001,1,&mean,&rms));CHECK(isnan(mean));
    CHECK(!current_window_add(&window,24501,NAN,&mean,&rms));
    cfg.id=71;cfg.bank=1;cfg.ch_supply=3;cfg.ch_ground=4;cfg.ch_feedback=2;cfg.current_valid=false;
    trigger_configure(&cfg,2000);float v[8]={0,0,2.5f,5,0,NAN,12,0};
    for(unsigned j=0;j<=2000;j++) trigger_sample(v,1+500*j);
    summary_t sum;CHECK(trigger_take_summary(&sum));CHECK(sum.config_id==71 && sum.bank==1);
    CHECK(sum.t_us-sum.start_us==1000000);CHECK(sum.valid_count[5]==0 && isnan(sum.mean[5]));
    CHECK(sum.valid_count[3]==2001 && fabsf(sum.mean[3]-5)<.001f);
    trigger_configure(&cfg,2000);trigger_sample(v,1);v[2]=3.5f;
    CHECK(!(trigger_sample(v,501)&TRIG_JUMP));CHECK(trigger_sample(v,1001)&TRIG_JUMP);
    CHECK(!(trigger_sample(v,1501)&TRIG_JUMP));
    /* 6.3-m1 M-06: programowe ograniczenie pradu z CH6 (zakres +-5 V, gain 1,0002, zero 2,5 V, 0,25 V/A). */
    #define RAW_FOR(amps) ((int16_t)lroundf((2.5f+.25f*(amps))/1.0002f/5.0f*32768.0f))
    CHECK(fabsf(overcurrent_amps(RAW_FOR(0),5,1.0002f,0,2.5f,.25f))<.01f);
    CHECK(fabsf(overcurrent_amps(RAW_FOR(3),5,1.0002f,0,2.5f,.25f)-3)<.01f);
    CHECK(fabsf(overcurrent_amps(RAW_FOR(-8.5f),5,1.0002f,0,2.5f,.25f)+8.5f)<.01f);
    CHECK(isinf(overcurrent_amps(32767,5,1.0002f,0,2.5f,.25f)));     /* nasycenie = poza zakresem */
    CHECK(isnan(overcurrent_amps(RAW_FOR(0),NAN,1.0002f,0,2.5f,.25f))); /* RANGE_UNKNOWN */
    CHECK(isnan(overcurrent_amps(RAW_FOR(0),5,1.0002f,0,2.5f,0)));
    overcurrent_t oc={0};
    CHECK(!overcurrent_sample(&oc,overcurrent_amps(RAW_FOR(8.5f),5,1.0002f,0,2.5f,.25f),8,2));
    CHECK(overcurrent_sample(&oc,overcurrent_amps(RAW_FOR(8.5f),5,1.0002f,0,2.5f,.25f),8,2));
    CHECK(overcurrent_sample(&oc,8.1f,8,2));                          /* zatrzask trwa, dopoki prad nie spadnie */
    CHECK(!overcurrent_sample(&oc,7.9f,8,2) && oc.over==0);
    CHECK(!overcurrent_sample(&oc,-8.5f,8,2));CHECK(!overcurrent_sample(&oc,1,8,2)); /* pojedyncza probka nie wylacza */
    CHECK(!overcurrent_sample(&oc,NAN,8,2));CHECK(overcurrent_sample(&oc,INFINITY,8,2)); /* nieznane = przekroczenie */
    CHECK(!overcurrent_sample(&oc,8,8,2));                            /* rowno limitowi - jeszcze nie */
    printf("runtime: %d assertions OK\n",assertions);return 0;
}

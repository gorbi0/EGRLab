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
    CHECK(profile_command(&c.profile,"auxcal 1 1.01995 -0.003"));
    CHECK(profile_command(&c.profile,"limits .1 .5 60"));
    CHECK(profile_command(&c.profile,"metric 1"));
    c.profile.ch_supply=3;c.profile.ch_ground=4;c.profile.ch_feedback=2;
    control_apply_ranges(&c.profile,true);
    CHECK(c.profile.range[3]==RANGE_10V);
    CHECK(c.profile.range[4]==RANGE_2V5);
    CHECK(c.profile.range[2]==RANGE_5V);
    session_config_t cfg; c.test_bank=true;
    control_build_config(&c,&cfg,65535,c.profile.range,true,true);
    for(int j=0;j<8;j++) {cfg.gain[j]=19.987654f;cfg.offset[j]=-1.987654f;}
    cfg.closed=NAN;cfg.open=NAN;
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
    printf("runtime: %d assertions OK\n",assertions);return 0;
}

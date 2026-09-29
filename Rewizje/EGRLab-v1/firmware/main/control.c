#include "control.h"
#include <math.h>
#include <string.h>

static float clamp(float x, float lo, float hi) { return fmaxf(lo,fminf(x,hi)); }
const char *control_name(state_t s) {
    static const char *names[]={"SAFE","LOGGER","IDENTIFY","SENSOR_CHECK","READY",
        "MANUAL","GOTO","SWEEP","FRICTION","CYCLE","THERMAL","FAULT"};
    return (unsigned)s < sizeof(names)/sizeof(names[0]) ? names[s] : "INVALID";
}
bool control_moving(const control_t *c) { return c->state>=MANUAL && c->state<=THERMAL; }
static void fail(control_t *c,const char *reason) {
    c->state=FAULT; c->duty=0; c->sensor_on=false; c->fault=reason;
}
void control_init(control_t *c) {
    memset(c,0,sizeof(*c)); c->profile.magic=0x45475231;
    c->profile.max_duty=.35f; c->profile.current_limit=1.5f;
    c->profile.temp_limit=60; c->profile.opening_sign=1;
    const float gains[]={4.06f,4.06f,1.01996f,1.01996f,1.01996f,1,1,6.0796f};
    memcpy(c->profile.gain,gains,sizeof gains);
}
void control_stop(control_t *c) {
    c->state=SAFE; c->duty=0; c->sensor_on=false; c->fault=NULL;
    c->stable_since=0; c->dwell_since=0;
}
static bool sensor_valid(const control_t *c,const inputs_t *in) {
    int g=c->profile.supply_pin==5?4:3, s=c->profile.supply_pin==5?3:4;
    if (c->profile.supply_pin!=5 && c->profile.supply_pin!=6) return false;
    float ref=in->v[s]-in->v[g], fb=in->v[2]-in->v[g];
    return isfinite(ref)&&isfinite(fb)&&in->v[g]>=-.2f&&in->v[g]<=.3f
        &&ref>=4.5f&&ref<=5.5f&&fb>=.2f&&fb<=4.8f&&!in->sensor_fault;
}
float control_ratio(const control_t *c,const inputs_t *in) {
    if (!sensor_valid(c,in)) return NAN;
    int g=c->profile.supply_pin==5?4:3, s=c->profile.supply_pin==5?3:4;
    return (in->v[2]-in->v[g])/(in->v[s]-in->v[g]);
}
float control_position(const control_t *c,const inputs_t *in) {
    float span=c->profile.open-c->profile.closed;
    return c->profile.learned && fabsf(span)>.2f ?
        (control_ratio(c,in)-c->profile.closed)/span : NAN;
}
bool control_command(control_t *c,const char *cmd,float a,int b,uint64_t now) {
    if(!strcmp(cmd,"stop")){control_stop(c);return true;}
    if(!strcmp(cmd,"logger")){
        control_stop(c);c->state=LOGGER;c->test_bank=false;return true;
    }
    if(!strcmp(cmd,"identify") && c->state==LOGGER){
        c->state=IDENTIFY;c->identify_since=0;c->identified=false;return true;
    }
    if(!strcmp(cmd,"test") && c->state==SAFE && c->profile.qualified
            &&(c->profile.supply_pin==5||c->profile.supply_pin==6)){
        c->test_bank=true;c->sensor_on=true;c->state=SENSOR_CHECK;
        c->started=now;c->deadline=now+2000000;c->stable_since=0;return true;
    }
    if(c->state!=READY) return false;
    if(!strcmp(cmd,"manual") && isfinite(a) && fabsf(a)<=c->profile.max_duty
            &&b>0&&b<=250){
        c->state=MANUAL;c->manual_duty=a;c->deadline=now+(uint64_t)b*1000;
    }else if(c->profile.learned && !strcmp(cmd,"goto") && a>=.1f&&a<=.9f){
        c->state=GOTO;c->target=a;c->deadline=now+2000000;
    }else if(c->profile.learned && (!strcmp(cmd,"sweep")||!strcmp(cmd,"thermal"))){
        c->thermal=!strcmp(cmd,"thermal");c->state=c->thermal?THERMAL:SWEEP;
        c->index=0;c->target=.1f;c->deadline=now+2000000;
    }else if(c->profile.learned&&!strcmp(cmd,"cycle")&&b>0&&b<=200){
        c->state=CYCLE;c->cycles=b;c->cycle_done=0;c->index=0;
        c->target=.1f;c->deadline=now+2000000;
    }else if(c->profile.learned&&!strcmp(cmd,"friction")&&(b==1||b==-1)){
        c->state=FRICTION;c->friction_sign=b;c->start_position=NAN;
        c->deadline=now+2000000;
    }else return false;
    c->started=now;c->stable_since=0;c->dwell_since=0;return true;
}
static int candidate(const inputs_t *in) {
    int result=0;
    for(int supply=5;supply<=6;supply++){
        int s=supply==5?3:4,g=supply==5?4:3;
        float ref=in->v[s]-in->v[g],fb=in->v[2]-in->v[g];
        if(isfinite(ref)&&isfinite(fb)&&in->v[g]>=-.2f&&in->v[g]<=.3f&&
                ref>=4.5f&&ref<=5.5f&&fb>=.2f&&fb<=4.8f){
            if(result) return 0; result=supply;
        }
    }return result;
}
void control_step(control_t *c,const inputs_t *in) {
    c->duty=0;
    bool fresh=in->now>=in->sample_time && in->now-in->sample_time<=10000;
    if(c->state==IDENTIFY){
        int k=fresh?candidate(in):0;
        if(!k||k!=c->identify_candidate){c->identify_since=in->now;c->identify_candidate=k;}
        if(k&&in->now-c->identify_since>=2000000){
            c->profile.supply_pin=k;c->identified=true;c->state=LOGGER;
        }return;
    }
    if(c->state==SAFE||c->state==LOGGER||c->state==FAULT)return;
    if(!fresh){fail(c,"ADC_STALE");return;}
    if(!in->interlock){fail(c,"INTERLOCK");return;}
    if(!in->storage_ok){fail(c,"STORAGE");return;}
    if(!isfinite(in->v[7])||in->v[7]<9||in->v[7]>16.5f){fail(c,"SUPPLY");return;}
    if(c->state==SENSOR_CHECK){
        if(sensor_valid(c,in)){
            if(!c->stable_since)c->stable_since=in->now;
            if(in->now-c->stable_since>=200000){c->state=READY;}
        }else c->stable_since=0;
        if(in->now>c->deadline)fail(c,"SENSOR_CHECK_TIMEOUT");
        return;
    }
    if(!sensor_valid(c,in)){fail(c,"SENSOR");return;}
    if(c->state==READY)return;
    if(!in->hw_armed){fail(c,"HARDWARE_NOT_ARMED");return;}
    float current=(in->v[5]-2.5f)/.25f;
    if(!isfinite(current)||fabsf(current)>c->profile.current_limit){fail(c,"CURRENT");return;}
    if(!in->tc_ok||!isfinite(in->t1)||in->t1>c->profile.temp_limit){fail(c,"TEMPERATURE");return;}
    if(c->state==MANUAL){
        if(in->now>=c->deadline){c->state=READY;return;}
        c->duty=c->manual_duty;return;
    }
    float pos=control_position(c,in);
    if(!isfinite(pos)||pos<-.05f||pos>1.05f){fail(c,"POSITION");return;}
    if(in->now>c->deadline){fail(c,"MOVE_TIMEOUT");return;}
    if(c->state==FRICTION){
        if(!isfinite(c->start_position))c->start_position=pos;
        if(fabsf(pos-c->start_position)>=.01f){
            if(!c->stable_since)c->stable_since=in->now;
            if(in->now-c->stable_since>=20000){c->state=READY;return;}
        }else c->stable_since=0;
        if((pos<=.1f&&c->friction_sign<0)||(pos>=.9f&&c->friction_sign>0)){
            fail(c,"FRICTION_RANGE");return;
        }
        float d=.01f*(float)((in->now-c->started)/50000);
        if(d>c->profile.max_duty){fail(c,"NO_BREAKAWAY");return;}
        c->duty=d*c->friction_sign*c->profile.opening_sign;return;
    }
    float error=c->target-pos;
    if(fabsf(error)<.02f){
        if(!c->stable_since)c->stable_since=in->now;
        if(in->now-c->stable_since>=100000){
            if(!c->dwell_since)c->dwell_since=in->now;
            uint64_t dwell=c->state==CYCLE?500000:300000;
            if(in->now-c->dwell_since>=dwell){
                if(c->state==GOTO){c->state=READY;return;}
                if(c->state==CYCLE){
                    c->index++;
                    if(c->index>=3 && c->index%2==1)c->cycle_done++;
                    if(c->cycle_done>=c->cycles){c->state=READY;return;}
                    c->target=c->index%2?.9f:.1f;
                }else{
                    c->index++;
                    if(c->index>=17){c->state=READY;return;}
                    c->target=c->index<=8?.1f+.1f*c->index:.9f-.1f*(c->index-8);
                }
                c->deadline=in->now+2000000;c->stable_since=0;c->dwell_since=0;
            }
        }
    }else {c->stable_since=0;c->dwell_since=0;}
    c->duty=fabsf(error)<.01f?0:clamp(.8f*error,-c->profile.max_duty,c->profile.max_duty)
        *c->profile.opening_sign;
}

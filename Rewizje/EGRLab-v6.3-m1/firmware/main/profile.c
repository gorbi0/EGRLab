#include "control.h"
#include <math.h>
#include <stdio.h>
#include <string.h>

bool profile_valid(const profile_t *p) {
    if (p->magic != EGR_PROFILE_MAGIC || p->version != EGR_PROFILE_VERSION) return false;
    int s=p->ch_supply, g=p->ch_ground, f=p->ch_feedback;
    if (!((s == -1 && g == -1 && f == -1) ||
        (s>=2 && s<=4 && g>=2 && g<=4 && f>=2 && f<=4 && s!=g && s!=f && g!=f))) return false;
    if (!isfinite(p->max_duty) || p->max_duty<=0 || p->max_duty>.35f ||
        !isfinite(p->current_limit) || p->current_limit<=0 || p->current_limit>3.5f ||
        !isfinite(p->temp_limit) || p->temp_limit<10 || p->temp_limit>60 || p->aux_position>1) return false;
    if (p->opening_sign!=1 && p->opening_sign!=-1) return false;
    if (p->learned && (s<2 || !isfinite(p->closed) || !isfinite(p->open) ||
        p->closed<=.02f || p->closed>=.98f || p->open<=.02f || p->open>=.98f ||
        fabsf(p->open-p->closed)<=.2f)) return false;
    if (!memchr(p->vehicle_id,0,24) || !memchr(p->session_note,0,24) || !memchr(p->daq_module,0,24)) return false;
    if (!memchr(p->valve,0,sizeof p->valve) || !memchr(p->adapter,0,sizeof p->adapter)) return false;
    for(int b=0;b<2;b++) {
        if (!memchr(p->current_module[b],0,24) ||
            !isfinite(p->current_volts_per_amp[b]) || p->current_volts_per_amp[b]<.05f || p->current_volts_per_amp[b]>2 ||
            !isfinite(p->current_adc_gain[b]) || p->current_adc_gain[b]<.0001f || p->current_adc_gain[b]>.01f ||
            !isfinite(p->current_adc_offset[b]) || fabsf(p->current_adc_offset[b])>.5f) return false;
        if (!isfinite(p->current_zero[b]) || p->current_zero[b]<1 || p->current_zero[b]>4 ||
            !isfinite(p->aux_gain[b]) || p->aux_gain[b]<.1f || p->aux_gain[b]>20 ||
            !isfinite(p->aux_offset[b]) || fabsf(p->aux_offset[b])>2) return false;
        for(int j=0;j<8;j++) if (!isfinite(p->gain[b][j]) || p->gain[b][j]<.1f ||
            p->gain[b][j]>20 || !isfinite(p->offset[b][j]) || fabsf(p->offset[b][j])>2) return false;
    }
    return true;
}

/* Candidate copy: invalid commands cannot partially edit the live profile. */
bool profile_command(profile_t *p, const char *line) {
    profile_t n=*p; char cmd[24], extra; int b,j; float a,z,t;
    if (sscanf(line,"%23s",cmd)!=1) return false;
    if (!strcmp(cmd,"cal") && sscanf(line,"%*s %d %d %f %f %c",&b,&j,&a,&z,&extra)==4
        && b>=0 && b<2 && j>=0 && j<8) { n.gain[b][j]=a; n.offset[b][j]=z; }
    else if (!strcmp(cmd,"currentcal") && sscanf(line,"%*s %d %f %c",&b,&a,&extra)==2
        && b>=0 && b<2) n.current_zero[b]=a;
    /* 6.3-m1 (M-04): bez MCP3201 - "iscal" i "auxcal" (brak AUX) odrzucane, zeby profil S1 nie trafil na M1.
     * Skala pradu CH6: ivpa <bank> <V/A>; napiecie wyjscia INA240 kalibruje "cal <bank> 5". */
    else if (!strcmp(cmd,"ivpa") && sscanf(line,"%*s %d %f %c",&b,&t,&extra)==2
        && b>=0 && b<2) { n.current_volts_per_amp[b]=t; n.current_calibrated[b]=false; n.qualified=false; n.current_window_qualified=false; }
    else if (!strcmp(cmd,"icalok") && sscanf(line,"%*s %d %d %c",&b,&j,&extra)==2
        && b>=0 && b<2 && (j==0 || j==1) && strcmp(n.current_module[b],"UNBOUND")) {
        n.current_calibrated[b]=j; n.qualified=false;
    }
    else if (!strcmp(cmd,"vcalok") && sscanf(line,"%*s %d %d %c",&b,&j,&extra)==2
        && b>=0 && b<2 && (j==0 || j==1) && strcmp(n.daq_module,"UNBOUND")) {
        n.voltage_calibrated[b]=j; n.qualified=false;
    }
    else if (!strcmp(cmd,"limits") && sscanf(line,"%*s %f %f %f %c",&a,&z,&t,&extra)==3) {
        n.max_duty=a; n.current_limit=z; n.temp_limit=t;
    } else if (!strcmp(cmd,"metric") && sscanf(line,"%*s %d %c",&b,&extra)==1 && (b==0 || b==1))
        n.current_window_qualified=b!=0;
    else return false;
    if (!profile_valid(&n)) return false;
    if (!strcmp(cmd,"cal")) {n.qualified=false;n.voltage_calibrated[b]=false;}
    *p=n; return true;
}

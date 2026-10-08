#include "control.h"
#include "jsonlog.h"
#include "trigger.h"
#include <stdio.h>
#include <string.h>
#include <math.h>
int main(void) {
  control_t ctrl; control_init(&ctrl);
  profile_t *p=&ctrl.profile;
  p->ch_supply=2;p->ch_ground=4;p->ch_feedback=3;
  p->current_valid[0]=p->current_calibrated[0]=p->voltage_calibrated[0]=true;
  p->learned=true;p->closed=.15f;p->open=.85f;
  strcpy(p->daq_module,"M1_SYNTHETIC");strcpy(p->current_module[0],"M1_SYNTHETIC");
  control_apply_ranges(p,true);
  session_config_t config;
  control_build_config(&ctrl,&config,1,p->range,true,true);
  char line[2048]; if(!json_config(line,sizeof line,&config,0))return 1;
  puts(line);
  /* Same invalid-vector construction as acquisition(): no accepted voltage calibration => NaN. */
  config.voltage_calibrated=false;
  float invalid[8];for(int i=0;i<8;i++)invalid[i]=NAN;
  trigger_configure(&config,2000);
  unsigned flags=trigger_sample(invalid,1000);
  printf("UNCALIBRATED_VECTOR_MASK=%u REF=%d FEEDBACK=%d\n",flags,!!(flags&TRIG_REF),!!(flags&TRIG_FB));
  config.voltage_calibrated=true;
  trigger_configure(&config,2000);
  float real_low_ref[8]={0,0,4.0f,2.0f,0,2.5f,13.5f,0};
  flags=trigger_sample(real_low_ref,1000);
  printf("REAL_LOW_REF_MASK=%u REF=%d FEEDBACK=%d\n",flags,!!(flags&TRIG_REF),!!(flags&TRIG_FB));
  /* Real profile_command: CH6 voltage calibration now belongs to current. */
  p->current_calibrated[1]=p->voltage_calibrated[1]=p->current_valid[1]=true;
  p->current_window_qualified=p->qualified=true;
  strcpy(p->current_module[1],"M1_SYNTHETIC");
  int cal_ok=profile_command(p,"cal 1 5 0.8 0.5");
  printf("AFTER_CH6_CAL accepted=%d vcal=%d ical=%d metric=%d qualified=%d zero=%.6f vpa=%.6f\n",
    cal_ok,p->voltage_calibrated[1],p->current_calibrated[1],p->current_window_qualified,p->qualified,p->current_zero[1],p->current_volts_per_amp[1]);
  int vcal_ok=profile_command(p,"vcalok 1 1");
  printf("AFTER_VCAL accepted=%d qualify_predicate_without_HARDWARE_ACCEPTED=%d\n",vcal_ok,
    p->voltage_calibrated[1] && p->current_calibrated[1] && p->current_window_qualified);
  printf("CAL_EXAMPLE input_ADC_V=2.75 actual_I_if_original_gain1_offset0=1A now_I=%.6fA zero_I=%.6fA\n",
    (2.75*p->gain[1][5]+p->offset[1][5]-p->current_zero[1])/p->current_volts_per_amp[1],
    (2.50*p->gain[1][5]+p->offset[1][5]-p->current_zero[1])/p->current_volts_per_amp[1]);
  return 0;
}

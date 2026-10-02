#include "measure.h"
#include <math.h>
#include <string.h>
void current_window_reset(current_window_t *w) { memset(w,0,sizeof *w); }
uint8_t measurement_saturation(const int16_t raw[8]) {
    uint8_t m=0;
    for(int j=0;j<8;j++) if(raw[j]>=32760 || raw[j]<=-32760) m|=(uint8_t)(1u<<j);
    return m;
}
bool current_window_add(current_window_t *w, uint64_t t, float i, float *mean, float *rms) {
    *mean=*rms=NAN;
    if(!isfinite(i)) { current_window_reset(w); return false; }
    if(w->count) {
        uint64_t last=w->p[(w->head+CURRENT_WINDOW_N-1)%CURRENT_WINDOW_N].t;
        if(t<=last || t-last>2000) current_window_reset(w);
    }
    w->p[w->head]=(current_point_t){t,i}; w->head=(w->head+1)%CURRENT_WINDOW_N;
    if(w->count<CURRENT_WINDOW_N) w->count++;
    double sum=0, squares=0; unsigned n=0; uint64_t oldest=t;
    for(unsigned k=0;k<w->count;k++) {
        current_point_t p=w->p[(w->head+CURRENT_WINDOW_N-1-k)%CURRENT_WINDOW_N];
        if(t-p.t>20000) break;
        sum+=p.i; squares+=(double)p.i*p.i; n++; oldest=p.t;
    }
    if(n<16 || t-oldest<18000) return false;
    *mean=(float)(sum/n); *rms=(float)sqrt(squares/n); return true;
}

#include "obd.h"
#include <math.h>
#include <stdio.h>
#include <string.h>
/* 6.2-s1 F-08: dekoder RPM (P10 R2 docs/INTEGRACJA.md) - ISO-TP SF wobec DLC, jeden ECU, brak danych != 0 rpm. */
static int checks,failures;
#define CHECK(x) do { checks++; if(!(x)) { failures++; printf("FAIL line %d: %s\n",__LINE__,#x); } } while(0)
static obd_result_t f(obd_rpm_t *s,uint32_t id,uint8_t dlc,const char *hex,uint64_t t,float *r) {
    uint8_t d[8]={0}; for(int i=0;i<8 && hex[2*i];i++) { unsigned v; sscanf(hex+2*i,"%2x",&v); d[i]=(uint8_t)v; }
    return obd_rpm_frame(s,id,false,false,dlc,d,t,r);
}
int main(void) {
    obd_rpm_t s; float r; obd_rpm_init(&s);
    CHECK(isnan(obd_rpm_now(&s,0)));                                        /* brak danych to NAN, nie 0 */
    CHECK(f(&s,0x7e8,8,"04410c1af8555555",1000,&r)==OBD_RPM_OK && fabsf(r-1726.0f)<1e-3f && s.ecu==0x7e8);
    CHECK(fabsf(obd_rpm_now(&s,1000+OBD_RPM_STALE_US)-1726.0f)<1e-3f);
    CHECK(isnan(obd_rpm_now(&s,1001+OBD_RPM_STALE_US)));                     /* nieaktualne po 1 s */
    CHECK(isnan(obd_rpm_now(&s,999)));                                      /* czas wstecz */
    CHECK(f(&s,0x7e8,8,"04410c0000555555",2000,&r)==OBD_RPM_OK && r==0.0f);  /* prawdziwe 0 rpm jest liczba */
    CHECK(f(&s,0x7e8,8,"03410c1af8555555",3000,&r)==OBD_BAD_LENGTH && isnan(r));   /* SF krotszy niz 41 0C A B */
    CHECK(f(&s,0x7e8,4,"04410c1a",3000,&r)==OBD_BAD_LENGTH);                /* deklarowane 4 bajty, DLC 4 */
    CHECK(f(&s,0x7e8,5,"04410c1af8",3000,&r)==OBD_RPM_OK);                  /* DLC 5 wystarcza */
    CHECK(f(&s,0x7e8,8,"06410c1af80d32aa",3000,&r)==OBD_RPM_OK);            /* wiele PID-ow w jednej odpowiedzi */
    CHECK(f(&s,0x7e8,8,"0f410c1af8555555",3000,&r)==OBD_BAD_LENGTH);        /* 15 > DLC 8 */
    CHECK(f(&s,0x7e8,8,"10144a0c1af85555",3000,&r)==OBD_NOT_RPM);           /* First Frame, nie SF */
    CHECK(f(&s,0x7e8,8,"04410d1af8555555",3000,&r)==OBD_NOT_RPM);           /* PID 0D */
    CHECK(f(&s,0x7e0,8,"04410c1af8555555",3000,&r)==OBD_NOT_RPM);           /* zapytanie, nie odpowiedz */
    CHECK(f(&s,0x7f0,8,"04410c1af8555555",3000,&r)==OBD_NOT_RPM);
    uint8_t d[8]={4,0x41,0x0c,0x1a,0xf8};
    CHECK(obd_rpm_frame(&s,0x7e8,true,false,8,d,3000,&r)==OBD_NOT_RPM);    /* ramka rozszerzona */
    CHECK(obd_rpm_frame(&s,0x7e8,false,true,8,d,3000,&r)==OBD_NOT_RPM);    /* RTR */
    CHECK(obd_rpm_frame(&s,0x7e8,false,false,2,d,3000,&r)==OBD_NOT_RPM);   /* DLC 2 */
    /* jeden ECU: pierwszy odpowiadajacy, nizszy identyfikator (0x7E8) wypiera wyzszy */
    obd_rpm_t e; obd_rpm_init(&e);
    CHECK(f(&e,0x7e9,8,"04410c0fa0555555",10,&r)==OBD_RPM_OK && e.ecu==0x7e9);
    CHECK(f(&e,0x7ea,8,"04410c0fa0555555",20,&r)==OBD_OTHER_ECU && e.other_ecu==1 && isnan(r));
    CHECK(f(&e,0x7e8,8,"04410c1f40555555",30,&r)==OBD_RPM_OK && e.ecu==0x7e8 && e.ecu_changes==1 && fabsf(r-2000.0f)<1e-3f);
    CHECK(f(&e,0x7e9,8,"04410c0fa0555555",40,&r)==OBD_OTHER_ECU && e.ecu==0x7e8);
    CHECK(e.accepted==2 && e.bad_length==0);
    printf("obd: %d assertions, %d failed\n",checks,failures);return failures!=0;
}

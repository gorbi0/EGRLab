#include "webui.h"
#include "sdkconfig.h"
#include <string.h>
#include <stdlib.h>

static webui_status_fn status_cb;
static webui_command_fn command_cb;
void webui_init(webui_status_fn s, webui_command_fn c) { status_cb = s; command_cb = c; }

#if CONFIG_EGR_WIFI_UI

#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_netif.h"
#include "esp_http_server.h"
#include "esp_log.h"
#include "nvs_flash.h"

static httpd_handle_t server;
static bool started;
static const char *TAG = "webui";

static const char PAGE[] =
"<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
"<title>EGRLab v4</title><style>"
"body{font:16px system-ui;margin:0;padding:12px;background:#111;color:#eee}"
"table{width:100%;border-collapse:collapse;margin:8px 0}"
"td{padding:6px 4px;border-bottom:1px solid #333}td:last-child{text-align:right;font-variant-numeric:tabular-nums}"
"button{font:16px system-ui;padding:12px;margin:3px;border:0;border-radius:8px;background:#2a4;color:#fff;min-width:74px}"
"button.stop{background:#c33;width:100%;padding:18px;font-size:20px}"
"#s{padding:6px;border-radius:6px;background:#222;text-align:center}"
"</style>"
"<div id=s>...</div><table id=t></table>"
"<div><button onclick=\"c('goto',0.1)\">10%</button><button onclick=\"c('goto',0.3)\">30%</button>"
"<button onclick=\"c('goto',0.5)\">50%</button><button onclick=\"c('goto',0.7)\">70%</button>"
"<button onclick=\"c('goto',0.9)\">90%</button></div>"
"<div><button onclick=\"c('manual',0.1,50)\">+ impuls</button><button onclick=\"c('manual',-0.1,50)\">- impuls</button>"
"<button onclick=\"c('friction',0,1)\">tarcie +</button><button onclick=\"c('friction',0,-1)\">tarcie -</button></div>"
"<div><button onclick=\"c('sweep')\">SWEEP</button><button onclick=\"c('mark')\">MARK</button></div>"
"<button class=stop onclick=\"c('stop')\">STOP</button>"
"<script>"
"function c(n,a,b){fetch('/api/cmd?c='+n+'&a='+(a||0)+'&b='+(b||0),{method:'POST'})}"
"const K=['stan','pozycja','ratio','prad_A','pin_zasil_V','pin_masa_V','pin_sygnal_V','VBAT_V','TC1_C','TC2_C','uzbrojony','adapter'];"
"async function u(){try{const r=await(await fetch('/api/status')).json();"
"document.getElementById('s').textContent=r.stan+(r.fault?' / '+r.fault:'');"
"document.getElementById('t').innerHTML=K.map(k=>'<tr><td>'+k+'</td><td>'+(r[k]==null?'brak danych':r[k])+'</td></tr>').join('')"
"}catch(e){document.getElementById('s').textContent='brak polaczenia'}}"
"setInterval(u,250);u()</script>";

static esp_err_t page_handler(httpd_req_t *r) {
    httpd_resp_set_type(r, "text/html; charset=utf-8");
    return httpd_resp_send(r, PAGE, HTTPD_RESP_USE_STRLEN);
}
static esp_err_t status_handler(httpd_req_t *r) {
    char json[1024] = "{}";
    if (status_cb) status_cb(json, sizeof json);
    httpd_resp_set_type(r, "application/json");
    return httpd_resp_send(r, json, HTTPD_RESP_USE_STRLEN);
}
static esp_err_t cmd_handler(httpd_req_t *r) {
    char query[96], name[24] = {0}, a[24] = {0}, b[24] = {0};
    bool ok = false;
    if (httpd_req_get_url_query_str(r, query, sizeof query) == ESP_OK) {
        httpd_query_key_value(query, "c", name, sizeof name);
        httpd_query_key_value(query, "a", a, sizeof a);
        httpd_query_key_value(query, "b", b, sizeof b);
        /* Biała lista: bez learn, save, bind i bez zmiany kalibracji. */
        static const char *allowed[] = {"stop","goto","manual","friction","sweep","cycle","mark",
                                        "hotsoak","hotsoak_stop", NULL};   /* bez learn, save, bind, zero, aux, bypass */
        for (int i = 0; allowed[i] && !ok; i++) ok = !strcmp(name, allowed[i]);
        if (ok && command_cb) ok = command_cb(name, strtof(a, NULL), atoi(b));
    }
    httpd_resp_set_type(r, "application/json");
    return httpd_resp_send(r, ok ? "{\"ok\":true}" : "{\"ok\":false}", HTTPD_RESP_USE_STRLEN);
}
/* Called only by the radio task, never while holding control_mutex.
 * One default AP interface and one Wi-Fi driver for the entire boot. */
static bool initialized;
static esp_netif_t *ap_netif;
void webui_start(void) {
    if (started) return;
    if (!initialized) {
        if (esp_netif_init()!=ESP_OK) return;
        esp_err_t e=esp_event_loop_create_default();
        if (e!=ESP_OK && e!=ESP_ERR_INVALID_STATE) return;
        if (!ap_netif) ap_netif=esp_netif_create_default_wifi_ap();
        if (!ap_netif) return;
        wifi_init_config_t cfg=WIFI_INIT_CONFIG_DEFAULT();
        if (esp_wifi_init(&cfg)!=ESP_OK) return;
        initialized=true;
    }
    wifi_config_t ap={0};
    strlcpy((char *)ap.ap.ssid,CONFIG_EGR_WIFI_SSID,sizeof ap.ap.ssid);
    strlcpy((char *)ap.ap.password,CONFIG_EGR_WIFI_PASSWORD,sizeof ap.ap.password);
    ap.ap.ssid_len=strlen(CONFIG_EGR_WIFI_SSID); ap.ap.max_connection=2;
    ap.ap.authmode=strlen(CONFIG_EGR_WIFI_PASSWORD)>=8?WIFI_AUTH_WPA2_PSK:WIFI_AUTH_OPEN;
    if(esp_wifi_set_mode(WIFI_MODE_AP)!=ESP_OK || esp_wifi_set_config(WIFI_IF_AP,&ap)!=ESP_OK
            || esp_wifi_start()!=ESP_OK) { esp_wifi_stop(); return; }
    httpd_config_t hc=HTTPD_DEFAULT_CONFIG(); hc.lru_purge_enable=true;
    if(httpd_start(&server,&hc)!=ESP_OK) { server=NULL; esp_wifi_stop(); return; }
    httpd_uri_t page={.uri="/",.method=HTTP_GET,.handler=page_handler};
    httpd_uri_t st={.uri="/api/status",.method=HTTP_GET,.handler=status_handler};
    httpd_uri_t cm={.uri="/api/cmd",.method=HTTP_POST,.handler=cmd_handler};
    if(httpd_register_uri_handler(server,&page)!=ESP_OK || httpd_register_uri_handler(server,&st)!=ESP_OK
            || httpd_register_uri_handler(server,&cm)!=ESP_OK) {
        httpd_stop(server); server=NULL; esp_wifi_stop(); return;
    }
    started=true;
    ESP_LOGI(TAG,"SoftAP %s, http://192.168.4.1/",CONFIG_EGR_WIFI_SSID);
}
void webui_stop(void) {
    if(server) { httpd_stop(server); server=NULL; }
    if(initialized) esp_wifi_stop();
    started=false;
}
bool webui_running(void) { return started; }

#else  /* CONFIG_EGR_WIFI_UI wyłączone */

void webui_start(void) {}
void webui_stop(void) {}
bool webui_running(void) { return false; }

#endif

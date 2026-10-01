idf_component_register(SRCS "app_main.c" "board.c" "control.c" "profile.c" "jsonlog.c" "measure.c" "storage.c" "trigger.c" "webui.c" "obd.c"
                       INCLUDE_DIRS "."
                       REQUIRES driver esp_timer esp_psram esp_ringbuf fatfs sdmmc nvs_flash esp_http_server esp_wifi esp_netif esp_event)

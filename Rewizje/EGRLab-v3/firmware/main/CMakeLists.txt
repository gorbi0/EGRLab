idf_component_register(SRCS "app_main.c" "board.c" "control.c" "storage.c" "trigger.c" "webui.c"
                       INCLUDE_DIRS "."
                       REQUIRES driver esp_timer esp_psram fatfs sdmmc nvs_flash esp_http_server esp_wifi esp_netif esp_event)

idf_component_register(SRCS "app_main.c" "board.c" "control.c" "profile.c" "jsonlog.c" "measure.c" "storage.c" "trigger.c" "webui.c" "obd.c"
                       INCLUDE_DIRS "."
                       REQUIRES driver esp_timer esp_psram esp_ringbuf fatfs sdmmc nvs_flash esp_http_server esp_wifi esp_netif esp_event esp_system esp_hw_support hal)
# 6.3-m1 M-06: DRIVE_EN i SENS_EN w dol na poczatku paniki (board.c, __wrap_esp_panic_handler).
target_link_libraries(${COMPONENT_LIB} INTERFACE "-Wl,--wrap=esp_panic_handler")

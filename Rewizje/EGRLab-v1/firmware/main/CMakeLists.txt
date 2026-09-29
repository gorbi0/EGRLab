idf_component_register(SRCS "app_main.c" "board.c" "control.c" "storage.c"
    INCLUDE_DIRS "." REQUIRES driver esp_timer nvs_flash fatfs sdmmc esp_psram)

#pragma once
#include <stdbool.h>
#include <stddef.h>

/* Opcjonalny podgląd i przyciski na telefonie. Radio wolno podnieść tylko
 * poza trybem LOGGER — decyduje o tym app_main, nie ten moduł. Fizyczny ARM
 * obowiązuje tak samo jak przy konsoli: to zdalny wyświetlacz, nie pilot. */
typedef void (*webui_status_fn)(char *out, size_t len);
typedef bool (*webui_command_fn)(const char *cmd, float a, int b);

void webui_init(webui_status_fn status, webui_command_fn command);
void webui_start(void);
void webui_stop(void);
bool webui_running(void);

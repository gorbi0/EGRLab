#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "control.h"
#define JSON_EVENT_MAX 2048
typedef struct { char *p; size_t cap, used; bool ok; } json_buf_t;
void json_init(json_buf_t *b, char *p, size_t cap);
void json_add(json_buf_t *b, const char *fmt, ...);
const char *json_number(char out[32], double value);
bool json_config(char *out, size_t cap, const session_config_t *c, uint64_t t);

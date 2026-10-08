/* Host-only shim for TinyCC 0.9.27's incompatible bundled x87 math.h.
 * No EGRLab source is modified. Only operations needed by the pure C tests. */
#ifndef REVIEW_MATH_H
#define REVIEW_MATH_H
#include <stdint.h>
static float review_float(uint32_t u) { union { uint32_t u; float f; } x; x.u=u; return x.f; }
#define NAN (review_float(0x7fc00000u))
#define INFINITY (review_float(0x7f800000u))
static int review_isnan(double x) { return x != x; }
static int review_isfinite(double x) { return x == x && x != (double)INFINITY && x != -(double)INFINITY; }
#define isnan(x) review_isnan(x)
#define isfinite(x) review_isfinite(x)
static float fabsf(float x) { union { uint32_t u; float f; } v; v.f=x; v.u &= 0x7fffffffu; return v.f; }
static float fminf(float a, float b) { return isnan(a) ? b : isnan(b) ? a : (a < b ? a : b); }
static float fmaxf(float a, float b) { return isnan(a) ? b : isnan(b) ? a : (a > b ? a : b); }
#endif
double sqrt(double);

/* Reviewer host compatibility only; firmware unchanged. */
#define isinf(x) (!review_isnan(x) && !review_isfinite(x))
static long lroundf(float x) { return (long)(x >= 0 ? x + .5f : x - .5f); }

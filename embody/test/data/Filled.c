/*
 * FilledTest module.
 *
 * Copyright 2015 Spencer Russell
 */

/************
 * Includes *
 ************/

#include <stdio.h>
#include <stdbool.h>
#include "OtherModule.h"

/*********************
 * Defines and Types *
 *********************/

#define BUFLEN 32
#define PI 3.14159

typedef struct {
    float x;
    float y;
} point2;

/********************************
 * Static Function Declarations *
 ********************************/

static void process(void);
static int *intfunc(float x);

/*********************************
 * Exported Function Definitions *
 *********************************/

point2 point2_add(point2 p1, point2 p2) {
}

float point2_length(point2 p) {
}

void fill_point2(point2 *p, float x, float y) {
}

void noop(void) {
}

void *something(void *thing) {
}

/*******************************
 * Static Function Definitions *
 *******************************/

static void process(void) {
}

static int *intfunc(float x) {
}

/*
 * FilledTest module.
 *
 * Copyright 2015 Spencer Russell
 */

#ifndef __FILLED_H
#define __FILLED_H

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

/**********************************
 * Exported Function Declarations *
 **********************************/

point2 point2_add(point2 p1, point2 p2);
float point2_length(point2 p);
void fill_point2(point2 *p, float x, float y);
void noop(void);
void *something(void *thing);

#endif // __FILLED_H

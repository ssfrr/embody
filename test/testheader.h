#ifndef TEST_HEADER_H
#define TEST_HEADER_H

/*
 * Copyright (c) Spencer Russell 2015
 */

typedef struct {
    float x;
    float y;
} point2;

point2 point2_add(point2 p1, point2 p2);
float point2_length(point2 p);
void fill_point2(point2 *p, float x, float y);
void noop(void);
void something(void *thing);

#endif

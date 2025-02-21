#include "Titik.h"

Titik fungsiTranslasi(Titik t, int x, int y){
    t.x  += x;
    t.y += y;
    return t;
}

void prosedurTranslasi(Titik *t, int x, int y){
    t -> x += x;
    t -> y += y;
}

Titik fungsiBuatTitik(Titik t, int x, int y){
    t.x = x;
    t.y = y;
    return t;
}

void prosedurBuatTitik(Titik *t, int x, int y){
    t -> x = x;
    t -> y = y;
}

void hapusTitik(Titik *t){
    t ->x = 0;
    t ->y= 0;
}
#include "Titik.h"
#include <stdio.h>
int main(){
    Titik a;
    prosedurBuatTitik(&a, 12, 3);
    printf("%d", a.x);
    return 0;
}
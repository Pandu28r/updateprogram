typedef struct
{
    int x;
    int y;
} Titik;

Titik fungsiTranslasi(Titik t, int x, int y);

void prosedurTranslasi(Titik *t, int x, int y);

Titik fungsiBuatTitik(Titik t, int x, int y);

void prosedurBuatTitik(Titik *t, int x, int y);

void hapusTitik(Titik *t);
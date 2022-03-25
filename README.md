# papada
Procesa e imprime estadisticas de los Campeonatos de Poker

usage: parsePokerData.py [-h] [-d INDIR] [-pd] [-pp] [-pu] [-r]

PArsePAkerDAta.py (PAPADA) - Procesa e imprime las estadisticas de los
Campeonatos de Poker

optional arguments:
  -h, --help            show this help message and exit
  -d INDIR, --inDir INDIR
                        Directorio con todos los archivos CSV
  -pd, --podios         Imprimir Puestos y Podios - Ordenados x Podios
  -pp, --podiosPrim     Imprimir Puestos y Podios - Ordenados x Primeros
                        Puestos
  -pu, --podiosUlt      Imprimir Puestos y Podios - Ordenados x Ultimos
                        Puestos
  -r, --rivalidades     Imprimir Rivalidades - Heads Up (2 o mas)
example: python parsePokerData.py -d torneos

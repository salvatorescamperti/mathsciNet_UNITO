1)Installare il programma che permette di settare tutti i file in formato Unix, così da non avere problemi di UNCODE

sudo apt-get install dos2unix

2)Applicare dos2unix ai files: installazione_iniziale.sh, variabili.ini, peano_unito_MATHSCINET.py. Esempio: portare il terminale nella cartella dove sta il file installazione_iniziale.sh e poi digitare

dos2unix installazione_iniziale.sh

3)Rendere i file installazione_iniziale,sh, peano_unito_MATHSCINET.py eseguibili, così che possano essere eseguiti come applicazioni. Per fare questo andare nella cartella dove sono e digitare chmod 777. Ad esempio, se siamo nella cartella dove sta il file installazione_iniziale.sh, digitare sul terminale

chmod 777 installazione_iniziale.sh

4)Lanciare installazione_iniziale.sh. Andare col terminale nella cartella dove sta installazione_iniziale.sh e digitare

./instalazzione_iniziale.sh

5)Creare un file PROGRAMMA.sh, aprirlo con un editor di testo e scrivere all'interno come prima riga (supponiamo che il file peano_unito_MATHSCINET.py sia alla locazione /home/salvatore/Desktop

#!/bin/bash
python3 /home/salvatore/Desktop/peano_unito_MATHSCINET.py compreso di nome file

6)Rendere eseguibile il file PROGRAMMA.sh (fare come al punto 3)

7)Cliccare tasto destro su PROGRAMMA.sh e scegliere di lanciarlo come programma

WARNING
Se viene cambiata la locazione del file peano_unito_MATHSCINET.py allora deve essere cambiata anche all'interno del file PROGRAMMA.sh.

Inoltre ricordarsi sempre che insieme a peano_unito_MATHSCINET.py si sposta anche la cartella risorse.

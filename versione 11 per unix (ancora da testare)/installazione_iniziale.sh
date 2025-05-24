#!/bin/bash

# File di log
LOG_FILE="log_install.txt"

# Elimina eventuali vecchi log
echo "Log di installazione - $(date)" > $LOG_FILE


# Funzione per installare pacchetti usando apt
install_with_apt() {
    sudo apt update
    sudo apt install -y "$1"
}

# Verifica se python3 è installato
if ! command -v python3 &> /dev/null; then
    echo "Python3 non è installato. Installazione in corso..." >> $LOG_FILE
    install_with_apt python3
else
    echo "Python3 è già installato." >> $LOG_FILE
fi

# Controllo se Python 3 è installato
if command -v python3 &>/dev/null; then
    echo "Python 3 è installato." >> $LOG_FILE
else
    echo "Python 3 non è installato. Installalo prima di continuare." >> $LOG_FILE
    echo "Errore: Python 3 non trovato. Esci."
    exit 1
fi

# Verifica se pip3 è installato
if ! command -v pip3 &> /dev/null; then
    echo "pip3 non è installato. Installazione in corso..." >> $LOG_FILE
    install_with_apt python3-pip
else
    echo "pip3 è già installato." >> $LOG_FILE
fi

# Elenco dei pacchetti richiesti
REQUIRED_PKG=(
    "sys"
    "stat"
    "os"
    "logging"
    "time"
    "math"
    "datetime"
    "configparser"
    "sqlite3"
    "csv"
    "tkinter"
    "pyautogui"
    "pandas"
    "selenium"
    "webdriver_manager"
    "beautifulsoup4"
    "flask"
    "webbrowser"
    "xlrd"
)

# Verifica e installazione dei pacchetti
for package in "${PACKAGES[@]}"; do
    echo "Controllo il pacchetto $package..." >> $LOG_FILE
    python3 -c "import $package" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "$package non è installato. Tentativo di installazione..." >> $LOG_FILE
        pip install $package >> $LOG_FILE 2>&1
        if [ $? -eq 0 ]; then
            echo "$package installato con successo." >> $LOG_FILE
        else
            echo "Errore durante l'installazione di $package." >> $LOG_FILE
        fi
    else
        echo "$package è già installato." >> $LOG_FILE
    fi
    echo "" >> $LOG_FILE
    sleep 1
    # Optional: aggiungi un ritardo per evitare problemi di rete o congestione

done

echo "Verifica completata. Controlla il file $LOG_FILE per i dettagli."

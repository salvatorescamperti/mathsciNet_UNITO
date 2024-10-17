#!/bin/bash

# Funzione per installare pacchetti usando apt
install_with_apt() {
    sudo apt update
    sudo apt install -y "$1"
}

# Verifica se python3 è installato
if ! command -v python3 &> /dev/null; then
    echo "Python3 non è installato. Installazione in corso..."
    install_with_apt python3
else
    echo "Python3 è già installato."
fi

# Verifica se pip3 è installato
if ! command -v pip3 &> /dev/null; then
    echo "pip3 non è installato. Installazione in corso..."
    install_with_apt python3-pip
else
    echo "pip3 è già installato."
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
    "selenium"
    "webdriver_manager"
    "tkinter"
    "pyautogui"
    "pandas"
    "beautifulsoup4"
)

# Funzione per installare pacchetti mancanti
for pkg in "${REQUIRED_PKG[@]}"; do
    if python3 -c "import ${pkg}" &> /dev/null; then
        echo "Il pacchetto $pkg è già installato."
    else
        echo "Il pacchetto $pkg non è installato. Installazione in corso..."
        if [[ "$pkg" == "configparser" ]]; then
            sudo apt-get install -y python3-configparser
        elif [[ "$pkg" == "beautifulsoup4" ]]; then
            sudo apt-get install -y python3-bs4
        elif [[ "$pkg" == "tkinter" ]]; then
            sudo apt-get install -y python3-tk
        else
            pip3 install "$pkg"
        fi
    fi
done

echo "Verifica completata. Tutti i pacchetti necessari sono installati."


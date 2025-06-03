FROM python:3.10-slim

# Installa pacchetti di sistema necessari
RUN apt-get update && apt-get install -y \
    wget gnupg curl unzip \
    libnss3 libxss1 libasound2 libatk-bridge2.0-0 libgtk-3-0 \
    fonts-liberation libappindicator3-1 libu2f-udev \
    && rm -rf /var/lib/apt/lists/*

# Aggiunge il repository di Google Chrome e installa Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Directory di lavoro
WORKDIR /app

# Copia requirements e installa dipendenze Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia il resto dei file
COPY . .

# Crea cartella per gli screenshot
RUN mkdir -p /app/screen

# Comando di avvio
CMD ["python", "peano_unito_MATHSCINET.py"]

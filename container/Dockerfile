FROM python:3.10-slim

# Evita prompt interattivi
ENV DEBIAN_FRONTEND=noninteractive

# Installa pacchetti di sistema necessari
RUN apt-get update && apt-get install -y \
    wget curl gnupg unzip \
    libnss3 libxss1 libasound2 libatk-bridge2.0-0 libgtk-3-0 \
    fonts-liberation libu2f-udev xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Aggiunge il repository di Google Chrome in modo moderno
RUN mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://dl.google.com/linux/linux_signing_key.pub \
       | gpg --dearmor -o /etc/apt/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-chrome.gpg] \
       http://dl.google.com/linux/chrome/deb/ stable main" \
       > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Directory di lavoro
WORKDIR /app

# Copia requirements e installa dipendenze Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia il resto dei file
COPY . .

# Crea cartella per screenshot
RUN mkdir -p /app/screen

# Comando di avvio
CMD ["python", "peano_unito_MATHSCINET.py"]

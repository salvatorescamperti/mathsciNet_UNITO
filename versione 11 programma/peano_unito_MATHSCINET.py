#!/usr/bin/env python
import sys
import stat
import os
import logging
import time
import math
import datetime
import configparser
import sqlite3 as sl
import csv
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import pyautogui
import pandas as pd
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver import EdgeOptions, ChromeOptions
from selenium.webdriver.common.keys import Keys
from functools import partial
from bs4 import BeautifulSoup
from tkinter import Toplevel

class MathscinetScraper:
    """
    Classe per il WebScraping di riviste su MathSciNet.
    Con priorità alla stabilità (chiusure sicure di driver/DB/GUI)
    e inversione della logica dei quartili (Q4 > Q3 > Q2 > Q1).
    """

    def __init__(self):
        """Inizializzazione: carica la config, setup logging, tkinter root, ecc."""
         # Carichiamo config e impostiamo logging
        self.config = configparser.ConfigParser()
        self.application_path = self.determina_path_ini()
         # Impostiamo logging
        log_path = os.path.join(self.application_path, "log.txt")
        logging.basicConfig(
            filename=log_path,
            level=logging.DEBUG,
            format="%(asctime)s | Message: %(message)s",
            filemode="w",
        )

        # Inizializziamo la GUI base, nascosta
        self.root = tk.Tk()
        self.root.withdraw()

        print(f"Path variabili.ini: {os.path.join(self.application_path, "risorse","variabili.ini")}")
        if os.path.exists(os.path.isdir(os.path.join(self.application_path, "risorse","variabili.ini"))):
            self.config.read(os.path.join(self.application_path, "risorse","variabili.ini"))
        else:
            self.verbose_print(f"Non trovato il file varibili.ini")

       
        # Leggiamo dal file di config
        self.browser = self.config['DEFAULT']['browser']
        self.driverPath = ""
        if self.config['DEFAULT']['driverPath'] == "True":
            fileName = filedialog.askopenfilename(
                filetypes=[("Eseguibili", ".exe")],
                title="Selezionare il driver"
            )
            self.driverPath = fileName

        self.tempo_singola_ricerca = float(self.config['DEFAULT']['tempo_singola_ricerca'])
        self.tempo_attesa_caricamento = float(self.config['DEFAULT']['attesa_per_caricamento'])
        self.colonna_eISSN = self.config['DEFAULT']['colonna_eISSN']
        self.colonna_pISSN = self.config['DEFAULT']['colonna_pISSN']
        self.colonnaTitolo = self.config['DEFAULT']['colonnaTitolo']
        self.carattereDelimitatorecsv = self.config['DEFAULT']['carattereDelimitatorecsv']
        self.divisionePercentile = True

        #QUI è DOVE CAMBIARE PER LE COLONNE
        # Possibilità di settori
        #self.ask_settori(self.root)
        self.ask_colonne(self.root)



        # Anni selezionati (GUI)
        self.anniSelezionati = self.get_years_range(self.root)

        try:
           if not os.path.exists(os.path.isdir(os.path.join(self.application_path, "risorse","mathscinet_databse.db"))):
               self.verbose_print(f"non trovato il file oppure errore nella connessione a mathscinet_databse.db: {e}")
           self.con = sl.connect(os.path.join(self.application_path, "risorse","mathscinet_databse.db"))
        except Exception as e:
            self.verbose_print(f"non trovato il file oppure errore nella connessione a mathscinet_databse.db: {e}")

        # Apriamo la connessione DB
        self.cur = self.con.cursor()

        # Variabili per file e output
        self.files = {}
        self.outputPath = ""

        #settori default
        self.settori = self.config['DEFAULT']['settori'].split(',')
        # Possibilità di settori
        self.ask_settori(self.root)
        # Selezione di eventuali file per i settori
        self.seleziona_file_settori()

        # Selezione cartella output
        self.info(self.root, "Seleziona cartella output", "Selezionare la cartella di output")
        self.outputPath = filedialog.askdirectory(title="Seleziona cartella output")

        self.driver = None  # webdriver Selenium
        self.root.attributes("-topmost", False)

        # Percentili di default
        self.percentiles = [10, 25, 50, 75]

        # Possibilità di personalizzarli
        self.ask_percentiles(self.root)

        

        # Fine init
        self.verbose_print("Inizializzazione completata, pronto per eseguire.")

    # -----------------------------------------------
    # Chiusura sicura di driver, DB e GUI
    # -----------------------------------------------
    def close_all(self, force_exit=True):
        """
        Chiude driver, DB e GUI in modo sicuro.
        Se force_exit = True, chiude l'intero script con sys.exit(0).
        """
        self.verbose_print("Chiusura risorse (driver, DB, GUI).")
        # chiusura driver
        try:
            if self.driver is not None:
                self.driver.close()
                self.driver.quit()
        except Exception as e:
            self.verbose_print(f"Errore in chiusura driver: {e}")

        # chiusura DB
        try:
            if self.con is not None:
                self.con.close()
        except Exception as e:
            self.verbose_print(f"Errore in chiusura DB: {e}")

        # distrugge la GUI
        try:
            self.root.destroy()
        except:
            pass

        if force_exit:
            sys.exit(0)

    # -----------------------------------------------
    # GUI per personalizzare percentili
    # -----------------------------------------------
    def ask_percentiles(self,root):
        """
        Chiede all'utente via tkinter se vuole modificare i percentili di default.
        Se dice di sì, richiede 4 valori in ordine crescente (0 < p1 < p2 < p3 < p4 < 100).
        Se l'utente inserisce valori non validi, ripete la procedura.
        """
        answer = self.chiedisino(root,"Vuoi modificare i percentili di default (p1 = 10 quindi top10%, p2 = 25 quindi Q1<=25%, p3 = 50 quindi 25%<Q2<=50%, p4 = 75 quindi 50%<Q3<=75%, Q4>75%)?", title="Percentili personalizzati", color_si="red",color_no="green",geometria="450x300")
        
        if not answer:
            self.verbose_print("Mantengo i percentili di default: [10, 25, 50, 75].")
            return

        while True:
            try:
                msg = ("Inserisci i 4 valori di cutoff percentile separati da virgola.\n"
                       "Esempio: 10,25,50,75\n\n"
                       "ATTENZIONE: Q4 è il quartile più 'alto' (peggiore) che sarà la parte rimanente. ")
                user_input = simpledialog.askstring(
                    "Personalizza percentili",
                    msg,
                    parent=self.root
                )
                if user_input is None:
                    # annullato => manteniamo i default
                    self.verbose_print("L'utente ha annullato, mantengo i percentili di default.")
                    return

                new_p = [int(x.strip()) for x in user_input.split(",")]
                if len(new_p) != 4:
                    raise ValueError("Devi inserire esattamente 4 valori.")
                new_p.sort()
                if new_p[0] <= 0 or new_p[3] >= 100:
                    raise ValueError("I percentili devono essere compresi tra 1 e 99.")
                self.percentiles = new_p
                self.verbose_print(f"Percentili modificati con successo in: {self.percentiles}")
                return
            except Exception as e:
                messagebox.showerror("Errore Percentili", f"Valori invalidi: {e}\nRiprova.")


     #--------------------------------------
    #GUI per personalizzare settori
    #-----------------------------------
    def ask_colonne(self,root):
        """
        Chiede all'utente via tkinter se vuole modificare le colonne dei file
        """
        answer = self.chiedisino(root,f"Vuoi modificare le colonne di default ({self.colonna_eISSN},{self.colonna_pISSN}, {self.colonnaTitolo}) \noppure il carattere delimitatore del csv {self.carattereDelimitatorecsv}?", title="Settori personalizzati", color_si="red",color_no="green",geometria="450x300")
        
        if not answer:
            self.verbose_print("Mantengo default.")
            return

        while True:
            try:
                msg = ("Inserisci i nomi delle colonne separati da virgola e senza spazi, 'titolo,p_issn,e_issn'.\nSe i nomi delle colonne contengono spazi, toglierli dai file e poi continuare.\n"
                       "Esempio: Colonnatitolo,PISSN,EISSN")
                user_input = simpledialog.askstring(
                    "Personalizza colonne",
                    msg,
                    parent=self.root
                )
                if user_input is None:
                    # annullato => manteniamo i default
                    self.verbose_print("L'utente ha annullato, mantengo default.")
                    return

                new_p = [x.strip() for x in user_input.split(",")]
                self.colonnaTitolo = new_p[0].replace(" ","")
                self.colonna_pISSN = new_p[1].replace(" ","")
                self.colonna_eISSN = new_p[2].replace(" ","")
                self.verbose_print(f"Settori modificati con successo in: {self.colonnaTitolo},{self.colonna_pISSN},{self.colonna_eISSN}")   

                msg = ("Inserisci il carattere delimitatore del csv senza mettere spazi.\n"
                       "Esempio: ;")
                user_input = simpledialog.askstring(
                    "Personalizza selimitatore",
                    msg,
                    parent=self.root
                )
                if user_input is None:
                    # annullato => manteniamo i default
                    self.verbose_print("L'utente ha annullato, mantengo default.")
                    return

                self.carattereDelimitatorecsv = user_input.replace(" ","")
                self.verbose_print(f"Delimitatore modificato con successo in: {self.carattereDelimitatorecsv}")
                self.root.attributes("-topmost", True)
                self.info(
                    self.root,
                    f"Nuove colonne: {self.colonnaTitolo},{self.colonna_pISSN},{self.colonna_eISSN}\nNuovo delimitatore: {self.carattereDelimitatorecsv}",
                    "Cambio colonne e delimitatore"
                )
                return
            except Exception as e:
                messagebox.showerror("Errore settori", f"Valori invalidi: {e}\nRiprova.")

    # -----------------------------------------------
    #--------------------------------------
    #GUI per personalizzare settori
    #-----------------------------------
    def ask_settori(self,root):
        """
        Chiede all'utente via tkinter se vuole modificare i settori
        """
        answer = self.chiedisino(root,f"Vuoi modificare i settori di default ({self.settori})?", title="Settori personalizzati", color_si="red",color_no="green",geometria="450x300")
        
        if not answer:
            self.verbose_print("Mantengo i settori di default.")
            return

        while True:
            try:
                msg = ("Inserisci i settori separati da una virgola.\n"
                       "Esempio: MAT01,MAT02A,MAT03B")
                user_input = simpledialog.askstring(
                    "Personalizza settori",
                    msg,
                    parent=self.root
                )
                if user_input is None:
                    # annullato => manteniamo i default
                    self.verbose_print("L'utente ha annullato, mantengo i settori di default.")
                    return

                new_p = [x.strip() for x in user_input.split(",")]
                self.settori = new_p
                self.verbose_print(f"Settori modificati con successo in: {self.settori}")
                self.root.attributes("-topmost", True)
                self.info(
                    self.root,
                    f"Nuovi settori: {self.settori}",
                    "Cambio colonne e delimitatore"
                )
                return
            except Exception as e:
                messagebox.showerror("Errore settori", f"Valori invalidi: {e}\nRiprova.")

    # -----------------------------------------------

    # -----------------------------------------------
    # Funzione di stampa/LOG centralizzata
    # -----------------------------------------------
    def verbose_print(self, msg):
        """Stampa su console e logga allo stesso tempo."""
        if isinstance(msg, str):
            print(msg)
            logging.critical(msg)
        else:
            print(str(msg))
            logging.critical(str(msg))

    # -----------------------------------------------
    # Metodi di utilità
    # -----------------------------------------------
    def determina_path_ini(self):
        """Determiniamo il path giusto per il file delle risorse."""
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.dirname(__file__)
        else:
            application_path = os.getcwd()
        return application_path

    def get_years_range(self, root):
        """
        Funzione per chiedere input dell'utente con finestre di dialogo:
        Ritorna lista [start_year, ..., end_year].
        """
        def valid_year(year):
            return 1900 <= year <= 3000

        while True:
            self.root.attributes("-topmost", True)
            start_year = simpledialog.askinteger(
                "Anno di inizio",
                "Inserisci l'anno di inizio raccolta (tra 1900 e 3000):",
                parent=root
            )
            end_year = simpledialog.askinteger(
                "Anno di fine",
                "Inserisci l'anno di fine raccolta (tra 1900 e 3000):",
                parent=root
            )

            if start_year is None or end_year is None:
                messagebox.showerror("Errore", "Inserimento annullato.", parent=root)
                self.close_all(force_exit=True)

            if not valid_year(start_year) or not valid_year(end_year):
                messagebox.showerror(
                    "Errore",
                    "Gli anni devono essere compresi tra 1900 e 3000.",
                    parent=root
                )
                continue
            elif start_year > end_year:
                messagebox.showerror(
                    "Errore",
                    "L'anno di inizio deve essere minore o uguale all'anno di fine.",
                    parent=root
                )
                continue
            else:
                return list(range(start_year, end_year + 1))

    def info(self, root, message, title="ShowInfo"):
        """Mostra una info box su tkinter."""
        self.root.attributes("-topmost", True)
        messagebox.showinfo(title, message, parent=root)

    # def chiedisino(self, root, message, title="ShowInfo"):
    #     """Chiede yes/no su tkinter, ritorna boolean."""
    #     self.root.attributes("-topmost", True)
    #     risposta = messagebox.askyesno(title, message, parent=root)
    #     return risposta

    def chiedisino(self, root, message, title="ShowInfo", color_si="green",color_no="red",geometria="300x150"):
        """Chiede yes/no su tkinter, ritorna boolean."""
        # Creazione della finestra personalizzata
        dialog = Toplevel(root)
        dialog.title(title)
        dialog.attributes("-topmost", True)  # Mantieni in primo piano
        dialog.geometry(geometria)
        dialog.grab_set()  # Blocca interazioni con la finestra principale

        # Messaggio
        tk.Label(dialog, text=message, wraplength=250, padx=10, pady=10).pack()

        # Variabile per la risposta
        risposta = tk.BooleanVar(value=None)

        # Pulsanti personalizzati
        def chiudi_si():
            risposta.set(True)
            dialog.destroy()

        def chiudi_no():
            risposta.set(False)
            dialog.destroy()

        tk.Button(dialog, text="Sì", command=chiudi_si, bg=color_si, fg="white", width=10).pack(side=tk.LEFT, padx=20, pady=10)
        tk.Button(dialog, text="No", command=chiudi_no, bg=color_no, fg="white", width=10).pack(side=tk.RIGHT, padx=20, pady=10)

        # Attendi la chiusura della finestra
        dialog.wait_window(dialog)
        return risposta.get()

    # -----------------------------------------------
    # Selezione file settori
    # -----------------------------------------------
    def seleziona_file_settori(self):
        """
        Esempio: chiede se vogliamo selezionare il file per alcuni settori (es. "MAT01").
        Aggiunge i file selezionati a self.files
        """
        
        for x in self.settori:
            self.verbose_print(f"Richiesta selezione files per settore {x}")
            answer = self.chiedisino(
                self.root,
                f"Vuoi selezionare il file per il settore {x}?",
                "Seleziona il file"
            )
            if answer:
                fileName = filedialog.askopenfilename(
                    filetypes=[("Excel files e CSV", ".xlsx .xls .csv")],
                    title=f"Selezionare file per il settore {x}"
                )
                if fileName:
                    # Evitiamo duplicati
                    if fileName not in self.files.values():
                        self.files[x] = fileName
                    self.verbose_print(fileName)
                    self.verbose_print(self.files)

    # -----------------------------------------------
    # Parsing HTML con BeautifulSoup
    # -----------------------------------------------
    def parse_html_table(self, html_str):
        """
        Parsea una tabella HTML e ritorna una lista di liste (tipo CSV).
        """
        soup = BeautifulSoup(html_str, 'html.parser')
        table_data = []

        # Headers
        headers = [th.get_text(strip=True) for th in soup.find_all('th')]
        if headers:
            table_data.append(headers)

        # Rows
        rows = soup.find_all('tr')
        if rows:
            for row in rows:
                row_data = [td.get_text(strip=True) for td in row.find_all('td')]
                if row_data:
                    table_data.append(row_data)
        else:
            # fallback
            current_row = []
            for td in soup.find_all('td'):
                current_row.append(td.get_text(strip=True))
                if len(current_row) == len(headers):
                    table_data.append(current_row)
                    current_row = []

        return table_data

    # -----------------------------------------------
    # DB - creazione e gestione
    # -----------------------------------------------
    def init_db(self):
        """
        Inizializza (azzera) le tabelle general e inforiviste nel DB self.con
        """
        self.verbose_print("Pulizia e creazione tabelle DB...")
        with self.con:
            self.con.execute("DROP TABLE IF EXISTS general;")
            self.con.execute("""
                CREATE TABLE IF NOT EXISTS general (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    p_issn TEXT,
                    e_issn TEXT,
                    sector TEXT
                );
            """)
            self.con.execute("DROP TABLE IF EXISTS inforiviste;")
            self.con.execute("""
                CREATE TABLE IF NOT EXISTS inforiviste (
                    titolo TEXT,
                    p_issn TEXT,
                    e_issn TEXT,
                    anno TEXT,
                    MCQ TEXT
                );
            """)

    def inserimento_not_found(self, row):
        """
        Inserisce 'Not Found' per i vari anni in inforiviste
        row = [titolo, p_issn, e_issn]
        """
        for anno in self.anniSelezionati:
            with self.con:
                query = f"""
                INSERT INTO inforiviste (titolo, p_issn, e_issn, MCQ, anno)
                VALUES ("{row[0]}", "{row[1]}", "{row[2]}", "Not Found", "{anno}");
                """
                self.verbose_print(f"Query di inserimento NOT FOUND:\n{query}")
                self.con.execute(query)

    # -----------------------------------------------
    # Lettura file CSV/XLSX e caricamento su DB
    # -----------------------------------------------
    def load_riviste_from_file(self, settore, file_path):
        """
        Carica riviste da CSV/XLSX in DB 'general'.
        settore: usato per la colonna 'sector' di DB
        file_path: path del file
        """
        self.verbose_print(f"Inizio load_riviste_from_file: settore={settore}, file_path={file_path}")
        try:
            if ".csv" in file_path.lower():
                with open(file_path, encoding="utf-8") as f:
                    csvreader = csv.reader(f, delimiter=self.carattereDelimitatorecsv, quoting=csv.QUOTE_ALL)
                    header = next(csvreader)
                    header = self.arriamoheader(header)

                    indexs = self.get_header_indexes(header)
                    if not indexs:
                        self.info(
                            self.root,
                            f"Nel file {file_path} le colonne non sono denominate correttamente.\nTermino.",
                            "Error"
                        )
                        self.close_all(force_exit=True)

                    rows_read = []
                    for row in csvreader:
                        rows_read.append(row)

                    newrows = self.check_and_clean_rows(rows_read, file_path, indexs)
                    if not newrows:
                        self.close_all(force_exit=True)

                    for row in newrows:
                        p_issn = self.format_issn(row[indexs[1]])
                        e_issn = self.format_issn(row[indexs[2]])
                        query = f"""
                        INSERT INTO general (title, p_issn, e_issn, sector)
                        VALUES ("{row[indexs[0]].replace(';','')}", "{p_issn}", "{e_issn}", "{settore}");
                        """
                        self.verbose_print(f"Query insert general:\n{query}")
                        with self.con:
                            self.con.execute(query)

            elif ".xlsx" in file_path.lower() or ".xls" in file_path.lower():
                dfs = pd.read_excel(
                    file_path,
                    sheet_name=None,
                    dtype=str,
                    converters={
                        self.colonnaTitolo: str,
                        self.colonna_pISSN: str,
                        self.colonna_eISSN: str
                    }
                )
                rows_read = []
                for sheet_name in dfs.keys():
                    df = dfs[sheet_name]
                    for idx, row in df.iterrows():
                        tripletta = [
                            str(row[self.colonnaTitolo]),
                            str(row[self.colonna_pISSN]),
                            str(row[self.colonna_eISSN])
                        ]
                        if tripletta not in rows_read:
                            rows_read.append(tripletta)

                for row in rows_read:
                    p_issn = self.format_issn(row[1])
                    e_issn = self.format_issn(row[2])
                    query = f"""
                    INSERT INTO general (title, p_issn, e_issn, sector)
                    VALUES ("{row[0].replace(';','')}", "{p_issn}", "{e_issn}", "{settore}");
                    """
                    self.verbose_print(f"Query insert general:\n{query}")
                    with self.con:
                        self.con.execute(query)

            else:
                self.verbose_print(f"Formato file non gestito: {file_path}")

        except Exception as e:
            self.verbose_print(f"Errore caricamento file {file_path}: {e}")
            # in caso di errore, chiudiamo tutto
            self.close_all(force_exit=True)

    def get_header_indexes(self, header):
        """Ottiene gli indici per [colonnaTitolo, colonna_pISSN, colonna_eISSN] se esistono."""
        idx_tit = None
        idx_p = None
        idx_e = None

        for i, col_name in enumerate(header):
            if self.colonnaTitolo in col_name:
                idx_tit = i
            if self.colonna_pISSN in col_name:
                idx_p = i
            if self.colonna_eISSN in col_name:
                idx_e = i

        if None in (idx_tit, idx_p, idx_e):
            return False
        return [idx_tit, idx_p, idx_e]

    def check_and_clean_rows(self, rows, file_path, indexsHeaders):
        """
        Controlla e pulisce le righe di un CSV.
        Ritorna newrows, o False in caso di errore.
        """
        newrows = []
        for row in rows:
            row_norm = self.arriamoheader(row)
            if len(row_norm) < 3:
                self.verbose_print(f"Riga anomala in {file_path}, forse delimitatore errato: {row_norm}")
                self.info(
                    self.root,
                    f"Riga anomala in {file_path}, forse delimitatore CSV errato.",
                    "End"
                )
                return False
            # Se p_issn e e_issn sono entrambe vuote
            if len(row_norm[indexsHeaders[1]]) < 1 and len(row_norm[indexsHeaders[2]]) < 3:
                self.verbose_print(f"Riga senza p_issn e e_issn: {row_norm}")
                continue
            newrows.append(row_norm)
        return newrows

    def format_issn(self, issn):
        """Inserisce un '-' nel mezzo dell'ISSN, se manca."""
        clean = issn.strip()
        if len(clean) > 4 and "-" not in clean:
            clean = clean[:4] + "-" + clean[4:]
        return clean

    def arriamoheader(self, row):
        """Funzione di pulizia della riga/array."""
        arr = []
        for elem in row:
            arr.append(str(elem).strip())
        return arr

    # -----------------------------------------------
    # Inizializzazione Browser e login
    # -----------------------------------------------
    def start_browser(self):
        """
        Avvia il browser Selenium in base alla config su self.browser.
        """
        self.verbose_print(f"Avvio browser: {self.browser}")
        headless = (self.config['DEFAULT']['headless'] == "True")

        try:
            if self.browser == "Edge":
                if headless:
                    options = EdgeOptions()
                    options.add_argument("--headless")
                    options.add_argument("--window-size=1920x1080")
                    options.add_argument("--disable-gpu")
                    options.add_argument("--no-sandbox")
                    options.add_argument("--start-maximized")
                    self.driver = webdriver.Edge(
                        service=EdgeService(EdgeChromiumDriverManager().install()),
                        options=options
                    )
                else:
                    self.driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))

            elif self.browser == "Chrome":
                if headless:
                    options = ChromeOptions()
                    options.add_argument("--headless")
                    options.add_argument("--window-size=1920x1080")
                    options.add_argument('--disable-gpu')
                    options.add_argument('--no-sandbox')
                    options.add_argument("--start-maximized")
                    self.driver = webdriver.Chrome(
                        service=ChromeService(ChromeDriverManager().install()),
                        options=options
                    )
                else:
                    self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

            elif self.browser == "Mozilla Firefox":
                self.driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
            else:
                self.verbose_print("Browser non supportato, termino.")
                self.close_all(force_exit=True)

            if not headless and self.driver is not None:
                self.driver.maximize_window()

            pyautogui.FAILSAFE = False
        except Exception as e:
            self.verbose_print(f"Errore avvio browser: {e}")
            self.close_all(force_exit=True)

    def do_login(self):
        """
        Esegue il login su MathSciNet.
        Se headless, fa inserire credenziali via tkinter.
        Altrimenti si aspetta che l'utente logghi manualmente.
        """
        pagina_iniziale = self.config['LINK']['pagina_iniziale']
        try:
            self.driver.get(pagina_iniziale)
            time.sleep(self.tempo_attesa_caricamento)
        except Exception as e:
            self.verbose_print(f"Errore caricamento pagina iniziale: {e}")
            self.close_all(force_exit=True)

        if self.config['DEFAULT']['headless'] == "True":
            unito_parziale = self.config['LINK']['log_in_unito_parziale']
            if unito_parziale in self.driver.current_url:
                self.loginheadless()
            else:
                self.verbose_print("Accesso a MathSciNet già effettuato (headless) o link di login assente.")
        else:
            # Non headless => login manuale
            self.root.attributes("-topmost", True)
            self.info(
                self.root,
                "Se nel browser automatico che è comparso chiede le credenziali, fare l'accesso. Poi cliccare OK.",
                "Login manuale"
            )
            self.root.attributes("-topmost", False)

    def validate_login(self, username, password):
        """
        Esegue la validazione dei campi di login su IDP Unito.
        """
        try:
            self.driver.find_element(By.XPATH, self.config['LINK']['username_unito']).clear()
            self.driver.find_element(By.XPATH, self.config['LINK']['password_unito']).clear()
            self.driver.find_element(By.XPATH, self.config['LINK']['username_unito']).send_keys(username.get())
            self.driver.find_element(By.XPATH, self.config['LINK']['password_unito']).send_keys(password.get())

            try:
                self.driver.find_element(By.XPATH, self.config['LINK']['accedi_unito_ita']).send_keys(Keys.ENTER)
            except:
                self.driver.find_element(By.XPATH, self.config['LINK']['accedi_unito_eng']).send_keys(Keys.ENTER)

            time.sleep(self.tempo_attesa_caricamento)
            if "https://idp.unito.it/idp/profile/SAML2" in self.driver.current_url:
                self.info(self.root, "User o password sbagliati, ritentare", "Errore Login")
            elif "https://mathscinet-ams-org" in self.driver.current_url:
                self.info(
                    self.root,
                    "Accesso a Mathscinet Effettuato con successo, chiudi finestra e continua.",
                    "Ok!"
                )
            else:
                self.info(self.root, "Condizione inaspettata, termino.", "Errore")
                self.close_all(force_exit=True)
        except Exception as e:
            self.verbose_print(f"Errore in validate_login: {e}")
            self.close_all(force_exit=True)

    def loginheadless(self):
        """
        Crea la finestra Tk per login UNITO in headless, e aspetta l'input dell'utente.
        """
        tkWindow = tk.Tk()
        tkWindow.title('Log-in UNITO request')

        label_info = tk.Label(
            tkWindow,
            text=f"Controllare che il link di log-in UNITO sia:\n{self.driver.current_url}",
            font='Helvetica 10 bold'
        )
        label_info.grid(row=0, columnspan=2)

        usernameLabel = tk.Label(tkWindow, text="User Name", fg='#05214a', font='Helvetica 12 bold')
        usernameLabel.grid(row=1, column=0)
        username = tk.StringVar()
        usernameEntry = tk.Entry(tkWindow, textvariable=username)
        usernameEntry.grid(row=1, column=1)

        passwordLabel = tk.Label(tkWindow, text="Password", fg='#05214a', font='Helvetica 12 bold')
        passwordLabel.grid(row=2, column=0)
        password = tk.StringVar()
        passwordEntry = tk.Entry(tkWindow, textvariable=password, show='*')
        passwordEntry.grid(row=2, column=1)

        def do_local_login():
            self.validate_login(username, password)

        loginButton = tk.Button(
            tkWindow, text="Login", fg='#05214a', bg='#fff',
            font='Helvetica 10 bold', command=do_local_login
        )
        loginButton.grid(row=3, column=0)

        closeButton = tk.Button(
            tkWindow, text="Close", fg='#f00', bg='#fff',
            font='Helvetica 10 bold', command=lambda: tkWindow.destroy()
        )
        closeButton.grid(row=3, column=1)

        tkWindow.mainloop()

    # -----------------------------------------------
    # Funzioni di ricerca e scraping su Mathscinet
    # -----------------------------------------------
    def search_journal(self, row):
        """
        row = (titolo, p_issn, e_issn).
        Tenta la ricerca su MathSciNet con p_issn e poi e_issn.
        """
        titolo, p_issn, e_issn = row[0], row[1], row[2]
        self.verbose_print(f"[search_journal] row: {row}")

        # se non abbiamo p_issn/e_issn validi
        if (len(p_issn) < 5) and (len(e_issn) < 5):
            self.verbose_print("Impossibile cercare: pISSN e eISSN mancanti.")
            return False

        link_search = self.config['LINK']['link_search']

        # Tenta p_issn
        if len(p_issn) > 4:
            url = link_search.replace("???VARIABILE???", p_issn)
            self.driver.get(url)
            time.sleep(self.tempo_attesa_caricamento)
            if "groupId" in self.driver.current_url or "journalId" in self.driver.current_url:
                self.verbose_print("Ricerca PISSN con successo.")
                return True
            else:
                if self.try_click_first_valid_search_result():
                    return True

        # Tenta e_issn
        if len(e_issn) > 4:
            # Non consideriamo e_issn lunghi
            if len(e_issn) > 9:
                return False
            url = link_search.replace("???VARIABILE???", e_issn)
            self.driver.get(url)
            time.sleep(self.tempo_attesa_caricamento)
            if "groupId" in self.driver.current_url or "journalId" in self.driver.current_url:
                self.verbose_print("Ricerca EISSN con successo.")
                return True
            else:
                if self.try_click_first_valid_search_result():
                    return True

        self.verbose_print("Ricerca pISSN/eISSN fallita.")
        return False

    def try_click_first_valid_search_result(self):
        """
        Se la ricerca restituisce più risultati, clicca il primo link indicizzato correttamente.
        """
        try:
            elements = self.driver.find_elements(By.XPATH, self.config['HTML']['MoreresultsSearch'])
            for elem in elements:
                txt = elem.text.lower()
                if self.config['HTML']['Noindexresearch'].lower() not in txt:
                    href = elem.find_element(By.XPATH, ".//a").get_attribute('href')
                    self.driver.get(href)
                    if "groupId" in self.driver.current_url or "journalId" in self.driver.current_url:
                        self.verbose_print("Ricerca con lista risultati: clic primo link idoneo, ok.")
                        return True
            return False
        except:
            return False

    def search_journal_first_link_also_if_no_valid(self, row):
        """
        row = (titolo, p_issn, e_issn).
        Tenta la ricerca su MathSciNet con p_issn e poi e_issn.
        """
        titolo, p_issn, e_issn = row[0], row[1], row[2]
        self.verbose_print(f"[search_journal] row: {row}")

        # se non abbiamo p_issn/e_issn validi
        if (len(p_issn) < 5) and (len(e_issn) < 5):
            self.verbose_print("Impossibile cercare: pISSN e eISSN mancanti.")
            return False

        link_search = self.config['LINK']['link_search']

        # Tenta p_issn
        if len(p_issn) > 4:
            url = link_search.replace("???VARIABILE???", p_issn)
            self.driver.get(url)
            time.sleep(self.tempo_attesa_caricamento)
            if "groupId" in self.driver.current_url or "journalId" in self.driver.current_url:
                self.verbose_print("Ricerca PISSN con successo.")
                return True
            else:
                if self.try_click_first_search_result():
                    return True

        # Tenta e_issn
        if len(e_issn) > 4:
            # Non consideriamo e_issn lunghi
            if len(e_issn) > 9:
                return False
            url = link_search.replace("???VARIABILE???", e_issn)
            self.driver.get(url)
            time.sleep(self.tempo_attesa_caricamento)
            if "groupId" in self.driver.current_url or "journalId" in self.driver.current_url:
                self.verbose_print("Ricerca EISSN con successo.")
                return True
            else:
                if self.try_click_first_search_result():
                    return True

        self.verbose_print("Ricerca pISSN/eISSN fallita.")
        return False

   
    def try_click_first_search_result(self):
        """
        Se la ricerca restituisce più risultati, clicca il primo link indicizzato correttamente.
        """
        try:
            elements = self.driver.find_elements(By.XPATH, self.config['HTML']['MoreresultsSearch'])
            for elem in elements:
                txt = elem.text.lower()
                href = elem.find_element(By.XPATH, ".//a").get_attribute('href')
                self.driver.get(href)
                if "groupId" in self.driver.current_url or "journalId" in self.driver.current_url:
                    self.verbose_print("Ricerca con lista risultati: clic primo link anche se non idoneo, ok.")
                    return True
            return False
        except:
            return False
        
    def click_first_valid_xpath(self, *xpaths):
        """
        Tenta di cliccare in successione i vari xpaths passati. 
        Se trova quello cliccabile, ritorna True.
        """
        time.sleep(self.tempo_attesa_caricamento)
        for xp in xpaths:
            try:
                elem = self.driver.find_element(By.XPATH, xp)
                elem.send_keys(Keys.ENTER)
                self.verbose_print(f"click_first_valid_xpath: cliccato xpath {xp}")
                return True
            except Exception as e:
                self.verbose_print(f"Tentativo fallito con xpath={xp}, errore: {e}")
        return False

    def find_first_valid_element(self, *xpaths):
        """
        Ritorna l'elemento corrispondente al primo xpath che trova, altrimenti None.
        """
        for xp in xpaths:
            try:
                elem = self.driver.find_element(By.XPATH, xp)
                return elem
            except:
                pass
        return None

    def get_MCQ(self, titolo, p_issn, e_issn):
        """
        Clicca il bottone tabella, prende l'header/tabella MCQ,
        e inserisce su DB i dati per ogni anno.
        """
        self.verbose_print(f"Ottengo MCQ per rivista: {titolo}, PISSN={p_issn}, EISSN={e_issn}")
        # Bottone tabella
        if not self.click_first_valid_xpath(
            self.config['HTML']['bottonetabella'],
            self.config['HTML']['bottonetabellasecondo'],
            self.config['HTML']['bottonetabellaterzo']
        ):
            self.inserimento_not_found([titolo, p_issn, e_issn])
            return False

        # Troviamo l'elemento della tabella
        table_elem = self.find_first_valid_element(
            self.config["HTML"]["tabellaMCQ"],
            self.config["HTML"]["tabellaMCQ2"],
            self.config["HTML"]["tabellaMCQ3"]
        )
        if not table_elem:
            self.verbose_print("Tabella MCQ non trovata.")
            self.inserimento_not_found([titolo, p_issn, e_issn])
            return False

        html_table = table_elem.get_attribute('innerHTML')
        table = self.parse_html_table(html_table)
        if len(table) < 2:
            self.verbose_print("Tabella MCQ vuota o parsing fallito.")
            self.inserimento_not_found([titolo, p_issn, e_issn])
            return False

        # Header -> cerchiamo indici
        header = table[0]
        try:
            index_anno = header.index("Year")
            index_mcq = header.index("MCQ")
        except ValueError:
            self.verbose_print("Colonne 'Year' e/o 'MCQ' non trovate.")
            self.inserimento_not_found([titolo, p_issn, e_issn])
            return False

        # Raccolta e inserimento
        anniTrovati = []
        for i, riga in enumerate(table):
            if i == 0:  # skip header
                continue
            anno_val = riga[index_anno]
            mcq_val = riga[index_mcq]

            if anno_val.isdigit() or self.is_float(anno_val):
                anniTrovati.append(anno_val)
                if self.is_float(mcq_val):
                    query = f"""
                    INSERT INTO inforiviste (titolo, p_issn, e_issn, MCQ, anno)
                    VALUES ("{titolo}", "{p_issn}", "{e_issn}", "{mcq_val}", "{anno_val}");
                    """
                    self.verbose_print(query)
                    with self.con:
                        self.con.execute(query)

        # Inseriamo "Not Found" per gli anni non presenti
        for anno in self.anniSelezionati:
            if str(anno) not in anniTrovati:
                query = f"""
                INSERT INTO inforiviste (titolo, p_issn, e_issn, MCQ, anno)
                VALUES ("{titolo}", "{p_issn}", "{e_issn}", "Not Found", "{anno}");
                """
                self.verbose_print(query)
                with self.con:
                    self.con.execute(query)
        return True

    def is_float(self, testo):
        try:
            float(testo)
            return True
        except:
            return False

    # -----------------------------------------------
    # Backup e salvataggio su CSV/Excel
    # -----------------------------------------------
    def backup_results(self, settore):
        """
        Crea cartelle, esporta i dati su CSV ed Excel in base alle self.anniSelezionati.
        Aggiunge la colonna 'Percentile' in base ai self.percentiles (cut-off personalizzabili).
        Logica invertita Q4>Q3>Q2>Q1:
          - <= p1% => Q4
          - <= p2% => Q3
          - <= p3% => Q2
          - <= p4% => Q1
          -  > p4% => 'peggio di Q1'
        """
        current_time = datetime.datetime.now()
        today = f"{current_time.year}{current_time.month:02d}{current_time.day:02d}"

        base_path = os.path.join(self.outputPath, f'mathscinetWebscraping{today}')
        if not os.path.exists(base_path):
            os.makedirs(base_path)
            os.chmod(base_path, stat.S_IRWXO)

        settore_path = os.path.join(base_path, settore)
        if not os.path.exists(settore_path):
            os.makedirs(settore_path)
            os.chmod(settore_path, stat.S_IRWXO)
            os.makedirs(os.path.join(settore_path, 'CSV'))
            os.chmod(os.path.join(settore_path, 'CSV'), stat.S_IRWXO)
            os.makedirs(os.path.join(settore_path, 'EXCEL'))
            os.chmod(os.path.join(settore_path, 'EXCEL'), stat.S_IRWXO)

        pathFilexlsx = os.path.join(settore_path, 'EXCEL', f"{settore}_MCQ.xlsx")

        with pd.ExcelWriter(pathFilexlsx, engine='xlsxwriter') as writer:
            for anno in self.anniSelezionati:
                query = f"""
                SELECT DISTINCT general.title, general.p_issn, general.e_issn, inforiviste.MCQ 
                FROM general 
                JOIN inforiviste ON inforiviste.titolo = general.title 
                WHERE inforiviste.anno = '{anno}' AND general.sector='{settore}' 
                ORDER BY inforiviste.MCQ DESC
                """
                self.verbose_print(f"Eseguo query backup per anno={anno}, settore={settore}\n{query}")
                data = self.con.execute(query)
                results = data.fetchall()

                csv_path = os.path.join(settore_path, 'CSV', f"{settore}_MCQ{anno}.csv")
                if len(results) > 0:
                    with open(csv_path, 'w', encoding='utf-8', errors='ignore') as f:
                        wrt = csv.writer(f)
                        wrt.writerow(['title', 'p_issn', 'e_issn', 'MCQ'])
                        wrt.writerows(results)

                    df = pd.read_csv(csv_path, sep=",", encoding='utf-8', on_bad_lines='skip')
                    total = len(df.index)
                    if total > 0:
                        df['Percentile'] = df.index.map(lambda x: self.get_percentile_label(x+1, total))
                        df.to_csv(csv_path, index=False, sep=",", mode='w', errors="ignore")
                        df.to_excel(writer, sheet_name=str(anno), index=False)

    def get_percentile_label(self, rank, total):
        """
        Inversione: Q4 > Q3 > Q2 > Q1
        Supponiamo p1 < p2 < p3 < p4 < 100:
          - <= p1 => Q4  (best)
          - <= p2 => Q3
          - <= p3 => Q2
          - <= p4 => Q1
          -  > p4 => peggio di Q1
        """
        p1, p2, p3, p4 = self.percentiles
        percentage = (rank / total) * 100

        if percentage <= p1:
            return f"top 10 perc - Q1 (<= {p1}%)"
        elif percentage <= p2:
            return f"Q1 (<= {p2}%)"
        elif percentage <= p3:
            return f"Q2 (<= {p3}%)"
        elif percentage <= p4:
            return f"Q3 (<= {p4}%)"
        else:
            return f"Q4 (>{p4}%)"

    # -----------------------------------------------
    # Flusso di elaborazione
    # -----------------------------------------------
    def run(self):
        """
        Esegue il workflow generale in un try/finally:
            - Avvio browser, login
            - Per ciascun settore/file:
                - Inizializza tabelle DB
                - Carica riviste da file
                - Per ogni rivista, cerca su MathSciNet e salva MCQ
                - Salva su CSV/Excel
        """
        try:
            counter = 0
            for key, file_path in self.files.items():
                if len(file_path) > 4:
                    counter +=1
            if counter > 0:
                self.start_browser()
                self.do_login()

            tot_settori = len(self.files.keys())
            counter = 0

            for key, file_path in self.files.items():
                counter += 1
                if len(file_path) > 0:
                    self.verbose_print(f"[SETTORE={key}] Inizio elaborazione (file={file_path}) ...")
                    # Init tabelle
                    self.init_db()

                    # Carichiamo dal CSV/XLSX
                    self.load_riviste_from_file(key, file_path)

                    # Otteniamo tutte le riviste dalla tabella general
                    self.cur.execute("SELECT DISTINCT title, p_issn, e_issn FROM general")
                    rows = self.cur.fetchall()
                    num_riviste = len(rows)

                    tempo_stimato_ore = round((num_riviste * self.tempo_singola_ricerca) / 3600)
                    resto_minuti = (num_riviste * self.tempo_singola_ricerca) / 3600 - tempo_stimato_ore
                    minuti_stimati = round(resto_minuti * 60)

                    for i, row in enumerate(rows):
                        self.verbose_print(
                            f"[{counter}/{tot_settori}] Settore={key}: "
                            f"Rivista {i+1}/{num_riviste}, tempo stimato rimanente={tempo_stimato_ore}h:{minuti_stimati}m"
                        )
                        # for _ in range(3):
                        #     pyautogui.press('shift')

                        ##########################################
                        #Qui è da inserire che prima verifica se il giornale è già stato trovato. in quel caso si devono saltare questi passaggi
                        ###########################################
                        if self.search_journal(row):
                            self.get_MCQ(row[0], row[1], row[2])
                        elif self.search_journal_first_link_also_if_no_valid(row):
                            #sarebbe bello inserire un dato che ci dice che è stato trovato MCQ in questo caso
                            self.get_MCQ(row[0], row[1], row[2])
                        else:
                            self.inserimento_not_found([row[0], row[1], row[2]])

                    # Salvataggio e backup
                    self.backup_results(key)

            # Info e chiusura “pulita”
            self.root.attributes("-topmost", True)
            if self.settori == "" or self.anniSelezionati == [] or self.files == {} or self.outputPath == "":
                self.info(self.root, "Il programma è terminato per il mancato inserimento di informazioni necessarie. Per far girare il programma devono essere impostati l'anno di inizio e di fine ricerca, i percentili, almeno un settore con un file di riviste e la cartella dove inserire gli output.", "Fine")
            else:
                self.info(self.root, "Il programma è terminato", "Fine")
        except Exception as e:
            self.verbose_print(f"ERRORE GENERALE: {e}")
        finally:
            # Chiudiamo tutto, anche in caso di successo o errore
            self.close_all(force_exit=True)

# ESECUZIONE
if __name__ == "__main__":
    try:
        scraper = MathscinetScraper()
        scraper.run()
    except Exception as e:
        print(f"Errore iniziale: {e}")
    
    

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
#import pyautogui
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
#from functools import partial
from bs4 import BeautifulSoup
import getpass
import logging
import argparse
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Disabilita i log di selenium webdriver
logging.getLogger('selenium').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

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
        #Creazione della cartella per gli screenshot
        self.screenshot_dir = os.path.join(self.application_path, 'screen')
        os.makedirs(self.screenshot_dir, exist_ok=True)
         # Impostiamo logging
        log_path = os.path.join(self.application_path, 'log.txt')
        logging.basicConfig(
            filename=log_path,
            level=logging.DEBUG,
            format="%(asctime)s | Message: %(message)s",
            filemode="w",
        )

        print(f"New version program")
        print(f"Path variabili.ini: {os.path.join(self.application_path, 'risorse','variabili.ini')}")
        if os.path.exists(os.path.join(self.application_path, 'risorse','variabili.ini')):
            self.config.read(os.path.join(self.application_path, 'risorse','variabili.ini'))
        else:
            self.verbose_print(f"Non trovato il file varibili.ini")
            self.close_all(force_exit=True)
        
       
        # Leggiamo dal file di config
        self.browser = self.config['DEFAULT']['browser']
        self.driverPath = ""
        self.debug_mode = True if self.config['DEFAULT']['debug_mode'] == "True" else False
        

        self.tempo_singola_ricerca = float(self.config['DEFAULT']['tempo_singola_ricerca'])
        self.tempo_attesa_caricamento = float(self.config['DEFAULT']['attesa_per_caricamento'])
        self.colonna_eISSN = self.config['DEFAULT']['colonna_eISSN']
        self.colonna_pISSN = self.config['DEFAULT']['colonna_pISSN']
        self.colonnaTitolo = self.config['DEFAULT']['colonnaTitolo']
        self.carattereDelimitatorecsv = self.config['DEFAULT']['carattereDelimitatorecsv']
        self.divisionePercentile = True

        ## Opzione --config : viene esposto a terminale il file di configurazione (le parti di interesse)
        parser = argparse.ArgumentParser(description='WebScrapint Mathscinet per riviste UNITO')
    
        # Aggiungi l'opzione --config
        parser.add_argument('--config', 
                        action='store_true',
                        help='Mostra informazioni di configurazione')
        
        parser.add_argument('--checkFile', 
                        action='store_true',
                        help='Check esistenza file di input')
        
        # Leggi gli argomenti
        args = parser.parse_args()
        
        # Controlla se è stata usata l'opzione --config
        if args.config:
            self.print_section("InputRicerca")
            self.verbose_print(f"Fine scrittura configurazione")
            # in caso di errore, chiudiamo tutto
            exit()
        
        if args.checkFile:
            self.settori = self.config['DEFAULT']['settori'].split(',')
            for settore in self.settori:
                nomeChiave = 'InputFileFullPath' + settore
                if (len(self.config['InputRicerca'][nomeChiave]) > 3 ):
                    if not os.path.exists(self.config['InputRicerca'][nomeChiave]):
                        print(f"Settore = {nomeChiave}, FullPathFile = {self.config['InputRicerca'][nomeChiave]} -> ERRORE : File non trovato")
                    else:
                        print(" -> File trovato")
            self.verbose_print(f"Fine check")
            # in caso di errore, chiudiamo tutto
            exit()



        ##################################




        # Anni selezionati 
        self.anniSelezionati = list(range(int(self.config['InputRicerca']['annoInizio']), int(self.config['InputRicerca']['annoFine']) + 1))
        self.verbose_print(f"Anni selezionati: {self.anniSelezionati}")

        try:
           if not os.path.exists(os.path.join(self.application_path, 'risorse','mathscinet_databse.db')):
               self.verbose_print(f"non trovato il file oppure errore nella connessione a mathscinet_databse.db: {e}")
           self.con = sl.connect(os.path.join(self.application_path, 'risorse','mathscinet_databse.db'))
        except Exception as e:
            self.verbose_print(f"non trovato il file oppure errore nella connessione a mathscinet_databse.db: {e}")
            self.close_all(force_exit=True)

        # Apriamo la connessione DB
        self.cur = self.con.cursor()

        # Variabili per file e output
        self.files = {}
        self.outputPath = ""


        #settori default
        self.settori = self.config['DEFAULT']['settori'].split(',')
        self.verbose_print(f"Settori selezionati: {self.settori}")
        
        

        for settore in self.settori:
            nomeChiave = 'InputFileFullPath' + settore
            if nomeChiave not in self.config['InputRicerca']:
                print(f"ERRORE: chiave '{nomeChiave}' non trovata nella sezione [InputRicerca]")
                exit()
            if (len(self.config['InputRicerca'][nomeChiave]) > 3 ):
                self.files[settore] = self.config['InputRicerca'][nomeChiave]
                if not os.path.exists(self.config['InputRicerca'][nomeChiave]):
                    print(f"Settore = {nomeChiave}, FullPathFile = {self.config['InputRicerca'][nomeChiave]} -> ERRORE : File non trovato")
                    exit()
        
        self.verbose_print(f"Lista dei settori che hanno dei files: {self.files}")
        


        # Selezione cartella output -- commentati perchè verrà selezionata nella variabili.ini
        #self.info(self.root, "Seleziona cartella output", "Selezionare la cartella di output")
        #self.outputPath = filedialog.askdirectory(title="Seleziona cartella output")

        self.outputPath = self.config['InputRicerca']['OutputDirectory']
        self.verbose_print(f'Output directory:{self.outputPath}')

        if len(self.config['InputRicerca']['OutputDirectory']) == 0:
            print(f"No output directory")
            self.close_all(force_exit=True)
        
        

        self.driver = None  # webdriver Selenium
        

        # Percentili di default
        self.percentiles = [10, 25, 50, 75]
        self.verbose_print("Mantengo i percentili di default: [10, 25, 50, 75].")

        

        

        # Fine init
        self.verbose_print("Inizializzazione completata, pronto per eseguire.")
    # -----------------------------------------------
    # Sezione per stampare il config
    def print_section(self, section_name):
        """Stampa una sezione specifica del file INI"""
        if section_name in self.config:
            print(f"=== {section_name.upper()} ===")
            for key, value in self.config[section_name].items():
                print(f"{key} = {value}")
            print()  # Riga vuota
        else:
            print(f"⚠ Sezione '{section_name}' non trovata")
    # -----------------------------------------------

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

        

        if force_exit:
            sys.exit(0)

    
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
            self.con.execute("DROP TABLE IF EXISTS staging;")
            self.con.execute("""
                CREATE TABLE IF NOT EXISTS staging (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    p_issn TEXT,
                    e_issn TEXT,
                    sector TEXT
                );
            """)
            self.con.execute("""
                CREATE TABLE IF NOT EXISTS general (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    p_issn TEXT,
                    e_issn TEXT,
                    sector TEXT,
                    Note TEXT
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

    def FromStagingToGeneral(self,settore):
        """
        Sposta i dati dalla tabella staging alla tabella general, gestendo i duplicati.
        """
        self.verbose_print(f"Spostamento dati da staging a general per il settore: {settore}")
        query = f"""
            WITH compress_pissn as (
                select p_issn, 
                    MAX(nullif(e_issn,'nan')) as e_issn,
                    max(sector) as sector,
                    max(title) as title
                    FROM staging
                    where nullif(p_issn,'nan') is not null and p_issn != ''
                    group by p_issn
                    having count(*) > 1
                ),
            compress_eissn as (
                select e_issn, 
                    MAX(nullif(p_issn,'nan')) as p_issn,
                    max(sector) as sector,
                    max(title) as title
                    FROM staging
                    where nullif(e_issn,'nan') is not null and e_issn != ''
                    group by e_issn
                    having count(*) > 1
                ),
            unione as (
                select title,
                    p_issn,
                    e_issn,
                    sector
                    from compress_pissn
                    union
                    select title,
                    p_issn,
                    e_issn,
                    sector
                    from compress_eissn
                ),
                finalaze as (
                    select max(title) as title, 
                    p_issn, 
                    e_issn, 
                    sector,
                    'Duplicato in input' as Note
                    from unione
                    group by p_issn, e_issn
                )
                INSERT INTO general (title, p_issn, e_issn, sector, Note)
                select title, 
                ifnull(p_issn,''), 
                ifnull(e_issn,''), 
                sector, 
                Note
                from finalaze
                union 
                select title, 
                ifnull(p_issn,''), 
                ifnull(e_issn,''), 
                sector,
                '' 
                from staging 
                where
                (
                (
                    nullif(p_issn,'nan') is not null 
                    and 
                    p_issn not in (select p_issn from finalaze) 
                )
                or 
                (
                    nullif(e_issn,'nan') is not null 
                    and 
                    e_issn not in (select e_issn from finalaze) 
                )
                ) = True
        """
        
        try:
            with self.con:
                self.con.execute(query)

                self.verbose_print(f"Righe spostate")
                query = "SELECT * FROM general where sector = '" + settore + "';"
                data = self.con.execute(query)
                results = data.fetchall()
                col_names = [desc[0] for desc in data.description]  # nomi colonne

                self.verbose_print(f"Colonne: {col_names}")
                for row in results:
                    self.verbose_print(row)

                self.con.execute("DELETE FROM staging;")
        except Exception as e:
            self.verbose_print(f"Errore spostamento dati da staging a general: {e}")
            self.close_all(force_exit=True)


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
                        self.verbose_print(f"Nel file {file_path} le colonne non sono denominate correttamente.\nTermino.")
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
                        INSERT INTO staging (title, p_issn, e_issn, sector)
                        VALUES ("{row[indexs[0]].replace(';','').replace('"',' ').replace("'",'')}", "{p_issn}", "{e_issn}", "{settore}");
                        """
                        self.verbose_print(f"Query insert staging:\n{query}")
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
                    INSERT INTO staging (title, p_issn, e_issn, sector)
                    VALUES ("{row[0].replace(';','').replace('"',' ').replace("'",'')}", "{p_issn}", "{e_issn}", "{settore}");
                    """
                    self.verbose_print(f"Query insert staging:\n{query}")
                    with self.con:
                        self.con.execute(query)

            else:
                self.verbose_print(f"Formato file non gestito: {file_path}")
            
            # Dopo aver caricato, spostiamo da staging a general
            self.FromStagingToGeneral(settore)

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
                    options.add_argument("--disable-dev-shm-usage")
                    options.add_argument("--disable-gpu")
                    options.add_argument("--no-sandbox")
                    options.add_argument("--remote-debugging-port=9222")  # Evita crash tab
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
                    options.add_argument("--no-sandbox")
                    options.add_argument("--disable-dev-shm-usage")
                    options.add_argument("--disable-gpu")
                    options.add_argument("--window-size=1920,1080")
                    options.add_argument("--remote-debugging-port=9222")  # Evita crash tab
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

            #pyautogui.FAILSAFE = False
        except Exception as e:
            self.verbose_print(f"Errore avvio browser: {e}")
            self.close_all(force_exit=True)

    



    def do_login(self):
        pagina_iniziale = self.config['LINK']['pagina_iniziale']
        try:
            self.driver.get(pagina_iniziale)
            time.sleep(self.tempo_attesa_caricamento)
        except Exception as e:
            self.verbose_print(f"Errore caricamento pagina iniziale: {e}")
            self.close_all(force_exit=True)
        self.loginheadless()
    
    
    def loginheadless(self):

        self.driver.save_screenshot(os.path.join(self.application_path, "screen", "login_iniziale.png"))
        time.sleep(2)

        try:
        # Controlla se la pagina contiene il campo username
          self.driver.find_element(By.XPATH, self.config['LINK']['username_unito'])
        
        # Se il campo username è visibile, allora serve login manuale
          print("Login richiesto - inserisci credenziali UNITO")
          print(f"Questo è il link di log-in derivato da variabili.ini (uno screen della pagina è presente nella directory screen): {self.driver.current_url}")
        
          username = input("Username: ")
          password = getpass.getpass("Password (non sarà visibile a terminale): ")
          self.validate_login_from_terminal(username, password)
        
        except Exception as e:
        # Se il campo non è presente, consideriamo il login già effettuato
          self.verbose_print("Login non richiesto: già autenticato tramite rete UniTo")
    
    def validate_login_from_terminal(self, username, password):
        try:
            self.driver.find_element(By.XPATH, self.config['LINK']['username_unito']).clear()
            self.driver.find_element(By.XPATH, self.config['LINK']['username_unito']).send_keys(username)
            self.driver.find_element(By.XPATH, self.config['LINK']['password_unito']).clear()
            self.driver.find_element(By.XPATH, self.config['LINK']['password_unito']).send_keys(password)

            try:
                self.driver.find_element(By.XPATH, self.config['LINK']['accedi_unito_ita']).send_keys(Keys.ENTER)
            except:
                self.driver.find_element(By.XPATH, self.config['LINK']['accedi_unito_eng']).send_keys(Keys.ENTER)

            time.sleep(self.tempo_attesa_caricamento)

            # Screenshot dopo il login
            self.driver.save_screenshot(os.path.join(self.application_path, "screen", "after_login.png"))

            if "mathscinet-ams-org" not in self.driver.current_url:
                self.driver.save_screenshot(os.path.join(self.application_path, "screen", "login_url_inatteso.png"))
                raise Exception("Login fallito: URL inatteso")
                
        except Exception as e:
            self.verbose_print(f"Errore login terminale: {e}")
            self.driver.save_screenshot(os.path.join(self.application_path, "screen", "login_error.png"))
            self.close_all(force_exit=True)


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
        current_time = datetime.now()
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
                SELECT DISTINCT general.title
                , general.p_issn
                , general.e_issn
                , CASE WHEN inforiviste.MCQ != 'Not Found' THEN cast(inforiviste.MCQ as float) ELSE 0 END as MCQ
                , CASE WHEN inforiviste.MCQ = 'Not Found' THEN 'Not Found' WHEN general.Note = 'Duplicato in input' THEN general.Note ELSE NULL END AS Note
                FROM general 
                JOIN inforiviste ON inforiviste.titolo = general.title 
                WHERE inforiviste.anno = '{anno}' AND general.sector='{settore}'
                ORDER BY CASE WHEN inforiviste.MCQ != 'Not Found' THEN cast(inforiviste.MCQ as float) ELSE 0 END DESC
                """
                
                self.verbose_print(f"Eseguo query backup per anno={anno}, settore={settore}\n{query}")
                data = self.con.execute(query)
                results = data.fetchall()

                csv_path = os.path.join(settore_path, 'CSV', f"{settore}_MCQ{anno}.csv")
                if len(results) > 0:
                    with open(csv_path, 'w', encoding='utf-8', errors='ignore') as f:
                        wrt = csv.writer(f)
                        wrt.writerow(['title', 'p_issn', 'e_issn', 'MCQ','Note'])
                        wrt.writerows(results)

                    df = pd.read_csv(csv_path, sep=",", encoding='utf-8', on_bad_lines='skip')
                    total = len(df.index)
                    if total > 0:
                        df['Percentile'] = df.index.map(lambda x: self.get_percentile_label(x+1, total, option = 'number'))
                        df['Percentile'] = df.groupby('MCQ')['Percentile'].transform('mean').round(3)
                        df['Fascia percentile MSN'] = df.index.map(lambda x: self.get_percentile_label(x+1, total))
                        df['Settore'] = settore
                        df['Anno'] = anno
                        df.to_csv(csv_path, index=False, sep=",", mode='w', errors="ignore")
                        df.to_excel(writer, sheet_name=str(anno), index=False)

    def get_percentile_label(self, rank, total, option='label'):
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
        percentage = math.ceil((rank / total) * 10000)/100
        if option == 'number':
            return percentage

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
    # CheckQuery con debug
    # -----------------------------------------------

    def check_query(self,query):
        """
        Esegue una query di debug e stampa i risultati.
        """
        try:
            data = self.con.execute(query,("MAT01A",))
            results = data.fetchall()
            for row in results:
                self.verbose_print(row)
        except Exception as e:
            self.verbose_print(f"Errore esecuzione query di debug: {e}")

    def debug_mode_start(self):
        self.query = ""
        if self.debug_mode == True:
            self.verbose_print("Eseguo operazioni impostate per debugmode.")

            # self.init_db()
            counter = 0
            for key, file_path in self.files.items():
                counter += 1
                if len(file_path) > 0:
                    self.verbose_print(f"[SETTORE={key}] Inizio caricmento (file={file_path}) ...")

                    # Carichiamo dal CSV/XLSX
                    self.load_riviste_from_file(key, file_path)


            if self.query != "":
                self.verbose_print("Eseguo query di debug:")
                self.check_query(self.query)
                self.verbose_print("Query di debug terminata.")
                
            
           
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
           

            tot_settori = len(self.files.keys())
            counter = 0

            # Init tabelle solo se non sono in debug mode
            if self.debug_mode == False:
                self.verbose_print("Debug mode disattivato: carico nuovi dati ed inizializzo db.")
                self.init_db()
                for key, file_path in self.files.items():
                    counter += 1
                    if len(file_path) > 0:
                        self.verbose_print(f"[SETTORE={key}] Inizio caricmento (file={file_path}) ...")

                        # Carichiamo dal CSV/XLSX
                        self.load_riviste_from_file(key, file_path)
            else:
                self.verbose_print("Debug mode attivo: salto init_db per mantenere dati precedenti.\n" \
                "Verrà saltata l'inizializzazione ma la scrittura dei file avverrà lo stesso.\n" \
                "Verrà lanciato il check_query se c'è una query al suo interno\n" \
                "Inoltre non viene verificata la presenza di tutti gli input necessari.")

            self.debug_mode_start()
                
            counter = 0
            for key, file_path in self.files.items():
                if len(file_path) > 4:
                    counter +=1
            if counter > 0:
                if self.debug_mode == False:
                    self.start_browser()
                    self.do_login()
            counter = 0

            if self.debug_mode == False:
                for key, file_path in self.files.items():
                    counter += 1
                    if len(file_path) > 0:
                        #self.verbose_print(f"[SETTORE={key}] Inizio elaborazione (file={file_path}) ...")
                        # Init tabelle
                        #self.init_db()

                        # Carichiamo dal CSV/XLSX
                        #self.load_riviste_from_file(key, file_path)

                        # Otteniamo tutte le riviste dalla tabella general
                        self.cur.execute("SELECT DISTINCT title, p_issn, e_issn FROM general WHERE sector=?;", (key,))
                        rows = self.cur.fetchall()
                        num_riviste = len(rows)

                        tempo_stimato_ore = round((num_riviste * self.tempo_singola_ricerca) / 3600)
                        resto_minuti = (num_riviste * self.tempo_singola_ricerca) / 3600 - tempo_stimato_ore
                        minuti_stimati = round(resto_minuti * 60)

                        # Orario attuale
                        fuso_roma = ZoneInfo("Europe/Rome")
                        ora_inizio = datetime.now(fuso_roma)

                        # Calcolo orario stimato di fine
                        fine_stimata = ora_inizio + timedelta(hours=tempo_stimato_ore, minutes=minuti_stimati)

                        for i, row in enumerate(rows):
                            self.verbose_print(
                                f"[{counter}/{tot_settori}] Settore={key}: "
                                f"Rivista {i+1}/{num_riviste}, tempo stimato fine={fine_stimata.strftime('%H:%M')}, ora inizio = {ora_inizio.strftime('%H:%M')}"
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
            
            if (self.settori == "" or self.anniSelezionati == [] or self.files == {} or self.outputPath == "") and self.debug_mode == False:
                self.verbose_print("Il programma è terminato per il mancato inserimento di informazioni necessarie. Per far girare il programma devono essere impostati l'anno di inizio e di fine ricerca, i percentili, almeno un settore con un file di riviste e la cartella dove inserire gli output.")
                
            else:
                self.verbose_print("Il programma è terminato.")
                
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
    
    

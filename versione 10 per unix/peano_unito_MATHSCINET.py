#!/usr/bin/env python

import sys, stat
import os.path
import logging
import time
import math
import datetime
import configparser
import sqlite3 as sl
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import simpledialog
import pyautogui
import pandas as pd
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import EdgeOptions
from selenium.webdriver import ChromeOptions
from functools import partial
from bs4 import BeautifulSoup

root = tk.Tk()
root.withdraw()

def get_years_range(root):
    # Funzione per chiedere input dell'utente con finestre di dialogo
    # Funzione per verificare che l'anno sia tra 1900 e 3000
    def valid_year(year):
        return 1900 <= year <= 3000

    while True:
        # Chiediamo l'anno di inizio
        start_year = simpledialog.askinteger("Anno di inizio", "Inserisci l'anno di inizio raccolta (tra 1900 e 3000):", parent=root)
        # Chiediamo l'anno di fine
        end_year = simpledialog.askinteger("Anno di fine", "Inserisci l'anno di fine raccolta (tra 1900 e 3000):", parent=root)

        # Controlliamo che gli anni siano validi
        if start_year is None or end_year is None:
            messagebox.showerror("Errore", "Inserimento annullato.", parent=root)
            return None
        
        if not valid_year(start_year) or not valid_year(end_year):
            messagebox.showerror("Errore", "Gli anni devono essere compresi tra 1900 e 3000.", parent=root)
            continue  # Chiedi di nuovo gli anni
        elif start_year > end_year:
            messagebox.showerror("Errore", "L'anno di inizio deve essere minore o uguale all'anno di fine.", parent=root)
            continue  # Chiedi di nuovo gli anni
        else:
            # Se gli anni sono validi, restituiamo la lista
            return list(range(start_year, end_year + 1))

# Finestra on top alert
def info(root, message, title="ShowInfo"):
    messagebox.showinfo(title, message, parent=root)

def chiedisino(root, message, title="ShowInfo"):
    risposta = messagebox.askyesno(title, message, parent=root)
    return risposta

        

def parse_html_table(html_str):
    # Unire i frammenti di stringa
    #html_str = ''.join(html_str)
    
    # Utilizzare BeautifulSoup per fare il parsing dell'HTML
    soup = BeautifulSoup(html_str, 'html.parser')
    
    # Lista per memorizzare le righe della tabella
    table_data = []

    # Estrarre i titoli delle colonne (dall'elemento <thead> se presente)
    headers = [th.get_text(strip=True) for th in soup.find_all('th')]
    if headers:
        table_data.append(headers)

    # Controllare se esistono i tag <tr> per le righe della tabella
    rows = soup.find_all('tr')

    if rows:
        # Se ci sono i tag <tr>, processiamo le righe
        for row in rows:
            row_data = [td.get_text(strip=True) for td in row.find_all('td')]
            if row_data:  # Aggiungere solo se la riga contiene dati
                table_data.append(row_data)
    else:
        # Se non ci sono tag <tr>, processiamo i tag <td> direttamente
        current_row = []
        for td in soup.find_all('td'):
            current_row.append(td.get_text(strip=True))
            if len(current_row) == len(headers):  # Quando una riga è completa
                table_data.append(current_row)
                current_row = []

    return table_data


# funzioni in generale
def determinopathini():
    # determiniamo il path giusto per il file delle risorse
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)
    return application_path

def nomeFile(path):
        head, tail = os.path.split(path)
        return tail


    
#funzioni di parser
def dividiHTML(lista):
    div_terminale = []
    tupla=[]
    for element in lista:
        #print(f"Element: {element}")
        if "<th" in element:
            #print("procedura th")
            tupla = dividiTH(element)
            if len(tupla)>1:
                div_terminale.append(tupla)
        if "<td>" in element:
            #print("procedura td")
            tupla = dividiTD(element)
            if len(tupla)>1:
                div_terminale.append(tupla)
        #time.sleep(5)
    return div_terminale

def dividiTD(element):
    tupla = []
    lista = element.split("<td>")
    #print(f"lista: {lista}")
    for parte in lista:
        #print(type(parte))
        parte = parte.replace('\\n','')
        parte = parte.replace('\\t','')
        parte = parte.replace('\n','')
        parte = parte.replace('\t','')
        parte = parte.replace('</td>','')
        parte = parte.replace('\"','')
        parte = parte.replace('<a href=','')
        parte = parte.replace('</a>','')
        parte = parte.replace('<tr>','')
        parte = parte.replace('</tr>','')
        parte = parte.replace('</tbody>','')
        if "id=" in parte:
            url_e_nome = parte.split(">")
            url = url_e_nome[0]
            nome = url_e_nome[1]
            tupla.append(url.strip())
            tupla.append(nome.strip())
        else:
            if len(parte.strip())>1:
                tupla.append(parte.strip())
    return tupla

def dividiTH(element):
    tupla = []
    lista = element.split(">")
    #print(f"lista: {lista}")
    #time.sleep(5)
    for parte in lista:
        if "style" not in parte:
            if "<td" not in parte:
                #print(type(parte))
                parte = parte.replace('\\n','')
                parte = parte.replace('\\t','')
                parte = parte.replace('\n','')
                parte = parte.replace('\t','')
                parte = parte.replace('<th','')
                parte = parte.replace('</th>','')
                parte = parte.replace('/th','')
                parte = parte.replace('/tr','')
                parte = parte.replace('\"','')
                parte = parte.replace('<a href=','')
                parte = parte.replace('</a>','')
                parte = parte.replace('>','')
                parte = parte.replace('<','')
                if len(parte.strip())>1:
                        tupla.append(parte.strip())
    return tupla

def dividiHTMLmcq(lista):
    rereprint(f"Inizio funzione dividiHTMLmcq, la lista:\n{lista}")
    div_terminale = []
    tupla=[]
    rereprint(f"Questa è la lista nella funzione dividiHTMLmcq \n {lista}")
    for element in lista:
        tupla = dividiTDmcq(element)
        if len(tupla)>1:
            div_terminale.append(tupla)
        #time.sleep(5)
    return div_terminale

def dividiTDmcq(element):
    tupla = []
    if "<td>" in element or "thead" in element or "<th" in element:
          lista = element.split("<td>")    
    else: 
          lista = element.split("<td ")
    #print(f"lista: {lista}")
    for parte in lista:
        #print(type(parte))
        for pezzetto in parte.split("<span"):
            for pezzettino in pezzetto.split("</span>"):
                #print(f"Analisi pezzetto\n{pezzettino}")
                pezzettino = pezzettino.replace('\\n','')
                pezzettino = pezzettino.replace('style=','')
                pezzettino = pezzettino.replace('class=','')
                pezzettino = pezzettino.replace('\\t','')
                pezzettino = pezzettino.replace('\n','')
                pezzettino = pezzettino.replace('\t','')
                pezzettino = pezzettino.replace('</span>','')
                pezzettino = pezzettino.replace('\"','')
                pezzettino = pezzettino.replace('</tr','')
                pezzettino = pezzettino.replace('>','')
                pezzettino = pezzettino.replace('<tr','')
                pezzettino = pezzettino.replace('</td','')
                pezzettino = pezzettino.replace('<td','')
                pezzettino = pezzettino.replace('</tbody','')
                pezzettino = pezzettino.replace('\\n','')
                pezzettino = pezzettino.replace('\\t','')
                pezzettino = pezzettino.replace('\n','')
                pezzettino = pezzettino.replace('\t','')
                pezzettino = pezzettino.replace('</span>','')
                pezzettino = pezzettino.replace('\"','')
                pezzettino = pezzettino.replace('</tr','')
                pezzettino = pezzettino.replace('>','')
                pezzettino = pezzettino.replace('<tr','')
                pezzettino = pezzettino.replace('</td','')
                pezzettino = pezzettino.replace('<td','')
                pezzettino = pezzettino.replace('</tbody','')
                pezzettino = pezzettino.replace('<thead','')
                pezzettino = pezzettino.replace('/thead','')
                pezzettino = pezzettino.replace('tbody','')
                pezzettino = pezzettino.replace('body','')
                pezzettino = pezzettino.replace('data-v-2666a86c=','')
                pezzettino = pezzettino.replace('</td</tr','')
                pezzettino = pezzettino.replace('class=""','')
                pezzettino = pezzettino.replace('"rightAligned"','')
                pezzettino = pezzettino.replace('""','')
                pezzettino = pezzettino.replace('<','')
                pezzettino = pezzettino.replace('/','')
                pezzettino = pezzettino.replace('</td</tr','')
                pezzettino = pezzettino.replace('data-v-2666a86c="" class=','')                                
                pezzettino = pezzettino.replace('rightAligned','')
                pezzettino = pezzettino.replace('right','')
                pezzettino = pezzettino.replace('Aligned','')
                pezzettino = pezzettino.replace('left','')
                pezzettino = pezzettino.replace('span','')
                if len(pezzettino.strip())>0:
                    tupla.append(pezzettino.strip())
    return tupla

def determinoHeader(header):
    tupla = []
    lista = header.split("<th>")
    #print(f"lista: {lista}")
    for parte in lista:
        #print(type(parte))
        for pezzetto in parte.split(">"):
            for pezzettino in pezzetto.split("</td>"):
                #print(f"Analisi pezzetto\n{pezzettino}")
                if "class=" not in pezzettino:
                    if "style=" not in pezzettino:
                        pezzettino = pezzettino.replace('\\n','')
                        pezzettino = pezzettino.replace('\\t','')
                        pezzettino = pezzettino.replace('\n','')
                        pezzettino = pezzettino.replace('\t','')
                        pezzettino = pezzettino.replace('</td>','')
                        pezzettino = pezzettino.replace('\"','')
                        pezzettino = pezzettino.replace('>','')
                        pezzettino = pezzettino.replace('<tr','')
                        pezzettino = pezzettino.replace('</th','')
                        pezzettino = pezzettino.replace('<td','')
                        pezzettino = pezzettino.replace('</tbody','')
                        pezzettino = pezzettino.replace('\\n','')
                        pezzettino = pezzettino.replace('\\t','')
                        pezzettino = pezzettino.replace('\n','')
                        pezzettino = pezzettino.replace('\t','')
                        pezzettino = pezzettino.replace('</span>','')
                        pezzettino = pezzettino.replace('\"','')
                        pezzettino = pezzettino.replace('</tr','')
                        pezzettino = pezzettino.replace('>','')
                        pezzettino = pezzettino.replace('<tr','')
                        pezzettino = pezzettino.replace('</td','')
                        pezzettino = pezzettino.replace('<td','')
                        pezzettino = pezzettino.replace('</tbody','')
                        pezzettino = pezzettino.replace('<thead','')
                        pezzettino = pezzettino.replace('/thead','')
                        pezzettino = pezzettino.replace('tbody','')
                        pezzettino = pezzettino.replace('body','')
                        pezzettino = pezzettino.replace('data-v-2666a86c=','')
                        pezzettino = pezzettino.replace('</td</tr','')
                        pezzettino = pezzettino.replace('class=""','')
                        pezzettino = pezzettino.replace('"rightAligned"','')
                        pezzettino = pezzettino.replace('""','')
                        pezzettino = pezzettino.replace('<','')
                        pezzettino = pezzettino.replace('/','')
                        pezzettino = pezzettino.replace('</th','')
                        pezzettino = pezzettino.replace('</tr','')
                        pezzettino = pezzettino.replace('"rightAligned"','')
                        pezzettino = pezzettino.replace('""','')
                        pezzettino = pezzettino.replace('<','')
                        pezzettino = pezzettino.replace('/','')
                        pezzettino = pezzettino.replace('</td</tr','')
                        pezzettino = pezzettino.replace('data-v-2666a86c="" class=','')                                
                        pezzettino = pezzettino.replace('rightAligned','')
                        pezzettino = pezzettino.replace('right','')
                        pezzettino = pezzettino.replace('Aligned','')
                        pezzettino = pezzettino.replace('left','')
                        pezzettino = pezzettino.replace('span','')
                        if len(pezzettino.strip())>0:
                            tupla.append(pezzettino.strip())
    return tupla

#funzione che controlla se è un numero
def isfloat(testo):
    try:
        float(testo)
        return True
    except:
        return False
#variabili globali
pyautogui.FAILSAFE = False

files = {}
#queste due righe servono per inizializzare le informazioni dal file delle risorse
config = configparser.ConfigParser()
config_name = '/risorse/variabili.ini'
config.read(determinopathini()+config_name)
outputPath = ""
browser = config['DEFAULT']['browser']
driverPath = ""
if config['DEFAULT']['driverPath']=="True":
    fileName = filedialog.askopenfilename(filetypes=[("Eseguibili", ".exe")],title=f"Selezionare il driver")
    driverPath=fileName
#Creazioni connessioni col DB
#reprint(str(config['DATABASE']['default_path']))
print(f"path_app:{determinopathini()}")
con = sl.connect(determinopathini()+"/risorse/mathscinet_databse.db")
#cur serve per stampare i dati del db
cur = con.cursor()
driver=""
anniSelezionati = get_years_range(root)
####estraggo anni selezionati
# for x in config['DEFAULT']['anniSelezionati'].split(","):
#     anniSelezionati.append(x)
#######
divisionePercentile = True
colonna_eISSN = config['DEFAULT']['colonna_eISSN']
colonna_pISSN = config['DEFAULT']['colonna_pISSN']
colonnaTitolo = config['DEFAULT']['colonnaTitolo']
carattereDelimitatorecsv = config['DEFAULT']['carattereDelimitatorecsv']
rows=[]
filesCounter=0
tempo_singola_ricerca=float(config['DEFAULT']['tempo_singola_ricerca'])
tempo_attesa_caricamento=float(config['DEFAULT']['attesa_per_caricamento'])
#######################Funzioni programma
f = open(f"{determinopathini()}/log.txt", "w")

f.close()
logging.basicConfig(filename=f"{determinopathini()}/log.txt", level=logging.DEBUG,format="%(asctime)s \n\tMessage: %(message)s", filemode="w")
logging.debug("Debug logging test...")


#questa funzione serve per reprintare in debug
def reprint(stringa):
    print(stringa)
    logging.critical(str(stringa))
    
#questa funzione serve per reprintare in debug
def rereprint(stringa):
    reprint(stringa)
    # logging.debug(stringa)
    return
#questa funzione fa diventare una lista un array
def arriamoheader(roba):
    array = []
    for element in roba:
        # reprint(element)
        for x in element.split(';'):
            # reprint(x)
            if x == "Top 10%":
                x = "topX"
            if x == "10% - 35%":
                x = "XtoXXXV"
            if x == "35% - 60%":
                x = "XXXVtoXXXXXX"
            if x == "60% - 80%":
                x = "XXXXXXtoXXXXXXXX"
            if x == "Bottom 20%":
                x = "bottomXX"
            array.append(x)
    # reprint(array)
    return array


#inserimento not found db
def inserimento_not_found(connessione,row):
    for anno in anniSelezionati:
                        with connessione:
                                query = "INSERT INTO inforiviste ('titolo','p_issn','e_issn','MCQ','anno') VALUES (\""+row[0]+"\",\""+row[1]+"\",\""+row[2]+"\",\""+"Not Found"+"\",\""+str(anno)+"\");"
                                rereprint(f"Query per rivista {row[0]}\n{query}")
                                con.execute(query)

##Prima cosa da fare è caricare la lista dei files da controllare
settori=["MAT01","MAT02","MAT03","MAT04","MAT05","MAT06","MAT07","MAT08","MAT09"]

for x in settori:
    rereprint(f"Richiesta selezione files per settore {x}")
    answer= chiedisino(root,f"Vuoi selezionare il file per il settore {x}","Seleziona il file")
    if answer:
        fileName = filedialog.askopenfilename(filetypes=[("Excel files e CSV", ".xlsx .xls .csv")],title=f"Selezionare file per il settore {x}")
        sentinella = True
        for value in files.values():
            if value == fileName:
                sentinella = False
        if sentinella:
            files[f"{x}"] = fileName
        print(fileName)
        print(files)

#clicco due pulsanti con try
def clicca_questi_tre(pulsante1,pulsante2, pulsante3):
    time.sleep(tempo_attesa_caricamento)
    try:
        driver.find_element(By.XPATH,pulsante1).send_keys(Keys.ENTER)
        return 1
    except Exception as e:
        rereprint(f"Non e' riuscito a cliccare il bottone della tabella al primo tentativo\n{e}")
        try:
            driver.find_element(By.XPATH,pulsante2).send_keys(Keys.ENTER)
            return 2
        except Exception as e:
            rereprint(f"Non e' riuscito a cliccare il bottone della tabella al secondo tentativo\n{e}")
            try:
                driver.find_element(By.XPATH,pulsante3).send_keys(Keys.ENTER)
                return 3
            except Exception as e:
                rereprint(f"Non e' riuscito a cliccare il bottone della tabella al terzo tentativo\n{e}")
                return 0

#trova uno di questi due elementi nella pagina
def trova_uno_di_questi(elemento1,elemento2,elemento3):
    try:
        testa = driver.find_element(By.XPATH,elemento1)
        return testa
    except Exception as e:
        try:
            testa = driver.find_element(By.XPATH,elemento2)
            return testa
        except Exception as e:
            try:
                testa = driver.find_element(By.XPATH,elemento3)
                return testa
            except Exception as e:
                return False
        
#selezioniamo la cartella di output
info(root,"Seleziona cartella output", f"Selezionare la cartella di output")
fileDir = filedialog.askdirectory(title=f"Seleziona cartella output")
outputPath = fileDir
#questa funzione serve per controllare che il csv abbia le colonne importanti come ce le aspettiamo
def controlloheader(header):
    #reprint(header)
    indexs = []
    print(f"Header:{header}")
    indexs.append(checkheader(header,colonnaTitolo))
    indexs.append(checkheader(header,colonna_pISSN))
    indexs.append(checkheader(header,colonna_eISSN))
    print(f"index: {indexs}")
    if len(indexs)!=3:
        return False
    else:
        return indexs

def checkheader(header, testo):
    for i in range(len(header)):
        if testo in header[i]:
            return i
    return False
#questa funzione serve per vedere che tutte le righe abbiano le informazioni giuste
def controllorows(rows,file, indexsHeaders):
    # reprint(type(rows[0]))
    newrows = []
    for row in rows:
        # reprint(row)
        row = arriamoheader(row)
        reprint(row)
        reprint(len(row))
        if len(row) <3:
            reprint("Il file " + file + " ha una riga con qualche carattere particolare che non permette lo split della riga come vettore, ma la riconosce come tutta una riga testuale, oppure è stato sbagliato il caratte di divisione del csv\n")
            info(root,"Il file " + file + " ha una riga con qualche carattere particolare che non permette lo split della riga come vettore, ma la riconosce come tutta una riga testuale, oppure è stato sbagliato il caratte di divisione del csv!","End")
            return False
        if len(row[indexsHeaders[1]]) < 1 and len(row[indexsHeaders[2]]) < 3:
                reprint("Il file " + file + " ha una riga senza p_issn e e_issn\n")
                return False
        else:
            newrows.append(row)        
    return newrows

#funziona di apertura db
def aperturadb(con):
    reprint("Apertura DB, generazioni delle nuove tabelle di lavoro\n")
    #Cancella la tabella con i dati dai csv dell'ultima volta
    with con:
            con.execute("""
            DROP TABLE IF EXISTS general;
        """)

    #Creazione della tabella per memorizzare i nuovi dati dai csv

    with con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS general (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                p_issn TEXT,
                e_issn TEXT,
                sector TEXT
            );
        """)
    #risposta = messagebox.askquestion("Waiting", "Vuoi azzerare le informazioni presenti sul DB caricate dal web precedentemente?")
    #if (risposta in ["si","yes","y","Si","Yes"]):
        with con:
            con.execute("""
                DROP TABLE IF EXISTS inforiviste;
            """)
    #else:
    #    reprint("Non erano presenti dati precedentemente caricati dal web oppure non si vogliono cancellare i dati\n")
    with con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS inforiviste (
                titolo TEXT,
                p_issn TEXT,
                e_issn TEXT,
                anno TEXT,
                MCQ TEXT
            );
        """)

#controlla correttezza risultato prima di scriverlo su file

def controllo_results(results):
    results_to_iterate = results
    results_already_seen = []

    for tupla in results_to_iterate:
        if results_already_seen == []:
            sentinella = True
        else:
            sentinella = False
        for element in results_already_seen:
            if (tupla[0]==element[0] and tupla[1] == element[1] and tupla[2] == element[2] and tupla[4] == element[4]):
                sentinella = False
            else:
                sentinella = True
        if sentinella:
            # print(f"Tupla corrente: {tupla}")
            results_already_seen.append(tupla)
            i = 0
            for element in results:
                if (tupla[0]==element[0] and tupla[1] == element[1] and tupla[2] == element[2]):
                    i = i+1
            if i > 1:
                results_new = [x for x in results if not (tupla[0]==x[0] and tupla[1] == x[1] and tupla[2] == x[2])]
                results = results_new
                print("Fine cancellazione")
                if (tupla[0],tupla[1],tupla[2],"Not found",tupla[4],tupla[5]) not in results:
                    rereprint("Change")
                    results.append((tupla[0],tupla[1],tupla[2],"Not found",tupla[4],tupla[5]))
        i = 0
        rereprint("Risultato dopo il controllo dei dati acquisiti")
        for element in results:
            rereprint(element)
        return results
    

def caricamentoriviste(con, key, file):
    reprint("Caricamento riviste nei file csv nella tabella 'general' del DB\n")
    #Caricamento delle riviste nel database
    rereprint(f"File corrente :\n{file}")
    #time.sleep(20)
    
    if ".csv" in file:
        # reprint(value)
        file = open(file)
        csvreader = csv.reader(file, delimiter=carattereDelimitatorecsv, quoting=csv.QUOTE_ALL)
        header = []
        header = next(csvreader)
        header = arriamoheader(header)
        # reprint(header)
        #reprint(type(header))
        if controlloheader(header) == False:
            info(root,f"Nel file {file} le colonne non erano denominate nel modo in cui ci si aspettava.\nIl programma termina, correggere e riprovare","Error")
            exit()
        #questo vettore avrà gli indici del titolo, pISSN e eISSN
        indexsHeaders = controlloheader(header)
        rows = []
        for row in csvreader:
            rows.append(row)
        rows = controllorows(rows, file,indexsHeaders)
        file.close()
        if rows == False:
            exit()
        # reprint(rows)
        #carico la riga nel database
        for row in rows:
            pissn = ""
            eissn = ""
            if len(row[indexsHeaders[1]])>4:
                if row[indexsHeaders[1]][4]!= "-":
                    pissn = row[indexsHeaders[1]][0:4] + "-" + row[indexsHeaders[1]][4:]
                else:
                    pissn = row[indexsHeaders[1]]
            if len(row[indexsHeaders[2]])>4:
                if row[indexsHeaders[2]][4]!= "-":
                    eissn = row[indexsHeaders[2]][0:4] + "-" + row[indexsHeaders[2]][4:]
                else:
                    eissn = row[indexsHeaders[2]]

            query = "INSERT INTO general (title,p_issn,e_issn,sector) values(\""+ row[indexsHeaders[0]].replace(';','') + "\",\"" + pissn + "\",\"" + eissn + "\",\"" + key[0:5] + "\")"
            rereprint(f"Query:{query}")
            rereprint(f"row:{row}")
            #time.sleep(10)
            with con:
                con.execute(query)
    elif ".xlsx" in file:
        try:
            dfs = pd.read_excel(file,sheet_name=None, dtype=str,converters={colonnaTitolo:str,colonna_pISSN:str,colonna_eISSN:str})
            rows = []
            for keyinn in dfs.keys():
                for index, row in dfs[keyinn].iterrows():
                    if [str(row[colonnaTitolo]), str(row[colonna_pISSN]), str(row[colonna_eISSN])] not in rows:
                        rows.append([str(row[colonnaTitolo]), str(row[colonna_pISSN]), str(row[colonna_eISSN])])
        except:
            info(root,f"Nel file {file} le colonne non erano denominate nel modo in cui ci si aspettava.\nIl programma termina, correggere e riprovare","Error")
            exit()
        for row in rows:
            pissn = ""
            eissn = ""
            if len(str(row[1]))>4:
                if str(row[1])[4]!= "-":
                    pissn = str(row[1])[0:4] + "-" + str(row[1])[4:]
                else:
                    pissn = str(row[1])
            if len(str(row[2]))>4:
                if str(row[2])[4]!= "-":
                    eissn = str(row[2])[0:4] + "-" + str(row[2])[4:]
                else:
                    eissn = str(row[2])
            query = "INSERT INTO general (title,p_issn,e_issn,sector) values(\""+ str(row[0]).replace(';','') + "\",\"" + pissn + "\",\"" + eissn + "\",\"" + key[0:5] + "\")"
            rereprint(f"Query:{query}")
            rereprint(f"row:{row}")
            #time.sleep(10)
            with con:
                con.execute(query)

#funzione per salvare i dati nella cartella di salvataggio
def backupdb(key):
    current_time = datetime.datetime.now()
    today = str(current_time.year) + str(current_time.month) + str(current_time.day)
    #creazione cartelle
    if not os.path.exists(outputPath + '/mathscinetWebscraping'+today+'/'):
            os.makedirs(outputPath + '/mathscinetWebscraping'+today+'/')
            os.chmod(outputPath + '/mathscinetWebscraping'+today+'/',stat.S_IRWXO)

    if not os.path.exists(outputPath + '/mathscinetWebscraping'+today+'/'+key+'/'):
        os.makedirs(outputPath + '/mathscinetWebscraping'+today+'/'+key+'/')
        os.chmod(outputPath + '/mathscinetWebscraping'+today+'/'+key+'/',stat.S_IRWXO)
        os.makedirs(outputPath + '/mathscinetWebscraping'+today+'/'+key+'/CSV')
        os.chmod(outputPath + '/mathscinetWebscraping'+today+'/'+key+'/CSV',stat.S_IRWXO)
        os.makedirs(outputPath + '/mathscinetWebscraping'+today+'/'+key+'/EXCEL')
        os.chmod(outputPath + '/mathscinetWebscraping'+today+'/'+key+'/EXCEL',stat.S_IRWXO)


    #scrittura dati

  
    pathFilexlsx=outputPath + '/mathscinetWebscraping'+today+'/'+key+'/EXCEL/'+key+'_MCQ.xlsx'
    
    rereprint(f"Lista files keys: {list(files.keys())}")
    if key in list(files.keys()):
        rereprint(f"Sto memorizzando {key}")    
        with pd.ExcelWriter(pathFilexlsx, engine='xlsxwriter') as writer:
            for anno in anniSelezionati:
                rereprint(f"Salvo anno {anno} per {key}")
                data = con.execute("SELECT DISTINCT general.title,general.p_issn,general.e_issn,inforiviste.MCQ FROM general JOIN inforiviste ON inforiviste.titolo = general.title WHERE inforiviste.anno ='" + str(anno) + "' AND general.sector='"+key +"' ORDER BY inforiviste.MCQ DESC")
                results = data.fetchall()
                rereprint(f"Risultati query:{results}")
                results = controllo_results(results)
                pathFile=outputPath + '/mathscinetWebscraping'+today+'/'+key+'/CSV/'+key+'_MCQ' + str(anno) + '.csv'
                if len(results)>0:
                    with open(pathFile, 'w') as f:
                        wrt = csv.writer(f)
                        wrt.writerow(['title','p_issn','e_issn','MCQ'])
                        wrt.writerows(results)
                    
                    df = pd.read_csv(pathFile,sep=",")
                    #print(f"Pandas:\n{df}")
                    total=len(df.index)
                    vettorePercentili = []
                    for j in range(total):
                        vettorePercentili.append("00")
                    for j in range(total):
                        if j+1 <= math.ceil(total*10/100):
                            vettorePercentili[j]="10% TOP- Q1"
                        if j+1 > math.ceil(total*10/100):
                            vettorePercentili[j]="Q1"
                        if j+1 > math.ceil(total*25/100):
                            vettorePercentili[j]="Q2"
                        if j+1 > math.ceil(total*50/100):
                            vettorePercentili[j]="Q3"
                        if j+1 > math.ceil(total*75/100):
                            vettorePercentili[j]="Q4"
                    df['Percentile'] = vettorePercentili
                    df.to_csv(pathFile,index=False,sep=",",mode='w')
                    df.to_excel(writer, sheet_name=str(anno), index=False)
                
        
            

    reprint(' Salvataggio dei MCQ avvenuto con successo!\n')
    reprint(' I dati sono stati salvati nel file al seguente percorso ' + outputPath + '/mathscinetWebscraping'+today)


def long_process(key, numero_totale_files,numero_corrente):
#info sarà un vettore che conterra issn e il link associato, ad esempio info[0] = [issn_0,link_0]
    numerototale = len(rows)
    tempo = round((numerototale*tempo_singola_ricerca)/3600)
    minuti = (numerototale*tempo_singola_ricerca)/3600 - tempo
    if minuti < 0:
        tempo = tempo - 1
        minuti = round(((numerototale*tempo_singola_ricerca)/3600 - tempo)*60)
    else:
        minuti = round(minuti*60)
    rereprint(f"rows:{rows}")
    for i in range(0,numerototale):
        row = rows[i]
        os.system('cls')
        rereprint(f"Row:{row}")
        for j in range(3):
            pyautogui.press('shift')
        reprint(f"Analisi file {numero_corrente} su {numero_totale_files}\nStiamo prendendo MCQ.\nTempo stimato per {key}: {str(tempo)} ore e {str(minuti)} minuti \nAnalizzati {str(i+1)} su {str(numerototale)}...\n")
         
        reprint("Rivista corrente: " + row[0])
        try:
            if search(driver,row):
                get_MCQ(row[0],row[1],row[2],con)
            else:
                inserimento_not_found(con,row)
        except Exception as e:
            rereprint(f"La funzione run ha presentato un errore\n{e}\nvado avanti")
            inserimento_not_found(con,row)
    #salvataggio dati
    backupdb(key[0:5])


    

    

def recuperoinfopagina():
        dati = []
        try:
            WebDriverWait(driver,15).until(EC.presence_of_element_located((By.XPATH, config['HTML']['lista_riviste_prima_tabella'])))
            element = driver.find_element(By.XPATH,config["HTML"]["lista_riviste_prima_tabella"])
            HTML = str(element.get_attribute('innerHTML'))
            lista = HTML.split("<tr>")
            lista = dividiHTML(lista)
            if lista[0][0] =="ISSN":
                for riga in lista:
                    if riga[0] != "ISSN":
                        dati.append([riga[0],"https://mathscinet-ams-org.bibliopass.unito.it/"+riga[1]])
        except Exception as e:
            rereprint(f"Prima lista non trovata\n{e}")
        
        try:
            WebDriverWait(driver,15).until(EC.presence_of_element_located((By.XPATH, config['HTML']['lista_riviste_seconda_tabella'])))   
            element = driver.find_element(By.XPATH,config["HTML"]["lista_riviste_seconda_tabella"])
            HTML = str(element.get_attribute('innerHTML'))
            lista = HTML.split("<tr>")
            lista = dividiHTML(lista)
            if lista[0][0] =="ISSN":
                for riga in lista:
                    if riga[0] != "ISSN":
                        dati.append([riga[0],"https://mathscinet-ams-org.bibliopass.unito.it/"+riga[1]])
        except Exception as e:
            rereprint(f"Seconda lista non trovata\n{e}")
        rereprint(f"Questi sono i dati raccolti dalla tabella generica\n{dati}")
        #time.sleep(15)
        return dati


    


def validateLogin(username, password,driver,config):
    url_corrente = driver.current_url
    rereprint("Siamo in validateLogin")
    rereprint(f"Link corrente: {driver.current_url}")
    # driver.get_screenshot_as_file("screenshot.png")
    driver.find_element(By.XPATH,config['LINK']['username_unito']).clear()
    driver.find_element(By.XPATH,config['LINK']['password_unito']).clear()
    driver.find_element(By.XPATH,config['LINK']['username_unito']).send_keys(str(username.get()))
    driver.find_element(By.XPATH,config['LINK']['password_unito']).send_keys(str(password.get()))
    try:
        driver.find_element(By.XPATH,config['LINK']['accedi_unito_ita']).send_keys(Keys.ENTER)
    except:
        driver.find_element(By.XPATH,config['LINK']['accedi_unito_eng']).send_keys(Keys.ENTER)
    time.sleep(tempo_attesa_caricamento)
    rereprint(f"Link corrente: {driver.current_url}")
    if "https://idp.unito.it/idp/profile/SAML2/POST/SSO?execution=e" in driver.current_url:
        info(root,"User o password sbagliati, ritentare")
    elif driver.current_url == "https://mathscinet-ams-org.bibliopass.unito.it/mathscinet/publications-search":
        info(root,"Accesso a Mathscinet Effettuato con successo, chiudere finestra log in e continuare con la procedura!!")
    else:
        info(root,"Condizione inaspettata, termino. Se i problemi persistono provare variabile headless in file varibili.ini con valore False")
        driver.quit()
        exit()

    


    return None

def loginheadless(driver):
    #window
    tkWindow = tk.Tk()  
    # tkWindow.geometry('400x150')  
    tkWindow.title('Log-in UNITO request')
    tk.Label(tkWindow, text=f"Controllare che il link di log-in UNITO è il seguente:",font='Helvetica 10 bold').grid(row=0, columnspan=2)
    tk.Label(tkWindow, text=f"{driver.current_url}",fg='#f00',font='Helvetica 12 bold').grid(row=1, columnspan=2)
    #username label and text entry box
    usernameLabel = tk.Label(tkWindow, text="User Name",fg='#05214a',font='Helvetica 12 bold').grid(row=2, column=0)
    username = tk.StringVar()
    usernameEntry = tk.Entry(tkWindow, textvariable=username).grid(row=2, column=1)  

    #password label and password entry box
    passwordLabel = tk.Label(tkWindow,text="Password",fg='#05214a',font='Helvetica 12 bold').grid(row=3, column=0)  
    password = tk.StringVar()
    passwordEntry = tk.Entry(tkWindow, textvariable=password, show='*').grid(row=3, column=1)
    
    valiDateLogin = partial(validateLogin, username, password,tkWindow,driver)

    #login button
    loginButton = tk.Button(tkWindow, text="Login",fg='#05214a',bg='#fff',font='Helvetica 10 bold', command=valiDateLogin).grid(row=4, column=0)  
    loginButton = tk.Button(tkWindow, text="Login", command=valiDateLogin).grid(row=4, column=0)  
    closeButton = tk.Button(tkWindow, text="Close", command=lambda:tkWindow.destroy()).grid(row=5, column=0)  

    tkWindow.mainloop()

def loginheadless(driver,config):
    #window
    tkWindow = tk.Tk()  
    # tkWindow.geometry('400x150')  
    tkWindow.title('Log-in UNITO request')
    tk.Label(tkWindow, text=f"Controllare che il link di log-in UNITO è il seguente:",font='Helvetica 10 bold').grid(row=0, columnspan=2)
    tk.Label(tkWindow, text=f"{driver.current_url}",fg='#f00',font='Helvetica 12 bold').grid(row=1, columnspan=2)
    #username label and text entry box
    usernameLabel = tk.Label(tkWindow, text="User Name",fg='#05214a',font='Helvetica 12 bold').grid(row=2, column=0)
    username = tk.StringVar()
    usernameEntry = tk.Entry(tkWindow, textvariable=username).grid(row=2, column=1)  

    #password label and password entry box
    passwordLabel = tk.Label(tkWindow,text="Password",fg='#05214a',font='Helvetica 12 bold').grid(row=3, column=0)  
    password = tk.StringVar()
    passwordEntry = tk.Entry(tkWindow, textvariable=password, show='*').grid(row=3, column=1)
    
    valiDateLogin = partial(validateLogin, username, password,driver,config)

    #login button
    loginButton = tk.Button(tkWindow, text="Login", fg='#05214a',bg='#fff',font='Helvetica 10 bold',command=valiDateLogin).grid(row=4, column=0)  
    closeButton = tk.Button(tkWindow, text="Close",fg='#f00',bg='#fff',font='Helvetica 10 bold', command=lambda:tkWindow.destroy()).grid(row=4, column=1)  

    tkWindow.mainloop()


def loginmathscinet(driver,config):
    driver.get(config['LINK']['pagina_iniziale'])
    if config['DEFAULT']['headless']== "True":
        if config['LINK']['log_in_unito_parziale']in driver.current_url:
            loginheadless(driver,config)
        else:
            rereprint("Accesso a Mathscinet Effettuato con successo!!")
            return True

#serve per trovare la rivista tramite e_issn
def search(driver,row):
    rereprint("Sono in search")
    #controllo se posso cercare con p_issn
    if (len(row[1])<5 and len(row[2])<5):
        rereprint("PISSN e EISSN wrong, error in search")
        return False
    if len(row[1])>5:
        rereprint("Cerco con PISSN")
        if row[1][4] == "-":
            link = config['LINK']['link_search'].replace("???VARIABILE???",row[1])
        else:
            link = config['LINK']['link_search'].replace("???VARIABILE???",row[1][0:4] + '-' + row[1][4:])
        driver.get(link)
        time.sleep(tempo_attesa_caricamento)
        #controllo se la ricerca ha dato un buon risultato
        if "groupId" in driver.current_url or "journalId" in driver.current_url:
            rereprint("RIcerca PISSN con successo")
            return True
        else:
            rereprint("Verifico se non ne ha trovati più di uno, clicco il primo ancora indicizzato")
            try:
                #clicco il primo che è ancora indicizzato
                elements = driver.find_elements(By.XPATH,config['HTML']['MoreresultsSearch'])
                for element in elements:
                    rereprint(f'Elemento della lista risultati: {element.text}')
                    if config['HTML']['Noindexresearch'].lower() not in element.text.lower():
                        driver.get(element.find_element(By.XPATH,".//a").get_attribute('href'))
                        if "groupId" in driver.current_url or "journalId" in driver.current_url:
                            rereprint("Ricerca PISSN con successo")
                            return True
                rereprint("Tutti gli elementi della lista dei risultati apparentemente sono non idonei")
            except:
                rereprint("La verfica non è andata a buon fine")
    
    
    if(len(row[2])>5):
        rereprint("Cerco con EISSN")
        if (len(row[2])>9):
            return False
    
        if row[2][4] == "-":
            #provo con e_issn se riesco a trovare dei risultati
            link = config['LINK']['link_search'].replace("???VARIABILE???",row[2])
        else:
            link = config['LINK']['link_search'].replace("???VARIABILE???",row[2][0:4] + '-' + row[2][4:])
        driver.get(link)
        time.sleep(tempo_attesa_caricamento)
        #controllo se la ricerca ha dato un buon risultato
        if "groupId" in driver.current_url or "journalId" in driver.current_url:
            rereprint("RIcerca EISSN con successo")
            return True
        else:
            rereprint("Verifico se non ne ha trovati più di uno, clicco il primo ancora indicizzato")
            try:
                #clicco il primo che è ancora indicizzato
                elements = driver.find_elements(By.XPATH,config['HTML']['MoreresultsSearch'])
                for element in elements:
                    rereprint(f'Elemento della lista risultati: {element.text}')
                    if config['HTML']['Noindexresearch'].lower() not in element.text.lower():
                        driver.get(element.find_element(By.XPATH,".//a").get_attribute('href'))
                        if "groupId" in driver.current_url or "journalId" in driver.current_url:
                            rereprint("RIcerca EISSN con successo")
                            return True
                rereprint("Tutti gli elementi della lista dei risultati apparentemente sono non idonei")
                rereprint("RIcerca PISSN e EISSN senza successo")
                return False
            except:
                rereprint("RIcerca PISSN e EISSN senza successo")
                return False
    return False




#carichiamo i dati degli ultimi 5 anni della rivista corrente

def get_MCQ(titolo,p_issn,e_issn,con):
    #clicco il bottone per far comparire la tabella
    rereprint("Clicco il bottone della tabella")
    caso = clicca_questi_tre(config['HTML']['bottonetabella'],config['HTML']['bottonetabellasecondo'],config['HTML']['bottonetabellaterzo'])
    if caso == 0:
        inserimento_not_found(con,[titolo,p_issn,e_issn])
        return False

    rereprint(f"Prendo gli MCQ per {p_issn}")
    testa = trova_uno_di_questi(config["HTML"]["headerTabellamcq"],config["HTML"]["headerTabellamcq2"],config["HTML"]["headerTabellamcq3"])
    if testa == False:
        rereprint(f"Non ho trovato l'header della tabella {p_issn}")
        rereprint("Non sono riuscito a trovare il bottone della tabella, qualcosa è andato storto.")
        inserimento_not_found(con,[titolo,p_issn,e_issn])
        return False
    header = testa.get_attribute('innerHTML')
    #print(f"Header\n{header}")
    #header = determinoHeader(header)
    #print(f"header\n{header}")
    element = trova_uno_di_questi(config["HTML"]["tabellaMCQ"],config["HTML"]["tabellaMCQ2"],config["HTML"]["tabellaMCQ3"])
    HTML = str(element.get_attribute('innerHTML'))
    #print(HTML)
    #time.sleep(10)
    lista = parse_html_table(HTML)
    header = lista[0]
    rereprint("Ho completato la presa dati per questa rivista, li salvo nel db")
    for i in range(0,len(header)):
        if header[i] == "Year":
            index_anno = i
        if header[i] == "MCQ":
            index_mcq = i
    anniTrovati = []
    rereprint(f"Lista dopo di divisione per la rivista {titolo} \n{lista}")
    if lista == []:
        rereprint(f"Qualcosa e' andato storto, lista vuota!")
        inserimento_not_found(con,[titolo,p_issn,e_issn])
        return False
    for element in lista:
        if element[index_anno]!= "Year":
            anniTrovati.append(element[index_anno])
    for element in lista:
        if element[index_mcq]!="MCQ":
            if isfloat(element[index_anno]) and isfloat(element[index_mcq]):
                with con:
                    
                    query = "INSERT INTO inforiviste ('titolo','p_issn','e_issn','MCQ','anno') VALUES (\""+titolo+"\",\""+p_issn+"\",\""+e_issn+"\","+str(element[index_mcq])+",\""+element[index_anno]+"\");"
                    rereprint(f"Query per rivista {titolo}\n{query}")
                    con.execute(query)
    for anno in anniSelezionati:
        if str(anno) not in anniTrovati:
            with con:
                query = "INSERT INTO inforiviste ('titolo','p_issn','e_issn','MCQ','anno') VALUES (\""+titolo+"\",\""+p_issn+"\",\""+e_issn+"\",\""+"Not Found"+"\",\""+str(anno)+"\");"
                rereprint(f"Query per rivista {titolo}\n{query}")
                con.execute(query)
    return True



#questa funzione serve per trovare il link rispetto all'issn corrente
def get_link(row,info):
    for element in info:
        if element[0] == row[1]:
            return element[1]
    return "false"




######################################################################################

#programma principale

def webScraping():
        global rows
        global driver

        if browser=="" or files == {} or outputPath=="" or anniSelezionati == []:
            rereprint(f"Una delle variabili globali ha un valore che non può essere accettato. Il programma termina!\nBrowser: {browser}\ndriverPath: {driverPath}\nfiles: {files}\n outputPath={outputPath}\n anniSelezionati={anniSelezionati}")
            exit()
        
        selenium_logger = logging.getLogger("selenium")
        selenium_logger.setLevel(logging.CRITICAL)
        selenium_logger.addHandler(logging.StreamHandler())
        
        rereprint(f"Variabili globali inizio programma:\nBrowser: {browser}\ndriverPath: {driverPath}\nfiles: {files}\n outputPath={outputPath}\n anniSelezionati={anniSelezionati}")
        if (browser == "Edge"):
            try:
                if config['DEFAULT']['headless'] == "True":
                    options = EdgeOptions()
                    options.add_argument("--headless")
                    options.add_argument("--window-size=1920x1080")
                    options.add_argument('--disable-gpu')
                    options.add_argument('--no-sandbox')
                    options.add_argument("--start-maximized")
                    Driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()),options=options)
                else:
                    Driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))
            except:
                Driver = webdriver.Edge(driverPath)
        elif (browser == "Chrome"):
            try:
                if config['DEFAULT']['headless'] == "True":
                    options = ChromeOptions()
                    options.add_argument("--headless")
                    options.add_argument("--window-size=1920x1080")
                    options.add_argument('--disable-gpu')
                    options.add_argument('--no-sandbox')
                    options.add_argument("--start-maximized")
                    Driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
                else:
                    Driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
            except:
                Driver = webdriver.Chrome(driverPath) 
        elif (browser == "Mozilla Firefox"):
            try:
                Driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
            except:
                Driver = webdriver.Firefox(driverPath)
        else:
            exit()
            sys.exit(app.exec_())
        driver = Driver


        #login
        loginmathscinet(driver,config)

        if config['DEFAULT']['headless'] == "False":
            driver.maximize_window()
            root.attributes("-topmost", True)
            info(root,"Se nel browser automatico che è comparso chiede le credenziali, fare l'accesso. Poi cliccare OK.")
            driver.minimize_window()
            

        rereprint(f"files:\n{files}")
        #time.sleep(20)
        i=0
        for key in files.keys():
            i=i+1
            aperturadb(con)
            #caricamento dati da csv
            caricamentoriviste(con, key, files[key])

            #recupero la lista delle riviste con issn ed essn dalla tabella general

            cur.execute("SELECT DISTINCT title, p_issn,e_issn FROM general")

            rows = cur.fetchall()
            
            long_process(key[0:5], len(files.keys()),i)

      
 






webScraping()
con.close()
driver.close()
info(root,"Il programma è terminato","Fine")
sys.exit()
root.mainloop()
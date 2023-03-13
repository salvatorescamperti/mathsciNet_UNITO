#!/usr/bin/env python

import sys, stat
import os.path
from os import path
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QTabWidget,
    QFileDialog,
    QGridLayout,
    QScrollArea,
    QLabel,
    QCheckBox,
    QProgressBar,
    QLineEdit,
    QSizePolicy
)
import logging
import time
import math
import datetime
import configparser
import sqlite3 as sl
from asyncio.windows_events import NULL
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import datetime
import tkinter as tk
from tkinter import messagebox
import pyautogui
import pandas as pd
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
import openpyxl
import xlsxwriter
import pyinstaller_versionfile
import setuptools






#Finestra on top alert
def info(message, title="ShowInfo"):
    root = tk.Tk()
    root.overrideredirect(1)
    root.lift()
    root.withdraw()
    messagebox.showinfo(title, message)
    root.destroy()
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

def checkdriver(nome):
    if nome == "Edge":
        if path.exists(determinopathini()+"/drivers/Edge/Edgedriver.exe"):
            return determinopathini()+"/drivers/Edge/Edgedriver.exe"
        else:
            return False
    elif nome == "Chrome":
        if path.exists(determinopathini()+"/drivers/Chrome/chromedriver.exe"):
            return determinopathini()+"/drivers/Chrome/chromedriver.exe"
        else:
            return False
    elif nome == "Mozilla Firefox":
        if path.exists(determinopathini()+"/drivers/Mozilla/mozilladriver.exe"):
            return determinopathini()+"/drivers/Mozilla/mozilladriver.exe"
        else:
            return False
    else:
        return False
    
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
    div_terminale = []
    tupla=[]
    for element in lista:
        tupla = dividiTDmcq(element)
        if len(tupla)>1:
            div_terminale.append(tupla)
        #time.sleep(5)
    return div_terminale

def dividiTDmcq(element):
    tupla = []
    lista = element.split("<td>")
    #print(f"lista: {lista}")
    for parte in lista:
        #print(type(parte))
        for pezzetto in parte.split("<span>"):
            for pezzettino in pezzetto.split("</span>"):
                #print(f"Analisi pezzetto\n{pezzettino}")
                if "class=" not in pezzettino:
                    if "style=" not in pezzettino:
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
                        pezzettino = pezzettino.replace('</td</tr','')
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
                        pezzettino = pezzettino.replace('</th','')
                        pezzettino = pezzettino.replace('</tr','')
                        if len(pezzettino.strip())>0:
                            tupla.append(pezzettino.strip())
    return tupla

#variabili globali
pyautogui.FAILSAFE = False
browser = ""
driverPath = ""
files = {}
#queste due righe servono per inizializzare le informazioni dal file delle risorse
config = configparser.ConfigParser()
config_name = '\\variabili.ini'
config.read(determinopathini()+config_name)
outputPath = ""
#Creazioni connessioni col DB
#reprint(str(config['DATABASE']['default_path']))
print(f"path_app:{determinopathini()}")
con = sl.connect(determinopathini()+"\mathscinet_databse.db")
#cur serve per stampare i dati del db
cur = con.cursor()
driver=""
anniSelezionati = []
divisionePercentile = True
colonna_eISSN = "e_issn"
colonna_pISSN = "p_issn"
colonnaTitolo = "Source Title"
carattereDelimitatorecsv = ";"

#######################Funzioni programma
logging.basicConfig(filename="log.txt", level=logging.DEBUG,format="%(asctime)s \n\tMessage: %(message)s", filemode="w")
logging.debug("Debug logging test...")

#######################Funzioni programma
logging.basicConfig(filename="log.txt", level=logging.DEBUG,format="%(asctime)s \n\tMessage: %(message)s", filemode="w")
logging.debug("Debug logging test...")

#questa funzione serve per reprintare in debug
def reprint(stringa):
    print(stringa)
    logging.debug(str(stringa))
    
#questa funzione serve per reprintare in debug
def rereprint(stringa):
    reprint(stringa)
    logging.debug(stringa)
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

#questa funzione serve per vedre se una stringa è un float oppure no
def isfloat(stringa):
    try:
        float(stringa)
        return True
    except ValueError:
        return False


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
def controllorows(rows,file):
    # reprint(type(rows[0]))
    newrows = []
    for row in rows:
        # reprint(row)
        row = arriamoheader(row)
        # reprint(row)
        # reprint(len(row))
        if len(row[0]) != 0 or len(row[1]) != 0 or len(row[2]) != 0 or len(row[3]) == 0:
            # if len(row[0]) < 1:
            #     reprint("Il file " + file + " ha una riga senza il titolo della rivista\n")
            #     return False
            # if len(row[1]) < 1:
            #     reprint("Il file " + file + " ha una riga senza il Source ID\n")
            #     return False
            # if not isfloat(row[2]):
            #     reprint("Il file " + file + " ha una riga con MCQ sbagliato\n")
            #     return False
            if len(row[3]) < 1 and len(row[4]) < 3:
                 reprint("Il file " + file + " ha una riga senza p_issn e e_issn\n")
                 return False
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

def caricamentoriviste(con):
    reprint("Caricamento riviste nei file csv nella tabella 'general' del DB\n")
    #Caricamento delle riviste nel database
    rereprint(f"files:\n{files}")
    #time.sleep(20)
    for key in files.keys():
        if ".csv" in files[key]:
            # reprint(value)
            file = open(files[key])
            csvreader = csv.reader(file, delimiter=carattereDelimitatorecsv)
            header = []
            header = next(csvreader)
            header = arriamoheader(header)
            # reprint(header)
            #reprint(type(header))
            if controlloheader(header) == False:
                info(f"Nel file {file} le colonne non erano denominate nel modo in cui ci si aspettava.\nIl programma termina, correggere e riprovare","Error")
                exit()
            #questo vettore avrà gli indici del titolo, pISSN e eISSN
            indexsHeaders = controlloheader(header)
            rows = []
            for row in csvreader:
                rows.append(row)
            rows = controllorows(rows, files[key])
            file.close()
            if rows == False:
                exit()
            # reprint(rows)
            #carico la riga nel database
            for row in rows:
                query = "INSERT INTO general (title,p_issn,e_issn,sector) values(\""+ row[indexsHeaders[0]] + "\",\"" + row[indexsHeaders[1]] + "\",\"" + row[indexsHeaders[2]] + "\",\"" + key[0:5] + "\")"
                rereprint(f"Query:{query}")
                rereprint(f"row:{row}")
                #time.sleep(10)
                with con:
                    con.execute(query)
        if ".xlsx" in files[key]:
            try:
                dfs = pd.read_excel(files[key],sheet_name=None)
                rows = []
                for keyinn in dfs.keys():
                    for index, row in dfs[keyinn].iterrows():
                        if [str(row[colonnaTitolo]), row[colonna_pISSN], row[colonna_eISSN]] not in rows:
                            rows.append([str(row[colonnaTitolo]), row[colonna_pISSN], row[colonna_eISSN]])
            except:
                info(f"Nel file {files[key]} le colonne non erano denominate nel modo in cui ci si aspettava.\nIl programma termina, correggere e riprovare","Error")
                exit()
            for row in rows:
                query = "INSERT INTO general (title,p_issn,e_issn,sector) values(\""+ str(row[0]) + "\",\"" + str(row[1]) + "\",\"" + str(row[2]) + "\",\"" + key[0:5] + "\")"
                rereprint(f"Query:{query}")
                rereprint(f"row:{row}")
                #time.sleep(10)
                with con:
                    con.execute(query)

#funzione per salvare i dati nella cartella di salvataggio
def backupdb(con):
    current_time = datetime.datetime.now()
    today = str(current_time.year) + str(current_time.month) + str(current_time.day)
    data = con.execute("SELECT title,p_issn,e_issn,sector FROM general")
    if not os.path.exists(determinopathini() + '\\bkup\\'):
        os.makedirs(determinopathini() + '\\bkup\\')
        os.chmod(determinopathini() + '\\bkup\\',stat.S_IRWXO)
    with open(determinopathini() + '\\bkup\\' + today + '.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['title','p_issn','e_issn','sector'])
        writer.writerows(data)

    reprint(' Backup del DB avvenuto con successo!\n')
    reprint(' I dati sono stati salvati nel file al seguente percorso ' + determinopathini() +'\\bkup\\' + today + '.csv\n')

    if not os.path.exists(outputPath + '\\mathscinetWebscraping'+today+'\\'):
            os.makedirs(outputPath + '\\mathscinetWebscraping'+today+'\\')
            os.chmod(outputPath + '\\mathscinetWebscraping'+today+'\\',stat.S_IRWXO)
    if not os.path.exists(outputPath + '\\mathscinetWebscraping'+today+'\\tabellaGenerale\\'):
            os.makedirs(outputPath + '\\mathscinetWebscraping'+today+'\\tabellaGenerale\\')
            os.chmod(outputPath + '\\mathscinetWebscraping'+today+'\\tabellaGenerale\\',stat.S_IRWXO)
    if not os.path.exists(outputPath + '\\mathscinetWebscraping'+today+'\\NotFound\\'):
            os.makedirs(outputPath + '\\mathscinetWebscraping'+today+'\\NotFound\\')
            os.chmod(outputPath + '\\mathscinetWebscraping'+today+'\\NotFound\\',stat.S_IRWXO)
    for i in range(9):
        if not os.path.exists(outputPath + '\\mathscinetWebscraping'+today+'\\MAT0'+str(i+1)+'\\'):
            os.makedirs(outputPath + '\\mathscinetWebscraping'+today+'\\MAT0'+str(i+1)+'\\')
            os.chmod(outputPath + '\\mathscinetWebscraping'+today+'\\MAT0'+str(i+1)+'\\',stat.S_IRWXO)
            os.makedirs(outputPath + '\\mathscinetWebscraping'+today+'\\MAT0'+str(i+1)+'\\CSV')
            os.chmod(outputPath + '\\mathscinetWebscraping'+today+'\\MAT0'+str(i+1)+'\\CSV',stat.S_IRWXO)
            os.makedirs(outputPath + '\\mathscinetWebscraping'+today+'\\MAT0'+str(i+1)+'\\EXCEL')
            os.chmod(outputPath + '\\mathscinetWebscraping'+today+'\\MAT0'+str(i+1)+'\\EXCEL',stat.S_IRWXO)
    data = con.execute("SELECT DISTINCT general.title,general.p_issn,general.e_issn,inforiviste.MCQ,inforiviste.anno,general.sector FROM general JOIN inforiviste ON inforiviste.titolo = general.title")
    results = data.fetchall()
    rereprint(f"Risultati query:{results}")
    with open(outputPath + '\\mathscinetWebscraping'+today+'\\tabellaGenerale\\inforiviste' + today + '.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['title','p_issn','e_issn','MCQ','anno','sector'])
        writer.writerows(results)
        f.close()
        df_new = pd.read_csv(outputPath + '\\mathscinetWebscraping'+today+'\\tabellaGenerale\\inforiviste' + today + '.csv')
        GFG = pd.ExcelWriter(outputPath + '\\mathscinetWebscraping'+today+'\\tabellaGenerale\\inforiviste' + today + '.xlsx')
        df_new.to_excel(GFG, index=False)
        GFG.close()
    
        
    with open(determinopathini() + '\\bkup\\inforiviste' + today + '.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['title','p_issn','e_issn','MCQ','anno','sector'])
        writer.writerows(data)
        f.close()
    
    data = con.execute("SELECT DISTINCT general.title,general.p_issn,general.e_issn,inforiviste.MCQ,inforiviste.anno,general.sector FROM general JOIN inforiviste ON inforiviste.titolo = general.title Where inforiviste.MCQ='Not Found'")
    results = data.fetchall()
    rereprint(f"Risultati query:{results}")
    with open(outputPath + '\\mathscinetWebscraping'+today+'\\NotFound\\inforiviste' + today + '.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['title','p_issn','e_issn','MCQ','anno','sector'])
        writer.writerows(results)
        f.close()
        df_new = pd.read_csv(outputPath + '\\mathscinetWebscraping'+today+'\\NotFound\\inforiviste' + today + '.csv')
        GFG = pd.ExcelWriter(outputPath + '\\mathscinetWebscraping'+today+'\\NotFound\\inforiviste' + today + '.xlsx')
        df_new.to_excel(GFG, index=False)
        GFG.close()
    for i in range(9):
        pathFilexlsx=outputPath + '\\mathscinetWebscraping'+today+'\\MAT0'+str(i+1)+'\\EXCEL\\inforiviste.xlsx'
        
        rereprint(f"Lista files keys: {list(files.keys())}")
        if f"MAT0{str(i+1)}0" in list(files.keys()):
            rereprint(f"Sto memorizzando MAT0{str(i+1)}")    
            with pd.ExcelWriter(pathFilexlsx, engine='xlsxwriter') as writer:
                for anno in anniSelezionati:
                    rereprint(f"Salvo anno {anno} per MAT0{str(i+1)}")
                    data = con.execute("SELECT DISTINCT general.title,general.p_issn,general.e_issn,inforiviste.MCQ FROM general JOIN inforiviste ON inforiviste.titolo = general.title WHERE inforiviste.anno ='" + str(anno) + "' AND general.sector='MAT0"+str(i+1) +"' ORDER BY inforiviste.MCQ DESC")
                    results = data.fetchall()
                    rereprint(f"Risultati query:{results}")
                    pathFile=outputPath + '\\mathscinetWebscraping'+today+'\\MAT0'+str(i+1)+'\\CSV\\inforiviste' + str(anno) + '.csv'
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
    reprint(' I dati sono stati salvati nel file al seguente percorso ' + outputPath + '\\mathscinetWebscraping'+today)


class RicercaMCQ(QWidget):
    def __init__(self):
        super().__init__()
        
  
        # setting window geometry
        self.setMinimumSize(400, 300)
        self.windowLayout = QVBoxLayout()
        self.setLayout(self.windowLayout)
        self.etichetta_sopra = QLabel("Barra di Progressione")
        self.etichetta_sopra.setStyleSheet("QLabel""{""border-color: rgb(214, 213, 213);color: black;padding:5px;font-weight: 700;""}")
        self.etichetta_sopra.setFont(QFont('Times', 11))
        self.etichetta_warning=QLabel("Mentre il Webscraping è in corso: <html><ul><li> Non iconizzare il browser che è comparso automaticamente</li><li> Non bloccare la sessione utente</li><li> Non mettere in modalità sleep il computer</li><li> Non chiudere lo schermo (se è un portatile)</li><li>Durante tutta la procedura lo schermo deve rimanere acceso e la sessione sbloccata.</li></ul></html>")
        self.etichetta_warning.setStyleSheet("QLabel""{""border-color: rgb(214, 213, 213);color: red;padding:5px;font-weight: 500;""}")
        self.etichetta_warning.setFont(QFont('Times', 11))
        self.pbar = QProgressBar()
        self.windowLayout.addWidget(self.etichetta_sopra)
        self.windowLayout.addWidget(self.etichetta_warning)
        self.windowLayout.addWidget(self.pbar)
        self.pbar.setValue(0)
        self.pbar.setGeometry(20,30,200,50)
        self.windowLayout.setSpacing(0)
        # setting window action
        self.setWindowTitle("Progression Webscraping")
        self.bottoneCimprovvisa=Bottone("Chiusura Improvvisa - Salva i dati parziali raccolti - clicca tante volte")
        self.windowLayout.addWidget(self.bottoneCimprovvisa.bottone)
        self.bottoneCimprovvisa.bottone.pressed.connect(lambda: self.chiusuraImprovvisa())
  
        # showing all the widgets
        self.show()
        self.activateWindow()
  
    def chiusuraImprovvisa(self):
        backupdb(con)
        sys.exit("Chiusura Improvvisa attivata")

    def ricercaMCQ(self,driver,rows,con):
        #info sarà un vettore che conterra issn e il link associato, ad esempio info[0] = [issn_0,link_0]
        info = self.recuperoinfopagina()
        numerototale = len(rows)
        tempo = round((numerototale*10)/3600)  
        ora = datetime.datetime.now()     
        i = 0
        if tempo == 0:
            tempo = round((numerototale*10)/60)
            self.etichetta_sopra.setText("Stiamo acquisendo i MCQ.\nTempo stimato (connessione media): "+ str(tempo)+" minuti\nOra inizio: "+ ora.strftime("%X"))
        else:
            minuti = round((numerototale*10)/60) - 60*tempo
            if minuti < 0:
                minuti = (-1)*minuti
            self.etichetta_sopra.setText("Stiamo acquisendo i MCQ. Tempo stimato: (connessione media)"+ str(tempo)+" ore e " + str(minuti) + "minuti\nIn caso di connessione veloce dimezzare il tempo stimato. Ora inizio: "+ ora.strftime("%X"))
        for row in rows:
            os.system('cls')
            rereprint(f"Row:{row}")
            for j in range(3):
                pyautogui.press('shift')
            reprint("Stiamo prendendo MCQ.\nTempo stimato: "+ str(tempo)+" ore o minuti\nAnalizzati " + str(i+1) + " su " + str(numerototale) + "...\n")
            self.pbar.setValue(round((i+1)/numerototale*100))
            QApplication.processEvents()
            reprint("Rivista corrente: " + row[0])
            if len(row[1])>5:
                try:
                    prendiidati(driver, row, info,con)
                except Exception as e:
                    rereprint(f"La funzione ricercaMCQ ha presentato un errore\n{e}\nvado avanti")
            else:
                try:
                    search(driver,row,con)
                    prendiidati(driver, row, NULL,con)
                except Exception as e:
                    rereprint(f"La funzione ricercaMCQ ha presentato un errore\n{e}\nvado avanti")
                    for anno in anniSelezionati:
                        with con:
                                query = "INSERT INTO inforiviste ('titolo','p_issn','e_issn','MCQ','anno') VALUES (\""+row[0]+"\",\""+row[1]+"\",\""+row[2]+"\",\""+"Not Found"+"\",\""+str(anno)+"\");"
                                rereprint(f"Query per rivista {row[0]}\n{query}")
                                con.execute(query)      
            i = i+1
        self.close()


        # driver.get("https://mathscinet-ams-org.bibliopass.unito.it/mathscinet/search/journal/profile?groupId=33")
        # time.sleep(5)
        return NULL
    
    def recuperoinfopagina(self):
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


def loginmathscinet(driver,config):
    driver.get(config['LINK']['lista'])
    info("Cliccare OK una volta effettuato l'accesso (se richiesto). Dopo aver cliccato OK, se il browser automatico è stato iconizzato, espanderlo di nuovo.","Waiting")
    time.sleep(5)
    WebDriverWait(driver,15).until(EC.presence_of_element_located((By.XPATH, config['HTML']['testolista'])))


def prendiidati(driver,row,info,con):
    QApplication.processEvents()
    if info is NULL:
        search(driver,row,con)
        if "groupId" in driver.current_url or "journalId" in driver.current_url:
            rereprint("Siamo riusciti a caricare la pagina della rivista")
        else:
            rereprint("Non siamo riusciti a caricare la pagina della rivista, riprovo")
            search(driver,row,con)
        if "groupId" in driver.current_url or "journalId" in driver.current_url:
            rereprint("Siamo riusciti a caricare la pagina della rivista")
        else:
            rereprint("Non siamo riusciti a caricare la pagina della rivista, salto questa rivista")
            return
        get_MCQ(row[0],row[1],row[2],con)
        return
    else:
        link = get_link(row,info)
        if (link == "false"):
            reprint("Link registrato non ha dato risultati, provo con e_issn oppure con search")
            search(driver,row,con)
            if "groupId" in driver.current_url or "journalId" in driver.current_url:
                rereprint("Siamo riusciti a caricare la pagina della rivista")
            else:
                rereprint("Non siamo riusciti a caricare la pagina della rivista, riprovo")
                search(driver,row,con)
            if "groupId" in driver.current_url or "journalId" in driver.current_url:
                rereprint("Siamo riusciti a caricare la pagina della rivista")
            else:
                rereprint("Non siamo riusciti a caricare la pagina della rivista, salto questa rivista")
                return
            get_MCQ(row[0],row[1],row[2],con)
            return
        else:
            driver.get(link)
            if "groupId" in driver.current_url or "journalId" in driver.current_url:
                rereprint("Siamo riusciti a caricare la pagina della rivista")
                
            else:
                rereprint("Non siamo riusciti a caricare la pagina della rivista, riprovo")
                driver.get(link)
            if "groupId" in driver.current_url or "journalId" in driver.current_url:
                rereprint("Siamo riusciti a caricare la pagina della rivista")
                
            else:
                rereprint("Non siamo riusciti a caricare la pagina della rivista, salto questa rivista")
                return
            get_MCQ(row[0],row[1],row[2],con)
            return

#serve per trovare la rivista tramite e_issn
def search(driver,row,con):
    #controllo se posso cercare con p_issn
    QApplication.processEvents()
    if len(row[1])>5:
        if row[1][4] == "-":
            link = config['LINK']['link_search'].replace("???VARIABILE???",row[1])
        else:
            link = config['LINK']['link_search'].replace("???VARIABILE???",row[1][0:4] + '-' + row[1][4:])
        driver.get(link)
        time.sleep(3)
        #controllo se la ricerca ha dato un buon risultato
        if "groupId" in driver.current_url or "journalId" in driver.current_url:
            return
        else:
            rereprint("Verifico se non ne ha trovati due, clicco il primo")
            try:
                link = driver.find_element(By.XPATH,config['HTML']['firstitemsearch']).get_attribute('href')
                driver.get(link)
                if "groupId" in driver.current_url or "journalId" in driver.current_url:
                    return
            except:
                rereprint("La verfica non è andata a buon fine, provedo")
        # link = config['LINK']['link_search'].replace("???VARIABILE???",row[0])
        # driver.get(link)
        # time.sleep(3)
        # #controllo se la ricerca ha dato un buon risultato
        # if "groupId" in driver.current_url or "journalId" in driver.current_url:
        #     return
        # else:
        #     #verifico se ci sono stati dei match altrimenti proverò con e_issn
        #     rereprint("Vediamo se abbiamo trovato risultati e clicchiamo il primo - parte 1 - linea373")
        #     time.sleep(2)
        #     try:
        #         driver.find_element(By.XPATH,config['HTML']['mactchessearch']).text
        #     except:
        #         print("Provato la ricerca di un elemento per ricaricare la pagina")
        #     if "groupId" in driver.current_url or "journalId" in driver.current_url:
        #         return
        #     WebDriverWait(driver,15).until(EC.presence_of_element_located((By.XPATH, config['HTML']['mactchessearch'])))
        #     rereprint("Sono prima dell'if - linea 378")
        #     if config['HTML']['result0serch'] != driver.find_element(By.XPATH,config['HTML']['mactchessearch']).text:
        #         rereprint("Sto per cliccare il primo risultato")
        #         time.sleep(1)
        #         if "groupId" in driver.current_url or "journalId" in driver.current_url:
        #             return
        #         WebDriverWait(driver,15).until(EC.presence_of_element_located((By.XPATH, config['HTML']['firstitemsearch'])))
        #         link = driver.find_element(By.XPATH,config['HTML']['firstitemsearch']).get_attribute('href')
        #         driver.get(link)
        #         rereprint(f"Opero driver.get per {link}")
                # return       
    if(len(row[2])>5):
        if row[2][4] == "-":
            #provo con e_issn se riesco a trovare dei risultati
            link = config['LINK']['link_search'].replace("???VARIABILE???",row[2])
        else:
            link = config['LINK']['link_search'].replace("???VARIABILE???",row[2][0:4] + '-' + row[2][4:])
        driver.get(link)
        time.sleep(2)
        #controllo se la ricerca ha dato un buon risultato
        if "groupId" in driver.current_url or "journalId" in driver.current_url:
            return
        else:
            rereprint("Verifico se non ne ha trovati due, clicco il primo")
            try:
                link = driver.find_element(By.XPATH,config['HTML']['firstitemsearch']).get_attribute('href')
                driver.get(link)
                if "groupId" in driver.current_url or "journalId" in driver.current_url:
                    return
            except:
                rereprint("La verfica non è andata a buon fine, provedo")
    #salvo che non ho trovato il link
        for anno in anniSelezionati:
            with con:
                    query = "INSERT INTO inforiviste ('titolo','p_issn','e_issn','MCQ','anno') VALUES (\""+row[0]+"\",\""+row[1]+"\",\""+row[2]+"\",\""+"Not Found"+"\",\""+str(anno)+"\");"
                    rereprint(f"Query per rivista {row[0]}\n{query}")
                    con.execute(query)
        # else:
    #         rereprint("Vediamo se abbiamo trovato risultati e clicchiamo il primo - parte 2")
    #         #verifico se ci sono stati dei match altrimenti proverò col titolo
    #         WebDriverWait(driver,15).until(EC.presence_of_element_located((By.XPATH, config['HTML']['mactchessearch'])))
    #         time.sleep(1)
    #         if "groupId" in driver.current_url or "journalId" in driver.current_url:
    #             return
    #         if config['HTML']['result0serch'] != driver.find_element(By.XPATH,config['HTML']['mactchessearch']).text:
    #             rereprint("Sto per cliccare il primo risultato")
    #             WebDriverWait(driver,15).until(EC.presence_of_element_located((By.XPATH, config['HTML']['firstitemsearch'])))
    #             time.sleep(1)
    #             link = driver.find_element(By.XPATH,config['HTML']['firstitemsearch']).get_attribute('href')
    #             driver.get(link)
    #             rereprint(f"Opero driver.get per {link}")
    #             return       

    # #provo se col titolo riesco ad ottenere dei risultati
    # link = config['LINK']['link_search'].replace("???VARIABILE???",row[0])
    # driver.get(link)
    # time.sleep(3)
    # #controllo se la ricerca ha dato un buon risultato
    # if "groupId" in driver.current_url or "journalId" in driver.current_url:
    #     return
    # else:
    #     #verifico se ci sono stati dei match altrimentisi interromperà
    #     WebDriverWait(driver,15).until(EC.presence_of_element_located((By.XPATH, config['HTML']['mactchessearch'])))
    #     time.sleep(1)
    #     if config['HTML']['result0serch'] != driver.find_element(By.XPATH,config['HTML']['mactchessearch']).text:
    #         WebDriverWait(driver,15).until(EC.presence_of_element_located((By.XPATH, config['HTML']['firstitemsearch'])))
    #         link = driver.find_element(By.XPATH,config['HTML']['firstitemsearch']).get_attribute('href')
    #         driver.get(link)
    #         rereprint(f"Opero driver.get per {link}")
    #         return       



#carichiamo i dati degli ultimi 5 anni della rivista corrente

def get_MCQ(titolo,p_issn,e_issn,con):
    #clicco il bottone per far comparire la tabella
    rereprint("Clicco il bottone della tabella")
    try:
        WebDriverWait(driver,15).until(EC.presence_of_element_located((By.XPATH, config['HTML']['bottonetabella'])))
        driver.find_element(By.XPATH,config['HTML']['bottonetabella']).click()
    except Exception as e:
        rereprint(f"Non è riuscito a cliccare il bottone della tabella\n{e}")
        with con:
                for i in anniSelezionati:
                    query = "INSERT INTO inforiviste ('titolo','p_issn','e_issn','MCQ','anno') VALUES (\""+titolo+"\",\""+p_issn+"\",\""+e_issn+"\","+"Not found"+",\""+str(i)+"\");"
                    con.execute(query)

    #prendo gli ultimi cinque 5 anni mcq
    rereprint(f"Prendo gli MCQ per {p_issn}")
    time.sleep(2)
    try:
        rereprint(f"Controllo l'header della tabella {p_issn}")
        WebDriverWait(driver,15).until(EC.presence_of_element_located((By.XPATH, "//h5[contains(text(),'MCQ for')]//..//table/thead")))
        testa = driver.find_element(By.XPATH,config["HTML"]["headerTabellamcq"])
    except Exception as e:
        try:
            rereprint(f"Controllo l'header della tabella {p_issn}")
            WebDriverWait(driver,15).until(EC.presence_of_element_located((By.XPATH, config['HTML']['headerTabellamcq'])))
            testa = driver.find_element(By.XPATH,config["HTML"]["headerTabellamcq"])
        except:
            rereprint(f"Non ho trovato l'header della tabella {p_issn}")
            rereprint("Non sono riuscito a trovare il bottone della tabella, qualcosa è andato storto.")
            with con:
                    for i in anniSelezionati:
                        query = "INSERT INTO inforiviste ('titolo','p_issn','e_issn','MCQ','anno') VALUES (\""+titolo+"\",\""+p_issn+"\",\""+e_issn+"\","+"Not found"+",\""+str(i)+"\");"
                        con.execute(query)
            return

    header = testa.get_attribute('innerHTML')
    #print(f"Header\n{header}")
    header = determinoHeader(header)
    #print(f"header\n{header}")
    element = driver.find_element(By.XPATH,config["HTML"]["tabellaMCQ"])
    HTML = str(element.get_attribute('innerHTML'))
    #print(HTML)
    #time.sleep(10)
    lista = HTML.split("<tr>")
    #print(f"Lista prima di divsione\n{lista}")
    lista = dividiHTMLmcq(lista)
    rereprint("Ho completato la presa dati per questa rivista, li salvo nel db")
    for i in range(0,len(header)):
        if header[i] == "Year":
            index_anno = i
        if header[i] == "MCQ":
            index_mcq = i
    anniTrovati = []
    for element in lista:
        anniTrovati.append(element[index_anno])
    for element in lista:
        if element[index_anno] != "" and element[index_mcq] != "" and element[index_anno] != NULL and element[index_mcq] != NULL:
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


    rereprint("Da fare la funzione che verifica che i dati acquisiti abbiano senso?")


#questa funzione serve per trovare il link rispetto all'issn corrente
def get_link(row,info):
    for element in info:
        if element[0] == row[1]:
            return element[1]
    return "false"




######################################################################################

#programma principale

def webScraping():
        if browser=="" or driverPath=="" or files == {} or outputPath=="None" or outputPath=="" or anniSelezionati == []:
            rereprint(f"Una delle variabili globali ha un valore che non può essere accettato. Il programma termina!\nBrowser: {browser}\ndriverPath: {driverPath}\nfiles: {files}\n outputPath={outputPath}\n anniSelezionati={anniSelezionati}")
            return
        aperturadb(con)
        global driver
        rereprint(f"Variabili globali inizio programma:\nBrowser: {browser}\ndriverPath: {driverPath}\nfiles: {files}\n outputPath={outputPath}\n anniSelezionati={anniSelezionati}")
        if (browser == "Edge"):
            try:
                Driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))
            except:
                Driver = webdriver.Edge(driverPath)
        elif (browser == "Chrome"):
            try:
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

        #caricamento dati da csv
        caricamentoriviste(con)

        #recupero la lista delle riviste con issn ed essn dalla tabella general

        cur.execute("SELECT DISTINCT title, p_issn,e_issn FROM general")

        rows = cur.fetchall()






        ricercaMCQ = RicercaMCQ()
        ricercaMCQ.ricercaMCQ(driver,rows,con)


        #salvataggio dati
        backupdb(con)


        current_time = datetime.datetime.now()
        today = str(current_time.year) + str(current_time.month) + str(current_time.day)
            
        info("Fine Webscraping.","End")
        con.close()
        driver.close()
        sys.exit(0)
#funzioni webscraping
#classe bottone
class Bottone(QWidget):
    def __init__(self,titolo):
        self.bottone = QPushButton(titolo)
        # self.bottone.setMaximumWidth(450)
        #self.bottone.setMaximumWidth(160)
        if titolo == "Azzera Lista" or titolo=="Chiusura Improvvisa - Salva i dati parziali raccolti (clicca molte volte)":
            self.bottone.setStyleSheet("""
            QPushButton{
                border-color: rgb(74, 213, 255);
                color: black;
                background-color: rgb(235, 235, 235);
                padding:5px;
                font-weight: 700;
                }
                QPushButton::hover{
                    border-color: rgb(27, 255, 38);
                }
                QPushButton::pressed{
                    background-color: red;
                }
                QWidget
                {
                    border:2px solid rgb(74, 213, 255);
                    border-radius: 5%;margin:5px;
                }
            """)

        else:
            self.bottone.setStyleSheet("""
            QPushButton{
                border-color: rgb(74, 213, 255);
                color: black;
                background-color: rgb(235, 235, 235);
                padding:5px;
                font-weight: 700;
                }
                QPushButton::hover{
                    border-color: red;
                }
                QPushButton::pressed{
                    background-color: rgb(27, 255, 38);
                }
                QWidget
                {
                    border:2px solid rgb(74, 213, 255);
                    border-radius: 5%;margin:5px;
                }
            """)
            self.bottone.setFont(QFont('Times', 9))


#classe tab
class Maths(QWidget):
    def __init__(self,mathSerial,settoriScientifici):
        super(Maths, self).__init__()
        self.idName = f"MAT0{mathSerial}"
        self.filesCounter = 0
        self.files={}
        self.tab = QWidget()
        self.layout_tab = QVBoxLayout(self.tab)
        self.titleTab = f"{self.idName}"
        self.fullTitle =f"{self.idName} - {settoriScientifici[self.idName]}"
        self.listabottoni = []

        self.bottoneRicerca = Bottone("Cerca")
        self.bottoneRicerca.bottone.pressed.connect(lambda: self.avvioRicercafiles())
       

        self.listaFileslabel = QLabel("Lista files selezionati")
        self.listaFileslabel.setStyleSheet("QLabel""{""border-color: rgb(214, 213, 213);color: black;padding:5px;font-weight: 700;""}")
        self.listaFileslabel.setFont(QFont('Times', 11))

        self.testo = ""

        self.scrollw = QScrollArea()   
        #self.scrollw.setMaximumHeight(325)
        self.scrollw.setStyleSheet("""
 
        /* VERTICAL */
        QScrollBar:vertical {
            border: red;
            background: white;
            width: 10px;
            margin: 20px 0 26px 0;
        }

        QScrollBar::handle:vertical {
            background: red;
            min-height: 20px;
            border-radius: 5%;
        }

        QScrollBar::add-line:vertical {
            background: none;
            height: 20px;
            subcontrol-position: bottom;
            subcontrol-origin: margin;
        }

        QScrollBar::sub-line:vertical {
            background: none;
            height: 20px;
            subcontrol-position: top left;
            subcontrol-origin: margin;
            position: absolute;
        }

        QScrollBar:up-arrow:vertical {
            width: 20px;
            height: 20px;
            background: none;
            image: url('./frecciasu.png');
        }
        QScrollBar::down-arrow:vertical {
            width: 20px;
            height: 20px;
            background: none;
            image: url('./frecciagiu.png');
        }



        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }

    """)
        self.widget_inscroll = QWidget()
        self.widget_inscroll.setStyleSheet("QWidget""{""border-color: red 1.5px solid""}")
        vbox = QVBoxLayout()   
        self.widget_inscroll.setLayout(vbox)

        #Scroll Area Properties
        self.scrollw.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollw.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollw.setWidgetResizable(True)
        self.scrollw.setWidget(self.widget_inscroll)


        self.lista = QLabel(self.testo)
        
        # self.lista.setMinimumHeight(300)
        # self.lista.setMinimumWidth(500)
        self.lista.setStyleSheet("QLabel""{""font-weight: 450;background-color:white;margin:2px;padding:2px;border-color: red 1.5px solid""}")
        self.lista.setFont(QFont('Times', 9))
        vbox.addWidget(self.lista, stretch=4)
        # self.widget_inscroll.maximumHeight()
        self.bottoneAzzera = Bottone("Azzera Lista")
        self.bottoneAzzera.bottone.pressed.connect(lambda: self.azzeraLista())
        self.boxRicerca = BoxTabs(f"Seleziona i file di {self.fullTitle}",[self.bottoneRicerca.bottone,self.bottoneAzzera.bottone,self.listaFileslabel,self.scrollw])
        self.layout_tab.addWidget(self.boxRicerca.widget)
        
    #dialogo per trovare un file
    def ricercafiles(self):
        
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileNames(self,"Ricerca i Files", "","Files (*.csv *.xlsx)", options=options)
        sentinella = True
        if fileName:
            for n in fileName:
                for value in self.files.values():
                    if value == n:
                        sentinella = False
                if sentinella:
                    self.files[f"{self.idName}{self.filesCounter}"] = n
                    self.filesCounter +=1
            print(fileName)
            print(self.files)
            self.aggiungilista()
    
    def avvioRicercafiles(self):
        self.ricercafiles()
    
    #riscriva lista files
    def aggiungilista(self):
        lista = ""
        for n in self.files:
            lista = f"{lista} <html><ul><li>{nomeFile(self.files[n])}</li></ul></html>"
        self.lista.setText(lista)
    
    #azzera lista files
    def azzeraLista(self):
        self.files={}
        self.aggiungilista()





    


#classe box per tabs
class BoxTabs(QWidget):
    def __init__(self,titolo,elementi):
        super().__init__()
        self.widget = QWidget()
        self.widget.setMinimumSize(self.widget.maximumSize())
        self.widget.setStyleSheet("QWidget""{""background-color: rgb(214, 213, 213);border-color: rgb(173, 173, 173) 1px solid; border-radius: 5%;margin:5px;""}""")
        #self.widget.setStyleSheet("QWidget""{""background-color: red; border-color: black 2px solid; border-radius: 5%;margin:5px;""}""")
        #self.widget.setMinimumSize(50,50)
        self.nome_widget = QLabel(titolo)
        # self.nome_widget.setMinimumWidth(700)
        self.nome_widget.setStyleSheet("QLabel""{""border-color: none;color: black;padding:5px;font-weight: 700;""}")
        self.nome_widget.setFont(QFont('Times', 11))
        #self.nome_widget.move(5,5)
        # self.widgetElement = QWidget(self.widget)
        # self.widgetElement.setStyleSheet("QWidget""{""background-color: none;border-color: none; border-radius: 5%;margin:5px;""}""")
        #self.widgetElement.setStyleSheet("QWidget""{""background-color: black;border-color: black 1.5px solid; border-radius: 5%;margin:5px;""}""")
        #self.widgetElement.move(50,40)
        #self.widgetElement.setMinimumSize(300,600)
        #self.widgetElement.setMinimumSize(500,450)
        self.layout_widgetElement=QVBoxLayout(self.widget)
        self.layout_widgetElement.setAlignment(Qt.AlignCenter)
        self.layout_widgetElement.addWidget(self.nome_widget,stretch=1,alignment=Qt.AlignTop)
        self.layout_widgetElement.setSpacing(0)
        for e in elementi:
            if type(e) is QScrollArea:
                e.setMinimumHeight(400)
                self.layout_widgetElement.addWidget(e, stretch=4,alignment=Qt.AlignTop)
                e.maximumHeight()
                self.layout_widgetElement.addWidget(QWidget(), stretch=2,alignment=Qt.AlignTop)
                self.layout_widgetElement.addWidget(QWidget(), stretch=2,alignment=Qt.AlignTop)

            else:
                self.layout_widgetElement.addWidget(e, stretch=1,alignment=Qt.AlignTop)


#classe box
class Box(QWidget):
    def __init__(self,titolo,elementi):
        super().__init__()
        self.widget = QWidget()
        self.widget.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.widget.setStyleSheet("QWidget""{""background-color: rgb(214, 213, 213);border-color: none; border-radius: 5%;margin:5px;""}""")
        self.widget.setMinimumSize(350,325)
        self.nome_widget = QLabel(titolo,self.widget)
        self.nome_widget.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.nome_widget.setMaximumHeight(50)
        self.nome_widget.setStyleSheet("QLabel""{""border-color: none;color: black;padding:5px;font-weight: 700;""}")
        self.nome_widget.setFont(QFont('Times', 11))
        # self.nome_widget.move(5,5)
        #self.widgetElement.move(10,35)
        
        self.layout_widgetElement=QVBoxLayout(self.widget)
        self.layout_widgetElement.setAlignment(Qt.AlignCenter)
        # self.layout_widgetElement.sizeHint()
        self.layout_widgetElement.addWidget(self.nome_widget,alignment=Qt.AlignTop)
        self.layout_widgetElement.setSpacing(0)
        for e in elementi:
            self.layout_widgetElement.addWidget(e, stretch=1,alignment=Qt.AlignTop)
            e.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)

class BoxNMS(QWidget):
    def __init__(self,titolo,elementi):
        super().__init__()
        self.widget = QWidget()
        self.widget.setStyleSheet("QWidget""{""background-color: rgb(214, 213, 213);border-color: rgb(173, 173, 173) 1.5px solid; border-radius: 5%;margin:5px;""}""")
        self.widget.setMinimumSize(350,100)
        # self.nome_widget.move(5,5)
        # self.widgetElement = QWidget(self.widget)
        # self.widgetElement.setMinimumSize(350,100)
        # self.widgetElement.setStyleSheet("QWidget""{""background-color: none;border-color: none; border-radius: 5%;margin:5px;""}""")
        #self.widgetElement.move(10,35)
        # self.widgetElement.maximumSize()
        self.layout_widgetElement=QVBoxLayout(self.widget)
        self.layout_widgetElement.setSpacing(0)
        for e in elementi:
            self.layout_widgetElement.addWidget(e, stretch=1,alignment=Qt.AlignTop)

class BoxH(QWidget):
    def __init__(self,titolo,elementi):
        super().__init__()
        self.widget = QWidget()
        self.widget.setStyleSheet("QWidget""{""background-color: rgb(214, 213, 213);border-color: rgb(173, 173, 173) 1.5px solid; border-radius: 5%;margin:5px;""}""")
        #self.widget.setMinimumSize(350,325)
        self.nome_widget = QLabel(titolo)
        self.nome_widget.setMaximumHeight(50)
        self.nome_widget.setStyleSheet("QLabel""{""border-color: none;color: black;padding:5px;font-weight: 700;""}")
        self.nome_widget.setFont(QFont('Times', 11))
        # self.nome_widget.move(5,5)
        self.layoutwidgetSuperior = QVBoxLayout(self.widget)
        self.layoutwidgetSuperior.addWidget(self.nome_widget,stretch=1,alignment=Qt.AlignTop)
        self.widgetElement = QWidget()
        self.layoutwidgetSuperior.addWidget(self.widgetElement,stretch=1,alignment=Qt.AlignTop)
        #self.widgetElement.setMinimumSize(350,325)
        self.widgetElement.setStyleSheet("QWidget""{""background-color: none;border-color: none; border-radius: 5%;margin:5px;""}""")
        #self.widgetElement.move(10,35)
        #self.widgetElement.maximumSize()
        self.layout_widgetElement=QHBoxLayout(self.widgetElement)
        self.layout_widgetElement.setSpacing(0)
        for e in elementi:
            self.layout_widgetElement.addWidget(e, stretch=1,alignment=Qt.AlignTop)



# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.selectedDriver="None"
        self.selectedBrowser="None"
        self.selectedOutput= "None"
        self.setStyleSheet("background-color: black;")
        self.setWindowTitle("University of Turin - Department of Mathematics \"G. Peano\" - MATHSCINET WebScraping")
        self.setWindowIcon(QtGui.QIcon('dip_mate.png'))
        # self.setMinimumSize(1600, 900)

        #Parte oggetti

        self.finestraPrincipale = QTabWidget()
        self.finestraPrincipale.setStyleSheet("""QTabWidget{font-weight: 700;}QTabBar::tab:selected{background: red;color:white;}QWidget{border:auto;}QTabBar::scroller { /* the width of the scroll buttons */
            width: 100px;
        }

        QTabBar QToolButton { /* the scroll buttons are tool buttons */
            border-width: 2px;
            background: black;
        }

        QTabBar QToolButton::right-arrow { /* the arrow mark in the tool buttons */
            image: url('./frecciasupng.png');
        }

        QTabBar QToolButton::left-arrow {
            image: url('./frecciagiupng.png');
        }""")

        self.finestraPrincipale.setFont(QFont('Times', 9))
        self.finestraPrincipale.maximumSize()
        scroll_grigliaSecondaria = QScrollArea()
        scroll_grigliaSecondaria.setStyleSheet("""
 
        /* VERTICAL */
        QScrollBar:vertical {
            border: red;
            background: white;
            width: 5px;
            margin: 10px 0 10px 0;
        }

        QScrollBar::handle:vertical {
            background: red;
            min-height: 10px;
            border-radius: 5%;
        }

        QScrollBar::add-line:vertical {
            background: none;
            height: 10px;
            subcontrol-position: bottom;
            subcontrol-origin: margin;
        }

        QScrollBar::sub-line:vertical {
            background: none;
            height: 10px;
            subcontrol-position: top left;
            subcontrol-origin: margin;
            position: absolute;
        }

        QScrollBar:up-arrow:vertical {
            width: 20px;
            height: 20px;
            background: none;
            image: url('./frecciasu.png');
        }
        QScrollBar::down-arrow:vertical {
            width: 20px;
            height: 20px;
            background: none;
            image: url('./frecciagiu.png');
        }



        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }

    """)
        widgetGrigliaSecondaria = QWidget()
        
         
        

        #Scroll Area Properties
        scroll_grigliaSecondaria.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_grigliaSecondaria.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_grigliaSecondaria.setWidgetResizable(True)
        scroll_grigliaSecondaria.setWidget(widgetGrigliaSecondaria)









        
        widgetGrigliaSecondaria.setStyleSheet("QWidget""{""border:2px solid red;border-radius: 5%;margin:5px;""}""")
        #widgetGrigliaSecondaria.setMinimumSize(630,600)
        layout_GrigliaSecondaria = QGridLayout(widgetGrigliaSecondaria)

        #elementi nella griglia secondaria
        self.lista = QComboBox()
        self.lista.addItems(["Nessuno","Edge","Chrome","Mozilla Firefox"])
        self.lista.setStyleSheet("QComboBox::drop-down""{""border: 0px;""}""QComboBox::down-arrow""{""image:url(./freccia.png);width: 14px;height:14px;""}""QComboBox""{""background-color: white; border-color: rgb(87, 86, 86) 2px solid; border-radius: 0%;font-weight: 400;""}""QComboBox::hover""{""border-color: red;""}")
        self.lista.setFont(QFont('Times', 9))
        self.lista.currentTextChanged.connect(lambda: self.defaultDriver())
        bottone_cercaDriver = Bottone("Cerca Driver")
        bottone_cercaDriver.bottone.clicked.connect(lambda: self.openDriver())
        
        bottone_selezionaCartellaOutput = Bottone("Seleziona Cartella Output")
        bottone_selezionaCartellaOutput.bottone.clicked.connect(lambda: self.cartellaChoose())
        box_selectBrowser = Box("Input Browser e Output",[self.lista,bottone_cercaDriver.bottone,bottone_selezionaCartellaOutput.bottone])
        layout_GrigliaSecondaria.addWidget(box_selectBrowser.widget,0,0,2,1)

        widgetanni = QWidget()
        boxAnni = QGridLayout(widgetanni)
        widgetanni.setStyleSheet("QGridLayout""{""background-color: none;border-color: none;""}""")
        self.anni = []
        today = datetime.date.today()

        year = int(today.strftime("%Y"))
        for i in range(0,12):
            self.anni.append(QCheckBox(str(year-i)))
        for i in range(0,6):
            for j in range(0,2):
                boxAnni.addWidget(self.anni[(i*2)+j],i,j,alignment=Qt.AlignTop)
        box_anni = Box("MCQ: quali anni?",[widgetanni])
        #box_startProgram.widgetElement.move(0,50)
        layout_GrigliaSecondaria.addWidget(box_anni.widget,0,1,2,1) 

        bottone_quit = Bottone("Chiudi")
        bottone_quit.bottone.clicked.connect(self.close)
        bottone_start = Bottone("Start Now")
        bottone_start.bottone.clicked.connect(self.closeE)
        box_bottone_quit = BoxNMS("",[bottone_start.bottone,bottone_quit.bottone])
        # box_bottone_quit.widgetElement.setMinimumWidth(200)
        #box_bottone_quit.widgetElement.setFixedHeight(60)
        #box_bottone_quit.widget.setFixedHeight(60)
        #box_bottone_quit.widgetElement.move(20,0)
        box_bottone_quit.widget.setStyleSheet("QWidget""{""background-color: none;border-color: none;""}""")
        # box_bottone_quit.widgetElement.setStyleSheet("QWidget""{""background-color: none;border-color: none;""}""")
        layout_GrigliaSecondaria.addWidget(box_bottone_quit.widget,4,0) 

        self.listaSizeText = QComboBox()
        self.listaSizeText.addItems(["Modifica dimensione testo Interfaccia","8","9","10","11","12","14"])
        self.listaSizeText.setStyleSheet("QComboBox::drop-down""{""border: 0px;""}""QComboBox::down-arrow""{""image:url(./freccia.png);width: 14px;height:14px;""}""QComboBox""{""background-color: white; border-color: rgb(87, 86, 86) 2px solid; border-radius: 0%;font-weight: 400;""}""QComboBox::hover""{""border-color: red;""}")
        self.listaSizeText.setFont(QFont('Times', 9))
        self.listaSizeText.currentTextChanged.connect(lambda: self.chageSizeText())
        self.filesArea = QComboBox()
        self.filesArea.addItems(["Modifica Area lista Files","50px","100px","150px","200px", "300px","400px"])
        self.filesArea.setStyleSheet("QComboBox::drop-down""{""border: 0px;""}""QComboBox::down-arrow""{""image:url(./freccia.png);width: 14px;height:14px;""}""QComboBox""{""background-color: white; border-color: rgb(87, 86, 86) 2px solid; border-radius: 0%;font-weight: 400;""}""QComboBox::hover""{""border-color: red;""}")
        self.filesArea.setFont(QFont('Times', 9))
        self.filesArea.currentTextChanged.connect(lambda: self.chageAreaFiles())
        box_bottone_sizeText = BoxNMS("",[self.listaSizeText,self.filesArea])
        box_bottone_sizeText.widget.setStyleSheet("QWidget""{""background-color: none;border-color: none;""}""")
        # box_bottone_sizeText.widgetElement.setStyleSheet("QWidget""{""background-color: none;border-color: none;""}""")
        #box_bottone_sizeText.widgetElement.setFixedHeight(60)
        #box_bottone_sizeText.widget.setFixedHeight(60)
        #box_bottone_sizeText.widgetElement.move(20,0)
        layout_GrigliaSecondaria.addWidget(box_bottone_sizeText.widget,4,1) 
        

        self.etichetta_Driver = QLabel("Percorso Driver: ")
        self.etichetta_Driver.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.etichetta_Driver.setWordWrap(True)
        self.etichetta_Driver.setStyleSheet("QLabel""{""border-color: white;color: black;padding:5px;font-weight: 400;""}")
        self.etichetta_Driver.setFont(QFont('Times', 9))
        self.etichetta_Driver.setMinimumWidth(widgetGrigliaSecondaria.width())
        # self.etichetta_Driver.setMaximumWidth(600)
        self.etichetta_Driver.setMinimumHeight(70)
        self.etichetta_Output = QLabel("Percorso Output: ")
        self.etichetta_Output.setWordWrap(True)
        # self.etichetta_Output.setMaximumWidth(600)
        self.etichetta_Output.setMinimumHeight(70)
        self.etichetta_Output.setStyleSheet("QLabel""{""border-color: white;color: black;padding:5px;font-weight: 400;""}")
        self.etichetta_Output.setFont(QFont('Times', 9))
        box_verificaSelezioni = Box("Verifica Input Browser e Output",[self.etichetta_Driver,self.etichetta_Output])
        box_verificaSelezioni.widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout_GrigliaSecondaria.addWidget(box_verificaSelezioni.widget,2,0,1,2) 

 
        self.textBoxcolonnaTitolo = QLineEdit()
        self.textBoxcolonnaTitolo.setText(colonnaTitolo)
        self.textBoxcolonnaTitolo.setToolTip("Immettere il nome della colonna nei file selezionati in cui il programma si deve aspettare il titolo della rivista")
        self.textBoxcolonna_eISSN = QLineEdit()
        self.textBoxcolonna_eISSN.setText(colonna_eISSN)
        self.textBoxcolonna_eISSN.setToolTip("Immettere il nome della colonna nei file selezionati in cui il programma si deve aspettare il E-ISSN")
        self.textBoxcolonna_pISSN = QLineEdit()
        self.textBoxcolonna_pISSN.setText(colonna_pISSN)
        self.textBoxcolonna_pISSN.setToolTip("Immettere il nome della colonna nei file selezionati in cui il programma si deve aspettare il P-ISSN")
        self.textBoxcarattereDelimitatorecsv = QLineEdit()
        self.textBoxcarattereDelimitatorecsv.setText(carattereDelimitatorecsv)
        self.textBoxcarattereDelimitatorecsv.setToolTip("Immettere carattere che il programma si deve aspettare come separatore/delimitatore nei csv")
        box_datiFiles = BoxH("Proprietà dei files",[self.textBoxcolonnaTitolo,self.textBoxcolonna_eISSN,self.textBoxcolonna_pISSN,self.textBoxcarattereDelimitatorecsv])
        


        #Griglia opzioni
        

        widgetTabs = QWidget()
        layout_widgetTabs = QVBoxLayout(widgetTabs)
        widgetTabs.setStyleSheet("QWidget""{""border:2px solid red;border-radius: 5%;margin:5px;""}""")
        #widgetTabs.setMinimumSize(630,600)
        widgetTabsinside = QTabWidget()
        widgetTabsinside.setStyleSheet("""QTabWidget{font-weight: 700;}QTabBar::tab:selected{background: red;color:white;}QWidget{border:auto;}QTabBar::scroller { /* the width of the scroll buttons */
            width: 100px;
        }

        QTabBar QToolButton { /* the scroll buttons are tool buttons */
            border-width: 2px;
            background: black;
        }

        QTabBar QToolButton::right-arrow { /* the arrow mark in the tool buttons */
            image: url('./frecciasupng.png');
        }

        QTabBar QToolButton::left-arrow {
            image: url('./frecciagiupng.png');
        }
        QTabWidget>QWidget>QWidget{background: gray;}""")
        widgetTabsinside.setFont(QFont('Times', 9))
        self.maths=[]
        settoriScientifici = {"MAT01":"Logica Matematica", "MAT02":"Algebra", "MAT03":"Geometria", "MAT04":"Matematiche Complementari", "MAT05":"Analisi Matematica", "MAT06":"Probabilità e Statistica Matematica", "MAT07":"Fisica Matematica", "MAT08":"Analisi Numerica", "MAT09":"Ricerca Operativa"}
        for n in range(1,10):
            self.maths.append(Maths(n,settoriScientifici))
            print(f"Creata istanza Maths({self.maths[n-1].idName})")

        for n in range(1,10):
            widgetTabsinside.addTab(self.maths[n-1].tab,self.maths[n-1].titleTab)


        layout_widgetTabs.addWidget(widgetTabsinside, stretch=4)
        layout_widgetTabs.addWidget(box_datiFiles.widget, stretch=1) 
        self.finestraPrincipale.addTab(scroll_grigliaSecondaria, "Settings")
        self.finestraPrincipale.addTab(widgetTabs, "Files")
        
        
       

        # Set the central widget of the Window.
        self.setCentralWidget(self.finestraPrincipale)

    def closeE(self):
        global browser
        global driverPath
        global outputPath
        global files
        global anniSelezionati
        global carattereDelimitatorecsv
        global colonna_eISSN
        global colonna_pISSN
        global colonnaTitolo
        for n in range(1,10):
            for key in self.maths[n-1].files:
                files[key] = self.maths[n-1].files[key]
        for element in self.anni:
            if (element.isChecked()):
                anniSelezionati.append(element.text())
        if self.selectedBrowser=="" or self.selectedDriver=="" or files == {} or self.selectedOutput=="" or len(anniSelezionati)==0:
            rereprint(f"Una delle variabili globali ha un valore che non può essere accettato.\nBrowser: {browser}\ndriverPath: {driverPath}\nfiles: {files}\n outputPath={outputPath}\nanniSelezionati={anniSelezionati}")
            info("Assicurarsi di aver selezionato Browser, Driver, Cartella di output, almeno un anno ed almeno un file prima di avviare il Webscraping!","Warning")
            return
        browser = self.selectedBrowser
        driverPath = self.selectedDriver
        outputPath = self.selectedOutput
        colonnaTitolo = self.textBoxcolonnaTitolo.text()
        colonna_pISSN = self.textBoxcolonna_pISSN.text()
        colonna_eISSN = self.textBoxcolonna_eISSN.text()
        carattereDelimitatorecsv = self.textBoxcarattereDelimitatorecsv.text()
        self.close()
        webScraping()
    
    #ricerca automatica driver
    def defaultDriver(self):
        self.selectedBrowser = self.lista.currentText()
        print(f"currentBrowser {self.selectedBrowser}")
        print("Funzione defaultDriver in corso...")
        if self.selectedDriver != "None":
            self.selectedDriver = "None"
            self.etichetta_Driver.setText(f"Path Driver: {self.selectedDriver}")
        if checkdriver(self.selectedBrowser) != False:
            print("Il controllo driver è andato a buon fine.")
            self.selectedDriver=checkdriver(self.selectedBrowser)
            self.etichetta_Driver.setText(f"Path Driver: {self.selectedDriver}")
        print("Funzione defaultDriver fine")

    #seleziona cartella output
    def cartellaChoose(self):
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        fileName = QFileDialog.getExistingDirectory(self,"Selezione Cartella Output","", options=options)
        if fileName:
            self.selectedOutput = fileName
            self.etichetta_Output.setText(f"Path output: {self.selectedOutput}")
            print(self.selectedOutput)

    #seleziona driver
    def openDriver(self):
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Ricerca il driver", "","Executive (*.exe)", options=options)
        if fileName:
            self.selectedDriver = fileName
            self.etichetta_Driver.setText(f"Path driver: {self.selectedDriver}")
            print(fileName)
        
    def chageSizeText(self):

        if self.listaSizeText.currentText() == "9":
            rereprint("Cambio grandezza testo a 9")
            for widget in self.findChildren(QWidget):
                widget.setFont(QFont('Times', 9))
        if self.listaSizeText.currentText() == "8":
            rereprint("Cambio grandezza testo a 8")
            for widget in self.findChildren(QWidget):
                widget.setFont(QFont('Times', 9))

        if self.listaSizeText.currentText() == "10":
            rereprint("Cambio grandezza testo a 10")
            for widget in self.findChildren(QWidget):
                widget.setFont(QFont('Times', 10))

        if self.listaSizeText.currentText() == "11":
            rereprint("Cambio grandezza testo a 11")
            for widget in self.findChildren(QWidget):
                widget.setFont(QFont('Times', 11))

        if self.listaSizeText.currentText() == "12":
            rereprint("Cambio grandezza testo a 12")
            for widget in self.findChildren(QWidget):
                widget.setFont(QFont('Times', 12))

        if self.listaSizeText.currentText() == "14":
            rereprint("Cambio grandezza testo a 14")
            for widget in self.findChildren(QWidget):
                widget.setFont(QFont('Times', 14))

    def chageAreaFiles(self):

        if self.filesArea.currentText() == "50px":
            rereprint("Cambio grandezza testo a 9")
            for widget in self.findChildren(QWidget):
                if type(widget) is QScrollArea:
                    widget.setMinimumHeight(50)

        if self.filesArea.currentText() == "100px":
            rereprint("Cambio grandezza testo a 10")
            for widget in self.findChildren(QWidget):
                if type(widget) is QScrollArea:
                    widget.setMinimumHeight(100)

        if self.filesArea.currentText() == "150px":
            rereprint("Cambio grandezza testo a 11")
            for widget in self.findChildren(QWidget):
                if type(widget) is QScrollArea:
                    widget.setMinimumHeight(150)

        if self.filesArea.currentText() == "200px":
            rereprint("Cambio grandezza testo a 12")
            for widget in self.findChildren(QWidget):
                if type(widget) is QScrollArea:
                    widget.setMinimumHeight(200)
        
        if self.filesArea.currentText() == "300px":
            rereprint("Cambio grandezza testo a 12")
            for widget in self.findChildren(QWidget):
                if type(widget) is QScrollArea:
                    widget.setMinimumHeight(300)
        
        if self.filesArea.currentText() == "400px":
            rereprint("Cambio grandezza testo a 12")
            for widget in self.findChildren(QWidget):
                if type(widget) is QScrollArea:
                    widget.setMinimumHeight(400)





    



app = QApplication(sys.argv)


window = MainWindow()
window.show()

app.exec()
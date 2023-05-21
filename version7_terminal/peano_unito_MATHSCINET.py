#!/usr/bin/env python

import sys, stat
import os.path
from os import path
# from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject
# from PyQt5 import QtGui
# from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
     QFileDialog
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
from tkinter import messagebox, filedialog
import pyautogui
import pandas as pd
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
import openpyxl
import xlsxwriter
# import pyinstaller_versionfile
# import setuptools






#Finestra on top alert
def info(message, title="ShowInfo"):
    root = tk.Tk()
    root.overrideredirect(1)
    root.lift()
    root.withdraw()
    messagebox.showinfo(title, message)
    root.destroy()

def chiedisino(message, title="ShowInfo"):
    root = tk.Tk()
    root.overrideredirect(1)
    root.lift()
    root.withdraw()
    risposta = messagebox.askyesno(title, message)
    root.destroy()
    return risposta
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

files = {}
#queste due righe servono per inizializzare le informazioni dal file delle risorse
config = configparser.ConfigParser()
config_name = '\\risorse\\variabili.ini'
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
con = sl.connect(determinopathini()+"\\risorse\\mathscinet_databse.db")
#cur serve per stampare i dati del db
cur = con.cursor()
driver=""
anniSelezionati = []
####estraggo anni selezionati
for x in config['DEFAULT']['anniSelezionati'].split(","):
    anniSelezionati.append(x)
#######
divisionePercentile = True
colonna_eISSN = config['DEFAULT']['colonna_eISSN']
colonna_pISSN = config['DEFAULT']['colonna_pISSN']
colonnaTitolo = config['DEFAULT']['colonnaTitolo']
carattereDelimitatorecsv = config['DEFAULT']['carattereDelimitatorecsv']
rows=[]
filesCounter=0

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

##Prima cosa da fare è caricare la lista dei files da controllare
settori=["MAT01","MAT02","MAT03","MAT04","MAT05","MAT06","MAT07","MAT08","MAT09"]

for x in settori:
    rereprint(f"Richiesta selezione files per settore {x}")
    answer= chiedisino(f"Vuoi selezionare il file per il settore {x}","Seleziona il file")
    if answer:
        fileName = filedialog.askopenfilename(filetypes=[("Excel files e CSV", ".xlsx .xls .csv")],title=f"Selezionare file per il settore {x}")
        sentinella = True
        for value in files.values():
            if value == fileName:
                sentinella = False
        if sentinella:
            files[f"{x}{filesCounter}"] = fileName
            filesCounter +=1
        print(fileName)
        print(files)


#selezioniamo la cartella di output
messagebox.showinfo("Seleziona cartella output", f"Selezionare la cartella di output")
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
            info("Il file " + file + " ha una riga con qualche carattere particolare che non permette lo split della riga come vettore, ma la riconosce come tutta una riga testuale, oppure è stato sbagliato il caratte di divisione del csv!","End")
            return False
        #if len(row[0]) != 0 or len(row[1]) != 0 or len(row[2]) != 0 or len(row[3]) == 0:
            # if len(row[0]) < 1:
            #     reprint("Il file " + file + " ha una riga senza il titolo della rivista\n")
            #     return False
            # if len(row[1]) < 1:
            #     reprint("Il file " + file + " ha una riga senza il Source ID\n")
            #     return False
            # if not isfloat(row[2]):
            #     reprint("Il file " + file + " ha una riga con MCQ sbagliato\n")
            #     return False
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

def caricamentoriviste(con):
    reprint("Caricamento riviste nei file csv nella tabella 'general' del DB\n")
    #Caricamento delle riviste nel database
    rereprint(f"files:\n{files}")
    #time.sleep(20)
    for key in files.keys():
        if ".csv" in files[key]:
            # reprint(value)
            file = open(files[key])
            csvreader = csv.reader(file, delimiter=carattereDelimitatorecsv, quoting=csv.QUOTE_ALL)
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
            rows = controllorows(rows, files[key],indexsHeaders)
            file.close()
            if rows == False:
                exit()
            # reprint(rows)
            #carico la riga nel database
            for row in rows:
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
        if ".xlsx" in files[key]:
            try:
                dfs = pd.read_excel(files[key],sheet_name=None, dtype=str,converters={colonnaTitolo:str,colonna_pISSN:str,colonna_eISSN:str})
                rows = []
                for keyinn in dfs.keys():
                    for index, row in dfs[keyinn].iterrows():
                        if [str(row[colonnaTitolo]), str(row[colonna_pISSN]), str(row[colonna_eISSN])] not in rows:
                            rows.append([str(row[colonnaTitolo]), str(row[colonna_pISSN]), str(row[colonna_eISSN])])
            except:
                info(f"Nel file {files[key]} le colonne non erano denominate nel modo in cui ci si aspettava.\nIl programma termina, correggere e riprovare","Error")
                exit()
            for row in rows:
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
def backupdb():
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
    reprint(' I dati sono stati salvati nel file al seguente percorso ' + outputPath + '\\mathscinetWebscraping'+today)


def long_process():
#info sarà un vettore che conterra issn e il link associato, ad esempio info[0] = [issn_0,link_0]
    info = recuperoinfopagina()
    numerototale = len(rows)
    tempo = round((numerototale*8)/3600)  
    rereprint(f"rows:{rows}")
    for i in range(0,numerototale):
        row = rows[i]
        os.system('cls')
        rereprint(f"Row:{row}")
        for j in range(3):
            pyautogui.press('shift')
        reprint("Stiamo prendendo MCQ.\nTempo stimato: "+ str(tempo)+" ore\nAnalizzati " + str(i+1) + " su " + str(numerototale) + "...\n")
         
        reprint("Rivista corrente: " + row[0])
        if len(row[1])>5:
            try:
                prendiidati(driver, row, info,con)
            except Exception as e:
                rereprint(f"La funzione run ha presentato un errore\n{e}\nvado avanti")
                for anno in anniSelezionati:
                    with con:
                            query = "INSERT INTO inforiviste ('titolo','p_issn','e_issn','MCQ','anno') VALUES (\""+row[0]+"\",\""+row[1]+"\",\""+row[2]+"\",\""+"Not Found"+"\",\""+str(anno)+"\");"
                            rereprint(f"Query per rivista {row[0]}\n{query}")
                            con.execute(query)   
        else:
            try:
                search(driver,row,con)
                prendiidati(driver, row, NULL,con)
            except Exception as e:
                rereprint(f"La funzione run ha presentato un errore\n{e}\nvado avanti")
                for anno in anniSelezionati:
                    with con:
                            query = "INSERT INTO inforiviste ('titolo','p_issn','e_issn','MCQ','anno') VALUES (\""+row[0]+"\",\""+row[1]+"\",\""+row[2]+"\",\""+"Not Found"+"\",\""+str(anno)+"\");"
                            rereprint(f"Query per rivista {row[0]}\n{query}")
                            con.execute(query)      
    


    # driver.get("https://mathscinet-ams-org.bibliopass.unito.it/mathscinet/search/journal/profile?groupId=33")
    # time.sleep(5)
    #salvataggio dati
    backupdb()


    
    con.close()
    

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


    

    


def loginmathscinet(driver,config):
    driver.get(config['LINK']['lista'])
    


def prendiidati(driver,row,info,con):
    
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
            for anno in anniSelezionati:
                    with con:
                            query = "INSERT INTO inforiviste ('titolo','p_issn','e_issn','MCQ','anno') VALUES (\""+row[0]+"\",\""+row[1]+"\",\""+row[2]+"\",\""+"Not Found"+"\",\""+str(anno)+"\");"
                            rereprint(f"Query per rivista {row[0]}\n{query}")
                            con.execute(query)
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
                for anno in anniSelezionati:
                    with con:
                            query = "INSERT INTO inforiviste ('titolo','p_issn','e_issn','MCQ','anno') VALUES (\""+row[0]+"\",\""+row[1]+"\",\""+row[2]+"\",\""+"Not Found"+"\",\""+str(anno)+"\");"
                            rereprint(f"Query per rivista {row[0]}\n{query}")
                            con.execute(query)
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
                for anno in anniSelezionati:
                    with con:
                            query = "INSERT INTO inforiviste ('titolo','p_issn','e_issn','MCQ','anno') VALUES (\""+row[0]+"\",\""+row[1]+"\",\""+row[2]+"\",\""+"Not Found"+"\",\""+str(anno)+"\");"
                            rereprint(f"Query per rivista {row[0]}\n{query}")
                            con.execute(query)
                return
            get_MCQ(row[0],row[1],row[2],con)
            return

#serve per trovare la rivista tramite e_issn
def search(driver,row,con):
    #controllo se posso cercare con p_issn
    
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
            rereprint("Verifico se non ne ha trovati più di uno, clicco il primo ancora indicizzato")
            try:
                #clicco il primo che è ancora indicizzato
                elements = driver.find_elements(By.XPATH,config['HTML']['MoreresultsSearch'])
                for element in elements:
                    rereprint(f'Elemento della lista risultati: {element.text}')
                    if config['HTML']['Noindexresearch'] not in element.text:
                        driver.get(element.find_element(By.XPATH,".//a").get_attribute('href'))
                        if "groupId" in driver.current_url or "journalId" in driver.current_url:
                            return
                    rereprint("Tutti gli elementi della lista dei risultati apparentemente sono non idonei")
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
            rereprint("Verifico se non ne ha trovati più di uno, clicco il primo ancora indicizzato")
            try:
                #clicco il primo che è ancora indicizzato
                elements = driver.find_elements(By.XPATH,config['HTML']['MoreresultsSearch'])
                for element in elements:
                    rereprint(f'Elemento della lista risultati: {element.text}')
                    if config['HTML']['Noindexresearch'] not in element.text:
                        driver.get(element.find_element(By.XPATH,".//a").get_attribute('href'))
                        if "groupId" in driver.current_url or "journalId" in driver.current_url:
                            return
                rereprint("Tutti gli elementi della lista dei risultati apparentemente sono non idonei")
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
        global rows
        if browser=="" or files == {} or outputPath=="" or anniSelezionati == []:
            rereprint(f"Una delle variabili globali ha un valore che non può essere accettato. Il programma termina!\nBrowser: {browser}\ndriverPath: {driverPath}\nfiles: {files}\n outputPath={outputPath}\n anniSelezionati={anniSelezionati}")
            exit()
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

        info("Se nel browser automatico che è comparso chiede le credenziali, fare l'accesso. Poi cliccare OK.")
        driver.maximize_window()
        driver.minimize_window()

        #caricamento dati da csv
        caricamentoriviste(con)

        #recupero la lista delle riviste con issn ed essn dalla tabella general

        cur.execute("SELECT DISTINCT title, p_issn,e_issn FROM general")

        rows = cur.fetchall()
        
        long_process()

      
 





webScraping()
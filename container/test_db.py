import sqlite3


db_path = ".\\risorse\\mathscinet_databse.db"


query = "SELECT inforiviste.*,general.sector FROM inforiviste INNER JOIN general ON inforiviste.titolo = general.title where inforiviste.MCQ = 'Not Found' AND inforiviste.anno != '2025';"  # <-- cambia 'nome_tabella'
anno = '2022'
settore = 'MAT01A'
# query = f"""
#                 SELECT DISTINCT general.title, general.p_issn, general.e_issn, CASE WHEN inforiviste.MCQ != 'Not Found' THEN inforiviste.MCQ ELSE -1 END as MCQ, CASE WHEN inforiviste.MCQ = 'Not Found' THEN 'Not Found' ELSE NULL END AS Note
#                 FROM general 
#                 JOIN inforiviste ON inforiviste.titolo = general.title 
#                 WHERE inforiviste.anno = '{anno}' AND general.sector='{settore}' AND inforiviste.MCQ != 'Not Found'
#                 ORDER BY inforiviste.MCQ DESC
           
#                 """



query = f"""
 SELECT DISTINCT general.title, general.p_issn, general.e_issn, 
 CASE WHEN inforiviste.MCQ != 'Not Found' THEN cast(inforiviste.MCQ AS float) ELSE -1 END as MCQ
 , CASE WHEN inforiviste.MCQ = 'Not Found' THEN 'Not Found' ELSE NULL END AS Note
                FROM general 
                JOIN inforiviste ON inforiviste.titolo = general.title 
                WHERE inforiviste.anno = '2022' AND general.sector='MAT01A'
                ORDER BY CASE WHEN inforiviste.MCQ != 'Not Found' THEN cast(inforiviste.MCQ AS float) ELSE -1 END DESC
                 """
try:
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    
    cursor.execute(query)

    
    rows = cursor.fetchall()
    col_names = [desc[0] for desc in cursor.description]  # nomi colonne

    print("Colonne:", col_names)
    print("-" * 40)
    for row in rows:
        print(row)

except sqlite3.Error as e:
    print("❌ Errore nel database:", e)

finally:
    # 🔹 6. Chiusura della connessione
    if conn:
        conn.close()
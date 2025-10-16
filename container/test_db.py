import sqlite3


db_path = ".\\risorse\\mathscinet_databse.db"


query = "SELECT inforiviste.*,general.sector FROM inforiviste INNER JOIN general ON inforiviste.titolo = general.title where inforiviste.MCQ = 'Not Found' AND inforiviste.anno != '2025';"  # <-- cambia 'nome_tabella'
anno = '2022'
settore = 'MAT02B'
# query = f"""
#                 SELECT DISTINCT general.title, general.p_issn, general.e_issn, CASE WHEN inforiviste.MCQ != 'Not Found' THEN inforiviste.MCQ ELSE -1 END as MCQ, CASE WHEN inforiviste.MCQ = 'Not Found' THEN 'Not Found' ELSE NULL END AS Note
#                 FROM general 
#                 JOIN inforiviste ON inforiviste.titolo = general.title 
#                 WHERE inforiviste.anno = '{anno}' AND general.sector='{settore}' AND inforiviste.MCQ != 'Not Found'
#                 ORDER BY inforiviste.MCQ DESC
           
#                 """



query = f"""
 WITH base as (
                    SELECT DISTINCT general.title
                    , general.p_issn
                    , general.e_issn
                    , CASE WHEN inforiviste.MCQ != 'Not Found' THEN cast(inforiviste.MCQ as float) ELSE -1 END as MCQ
                    , CASE WHEN inforiviste.MCQ = 'Not Found' THEN 'Not Found' ELSE NULL END AS Note
                    FROM general 
                    JOIN inforiviste ON inforiviste.titolo = general.title 
                    WHERE inforiviste.anno = '{anno}' AND general.sector='{settore}'),
                    dup_titolo as (
                    select title, max(p_issn) as p_issn, max(e_issn) as e_issn, max(MCQ) as MCQ, 'duplicato' as Note
                    from base 
                    group by title
                    having count(*) > 1
                    ),
                    semifinal as (select * from base where title not in (select title from dup_titolo)
                    UNION ALL
                    select * from dup_titolo)
                    select * from semifinal
                    order by MCQ DESC




                    
                                                    """
query = f"""
    SELECT * FROM general
"""
query = f"""
    SELECT g1.title, 
    CASE WHEN max(g1.p_issn) != NULL AND max(g1.p_issn) != 'nan' and max(g1.p_issn) != '' THEN max(g1.p_issn) ELSE max(g2.p_issn) END AS p_issn,
    CASE WHEN max(g1.e_issn) != NULL AND max(g1.e_issn) != 'nan' and max(g1.e_issn) != '' THEN max(g1.e_issn) ELSE max(g2.e_issn) END AS e_issn,
    max(g1.sector), 'Duplicato in input' AS Note  
    from general g1
    INNER JOIN general g2
    on (g1.title = g2.title AND (g1.p_issn = g2.p_issn  OR g1.e_issn = g2.e_issn)) and g1.id != g2.id
    GROUP BY g1.title
"""
query = f"""
    WITH duplicati as (SELECT g1.title, 
    CASE WHEN max(nullif(g1.p_issn,'nan')) IS NOT NULL THEN max(nullif(g1.p_issn,'nan')) ELSE max(nullif(g2.p_issn,'nan')) END  AS p_issn,
    CASE WHEN max(nullif(g1.e_issn,'nan')) IS NOT NULL THEN max(nullif(g1.e_issn,'nan')) ELSE max(nullif(g2.e_issn,'nan')) END  AS e_issn,
    max(g1.sector) as sector, 'Duplicato in input' AS Note  
    from general g1
    INNER JOIN general g2
    on (g1.title = g2.title AND (g1.p_issn = g2.p_issn  OR g1.e_issn = g2.e_issn)) and g1.id != g2.id
    GROUP BY g1.title)
    SELECT title,p_issn,e_issn,sector, '' as Note
    FROM general
    WHERE title NOT IN (SELECT title FROM duplicati)
    UNION ALL
    SELECT title,p_issn,e_issn,sector,Note FROM duplicati
"""
query = f"""
SELECT DISTINCT general.title
                , general.p_issn
                , general.e_issn
                , CASE WHEN inforiviste.MCQ != 'Not Found' THEN cast(inforiviste.MCQ as float) ELSE -1 END as MCQ
                , CASE WHEN inforiviste.MCQ = 'Not Found' THEN 'Not Found' WHEN general.Note = 'Duplicato in input' THEN general.Note ELSE NULL END AS Note
                FROM general 
                JOIN inforiviste ON inforiviste.titolo = general.title 
                WHERE inforiviste.anno = '2024' AND general.sector='MAT02B'
                ORDER BY CASE WHEN inforiviste.MCQ != 'Not Found' THEN cast(inforiviste.MCQ as float) ELSE -1 END DESC
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
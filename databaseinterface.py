import sqlite3

def first_time_setup():
    conn = sqlite3.connect('searchengine.db')
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE keywords 
                        (word, urlid, PRIMARY KEY(urlid))
                   """)
    cursor.execute("""CREATE TABLE urls
                        (url, score, PRIMARY KEY(url))
                   """)
    conn.commit()




first_time_setup()

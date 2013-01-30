import sqlite3

def first_time_setup():
    conn = sqlite3.connect('searchengine.db')
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE keywords 
                        (word, postid)
                   """)
    cursor.execute("""CREATE TABLE links
                        (link, score)
                   """)

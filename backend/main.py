import os
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Biblioteka", root_path="/api")
DATABASE_URL = os.getenv("DATABASE_URL")

def polacz_z_db():
    return psycopg2.connect(DATABASE_URL)

class NowaKsiazka(BaseModel):
    tytul: str
    autor: str

@app.on_event("startup")
def utworz_tabele():
    conn = polacz_z_db()
    cursor = conn.cursor()

    #tabela książek

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ksiazki (
            id SERIAL PRIMARY KEY,
            tytul VARCHAR(255) NOT NULL,
            autor VARCHAR(255) NOT NULL
        );
    """)

    #tabela użytkowników

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS uzytkownicy (
            id SERIAL PRIMARY KEY,
            login VARCHAR(6) UNIQUE NOT NULL,
            haslo VARCHAR(255) NOT NULL,
            rola VARCHAR(50) DEFAULT 'user'
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()


@app.get("/ksiazki")
def pobierz_ksiazki():
    conn = polacz_z_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor) #RealDictCursor zmienia wyniki SQL na słowniki i przez to FastAPI zamienia łatwo na JSON
    cursor.execute("SELECT * FROM ksiazki;")
    dane = cursor.fetchall()

    cursor.close()
    conn.close()
    return dane

@app.get("/uzytkownicy")
def pobierz_uzytkownikow():
    conn = polacz_z_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT id, login, rola FROM uzytkownicy;")
    dane = cursor.fetchall()

    cursor.close()
    conn.close()
    return dane

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/ksiazki", status_code=201)
def dodaj_ksiazke(ksiazka: NowaKsiazka):
    conn = polacz_z_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO ksiazki (tytul, autor) VALUES (%s, %s) RETURNING id;", (ksiazka.tytul, ksiazka.autor)
    ) 
    nowe_id = cursor.fetchone()[0]

    conn.commit()
    cursor.close()
    conn.close()
    return {"id": nowe_id, "tytul": ksiazka.tytul, "autor": ksiazka.autor}

@app.delete("/ksiazki/{ksiazka_id}")
def usun_ksiazke(ksiazka_id: int):
    conn = polacz_z_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ksiazki WHERE id = %s RETURNING id;", (ksiazka_id,))
    usunieta = cursor.fetchone()

    if not usunieta:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Książka o podanym ID nie istnieje")

    conn.commit()
    cursor.close()
    conn.close()

    return {"status": "sukces", "usuniete_id": usunieta[0]}



# docker-compose up
# docker-compose down
# docker-compose up --build
# docker-compose down -v
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel

app = FastAPI(title="Biblioteka", root_path="/api")
DATABASE_URL = os.getenv("DATABASE_URL")

def polacz_z_db():
    return psycopg2.connect(DATABASE_URL)

class NowaKsiazka(BaseModel):
    tytul: str
    autor: str

class NowyUzytkownik(BaseModel):
    login: str
    haslo: str

class NoweWypozyczenie(BaseModel):
    ksiazka_id: int
    uzytkownik_id: int

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

    #dodawanie na starcie książki początkowej

    cursor.execute("SELECT COUNT(*) FROM ksiazki;")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO ksiazki (id, tytul, autor) VALUES (%s, %s, %s);",
            (1, 'Biblia', 'Jan Gutenberg')
        )

    #tabela użytkowników

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS uzytkownicy (
            id SERIAL PRIMARY KEY,
            login VARCHAR(6) UNIQUE NOT NULL,
            haslo VARCHAR(255) NOT NULL,
            rola VARCHAR(50) DEFAULT 'user'
        );
    """)

    #dodawanie na starcie konta admina

    cursor.execute("SELECT id FROM uzytkownicy WHERE login = 'admin';")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO uzytkownicy (login, haslo, rola) VALUES (%s, %s, %s);",
            ('admin', 'admin1', 'admin')
        )

    #tabela wypożyczeń, REFERENCES tworzy klucz obcy, ON DELETE CASCADE powoduje efekt kaskadowy (usunięcie książki z tabeli usuwa z tej tabeli wpisy dotyczące tej książki) - zabezpieczenie przed błędami

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wypozyczenia (
            id SERIAL PRIMARY KEY,
            ksiazka_id INTEGER NOT NULL REFERENCES ksiazki(id) ON DELETE CASCADE,
            uzytkownik_id INTEGER NOT NULL REFERENCES uzytkownicy(id) ON DELETE CASCADE,
            data_wypozyczenia TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    #synchronizacja licznika dla tabeli książek
    cursor.execute("SELECT setval('ksiazki_id_seq', (SELECT MAX(id) FROM ksiazki));")

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

@app.get("/ksiazki/{ksiazka_id}")
def pobierz_ksiazke(ksiazka_id: int):
    conn = polacz_z_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM ksiazki where id=%s;",(ksiazka_id,))
    dane = cursor.fetchone()
    if not dane:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Książka o podanym ID nie istnieje")
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
    try:
        conn = polacz_z_db()
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        cursor.fetchone()
        cursor.close()
        conn.close()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=503, detail="Baza danych nie odpowiada")

@app.post("/ksiazki", status_code=201)
def dodaj_ksiazke(ksiazka: NowaKsiazka):
    if ksiazka.tytul.strip() == "" or ksiazka.autor.strip() == "":
        raise HTTPException(status_code=400, detail="Tytuł albo autor nie może być pustym polem")

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

@app.put("/ksiazki/{ksiazka_id}")
def edytuj_ksiazke(ksiazka_id: int, ksiazka: NowaKsiazka):
    conn = polacz_z_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE ksiazki SET tytul = %s, autor = %s WHERE id = %s RETURNING id;",
        (ksiazka.tytul, ksiazka.autor, ksiazka_id))
    zaktualizowana = cursor.fetchone()

    if not zaktualizowana: #nie można zaktualizować danych o książce, która nie jest dodana do bazy danych
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Książka o podanym ID nie istnieje")

    conn.commit()
    cursor.close()
    conn.close()
    return {"id": ksiazka_id, "tytul": ksiazka.tytul, "autor": ksiazka.autor}

@app.post("/uzytkownicy", status_code=201)
def zarejestruj_uzytkownika(uzytkownik: NowyUzytkownik):
    conn = polacz_z_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM uzytkownicy WHERE login = %s;", (uzytkownik.login,))
    if cursor.fetchone(): #jeśli można pobrać z tabeli informacje o tym koncie - konto istnieje czyli login zajęty
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Ten login jest już zajęty")

    cursor.execute("INSERT INTO uzytkownicy (login, haslo) VALUES (%s, %s) RETURNING id, rola;",
        (uzytkownik.login, uzytkownik.haslo))

    wynik = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return {"id": wynik[0], "login": uzytkownik.login, "rola": wynik[1]}

# docker-compose up
# docker-compose down
# docker-compose up --build
# docker-compose down -v
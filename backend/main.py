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
    rok: int
    rodzaj: str

class NowyUzytkownik(BaseModel):
    login: str
    haslo: str

class NoweWypozyczenie(BaseModel):
    ksiazka_id: int
    uzytkownik_id: int
    typ: str

class DaneLogowania(BaseModel):
    login: str
    haslo: str

@app.on_event("startup")
def utworz_tabele():
    conn = polacz_z_db()
    cursor = conn.cursor()

    #tabela książek

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ksiazki (
            id SERIAL PRIMARY KEY,
            tytul VARCHAR(255) NOT NULL,
            autor VARCHAR(255) NOT NULL,
            rok INTEGER NOT NULL,
            rodzaj VARCHAR(255) NOT NULL
        );
    """)

    #dodawanie na starcie książki początkowej

    cursor.execute("SELECT COUNT(*) FROM ksiazki;")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO ksiazki (id, tytul, autor, rok, rodzaj) VALUES (%s, %s, %s, %s, %s);",
            (1, 'Biblia', 'Jan Gutenberg', 1452, "Książka")
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
            typ VARCHAR(255) NOT NULL,
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
        "INSERT INTO ksiazki (tytul, autor, rok, rodzaj) VALUES (%s, %s, %s, %s) RETURNING id;", (ksiazka.tytul, ksiazka.autor, ksiazka.rok, ksiazka.rodzaj)
    ) 
    nowe_id = cursor.fetchone()[0]

    conn.commit()
    cursor.close()
    conn.close()
    return {"id": nowe_id, "tytul": ksiazka.tytul, "autor": ksiazka.autor, "rok": ksiazka.rok, "rodzaj": ksiazka.rodzaj}

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
    cursor.execute("UPDATE ksiazki SET tytul = %s, autor = %s, rok = %s, rodzaj = %s WHERE id = %s RETURNING id;",
        (ksiazka.tytul, ksiazka.autor, ksiazka.rok, ksiazka.rodzaj, ksiazka_id))
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

@app.post("/logowanie")
def zaloguj_uzytkownika(dane: DaneLogowania):
    conn = polacz_z_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute(
        "SELECT id, login, rola FROM uzytkownicy WHERE login = %s AND haslo = %s;",
        (dane.login, dane.haslo)
    )
    uzytkownik = cursor.fetchone()
    cursor.close()
    conn.close()

    if not uzytkownik:
        raise HTTPException(status_code=401, detail="Nieprawidłowy login lub hasło")
    return uzytkownik

@app.get("/wypozyczenia/{uzytkownik_id}")
def pobierz_wypozyczenia_uzytkownika(uzytkownik_id: int):
    conn = polacz_z_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("SELECT id FROM uzytkownicy WHERE id = %s;", (uzytkownik_id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Użytkownik o podanym ID nie istnieje")

    cursor.execute("""
        SELECT k.tytul, w.typ, w.data_wypozyczenia
        FROM wypozyczenia w
        JOIN ksiazki k ON w.ksiazka_id = k.id
        WHERE w.uzytkownik_id = %s;
        """, (uzytkownik_id,)
    )

    dane = cursor.fetchall()
    cursor.close()
    conn.close()

    return dane

@app.post("/wypozyczenia", status_code=201)
def dodaj_wypozyczenie(wypoz: NoweWypozyczenie):
    conn = polacz_z_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO wypozyczenia (ksiazka_id, uzytkownik_id, typ) VALUES (%s, %s, %s) RETURNING id;",
            (wypoz.ksiazka_id, wypoz.uzytkownik_id, wypoz.typ)
        )
        nowe_id = cursor.fetchone()[0]
        conn.commit()
    except psycopg2.errors.ForeignKeyViolation:
        conn.rollback() #cofa transakcje w wyniku błędu
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Nie ma takiej książki lub użytkownika w bazie")

    cursor.close()
    conn.close()

    return {
        "id": nowe_id,
        "ksiazka_id": wypoz.ksiazka_id,
        "uzytkownik_id": wypoz.uzytkownik_id,
        "typ": wypoz.typ
    }

# docker-compose up
# docker-compose down
# docker-compose up --build
# docker-compose down -v
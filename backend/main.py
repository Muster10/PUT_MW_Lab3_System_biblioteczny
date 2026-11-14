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
            """
            INSERT INTO ksiazki (id, tytul, autor, rok, rodzaj) VALUES 
            (1, 'Biblia', 'Jan Gutenberg', 1452, 'Książka'),
            (2, 'The Walking Dead', 'Robert Kirkman, Tony Moore', 2003, 'Komiks'),
            (3, 'Punisher: Witaj powrotem, Frank', 'Garth Ennis, Steve Dillon', 2000, 'Komiks'),
            (4, 'Neuromancer', 'William Gibson', 1984, 'Książka'),
            (5, 'Człowiek z Wysokiego Zamku', 'Philip K. Dick', 1962, 'Książka'),
            (6, 'Daredevil: Odrodzony', 'Frank Miller, David Mazzucchelli', 1986, 'Komiks'),
            (7, 'Czy androidy śnią o elektrycznych owcach?', 'Philip K. Dick', 1968, 'Książka'),
            (8, 'Ubik', 'Philip K. Dick', 1969, 'Książka'),
            (9, 'Pixel', 'Idea Ahead', 2023, 'Czasopismo'),
            (10, 'Trudno być bogiem', 'Arkadij i Borys Strugaccy', 1964, 'Książka'),
            (11, 'Ekrany', 'Wydawnictwo Ekrany', 2023, 'Czasopismo'),
            (12, 'Piknik na skraju drogi', 'Arkadij i Borys Strugaccy', 1972, 'Książka'),
            (13, 'Modlitwa o Owena', 'John Irving', 1989, 'Książka'),
            (14, 'Regulamin tłoczni win', 'John Irving', 1985, 'Książka'),
            (15, 'Świat według Garpa', 'John Irving', 1978, 'Książka'),
            (16, 'Lód', 'Jacek Dukaj', 2007, 'Książka'),
            (17, 'Inne pieśni', 'Jacek Dukaj', 2003, 'Książka'),
            (18, 'Perfekcyjna niedoskonałość', 'Jacek Dukaj', 2004, 'Książka'),
            (19, 'Czarne oceany', 'Jacek Dukaj', 2001, 'Książka'),
            (20, 'Kino', 'Fundacja Kino', 2023, 'Czasopismo'),
            (21, 'X-Men: Mroczna Phoenix', 'Chris Claremont, John Byrne', 1980, 'Komiks'),
            (22, 'Spider-Man: Ostatnie łowy Kravena', 'J.M. DeMatteis, Mike Zeck', 1987, 'Komiks'),
            (23, 'Ślepnąc od świateł', 'Jakub Żulczyk', 2014, 'Książka'),
            (24, 'Hellboy: Nasienie zniszczenia', 'Mike Mignola', 1994, 'Komiks'),
            (25, 'Morfina', 'Szczepan Twardoch', 2012, 'Książka'),
            (26, 'Król', 'Szczepan Twardoch', 2016, 'Książka'),
            (27, 'Sin City: Miasto grzechu', 'Frank Miller', 1991, 'Komiks'),
            (28, 'Empuzjon', 'Olga Tokarczuk', 2022, 'Książka'),
            (29, 'Sens', 'Wydawnictwo Zwierciadło', 2023, 'Czasopismo'),
            (30, 'Prawiek i inne czasy', 'Olga Tokarczuk', 1996, 'Książka'),
            (31, 'Księgi Jakubowe', 'Olga Tokarczuk', 2014, 'Książka'),
            (32, 'Kaznodzieja', 'Garth Ennis, Steve Dillon', 1995, 'Komiks'),
            (33, 'Persepolis', 'Marjane Satrapi', 2000, 'Komiks'),
            (34, 'Charaktery', 'Forum Media Polska', 2023, 'Czasopismo'),
            (35, 'Bieguni', 'Olga Tokarczuk', 2007, 'Książka'),
            (36, 'Stary człowiek i morze', 'Ernest Hemingway', 1952, 'Książka'),
            (37, 'Kod Da Vinci', 'Dan Brown', 2003, 'Książka'),
            (38, 'Znak', 'Społeczny Instytut Wydawniczy Znak', 2023, 'Czasopismo'),
            (39, 'Mężczyźni, którzy nienawidzą kobiet', 'Stieg Larsson', 2005, 'Książka'),
            (40, 'Grona gniewu', 'John Steinbeck', 1939, 'Książka'),
            (41, 'Imię róży', 'Umberto Eco', 1980, 'Książka'),
            (42, 'Przeminęło z wiatrem', 'Margaret Mitchell', 1936, 'Książka'),
            (43, 'Pismo. Magazyn opinii', 'Fundacja Pismo', 2023, 'Czasopismo'),
            (44, 'Przekrój', 'Fundacja Przekrój', 2023, 'Czasopismo'),
            (45, 'Maus', 'Art Spiegelman', 1986, 'Komiks'),
            (46, 'Tygodnik Powszechny', 'Tygodnik Powszechny Sp. z o.o.', 2023, 'Czasopismo'),
            (47, 'Sieci', 'Fratria', 2023, 'Czasopismo'),
            (48, 'Do Rzeczy', 'Orle Pióro', 2023, 'Czasopismo'),
            (49, 'Wprost', 'AWR Wprost', 2023, 'Czasopismo'),
            (50, 'Newsweek Polska', 'Ringier Axel Springer Polska', 2023, 'Czasopismo'),
            (51, 'Polityka', 'Polityka Sp. z o.o.', 2023, 'Czasopismo'),
            (52, 'Wichrowe Wzgórza', 'Emily Brontë', 1847, 'Książka'),
            (53, 'Duma i uprzedzenie', 'Jane Austen', 1813, 'Książka'),
            (54, 'Bracia Karamazow', 'Fiodor Dostojewski', 1880, 'Książka'),
            (55, 'Nowy wspaniały świat', 'Aldous Huxley', 1932, 'Książka'),
            (56, 'Wielki Gatsby', 'F. Scott Fitzgerald', 1925, 'Książka'),
            (57, 'National Geographic Polska', 'Burda Media Polska', 2023, 'Czasopismo'),
            (58, 'Zabić drozda', 'Harper Lee', 1960, 'Książka'),
            (59, 'Lolita', 'Vladimir Nabokov', 1955, 'Książka'),
            (60, 'Buszujący w zbożu', 'J.D. Salinger', 1951, 'Książka'),
            (61, 'Pachnidło', 'Patrick Süskind', 1985, 'Książka'),
            (62, 'Alchemik', 'Paulo Coelho', 1988, 'Książka'),
            (63, 'Focus', 'Burda Media Polska', 2022, 'Czasopismo'),
            (64, 'Igrzyska śmierci', 'Suzanne Collins', 2008, 'Książka'),
            (65, 'Opowieści z Narnii: Lew, Czarownica i stara szafa', 'C.S. Lewis', 1950, 'Książka'),
            (66, 'Gra o tron', 'George R.R. Martin', 1996, 'Książka'),
            (67, 'Złodziejka książek', 'Markus Zusak', 2005, 'Książka'),
            (68, 'Sandman: Preludia i nokturny', 'Neil Gaiman', 1989, 'Komiks'),
            (69, 'Świat Nauki', 'Prószyński Media', 2023, 'Czasopismo'),
            (70, 'Sto lat samotności', 'Gabriel García Márquez', 1967, 'Książka'),
            (71, 'V jak vendetta', 'Alan Moore, David Lloyd', 1982, 'Komiks'),
            (72, 'Diuna', 'Frank Herbert', 1965, 'Książka'),
            (73, 'Cień wiatru', 'Carlos Ruiz Zafón', 2001, 'Książka'),
            (74, 'Strażnicy', 'Alan Moore, Dave Gibbons', 1986, 'Komiks'),
            (75, 'Batman: Zabójczy żart', 'Alan Moore, Brian Bolland', 1988, 'Komiks'),
            (76, 'Harry Potter i Kamień Filozoficzny', 'J.K. Rowling', 1997, 'Książka'),
            (77, 'Hobbit, czyli tam i z powrotem', 'J.R.R. Tolkien', 1937, 'Książka'),
            (78, 'Wiedza i Życie', 'Prószyński Media', 2023, 'Czasopismo'),
            (79, 'Smerfy: Czarne Smerfy', 'Peyo', 1963, 'Komiks'),
            (80, 'Władca Pierścieni: Drużyna Pierścienia', 'J.R.R. Tolkien', 1954, 'Książka'),
            (81, 'Kaczor Donald', 'Egmont Polska', 2023, 'Czasopismo'),
            (82, 'Mały Książę', 'Antoine de Saint-Exupéry', 1943, 'Książka'),
            (83, 'Folwark zwierzęcy', 'George Orwell', 1945, 'Książka'),
            (84, 'Rok 1984', 'George Orwell', 1949, 'Książka'),
            (85, 'Mistrz i Małgorzata', 'Michaił Bułhakow', 1967, 'Książka'),
            (86, 'Zbrodnia i kara', 'Fiodor Dostojewski', 1866, 'Książka'),
            (87, 'Tintin: Cygaro faraona', 'Hergé', 1934, 'Komiks'),
            (88, 'Chłopi', 'Władysław Reymont', 1904, 'Książka'),
            (89, 'Wesele', 'Stanisław Wyspiański', 1901, 'Książka'),
            (90, 'Dziady, cz. III', 'Adam Mickiewicz', 1832, 'Książka'),
            (91, 'Asteriks z Galij', 'René Goscinny, Albert Uderzo', 1961, 'Komiks'),
            (92, 'Thorgal: Zdradzona czarodziejka', 'Grzegorz Rosiński, Jean Van Hamme', 1980, 'Komiks'),
            (93, 'Star Wars: Darth Vader', 'Charles Soule', 2021, 'Komiks'),
            (94, 'Ferdydurke', 'Witold Gombrowicz', 1937, 'Książka'),
            (95, 'Quo Vadis', 'Henryk Sienkiewicz', 1896, 'Książka'),
            (96, 'Lalka', 'Bolesław Prus', 1890, 'Książka'),
            (97, 'Pan Tadeusz', 'Adam Mickiewicz', 1834, 'Książka'),
            (98, 'Kajko i Kokosz: Szkoła latania', 'Janusz Christa', 1975, 'Komiks'),
            (99, 'CD-Action', 'Wydawnictwo Bauer', 2023, 'Czasopismo'),
            (100, 'Solaris', 'Stanisław Lem', 1961, 'Książka'),
            (101, 'Wiedźmin: Ostatnie życzenie', 'Andrzej Sapkowski', 1993, 'Książka'),
            (102, 'Pan Samochodzik i templariusze', 'Zbigniew Nienacki', '1966', 'Książka');
        """
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
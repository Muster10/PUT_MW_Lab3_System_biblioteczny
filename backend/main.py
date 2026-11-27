import os
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="Biblioteka", root_path="/api")
Instrumentator().instrument(app).expose(app)
DATABASE_URL = os.getenv("DATABASE_URL")

def polacz_z_db():
    return psycopg2.connect(DATABASE_URL)

class NowaKsiazka(BaseModel):
    tytul: str
    autor: str
    rok: int
    rodzaj: str
    kolor_okladki: str = "#8b131b"

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

def zapisz_historie(cursor, ksiazka_id, akcja: str, szczegoly: str, wykonawca: str = "admin"):
    cursor.execute("""
        INSERT INTO historia_zmian (ksiazka_id, akcja, wykonawca, szczegoly)
        VALUES (%s, %s, %s, %s);
        """,
        (ksiazka_id, akcja, wykonawca, szczegoly),
    )

@app.on_event("startup")
def utworz_tabele():
    conn = polacz_z_db()
    cursor = conn.cursor()

    cursor.execute("SELECT pg_advisory_lock(123456);")      #zapobiega sytuacji, gdy 3 kontenery backendu próbują w ten samej milisekundzie tworzyć tabele i wywala to błędy
    try:
        #tabela książek

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ksiazki (
                id SERIAL PRIMARY KEY,
                tytul VARCHAR(255) NOT NULL,
                autor VARCHAR(255) NOT NULL,
                rok INTEGER NOT NULL,
                rodzaj VARCHAR(255) NOT NULL,
                kolor_okladki VARCHAR(7) DEFAULT '#8b131b'
            );
        """)

        #dodawanie na starcie książki początkowej

        cursor.execute("SELECT COUNT(*) FROM ksiazki;")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                """
                INSERT INTO ksiazki (id, tytul, autor, rok, rodzaj, kolor_okladki) VALUES 
                (1, 'Biblia', 'Jan Gutenberg', 1452, 'Książka', '#8b131b'),
                (2, 'Neuromancer', 'William Gibson', 1984, 'Książka', '#bf19b2'),
                (3, 'The Walking Dead', 'Robert Kirkman, Tony Moore', 2003, 'Komiks', '#96aef0'),
                (4, 'Człowiek z Wysokiego Zamku', 'Philip K. Dick', 1962, 'Książka', '#fc6f74'),
                (5, 'Pixel', 'Idea Ahead', 2023, 'Czasopismo', '#1b0e55'),
                (6, 'Ekrany', 'Wydawnictwo Ekrany', 2023, 'Czasopismo', '#80e9f4'),
                (7, 'Czy androidy śnią o elektrycznych owcach?', 'Philip K. Dick', 1968, 'Książka', '#3c664c'),
                (8, 'Ubik', 'Philip K. Dick', 1969, 'Książka', '#82f3d7'),
                (9, 'Trudno być bogiem', 'Arkadij i Borys Strugaccy', 1964, 'Książka', '#f71421'),
                (10, 'Punisher: Witaj powrotem, Frank', 'Garth Ennis, Steve Dillon', 2000, 'Komiks', '#2eefde'),
                (11, 'Piknik na skraju drogi', 'Arkadij i Borys Strugaccy', 1972, 'Książka', '#a1879f'),
                (12, 'Daredevil: Odrodzony', 'Frank Miller, David Mazzucchelli', 1986, 'Komiks', '#bc8524'),
                (13, 'Kino', 'Fundacja Kino', 2023, 'Czasopismo', '#ff2ac8'),
                (14, 'Modlitwa o Owena', 'John Irving', 1989, 'Książka', '#38940c'),
                (15, 'Sens', 'Wydawnictwo Zwierciadło', 2023, 'Czasopismo', '#fc4ffd'),
                (16, 'Regulamin tłoczni win', 'John Irving', 1985, 'Książka', '#1307fc'),
                (17, 'Świat według Garpa', 'John Irving', 1978, 'Książka', '#790362'),
                (18, 'Lód', 'Jacek Dukaj', 2007, 'Książka', '#d6c3ea'),
                (19, 'Inne pieśni', 'Jacek Dukaj', 2003, 'Książka', '#29d19f'),
                (20, 'Perfekcyjna niedoskonałość', 'Jacek Dukaj', 2004, 'Książka', '#e33671'),
                (21, 'X-Men: Mroczna Phoenix', 'Chris Claremont, John Byrne', 1980, 'Komiks', '#9335ac'),
                (22, 'Czarne oceany', 'Jacek Dukaj', 2001, 'Książka', '#c908b0'),
                (23, 'Ślepnąc od świateł', 'Jakub Żulczyk', 2014, 'Książka', '#c0a1fd'),
                (24, 'Spider-Man: Ostatnie łowy Kravena', 'J.M. DeMatteis, Mike Zeck', 1987, 'Komiks', '#8f4071'),
                (25, 'Charaktery', 'Forum Media Polska', 2023, 'Czasopismo', '#71dd65'),
                (26, 'Morfina', 'Szczepan Twardoch', 2012, 'Książka', '#b612c7'),
                (27, 'Król', 'Szczepan Twardoch', 2016, 'Książka', '#a506fd'),
                (28, 'Empuzjon', 'Olga Tokarczuk', 2022, 'Książka', '#199f5e'),
                (29, 'Prawiek i inne czasy', 'Olga Tokarczuk', 1996, 'Książka', '#0d05ef'),
                (30, 'Księgi Jakubowe', 'Olga Tokarczuk', 2014, 'Książka', '#f80f6f'),
                (31, 'Bieguni', 'Olga Tokarczuk', 2007, 'Książka', '#f59528'),
                (32, 'Znak', 'Społeczny Instytut Wydawniczy Znak', 2023, 'Czasopismo', '#5e3574'),
                (33, 'Stary człowiek i morze', 'Ernest Hemingway', 1952, 'Książka', '#83cfcd'),
                (34, 'Kod Da Vinci', 'Dan Brown', 2003, 'Książka', '#f514e1'),
                (35, 'Pismo. Magazyn opinii', 'Fundacja Pismo', 2023, 'Czasopismo', '#a14b10'),
                (36, 'Mężczyźni, którzy nienawidzą kobiet', 'Stieg Larsson', 2005, 'Książka', '#a9115d'),
                (37, 'Grona gniewu', 'John Steinbeck', 1939, 'Książka', '#dd95c7'),
                (38, 'Przekrój', 'Fundacja Przekrój', 2023, 'Czasopismo', '#7ec1e3'),
                (39, 'Imię róży', 'Umberto Eco', 1980, 'Książka', '#1232a8'),
                (40, 'Przeminęło z wiatrem', 'Margaret Mitchell', 1936, 'Książka', '#8c49c4'),
                (41, 'Hellboy: Nasienie zniszczenia', 'Mike Mignola', 1994, 'Komiks', '#167367'),
                (42, 'Wichrowe Wzgórza', 'Emily Brontë', 1847, 'Książka', '#c7115a'),
                (43, 'Duma i uprzedzenie', 'Jane Austen', 1813, 'Książka', '#73bfb1'),
                (44, 'Bracia Karamazow', 'Fiodor Dostojewski', 1880, 'Książka', '#cdac99'),
                (45, 'Sin City: Miasto grzechu', 'Frank Miller', 1991, 'Komiks', '#ae6f0f'),
                (46, 'Nowy wspaniały świat', 'Aldous Huxley', 1932, 'Książka', '#4fc86f'),
                (47, 'Tygodnik Powszechny', 'Tygodnik Powszechny Sp. z o.o.', 2023, 'Czasopismo', '#73417a'),
                (48, 'Sieci', 'Fratria', 2023, 'Czasopismo', '#79cf9d'),
                (49, 'Wielki Gatsby', 'F. Scott Fitzgerald', 1925, 'Książka', '#6f3a98'),
                (50, 'Do Rzeczy', 'Orle Pióro', 2023, 'Czasopismo', '#fafc37'),
                (51, 'Kaznodzieja', 'Garth Ennis, Steve Dillon', 1995, 'Komiks', '#c6b176'),
                (52, 'Wprost', 'AWR Wprost', 2023, 'Czasopismo', '#893953'),
                (53, 'Zabić drozda', 'Harper Lee', 1960, 'Książka', '#90169f'),
                (54, 'Persepolis', 'Marjane Satrapi', 2000, 'Komiks', '#404ce5'),
                (55, 'Lolita', 'Vladimir Nabokov', 1955, 'Książka', '#ae1fc7'),
                (56, 'Buszujący w zbożu', 'J.D. Salinger', 1951, 'Książka', '#4e47f4'),
                (57, 'Pachnidło', 'Patrick Süskind', 1985, 'Książka', '#f22615'),
                (58, 'Newsweek Polska', 'Ringier Axel Springer Polska', 2023, 'Czasopismo', '#8d6a48'),
                (59, 'Maus', 'Art Spiegelman', 1986, 'Komiks', '#0b3afa'),
                (60, 'Sandman: Preludia i nokturny', 'Neil Gaiman', 1989, 'Komiks', '#adf2f4'),
                (61, 'V jak vendetta', 'Alan Moore, David Lloyd', 1982, 'Komiks', '#5e138c'),
                (62, 'Alchemik', 'Paulo Coelho', 1988, 'Książka', '#a52399'),
                (63, 'Strażnicy', 'Alan Moore, Dave Gibbons', 1986, 'Komiks', '#17d0dc'),
                (64, 'Igrzyska śmierci', 'Suzanne Collins', 2008, 'Książka', '#7d20d3'),
                (65, 'Opowieści z Narnii: Lew, Czarownica i stara szafa', 'C.S. Lewis', 1950, 'Książka', '#e24e8b'),
                (66, 'Gra o tron', 'George R.R. Martin', 1996, 'Książka', '#42092f'),
                (67, 'Batman: Zabójczy żart', 'Alan Moore, Brian Bolland', 1988, 'Komiks', '#bc2c56'),
                (68, 'Złodziejka książek', 'Markus Zusak', 2005, 'Książka', '#e5243e'),
                (69, 'Sto lat samotności', 'Gabriel García Márquez', 1967, 'Książka', '#1d9a4c'),
                (70, 'Polityka', 'Polityka Sp. z o.o.', 2023, 'Czasopismo', '#797c2a'),
                (71, 'Smerfy: Czarne Smerfy', 'Peyo', 1963, 'Komiks', '#b246a1'),
                (72, 'Diuna', 'Frank Herbert', 1965, 'Książka', '#d72361'),
                (73, 'Cień wiatru', 'Carlos Ruiz Zafón', 2001, 'Książka', '#2786cd'),
                (74, 'Harry Potter i Kamień Filozoficzny', 'J.K. Rowling', 1997, 'Książka', '#daf3f1'),
                (75, 'Hobbit, czyli tam i z powrotem', 'J.R.R. Tolkien', 1937, 'Książka', '#8bc2b3'),
                (76, 'Władca Pierścieni: Drużyna Pierścienia', 'J.R.R. Tolkien', 1954, 'Książka', '#e6d3b1'),
                (77, 'National Geographic Polska', 'Burda Media Polska', 2023, 'Czasopismo', '#d47801'),
                (78, 'Mały Książę', 'Antoine de Saint-Exupéry', 1943, 'Książka', '#2200a0'),
                (79, 'Focus', 'Burda Media Polska', 2022, 'Czasopismo', '#7b6bb0'),
                (80, 'Folwark zwierzęcy', 'George Orwell', 1945, 'Książka', '#3b78db'),
                (81, 'Rok 1984', 'George Orwell', 1949, 'Książka', '#eb1789'),
                (82, 'Świat Nauki', 'Prószyński Media', 2023, 'Czasopismo', '#2b1d18'),
                (83, 'Tintin: Cygaro faraona', 'Hergé', 1934, 'Komiks', '#af35f1'),
                (84, 'Asteriks z Galij', 'René Goscinny, Albert Uderzo', 1961, 'Komiks', '#b40e64'),
                (85, 'Mistrz i Małgorzata', 'Michaił Bułhakow', 1967, 'Książka', '#b18652'),
                (86, 'Zbrodnia i kara', 'Fiodor Dostojewski', 1866, 'Książka', '#296a3a'),
                (87, 'Wiedza i Życie', 'Prószyński Media', 2023, 'Czasopismo', '#68b3c0'),
                (88, 'Chłopi', 'Władysław Reymont', 1904, 'Książka', '#1ebac5'),
                (89, 'Kaczor Donald', 'Egmont Polska', 2023, 'Czasopismo', '#20ef8d'),
                (90, 'Thorgal: Zdradzona czarodziejka', 'Grzegorz Rosiński, Jean Van Hamme', 1980, 'Komiks', '#4abd53'),
                (91, 'Wesele', 'Stanisław Wyspiański', 1901, 'Książka', '#436c32'),
                (92, 'Silmarillion', 'J.R.R Tolkien', '1977', 'Książka', '#72a83d'),
                (93, 'Dziady, cz. III', 'Adam Mickiewicz', 1832, 'Książka', '#2dc9f1'),
                (94, 'Ferdydurke', 'Witold Gombrowicz', 1937, 'Książka', '#1a092e'),
                (95, 'Quo Vadis', 'Henryk Sienkiewicz', 1896, 'Książka', '#8c6dc5'),
                (96, 'Kajko i Kokosz: Szkoła latania', 'Janusz Christa', 1975, 'Komiks', '#84f2fd'),
                (97, 'CD-Action', 'Wydawnictwo Bauer', 2023, 'Czasopismo', '#67ea7d'),
                (98, 'Lalka', 'Bolesław Prus', 1890, 'Książka', '#b933b8'),
                (99, 'Pan Tadeusz', 'Adam Mickiewicz', 1834, 'Książka', '#9f5539'),
                (100, 'Solaris', 'Stanisław Lem', 1961, 'Książka', '#fe14eb'),
                (101, 'Wiedźmin: Ostatnie życzenie', 'Andrzej Sapkowski', 1993, 'Książka', '#7372b2'),
                (102, 'Pan Samochodzik i templariusze', 'Zbigniew Nienacki', 1966, 'Książka', '#8b131b');
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

        #tabela historii zmian

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historia_zmian (
            id SERIAL PRIMARY KEY,
            ksiazka_id INTEGER REFERENCES ksiazki(id) ON DELETE SET NULL,
            akcja VARCHAR(20) NOT NULL,
            wykonawca VARCHAR(100) NOT NULL DEFAULT 'admin',
            szczegoly TEXT,
            data_zmiany TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        conn.commit()

    finally:
        cursor.execute("SELECT pg_advisory_unlock(123456);")
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
        "INSERT INTO ksiazki (tytul, autor, rok, rodzaj, kolor_okladki) VALUES (%s, %s, %s, %s, %s) RETURNING id;", 
        (ksiazka.tytul, ksiazka.autor, ksiazka.rok, ksiazka.rodzaj, ksiazka.kolor_okladki)
    ) 
    nowe_id = cursor.fetchone()[0]

    zapisz_historie(
        cursor,
        ksiazka_id=nowe_id,
        akcja="CREATE",
        szczegoly=f"Dodano pozycję: '{ksiazka.tytul}' ({ksiazka.autor}, {ksiazka.rok})",
    )

    conn.commit()
    cursor.close()
    conn.close()
    return {"id": nowe_id, "tytul": ksiazka.tytul, "autor": ksiazka.autor, "rok": ksiazka.rok, "rodzaj": ksiazka.rodzaj, "kolor_okladki": ksiazka.kolor_okladki}

@app.delete("/ksiazki/{ksiazka_id}")
def usun_ksiazke(ksiazka_id: int):
    conn = polacz_z_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("DELETE FROM ksiazki WHERE id = %s RETURNING id, tytul, autor;", (ksiazka_id,),)
    usunieta = cursor.fetchone()

    if not usunieta:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Książka o podanym ID nie istnieje")

    zapisz_historie(
        cursor,
        ksiazka_id=usunieta["id"],
        akcja="DELETE",
        szczegoly=f"Usunięto pozycję: '{usunieta['tytul']}' ({usunieta['autor']})",
    )

    conn.commit()
    cursor.close()
    conn.close()

    return {"status": "sukces", "usuniete_id": usunieta[0]}

@app.put("/ksiazki/{ksiazka_id}")
def edytuj_ksiazke(ksiazka_id: int, ksiazka: NowaKsiazka):
    conn = polacz_z_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE ksiazki SET tytul = %s, autor = %s, rok = %s, rodzaj = %s, kolor_okladki = %s WHERE id = %s RETURNING id;",
        (ksiazka.tytul, ksiazka.autor, ksiazka.rok, ksiazka.rodzaj, ksiazka.kolor_okladki, ksiazka_id))
    zaktualizowana = cursor.fetchone()

    if not zaktualizowana: #nie można zaktualizować danych o książce, która nie jest dodana do bazy danych
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Książka o podanym ID nie istnieje")

    zapisz_historie(
        cursor,
        ksiazka_id=ksiazka_id,
        akcja="UPDATE",
        szczegoly=f"Zaktualizowano pozycję: '{ksiazka.tytul}' ({ksiazka.autor}, {ksiazka.rok})",
    )

    conn.commit()
    cursor.close()
    conn.close()
    return {"id": ksiazka_id, "tytul": ksiazka.tytul, "autor": ksiazka.autor, "rok": ksiazka.rok, "rodzaj": ksiazka.rodzaj, "kolor_okladki": ksiazka.kolor_okladki}

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
            """
            SELECT 1 FROM wypozyczenia
            WHERE ksiazka_id = %s AND  uzytkownik_id = %s
            """,
            (wypoz.ksiazka_id, wypoz.uzytkownik_id)
        )

        if cursor.fetchone() is not None:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=400, detail="Masz już tę pozycję na liście wypożyczeń.")

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

@app.get("/ksiazki/{ksiazka_id}/history")
def pobierz_historie_ksiazek(ksiazka_id: int):
    conn = polacz_z_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("SELECT id FROM ksiazki WHERE id = %s;", (ksiazka_id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Książka o podanym ID nie istnieje")

    cursor.execute(
        """
        SELECT id, ksiazka_id, akcja, wykonawca, szczegoly, data_zmiany
        FROM historia_zmian
        WHERE ksiazka_id = %s
        ORDER BY data_zmiany DESC, id DESC;
        """,
        (ksiazka_id,),
    )

    historia = cursor.fetchall()
    cursor.close()
    conn.close()
    return historia

# docker-compose up --build -d
# docker-compose down -v
# docker compose up --build -d --scale backend=3

# Poniższe zrobić każdy punkt jako osobny commit (np. tworzysz tabelę historia to usuwasz tę linijkę stąd, commitujesz wszystko i push)
# TODO: Zapis historii (w każdym endpoincie modyfikującym POST/PUT/DELTE dodać INSERT'a do tabeli historii) + endpoint GET /history
# TODO: Testy automatyczne (ich mnóstwo będzie)
# TODO: Uzupełnić README o powyższe

# TODO: Cache lub prosta kolejka
# TODO: ALerty/detekcja anomalii
# TODO: Wprowadzenie systemu zwracania wypożyczeń, naliczania opłat itp
# TODO: Usprawnienie systemu rezerwacji
# TODO: CI/CD połączyć z tymi testami
# TODO: Potencjalnie zrobić bezpieczniejsze logowanie - hashowanie haseł itp

# TODO: Rozważyć wprowadzenie prometheus client w pythonie
# TODO: Rozważyć budowanie obrazu frontendu z konkretnej wersji alpine (zmiana w /frontend/Dockerfile)
# TODO: Rozważyć ukrycie przycisku pokazywania katalogu (automatyczne pokazywanie od razu po wejściu na stronę)
# TODO: Rozważyć automatyczne odświeżanie panelu konta (po usunięciu wypożyczonej książki trzeba f5 zrobić teraz)
# TODO: Rozważyć dodanie "wygaszenia" przycisków wypożyczenia i rejestracji kiedy dana książka jest przez nas aktualnie wypożyzcona/zarezerwowana (aktualnie można kliknąć i przychodzi komunikat localhost says)
# TODO: Dodać możliwość wyświetlenia jako administrator całej tabeli historii zmian (imo osobna stronka z możliwością filtrowania po id książki, rodzaju wpisu (update, post itp), autorze, dacie)
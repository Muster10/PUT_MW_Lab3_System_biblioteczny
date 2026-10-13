import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def wczytaj_dane_katalogu():
    with open("/app/database/db_k.json", "r", encoding="utf-8") as plik:
        dane = json.load(plik)
    return dane

def wczytaj_dane_uzytkownikow():
    with open("/app/database/db_u.json", "r", encoding="utf-8") as plik:
        dane = json.load(plik)
    return dane

'''
def rejestracja(dane_uzytkownikow):
    print("\nREJESTRACJA\n")
    imie = input("Wprowadź imię: ")
    nazwisko = input("Wprowadź nazwisko: ")
    wygenerowany_numer_karty = str(len(dane_uzytkownikow) + 1).zfill(6)
    while True:
        haslo = input("Wprowadź hasło: ")
        haslo2 = input("Wprowadź hasło ponownie: ")
        if haslo != haslo2:
            print("Hasła się nie zgadzają!")
        else:
            print("Rejestracja się powiodła")
            user = {
                "login": wygenerowany_numer_karty,
                "password": haslo,
                "role": "user" #szytwno user, bo nie chce aby uzytkownik rejestrował się jako administrator
            }
            dodanie_uzytkownika(user)
            return True
'''

def dodanie_uzytkownika(uzytkownik):
    with open("/app/database/db_u.json", "r", encoding="utf-8") as plik:
        dane = json.load(plik)
    dane.append(uzytkownik)
    with open("/app/database/db_u.json", "w", encoding="utf-8") as plik:
        json.dump(dane, plik, indent=4, ensure_ascii=False)

'''
def logowanie(dane_uzytkownikow):
    print("\nLOGOWANIE\n")
    login = input("Wprowadź numer karty czytelniczej: ")
    haslo = input("Wprowadź hasło: ")
    for uzytkownik in dane_uzytkownikow:
        if uzytkownik.get("login") == login and uzytkownik.get("password") == haslo:
            print("Zalogowano pomyślnie!")
            return True
    
    print("Nieprawidłowy login lub hasło.") #po zakonczeniu petli - przeszukaniu wszyskich uzytkownikow z bazy
    wybor = int(input("Wybierz opcję:\n1. Spróbuj ponownie\n2. Zarejestruj się\n3. Wyjdź\n"))
    match wybor:
        case 1:
            return logowanie()
        case 2:
            rejestracja()
        case 3:
            exit()
'''

@app.get("/api/ksiazki")
def pobierz_ksiazki(): #frontend wysyła zapytanie GET na endpoint /api/ksiazki, a backend odpowiada danymi katalogu w formacie JSON
    dane_katalogu = wczytaj_dane_katalogu()
    return dane_katalogu
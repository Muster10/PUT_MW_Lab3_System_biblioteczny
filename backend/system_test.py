import json
from pathlib import Path

BASEDIR = Path(__file__).resolve().parent.parent #przejscie do glownego folderu
sciezka_do_db = BASEDIR / "database"


def wczytaj_dane_katalogu():
    with open(sciezka_do_db / "db_k.json", "r", encoding="utf-8") as plik:
        dane = json.load(plik)
    return dane

def wczytaj_dane_uzytkownikow():
    with open(sciezka_do_db / "db_u.json", "r", encoding="utf-8") as plik:
        dane = json.load(plik)
    return dane

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
    

def dodanie_uzytkownika(uzytkownik):
    with open(sciezka_do_db / "db_u.json", "r", encoding="utf-8") as plik:
        dane = json.load(plik)
    dane.append(uzytkownik)
    with open(sciezka_do_db / "db_u.json", "w", encoding="utf-8") as plik:
        json.dump(dane, plik, indent=4, ensure_ascii=False)


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


def menu_glowne():
    katalog = wczytaj_dane_katalogu()
    uzytkownicy = wczytaj_dane_uzytkownikow()
    status = False #niezalogowany
    while status != True:
        print("Witaj w bibliotece!")
        print("1. Zaloguj się")
        print("2. Zarejestruj się")
        print("3. Wyjdź")
        wybor = input("\nWybierz opcję: ")
        if wybor == "1":
            status = logowanie(uzytkownicy)
        elif wybor == "2":
            status = rejestracja(uzytkownicy)
        elif wybor == "3":
            exit()
        else:
            print("Nieprawidłowy wybór. Spróbuj ponownie.")

if __name__ == "__main__":
    menu_glowne()
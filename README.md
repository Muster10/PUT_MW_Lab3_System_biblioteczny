# System biblioteczny (wypożyczenie, rezerwacja)

Wykonujący: Bartosz Hauff, Adam Musiał

Ostatnia aktualizacja: 12.11.2026

## Frontend

- Okienko zalogowania/rejestracji do systemu
- Katalog pozycji w systemie (lista z danymi o pozycjach do wypożyczenia)
- Filtrowane pozycji po roku wydania, rodzaju pozycji (książka, czasopismo, komiks itp)
- Po wybraniu interesującej nas pozycji otwiera się okienko z nią, widocznym zdjęciem i możliwością wypożyczenia/zarezerwowania
- Użytkownicy mają dostęp do swojej strony konta, gdzie widoczny jest ich profil, dane o wypożyczonych książkach, zaległości do zapłaty itp.
- Panel bibliotekarza (admina), który może dodawać nowe pozycje, edytować informacje o istniejących i usuwać

## Backend

- Kod systemu z zaimplementowanym FastAPI do komunikacji ze stroną i łączący się z bazami danych PostgreSQL

### Endpointy API

| Metoda | Ścieżka | Opis | Kody statusu |
| :--- | :--- | :--- | :--- |
| `GET` | `/ksiazki` | Pobiera listę wszystkich książek | `200 OK` |
| `GET` | `/ksiazki/{ksiazka_id}` | Pobiera pojedynczą książkę po ID | `200 OK`, `404 Not Found` |
| `POST` | `/ksiazki` | Dodaje nową książkę do bazy | `201 Created`, `400 Bad Request` |
| `PUT` | `/ksiazki/{ksiazka_id}` | Edytuje pojedynczą książkę po ID | `200 OK`, `404 Not Found` |
| `DELETE` | `/ksiazki/{ksiazka_id}` | Usuwa książkę o podanym ID | `200 OK`, `404 Not Found` |
| `GET` | `/uzytkownicy` | Pobiera listę użytkowników | `200 OK` |
| `POST` | `/uzytkownicy` | Dodaje nowe konto do bazy | `201 Created`, `400 Bad Request` |
| `POST` | `/logowanie` | Weryfikuje dane logowania i zwraca profil | `200 OK`, `401 Unauthorized` |
| `GET` | `/wypozyczenia/{uzytkownik_id}` | Zwraca listę pozycji użytkownika | `200 OK`, `404 Not Found` |
| `POST` | `/wypozyczenia` | Tworzy nowe wypożyczenie/rezerwacje | `201 Created`, `400 Bad Request` |
| `GET` | `/health` | Sprawdza fizyczne połączenie z bazą | `200 OK`, `503 Service Unavailable` |


---

####  `GET /ksiazki`
Zwraca listę wszystkich książek:
```json
[
  {
    "id": 1,
    "tytul": "Wiedźmin",
    "autor": "Andrzej Sapkowski",
    "rok": 1990,
    "rodzaj": "Książka"
  }
]
```

####  `GET /ksiazki/{ksiazka_id}`
Zwraca pojedynczą książkę (lub kod `404`, gdy zasób nie istnieje):
```json
{
  "id": 1,
  "tytul": "Wiedźmin",
  "autor": "Andrzej Sapkowski",
  "rok": 1990,
  "rodzaj": "Książka"
}
```

####  `POST /ksiazki`
Dodaje nową książkę (zwraca kod `201` lub `400`, gdy pola są puste).

**Request (wysyłane dane):**
```json
{
  "tytul": "Solaris",
  "autor": "Stanisław Lem",
  "rok": 1961,
  "rodzaj": "Książka"
}
```

**Response (odpowiedź serwera):**
```json
{
  "id": 2,
  "tytul": "Solaris",
  "autor": "Stanisław Lem",
  "rok": 1961,
  "rodzaj": "Książka"
}
```

#### `PUT /ksiazki/{ksiazka{id}`
Aktualizuje dane książki o podanym ID:
```json
{
  "id": 1,
  "tytul": "Wiedźmin - Poprawiony",
  "autor": "Andrzej Sapkowski",
  "rok": 1990,
  "rodzaj": "Książka"
}
```

####  `DELETE /ksiazki/{ksiazka_id}`
Usuwa książkę o podanym ID (lub zwraca kod `404`):
```json
{
  "status": "sukces",
  "usuniete_id": 1
}
```

####  `GET /uzytkownicy`
Zwraca listę użytkowników:
```json
[
  {
    "id": 1,
    "login": "admin",
    "rola": "admin"
  }
]
```

####  `POST /uzytkownicy`
Zwraca listę użytkowników:
```json
[
  {
    "id": 2,
    "login": "jan123",
    "rola": "user"
  }
]
```

#### `POST /logowanie`
Sprawdza poprawność loginu i hasła.

**Request (wysyłane dane):**
```json
{
  "login": "jan123",
  "haslo": "tajnehaslo"
}
```

**Response (odpowiedź serwera):**
```json
{
  "id": 2,
  "login": "jan123",
  "rola": "user"
}
```

#### `GET /wypozyczenia/{uzytkownik_id}`
Pobiera dane o profilu z wykorzystaniem JOIN:
```json
{
    "tytul": "Wiedźmin",
    "typ": "wypożyczono",
    "data_wypozyczenia": "2026-11-12T15:30:00"
}
```


#### `POST /wypozyczenia`
Dodaje akcję do książki:

**Request (wysyłane dane):**
```json
{
  "ksiazka_id": 1,
  "uzytkownik_id": 2,
  "typ": "wypożyczono"
}
```

**Response (odpowiedź serwera):**
```json
{
  "id": 1,
  "ksiazka_id": 1,
  "uzytkownik_id": 2,
  "typ": "wypożyczono"
}
```


####  `GET /health`
Sprawdza kondycję serwisu:
```json
{
  "status": "ok"
}
```

## Database

- Relacyjna baza danych PostgreSQL zarządzana wewnątrz kontenera Docker.
- Automatycznie generowane tabele ksiazki oraz uzytkownicy z wbudowanym mechanizmem tworzenia konta administratora przy starcie systemu.
- Trzecia powiązana tabela wypozyczenia wykorzystująca relacje kluczy obcych (FOREIGN KEY i ON DELETE CASCADE) na połączenie książek z użytkownikami.
- Izolowana wewnętrzna sieć kontenerów Docker Compose w celu zabezpieczenia portów bazy danych przed zewnętrznym dostępem.
- Zapytania inicjalizujące strukturę książek z synchronizacją autoinkrementacji SERIAL w celu uniknięcia błędów nadpisywania ID.

# System biblioteczny (wypożyczenie, rezerwacja)

Wykonujący: Bartosz Hauff, Adam Musiał

Ostatnia aktualizacja: 11.11.2026

## Frontend

- Okienko zalogowania/rejestracji do systemu
- Katalog pozycji w systemie (lista z danymi o pozycjach do wypożyczenia)
- Filtrowane pozycji po roku wydania, rodzaju pozycji (książka, czasopismo, komiks itp)
- Po wybraniu interesującej nas pozycji otwiera się okienko z nią, widocznym zdjęciem i możliwością wypożyczenia/zarezerwowania
- Użytkownicy mają dostęp do swojej strony konta, gdzie widoczny jest ich profil, dane o wypożyczonych książkach, zaległości do zapłaty itp.
- Panel bibliotekarza (admina), który może dodawać nowe pozycje do systemu

## Backend

- Kod systemu z zaimplementowanym FastAPI do komunikacji ze stroną i łączący się z bazami danych PostgreSQL

### Endpointy API

| Metoda | Ścieżka | Opis | Kody statusu |
| :--- | :--- | :--- | :--- |
| `GET` | `/ksiazki` | Pobiera listę wszystkich książek | `200 OK` |
| `GET` | `/ksiazki/{ksiazka_id}` | Pobiera pojedynczą książkę po ID | `200 OK`, `404 Not Found` |
| `POST` | `/ksiazki` | Dodaje nową książkę do bazy | `201 Created`, `400 Bad Request` |
| `DELETE` | `/ksiazki/{ksiazka_id}` | Usuwa książkę o podanym ID | `200 OK`, `404 Not Found` |
| `GET` | `/uzytkownicy` | Pobiera listę użytkowników | `200 OK` |
| `GET` | `/health` | Sprawdza kondycję serwisu | `200 OK` |
| `PUT` | `/ksiazki/{ksiazka_id}` | Edytuje pojedynczą książkę po ID | `200 OK`, `404 Not Found` |
| `POST` | `/uzytkownicy` | Dodaje nowe konto do bazy | `200 OK`, `400 Bad Request` |

---

####  `GET /ksiazki`
Zwraca listę wszystkich książek:
```json
[
  {
    "id": 1,
    "tytul": "Wiedźmin",
    "autor": "Andrzej Sapkowski"
  }
]
```

####  `GET /ksiazki/{ksiazka_id}`
Zwraca pojedynczą książkę (lub kod `404`, gdy zasób nie istnieje):
```json
{
  "id": 1,
  "tytul": "Wiedźmin",
  "autor": "Andrzej Sapkowski"
}
```

####  `POST /ksiazki`
Dodaje nową książkę (zwraca kod `201` lub `400`, gdy pola są puste).

**Request (wysyłane dane):**
```json
{
  "tytul": "Wiedźmin",
  "autor": "Andrzej Sapkowski"
}
```

**Response (odpowiedź serwera):**
```json
{
  "id": 1,
  "tytul": "Wiedźmin",
  "autor": "Andrzej Sapkowski"
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
    "login": "jan123",
    "rola": "user"
  }
]
```

####  `GET /health`
Sprawdza kondycję serwisu:
```json
{
  "status": "ok"
}
```

## Database

- Baza danych z pozycjami bibliotecznymi
- Baza danych z informacjami o kontach użytkowników
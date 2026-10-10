# System biblioteczny (wypożyczenie, rezerwacja)

Wykonujący: Bartosz Hauff, Adam Musiał

Ostatnia aktualizacja: 10.10.2026

## Frontend

- Okienko zalogowania/rejestracji do systemu
- Katalog pozycji w systemie (lista z danymi o pozycjach do wypożyczenia)
- Filtrowane pozycji po roku wydania, rodzaju pozycji (książka, czasopismo, komiks itp)
- Po wybraniu interesującej nas pozycji otwiera się okienko z nią, widocznym zdjęciem i możliwością wypożyczenia/zarezerwowania
- Użytkownicy mają dostęp do swojej strony konta, gdzie widoczny jest ich profil, dane o wypożyczonych książkach, zaległości do zapłaty itp.
- Panel bibliotekarza (admina), który może dodawać nowe pozycje do systemu

## Backend

- Kod systemu z zaimplementowanym FastAPI do komunikacji ze stroną i łączący się z bazami danych

## Database

- Baza danych z pozycjami bibliotecznymi
- Baza danych z informacjami o kontach użytkowników

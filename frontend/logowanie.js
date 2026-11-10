document.getElementById("formularz-logowania").addEventListener("submit", async (event) => {
    event.preventDefault();

    const wpisanyLogin = document.getElementById("login").value.trim();
    const wpisaneHaslo = document.getElementById("haslo").value.trim();
    const komunikat = document.getElementById("komunikat");

    try {
        // Pobieramy listę użytkowników z backendu
        const response = await fetch("/api/uzytkownicy");
        if (!response.ok) {
            throw new Error("Błąd pobierania danych");
        }

        const uzytkownicy = await response.json();

        // Szukamy użytkownika o podanym loginie
        const znaleziony = uzytkownicy.find(u => u.login === wpisanyLogin);

        if (!znaleziony) {
            komunikat.style.color = "red";
            komunikat.innerText = "Użytkownik o takim loginie nie istnieje.";
            return;
        }

        const zapisaneHasla = JSON.parse(localStorage.getItem("haslaUzytkownikow")) || {};

        if (znaleziony.login === "admin") {
            if (wpisaneHaslo !== "admin1") {
                komunikat.style.color = "red";
                komunikat.innerText = "Nieprawidłowe hasło!";
                return;
            }
        } 
        else {
            if (zapisaneHasla[znaleziony.login] !== wpisaneHaslo) {
                komunikat.style.color = "red";
                komunikat.innerText = "Nieprawidłowe hasło!";
                return;
            }
        }

        // Zapisujemy zalogowanego użytkownika w pamięci przeglądarki
        localStorage.setItem("zalogowanyUzytkownik", JSON.stringify(znaleziony));

        komunikat.style.color = "green";
        komunikat.innerText = "Zalogowano pomyślnie! Przekierowywanie...";

        // Po krótkiej chwili przenosimy na stronę główną
        setTimeout(() => {
            window.location.href = "index.html";
        }, 600);

    } catch (error) {
        komunikat.style.color = "red";
        komunikat.innerText = "Brak połączenia z API.";
        console.error(error);
    }
});
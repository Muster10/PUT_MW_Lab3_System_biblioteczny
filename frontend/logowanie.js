document.getElementById("formularz-logowania").addEventListener("submit", async (event) => {
    event.preventDefault();

    const wpisanyLogin = document.getElementById("login").value.trim();
    const wpisaneHaslo = document.getElementById("haslo").value.trim();
    const komunikat = document.getElementById("komunikat");

    try {
        const response = await fetch("/api/logowanie", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ login: wpisanyLogin, haslo: wpisaneHaslo })
        });
        if (!response.ok) {
            komunikat.style.color = "red";
            komunikat.innerText = "Nieprawidłowy login lub hasło!";
            return;
        }
        const znaleziony = await response.json();

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
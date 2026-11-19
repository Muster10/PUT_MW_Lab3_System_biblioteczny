const ikonaOko = `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#5c0a0a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>`;
const ikonaPrzekreslone = `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#5c0a0a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>`;

document.getElementById("pokaz-haslo").addEventListener("click", function() {
    const poleHasla = document.getElementById("haslo");
    if (poleHasla.type === "password") {
        poleHasla.type = "text";
        this.innerHTML = ikonaOko; 
    } else {
        poleHasla.type = "password";
        this.innerHTML = ikonaPrzekreslone;
    }
});

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
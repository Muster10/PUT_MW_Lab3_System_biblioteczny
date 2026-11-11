function SprawdzSesje() {
    let tekstUzytkownika = localStorage.getItem("zalogowanyUzytkownik");

    let powitanie = document.getElementById("powitanie-uzytkownika");
    let linkLogowanie = document.getElementById("link-logowanie");
    let linkRejestracja = document.getElementById("link-rejestracja");
    let btnWyloguj = document.getElementById("btn-wyloguj");
    let panelAdmina = document.getElementById("panel-admina");
    let daneProfilu = document.getElementById("dane-profilu");

    if (tekstUzytkownika !== null) {
        let uzytkownik = JSON.parse(tekstUzytkownika);

        powitanie.innerText = "Zalogowany: " + uzytkownik.login;
        linkLogowanie.style.display = "none";
        linkRejestracja.style.display  = "none";
        btnWyloguj.style.display = "inline-block";

        if (uzytkownik.rola === "admin") {
            panelAdmina.style.display = "block";
        }

        let wypozyczone = localStorage.getItem("wypozyczone_" + uzytkownik.login);

        if (wypozyczone === null) {
            wypozyczone = "Brak wypożyczonych pozycji";
        }

        daneProfilu.innerHTML = `
            <p>ID konta: <b>${uzytkownik.id}</b></p>
            <p>Login: <b>${uzytkownik.login}</b></p>
            <p>Rola: <b>${uzytkownik.rola}</b></p>
            <p>Zaległości do zapłaty: <b>0 PLN</b></p>
            <p>Twoje pozycje: <b>${wypozyczone}</b></p>
        `;
    }
}


function Wyloguj() {
    localStorage.removeItem("zalogowanyUzytkownik");
    window.location.href = "index.html";

}
async function PobierzKatalog() {
    let pojemnik = document.getElementById("katalog");
    let wybranyRodzaj = document.getElementById("filtr-rodzaj").value;
    let wpisanyRok = document.getElementById("filtr-rok").value;
    pojemnik.innerHTML = "Pobieranie danych z bazy...";

    try {
        let response = await fetch("/api/ksiazki");
        let ksiazki = await response.json();

        pojemnik.innerHTML = "";

        ksiazki.forEach(ksiazka => {
                    let rok = localStorage.getItem("rok_" + ksiazka.id);
                    let rodzaj = localStorage.getItem("rodzaj_" + ksiazka.id);

                    if (rok ===null) {
                        rok = "Brak danych";
                    }
                    if (rodzaj === null) {
                        rodzaj = "Brak danych";
                    }

                    if (wybranyRodzaj !== "wszystkie" && rodzaj !== wybranyRodzaj) {
                        return;
                    }
                    if (wpisanyRok !== "" && Number(rok) < Number(wpisanyRok)) {
                        return;
                    }
                    let kafelek = document.createElement("div");
                    kafelek.className = "ksiazka-karta";
                    
                    kafelek.innerHTML = `
                        <h3>${ksiazka.tytul}</h3>
                        <p>Autor: <b>${ksiazka.autor}</b></p>
                        <p>Rodzaj: ${rodzaj} | Rok: ${rok}</p>
                        <p>ID: ${ksiazka.id}</p>
                        <input type="button" value="Szczegóły" onclick="PokazSzczegoly(${ksiazka.id})" class="btn btn-red">
                    `;
                    
                    pojemnik.appendChild(kafelek);
                });
    }
    catch (error) {
        pojemnik.innerHTML = "Wystąpił błąd przy połączeniu z API";
        console.error(error);
    }
}

function FiltrujKatalog() {
    PobierzKatalog();
}

SprawdzSesje();
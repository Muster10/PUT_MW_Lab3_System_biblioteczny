async function SprawdzSesje() {
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

        let wypozyczone = "Brak wypożyczonych pozycji";
        let response = await fetch("/api/wypozyczenia/" + uzytkownik.id);
        if (response.ok) {
            let lista = await response.json();
            if (lista.length > 0) {
                wypozyczone = "";
                lista.forEach(wpis => {
                    wypozyczone += wpis.tytul + " (" + wpis.typ + "), ";
                });
            }
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
                    let rok = ksiazka.rok;
                    let rodzaj = ksiazka.rodzaj;

                    if (!rok) {
                        rok = "Brak danych";
                    }
                    if (!rodzaj) {
                        rodzaj = "Brak danych";
                    }

                    if (wybranyRodzaj !== "wszystkie" && rodzaj !== wybranyRodzaj) {
                        return;
                    }
                    if (wpisanyRok !== "" && (rok === "Brak danych" || Number(rok) < Number(wpisanyRok))) {
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

async function PokazSzczegoly(idKsiazki) {
    let pojemnikSzczegolow = document.getElementById("szczegoly-pozycji");
    pojemnikSzczegolow.innerHTML = "Ładowanie szczegółów...";

    try {
        let response = await fetch("/api/ksiazki/" + idKsiazki);
        let ksiazka = await response.json();

        let rok = ksiazka.rok;
        let rodzaj = ksiazka.rodzaj;

        if (!rok) {
            rok = "Brak danych";
        }
        if (!rodzaj) {
            rodzaj = "Brak danych";
        }

        let przyciskiAdmina = "";
        let tekstUzytkownika = localStorage.getItem("zalogowanyUzytkownik");
        if (tekstUzytkownika !== null) {
            let uzytkownik = JSON.parse(tekstUzytkownika);
            if (uzytkownik.rola === "admin") {
                przyciskiAdmina = `
                   <input type="button" value="Edytuj" onclick="ZaladujDoEdycji(${ksiazka.id}, '${ksiazka.tytul}', '${ksiazka.autor}')" class="btn btn-red">
                    <input type="button" value="Usuń" onclick="UsunKsiazke(${ksiazka.id})" class="btn btn-red"> 
                `;
            }
        }
        pojemnikSzczegolow.innerHTML = `
            <div class="ksiazka-karta">
                <img src="Logo.png" alt="Okładka" class="Logo">
                <h3>${ksiazka.tytul}</h3>
                <p>Autor: <b>${ksiazka.autor}</b></p>
                <p>Rodzaj: ${rodzaj} | Rok: ${rok}</p>
                <p>ID: ${ksiazka.id}</p>
                <input type="button" value="Wypożycz" onclick="WypozyczLubZarezerwuj('${ksiazka.id}', 'wypożyczono')" class="btn btn-red">
                <input type="button" value="Zarezerwuj" onclick="WypozyczLubZarezerwuj('${ksiazka.id}', 'zarezerwowano')" class="btn btn-red">
                ${przyciskiAdmina}
            </div>
        `;
    }
    catch (error) {
        pojemnikSzczegolow.innerHTML = "Wystąpił błąd przy pobieraniu szczegółów";
        console.log(error);
    }
}

async function WypozyczLubZarezerwuj(idKsiazki,akcja) {
    let tekstUzytkownika = localStorage.getItem("zalogowanyUzytkownik");

    if (tekstUzytkownika === null) {
        alert("Musisz się zalogować, aby wypożyczyć lub zarezerwować pozycję!");
        return;
    }

    let uzytkownik = JSON.parse(tekstUzytkownika);

    await fetch("/api/wypozyczenia", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            ksiazka_id: idKsiazki,
            uzytkownik_id: uzytkownik.id,
            typ: akcja
        })
    });
    SprawdzSesje();
}

async function DodajLubEdytujKsiazke(event) {
    event.preventDefault();

    let idEdycji = document.getElementById("edytuj-id").value;
    let tytul = document.getElementById("tytul-ksiazki").value;
    let autor = document.getElementById("autor-ksiazki").value;
    let rok = document.getElementById("rok-ksiazki").value;
    let rodzaj = document.getElementById("rodzaj-ksiazki").value;
    let komunikat = document.getElementById("komunikat-admin");

    let metoda = "POST";
    let adres = "/api/ksiazki";

    if (idEdycji !== "") {
        metoda = "PUT";
        adres = "/api/ksiazki/" + idEdycji;
    }

    try {
        let response = await fetch(adres, {
            method: metoda,
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ tytul: tytul, autor: autor, rok: Number(rok), rodzaj: rodzaj})
        });

        if (response.ok) {

            komunikat.style.color = "green";
            komunikat.innerText = "Zapisano pozycję w bazie!";

            document.getElementById("formularz-ksiazki").reset();
            document.getElementById("edytuj-id").value = "";
            document.getElementById("btn-zapisz-ksiazke").innerText = "Dodaj pozycję";

            PobierzKatalog();
        } else {
            komunikat.style.color = "red";
            komunikat.innerText = "Błąd zapisu danych.";
        }
    }
    catch (error) {
        komunikat.style.color = "red";
        komunikat.innerText = "Brak połączenia z API.";
        console.error(error);
    }
}

function ZaladujDoEdycji(id, tytul, autor) {
    document.getElementById("edytuj-id").value = id;
    document.getElementById("tytul-ksiazki").value = tytul;
    document.getElementById("autor-ksiazki").value = autor;
    document.getElementById("btn-zapisz-ksiazke").innerText = "Zapisz zmiany (ID: " + id + ")";
}

async function UsunKsiazke(idKsiazki) {
    try {
        let response = await fetch("/api/ksiazki/" + idKsiazki, {
            method: "DELETE"
        });

        if (response.ok) {
            document.getElementById("szczegoly-pozycji").innerHTML = "<p>Usunięto pozycję z bazy.</p>";
            PobierzKatalog();
        }
    }
    catch (error) {
        console.error(error);
    }
}

SprawdzSesje();


// DO ZROBIENIA W BACKENDZIE (main.py) I BAZIE DANYCH:
// 1. Tabela 'ksiazki' i klasa 'NowaKsiazka': dodać kolumny/pola 'rok' (INTEGER/int) oraz 'rodzaj' (VARCHAR/str) i uwzględnić je w POST /ksiazki oraz PUT /ksiazki/{id}.
// 2. Endpoint POST /logowanie: przyjąć login i haslo, sprawdzić w tabeli 'uzytkownicy' (WHERE login=%s AND haslo=%s) i zwrócić {id, login, rola} lub kod 401.
// 3. Tabela 'wypozyczenia' i klasa 'NoweWypozyczenie': dodać kolumnę/pole 'typ' (VARCHAR/str).
// 4. Endpointy wypożyczeń: dodać POST /wypozyczenia (zapis do tabeli) oraz GET /wypozyczenia/{uzytkownik_id} (SELECT z JOINem tabeli ksiazki zwracający tytul i typ).

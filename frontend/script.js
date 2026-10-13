async function PobierzKatalog() {
    let pojemnik = document.getElementById("katalog");
    pojemnik.innerHTML = "Pobieranie danych z bazy...";

    try {
        let response = await fetch("http://localhost:8000/api/ksiazki");
        let ksiazki = await response.json();

        pojemnik.innerHTML = "";

        ksiazki.forEach(ksiazka => {
                    let kafelek = document.createElement("div");
                    kafelek.className = "ksiazka-karta";
                    
                    kafelek.innerHTML = `
    <h3>${ksiazka.tytul}</h3>
    <p>Autor: <b>${ksiazka.autor}</b></p>
    <p>ID: ${ksiazka.id_ksiazki}</p>
`;
                    
                    pojemnik.appendChild(kafelek);
                });
    }
    catch (error) {
        pojemnik.innerHTML = "Wystąpił błąd przy połączeniu z API";
        console.error(error);
    }
}
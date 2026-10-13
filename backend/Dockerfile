# Wybieramy lekką wersję Pythona
FROM python:3.10-slim

# Tworzymy wirtualny folder roboczy wewnątrz kontenera
WORKDIR /app

# Kopiujemy listę potrzebnych bibliotek
COPY requirements.txt .

# Instalujemy te biblioteki
RUN pip install -r requirements.txt

# Kopiujemy całą resztę Twojego kodu z folderu backend
COPY . .

# Odpalamy serwer API (używamy nazwy system_test, bo taki masz plik pythona)
CMD ["uvicorn", "system_test:app", "--host", "0.0.0.0", "--port", "8000"]
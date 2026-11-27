import os
import sys
from pathlib import Path
import psycopg2
import pytest
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parent.parent   #ścieżka do głównego katalogu projektu
BACKEND_DIR = ROOT_DIR / "backend"  #ścieżka do katalogu backendu
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from main import app, polacz_z_db

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(autouse=True)
def cleanup_test_data():
    yield
    conn = polacz_z_db()
    cursor = conn.cursor()

    #usuwanie rekordów testowych utworzonych w trakcie testów (zachowanie danych startowych)

    cursor.execute("DELETE FROM historia_zmian WHERE szczegoly LIKE '[TEST]%';")
    cursor.execute("DELETE FROM wypozyczenia WHERE ksiazka_id > 102;")
    cursor.execute("DELETE FROM ksiazki WHERE id > 102;")
    cursor.execute("DELETE FROM uzytkownicy WHERE login != 'admin';")

    conn.commit()
    cursor.close()
    conn.close()
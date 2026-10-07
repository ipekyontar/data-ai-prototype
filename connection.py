"""
MySQL bağlantı katmanı
------------------------
mysql-connector-python kullanarak lokal MySQL sunucusuna (MySQL Workbench
ile aynı sunucu) bağlanır. Tüm bağlantı hataları anlamlı Türkçe mesajlarla
yakalanır (try-except) ki Streamlit arayüzünde kullanıcıya net bilgi
gösterilebilsin.
"""

import sys
import os

# Proje kökünü path'e ekle (app.py / seed_data.py farklı dizinlerden çalıştırılsa da import bozulmasın)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mysql.connector
from mysql.connector import Error

from config import DB_CONFIG


class BorusanDBError(Exception):
    """Uygulamaya özel, kullanıcı dostu DB hata sınıfı."""
    pass


def get_connection(with_database: bool = True):
    """
    MySQL sunucusuna yeni bir bağlantı açar.

    Parametreler
    ----------
    with_database : bool
        True  -> borusan_otomotiv_db şemasına bağlanır (normal kullanım)
        False -> Sadece sunucuya bağlanır (ilk kurulumda veritabanı
                 henüz yokken schema.sql çalıştırmak için kullanılır)
    """
    cfg = DB_CONFIG.copy()
    if not with_database:
        cfg.pop("database", None)

    try:
        conn = mysql.connector.connect(
            host=cfg["host"],
            port=cfg["port"],
            user=cfg["user"],
            password=cfg["password"],
            database=cfg.get("database"),
            connection_timeout=5,
        )
        return conn

    except Error as e:
        raise BorusanDBError(
            "MySQL bağlantısı kurulamadı.\n\n"
            f"Teknik detay: {e}\n\n"
            "Kontrol listesi (macOS):\n"
            "  1) MySQL sunucusu çalışıyor mu? (MySQL Workbench > Instance > Startup/Shutdown\n"
            "     veya terminalde: mysqladmin -u root -p status)\n"
            "  2) Host/port doğru mu? Varsayılan: localhost:3306\n"
            "  3) Kullanıcı adı/şifre doğru mu? (varsayılan kullanıcı: root)\n"
            "  4) Şifren varsa terminalde şu şekilde tanımladın mı?\n"
            "     export BORUSAN_DB_PASSWORD=\"sifren\"\n"
            "  5) 'borusan_otomotiv_db' veritabanı henüz oluşmadıysa önce şunu çalıştır:\n"
            "     python3 db/seed_data.py"
        ) from e


def run_query(sql: str, params: tuple = None, fetch: bool = True):
    """
    Tek seferlik sorgu çalıştırma yardımcı fonksiyonu.
    fetch=True  -> SELECT sorguları için (kolon adları + satırları döner)
    fetch=False -> INSERT/UPDATE/CREATE gibi DDL/DML sorguları için
    """
    conn = None
    cursor = None
    try:
        conn = get_connection(with_database=True)
        cursor = conn.cursor()
        cursor.execute(sql, params or ())

        if fetch:
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            return columns, rows
        else:
            conn.commit()
            return cursor.rowcount

    except BorusanDBError:
        raise
    except Error as e:
        raise BorusanDBError(f"Sorgu çalıştırılırken hata oluştu: {e}") from e
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()


def test_connection() -> bool:
    """Bağlantının sağlıklı olup olmadığını hızlıca test eder."""
    try:
        conn = get_connection(with_database=True)
        conn.close()
        return True
    except BorusanDBError:
        return False

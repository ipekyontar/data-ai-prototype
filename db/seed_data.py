"""
db/seed_data.py
------------------------------------------------------------
Bu script:
  1) borusan_otomotiv_db veritabanini (yoksa) olusturur
  2) musteriler / araclar / servis_kayitlari tablolarini kurar
  3) Gerceginmis gibi (sentetik) ornek verilerle doldurur

Calistirma (macOS terminal, proje kok dizininden):

    python3 db/seed_data.py

Not: Script tekrar tekrar calistirilirsa once mevcut veriler temizlenir
(TRUNCATE) ve yeniden uretilir; bu yuzden guvenle tekrar calistirabilirsin.
"""

import os
import sys
import random
from datetime import date, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mysql.connector
from mysql.connector import Error

from config import DB_CONFIG

SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")

random.seed(42)

AD_SOYAD_LISTESI = [
    "Ahmet Yilmaz", "Ayse Kaya", "Mehmet Demir", "Fatma Sahin", "Mustafa Celik",
    "Zeynep Yildiz", "Emre Aydin", "Elif Ozturk", "Can Arslan", "Selin Dogan",
    "Burak Kilic", "Ece Aslan", "Onur Cetin", "Deniz Kurt", "Gizem Aksoy",
    "Kaan Ozdemir", "Merve Turan", "Ali Koc", "Busra Er", "Serkan Bulut",
    "Nur Sen", "Tolga Guler", "Irem Polat", "Baris Tas", "Sibel Uysal",
    "Volkan Ozkan", "Aylin Bal", "Ugur Simsek", "Ceren Avci", "Ozan Aktas",
    "Damla Yalcin", "Furkan Tekin", "Pinar Kara", "Cem Bahar", "Hande Sonmez",
    "Berk Ergin", "Naz Kaplan", "Yusuf Toprak", "Gul Aydogan", "Serdar Isik",
    "Aslihan Cinar", "Tuncay Ozgur", "Melis Duran", "Kerem Bozkurt", "Sena Aktepe",
    "Eren Coban", "Ceyda Karatas", "Batuhan Ozer", "Sude Yavuz", "Arda Guven",
]

SEHIRLER = ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Kocaeli", "Kayseri", "Adana"]

# marka -> (model listesi, yakit tipi agirliklari)
ARAC_KATALOGU = {
    "Ford":       {"modeller": ["Focus", "Puma", "Kuga", "Transit"], "yakitlar": ["Benzinli", "Dizel", "Hibrit"]},
    "BMC":        {"modeller": ["Tugra", "Neyra"], "yakitlar": ["Dizel"]},
    "Otokar":     {"modeller": ["Territo", "Kent"], "yakitlar": ["Dizel", "Elektrikli"]},
    "Renault":    {"modeller": ["Megane", "Clio", "Zoe", "Austral"], "yakitlar": ["Benzinli", "Dizel", "Elektrikli"]},
    "Tesla":      {"modeller": ["Model 3", "Model Y"], "yakitlar": ["Elektrikli"]},
    "Togg":       {"modeller": ["T10X"], "yakitlar": ["Elektrikli"]},
    "Volkswagen": {"modeller": ["Golf", "Passat", "ID.4", "Tiguan"], "yakitlar": ["Benzinli", "Dizel", "Elektrikli", "Hibrit"]},
    "Toyota":     {"modeller": ["Corolla", "C-HR", "RAV4"], "yakitlar": ["Benzinli", "Hibrit"]},
}

SERVIS_TIPLERI = [
    "Periyodik Bakim", "Lastik Degisimi", "Fren Bakimi", "Batarya Kontrolu",
    "Yazilim Guncelleme", "Klima Bakimi", "Genel Kontrol", "Kaporta Onarimi",
    "Sarj Sistemi Kontrolu", "Motor Bakimi",
]

SERVIS_ACIKLAMALARI = [
    "Musteri memnun ayrildi.", "Bekleme suresi uzun oldu.", "Parca temininde gecikme yasandi.",
    "Islem sorunsuz tamamlandi.", "Musteri fiyattan sikayetci.", "Randevu saatinde baslandi.",
    "Ek ariza tespit edildi.", "Hizli ve sorunsuz servis.", "Musteri iletisimden memnun degil.",
    "Standart bakim tamamlandi.",
]


def read_schema_statements():
    """
    schema.sql dosyasini okuyup calistirilabilir SQL komutlarina ayirir.

    DUZELTME: Onceki surumde, bir SQL komutunun hemen ustunde yorum satiri
    (-- ile baslayan aciklama) varsa, komutun TAMAMI yanlislikla "yorum"
    sanilip atlaniyordu (ozellikle dosyanin en basindaki CREATE DATABASE
    komutu bu yuzden hic calismiyordu). Simdi her satir tek tek kontrol
    edilip sadece yorum SATIRLARI siliniyor, gercek SQL komutlari korunuyor.
    """
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    statements = []
    for raw_block in content.split(";"):
        # Blok icindeki her satiri kontrol et, yorum satirlarini (--) at
        temiz_satirlar = []
        for line in raw_block.split("\n"):
            if line.strip().startswith("--"):
                continue
            temiz_satirlar.append(line)

        stmt = "\n".join(temiz_satirlar).strip()
        if not stmt:
            continue
        statements.append(stmt)

    return statements


def create_schema():
    """Sunucuya (veritabani secmeden) baglanip semayi kurar."""
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            connection_timeout=5,
        )
        cursor = conn.cursor()
        for stmt in read_schema_statements():
            cursor.execute(stmt)
        conn.commit()
        cursor.close()
        conn.close()
        print("[OK] Veritabani ve tablolar hazir: borusan_otomotiv_db")
    except Error as e:
        print("[HATA] Sema olusturulamadi:", e)
        print(">> MySQL sunucusunun calistigindan ve kullanici/sifre bilgilerinin")
        print("   config.py / ortam degiskenleriyle uyustugundan emin olun.")
        sys.exit(1)


def random_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, max(delta, 0)))


def generate_and_insert_data(musteri_sayisi: int = 50):
    try:
        conn = mysql.connector.connect(**DB_CONFIG, connection_timeout=5)
        cursor = conn.cursor()

        # Tekrar calistirilabilir olmasi icin once temizle
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("TRUNCATE TABLE servis_kayitlari")
        cursor.execute("TRUNCATE TABLE araclar")
        cursor.execute("TRUNCATE TABLE musteriler")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        conn.commit()

        bugun = date.today()
        iki_yil_once = bugun - timedelta(days=730)

        musteri_ids = []
        for i in range(musteri_sayisi):
            ad_soyad = AD_SOYAD_LISTESI[i % len(AD_SOYAD_LISTESI)]
            sehir = random.choice(SEHIRLER)
            telefon = f"05{random.randint(30,59)}{random.randint(1000000,9999999)}"
            email = ad_soyad.lower().replace(" ", ".").replace("ı", "i") + "@example.com"
            kayit_tarihi = random_date(iki_yil_once, bugun)

            cursor.execute(
                """INSERT INTO musteriler (ad_soyad, sehir, telefon, email, kayit_tarihi)
                   VALUES (%s, %s, %s, %s, %s)""",
                (ad_soyad, sehir, telefon, email, kayit_tarihi),
            )
            musteri_ids.append(cursor.lastrowid)

        conn.commit()

        arac_ids = []
        markalar = list(ARAC_KATALOGU.keys())
        for musteri_id in musteri_ids:
            arac_sayisi = random.choices([1, 2], weights=[0.75, 0.25])[0]
            for _ in range(arac_sayisi):
                marka = random.choice(markalar)
                katalog = ARAC_KATALOGU[marka]
                model = random.choice(katalog["modeller"])
                yakit_tipi = random.choice(katalog["yakitlar"])
                model_yili = random.randint(2018, 2025)
                plaka = f"{random.randint(1,81):02d} {random.choice('ABCDEFGHJKLMNPRSTUVYZ')}{random.choice('ABCDEFGHJKLMNPRSTUVYZ')} {random.randint(100,999)}"

                cursor.execute(
                    """INSERT INTO araclar (musteri_id, plaka, marka, model, model_yili, yakit_tipi)
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (musteri_id, plaka, marka, model, model_yili, yakit_tipi),
                )
                arac_ids.append(cursor.lastrowid)

        conn.commit()

        for arac_id in arac_ids:
            servis_sayisi = random.randint(1, 4)
            for _ in range(servis_sayisi):
                servis_tarihi = random_date(iki_yil_once, bugun)
                servis_tipi = random.choice(SERVIS_TIPLERI)
                aciklama = random.choice(SERVIS_ACIKLAMALARI)
                maliyet = round(random.uniform(350, 9500), 2)
                memnuniyet = random.choices([1, 2, 3, 4, 5], weights=[0.08, 0.12, 0.20, 0.30, 0.30])[0]

                cursor.execute(
                    """INSERT INTO servis_kayitlari
                       (arac_id, servis_tarihi, servis_tipi, aciklama, maliyet_tl, memnuniyet_puani)
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (arac_id, servis_tarihi, servis_tipi, aciklama, maliyet, memnuniyet),
                )

        conn.commit()
        cursor.close()
        conn.close()

        print(f"[OK] {len(musteri_ids)} musteri, {len(arac_ids)} arac, servis kayitlari ile birlikte eklendi.")

    except Error as e:
        print("[HATA] Ornek veri eklenirken sorun olustu:", e)
        sys.exit(1)


if __name__ == "__main__":
    print("Borusan Otomotiv - Veritabani kurulumu baslatiliyor...")
    create_schema()
    generate_and_insert_data()
    print("Kurulum tamamlandi. Simdi 'streamlit run app.py' ile uygulamayi baslatabilirsin.")

"""
Borusan Otomotiv AI Prototipi - Konfigürasyon
------------------------------------------------
MySQL bağlantı bilgileri burada tutulur. Varsayılanlar, macOS üzerinde
MySQL Workbench ile birlikte kurulan yerel bir MySQL sunucusuna göre
ayarlanmıştır (localhost:3306, kullanıcı: root).

İstersen şifreni kod içine yazmak yerine terminalden ortam değişkeni
olarak da verebilirsin:

    export BORUSAN_DB_PASSWORD="senin_sifren"

Bu değer varsa otomatik olarak kullanılır, yoksa BOŞ ŞİFRE varsayılır
(Mac'te MySQL Workbench kurulumlarında sık görülen bir senaryodur).
"""

import os

DB_CONFIG = {
    "host": os.getenv("BORUSAN_DB_HOST", "localhost"),
    "port": int(os.getenv("BORUSAN_DB_PORT", "3306")),
    "user": os.getenv("BORUSAN_DB_USER", "root"),
    "password": os.getenv("BORUSAN_DB_PASSWORD", ""),  # kendi şifreni buraya ya da env'e yaz
    "database": os.getenv("BORUSAN_DB_NAME", "borusan_otomotiv_db"),
}

APP_TITLE = "Borusan Otomotiv | Veri & AI Prototipi"

"""
services/nlu_engine.py
------------------------------------------------------------
Cok basit ama genisletilebilir, KURAL TABANLI (anahtar kelime esleme)
bir "dogal dil -> SQL" motoru.

Bu prototipte harici bir LLM API'sine (OpenAI/Claude vb.) baglanmadan,
Turkce anahtar kelimeleri tanıyarak dinamik SQL uretiyoruz. Boylece:
  - API anahtari gerekmeden calisir (Vibe Coding / hizli prototip icin ideal)
  - Istersen ileride bu fonksiyonun icini bir LLM cagrisiyla degistirip
    "gercek" bir NL->SQL katmanina yukseltebilirsin (asagida NOT bolumune bak).

parse_soru(soru: str) -> dict:
    {
        "sql": "...",
        "params": (...),
        "aciklama": "Kullaniciya gosterilecek insan-okunur ozet"
    }
"""

import re

TABLO_JOIN = """
FROM servis_kayitlari sk
JOIN araclar a       ON sk.arac_id = a.arac_id
JOIN musteriler m     ON a.musteri_id = m.musteri_id
"""

TEMEL_SECIM = """
SELECT
    m.ad_soyad        AS musteri,
    m.sehir           AS sehir,
    a.marka           AS marka,
    a.model           AS model,
    a.yakit_tipi       AS yakit_tipi,
    sk.servis_tarihi   AS servis_tarihi,
    sk.servis_tipi      AS servis_tipi,
    sk.memnuniyet_puani AS memnuniyet_puani,
    sk.maliyet_tl        AS maliyet_tl
"""

YAKIT_TIPLERI = {
    "elektrikli": "Elektrikli",
    "elektrikliyle": "Elektrikli",
    "benzinli": "Benzinli",
    "benzin": "Benzinli",
    "dizel": "Dizel",
    "mazot": "Dizel",
    "hibrit": "Hibrit",
}

SEHIRLER = ["istanbul", "ankara", "izmir", "bursa", "antalya", "kocaeli", "kayseri", "adana"]

MARKALAR = ["ford", "bmc", "otokar", "renault", "tesla", "togg", "volkswagen", "toyota"]


def _normalize(text: str) -> str:
    text = text.lower()
    replacements = {"ı": "i", "İ": "i", "ş": "s", "ç": "c", "ğ": "g", "ö": "o", "ü": "u"}
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text


def parse_soru(soru: str) -> dict:
    norm = _normalize(soru)

    where_clauses = []
    params = []
    aciklama_parcalari = []

    # --- 1) Yakit tipi tespiti ---
    for anahtar, deger in YAKIT_TIPLERI.items():
        if anahtar in norm:
            where_clauses.append("a.yakit_tipi = %s")
            params.append(deger)
            aciklama_parcalari.append(f"yakit tipi = {deger}")
            break

    # --- 2) Sehir tespiti ---
    for sehir in SEHIRLER:
        if sehir in norm:
            where_clauses.append("LOWER(m.sehir) = %s")
            params.append(sehir)
            aciklama_parcalari.append(f"sehir = {sehir.title()}")
            break

    # --- 3) Marka tespiti ---
    for marka in MARKALAR:
        if marka in norm:
            where_clauses.append("LOWER(a.marka) = %s")
            params.append(marka)
            aciklama_parcalari.append(f"marka = {marka.title()}")
            break

    # --- 4) Memnuniyet puani (dusuk / yuksek / sayisal esik) ---
    esik_match = re.search(r"(\d)\s*(puan|uzeri|alti|ustunde|altinda)", norm)
    if "memnuniyet" in norm or "puan" in norm:
        if esik_match:
            esik = int(esik_match.group(1))
            if "alti" in norm or "altinda" in norm:
                where_clauses.append("sk.memnuniyet_puani < %s")
                params.append(esik)
                aciklama_parcalari.append(f"memnuniyet puani < {esik}")
            else:
                where_clauses.append("sk.memnuniyet_puani >= %s")
                params.append(esik)
                aciklama_parcalari.append(f"memnuniyet puani >= {esik}")
        elif "dusuk" in norm or "kotu" in norm or "sikayet" in norm:
            where_clauses.append("sk.memnuniyet_puani <= %s")
            params.append(2)
            aciklama_parcalari.append("memnuniyet puani <= 2 (dusuk)")
        elif "yuksek" in norm or "iyi" in norm or "memnun" in norm:
            where_clauses.append("sk.memnuniyet_puani >= %s")
            params.append(4)
            aciklama_parcalari.append("memnuniyet puani >= 4 (yuksek)")

    # --- 5) Servis tipi (basit anahtar kelime esleme) ---
    servis_anahtarlari = {
        "bakim": "Bakim",
        "lastik": "Lastik",
        "fren": "Fren",
        "batarya": "Batarya",
        "sarj": "Sarj",
        "klima": "Klima",
        "kaporta": "Kaporta",
        "yazilim": "Yazilim",
        "motor": "Motor",
    }
    for anahtar, etiket in servis_anahtarlari.items():
        if anahtar in norm:
            where_clauses.append("sk.servis_tipi LIKE %s")
            params.append(f"%{etiket}%")
            aciklama_parcalari.append(f"servis tipi ~ {etiket}")
            break

    # --- 6) Serbest metin arama (musteri adi vb.) - hicbir filtre bulunamadiysa ---
    if not where_clauses:
        where_clauses.append(
            "(m.ad_soyad LIKE %s OR m.sehir LIKE %s OR a.marka LIKE %s OR sk.servis_tipi LIKE %s)"
        )
        arama_terimi = f"%{soru.strip()}%"
        params.extend([arama_terimi, arama_terimi, arama_terimi, arama_terimi])
        aciklama_parcalari.append(f"'{soru}' icin genel metin araması")

    where_sql = " AND ".join(where_clauses)

    sql = f"""
    {TEMEL_SECIM}
    {TABLO_JOIN}
    WHERE {where_sql}
    ORDER BY sk.servis_tarihi DESC
    LIMIT 200
    """.strip()

    aciklama = "Filtreler: " + ", ".join(aciklama_parcalari) if aciklama_parcalari else "Genel sorgu"

    return {"sql": sql, "params": tuple(params), "aciklama": aciklama}


# ------------------------------------------------------------------
# NOT (Genişletme fikri):
# Bu fonksiyonun govdesini, Anthropic API'sine (Claude) bir sistem
# promptu ile "kullanicinin sorusunu asagidaki semaya gore SQL'e cevir"
# seklinde bir cagriyla degistirerek gercek bir LLM-tabanli NL->SQL
# katmanina yukseltebilirsin. Bu prototipte, harici bir API anahtarina
# ihtiyac duymadan calismasi icin kural tabanli yaklasim tercih edildi.
# ------------------------------------------------------------------

"""
services/queries.py
------------------------------------------------------------
Streamlit sol panelinde gosterilecek genel istatistikler icin
hazir (parametresiz) SQL sorgulari.
"""

TOPLAM_MUSTERI = "SELECT COUNT(*) AS toplam FROM musteriler"

TOPLAM_ARAC = "SELECT COUNT(*) AS toplam FROM araclar"

TOPLAM_SERVIS = "SELECT COUNT(*) AS toplam FROM servis_kayitlari"

ORTALAMA_MEMNUNIYET = "SELECT ROUND(AVG(memnuniyet_puani), 2) AS ortalama FROM servis_kayitlari"

YAKIT_DAGILIMI = """
SELECT yakit_tipi, COUNT(*) AS adet
FROM araclar
GROUP BY yakit_tipi
ORDER BY adet DESC
"""

SEHIR_DAGILIMI = """
SELECT sehir, COUNT(*) AS adet
FROM musteriler
GROUP BY sehir
ORDER BY adet DESC
"""

YAKIT_BAZLI_ORTALAMA_MEMNUNIYET = """
SELECT a.yakit_tipi, ROUND(AVG(sk.memnuniyet_puani), 2) AS ortalama_memnuniyet, COUNT(*) AS servis_sayisi
FROM servis_kayitlari sk
JOIN araclar a ON sk.arac_id = a.arac_id
GROUP BY a.yakit_tipi
ORDER BY ortalama_memnuniyet ASC
"""

DUSUK_MEMNUNIYET_SON_KAYITLAR = """
SELECT m.ad_soyad AS musteri, a.marka, a.yakit_tipi, sk.servis_tarihi, sk.memnuniyet_puani
FROM servis_kayitlari sk
JOIN araclar a ON sk.arac_id = a.arac_id
JOIN musteriler m ON a.musteri_id = m.musteri_id
WHERE sk.memnuniyet_puani <= 2
ORDER BY sk.servis_tarihi DESC
LIMIT 10
"""

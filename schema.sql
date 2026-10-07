-- ============================================================
-- Borusan Otomotiv - Veritabani Semasi (guncel MySQL surumleriyle uyumlu)
-- ============================================================

CREATE DATABASE IF NOT EXISTS borusan_otomotiv_db
    CHARACTER SET utf8mb4;

USE borusan_otomotiv_db;

-- 1) Musteriler
CREATE TABLE IF NOT EXISTS musteriler (
    musteri_id      INT AUTO_INCREMENT PRIMARY KEY,
    ad_soyad        VARCHAR(120) NOT NULL,
    sehir           VARCHAR(60)  NOT NULL,
    telefon         VARCHAR(20),
    email           VARCHAR(120),
    kayit_tarihi    DATE NOT NULL
) ENGINE=InnoDB;

-- 2) Araclar (Elektrikli / Benzinli / Dizel / Hibrit)
CREATE TABLE IF NOT EXISTS araclar (
    arac_id         INT AUTO_INCREMENT PRIMARY KEY,
    musteri_id      INT NOT NULL,
    plaka           VARCHAR(15) NOT NULL,
    marka           VARCHAR(50) NOT NULL,
    model            VARCHAR(50) NOT NULL,
    model_yili      INT NOT NULL,
    yakit_tipi      ENUM('Elektrikli','Benzinli','Dizel','Hibrit') NOT NULL,
    FOREIGN KEY (musteri_id) REFERENCES musteriler(musteri_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 3) Servis Kayitlari + memnuniyet puanlari (1-5)
CREATE TABLE IF NOT EXISTS servis_kayitlari (
    servis_id           INT AUTO_INCREMENT PRIMARY KEY,
    arac_id             INT NOT NULL,
    servis_tarihi       DATE NOT NULL,
    servis_tipi         VARCHAR(80) NOT NULL,
    aciklama            VARCHAR(255),
    maliyet_tl          DECIMAL(10,2) NOT NULL,
    memnuniyet_puani    TINYINT NOT NULL,
    FOREIGN KEY (arac_id) REFERENCES araclar(arac_id) ON DELETE CASCADE,
    CONSTRAINT chk_memnuniyet CHECK (memnuniyet_puani BETWEEN 1 AND 5)
) ENGINE=InnoDB;

CREATE INDEX idx_araclar_yakit ON araclar(yakit_tipi);
CREATE INDEX idx_servis_puan ON servis_kayitlari(memnuniyet_puani);
CREATE INDEX idx_servis_tarih ON servis_kayitlari(servis_tarihi);

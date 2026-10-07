# Borusan Otomotiv – Veri & AI Odaklı Prototip

Streamlit + MySQL kullanan, doğal dille sorgulanabilen bir müşteri/araç/servis
memnuniyeti prototipi. `Vibe Coding` yaklaşımıyla hızlı kurulup denenebilecek
şekilde tasarlandı.

## Klasör Yapısı

```
borusan_ai_prototip/
├── app.py                     # Streamlit ana uygulama
├── config.py                  # MySQL bağlantı ayarları
├── requirements.txt
├── README.md
├── db/
│   ├── connection.py          # mysql-connector-python bağlantı katmanı
│   ├── schema.sql             # Tablo tanımları (musteriler, araclar, servis_kayitlari)
│   └── seed_data.py           # Veritabanını kurar + örnek veriyle doldurur
└── services/
    ├── nlu_engine.py          # Doğal dil -> SQL (kural tabanlı) motor
    └── queries.py             # Sidebar istatistikleri için hazır sorgular
```

## 1) macOS'te Kurulum

Terminalde proje klasörüne girin ve (tercihen bir sanal ortam içinde) paketleri kurun:

```bash
cd borusan_ai_prototip

# (Opsiyonel ama önerilir) sanal ortam
python3 -m venv venv
source venv/bin/activate

# Gerekli paketler
pip3 install -r requirements.txt
```

MySQL sunucusu Mac'inizde kurulu değilse (Homebrew ile):

```bash
brew install mysql
brew services start mysql
```

MySQL Workbench zaten kuruluysa ve sunucu çalışıyorsa bu adımı atlayabilirsiniz.

## 2) Bağlantı Bilgilerini Ayarlama

Varsayılan ayarlar `config.py` içinde `localhost:3306`, kullanıcı `root`,
şifre boş olarak tanımlıdır. Eğer root kullanıcınızın bir şifresi varsa,
terminalde şunu çalıştırıp uygulamayı öyle başlatın:

```bash
export BORUSAN_DB_PASSWORD="senin_sifren"
```

(İsterseniz `config.py` içindeki `DB_CONFIG["password"]` değerini de doğrudan
düzenleyebilirsiniz.)

## 3) Veritabanını Kurma ve Örnek Veri Ekleme

```bash
python3 db/seed_data.py
```

Bu komut:
- `borusan_otomotiv_db` veritabanını (yoksa) oluşturur,
- `musteriler`, `araclar`, `servis_kayitlari` tablolarını kurar,
- 50 müşteri, her biri için 1-2 araç (Elektrikli/Benzinli/Dizel/Hibrit) ve
  her araç için 1-4 servis kaydı ile birlikte sentetik veriler ekler.

Script tekrar çalıştırıldığında mevcut veriler temizlenip yeniden üretilir,
bu yüzden istediğiniz kadar tekrar çalıştırabilirsiniz.

MySQL Workbench üzerinden `borusan_otomotiv_db` şemasını açarak tabloları
ve verileri görsel olarak da inceleyebilirsiniz.

## 4) Uygulamayı Başlatma

```bash
streamlit run app.py
```

Tarayıcıda otomatik olarak `http://localhost:8501` açılacaktır.

## Kullanım

- **Sol panel**: toplam müşteri/araç/servis sayısı, ortalama memnuniyet,
  yakıt tipine göre dağılım ve şehir dağılımı gibi canlı istatistikler.
- **Orta alan (sohbet)**: doğal dilde soru yazın, örnekler:
  - "Elektrikli araçlarla servise gelen memnuniyeti düşük müşteriler kimler?"
  - "İstanbul'daki hibrit araç sahiplerinin memnuniyeti nedir?"
  - "Lastik değişimi yaptıran müşteriler kimler?"
  - "Benzinli araçlarda memnuniyeti 4 puan üzeri olanlar"

Her cevabın altında, sonucu üreten SQL sorgusunu görmek için
**"Çalıştırılan SQL sorgusunu göster"** kısmını açabilirsiniz (şeffaflık için).

## Not: Doğal Dil Motoru Hakkında

`services/nlu_engine.py` içindeki `parse_soru()` fonksiyonu, harici bir LLM
API anahtarına ihtiyaç duymadan çalışsın diye **kural tabanlı** (anahtar
kelime eşleme) şekilde yazıldı. Yakıt tipi, şehir, marka, memnuniyet puanı
eşiği ve servis tipi gibi kalıpları tanır.

İstersen bu fonksiyonu, Anthropic API'sine (Claude) şemayı içeren bir sistem
promptuyla soru gönderip SQL üretecek şekilde genişleterek gerçek bir
LLM-tabanlı NL→SQL katmanına yükseltebilirsin — kod içinde bunun için bir
NOT bırakıldı.

## Sorun Giderme

| Hata | Olası Çözüm |
|---|---|
| `MySQL bağlantısı kurulamadı` | MySQL sunucusunun çalıştığından emin olun: `mysqladmin -u root -p status` |
| `Unknown database 'borusan_otomotiv_db'` | `python3 db/seed_data.py` çalıştırılmamış olabilir |
| `Access denied for user 'root'` | Şifreyi `export BORUSAN_DB_PASSWORD=...` ile tanımlayın |
| Port hatası | MySQL Workbench'te sunucunun `3306` portunda çalıştığını doğrulayın |

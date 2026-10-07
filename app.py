"""
Borusan Otomotiv - Veri & AI Odakli Prototip
------------------------------------------------------------
Calistirma (macOS terminal, proje kok dizininden):

    streamlit run app.py

Bu dosya ic ice iki sey yapar:
  1) Sol panelde MySQL veritabanindan canli istatistikler gosterir.
  2) Ortada, kullanicinin dogal dille soru sorabilecegi bir "chat"
     arayuzu sunar; sorular services/nlu_engine.py tarafindan SQL'e
     cevrilir ve sonuc bir tablo (pandas DataFrame) olarak basilir.
"""

import streamlit as st
import pandas as pd

from config import APP_TITLE
from db.connection import run_query, test_connection, BorusanDBError
from services import queries as q
from services.nlu_engine import parse_soru


# ------------------------------------------------------------------
# Sayfa ayarlari
# ------------------------------------------------------------------
st.set_page_config(page_title=APP_TITLE, page_icon="🚗", layout="wide")


# ------------------------------------------------------------------
# Yardimci: guvenli sorgu calistirma (try-except ile)
# ------------------------------------------------------------------
def safe_query(sql: str, params: tuple = None):
    """
    run_query'yi cagirir, hata olursa None ve hata mesaji dondurur.
    Basarili olursa (DataFrame, None) dondurur.
    """
    try:
        columns, rows = run_query(sql, params, fetch=True)
        df = pd.DataFrame(rows, columns=columns)
        return df, None
    except BorusanDBError as e:
        return None, str(e)
    except Exception as e:  # beklenmeyen her turlu hataya karsi son savunma
        return None, f"Beklenmeyen hata: {e}"


def safe_scalar(sql: str, default=0):
    """Tek deger donen (COUNT/AVG gibi) sorgular icin kisayol."""
    df, err = safe_query(sql)
    if err is not None or df is None or df.empty:
        return default, err
    return df.iloc[0, 0], None


# ------------------------------------------------------------------
# BASLIK
# ------------------------------------------------------------------
st.title("🚗 " + APP_TITLE)
st.caption(
    "Lokal MySQL (borusan_otomotiv_db) uzerinde calisan, "
    "dogal dil sorgu destekli veri/AI prototipi."
)


# ------------------------------------------------------------------
# BAGLANTI DURUMU KONTROLU
# ------------------------------------------------------------------
baglanti_ok = test_connection()

if not baglanti_ok:
    st.error(
        "⚠️ MySQL veritabanina baglanilamadi.\n\n"
        "Lutfen su adimlari kontrol edin:\n"
        "1. MySQL Workbench / sunucusunun calistigindan emin olun (localhost:3306).\n"
        "2. `config.py` icindeki kullanici/sifre bilgilerinin dogru oldugunu kontrol edin.\n"
        "3. Veritabani henuz olusturulmadiysa terminalde su komutu calistirin:\n\n"
        "   `python3 db/seed_data.py`\n"
    )
    st.stop()


# ------------------------------------------------------------------
# SOL PANEL (SIDEBAR): GENEL ISTATISTIKLER
# ------------------------------------------------------------------
with st.sidebar:
    st.header("📊 Veritabani Istatistikleri")
    st.success("MySQL baglantisi aktif ✅")

    toplam_musteri, err1 = safe_scalar(q.TOPLAM_MUSTERI)
    toplam_arac, err2 = safe_scalar(q.TOPLAM_ARAC)
    toplam_servis, err3 = safe_scalar(q.TOPLAM_SERVIS)
    ortalama_memnuniyet, err4 = safe_scalar(q.ORTALAMA_MEMNUNIYET, default=0.0)

    for err in (err1, err2, err3, err4):
        if err:
            st.warning(err)

    col1, col2 = st.columns(2)
    col1.metric("👤 Musteri", f"{toplam_musteri}")
    col2.metric("🚙 Arac", f"{toplam_arac}")

    col3, col4 = st.columns(2)
    col3.metric("🔧 Servis Kaydi", f"{toplam_servis}")
    col4.metric("⭐ Ort. Memnuniyet", f"{ortalama_memnuniyet}")

    st.divider()
    st.subheader("Yakit Tipine Gore Dagilim")
    df_yakit, err = safe_query(q.YAKIT_DAGILIMI)
    if err:
        st.warning(err)
    elif df_yakit is not None and not df_yakit.empty:
        st.bar_chart(df_yakit.set_index("yakit_tipi"))

    st.subheader("Yakit Tipine Gore Ort. Memnuniyet")
    df_yakit_memnuniyet, err = safe_query(q.YAKIT_BAZLI_ORTALAMA_MEMNUNIYET)
    if err:
        st.warning(err)
    elif df_yakit_memnuniyet is not None and not df_yakit_memnuniyet.empty:
        st.dataframe(df_yakit_memnuniyet, use_container_width=True, hide_index=True)

    st.subheader("Sehir Dagilimi")
    df_sehir, err = safe_query(q.SEHIR_DAGILIMI)
    if err:
        st.warning(err)
    elif df_sehir is not None and not df_sehir.empty:
        st.bar_chart(df_sehir.set_index("sehir"))

    st.divider()
    if st.button("🔄 Istatistikleri Yenile"):
        st.rerun()


# ------------------------------------------------------------------
# ORTA ALAN: DOGAL DIL SOHBET ARAYUZU
# ------------------------------------------------------------------
st.subheader("💬 Veriye Dogal Dille Soru Sor")
st.caption(
    "Ornek: *'Elektrikli araclarla servise gelen memnuniyeti dusuk musteriler kimler?'*, "
    "*'Istanbul'daki hibrit arac sahiplerinin memnuniyeti nedir?'*, "
    "*'Lastik degisimi yaptiran musteriler kimler?'*"
)

if "chat_gecmisi" not in st.session_state:
    st.session_state.chat_gecmisi = []

# Onceki mesajlari goster
for mesaj in st.session_state.chat_gecmisi:
    with st.chat_message(mesaj["rol"]):
        st.markdown(mesaj["icerik"])
        if mesaj.get("df") is not None:
            st.dataframe(mesaj["df"], use_container_width=True, hide_index=True)
            with st.expander("Calistirilan SQL sorgusunu goster"):
                st.code(mesaj.get("sql", ""), language="sql")

# Yeni soru girisi
kullanici_sorusu = st.chat_input(
    "Sorunuzu yazin... (orn. Elektrikli araclarda memnuniyeti dusuk musteriler kimler?)"
)

if kullanici_sorusu:
    st.session_state.chat_gecmisi.append(
        {"rol": "user", "icerik": kullanici_sorusu, "df": None, "sql": None}
    )
    with st.chat_message("user"):
        st.markdown(kullanici_sorusu)

    with st.chat_message("assistant"):
        try:
            sorgu = parse_soru(kullanici_sorusu)
            sql, params, aciklama = sorgu["sql"], sorgu["params"], sorgu["aciklama"]

            df, hata = safe_query(sql, params)

            if hata:
                cevap_metni = f"❌ Sorgu calistirilirken bir hata olustu:\n\n{hata}"
                st.error(cevap_metni)
                st.session_state.chat_gecmisi.append(
                    {"rol": "assistant", "icerik": cevap_metni, "df": None, "sql": sql}
                )
            elif df is None or df.empty:
                cevap_metni = f"🔍 {aciklama}.\n\nBu kriterlere uyan kayit bulunamadi."
                st.markdown(cevap_metni)
                st.session_state.chat_gecmisi.append(
                    {"rol": "assistant", "icerik": cevap_metni, "df": None, "sql": sql}
                )
            else:
                cevap_metni = f"🔍 {aciklama}.\n\n**{len(df)}** kayit bulundu:"
                st.markdown(cevap_metni)
                st.dataframe(df, use_container_width=True, hide_index=True)
                with st.expander("Calistirilan SQL sorgusunu goster"):
                    st.code(sql, language="sql")

                st.session_state.chat_gecmisi.append(
                    {"rol": "assistant", "icerik": cevap_metni, "df": df, "sql": sql}
                )

        except Exception as e:
            hata_metni = f"❌ Beklenmeyen bir hata olustu: {e}"
            st.error(hata_metni)
            st.session_state.chat_gecmisi.append(
                {"rol": "assistant", "icerik": hata_metni, "df": None, "sql": None}
            )

st.divider()
if st.button("🗑️ Sohbet Gecmisini Temizle"):
    st.session_state.chat_gecmisi = []
    st.rerun()

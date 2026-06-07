# -*- coding: utf-8 -*-
# DIS TICARET KARAR DESTEK SISTEMI
# Linear Cebir Donem Projesi
# 1. Sinif

from flask import Flask, render_template, request
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import random

# ============================================================
# VERI OLUSTURMA
# ============================================================

random.seed(100)
np.random.seed(100)

ulkeler = ["Almanya", "ABD", "Ingiltere", "Italya", "Fransa",
           "Rusya", "Cin", "BAE", "Irak", "Ispanya"]

urunler = ["Otomotiv", "Makina", "Kimyasal", "Elektronik",
           "Tekstil", "Gida", "Celik", "Plastik"]

yillar = list(range(2015, 2026))

# ihracat icin her ulkenin baz degerleri (milyon dolar)
ihracat_baz = {
    "Almanya": 18000, "ABD": 14000, "Ingiltere": 13000,
    "Italya": 11000, "Fransa": 10000, "Rusya": 7000,
    "Cin": 5500, "BAE": 8000, "Irak": 12000, "Ispanya": 7500
}

# ithalat icin her ulkenin baz degerleri
ithalat_baz = {
    "Almanya": 22000, "ABD": 18000, "Ingiltere": 11000,
    "Italya": 14000, "Fransa": 12000, "Rusya": 28000,
    "Cin": 35000, "BAE": 8000, "Irak": 5000, "Ispanya": 8000
}

def veri_olustur():
    """2015-2025 arasi ihracat ve ithalat verilerini olustur"""
    ihracat_verisi = []
    ithalat_verisi = []

    for yil in yillar:
        # her yil icin kucuk bir buyume katsayisi
        katsayi = 1 + (yil - 2015) * 0.035

        for ulke in ulkeler:
            # ihracat
            ihra = ihracat_baz[ulke] * katsayi * random.uniform(0.85, 1.15)
            ihracat_verisi.append([yil, ulke, round(ihra, 1)])

            # ithalat
            ithal = ithalat_baz[ulke] * katsayi * random.uniform(0.85, 1.15)
            ithalat_verisi.append([yil, ulke, round(ithal, 1)])

    return ihracat_verisi, ithalat_verisi

def urun_verisi_olustur():
    """urun kategorilerine gore veri"""
    urun_veri = []
    for yil in yillar:
        for urun in urunler:
            ihra = random.uniform(3000, 20000) * (1 + (yil - 2015) * 0.025)
            ithal = random.uniform(4000, 25000) * (1 + (yil - 2015) * 0.02)
            urun_veri.append([yil, urun, round(ihra, 1), round(ithal, 1)])
    return urun_veri

# verileri olustur
ihracat_liste, ithalat_liste = veri_olustur()
urun_liste = urun_verisi_olustur()

# dataframe'e cevir
df_ihracat = pd.DataFrame(ihracat_liste, columns=["Yil", "Ulke", "Ihracat"])
df_ithalat = pd.DataFrame(ithalat_liste, columns=["Yil", "Ulke", "Ithalat"])
df_urun = pd.DataFrame(urun_liste, columns=["Yil", "Urun", "Ihracat", "Ithalat"])

# ============================================================
# 1. LINEER CEBIR : MATRIS OLUSTURMA
# ============================================================

def matris_olustur(df, sutun_adi):
    """ulkeler ve yillara gore matris olustur"""
    ulke_list = sorted(df["Ulke"].unique())
    yil_list = sorted(df["Yil"].unique())
    matris = np.zeros((len(ulke_list), len(yil_list)))

    for i, ulke in enumerate(ulke_list):
        for j, yil in enumerate(yil_list):
            satir = df[(df["Ulke"] == ulke) & (df["Yil"] == yil)]
            if len(satir) > 0:
                matris[i, j] = satir[sutun_adi].values[0]
    return matris, ulke_list, yil_list

# matrisleri olustur
ihracat_matrisi, ulkeler_sira, yillar_sira = matris_olustur(df_ihracat, "Ihracat")
ithalat_matrisi, _, _ = matris_olustur(df_ithalat, "Ithalat")

# ============================================================
# 2. LINEER CEBIR : MATRIS CARPIMI
# ============================================================

def ticaret_hacmi_hesapla(ihr_mat, ith_mat):
    """matris carpimi ile ticaret hacmini hesapla"""
    # agirlik matrisi (her ulkenin toplam ticarete katkisi)
    toplam_ihracat = np.sum(ihr_mat, axis=1)
    toplam_ithalat = np.sum(ith_mat, axis=1)
    # matris carpimi ile agirliklandirilmis hacim
    hacim = np.dot(toplam_ihracat, toplam_ithalat)
    return hacim

# ============================================================
# 3. LINEER CEBIR : KORELASYON MATRISI
# ============================================================

def korelasyon_hesapla():
    """degiskenler arasi korelasyonu hesapla"""
    yillik_toplam = df_ihracat.groupby("Yil")["Ihracat"].sum().reset_index()
    yillik_ithalat = df_ithalat.groupby("Yil")["Ithalat"].sum().reset_index()

    yillik_toplam = yillik_toplam.merge(yillik_ithalat, on="Yil")
    yillik_toplam["Denge"] = yillik_toplam["Ihracat"] - yillik_toplam["Ithalat"]
    yillik_toplam["Hacim"] = yillik_toplam["Ihracat"] + yillik_toplam["Ithalat"]

    # USD kuru ve enflasyon (basit degerler)
    usd_kur = [2.7, 3.0, 3.5, 4.8, 5.7, 6.8, 8.0, 13.0, 19.0, 23.0, 29.0]
    enflasyon = [7.7, 8.5, 11.9, 16.3, 20.3, 12.8, 19.6, 72.3, 64.8, 53.4, 44.0]

    yillik_toplam["USD_Kur"] = usd_kur
    yillik_toplam["Enflasyon"] = enflasyon

    # korelasyon matrisini hesapla
    sayisal_veri = yillik_toplam[["Ihracat", "Ithalat", "Denge", "Hacim", "USD_Kur", "Enflasyon"]]
    korelasyon = sayisal_veri.corr()

    return yillik_toplam, korelasyon

yillik_veri, korelasyon_mt = korelasyon_hesapla()

# ============================================================
# GRAFIK OLUSTURMA
# ============================================================

def grafik_kaydet(fig, dosya_adi):
    """grafikleri kaydet"""
    os.makedirs("static", exist_ok=True)
    yol = os.path.join("static", dosya_adi)
    fig.savefig(yol, dpi=150)
    plt.close(fig)

def ihracat_grafigi():
    """ihracat trend grafigi"""
    fig, ax = plt.subplots(figsize=(10, 5))
    yillik = df_ihracat.groupby("Yil")["Ihracat"].sum()
    ax.plot(yillik.index, yillik.values, "b-o", linewidth=2, label="Ihracat")
    ax.set_title("Turkiye Ihracat Trendi (2015-2025)", fontsize=14)
    ax.set_xlabel("Yil")
    ax.set_ylabel("Milyon Dolar")
    ax.grid(True, alpha=0.3)
    ax.legend()
    grafik_kaydet(fig, "ihracat_trend.png")

def ithalat_grafigi():
    """ithalat trend grafigi"""
    fig, ax = plt.subplots(figsize=(10, 5))
    yillik = df_ithalat.groupby("Yil")["Ithalat"].sum()
    ax.plot(yillik.index, yillik.values, "r-s", linewidth=2, label="Ithalat")
    ax.set_title("Turkiye Ithalat Trendi (2015-2025)", fontsize=14)
    ax.set_xlabel("Yil")
    ax.set_ylabel("Milyon Dolar")
    ax.grid(True, alpha=0.3)
    ax.legend()
    grafik_kaydet(fig, "ithalat_trend.png")

def denge_grafigi():
    """ticaret dengesi grafigi"""
    fig, ax = plt.subplots(figsize=(10, 5))
    renkler = ["green" if d > 0 else "red" for d in yillik_veri["Denge"]]
    ax.bar(yillik_veri["Yil"], yillik_veri["Denge"], color=renkler, width=0.6)
    ax.axhline(y=0, color="black", linewidth=1)
    ax.set_title("Turkiye Ticaret Dengesi (2015-2025)", fontsize=14)
    ax.set_xlabel("Yil")
    ax.set_ylabel("Milyon Dolar")
    ax.grid(True, alpha=0.3, axis="y")
    grafik_kaydet(fig, "ticaret_dengesi.png")

def korelasyon_grafigi():
    """korelasyon isi haritasi (basit)"""
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(korelasyon_mt.values, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(korelasyon_mt.columns)))
    ax.set_yticks(range(len(korelasyon_mt.columns)))
    ax.set_xticklabels(korelasyon_mt.columns, rotation=45, ha="right", fontsize=8)
    ax.set_yticklabels(korelasyon_mt.columns, fontsize=8)
    for i in range(len(korelasyon_mt.columns)):
        for j in range(len(korelasyon_mt.columns)):
            ax.text(j, i, f"{korelasyon_mt.values[i,j]:.2f}",
                   ha="center", va="center", fontsize=7)
    ax.set_title("Korelasyon Matrisi", fontsize=14)
    fig.colorbar(im, ax=ax, shrink=0.8)
    grafik_kaydet(fig, "korelasyon.png")

# grafikleri olustur
ihracat_grafigi()
ithalat_grafigi()
denge_grafigi()
korelasyon_grafigi()

# ============================================================
# KARAR DESTEK FONKSIYONLARI
# ============================================================

ulke_risk = {
    "Almanya": 0.15, "ABD": 0.20, "Ingiltere": 0.25,
    "Italya": 0.20, "Fransa": 0.20, "Rusya": 0.65,
    "Cin": 0.40, "BAE": 0.35, "Irak": 0.70, "Ispanya": 0.25
}

urun_risk = {
    "Otomotiv": 0.35, "Makina": 0.30, "Kimyasal": 0.40,
    "Elektronik": 0.45, "Tekstil": 0.25, "Gida": 0.20,
    "Celik": 0.50, "Plastik": 0.30
}

def analiz_yap(ulke, urun):
    """kullanici icin ticaret analizi yap"""
    # ulke verilerini al
    u_ihracat = df_ihracat[df_ihracat["Ulke"] == ulke]["Ihracat"].values
    u_ithalat = df_ithalat[df_ithalat["Ulke"] == ulke]["Ithalat"].values

    if len(u_ihracat) == 0:
        return None

    # son degerler
    son_ihracat = u_ihracat[-1]
    son_ithalat = u_ithalat[-1]

    # buyume orani (basit)
    ilk_ihracat = u_ihracat[0]
    buyume = ((son_ihracat - ilk_ihracat) / ilk_ihracat) * 100

    # urun payi
    urun_satir = df_urun[(df_urun["Urun"] == urun) & (df_urun["Yil"] == 2024)]
    if len(urun_satir) > 0:
        urun_payi = urun_satir["Ihracat"].values[0] / df_urun[df_urun["Yil"] == 2024]["Ihracat"].sum() * 100
    else:
        urun_payi = 12.5

    # potansiyel hesapla
    potansiyel = son_ihracat * (1 + buyume / 100 / 10) * (urun_payi / 100)

    # risk skoru
    risk = (ulke_risk.get(ulke, 0.5) * 0.6 + urun_risk.get(urun, 0.3) * 0.4) * 100

    # risk seviyesi
    if risk < 30:
        risk_sev = "Dusuk"
        risk_cls = "green"
    elif risk < 55:
        risk_sev = "Orta"
        risk_cls = "orange"
    else:
        risk_sev = "Yuksek"
        risk_cls = "red"

    # oneriler
    oneriler = []
    if risk < 30:
        oneriler.append("Bu ulke-urun kombinasyonu dusuk risklidir.")
        oneriler.append("Pazarlama yatirimlarini artirabilirsiniz.")
    elif risk < 55:
        oneriler.append("Orta risk seviyesi, dikkatli olunmali.")
        oneriler.append("Pazar arastirmasi yapmaniz tavsiye edilir.")
    else:
        oneriler.append("Yuksek risk! Temkinli olunmali.")
        oneriler.append("Ticari sigorta kullanmaniz onerilir.")

    if buyume > 0:
        oneriler.append("Ihracat trendi pozitif, mevcut ivmeyi koruyun.")
    else:
        oneriler.append("Ihracat trendi negatif, strateji revize edilmeli.")

    return {
        "ulke": ulke,
        "urun": urun,
        "son_ihracat": round(son_ihracat, 0),
        "son_ithalat": round(son_ithalat, 0),
        "buyume_orani": round(buyume, 1),
        "potansiyel": round(potansiyel, 0),
        "urun_payi": round(urun_payi, 1),
        "risk_skoru": round(risk, 1),
        "risk_seviye": risk_sev,
        "risk_class": risk_cls,
        "oneriler": oneriler
    }

# ============================================================
# FLAST UYGULAMASI
# ============================================================

app = Flask(__name__)

@app.route("/")
def ana_sayfa():
    """ana sayfa"""
    # son yil istatistikleri
    son_yil = yillik_veri.iloc[-1]
    onceki_yil = yillik_veri.iloc[-2]

    ihracat_degisim = ((son_yil["Ihracat"] - onceki_yil["Ihracat"]) / onceki_yil["Ihracat"]) * 100
    ithalat_degisim = ((son_yil["Ithalat"] - onceki_yil["Ithalat"]) / onceki_yil["Ithalat"]) * 100

    istatistik = {
        "son_yil": int(son_yil["Yil"]),
        "toplam_ihracat": round(son_yil["Ihracat"], 0),
        "toplam_ithalat": round(son_yil["Ithalat"], 0),
        "ticaret_dengesi": round(son_yil["Denge"], 0),
        "ticaret_hacmi": round(son_yil["Hacim"], 0),
        "ihracat_degisim": round(ihracat_degisim, 1),
        "ithalat_degisim": round(ithalat_degisim, 1)
    }
    return render_template("ana.html", istatistik=istatistik)

@app.route("/analiz")
def analiz_sayfasi():
    """veri analizi sayfasi"""
    # yillik toplamlar
    yillik = df_ihracat.groupby("Yil")["Ihracat"].sum().reset_index()
    yillik2 = df_ithalat.groupby("Yil")["Ithalat"].sum().reset_index()
    yillik = yillik.merge(yillik2, on="Yil")
    yillik["Denge"] = yillik["Ihracat"] - yillik["Ithalat"]
    yillik["Hacim"] = yillik["Ihracat"] + yillik["Ithalat"]

    # ulke siralamasi
    son_yil_ihracat = df_ihracat[df_ihracat["Yil"] == 2024].sort_values("Ihracat", ascending=False)
    son_yil_ithalat = df_ithalat[df_ithalat["Yil"] == 2024].sort_values("Ithalat", ascending=False)

    # urun verisi
    urun_2024 = df_urun[df_urun["Yil"] == 2024].sort_values("Ihracat", ascending=False)

    return render_template("analiz.html",
                         yillik=yillik.to_dict("records"),
                         ihracat_sira=son_yil_ihracat.to_dict("records"),
                         ithalat_sira=son_yil_ithalat.to_dict("records"),
                         urunler=urun_2024.to_dict("records"))

@app.route("/karar", methods=["GET", "POST"])
def karar_sayfasi():
    """karar destek sayfasi"""
    sonuc = None
    if request.method == "POST":
        ulke = request.form.get("ulke")
        urun = request.form.get("urun")
        if ulke and urun:
            sonuc = analiz_yap(ulke, urun)

    return render_template("karar.html", ulkeler=ulkeler, urunler=urunler, sonuc=sonuc)

@app.route("/sonuc")
def sonuc_sayfasi():
    """sonuclar sayfasi"""
    # korelasyon degerlerini tablo icin hazirla
    korelasyon_liste = []
    for i in range(len(korelasyon_mt.columns)):
        for j in range(i+1, len(korelasyon_mt.columns)):
            korelasyon_liste.append({
                "degisken1": korelasyon_mt.columns[i],
                "degisken2": korelasyon_mt.columns[j],
                "deger": round(korelasyon_mt.values[i, j], 3)
            })

    # matris carpimi sonucu
    hacim_sonuc = ticaret_hacmi_hesapla(ihracat_matrisi, ithalat_matrisi)

    return render_template("sonuc.html",
                         korelasyon=korelasyon_liste,
                         matris_sonuc=round(hacim_sonuc, 0))

if __name__ == "__main__":
    print("=" * 40)
    print("DIS TICARET KARAR DESTEK SISTEMI")
    print("1. Sinif Linear Cebir Projesi")
    print("=" * 40)
    print("http://localhost:5001")
    app.run(debug=True, port=5001)

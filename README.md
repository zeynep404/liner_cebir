# Dış Ticaret Karar Destek Sistemi

Bu proje 1. sınıf **Lineer Cebir** dersi için yapılmıştır. Türkiye'nin 2015-2025 yılları arasındaki dış ticaret verilerini analiz eden bir Flask web uygulamasıdır.

## Ne İşe Yarar?

- İhracat ve ithalat verilerini tablo ve grafiklerle gösterir
- Lineer cebir yöntemleriyle ticaret hacmi hesaplar
- Ülke ve ürün bazında risk analizi yapar
- Kullanıcıya stratejik öneriler sunar

## Kullanılan Lineer Cebir Yöntemleri

1. **Matris Oluşturma** – Ülkeler ve yıllara göre 10×11 boyutunda ihracat/ithalat matrisleri
2. **Matris Çarpımı** – Ağırlıklandırılmış ticaret hacmi hesaplama
3. **Korelasyon Analizi** – Değişkenler arası ilişkilerin incelenmesi

## Nasıl Çalıştırılır?

```bash
pip install -r requirements.txt
python app.py
```

Veya `calistir.bat` dosyasına çift tıklayarak da çalıştırabilirsiniz.

## Sayfalar

- **Ana Sayfa** – Genel istatistikler ve grafikler
- **Veri Analizi** – Yıllık veriler ve ülke sıralamaları
- **Karar Destek** – Ülke + ürün seçip risk analizi yapma
- **Sonuçlar** – Matris çarpımı ve korelasyon analizi sonuçları

## Kullanılan Kütüphaneler

- Flask (web arayüzü)
- Pandas (veri işleme)
- NumPy (matris işlemleri)
- Matplotlib (grafikler)

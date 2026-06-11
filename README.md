# İstanbul Yıldız Akademi — Yönetim Sistemi

## Yarın Yapılacaklar (15-20 dakika)

### 1. GitHub Hesabı Aç
- github.com → Sign up → Ücretsiz hesap aç

### 2. Yeni Repository Oluştur
- GitHub'da "New repository" → İsim: `akademi-app` → Public → Create

### 3. Dosyaları Yükle
Repository sayfasında "uploading an existing file" linkine tıkla.
Bu klasördeki TÜM dosyaları sürükle-bırak yap:
- app.py
- requirements.txt
- Procfile
- .gitignore
- templates/ klasörü (içindeki index.html ile birlikte)

"Commit changes" butonuna bas.

### 4. Render.com Hesabı Aç
- render.com → Sign up → GitHub ile giriş yap (aynı hesap)

### 5. Web Service Oluştur
- "New +" → "Web Service"
- GitHub reposunu seç: `akademi-app`
- Ayarlar:
  - **Name:** yildiz-akademi
  - **Runtime:** Python 3
  - **Build Command:** `pip install -r requirements.txt`
  - **Start Command:** `gunicorn app:app`
  - **Plan:** Free

### 6. PostgreSQL Veritabanı Ekle
- Render dashboard → "New +" → "PostgreSQL"
- **Name:** akademi-db
- **Plan:** Free
- Oluştur → "Internal Database URL"yi kopyala

### 7. Ortam Değişkeni Ekle
- Web Service ayarları → "Environment"
- Key: `DATABASE_URL`
- Value: kopyaladığın URL

### 8. Deploy Et
- "Deploy" butonuna bas → 2-3 dakika bekle
- Sana `https://yildiz-akademi.onrender.com` gibi bir URL verilecek
- Bu URL'yi her cihazdan açabilirsin!

---

## Notlar
- Render'ın ücretsiz planında uygulama 15 dakika aktif değilse uyur, ilk açılışta 30 saniye bekleyebilirsin.
- Veriler PostgreSQL'de kalıcı olarak tutulur.
- İstersen özel domain bağlanabilir (opsiyonel).

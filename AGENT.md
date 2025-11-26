# AGENT.md

## Proje Genel Bakış

Bu proje, yerel yapay zeka sunucularıyla (Ollama, LM Studio) etkileşim kuran Türkçe bir Streamlit sohbet uygulamasıdır. Vektör veritabanı tabanlı akıllı önbellekleme sistemi ile performansı optimize eder.

## Proje Yapısı

```
C_Notlar/
├── app.py              # Ana Streamlit uygulaması
├── vector_db.py         # Vektör veritabanı işlemleri
├── constants.py         # Sabit değişkenler ve yollar
├── configs.json         # Sunucu ve model yapılandırmaları
├── prompt.aitk.txt      # Sistem prompt'u
├── requirements.txt     # Python bağımlılıkları
├── feedback.log         # Geri bildirim kayıtları
├── data/               # Vektör veritabanı dosyaları
│   └── vector_cache.index
└── README.md           # Proje dokümantasyonu
```

## Temel Özellikler

### 1. Dinamik Model ve Sunucu Yönetimi
- `configs.json` üzerinden çoklu sunucu ve model desteği
- Runtime'da model değiştirme imkanı
- Farklı endpoint'ler arasında geçiş

### 2. Akıllı Önbellekleme Sistemi
- **FAISS** vektör veritabanı kullanımı
- **SentenceTransformer** (`all-MiniLM-L6-v2`) embedding modeli
- Anlamsal benzerlik araması ile cache hit optimizasyonu
- Beğenilen yanıtların otomatik önbelleğe alınması

### 3. Geri Bildirim Mekanizması
- 👍/👎 emoji ile yanıt değerlendirme
- `feedback.log` dosyasına detaylı kayıt
- Önbellek kalitesi için kullanıcı geri bildirimleri

### 4. Sohbet Geçmişi Yönetimi
- JSON formatında dışa/içe aktarma
- Oturum devam ettirme özelliği
- Konuşma geçmişinin korunması

## Kritik Fonksiyonlar

### `app.py:14` - `chat()`
LLM sunucusuna istek gönderir, yanıtı işler ve hata yönetimi yapar.

### `vector_db.py:24` - `create_vector_db_from_feedback()`
Geri bildirim log'undan vektör veritabanı oluşturur.

### `vector_db.py` - `search_cache()`
Anlamsal benzerlik araması ile önbellekten sonuç getirir.

## Geliştirme Kuralları

### Kod Standartları
- **Dil**: Türkçe yorumlar ve değişken isimleri
- **Style**: PEP 8 uyumlu Python kodu
- **Error Handling**: Try-catch blokları ile sağlam hata yönetimi
- **Logging**: `feedback.log` için özel logger yapılandırması

### Dosya Düzeni
- **Yapılandırma**: `configs.json` üzerinden yönetilir
- **Sabitler**: `constants.py` dosyasında toplanır
- **Veri Yolları**: `DATA_DIR` altında organize edilir

### Performans İyileştirmeleri
- `@st.cache_resource` ile embedding model önbellekleme
- Asenkron istekler için `aiohttp` önerisi (todo listesinde)
- Model listesi önbellekleme (gelecek plan)

## Test Stratejisi

### Birim Testleri
- `chat()` fonksiyonu için mock API testleri
- `search_cache()` için vektör benzerlik testleri
- Geri bildirim mekanizması testleri

### Entegrasyon Testleri
- Tam sohbet akışı testleri
- Vektör veritabanı entegrasyonu
- Dosya içe/dışa aktarma işlemleri

## Güvenlik ve Best Practices

### API Güvenliği
- Endpoint validation
- Hata mesajlarında bilgi sızıntısını önleme
- Rate limiting (öneri)

### Veri Yönetimi
- `feedback.log` rotation
- Vektör veritabanı boyut limitleri
- Hassas verilerin loglanmaması

## Dağıtım

### Lokal Geliştirme
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Konteynerleştirme (Gelecek Plan)
- Dockerfile oluşturma
- Multi-stage build optimizasyonu
- Environment variable yönetimi

## İyileştirme Öncelikleri

### Yüksek Öncelik
1. Asenkron API istekleri
2. Önbellek hit rate istatistikleri
3. Tema seçimi (dark/light mode)

### Orta Öncelik
1. Sohbet içinde arama özelliği
2. Kod blokları için syntax highlighting
3. Birim testleri implementasyonu

### Düşük Öncelik
1. Docker konteynerleştirme
2. Multi-prompt desteği
3. Otomatik tamamlama özellikleri

## Hata Ayıklama

### Log Dosyaları
- `feedback.log`: Geri bildirim ve önbellek etkileşimleri
- Streamlit logları: Uygulama hataları

### Yaygın Sorunlar
- **Bağlantı Hataları**: `configs.json` endpoint kontrolü
- **Önbellek Sorunları**: `data/vector_cache.index` dosyası kontrolü
- **Model Hataları**: Sunucudaki model可用性 kontrolü
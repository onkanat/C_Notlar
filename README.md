markdown# Basit Sohbet Arayüzü

Bu Streamlit uygulaması, Ollama veya LM Studio gibi yerel yapay zeka sunucularıyla etkileşim kurmak için basit bir sohbet arayüzü sağlar. Uygulama, sık sorulan sorular için bir önbellekleme mekanizması ve oturumları yönetmek için sohbet geçmişini içe/dışa aktarma gibi özellikler içerir.

## Özellikler

- **Dinamik Model ve Sunucu Seçimi**: Arayüz üzerinden farklı yapay zeka modelleri ve sunucu endpoint'leri arasında geçiş yapma imkanı.
- **Vektör Veritabanı ile Akıllı Önbellekleme**:
    - Kullanıcılar tarafından "beğenilen" yanıtlar, bir vektör veritabanında saklanır.
    - Yeni bir soru sorulduğunda, bu veritabanında anlamsal olarak benzer bir soru aranır.
    - Yüksek benzerlikte bir eşleşme bulunursa, yanıt doğrudan önbellekten sunularak API maliyetlerinden ve zamandan tasarruf edilir.
- **Geri Bildirim Mekanizması**:
    - Modelden gelen yanıtlara "Beğen" (👍) veya "Beğenme" (👎) ile geri bildirim verilebilir.
    - Önbellekten gelen yanıtların yardımcı olup olmadığı "Evet" veya "Hayır" ile belirtilebilir.
    - Tüm geri bildirimler `feedback.log` dosyasına kaydedilir ve "beğenilen" yanıtlar vektör veritabanını eğitmek için kullanılır.
- **Sohbet Geçmişi Yönetimi**:
    - **Dışa Aktarma**: Mevcut sohbet geçmişi, kenar çubuğundaki "Sohbet Geçmişini İndir (JSON)" butonu ile bir JSON dosyası olarak indirilebilir.
    - **İçe Aktarma**: Daha önce kaydedilmiş bir sohbet oturumu, "Sohbet Geçmişini Yükle (JSON)" özelliği kullanılarak geri yüklenebilir. Bu sayede kullanıcılar sohbetlerine kaldıkları yerden devam edebilirler.

## Kurulum ve Çalıştırma

1.  Gerekli Python kütüphanelerini yükleyin:
    ```bash
    pip install -r requirements.txt
    ```
2.  `configs.json` dosyasını kendi yerel sunucu yapılandırmanıza göre düzenleyin.
3.  Uygulamayı çalıştırın:
    ```bash
    streamlit run app.py
    ```

---

## Geliştirme ve Optimizasyon Fikirleri (Todo List)

Bu liste, projenin gelecekteki gelişim yönünü ve potansiyel iyileştirmeleri özetlemektedir.

### 1. Akıllı Önbellek Yönetimi
- **Otomatik Silme**: Önbellekten gelen ve kullanıcı tarafından "Hayır" (yardımcı olmadı) olarak oylanan yanıtları vektör veritabanından otomatik olarak silen bir mekanizma.
- **İstatistikler**: Önbellek isabet oranını (cache hit rate) izleme ve bu istatistiği arayüzde gösterme.
- **Yaşam Süresi (TTL)**: Önbellek girişlerine bir "yaşam süresi" (Time To Live) ekleyerek eski kayıtların belirli bir süre sonra otomatik olarak güncellenmesini sağlama.

### 2. Arayüz ve Kullanıcı Deneyimi (UI/UX)
- **Tema Seçimi**: Kullanıcının açık ve koyu mod arasında geçiş yapabilmesi için bir tema seçeneği ekleme.
- **Sohbette Arama**: Sohbet geçmişi içinde metin tabanlı arama yapma özelliği.
- **Gelişmiş Kod Görünümü**: Yanıtlar içindeki kod blokları için otomatik olarak sözdizimi vurgulama (syntax highlighting) ve bloğa özel kopyalama butonu ekleme.
- **Otomatik Tamamlama**: Model ve sunucu seçimi gibi alanlarda otomatik tamamlama özelliği.

### 3. Yapılandırma ve Esneklik
- **Arayüzden Yönetim**: `configs.json` ve `prompt.aitk.txt` dosyalarının içeriğini doğrudan Streamlit arayüzü üzerinden düzenleme imkanı.
- **Çoklu Prompt Desteği**: Farklı sistem prompt'ları arasında kolayca geçiş yapabilme.

### 4. Performans ve Ağ
- **Asenkron İstekler**: `requests` yerine `aiohttp` gibi bir kütüphane kullanarak API isteklerini asenkron hale getirme.
- **Model Listesini Önbelleğe Alma**: Sunuculardan alınan model listesini belirli bir süre önbelleğe alarak gereksiz API çağrılarını azaltma.

### 5. Test ve Güvenilirlik
- **Birim Testleri (Unit Tests)**: `pytest` kullanarak `chat`, `search_cache` gibi kritik fonksiyonlar için test senaryoları yazma.
- **Entegrasyon Testleri**: API ile iletişimi ve veritabanı işlemlerini bütünsel olarak test etme.

### 6. Dağıtım ve Bakım
- **Konteynerleştirme**: Uygulamayı ve bağımlılıklarını bir `Dockerfile` ile paketleyerek dağıtımı ve çalıştırmayı kolaylaştırma.

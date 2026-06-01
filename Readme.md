# Yakınskop: Türkiye Ulusal Gözlemevleri Teleskoplarını Yakından ve Daha Detaylı Tanıtan Chatbot Arayüzü

**Yakınskop**, Türkiye Ulusal Gözlemevleri sitesinde bulunan altı adet teleskop sayfasındaki teknik verileri (https://trgozlemevleri.gov.tr/) toplumun her kesimine (7'den 77'ye) anlaşılır, kaliteli ve bilimsel doğruluktan ödün vermeden aktarmayı amaçlayan yapay zeka destekli bir interaktif sohbet (chatbot) arayüz (dashboard) projesidir.

Proje, teknik ve toplumun büyük bir bölümü için soyut olabilecek verileri (okuma gürültüleri, piksel ölçekleri, dalga cephesi hataları vb.) kullanıcının yaş ve eğitim gibi arka plan bilgisine göre dinamik olarak hikayeleştiren bir **Context-Injection RAG (Retrieval-Augmented Generation)** mimarisine sahiptir.

Yakınskop arayüzünden bir görünüm:

![Yakınskop Arayüz Görünümü](demo-foto/Ekran%20görüntüsü%202026-05-28%20110634.png)

---
## Kurulum

  Test etmek için adım adım, proje dizini local'e klonlandıktan sonra, proje yolunda çalıştırılması komutlar:

  pip install -r requirements.txt

  Ardından .env dosyasına gerçek API key'ini yaz (https://aistudio.google.com/ adresinden alınmaktadır.):
  GEMINI_API_KEY="senin_gercek_api_keyin"
  
  Sonra çalıştır:
  python server.py

---
## 🚀 Öne Çıkan Özellikler

* **Persona-Adaptive Mutation (Profil Tabanlı Uyarlanabilir Anlatım):** Kullanıcı onboarding ekranında yaşını ve eğitim durumunu seçer. Sistem prompt katmanı bu verilere göre anlık mutasyona uğrayarak; bir ilkokul öğrencisine yapısal ölçeklerle, bir mühendislik öğrencisine ise doğrudan temel fizik ilkeleriyle (First-Principles) açıklama yapar.
* **Context-Injection RAG:** Büyük ve maliyetli Vector DB/Embedding süreçleri yerine, teleskopların tüm teknik speşlerini içeren statik Markdown dosyalarını Gemini API'nin geniş bağlam penceresine doğrudan "bağlam" olarak enjekte eder. %100 deterministik ve sapmasız (hallucination-free) çalışır.
* **Elit ve Gerçekçi Dil Sınırı:** Anlatımlarda çocuksu, abartılı veya gerçek dışı analojiler kesinlikle kullanılmaz. Tüm açıklamalar akademik kalitede, popüler bilim çizgisine uygun ve fiziksel gerçekliklere dayalıdır.
* **Ekosistem Karşılaştırma Modülü:** Ulusal teleskopların birbirleriyle olan teknik farklarını ve uluslararası gözlemevleri karşısındaki stratejik önemini yapısal olarak analiz eder.

---

## 📂 Proje Dizini Yapısı

```text
Yakınskop/
├── data/                   # Teleskop verileri (Markdown + görseller)
│   ├── antalya/
│   │   ├── rtt150.md/.avif # RTT150 teleskop ve odak düzlem verileri
│   │   ├── tug100.md/.avif # TUG T100 teleskop verileri
│   │   └── tug060.md/.avif # TUG T060 teleskop ve Andor iKon-L 936 kamera speşleri
│   └── erzurum/
│       ├── dag400.md/.avif # DAG400 teleskop, KORAY, DIRAC, TROIA, PLACID, DAGOS özellikleri
│       ├── ata050.md/.avif # ATA050 robotik teleskop verileri
│       └── dagtps.md/.avif # DAG TPS donanım verileri
├── server.py               # Flask backend (API rotaları ve şablon sunucusu)
├── rag_engine.py           # Gemini API (google-genai SDK) entegrasyonu ve Context-Injection RAG motoru
├── templates/
│   └── index.html          # Ana arayüz şablonu (sidebar, içerik alanı, sohbet paneli)
├── static/
│   ├── app.js              # Frontend JavaScript (API çağrıları, etkileşim mantığı)
│   └── style.css           # Arayüz stilleri
├── .env                    # API anahtarı (GEMINI_API_KEY)
└── requirements.txt        # Bağımlılıklar (flask, google-genai, python-dotenv)

# 🎯 BL4S 2026: Jüriye Söylenecek Kilit Cümleler ve Soru-Cevap Rehberi
# (CERN Jury Key Phrases & Q&A Cheat Sheet - Turkish & English)

Bu doküman, CERN BL4S jürisi karşısında hem sunum sırasında hem de sunum sonrasındaki soru-cevap (Q&A) bölümünde kullanabileceğiniz **en kritik teknik cümleleri**, **savunma argümanlarını** ve **Türkçe/İngilizce karşılıklarını** içerir.

---

## 📑 İçindekiler
1. [Giriş ve Proje Özeti (Opening & Overview)](#1-giriş-ve-proje-özeti)
2. [SSH Tünelleri ve Güvenlik (Why SSH Tunnels?)](#2-ssh-tünelleri-ve-güvenlik)
3. [TDAQ ve Polling Trigger Mimarisi (Trigger & Polling)](#3-tdaq-ve-polling-trigger-mimarisi)
4. [Simülasyondan Gerçek C++ Donanıma Geçiş (Transition to Real Beam)](#4-simülasyondan-gerçek-c-donanıma-geçiş)
5. [CAEN SY5527 ve Web GECO Sistemi (High Voltage Slow Control)](#5-caen-sy5527-ve-web-geco-sistemi)
6. [Machine Learning ve Gerçek Zamanlı Rekonstrüksiyon (AI & Reconstruction)](#6-machine-learning-ve-gerçek-zamanlı-rekonstrüksiyon)
7. [Kapanış ve Teşekkür (Closing)](#7-kapanış-ve-teşekkür)

---

## 1. Giriş ve Proje Özeti

### 🇹🇷 Türkçe:
> "Merhaba, ben Kayra Yavuz. Team PionIST 3 adına, CERN PS East Area T9 hüzme hattındaki nötr pion ($\pi^0 \to \gamma\gamma$) bozunumu deneyimiz için geliştirdiğimiz uçtan uca Constellation DAQ ve gerçek zamanlı gözlemlenebilirlik (observability) sistemimizi sunmaktan gurur duyuyorum."

### 🇬🇧 English:
> *"Good day, I am Kayra Yavuz. On behalf of Team PionIST 3, I am proud to present our end-to-end Constellation DAQ and real-time observability framework, engineered specifically for our neutral pion decay ($\pi^0 \to \gamma\gamma$) experiment at the CERN PS East Area T9 beamline."*

---

## 2. SSH Tünelleri ve Güvenlik

### ❓ Olası Jüri Sorusu:
* **TR:** *"Neden Kafka ve arayüz için SSH tünelleri kullandınız?"*
* **EN:** *"Why did you use SSH tunnels for Kafka and your monitoring stack?"*

### 🇹🇷 Türkçe Cevap:
> "Gerçek zamanlı izleme sistemimizi kritik Constellation DAQ sisteminden ayırmak (decouple) ve CERN güvenlik duvarı kurallarına tam uyum sağlamak için SSH tünelleri kullanıyoruz. Bu sayede uzaktan izleme bağlantımız kopsa bile, CERN'deki birincil ZeroMQ veri alımı ve diske HDF5 yazımı bundan kesinlikle etkilenmiyor ve sıfır veri kaybı yaşanıyor."

### 🇬🇧 English Answer:
> *"We use SSH tunnels to decouple our real-time observability stack from the mission-critical Constellation DAQ while strictly complying with CERN firewall security policies. This ensures that even if our remote monitoring connection drops, the primary ZeroMQ data acquisition and lossless HDF5 disk writing at CERN remain completely unaffected with zero data loss."*

---

## 3. TDAQ ve Polling Trigger Mimarisi

### ❓ Olası Jüri Sorusu:
* **TR:** *"Tetikleme (Trigger) sisteminizi nasıl modellediniz ve neden 2 uydu kullandınız?"*
* **EN:** *"How did you model your trigger system and why do you use 2 satellites?"*

### 🇹🇷 Türkçe Cevap:
> "Tetikleme mimarimizde DESY ve CERN Constellation ana geliştiricilerinin resmi `SWTRIG` telemetri standardını uyguladık. İki uydulu bir iş bölümü kurguladık: `TriggerModuleSatellite`, donanım yazmaçlarını polling ile sorgulayıp 3.5 milisaniyelik ölü zaman (dead-time veto) kapısını yönetiyor. İkinci uydumuz olan `CoincidenceEventBuilder` ise alt dedektörlerden (Kalorimetre, Timepix, Cherenkov) gelen vuruşları $\pm 10\text{ ns}$ zaman penceresinde eşleştirerek global fizik olaylarını inşa ediyor."

### 🇬🇧 English Answer:
> *"Our trigger architecture strictly adheres to the official `SWTRIG` telemetry standard developed by DESY and CERN Constellation authors. We employ a modular two-satellite design: the `TriggerModuleSatellite` polls hardware registers and manages a realistic 3.5 ms dead-time veto gate, while the `CoincidenceEventBuilder` correlates asynchronous hits across sub-detectors within a $\pm 10\text{ ns}$ timing window to assemble coherent global physics events."*

---

## 4. Simülasyondan Gerçek C++ Donanıma Geçiş

### ❓ Olası Jüri Sorusu:
* **TR:** *"CERN'e gittiğinizde mevcut C++ dedektör sürücülerinizi (VME/CAEN) bu sisteme nasıl entegre edeceksiniz?"*
* **EN:** *"When you deploy at CERN, how will you interface your existing C++ detector drivers with this system?"*

### 🇹🇷 Türkçe Cevap:
> "Sistemimiz baştan sona modüler bir 'Microservices / Satellite' mimarisiyle tasarlandı. Simülasyondan gerçek donanıma geçerken Kafka veri hattı, Protobuf şeması, Web Event Explorer veya Grafana tarafında tek bir satır kod bile değiştirmeyeceğiz. Sadece uyduların içindeki `generate_physics_event` fonksiyonuna donanımımızın C++ API çağrılarını (`libCAENVME.so` gibi) bağlamamız yeterli olacaktır."

### 🇬🇧 English Answer:
> *"Our entire system is built on a highly modular satellite architecture. When transitioning from simulation to real beamline hardware, not a single line of code needs to change in our Kafka streaming pipeline, Protobuf schema, Web Event Explorer, or Grafana dashboards. We simply link the hardware C++ API calls (such as `libCAENVME.so`) directly inside the `generate_physics_event` method of our satellites."*

---

## 5. CAEN SY5527 ve Web GECO Sistemi

### ❓ Olası Jüri Sorusu:
* **TR:** *"Dedektörlerin yüksek gerilimini (High Voltage) nasıl kontrol ediyorsunuz, harici bir programa gerek var mı?"*
* **EN:** *"How do you control detector high voltages, and do you require external standalone software?"*

### 🇹🇷 Türkçe Cevap:
> "CAEN SY5527 yüksek gerilim kasasını yönetmek için resmi `CAENHVWrapper` kütüphanesiyle haberleşen web tabanlı entegre bir GECO Slow Control paneli geliştirdik. Kontrol odasındaki herkes herhangi bir masaüstü programı kurmadan, doğrudan tarayıcıdan (`localhost:5050`) tüm kanalların voltaj ve akımlarını canlı izleyebilir, voltaj verebilir ve trip koruma durumlarını denetleyebilir."

### 🇬🇧 English Answer:
> *"To control the CAEN SY5527 High Voltage mainframe, we developed an integrated web-based GECO Slow Control interface communicating via the official `CAENHVWrapper` library. Shifters in the control room do not need standalone desktop software; any browser at `localhost:5050` allows real-time channel toggling, voltage ramping, current monitoring, and overcurrent trip safety management."*

---

## 6. Machine Learning ve Gerçek Zamanlı Rekonstrüksiyon

### ❓ Olası Jüri Sorusu:
* **TR:** *"Gerçek zamanlı Machine Learning ve rekonstrüksiyon modeliniz nasıl çalışıyor?"*
* **EN:** *"How does your real-time Machine Learning and reconstruction model operate?"*

### 🇹🇷 Türkçe Cevap:
> "Sistemimiz 7 boyutlu dedektör öznitelik vektörünü (Kalorimetre enerjisi, Cherenkov QDC, Timepix küme boyutu, ToF vb.) kullanarak 50 mikrosaniyenin altında çıkarım (inference) yapmaktadır. 6 farklı parçacık sınıfında %98.2 doğrulukla parçacık kimliği (PID) belirlemekte, Mahalanobis uzaklığı ile anomali tespiti yapmakta ve eşzamanlı olarak $\pi^0 \to \gamma\gamma$ değişmez kütlesini (invariant mass) canlı hesaplamaktadır."

### 🇬🇧 English Answer:
> *"Our Machine Learning satellite runs sub-50-microsecond inference over a 7-dimensional detector feature vector (calorimeter energy, Cherenkov QDC, Timepix cluster size, ToF, etc.). It achieves 98.2% accuracy across 6 particle classes, provides Mahalanobis-distance-based anomaly detection, and computes the $\pi^0 \to \gamma\gamma$ invariant mass spectrum live during data acquisition."*

---

## 7. Kapanış ve Teşekkür

### 🇹🇷 Türkçe:
> "Özetle; parçacık üretiminden canlı web görselleştirmesine kadar endüstri standartlarında, ölçeklenebilir ve CERN standartlarına tam uyumlu bir DAQ ve izleme ekosistemi geliştirdik. Dinlediğiniz için çok teşekkür ederim, sorularınızı yanıtlamaktan memnuniyet duyarım."

### 🇬🇧 English:
> *"In summary, we have built an industry-standard, scalable, and fully CERN-compliant DAQ and observability ecosystem from particle generation to live web visual analytics. Thank you very much for your time, and I look forward to answering any questions you may have."*

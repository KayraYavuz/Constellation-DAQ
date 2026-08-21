#!/bin/bash

# ==============================================================================
# CERN SSH Tunnel Setup Script for BL4S DAQ
# ==============================================================================
# Bu script lxplus üzerinden geçerek içerideki CERN bilgisayarına SSH tüneli kurar
# ve DAQ web sunucusunu kendi bilgisayarınıza (localhost:8080) yönlendirir.

echo "======================================================="
echo " 🌐 CERN SSH Tüneli Başlatıcı (BL4S DAQ) "
echo "======================================================="

# Kullanıcıdan bilgileri al
read -p "CERN Kullanıcı Adınız (Örn: kyavuz): " CERN_USER
if [ -z "$CERN_USER" ]; then
    echo "Hata: Kullanıcı adı boş olamaz!"
    exit 1
fi

read -p "İçerideki PC'nin Host Adı veya IP'si (Örn: pc-bl4s-01): " CERN_PC
if [ -z "$CERN_PC" ]; then
    echo "Hata: Hedef bilgisayar adı boş olamaz!"
    exit 1
fi

echo ""
echo "⏳ $CERN_PC bilgisayarına lxplus üzerinden tünel kuruluyor..."
echo "👉 Event Explorer: http://localhost:5050"
echo "👉 Grafana Paneli : http://localhost:3000"
echo "👉 DAQ Run Control: http://localhost:8080"
echo "👉 Prometheus    : http://localhost:9090"
echo "👉 Metrik Exporter: http://localhost:9100/metrics"
echo "❗️ Lütfen şifre veya 2FA (iki aşamalı doğrulama) isteklerini takip edin."
echo "Tüneli kapatmak için bu terminalde CTRL+C tuşlarına basabilirsiniz."
echo "======================================================="

# SSH tüneli komutunu çalıştır (5050: Event Explorer, 3000: Grafana, 9090: Prometheus, 9100: Metrics, 8080: Run Control)
ssh -L 5050:localhost:5050 -L 3000:localhost:3000 -L 9090:localhost:9090 -L 9100:localhost:9100 -L 8080:localhost:8080 -J ${CERN_USER}@lxplus.cern.ch ${CERN_USER}@${CERN_PC}

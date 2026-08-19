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
echo "👉 Başarılı olduğunda tarayıcınızdan http://localhost:8080 adresine girebilirsiniz."
echo "❗️ Lütfen şifre veya 2FA (iki aşamalı doğrulama) isteklerini takip edin."
echo "Tüneli kapatmak için bu terminalde CTRL+C tuşlarına basabilirsiniz."
echo "======================================================="

# SSH tüneli komutunu çalıştır
# -L 8080:localhost:8080 -> Yerel 8080 portunu hedefteki 8080'e bağlar.
# -J -> lxplus.cern.ch üzerinden atlama (jump) yapar.
ssh -L 8080:localhost:8080 -J ${CERN_USER}@lxplus.cern.ch ${CERN_USER}@${CERN_PC}

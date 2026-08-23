#!/bin/bash
echo "CERN Sunucusuna Tünel Açılıyor..."
echo "👉 Event Explorer: http://localhost:5050 (Uzaktan geliyor)"
echo "👉 Grafana Paneli: http://localhost:3000 (Lokal Docker'dan geliyor)"
echo "Tüneli kapatmak için bu terminalde CTRL+C tuşlarına basabilirsiniz."
ssh -N -L 5050:localhost:5050 -L 9100:localhost:9100 -R 9092:localhost:9092 kayra@128.141.131.221

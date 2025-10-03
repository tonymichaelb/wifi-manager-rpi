#!/bin/bash
# Script automático para instalar e rodar TUPANA Wi-Fi Manager no Raspberry Pi via SSH
# Uso: bash install-tupana-ssh.sh

set -e

# Instalar Docker
if ! command -v docker &> /dev/null; then
  echo "Instalando Docker..."
  curl -fsSL https://get.docker.com -o get-docker.sh
  sudo sh get-docker.sh
  sudo usermod -aG docker $USER
  rm get-docker.sh
  echo "Docker instalado."
else
  echo "Docker já instalado."
fi

# Instalar Docker Compose
if ! command -v docker-compose &> /dev/null; then
  echo "Instalando Docker Compose..."
  sudo apt-get update -qq
  sudo apt-get install -y python3-pip
  sudo pip3 install docker-compose
  echo "Docker Compose instalado."
else
  echo "Docker Compose já instalado."
fi

# Criar diretório do projeto
mkdir -p ~/tupana-wifi
cd ~/tupana-wifi

# Gerar docker-compose.yml
cat > docker-compose.yml <<EOF
services:
  tupana-wifi:
    image: tonymichael/wifi-manager:tupana-clean
    container_name: tupana-wifi-manager
    privileged: true
    network_mode: host
    restart: unless-stopped
    volumes:
      - /var/run/dbus:/var/run/dbus
      - /etc/wpa_supplicant:/etc/wpa_supplicant
      - /var/lib/dhcp:/var/lib/dhcp
      - /dev:/dev
    environment:
      - WIFI_INTERFACE=wlan0
      - FLASK_ENV=production
      - PYTHONUNBUFFERED=1
    ports:
      - "8080:8080"
    labels:
      - "tupana.service=wifi-manager"
      - "tupana.version=clean"
      - "tupana.description=Sistema de gerenciamento Wi-Fi para Raspberry Pi Zero 2W"
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8080/api/status || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
EOF

# Subir o serviço
echo "Subindo TUPANA Wi-Fi Manager..."
docker-compose up -d
sleep 5

echo "Status do container:"
docker ps -f name=tupana-wifi-manager

echo "Acesse a interface web em: http://$(hostname -I | awk '{print $1}'):8080"
echo "Hotspot fallback: TUPANA-WiFi-Config (senha: tupana123)"

#!/bin/bash

# Script de Deploy TUPANA Wi-Fi Manager
# Versão personalizada para sistemas TUPANA

echo "🚀 Deploying TUPANA Wi-Fi Manager..."

# Configurações
PI_HOST="tony@192.168.1.40"
CONTAINER_NAME="rpi-wifi-manager"
IMAGE="tonymichael/wifi-manager:tupana"

echo "📡 Connecting to TUPANA system..."

# Parar e remover container existente
ssh $PI_HOST "docker stop $CONTAINER_NAME 2>/dev/null || true"
ssh $PI_HOST "docker rm $CONTAINER_NAME 2>/dev/null || true"

# Deploy da versão TUPANA
echo "🔄 Deploying TUPANA version..."
ssh $PI_HOST "docker run -d \
  --name $CONTAINER_NAME \
  --privileged \
  --network host \
  --restart unless-stopped \
  -e WIFI_INTERFACE=wlan0 \
  -v /var/run/dbus:/var/run/dbus \
  $IMAGE"

# Verificar status
echo "📊 Checking TUPANA system status..."
sleep 5
ssh $PI_HOST "docker ps | grep $CONTAINER_NAME"

echo "✅ TUPANA Wi-Fi Manager deployed successfully!"
echo "🌐 Access: http://192.168.1.40:8080 (connected) or http://192.168.4.1:8080 (hotspot)"
echo "📱 Hotspot: TUPANA-WiFi-Config (password: tupana123)"
echo "🎯 System: TUPANA Wi-Fi Management System"
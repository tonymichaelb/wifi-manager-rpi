#!/bin/bash

# Script de Deploy da Versão LITE para Raspberry Pi Zero 2W
# Otimizada para menor consumo de recursos

echo "🚀 Deploying Wi-Fi Manager LITE to Raspberry Pi..."

# Configurações
PI_HOST="tony@192.168.1.40"
CONTAINER_NAME="rpi-wifi-manager"
IMAGE="tonymichael/wifi-manager:lite-v3"

echo "📡 Connecting to Raspberry Pi..."

# Parar e remover container existente
ssh $PI_HOST "docker stop $CONTAINER_NAME 2>/dev/null || true"
ssh $PI_HOST "docker rm $CONTAINER_NAME 2>/dev/null || true"

# Deploy da versão LITE
echo "🔄 Deploying LITE version..."
ssh $PI_HOST "docker run -d \
  --name $CONTAINER_NAME \
  --privileged \
  --network host \
  --restart unless-stopped \
  -p 8080:8080 \
  -e WIFI_INTERFACE=wlan0 \
  -v /var/run/dbus:/var/run/dbus \
  $IMAGE"

# Verificar status
echo "📊 Checking deployment status..."
sleep 5
ssh $PI_HOST "docker ps | grep $CONTAINER_NAME"

echo "✅ LITE Version deployed successfully!"
echo "🌐 Access: http://192.168.1.40:8080 (connected) or http://192.168.4.1:8080 (hotspot)"
echo "📱 Hotspot: RPi-WiFi-Config (password: raspberry123)"
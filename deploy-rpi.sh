#!/bin/bash
# Script de deploy para Raspberry Pi Zero 2W - Wi-Fi Manager

echo "🍓 Iniciando deploy no Raspberry Pi Zero 2W"
echo "📍 IP: 192.168.1.40"
echo ""

# Verificar se estamos no Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  Este script deve ser executado no Raspberry Pi"
    exit 1
fi

# Verificar dependências
echo "🔍 Verificando dependências..."

# Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Instalando..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "✅ Docker instalado"
else
    echo "✅ Docker encontrado"
fi

# Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não encontrado. Instalando..."
    sudo apt-get update
    sudo apt-get install -y docker-compose
    echo "✅ Docker Compose instalado"
else
    echo "✅ Docker Compose encontrado"
fi

# Ferramentas de rede necessárias
echo "📡 Verificando ferramentas de rede..."
sudo apt-get update
sudo apt-get install -y wireless-tools wpasupplicant hostapd dnsmasq iptables

# Parar serviços que podem conflitar
echo "🛑 Parando serviços conflitantes..."
sudo systemctl stop hostapd 2>/dev/null || true
sudo systemctl stop dnsmasq 2>/dev/null || true
sudo systemctl disable hostapd 2>/dev/null || true
sudo systemctl disable dnsmasq 2>/dev/null || true

# Criar diretórios necessários
echo "📁 Criando diretórios..."
mkdir -p ./config
mkdir -p ./logs
sudo mkdir -p /var/log/wifi-manager

# Definir permissões
sudo chown -R $USER:$USER ./config ./logs
sudo chmod 755 ./config ./logs

# Baixar imagem Docker
echo "📦 Baixando imagem do WiFi Manager..."
docker pull tonymichael/wifi-manager:1.0.5

# Parar container anterior se existir
echo "🔄 Parando container anterior..."
docker-compose -f docker-compose.rpi.yml down 2>/dev/null || true

# Iniciar WiFi Manager
echo "🚀 Iniciando WiFi Manager em modo PRODUÇÃO..."
docker-compose -f docker-compose.rpi.yml up -d

# Aguardar inicialização
echo "⏳ Aguardando inicialização..."
sleep 10

# Verificar status
if docker ps | grep -q rpi-wifi-manager; then
    echo ""
    echo "🎉 WiFi Manager iniciado com sucesso!"
    echo ""
    echo "📊 Status:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep rpi-wifi-manager
    echo ""
    echo "🌐 Interface Web:"
    echo "   Local: http://localhost:8080"
    echo "   Rede:  http://192.168.1.40:8080"
    echo ""
    echo "📋 Comandos úteis:"
    echo "   Ver logs:    docker logs -f rpi-wifi-manager"
    echo "   Reiniciar:   docker-compose -f docker-compose.rpi.yml restart"
    echo "   Parar:       docker-compose -f docker-compose.rpi.yml down"
    echo ""
    echo "✅ Deploy concluído com sucesso!"
else
    echo "❌ Falha ao iniciar WiFi Manager"
    echo "📋 Logs para debug:"
    docker logs rpi-wifi-manager 2>/dev/null || echo "Container não encontrado"
    exit 1
fi
#!/bin/bash

# Script de instalação do TUPANA Wi-Fi Manager no Raspberry Pi Zero 2W
# Execute com: curl -sSL https://raw.githubusercontent.com/... | bash
# Ou baixe e execute: chmod +x install-tupana.sh && ./install-tupana.sh

set -e

echo "🔧 TUPANA Wi-Fi Manager - Instalação Automática"
echo "================================================="
echo ""

# Verificar se é Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
    echo "❌ Este script foi projetado para Raspberry Pi"
    exit 1
fi

echo "📋 Verificando sistema..."

# Atualizar sistema
echo "🔄 Atualizando sistema..."
sudo apt update -qq

# Instalar Docker se não estiver instalado
if ! command -v docker &> /dev/null; then
    echo "🐳 Instalando Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "✅ Docker instalado"
else
    echo "✅ Docker já instalado"
fi

# Instalar Docker Compose se não estiver instalado
if ! command -v docker-compose &> /dev/null; then
    echo "📦 Instalando Docker Compose..."
    sudo pip3 install docker-compose
    echo "✅ Docker Compose instalado"
else
    echo "✅ Docker Compose já instalado"
fi

# Criar diretório do projeto
PROJECT_DIR="/home/$USER/tupana-wifi"
echo "📁 Criando diretório do projeto: $PROJECT_DIR"
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# Criar docker-compose.yml
echo "📝 Criando docker-compose.yml..."
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  tupana-wifi:
    image: tonymichael/wifi-manager:tupana-clean
    container_name: tupana-wifi-manager
    privileged: true
    network_mode: host
    restart: unless-stopped
    
    volumes:
      # Acesso ao D-Bus para comunicação com NetworkManager
      - /var/run/dbus:/var/run/dbus
      # Configurações Wi-Fi persistentes
      - /etc/wpa_supplicant:/etc/wpa_supplicant
      # DHCP lease files
      - /var/lib/dhcp:/var/lib/dhcp
      # Acesso aos dispositivos de rede
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

# Criar scripts de controle
echo "📝 Criando scripts de controle..."

# Script de start
cat > start-tupana.sh << 'EOF'
#!/bin/bash
echo "🚀 Iniciando TUPANA Wi-Fi Manager..."
docker-compose up -d
echo "✅ TUPANA iniciado!"
echo "🌐 Acesse: http://$(hostname -I | awk '{print $1}'):8080"
echo "📱 Hotspot: TUPANA-WiFi-Config (senha: tupana123)"
EOF

# Script de stop
cat > stop-tupana.sh << 'EOF'
#!/bin/bash
echo "🛑 Parando TUPANA Wi-Fi Manager..."
docker-compose down
echo "✅ TUPANA parado!"
EOF

# Script de logs
cat > logs-tupana.sh << 'EOF'
#!/bin/bash
echo "📝 Logs do TUPANA Wi-Fi Manager:"
docker-compose logs -f tupana-wifi
EOF

# Script de status
cat > status-tupana.sh << 'EOF'
#!/bin/bash
echo "📊 Status do TUPANA Wi-Fi Manager:"
docker-compose ps
echo ""
echo "🔍 Health check:"
docker inspect tupana-wifi-manager --format='{{.State.Health.Status}}' 2>/dev/null || echo "Container não encontrado"
EOF

# Script de atualização
cat > update-tupana.sh << 'EOF'
#!/bin/bash
echo "🔄 Atualizando TUPANA Wi-Fi Manager..."
docker-compose pull
docker-compose up -d
echo "✅ TUPANA atualizado!"
EOF

# Tornar scripts executáveis
chmod +x *.sh

# Baixar imagem Docker
echo "⬇️ Baixando imagem TUPANA..."
docker pull tonymichael/wifi-manager:tupana-clean

# Parar container anterior se existir
echo "🔄 Parando container anterior..."
docker stop tupana-wifi-manager 2>/dev/null || true
docker rm tupana-wifi-manager 2>/dev/null || true

# Iniciar TUPANA
echo "🚀 Iniciando TUPANA Wi-Fi Manager..."
docker-compose up -d

# Aguardar inicialização
echo "⏳ Aguardando inicialização..."
sleep 10

# Obter IP local
LOCAL_IP=$(hostname -I | awk '{print $1}')

echo ""
echo "🎉 INSTALAÇÃO CONCLUÍDA!"
echo "=========================="
echo ""
echo "✅ TUPANA Wi-Fi Manager instalado e rodando!"
echo "🌐 Interface Web: http://$LOCAL_IP:8080"
echo "📱 Hotspot Fallback: TUPANA-WiFi-Config (senha: tupana123)"
echo ""
echo "📁 Diretório do projeto: $PROJECT_DIR"
echo ""
echo "🔧 Comandos disponíveis:"
echo "  ./start-tupana.sh   - Iniciar serviço"
echo "  ./stop-tupana.sh    - Parar serviço"
echo "  ./logs-tupana.sh    - Ver logs"
echo "  ./status-tupana.sh  - Ver status"
echo "  ./update-tupana.sh  - Atualizar versão"
echo ""
echo "📖 Logs atuais:"
docker-compose logs --tail 5 tupana-wifi

echo ""
echo "🔧 Para gerenciar o serviço:"
echo "cd $PROJECT_DIR && ./status-tupana.sh"
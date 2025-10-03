#!/bin/bash

# Script de instalação rápida do WiFi Manager
# Uso: curl -sSL https://raw.githubusercontent.com/user/repo/main/scripts/install.sh | bash

set -e

# Configurações
DOCKER_IMAGE="tonymichael/wifi-manager:latest"
CONTAINER_NAME="rpi-wifi-manager"
WEB_PORT="8080"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"; }
success() { echo -e "${GREEN}✅ $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; }
warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }

echo -e "${BLUE}"
cat << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║                WiFi Manager - Instalação                    ║
║               Sistema para Raspberry Pi Zero 2W             ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Verificar sistema
log "Verificando sistema..."

if ! command -v docker >/dev/null 2>&1; then
    log "Instalando Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    success "Docker instalado"
else
    success "Docker já instalado"
fi

# Verificar se é Raspberry Pi
if grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    log "Raspberry Pi detectado - usando configuração otimizada"
    EXTRA_ARGS="--privileged --network host -v /etc/wpa_supplicant:/etc/wpa_supplicant -v /etc/hostapd:/etc/hostapd --device /dev/rfkill:/dev/rfkill"
else
    log "Sistema genérico detectado - usando configuração básica"
    EXTRA_ARGS="-p ${WEB_PORT}:8080"
fi

# Parar container existente
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    log "Parando container existente..."
    docker stop ${CONTAINER_NAME} >/dev/null 2>&1 || true
    docker rm ${CONTAINER_NAME} >/dev/null 2>&1 || true
fi

# Pull da imagem
log "Baixando imagem WiFi Manager..."
if docker pull ${DOCKER_IMAGE}; then
    success "Imagem baixada"
else
    error "Falha ao baixar imagem"
    exit 1
fi

# Criar volumes
log "Criando volumes..."
docker volume create wifi-config >/dev/null 2>&1 || true
docker volume create wifi-logs >/dev/null 2>&1 || true

# Iniciar container
log "Iniciando WiFi Manager..."
docker run -d \
    --name ${CONTAINER_NAME} \
    --restart unless-stopped \
    -v wifi-config:/app/config \
    -v wifi-logs:/var/log/wifi-manager \
    -e PYTHONUNBUFFERED=1 \
    ${EXTRA_ARGS} \
    ${DOCKER_IMAGE}

# Aguardar inicialização
log "Aguardando inicialização..."
sleep 10

# Verificar status
if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    success "WiFi Manager iniciado com sucesso!"
else
    error "Falha ao iniciar WiFi Manager"
    docker logs ${CONTAINER_NAME}
    exit 1
fi

# Informações finais
echo
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                 Instalação Concluída! 🎉                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${BLUE}📱 Acesso à Interface:${NC}"
if [[ $EXTRA_ARGS == *"--network host"* ]]; then
    # Raspberry Pi
    CURRENT_IP=$(hostname -I | awk '{print $1}' 2>/dev/null || echo "IP_NOT_FOUND")
    if [ "$CURRENT_IP" != "IP_NOT_FOUND" ]; then
        echo "   • Wi-Fi Mode: http://${CURRENT_IP}:8080"
    fi
    echo "   • Hotspot Mode: http://192.168.4.1:8080"
    echo "   • Hotspot SSID: RPi-WiFi-Config"
    echo "   • Hotspot Password: raspberry123"
else
    # Sistema genérico
    echo "   • Interface: http://localhost:${WEB_PORT}"
fi

echo
echo -e "${BLUE}🔧 Comandos Úteis:${NC}"
echo "   • Ver logs: docker logs ${CONTAINER_NAME} -f"
echo "   • Parar: docker stop ${CONTAINER_NAME}"
echo "   • Reiniciar: docker restart ${CONTAINER_NAME}"
echo "   • Remover: docker rm -f ${CONTAINER_NAME}"

echo
echo -e "${BLUE}📋 Status:${NC}"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" --filter "name=${CONTAINER_NAME}"

echo
success "WiFi Manager instalado e funcionando!"

if grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo
    warning "Para usar todas as funcionalidades no Raspberry Pi:"
    echo "   1. Conecte-se ao hotspot 'RPi-WiFi-Config' se necessário"
    echo "   2. Acesse a interface web para configurar Wi-Fi"
    echo "   3. O sistema mudará automaticamente entre Wi-Fi e hotspot"
fi
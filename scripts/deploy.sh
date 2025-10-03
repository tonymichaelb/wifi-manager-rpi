#!/bin/bash

# Script de deployment rápido para Raspberry Pi
# Este script automatiza a instalação completa

set -e

INSTALL_DIR="/home/pi/wifi-manager"
SERVICE_NAME="wifi-manager"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log colorido
log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    error "Este script deve ser executado como root"
    echo "Use: sudo $0"
    exit 1
fi

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              WiFi Manager - Deployment Script               ║"
echo "║                  Raspberry Pi Zero 2W                       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Verificar se é Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    warning "Este sistema não parece ser um Raspberry Pi"
    read -p "Continuar mesmo assim? (y/N): " confirm
    if [[ $confirm != [yY] ]]; then
        exit 1
    fi
fi

# Parar serviço se estiver rodando
log "Verificando serviços existentes..."
if systemctl is-active --quiet $SERVICE_NAME; then
    log "Parando serviço existente..."
    systemctl stop $SERVICE_NAME
fi

# Backup de configuração existente
if [ -d "$INSTALL_DIR" ]; then
    log "Fazendo backup da configuração existente..."
    cp -r "$INSTALL_DIR/config" "/tmp/wifi-manager-config-backup-$(date +%s)" 2>/dev/null || true
fi

# Criar diretório de instalação
log "Preparando diretório de instalação..."
mkdir -p "$INSTALL_DIR"

# Detectar origem dos arquivos
if [ -f "./docker-compose.yml" ]; then
    # Executando do diretório do projeto
    log "Copiando arquivos do projeto..."
    cp -r ./* "$INSTALL_DIR/"
    CURRENT_DIR=$(pwd)
elif [ -f "/app/docker-compose.yml" ]; then
    # Executando de dentro do container
    log "Copiando arquivos do container..."
    cp -r /app/* "$INSTALL_DIR/"
else
    error "Arquivos do projeto não encontrados"
    echo "Execute este script do diretório do projeto ou forneça o caminho"
    exit 1
fi

# Configurar permissões
log "Configurando permissões..."
chown -R pi:pi "$INSTALL_DIR" 2>/dev/null || true
chmod +x "$INSTALL_DIR/scripts"/*.sh

# Configurar ambiente
cd "$INSTALL_DIR"

# Verificar e instalar Docker se necessário
log "Verificando Docker..."
if ! command -v docker >/dev/null 2>&1; then
    log "Instalando Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    usermod -aG docker pi 2>/dev/null || true
    rm get-docker.sh
    success "Docker instalado"
else
    success "Docker já instalado"
fi

# Verificar Docker Compose
if ! command -v docker-compose >/dev/null 2>&1; then
    log "Instalando Docker Compose..."
    pip3 install docker-compose || {
        apt-get update
        apt-get install -y python3-pip
        pip3 install docker-compose
    }
    success "Docker Compose instalado"
else
    success "Docker Compose já instalado"
fi

# Construir imagem
log "Construindo imagem Docker..."
if docker-compose build; then
    success "Imagem construída com sucesso"
else
    error "Falha ao construir imagem"
    exit 1
fi

# Configurar serviço systemd
log "Configurando serviço systemd..."
cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=WiFi Manager for Raspberry Pi
After=docker.service network-online.target
Wants=network-online.target
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
ExecReload=/usr/bin/docker-compose restart
TimeoutStartSec=300
TimeoutStopSec=30
User=root
Group=root

[Install]
WantedBy=multi-user.target
EOF

# Recarregar systemd
systemctl daemon-reload
systemctl enable $SERVICE_NAME

# Configurar logrotate
log "Configurando rotação de logs..."
cat > /etc/logrotate.d/wifi-manager << EOF
/var/log/wifi-manager/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    copytruncate
    su root root
}
EOF

# Configurações de rede para Raspberry Pi
log "Otimizando configurações de rede..."

# Desabilitar gerenciamento de energia Wi-Fi
echo 'iwconfig wlan0 power off 2>/dev/null || true' >> /etc/rc.local

# Configurar dhcpcd para não gerenciar wlan0
if ! grep -q "denyinterfaces wlan0" /etc/dhcpcd.conf; then
    echo "denyinterfaces wlan0" >> /etc/dhcpcd.conf
fi

# Verificar e otimizar configurações boot
log "Verificando configurações de boot..."
BOOT_CONFIG="/boot/config.txt"
if [ -f "$BOOT_CONFIG" ]; then
    # Otimizar memória GPU para headless
    if ! grep -q "gpu_mem=16" "$BOOT_CONFIG"; then
        echo "gpu_mem=16" >> "$BOOT_CONFIG"
        log "Configuração GPU otimizada"
    fi
    
    # Habilitar SSH por padrão
    systemctl enable ssh 2>/dev/null || true
fi

# Testar configuração
log "Testando configuração..."
if docker-compose config >/dev/null 2>&1; then
    success "Configuração Docker válida"
else
    error "Configuração Docker inválida"
    docker-compose config
    exit 1
fi

# Iniciar serviço
log "Iniciando WiFi Manager..."
if systemctl start $SERVICE_NAME; then
    success "Serviço iniciado com sucesso"
else
    error "Falha ao iniciar serviço"
    journalctl -u $SERVICE_NAME --no-pager -l
    exit 1
fi

# Aguardar serviço ficar ativo
log "Aguardando serviço ficar ativo..."
sleep 10

# Verificar status
if systemctl is-active --quiet $SERVICE_NAME; then
    success "WiFi Manager está rodando!"
else
    warning "Serviço pode não estar completamente ativo"
    systemctl status $SERVICE_NAME --no-pager
fi

# Mostrar informações finais
echo
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                  Instalação Concluída!                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${BLUE}📋 Informações do Sistema:${NC}"
echo "   • Diretório: $INSTALL_DIR"
echo "   • Serviço: $SERVICE_NAME"
echo "   • Interface Web: http://IP_DO_RPI:8080"
echo "   • Hotspot: RPi-WiFi-Config (senha: raspberry123)"

echo
echo -e "${BLUE}🔧 Comandos Úteis:${NC}"
echo "   • Status: systemctl status $SERVICE_NAME"
echo "   • Logs: journalctl -u $SERVICE_NAME -f"
echo "   • Parar: systemctl stop $SERVICE_NAME"
echo "   • Reiniciar: systemctl restart $SERVICE_NAME"
echo "   • Docker: docker-compose logs -f"

echo
echo -e "${BLUE}🌐 Acesso à Interface:${NC}"
# Detectar IP atual
CURRENT_IP=$(ip route get 8.8.8.8 2>/dev/null | grep -oP 'src \K\S+' || echo "IP_NOT_FOUND")
if [ "$CURRENT_IP" != "IP_NOT_FOUND" ]; then
    echo "   • Modo Wi-Fi: http://$CURRENT_IP:8080"
fi
echo "   • Modo Hotspot: http://192.168.4.1:8080"

echo
echo -e "${YELLOW}⚠️  Próximos Passos:${NC}"
echo "   1. Conecte-se ao hotspot 'RPi-WiFi-Config' se necessário"
echo "   2. Acesse a interface web para configurar Wi-Fi"
echo "   3. Monitore logs para verificar funcionamento"

if [ "$CURRENT_IP" == "IP_NOT_FOUND" ]; then
    echo
    warning "Sistema pode estar em modo hotspot"
    echo "   Conecte-se à rede 'RPi-WiFi-Config' e acesse http://192.168.4.1:8080"
fi

echo
echo -e "${GREEN}✅ Deploy concluído com sucesso!${NC}"
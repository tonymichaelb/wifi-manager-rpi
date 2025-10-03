#!/bin/bash

# Script de instalação fácil para Raspberry Pi
# WiFi Manager v1.0.3
# Execute: curl -sSL https://raw.githubusercontent.com/user/repo/main/scripts/install-rpi.sh | sudo bash

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Banner
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║            WiFi Manager para Raspberry Pi v1.0.3            ║"
echo "║                 Instalação Automática                       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Verificar se é root
if [[ $EUID -ne 0 ]]; then
   error "Este script deve ser executado como root (use sudo)"
   exit 1
fi

# Detectar sistema
log "Detectando sistema..."
if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    OS=$NAME
    VERSION=$VERSION_ID
else
    error "Sistema não suportado"
    exit 1
fi

echo "Sistema: $OS $VERSION"

# Verificar se é Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    warning "Este sistema pode não ser um Raspberry Pi. Continuar? (y/N)"
    read -r response
    if [[ ! $response =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Atualizar sistema
log "Atualizando sistema..."
apt-get update -qq
apt-get upgrade -y -qq

# Instalar Docker
log "Verificando Docker..."
if ! command -v docker >/dev/null 2>&1; then
    log "Instalando Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    
    # Adicionar usuário pi ao grupo docker
    if id "pi" &>/dev/null; then
        usermod -aG docker pi
        log "Usuário 'pi' adicionado ao grupo docker"
    fi
fi

# Instalar Docker Compose
log "Verificando Docker Compose..."
if ! command -v docker-compose >/dev/null 2>&1; then
    log "Instalando Docker Compose..."
    pip3 install docker-compose
fi

success "Docker instalado"

# Criar diretório do projeto
INSTALL_DIR="/opt/wifi-manager"
log "Criando diretório $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Criar docker-compose.yml para produção
log "Criando configuração..."
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  wifi-manager:
    image: tonymichael/wifi-manager-rpi:latest
    container_name: wifi-manager
    privileged: true
    network_mode: host
    restart: unless-stopped
    volumes:
      - /var/run/dbus:/var/run/dbus:rw
      - /etc/wpa_supplicant:/etc/wpa_supplicant:rw
      - /var/lib/dhcp:/var/lib/dhcp:rw
      - ./config:/app/config:rw
      - ./logs:/app/logs:rw
      - /dev:/dev:rw
      - /sys:/sys:rw
      - /proc:/proc:rw
      - /etc/systemd/network:/etc/systemd/network:rw
    environment:
      - WIFI_INTERFACE=wlan0
      - WEB_PORT=8080
      - DEMO_MODE=false
      - LOG_LEVEL=INFO
      - PYTHONUNBUFFERED=1
    cap_add:
      - NET_ADMIN
      - NET_RAW
      - SYS_ADMIN
    devices:
      - /dev/rfkill:/dev/rfkill
    labels:
      - "wifi-manager.service=main"
      - "wifi-manager.version=1.0.3"
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8080/status || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
EOF

# Criar diretórios necessários
mkdir -p config logs

# Criar arquivo de configuração padrão
cat > config/system_config.json << 'EOF'
{
  "wifi_interface": "wlan0",
  "hotspot_ssid": "RPi-WiFi-Config",
  "hotspot_password": "raspberry123",
  "web_port": 8080,
  "check_interval": 10,
  "max_failures": 3,
  "auto_reconnect": true,
  "log_level": "INFO"
}
EOF

# Criar script de controle
cat > wifi-manager-control.sh << 'EOF'
#!/bin/bash

COMPOSE_FILE="/opt/wifi-manager/docker-compose.yml"

case "$1" in
    start)
        echo "Iniciando WiFi Manager..."
        cd /opt/wifi-manager
        docker-compose up -d
        ;;
    stop)
        echo "Parando WiFi Manager..."
        cd /opt/wifi-manager
        docker-compose down
        ;;
    restart)
        echo "Reiniciando WiFi Manager..."
        cd /opt/wifi-manager
        docker-compose restart
        ;;
    status)
        cd /opt/wifi-manager
        docker-compose ps
        ;;
    logs)
        cd /opt/wifi-manager
        docker-compose logs -f
        ;;
    update)
        echo "Atualizando WiFi Manager..."
        cd /opt/wifi-manager
        docker-compose pull
        docker-compose up -d
        ;;
    *)
        echo "Uso: $0 {start|stop|restart|status|logs|update}"
        exit 1
        ;;
esac
EOF

chmod +x wifi-manager-control.sh
ln -sf "$INSTALL_DIR/wifi-manager-control.sh" /usr/local/bin/wifi-manager

# Criar serviço systemd
log "Criando serviço systemd..."
cat > /etc/systemd/system/wifi-manager.service << 'EOF'
[Unit]
Description=WiFi Manager para Raspberry Pi
Requires=docker.service
After=docker.service
StartLimitBurst=3
StartLimitInterval=60s

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/wifi-manager
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Recarregar systemd e habilitar serviço
systemctl daemon-reload
systemctl enable wifi-manager.service

# Baixar e iniciar
log "Baixando imagem Docker..."
docker pull tonymichael/wifi-manager-rpi:latest

log "Iniciando WiFi Manager..."
systemctl start wifi-manager.service

# Aguardar inicialização
sleep 10

# Verificar status
if systemctl is-active --quiet wifi-manager.service; then
    success "WiFi Manager instalado e funcionando!"
else
    error "Falha na inicialização. Verificando logs..."
    journalctl -u wifi-manager.service --no-pager -l
    exit 1
fi

echo
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              Instalação Concluída! 🎉                       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${BLUE}📱 Acesso:${NC}"
echo "   Interface Web: http://$(hostname -I | awk '{print $1}'):8080"
echo "   Interface Web Local: http://localhost:8080"
echo

echo -e "${BLUE}🔧 Comandos úteis:${NC}"
echo "   wifi-manager start      # Iniciar serviço"
echo "   wifi-manager stop       # Parar serviço"
echo "   wifi-manager restart    # Reiniciar serviço"
echo "   wifi-manager status     # Ver status"
echo "   wifi-manager logs       # Ver logs"
echo "   wifi-manager update     # Atualizar"
echo

echo -e "${BLUE}📂 Arquivos:${NC}"
echo "   Configuração: /opt/wifi-manager/config/"
echo "   Logs: /opt/wifi-manager/logs/"
echo "   Controle: wifi-manager {start|stop|restart|status|logs|update}"
echo

echo -e "${BLUE}🛜 Funcionamento:${NC}"
echo "   • O sistema monitora a conexão Wi-Fi automaticamente"
echo "   • Se a conexão cair, ativa o hotspot 'RPi-WiFi-Config'"
echo "   • Conecte-se ao hotspot e acesse http://192.168.4.1:8080"
echo "   • Configure uma nova rede Wi-Fi pela interface web"
echo

warning "Reinicie o Raspberry Pi para garantir que tudo funcione corretamente:"
echo "   sudo reboot"
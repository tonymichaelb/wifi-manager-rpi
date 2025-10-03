#!/bin/bash

# Script para configuração inicial do Raspberry Pi
# Execute este script uma vez após instalar o sistema

set -e

echo "=== Configuração Inicial do WiFi Manager ==="

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    echo "ERRO: Este script deve ser executado como root"
    exit 1
fi

# Função para log
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Atualizar sistema
log "Atualizando sistema..."
apt-get update

# Instalar dependências
log "Instalando dependências..."
apt-get install -y \
    hostapd \
    dnsmasq \
    iproute2 \
    wireless-tools \
    wpasupplicant \
    iptables \
    iptables-persistent \
    python3 \
    python3-pip \
    docker.io \
    docker-compose \
    git

# Habilitar serviços do Docker
log "Configurando Docker..."
systemctl enable docker
systemctl start docker

# Adicionar usuário pi ao grupo docker (se existir)
if id "pi" &>/dev/null; then
    usermod -aG docker pi
    log "Usuário pi adicionado ao grupo docker"
fi

# Desabilitar serviços conflitantes
log "Desabilitando serviços conflitantes..."
systemctl disable NetworkManager 2>/dev/null || true
systemctl disable wpa_supplicant 2>/dev/null || true
systemctl disable hostapd 2>/dev/null || true
systemctl disable dnsmasq 2>/dev/null || true

# Configurar arquivo de rede para interface Wi-Fi
log "Configurando interface de rede..."
cat > /etc/dhcpcd.conf.backup << 'EOF'
# Backup original do dhcpcd.conf
# Configuração será gerenciada pelo WiFi Manager
EOF

# Habilitar SSH (opcional)
log "Habilitando SSH..."
systemctl enable ssh
systemctl start ssh

# Configurar regras iptables básicas
log "Configurando iptables..."
iptables-save > /etc/iptables/rules.v4.backup

# Criar serviço systemd para o WiFi Manager
log "Criando serviço systemd..."
cat > /etc/systemd/system/wifi-manager.service << 'EOF'
[Unit]
Description=WiFi Manager for Raspberry Pi
After=docker.service
Requires=docker.service

[Service]
Type=forking
RemainAfterExit=yes
WorkingDirectory=/home/pi/wifi-manager
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

# Habilitar serviço (não iniciar ainda)
systemctl enable wifi-manager.service

# Configurar logrotate
log "Configurando logrotate..."
cat > /etc/logrotate.d/wifi-manager << 'EOF'
/var/log/wifi-manager/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    copytruncate
}
EOF

# Criar diretórios necessários
log "Criando diretórios..."
mkdir -p /var/log/wifi-manager
mkdir -p /var/lib/dhcp
mkdir -p /home/pi/wifi-manager

# Configurar permissões
chown -R pi:pi /home/pi/wifi-manager 2>/dev/null || true

# Verificar configuração do módulo Wi-Fi
log "Verificando módulo Wi-Fi..."
if lsmod | grep -q "brcmfmac"; then
    log "Módulo Wi-Fi Broadcom detectado"
elif lsmod | grep -q "rt2800usb\|rt2x00usb"; then
    log "Módulo Wi-Fi Ralink detectado"
else
    log "AVISO: Módulo Wi-Fi não detectado claramente"
    log "Módulos de rede carregados:"
    lsmod | grep -E "(wlan|wifi|80211)" || log "Nenhum módulo Wi-Fi padrão encontrado"
fi

# Mostrar interfaces de rede
log "Interfaces de rede disponíveis:"
ip link show | grep -E "^[0-9]+:" | while read line; do
    interface=$(echo "$line" | cut -d: -f2 | sed 's/^ *//')
    log "  $interface"
done

# Configuração adicional para Raspberry Pi Zero 2W
if grep -q "Raspberry Pi Zero 2" /proc/device-tree/model 2>/dev/null; then
    log "Raspberry Pi Zero 2W detectado - aplicando configurações específicas..."
    
    # Otimizar configurações de energia para Wi-Fi
    echo 'iwconfig wlan0 power off' >> /etc/rc.local
    
    # Configurar GPU memory split para dispositivos headless
    if ! grep -q "gpu_mem" /boot/config.txt; then
        echo "gpu_mem=16" >> /boot/config.txt
        log "Configuração GPU memory adicionada ao /boot/config.txt"
    fi
fi

log "=== Configuração inicial concluída ==="
log ""
log "Próximos passos:"
log "1. Copie os arquivos do projeto para /home/pi/wifi-manager/"
log "2. Execute: cd /home/pi/wifi-manager && docker-compose build"
log "3. Inicie o serviço: systemctl start wifi-manager"
log "4. Para iniciar automaticamente no boot: systemctl enable wifi-manager"
log ""
log "Para monitorar logs: journalctl -u wifi-manager -f"
log "Para acessar interface web: http://192.168.4.1:8080 (quando em modo hotspot)"
log ""
log "Reinicie o sistema para aplicar todas as configurações."
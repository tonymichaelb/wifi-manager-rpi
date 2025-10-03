#!/bin/bash

# Script de inicialização do sistema WiFi Manager
# Este script prepara o ambiente e inicia o sistema

set -e

echo "=== Iniciando WiFi Manager System ==="

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    echo "ERRO: Este script deve ser executado como root"
    exit 1
fi

# Função para log
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Criar diretórios necessários
log "Criando diretórios..."
mkdir -p /var/lib/dhcp
mkdir -p /var/run/hostapd
mkdir -p /var/log/wifi-manager

# Verificar interface Wi-Fi
WIFI_INTERFACE=${WIFI_INTERFACE:-wlan0}
log "Verificando interface Wi-Fi: $WIFI_INTERFACE"

if ! ip link show $WIFI_INTERFACE >/dev/null 2>&1; then
    log "AVISO: Interface $WIFI_INTERFACE não encontrada"
    log "Interfaces disponíveis:"
    ip link show | grep -E "^[0-9]+:" | cut -d: -f2 | sed 's/^ */  /'
fi

# Parar serviços conflitantes
log "Parando serviços conflitantes..."
systemctl stop NetworkManager 2>/dev/null || true
systemctl stop wpa_supplicant 2>/dev/null || true
systemctl stop hostapd 2>/dev/null || true
systemctl stop dnsmasq 2>/dev/null || true

# Aguardar serviços pararem
sleep 2

# Verificar dependências
log "Verificando dependências..."
for cmd in hostapd dnsmasq iw iwconfig; do
    if ! command -v $cmd >/dev/null 2>&1; then
        log "ERRO: Comando $cmd não encontrado"
        exit 1
    fi
done

# Configurar permissões
log "Configurando permissões..."
chmod +x /app/scripts/*.sh 2>/dev/null || true

# Verificar conectividade inicial
log "Verificando conectividade inicial..."
if ping -c 1 -W 3 8.8.8.8 >/dev/null 2>&1; then
    log "Conectividade detectada - iniciando em modo Wi-Fi"
    INITIAL_MODE="wifi"
else
    log "Sem conectividade - iniciando em modo hotspot"
    INITIAL_MODE="hotspot"
fi

# Exportar variáveis de ambiente
export WIFI_INTERFACE
export INITIAL_MODE

log "Sistema preparado com sucesso"
log "Interface Wi-Fi: $WIFI_INTERFACE"
log "Modo inicial: $INITIAL_MODE"

# Iniciar aplicação Python
log "Iniciando aplicação WiFi Manager..."
exec python /app/src/main.py
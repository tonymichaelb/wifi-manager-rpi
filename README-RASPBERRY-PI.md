# 🍓 WiFi Manager - Deploy no Raspberry Pi Zero 2W

## 📍 Configuração para Raspberry Pi
- **IP**: 192.168.1.40
- **Modo**: PRODUÇÃO (Wi-Fi real)
- **Hardware**: Raspberry Pi Zero 2W

## 🚀 Deploy Rápido

### 1. Conectar no Raspberry Pi
```bash
ssh pi@192.168.1.40
```

### 2. Baixar e Executar
```bash
# Download do projeto
wget https://github.com/user/wifi-manager/archive/main.zip
unzip main.zip
cd wifi-manager-main

# Executar deploy automático
chmod +x deploy-rpi.sh
sudo ./deploy-rpi.sh
```

### 3. Acessar Interface
- **Local**: http://localhost:8080
- **Rede**: http://192.168.1.40:8080

## 🔧 Deploy Manual

### Preparar Sistema
```bash
# Atualizar sistema
sudo apt-get update && sudo apt-get upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER

# Instalar ferramentas de rede
sudo apt-get install -y wireless-tools wpasupplicant hostapd dnsmasq

# Reiniciar para aplicar grupos
sudo reboot
```

### Configurar WiFi Manager
```bash
# Baixar imagem
docker pull tonymichael/wifi-manager:1.0.5

# Iniciar com configuração para Raspberry Pi
docker-compose -f docker-compose.rpi.yml up -d
```

## 📋 Diferenças do Modo Produção

### ✅ No Raspberry Pi (Modo Real)
- `DEMO_MODE=false`
- Acesso completo às interfaces Wi-Fi (`wlan0`)
- Scan de redes Wi-Fi **reais** do ambiente
- Hotspot funcional com `hostapd` e `dnsmasq`
- Configuração real de iptables e NAT
- Privileged mode para acesso ao hardware

### 🧪 No MacOS (Modo Demo)
- `DEMO_MODE=true`
- Redes Wi-Fi simuladas
- Sem acesso ao hardware Wi-Fi real
- Hotspot simulado

## 🌐 Funcionalidades no Raspberry Pi

### Wi-Fi Real
- ✅ Scan de redes reais: `iwlist wlan0 scan`
- ✅ Conexão real com `wpa_supplicant`
- ✅ Testes de conectividade real
- ✅ Monitoramento de interface real

### Hotspot Real
- ✅ Access Point com `hostapd`
- ✅ DHCP server com `dnsmasq`
- ✅ NAT e roteamento com `iptables`
- ✅ Portal captivo funcional

### Interface Web
- ✅ Dashboard em tempo real
- ✅ Scan de redes do ambiente
- ✅ Configuração de Wi-Fi
- ✅ Logs do sistema
- ✅ Acesso via rede local

## 🔍 Verificar Funcionamento

### Logs do Sistema
```bash
# Ver logs em tempo real
docker logs -f rpi-wifi-manager

# Verificar status
docker ps | grep rpi-wifi-manager
```

### Testar Wi-Fi Real
```bash
# Scan manual para comparar
sudo iwlist wlan0 scan | grep ESSID

# Via API do sistema
curl http://192.168.1.40:8080/scan
```

### Interface Web
```bash
# Testar status
curl http://192.168.1.40:8080/status

# Abrir no navegador
firefox http://192.168.1.40:8080
```

## 📱 Exemplo de Uso

### Cenário: Wi-Fi da Casa Cai
1. **Sistema detecta**: Falhas consecutivas de conectividade
2. **Ativa hotspot**: Raspberry Pi vira access point `RPi-WiFi-Config`
3. **Usuário conecta**: No hotspot via celular/laptop
4. **Acessa interface**: `http://192.168.4.1:8080`
5. **Configura nova rede**: Seleciona Wi-Fi e insere senha
6. **Sistema reconecta**: Volta ao modo Wi-Fi normal

## 🛠️ Comandos Úteis

### Gerenciar Container
```bash
# Parar
docker-compose -f docker-compose.rpi.yml down

# Reiniciar
docker-compose -f docker-compose.rpi.yml restart

# Ver logs
docker logs -f rpi-wifi-manager

# Shell no container
docker exec -it rpi-wifi-manager /bin/bash
```

### Debug Wi-Fi
```bash
# Status da interface
ip link show wlan0

# Scan manual
sudo iwlist wlan0 scan

# Status wpa_supplicant
sudo wpa_cli status

# Processos de rede
ps aux | grep -E "(hostapd|dnsmasq|wpa_supplicant)"
```

## 🔒 Segurança

### Firewall
```bash
# Permitir porta da interface web
sudo ufw allow 8080/tcp

# Permitir SSH
sudo ufw allow ssh

# Ativar firewall
sudo ufw enable
```

### Senha do Hotspot
- Padrão: `raspberry123`
- Alterar em: `docker-compose.rpi.yml` → `HOTSPOT_PASSWORD`

## 📊 Monitoramento

### Health Check
- Verifica se interface web responde
- Reinicia automaticamente se falhar
- Logs em `/var/log/wifi-manager/`

### Logs Estruturados
- Timestamp preciso
- Níveis: INFO, WARNING, ERROR
- Rotação automática de logs

---

**🎯 Status**: Pronto para produção no Raspberry Pi Zero 2W
**🌐 Acesso**: http://192.168.1.40:8080
**📞 Suporte**: Logs detalhados para troubleshooting
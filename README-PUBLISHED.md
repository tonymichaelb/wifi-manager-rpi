# 🛜 WiFi Manager para Raspberry Pi Zero 2W

Sistema completo de gerenciamento Wi-Fi que monitora conexão e ativa hotspot automático quando necessário.

[![Docker Hub](https://img.shields.io/docker/v/tonymichael/wifi-manager-rpi?label=Docker%20Hub)](https://hub.docker.com/r/tonymichael/wifi-manager-rpi)
[![Docker Pulls](https://img.shields.io/docker/pulls/tonymichael/wifi-manager-rpi)](https://hub.docker.com/r/tonymichael/wifi-manager-rpi)
[![Image Size](https://img.shields.io/docker/image-size/tonymichael/wifi-manager-rpi/latest)](https://hub.docker.com/r/tonymichael/wifi-manager-rpi)

## 🚀 Instalação Rápida (Raspberry Pi)

```bash
# Instalação automática
curl -sSL https://raw.githubusercontent.com/user/repo/main/scripts/install-rpi.sh | sudo bash

# Ou instalação manual com Docker
docker run -d --name wifi-manager \
  --privileged \
  --network host \
  --restart unless-stopped \
  -v /var/run/dbus:/var/run/dbus:rw \
  -v /etc/wpa_supplicant:/etc/wpa_supplicant:rw \
  -v wifi-config:/app/config \
  tonymichael/wifi-manager-rpi:latest
```

## ✨ Funcionalidades

- ✅ **Monitoramento automático** de conexão Wi-Fi
- ✅ **Hotspot de emergência** quando conexão cai
- ✅ **Interface web responsiva** para configuração
- ✅ **Captive portal** integrado
- ✅ **Compatível** com Raspberry Pi Zero 2W
- ✅ **Docker** para fácil instalação
- ✅ **Logs detalhados** para troubleshooting
- ✅ **Múltiplos métodos** de conexão Wi-Fi

## 📱 Como Funciona

1. **Modo Normal**: Sistema monitora conexão Wi-Fi a cada 10 segundos
2. **Falha Detectada**: Após 3 falhas consecutivas, ativa modo hotspot
3. **Hotspot Ativo**: Cria rede "RPi-WiFi-Config" (senha: raspberry123)
4. **Configuração**: Conecte-se ao hotspot e acesse http://192.168.4.1:8080
5. **Nova Conexão**: Configure nova rede Wi-Fi pela interface web
6. **Retorno Automático**: Sistema volta ao modo normal quando conectado

## 🐳 Instalação com Docker

### Quick Start
```bash
docker pull tonymichael/wifi-manager-rpi:latest

docker run -d \
  --name wifi-manager \
  --privileged \
  --network host \
  --restart unless-stopped \
  -v /var/run/dbus:/var/run/dbus:rw \
  -v /etc/wpa_supplicant:/etc/wpa_supplicant:rw \
  -v ./config:/app/config:rw \
  -v ./logs:/app/logs:rw \
  -e DEMO_MODE=false \
  tonymichael/wifi-manager-rpi:latest
```

### Docker Compose (Recomendado)
```bash
# Baixar configuração de produção
curl -O https://raw.githubusercontent.com/user/repo/main/docker-compose.prod.yml

# Renomear arquivo
mv docker-compose.prod.yml docker-compose.yml

# Criar diretórios
mkdir -p config logs

# Iniciar
docker-compose up -d
```

### Configuração Completa
```yaml
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
    environment:
      - WIFI_INTERFACE=wlan0
      - WEB_PORT=8080
      - DEMO_MODE=false
      - LOG_LEVEL=INFO
    cap_add:
      - NET_ADMIN
      - NET_RAW
      - SYS_ADMIN
    devices:
      - /dev/rfkill:/dev/rfkill
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8080/status || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## 🔧 Comandos de Controle

Após instalação automática, você terá os comandos:

```bash
wifi-manager start      # Iniciar serviço
wifi-manager stop       # Parar serviço
wifi-manager restart    # Reiniciar serviço
wifi-manager status     # Ver status
wifi-manager logs       # Ver logs em tempo real
wifi-manager update     # Atualizar para versão mais recente
```

## 📊 Interface Web

### Acesso
- **Modo Normal**: http://raspberry-pi-ip:8080
- **Modo Hotspot**: http://192.168.4.1:8080

### Funcionalidades da Interface
- 📶 **Scan de redes** Wi-Fi disponíveis
- 🔐 **Conexão segura** com senha
- 📈 **Monitor de status** em tempo real
- 📋 **Logs do sistema**
- ⚙️ **Configurações avançadas**

## 🛠️ Configuração

### Variáveis de Ambiente

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `WIFI_INTERFACE` | `wlan0` | Interface Wi-Fi |
| `WEB_PORT` | `8080` | Porta da interface web |
| `DEMO_MODE` | `false` | Modo demonstração |
| `LOG_LEVEL` | `INFO` | Nível de log |
| `HOTSPOT_SSID` | `RPi-WiFi-Config` | Nome do hotspot |
| `HOTSPOT_PASSWORD` | `raspberry123` | Senha do hotspot |

### Arquivo de Configuração

```json
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
```

## 🐛 Troubleshooting

### Logs
```bash
# Ver logs do container
docker logs wifi-manager -f

# Ver logs do sistema (se instalado como serviço)
journalctl -u wifi-manager -f

# Ver logs da aplicação
tail -f logs/wifi-manager.log
```

### Problemas Comuns

#### 1. Interface wlan0 não encontrada
```bash
# Verificar interfaces disponíveis
ip link show

# Ajustar variável de ambiente
docker run ... -e WIFI_INTERFACE=wlp2s0 ...
```

#### 2. Erro de autenticação Wi-Fi
- Verificar senha da rede
- Tentar método alternativo no log
- Verificar se a rede está disponível

#### 3. Hotspot não inicia
- Verificar se interface suporta modo AP
- Verificar conflitos com NetworkManager
- Verificar logs: `docker logs wifi-manager`

#### 4. Sem acesso à interface web
```bash
# Verificar se container está rodando
docker ps

# Verificar porta
netstat -tlnp | grep 8080

# Verificar firewall
sudo ufw status
```

## 🔧 Desenvolvimento

### Build Local
```bash
git clone https://github.com/user/repo.git
cd wifi-manager
docker build -t wifi-manager .
```

### Modo Demo
```bash
docker run -d \
  --name wifi-manager-demo \
  -p 8080:8080 \
  -e DEMO_MODE=true \
  tonymichael/wifi-manager-rpi:latest
```

### Estrutura do Projeto
```
wifi-manager/
├── src/                    # Código Python
│   ├── main.py            # Aplicação principal
│   ├── wifi_monitor.py    # Monitor Wi-Fi
│   ├── hotspot_manager.py # Gerenciador hotspot
│   ├── web_interface.py   # Interface web
│   └── config_manager.py  # Gerenciador configuração
├── templates/             # Templates HTML
├── config/               # Configurações
├── scripts/              # Scripts auxiliares
├── Dockerfile           # Imagem Docker
└── docker-compose.yml   # Configuração Docker
```

## 📋 Requisitos

### Hardware
- Raspberry Pi Zero 2W (recomendado)
- Raspberry Pi 3/4 (compatível)
- Interface Wi-Fi compatível
- Cartão SD (8GB+)

### Software
- Raspberry Pi OS (Bullseye/Bookworm)
- Docker & Docker Compose
- Acesso root (sudo)

## 🤝 Contribuição

1. Fork o projeto
2. Crie sua feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

- Comunidade Raspberry Pi
- Documentação Docker
- Contribuidores do projeto

## 📞 Suporte

- **Issues**: [GitHub Issues](https://github.com/user/repo/issues)
- **Docker Hub**: [tonymichael/wifi-manager-rpi](https://hub.docker.com/r/tonymichael/wifi-manager-rpi)
- **Wiki**: [Project Wiki](https://github.com/user/repo/wiki)

---

**WiFi Manager v1.0.3** - Sistema robusto e fácil de usar para gerenciamento Wi-Fi em Raspberry Pi! 🎉
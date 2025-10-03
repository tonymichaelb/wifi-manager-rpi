# WiFi Manager para Raspberry Pi Zero 2W

Sistema completo de gerenciamento Wi-Fi usando Docker que monitora a conexão Wi-Fi e ativa automaticamente um hotspot quando a conexão é perdida.

[![Docker Hub](https://img.shields.io/docker/pulls/tonymichael/wifi-manager.svg)](https://hub.docker.com/r/tonymichael/wifi-manager)
[![Docker Image Size](https://img.shields.io/docker/image-size/tonymichael/wifi-manager/latest.svg)](https://hub.docker.com/r/tonymichael/wifi-manager)

## 🚀 Instalação Rápida

### Raspberry Pi (Recomendado)
```bash
# Instalação com um comando
curl -sSL https://raw.githubusercontent.com/user/repo/main/scripts/install.sh | bash
```

### Docker Pull Direto
```bash
# Baixar imagem
docker pull tonymichael/wifi-manager:latest

# Executar (Raspberry Pi)
docker run -d --name wifi-manager \
  --privileged --network host \
  --restart unless-stopped \
  -v wifi-config:/app/config \
  -v /etc/wpa_supplicant:/etc/wpa_supplicant \
  tonymichael/wifi-manager:latest

# Executar (Outros sistemas)
docker run -d --name wifi-manager \
  -p 8080:8080 \
  --restart unless-stopped \
  -v wifi-config:/app/config \
  tonymichael/wifi-manager:latest
```

### Docker Compose
```bash
# Baixar configuração
curl -o docker-compose.yml https://raw.githubusercontent.com/user/repo/main/docker-compose.prod.yml

# Iniciar
docker-compose up -d
```

## 🚀 Características

- **Monitoramento Automático**: Verifica conexão Wi-Fi continuamente
- **Hotspot Automático**: Ativa hotspot quando Wi-Fi cai
- **Interface Web**: Configuração fácil via navegador
- **Docker**: Execução containerizada para isolamento
- **Captive Portal**: Redirecionamento automático para configuração
- **Logs Completos**: Monitoramento detalhado do sistema

## 📋 Requisitos

- Raspberry Pi Zero 2W com Raspberry Pi OS Lite 64-bit
- Docker e Docker Compose
- Módulo Wi-Fi interno do RPi
- Acesso root para configuração inicial

## 🛠️ Instalação

### 1. Preparar o Raspberry Pi

```bash
# Conectar via SSH ou terminal local
sudo apt update && sudo apt upgrade -y

# Clonar ou copiar os arquivos do projeto
git clone <repositorio> /home/pi/wifi-manager
cd /home/pi/wifi-manager

# Executar script de configuração inicial
sudo chmod +x scripts/setup-rpi.sh
sudo ./scripts/setup-rpi.sh
```

### 2. Construir e Iniciar

```bash
# Construir container Docker
sudo docker-compose build

# Iniciar sistema
sudo docker-compose up -d

# Verificar status
sudo docker-compose logs -f
```

### 3. Configurar Serviço Automático

```bash
# Habilitar início automático
sudo systemctl enable wifi-manager

# Iniciar serviço
sudo systemctl start wifi-manager

# Verificar status
sudo systemctl status wifi-manager
```

## 🔧 Configuração

### Variáveis de Ambiente

Edite o arquivo `docker-compose.yml` para personalizar:

```yaml
environment:
  - WIFI_INTERFACE=wlan0          # Interface Wi-Fi
  - HOTSPOT_SSID=RPi-WiFi-Config  # Nome do hotspot
  - HOTSPOT_PASSWORD=raspberry123  # Senha do hotspot
  - WEB_PORT=8080                 # Porta da interface web
```

### Configuração do Sistema

O arquivo `config/system_config.json` contém configurações avançadas:

- `check_interval`: Intervalo de verificação (segundos)
- `max_failures`: Falhas consecutivas antes de ativar hotspot
- `auto_reconnect`: Reconexão automática quando rede volta

## 🌐 Uso

### Modo Wi-Fi (Normal)

Quando conectado a uma rede Wi-Fi:
- Sistema monitora conexão continuamente
- Interface web acessível via IP da rede
- Logs disponíveis para monitoramento

### Modo Hotspot (Falha de Conexão)

Quando Wi-Fi falha ou não há configuração:
- Ativa hotspot `RPi-WiFi-Config`
- Interface web em `http://192.168.4.1:8080`
- Captive portal redireciona automaticamente

### Interface Web

Acesse via navegador para:
- ✅ Ver status da conexão
- 📡 Escanear redes disponíveis
- 🔗 Conectar a novas redes
- 📊 Visualizar logs do sistema
- ⚙️ Configurar parâmetros

## 📱 Captive Portal

O sistema inclui captive portal que:
- Detecta dispositivos conectados ao hotspot
- Redireciona automaticamente para configuração
- Funciona com Android, iOS e desktop
- URLs de detecção: `/generate_204`, `/hotspot-detect.html`

## 🐳 Docker

### Comandos Úteis

```bash
# Ver logs em tempo real
sudo docker-compose logs -f

# Reiniciar serviço
sudo docker-compose restart

# Parar sistema
sudo docker-compose down

# Reconstruir após mudanças
sudo docker-compose build --no-cache

# Verificar containers
sudo docker ps

# Entrar no container
sudo docker-compose exec wifi-manager bash
```

### Volumes Persistentes

O sistema monta volumes para persistir:
- `/etc/wpa_supplicant` - Configurações Wi-Fi
- `/var/log/wifi-manager` - Logs do sistema
- `./config` - Configurações personalizadas

## 🔍 Troubleshooting

### Interface Wi-Fi não encontrada

```bash
# Verificar interfaces disponíveis
ip link show

# Verificar módulos carregados
lsmod | grep brcm

# Reiniciar interface
sudo ip link set wlan0 down
sudo ip link set wlan0 up
```

### Problemas de Permissão

```bash
# Verificar se container tem privilégios
sudo docker-compose exec wifi-manager ip link show

# Reiniciar com privilégios completos
sudo docker-compose down
sudo docker-compose up -d
```

### Hotspot não funciona

```bash
# Verificar processos
sudo docker-compose exec wifi-manager pgrep hostapd
sudo docker-compose exec wifi-manager pgrep dnsmasq

# Ver logs detalhados
sudo docker-compose logs wifi-manager | grep -i "hostapd\|dnsmasq"

# Verificar iptables
sudo docker-compose exec wifi-manager iptables -L -n
```

### Debug de Conectividade

```bash
# Testar ping
sudo docker-compose exec wifi-manager ping -c 3 8.8.8.8

# Verificar DNS
sudo docker-compose exec wifi-manager nslookup google.com

# Status da interface
sudo docker-compose exec wifi-manager iwconfig wlan0
```

## 📊 Monitoramento

### Logs do Sistema

```bash
# Logs do container
sudo docker-compose logs -f

# Logs do sistema
sudo journalctl -u wifi-manager -f

# Logs específicos do Wi-Fi
tail -f /var/log/wifi-manager/wifi-manager.log
```

### Status via API

```bash
# Status geral do sistema
curl http://localhost:8080/status

# Redes Wi-Fi disponíveis
curl http://localhost:8080/scan

# Logs via API
curl http://localhost:8080/api/logs
```

## 🔒 Segurança

### Recomendações

- Altere senha padrão do hotspot
- Configure firewall para porta 8080
- Use HTTPS em produção (configure reverse proxy)
- Monitore logs para tentativas de acesso

### Configuração de Firewall

```bash
# Permitir apenas rede local
sudo ufw allow from 192.168.0.0/16 to any port 8080

# Ou permitir apenas interface específica
sudo ufw allow in on wlan0 to any port 8080
```

## 🚀 Customização

### Adicionar Funcionalidades

1. Edite `src/main.py` para lógica principal
2. Modifique `src/web_interface.py` para interface
3. Atualize `templates/index.html` para UI
4. Reconstrua: `sudo docker-compose build`

### Temas da Interface

Edite `templates/index.html` seção `<style>` para personalizar:
- Cores e gradientes
- Layout responsivo
- Ícones e fontes

## 📝 Arquivos Importantes

```
wifi-manager/
├── Dockerfile              # Container principal
├── docker-compose.yml      # Orquestração
├── requirements.txt        # Dependências Python
├── src/
│   ├── main.py             # Sistema principal
│   ├── wifi_monitor.py     # Monitoramento Wi-Fi
│   ├── hotspot_manager.py  # Gerenciamento hotspot
│   ├── web_interface.py    # Interface web
│   └── config_manager.py   # Configurações
├── templates/
│   └── index.html          # Interface web
├── scripts/
│   ├── setup-rpi.sh        # Configuração inicial
│   └── start.sh            # Script de inicialização
└── config/
    └── system_config.json  # Configurações do sistema
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie branch para feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para branch (`git push origin feature/nova-funcionalidade`)
5. Crie Pull Request

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

- 📖 Documentação: [Wiki do projeto]
- 🐛 Issues: [GitHub Issues]
- 💬 Discussões: [GitHub Discussions]
- 📧 Email: [seu-email@exemplo.com]

## 🎯 Roadmap

- [ ] Suporte a múltiplas redes Wi-Fi
- [ ] Interface mobile otimizada
- [ ] Backup automático de configurações
- [ ] Integração com APIs externas
- [ ] Suporte a VPN
- [ ] Dashboard de estatísticas
- [ ] Notificações push

---

**Desenvolvido com ❤️ para Raspberry Pi Zero 2W**
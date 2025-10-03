# 🔧 TUPANA Wi-Fi Manager# WiFi Manager para Raspberry Pi Zero 2W



Sistema completo de gerenciamento Wi-Fi para **Raspberry Pi Zero 2W** com interface web responsiva e hotspot automático.Sistema completo de gerenciamento Wi-Fi usando Docker que monitora a conexão Wi-Fi e ativa automaticamente um hotspot quando a conexão é perdida.



![TUPANA](https://img.shields.io/badge/TUPANA-WiFi%20Manager-blue) ![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-Zero%202W-red) ![Docker](https://img.shields.io/badge/Docker-Supported-green)[![Docker Hub](https://img.shields.io/docker/pulls/tonymichael/wifi-manager.svg)](https://hub.docker.com/r/tonymichael/wifi-manager)

[![Docker Image Size](https://img.shields.io/docker/image-size/tonymichael/wifi-manager/latest.svg)](https://hub.docker.com/r/tonymichael/wifi-manager)

## ✨ Funcionalidades

## 🚀 Instalação Rápida

- 🌐 **Interface Web Responsiva** - Controle via navegador

- 📱 **Hotspot Automático** - Ativa quando perde conexão Wi-Fi  ### Raspberry Pi (Recomendado)

- 🔍 **Scan de Redes** - Detecta redes disponíveis```bash

- 💾 **Gerenciamento de Redes Salvas** - Lista e exclui redes configuradas# Instalação com um comando

- 🔒 **Conexão Segura** - Suporte WPA/WPA2curl -sSL https://raw.githubusercontent.com/user/repo/main/scripts/install.sh | bash

- 🚀 **Deploy com Docker** - Instalação simples e isolada```

- 💡 **Otimizado para Pi Zero 2W** - Baixo consumo de recursos

### Docker Pull Direto

## 🚀 Instalação no Raspberry Pi```bash

# Baixar imagem

### Pré-requisitosdocker pull tonymichael/wifi-manager:latest

- Raspberry Pi Zero 2W com Raspberry Pi OS Lite 64-bit

- Conexão com internet (cabo ethernet ou Wi-Fi temporário)# Executar (Raspberry Pi)

docker run -d --name wifi-manager \

### Instalação Automática  --privileged --network host \

  --restart unless-stopped \

```bash  -v wifi-config:/app/config \

# Fazer download do script  -v /etc/wpa_supplicant:/etc/wpa_supplicant \

wget https://raw.githubusercontent.com/your-repo/tupana-wifi/main/install-tupana.sh  tonymichael/wifi-manager:latest



# Executar instalação# Executar (Outros sistemas)

chmod +x install-tupana.shdocker run -d --name wifi-manager \

./install-tupana.sh  -p 8080:8080 \

```  --restart unless-stopped \

  -v wifi-config:/app/config \

### Instalação Manual  tonymichael/wifi-manager:latest

```

1. **Instalar Docker**:

```bash### Docker Compose

curl -fsSL https://get.docker.com -o get-docker.sh```bash

sudo sh get-docker.sh# Baixar configuração

sudo usermod -aG docker $USERcurl -o docker-compose.yml https://raw.githubusercontent.com/user/repo/main/docker-compose.prod.yml

```

# Iniciar

2. **Criar projeto**:docker-compose up -d

```bash```

mkdir tupana-wifi && cd tupana-wifi

```## 🚀 Características



3. **Criar docker-compose.yml**:- **Monitoramento Automático**: Verifica conexão Wi-Fi continuamente

```yaml- **Hotspot Automático**: Ativa hotspot quando Wi-Fi cai

version: '3.8'- **Interface Web**: Configuração fácil via navegador

- **Docker**: Execução containerizada para isolamento

services:- **Captive Portal**: Redirecionamento automático para configuração

  tupana-wifi:- **Logs Completos**: Monitoramento detalhado do sistema

    image: tonymichael/wifi-manager:tupana-clean

    container_name: tupana-wifi-manager## 📋 Requisitos

    privileged: true

    network_mode: host- Raspberry Pi Zero 2W com Raspberry Pi OS Lite 64-bit

    restart: unless-stopped- Docker e Docker Compose

    - Módulo Wi-Fi interno do RPi

    volumes:- Acesso root para configuração inicial

      - /var/run/dbus:/var/run/dbus

      - /etc/wpa_supplicant:/etc/wpa_supplicant## 🛠️ Instalação

      - /var/lib/dhcp:/var/lib/dhcp

      - /dev:/dev### 1. Preparar o Raspberry Pi

    

    environment:```bash

      - WIFI_INTERFACE=wlan0# Conectar via SSH ou terminal local

      - FLASK_ENV=productionsudo apt update && sudo apt upgrade -y

    

    ports:# Clonar ou copiar os arquivos do projeto

      - "8080:8080"git clone <repositorio> /home/pi/wifi-manager

```cd /home/pi/wifi-manager



4. **Iniciar TUPANA**:# Executar script de configuração inicial

```bashsudo chmod +x scripts/setup-rpi.sh

docker-compose up -dsudo ./scripts/setup-rpi.sh

``````



## 🔧 Uso### 2. Construir e Iniciar



### Acesso à Interface```bash

# Construir container Docker

- **Quando conectado**: `http://[IP_DO_RASPBERRY]:8080`sudo docker-compose build

- **Hotspot ativo**: Conecte em `TUPANA-WiFi-Config` (senha: `tupana123`)

- **Então acesse**: `http://192.168.4.1:8080`# Iniciar sistema

sudo docker-compose up -d

### Fluxo de Uso

# Verificar status

1. **Primeira conexão**: Sistema ativa hotspot automaticamentesudo docker-compose logs -f

2. **Conectar dispositivo**: Conecte seu celular/computador no hotspot```

3. **Configurar Wi-Fi**: Acesse a interface e configure sua rede

4. **Funcionamento normal**: Sistema monitora e reconecta automaticamente### 3. Configurar Serviço Automático



## 📋 Comandos Úteis```bash

# Habilitar início automático

```bashsudo systemctl enable wifi-manager

# Ver status do serviço

cd tupana-wifi && docker-compose ps# Iniciar serviço

sudo systemctl start wifi-manager

# Ver logs em tempo real

docker-compose logs -f tupana-wifi# Verificar status

sudo systemctl status wifi-manager

# Parar serviço```

docker-compose down

## 🔧 Configuração

# Reiniciar serviço

docker-compose restart### Variáveis de Ambiente



# Atualizar para nova versãoEdite o arquivo `docker-compose.yml` para personalizar:

docker-compose pull && docker-compose up -d

``````yaml

environment:

## 🏗️ Como Funciona  - WIFI_INTERFACE=wlan0          # Interface Wi-Fi

  - HOTSPOT_SSID=RPi-WiFi-Config  # Nome do hotspot

```  - HOTSPOT_PASSWORD=raspberry123  # Senha do hotspot

┌─────────────────────────────────────────┐  - WEB_PORT=8080                 # Porta da interface web

│           TUPANA Wi-Fi Manager          │```

├─────────────────────────────────────────┤

│  🌐 Interface Web (Flask)               │### Configuração do Sistema

│  📡 Monitor Wi-Fi (Background)          │  

│  🔧 wpa_supplicant Manager              │O arquivo `config/system_config.json` contém configurações avançadas:

│  📱 Hotspot Controller (hostapd)        │

└─────────────────────────────────────────┘- `check_interval`: Intervalo de verificação (segundos)

```- `max_failures`: Falhas consecutivas antes de ativar hotspot

- `auto_reconnect`: Reconexão automática quando rede volta

### Lógica de Funcionamento

## 🌐 Uso

1. **Monitoramento**: Verifica conexão Wi-Fi a cada 30 segundos

2. **Hotspot Automático**: Se não há conexão, ativa hotspot `TUPANA-WiFi-Config`### Modo Wi-Fi (Normal)

3. **Configuração**: Interface web permite adicionar/remover redes

4. **Reconexão**: Tenta reconectar em redes salvas automaticamenteQuando conectado a uma rede Wi-Fi:

5. **Persistência**: Configurações salvas no wpa_supplicant- Sistema monitora conexão continuamente

- Interface web acessível via IP da rede

## 📱 Interface Web- Logs disponíveis para monitoramento



### Tela Principal### Modo Hotspot (Falha de Conexão)

- 📊 **Status atual**: Rede conectada e qualidade do sinal

- 🔍 **Scan de redes**: Lista redes Wi-Fi disponíveisQuando Wi-Fi falha ou não há configuração:

- 🔗 **Conectar**: Formulário para nova conexão- Ativa hotspot `RPi-WiFi-Config`

- Interface web em `http://192.168.4.1:8080`

### Redes Salvas  - Captive portal redireciona automaticamente

- 📋 **Lista limpa**: Apenas redes realmente configuradas

- 🗑️ **Exclusão**: Remove redes não utilizadas### Interface Web

- ✅ **Sem confusão**: Não mistura com redes detectadas

Acesse via navegador para:

## 🎨 Personalização- ✅ Ver status da conexão

- 📡 Escanear redes disponíveis

### Configurar Hotspot Personalizado- 🔗 Conectar a novas redes

```yaml- 📊 Visualizar logs do sistema

environment:- ⚙️ Configurar parâmetros

  - WIFI_INTERFACE=wlan0

  - HOTSPOT_SSID=MeuHotspot## 📱 Captive Portal

  - HOTSPOT_PASSWORD=minhasenha123

```O sistema inclui captive portal que:

- Detecta dispositivos conectados ao hotspot

### Usar Porta Diferente- Redireciona automaticamente para configuração

```yaml- Funciona com Android, iOS e desktop

ports:- URLs de detecção: `/generate_204`, `/hotspot-detect.html`

  - "8090:8080"  # Interface em http://ip:8090

```## 🐳 Docker



### Interface Wi-Fi Diferente### Comandos Úteis

```yaml

environment:```bash

  - WIFI_INTERFACE=wlan1  # Para usar wlan1# Ver logs em tempo real

```sudo docker-compose logs -f



## 🛠️ Desenvolvimento# Reiniciar serviço

sudo docker-compose restart

### Build Local

```bash# Parar sistema

# Clonar repositóriosudo docker-compose down

git clone https://github.com/your-repo/tupana-wifi.git

cd tupana-wifi# Reconstruir após mudanças

sudo docker-compose build --no-cache

# Build da imagem

docker build -f Dockerfile.lite -t tupana-wifi:local .# Verificar containers

sudo docker ps

# Executar versão local  

docker run -d --name tupana-local --privileged --network host tupana-wifi:local# Entrar no container

```sudo docker-compose exec wifi-manager bash

```

### Estrutura do Projeto

```### Volumes Persistentes

tupana-wifi/

├── src/O sistema monta volumes para persistir:

│   └── main-lite.py          # Aplicação principal- `/etc/wpa_supplicant` - Configurações Wi-Fi

├── templates/- `/var/log/wifi-manager` - Logs do sistema

│   └── index-lite.html       # Interface web- `./config` - Configurações personalizadas

├── Dockerfile.lite           # Container otimizado

├── docker-compose.yml        # Configuração de deploy## 🔍 Troubleshooting

├── install-tupana.sh         # Script de instalação

└── README.md                 # Esta documentação### Interface Wi-Fi não encontrada

```

```bash

## 🔍 Troubleshooting# Verificar interfaces disponíveis

ip link show

### Container não inicia

```bash# Verificar módulos carregados

# Verificar logs detalhadoslsmod | grep brcm

docker logs tupana-wifi-manager

# Reiniciar interface

# Verificar se interface existesudo ip link set wlan0 down

iwconfigsudo ip link set wlan0 up

```

# Verificar permissões dbus

ls -la /var/run/dbus### Problemas de Permissão

```

```bash

### Interface web não carrega# Verificar se container tem privilégios

```bashsudo docker-compose exec wifi-manager ip link show

# Verificar se porta está aberta

sudo netstat -tlnp | grep 8080# Reiniciar com privilégios completos

sudo docker-compose down

# Verificar IP do Raspberrysudo docker-compose up -d

hostname -I```



# Verificar firewall### Hotspot não funciona

sudo ufw status

``````bash

# Verificar processos

### Wi-Fi não conectasudo docker-compose exec wifi-manager pgrep hostapd

```bashsudo docker-compose exec wifi-manager pgrep dnsmasq

# Verificar interface Wi-Fi

iwconfig wlan0# Ver logs detalhados

sudo docker-compose logs wifi-manager | grep -i "hostapd\|dnsmasq"

# Ver status wpa_supplicant

sudo systemctl status wpa_supplicant# Verificar iptables

sudo docker-compose exec wifi-manager iptables -L -n

# Verificar configuração```

cat /etc/wpa_supplicant/wpa_supplicant.conf

```### Debug de Conectividade



### Hotspot não ativa```bash

```bash# Testar ping

# Verificar hostapdsudo docker-compose exec wifi-manager ping -c 3 8.8.8.8

sudo which hostapd

# Verificar DNS

# Verificar dnsmasq  sudo docker-compose exec wifi-manager nslookup google.com

sudo which dnsmasq

# Status da interface

# Ver logs específicossudo docker-compose exec wifi-manager iwconfig wlan0

docker logs tupana-wifi-manager | grep -i hotspot```

```

## 📊 Monitoramento

## 📈 Histórico de Versões

### Logs do Sistema

- **v1.0.x**: Versão inicial básica

- **tupana-v3**: Rebranding completo para TUPANA```bash

- **tupana-v4**: Correção exclusão de redes# Logs do container

- **tupana-v5**: Filtros melhorados  sudo docker-compose logs -f

- **tupana-clean**: Versão final otimizada ✅

# Logs do sistema

### O que há de novo no tupana-cleansudo journalctl -u wifi-manager -f

- ✅ Lista de redes salvas **limpa** (sem redes detectadas)

- ✅ Exclusão de redes **funcional** # Logs específicos do Wi-Fi

- ✅ Interface **responsiva** otimizadatail -f /var/log/wifi-manager/wifi-manager.log

- ✅ Monitoramento **estável** ```

- ✅ Hotspot **confiável**

### Status via API

## 🆘 Suporte e FAQ

```bash

### Como acessar se esqueci o IP?# Status geral do sistema

```bashcurl http://localhost:8080/status

# No Raspberry Pi

hostname -I# Redes Wi-Fi disponíveis

curl http://localhost:8080/scan

# Ou use o hotspot

# Conecte em TUPANA-WiFi-Config e acesse http://192.168.4.1:8080# Logs via API

```curl http://localhost:8080/api/logs

```

### Como fazer backup das configurações?

```bash## 🔒 Segurança

# Backup do wpa_supplicant

sudo cp /etc/wpa_supplicant/wpa_supplicant.conf ~/backup-wifi.conf### Recomendações



# Restaurar- Altere senha padrão do hotspot

sudo cp ~/backup-wifi.conf /etc/wpa_supplicant/wpa_supplicant.conf- Configure firewall para porta 8080

```- Use HTTPS em produção (configure reverse proxy)

- Monitore logs para tentativas de acesso

### Como desinstalar?

```bash### Configuração de Firewall

cd tupana-wifi

docker-compose down```bash

docker rmi tonymichael/wifi-manager:tupana-clean# Permitir apenas rede local

cd .. && rm -rf tupana-wifisudo ufw allow from 192.168.0.0/16 to any port 8080

```

# Ou permitir apenas interface específica

---sudo ufw allow in on wlan0 to any port 8080

```

<div align="center">

  <strong>🔧 TUPANA Wi-Fi Manager</strong><br>## 🚀 Customização

  <em>Gerenciamento Wi-Fi inteligente para Raspberry Pi Zero 2W</em><br><br>

  <small>Versão: tupana-clean | Otimizado para produção</small>### Adicionar Funcionalidades

</div>
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
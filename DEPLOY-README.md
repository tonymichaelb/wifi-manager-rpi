# TUPANA 1.0 - Gerenciador Wi-Fi 🚀

## Imagem Publicada no Docker Hub

A imagem **TUPANA 1.0** está oficialmente disponível no Docker Hub:

- `tonymichael/wifi-manager:tupana-1.0` - Versão estável
- `tonymichael/wifi-manager:latest` - Última versão (aponta para tupana-1.0)

## Instalação no Raspberry Pi Zero 2W

### 1. Baixar e Executar

```bash
# Baixar a imagem
docker pull tonymichael/wifi-manager:tupana-1.0

# Criar arquivo docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  wifi-manager:
    image: tonymichael/wifi-manager:tupana-1.0
    container_name: tupana-wifi-manager
    privileged: true
    network_mode: host
    volumes:
      - /etc/wpa_supplicant:/etc/wpa_supplicant
      - /var/lib/dhcp:/var/lib/dhcp
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
EOF

# Executar
docker-compose up -d
```

### 2. Acesso à Interface

- **URL:** `http://[IP_DO_PI]:8080`
- **Interface:** Responsiva e otimizada para mobile
- **Funcionalidades:**
  - Monitoramento automático da conexão Wi-Fi
  - Hotspot automático quando conexão cair
  - Gerenciamento de redes salvas
  - Interface limpa e intuitiva

## Recursos do TUPANA 1.0

### ✅ **Automático**
- Carregamento automático de redes salvas
- Ativação automática do hotspot quando Wi-Fi cair
- Monitoramento contínuo da conexão

### ✅ **Interface Simplificada**
- Design limpo e profissional
- Sem elementos manuais desnecessários
- Responsivo para todos os dispositivos

### ✅ **Gerenciamento Completo**
- Escaneamento de redes disponíveis
- Conexão a novas redes Wi-Fi
- Exclusão de redes salvas
- Visualização da rede atual

## Configuração de Hotspot

O TUPANA cria automaticamente um hotspot com:
- **SSID:** `TUPANA-Setup`
- **Senha:** `tupana123`
- **IP:** `192.168.4.1`

## Logs e Monitoramento

```bash
# Ver logs do container
docker logs tupana-wifi-manager -f

# Status do container
docker ps --filter "name=tupana"

# Restart se necessário
docker-compose restart
```

## Atualizações

Para atualizar para novas versões:

```bash
docker-compose down
docker pull tonymichael/wifi-manager:latest
docker-compose up -d
```

---

**TUPANA 1.0** - Sistema completo de gerenciamento Wi-Fi para Raspberry Pi Zero 2W
Desenvolvido com 💚 para facilitar o gerenciamento de conexões Wi-Fi
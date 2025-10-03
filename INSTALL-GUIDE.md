# 🚀 Instruções de Instalação - WiFi Manager v1.0.3

## 📦 Imagem Publicada no Docker Hub

**Imagem**: `tonymichael/wifi-manager-rpi:latest`
**Link**: https://hub.docker.com/r/tonymichael/wifi-manager-rpi

## 🛠️ Instalação no Raspberry Pi

### Opção 1: Instalação Automática (Recomendada)
```bash
curl -sSL https://raw.githubusercontent.com/user/repo/main/scripts/install-rpi.sh | sudo bash
```

### Opção 2: Docker Run Manual
```bash
docker run -d --name wifi-manager \
  --privileged --network host --restart unless-stopped \
  -v /var/run/dbus:/var/run/dbus:rw \
  -v /etc/wpa_supplicant:/etc/wpa_supplicant:rw \
  -v wifi-config:/app/config \
  -e DEMO_MODE=false \
  tonymichael/wifi-manager-rpi:latest
```

### Opção 3: Docker Compose
```bash
# Baixar configuração
curl -O https://raw.githubusercontent.com/user/repo/main/docker-compose.prod.yml
mv docker-compose.prod.yml docker-compose.yml

# Iniciar
docker-compose up -d
```

## 🌐 Acesso à Interface

- **Normal**: http://ip-do-raspberry:8080
- **Hotspot**: http://192.168.4.1:8080

## 📋 Como Usar

1. **Instale** usando uma das opções acima
2. **Acesse** a interface web no navegador
3. **Configure** sua rede Wi-Fi
4. **Pronto**! O sistema monitora automaticamente

## 🔧 Controle do Sistema

```bash
# Comandos disponíveis após instalação automática
wifi-manager start      # Iniciar
wifi-manager stop       # Parar
wifi-manager restart    # Reiniciar
wifi-manager status     # Status
wifi-manager logs       # Ver logs
wifi-manager update     # Atualizar
```

## 🐛 Problemas?

1. **Verificar logs**: `docker logs wifi-manager`
2. **Status do container**: `docker ps`
3. **Reiniciar**: `docker restart wifi-manager`

## 📱 Funcionalidades

- ✅ Monitor Wi-Fi automático
- ✅ Hotspot de emergência
- ✅ Interface web intuitiva
- ✅ Fácil configuração
- ✅ Logs detalhados

---

**Sistema testado e funcionando!** 🎉

Para mais detalhes, consulte o README-PUBLISHED.md
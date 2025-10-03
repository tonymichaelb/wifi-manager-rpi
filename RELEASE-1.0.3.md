# WiFi Manager v1.0.3 - Release Notes

## 🚀 Publicação no Docker Hub

**Imagem:** `tonymichael/wifi-manager-rpi:1.0.3`

## 📦 Como usar:

### Quick Start:
```bash
docker run -d --name wifi-manager \
  --privileged \
  --network host \
  -v wifi-config:/app/config \
  -v /etc/wpa_supplicant:/etc/wpa_supplicant \
  tonymichael/wifi-manager-rpi:latest
```

### Docker Compose:
```bash
curl -o docker-compose.yml https://raw.githubusercontent.com/user/repo/main/docker-compose.prod.yml
docker-compose up -d
```

### Raspberry Pi:
```bash
curl -sSL https://raw.githubusercontent.com/user/repo/main/scripts/install-rpi.sh | sudo bash
```

## ✨ Funcionalidades:

- ✅ Monitoramento Wi-Fi automático
- ✅ Hotspot de emergência
- ✅ Interface web responsiva
- ✅ Captive portal integrado
- ✅ Compatível com Raspberry Pi Zero 2W
- ✅ Configuração via Docker

## 🔗 Links:

- **Docker Hub:** https://hub.docker.com/r/tonymichael/wifi-manager-rpi
- **Documentação:** README.md
- **Issues:** GitHub Issues

## 📱 Acesso:

- **Interface Web:** http://localhost:8080
- **Modo Hotspot:** http://192.168.4.1:8080

Publicado em: Fri Oct  3 11:35:46 -04 2025

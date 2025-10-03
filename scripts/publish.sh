#!/bin/bash

# Script para publicar o WiFi Manager no Docker Hub
# Execute: ./scripts/publish.sh

set -e

# Configurações
DOCKER_USERNAME="tonymichael"
IMAGE_NAME="wifi-manager-rpi"
VERSION="1.0.3"
LATEST_TAG="latest"

# Cores para output
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

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║               WiFi Manager - Publish Script                 ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Verificar se está no diretório correto
if [ ! -f "Dockerfile" ]; then
    error "Dockerfile não encontrado! Execute este script do diretório do projeto."
    exit 1
fi

# Verificar Docker
log "Verificando Docker..."
if ! command -v docker >/dev/null 2>&1; then
    error "Docker não encontrado!"
    exit 1
fi

if ! docker info >/dev/null 2>&1; then
    error "Docker não está rodando!"
    exit 1
fi

success "Docker OK"

# Verificar login no Docker Hub
log "Verificando login no Docker Hub..."
if ! docker info | grep -q "Username"; then
    warning "Não está logado no Docker Hub"
    echo "Faça login com: docker login"
    read -p "Deseja fazer login agora? (y/N): " do_login
    
    if [[ $do_login == [yY] ]]; then
        docker login
    else
        error "Login necessário para publicar"
        exit 1
    fi
fi

success "Docker Hub login OK"

# Parar containers existentes
log "Parando containers existentes..."
docker-compose down 2>/dev/null || true
docker stop $(docker ps -q --filter "name=wifi-manager") 2>/dev/null || true

# Build da imagem
log "Construindo imagem..."
FULL_IMAGE_NAME="${DOCKER_USERNAME}/${IMAGE_NAME}"

if docker build -t "${FULL_IMAGE_NAME}:${VERSION}" -t "${FULL_IMAGE_NAME}:${LATEST_TAG}" .; then
    success "Build concluído"
else
    error "Falha no build"
    exit 1
fi

# Verificar imagem
log "Verificando imagem construída..."
docker images "${FULL_IMAGE_NAME}"

# Teste local
log "Testando imagem localmente..."
if docker run -d --name wifi-manager-test -p 8081:8080 "${FULL_IMAGE_NAME}:${LATEST_TAG}"; then
    sleep 10
    
    if curl -f http://localhost:8081/ >/dev/null 2>&1; then
        success "Teste local passou"
        docker stop wifi-manager-test >/dev/null 2>&1
        docker rm wifi-manager-test >/dev/null 2>&1
    else
        error "Teste local falhou"
        docker logs wifi-manager-test
        docker stop wifi-manager-test >/dev/null 2>&1
        docker rm wifi-manager-test >/dev/null 2>&1
        exit 1
    fi
else
    error "Falha ao iniciar container de teste"
    exit 1
fi

# Confirmar publicação
echo
echo -e "${YELLOW}📋 Informações da publicação:${NC}"
echo "   • Imagem: ${FULL_IMAGE_NAME}"
echo "   • Versão: ${VERSION}"
echo "   • Tag latest: ${LATEST_TAG}"
echo "   • Size: $(docker images --format "table {{.Size}}" "${FULL_IMAGE_NAME}:${LATEST_TAG}" | tail -1)"
echo

read -p "Confirma a publicação no Docker Hub? (y/N): " confirm_publish

if [[ $confirm_publish != [yY] ]]; then
    warning "Publicação cancelada"
    exit 0
fi

# Push para Docker Hub
log "Publicando no Docker Hub..."

echo "Enviando versão ${VERSION}..."
if docker push "${FULL_IMAGE_NAME}:${VERSION}"; then
    success "Versão ${VERSION} publicada"
else
    error "Falha ao publicar versão ${VERSION}"
    exit 1
fi

echo "Enviando tag latest..."
if docker push "${FULL_IMAGE_NAME}:${LATEST_TAG}"; then
    success "Tag latest publicada"
else
    error "Falha ao publicar tag latest"
    exit 1
fi

# Verificar publicação
log "Verificando publicação..."
if docker pull "${FULL_IMAGE_NAME}:${LATEST_TAG}" >/dev/null 2>&1; then
    success "Imagem disponível no Docker Hub"
else
    warning "Imagem pode não estar disponível ainda (pode levar alguns minutos)"
fi

# Criar release notes
log "Criando release notes..."
cat > RELEASE-${VERSION}.md << EOF
# WiFi Manager v${VERSION} - Release Notes

## 🚀 Publicação no Docker Hub

**Imagem:** \`${FULL_IMAGE_NAME}:${VERSION}\`

## 📦 Como usar:

### Quick Start:
\`\`\`bash
docker run -d --name wifi-manager \\
  --privileged \\
  --network host \\
  -v wifi-config:/app/config \\
  -v /etc/wpa_supplicant:/etc/wpa_supplicant \\
  ${FULL_IMAGE_NAME}:latest
\`\`\`

### Docker Compose:
\`\`\`bash
curl -o docker-compose.yml https://raw.githubusercontent.com/user/repo/main/docker-compose.prod.yml
docker-compose up -d
\`\`\`

### Raspberry Pi:
\`\`\`bash
curl -sSL https://raw.githubusercontent.com/user/repo/main/scripts/install-rpi.sh | sudo bash
\`\`\`

## ✨ Funcionalidades:

- ✅ Monitoramento Wi-Fi automático
- ✅ Hotspot de emergência
- ✅ Interface web responsiva
- ✅ Captive portal integrado
- ✅ Compatível com Raspberry Pi Zero 2W
- ✅ Configuração via Docker

## 🔗 Links:

- **Docker Hub:** https://hub.docker.com/r/${DOCKER_USERNAME}/${IMAGE_NAME}
- **Documentação:** README.md
- **Issues:** GitHub Issues

## 📱 Acesso:

- **Interface Web:** http://localhost:8080
- **Modo Hotspot:** http://192.168.4.1:8080

Publicado em: $(date)
EOF

success "Release notes criadas: RELEASE-${VERSION}.md"

echo
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                Publicação Concluída! 🎉                     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${BLUE}📦 Imagem publicada:${NC}"
echo "   docker pull ${FULL_IMAGE_NAME}:${VERSION}"
echo "   docker pull ${FULL_IMAGE_NAME}:latest"
echo
echo -e "${BLUE}🌐 Docker Hub:${NC}"
echo "   https://hub.docker.com/r/${DOCKER_USERNAME}/${IMAGE_NAME}"
echo
echo -e "${BLUE}🚀 Como usar:${NC}"
echo "   docker run -d --name wifi-manager \\"
echo "     --privileged --network host \\"
echo "     ${FULL_IMAGE_NAME}:latest"
echo
echo -e "${BLUE}📋 Próximos passos:${NC}"
echo "   • Atualizar README.md com instruções de uso"
echo "   • Criar release no GitHub"
echo "   • Testar em Raspberry Pi"
echo "   • Compartilhar com a comunidade"

# Restart do container local
log "Reiniciando container local..."
docker-compose up -d

success "Sistema publicado e funcionando! 🎉"
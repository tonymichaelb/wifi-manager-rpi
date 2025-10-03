#!/bin/bash

# Script de verificação e deploy
# Verifica se todos os arquivos necessários estão presentes antes do deploy

set -e

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
echo "║               WiFi Manager - Deploy Check                   ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Verificar diretório atual
log "Verificando diretório atual: $(pwd)"

# Lista de arquivos necessários
REQUIRED_FILES=(
    "Dockerfile"
    "docker-compose.yml"
    "requirements.txt"
    "README.md"
    "src/main.py"
    "src/wifi_monitor.py"
    "src/hotspot_manager.py"
    "src/web_interface.py"
    "src/config_manager.py"
    "templates/index.html"
    "config/system_config.json"
    "scripts/deploy.sh"
    "scripts/setup-rpi.sh"
    "scripts/start.sh"
)

# Verificar arquivos necessários
log "Verificando arquivos necessários..."
missing_files=0

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        success "$file"
    else
        error "Arquivo não encontrado: $file"
        missing_files=$((missing_files + 1))
    fi
done

if [ $missing_files -gt 0 ]; then
    error "Encontrados $missing_files arquivos faltando!"
    echo
    echo "Certifique-se de que você está no diretório correto do projeto"
    echo "e que todos os arquivos foram criados adequadamente."
    exit 1
fi

# Verificar Docker
log "Verificando Docker..."
if ! command -v docker >/dev/null 2>&1; then
    error "Docker não encontrado! Instale o Docker primeiro."
    exit 1
fi

if ! docker info >/dev/null 2>&1; then
    error "Docker não está rodando! Inicie o Docker primeiro."
    exit 1
fi

success "Docker está funcionando"

# Verificar Docker Compose
log "Verificando Docker Compose..."
if ! command -v docker-compose >/dev/null 2>&1; then
    error "Docker Compose não encontrado!"
    exit 1
fi

success "Docker Compose está disponível"

# Verificar sintaxe do docker-compose.yml
log "Verificando sintaxe do docker-compose.yml..."
if docker-compose config >/dev/null 2>&1; then
    success "docker-compose.yml está válido"
else
    error "Erro na sintaxe do docker-compose.yml:"
    docker-compose config
    exit 1
fi

# Verificar portas em uso
log "Verificando porta 8080..."
if lsof -i :8080 >/dev/null 2>&1; then
    warning "Porta 8080 já está em uso"
    echo "Processos usando a porta 8080:"
    lsof -i :8080
    echo
    read -p "Deseja parar os containers existentes? (y/N): " stop_existing
    if [[ $stop_existing == [yY] ]]; then
        log "Parando containers existentes..."
        docker-compose down 2>/dev/null || true
        docker stop $(docker ps -q --filter "publish=8080") 2>/dev/null || true
    fi
else
    success "Porta 8080 está disponível"
fi

# Criar diretórios necessários
log "Criando diretórios necessários..."
mkdir -p logs
mkdir -p config
success "Diretórios criados"

# Verificar espaço em disco
log "Verificando espaço em disco..."
available_space=$(df . | tail -1 | awk '{print $4}')
if [ "$available_space" -lt 1000000 ]; then  # Menos de 1GB
    warning "Pouco espaço em disco disponível: $(df -h . | tail -1 | awk '{print $4}')"
else
    success "Espaço em disco suficiente"
fi

echo
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                Verificação Concluída!                       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${BLUE}🚀 Comandos para deploy:${NC}"
echo
echo "   # Build da imagem:"
echo "   docker-compose build"
echo
echo "   # Iniciar container:"
echo "   docker-compose up -d"
echo
echo "   # Verificar logs:"
echo "   docker-compose logs -f"
echo
echo "   # Verificar status:"
echo "   docker-compose ps"
echo
echo "   # Acessar interface:"
echo "   http://localhost:8080"

# Opção de deploy automático
echo
read -p "Deseja executar o deploy agora? (y/N): " auto_deploy

if [[ $auto_deploy == [yY] ]]; then
    echo
    log "Iniciando deploy automático..."
    
    # Build
    log "Construindo imagem..."
    if docker-compose build; then
        success "Build concluído"
    else
        error "Falha no build"
        exit 1
    fi
    
    # Deploy
    log "Iniciando container..."
    if docker-compose up -d; then
        success "Container iniciado"
    else
        error "Falha ao iniciar container"
        exit 1
    fi
    
    # Verificar status
    sleep 3
    log "Verificando status..."
    docker-compose ps
    
    echo
    success "Deploy concluído com sucesso!"
    echo "Acesse: http://localhost:8080"
    
else
    echo
    log "Execute os comandos acima quando estiver pronto para o deploy."
fi
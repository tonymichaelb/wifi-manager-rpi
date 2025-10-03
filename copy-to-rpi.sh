#!/bin/bash
# Script para copiar arquivos para o Raspberry Pi

RPI_IP="192.168.1.40"
RPI_USER="tony"
PROJECT_DIR="wifi-manager"

echo "📡 Copiando WiFi Manager para Raspberry Pi Zero 2W"
echo "🎯 Destino: $RPI_USER@$RPI_IP"
echo ""

# Verificar conectividade
echo "🔍 Testando conexão com Raspberry Pi..."
if ! ping -c 1 $RPI_IP &> /dev/null; then
    echo "❌ Não foi possível conectar ao Raspberry Pi em $RPI_IP"
    echo "   Verifique se o Pi está ligado e conectado à rede"
    exit 1
fi
echo "✅ Raspberry Pi acessível"

# Criar diretório no Pi
echo "📁 Criando diretório no Raspberry Pi..."
ssh $RPI_USER@$RPI_IP "mkdir -p ~/$PROJECT_DIR"

# Copiar arquivos essenciais
echo "📋 Copiando arquivos de configuração..."
scp docker-compose.rpi.yml $RPI_USER@$RPI_IP:~/$PROJECT_DIR/docker-compose.yml
scp deploy-rpi.sh $RPI_USER@$RPI_IP:~/$PROJECT_DIR/
scp README-RASPBERRY-PI.md $RPI_USER@$RPI_IP:~/$PROJECT_DIR/

# Copiar diretórios
echo "📂 Copiando diretórios de configuração..."
scp -r config $RPI_USER@$RPI_IP:~/$PROJECT_DIR/ 2>/dev/null || echo "⚠️  Diretório config não encontrado (será criado)"

# Dar permissão de execução
echo "🔑 Configurando permissões..."
ssh $RPI_USER@$RPI_IP "chmod +x ~/$PROJECT_DIR/deploy-rpi.sh"

echo ""
echo "✅ Arquivos copiados com sucesso!"
echo ""
echo "🚀 Próximos passos:"
echo "1. Conectar no Raspberry Pi:"
echo "   ssh $RPI_USER@$RPI_IP"
echo ""
echo "2. Navegar para o projeto:"
echo "   cd $PROJECT_DIR"
echo ""
echo "3. Executar deploy:"
echo "   sudo ./deploy-rpi.sh"
echo ""
echo "4. Acessar interface web:"
echo "   http://$RPI_IP:8080"
echo ""
echo "📋 Comando completo:"
echo "ssh $RPI_USER@$RPI_IP 'cd $PROJECT_DIR && sudo ./deploy-rpi.sh'"
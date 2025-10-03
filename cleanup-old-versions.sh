#!/bin/bash

echo "🧹 Limpando versões antigas que não são TUPANA..."
echo "================================================="

# Parar todos os containers do wifi-manager
echo "🛑 Parando containers ativos..."
docker stop $(docker ps -q --filter "ancestor=tonymichael/wifi-manager") 2>/dev/null || true

# Remover containers antigos
echo "🗑️ Removendo containers antigos..."
docker rm $(docker ps -aq --filter "ancestor=tonymichael/wifi-manager") 2>/dev/null || true

# Lista de tags a serem removidas (versões não-TUPANA)
echo "🎯 Removendo imagens não-TUPANA..."

# Versões antigas numeradas
docker rmi tonymichael/wifi-manager:latest 2>/dev/null || true
docker rmi tonymichael/wifi-manager:1.0.0 2>/dev/null || true
docker rmi tonymichael/wifi-manager:1.0.1 2>/dev/null || true
docker rmi tonymichael/wifi-manager:1.0.2 2>/dev/null || true
docker rmi tonymichael/wifi-manager:1.0.3 2>/dev/null || true
docker rmi tonymichael/wifi-manager:1.0.4 2>/dev/null || true
docker rmi tonymichael/wifi-manager:1.0.5 2>/dev/null || true
docker rmi tonymichael/wifi-manager:1.0.6 2>/dev/null || true
docker rmi tonymichael/wifi-manager:1.0.7 2>/dev/null || true
docker rmi tonymichael/wifi-manager:1.0.8 2>/dev/null || true
docker rmi tonymichael/wifi-manager:1.0.9 2>/dev/null || true

# Versões lite antigas
docker rmi tonymichael/wifi-manager:lite 2>/dev/null || true
docker rmi tonymichael/wifi-manager:lite-v2 2>/dev/null || true
docker rmi tonymichael/wifi-manager:lite-v3 2>/dev/null || true

# Versões de desenvolvimento
docker rmi pastasemttulo5-wifi-manager:latest 2>/dev/null || true
docker rmi pastasemttulo5-wifi-manager-dev:latest 2>/dev/null || true

echo "✅ Limpeza concluída!"
echo ""
echo "🔍 Imagens TUPANA mantidas:"
docker images | grep tupana | head -10

echo ""
echo "💾 Espaço liberado:"
docker system df

echo ""
echo "🧹 Para limpeza completa do Docker (opcional):"
echo "docker system prune -a"
#!/bin/bash

echo "🧹 Removendo todas as versões TUPANA exceto tupana-v3..."
echo "======================================================="

# Parar todos os containers do wifi-manager
echo "🛑 Parando containers ativos..."
docker stop $(docker ps -q --filter "ancestor=tonymichael/wifi-manager") 2>/dev/null || true

# Remover containers antigos
echo "🗑️ Removendo containers antigos..."
docker rm $(docker ps -aq --filter "ancestor=tonymichael/wifi-manager") 2>/dev/null || true

# Remover versões TUPANA exceto v3
echo "🎯 Removendo versões TUPANA (mantendo apenas tupana-v3)..."

docker rmi tonymichael/wifi-manager:tupana-clean 2>/dev/null || true
docker rmi tonymichael/wifi-manager:tupana-v5 2>/dev/null || true
docker rmi tonymichael/wifi-manager:tupana-v4 2>/dev/null || true
docker rmi tonymichael/wifi-manager:tupana-v2 2>/dev/null || true
docker rmi tonymichael/wifi-manager:tupana 2>/dev/null || true

echo "✅ Limpeza concluída!"
echo ""
echo "🔍 Versão TUPANA mantida:"
docker images | grep tupana-v3

echo ""
echo "💾 Espaço liberado:"
docker system df

echo ""
echo "✅ Apenas tupana-v3 foi mantida conforme solicitado!"
#!/bin/bash

echo "🔄 Parando container anterior..."
docker stop tupana-wifi 2>/dev/null || true
docker rm tupana-wifi 2>/dev/null || true

echo "🏗️ Subindo TUPANA Wi-Fi Manager CLEAN..."
docker run -d \
  --name tupana-wifi \
  --privileged \
  --network host \
  -v /var/run/dbus:/var/run/dbus \
  -v /etc/wpa_supplicant:/etc/wpa_supplicant \
  -v /var/lib/dhcp:/var/lib/dhcp \
  -v /dev:/dev \
  --restart unless-stopped \
  tonymichael/wifi-manager:tupana-clean

echo "⏳ Aguardando inicialização..."
sleep 5

echo "📊 Status do container:"
docker ps -f name=tupana-wifi

echo "📝 Logs iniciais:"
docker logs tupana-wifi --tail 10

echo ""
echo "✅ TUPANA Wi-Fi Manager CLEAN em execução!"
echo "🌐 Acesse: http://192.168.1.40:8080"
echo "📱 Hotspot: TUPANA-WiFi-Config (senha: tupana123)"
echo ""
echo "🔧 Versão CLEAN:"
echo "• ✅ Seção 'Redes Salvas' mostra APENAS redes configuradas"
echo "• ✅ Lista vazia quando não há redes salvas"
echo "• ✅ Exclusão funcional mantida"
echo "• ✅ Sem confusão com redes disponíveis"
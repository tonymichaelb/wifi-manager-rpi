#!/bin/bash
# Script para coletar redes Wi-Fi reais no macOS e disponibilizar para o container

WIFI_FILE="/tmp/wifi_scan.json"

echo "🔍 Escaneando redes Wi-Fi reais no macOS..."

# Usar comando airport do macOS para escanear Wi-Fi
if command -v /System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport &> /dev/null; then
    echo "📡 Usando comando airport do macOS..."
    
    # Executar scan
    AIRPORT_OUTPUT=$(/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -s 2>/dev/null)
    
    if [ $? -eq 0 ] && [ ! -z "$AIRPORT_OUTPUT" ]; then
        echo "✅ Scan bem-sucedido, processando resultados..."
        
        # Processar saída e converter para JSON
        python3 -c "
import sys
import json
import re

lines = '''$AIRPORT_OUTPUT'''.strip().split('\n')
networks = []

for line in lines[1:]:  # Pular cabeçalho
    if not line.strip():
        continue
    
    # Dividir por espaços mas manter SSID com espaços
    parts = line.split()
    if len(parts) >= 6:
        ssid = parts[0]
        bssid = parts[1]
        try:
            rssi = int(parts[4])
            # Converter RSSI para porcentagem
            signal_strength = max(0, min(100, (rssi + 100) * 2))
        except:
            signal_strength = 50
            
        flags = ' '.join(parts[5:])
        encrypted = 'WPA' in flags or 'WEP' in flags or 'NONE' not in flags
        
        if ssid and ssid != '--':
            networks.append({
                'ssid': ssid,
                'bssid': bssid,
                'signal_strength': signal_strength,
                'encrypted': encrypted
            })

# Ordenar por força do sinal
networks.sort(key=lambda x: x['signal_strength'], reverse=True)

# Salvar em JSON
with open('$WIFI_FILE', 'w') as f:
    json.dump(networks, f, indent=2)

print(f'📝 {len(networks)} redes Wi-Fi salvas em $WIFI_FILE')
for net in networks[:5]:  # Mostrar top 5
    lock = '🔒' if net['encrypted'] else '📶'
    print(f'  {lock} {net[\"ssid\"]} ({net[\"signal_strength\"]}%)')
"
        
        echo "✅ Redes Wi-Fi reais disponíveis para o container!"
    else
        echo "❌ Falha no scan via airport"
        exit 1
    fi
else
    echo "❌ Comando airport não encontrado"
    exit 1
fi
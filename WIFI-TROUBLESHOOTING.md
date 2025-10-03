# 🔧 Solução de Problemas de Autenticação Wi-Fi

Este documento descreve os problemas comuns de autenticação Wi-Fi e suas soluções.

## 🔍 Diagnóstico Rápido

### 1. Execute o Teste de Diagnóstico
```bash
python3 test-wifi-connection.py
```

### 2. Verifique os Logs
```bash
# Logs do sistema Wi-Fi
tail -f logs/wifi-manager.log

# Logs do wpa_supplicant (se disponível)
tail -f /tmp/wpa_supplicant.log

# Logs do sistema
sudo journalctl -u NetworkManager -f
```

## ❌ Problemas Comuns e Soluções

### 1. Erro de Autenticação / Senha Incorreta

**Sintomas:**
- "authentication failed"
- "4-way handshake failed" 
- "Secrets were required"

**Possíveis Causas:**
- Senha incorreta
- Tipo de segurança incompatível
- Caracteres especiais na senha

**Soluções:**
1. **Verifique a senha:**
   - Confirme se a senha está correta
   - Teste conectar com outro dispositivo
   - Verifique se há caracteres especiais problemáticos

2. **Verifique o tipo de segurança:**
   ```bash
   # Verificar tipo de segurança da rede
   nmcli dev wifi list | grep "NOME_DA_REDE"
   ```

3. **Teste com diferentes métodos:**
   - WPA/WPA2 Personal
   - WPA3 (pode não ser suportado em hardware antigo)
   - WEP (obsoleto, evite)

### 2. Rede Não Encontrada

**Sintomas:**
- "network not found"
- "No network with SSID"

**Soluções:**
1. **Verifique a proximidade:**
   - Aproxime-se do roteador
   - Verifique se a rede está ativa

2. **Force um novo scan:**
   ```bash
   # Via interface web: clique em "Escanear Redes"
   # Via terminal:
   nmcli dev wifi rescan
   ```

3. **Verifique se a rede está oculta:**
   - Redes ocultas não aparecem no scan
   - Digite o SSID manualmente

### 3. Conexão Rejeitada

**Sintomas:**
- "association rejected"
- "Connection activation failed"

**Possíveis Causas:**
- Rede sobrecarregada
- Filtro MAC ativo
- Limite de dispositivos atingido

**Soluções:**
1. **Tente novamente mais tarde:**
   - Aguarde alguns minutos
   - Rede pode estar temporariamente sobrecarregada

2. **Verifique configurações do roteador:**
   - Filtro MAC
   - Limite de dispositivos
   - Bloqueio de novos dispositivos

### 4. Falha ao Obter IP (DHCP)

**Sintomas:**
- Conecta mas sem internet
- "failed to get IP"
- "dhcp timeout"

**Soluções:**
1. **Reinicie a conexão:**
   ```bash
   # Desconectar e reconectar
   nmcli con down "NOME_DA_REDE"
   nmcli con up "NOME_DA_REDE"
   ```

2. **Teste DHCP manualmente:**
   ```bash
   sudo dhclient -r wlan0  # Release IP
   sudo dhclient wlan0     # Request new IP
   ```

## 🛠️ Comandos Úteis para Diagnóstico

### Verificar Status da Interface
```bash
# Status geral
ip addr show wlan0

# Status Wi-Fi
iwconfig wlan0

# Conexões NetworkManager
nmcli con show
```

### Scan Manual de Redes
```bash
# NetworkManager
nmcli dev wifi list

# iwlist (mais detalhado)
sudo iwlist wlan0 scan | grep -E "(ESSID|Quality|Encryption)"
```

### Teste de Conectividade
```bash
# Ping básico
ping -c 4 8.8.8.8

# Teste DNS
nslookup google.com

# Trace route
traceroute 8.8.8.8
```

### Reset Completo da Rede
```bash
# Parar NetworkManager
sudo systemctl stop NetworkManager

# Limpar configurações
sudo rm /etc/NetworkManager/system-connections/*

# Reiniciar NetworkManager
sudo systemctl start NetworkManager
```

## 🔐 Tipos de Segurança Suportados

### ✅ Suportados
- **WPA/WPA2 Personal (PSK)** - Recomendado
- **WPA3 Personal** - Mais seguro, nem sempre suportado
- **Redes Abertas** - Sem senha

### ⚠️ Problemas Conhecidos
- **WEP** - Obsoleto, problemas de compatibilidade
- **WPA Enterprise** - Requer configuração adicional
- **Captive Portal** - Pode requerer configuração manual

## 📋 Validação de Entrada

### SSID (Nome da Rede)
- Máximo: 32 caracteres
- Evitar: aspas duplas, barras invertidas
- Caracteres especiais podem causar problemas

### Senha
- WPA mínimo: 8 caracteres
- Máximo: 63 caracteres  
- Evitar: aspas duplas, barras invertidas
- Caracteres especiais: teste se necessário

## 🚨 Quando Buscar Ajuda

Se após seguir este guia o problema persistir:

1. **Colete informações:**
   ```bash
   # Salvar logs
   journalctl -u NetworkManager > /tmp/nm-logs.txt
   dmesg | grep -i wifi > /tmp/wifi-dmesg.txt
   ```

2. **Execute diagnóstico completo:**
   ```bash
   python3 test-wifi-connection.py > /tmp/wifi-test-full.log 2>&1
   ```

3. **Informações do hardware:**
   ```bash
   lspci | grep -i network
   lsusb | grep -i wireless
   uname -a
   ```

## 📝 Logs de Exemplo

### Conexão Bem-Sucedida
```
INFO - Conectando à rede MinhaRede
INFO - NetworkManager conectou com sucesso à rede MinhaRede
INFO - Conexão estabelecida após 3 segundos
INFO - Configuração Wi-Fi salva para rede: MinhaRede
```

### Erro de Autenticação
```
ERROR - Erro NetworkManager (código 4): Secrets were required, but not provided
ERROR - Erro de autenticação - senha incorreta ou método de segurança incompatível
```

### Rede Não Encontrada
```
WARNING - Rede MinhaRede não encontrada durante scan
ERROR - Rede MinhaRede não está disponível. Execute um scan primeiro.
```

---

**💡 Dica:** Mantenha sempre o sistema atualizado para melhor compatibilidade com redes Wi-Fi modernas.
#!/usr/bin/env python3
"""
Script de teste para diagnóstico de problemas de conexão Wi-Fi
Use este script para testar e diagnosticar problemas de autenticação Wi-Fi
"""

import os
import sys
import subprocess
import json
import time
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/wifi-test.log')
    ]
)

logger = logging.getLogger(__name__)

def test_wifi_environment():
    """Testa o ambiente Wi-Fi"""
    logger.info("=== Testando Ambiente Wi-Fi ===")
    
    # Verificar interface Wi-Fi
    interfaces = []
    try:
        result = subprocess.run(['ip', 'link'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if 'wlan' in line or 'wlp' in line:
                interface = line.split(':')[1].strip()
                interfaces.append(interface)
                logger.info(f"Interface Wi-Fi encontrada: {interface}")
    except Exception as e:
        logger.error(f"Erro ao verificar interfaces: {e}")
    
    if not interfaces:
        logger.warning("Nenhuma interface Wi-Fi encontrada")
        return None
    
    return interfaces[0]

def test_network_tools():
    """Testa ferramentas de rede disponíveis"""
    logger.info("=== Testando Ferramentas de Rede ===")
    
    tools = {
        'nmcli': 'NetworkManager CLI',
        'iwlist': 'Wireless tools',
        'wpa_supplicant': 'WPA Supplicant',
        'dhclient': 'DHCP Client'
    }
    
    available_tools = {}
    for tool, description in tools.items():
        try:
            result = subprocess.run(['which', tool], capture_output=True)
            if result.returncode == 0:
                logger.info(f"✓ {description} ({tool}) disponível")
                available_tools[tool] = True
            else:
                logger.warning(f"✗ {description} ({tool}) não encontrado")
                available_tools[tool] = False
        except Exception as e:
            logger.error(f"Erro ao verificar {tool}: {e}")
            available_tools[tool] = False
    
    return available_tools

def scan_networks(interface):
    """Escaneia redes Wi-Fi"""
    logger.info("=== Escaneando Redes Wi-Fi ===")
    
    networks = []
    
    # Método 1: nmcli
    try:
        logger.info("Tentando scan com nmcli...")
        result = subprocess.run([
            'nmcli', '-t', '-f', 'SSID,SIGNAL,SECURITY', 'dev', 'wifi', 'list'
        ], capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line and ':' in line:
                    parts = line.split(':')
                    if len(parts) >= 3:
                        ssid = parts[0]
                        signal = parts[1]
                        security = parts[2]
                        if ssid:
                            networks.append({
                                'ssid': ssid,
                                'signal': signal,
                                'security': security,
                                'method': 'nmcli'
                            })
            logger.info(f"nmcli encontrou {len(networks)} redes")
    except Exception as e:
        logger.error(f"Erro com nmcli: {e}")
    
    # Método 2: iwlist
    if not networks:
        try:
            logger.info("Tentando scan com iwlist...")
            result = subprocess.run([
                'iwlist', interface, 'scan'
            ], capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                current_network = {}
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if 'Cell' in line and 'Address:' in line:
                        if current_network:
                            networks.append(current_network)
                        current_network = {'method': 'iwlist'}
                    elif 'ESSID:' in line:
                        essid = line.split('ESSID:')[1].strip().strip('"')
                        if essid and essid != '<hidden>':
                            current_network['ssid'] = essid
                    elif 'Quality=' in line:
                        import re
                        quality_match = re.search(r'Quality=(\d+)/(\d+)', line)
                        if quality_match:
                            quality = int(quality_match.group(1))
                            max_quality = int(quality_match.group(2))
                            current_network['signal'] = str(int((quality / max_quality) * 100))
                    elif 'Encryption key:' in line:
                        current_network['security'] = 'on' if 'on' in line else 'off'
                
                if current_network:
                    networks.append(current_network)
                    
                logger.info(f"iwlist encontrou {len(networks)} redes")
        except Exception as e:
            logger.error(f"Erro com iwlist: {e}")
    
    # Mostrar redes encontradas
    if networks:
        logger.info("Redes encontradas:")
        for i, network in enumerate(networks, 1):
            logger.info(f"  {i}. {network.get('ssid', 'N/A')} - "
                       f"Sinal: {network.get('signal', 'N/A')}% - "
                       f"Segurança: {network.get('security', 'N/A')} - "
                       f"Método: {network.get('method', 'N/A')}")
    else:
        logger.warning("Nenhuma rede Wi-Fi encontrada")
    
    return networks

def test_connection(interface, ssid, password=None):
    """Testa conexão a uma rede específica"""
    logger.info(f"=== Testando Conexão: {ssid} ===")
    
    # Método 1: NetworkManager
    try:
        logger.info("Tentando conexão com NetworkManager...")
        
        if password:
            cmd = ['nmcli', 'dev', 'wifi', 'connect', ssid, 'password', password, 'ifname', interface]
            log_cmd = ['nmcli', 'dev', 'wifi', 'connect', ssid, 'password', '***', 'ifname', interface]
        else:
            cmd = ['nmcli', 'dev', 'wifi', 'connect', ssid, 'ifname', interface]
            log_cmd = cmd
        
        logger.info(f"Executando: {' '.join(log_cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        logger.info(f"NetworkManager retornou código: {result.returncode}")
        if result.stdout:
            logger.info(f"Stdout: {result.stdout}")
        if result.stderr:
            logger.error(f"Stderr: {result.stderr}")
        
        if result.returncode == 0:
            logger.info("NetworkManager reportou sucesso")
            
            # Verificar conectividade
            time.sleep(5)
            if test_connectivity():
                logger.info("✓ Conexão bem-sucedida com NetworkManager")
                return True
            else:
                logger.warning("NetworkManager conectou mas sem internet")
        else:
            logger.error("NetworkManager falhou na conexão")
            
    except subprocess.TimeoutExpired:
        logger.error("Timeout na conexão NetworkManager")
    except Exception as e:
        logger.error(f"Erro NetworkManager: {e}")
    
    return False

def test_connectivity():
    """Testa conectividade com a internet"""
    logger.info("Testando conectividade...")
    
    test_hosts = ['8.8.8.8', '1.1.1.1', 'google.com']
    for host in test_hosts:
        try:
            result = subprocess.run(['ping', '-c', '2', '-W', '3', host], 
                                  capture_output=True, timeout=10)
            if result.returncode == 0:
                logger.info(f"✓ Conectividade OK com {host}")
                return True
            else:
                logger.warning(f"✗ Falha no ping para {host}")
        except Exception as e:
            logger.warning(f"Erro no teste de conectividade com {host}: {e}")
    
    logger.error("✗ Sem conectividade com a internet")
    return False

def main():
    """Função principal"""
    print("=" * 60)
    print("TESTE DE DIAGNÓSTICO WI-FI")
    print("=" * 60)
    
    logger.info("Iniciando diagnóstico Wi-Fi")
    
    # Teste 1: Ambiente
    interface = test_wifi_environment()
    if not interface:
        logger.error("Nenhuma interface Wi-Fi disponível. Abortando.")
        return
    
    # Teste 2: Ferramentas
    tools = test_network_tools()
    if not any(tools.values()):
        logger.error("Nenhuma ferramenta de rede disponível. Abortando.")
        return
    
    # Teste 3: Scan
    networks = scan_networks(interface)
    if not networks:
        logger.warning("Nenhuma rede encontrada para teste")
        return
    
    # Teste 4: Conexão interativa
    print("\nRedes disponíveis para teste:")
    for i, network in enumerate(networks[:5], 1):  # Mostrar apenas as 5 primeiras
        print(f"  {i}. {network.get('ssid', 'N/A')} - {network.get('signal', 'N/A')}%")
    
    try:
        choice = input("\nEscolha uma rede para testar (número) ou 'q' para sair: ").strip()
        
        if choice.lower() == 'q':
            logger.info("Teste cancelado pelo usuário")
            return
        
        network_index = int(choice) - 1
        if 0 <= network_index < len(networks):
            selected_network = networks[network_index]
            ssid = selected_network['ssid']
            
            password = None
            if selected_network.get('security', '') not in ['off', 'NONE', '']:
                password = input(f"Digite a senha para '{ssid}' (deixe vazio para rede aberta): ").strip()
                if not password:
                    password = None
            
            # Executar teste
            success = test_connection(interface, ssid, password)
            
            if success:
                print(f"\n✓ SUCESSO: Conectado à rede '{ssid}'")
            else:
                print(f"\n✗ FALHA: Não foi possível conectar à rede '{ssid}'")
                print("Verifique os logs em /tmp/wifi-test.log para detalhes")
        else:
            logger.error("Seleção inválida")
    
    except KeyboardInterrupt:
        logger.info("Teste interrompido pelo usuário")
    except ValueError:
        logger.error("Entrada inválida")
    except Exception as e:
        logger.error(f"Erro durante teste interativo: {e}")

if __name__ == "__main__":
    main()
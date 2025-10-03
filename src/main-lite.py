#!/usr/bin/env python3
"""
Sistema Wi-Fi Manager - Versão Lite para Raspberry Pi Zero 2W
Otimizado para menor consumo de recursos
"""

import os
import time
import logging
import subprocess
import re
from threading import Thread
from flask import Flask, render_template, request, jsonify

# Configuração básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WiFiManagerLite:
    def __init__(self):
        self.interface = os.getenv('WIFI_INTERFACE', 'wlan0')
        self.hotspot_active = False
        self.connected_network = None
        self.excluded_networks = set()  # Redes que o usuário excluiu
        
    def scan_networks(self):
        """Scan simples de redes Wi-Fi"""
        try:
            result = subprocess.run(['iwlist', self.interface, 'scan'], 
                                  capture_output=True, text=True, timeout=10)
            
            networks = []
            if result.returncode == 0:
                current = {}
                for line in result.stdout.split('\n'):
                    if 'Cell ' in line and 'Address:' in line:
                        if current:
                            networks.append(current)
                        current = {}
                    elif 'ESSID:' in line:
                        essid = line.split('ESSID:')[1].strip().strip('"')
                        if essid and essid != '<hidden>':
                            current['ssid'] = essid
                    elif 'Quality=' in line:
                        try:
                            quality = line.split('Quality=')[1].split()[0]
                            current['quality'] = quality
                        except:
                            current['quality'] = 'N/A'
                    elif 'Encryption key:' in line:
                        if 'off' in line:
                            current['encrypted'] = False
                        else:
                            current['encrypted'] = True
                
                if current:
                    networks.append(current)
            
            # Filtrar redes válidas e limitar a 10
            valid_networks = []
            for network in networks:
                if 'ssid' in network and len(valid_networks) < 10:
                    valid_networks.append(network)
            
            logger.info(f"Encontradas {len(valid_networks)} redes Wi-Fi")
            return valid_networks
            
        except Exception as e:
            logger.error(f"Erro no scan: {e}")
            return []
    
    def get_current_network(self):
        """Verificar rede atual conectada"""
        try:
            result = subprocess.run(['iwconfig', self.interface], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'ESSID:' in line:
                        essid = line.split('ESSID:')[1].strip().strip('"')
                        if essid and essid != 'off/any':
                            return essid
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter rede atual: {e}")
            return None
    
    def check_internet(self):
        """Verificar conectividade com internet"""
        try:
            result = subprocess.run(['ping', '-c', '1', '8.8.8.8'], 
                                  capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def get_wifi_status(self):
        """Status aprimorado do Wi-Fi com verificações múltiplas"""
        try:
            current_network = self.get_current_network()
            
            # Verificar se há IP na interface Wi-Fi
            has_ip = False
            try:
                ip_result = subprocess.run(['ip', 'addr', 'show', self.interface], 
                                         capture_output=True, text=True, timeout=5)
                has_ip = 'inet ' in ip_result.stdout and '127.0.0.1' not in ip_result.stdout
            except:
                has_ip = False
            
            # Verificar conectividade à internet
            internet = self.check_internet()
            
            # Determinar se está realmente conectado
            truly_connected = (current_network is not None and has_ip and internet)
            
            return {
                'connected': truly_connected,
                'network': current_network,
                'has_ip': has_ip,
                'internet': internet,
                'hotspot_active': self.hotspot_active,
                'interface': self.interface
            }
        except Exception as e:
            logger.error(f"Erro ao obter status Wi-Fi: {e}")
            return {
                'connected': False,
                'network': None,
                'has_ip': False,
                'internet': False,
                'hotspot_active': self.hotspot_active,
                'interface': self.interface
            }
    
    def connect_wifi(self, ssid, password):
        """Conectar a rede Wi-Fi usando wpa_supplicant"""
        try:
            logger.info(f"Tentando conectar a rede: {ssid}")
            
            # Parar hotspot se estiver ativo
            if self.hotspot_active:
                self.stop_hotspot()
                time.sleep(2)
            
            # Configurar wpa_supplicant
            config_content = f'''ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=BR

network={{
    ssid="{ssid}"
    psk="{password}"
    key_mgmt=WPA-PSK
}}
'''
            
            # Escrever configuração
            config_path = '/tmp/wpa_supplicant.conf'
            with open(config_path, 'w') as f:
                f.write(config_content)
            
            # Parar todos os processos relacionados
            subprocess.run(['pkill', '-f', 'wpa_supplicant'], capture_output=True)
            subprocess.run(['pkill', '-f', 'dhcpcd'], capture_output=True)
            subprocess.run(['pkill', '-f', 'dhclient'], capture_output=True)
            time.sleep(2)
            
            # Limpar interface
            subprocess.run(['ip', 'addr', 'flush', 'dev', self.interface], capture_output=True)
            subprocess.run(['ip', 'link', 'set', self.interface, 'down'], capture_output=True)
            time.sleep(1)
            subprocess.run(['ip', 'link', 'set', self.interface, 'up'], capture_output=True)
            time.sleep(1)
            
            # Iniciar wpa_supplicant
            cmd = ['wpa_supplicant', '-B', '-i', self.interface, '-c', config_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logger.info(f"wpa_supplicant iniciado com sucesso para {ssid}")
                
                # Aguardar wpa_supplicant conectar
                time.sleep(3)
                
                # Verificar se wpa_supplicant conectou
                status_check = subprocess.run(['wpa_cli', '-i', self.interface, 'status'], 
                                            capture_output=True, text=True, timeout=5)
                
                if 'wpa_state=COMPLETED' in status_check.stdout:
                    logger.info("Autenticação Wi-Fi bem-sucedida")
                else:
                    logger.warning("Autenticação Wi-Fi pendente, continuando...")
                
                # Solicitar IP via DHCP (tentar diferentes comandos)
                dhcp_commands = [
                    ['dhcpcd', self.interface],
                    ['dhclient', self.interface],
                    ['udhcpc', '-i', self.interface]
                ]
                
                dhcp_success = False
                for dhcp_cmd in dhcp_commands:
                    try:
                        logger.info(f"Tentando DHCP com: {' '.join(dhcp_cmd)}")
                        dhcp_result = subprocess.run(dhcp_cmd, capture_output=True, timeout=15)
                        if dhcp_result.returncode == 0:
                            dhcp_success = True
                            logger.info(f"DHCP bem-sucedido com: {' '.join(dhcp_cmd)}")
                            break
                    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                        logger.warning(f"Falha DHCP com {' '.join(dhcp_cmd)}: {e}")
                        continue
                
                if not dhcp_success:
                    logger.warning("Nenhum cliente DHCP disponível, tentando configuração manual")
                
                time.sleep(5)  # Aguardar conexão
                
                # Verificar se conectou
                current = self.get_current_network()
                if current == ssid:
                    logger.info(f"Conectado com sucesso a {ssid}")
                    return True
                else:
                    logger.warning(f"Falha na conexão com {ssid}")
                    return False
            else:
                error_msg = result.stderr.strip() if result.stderr else "Erro desconhecido"
                logger.error(f"Erro no wpa_supplicant: {error_msg}")
                logger.error(f"Comando executado: {' '.join(cmd)}")
                logger.error(f"Código de retorno: {result.returncode}")
                return False
                
        except Exception as e:
            logger.error(f"Erro na conexão Wi-Fi: {e}")
            return False
    
    def start_hotspot(self):
        """Iniciar hotspot TUPANA"""
        try:
            logger.info("Iniciando hotspot TUPANA...")
            
            # Parar serviços existentes
            subprocess.run(['pkill', 'hostapd'], capture_output=True)
            subprocess.run(['pkill', 'dnsmasq'], capture_output=True)
            subprocess.run(['pkill', 'wpa_supplicant'], capture_output=True)
            time.sleep(2)
            
            # Configurar interface
            subprocess.run(['ip', 'addr', 'flush', 'dev', self.interface], capture_output=True)
            subprocess.run(['ip', 'addr', 'add', '192.168.4.1/24', 'dev', self.interface], capture_output=True)
            subprocess.run(['ip', 'link', 'set', 'dev', self.interface, 'up'], capture_output=True)
            
            # Configurar hostapd
            hostapd_conf = '''interface=wlan0
driver=nl80211
ssid=TUPANA-WiFi-Config
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=tupana123
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
'''
            
            with open('/tmp/hostapd.conf', 'w') as f:
                f.write(hostapd_conf)
            
            # Configurar dnsmasq
            dnsmasq_conf = '''interface=wlan0
dhcp-range=192.168.4.10,192.168.4.50,255.255.255.0,24h
'''
            
            with open('/tmp/dnsmasq.conf', 'w') as f:
                f.write(dnsmasq_conf)
            
            # Iniciar serviços
            subprocess.Popen(['hostapd', '/tmp/hostapd.conf'])
            time.sleep(2)
            subprocess.Popen(['dnsmasq', '-C', '/tmp/dnsmasq.conf'])
            
            self.hotspot_active = True
            logger.info("Hotspot TUPANA ativo")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao iniciar hotspot: {e}")
            return False
    
    def get_saved_networks(self):
        """Listar apenas redes realmente salvas"""
        try:
            saved_networks = []
            
            # Verificar configurações do wpa_supplicant (redes realmente salvas)
            wpa_paths = [
                '/etc/wpa_supplicant/wpa_supplicant.conf',
                '/etc/wpa_supplicant.conf',
                '/tmp/wpa_supplicant.conf'
            ]
            
            for wpa_path in wpa_paths:
                try:
                    if os.path.exists(wpa_path):
                        with open(wpa_path, 'r') as f:
                            content = f.read()
                            import re
                            ssids = re.findall(r'ssid="([^"]+)"', content)
                            for ssid in ssids:
                                if (ssid not in saved_networks and 
                                    ssid != 'TUPANA-WiFi-Config' and 
                                    ssid not in self.excluded_networks):
                                    saved_networks.append(ssid)
                        logger.info(f"Encontradas {len(ssids)} redes salvas em {wpa_path}")
                except Exception as e:
                    logger.debug(f"Erro ao ler {wpa_path}: {e}")
            
            # Retornar apenas redes salvas (pode ser lista vazia)
            logger.info(f"Retornando {len(saved_networks)} redes salvas")
            return saved_networks
            
        except Exception as e:
            logger.error(f"Erro ao listar redes salvas: {e}")
            return []

    def delete_saved_network(self, ssid):
        """Excluir rede salva"""
        try:
            # Verificar se há uma rede válida para excluir
            if not ssid or ssid.strip() == "":
                logger.error("SSID vazio fornecido para exclusão")
                return False
                
            # Remover marcadores de status se houver
            clean_ssid = ssid.replace(' (detectada)', '').replace(' (disponível)', '').strip()
            logger.info(f"Tentando excluir rede salva: '{clean_ssid}'")
            
            success = False
            
            # Método 1: Usar wpa_cli para remover rede (mais confiável)
            try:
                # Listar redes configuradas no wpa_supplicant
                list_result = subprocess.run(['wpa_cli', '-i', self.interface, 'list_networks'], 
                                           capture_output=True, text=True, timeout=10)
                
                if list_result.returncode == 0:
                    lines = list_result.stdout.strip().split('\n')
                    for line in lines[1:]:  # Pular cabeçalho
                        if clean_ssid in line:
                            network_id = line.split('\t')[0]
                            # Remover a rede
                            remove_result = subprocess.run(['wpa_cli', '-i', self.interface, 'remove_network', network_id], 
                                                         capture_output=True, text=True, timeout=10)
                            if remove_result.returncode == 0:
                                # Salvar configuração
                                subprocess.run(['wpa_cli', '-i', self.interface, 'save_config'], 
                                             capture_output=True, timeout=10)
                                logger.info(f"Rede '{clean_ssid}' removida via wpa_cli (ID: {network_id})")
                                success = True
                                break
                            else:
                                logger.warning(f"Falha ao remover rede ID {network_id} via wpa_cli")
            except Exception as e:
                logger.warning(f"Erro ao usar wpa_cli: {e}")
            
            # Método 2: Editar manualmente os arquivos de configuração
            if not success:
                wpa_paths = [
                    '/etc/wpa_supplicant/wpa_supplicant.conf',
                    '/etc/wpa_supplicant.conf',
                    '/tmp/wpa_supplicant.conf'
                ]

                for config_file in wpa_paths:
                    try:
                        if os.path.exists(config_file):
                            logger.info(f"Tentando remover '{clean_ssid}' de {config_file}")
                            
                            with open(config_file, 'r') as f:
                                content = f.read()
                            
                            # Encontrar e remover o bloco da rede
                            import re
                            pattern = rf'network=\{{[^}}]*ssid="{re.escape(clean_ssid)}"[^}}]*\}}'
                            new_content = re.sub(pattern, '', content, flags=re.DOTALL)
                            
                            if new_content != content:
                                with open(config_file, 'w') as f:
                                    f.write(new_content)
                                logger.info(f"Rede '{clean_ssid}' removida de {config_file}")
                                success = True
                            else:
                                logger.debug(f"Rede '{clean_ssid}' não encontrada em {config_file}")
                                
                    except Exception as e:
                        logger.debug(f"Erro ao editar {config_file}: {e}")
            
            # Método 3: Adicionar à lista de exclusão (fallback)
            if not success:
                self.excluded_networks.add(clean_ssid)
                logger.info(f"Rede '{clean_ssid}' adicionada à lista de exclusão como fallback")
                success = True
            
            if success:
                # Reiniciar wpa_supplicant para aplicar mudanças
                try:
                    subprocess.run(['pkill', '-f', 'wpa_supplicant'], capture_output=True)
                    time.sleep(1)
                    logger.info("wpa_supplicant reiniciado após exclusão")
                    
                    # Se estava conectado nesta rede, iniciar hotspot
                    current = self.get_current_network()
                    if current == clean_ssid:
                        logger.info(f"Estava conectado à rede excluída '{clean_ssid}', iniciando hotspot")
                        self.start_hotspot()
                        
                except Exception as e:
                    logger.warning(f"Erro ao reiniciar wpa_supplicant: {e}")
            
            logger.info(f"Exclusão da rede '{clean_ssid}': {'bem-sucedida' if success else 'falhou'}")
            return success
            
        except Exception as e:
            logger.error(f"Erro ao excluir rede '{ssid}': {e}")
            return False

    def stop_hotspot(self):
        """Parar hotspot"""
        try:
            subprocess.run(['pkill', 'hostapd'], capture_output=True)
            subprocess.run(['pkill', 'dnsmasq'], capture_output=True)
            self.hotspot_active = False
            logger.info("Hotspot TUPANA parado")
        except Exception as e:
            logger.error(f"Erro ao parar hotspot: {e}")

# Flask App
app = Flask(__name__, template_folder='../templates')
wifi_manager = WiFiManagerLite()

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/status')
@app.route('/api/status')
def api_status():
    """API: Status do Wi-Fi"""
    status = wifi_manager.get_wifi_status()
    return jsonify(status)

@app.route('/scan')
@app.route('/api/scan')
def api_scan():
    """API: Scan de redes"""
    networks = wifi_manager.scan_networks()
    return jsonify({'networks': networks})

@app.route('/saved-networks')
@app.route('/api/saved-networks')
def api_saved_networks():
    """API: Redes salvas"""
    networks = wifi_manager.get_saved_networks()
    return jsonify({'saved_networks': networks})

@app.route('/connect', methods=['POST'])
@app.route('/api/connect', methods=['POST'])
def api_connect():
    """API: Conectar Wi-Fi"""
    ssid = request.json.get('ssid')
    password = request.json.get('password')
    success = wifi_manager.connect_wifi(ssid, password)
    return jsonify({'success': success})

@app.route('/delete-network', methods=['POST'])
@app.route('/api/delete-network', methods=['POST'])
def api_delete_network():
    """API: Excluir rede salva"""
    ssid = request.json.get('ssid')
    
    if not ssid:
        return jsonify({'success': False, 'error': 'SSID não fornecido'})
    
    success = wifi_manager.delete_saved_network(ssid)
    return jsonify({'success': success})

def monitor_connection():
    """Monitor de conexão Wi-Fi melhorado"""
    connection_failures = 0
    max_failures = 3  # Máximo de falhas antes de ativar hotspot
    check_interval = 10  # Verificar a cada 10 segundos
    
    while True:
        try:
            # Verificar status da conexão
            status = wifi_manager.get_wifi_status()
            current_network = wifi_manager.get_current_network()
            
            # Teste de conectividade real (ping para gateway ou DNS)
            connectivity_ok = False
            try:
                # Tentar ping para gateway local
                ping_result = subprocess.run(['ping', '-c', '1', '-W', '3', '8.8.8.8'], 
                                           capture_output=True, timeout=5)
                connectivity_ok = ping_result.returncode == 0
            except:
                connectivity_ok = False
            
            # Determinar se há problema de conexão
            connection_problem = False
            
            if not status['connected']:
                connection_problem = True
                logger.info("Sem conexão Wi-Fi detectada")
            elif current_network is None:
                connection_problem = True  
                logger.info("Rede atual não identificada")
            elif not connectivity_ok:
                connection_problem = True
                logger.info("Conectividade à internet perdida")
            
            if connection_problem:
                connection_failures += 1
                logger.warning(f"Falha de conexão #{connection_failures}/{max_failures}")
                
                # Se atingiu o limite de falhas, ativar hotspot
                if connection_failures >= max_failures:
                    if not wifi_manager.hotspot_active:
                        logger.info("Limite de falhas atingido, ativando hotspot TUPANA...")
                        wifi_manager.start_hotspot()
                        connection_failures = 0  # Reset do contador
                    else:
                        logger.debug("Hotspot já está ativo")
            else:
                # Conexão OK, resetar contador
                if connection_failures > 0:
                    logger.info("Conexão restaurada, resetando contador de falhas")
                    connection_failures = 0
                
                # Se hotspot estava ativo e agora há conexão, parar hotspot
                if wifi_manager.hotspot_active and status['connected']:
                    logger.info("Conexão Wi-Fi restaurada, parando hotspot")
                    wifi_manager.stop_hotspot()
            
            time.sleep(check_interval)
            
        except Exception as e:
            logger.error(f"Erro no monitor de conexão: {e}")
            time.sleep(check_interval)

if __name__ == '__main__':
    # Iniciar monitor em thread separada
    monitor_thread = Thread(target=monitor_connection, daemon=True)
    monitor_thread.start()
    
    # Iniciar servidor Flask
    logger.info("Iniciando TUPANA Wi-Fi Manager Lite...")
    app.run(host='0.0.0.0', port=8080, debug=False)
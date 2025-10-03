#!/usr/bin/env python3
"""
Módulo para monitoramento de conexão Wi-Fi
"""

import os
import subprocess
import logging
import time
import re
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

class WiFiMonitor:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.interface = os.getenv('WIFI_INTERFACE', 'wlan0')
        self.demo_mode = os.getenv('DEMO_MODE', 'false').lower() == 'true'
        
    def is_connected(self) -> bool:
        """Verifica se está conectado a uma rede Wi-Fi"""
        try:
            # Em modo demo, simular comportamento
            if self.demo_mode:
                return False  # Simula desconectado para ativar modo demo
                
            # Verificar se a interface está up
            result = subprocess.run(['ip', 'link', 'show', self.interface], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode != 0:
                if not self.demo_mode:  # Só log warning se não for demo
                    logger.warning(f"Interface {self.interface} não encontrada")
                return False
                
            if 'state UP' not in result.stdout:
                logger.debug(f"Interface {self.interface} está down")
                return False
                
            # Verificar se tem IP
            result = subprocess.run(['ip', 'addr', 'show', self.interface], 
                                  capture_output=True, text=True, timeout=5)
            
            if 'inet ' not in result.stdout:
                logger.debug(f"Interface {self.interface} sem IP")
                return False
                
            # Testar conectividade
            return self.test_connectivity()
            
        except subprocess.TimeoutExpired:
            logger.error("Timeout ao verificar conexão Wi-Fi")
            return False
        except Exception as e:
            logger.error(f"Erro ao verificar conexão Wi-Fi: {e}")
            return False
            
    def test_connectivity(self) -> bool:
        """Testa conectividade com a internet"""
        test_hosts = ['8.8.8.8', '1.1.1.1', 'google.com']
        
        for host in test_hosts:
            try:
                result = subprocess.run(['ping', '-c', '1', '-W', '3', host], 
                                      capture_output=True, timeout=5)
                if result.returncode == 0:
                    return True
            except (subprocess.TimeoutExpired, Exception):
                continue
                
        logger.warning("Falha nos testes de conectividade")
        return False
        
    def scan_networks(self) -> List[Dict]:
        """Escaneia redes Wi-Fi disponíveis"""
        try:
            # Primeiro, tentar scan real mesmo em modo demo
            real_networks = self._try_real_scan()
            
            # Se conseguiu scan real, usar essas redes
            if real_networks:
                logger.info(f"Encontradas {len(real_networks)} redes Wi-Fi reais")
                return real_networks
            
            # Se em modo demo e não conseguiu scan real, usar redes realistas
            if self.demo_mode:
                logger.debug("[DEMO] Usando redes Wi-Fi realistas (scan real não disponível)")
                return self._get_realistic_demo_networks()
            
            # Modo produção sem redes encontradas
            logger.warning("Nenhuma rede Wi-Fi encontrada")
            return []
            
        except Exception as e:
            if not self.demo_mode:
                logger.error(f"Erro ao escanear redes Wi-Fi: {e}")
            else:
                logger.debug(f"[DEMO] Erro esperado ao escanear: {e}")
            return self._get_realistic_demo_networks() if self.demo_mode else []
    
    def _get_realistic_demo_networks(self) -> List[Dict]:
        """Retorna redes Wi-Fi realistas para demonstração"""
        import random
        
        # Nomes de redes comuns e realistas
        realistic_ssids = [
            "HOME_WiFi", "WiFi_Casa", "Minha_Rede", "Internet_Casa",
            "TP-Link_5G", "NET_2.4G", "Vivo-Fibra", "Claro_WiFi",
            "DESKTOP-PC", "iPhone_Hotspot", "Samsung_Mobile",
            "Cafe_WiFi", "Escritorio_5G", "Neighbor_WiFi"
        ]
        
        networks = []
        num_networks = random.randint(4, 8)  # Entre 4 e 8 redes
        
        for i in range(num_networks):
            ssid = random.choice(realistic_ssids)
            if ssid not in [net['ssid'] for net in networks]:  # Evitar duplicatas
                networks.append({
                    'ssid': ssid,
                    'bssid': f"{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}",
                    'signal_strength': random.randint(20, 95),
                    'encrypted': random.choice([True, True, True, False])  # 75% com senha
                })
        
        # Sempre incluir algumas redes padrão
        default_networks = [
            {
                'ssid': 'WiFi_Demo_Network',
                'bssid': '00:11:22:33:44:55',
                'signal_strength': 85,
                'encrypted': True
            },
            {
                'ssid': 'OpenWiFi_Guest',
                'bssid': '00:11:22:33:44:66',
                'signal_strength': 70,
                'encrypted': False
            }
        ]
        
        # Adicionar redes padrão se não existirem
        for default_net in default_networks:
            if default_net['ssid'] not in [net['ssid'] for net in networks]:
                networks.append(default_net)
        
        # Ordenar por força do sinal
        networks.sort(key=lambda x: x['signal_strength'], reverse=True)
        
        return networks[:10]  # Máximo 10 redes
    
    def _try_real_scan(self) -> List[Dict]:
        """Tenta fazer scan real das redes Wi-Fi"""
        try:
            # Método 1: Tentar ler arquivo compartilhado com redes reais (para macOS)
            real_networks = self._try_shared_wifi_file()
            if real_networks:
                return real_networks
            
            # Método 2: Verificar se temos acesso a interfaces Wi-Fi do host
            for interface in ['wlan0', 'wlp2s0', 'wlp3s0', 'en0', 'en1']:
                try:
                    result = subprocess.run(['iwlist', interface, 'scan'], 
                                          capture_output=True, text=True, timeout=15)
                    
                    if result.returncode == 0 and result.stdout:
                        networks = self._parse_scan_results(result.stdout)
                        if networks:
                            logger.info(f"Scan real bem-sucedido via interface {interface}")
                            return networks
                except:
                    continue
            
            # Método 3: Tentar com nmcli (NetworkManager)
            try:
                result = subprocess.run(['nmcli', '-t', '-f', 'SSID,SIGNAL,SECURITY', 'dev', 'wifi'], 
                                      capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0 and result.stdout:
                    networks = self._parse_nmcli_results(result.stdout)
                    if networks:
                        logger.info("Scan real bem-sucedido via nmcli")
                        return networks
            except:
                pass
            
            # Método 4: Tentar comando específico do macOS (via volume mount)
            try:
                result = subprocess.run(['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport', '-s'], 
                                      capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0 and result.stdout:
                    networks = self._parse_macos_airport_results(result.stdout)
                    if networks:
                        logger.info("Scan real bem-sucedido via airport (macOS)")
                        return networks
            except:
                pass
                
            return []
            
        except Exception as e:
            logger.debug(f"Falha no scan real: {e}")
            return []
    
    def _try_shared_wifi_file(self) -> List[Dict]:
        """Tenta ler arquivo compartilhado com redes Wi-Fi reais"""
        try:
            wifi_file_paths = [
                '/tmp/wifi_scan.json',
                '/shared/wifi_scan.json', 
                '/app/shared/wifi_scan.json',
                '/var/tmp/wifi_scan.json'
            ]
            
            for file_path in wifi_file_paths:
                try:
                    if os.path.exists(file_path):
                        with open(file_path, 'r') as f:
                            import json
                            data = json.load(f)
                            if data and isinstance(data, list):
                                logger.info(f"Redes Wi-Fi reais carregadas de {file_path}")
                                return data
                except:
                    continue
            
            return []
        except Exception as e:
            logger.debug(f"Erro ao ler arquivo de Wi-Fi compartilhado: {e}")
            return []
    
    def _parse_macos_airport_results(self, airport_output: str) -> List[Dict]:
        """Parse dos resultados do comando airport do macOS"""
        networks = []
        
        lines = airport_output.strip().split('\n')
        if len(lines) < 2:  # Primeira linha é cabeçalho
            return []
            
        for line in lines[1:]:  # Pular cabeçalho
            if not line.strip():
                continue
                
            # Formato típico do airport:
            # SSID BSSID             Channel  CC  RSSI  Flags
            parts = line.split()
            if len(parts) >= 6:
                ssid = parts[0]
                bssid = parts[1] if len(parts) > 1 else "unknown"
                try:
                    rssi = int(parts[4]) if len(parts) > 4 else -50
                    # Converter RSSI para porcentagem (RSSI vai de -100 a -20 tipicamente)
                    signal_strength = max(0, min(100, (rssi + 100) * 2))
                except:
                    signal_strength = 50
                    
                flags = ' '.join(parts[5:]) if len(parts) > 5 else ""
                encrypted = 'WPA' in flags or 'WEP' in flags or 'NONE' not in flags
                
                if ssid and ssid != '--':
                    networks.append({
                        'ssid': ssid,
                        'bssid': bssid,
                        'signal_strength': signal_strength,
                        'encrypted': encrypted
                    })
        
        return networks
            
    def _parse_scan_results(self, scan_output: str) -> List[Dict]:
        """Parse dos resultados do scan Wi-Fi"""
        networks = []
        current_network = {}
        
        for line in scan_output.split('\n'):
            line = line.strip()
            
            if 'Cell ' in line and 'Address:' in line:
                if current_network:
                    networks.append(current_network)
                current_network = {'bssid': line.split('Address: ')[1]}
                
            elif 'ESSID:' in line:
                essid = line.split('ESSID:')[1].strip().strip('"')
                if essid and essid != '<hidden>':
                    current_network['ssid'] = essid
                    
            elif 'Quality=' in line:
                quality_match = re.search(r'Quality=(\d+)/(\d+)', line)
                if quality_match:
                    quality = int(quality_match.group(1))
                    max_quality = int(quality_match.group(2))
                    current_network['signal_strength'] = int((quality / max_quality) * 100)
                    
            elif 'Encryption key:' in line:
                current_network['encrypted'] = 'on' in line
                
        if current_network:
            networks.append(current_network)
            
        # Filtrar redes sem SSID
        return [net for net in networks if 'ssid' in net]
        
    def _parse_nmcli_results(self, nmcli_output: str) -> List[Dict]:
        """Parse dos resultados do nmcli"""
        networks = []
        
        for line in nmcli_output.strip().split('\n'):
            if not line:
                continue
                
            parts = line.split(':')
            if len(parts) >= 3:
                ssid = parts[0].strip()
                try:
                    signal = int(parts[1].strip()) if parts[1].strip() else 0
                except:
                    signal = 0
                    
                security = parts[2].strip() if len(parts) > 2 else ''
                encrypted = security and security != '--'
                
                if ssid and ssid != '--':
                    networks.append({
                        'ssid': ssid,
                        'signal_strength': signal,
                        'encrypted': encrypted,
                        'bssid': f"nmcli:{hash(ssid) % 1000000:06d}"  # BSSID simulado baseado no SSID
                    })
        
        return networks
        
    def is_network_available(self, ssid: str) -> bool:
        """Verifica se uma rede específica está disponível"""
        networks = self.scan_networks()
        return any(net.get('ssid') == ssid for net in networks)
        
    def connect(self, ssid: str = None, password: str = None) -> bool:
        """Conecta a uma rede Wi-Fi"""
        try:
            if not ssid:
                # Usar configuração salva
                wifi_config = self.config_manager.get_wifi_config()
                if not wifi_config:
                    if not self.demo_mode:
                        logger.error("Nenhuma configuração Wi-Fi encontrada")
                    return False
                ssid = wifi_config.get('ssid')
                password = wifi_config.get('password')
                
            if not ssid:
                if not self.demo_mode:
                    logger.error("SSID não fornecido")
                return False
            
            # Validar configuração antes de tentar conectar
            if not self.config_manager.validate_wifi_config(ssid, password):
                logger.error("Configuração Wi-Fi inválida - falha na validação")
                return False
            
            # Em modo demo, simular conexão
            if self.demo_mode:
                logger.info(f"[DEMO] Simulando conexão à rede {ssid}")
                time.sleep(2)  # Simular tempo de conexão
                logger.info(f"[DEMO] Conexão simulada com sucesso à rede {ssid}")
                return True
                
            logger.info(f"Iniciando conexão à rede: {ssid}")
            
            # Verificar se a rede está disponível
            if not self.is_network_available(ssid):
                logger.error(f"Rede {ssid} não está disponível. Execute um scan primeiro.")
                return False
                
            try:
                # Método 1: Usar NetworkManager para conectar
                success = self._connect_with_networkmanager(ssid, password)
                if success:
                    return success
                    
                # Método 2: Fallback para wpa_supplicant se NetworkManager falhar
                logger.warning("NetworkManager falhou, tentando wpa_supplicant...")
                return self._connect_with_wpa_supplicant(ssid, password)
                
            except subprocess.TimeoutExpired:
                logger.error("Timeout na conexão Wi-Fi")
                return False
            except Exception as e:
                logger.error(f"Erro durante tentativa de conexão: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Erro geral durante conexão Wi-Fi: {e}")
            return False
    
    def _connect_with_networkmanager(self, ssid: str, password: str = None) -> bool:
        """Conecta usando NetworkManager"""
        try:
            logger.info(f"Tentando conexão via NetworkManager para {ssid}")
            
            # Verificar se NetworkManager está disponível
            result = subprocess.run(['which', 'nmcli'], capture_output=True)
            if result.returncode != 0:
                logger.warning("NetworkManager (nmcli) não encontrado")
                return False
            
            # Desconectar conexões existentes primeiro
            try:
                subprocess.run(['nmcli', 'connection', 'down', 'id', ssid], 
                             capture_output=True, timeout=10)
            except:
                pass  # Ignorar erro se conexão não existir
            
            # Comando de conexão
            if password:
                cmd = ['nmcli', 'dev', 'wifi', 'connect', ssid, 'password', password, 'ifname', self.interface]
                log_cmd = ['nmcli', 'dev', 'wifi', 'connect', ssid, 'password', '***', 'ifname', self.interface]
            else:
                cmd = ['nmcli', 'dev', 'wifi', 'connect', ssid, 'ifname', self.interface]
                log_cmd = cmd
            
            logger.info(f"Executando: {' '.join(log_cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
            
            if result.returncode == 0:
                logger.info(f"NetworkManager: conexão iniciada para {ssid}")
                
                # Aguardar e verificar conexão estabelecida
                for i in range(30):  # 30 segundos timeout
                    time.sleep(1)
                    if self._check_network_connection():
                        logger.info(f"Conexão estabelecida após {i+1} segundos")
                        # Salvar configuração apenas se conexão bem-sucedida
                        wifi_config = self.config_manager.get_wifi_config()
                        if not wifi_config or wifi_config.get('ssid') != ssid:
                            self.config_manager.save_wifi_config(ssid, password)
                        return True
                
                logger.error("NetworkManager conectou mas sem conectividade verificada")
                return False
            else:
                error_msg = result.stderr.strip()
                logger.error(f"Erro NetworkManager (código {result.returncode}): {error_msg}")
                
                # Analisar tipo de erro para dar feedback específico
                if "Secrets were required" in error_msg or "authentication" in error_msg.lower():
                    logger.error("Erro de autenticação - senha incorreta ou método de segurança incompatível")
                elif "No network with SSID" in error_msg:
                    logger.error("Rede não encontrada - execute um novo scan")
                elif "Connection activation failed" in error_msg:
                    logger.error("Falha na ativação da conexão - verifique configurações de rede")
                
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Timeout na conexão via NetworkManager")
            return False
        except Exception as e:
            logger.error(f"Erro no método NetworkManager: {e}")
            return False
    
    def _check_network_connection(self) -> bool:
        """Verifica se a conexão de rede está funcionando"""
        try:
            # Verificar se tem IP
            result = subprocess.run(['ip', 'addr', 'show', self.interface], 
                                  capture_output=True, text=True, timeout=5)
            
            if 'inet ' not in result.stdout:
                return False
                
            # Teste rápido de conectividade
            result = subprocess.run(['ping', '-c', '1', '-W', '2', '8.8.8.8'], 
                                  capture_output=True, timeout=5)
            
            return result.returncode == 0
            
        except:
            return False
    
    def _connect_with_wpa_supplicant(self, ssid: str, password: str = None) -> bool:
        """Método alternativo usando wpa_supplicant diretamente"""
        try:
            logger.info(f"Tentando conexão via wpa_supplicant para {ssid}")
            
            # Verificar se wpa_supplicant está disponível
            result = subprocess.run(['which', 'wpa_supplicant'], capture_output=True)
            if result.returncode != 0:
                logger.warning("wpa_supplicant não encontrado")
                return False
            
            # Parar processos wpa_supplicant existentes
            try:
                subprocess.run(['pkill', '-f', f'wpa_supplicant.*{self.interface}'], 
                             capture_output=True, timeout=5)
                time.sleep(2)
            except:
                pass
            
            # Preparar interface
            try:
                subprocess.run(['ip', 'link', 'set', self.interface, 'up'], 
                             capture_output=True, timeout=5)
            except Exception as e:
                logger.error(f"Erro ao ativar interface {self.interface}: {e}")
                return False
            
            # Gerar e validar configuração wpa_supplicant
            wpa_config = self._generate_wpa_config(ssid, password)
            config_file = '/tmp/wpa_supplicant.conf'
            
            try:
                with open(config_file, 'w') as f:
                    f.write(wpa_config)
                logger.debug(f"Configuração wpa_supplicant salva em {config_file}")
            except Exception as e:
                logger.error(f"Erro ao salvar configuração wpa_supplicant: {e}")
                return False
            
            # Testar configuração antes de usar
            test_result = subprocess.run([
                'wpa_supplicant', '-c', config_file, '-i', self.interface, '-D', 'nl80211', '-t'
            ], capture_output=True, text=True, timeout=10)
            
            if "Failed to initialize driver" in test_result.stderr:
                logger.error("Driver Wi-Fi não suportado ou interface inválida")
                return False
                
            # Iniciar wpa_supplicant em background
            cmd = [
                'wpa_supplicant', '-B', '-i', self.interface,
                '-c', config_file, '-D', 'nl80211', '-f', '/tmp/wpa_supplicant.log'
            ]
            
            logger.info(f"Iniciando wpa_supplicant: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            
            if result.returncode != 0:
                error_msg = result.stderr.strip()
                logger.error(f"Erro ao iniciar wpa_supplicant: {error_msg}")
                
                # Analisar logs para erros específicos
                try:
                    with open('/tmp/wpa_supplicant.log', 'r') as f:
                        log_content = f.read()
                        if "authentication failed" in log_content.lower():
                            logger.error("Falha na autenticação - senha incorreta")
                        elif "association rejected" in log_content.lower():
                            logger.error("Associação rejeitada pelo ponto de acesso")
                        elif "network not found" in log_content.lower():
                            logger.error("Rede não encontrada")
                except:
                    pass
                    
                return False
            
            logger.info("wpa_supplicant iniciado, aguardando associação...")
            
            # Aguardar associação com timeout e verificação detalhada
            association_success = False
            for i in range(45):  # 45 segundos timeout
                time.sleep(1)
                
                # Verificar status da associação
                if self._is_associated():
                    logger.info(f"Associação Wi-Fi estabelecida após {i+1} segundos")
                    association_success = True
                    break
                    
                # Verificar logs para erros durante a associação
                if i % 5 == 0:  # Verificar logs a cada 5 segundos
                    try:
                        with open('/tmp/wpa_supplicant.log', 'r') as f:
                            recent_logs = f.read()
                            if "authentication failed" in recent_logs.lower():
                                logger.error("Autenticação falhada durante associação")
                                return False
                            elif "4-way handshake failed" in recent_logs.lower():
                                logger.error("Falha no handshake WPA - verifique a senha")
                                return False
                    except:
                        pass
            
            if not association_success:
                logger.error("Timeout na associação Wi-Fi")
                return False
            
            # Obter IP via DHCP com múltiplas tentativas
            logger.info("Solicitando endereço IP via DHCP...")
            dhcp_success = False
            
            for attempt in range(3):
                try:
                    # Limpar configuração IP anterior
                    subprocess.run(['ip', 'addr', 'flush', 'dev', self.interface], 
                                 capture_output=True, timeout=5)
                    
                    # Solicitar IP via DHCP
                    dhcp_result = subprocess.run(['dhclient', '-v', self.interface], 
                                               capture_output=True, text=True, timeout=20)
                    
                    if dhcp_result.returncode == 0:
                        dhcp_success = True
                        break
                    else:
                        logger.warning(f"Tentativa DHCP {attempt+1} falhou: {dhcp_result.stderr}")
                        time.sleep(3)
                        
                except subprocess.TimeoutExpired:
                    logger.warning(f"Timeout na tentativa DHCP {attempt+1}")
                    time.sleep(3)
                except Exception as e:
                    logger.warning(f"Erro na tentativa DHCP {attempt+1}: {e}")
                    time.sleep(3)
            
            if not dhcp_success:
                logger.error("Falha ao obter endereço IP via DHCP")
                return False
            
            # Verificar conectividade final com timeout
            logger.info("Verificando conectividade...")
            for i in range(20):  # 20 segundos para verificar conectividade
                time.sleep(1)
                if self._check_network_connection():
                    logger.info(f"Conexão wpa_supplicant estabelecida com sucesso após {i+1} segundos")
                    
                    # Salvar configuração apenas se conexão bem-sucedida
                    wifi_config = self.config_manager.get_wifi_config()
                    if not wifi_config or wifi_config.get('ssid') != ssid:
                        self.config_manager.save_wifi_config(ssid, password)
                    
                    return True
            
            logger.error("wpa_supplicant associou mas sem conectividade com a internet")
            return False
            
        except subprocess.TimeoutExpired:
            logger.error("Timeout geral no método wpa_supplicant")
            return False
        except Exception as e:
            logger.error(f"Erro no método wpa_supplicant: {e}")
            return False
        finally:
            # Limpar arquivo de configuração temporário
            try:
                if os.path.exists('/tmp/wpa_supplicant.conf'):
                    os.remove('/tmp/wpa_supplicant.conf')
            except:
                pass
            
    def _generate_wpa_config(self, ssid: str, password: str = None) -> str:
        """Gera configuração do wpa_supplicant com suporte a diferentes tipos de segurança"""
        
        # Escapar caracteres especiais no SSID
        ssid_escaped = ssid.replace('"', '\\"').replace('\\', '\\\\')
        
        config = f"""# Configuração wpa_supplicant gerada automaticamente
country=BR
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
ap_scan=1

network={{
    ssid="{ssid_escaped}"
"""
        
        if password:
            # Escapar caracteres especiais na senha
            password_escaped = password.replace('"', '\\"').replace('\\', '\\\\')
            
            # Detectar tipo de segurança baseado no comprimento e formato da senha
            if len(password) == 64 and all(c in '0123456789abcdefABCDEF' for c in password):
                # Senha em formato hexadecimal (PSK pré-computada)
                config += f'    psk={password}\n'
                logger.debug("Usando PSK hexadecimal pré-computada")
            else:
                # Senha em formato ASCII (será convertida para PSK)
                config += f'    psk="{password_escaped}"\n'
                logger.debug("Usando senha ASCII (será convertida para PSK)")
            
            # Configurações de segurança robustas
            config += """    key_mgmt=WPA-PSK WPA-EAP
    pairwise=CCMP TKIP
    group=CCMP TKIP
    proto=RSN WPA
    scan_ssid=1
    priority=5
"""
        else:
            # Rede aberta
            config += """    key_mgmt=NONE
    priority=1
    scan_ssid=1
"""
            logger.debug("Configurando para rede aberta")
        
        config += "}\n"
        
        # Adicionar configuração de fallback para redes conhecidas
        config += """
# Configuração de fallback para redes Enterprise (opcional)
network={
    ssid="*"
    key_mgmt=WPA-EAP
    eap=PEAP TTLS
    priority=1
    disabled=1
}
"""
        
        logger.debug(f"Configuração wpa_supplicant gerada para SSID: {ssid}")
        return config
        
    def _is_associated(self) -> bool:
        """Verifica se está associado a uma rede"""
        try:
            result = subprocess.run(['iwconfig', self.interface], 
                                  capture_output=True, text=True, timeout=5)
            return 'Not-Associated' not in result.stdout
        except:
            return False
            
    def disconnect(self):
        """Desconecta do Wi-Fi"""
        try:
            logger.info("Desconectando Wi-Fi")
            subprocess.run(['pkill', 'wpa_supplicant'], capture_output=True)
            subprocess.run(['pkill', 'dhclient'], capture_output=True)
            subprocess.run(['ip', 'addr', 'flush', 'dev', self.interface], capture_output=True)
            subprocess.run(['ip', 'link', 'set', self.interface, 'down'], capture_output=True)
        except Exception as e:
            logger.error(f"Erro ao desconectar Wi-Fi: {e}")
            
    def get_current_network(self) -> Optional[str]:
        """Retorna o SSID da rede atual"""
        try:
            result = subprocess.run(['iwconfig', self.interface], 
                                  capture_output=True, text=True, timeout=5)
            
            for line in result.stdout.split('\n'):
                if 'ESSID:' in line:
                    match = re.search(r'ESSID:"([^"]*)"', line)
                    if match:
                        return match.group(1)
            return None
        except Exception as e:
            logger.error(f"Erro ao obter rede atual: {e}")
            return None
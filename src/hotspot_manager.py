#!/usr/bin/env python3
"""
Módulo para gerenciamento do hotspot (Access Point)
"""

import os
import subprocess
import logging
import time
import tempfile
from typing import Optional

logger = logging.getLogger(__name__)

class HotspotManager:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.interface = os.getenv('WIFI_INTERFACE', 'wlan0')
        self.ssid = os.getenv('HOTSPOT_SSID', 'RPi-WiFi-Config')
        self.password = os.getenv('HOTSPOT_PASSWORD', 'raspberry123')
        self.ip_range = '192.168.4.1/24'
        self.dhcp_range = '192.168.4.2,192.168.4.50,255.255.255.0,12h'
        self.running = False
        self.demo_mode = os.getenv('DEMO_MODE', 'false').lower() == 'true'
        
    def start_hotspot(self) -> bool:
        """Inicia o hotspot"""
        try:
            if self.running:
                logger.info("Hotspot já está rodando")
                return True
            
            # Em modo demo, simular sucesso sem configurar hardware
            if self.demo_mode:
                logger.info(f"[DEMO] Simulando início do hotspot {self.ssid}")
                self.running = True
                return True
                
            logger.info(f"Iniciando hotspot {self.ssid}")
            
            # Parar serviços que podem interferir
            self._stop_conflicting_services()
            
            # Configurar interface
            self._configure_interface()
            
            # Configurar hostapd
            hostapd_config = self._create_hostapd_config()
            
            # Configurar dnsmasq
            dnsmasq_config = self._create_dnsmasq_config()
            
            # Configurar iptables
            self._configure_iptables()
            
            # Iniciar dnsmasq
            if not self._start_dnsmasq(dnsmasq_config):
                raise Exception("Falha ao iniciar dnsmasq")
                
            # Iniciar hostapd
            if not self._start_hostapd(hostapd_config):
                raise Exception("Falha ao iniciar hostapd")
                
            self.running = True
            logger.info("Hotspot iniciado com sucesso")
            return True
            
        except Exception as e:
            if not self.demo_mode:
                logger.error(f"Erro ao iniciar hotspot: {e}")
            else:
                logger.info(f"[DEMO] Simulando erro de hotspot (normal em demo): {e}")
            self.stop_hotspot()
            return False
            
    def stop_hotspot(self):
        """Para o hotspot"""
        try:
            if not self.running:
                return
            
            # Em modo demo, apenas simular
            if self.demo_mode:
                logger.info("[DEMO] Simulando parada do hotspot")
                self.running = False
                return
                
            logger.info("Parando hotspot")
            
            # Parar serviços
            subprocess.run(['pkill', 'hostapd'], capture_output=True)
            subprocess.run(['pkill', 'dnsmasq'], capture_output=True)
            
            # Limpar iptables
            self._clear_iptables()
            
            # Resetar interface
            subprocess.run(['ip', 'addr', 'flush', 'dev', self.interface], capture_output=True)
            subprocess.run(['ip', 'link', 'set', self.interface, 'down'], capture_output=True)
            
            self.running = False
            logger.info("Hotspot parado")
            
        except Exception as e:
            logger.error(f"Erro ao parar hotspot: {e}")
            
    def _stop_conflicting_services(self):
        """Para serviços que podem interferir"""
        services = ['wpa_supplicant', 'dhclient', 'NetworkManager']
        
        for service in services:
            try:
                subprocess.run(['pkill', service], capture_output=True)
            except:
                pass
                
        # Aguardar processos terminarem
        time.sleep(2)
        
    def _configure_interface(self):
        """Configura a interface de rede"""
        try:
            # Ativar interface
            subprocess.run(['ip', 'link', 'set', self.interface, 'up'], 
                         capture_output=True, timeout=5)
            
            # Configurar IP
            subprocess.run(['ip', 'addr', 'add', self.ip_range, 'dev', self.interface], 
                         capture_output=True, timeout=5)
                         
            logger.info(f"Interface {self.interface} configurada com IP {self.ip_range}")
            
        except subprocess.TimeoutExpired:
            raise Exception("Timeout ao configurar interface")
        except Exception as e:
            raise Exception(f"Erro ao configurar interface: {e}")
            
    def _create_hostapd_config(self) -> str:
        """Cria configuração do hostapd"""
        config_content = f"""
interface={self.interface}
driver=nl80211
ssid={self.ssid}
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={self.password}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
"""
        
        # Salvar em arquivo temporário
        config_file = '/tmp/hostapd.conf'
        with open(config_file, 'w') as f:
            f.write(config_content)
            
        logger.info(f"Configuração hostapd criada: {config_file}")
        return config_file
        
    def _create_dnsmasq_config(self) -> str:
        """Cria configuração do dnsmasq"""
        config_content = f"""
interface={self.interface}
dhcp-range={self.dhcp_range}
domain=local
address=/captive.portal/192.168.4.1
address=/wifi.config/192.168.4.1
server=8.8.8.8
server=8.8.4.4
log-queries
log-dhcp
"""
        
        # Salvar em arquivo temporário
        config_file = '/tmp/dnsmasq.conf'
        with open(config_file, 'w') as f:
            f.write(config_content)
            
        logger.info(f"Configuração dnsmasq criada: {config_file}")
        return config_file
        
    def _configure_iptables(self):
        """Configura regras iptables para NAT"""
        try:
            # Em modo demo, apenas simular
            if self.demo_mode:
                logger.info("[DEMO] Simulando configuração iptables")
                return
                
            # Limpar regras existentes
            subprocess.run(['iptables', '-F'], capture_output=True)
            subprocess.run(['iptables', '-t', 'nat', '-F'], capture_output=True)
            
            # Configurar NAT (se tiver conexão ethernet)
            subprocess.run([
                'iptables', '-t', 'nat', '-A', 'POSTROUTING', 
                '-o', 'eth0', '-j', 'MASQUERADE'
            ], capture_output=True)
            
            # Permitir forwarding
            subprocess.run([
                'iptables', '-A', 'FORWARD', '-i', 'eth0', 
                '-o', self.interface, '-m', 'state', 
                '--state', 'RELATED,ESTABLISHED', '-j', 'ACCEPT'
            ], capture_output=True)
            
            subprocess.run([
                'iptables', '-A', 'FORWARD', '-i', self.interface, 
                '-o', 'eth0', '-j', 'ACCEPT'
            ], capture_output=True)
            
            # Redirecionar HTTP para interface web
            subprocess.run([
                'iptables', '-t', 'nat', '-A', 'PREROUTING',
                '-i', self.interface, '-p', 'tcp', '--dport', '80',
                '-j', 'DNAT', '--to-destination', '192.168.4.1:8080'
            ], capture_output=True)
            
            # Habilitar IP forwarding
            with open('/proc/sys/net/ipv4/ip_forward', 'w') as f:
                f.write('1')
                
            logger.info("Regras iptables configuradas")
            
        except Exception as e:
            if not self.demo_mode:
                logger.warning(f"Erro ao configurar iptables: {e}")
            else:
                logger.debug(f"[DEMO] Erro esperado em iptables: {e}")
            
    def _clear_iptables(self):
        """Limpa regras iptables"""
        try:
            subprocess.run(['iptables', '-F'], capture_output=True)
            subprocess.run(['iptables', '-t', 'nat', '-F'], capture_output=True)
            
            # Desabilitar IP forwarding
            with open('/proc/sys/net/ipv4/ip_forward', 'w') as f:
                f.write('0')
                
        except Exception as e:
            logger.warning(f"Erro ao limpar iptables: {e}")
            
    def _start_dnsmasq(self, config_file: str) -> bool:
        """Inicia o dnsmasq"""
        try:
            # Em modo demo, simular sucesso
            if self.demo_mode:
                logger.info("[DEMO] Simulando início do dnsmasq")
                return True
                
            cmd = ['dnsmasq', '--conf-file=' + config_file, '--no-daemon']
            
            # Iniciar em background
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Aguardar serviço iniciar
            time.sleep(2)
            
            # Verificar se está rodando
            result = subprocess.run(['pgrep', 'dnsmasq'], capture_output=True)
            
            if result.returncode == 0:
                logger.info("dnsmasq iniciado com sucesso")
                return True
            else:
                logger.error("dnsmasq falhou ao iniciar")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao iniciar dnsmasq: {e}")
            return False
            
    def _start_hostapd(self, config_file: str) -> bool:
        """Inicia o hostapd"""
        try:
            # Em modo demo, simular sucesso
            if self.demo_mode:
                logger.info("[DEMO] Simulando início do hostapd")
                return True
                
            cmd = ['hostapd', config_file]
            
            # Iniciar em background
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Aguardar serviço iniciar
            time.sleep(3)
            
            # Verificar se está rodando
            result = subprocess.run(['pgrep', 'hostapd'], capture_output=True)
            
            if result.returncode == 0:
                logger.info("hostapd iniciado com sucesso")
                return True
            else:
                logger.error("hostapd falhou ao iniciar")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao iniciar hostapd: {e}")
            return False
            
    def is_running(self) -> bool:
        """Verifica se o hotspot está rodando"""
        try:
            # Verificar processos
            hostapd_running = subprocess.run(['pgrep', 'hostapd'], capture_output=True).returncode == 0
            dnsmasq_running = subprocess.run(['pgrep', 'dnsmasq'], capture_output=True).returncode == 0
            
            # Verificar interface
            result = subprocess.run(['ip', 'addr', 'show', self.interface], 
                                  capture_output=True, text=True)
            interface_configured = '192.168.4.1' in result.stdout
            
            running = hostapd_running and dnsmasq_running and interface_configured
            self.running = running
            return running
            
        except Exception as e:
            logger.error(f"Erro ao verificar status do hotspot: {e}")
            return False
            
    def get_connected_clients(self) -> list:
        """Retorna lista de clientes conectados"""
        clients = []
        
        try:
            # Ler arquivo de leases do dnsmasq
            lease_file = '/var/lib/dhcp/dnsmasq.leases'
            if os.path.exists(lease_file):
                with open(lease_file, 'r') as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) >= 4:
                            clients.append({
                                'ip': parts[2],
                                'mac': parts[1],
                                'hostname': parts[3] if len(parts) > 3 else 'Unknown'
                            })
                            
        except Exception as e:
            logger.error(f"Erro ao obter clientes conectados: {e}")
            
        return clients
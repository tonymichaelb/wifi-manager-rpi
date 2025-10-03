#!/usr/bin/env python3
"""
Sistema principal de gerenciamento Wi-Fi para Raspberry Pi Zero 2W
Monitora conexão Wi-Fi e ativa hotspot quando necessário
"""

import os
import sys
import time
import logging
import threading
from datetime import datetime

from wifi_monitor import WiFiMonitor
from hotspot_manager import HotspotManager
from web_interface import WebInterface
from config_manager import ConfigManager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/wifi-manager/wifi-manager.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class WiFiManagerSystem:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.wifi_monitor = WiFiMonitor(self.config_manager)
        self.hotspot_manager = HotspotManager(self.config_manager)
        self.web_interface = WebInterface(self.config_manager, self.wifi_monitor, self.hotspot_manager)
        
        self.running = False
        self.mode = "wifi"  # "wifi" ou "hotspot"
        self.demo_mode = os.getenv('DEMO_MODE', 'false').lower() == 'true'
        
        # Configurar logging para modo demo
        if self.demo_mode:
            logger.info("=== MODO DEMO ATIVADO ===")
            logger.info("Sistema funcionando em modo demonstração")
            logger.info("Para produção no Raspberry Pi, remover DEMO_MODE=true")
        
    def start(self):
        """Inicia o sistema de gerenciamento Wi-Fi"""
        logger.info("Iniciando sistema de gerenciamento Wi-Fi")
        self.running = True
        
        # Iniciar interface web em thread separada
        web_thread = threading.Thread(target=self.web_interface.start, daemon=True)
        web_thread.start()
        
        # Loop principal de monitoramento
        self.main_loop()
        
    def main_loop(self):
        """Loop principal do sistema"""
        consecutive_failures = 0
        max_failures = 3
        
        # Intervalo baseado no modo
        check_interval = 30 if self.demo_mode else 10  # Intervalo maior em demo
        
        if self.demo_mode:
            logger.info(f"Ciclo de verificação: {check_interval}s (modo demo)")
        
        while self.running:
            try:
                if self.mode == "wifi":
                    # Modo Wi-Fi: monitorar conexão
                    if self.wifi_monitor.is_connected():
                        consecutive_failures = 0
                        if self.demo_mode and consecutive_failures == 0:
                            logger.debug("[DEMO] Simulando verificação Wi-Fi")
                        else:
                            logger.debug("Conexão Wi-Fi ativa")
                    else:
                        consecutive_failures += 1
                        if self.demo_mode:
                            logger.info(f"[DEMO] Simulando falha Wi-Fi ({consecutive_failures}/{max_failures})")
                        else:
                            logger.warning(f"Falha na conexão Wi-Fi ({consecutive_failures}/{max_failures})")
                        
                        if consecutive_failures >= max_failures:
                            if self.demo_mode:
                                logger.info("[DEMO] Ativando modo hotspot (simulação)")
                            else:
                                logger.info("Ativando modo hotspot devido a falhas consecutivas")
                            self.switch_to_hotspot()
                            
                elif self.mode == "hotspot":
                    # Modo Hotspot: verificar se deve tentar reconectar
                    if self.should_try_wifi_reconnect():
                        if self.demo_mode:
                            logger.info("[DEMO] Tentando reconectar ao Wi-Fi (simulação)")
                        else:
                            logger.info("Tentando reconectar ao Wi-Fi")
                        self.switch_to_wifi()
                        
                time.sleep(check_interval)
                
            except KeyboardInterrupt:
                logger.info("Interrupção recebida, parando sistema")
                self.stop()
                break
            except Exception as e:
                logger.error(f"Erro no loop principal: {e}")
                time.sleep(check_interval)
                
    def switch_to_hotspot(self):
        """Muda para modo hotspot"""
        try:
            if self.demo_mode:
                logger.info("[DEMO] Mudando para modo hotspot")
            else:
                logger.info("Mudando para modo hotspot")
            self.wifi_monitor.disconnect()
            self.hotspot_manager.start_hotspot()
            self.mode = "hotspot"
            if self.demo_mode:
                logger.info("[DEMO] Modo hotspot ativado (simulação completa)")
            else:
                logger.info("Modo hotspot ativado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao ativar hotspot: {e}")
            
    def switch_to_wifi(self):
        """Muda para modo Wi-Fi"""
        try:
            logger.info("Mudando para modo Wi-Fi")
            self.hotspot_manager.stop_hotspot()
            
            if self.wifi_monitor.connect():
                self.mode = "wifi"
                logger.info("Modo Wi-Fi ativado com sucesso")
            else:
                logger.warning("Falha ao conectar Wi-Fi, mantendo hotspot")
                self.hotspot_manager.start_hotspot()
                
        except Exception as e:
            logger.error(f"Erro ao ativar Wi-Fi: {e}")
            
    def should_try_wifi_reconnect(self):
        """Verifica se deve tentar reconectar ao Wi-Fi"""
        # Verificar se há configuração Wi-Fi disponível
        wifi_config = self.config_manager.get_wifi_config()
        if not wifi_config or not wifi_config.get('ssid'):
            return False
            
        # Verificar se a rede está disponível
        return self.wifi_monitor.is_network_available(wifi_config['ssid'])
        
    def stop(self):
        """Para o sistema"""
        logger.info("Parando sistema de gerenciamento Wi-Fi")
        self.running = False
        
        try:
            self.hotspot_manager.stop_hotspot()
            self.web_interface.stop()
        except Exception as e:
            logger.error(f"Erro ao parar sistema: {e}")

def main():
    """Função principal"""
    logger.info("=== Iniciando WiFi Manager System ===")
    
    # Verificar se está rodando como root
    if os.geteuid() != 0:
        logger.error("Este programa deve ser executado como root")
        sys.exit(1)
        
    # Criar diretório de logs se não existir
    os.makedirs('/var/log/wifi-manager', exist_ok=True)
    
    try:
        system = WiFiManagerSystem()
        system.start()
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
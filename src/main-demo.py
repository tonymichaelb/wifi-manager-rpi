#!/usr/bin/env python3
"""
TUPANA Wi-Fi Manager - Versão Demo/Simulação
Sistema de gerenciamento Wi-Fi para Raspberry Pi Zero 2W
Versão adaptada para testes sem hardware Wi-Fi real
"""

import os
import time
import json
import subprocess
import logging
from flask import Flask, render_template, request, jsonify
from threading import Thread
import random

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WiFiManagerDemo:
    """Gerenciador Wi-Fi simulado para demonstração"""
    
    def __init__(self):
        self.interface = os.getenv('WIFI_INTERFACE', 'wlan0')
        self.current_network = None
        self.hotspot_active = False
        self.connected = False
        
        # Redes simuladas para demonstração
        self.demo_networks = [
            {'ssid': 'WiFi-Casa', 'signal_strength': 85, 'encrypted': True},
            {'ssid': 'WiFi-Vizinho', 'signal_strength': 65, 'encrypted': True},
            {'ssid': 'WiFi-Trabalho', 'signal_strength': 90, 'encrypted': True},
            {'ssid': 'WiFi-Publico', 'signal_strength': 45, 'encrypted': False},
            {'ssid': 'TUPANA-Setup', 'signal_strength': 100, 'encrypted': True}
        ]
        
        # Redes salvas simuladas
        self.saved_networks = ['WiFi-Casa', 'WiFi-Trabalho']
        
        logger.info("TUPANA Wi-Fi Manager Demo iniciado")
    
    def get_wifi_status(self):
        """Retorna status simulado do Wi-Fi"""
        return {
            'connected': self.connected,
            'network': self.current_network,
            'hotspot_active': self.hotspot_active,
            'interface': self.interface
        }
    
    def scan_networks(self):
        """Simula scan de redes Wi-Fi"""
        logger.info("Simulando scan de redes Wi-Fi...")
        time.sleep(1)  # Simula tempo de scan
        
        # Adiciona variação no sinal
        networks = []
        for net in self.demo_networks:
            network = net.copy()
            network['signal_strength'] = max(20, net['signal_strength'] + random.randint(-10, 10))
            networks.append(network)
        
        return networks
    
    def connect_wifi(self, ssid, password):
        """Simula conexão Wi-Fi"""
        logger.info(f"Simulando conexão com {ssid}")
        
        # Simula tempo de conexão
        time.sleep(2)
        
        # Simula falha ocasional (10% de chance)
        if random.random() < 0.1:
            logger.error(f"Falha simulada na conexão com {ssid}")
            return False
        
        # Simula conexão bem-sucedida
        self.connected = True
        self.current_network = ssid
        self.hotspot_active = False
        
        # Adiciona à lista de redes salvas se não estiver
        if ssid not in self.saved_networks:
            self.saved_networks.append(ssid)
        
        logger.info(f"Conectado com sucesso à rede {ssid}")
        return True
    
    def get_saved_networks(self):
        """Retorna redes salvas simuladas"""
        return self.saved_networks.copy()
    
    def delete_saved_network(self, ssid):
        """Remove rede salva simulada"""
        try:
            if ssid in self.saved_networks:
                self.saved_networks.remove(ssid)
                logger.info(f"Rede {ssid} removida das redes salvas")
                
                # Se estava conectado nesta rede, desconecta
                if self.current_network == ssid:
                    self.connected = False
                    self.current_network = None
                    self.start_hotspot()
                
                return True
            else:
                logger.warning(f"Rede {ssid} não encontrada nas redes salvas")
                return False
        except Exception as e:
            logger.error(f"Erro ao remover rede {ssid}: {e}")
            return False
    
    def start_hotspot(self):
        """Simula início do hotspot"""
        logger.info("Simulando início do hotspot TUPANA...")
        self.hotspot_active = True
        self.connected = False
        self.current_network = None
        logger.info("Hotspot TUPANA simulado ativo")
    
    def stop_hotspot(self):
        """Simula parada do hotspot"""
        logger.info("Simulando parada do hotspot TUPANA...")
        self.hotspot_active = False
        logger.info("Hotspot TUPANA simulado desativado")
    
    def monitor_connection(self):
        """Simula monitoramento de conexão"""
        while True:
            try:
                if self.connected and self.current_network:
                    # Simula perda de conexão ocasional (5% de chance a cada 30s)
                    if random.random() < 0.05:
                        logger.warning(f"Simulando perda de conexão com {self.current_network}")
                        self.connected = False
                        self.current_network = None
                        self.start_hotspot()
                
                elif not self.hotspot_active and not self.connected:
                    # Se não está conectado e hotspot não está ativo, ativa hotspot
                    self.start_hotspot()
                
                time.sleep(30)  # Verifica a cada 30 segundos
                
            except Exception as e:
                logger.error(f"Erro no monitoramento: {e}")
                time.sleep(10)

# Inicializar gerenciador Wi-Fi
wifi_manager = WiFiManagerDemo()

# Inicializar Flask
app = Flask(__name__)

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
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Dados não fornecidos'})
    
    ssid = data.get('ssid')
    password = data.get('password')
    
    if not ssid:
        return jsonify({'success': False, 'error': 'SSID não fornecido'})
    
    success = wifi_manager.connect_wifi(ssid, password)
    return jsonify({'success': success})

@app.route('/delete-network', methods=['POST'])
@app.route('/api/delete-network', methods=['POST'])
def api_delete_network():
    """API: Excluir rede salva"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Dados não fornecidos'})
    
    ssid = data.get('ssid')
    
    if not ssid:
        return jsonify({'success': False, 'error': 'SSID não fornecido'})
    
    success = wifi_manager.delete_saved_network(ssid)
    return jsonify({'success': success})

@app.route('/health')
def health():
    """Health check"""
    return jsonify({'status': 'ok', 'mode': 'demo'})

def start_monitoring():
    """Inicia thread de monitoramento"""
    monitor_thread = Thread(target=wifi_manager.monitor_connection, daemon=True)
    monitor_thread.start()

if __name__ == '__main__':
    logger.info("Iniciando TUPANA Wi-Fi Manager Demo...")
    
    # Simula estado inicial
    wifi_manager.start_hotspot()
    
    # Inicia monitoramento em background
    start_monitoring()
    
    # Inicia servidor Flask
    logger.info("TUPANA Demo ativo - Acesse http://localhost:8080")
    app.run(host='0.0.0.0', port=8080, debug=False)
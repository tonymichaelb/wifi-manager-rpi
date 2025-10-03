#!/usr/bin/env python3
"""
Script de teste para interface web isolada
"""

import os
import sys
import logging
from flask import Flask, render_template, jsonify

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock classes para teste
class MockConfigManager:
    def get_wifi_config(self):
        return {"ssid": "TestNetwork", "password": "test123"}
    
    def get_system_config(self):
        return {"wifi_interface": "mock0", "hotspot_ssid": "Test-Hotspot"}
    
    def get_all_configs(self):
        return {"wifi": self.get_wifi_config(), "system": self.get_system_config()}

class MockWiFiMonitor:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.interface = "mock0"
    
    def is_connected(self):
        return True
    
    def get_current_network(self):
        return "MockNetwork"
    
    def scan_networks(self):
        return [
            {"ssid": "MockNetwork1", "signal_strength": 85, "encrypted": True},
            {"ssid": "MockNetwork2", "signal_strength": 65, "encrypted": False},
            {"ssid": "MockNetwork3", "signal_strength": 45, "encrypted": True}
        ]

class MockHotspotManager:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.ssid = "Mock-Hotspot"
    
    def is_running(self):
        return False
    
    def get_connected_clients(self):
        return []

# Criar app Flask
app = Flask(__name__, template_folder='../templates')

config_manager = MockConfigManager()
wifi_monitor = MockWiFiMonitor(config_manager)
hotspot_manager = MockHotspotManager(config_manager)

@app.route('/')
def index():
    """Página principal"""
    status = {
        'wifi': {
            'connected': wifi_monitor.is_connected(),
            'current_network': wifi_monitor.get_current_network(),
            'interface': wifi_monitor.interface
        },
        'hotspot': {
            'running': hotspot_manager.is_running(),
            'ssid': hotspot_manager.ssid,
            'clients': len(hotspot_manager.get_connected_clients())
        },
        'mode': 'wifi',
        'system': {
            'uptime': 12345,
            'memory': {'percent': 45},
            'cpu': 25
        }
    }
    return render_template('index.html', status=status)

@app.route('/scan')
def scan_networks():
    """Escaneia redes Wi-Fi disponíveis"""
    try:
        networks = wifi_monitor.scan_networks()
        return jsonify({
            'success': True,
            'networks': networks
        })
    except Exception as e:
        logger.error(f"Erro ao escanear redes: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/status')
def get_status():
    """Retorna status do sistema"""
    return jsonify({
        'timestamp': '2025-10-02T12:00:00',
        'wifi': {
            'connected': wifi_monitor.is_connected(),
            'current_network': wifi_monitor.get_current_network(),
            'interface': wifi_monitor.interface
        },
        'hotspot': {
            'running': hotspot_manager.is_running(),
            'ssid': hotspot_manager.ssid,
            'clients': len(hotspot_manager.get_connected_clients())
        },
        'mode': 'wifi',
        'system': {
            'uptime': 12345,
            'memory': {'percent': 45},
            'cpu': 25
        }
    })

@app.route('/api/logs')
def api_logs():
    """API para obter logs"""
    return jsonify({
        'success': True,
        'logs': [
            '2025-10-02 12:00:00 - INFO - Sistema iniciado',
            '2025-10-02 12:00:05 - INFO - Wi-Fi conectado',
            '2025-10-02 12:00:10 - INFO - Interface web iniciada'
        ]
    })

if __name__ == '__main__':
    port = int(os.getenv('WEB_PORT', 8080))
    logger.info(f"Iniciando interface web de teste em http://0.0.0.0:{port}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True,
        threaded=True
    )
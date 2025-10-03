#!/usr/bin/env python3
"""
Interface web para configuração do Wi-Fi
"""

import os
import logging
import json
from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime

logger = logging.getLogger(__name__)

class WebInterface:
    def __init__(self, config_manager, wifi_monitor, hotspot_manager):
        self.config_manager = config_manager
        self.wifi_monitor = wifi_monitor
        self.hotspot_manager = hotspot_manager
        
        self.app = Flask(__name__, 
                        template_folder='../templates',
                        static_folder='../static')
        
        self._setup_routes()
        
    def _setup_routes(self):
        """Configura rotas da aplicação web"""
        
        @self.app.route('/')
        def index():
            """Página principal"""
            return render_template('index.html', 
                                 status=self._get_system_status())
        
        @self.app.route('/scan')
        def scan_networks():
            """Escaneia redes Wi-Fi disponíveis"""
            try:
                networks = self.wifi_monitor.scan_networks()
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
        
        @self.app.route('/connect', methods=['POST'])
        def connect_wifi():
            """Conecta a uma rede Wi-Fi"""
            try:
                data = request.get_json()
                ssid = data.get('ssid')
                password = data.get('password', '')
                
                if not ssid:
                    return jsonify({
                        'success': False,
                        'error': 'SSID é obrigatório',
                        'error_type': 'validation'
                    })
                
                # Sanitizar entrada
                ssid = ssid.strip()
                password = password.strip() if password else None
                
                # Validar configuração com feedback detalhado
                if not self.config_manager.validate_wifi_config(ssid, password):
                    # O ConfigManager já fez log do erro específico
                    return jsonify({
                        'success': False,
                        'error': 'Configuração Wi-Fi inválida. Verifique o SSID e senha.',
                        'error_type': 'validation',
                        'details': {
                            'ssid_length': len(ssid),
                            'password_length': len(password) if password else 0,
                            'max_ssid_length': 32,
                            'min_password_length': 8
                        }
                    })
                
                logger.info(f"Tentativa de conexão Wi-Fi: SSID={ssid}, senha={'***' if password else 'sem senha'}")
                
                # Tentar conectar
                connection_success = self.wifi_monitor.connect(ssid, password)
                
                if connection_success:
                    logger.info(f"Conexão Wi-Fi bem-sucedida: {ssid}")
                    return jsonify({
                        'success': True,
                        'message': f'Conectado à rede {ssid} com sucesso!',
                        'ssid': ssid
                    })
                else:
                    # Analisar logs recentes para identificar tipo de erro
                    error_details = self._analyze_connection_error()
                    
                    logger.error(f"Falha na conexão Wi-Fi: {ssid} - {error_details['error']}")
                    
                    return jsonify({
                        'success': False,
                        'error': error_details['error'],
                        'error_type': error_details['type'],
                        'suggestions': error_details['suggestions']
                    })
                    
            except Exception as e:
                logger.error(f"Erro durante tentativa de conexão Wi-Fi: {e}")
                return jsonify({
                    'success': False,
                    'error': f'Erro interno: {str(e)}',
                    'error_type': 'internal'
                })
        
        @self.app.route('/disconnect', methods=['POST'])
        def disconnect_wifi():
            """Desconecta do Wi-Fi"""
            try:
                self.wifi_monitor.disconnect()
                return jsonify({
                    'success': True,
                    'message': 'Desconectado do Wi-Fi'
                })
            except Exception as e:
                logger.error(f"Erro ao desconectar Wi-Fi: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                })
        
        @self.app.route('/status')
        def get_status():
            """Retorna status do sistema"""
            return jsonify(self._get_system_status())
        
        @self.app.route('/config')
        def config_page():
            """Página de configuração"""
            config = self.config_manager.get_all_configs()
            return render_template('config.html', config=config)
        
        @self.app.route('/config', methods=['POST'])
        def update_config():
            """Atualiza configuração do sistema"""
            try:
                data = request.get_json()
                
                if self.config_manager.update_system_config(data):
                    return jsonify({
                        'success': True,
                        'message': 'Configuração atualizada'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Erro ao salvar configuração'
                    })
                    
            except Exception as e:
                logger.error(f"Erro ao atualizar configuração: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                })
        
        @self.app.route('/restart', methods=['POST'])
        def restart_system():
            """Reinicia o sistema"""
            try:
                # Implementar reinicialização do sistema
                return jsonify({
                    'success': True,
                    'message': 'Sistema será reiniciado'
                })
            except Exception as e:
                logger.error(f"Erro ao reiniciar sistema: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                })
        
        @self.app.route('/logs')
        def view_logs():
            """Visualiza logs do sistema"""
            try:
                log_file = '/var/log/wifi-manager/wifi-manager.log'
                logs = []
                
                if os.path.exists(log_file):
                    with open(log_file, 'r') as f:
                        lines = f.readlines()[-100:]  # Últimas 100 linhas
                        logs = [line.strip() for line in lines]
                
                return render_template('logs.html', logs=logs)
                
            except Exception as e:
                logger.error(f"Erro ao carregar logs: {e}")
                return render_template('logs.html', logs=[f"Erro ao carregar logs: {e}"])
        
        @self.app.route('/api/logs')
        def api_logs():
            """API para obter logs"""
            try:
                log_file = '/var/log/wifi-manager/wifi-manager.log'
                logs = []
                
                if os.path.exists(log_file):
                    with open(log_file, 'r') as f:
                        lines = f.readlines()[-50:]  # Últimas 50 linhas
                        logs = [line.strip() for line in lines]
                
                return jsonify({
                    'success': True,
                    'logs': logs
                })
                
            except Exception as e:
                logger.error(f"Erro ao obter logs: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                })
        
        @self.app.route('/hotspot/clients')
        def hotspot_clients():
            """Lista clientes conectados ao hotspot"""
            try:
                clients = self.hotspot_manager.get_connected_clients()
                return jsonify({
                    'success': True,
                    'clients': clients
                })
            except Exception as e:
                logger.error(f"Erro ao obter clientes do hotspot: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                })
        
        # Página de fallback para captive portal
        @self.app.route('/captive-portal')
        @self.app.route('/generate_204')
        @self.app.route('/hotspot-detect.html')
        def captive_portal():
            """Captive portal redirection"""
            return redirect(url_for('index'))
    
    def _analyze_connection_error(self):
        """Analisa logs recentes para identificar tipo específico de erro"""
        try:
            error_patterns = {
                'authentication': {
                    'patterns': [
                        'authentication failed', 'senha incorreta', 'password', 'auth',
                        '4-way handshake failed', 'Secrets were required'
                    ],
                    'error': 'Falha na autenticação - senha incorreta ou método de segurança incompatível',
                    'suggestions': [
                        'Verifique se a senha está correta',
                        'Certifique-se de que a rede usa WPA/WPA2',
                        'Tente novamente em alguns minutos'
                    ]
                },
                'network_not_found': {
                    'patterns': [
                        'network not found', 'No network with SSID', 'rede não encontrada'
                    ],
                    'error': 'Rede não encontrada',
                    'suggestions': [
                        'Execute um novo scan de redes',
                        'Verifique se está dentro do alcance da rede',
                        'Confirme se o nome da rede está correto'
                    ]
                },
                'connection_failed': {
                    'patterns': [
                        'Connection activation failed', 'association rejected', 'timeout'
                    ],
                    'error': 'Falha na conexão - ponto de acesso rejeitou a conexão',
                    'suggestions': [
                        'A rede pode estar sobrecarregada',
                        'Tente novamente em alguns momentos',
                        'Verifique se a rede permite novos dispositivos'
                    ]
                },
                'dhcp_failed': {
                    'patterns': [
                        'dhcp', 'no IP', 'timeout.*dhcp', 'failed to get IP'
                    ],
                    'error': 'Falha ao obter endereço IP',
                    'suggestions': [
                        'A rede pode estar com problemas de DHCP',
                        'Tente desconectar e conectar novamente',
                        'Verifique se a rede não exige configuração manual'
                    ]
                }
            }
            
            # Tentar ler logs recentes (últimas 50 linhas)
            log_content = ""
            possible_log_files = [
                '/var/log/wifi-manager/wifi-manager.log',
                '/tmp/wpa_supplicant.log',
                '/var/log/syslog'
            ]
            
            for log_file in possible_log_files:
                try:
                    if os.path.exists(log_file):
                        with open(log_file, 'r') as f:
                            lines = f.readlines()
                            # Pegar últimas 20 linhas de cada arquivo
                            recent_lines = lines[-20:] if len(lines) > 20 else lines
                            log_content += ' '.join(recent_lines).lower()
                except:
                    continue
            
            # Analisar padrões de erro
            for error_type, error_info in error_patterns.items():
                for pattern in error_info['patterns']:
                    if pattern.lower() in log_content:
                        return {
                            'type': error_type,
                            'error': error_info['error'],
                            'suggestions': error_info['suggestions']
                        }
            
            # Erro genérico se nenhum padrão específico for encontrado
            return {
                'type': 'generic',
                'error': 'Falha na conexão Wi-Fi - erro não especificado',
                'suggestions': [
                    'Verifique se a senha está correta',
                    'Confirme se está dentro do alcance da rede',
                    'Tente executar um novo scan de redes',
                    'Verifique se a rede aceita novos dispositivos'
                ]
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar logs de conexão: {e}")
            return {
                'type': 'analysis_failed',
                'error': 'Falha na conexão Wi-Fi',
                'suggestions': ['Tente novamente ou verifique os logs do sistema']
            }
    
    def _get_system_status(self):
        """Retorna status completo do sistema"""
        try:
            wifi_connected = self.wifi_monitor.is_connected()
            current_network = self.wifi_monitor.get_current_network()
            hotspot_running = self.hotspot_manager.is_running()
            
            status = {
                'timestamp': datetime.now().isoformat(),
                'wifi': {
                    'connected': wifi_connected,
                    'current_network': current_network,
                    'interface': self.wifi_monitor.interface
                },
                'hotspot': {
                    'running': hotspot_running,
                    'ssid': self.hotspot_manager.ssid,
                    'clients': len(self.hotspot_manager.get_connected_clients()) if hotspot_running else 0
                },
                'mode': 'hotspot' if hotspot_running else 'wifi',
                'system': {
                    'uptime': self._get_uptime(),
                    'memory': self._get_memory_usage(),
                    'cpu': self._get_cpu_usage()
                }
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Erro ao obter status do sistema: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _get_uptime(self):
        """Retorna uptime do sistema"""
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                return int(uptime_seconds)
        except:
            return 0
    
    def _get_memory_usage(self):
        """Retorna uso de memória"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return {
                'total': memory.total,
                'used': memory.used,
                'percent': memory.percent
            }
        except:
            return {'percent': 0}
    
    def _get_cpu_usage(self):
        """Retorna uso de CPU"""
        try:
            import psutil
            return psutil.cpu_percent(interval=1)
        except:
            return 0
    
    def start(self, host='0.0.0.0', port=None):
        """Inicia o servidor web"""
        if port is None:
            port = int(os.getenv('WEB_PORT', 8080))
            
        logger.info(f"Iniciando interface web em http://{host}:{port}")
        
        try:
            self.app.run(
                host=host,
                port=port,
                debug=False,
                threaded=True,
                use_reloader=False
            )
        except Exception as e:
            logger.error(f"Erro ao iniciar interface web: {e}")
    
    def stop(self):
        """Para o servidor web"""
        # Flask não tem método stop() direto, usar shutdown através de request
        pass
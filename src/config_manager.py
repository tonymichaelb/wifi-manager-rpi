#!/usr/bin/env python3
"""
Módulo para gerenciamento de configurações
"""

import os
import json
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class ConfigManager:
    def __init__(self):
        self.config_dir = '/app/config'
        self.wifi_config_file = os.path.join(self.config_dir, 'wifi_config.json')
        self.system_config_file = os.path.join(self.config_dir, 'system_config.json')
        
        # Criar diretório se não existir
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Carregar configurações padrão
        self._load_default_configs()
        
    def _load_default_configs(self):
        """Carrega configurações padrão"""
        default_system_config = {
            'wifi_interface': 'wlan0',
            'hotspot_ssid': 'RPi-WiFi-Config',
            'hotspot_password': 'raspberry123',
            'web_port': 8080,
            'check_interval': 10,
            'max_failures': 3,
            'auto_reconnect': True,
            'log_level': 'INFO'
        }
        
        # Criar arquivo de configuração do sistema se não existir
        if not os.path.exists(self.system_config_file):
            self.save_system_config(default_system_config)
            
    def get_wifi_config(self) -> Optional[Dict]:
        """Retorna configuração Wi-Fi salva"""
        try:
            if os.path.exists(self.wifi_config_file):
                with open(self.wifi_config_file, 'r') as f:
                    config = json.load(f)
                    logger.debug("Configuração Wi-Fi carregada")
                    return config
            return None
        except Exception as e:
            logger.error(f"Erro ao carregar configuração Wi-Fi: {e}")
            return None
            
    def save_wifi_config(self, ssid: str, password: str = None) -> bool:
        """Salva configuração Wi-Fi"""
        try:
            config = {
                'ssid': ssid,
                'password': password,
                'saved_at': str(os.time())
            }
            
            with open(self.wifi_config_file, 'w') as f:
                json.dump(config, f, indent=2)
                
            logger.info(f"Configuração Wi-Fi salva para rede: {ssid}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar configuração Wi-Fi: {e}")
            return False
            
    def get_system_config(self) -> Dict:
        """Retorna configuração do sistema"""
        try:
            if os.path.exists(self.system_config_file):
                with open(self.system_config_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Erro ao carregar configuração do sistema: {e}")
            return {}
            
    def save_system_config(self, config: Dict) -> bool:
        """Salva configuração do sistema"""
        try:
            with open(self.system_config_file, 'w') as f:
                json.dump(config, f, indent=2)
                
            logger.info("Configuração do sistema salva")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar configuração do sistema: {e}")
            return False
            
    def update_system_config(self, updates: Dict) -> bool:
        """Atualiza configuração do sistema"""
        try:
            current_config = self.get_system_config()
            current_config.update(updates)
            return self.save_system_config(current_config)
        except Exception as e:
            logger.error(f"Erro ao atualizar configuração do sistema: {e}")
            return False
            
    def delete_wifi_config(self) -> bool:
        """Remove configuração Wi-Fi salva"""
        try:
            if os.path.exists(self.wifi_config_file):
                os.remove(self.wifi_config_file)
                logger.info("Configuração Wi-Fi removida")
            return True
        except Exception as e:
            logger.error(f"Erro ao remover configuração Wi-Fi: {e}")
            return False
            
    def get_all_configs(self) -> Dict:
        """Retorna todas as configurações"""
        return {
            'wifi': self.get_wifi_config(),
            'system': self.get_system_config()
        }
        
    def backup_configs(self, backup_path: str) -> bool:
        """Faz backup das configurações"""
        try:
            import shutil
            
            backup_dir = os.path.dirname(backup_path)
            os.makedirs(backup_dir, exist_ok=True)
            
            # Criar arquivo tar com configurações
            import tarfile
            with tarfile.open(backup_path, 'w:gz') as tar:
                tar.add(self.config_dir, arcname='config')
                
            logger.info(f"Backup das configurações criado: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar backup: {e}")
            return False
            
    def restore_configs(self, backup_path: str) -> bool:
        """Restaura configurações do backup"""
        try:
            import tarfile
            import shutil
            
            if not os.path.exists(backup_path):
                logger.error(f"Arquivo de backup não encontrado: {backup_path}")
                return False
                
            # Fazer backup da configuração atual
            current_backup = f"{self.config_dir}_backup_{int(os.time())}"
            shutil.copytree(self.config_dir, current_backup)
            
            # Extrair backup
            with tarfile.open(backup_path, 'r:gz') as tar:
                tar.extractall(path=os.path.dirname(self.config_dir))
                
            logger.info(f"Configurações restauradas do backup: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao restaurar backup: {e}")
            return False
            
    def validate_wifi_config(self, ssid: str, password: str = None) -> bool:
        """Valida configuração Wi-Fi"""
        if not ssid or len(ssid.strip()) == 0:
            logger.error("SSID não pode estar vazio")
            return False
            
        if len(ssid) > 32:  # Limite do SSID
            logger.error(f"SSID muito longo: {len(ssid)} caracteres (máximo 32)")
            return False
            
        # Verificar caracteres especiais problemáticos no SSID
        invalid_chars = ['\"', '\'', '\\', '\n', '\r', '\t']
        for char in invalid_chars:
            if char in ssid:
                logger.error(f"SSID contém caractere inválido: {char}")
                return False
        
        # Validar senha se fornecida
        if password is not None:
            if len(password) > 0 and len(password) < 8:  # WPA mínimo quando senha fornecida
                logger.error(f"Senha muito curta: {len(password)} caracteres (mínimo 8 para WPA)")
                return False
                
            if len(password) > 63:  # Limite WPA
                logger.error(f"Senha muito longa: {len(password)} caracteres (máximo 63)")
                return False
            
            # Verificar caracteres especiais problemáticos na senha
            for char in invalid_chars:
                if char in password:
                    logger.error(f"Senha contém caractere inválido: {char}")
                    return False
            
        logger.debug(f"Configuração Wi-Fi válida: SSID={ssid}, senha={'***' if password else 'sem senha'}")
        return True
        
    def get_config_value(self, key: str, default=None):
        """Retorna valor específico da configuração"""
        system_config = self.get_system_config()
        return system_config.get(key, default)
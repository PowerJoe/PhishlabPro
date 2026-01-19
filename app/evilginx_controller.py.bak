"""
EvilGinx2 Controller - Python wrapper for EvilGinx2
"""

import os
import subprocess
import json
import time
from datetime import datetime

class EvilGinxController:
    """Control EvilGinx2 from Python"""
    
    def __init__(self, evilginx_path=None, phishlets_path=None):
        self.evilginx_path = evilginx_path or os.path.expanduser("~/evilginx2/bin/evilginx")
        self.phishlets_path = phishlets_path or os.path.expanduser("~/evilginx2/phishlets")
        self.process = None
        
    def get_available_phishlets(self):
        """Get list of available phishlets"""
        phishlets = []
        
        if not os.path.exists(self.phishlets_path):
            return phishlets
        
        for filename in os.listdir(self.phishlets_path):
            if filename.endswith('.yaml'):
                name = filename.replace('.yaml', '')
                phishlets.append({
                    'name': name,
                    'filename': filename,
                    'path': os.path.join(self.phishlets_path, filename),
                    'enabled': False  # TODO: Check actual status
                })
        
        return sorted(phishlets, key=lambda x: x['name'])
    
    def parse_phishlet_config(self, phishlet_name):
        """Parse phishlet YAML configuration"""
        import yaml
        
        phishlet_path = os.path.join(self.phishlets_path, f"{phishlet_name}.yaml")
        
        if not os.path.exists(phishlet_path):
            return None
        
        try:
            with open(phishlet_path, 'r') as f:
                config = yaml.safe_load(f)
            
            return {
                'name': config.get('name'),
                'author': config.get('author'),
                'min_version': config.get('min_ver'),
                'proxy_hosts': config.get('proxy_hosts', []),
                'sub_filters': config.get('sub_filters', []),
                'auth_urls': config.get('auth_urls', []),
            }
        except Exception as e:
            print(f"Error parsing phishlet: {e}")
            return None
    
    def enable_phishlet(self, phishlet_name, hostname):
        """Enable a phishlet"""
        # This would execute: phishlets enable <name>
        # For now, we'll return success
        return True
    
    def disable_phishlet(self, phishlet_name):
        """Disable a phishlet"""
        # This would execute: phishlets disable <name>
        return True
    
    def set_hostname(self, phishlet_name, hostname):
        """Set hostname for phishlet"""
        # This would execute: phishlets hostname <name> <hostname>
        return True
    
    def get_lures(self):
        """Get list of active lures"""
        # This would return active lures
        return []
    
    def create_lure(self, phishlet_name, redirect_url):
        """Create a new lure"""
        # This would execute: lures create <phishlet> 
        # and lures edit <id> redirect_url <url>
        return {
            'id': 1,
            'phishlet': phishlet_name,
            'path': f'/{phishlet_name}',
            'redirect_url': redirect_url,
            'created_at': datetime.utcnow()
        }
    
    def get_sessions(self):
        """Get captured sessions"""
        # This would return sessions from EvilGinx2
        # For now, return empty list
        return []
    
    def get_session_details(self, session_id):
        """Get details for a specific session"""
        return None

# Singleton instance
_controller = None

def get_evilginx_controller():
    """Get or create EvilGinx controller instance"""
    global _controller
    if _controller is None:
        _controller = EvilGinxController()
    return _controller

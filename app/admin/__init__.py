from flask import Blueprint

admin_bp = Blueprint('admin', __name__)

from flask import render_template
from flask_login import login_required

@admin_bp.route('/users')
@login_required
def users():
    return "Admin panel coming soon!"

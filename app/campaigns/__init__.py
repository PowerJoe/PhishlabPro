from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import db, Campaign, Target, EmailTemplate
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateTimeField, FileField, SubmitField
from wtforms.validators import DataRequired, Length, URL, Optional
import csv
import io
import secrets

campaigns_bp = Blueprint('campaigns', __name__)

class CampaignForm(FlaskForm):
    """Form for creating campaigns"""
    name = StringField('Campaign Name', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[Length(max=1000)])
    template_id = SelectField('Email Template', coerce=int, validators=[DataRequired()])
    phishing_url = StringField('Phishing URL', validators=[DataRequired(), URL()])
    submit = SubmitField('Create Campaign')

@campaigns_bp.route('/')
@login_required
def list_campaigns():
    """List all campaigns"""
    if current_user.is_super_admin():
        campaigns = Campaign.query.order_by(Campaign.created_at.desc()).all()
    else:
        campaigns = Campaign.query.filter_by(group_id=current_user.group_id).order_by(Campaign.created_at.desc()).all()
    
    return render_template('campaigns/list.html', campaigns=campaigns)

@campaigns_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new campaign"""
    form = CampaignForm()
    
    # Populate template choices
    if current_user.is_super_admin():
        templates = EmailTemplate.query.all()
    else:
        templates = EmailTemplate.query.filter_by(group_id=current_user.group_id).all()
    
    form.template_id.choices = [(t.id, t.name) for t in templates]
    
    if form.validate_on_submit():
        campaign = Campaign(
            name=form.name.data,
            description=form.description.data,
            template_id=form.template_id.data,
            phishing_url=form.phishing_url.data,
            group_id=current_user.group_id,
            created_by=current_user.id,
            status='draft'
        )
        
        db.session.add(campaign)
        db.session.commit()
        
        flash('Campaign created successfully!', 'success')
        return redirect(url_for('campaigns.detail', campaign_id=campaign.id))
    
    return render_template('campaigns/create.html', form=form)

@campaigns_bp.route('/<int:campaign_id>')
@login_required
def detail(campaign_id):
    """View campaign details"""
    campaign = Campaign.query.get_or_404(campaign_id)
    
    # Check permissions
    if not current_user.is_super_admin() and campaign.group_id != current_user.group_id:
        flash('Access denied', 'danger')
        return redirect(url_for('campaigns.list_campaigns'))
    
    return render_template('campaigns/detail.html', campaign=campaign)

@campaigns_bp.route('/<int:campaign_id>/targets', methods=['GET', 'POST'])
@login_required
def manage_targets(campaign_id):
    """Manage campaign targets"""
    campaign = Campaign.query.get_or_404(campaign_id)
    
    if not current_user.is_super_admin() and campaign.group_id != current_user.group_id:
        flash('Access denied', 'danger')
        return redirect(url_for('campaigns.list_campaigns'))
    
    return render_template('campaigns/targets.html', campaign=campaign)

@campaigns_bp.route('/<int:campaign_id>/upload-targets', methods=['POST'])
@login_required
def upload_targets(campaign_id):
    """Upload targets from CSV"""
    campaign = Campaign.query.get_or_404(campaign_id)
    
    if not current_user.is_super_admin() and campaign.group_id != current_user.group_id:
        return jsonify({'error': 'Access denied'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Read CSV
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        count = 0
        for row in csv_reader:
            # Generate unique tracking token
            tracking_token = secrets.token_urlsafe(32)
            
            target = Target(
                campaign_id=campaign.id,
                email=row.get('email', '').strip(),
                first_name=row.get('first_name', '').strip(),
                last_name=row.get('last_name', '').strip(),
                company=row.get('company', '').strip(),
                job_title=row.get('job_title', '').strip(),
                tracking_token=tracking_token
            )
            
            if target.email:  # Only add if email exists
                db.session.add(target)
                count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Uploaded {count} targets successfully',
            'count': count
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@campaigns_bp.route('/<int:campaign_id>/launch', methods=['POST'])
@login_required
def launch(campaign_id):
    """Launch campaign"""
    campaign = Campaign.query.get_or_404(campaign_id)
    
    if not current_user.is_super_admin() and campaign.group_id != current_user.group_id:
        return jsonify({'error': 'Access denied'}), 403
    
    if campaign.status != 'draft':
        return jsonify({'error': 'Campaign already launched'}), 400
    
    # TODO: Implement actual email sending
    campaign.status = 'running'
    campaign.started_at = datetime.utcnow()
    db.session.commit()
    
    flash('Campaign launched! (Email sending not yet implemented)', 'success')
    return jsonify({'success': True})

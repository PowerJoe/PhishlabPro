"""
Email Generator Blueprint - Using Groq AI
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired
import os
from dotenv import load_dotenv

# Import Groq AI generator
from app.campaigns.ai_generator import generate_phishing_email

load_dotenv()

email_gen_bp = Blueprint('email_gen', __name__)

class EmailGeneratorForm(FlaskForm):
    """Form for AI email generation"""
    scenario = SelectField('Scenario', choices=[
        ('password_reset', 'Password Reset'),
        ('security_alert', 'Security Alert'),
        ('invoice', 'Invoice/Payment'),
        ('package_delivery', 'Package Delivery'),
        ('account_verify', 'Account Verification'),
        ('it_support', 'IT Support Request'),
        ('hr_notification', 'HR Notification'),
    ], validators=[DataRequired()])
    
    company = StringField('Company/Brand', default='Microsoft', validators=[DataRequired()])
    
    urgency = SelectField('Urgency Level', choices=[
        ('low', 'Low - Routine'),
        ('medium', 'Medium - Important'),
        ('high', 'High - Urgent'),
    ], default='medium')
    
    tone = SelectField('Email Tone', choices=[
        ('professional', 'Professional'),
        ('casual', 'Casual/Friendly'),
        ('urgent', 'Urgent/Alarming'),
        ('formal', 'Formal/Corporate'),
    ], default='professional')
    
    custom_instructions = TextAreaField('Custom Instructions (Optional)')
    
    submit = SubmitField('🤖 Generate Email')

class ManualEmailForm(FlaskForm):
    """Form for manual email creation"""
    subject = StringField('Subject Line', validators=[DataRequired()])
    body = TextAreaField('Email Body', validators=[DataRequired()])
    submit = SubmitField('💾 Save Email')

@email_gen_bp.route('/generate', methods=['GET', 'POST'])
@login_required
def generate():
    """AI Email Generator"""
    form = EmailGeneratorForm()
    
    # Check if Groq API key is configured
    has_api_key = bool(os.getenv('GROQ_API_KEY'))
    
    if form.validate_on_submit():
        if not has_api_key:
            flash('Groq API key not configured!', 'danger')
            return redirect(url_for('email_gen.manual'))
        
        try:
            # Generate email using Groq AI
            result = generate_phishing_email(
                scenario=form.scenario.data,
                company=form.company.data,
                urgency=form.urgency.data,
                tone=form.tone.data,
                custom=form.custom_instructions.data or ''
            )
            
            if result['success']:
                # Store in session for preview
                session['generated_email'] = {
                    'subject': result['subject'],
                    'body': result['body'],
                    'model': result['model'],
                    'provider': result['provider']
                }
                
                session['generation_params'] = {
                    'scenario': form.scenario.data,
                    'company': form.company.data,
                    'urgency': form.urgency.data,
                    'tone': form.tone.data
                }
                
                flash('Email generated successfully!', 'success')
                return redirect(url_for('email_gen.preview'))
            else:
                flash(f'AI generation failed: {result["error"]}', 'danger')
                
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('email_gen/generate.html', form=form, has_api_key=has_api_key)

@email_gen_bp.route('/manual', methods=['GET', 'POST'])
@login_required
def manual():
    """Manual Email Creator"""
    form = ManualEmailForm()
    
    if form.validate_on_submit():
        # Store in session for preview
        session['generated_email'] = {
            'subject': form.subject.data,
            'body': form.body.data,
            'model': 'manual',
            'provider': 'user'
        }
        
        flash('Email created successfully!', 'success')
        return redirect(url_for('email_gen.templates'))
    
    return render_template('email_gen/manual.html', form=form)

@email_gen_bp.route('/preview')
@login_required
def preview():
    """Preview generated email"""
    email_data = session.get('generated_email')
    params = session.get('generation_params', {})
    
    if not email_data:
        flash('No email to preview', 'warning')
        return redirect(url_for('email_gen.generate'))
    
    return render_template('email_gen/preview.html', email=email_data, params=params)

@email_gen_bp.route('/save', methods=['POST'])
@login_required
def save():
    """Save email as template"""
    # TODO: Implement database saving
    flash('Email saved as template! (Feature coming soon)', 'success')
    return redirect(url_for('email_gen.templates'))

@email_gen_bp.route('/templates')
@login_required
def templates():
    """List saved email templates"""
    # TODO: Load from database
    templates = []
    return render_template('email_gen/templates.html', templates=templates)

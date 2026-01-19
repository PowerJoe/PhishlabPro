from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, session
from flask_login import login_required, current_user
from app.models import db, EmailTemplate
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length
import os

email_gen_bp = Blueprint('email_gen', __name__)

class EmailGeneratorForm(FlaskForm):
    """Form for AI email generation"""
    target_name = StringField('Target Name', validators=[DataRequired(), Length(max=100)])
    company = StringField('Company', validators=[DataRequired(), Length(max=100)])
    job_title = StringField('Job Title', validators=[DataRequired(), Length(max=100)])
    scenario = SelectField('Scenario', choices=[
        ('it_security', '🔒 IT Security Alert'),
        ('ceo_request', '👔 CEO/Executive Request'),
        ('hr_update', '📋 HR Update'),
        ('vendor_invoice', '💰 Vendor Invoice'),
        ('password_reset', '🔑 Password Reset'),
        ('mfa_setup', '🛡️ MFA Setup Requirement'),
    ], validators=[DataRequired()])
    custom_details = TextAreaField('Additional Details (Optional)', validators=[Length(max=500)])
    submit = SubmitField('Generate Email')

class ManualEmailForm(FlaskForm):
    """Form for manual email creation"""
    name = StringField('Template Name', validators=[DataRequired(), Length(max=200)])
    subject = StringField('Email Subject', validators=[DataRequired(), Length(max=500)])
    body = TextAreaField('Email Body', validators=[DataRequired()], render_kw={"rows": 15})
    preview = StringField('Preview Text', validators=[Length(max=100)])
    submit = SubmitField('Save Template')

@email_gen_bp.route('/generate', methods=['GET', 'POST'])
@login_required
def generate():
    """Email generation page"""
    form = EmailGeneratorForm()
    
    # Check if API key is available
    api_key = os.getenv('ANTHROPIC_API_KEY')
    has_api_key = api_key and api_key != 'your-anthropic-api-key-here'
    
    if form.validate_on_submit():
        if not has_api_key:
            flash('AI generation requires an Anthropic API key. Use Manual Creator instead.', 'warning')
            return redirect(url_for('email_gen.manual'))
        
        try:
            from app.ai_engine import get_ai_generator
            ai_gen = get_ai_generator()
            
            result = ai_gen.generate_phishing_email(
                target_name=form.target_name.data,
                company=form.company.data,
                job_title=form.job_title.data,
                scenario=form.scenario.data,
                custom_details=form.custom_details.data
            )
            
            session['generated_email'] = result
            session['generation_params'] = {
                'target_name': form.target_name.data,
                'company': form.company.data,
                'job_title': form.job_title.data,
                'scenario': form.scenario.data,
            }
            
            return redirect(url_for('email_gen.preview'))
            
        except Exception as e:
            flash(f'Error generating email: {str(e)}', 'danger')
    
    return render_template('email_gen/generate.html', form=form, has_api_key=has_api_key)

@email_gen_bp.route('/manual', methods=['GET', 'POST'])
@login_required
def manual():
    """Manual email creation page"""
    form = ManualEmailForm()
    
    if form.validate_on_submit():
        template = EmailTemplate(
            name=form.name.data,
            subject=form.subject.data,
            body_html=form.body.data.replace('\n', '<br>'),
            body_text=form.body.data,
            group_id=current_user.group_id,
            created_by=current_user.id,
            generated_by_ai=False
        )
        
        db.session.add(template)
        db.session.commit()
        
        flash('Email template created successfully!', 'success')
        return redirect(url_for('email_gen.templates'))
    
    return render_template('email_gen/manual.html', form=form)

@email_gen_bp.route('/preview')
@login_required
def preview():
    """Preview generated email"""
    email_data = session.get('generated_email')
    params = session.get('generation_params')
    
    if not email_data:
        flash('No email to preview. Generate one first.', 'warning')
        return redirect(url_for('email_gen.generate'))
    
    return render_template('email_gen/preview.html', email=email_data, params=params)

@email_gen_bp.route('/save', methods=['POST'])
@login_required
def save():
    """Save email as template"""
    email_data = session.get('generated_email')
    params = session.get('generation_params', {})
    
    if not email_data:
        return jsonify({'error': 'No email to save'}), 400
    
    template_name = request.form.get('name', f"{params.get('scenario', 'custom')} - {params.get('company', 'Template')}")
    
    template = EmailTemplate(
        name=template_name,
        subject=email_data['subject'],
        body_html=email_data['body'].replace('\n', '<br>'),
        body_text=email_data['body'],
        group_id=current_user.group_id,
        created_by=current_user.id,
        generated_by_ai=True,
        ai_prompt=f"Target: {params.get('target_name')}, Company: {params.get('company')}, Scenario: {params.get('scenario')}"
    )
    
    db.session.add(template)
    db.session.commit()
    
    flash('Email template saved successfully!', 'success')
    return redirect(url_for('email_gen.templates'))

@email_gen_bp.route('/templates')
@login_required
def templates():
    """List saved templates"""
    if current_user.is_super_admin():
        templates = EmailTemplate.query.order_by(EmailTemplate.created_at.desc()).all()
    else:
        templates = EmailTemplate.query.filter_by(group_id=current_user.group_id).order_by(EmailTemplate.created_at.desc()).all()
    
    return render_template('email_gen/templates.html', templates=templates)

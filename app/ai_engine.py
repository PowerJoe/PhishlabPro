"""
AI Email Generator - Claude API Integration
"""

import os
from anthropic import Anthropic

class AIEmailGenerator:
    """Generate phishing emails using Claude API"""
    
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Anthropic client"""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set in environment")
        self.client = Anthropic(api_key=api_key)
    
    def generate_phishing_email(self, target_name, company, job_title, scenario, custom_details=""):
        """Generate a phishing email using Claude"""
        
        prompt = self._build_prompt(target_name, company, job_title, scenario, custom_details)
        
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text
            return self._parse_email_response(response_text)
            
        except Exception as e:
            raise Exception(f"AI generation failed: {str(e)}")
    
    def _build_prompt(self, target_name, company, job_title, scenario, custom_details):
        """Build the prompt for Claude"""
        
        scenario_templates = {
            'it_security': {
                'context': 'IT Security Alert requiring immediate action',
                'urgency': 'high',
                'sender': 'IT Security Team',
            },
            'ceo_request': {
                'context': 'Urgent request from CEO/Executive',
                'urgency': 'high',
                'sender': 'CEO or Executive',
            },
            'hr_update': {
                'context': 'HR policy update or benefits enrollment',
                'urgency': 'medium',
                'sender': 'HR Department',
            },
            'vendor_invoice': {
                'context': 'Invoice or payment request from vendor',
                'urgency': 'medium',
                'sender': 'Finance/Vendor',
            },
            'password_reset': {
                'context': 'Password reset or account verification',
                'urgency': 'medium',
                'sender': 'IT Support',
            },
            'mfa_setup': {
                'context': 'MFA/2FA enrollment requirement',
                'urgency': 'high',
                'sender': 'Security Team',
            },
        }
        
        scenario_info = scenario_templates.get(scenario, {
            'context': 'General business communication',
            'urgency': 'medium',
            'sender': 'Internal Team',
        })
        
        prompt = f"""You are helping create a phishing simulation email for authorized security testing.

TARGET INFORMATION:
- Name: {target_name}
- Company: {company}
- Job Title: {job_title}

SCENARIO: {scenario_info['context']}
Urgency Level: {scenario_info['urgency']}
Apparent Sender: {scenario_info['sender']}

{f'ADDITIONAL DETAILS: {custom_details}' if custom_details else ''}

Generate a realistic phishing email for professional security testing. The email should:

1. Be professionally written and realistic
2. Create appropriate urgency
3. Include a plausible call-to-action (use placeholder: [PHISHING_LINK])
4. Be personalized to the target
5. Avoid obvious spelling/grammar errors

Format your response EXACTLY as follows:

SUBJECT: [email subject line]

BODY:
[email body text]

PREVIEW: [short preview text - max 50 chars]

Keep the email concise (150-250 words)."""

        return prompt
    
    def _parse_email_response(self, response_text):
        """Parse Claude's response"""
        lines = response_text.strip().split('\n')
        
        subject = ""
        body = ""
        preview = ""
        
        current_section = None
        body_lines = []
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('SUBJECT:'):
                subject = line.replace('SUBJECT:', '').strip()
                current_section = 'subject'
            elif line.startswith('BODY:'):
                current_section = 'body'
            elif line.startswith('PREVIEW:'):
                preview = line.replace('PREVIEW:', '').strip()
                current_section = 'preview'
            elif current_section == 'body' and line:
                body_lines.append(line)
        
        body = '\n\n'.join(body_lines).strip()
        
        if not subject or not body:
            subject = "Security Alert - Action Required"
            body = response_text
            preview = "Action required on your account"
        
        return {
            'subject': subject,
            'body': body,
            'preview': preview
        }

_ai_generator = None

def get_ai_generator():
    """Get or create AI generator instance"""
    global _ai_generator
    if _ai_generator is None:
        _ai_generator = AIEmailGenerator()
    return _ai_generator

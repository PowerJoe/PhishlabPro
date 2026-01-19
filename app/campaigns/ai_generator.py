"""
AI Email Generator - Groq Implementation
"""

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class AIEmailGenerator:
    """Generate phishing emails using Groq AI"""
    
    def __init__(self):
        self.provider = os.getenv('AI_PROVIDER', 'groq')
        
        if self.provider == 'groq':
            api_key = os.getenv('GROQ_API_KEY')
            if not api_key:
                raise ValueError("GROQ_API_KEY not found in .env")
            self.client = Groq(api_key=api_key)
            self.model = os.getenv('GROQ_MODEL', 'llama-3.1-70b-versatile')
        elif self.provider == 'anthropic':
            # Fallback to Anthropic if configured
            from anthropic import Anthropic
            self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
            self.model = 'claude-sonnet-4-20250514'
    
    def generate_email(self, context):
        """
        Generate phishing email based on context
        
        Args:
            context (dict): {
                'scenario': 'password reset' / 'invoice' / 'security alert',
                'company': 'Microsoft' / 'Google' / custom,
                'urgency': 'low' / 'medium' / 'high',
                'tone': 'professional' / 'casual' / 'urgent',
                'custom_instructions': optional additional instructions
            }
        """
        
        prompt = self._build_prompt(context)
        
        try:
            if self.provider == 'groq':
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a cybersecurity professional creating realistic phishing simulation emails for authorized security testing. Generate professional, believable emails that would be used in legitimate security awareness training."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.8,
                    max_tokens=1024,
                )
                
                return {
                    'success': True,
                    'subject': self._extract_subject(response.choices[0].message.content),
                    'body': self._extract_body(response.choices[0].message.content),
                    'raw': response.choices[0].message.content,
                    'model': self.model,
                    'provider': 'groq'
                }
            
            elif self.provider == 'anthropic':
                # Anthropic implementation (if you get credits later)
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                return {
                    'success': True,
                    'subject': self._extract_subject(message.content[0].text),
                    'body': self._extract_body(message.content[0].text),
                    'raw': message.content[0].text,
                    'model': self.model,
                    'provider': 'anthropic'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _build_prompt(self, context):
        """Build AI prompt from context"""
        
        scenario = context.get('scenario', 'password reset')
        company = context.get('company', 'Microsoft')
        urgency = context.get('urgency', 'medium')
        tone = context.get('tone', 'professional')
        custom = context.get('custom_instructions', '')
        
        urgency_map = {
            'low': 'routine and non-urgent',
            'medium': 'important but not critical',
            'high': 'urgent and time-sensitive'
        }
        
        prompt = f"""Generate a realistic phishing email for security awareness training.

SCENARIO: {scenario}
IMPERSONATED COMPANY: {company}
URGENCY LEVEL: {urgency_map[urgency]}
TONE: {tone}

{f'ADDITIONAL INSTRUCTIONS: {custom}' if custom else ''}

FORMAT YOUR RESPONSE EXACTLY LIKE THIS:

SUBJECT: [Email subject line here]

BODY:
[Email body here]

Make it realistic and believable. Include typical email elements like greetings, body paragraphs, call-to-action, and signature. Do not include any explanations or meta-commentary - just the email itself."""

        return prompt
    
    def _extract_subject(self, raw_text):
        """Extract subject line from AI response"""
        lines = raw_text.strip().split('\n')
        for line in lines:
            if line.startswith('SUBJECT:'):
                return line.replace('SUBJECT:', '').strip()
        # Fallback
        return "Important Security Update"
    
    def _extract_body(self, raw_text):
        """Extract email body from AI response"""
        if 'BODY:' in raw_text:
            body = raw_text.split('BODY:')[1].strip()
            return body
        # Fallback: return everything after subject
        lines = raw_text.strip().split('\n')
        body_lines = []
        found_body = False
        for line in lines:
            if found_body:
                body_lines.append(line)
            elif line.startswith('SUBJECT:'):
                found_body = True
        return '\n'.join(body_lines).strip()

# Convenience function
def generate_phishing_email(scenario='password reset', company='Microsoft', 
                           urgency='medium', tone='professional', custom=''):
    """Quick function to generate email"""
    generator = AIEmailGenerator()
    context = {
        'scenario': scenario,
        'company': company,
        'urgency': urgency,
        'tone': tone,
        'custom_instructions': custom
    }
    return generator.generate_email(context)

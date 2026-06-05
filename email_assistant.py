import smtplib
import json
import re
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from groq import Groq
import streamlit as st


class EmailAssistant:

    def __init__(self):
        self.config_file = 'email_config.json'
        self.email       = None
        self.password    = None
        self.load_config()

    def load_config(self):
        #  Check environment variables 
        env_email    = os.environ.get('GMAIL_ADDRESS')
        env_password = os.environ.get('GMAIL_APP_PASSWORD')
        if env_email and env_password:
            self.email    = env_email
            self.password = env_password
            return

        #  load from JSON config file
        try:
            with open(self.config_file, 'r') as f:
                config        = json.load(f)
                self.email    = config.get('email')
                self.password = config.get('password')
        except Exception:
            pass

    def save_config(self, email, password):
        with open(self.config_file, 'w') as f:
            json.dump({'email': email, 'password': password}, f)
        self.email    = email
        self.password = password
        return "✅ Gmail configured successfully!"

    def is_configured(self):
        return bool(self.email and self.password)

    def generate_draft(self, to, cc, purpose):
        prompt = f"""You must reply ONLY in this exact format, nothing else:

SUBJECT: <one line subject>
BODY:
<email body here>

---
Now write a professional email with:
To: {to}
CC: {cc if cc else 'None'}
Purpose: {purpose}"""

       
        try:
            client   = Groq(api_key=st.secrets["GROQ_API_KEY"])
            response = client.chat.completions.create(
               model="openai/gpt-oss-120b",
               messages=[
                  {
                     "role": "user",
                     "content": prompt
                     }
                  ],
               temperature=0.3
               )
            content = response.choices[0].message.content
            
        except Exception as e:
            return '', f'❌ Groq  error: {str(e)}\n\.'

        # 
        subject = ''
        body    = ''

        subject_match = re.search(r'(?i)^subject:\s*(.+)', content, re.MULTILINE)
        body_match    = re.search(r'(?i)^body:\s*\n([\s\S]+)', content, re.MULTILINE)

        if subject_match:
            subject = re.sub(r'\*+', '', subject_match.group(1)).strip()

        if body_match:
            body = body_match.group(1).strip()
        elif subject_match:
            # Fallback: everything after the subject line is the body
            after_subject = content[subject_match.end():].strip()
            body = re.sub(r'(?i)^body:\s*\n?', '', after_subject).strip()

        
        if not subject and not body:
            subject = 'Email Draft'
            body    = content

        return subject, body

    def send_email(self, to, cc, subject, body):
        if not self.is_configured():
            return " Please configure Gmail first!"

        try:
            msg            = MIMEMultipart()
            msg['From']    = self.email
            msg['To']      = to
            msg['Subject'] = subject

            if cc:
                msg['CC'] = cc

            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.email, self.password)

            recipients = [to] + ([cc] if cc else [])
            server.sendmail(self.email, recipients, msg.as_string())
            server.quit()

            return f" Email sent to {to} successfully!"

        except smtplib.SMTPAuthenticationError:
            return " Gmail authentication failed. Check your App Password."
        except Exception as e:
            return f" Error: {str(e)}"

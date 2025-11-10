# api/services/email_service.py 
from .body_email_service import get_html_reset_code, get_html_send_exchange, get_html_response_exchange, get_html_cancel_exchange
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 

import smtplib 
import os 


class EmailService:

    @staticmethod
    def send_email(to_email, reason, user_name, reset_code=None, publication_title=None, publication_image=None, 
                   responder_name=None, status_label=None, request_title=None, request_image=None, offered_title=None,
                    offered_image=None, extra_message=None):

        # Configuración SMTP desde variables de entorno 
        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')  
        smtp_port = int(os.environ.get('SMTP_PORT', '587'))  
        smtp_username = os.environ.get('SMTP_USERNAME')  
        smtp_password = os.environ.get('SMTP_PASSWORD')  
        from_email = os.environ.get('FROM_EMAIL', smtp_username)  

        if not smtp_username or not smtp_password:  
            return False  
        
        if reason == 'reset_code':
            subject, html_body, text_body = get_html_reset_code(user_name, reset_code)
        elif reason == 'send_exchange':
            subject, html_body, text_body = get_html_send_exchange(user_name, publication_title, publication_image)
        elif reason == 'exchange_response':
            subject, html_body, text_body = get_html_response_exchange(
                user_name, 
                responder_name, 
                status_label,
                request_title,
                request_image,
                offered_title,
                offered_image
            )
        elif reason == 'cancel_exchange':
            subject, html_body, text_body = get_html_cancel_exchange(
                user_name,
                responder_name,
                status_label,
                request_title,
                request_image,
                offered_title,
                offered_image,
                extra_message
            )

        # Crear mensaje  
        message = MIMEMultipart('alternative')  
        message['Subject'] = subject 
        message['From'] = f"EcoSwap <{from_email}>"  
        message['To'] = to_email

        # Adjuntar partes         
        part1 = MIMEText(text_body, 'plain', 'utf-8')
        part2 = MIMEText(html_body, 'html', 'utf-8')  
        message.attach(part1)  
        message.attach(part2)  

        try:
            # Conectar al servidor SMTP  
            if smtp_port == 465:  
                # SSL                 
                server = smtplib.SMTP_SSL(smtp_server, smtp_port) 
            else:  
                # TLS (587)  
                server = smtplib.SMTP(smtp_server, smtp_port)  
                server.starttls()  
                # Enviar email  
                server.login(smtp_username, smtp_password)  
                server.send_message(message)  
                # Cerrar conexión  
                server.quit()  

            return True
        
        except smtplib.SMTPAuthenticationError as e:  
            return False  
        
        except smtplib.SMTPException as e:  
            return False  
        except Exception as e:  
            return False
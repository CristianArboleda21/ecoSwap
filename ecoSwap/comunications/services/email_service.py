# api/services/email_service.py 
from email.mime.text import MIMEText 
from email.mime.multipart import MIMEMultipart 
import smtplib 
import os 


class EmailService:

    @staticmethod
    def send_password_reset_email(to_email, reset_code, user_name):   
        """  Envía email con código de restablecimiento usando SMTP  
            Returns: 
                bool: True si se envió exitosamente 
        """  
        
        # Configuración SMTP desde variables de entorno 
        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')  
        smtp_port = int(os.environ.get('SMTP_PORT', '587'))  
        smtp_username = os.environ.get('SMTP_USERNAME')  
        smtp_password = os.environ.get('SMTP_PASSWORD')  
        from_email = os.environ.get('FROM_EMAIL', smtp_username)  
       
        
        if not smtp_username or not smtp_password:  
            return False  
        
        # Crear mensaje  
        message = MIMEMultipart('alternative')  
        message['Subject'] = 'Código de Restablecimiento de Contraseña'  
        message['From'] = f"EcoSwap <{from_email}>"  
        message['To'] = to_email  
        
        # Texto plano  
        text_body = f""" Restablecimiento de Contraseña Hola {user_name}, 
        Recibimos una solicitud para restablecer tu contraseña.
        Tu código de verificación es: {reset_code} Este código expirará en 15 minutos. 
        Si no solicitaste restablecer tu contraseña, ignora este mensaje. 
        --- Este es un mensaje automático, por favor no respondas a este email.        
        """  
        
        # HTML  
        html_body = f""" 
            <!DOCTYPE html> 
            <html> 
                <head>     
                <style>         
                    body {{             
                        font-family: Arial, sans-serif;             
                        line-height: 1.6;             
                        color: #333;             
                        margin: 0;             
                        padding: 0;         
                    }}         
                    .container {{             
                        max-width: 600px;  
                        margin: 0 auto;  
                        padding: 20px;  
                        background-color: #ffffff;  
                    }}  
                    .header {{  
                        background-color: #2c3e50;  
                        color: white;  
                        padding: 20px;  
                        text-align: center;  
                        border-radius: 5px 5px 0 0;  
                    }}  
                    .content {{  
                        padding: 30px 20px;  
                        background-color: #f9f9f9;  
                    }}  
                    .code-box {{  
                        background-color: #ffffff;  
                        border: 2px dashed #3498db;  
                        padding: 20px;  
                        text-align: center;  
                        font-size: 32px;  
                        font-weight: bold;  
                        letter-spacing: 5px;  
                        border-radius: 5px;  
                        margin: 20px 0;  
                        color: #2c3e50;  
                    }}  
                    .info-box {{  
                        background-color: #e8f4f8;  
                        border-left: 4px solid #3498db;  
                        padding: 15px;  
                        margin: 20px 0;  
                        border-radius: 3px;         
                    }}         
                    .footer {{  
                        color: #888;  
                        font-size: 12px;  
                        margin-top: 30px;  
                        padding-top: 20px;  
                        border-top: 1px solid #ddd;  
                        text-align: center;  
                    }}     
                </style>
                </head> 
                <body>     
                    <div class="container">         
                        <div class="header">  
                            <h2 style="margin: 0;">EcoSwap</h2>         
                        </div>         
                        <div class="content">  
                            <h2 style="color: #2c3e50;">Restablecimiento de Contraseña</h2>  
                            <p>Hola <strong>{user_name}</strong>,</p>  
                            <p>Recibimos una solicitud para restablecer tu contraseña. Usa el siguiente código de verificación:</p>  
                            
                            <div class="code-box">{reset_code}</div>  
                            <div class="info-box">  
                                <strong>Importante:</strong> Este código expirará en <strong>15 minutos</strong>.  
                            </div>  
                            <p>Si no solicitaste restablecer tu contraseña, puedes ignorar este mensaje de forma segura.</p>  
                            <div class="footer">  
                                <p>Este es un mensaje automático, por favor no respondas a este email.</p>  
                                <p>&copy; EcoSwap. Todos los derechos reservados.</p>  
                            </div>         
                        </div>     
                    </div> 
                </body> 
            </html>  
        """  
    
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
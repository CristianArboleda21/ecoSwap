html_reset_code = """ 
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

text_body_reset_code = """ Restablecimiento de Contraseña Hola {user_name}, 
        Recibimos una solicitud para restablecer tu contraseña.
        Tu código de verificación es: {reset_code} Este código expirará en 15 minutos. 
        Si no solicitaste restablecer tu contraseña, ignora este mensaje. 
        --- Este es un mensaje automático, por favor no respondas a este email.        
        """ 

html_send_exchange = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f7;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background: #ffffff;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            .header {{
                background-color: #2c3e50;
                padding: 20px;
                text-align: center;
            }}
            .header h2 {{
                margin: 0;
                color: white;
            }}
            .content {{
                padding: 25px;
                background: #ffffff;
            }}
            .content h3 {{
                color: #2c3e50;
            }}
            .product-box {{
                background: #f9f9f9;
                padding: 15px;
                border-radius: 6px;
                text-align: center;
                margin-top: 20px;
            }}
            .product-box img {{
                max-width: 100%;
                border-radius: 6px;
                margin-bottom: 10px;
            }}
            .footer {{
                font-size: 12px;
                color: #777;
                text-align: center;
                padding: 20px;
                border-top: 1px solid #e1e1e1;
                background: #fafafa;
            }}
        </style>
    </head>

    <body>
        <div class="container">
            <div class="header">
                <h2>EcoSwap</h2>
            </div>

            <div class="content">
                <h3>¡Nueva oferta de intercambio!</h3>

                <p>Hola <strong>{user_name}</strong>,</p>

                <p>Tu publicación ha recibido una nueva oferta de intercambio.</p>

                <p><strong>Publicación que recibió la oferta:</strong></p>

                <div class="product-box">
                    <img src="{publication_image}" alt="Imagen de la publicación">
                    <p style="font-size: 18px; font-weight: bold; margin: 10px 0;">
                        {publication_title}
                    </p>
                </div>

                <p style="margin-top: 25px;">
                    Ingresa a EcoSwap para revisar la oferta y responder al usuario lo antes posible.
                </p>

                <p>¡Esperamos que tengas un excelente intercambio! 🌿</p>
            </div>

            <div class="footer">
                <p>Este es un mensaje automático, por favor no respondas a este correo.</p>
                <p>© EcoSwap. Todos los derechos reservados.</p>
            </div>
        </div>
    </body>
    </html>
"""
 
text_body_send_exchange = """ Hola {user_name}, 

    Tu publicación recibio una oferta de intercambio.
    El producto que recibio la oferta es: {publication_title}. 
    
    Revisa la oferta lo antes posible y responde la oferta al usuario. 

    --- Este es un mensaje automático, por favor no respondas a este email.        
""" 

html_response_exchange = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f4f4f7;
            margin: 0;
            padding: 0;
        }}
        .container {{
            max-width: 600px;
            margin: 20px auto;
            background: #ffffff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .header {{
            background-color: #2c3e50;
            padding: 20px;
            text-align: center;
        }}
        .header h2 {{
            margin: 0;
            color: white;
        }}
        .content {{
            padding: 25px;
            background: #ffffff;
        }}
        .content h3 {{
            color: #2c3e50;
        }}
        .status-pill {{
            display: inline-block;
            padding: 8px 14px;
            font-size: 14px;
            font-weight: bold;
            border-radius: 20px;
            margin: 10px 0;
        }}
        .Aceptada {{
            background-color: #e4f7ec;
            color: #2c7a4b;
        }}
        .Rechazada {{
            background-color: #fdecea;
            color: #b02a37;
        }}
        .Cancelada {{
            background-color: #fff4e6;
            color: #b35500;
        }}
        .product-box {{
            background: #f9f9f9;
            padding: 15px;
            border-radius: 6px;
            text-align: center;
            margin-top: 20px;
        }}
        .product-box img {{
            max-width: 100%;
            border-radius: 6px;
            margin-bottom: 10px;
        }}
        .footer {{
            font-size: 12px;
            color: #777;
            text-align: center;
            padding: 20px;
            border-top: 1px solid #e1e1e1;
            background: #fafafa;
        }}
        .btn {{
            display: inline-block;
            margin-top: 18px;
            padding: 12px 18px;
            background-color: #3498db;
            color: #fff !important;
            text-decoration: none;
            border-radius: 6px;
            font-weight: bold;
        }}
    </style>
</head>

<body>
    <div class="container">
        <div class="header">
            <h2>EcoSwap</h2>
        </div>

        <div class="content">
            <h3>Respuesta a tu oferta de intercambio</h3>

            <p>Hola <strong>{user_name}</strong>,</p>

            <p>
                <strong>{responder_name}</strong> ha respondido a la oferta que enviaste.
            </p>

            <span class="status-pill {status_label}">
                {status_label}
            </span>

            <h4 style="margin-top:25px;">Tu publicación:</h4>
            <div class="product-box">
                <img src="{request_image}" alt="Imagen de la publicación solicitada">
                <p style="font-size: 18px; font-weight: bold;">{request_title}</p>
            </div>

            <h4 style="margin-top:25px;">Publicación que ofreciste:</h4>
            <div class="product-box">
                <img src="{offered_image}" alt="Imagen de la publicación ofrecida">
                <p style="font-size: 18px; font-weight: bold;">{offered_title}</p>
            </div>
        </div>

        <div class="footer">
            <p>Este es un mensaje automático, por favor no respondas a este correo.</p>
            <p>© EcoSwap. Todos los derechos reservados.</p>
        </div>
    </div>
</body>
</html>
"""

text_body_response_exchange = """
    Hola {user_name},

    {responder_name} ha respondido a la oferta que enviaste.
    Estado: {status_label}

    Tu publicación:
    - {request_title}

    Publicación que ofreciste:
    - {offered_title}

    Para ver más detalles ingresa a EcoSwap.
    ---
    Este es un mensaje automático, por favor no respondas a este correo.
"""

html_cancel_exchange = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
    body {{
        font-family: Arial, sans-serif;
        background-color: #f4f4f7;
        margin: 0;
        padding: 0;
        color: #333;
    }}
    .container {{
        max-width: 600px;
        margin: 20px auto;
        background: #ffffff;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }}
    .header {{
        background-color: #2c3e50;
        padding: 18px;
        text-align: center;
    }}
    .header h2 {{
        margin: 0;
        color: white;
        font-size: 20px;
    }}
    .content {{
        padding: 22px;
    }}
    .lead {{
        font-size: 16px;
        margin-bottom: 10px;
    }}
    .status-pill {{
        display: inline-block;
        padding: 8px 12px;
        border-radius: 18px;
        font-weight: 700;
        margin: 8px 0 18px 0;
    }}
    .status-CANCELLED {{ background:#fff4e6; color:#b35500; border:1px solid #f1d7b3; }}
    .status-REJECTED  {{ background:#fdecea; color:#b02a37; border:1px solid #f5c6c8; }}
    .status-ACCEPTED  {{ background:#e4f7ec; color:#2c7a4b; border:1px solid #c6edd3; }}

    .cards {{ display:flex; gap:14px; flex-wrap:wrap; margin-top:16px; }}
    .card {{
        flex:1 1 48%;
        background:#fafafa;
        border-radius:6px;
        padding:12px;
        text-align:center;
        box-sizing:border-box;
    }}
    .card img {{ width:100%; height:150px; object-fit:cover; border-radius:4px; }}
    .card .title {{ margin-top:10px; font-weight:700; color:#2c3e50; font-size:15px; }}

    .btn {{ display:inline-block; margin-top:18px; padding:12px 18px; background:#3498db; color:#fff; text-decoration:none; border-radius:6px; font-weight:700; }}
    .note {{ margin-top:16px; font-size:13px; color:#666; }}
    .footer {{ background:#fafafa; padding:14px 18px; font-size:12px; color:#888; text-align:center; border-top:1px solid #eee; margin-top:22px; }}
    @media (max-width:600px) {{
        .cards {{ flex-direction:column; }}
        .card {{ flex-basis:100%; }}
    }}
</style>

</head>
<body>
    <div class="container">
        <div class="header">
            <h2>EcoSwap</h2>
        </div>

        <div class="content">
            <p class="lead">Hola <strong>{user_name}</strong>,</p>

            <p>
                <strong>{canceler_name}</strong> ha <strong>{status_label}</strong> la oferta relacionada con tu publicación.
            </p>

            <div class="cards">
                <div class="card">
                    <div style="font-size:12px;color:#666;">Publicación que recibiste</div>
                    {request_image_block}
                    <div class="title">{request_title}</div>
                </div>

                <div class="card">
                    <div style="font-size:12px;color:#666;">Publicación ofrecida</div>
                    {offered_image_block}
                    <div class="title">{offered_title}</div>
                </div>
            </div>

            <p>
                <strong>Motivo: </strong> {extra_message_block}
            </p>

        </div>

        <div class="footer">
            <p>Este es un mensaje automático, por favor no respondas a este correo.</p>
            <p>© EcoSwap. Todos los derechos reservados.</p>
        </div>
    </div>
</body>
</html>
"""

text_body_cancel_exchange = """
Hola {user_name},

{canceler_name} ha {status_label} la oferta relacionada con tu publicación.

Publicación que recibiste:
- {request_title}

Publicación ofrecida:
- {offered_title}

Motivo de cancelación
- {extra_message}

Este es un mensaje automático, por favor no respondas a este correo.
© EcoSwap.
"""

def get_html_reset_code(user_name, reset_code):
    subject = 'Código de Restablecimiento de Contraseña'
    html = html_reset_code.format(user_name=user_name, reset_code=reset_code)
    text_body = text_body_reset_code.format(user_name=user_name, reset_code=reset_code)
    return subject, html, text_body

def get_html_send_exchange(user_name, publication_title, publication_image):
    subject = 'Nueva oferta de intercambio en EcoSwap'
    html = html_send_exchange.format(
        user_name=user_name,
        publication_title=publication_title,
        publication_image=publication_image
    )
    text_body = text_body_send_exchange.format(
        user_name=user_name,
        publication_title=publication_title
    )

    return subject, html, text_body

def get_html_response_exchange(user_name, responder_name, status_label, request_title, request_image, offered_title, offered_image):
    subject = 'Respuesta a tu oferta de intercambio en EcoSwap'

    html = html_response_exchange.format(
        user_name=user_name,
        responder_name=responder_name,
        status_label=status_label,
        request_title=request_title,
        request_image=request_image,
        offered_title=offered_title,
        offered_image=offered_image
    )
    text_body = text_body_response_exchange.format(
        user_name=user_name,
        responder_name=responder_name,
        status_label=status_label,
        request_title=request_title,
        offered_title=offered_title
    )

    return subject, html, text_body

def get_html_cancel_exchange(user_name, canceler_name, status_label, request_title, request_image, offered_title, offered_image, extra_message):
    subject = 'Notificación de cancelación/rechazo de oferta de intercambio en EcoSwap'

    request_image_block = f'<img src="{request_image}" alt="Imagen de la publicación solicitada">' if request_image else ''
    offered_image_block = f'<img src="{offered_image}" alt="Imagen de la publicación ofrecida">' if offered_image else ''
    extra_message_block = f'<p>{extra_message}</p>' if extra_message else ''

    if status_label == 'Cancelada':
        status_label = 'Cancelado'
    
    html = html_cancel_exchange.format(
        user_name=user_name,
        canceler_name=canceler_name,
        status_label=status_label,
        request_title=request_title,
        request_image_block=request_image_block,
        offered_title=offered_title,
        offered_image_block=offered_image_block,
        extra_message_block=extra_message_block,
    )

    text_body = text_body_cancel_exchange.format(
        user_name=user_name,
        canceler_name=canceler_name,
        status_label=status_label,
        request_title=request_title,
        offered_title=offered_title,
        extra_message=extra_message
    )

    return subject, html, text_body
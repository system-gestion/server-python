"""
Servicio de envío de correos electrónicos
Gestiona el envío de emails de verificación y notificaciones
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import secrets
from datetime import datetime, timedelta
from app.config import settings


class EmailService:
    """
    Servicio para envío de correos electrónicos
    """
    
    def __init__(self):
        """
        Inicializa el servicio de email con Gmail
        """
        self.gmail_email = settings.GMAIL_EMAIL
        self.gmail_password = settings.GMAIL_PASSWORD
        self.frontend_url = settings.FRONTEND_URL
        
        # Validar configuración
        if not self.gmail_email or not self.gmail_password:
            print("⚠️ ADVERTENCIA: No se configuró Gmail. Los emails se mostrarán en consola.")
            print("   Configura GMAIL_EMAIL y GMAIL_PASSWORD en el archivo .env")
            self.gmail_configured = False
        else:
            self.gmail_configured = True
        
    def generate_verification_token(self) -> str:
        """
        Genera un token de verificación único
        
        Returns:
            str: Token hexadecimal único de 32 caracteres
        """
        return secrets.token_urlsafe(32)
    
    def send_verification_email(self, recipient_email: str, username: str, token: str, plain_password: Optional[str] = None, role_name: Optional[str] = None) -> bool:
        """
        Envía un email de verificación al usuario usando Gmail SMTP
        
        Args:
            recipient_email (str): Email del destinatario
            username (str): Nombre del usuario
            token (str): Token de verificación
            
        Returns:
            bool: True si el email se envió correctamente, False en caso contrario
        """
        # Si no está configurado Gmail, solo mostrar en consola
        if not self.gmail_configured:
            verification_url = f"{self.frontend_url}/auth/verify-email?token={token}"
            print("\n" + "=" * 70)
            print("📧 EMAIL DE VERIFICACIÓN (MODO DESARROLLO - SIN GMAIL)")
            print("=" * 70)
            print(f"📨 Para: {recipient_email}")
            print(f"👤 Usuario: {username}")
            if role_name:
                print(f"🏷️ Rol: {role_name}")
            if plain_password:
                print(f"🔐 Contraseña: {plain_password}")
            print(f"🔑 Token: {token}")
            print(f"🔗 URL de verificación:")
            print(f"   {verification_url}")
            print("=" * 70 + "\n")
            return True
        
        try:
            # Crear el mensaje
            message = MIMEMultipart("alternative")
            message["Subject"] = "Verifica tu cuenta - Sistema de Gestión"
            message["From"] = self.gmail_email
            message["To"] = recipient_email
            
            # URL de verificación
            verification_url = f"{self.frontend_url}/auth/verify-email?token={token}"
            
            # Contenido HTML del email
            # Mostrar credenciales y rol en el correo si se proveyeron
            html_credentials = ""
            if plain_password or role_name:
                html_credentials = "<div style=\"background:#fff; border:1px solid #eee; padding:12px; border-radius:6px; margin:18px 0;\">"
                if role_name:
                    html_credentials += f"<p><strong>🏷️ Rol:</strong> {role_name}</p>"
                if plain_password:
                    html_credentials += f"<p><strong>📧 Email:</strong> {recipient_email}</p><p><strong>🔐 Contraseña:</strong> {plain_password}</p>"
                html_credentials += "</div>"

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .container {{
                        background-color: #f9f9f9;
                        border-radius: 10px;
                        padding: 30px;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    }}
                    .header {{
                        text-align: center;
                        color: #4CAF50;
                        margin-bottom: 30px;
                    }}
                    .button {{
                        display: inline-block;
                        padding: 15px 30px;
                        background-color: #4CAF50;
                        color: white !important;
                        text-decoration: none;
                        border-radius: 5px;
                        font-weight: bold;
                        margin: 20px 0;
                    }}
                    .button:hover {{
                        background-color: #45a049;
                    }}
                    .footer {{
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #ddd;
                        font-size: 12px;
                        color: #666;
                        text-align: center;
                    }}
                    .warning {{
                        background-color: #fff3cd;
                        border-left: 4px solid #ffc107;
                        padding: 10px;
                        margin: 20px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎉 ¡Bienvenido/a, {username}!</h1>
                    </div>
                    
                    <p>Gracias por registrarte en nuestro Sistema de Gestión.</p>

                    <p></p>
                    
                    <p>Para completar tu registro y activar tu cuenta, por favor verifica tu correo electrónico haciendo clic en el siguiente botón:</p>
                    
                    <div style="text-align: center;">
                        <a href="{verification_url}" class="button">
                            ✓ Verificar mi correo electrónico
                        </a>
                    </div>
                    
                    <div class="warning">
                        <p><strong>⚠️ Importante:</strong> Este enlace expirará en 24 horas por seguridad.</p>
                    </div>
                    
                    <p>Si no puedes hacer clic en el botón, copia y pega este enlace en tu navegador:</p>
                    <p style="word-break: break-all; color: #4CAF50;">{verification_url}</p>
                    {html_credentials}
                    <div class="footer">
                        <p>Si no creaste una cuenta en nuestro sistema, puedes ignorar este correo.</p>
                        <p>Este es un correo automático, por favor no respondas a este mensaje.</p>
                        <p>&copy; 2025 Sistema de Gestión. Todos los derechos reservados.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Contenido de texto plano (fallback)
            cred_text = ""
            if role_name:
                cred_text += f"\nRol: {role_name}\n"
            if plain_password:
                cred_text += f"\nEmail: {recipient_email}\nPassword: {plain_password}\n"

            text_content = f"""
            ¡Bienvenido/a, {username}!
            
            Gracias por registrarte en nuestro Sistema de Gestión.
            
            Para completar tu registro, verifica tu correo electrónico visitando el siguiente enlace:
            {verification_url}
            
            Este enlace expirará en 24 horas.
            
            {cred_text}
            Si no creaste una cuenta, puedes ignorar este correo.
            """
            
            # Adjuntar ambas versiones
            part1 = MIMEText(text_content, "plain")
            part2 = MIMEText(html_content, "html")
            message.attach(part1)
            message.attach(part2)
            
            # Enviar el email vía Gmail
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(self.gmail_email, self.gmail_password)
                server.send_message(message)
            
            print(f"✅ Email de verificación enviado a: {recipient_email}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            print(f"❌ Error de autenticación Gmail. Verifica tu email y App Password")
            return False
        except smtplib.SMTPException as e:
            print(f"❌ Error al enviar email: {e}")
            return False
        except Exception as e:
            print(f"❌ Error al enviar email de verificación: {e}")
            return False
    
    def send_welcome_email(self, recipient_email: str, username: str) -> bool:
        """
        Envía un email de bienvenida después de verificar la cuenta usando Gmail SMTP
        
        Args:
            recipient_email (str): Email del destinatario
            username (str): Nombre del usuario
            
        Returns:
            bool: True si el email se envió correctamente, False en caso contrario
        """
        # Si no está configurado Gmail, solo mostrar en consola
        if not self.gmail_configured:
            print("\n" + "=" * 70)
            print("🎉 EMAIL DE BIENVENIDA (MODO DESARROLLO - SIN GMAIL)")
            print("=" * 70)
            print(f"📨 Para: {recipient_email}")
            print(f"👤 Usuario: {username}")
            print(f"✅ ¡Cuenta verificada exitosamente!")
            print("=" * 70 + "\n")
            return True
        
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = "¡Cuenta verificada exitosamente! - Sistema de Gestión"
            message["From"] = self.gmail_email
            message["To"] = recipient_email
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .container {{
                        background-color: #f9f9f9;
                        border-radius: 10px;
                        padding: 30px;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    }}
                    .header {{
                        text-align: center;
                        color: #4CAF50;
                        margin-bottom: 30px;
                    }}
                    .success {{
                        background-color: #d4edda;
                        border-left: 4px solid #28a745;
                        padding: 15px;
                        margin: 20px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>✓ ¡Cuenta verificada!</h1>
                    </div>
                    
                    <div class="success">
                        <p><strong>¡Felicitaciones, {username}!</strong></p>
                        <p>Tu cuenta ha sido verificada exitosamente.</p>
                    </div>
                    
                    <p>Ya puedes acceder a todas las funcionalidades del sistema.</p>
                    <p>Gracias por unirte a nosotros.</p>
                    
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666; text-align: center;">
                        <p>&copy; 2025 Sistema de Gestión. Todos los derechos reservados.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
            ¡Cuenta verificada!
            
            ¡Felicitaciones, {username}!
            
            Tu cuenta ha sido verificada exitosamente.
            Ya puedes acceder a todas las funcionalidades del sistema.
            
            Gracias por unirte a nosotros.
            """
            
            part1 = MIMEText(text_content, "plain")
            part2 = MIMEText(html_content, "html")
            message.attach(part1)
            message.attach(part2)
            
            # Enviar el email vía Gmail
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(self.gmail_email, self.gmail_password)
                server.send_message(message)
            
            print(f"✅ Email de bienvenida enviado a: {recipient_email}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            print(f"❌ Error de autenticación Gmail. Verifica tu email y App Password")
            return False
        except smtplib.SMTPException as e:
            print(f"❌ Error al enviar email: {e}")
            return False
        except Exception as e:
            print(f"❌ Error al enviar email de bienvenida: {e}")
            return False


# Instancia singleton del servicio
email_service = EmailService()

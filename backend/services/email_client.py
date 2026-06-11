"""
email_client.py -- Envío de correos vía SendGrid
=================================================
Requiere en .env:
  SENDGRID_API_KEY=SG.xxxxxxxxxxxx
  QUIMERA_FROM_EMAIL=hola@tudominio.com      # Debe estar verificado en SendGrid
  QUIMERA_FROM_NAME=Quimera AI
  QUIMERA_APP_URL=https://quimera.ai         # URL del app para los CTAs

Si SENDGRID_API_KEY está vacío, los envíos se omiten con un log warning.
"""

import os
import asyncio
import logging

logger = logging.getLogger(__name__)

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
FROM_EMAIL       = os.getenv("QUIMERA_FROM_EMAIL", "hola@quimera.ai")
FROM_NAME        = os.getenv("QUIMERA_FROM_NAME", "Quimera AI")
APP_URL          = os.getenv("QUIMERA_APP_URL", "http://localhost:3000")


# ============================================================================
# Templates HTML
# ============================================================================

def _welcome_html(name: str) -> str:
    """Email de bienvenida para nuevo usuario registrado."""
    first_name = name.strip().split()[0] if name.strip() else "diseñador"

    features = [
        ("✦", "Genera sitios HTML completos",
         "Describe tu interfaz y Quimera la construye en segundos con Gemini 2.5"),
        ("◆", "Edita visualmente en Studio",
         "Cambia colores, textos y elementos con un solo clic sin tocar código"),
        ("▲", "Guarda en tu biblioteca",
         "Todos tus diseños disponibles entre sesiones, siempre accesibles"),
    ]

    features_html = ""
    for icon, title, desc in features:
        features_html += f"""
        <tr>
          <td style="padding-bottom:16px;">
            <table cellpadding="0" cellspacing="0"><tr>
              <td style="vertical-align:top;padding-right:12px;">
                <div style="width:26px;height:26px;border-radius:8px;
                            background:rgba(99,102,241,0.2);
                            text-align:center;line-height:26px;
                            font-size:12px;color:#818cf8;">
                  {icon}
                </div>
              </td>
              <td>
                <p style="margin:0;font-size:13px;font-weight:600;
                           color:rgba(255,255,255,0.85);">{title}</p>
                <p style="margin:3px 0 0;font-size:12px;
                           color:rgba(255,255,255,0.38);line-height:1.5;">{desc}</p>
              </td>
            </tr></table>
          </td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Bienvenido/a a Quimera</title>
</head>
<body style="margin:0;padding:0;background:#0D0D10;
             font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;">

  <table width="100%" cellpadding="0" cellspacing="0"
         style="background:#0D0D10;padding:48px 20px 60px;">
    <tr><td align="center">
      <table width="560" cellpadding="0" cellspacing="0"
             style="max-width:560px;width:100%;">

        <!-- Logotipo -->
        <tr><td align="center" style="padding-bottom:36px;">
          <table cellpadding="0" cellspacing="0"><tr>
            <td style="vertical-align:middle;padding-right:10px;">
              <div style="width:42px;height:42px;border-radius:13px;
                          background:linear-gradient(135deg,#4F46E5,#7C3AED);
                          box-shadow:0 0 30px rgba(99,102,241,0.4);">
              </div>
            </td>
            <td style="vertical-align:middle;">
              <span style="font-size:22px;font-weight:900;color:#ffffff;
                           letter-spacing:-0.035em;">
                Quimera <span style="color:#818cf8;">AI</span>
              </span>
            </td>
          </tr></table>
        </td></tr>

        <!-- Card principal -->
        <tr><td style="background:#1C1C1F;
                        border:1px solid rgba(255,255,255,0.08);
                        border-radius:20px;
                        overflow:hidden;">

          <!-- Gradiente superior -->
          <div style="height:4px;
                      background:linear-gradient(90deg,#4F46E5,#7C3AED,#4F46E5);"></div>

          <table width="100%" cellpadding="0" cellspacing="0">

            <!-- Cabecera -->
            <tr><td style="padding:36px 36px 28px;">
              <h1 style="margin:0 0 10px;font-size:26px;font-weight:800;
                          color:#ffffff;letter-spacing:-0.04em;line-height:1.2;">
                ¡Bienvenido/a a Quimera,<br>{first_name}! 🎉
              </h1>
              <p style="margin:0;font-size:15px;color:rgba(255,255,255,0.45);
                         line-height:1.7;">
                Tu cuenta está lista. Ahora puedes diseñar interfaces increíbles
                describiendo lo que necesitas — sin escribir una línea de código.
              </p>
            </td></tr>

            <!-- Separador -->
            <tr><td style="padding:0 36px;">
              <div style="height:1px;background:rgba(255,255,255,0.06);"></div>
            </td></tr>

            <!-- Características -->
            <tr><td style="padding:28px 36px 20px;">
              <p style="margin:0 0 20px;font-size:10px;font-weight:700;
                          color:rgba(255,255,255,0.28);
                          text-transform:uppercase;letter-spacing:0.1em;">
                Lo que puedes hacer
              </p>
              <table width="100%" cellpadding="0" cellspacing="0">
                {features_html}
              </table>
            </td></tr>

            <!-- CTA -->
            <tr><td style="padding:8px 36px 36px;text-align:center;">
              <a href="{APP_URL}"
                 style="display:inline-block;padding:14px 36px;
                         background:linear-gradient(135deg,#4F46E5,#7C3AED);
                         color:#ffffff;font-size:14px;font-weight:700;
                         text-decoration:none;border-radius:12px;
                         letter-spacing:-0.01em;
                         box-shadow:0 4px 20px rgba(99,102,241,0.4);">
                Empezar a diseñar →
              </a>
            </td></tr>

          </table>
        </td></tr>

        <!-- Footer -->
        <tr><td align="center" style="padding-top:28px;">
          <p style="margin:0;font-size:11px;
                     color:rgba(255,255,255,0.18);line-height:2;">
            Powered by Gemini 2.5 Pro · Google AI Agents Challenge 2026<br>
            Si no creaste esta cuenta, puedes ignorar este correo.
          </p>
        </td></tr>

      </table>
    </td></tr>
  </table>

</body>
</html>"""


# ============================================================================
# Funciones públicas
# ============================================================================

async def send_welcome_email(name: str, to_email: str) -> bool:
    """
    Envía el correo de bienvenida de forma async.
    Retorna True si fue enviado correctamente.
    Si no hay API key configurada, retorna False sin lanzar excepción.
    """
    if not SENDGRID_API_KEY:
        logger.warning(
            "SENDGRID_API_KEY no configurada. "
            "Email de bienvenida a %s omitido.", to_email
        )
        return False
    if not to_email or "@" not in to_email:
        logger.warning("Email inválido: %s. Omitiendo envío.", to_email)
        return False

    try:
        return await asyncio.to_thread(_send_sync_welcome, name, to_email)
    except Exception as e:
        logger.error("Error enviando welcome email a %s: %s", to_email, e)
        return False


def _send_sync_welcome(name: str, to_email: str) -> bool:
    """Llamada síncrona a SendGrid (corre en thread pool)."""
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail

    first_name = name.strip().split()[0] if name.strip() else "diseñador"

    message = Mail(
        from_email=(FROM_EMAIL, FROM_NAME),
        to_emails=to_email,
        subject=f"Bienvenido/a a Quimera, {first_name} 🎉",
        html_content=_welcome_html(name),
    )

    sg = SendGridAPIClient(SENDGRID_API_KEY)
    response = sg.send(message)

    success = response.status_code in (200, 202)
    if success:
        logger.info(
            "Welcome email enviado a %s (HTTP %s)",
            to_email, response.status_code
        )
    else:
        logger.error(
            "SendGrid retornó HTTP %s para %s",
            response.status_code, to_email
        )
    return success

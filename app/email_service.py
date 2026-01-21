# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart

# from app.config import (
#     SMTP_HOST,
#     SMTP_PORT,
#     SMTP_USER,
#     SMTP_PASS,
#     RECEIVER_EMAIL,
# )

# def send_contact_email(name: str, email: str, contact_no: str, message: str):
#     subject = "New Contact Form Submission - Uplife"

#     body = f"""
# New contact form submission:

# Name: {name}
# Email: {email}
# Contact No: {contact_no}

# Message:
# {message}
# """

#     msg = MIMEMultipart()
#     msg["From"] = SMTP_USER
#     msg["To"] = RECEIVER_EMAIL
#     msg["Subject"] = subject

#     msg.attach(MIMEText(body, "plain"))

#     with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
#         server.starttls()
#         server.login(SMTP_USER, SMTP_PASS)
#         server.send_message(msg)


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.config import (
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USER,
    SMTP_PASS,
    RECEIVER_EMAIL,
)

def send_contact_email(name: str, email: str, contact_no: str, message: str):
    subject = "New Contact Form Submission – Uplife"

    html_body = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <title>Uplife Contact</title>
</head>
<body style="margin:0; padding:0; background-color:#f4f6f6; font-family:Arial, sans-serif;">

  <table width="100%" cellpadding="0" cellspacing="0">
    <tr>
      <td align="center" style="padding:30px 10px;">
        <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff; border-radius:8px; overflow:hidden;">

          <!-- Header -->
          <tr>
            <td style="background:#457e7f; padding:20px 30px;">
              <h2 style="margin:0; color:#ffffff; font-size:22px;">
                Uplife – Contact Form
              </h2>
            </td>
          </tr>

          <!-- Content -->
          <tr>
            <td style="padding:30px; color:#333333; font-size:15px; line-height:1.6;">
              <p style="margin-top:0;">
                You have received a new contact form submission.
              </p>

              <table width="100%" cellpadding="0" cellspacing="0" style="margin-top:20px;">
                <tr>
                  <td style="padding:8px 0; font-weight:bold; color:#457e7f;">Name</td>
                  <td style="padding:8px 0;">{name}</td>
                </tr>
                <tr>
                  <td style="padding:8px 0; font-weight:bold; color:#457e7f;">Email</td>
                  <td style="padding:8px 0;">{email}</td>
                </tr>
                <tr>
                  <td style="padding:8px 0; font-weight:bold; color:#457e7f;">Contact No</td>
                  <td style="padding:8px 0;">{contact_no}</td>
                </tr>
              </table>

              <div style="margin-top:25px;">
                <p style="font-weight:bold; color:#457e7f; margin-bottom:8px;">
                  Message
                </p>
                <div style="background:#f4f6f6; padding:15px; border-radius:6px; white-space:pre-line;">
                  {message}
                </div>
              </div>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#f4f6f6; padding:15px 30px; text-align:center; font-size:12px; color:#777;">
              This email was sent from the Uplife website contact form.
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>

</body>
</html>
"""

    msg = MIMEMultipart("alternative")
    msg["From"] = SMTP_USER
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = subject

    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

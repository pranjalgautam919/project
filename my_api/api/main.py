
import os
from smtplib import SMTP, SMTP_SSL
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Initialize FastAPI app
app = FastAPI()

# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(__file__), 'requirment.env')
load_dotenv(dotenv_path)

# Function to send an email
def send_email(name: str, email: str, phone: str, language: str, description: str):
    # Retrieve environment variables
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port_ssl = int(os.getenv('SMTP_PORT_SSL', 465))
    smtp_port_tls = int(os.getenv('SMTP_PORT_TLS', 587))
    email_user = os.getenv('EMAIL_USER')
    email_password = os.getenv('EMAIL_PASSWORD')
    recipient_email = os.getenv('RECIPIENT_EMAIL')

    # Create the email content
    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = recipient_email
    msg['Subject'] = 'New Contact Request'

    body = f"""
    Name: {name}
    Email: {email}
    Phone: {phone}
    Language: {language}
    Description: {description}
    """
    msg.attach(MIMEText(body, 'plain'))

    # Print statements for debugging
    print(f"SMTP Server: {smtp_server}")
    print(f"SMTP Port SSL: {smtp_port_ssl}")
    print(f"SMTP Port TLS: {smtp_port_tls}")
    print(f"Email User: {email_user}")
    print(f"Recipient Email: {recipient_email}")
    print(f"Email Body:\n{body}")

    # Send the email using SSL
    try:
        with SMTP_SSL(smtp_server, smtp_port_ssl) as server:
            server.login(email_user, email_password)
            server.sendmail(email_user, recipient_email, msg.as_string())
        return True
    except Exception as e_ssl:
        print(f'Failed to send email using SSL. Error: {e_ssl}')
        
        # Try using TLS if SSL fails
        try:
            with SMTP(smtp_server, smtp_port_tls) as server:
                server.starttls()
                server.login(email_user, email_password)
                server.sendmail(email_user, recipient_email, msg.as_string())
            return True
        except Exception as e_tls:
            print(f'Failed to send email using TLS. Error: {e_tls}')
            return False

# Define the /contact/ endpoint
@app.post("/contact/")
async def contact(
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    language: str = Form(...),
    description: str = Form(...)
):
    email_sent = send_email(name, email, phone, language, description)
    if email_sent:
        return JSONResponse(content={"message": "Thank you! We will contact you soon."})
    else:
        raise HTTPException(status_code=500, detail="Failed to send email. Please try again later.")

# Run the FastAPI application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



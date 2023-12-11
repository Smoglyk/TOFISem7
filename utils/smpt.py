from fastapi import FastAPI, File, UploadFile
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(to_email: str, subject: str, body: str):
    # Здесь укажите данные вашего SMTP-сервера
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'CableNathe@gmail.com'
    smtp_password = 'utxyzvgmoyrddheu'

    # Создаем объект сервера SMTP
    server = smtplib.SMTP(smtp_server, smtp_port)

    # Начинаем сессию
    server.starttls()

    # Авторизация на сервере SMTP
    server.login(smtp_username, smtp_password)

    # Создаем сообщение
    message = MIMEMultipart()
    message["From"] = smtp_username
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    # Отправляем сообщение
    server.sendmail(smtp_username, to_email, message.as_string())

    # Завершаем сессию
    server.quit()

    return

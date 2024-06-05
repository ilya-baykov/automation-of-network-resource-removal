import smtplib
from email.message import EmailMessage
from pathlib import Path
from typing import Optional
from src.utils.json_reader import ConfigParams
from logging import getLogger

logger = getLogger(__name__)


class EmailSender:
    def __init__(self, smtp_server: str = 'mail.center.rt.ru') -> None:
        """
        Инициализирует объект EmailSender.

        Args:
            smtp_server (str): Адрес SMTP-сервера. По умолчанию 'mail.center.rt.ru'.
        """
        self.smtp_server = smtp_server

    def send_email(self, sender_email: str, recipient_emails: list, subject: str, message: str,
                   attachment_path: Optional[str] = None) -> str:
        """
        Отправляет электронное письмо с возможным вложением.

        Args:
            sender_email (str): Адрес электронной почты отправителя.
            recipient_emails (list): Адреса электронной почты получателя.
            subject (str): Тема письма.
            message (str): Содержание сообщения письма.
            attachment_path (str, optional): Путь к файлу вложения. По умолчанию None.

        Returns:
            str: Сообщение об успешной или неудачной отправке письма.
        """
        try:
            msg = EmailMessage()
            msg['Subject'] = subject.encode('utf-8').decode('utf-8')
            msg['From'] = sender_email
            msg['To'] = ", ".join(recipient_emails)
            msg.set_content(message, subtype='plain', charset='utf-8')

            if attachment_path:
                file_path = Path(attachment_path)
                with file_path.open('rb') as fp:
                    msg.add_attachment(
                        fp.read(),
                        maintype='application',
                        subtype=file_path.suffix,
                        filename=file_path.name
                    )

            with smtplib.SMTP(self.smtp_server) as smtp_obj:
                smtp_obj.send_message(msg)
                logger.info("Электронное письмо успешно отправлено")
                return "Электронное письмо успешно отправлено"
        except Exception as e:
            logger.error("Ошибка при отправке письма: %s", e)
            return f"Ошибка при отправке письма: {e}"


def send_email(json_params: ConfigParams, attached_file_path: Optional[str] = None):
    email_sender = EmailSender(smtp_server="mail.center.rt.ru")
    email_sender.send_email(
        sender_email=json_params.mail_sender,
        recipient_emails=json_params.mail_recipients,
        subject=json_params.subject,
        message=json_params.message,
        attachment_path=attached_file_path
    )

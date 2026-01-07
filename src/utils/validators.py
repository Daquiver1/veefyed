"""Validators module."""

import re

import validators


class Validators:
    """Validators class."""

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate an email address."""
        if not email:
            return False

        if not validators.email(email): # type: ignore
            return False

        if email.endswith(".con"):
            return False

        disposable_domains = {
            "mailinator.com",
            "10minutemail.com",
            "temp-mail.org",
            "yopmail.com",
            "guerrillamail.com",
            "discardmail.com",
            "maildrop.cc",
            "fakeinbox.com",
            "getnada.com",
            "temp.com",
            "test.com",
            "test1.com",
            "test2.com",
            "temp1.com",
            "temp2.com",
        }

        domain = email.split("@")[1].lower()
        if domain in disposable_domains:
            return False

        dummy_patterns = [
            r"^test@",
            r"^dummy@",
            r"^fake@",
            r"^no-reply@",
            r"^temp@",
            r"^trial@",
            r"^trial1@",
            r"^temp1@",
            r"^temp2@",
            r"^example@",
            r"^[a-zA-Z]@[a-zA-Z]\.[a-zA-Z]{2,}$",
        ]
        return not any(re.match(pattern, email) for pattern in dummy_patterns)

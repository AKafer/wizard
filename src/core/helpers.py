from datetime import date, timedelta

from database.models import Certificates


def is_cert_expired(cert: Certificates) -> bool:
    if cert.indefinite:
        return False

    deadline = cert.created_at + timedelta(days=cert.period)
    return date.today() >= deadline

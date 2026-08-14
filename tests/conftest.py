"""Suiteweite Isolation externer Credentialspeicher."""

import keyring
import pytest
from keyring.errors import PasswordDeleteError


@pytest.fixture(autouse=True)
def isolated_keyring(monkeypatch):
    """Verhindert echte Keyring-Zugriffe durch SettingsManager-Tests."""
    entries = {}

    def get_password(service, account):
        return entries.get((service, account))

    def set_password(service, account, value):
        entries[(service, account)] = value

    def delete_password(service, account):
        try:
            del entries[(service, account)]
        except KeyError as exc:
            raise PasswordDeleteError("credential not found") from exc

    monkeypatch.setattr(keyring, "get_password", get_password)
    monkeypatch.setattr(keyring, "set_password", set_password)
    monkeypatch.setattr(keyring, "delete_password", delete_password)

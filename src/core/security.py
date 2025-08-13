"""
Módulo de seguridad para NeXOptimIA
Implementa protocolo GibberLink-RF (ofuscación XOR+salt) y cifrado AES-256
Singleton thread-safe para acceso global
"""
from typing import Optional
from threading import Lock
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
import os

class SecurityManager:
    """
    Singleton para seguridad: GibberLink-RF y AES-256
    """
    _instance: Optional['SecurityManager'] = None
    _lock: Lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init()
            return cls._instance

    def _init(self):
        self._aes_key = os.environ.get('NEXOPTIMIA_AES_KEY') or base64.urlsafe_b64encode(get_random_bytes(32)).decode()
        self._salt = os.environ.get('NEXOPTIMIA_GIBBER_SALT') or 'nexoptimia2025'

    def gibber(self, data: bytes) -> bytes:
        """
        Ofusca datos usando XOR+salt (GibberLink-RF capa 1)
        """
        salt_bytes = self._salt.encode()
        return bytes([b ^ salt_bytes[i % len(salt_bytes)] for i, b in enumerate(data)])

    def ungibber(self, data: bytes) -> bytes:
        """
        Revierte la ofuscación XOR+salt
        """
        return self.gibber(data)  # XOR reversible

    def encrypt(self, data: bytes) -> bytes:
        """
        Cifra datos con AES-256 (Capa 2)
        """
        key = base64.urlsafe_b64decode(self._aes_key)
        iv = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_CFB, iv=iv)
        ciphertext = cipher.encrypt(data)
        return base64.b64encode(iv + ciphertext)

    def decrypt(self, token: bytes) -> bytes:
        """
        Descifra datos AES-256
        """
        raw = base64.b64decode(token)
        key = base64.urlsafe_b64decode(self._aes_key)
        iv = raw[:16]
        cipher = AES.new(key, AES.MODE_CFB, iv=iv)
        return cipher.decrypt(raw[16:])

# Instancia global
security_manager = SecurityManager()

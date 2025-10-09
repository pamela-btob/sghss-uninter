from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from django.db import models

# Gera uma chave Fernet válida a partir de uma senha
def generate_fernet_key():
    password = b"minha_senha_secreta_sghss_2025"  # Em produção, use variável de ambiente
    salt = b"sghss_salt_2025"  # Em produção, use um salt único
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key

KEY = generate_fernet_key()

class EncryptedField(models.CharField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cipher = Fernet(KEY)
    
    def get_prep_value(self, value):
        if value is None or value == "":
            return value
        # Criptografa o valor antes de salvar no banco
        try:
            encrypted_value = self.cipher.encrypt(value.encode('utf-8'))
            return base64.urlsafe_b64encode(encrypted_value).decode('utf-8')
        except Exception as e:
            # Se der erro na criptografia, retorna o valor original
            print(f"Erro na criptografia: {e}")
            return value
    
    def from_db_value(self, value, expression, connection):
        if value is None or value == "":
            return value
        # Descriptografa o valor ao ler do banco
        try:
            encrypted_value = base64.urlsafe_b64decode(value.encode('utf-8'))
            decrypted_value = self.cipher.decrypt(encrypted_value)
            return decrypted_value.decode('utf-8')
        except Exception as e:
            # Se der erro na descriptografia, retorna o valor criptografado
            print(f"Erro na descriptografia: {e}")
            return value
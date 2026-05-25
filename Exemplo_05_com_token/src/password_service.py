from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerifyMismatchError

_ph = PasswordHasher()


def hash_senha(senha: str) -> str:
    """Recebe uma senha em texto puro e retorna o hash argon2."""
    return _ph.hash(senha)


def verificar_senha(hash_salvo: str, tentativa: str) -> bool:
    """
    Compara a tentativa com o hash salvo.
    Retorna True se a senha estiver correta, False caso contrário.
    """
    try:
        _ph.verify(hash_salvo, tentativa)
        return True
    except VerifyMismatchError:
        return False

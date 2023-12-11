from bcrypt import hashpw, gensalt, checkpw
import hashlib

def hash_password(password: str):
    salt = gensalt()
    sha256 = hashlib.sha256()
    sha256.update(password.encode('utf-8'))
    hashed_password = sha256.hexdigest()

    return hashed_password

def verify_password(plain_password: str, hashed_password: str):

    return hash_password(plain_password) == hashed_password

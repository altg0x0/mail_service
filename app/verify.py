from hashlib import sha512
import crypt
import base64
from hmac import compare_digest as constant_time_compare

def verify(password, encoded):
    striped = encoded.replace('{SHA512-CRYPT}', '')
    salt = striped[:19]
    #print(password, crypt.crypt(password,  salt))
    return constant_time_compare(striped, crypt.crypt(password,  salt))

import hashlib
import base64
from Crypto import Random
from Crypto.Cipher import AES

BS = 16
pad = lambda s: bytes(s + (BS - len(s) % BS) * chr(BS - len(s) % BS), 'utf-8')
unPad = lambda s: s[0:-ord(s[-1:])]


class AESCipher:

    def __init__(self, main_key):
        self.key = bytes(main_key, 'utf-8')

    def encrypt(self, raw):
        raw = pad(raw)
        print(raw)
        iv = Random.new().read(AES.block_size)
        cipher_text = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher_text.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher_text = AES.new(self.key, AES.MODE_CBC, iv)
        return unPad(cipher_text.decrypt(enc[16:])).decode('utf-8')


def hasher(k):
    hash_object = hashlib.sha512(k.encode('utf-8'))
    hexd = hash_object.hexdigest()
    hash_object = hashlib.md5(hexd.encode('utf-8'))
    hex_dig = hash_object.hexdigest()
    return hex_dig


key = "akhil archit salman mradima"
key_hash = hasher(key)

message = "Hello its encrypted"

cipher = AESCipher(key_hash)
encrypted = cipher.encrypt(message)
decrypted = cipher.decrypt(encrypted)

print(encrypted)
print(decrypted)

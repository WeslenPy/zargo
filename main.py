from  zargo.argo_message_decoder import ArgoMessageDecoder
import base64,binascii
import json
from zargo.utils.jid import Jid
from Crypto.Cipher import AES
import re
import base64
class BytesEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, bytes):
            if obj[0]==250 or obj[0]==247:
                return Jid.readJid(obj)
            else:
                return base64.b64encode(obj).decode('utf-8') 
        return json.JSONEncoder.default(self, obj)

import hashlib
class RCDecrypt:
    RECOVERY_TOKEN_HEADER = b"\x00\x02"
    

    def __init__(self,phone_number:str, google_play_email = ""):
        self.pn = phone_number
        self.email = google_play_email
        self.RC_SECRET = self.decode("A\u0004\u001d@\u0011\u0018V\u0091\u0002\u0090\u0088\u009f\u009eT(3{;ES")
        
        
    def sxor(self, s1, s2):
        return ''.join(chr(ord(a) ^ ord(b)) for a,b in zip(s1,s2))

    def decode(self, s):
        sb = []
        for i in range(len(s)):
            sb.append(self.sxor("\u0012", s[i]))
        return ''.join(sb)

    def get_recovery_token(self,data:bytes):
        secret =self.RC_SECRET + self.get_recovery_jid_from_jid(self.pn) + self.email;
        result =  self.get_encrypted_data(secret, data)

        print(base64.b64encode(result))

        return f"{self.pn}#".encode()+result
    
    
    def get_encrypted_data(self, secret, data):
        data = data[27:]
        header = data[:2]
        salt = data[2:6]
        iv = data[6:22]
        encrypted_data = data[22:42]

        if header != self.RECOVERY_TOKEN_HEADER:
            raise Exception('Header mismatch')

        key = self.get_key(secret, salt)
        cipher = AES.new(key, AES.MODE_OFB, iv)

        return cipher.decrypt(encrypted_data)

    def get_key(self, secret, salt):
        return hashlib.pbkdf2_hmac('sha1', 
                                   bytes(secret, 'utf-8'), 
                                   salt, 16, 16)

    def get_recovery_jid_from_jid(self, phone_number):
        c = re.compile("^([17]|2[07]|3[0123469]|4[013456789]|5[12345678]|6[0123456]|8[1246]|9[0123458]|\d{3})\d*?(\d{4,6})$")
        g = c.match(phone_number)

        if g is not None:
            return g.group(1) + g.group(2)
        else:
            return ""
    
    def decrypt(self,data:bytes):
        
        decoded = self.get_recovery_token(data)

        print(decoded)
        
        return base64.b64encode(decoded).decode()        
    
if __name__ == "__main__":

    a = RCDecrypt("919986514543","")

    f = open("D:\\rc2","rb")

    data = f.read()


    b = a.decrypt(data)

    print(b)


    '''

    ArgoMessageDecoder.setSchemaFile("d:\\argo-wire-type-store.argo")

    #receivedBytes = b'\x04bNot Allowederror_codeis_retryableseverityCRITICAL\x06\x00\xaa\x06"\x00\x01\x02\x16\x03\x02\x00\x04\x06\x14\x0c\x18\x00\x10\x08\x10\x03'

    receivedBytes = b'\x04dXWA2BusinessUserXWA2ResponseStatusXWA2Reachability\x14\xfa\xff\x86\x16&ad6?\x03\nEMPTY4\x00\x02 \x01\x14\x00$\x03\x03\x03\x03\n\x00 \x00\x03\x03\x03\x03\x03\x03\x03\x03\x03\x03\x03'



    print(base64.b64encode(receivedBytes))
    obj = ArgoMessageDecoder.decodeMessage("ContactsBackupQuery",receivedBytes)

    x = json.dumps(obj,cls=BytesEncoder)
    print(x)
    '''
    







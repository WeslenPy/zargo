from  zargo.argo_message_decoder import ArgoMessageDecoder
import base64,binascii
import json
from zargo.utils.jid import Jid

class BytesEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, bytes):
            if obj[0]==250 or obj[0]==247:
                return Jid.readJid(obj)
            else:
                return base64.b64encode(obj).decode('utf-8') 
        return json.JSONEncoder.default(self, obj)
    
if __name__ == "__main__":




    ArgoMessageDecoder.setSchemaFile("d:\\argo-wire-type-store.argo")

    #receivedBytes = b'\x04bNot Allowederror_codeis_retryableseverityCRITICAL\x06\x00\xaa\x06"\x00\x01\x02\x16\x03\x02\x00\x04\x06\x14\x0c\x18\x00\x10\x08\x10\x03'

    receivedBytes = b'\x04dXWA2BusinessUserXWA2ResponseStatusXWA2Reachability\x14\xfa\xff\x86\x16&ad6?\x03\nEMPTY4\x00\x02 \x01\x14\x00$\x03\x03\x03\x03\n\x00 \x00\x03\x03\x03\x03\x03\x03\x03\x03\x03\x03\x03'



    print(base64.b64encode(receivedBytes))
    obj = ArgoMessageDecoder.decodeMessage("ContactsBackupQuery",receivedBytes)

    x = json.dumps(obj,cls=BytesEncoder)
    print(x)
    







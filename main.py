from  zargo.argo_message_decoder import ArgoMessageDecoder
import base64,binascii
import json
from zargo.utils.jid import Jid

class BytesEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, bytes):
            if obj[0]==250:
                return Jid.readJid(obj);
            else:
                return base64.b64encode(obj).decode('utf-8') 
        return json.JSONEncoder.default(self, obj)
    
if __name__ == "__main__":

    ArgoMessageDecoder.setSchemaFile("/Volumes/Project_Wisight/argo-wire-type-store.argo")

    receivedBytes = base64.b64decode("BIQBWFdBMkJ1c2luZXNzVXNlclhXQTJJbnRlZ3JpdHlTaWduYWxzMTc0MDU0MTM4NzAwMFRMMTc0MDA3NTMzMjAwMExLKPr/hmcHY4MATwP6/4aUcoAhFR8DFFNVU1BJQ0lPVVNAAAQgARQAKAEAAgEBGgQUAwcBFAAJAQACAQEaBAcDAwM=")
    obj = ArgoMessageDecoder.decodeMessage("BizIntegrityQuery",receivedBytes)

    x = json.dumps(obj,cls=BytesEncoder)
    print(x)









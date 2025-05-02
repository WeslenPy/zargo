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

    ArgoMessageDecoder.setSchemaFile("/Volumes/Project_Wisight/argo-wire-type-store.argo")

    receivedBytes = b"\x04\x18PHONE_NUMBER(XWA2ParticipantError\x1c\x00\x00\x00\x18\x02(\x03\x03\x03\x03\x01\x01\x03\x03"

    print(base64.b64encode(receivedBytes))
    obj = ArgoMessageDecoder.decodeMessage("AddParticipantsToGroupV2",receivedBytes)

    x = json.dumps(obj,cls=BytesEncoder)
    print(x)
    







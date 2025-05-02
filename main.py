from  zargo.argo_message_decoder import ArgoMessageDecoder
import base64
import json

class BytesEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return base64.b64encode(obj).decode('utf-8') 
        return json.JSONEncoder.default(self, obj)
    
if __name__ == "__main__":

    ArgoMessageDecoder.loadSchemaDataFromFile("/Volumes/Project_Wisight/argo-wire-type-store.argo")

    receivedBytes = base64.b64decode("BAIwCgAAAgMD")
    obj = ArgoMessageDecoder.decodeMessage("FetchReachoutTimelockQuery",receivedBytes)

    x = json.dumps(obj,cls=BytesEncoder)
    print(x)









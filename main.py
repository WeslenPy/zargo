import sys
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

    receivedBytes = base64.b64decode("BEJYV0EyVXNlclhXQTJMaWRYV0EyTGlua2VkUHJvZmlsZXMW+v+HhhmHRAYUTwMa9wEA/4gkiEY0UQFRHy4AAhABFgMDAwMDAwMDAA4aAwAkAAMDAw==")

    receivedBytes = base64.b64decode("BEJYV0EyVXNlclhXQTJMaWRYV0EyTGlua2VkUHJvZmlsZXMq+v+HhhmHRAYUTwP6/wYgERIGZnQDNPcBAP+IJIhGNFEBUR/3AQD/iBcpRZhQMiAvVAAEEAEWAwMDAwMDAwMADhoDACQAAwcBFAMDAwMDAwMDAAkaAwALAAMDAw==")
    #receivedBytes = base64.b64decode("BAIwCgAAAgMD")
    obj = ArgoMessageDecoder.decodeMessage("UsyncQuery",receivedBytes)

    x = json.dumps(obj,cls=BytesEncoder)
    print(x)












class ErrorWireType :

    def  __init__(self,message,locations,path,extensions):
        self.message = message
        self.locations = locations  
        self.path = path
        self.extensions = extensions

    def __str__(self):
        return "ErrorWireType(message=%s,location=%s,path=%s,extensions=%s)" % (self.message,self.locations,self.path,self.extensions)
    
    




    
class ClientLogger:
    """ 
    Cleared out between requests.
    Using a singleton because I don't want to pass it to every function signature.
    """
    class __ClientLogger:
        def __init__(self):
            self.request_logs = []
    
    instance = None
    def __init__(self):
        if not ClientLogger.instance:
            ClientLogger.instance = ClientLogger.__ClientLogger()

    def log(self, message):
        # print(message)
        self.instance.request_logs.append(message)
    
    def get_logs(self):
        return self.instance.request_logs
    
    def clear_logs(self):
        self.instance.request_logs = []
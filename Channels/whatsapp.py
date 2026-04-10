# Stub for WhatsApp integration.
# Can be implemented via Twilio API or Meta Cloud API later.

class WhatsAppChannel:
    def __init__(self, token: str, agent):
        self.token = token
        self.agent = agent

    def start(self):
        print("[WhatsApp] Channel not fully implemented yet.")
        pass

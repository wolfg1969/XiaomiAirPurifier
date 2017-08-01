import codecs
from .miio import miio


class AirPurifier:
    
    def __init__(self, addr, token, debug=0):
        self.device = miio.device(addr, token, debug=debug)
        
    @staticmethod
    def getToken(addr):
        m = miio.device.discover(addr)
        if m is not None:
            return codecs.encode(m.checksum, 'hex')
        
    def getStatus(self):
        return self.device.raw_command('getProperties')
        
    def powerOn(self):
        pass
        
    def powerOff(self):
        pass
        
    def setFanSpeed(self):
        pass
        
    def setFanMode(self):
        pass
        
    def setLedMode(self):
        pass
        
    def turnOnBuzzer(self):
        pass
        
    def turnOffBuzzer(self):
        pass

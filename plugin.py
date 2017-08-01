# Xiaomi Air Purifier
#
# Author: wolfg1969
#
"""
<plugin key="XiaomiAirPurifier" name="Xiaomi Air Purifier" author="wolfg1969" version="1.0.0"  externallink="https://www.mi.com/air2/">
    <params>
        <param field="Address" label="IP Address" width="150px" required="true"/>
        <param field="Mode1" label="Polling interval (minutes, 5 mini)" width="40px" required="true" default="15"/>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal"  default="true" />
            </options>
        </param>
    </params>
</plugin>
"""
import sys
import Domoticz
from datetime import datetime, timedelta

from .mi_airpurifier import AirPurifier


sys.path.append('/usr/local/lib/python3.4/dist-packages/')


class XiaomiAirPurifierPlugin:
    enabled = False
    def __init__(self):
        self.debug = False
        self.pollinterval = 15
        self.nextupdate = datetime.now()
        return

    def onStart(self):
        if Parameters["Mode6"] == "Debug":
            self.debug = True
            Domoticz.Debugging(1)
        else:
            self.debug = False
            Domoticz.Debugging(0)
            
        # check polling interval parameter
        try:
            temp = int(Parameters["Mode1"])
        except:
            Domoticz.Error("Invalid polling interval parameter")
        else:
            if temp < 5:
                temp = 15  # minimum polling interval
                Domoticz.Error("Specified polling interval too short: changed to 15 minutes")
            elif temp > 1440:
                temp = 1440  # maximum polling interval is 1 day
                Domoticz.Error("Specified polling interval too long: changed to 1440 minutes (24 hours)")
            self.pollinterval = temp
        Domoticz.Log("Using polling interval of {} minutes".format(str(self.pollinterval)))
            
        if (len(Devices) == 0):
            Domoticz.Device(Name="AQI", Unit=1, TypeName="Custom").Create()
            Domoticz.Device(Name="Temperature / Humidity", Unit=2, TypeName="Temp+Hum").Create()
            Domoticz.Device(
                Name="Mi Smart Air Purifier", 
                Unit=3, 
                TypeName="Selector Switch", 
                Options={
                    "LevelActions": "|||||",
                    "LevelNames": "Off|Silent|Auto|Low|Medium|Max",
                    "LevelOffHidden": "false",
                    "SelectorStyle": "0",
                },
                Image=7
            ).Create()
            Domoticz.Log("Devices created.")
            
        self.token = AirPurifier.getToken(Parameters["Address"])
        Domoticz.Debug("getToken: %s" % self.token)
        if not self.token:
            Domoticz.Error("Failed to get token: %s", Parameters["Address"])
            
        DumpConfigToLog()
        Domoticz.Debug("Plugin is started.")

    def onStop(self):
        Domoticz.Debug("Plugin is stopping.")
        Domoticz.Debugging(0)

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called")

    def onMessage(self, Connection, Data, Status, Extra):
        Domoticz.Debug("onMessage called")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Debug("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called")

    def onHeartbeat(self):
        now = datetime.now()
        if now >= self.nextupdate:
            self.nextupdate = now + timedelta(minutes=self.pollinterval)
            self.polldata()
            
    def polldata(self):
        device = AirPurifier(Parameters["Address"], self.token, debug=1 if self.debug else 0)
        #power, mode, aqi, temperature, humidity = device.getStatus()
        status = device.getStatus()
        # Domoticz.Debug("getStatus: %s, %s, %s, %s, %s" % (power, mode, aqi, temperature, humidity))
        Domoticz.Debug("getStatus: %s" % status)


global _plugin
_plugin = XiaomiAirPurifierPlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data, Status, Extra):
    global _plugin
    _plugin.onMessage(Connection, Data, Status, Extra)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return

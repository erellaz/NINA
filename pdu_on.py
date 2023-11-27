import dlipower
#if you get this error: 
# Digital Loggers Web Powerswitch xx.xx.xx.xx.xx(UNCONNECTED)
# Go to the PDU admin page and change:
# Allow legacy plaintext login methods (enable)
# Then also allow this if the outlet cannot be changed by the script:
# Allow legacy state-changing GET requests

hostname=r"192.168.0.xxx:yyy" 
userid="JohnDoe"
password="123456"

print('Connecting to DLI PowerSwitch:',hostname, userid, password)

switch = dlipower.PowerSwitch(hostname=hostname, userid=userid, password=password,use_https=False)

print(switch)

status1=switch.on(outlet=2)
status2=switch.on(outlet=3)


print(switch)





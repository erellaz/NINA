# NINA
Script for NINA start up and end
## NINA Start up scripts

![Nina Start](Nina_start.png)
Wait for a certain time
Use NINA switches and the PDU ASCOM driver to connect to the Digital Loggers Web Powerswitch.
### Alternative
One weakness of NINA is that you can use switches with only one ASCOM driver. If you need to connect to 2 PDUs, or one PDU and one PEGSUS power box, NINA can't do it. 
I provide however a work around: you could use the python programs provided to connect to your  Digital Loggers Web Powerswitch, which then frees the NINA switches
for, for example a PEGSUS power switch accessed via ASCOM.
Power up the Mount bus then the equipment bus.

Start APCC via script, alternativly use the APCC start module in AP tools

If safe, unpark and start the imaging sequence.

## NINA end of session and shut doen scripts
![Nina End(Nina_end.png)
Stop guiding, discoonect the guider and park the scope while warming the camera slowly.
Then kill phd2
Disconnect the rest of the equipment, EXCEPT, of course, the switch (if you used "Disconnect all", then you would not be able to switch off the equipment on the PDU using Switches)
Once the Telescope is disconnected and the Mount id pwoer down, APCC should autoclose on its own after 1 minute. Except sometimes it does not, so for additional safety, kill APCC after 5mn just in case it failed to autoclose.
Same for the AP driver.
Then run a python script to clean up last night production using the NINA CSV.

GNSS+IMU Localization is setup to start running at system startup.

For this purpose, a systemctl service called "autostartLocalization.service" was created. This file is located within the directory "/lib/systemd/system/".

The service runs the "Sender.py" python script that is expected to be located within "/home/pi/NavsparkLocalization/src/".

If you choose to change the location of this file, you will need to update the service. Please see "Systemctl Service Guide" for more information. You will also need to ensure that the "NavMessageParsing.py" python script is kept in the same subdirectory as it.

The IP address of the Jetson board is expected to "192.168.1.100". Please update "UDP_IP" constant in the sender script to reflect the new IP address if this is modified.

The localization message schema is defined in the "NavMessageParsing.py" python script.
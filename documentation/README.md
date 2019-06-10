Getting Started with Localization Node
---

GNSS+IMU Localization is setup to start running at system startup.

For this purpose, a systemctl service called _**autostartLocalization.service**_ was created. This file is located within the directory "_**/lib/systemd/system/**_".

The service runs the _**Sender.py**_ python script that is expected to be located within "_**/home/pi/NavsparkLocalization/src/**_".

If you choose to change the location of this file, you will need to update the service. Please see _**Systemctl Service Guide**_ for more information. You will also need to ensure that the _**NavMessageParsing.py**_ python script is kept in the same subdirectory as it.

The IP address of the Jetson board is expected to `192.168.1.100`. Please update `UDP_IP` constant in the sender script to reflect the new IP address if this is modified.

The localization message schema is defined in the _**NavMessageParsing.py**_ python script.
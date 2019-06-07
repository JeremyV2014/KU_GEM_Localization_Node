Create a new service to run a python script:
	1. Create the service file: sudo nano /lib/systemd/system/<SERVICE_NAME>.service
	2. Add the following to the file:

		 [Unit]
		 Description=<DESCRIPTION OF SERVICE>
		 After=multi-user.target
		
		 [Service]
		 Type=idle
		 ExecStart=/usr/bin/python3 <FILE_PATH>/<FILE_NAME>.py
		
		 [Install]
		 WantedBy=multi-user.target

	3. Modify the file permissions to allow root to run the service: sudo chmod 644 /lib/systemd/system/<SERVICE_NAME>.service
	4. Reload the daemon: sudo systemctl daemon-reload
	5. Enable the service: sudo systemctl enable <SERVICE_NAME>.service
	6. Reboot the system: reboot
	
Updating a service to reflect script location change:
	1. Open the file: sudo nano /lib/systemd/system/<SERVICE_NAME>.service
	2. Modify "ExecStart" to reflect the new location of the script
	3. Reload the daemon: sudo systemctl daemon-reload
	4. Enable the service: sudo systemctl enable <SERVICE_NAME>.service
	5. Reboot the system: reboot

Check enabled services:
	1. systemctl list-unit-files | grep enabled

Check running services:
	1. systemctl | grep running
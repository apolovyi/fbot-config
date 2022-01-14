# Start the service:
sudo systemctl start freq_bot_a.service
sudo systemctl start freq_bot_b.service

# Check the service status:        

# Stop the service:
sudo systemctl stop freq_bot_a.service
sudo systemctl stop freq_bot_b.service

# Enable the service at system startup (start at boot):
sudo systemctl enable freq_bot_a.service
sudo systemctl enable freq_bot_b.service

# Disable the service at system startup (no start at boot):
sudo systemctl disable freq_bot_a.service
sudo systemctl disable freq_bot_b.service

# After each service config change
sudo systemctl daemon-reload

# Show activity 
sudo tail -f /var/log/syslog

## See the bots in action with FreqUI

Open a browser and go to: http://localhost:8080

If your bot is on your local host. Otherwise enter the IP address of the server into the url.

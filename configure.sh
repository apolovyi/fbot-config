cp -r service/* /lib/systemd/system
cp -r user_data/* /opt/freqtrade/user_data
mkdir /opt/freqtrade/user_data/db
cp -r strategies/* /opt/freqtrade/user_data/strategies
sudo chown admin:admin -R /opt
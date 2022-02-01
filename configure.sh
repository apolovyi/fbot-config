cp -r service/* /lib/systemd/system
cp -r user_data/* /opt/freqtrade/user_data
mkdir -p /opt/freqtrade/user_data/db
rm -rf /opt/freqtrade/user_data/db/*
#sudo chown admin:admin -R /opt
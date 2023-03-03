sudo apt update
sudo apt install build-essential wget sudo -y
sudo apt install python3.8 -y
ln -s /usr/bin/python3.8 /usr/bin/python3
python3 -V

sudo apt install python3-pip -y
pip3 install flask
pip3 install paho-mqtt

sudo apt-get update
sudo apt-get dist-upgrade -y
sudo apt-get install openssh-server -y
sudo apt-get install build-essential python-dev python-setuptools python-pip python-smbus -y
sudo apt-get install libncursesw5-dev libgdbm-dev libc6-dev -y
sudo apt-get install zlib1g-dev libsqlite3-dev tk-dev -y
sudo apt-get install libssl-dev openssl -y
sudo apt-get install libffi-dev -y
sudo apt-get install libhdf5-dev -y

tar xvfz /home/dom/dom/Python-3.8.10.tgz
/home/dom/dom/Python-3.8.10/configure
make 
sudo make altinstall
pip3.8 install --upgrade pip setuptools wheel
pip3.8 install tensorflow-2.6.0-cp38-cp38-linux_aarch64.whl
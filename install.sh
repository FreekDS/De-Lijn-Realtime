#!/bin/bash

function installNpm() {
	if hash npm 2>/dev/null; then
		echo "Npm is already installed"
	else
		echo "Npm is not installed, installing...";
		sudo apt-get install curl -y
		curl -sL https://deb.nodesource.com/setup_10.x | sudo -E bash -
		sudo apt-get install nodejs
		if hash npm 2>/dev/null; then
			echo "Successfully installed npm"
		else
			echo "Cannot install npm, try installing it manually"
			exit 1
		fi
	fi
}


function installPython() {
	if hash python3 2>/dev/null; then
		echo "python3 is already installed"
	else
		echo "Python3 is not installed, installing..."
		sudo apt install software-properties-common
		sudo add-apt-repository ppa:deadsnakes/ppa
		sudo apt install python3.7
		if hash python3 2>/div/null; then
			echo "Python3 has been installed"
		else
			echo "Cannot install python3, try installing it manually"
			exit 1
		fi
	fi
}


function installPip() {
	if hash pip3 2>/dev/null; then
		echo "Pip3 is already installed"
	else
		echo "Pip is not installed, installing..."
		sudo apt install python3-pip
		if hash pip3 2>/dev/null; then
			echo "Successfully installed pip3"
		else 
			echo "Cannot install pip3, try installing it manually"
			exit 1
		fi
	fi
}

installNpm
installPython
installPip

sudo pip3 install -r ./WebServices/requirements.txt
sudo npm --prefix ./web-services-front/ install


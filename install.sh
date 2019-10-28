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
			echo "Cannot install npm, trying installing it manually"
			exit 1
		fi
	fi
}


function installPython() {
	if hash python3 2>/dev/null; then
		echo "python3 is already installed"
	else
		echo "Python3 is not installed"
		exit 1
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

installPython
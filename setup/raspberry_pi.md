# Raspberry Pi Setup

## Update system
```bash
sudo apt update
sudo apt upgrade -y
```

## Install Python tools
```bash
sudo apt install python3-pip python3-venv -y
```

## Create virtual environment
```bash
python3 -m venv depthai_env
source depthai_env/bin/activate
```

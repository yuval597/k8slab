Infra-Automation project v1.0

# Overview
This project is an infrastructure provisioning simulator written in Python
It allows the user to create virtual machines (VMs), saves it into JSON file and then install NGINX

# Project Objectives
- Ask for machine details (Name,OS,CPU,RAM)
- Validate the input using Pydantic
- Saving all machines into file configs/instances.json
- Run install_nginx.sh to install or skip NGINX
- Everything written into logs/provisioning.log

# Setup
- Clone the repository
- Create virtual environment
- Install the required python packages from requirements.txt
- Run the program

# How it works
- Program asks Add new machine? (y/n)
- Valid machines saved to JSON
- Script installs NGINX if not already installed
- All actions logged to logs/provisioning.log

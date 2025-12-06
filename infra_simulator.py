# Main autoation script
# This script:
# 1. asks the user to enter machine information
# 2. validates the input
# 3. creates Machine objects
# 4. saves them into configs/instances.json
# 5. runs a bash script to install nginx
# 6. writes logs to logs/provisioning.log

from pydantic import ValidationError
import json
from src.machine import Machine, _machine
import subprocess
import logging

LOG_FILE = "logs/provisioning.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Ask the user to enter machine details (name, OS, CPU, RAM)
# Uses _machine to validate the input
# Returns a Machine object if valid, or None if invalid
def prompt_for_machine ():
    name = input("Enter machine name here: ")
    os = input("Enter required OS here: ")
    cpu = input("Enter required CPU here: ")
    ram = input("Enter required RAM here: ")
    try:
        machine = _machine(
        name=name,
        os=os,
        cpu=cpu,
        ram=ram
        )
        
    except ValidationError as e:
        logger.error("Invalid input: %s", e)
        return None
    
    return machine.model_dump()
    
# Runs the install_nginx.sh bash script
# Uses subprocess to execute the script
# Logs success and errors into the provisioning.log file
def install_service():
    logger.info("Starting NGINX install script (scripts/install_nginx.sh)")
    try:
        logger.info("Running NGINX installation script")
        # Run the bash script and capture its output
        result = subprocess.run(
            ["bash", "scripts/install_nginx.sh"],
            check=True,
            capture_output=True,
            text=True,
        )
        logger.info("NGINX install script finished successfully")
        if result.stdout and result.stdout.strip():
                logger.info("NGINX script stdout:\n%s", result.stdout.strip())
    
    except subprocess.CalledProcessError as e:
        logger.error("NGINX install script failed with exit code %d", e.returncode)
        if e.stdout:
            logger.error("NGINX script stdout on error:\n%s", e.stdout.strip())
        if e.stderr:
            logger.error("NGINX script stderr on error:\n%s", e.stderr.strip())

 # Main program loop
 # Repeatedly asks the user to add machines
 # Saves all collected machines to instances.json
 # Then runs the nginx installation script.       
def main():
    logger.info("Provisioning started")
    machines = []
    # Loops: ask user if they want to add another machine
    while True:
        add_machine = input("Add new machine? (y/n): ").lower()
        if add_machine not in ("y" , "n"):
            print("Please enter 'y' or 'n' only") 
            continue
        if add_machine == "n":
            break 
        machine_data = prompt_for_machine()
        if machine_data:
            machines.append(machine_data)
            print(f"{machine_data['name']} added successfully")

    # Save all machines into configs/instances.json as a list of dictionaries
    with open("configs/instances.json", "w") as f:
        json.dump(machines, f, indent=4)
        logger.info("Saved %d machines to configs/instances.json", len(machines))
    install_service()

if __name__ == "__main__":
    main()
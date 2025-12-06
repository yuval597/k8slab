# This file defines the _machine (for validation) and Machine (final machine object).
# _machine = the actual object we create and save, based on the validated data

import logging
from pydantic import BaseModel, field_validator

logger = logging.getLogger(__name__)

# _machine - validates raw user input for machine details before creating a Machine object
# It makes sure the name is valid, CPU/RAM are numbers, OS is allowed, etc
class _machine(BaseModel):
    name: str
    os: str
    cpu: int
    ram: int

# Validate name field: must contain letters, not only numbers
    @field_validator("name")
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("Name cannot be empty")
        if v.isdigit():
            raise ValueError("Name cannot be numeric")
        return v
    @field_validator("os")
    def validate_os(cls, v):
        if not v.strip():
            raise ValueError("OS cannot be empty")
        if v.isdigit():
            raise ValueError("OS cannot be numeric")
        return v
    @field_validator("cpu", "ram")
    def validate_positive(cls, v:int, info):
        if v <= 0:
            raise ValueError (f"{info.field_name.upper()} must be positive integer")
        return v

    
# Machine class - represents a final machine in the system
# It stores machine data after validation and can turn itself into a dictionary for saving to JSON
class Machine:
    def __init__(self, name, os, cpu, ram):
        self.name = name
        self.os = os
        self.cpu = cpu
        self.ram = ram
        
        logger.info(f"Machine created:{self.name}(OS={self.os},CPU={self.cpu},RAM={self.ram})")

# Convert Machine object into a dictionary (used when saving to JSON file)
    def to_dict(self):
        return {
            "name":self.name,
            "os":self.os,
            "cpu":self.cpu,
            "ram":self.ram

        }
        
import os
import json
import logging
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from api.core.config import settings

logger = logging.getLogger(__name__)

def read_data() -> List[Dict[str, Any]]:
    """
    Reads data from the JSON file. Returns an empty list if file is missing or corrupted.
    Includes validation of file integrity.
    """
    file_path = settings.FILE_PATH
    checksum_path = f"{file_path}.checksum"
    
    if not os.path.exists(file_path):
        logger.warning(f"Data file not found at {file_path}")
        return []
        
    try:
        # Read the file
        with open(file_path, "r") as file:
            try:
                data = json.load(file)
                
                # Verify checksum if available
                if os.path.exists(checksum_path):
                    with open(checksum_path, "r") as checksum_file:
                        stored_checksum = checksum_file.read().strip()
                        
                        # Calculate current checksum
                        current_checksum = calculate_file_checksum(file_path)
                        
                        if stored_checksum != current_checksum:
                            logger.error("File checksum validation failed - possible tampering")
                            # In production, you might want to trigger an alert here
                
                return data
            except json.JSONDecodeError as err:
                logger.error(f"Error parsing JSON: {err}")
                return []
    except Exception as e:
        logger.error(f"Error reading data file: {str(e)}")
        return []

def write_data(new_entry: dict) -> bool:
    """
    Appends a new entry with a timestamp to the JSON file.
    Includes file integrity protection.
    """
    try:
        # Ensure directory exists
        file_path = settings.FILE_PATH
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Read existing data
        data = read_data()
        
        # Add timestamp and transaction ID for traceability
        new_entry["dateSaved"] = datetime.utcnow().isoformat()
        new_entry["backupId"] = f"backup_{datetime.utcnow().timestamp()}"
        
        # Append new entry
        data.append(new_entry)
        
        # Write data
        with open(file_path, "w") as file:
            json.dump(data, file, indent=2)
            
        # Update checksum
        checksum = calculate_file_checksum(file_path)
        with open(f"{file_path}.checksum", "w") as checksum_file:
            checksum_file.write(checksum)
            
        logger.info(f"Successfully wrote data backup with ID {new_entry['backupId']}")
        return True
    except Exception as e:
        logger.error(f"Error writing data: {str(e)}")
        return False

def calculate_file_checksum(file_path: str) -> str:
    """Calculate SHA-256 checksum of a file"""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256.update(byte_block)
    return sha256.hexdigest()
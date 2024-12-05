import os
import json
import logging

class UserProfileManager:
    """
    Manages persistent user profile information across the AI trading system
    """
    _PROFILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'user_profile.json')
    
    @classmethod
    def save_user_name(cls, user_name):
        """
        Save the user's name to a persistent JSON file
        
        Args:
            user_name (str): Name of the user
        """
        try:
            profile = {
                "user_name": user_name,
                "last_interaction": str(datetime.now())
            }
            
            with open(cls._PROFILE_PATH, 'w') as f:
                json.dump(profile, f, indent=4)
            
            logging.info(f"User profile updated: {user_name}")
        except Exception as e:
            logging.error(f"Error saving user profile: {e}")
    
    @classmethod
    def get_user_name(cls):
        """
        Retrieve the user's name from the persistent JSON file
        
        Returns:
            str: User's name, or 'Trader' if not found
        """
        try:
            if not os.path.exists(cls._PROFILE_PATH):
                return "Trader"
            
            with open(cls._PROFILE_PATH, 'r') as f:
                profile = json.load(f)
            
            return profile.get("user_name", "Trader")
        except Exception as e:
            logging.error(f"Error reading user profile: {e}")
            return "Trader"
    
    @classmethod
    def update_last_interaction(cls):
        """
        Update the timestamp of the last user interaction
        """
        try:
            profile = cls.get_profile()
            profile["last_interaction"] = str(datetime.now())
            
            with open(cls._PROFILE_PATH, 'w') as f:
                json.dump(profile, f, indent=4)
        except Exception as e:
            logging.error(f"Error updating last interaction: {e}")
    
    @classmethod
    def get_profile(cls):
        """
        Retrieve the entire user profile
        
        Returns:
            dict: User profile information
        """
        try:
            if not os.path.exists(cls._PROFILE_PATH):
                return {"user_name": "Trader", "last_interaction": str(datetime.now())}
            
            with open(cls._PROFILE_PATH, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error reading user profile: {e}")
            return {"user_name": "Trader", "last_interaction": str(datetime.now())}

# Ensure datetime is imported
from datetime import datetime

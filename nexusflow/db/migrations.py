from alembic.config import Config
from alembic import command
import os
import sys

def run_migrations():
    """Run database migrations"""
    # Get the directory of this file
    dir_path = os.path.dirname(os.path.realpath(__file__))
    
    # Create an Alembic configuration
    alembic_cfg = Config(os.path.join(dir_path, "alembic.ini"))
    
    # Set the path to the migration scripts
    alembic_cfg.set_main_option("script_location", os.path.join(dir_path, "alembic"))
    
    # Run the migration
    command.upgrade(alembic_cfg, "head")

if __name__ == "__main__":
    run_migrations()

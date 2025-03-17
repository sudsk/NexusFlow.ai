#!/usr/bin/env python
"""
Database initialization script for NexusFlow

This script initializes the database tables and runs migrations.
It can be run directly to create or update the database schema.

Usage:
    python -m initialize_db [--drop-all]

Options:
    --drop-all  Drop all existing tables before creating new ones (caution!)
"""

import os
import sys
import argparse
import logging
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from alembic.config import Config
from alembic import command

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import database components
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from nexusflow.db.models import Base
from nexusflow.db.session import engine


def init_db(drop_all=False):
    """
    Initialize database tables
    
    Args:
        drop_all (bool): Whether to drop all tables before creating new ones
    """
    try:
        if drop_all:
            logger.warning("Dropping all tables...")
            Base.metadata.drop_all(bind=engine)
            logger.info("All tables dropped")

        logger.info("Creating tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Tables created successfully")
        
        return True
    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False


def run_migrations():
    """Run database migrations using Alembic"""
    try:
        logger.info("Running migrations...")
        # Get the directory of this file
        dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        migrations_path = os.path.join(dir_path, 'nexusflow', 'db', 'alembic')
        
        # Create an Alembic configuration
        alembic_cfg = Config()
        alembic_cfg.set_main_option('script_location', migrations_path)
        
        # Set the database URL
        if 'DB_HOST' in os.environ:
            db_host = os.environ.get('DB_HOST', 'localhost')
            db_port = os.environ.get('DB_PORT', '5432')
            db_name = os.environ.get('DB_NAME', 'nexusflow')
            db_user = os.environ.get('DB_USER', 'nexusflow-user')
            db_password = os.environ.get('DB_PASSWORD', '')
            
            db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            alembic_cfg.set_main_option('sqlalchemy.url', db_url)
        
        # Run the migration
        command.upgrade(alembic_cfg, "head")
        logger.info("Migrations completed successfully")
        
        return True
    except Exception as e:
        logger.error(f"Error running migrations: {e}")
        return False


def setup_alembic_if_needed():
    """Set up Alembic directory if it doesn't exist"""
    dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    alembic_dir = os.path.join(dir_path, 'nexusflow', 'db', 'alembic')
    
    if not os.path.exists(alembic_dir):
        try:
            logger.info("Setting up Alembic directory...")
            os.makedirs(alembic_dir, exist_ok=True)
            
            # Create alembic.ini file
            alembic_ini_path = os.path.join(dir_path, 'nexusflow', 'db', 'alembic.ini')
            with open(alembic_ini_path, 'w') as f:
                f.write("""[alembic]
script_location = alembic
prepend_sys_path = .
revision_environment = false
sourceless = false
version_locations = alembic/versions

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = INFO
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
""")
            
            # Initialize Alembic
            alembic_cfg = Config(alembic_ini_path)
            alembic_cfg.set_main_option('script_location', alembic_dir)
            command.init(alembic_cfg, alembic_dir)
            
            logger.info("Alembic setup completed")
        except Exception as e:
            logger.error(f"Error setting up Alembic: {e}")
            return False
    
    return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Initialize NexusFlow database')
    parser.add_argument('--drop-all', action='store_true', help='Drop all tables before creating them')
    args = parser.parse_args()
    
    # Set up Alembic if needed
    if not setup_alembic_if_needed():
        sys.exit(1)
    
    # Initialize database tables
    if not init_db(args.drop_all):
        sys.exit(1)
    
    # Run migrations
    if not run_migrations():
        sys.exit(1)
    
    logger.info("Database initialization completed successfully")


if __name__ == "__main__":
    main()

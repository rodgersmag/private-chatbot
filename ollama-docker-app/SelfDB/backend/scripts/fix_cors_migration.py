#!/usr/bin/env python3
"""
Script to fix CORS origins migration state issue.
This script will mark the add_cors_origins_table migration as completed 
if the table already exists in the database.
"""

import asyncio
import logging
import os
import sys
from sqlalchemy import text

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.session import AsyncSessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def fix_cors_migration():
    """
    Check if cors_origins table exists and mark migration as completed if it does.
    """
    async with AsyncSessionLocal() as db:
        try:
            # Check if cors_origins table exists using SQL query
            result = await db.execute(
                text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'cors_origins')")
            )
            table_exists = result.scalar()
            
            if table_exists:
                logger.info("cors_origins table already exists in database")
                
                # Check if migration is already marked as completed
                result = await db.execute(
                    text("SELECT version_num FROM alembic_version WHERE version_num = 'add_cors_origins_table'")
                )
                migration_exists = result.fetchone()
                
                if not migration_exists:
                    logger.info("Marking add_cors_origins_table migration as completed...")
                    
                    # Get current migration state
                    result = await db.execute(text("SELECT version_num FROM alembic_version"))
                    current_version = result.scalar()
                    
                    if current_version == 'remove_function_trigger_fields':
                        # Update to the cors migration
                        await db.execute(
                            text("UPDATE alembic_version SET version_num = 'add_cors_origins_table'")
                        )
                        await db.commit()
                        logger.info("Successfully marked add_cors_origins_table migration as completed")
                    else:
                        logger.warning(f"Current migration version is {current_version}, not updating")
                else:
                    logger.info("Migration add_cors_origins_table is already marked as completed")
            else:
                logger.info("cors_origins table does not exist, migration should run normally")
                
        except Exception as e:
            logger.error(f"Error checking/fixing migration state: {e}")
            await db.rollback()
            raise


async def main():
    """Main function"""
    try:
        await fix_cors_migration()
        logger.info("Migration fix completed successfully")
    except Exception as e:
        logger.error(f"Migration fix failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

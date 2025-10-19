import logging
from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.settings import getSettings
from app.models.base import ServiceBase

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, databaseUrl: str, echo: bool = False):
        # Service specific database configuration
        engineKwargs: Dict[str, Any] = {
            "echo": echo,
            "future": True,
        }

        if "sqlite" in databaseUrl:
            """SQLite specific configuration"""
            engineKwargs["connect_args"] = {
                "timeout": 60,
                "check_same_thread": False,
            }
            logger.info(
                "Configuring SQLite database",
                extra={
                    "database_type": "sqlite",
                    "timeout": 60,
                },
            )

        else:
            """PostgreSQL/MySQL specific configuration"""
            engineKwargs.update(
                {
                    "pool_size": 20,
                    "max_overflow": 0,
                    "pool_pre_ping": True,
                    "pool_recycle": 3600,
                    "pool_reset_on_return": "commit",
                    "connect_args": {
                        "connect_timeout": 10,
                        "prepared_statement_cache_size": 100,
                    },
                }
            )
            logger.info(
                "Configured PostgreSQL/MySQL database",
                extra={
                    "database_type": "postgresql/mysql",
                    "pool_size": 20,
                    "max_overflow": 0,
                    "pool_pre_ping": True,
                    "pool_recycle": 3600,
                    "pool_reset_on_return": "commit",
                    "connect_timeout": 10,
                    "prepared_statement_cache_size": 100,
                },
            )

        self.asyncEngine = create_async_engine(databaseUrl, **engineKwargs)
        self.asyncSessionMaker = async_sessionmaker(
            bind=self.asyncEngine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

        logger.info(
            "Service database manager initialized",
            extra={
                "operation": "initialize_database_manager",
                "event_type": "database_initialization",
            },
        )

    async def createTables(self) -> None:
        """create all service database tables"""
        try:
            async with self.asyncEngine.begin() as conn:
                await conn.run_sync(
                    ServiceBase.metadata.create_all,
                    checkfirst=True,
                )
            logger.info(
                "Database tables created successfully",
                extra={
                    "operation": "create_tables",
                    "event_type": "database_table_creation",
                },
            )
        except Exception as e:
            logger.warning(
                "Failed to create database tables",
                exc_info=True,
                extra={
                    "operation": "create_tables",
                    "event_type": "database_table_creation_failure",
                    "error_type": type(e).__name__,
                },
            )

    async def close(self) -> None:
        """Properly close the database engine and connections"""
        await self.asyncEngine.dispose()
        logger.info(
            "Database engine disposed and connections closed",
            extra={
                "operation": "close_database",
                "event_type": "database_shutdown",
            },
        )


# Initialize a global database manager instance
if not getSettings.DATABASE_URL:
    errMsg = "DATABASE_URL is not set in settings."
    logger.error(
        errMsg,
        extra={
            "operation": "initialize_database_manager",
            "database_config": False,
            "event_type": "database_initialization_failure",
        },
    )
    raise ValueError(errMsg)

databaseManager = DatabaseManager(
    databaseUrl=getSettings.DATABASE_URL, echo=getSettings.DEBUG
)
logger.info(
    "Service database manager instance created",
    extra={
        "operation": "initialize_database_manager",
        "database_config": True,
        "event_type": "database_initialization_success",
    },
)

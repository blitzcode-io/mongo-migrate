from argparse import Namespace
from configparser import ConfigParser
from dataclasses import dataclass
import enum
from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Optional, Self

from mongo_migrate.env import EnvSettings
from mongo_migrate.exceptions import ConfigException
from mongo_migrate.utils import values_are_complete

@dataclass
class Config:
    """
    Database configuration
    """
    host: str
    port: int
    database: str
    username: str | None = None
    password: str | None = None

class BaseConfig(BaseModel):
    """
    Base parent class for configurations
    """
    model_config = ConfigDict(extra="ignore")

    @property
    def names(self) -> list[str]:
        """
        List of field names.
        """
        ret = list(self.model_dump().keys())
        return ret

    @property
    def is_complete(self) -> bool:
        """
        Check if configuration is complete.

        Complete means all fields are not null.
        """
        field_values = self.model_dump().values()
        ret = values_are_complete(field_values)
        return ret

    def is_complementary(self, other: Self) -> bool:
        """
        Check if given configuration is complementary.

        Complementary means that each field is not non-null in both.
        (both null; or either one or the other null)
        """
        other_model = other.model_dump()
        for field_name, field_value in self.model_dump().items():
            other_value = other_model[field_name]
            field_is_not_complementary = field_value is not None and other_value is not None
            if field_is_not_complementary:
                return False

        return True    

    def __add__(self, other):
        """
        Combine two configurations.

        Null fields take value of other, non-null stay as is.
        """
        other_model = other.model_dump()
        args = {
            field_name: field_value or other_model[field_name]
            for field_name, field_value in self.model_dump().items()
        }
        ret = self.__class__(**args)
        return ret


class DBConfig(BaseConfig):
    """
    Settings for database configuration
    """
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

    @property
    def is_complete(self) -> bool:
        """
        Check if database configuration is complete.

        Complete means all fields are provided with exception of username and password.
        Those can be null in case database does not require authentication.
        """
        field_values = self.model_dump(exclude={"username": True, "password": True})
        ret = values_are_complete(field_values)
        return ret



class MigrationConfig(BaseConfig):
    """
    Migrations configuration.
    """
    migrations: Optional[str] = Field(None, description="Migrations folder name")


class ConfigType(str, enum.Enum):
    """
    Configuration type.

    Value corresponds to section name in .ini file.
    """
    database = "database"
    migrations = "migrations"


class ConfigClass(enum.Enum):
    database = DBConfig
    migrations = MigrationConfig

    @classmethod
    def from_config_type(cls, config_type: ConfigType):
        return cls[config_type.name]


class ConfigBuilder:
    """
    Configuration builder.
    """
    def __init__(self, config_file: str):
        self._config_file = config_file

        self._ini_parser = ConfigParser()
        self._ini_parser.read(self._config_file)

    def build(self, config_type: ConfigType, args: Namespace | None) -> BaseConfig:
        """
        Build complete configuration of given type.
         
        Combine settings based on:
        - argparse arguments
        - .ini configuration
        - .env

        Each argument must be complementary i.e. either in one source or another (no duplications)
        """
        ini_config = self._build_ini_config(config_type)
        args_config = self._build_args_config(config_type, args)
        env_config = self._build_env_config(config_type)

        for config in [args_config, env_config]:
            if not config.is_complementary(ini_config):
                raise ConfigException(f"Provide {', '.join(ini_config.names)} either in .ini, or .env, or command line arguments")

        final_config = args_config + ini_config + env_config
        if not final_config.is_complete:
            raise ConfigException(f"Provide {', '.join(ini_config.names)} either in .ini, or .env, or command line arguments")

        return final_config

    def _build_ini_config(self, config_type: ConfigType) -> BaseConfig:
        """
        Build configuration of given type based on .ini parser values
        """
        init_args = self._ini_parser[config_type.value] if config_type.value in self._ini_parser.sections() else {}
        return self._build_config(config_type, init_args)
    
    def _build_args_config(self, config_type: ConfigType, args: Namespace | None) -> BaseConfig:
        """
        Build configuration of given type based on argparse arguments
        """
        init_args = {} if args is None else vars(args)
        return self._build_config(config_type, init_args)

    def _build_env_config(self, config_type: ConfigType) -> BaseConfig:
        """
        Build configuration of given type based on .env
        """
        env_settings = EnvSettings()
        init_args = env_settings.model_dump(by_alias=False)
        return self._build_config(config_type, init_args)

    def _build_config(self, config_type: ConfigType, init_args: dict[str, Any]) -> BaseConfig:
        """
        Build configuration of given type with class init arguments.
        """
        config_class = ConfigClass.from_config_type(config_type).value
        ret = config_class(**init_args)
        return ret

class ConfigManager:
    """
    Manager for DB and migration configurations.

    Combine settings based on:
        - argparse arguments
        - .ini configuration
        - .env

    and get desired parameters.
    """
    def __init__(self, config_file: str = "mongomigrate.ini"):
        self._config_file = config_file

        self._config_builder = ConfigBuilder(self._config_file)

    def get_config(self, args: Namespace | None) -> Config:
        """
        Build database config.
        """
        ret = self._config_builder.build(ConfigType.database, args)
        return ret

    def get_migrations(self, args: Namespace | None) -> str:
        """
        Get migrations folder name.
        """
        migration_config = self._config_builder.build(ConfigType.migrations, args)
        return migration_config.migrations
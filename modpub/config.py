"""Configuration management for modpub.

Loads configuration from multiple sources with the following precedence (highest to lowest):
1. Environment variables (THINGIVERSE_TOKEN, etc.)
2. .modpub.conf in current directory
3. ~/.modpub.conf in home directory
4. Default values

Config files use INI format with sections for each plugin.
"""

import os
import configparser
from pathlib import Path
from typing import Optional, Dict, Any


class Config:
    """Manages configuration from multiple sources."""

    def __init__(self):
        self._config = configparser.ConfigParser()
        self._env_vars = {}
        self._load_configs()

    def _load_configs(self):
        """Load configuration files in order of precedence."""
        config_files = []

        # Home directory config
        home_config = Path.home() / ".modpub.conf"
        if home_config.exists():
            config_files.append(home_config)

        # Current directory config
        local_config = Path.cwd() / ".modpub.conf"
        if local_config.exists():
            config_files.append(local_config)

        # Read config files (later files override earlier ones)
        for config_file in config_files:
            self._config.read(config_file)

        # Cache environment variables
        self._env_vars = {
            'thingiverse': {
                'token': os.environ.get('THINGIVERSE_TOKEN'),
            }
        }

    def get(self, section: str, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a configuration value with proper precedence.

        Args:
            section: Config section (e.g., 'thingiverse')
            key: Config key (e.g., 'token')
            default: Default value if not found

        Returns:
            The configuration value or default
        """
        # 1. Check environment variables
        if section in self._env_vars and key in self._env_vars[section]:
            env_val = self._env_vars[section][key]
            if env_val is not None:
                return env_val

        # 2. Check config files
        if self._config.has_section(section) and self._config.has_option(section, key):
            return self._config.get(section, key)

        # 3. Return default
        return default

    def get_thingiverse_token(self) -> Optional[str]:
        """Get the Thingiverse API token from config sources."""
        return self.get('thingiverse', 'token')

    def reload(self):
        """Reload configuration from all sources."""
        self._config.clear()
        self._load_configs()


# Global config instance
_config = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def create_sample_config(path: Optional[Path] = None) -> str:
    """Create a sample configuration file.

    Args:
        path: Path to write the config file (optional)

    Returns:
        The sample configuration content
    """
    sample = """# modpub configuration file
#
# Configuration can be set in:
# 1. Environment variables (highest priority)
# 2. .modpub.conf in current directory
# 3. ~/.modpub.conf in home directory (lowest priority)

[thingiverse]
# Thingiverse API token (get from https://www.thingiverse.com/apps)
# Can also be set via THINGIVERSE_TOKEN environment variable
# token = your_token_here

[localdir]
# Default author name for local directory exports
# author_name = Your Name
# author_url = https://example.com

[defaults]
# Default license for new designs
# license = CC-BY-4.0
"""

    if path:
        path.write_text(sample)

    return sample
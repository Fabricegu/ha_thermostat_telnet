"""Initialisation du package de l'intégration"""
import logging
import asyncio

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_TIMEOUT

from .const import DOMAIN, PLATFORMS, DEFAULT_TIMEOUT

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Initialisation de l'intégration avec configuration.yaml"""
    if DOMAIN not in config:
        return True  # Rien à faire si le domaine n'est pas dans le fichier de configuration

    domain_config = config[DOMAIN]

    # Charger la configuration des entités à partir de configuration.yaml
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]['config'] = domain_config

    # Configuration des plateformes
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(domain_config, PLATFORMS)
    )

    return True

'''
async def async_setup(hass: HomeAssistant, config: dict):
    """Initialisation de l'intégration à partir de configuration.yaml"""
    _LOGGER.info("Initializing %s integration from configuration.yaml", DOMAIN)

    if DOMAIN not in config:
        return True

    # Récupérer la configuration à partir de configuration.yaml
    domain_config = config[DOMAIN]

    # Stocker la configuration dans hass.data pour qu'elle soit accessible par d'autres parties du composant
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]['config'] = domain_config
    hass.data[DOMAIN]['telnet_lock'] = asyncio.Lock()

    # Charger les plateformes spécifiées
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(ConfigEntry(DOMAIN, DOMAIN, domain_config, 'yaml'), PLATFORMS)
    )
'''
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Configure l'intégration via l'interface utilisateur."""
    _LOGGER.info("Setting up entry for %s", DOMAIN)

    # Stocker le verrou et d'autres données nécessaires dans hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]['telnet_lock'] = asyncio.Lock()

    # Transférer l'entrée aux plateformes spécifiées
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Décharge l'entrée de configuration."""
    _LOGGER.info("Unloading entry for %s", DOMAIN)

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data.pop(DOMAIN, None)

    return unload_ok

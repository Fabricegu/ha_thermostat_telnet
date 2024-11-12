"""Initialisation du package de l'intégration"""
import logging
import asyncio

from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_HOST, CONF_TIMEOUT

from .const import DOMAIN, PLATFORMS, DEFAULT_TIMEOUT

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Configure le composant personnalisé via configuration.yaml."""
    _LOGGER.info("Chargement de la configuration pour %s", DOMAIN)
    domain_config = config.get(DOMAIN)
    if not domain_config:
        return True

    host = domain_config.get(CONF_HOST)
    timeout = domain_config.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)

    if not host:
        _LOGGER.error("Le paramètre 'host' est manquant dans la configuration.")
        return False

    _LOGGER.info(
        "Initialisation de l'intégration %s avec les plateformes : %s",
        DOMAIN,
        PLATFORMS,
    )

    # Charger les plateformes spécifiées
    for platform in PLATFORMS:
        _LOGGER.info("Chargement de la plateforme %s", platform)
        hass.async_create_task(
            hass.helpers.discovery.async_load_platform(platform, DOMAIN, {}, config)
        )

    return True

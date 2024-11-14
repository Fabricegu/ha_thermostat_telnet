import logging
import asyncio
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType

from .shared import telnet_lock

_LOGGER = logging.getLogger(__name__)

TELNET_PORT = 23
DEFAULT_TIMEOUT = 5

# Déclaration du verrou global (assurez-vous qu'il est le même que celui utilisé dans sensor.py)
#telnet_lock = asyncio.Lock()

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info=None,
):
    """Configurer la plate-forme du commutateur de commande de chauffage."""
    host = config.get("host")
    timeout = config.get("timeout", DEFAULT_TIMEOUT)

    if not host:
        _LOGGER.error("L'adresse IP du module esp-link est requise.")
        return

    # Ajout des entités de commutateurs pour activer et désactiver le chauffage
    async_add_entities([
        HeatingControlSwitch(host, timeout, "Activer Chauffage", "$CMDTHE1"),
        HeatingControlSwitch(host, timeout, "Désactiver Chauffage", "$CMDTHE0")
    ])

class HeatingControlSwitch(SwitchEntity):
    """Entité de commutateur pour activer/désactiver le chauffage."""

    def __init__(self, host: str, timeout: int, name: str, command: str):
        self._host = host
        self._timeout = timeout
        self._attr_name = name
        self._command = command
        self._is_on = False  # État initial du commutateur

    async def async_turn_on(self, **kwargs):
        """Allumer le commutateur."""
        if await self.send_command(self._command):
            self._is_on = True
            await self.async_update_ha_state()
            _LOGGER.info("Commande %s envoyée avec succès.", self._attr_name)
        else:
            _LOGGER.error("Échec de l'envoi de la commande %s.", self._attr_name)

    async def async_turn_off(self, **kwargs):
        """Éteindre le commutateur."""
        if await self.send_command(self._command):
            self._is_on = False
            await self.async_update_ha_state()
            _LOGGER.info("Commande %s envoyée avec succès.", self._attr_name)
        else:
            _LOGGER.error("Échec de l'envoi de la commande %s.", self._attr_name)

    async def send_command(self, command: str) -> bool:
        """Envoie une commande Telnet et vérifie le retour."""
        async with telnet_lock:  # Utilise le verrou pour synchroniser l'accès
            try:
                reader, writer = await asyncio.open_connection(self._host, TELNET_PORT)
                writer.write(command.encode('utf-8') + b"\n")
                await writer.drain()

                try:
                    response = await asyncio.wait_for(reader.read(100), timeout=self._timeout)
                    response_str = response.decode('utf-8').strip()
                    _LOGGER.debug("Réponse Telnet : %s", response_str)

                    if response_str == "#10@":
                        return True  # Commande valide
                    else:
                        _LOGGER.error("Erreur reçue : %s", response_str)
                        return False

                except asyncio.TimeoutError:
                    _LOGGER.error("Délai d'attente dépassé lors de l'envoi de la commande Telnet.")
                    return False

                finally:
                    writer.close()
                    await writer.wait_closed()

            except (ConnectionError, OSError) as e:
                _LOGGER.error("Erreur de connexion lors de l'envoi de la commande : %s", e)
                return False

    @property
    def is_on(self) -> bool:
        """Retourne l'état du commutateur."""
        return self._is_on

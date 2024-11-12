import logging
import asyncio
from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

TELNET_PORT = 23
DEFAULT_TIMEOUT = 5

# Verrou global pour synchroniser l'accès au Telnet
telnet_lock = asyncio.Lock()

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info=None,
):
    """Configurer la plate-forme du bouton de commande de chauffage."""
    host = config.get("host")
    timeout = config.get("timeout", DEFAULT_TIMEOUT)

    if not host:
        _LOGGER.error("L'adresse IP du module esp-link est requise.")
        return

    # Ajout des entités de boutons pour activer et désactiver le chauffage
    async_add_entities([
        HeatingControlButton(host, timeout, "Activer Chauffage"),
        HeatingControlButton(host, timeout, "Désactiver Chauffage")
    ])

class HeatingControlButton(ButtonEntity):
    """Entité de bouton pour activer/désactiver le chauffage."""

    def __init__(self, host: str, timeout: int, name: str):
        """Initialise l'entité du bouton."""
        self._host = host
        self._timeout = timeout
        self._attr_name = name
        self._command = "$CMDTHE1" if "Activer" in name else "$CMDTHE0"

    async def async_press(self) -> None:
        """Action à exécuter lors de l'appui sur le bouton."""
        if await self.send_command(self._command):
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

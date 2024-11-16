import logging
import asyncio
#import telnetlib3
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import TEMP_CELSIUS

_LOGGER = logging.getLogger(__name__)

DOMAIN = "custom_telnet_sensor"

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Configure les capteurs et ajoute les entités."""
    ip_address = config.get("ip_address")
    port = config.get("port")
    name = config.get("name", "Telnet Sensor")
    timeout = config.get("timeout", 10)  # Timeout par défaut de 10 secondes

    if not ip_address or not port:
        _LOGGER.error("L'adresse IP et le port doivent être spécifiés")
        return
    _LOGGER.warning("initilisation des entités")
    # Initialisation explicite des entités
    sensor_1 = TelnetTemperatureSensor(ip_address, port, f"{name} Température 1", "$RDTEMP0", timeout)
    sensor_2 = TelnetTemperatureSensor(ip_address, port, f"{name} Température 2", "$RDTEMP1", timeout)
    sensor_3 = TelnetTemperatureSensor(ip_address, port, f"{name} Température 3", "$RDTEMP2", timeout)

    # Ajout explicite des entités
    add_entities([sensor_1, sensor_2, sensor_3])

class TelnetTemperatureSensor(SensorEntity):
    """Représentation d'un capteur de température récupéré via Telnet."""

    def __init__(self, ip_address, port, name, command, timeout):
        self._ip_address = ip_address
        self._port = port
        self._name = name
        self._command = command  # Commande Telnet spécifique pour obtenir la température
        self._state = None
        self._timeout = timeout  # Timeout ajustable
        self._lock = asyncio.Lock()
        self._unique_id = f"{ip_address}_{port}_{command}"

    @property
    def unique_id(self):
        """Retourne l'identifiant unique de l'entité."""
        return self._unique_id

    @property
    def name(self):
        """Retourne le nom de l'entité."""
        return self._name

    @property
    def state(self):
        """Retourne l'état de la température."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Retourne l'unité de mesure."""
        return TEMP_CELSIUS

    async def async_update(self):
        """Récupère la valeur de température via Telnet avec gestion de verrou et timeout."""
        _LOGGER.warning("appel de async_update")
        async with self._lock:
            try:
                _LOGGER.debug("Tentative de connexion Telnet à %s:%s pour %s", self._ip_address, self._port, self._command)
                async with telnetlib3.open_connection(self._ip_address, self._port) as conn:
                    await asyncio.wait_for(conn.write(f'{self._command}\n'), timeout=self._timeout)
                    response = await asyncio.wait_for(conn.read_until("\n"), timeout=self._timeout)
                    response = response.strip()

                    # Vérification de la réponse
                    if response.startswith("#"):
                        _LOGGER.error("Erreur détectée lors de la récupération de la température avec %s", self._command)
                        self._state = "error"
                    else:
                        try:
                            self._state = float(response)
                        except ValueError:
                            _LOGGER.error("Impossible de convertir la réponse en float : %s", response)
                            self._state = "error"

                    _LOGGER.debug("Donnée reçue pour %s : %s", self._name, response)
            except asyncio.TimeoutError:
                _LOGGER.error("Timeout lors de la récupération de la température pour %s", self._command)
                self._state = "timeout"
            except Exception as e:
                _LOGGER.error("Erreur lors de la connexion Telnet : %s", e)
                self._state = "unavailable"

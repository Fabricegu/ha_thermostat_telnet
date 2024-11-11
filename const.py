""" Les constantes pour l'intégration  """

from homeassistant.const import Platform

DOMAIN = "thermostat_telnet"
PLATFORMS: list[Platform] = [Platform.SENSOR]

# Ajoutez cette ligne pour définir DEFAULT_TIMEOUT
DEFAULT_TIMEOUT = 5  # ou une autre valeur par défaut que vous souhaitez utiliser

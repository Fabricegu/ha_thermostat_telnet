from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

DOMAIN = "thermostat_telnet"

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Configurer l'entrée pour l'intégration."""
    # Enregistrez le service pour activer/désactiver le chauffage
    hass.data.setdefault(DOMAIN, {})
    return True

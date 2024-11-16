"""Initialisation du composant personnalisé Telnet Sensor pour Home Assistant."""

DOMAIN = "custom_telnet_sensor"

def setup(hass, config):
    """Configure le domaine du composant."""
    # Si vous souhaitez exécuter du code au démarrage de Home Assistant, vous pouvez le faire ici.
    hass.states.set(f"{DOMAIN}.loaded", "true")
    return True

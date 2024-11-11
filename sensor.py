""" Implements the VersatileThermostat sensors component """
import logging
import asyncio

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.typing import ConfigType
from homeassistant.const import UnitOfTemperature
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)

_LOGGER = logging.getLogger(__name__)

TELNET_PORT = 23
DEFAULT_TIMEOUT = 5

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info=None,
):
    host = config.get("host")
    timeout = config.get("timeout", DEFAULT_TIMEOUT)

    if not host:
        _LOGGER.error("L'adresse IP du module esp-link est requise.")
        return

    sensors = config.get("sensors", [])
    temperature_entities = [
        ThermostatTelnetEntity(hass, host, timeout, sensor["command"], sensor["name"])
        for sensor in sensors
    ]

    orchestrator = TemperatureOrchestrator(hass, temperature_entities)
    async_add_entities(temperature_entities + [orchestrator], True)

class ThermostatTelnetEntity(SensorEntity):
    def __init__(self, hass: HomeAssistant, host: str, timeout: int, command: str, name: str) -> None:
        self._host = host
        self._timeout = timeout
        self._command = command
        self._attr_name = name
        self._attr_unique_id = f"{name.replace(' ', '_').lower()}"
        self._attr_native_value = None
        self._attr_has_entity_name = True

    async def fetch_temperature(self):
        try:
            reader, writer = await asyncio.open_connection(self._host, TELNET_PORT)
            writer.write(self._command.encode('utf-8') + b"\n")
            await writer.drain()

            try:
                response = await asyncio.wait_for(reader.read(100), timeout=self._timeout)
                _LOGGER.warning("valeur retournée %s", response)
            except asyncio.TimeoutError:
                _LOGGER.warning("Délai d'attente dépassé pour le capteur %s", self._attr_name)
                self._attr_native_value = None
                return

            writer.close()
            await writer.wait_closed()

            response_str = response.decode('utf-8').strip()
            _LOGGER.warning("valeur du capteur %s", response_str)
            if response_str.startswith("#"):
                _LOGGER.error("Erreur reçue de l'esp-link pour le capteur %s : %s", self._attr_name, response_str)
                self._attr_native_value = None
            else:
                try:
                    self._attr_native_value = float(response_str)
                    _LOGGER.warning("valeur du capteur transmise = %f", self._attr_native_value)
                except ValueError:
                    _LOGGER.error("Conversion en float échouée pour %s", response_str)
                    self._attr_native_value = None
                        # Notifier Home Assistant de la mise à jour    
            await self.async_update_ha_state(True)

        except (ConnectionError, ValueError) as e:
            _LOGGER.error("Erreur lors de la connexion ou de la conversion pour le capteur %s : %s", self._attr_name, e)
            self._attr_native_value = None
            await self.async_update_ha_state(True)

    @property
    def icon(self) -> str | None:
        return "mdi:thermometer"

    @property
    def device_class(self) -> SensorDeviceClass | None:
        return SensorDeviceClass.TEMPERATURE

    @property
    def state_class(self) -> SensorStateClass | None:
        return SensorStateClass.MEASUREMENT

    @property
    def native_unit_of_measurement(self) -> str | None:
        return UnitOfTemperature.CELSIUS

    @property
    def should_poll(self) -> bool:
        return False

class TemperatureOrchestrator(SensorEntity):
    def __init__(self, hass: HomeAssistant, entities: list[ThermostatTelnetEntity]) -> None:
        self._entities = entities
        self._attr_name = "température chaudière"
        self._attr_unique_id = "temperature_orchestrator"
        _LOGGER.warning("instanciation orchestrator")

    async def async_update(self):
        for entity in self._entities:
            _LOGGER.warning("updating orchestrator")
            await entity.fetch_temperature()
            await asyncio.sleep(1)

    @property
    def should_poll(self) -> bool:
        return True

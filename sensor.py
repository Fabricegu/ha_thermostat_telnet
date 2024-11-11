class TutoHacsHeatingControl:
    """Classe pour contrôler le chauffage via Telnet."""

    def __init__(self, host: str, timeout: int):
        """Initialisation avec l'hôte et le délai d'attente."""
        self._host = host
        self._timeout = timeout

    async def send_command(self, command: str) -> bool:
        """Envoie une commande Telnet et vérifie le retour."""
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
                    return False  # Commande invalide

            except asyncio.TimeoutError:
                _LOGGER.error("Délai d'attente dépassé lors de l'envoi de la commande Telnet.")
                return False

            finally:
                writer.close()
                await writer.wait_closed()

        except ConnectionError as e:
            _LOGGER.error("Erreur de connexion lors de l'envoi de la commande : %s", e)
            return False

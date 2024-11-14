# shared.py
import asyncio

# Verrou global pour synchroniser l'accès au Telnet
telnet_lock = asyncio.Lock()

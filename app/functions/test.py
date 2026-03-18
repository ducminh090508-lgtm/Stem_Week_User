import asyncio
import ssl
import websockets

async def test():
    uri = "wss://34.143.182.90:8080"
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async with websockets.connect(uri, ssl=ssl_context, open_timeout=15) as ws:
        print("connected")
        await ws.send("VERIFY_PIN 624381")
        print(await ws.recv())

asyncio.run(test())
import os
import sys
import asyncio
import subprocess
import websockets
import hashlib
import pickle
import datetime

PORT = 8080

if len(sys.argv) > 1:
    PORT = sys.argv[1]

if __name__ == '__main__':
    subprocess.Popen(["python3", "-m", "startHTTP.py", str(PORT)])


class Server:
    current_noise = None
    current_noise_hash = None
    connected = set()

    def get_port(self):
        return os.getenv('WS_PORT', '5678')

    def get_host(self):
        return os.getenv('WS_HOST', 'localhost')

    def start(self):
        return websockets.serve(self.handler, self.get_host(), self.get_port())

    def save_noise(self):
        fname = f'mouth_sounds/{Server.current_noise_hash}_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.pickle'
        with open(fname, 'wb') as f:
            pickle.dump(Server.current_noise, f)
        return fname

    async def handler(self, websocket, path):
        self.connected.add(websocket)
        recvSound = False
        async for message in websocket:
            if recvSound:
                recvSound = False
                Server.current_noise = list(message)
                filename = self.save_noise()
                await asyncio.wait([websocket.send(f'F:{filename}') for websocket in self.connected])
            elif message[0] == "M":
                hash = hashlib.sha256()
                hash.update(message[1:].encode('utf-8'))
                Server.current_noise_hash = hash.hexdigest()
                try:
                    await asyncio.wait([ws.send(message) for ws in self.connected])
                except:
                    print("oopsie")
            elif message == "S":
                recvSound = True
            else:
                print(message)


async def main():
    ws = Server()
    async with ws.start():
        await asyncio.Future()

if __name__ == '__main__':
    asyncio.run(main())

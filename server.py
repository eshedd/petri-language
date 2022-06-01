import os
import sys
import asyncio
import subprocess
import websockets
import hashlib
import pickle
import datetime
from scipy.io import wavfile
import numpy as np

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
        fname = f'{Server.current_noise_hash}_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}'
        os.mkdir(f"mouth_sounds/{fname}")
        with open(f"mouth_sounds/{fname}/{fname}.wav", 'wb') as f:
            f.write(Server.current_noise)
        with open(f"mouth_sounds/{fname}/{fname}.pickle", 'wb') as f:
            sampRate, data = wavfile.read(f"mouth_sounds/{fname}/{fname}.wav")
            pickle.dump(list(np.delete(data, 1, 1).flatten()), f)
        return f"mouth_sounds/{fname}"

    async def handler(self, websocket, path):
        self.connected.add(websocket)
        recvSound = False
        async for message in websocket:
            if recvSound:
                recvSound = False
                Server.current_noise = message
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

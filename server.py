import os
import asyncio
import websockets

import subprocess

subprocess.Popen(["python3", "-m", "http.server", "8080"])


class Server:
    connected = set()

    def get_port(self):
        return os.getenv('WS_PORT', '5678')

    def get_host(self):
        return os.getenv('WS_HOST', 'localhost')


    def start(self):
        return websockets.serve(self.handler, self.get_host(), self.get_port())

    async def handler(self, websocket, path):
      self.connected.add(websocket)
      async for message in websocket:
        if message:
            try:
                await asyncio.wait([ws.send(message) for ws in self.connected])
            except:
                print("oopsie")

if __name__ == '__main__':
  ws = Server()
  asyncio.get_event_loop().run_until_complete(ws.start())
  asyncio.get_event_loop().run_forever()
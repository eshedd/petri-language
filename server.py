import os
import asyncio
import websockets
import sys

import subprocess

PORT = 8080

if len(sys.argv) > 1:
    PORT = sys.argv[1]

subprocess.Popen(["python3", "-m", "http.server", str(PORT)])


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
      recvSound = False
      doneRecv = False
      testBuff = []
      async for message in websocket:
        if recvSound:
            testBuff.append(list(message))
            recvSound = False
            if(doneRecv):
                print(testBuff)
                testBuff = []
                doneRecv = False
        elif message[0] == "M":
            try:
                await asyncio.wait([ws.send(message) for ws in self.connected])
            except:
                print("oopsie")
        elif message[0] == "S":
            print(message)
            recvSound = True
            [position, length] = message[2:].split("/")
            if(position==length):
                doneRecv = True

if __name__ == '__main__':
  ws = Server()
  asyncio.get_event_loop().run_until_complete(ws.start())
  asyncio.get_event_loop().run_forever()
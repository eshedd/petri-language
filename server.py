import os, sys, asyncio, subprocess
import websockets
import hashlib
import pickle
import datetime

PORT = 8080

if len(sys.argv) > 1:
    PORT = sys.argv[1]

if __name__ == '__main__':
    subprocess.Popen(["python3", "-m", "http.server", str(PORT)])


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
        fname = f'mouth_sounds/{Server.current_noise_hash}-{datetime.datetime.now()}.pickle'
        with open(fname, 'wb') as f:
            pickle.dump(Server.current_noise, f)
        return fname

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
                Server.current_noise = testBuff
                filename = self.save_noise()
                await asyncio.wait([websocket.send(filename) for websocket in self.connected])
                testBuff = []
                doneRecv = False
        elif message[0] == "M":
            hash = hashlib.sha256()
            hash.update(message[1:].encode('utf-8'))
            Server.current_noise_hash = hash.hexdigest()
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
import sys
import pickle
import wave

if len(sys.argv) > 1:
    path = sys.argv[1]
else:
    path = input("path to pickle? ")
with open(path, mode="r+b") as f:
    auData = pickle.load(f)
fname = path.replace(".pickle", ".wav")
with wave.open(fname, "wb") as f:
    f.setparams((1, 4, 48000, 100, "NONE", "NONE"))
    f.writeframesraw(bytes(auData))

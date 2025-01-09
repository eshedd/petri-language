from timeit import timeit
import numpy as np
import soundfile as sf

from pynktrombone.voc import Voc

CHUNK = 512
# samplerate = 48000
samplerate = 8000
duration = 10.0  # seconds


def main():
    vocal = Voc(samplerate)
    output = []
    while len(output)*CHUNK < samplerate * duration:

        vocal.set_tract_parameters(
            trachea=0.5,
            epiglottis=0.5,
            velum=0.5,
            tongue_index=0.5,
            tongue_diameter=0.5,
            lips=0.5
        )
        vocal.set_glottis_parameters(
            enable=True,
            frequency=300
        )

        out = [vocal.compute()]
        while vocal.counter != 0:
            out.append(vocal.compute())
        output.append(out)

    sf.write('test.wav', np.concatenate(output), samplerate)


if __name__ == '__main__':
    t = timeit(main, number=1)
    print(t, 'seconds')

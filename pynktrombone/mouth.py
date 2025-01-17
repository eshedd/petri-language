from timeit import timeit
import numpy as np
import soundfile as sf

from pynktrombone.voc import Voc


CHUNK = 512
# samplerate = 48000
SAMPLE_RATE = 8000


class Mouth:
    """
    A wrapper for the Voc class that generates sound files
    from Pink Trombone parameters.
    """
    def __init__(self, sample_rate=SAMPLE_RATE):
        self.sample_rate = sample_rate
        self.vocal = Voc(self.sample_rate)

    def speak(self, save_path, trachea=0.5, epiglottis=0.5,
              velum=0.5, tongue_index=0.5, tongue_diameter=0.5,
              lips=0.5, glottis_enable=True, glottis_frequency=300,
              duration=1) -> None:
        """
        Generate a sound file from Pink Trombone parameters.
        """
        assert save_path.endswith('.wav'), 'Save path must end with .wav'

        output = []
        while len(output)*CHUNK < self.sample_rate * duration:
            self.vocal.set_tract_parameters(
                trachea=trachea,
                epiglottis=epiglottis,
                velum=velum,
                tongue_index=tongue_index,
                tongue_diameter=tongue_diameter,
                lips=lips
            )
            self.vocal.set_glottis_parameters(
                enable=glottis_enable,
                frequency=glottis_frequency
            )

            out = [self.vocal.compute()]
            while self.vocal.counter != 0:
                out.append(self.vocal.compute())
            output.append(out)

        sf.write(save_path, np.concatenate(output), self.sample_rate)

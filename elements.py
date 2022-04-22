import pyaudio, random, math
import numpy as np

class World:
    '''
    Only the dirtiest, filthiest, down-right nastiest 
    dogs of programmers reference the Agent class from the 
    World class.
    '''
    def __init__(self, dim: tuple):
        self.agents = {}
        self.dim = dim
        self.grid = []
        for n in range(self.dim[0]):
            self.grid.append([])
            for _ in range(self.dim[1]):
                self.grid[n].append('▢')

    def is_legal_pos(self, pos: tuple):

        return len(pos) == 2 and 0 <= pos[0] < self.dim[0] and 0 <= pos[1] < self.dim[1]

    def place_agent(self, agent, pos: tuple):
        if not self.is_legal_pos(pos):
            print(f'illegal position ({pos}) for agent ({agent})')
        self.agents[str(agent)] = pos
        self.grid[pos[0]][pos[1]] = 'X'

    def move_agent(self, agent, action: str):
        '''
        moves an agent, returns reward from agent's movement
        '''
        pos = self.agents[str(agent)]
        new_pos = pos
        if action == 'north':
            new_pos = (new_pos[0] - 1, new_pos[1])
        elif action == 'east':
            new_pos = (new_pos[0], new_pos[1] + 1)
        elif action == 'south':
            new_pos = (new_pos[0] + 1, new_pos[1])
        elif action == 'west':
            new_pos = (new_pos[0], new_pos[1] - 1)

        legal = self.is_legal_pos(new_pos)

        if legal:
            self.agents[str(agent)] = new_pos
            self.grid[pos[0]][pos[1]] = '▢'
            self.grid[new_pos[0]][new_pos[1]] = 'X'
            return 1  # reward for taking valid move

        return -2  # reward for taking invalid move

    def __str__(self):
        s = ''
        for n in range(self.dim[0]):
            for m in range(self.dim[1]):
                s += self.grid[n][m] + ' '
            s += '\n'
        return s


ACTIONS = ['north', 'east', 'south', 'west']
VOLUME = 0.5     # range [0.0, 1.0]
FS = 44100       # sampling rate, Hz, must be integer
F_THRESH_HIGH = 5000
F_THRESH_LOW = 20
DUR_LOW = 0
DUR_HIGH = 10

class Agent:

    def __init__(self, name):
        self.name = name
        self.words = {}
        self.trial = ()  # internal agent knowledge
    
    def plan(self, w: World, decision_func):
        action = random.choice(ACTIONS)
        if action not in self.words.keys():  # action not yet in words dictionary
            self.words[action] = {}
            self.words[action][self.get_new_noise()] = 0  # initialize noise/action score

        noise_choice = decision_func(self.words[action])
        if noise_choice not in self.words[action].keys():  # decision function tried new noise
            self.words[action][noise_choice] = 0

        self.trial = (action, noise_choice)
        return noise_choice
    
    @staticmethod
    def get_new_noise():
        '''
        returns a randomly generated noise tuple within the specified global bounds
        '''
        duration = random.uniform(DUR_LOW, DUR_HIGH)  # in seconds, may be float
        f = random.uniform(F_THRESH_LOW, F_THRESH_HIGH)  # sine frequency, Hz, may be float
        return (duration, f)

    def speak(self, duration, f):
        # generate samples, note conversion to float32 array
        def generate_samples(fs, duration, f):
            return (np.sin(2*np.pi*np.arange(fs*duration)*f/fs)).astype(np.float32)

        print(f'{self} speaking...')

        p = pyaudio.PyAudio()

        samples = generate_samples(FS, duration, f)

        # for paFloat32 sample values must be in range [-1.0, 1.0]
        stream = p.open(format=pyaudio.paFloat32,
                        channels=1,
                        rate=FS,
                        output=True)

        # play. May repeat with different volume values (if done interactively) 
        stream.write(VOLUME*samples)

        stream.stop_stream()
        stream.close()

        p.terminate()
    
    def reward(self, world, action):
        return world.move_agent(self, action)

    def listen(self, world: World, permission: bool):
        action, noise = self.trial
        # if not permission:
            # self.words[action][noise] = 1
        if permission:
            self.words[action][noise] += self.reward(world, action)
            print(f'{self} moved {action}')


    def __str__(self):
        return self.name

    # Decision Functions
    @staticmethod
    def no_greed(noise_dict: dict):
        noise = max(noise_dict, key=noise_dict.get)
        return noise
    
    @staticmethod
    def uniform_greed_prob(noise_dict: dict):
        '''
        new_sound_prob: probability of a new sound
        1 - new_sound_prob: probability of using an existing sound

        (1-new_sound_prob) is 
        '''
        print(noise_dict)
        new_sound_prob = 0.4
        exponential_scores = map(math.exp, noise_dict.values())  # exponent because of negative scores
        total_score = sum(exponential_scores)
        c = (1-new_sound_prob)/total_score
        p = random.random()
        if p > new_sound_prob:
            growing_prob = new_sound_prob
            for noise, score in noise_dict.items():
                print(noise, ':', math.exp(score))
                growing_prob += math.exp(score) * c
                print(f'p:{p} <=? gp:{growing_prob}')
                if p <= growing_prob:
                    return noise
        return Agent.get_new_noise()

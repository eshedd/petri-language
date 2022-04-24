import pyaudio, random, math, sys
import numpy as np

ACTIONS = ['north', 'east', 'south', 'west']
VOLUME = 0.5     # range [0.0, 1.0]
FS = 44100       # sampling rate, Hz, must be integer
F_THRESH_HIGH = 2500
F_THRESH_LOW = 50
DUR_LOW = 0
DUR_HIGH = 7

class World:
    '''
    Only the dirtiest, filthiest, down-right nastiest 
    DOGS of programmers reference the Agent class from the 
    World class.
    '''
    def __init__(self, dim: tuple, rand_walls=False, walliness=0.2):
        self.agents = {}
        self.dim = dim
        self.grid = []
        for n in range(self.dim[0]):
            self.grid.append([])
            for _ in range(self.dim[1]):
                if rand_walls and random.random() <= walliness:
                    self.grid[n].append('■')
                else:
                    self.grid[n].append('▢')
        self.place_goal()

    def place_goal(self):
        n = random.randint(0, self.dim[0] - 1)
        m = random.randint(0, self.dim[1] - 1)
        self.grid[n][m] = '!'

    def is_goal(self, pos: tuple):
        (n, m) = pos
        return self.grid[n][m] == '!'

    def is_legal(self, pos: tuple):
        (n, m) = pos
        return self.is_in_bounds(pos) and self.grid[n][m] != '■'

    def is_in_bounds(self, pos: tuple) -> bool:
        return len(pos) == 2 and 0 <= pos[0] < self.dim[0] and 0 <= pos[1] < self.dim[1]

    def place_agent(self, agent, pos: tuple):
        if not self.is_in_bounds(pos) or self.is_goal(pos):
            print(f'illegal position ({pos}) for agent ({agent})')
            return False
        self.agents[str(agent)] = pos
        self.grid[pos[0]][pos[1]] = 'X'
        return True

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

        if self.is_legal(new_pos):
            print(f'{agent} @ {new_pos}')
            if self.is_goal(new_pos):
                print(f'{agent} reached goal!')
                sys.exit()  # TODO: remove system exit; add proper exit case
            self.agents[str(agent)] = new_pos
            self.grid[pos[0]][pos[1]] = '▢'
            self.grid[new_pos[0]][new_pos[1]] = 'X'
            return 1  # reward for taking valid move
        print(f'{agent} move failed')
        return -2  # reward for taking invalid move

    def __str__(self):
        s = ''
        for n in range(self.dim[0]):
            for m in range(self.dim[1]):
                s += self.grid[n][m] + ' '
            s += '\n'
        return s

class Agent:

    def __init__(self, name, thinking_aloud=False):
        self.name = name
        self.score = 0
        self.thinking_aloud = thinking_aloud

    def __str__(self):
        return self.name


class Searcher(Agent):

    def __init__(self, name, thinking_aloud=False):
        self.words = {}
        self.trial = ()  # current trial memory from plan to listen phase
        Agent.__init__(self, name, thinking_aloud)

    
    def plan(self, w: World, decision_func):
        action = random.choice(ACTIONS)  # TODO: change to plannable actions
        if action not in self.words.keys():  # action not yet in words dictionary
            self.words[action] = {}
            self.words[action][self.get_new_noise()] = 0  # initialize noise/action score

        if self.thinking_aloud:
            print(f'{self}\'s {action} dictionary: {self.words[action]}')

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
            reward = self.reward(world, action)
            self.words[action][noise] += reward
            self.score += reward

    # Decision Functions
    @staticmethod
    def greed(noise_dict: dict):
        noise = max(noise_dict, key=noise_dict.get)
        return noise
    
    @staticmethod
    def uniform_less_greed_prob(noise_dict: dict):
        '''
        new_sound_prob: probability of a new sound
        1 - new_sound_prob: probability of using an existing sound

        (1-new_sound_prob) is 
        '''
        new_sound_prob = 0.4
        exponential_scores = map(math.exp, noise_dict.values())  # exponent because of negative scores
        total_score = sum(exponential_scores)
        c = (1-new_sound_prob)/total_score
        p = random.random()
        if p > new_sound_prob:
            growing_prob = new_sound_prob
            for noise, score in noise_dict.items():
                growing_prob += math.exp(score) * c
                if p <= growing_prob:
                    return noise
        return Searcher.get_new_noise()


class Interpreter(Agent):

    def __init__(self, name, thinking_alound=False):

        Agent.__init__(self, name, thinking_alound)
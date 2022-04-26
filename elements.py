import random, math, sys
import numpy as np
import datetime, random, websockets
import asyncio

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
        '''
        dim: dimensions of world (n x m), n rows, m columns
        rand_walls: spatters world with random walls
        walliness: prob of wall spawning when rand_walls=True
        '''
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
        self.trial = ()  # current trial memory
        self.thinking_aloud = thinking_aloud

    def __str__(self):
        return self.name

class Squealer(Agent):
    def __init__(self, name, thinking_aloud=False):
        self.words = {}
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

    def speak_human(self, duration, f):
        async def send_socket():
            async with websockets.connect("ws://localhost:5678") as websocket:
                print(f'{self} speaking...')
                await websocket.send("pee")
                await websocket.recv()

        loop = asyncio.get_event_loop()
        coroutine = send_socket()
        loop.run_until_complete(coroutine)

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
        ''''
        Squealer listens to permission and updates self.words 
        according to reward
        Takes in world to move self in above reward func
        '''
        action, noise = self.trial
        # if not permission:
            # self.words[action][noise] = 1
        if permission:
            reward = self.reward(world, action)
            self.words[action][noise] += reward
            self.score += reward
            if reward >= 0: return action  # TODO: make better movement-success check
        return None


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
        (1-new_sound_prob) is split into probabilistic intervals
        then random number either falls in the intervals or new sound
        '''
        new_sound_prob = 0.25
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
        return Squealer.get_new_noise()

class Interpreter(Agent):
    '''
    Listen to squealer w/ some handicap
        distort with some noise function
    Guess action from sound
        measure distances between all existing sounds
        if best match within threshold: guess best match
        else: assume new noise
            DEEPER: evaluate whether new noise is worth risk
    If action hits wall: no permit
    If action brings squealer closer to goal: permit
        get agent distance from goal
        if action brings closer: permit
        if action goes further: no permit
    '''

    def __init__(self, name, thinking_alound=False):
        self.guessed_words = {}
        Agent.__init__(self, name, thinking_alound)

    @staticmethod
    def euclidean_distance(tup1: tuple, tup2: tuple):
        vec1 = np.asarray(vec1)
        vec2 = np.asarray(vec2)
        return np.linalg.norm(vec1 - vec2)

    def get_guess(self, new_noise_threshold):
        '''
        Find the best guess for action within the threshold.
        If above threshold: returns False (meaning its an unidentified noise)
        '''
        if not self.guessed_words:
            return False

        # guessed_words has previous entries
        min_k = None
        min_v = float('inf')
        min_dist = float('inf')
        for k, v in self.guessed_words.items():
            dist = self.euclidean_distance(self.trial, v)
            if dist < min_dist:
                min_k, min_v, min_dist = k, v, dist
        if min_dist > new_noise_threshold:
            # didn't make the cut, buddy
            return False
        return min_k  # return the best action

    def listen(self, world: World, duration, f, distortion_func, new_noise_threshold) -> bool:
        duration = distortion_func(duration)
        f = distortion_func(f)
        self.trial = (duration, f)
        if self.thinking_aloud:
            print(f'{self} heard {self.trial}')

        # guess at which action the noise is associated with
        action = self.get_guess(new_noise_threshold)

        if not action:  # doesn't recognize the sound
            return True
        

        # world.move_agent() TODO: differentiate between moving and experimenting
        # might need a distance function added to World

        
       
# # Python3 program for the above approach
# from collections import deque as queue
 
# # Direction vectors
# dRow = [ -1, 0, 1, 0]
# dCol = [ 0, 1, 0, -1]
 
# # Function to check if a cell
# # is be visited or not
# def isValid(vis, row, col):
   
#     # If cell lies out of bounds
#     if (row < 0 or col < 0 or row >= 4 or col >= 4):
#         return False
 
#     # If cell is already visited
#     if (vis[row][col]):
#         return False
 
#     # Otherwise
#     return True
 
# # Function to perform the BFS traversal
# def BFS(grid, vis, row, col):
   
#     # Stores indices of the matrix cells
#     q = queue()
 
#     # Mark the starting cell as visited
#     # and push it into the queue
#     q.append(( row, col ))
#     vis[row][col] = True
 
#     # Iterate while the queue
#     # is not empty
#     while (len(q) > 0):
#         cell = q.popleft()
#         x = cell[0]
#         y = cell[1]
#         print(grid[x][y], end = " ")
 
#         #q.pop()
 
#         # Go to the adjacent cells
#         for i in range(4):
#             adjx = x + dRow[i]
#             adjy = y + dCol[i]
#             if (isValid(vis, adjx, adjy)):
#                 q.append((adjx, adjy))
#                 vis[adjx][adjy] = True
 
# # Driver Code
# if __name__ == '__main__':
   
#     # Given input matrix
#     grid= [ [ 1, 2, 3, 4 ],
#            [ 5, 6, 7, 8 ],
#            [ 9, 10, 11, 12 ],
#            [ 13, 14, 15, 16 ] ]
 
#     # Declare the visited array
#     vis = [[ False for i in range(4)] for i in range(4)]
#     # vis, False, sizeof vis)
 
#     BFS(grid, vis, 0, 0)
 
# # This code is contributed by mohit kumar 29.
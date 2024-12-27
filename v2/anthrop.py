import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import asyncio
import websockets
import pickle

import seed_handler
from reality import World


# Human eyes operate at 60fps -->
# 60 perceives/sec * 60 sec/min * 60 min/hour = 216000 perceives/hour
PERCEIVES_PER_HOUR = 21600  # decreased for performance reasons


class Memory:
    '''
    Encodes an object with a diminishing salience connected to other memories.
    '''
    def __init__(self, object, salience: float):
        self.object = object
        self.salience = salience
        self.age = 0
        self.base_salience = salience
        self.connections = {}

    def connect(self, memory, strength: float) -> None:
        '''
        Connects other Memory to this Memory with a provided strength.

        Parameters:
        memory: other Memory to connect to this Memory
        strength: strength of connection between this Memory
                  and the provided memory
        '''
        if memory not in self.connections:
            self.connections[memory] = 0
        self.connections[memory] += strength

    def get_strength(self, memory):
        '''
        Returns the strength of the connection from this Memory
        to other Memory.

        Parameters:
        memory: other Memory to get connection strength
        '''
        return self.connections[memory]

    def __str__(self):
        return f'{self.object}'

    def __repr__(self):
        return f'{self.object}:{round(self.salience, 4)}'

    def __hash__(self):
        return hash(id(self.object))

    def __eq__(self, __o: object) -> bool:
        if type(__o) is not Memory:
            return False
        return __o.object is self.object

    def decay_function(age: float) -> float:
        '''
        Returns percentage left of memory based on memory age, modeling decay.
        Based on Jiang-Shedd hourly memory decay approximation.
        '''
        age_in_hours = age/PERCEIVES_PER_HOUR
        if age_in_hours < 1:
            return np.e**(-0.7*age_in_hours)
        else:
            return np.e**(-0.7*age_in_hours**(1/6))


class VisualMemory(Memory):
    def __init__(self, object, salience: float):
        super(object, salience)


class AudioMemory(Memory):
    def __init__(self, object, salience: float):
        super(object, salience)


class Mind:
    '''
    Holds the memories of a Person and allows them to intelligently function.
    '''
    def __init__(self, capacity: float, att_span: float, stm_thresh: float):
        '''
        Constructs the mind of a Person.

        Parameters:
        capacity: space available for memories in long term memory
        att_span: attention span for focus, float between [0, 1]
        stm_thresh: threshold for a memory to stay in short term memory
        '''
        assert att_span >= 0 and att_span <= 1

        self.capacity = capacity
        self.att_span = att_span
        self.stm_thresh = stm_thresh
        self.focus = [None, None]  # [object, distance]
        self.ltm = set()  # long term memory
        self.stm = set()  # short term memory (more salient)

    def set_focus(self, perceiving: list, horizon: float):
        '''
        Moves focus based on attention span and distance of percepts
        from Person

        Parameters:
        perceiving: list of perceived objects in environment
                    with relative distances
        horizon: max perceivable distance from Person
        '''
        # attention span determines whether focus on last object continues
        p = np.random.uniform()
        if p <= self.att_span:
            # focus stays on last object
            for percept in perceiving:
                if percept[0] is self.focus[0]:  # last object still perceived
                    # object remains same, its distance updates
                    self.focus = percept
                    return
        # changes focus to something nearby
        # (items farther from horizon are more likely)
        reverse_dists = 0
        for percept in perceiving:
            dist = percept[1]
            reverse_dists += horizon - dist
        gaze = np.random.uniform(0, reverse_dists)
        for percept in perceiving:
            reverse_dists -= horizon - percept[1]
            if gaze >= reverse_dists:
                self.focus = percept
                return

    def memorize(self, perceiving: list, horizon: float, world):
        '''
        Encode focus into memory, associating surrounding percepts with it

        Parameters:
        perceiving: list of perceived objects in environment
                    with relative distances
        horizon: max perceivable distance from Person
        '''
        memory = self.deep_remember(self.focus[0])
        salience_mutation = abs(np.random.normal(0, 0.5))
        salience = np.e**((horizon/2 - self.focus[1]) * salience_mutation)

        if not memory:  # focus is not an existing memory
            memory = Memory(self.focus[0], salience)
        else:  # focus is an existing memory
            memory.salience += salience
            # reset the base salience for the decay function
            memory.base_salience = memory.salience
        self.contextualize(memory, perceiving, world)
        self.ltm.add(memory)

    def contextualize(self, core_memory: Memory, perceiving: list,
                      world: World) -> None:
        '''
        Connects Memory with the perceived Memories around it
        in short term memory

        Parameters:
        core_memory: memory to have perceiving objects' memories connected to
        perceiving: list of perceived objects in environment
                    with relative distances
        '''
        for percept in perceiving:
            memory = self.shallow_remember(percept[0])
            if not memory:  # percept not a memory in short term memory
                continue
            if memory is core_memory:
                continue
            dist = world.get_dist_between(core_memory.object, memory.object)
            core_memory.connect(memory, strength=dist)

    def move_memories(self) -> None:
        '''
        Decays memories and moves outdated memories to/from short term memory.
        '''
        # decay memories
        for memory in self.ltm:
            memory.age += 1
            memory.salience = memory.base_salience * \
                Memory.decay_function(memory.age)
        # remove insufficiently salient memories from short term memory
        temp = self.stm.copy()
        for memory in self.stm:
            if memory.salience < self.stm_thresh:
                temp.remove(memory)
        self.stm = temp
        # add sufficiently salient memories to short term memory
        for memory in self.ltm:
            if memory.salience >= self.stm_thresh:
                self.stm.add(memory)

    def shallow_remember(self, object) -> Memory:
        '''
        Returns memory if the object is a memory in short term memory
        '''
        for memory in self.stm:
            if memory.object is object:
                return memory
        return None

    def deep_remember(self, object) -> Memory:
        '''
        Returns memory if the object is a memory in long term memory
        '''
        for memory in self.ltm:
            if memory.object is object:
                return memory
        return None

    def get_action(self):
        # memory = self.deep_remember(self.focus[0])
        # TODO: How do they decided how to take an action???
        # movement, speaking, doing???
        pass

    def show_network(self, name: str) -> None:
        '''
        Display the long term memory network as a directed graph.

        Parameters:
        name: name of Person
        '''
        edges = []
        edges_labels = {}
        disconnected_nodes = []
        for memory in self.ltm:
            connected = False
            for connection in memory.connections:
                edges.append((memory, connection))
                edges_labels[(memory, connection)] = round(
                    memory.get_strength(connection), 3)
                connected = True
            if not connected:
                disconnected_nodes.append(memory)

        G = nx.DiGraph()
        G.add_edges_from(edges)
        G.add_nodes_from(disconnected_nodes)
        saliences = [memory.salience for memory in G.nodes]
        max_salience = max(saliences)
        max_salience_str = str(int(max_salience))
        node_multiplier = int('1' + ('0' * (5 - len(max_salience_str))))

        # scales the nodes according to saliences
        node_sizes = [s * node_multiplier for s in saliences]
        pos = nx.spring_layout(G)
        nx.draw_networkx(
            Graph=G,
            Mapping=pos,
            arrows=True,
            with_labels=True,
            node_size=node_sizes
        )
        nx.draw_networkx_edge_labels(
            Graph=G,
            Mapping=pos,
            edge_labels=edges_labels,
            font_color='red'
        )
        plt.title(f'{name} memory network')
        print(f'\n{name} memory network contents')
        print('  connections:', edges)
        print('  singletons:', disconnected_nodes)
        plt.show()


class Person:
    '''
    A person perceives objects in its environment, forms memories,
    converses with other Persons.
    '''
    counter = 0
    names = [
        'grant', 'ethan', 'jennifer', 'brent', 'braun', 'kevin', 'claudia',
        'brian', 'dane', 'hunter', 'clinton', 'ashley'
    ]

    def __init__(self, parent: 'Person' = None):
        '''
        Constructs mind of Person and sets biophysiological facts.

        Parameters:
        parent: the Person(s) passing traits to this Person
        '''
        seed = seed_handler.load_seed()
        np.random.seed(seed)

        self.alive = True
        self.age = 0
        self.perceiving = []  # objects Person perceives
        self.horizon = 3  # distance Person can see
        self.name = Person.names[Person.counter]
        Person.counter += 1

        # construct mind
        capacity = np.random.normal(10, 2)
        att_span = np.random.normal(0.5, 0.2)
        stm_thresh = abs(np.random.normal(1, 0.25))
        if parent:
            capacity_mutation = np.random.normal(0, 1)
            att_span_mutation = np.random.normal(0, 0.05)
            stm_thresh_mutation = np.random.normal(0, 0.05)
            capacity = parent.mind.capacity + capacity_mutation
            att_span = parent.mind.att_span + att_span_mutation
            stm_thresh = parent.mind.stm_threh + stm_thresh_mutation
        att_span = max(0, min(att_span, 1))
        self.mind = Mind(capacity, att_span, stm_thresh)

        self.mouth = Mouth()

        seed_handler.save_seed(seed+1)

    def perceive(self, world: World) -> None:
        self.perceiving = world.get_nearby_from_object(self, self.horizon)
        self.mind.set_focus(self.perceiving, self.horizon)
        self.mind.memorize(self.perceiving, self.horizon, world)
        self.mind.move_memories()
        self.age += 1

    def act(self, world: World) -> None:
        # self.mind.get_action()
        self.speak(world)

    def speak(self, world: World) -> None:
        '''
        Person sometimes speaks from memory, other times speaks randomly.
        '''
        # random speech, params by rohan
        seed = seed_handler.load_seed()
        np.random.seed(seed)
        sound = self.mouth.speak(
            tongue={
                "index": np.random.uniform(0, 35),
                "diameter": np.random.uniform(0, 6)
            },
            constriction={
                "index": np.random.uniform(2, 50),
                "diameter": np.random.uniform(-1, 4)
            },
            timeout=np.random.uniform(0.2, 3),
            intensity=np.random.uniform(0.3, 1),
            tenseness=np.random.uniform(0, 1),
            frequency=np.random.uniform(20, 1000)
        )

        world.attribute_sound(self, sound)

        seed_handler.save_seed(seed+1)

    def show_network(self) -> None:
        self.mind.show_network(self.name)

    def stats(self, world: World):
        print(self)
        print(f'  age: {self.age}')
        print(f'  coords: {world.get_coords(self)}')
        print(f'  horizon: {self.horizon}')
        print(f'  capacity: {self.mind.capacity}')
        print(f'  attention span: {self.mind.att_span}')
        print(f'  focus: {self.mind.focus}')
        print(f'  perceiving: {self.perceiving}')

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)


class Sound:
    def __init__(self, directory: str, properties: tuple) -> None:
        '''
        Parameters:
        filename: wave file path
        properties: settings
        '''
        self.directory = directory
        self.name = directory.split('/')[1]
        self.properties = properties
        self.volume = properties[3]  # intensity used as volume for now
        # get sound wave from pickle
        with (open(f'{directory}/{self.name}.pickle', 'rb')) as openfile:
            self.wave = np.asarray(pickle.load(openfile))

    def __str__(self):
        return 's:' + self.name[:8]

    def __repr__(self):
        return str(self)

    def compare(sound1: 'Sound', sound2: 'Sound') -> None:
        '''
        TODO:
        This looks like an ideal application
        for the cross correlation function,
        which will show the correlation between the two waveforms
        for every time offset between the two.
        This is done by first removing the mean from each waveform,
        and then multiplying the two resulting zero-mean waveforms
        together element by element and summing the result,
        repeating for each possible sample shift between the waveforms.
        These results can be scaled by the product
        of the standard deviation of the two waveforms,
        which would normalize the result similar to what is done
        in the Pearson correlation coefficient.
        '''
        pass


class Mouth:
    '''
    Capable of holding all parameters of a phone.
    '''
    def __init__(self):
        self.tongue = {"index": 0, "diameter": 0}
        self.constriction = {"index": 0, "diameter": 0}
        self.timeout = 0
        self.intensity = 0
        self.tenseness = 0
        self.frequency = 0
        self.duration = 1

    def speak(self, tongue: float, constriction: float, timeout: float,
              intensity: float, tenseness: float, frequency: float,
              human_audible: bool = False) -> Sound:
        '''
        Prepares the mouth to speak with provided parameters
        and returns file of sound location.

        Parameters:
        human_audible: plays sound if True
        '''
        self.tongue = tongue
        self.constriction = constriction
        self.timeout = timeout
        self.intensity = intensity
        self.tenseness = tenseness
        self.frequency = frequency

        async def send_socket(mouth: Mouth):
            async with websockets.connect("ws://localhost:5678") as websocket:
                await websocket.send(f"M:{mouth}")
                new_message = await websocket.recv()
                if new_message[0:2] != 'F:':
                    new_sound = await websocket.recv()
                print(new_sound[2:])
                return Sound(
                    new_sound[2:],
                    (self.tongue, self.constriction, self.timeout,
                        self.intensity, self.tenseness,
                        self.frequency, self.duration)
                )

        loop = asyncio.get_event_loop()
        coroutine = send_socket(self)
        sound = loop.run_until_complete(coroutine)
        return sound

    def __str__(self):
        return f'{self.tongue["index"]}|{self.tongue["diameter"]}| \
                {self.constriction["index"]}|{self.constriction["diameter"]}|\
                {self.duration}|{self.timeout}|{self.intensity}|\
                {self.tenseness}|{self.frequency}'


# dist = abs(np.random.normal(0, 0.5, size=100))
# plt.hist(dist)
# plt.show()

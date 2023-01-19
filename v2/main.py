import argparse
import numpy as np

import seed_handler
from anthrop import Person
from reality import World


def main(width:int, height:int, seed:int):
    seed_handler.save_seed(seed)
    np.random.seed(seed)
    world = World(width, height, seed)
    # population = 5
    # np.random.uniform(0, width, population).astype(int)
    # np.random.uniform(0, height, population).astype(int)
    pop = [world.create_person(1, 0), world.create_person(3, 0), 
            world.create_person(0, 1), world.create_person(0, 2)]
    world.show()
    # for _ in range(1):
    #     pop[0].perceive(world)
    #     pop[0].act(world)
        # pop[0].stats(world)
    pop[0].perceive(world)
    pop[0].act(world)
    pop[1].perceive(world)
    pop[1].stats(world)
    # pop[0].show_network()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Insert description.')  # TODO: figure out what to put here
    parser.add_argument('width', type=int, help='width of the map')
    parser.add_argument('height', type=int, help='height of the map')
    parser.add_argument('-l', '--seed', type=int, help='set random seed')

    args = parser.parse_args()
    main(args.width, args.height, args.seed)


# TODO
# introduce mutation chances changing with individual and environment
# consolidate memories during a sleep cycle?
# https://www.simplypsychology.org/memory.html
# feed, then wander
# inner product of fourier
# add muted feature when speaking and control with human_audible in Mouth.speak
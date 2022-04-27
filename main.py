from elements import World, Squealer, Interpreter

# duration = 1.0   # in seconds, may be float
# f = 440.0        # sine frequency, Hz, may be float
def human_game(world: World, squealer: Squealer):
    while True:
        print('\n'+str(world)+'\n')
        (duration, f) = squealer.plan(world, squealer.uniform_less_greed_prob)
        squealer.speak(duration, f)

        print('Allow? (y/n)')
        permission = (input() == 'y')
        squealer.listen(world, permission)

def humanless_game(world: World, squealer: Squealer, interpreter: Interpreter):
    distortion_func = lambda x: x
    while True:
        (duration, f) = squealer.plan(world, squealer.uniform_less_greed_prob)
        permission = interpreter.listen(world, duration, f, distortion_func, 100)
        action = squealer.listen(world, permission)
        if action:
            interpreter.associate(action)



def main():
    w = World(dim=(4,4), rand_walls=False, walliness=0.3)
    squealer = Squealer(name='paul', thinking_aloud=False)
    human_present = False

    successfully_placed = w.place_agent(squealer, pos=(0,0))
    while not successfully_placed:
        pos = input(f'trouble placing {squealer}, give coords (\'n, m\'):')
        successfully_placed = w.place_agent(squealer, pos=pos)

    if human_present:
        score = human_game(w, squealer)
    else:
        interpreter = Interpreter(name='dave', thinking_alound=False)
        score = humanless_game(w, squealer, interpreter)
        
    # print(f'{squealer}\'s score: {squealer.score}')


if __name__ == '__main__':
    main()
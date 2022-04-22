from elements import World, Agent

# duration = 1.0   # in seconds, may be float
# f = 440.0        # sine frequency, Hz, may be float
    

def main():
    print('\n')
    w = World(dim=(15,15), rand_walls=True, walliness=0.3)
    paul = Agent(name='paul')
    w.place_agent(paul, pos=(0,0))

    
    
    while True:
        print(str(w)+'\n\n\n')
        (duration, f) = paul.plan(w, paul.uniform_greed_prob)
        paul.speak(duration, f)

        print('Allow? (y/n)')
        permission = (input() == 'y')
        paul.listen(w, permission)


if __name__ == '__main__':
    main()
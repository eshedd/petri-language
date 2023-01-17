# file that stores the shared seed value 
seed_val_file = "seed_val.txt"

def save_seed(val, filename=seed_val_file):
    """ saves val """
    with open(filename, 'w') as f:
        f.write(str(val))

def load_seed(filename=seed_val_file):
    """ loads val. Called by all scripts that need the shared seed value """
    with open(filename, 'r') as f:
        return int(f.read())
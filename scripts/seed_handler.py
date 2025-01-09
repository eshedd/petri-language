# file that stores the shared seed value
seed_val_file = "seed_val.txt"


def save_seed(val, filename: str = seed_val_file):
    """
    Saves values to seed_val_file.
    """
    with open(filename, 'w') as f:
        f.write(str(val))


def load_seed(filename: str = seed_val_file):
    """
    Loads value from seed_val_file.
    Called by all scripts that need the shared seed value.
    """
    with open(filename, 'r') as f:
        return int(f.read())

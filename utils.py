

def str_to_bool(s):
    # Convert string to lower case to make the function case-insensitive
    s = s.lower()
    if s in ['true', 'yes', '1']:
        return True
    elif s in ['false', 'no', '0']:
        return False
    else:
        raise ValueError(f"Cannot convert '{s}' to a boolean value")
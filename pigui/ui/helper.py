
def deep_compare(dict1, dict2):
    # Check if both inputs are dictionaries
    if not isinstance(dict1, dict) or not isinstance(dict2, dict):
        return False

    # Check if the keys in dict1 match the keys in dict2
    if set(dict1.keys()) != set(dict2.keys()):
        return False

    # Recursively compare the values for each key
    for key in dict1.keys():
        value1, value2 = dict1[key], dict2[key]

        # If both values are dictionaries, recursively compare them
        if isinstance(value1, dict) and isinstance(value2, dict):
            if not deep_compare(value1, value2):
                return False
        # Otherwise, compare the values directly
        else:
            if value1 != value2:
                return False

    return True
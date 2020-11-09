def str_to_bool(value):
    if str(value).lower() in ['true', 't', '1']:
        return True
    elif str(value).lower() in ['false', 'f', '0']:
        return False
    raise ValueError(f'Cannot convert {value} to boolean')


def flatten_value_in_nested_dict(nested_dict, key_path):
    """Flatten a value within a nested dict.

    eg.
        If nested_dict = {'outer-key': {'inner-key': 'inner-value'}}
        And key_path = 'outer-key.inner-value'
        Then result = {'outer-key: 'inner-value'}
    """
    val = nested_dict
    for key in key_path.split('.'):
        val = val.get(key) or {}
    return val


def flatten_nested_dict(nested_dict, flatten_map):
    for k, m in flatten_map.items():
        nested_dict[k] = flatten_value_in_nested_dict(nested_dict, key_path=m)
    return nested_dict

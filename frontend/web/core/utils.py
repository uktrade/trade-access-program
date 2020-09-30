def str_to_bool(value):
    if str(value).lower() in ['true', 't', '1']:
        return True
    elif str(value).lower() in ['false', 'f', '0']:
        return False
    raise ValueError(f'Cannot convert {value} to boolean')


def flatten_nested_dict(d, key_path):
    val = d
    for key in key_path:
        val = val.get(key) or {}
    return val

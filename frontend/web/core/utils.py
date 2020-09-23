def flatten_nested_dict(d, keys):
    val = d
    for key in keys:
        val = val.get(key) or {}
    return val

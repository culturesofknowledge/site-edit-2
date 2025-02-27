# A group of stand-alone functions for suggestion work used in multiple places

def suggestion_fields(fields_map):
    c = ()
    for b in fields_map:
        c = c + (b[0],)
    return c

def suggestion_fields_dict(fields_map):
    x = {}
    for b in fields_map:
        x[b[0]] = b[1]
    return x

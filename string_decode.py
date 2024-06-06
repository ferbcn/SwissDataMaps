# Decodes wrongly encoded strings
def decode_string(s):
    if isinstance(s, str):
        return s.encode('latin1').decode('utf8')
    return s
"""Simple utility to generate code to communicate between C and Python.

This utility generates C definitions and Python definitions in order to
send integers, strings, lists, and other custom types over a socket.

"""
import logtbl


def read_int32(buf, offset):
    """Reads a 32bit integer from the buffer."""
    return 4, unpack('I', buf[offset:offset+4])[0]


def read_ptr(buf, offset):
    """Read a pointer from the buffer."""
    length, value = read_int32(buf, offset)
    return length, '0x%08x' % value


def read_string(buf, offset):
    """Reads an utf8 string from the buffer."""
    length, maxlength = unpack('HH', buf[offset:offset+8])
    return length+4, (length, maxlength, buf[offset+4:offset+4+length])


def read_buffer(buf, offset):
    """Reads a memory buffer from the buffer."""
    length, maxlength = unpack('HH', buf[offset:offset+8])
    # only return the maxlength, as we don't log the actual buffer right now
    return 4, maxlength


def read_registry(buf, offset):
    """Read logged registry data from the buffer."""
    typ = unpack('H', buf[offset:offset+2])[0]
    # do something depending on type
    return


def read_list(buf, offset, fn):
    """Reads a list of _fn_ from the buffer."""
    count = unpack('H', buf[offset:offset+2])[0]
    ret, length = [], 0
    for x in xrange(count):
        item_length, item = fn(buf, offset+length)
        length += item_length
        ret.append(item)
    return item_length+2, ret


def parse_fmt(funcname, fmt, *args):
    typ = {
        's': read_string,
        'S': read_string,
        'u': read_string,
        'U': read_string,
        'b': read_buffer,
        'B': read_buffer,
        'i': read_int32,
        'l': read_int32,
        'L': read_int32,
        'p': read_ptr,
        'P': read_ptr,
        'o': read_string,
        'O': read_string,
        'a': None,
        'A': None,
        'r': read_registry,
        'R': read_registry,
    }


def generate_c_code():
    for index, (funcname, args) in enumerate(logtbl.table[2:]):
        definitions = [k for k, (v, _) in enumerate(logtbl.table[2:])
                       if v == funcname]
        print '#define LOG_%s_%d "%s"' % (funcname,
                                          definitions.index(index),
                                          args[0])

if __name__ == '__main__':
    generate_c_code()

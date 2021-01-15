# distutils: include_dirs = .
from libc.stdlib cimport malloc, free


cdef extern from "yxml.h":
    ctypedef struct yxml_t:
        char *elem
        char data[8]
        char *attr
        char *pi
        unsigned long byte
        unsigned long total
        unsigned int line


    ctypedef enum yxml_ret_t:
        YXML_EEOF = -5
        YXML_EREF = -4
        YXML_ECLOSE = -3
        YXML_ESTACK = -2
        YXML_ESYN = -1
        YXML_OK = 0
        YXML_ELEMSTART = 1
        YXML_CONTENT = 2
        YXML_ELEMEND = 3
        YXML_ATTRSTART = 4
        YXML_ATTRVAL = 5
        YXML_ATTREND = 6
        YXML_PISTART = 7
        YXML_PICONTENT = 8
        YXML_PIEND = 9

    void yxml_init(yxml_t *yx, void *buf, size_t siz)
    yxml_ret_t yxml_parse(yxml_t *, int)


START = 1
END = 2
ATTR = 3
CONTENT = 4

def parse_file(f, *, state_size=4096, chunk_size=4096, data_size=4096, utf8=False):
    cdef yxml_t yx
    cdef void* state_buf
    cdef char* data_buf
    cdef char* data_p
    try:
        data_buf = <char*> malloc(data_size)
        if not data_buf:
            raise MemoryError("could not allocate data buffer")
        data_p = data_buf
        state_buf = malloc(state_size)
        if not state_buf:
            raise MemoryError("could not allocate state buffer")
        yxml_init(&yx, state_buf, state_size)
        el_stack = []  # TODO: statically allocate size
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            for b in bytes(chunk):
                res = yxml_parse(&yx, b)
                if res < 0:
                    raise RuntimeError("XML error %d at position line %d byte %d (offset %d)" % (res, yx.line, yx.byte, yx.total))
                if res == YXML_ELEMEND:
                    el_name = el_stack.pop(-1)
                    if data_p - data_buf > 0:
                        if utf8:
                            val = data_buf[:(data_p - data_buf)].decode('UTF-8')
                        else:
                            val = bytes(data_buf)
                        yield (CONTENT, el_name, val)
                        data_p = data_buf
                    yield (END, el_name)
                elif res == YXML_ELEMSTART:
                    if utf8:
                        el_name = yx.elem.decode('UTF-8')
                    else:
                        el_name = bytes(data_buf)
                    el_stack.append(el_name)
                    yield (START, el_name)
                elif res == YXML_ATTREND:
                    if utf8:
                        attr_val = yx.attr.decode('UTF-8')
                        val = data_buf[:(data_p - data_buf)].decode('UTF-8')
                    else:
                        attr_val = bytes(yx.attr)
                        val = bytes(data_buf)
                    yield (ATTR, el_stack[-1], attr_val, val)
                    data_p = data_buf
                elif res == YXML_ATTRVAL or res == YXML_CONTENT:
                    for i in range(8):
                        if not yx.data[i]:
                            break
                        data_p[0] = yx.data[i]
                        data_p += 1
                        if data_p - data_buf >= data_size:
                            raise RuntimeError("Data or attribute too long for data buffer; increase size")
                    data_p[0] = 0

    finally:
        if state_buf:
            free(state_buf)
        if data_buf:
            free(data_buf)

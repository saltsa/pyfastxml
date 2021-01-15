# distutils: include_dirs = .
from libc.stdlib cimport malloc, free
from libc.string cimport strlen

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
    size_t yxml_symlen(yxml_t *x, const char *s)


E_START = 1
E_END = 2
E_ATTR = 3
E_CONTENT = 4

cdef to_string(const char *data_buf, int len, int utf8):
    if utf8:
        return data_buf[:len].decode('UTF-8')
    return bytes(data_buf[:len])

def parse(
    read,
    handle,
    *,
    int state_size=4096,
    int chunk_size=4096,
    int data_size=4096,
    int el_stack_size=64,
    int utf8=False,
):
    cdef yxml_t yx
    cdef void*state_buf=<void*>0
    cdef char*data_buf=<char*>0
    cdef int data_p
    cdef int el_stack_p
    E_START = 1
    E_END = 2
    E_ATTR = 3
    E_CONTENT = 4
    try:
        data_buf = <char*> malloc(data_size)
        if not data_buf:
            raise MemoryError("could not allocate data buffer")
        data_p = 0
        state_buf = malloc(state_size)
        if not state_buf:
            raise MemoryError("could not allocate state buffer")
        yxml_init(&yx, state_buf, state_size)
        el_stack = [None] * el_stack_size
        el_stack_p = 0
        while True:
            chunk = read(chunk_size)
            if not chunk:
                break
            for b in bytes(chunk):
                res = yxml_parse(&yx, b)
                if res < 0:
                    raise RuntimeError(
                        "XML error %d at position line %d byte %d (offset %d)" % (res, yx.line, yx.byte, yx.total))
                if res == YXML_ELEMEND:
                    el_name = el_stack[el_stack_p - 1]
                    el_stack_p -= 1
                    assert el_stack_p >= 0
                    if data_p:
                        handle(E_CONTENT, el_name, to_string(data_buf, data_p, utf8))
                        data_p = 0
                    handle(E_END, el_name)
                elif res == YXML_ELEMSTART:
                    el_name = to_string(yx.elem, yxml_symlen(&yx, yx.elem), utf8)
                    el_stack[el_stack_p] = el_name
                    el_stack_p += 1
                    if el_stack_p >= el_stack_size:
                        raise RuntimeError("Too deep, raise stack size")
                    handle(E_START, el_name)
                elif res == YXML_ATTREND:
                    attr_val = to_string(yx.attr, strlen(yx.attr), utf8)
                    val = to_string(data_buf, data_p, utf8)
                    handle(E_ATTR, el_stack[el_stack_p - 1], attr_val, val)
                    data_p = 0
                elif res == YXML_ATTRVAL or res == YXML_CONTENT:
                    for i in range(8):
                        if not yx.data[i]:
                            break
                        data_buf[data_p] = yx.data[i]
                        data_p += 1
                        if data_p >= data_size:
                            raise RuntimeError("Data or attribute too long for data buffer; increase size")
    finally:
        if state_buf:
            free(state_buf)
        if data_buf:
            free(data_buf)

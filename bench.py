import io
import time
import psutil
import xml.sax as sax
import xml.sax.handler as sh
import lxml.etree as ET
import sys
from itertools import islice


class Grabber(sh.ContentHandler):
    def __init__(self):
        self.data = {}
        self.string_pool = {}

    def startElement(self, tag, attrib):
        if tag == "muntagi":
            attrib = {self.string_pool.get(k, k): v for (k, v) in attrib.items()}
            # attrib = dict(attrib)
            self.data[attrib["id"]] = attrib


def m1():
    sg = Grabber()
    sax.parse("example.xml", handler=sg)
    result = sg.data
    return result


def m2():
    results = {}
    for event, elem in ET.iterparse("example.xml", events=("start",), tag="muntagi"):
        results[elem.attrib["id"]] = dict(elem.attrib)
        elem.clear()
    return results


def test(m):
    t0 = time.time()
    result = m()
    t = time.time() - t0
    print(len(result))
    print(list(islice(result.items(), 0, 10)))
    print(t)
    print(psutil.Process().memory_info())


if __name__ == "__main__":
    test(globals()[sys.argv[1]])

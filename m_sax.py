import xml.sax as sax
import xml.sax.handler as sh


class Grabber(sh.ContentHandler):
    def __init__(self):
        self.data = {}
        self.string_pool = {}

    def startElement(self, tag, attrib):
        if tag == "muntagi":
            attrib = {self.string_pool.get(k, k): v for (k, v) in attrib.items()}
            self.data[attrib["id"]] = attrib


def m1():
    sg = Grabber()
    sax.parse("example.xml", handler=sg)
    result = sg.data
    return result

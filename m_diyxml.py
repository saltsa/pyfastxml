import attr
import io
import sys
import time
import string



def get_data(file):
    with open(file, mode="r", encoding="utf-8-sig") as f:
        data = f.read()
    return data


class XMLSyntaxError(SyntaxError):
    pass


@attr.s
class Attr:
    name = attr.ib(default=None)
    value = attr.ib(default=None)

@attr.s
class Token:
    tag = attr.ib(default=None)
    attributes = attr.ib(default=None)
    text = attr.ib(default=None)

    _type = attr.ib(default=None)
    def empty(self):
        return not any((self.tag, self.attributes, self.text))

@attr.s
class Decoder:
    """
    Loosely based on XML parse logic in Go:
    https://golang.org/src/encoding/xml/xml.go
    """
    stream = attr.ib()


    def _getc(self):
        """Get one char from stream"""
        c = self.stream.read(1)
        if len(c) == 0:
            raise EOFError()
        return c

    def _space(self):
        """Forward stream until whitespace"""
        while True:
            c = self.stream.read(1)
            if not c.isspace():
                self._ungetc()
                return

    def _ungetc(self):
        """Rewind stream by one char"""
        te = self.stream.tell()
        self.stream.seek(te-1, io.SEEK_SET)

    def _until_end_tag(self):
        """Read until end of tag spec"""
        while True:
            c = self.stream.read(1)
            if c == '>':
                break

    def token(self):

        t = self.raw_token()

        # if t._type == "start":
        #     print("start element", t)
        # elif t._type == "end":
        #     print("end element", t)
        # elif t._type == "startend":
        #     print("startend element", t)
        return t

    def raw_token(self):

        self._space()

        b = self._getc()

        if b != '<':
            self._ungetc()
            return Token(text=self._text(), type="text")

        b = self._getc()

        if b == '/':
            self._space()
            tag_name = self._get_name()
            b = self._getc()
            if b != '>':
                raise XMLSyntaxError("invalid endtag")
            return Token(tag=tag_name, type="end")
        elif b == '?':
            # starting <?xml... tag
            # TODO: Validate this
            self._until_end_tag()
            return Token("xml")
        elif b == '!':
            print("comment or cdata")
            # TODO: Fix this, does not handle all cases
            self._until_end_tag()
            return Token("!", type="comment")

        self._ungetc()

        tag_name = self._get_name()
        attributes = []

        while True:
            self._space()

            b = self._getc()
            if b == '/':
                b = self._getc()
                if b != '>':
                    raise XMLSyntaxError("syntax error")
                return Token(tag=tag_name, attributes=attributes, type="startend")
                break
            elif b == '>':
                break

            self._ungetc()

            attribute = Attr(self._get_name())
            self._space()

            b = self._getc()
            if b != '=':
                raise XMLSyntaxError("attrib without value: {}".format(attribute.name))

            self._space()
            attribute.value = self._quoted_text()

            attributes.append(attribute)

    
        return Token(tag=tag_name, attributes=attributes, type="start")

    @staticmethod
    def valid_name_byte(b):
        valid_chars = string.ascii_letters + string.digits + "_-:."
        return b in valid_chars

    def _get_name(self):
        buf = ""
        while True:
            b = self._getc()
            if Decoder.valid_name_byte(b):
                buf += b
            else:
                self._ungetc()
                break
        return buf

    def _quoted_text(self):
        buf = ""
        b = self._getc()
        if not (b == '"' or b == '\''):
            raise XMLSyntaxError("invalid attribute quote")

        while True:
            b = self._getc()
            if b == '<' or b == '>':
                raise XMLSyntaxError("< or > in text input")
            if b == '"' or b == '\'':
                break
    
            buf += b

        return buf

    def _text(self):
        buf = ""
        while True:
            b = self._getc()
            if b == '<' or b == '>':
                self._ungetc()
                break
    
            buf += b
        if len(buf) == 0:
            return None
        return buf



def get_dict(dec):
    list_of_dicts = {}

    while True:
        try:
            t = dec.token()
        except EOFError:
            print("EOFERROR")
            break
        if t is None:
            print("t is none")
            break
        if t.empty():
            #print("t is empty")
            break
        
        # TODO: ugly
        if t.attributes and len(t.attributes) > 0:
            key = [x for x in t.attributes if x.name == "id"][0].value
            
            list_of_dicts[key] = {}

            for a in t.attributes:
                list_of_dicts[key] |= {a.name: a.value}
                
    return list_of_dicts


def m4():
    #results = {}
    dec = Decoder(io.StringIO(get_data("example.xml")))
    return get_dict(dec)

if __name__ == '__main__':
    print("get data..")
    d = get_data(sys.argv[1])
    print("decoder...")
    dec = Decoder(io.StringIO(d))

    start = time.time()
    dicts = get_dict(dec)
    end = time.time()
    
    for d in dicts:
        print(d)

    print("item count was {}".format(len(dicts)))
    print("parsing took {} seconds".format(end-start))
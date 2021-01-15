import lxml.etree as ET


def m2():
    results = {}
    for event, elem in ET.iterparse("example.xml", events=("start",), tag="muntagi"):
        results[elem.attrib["id"]] = dict(elem.attrib)
        elem.clear()
    return results

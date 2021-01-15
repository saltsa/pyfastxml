def m3():
    import fastxml

    tag = "muntagi"
    with open("example.xml", "rb") as f:
        els = []
        el = None

        def handle(*r):
            nonlocal el
            a = r[0]
            if a == 1:  # new tag
                if r[1] == tag:
                    el = {}
                    els.append(el)
            if r[0] == 3:  # attribute
                if r[1] == tag:
                    el[r[2]] = r[3]

        fastxml.parse(f.read, handle, utf8=True, chunk_size=524288)
    return {e["id"]: e for e in els}

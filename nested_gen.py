with open("example.xml", "w") as f:
    f.write("<root>")
    f.write("<nest>")
    for x in range(50):
        if x % 8 == 0:
            f.write(
                f'<contagi id="{x}" ccc="{(x * 331) % 96452}">{x} {x} {x}</contagi>'
            )
        else:
            f.write(f'<muntagi id="{x}" a="{(x * 331) % 96452}" />')
    f.write("</root>")
    f.write("</root>")

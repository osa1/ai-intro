def print_confusion_matrix(handle, classified_0, classified_90, classified_180, classified_270):
    # First row
    a00 = len(filter(lambda x: x.orientation == 0,   classified_0))
    a10 = len(filter(lambda x: x.orientation == 90,  classified_0))
    a20 = len(filter(lambda x: x.orientation == 180, classified_0))
    a30 = len(filter(lambda x: x.orientation == 270, classified_0))

    # Second row
    a01 = len(filter(lambda x: x.orientation == 0,   classified_90))
    a11 = len(filter(lambda x: x.orientation == 90,  classified_90))
    a21 = len(filter(lambda x: x.orientation == 180, classified_90))
    a31 = len(filter(lambda x: x.orientation == 270, classified_90))

    # Third row
    a02 = len(filter(lambda x: x.orientation == 0,   classified_180))
    a12 = len(filter(lambda x: x.orientation == 90,  classified_180))
    a22 = len(filter(lambda x: x.orientation == 180, classified_180))
    a32 = len(filter(lambda x: x.orientation == 270, classified_180))

    # Fourth row
    a03 = len(filter(lambda x: x.orientation == 0,   classified_270))
    a13 = len(filter(lambda x: x.orientation == 90,  classified_270))
    a23 = len(filter(lambda x: x.orientation == 180, classified_270))
    a33 = len(filter(lambda x: x.orientation == 270, classified_270))

    handle.write("+-----------------------------------+\n")

    handle.write("|  %s  |  %s  |  %s  |  %s  |\n" \
                 % (str(a00).rjust(4, ' '),
                    str(a10).rjust(4, ' '),
                    str(a20).rjust(4, ' '),
                    str(a30).rjust(4, ' ')))

    handle.write("|  %s  |  %s  |  %s  |  %s  |\n" \
                 % (str(a01).rjust(4, ' '),
                    str(a11).rjust(4, ' '),
                    str(a21).rjust(4, ' '),
                    str(a31).rjust(4, ' ')))

    handle.write("|  %s  |  %s  |  %s  |  %s  |\n" \
                 % (str(a02).rjust(4, ' '),
                    str(a12).rjust(4, ' '),
                    str(a22).rjust(4, ' '),
                    str(a32).rjust(4, ' ')))

    handle.write("|  %s  |  %s  |  %s  |  %s  |\n" \
                 % (str(a03).rjust(4, ' '),
                    str(a13).rjust(4, ' '),
                    str(a23).rjust(4, ' '),
                    str(a33).rjust(4, ' ')))

    handle.write("+-----------------------------------+\n")

class ImageData:
    def __init__(self, name, orientation, rgbs):
        self.name = name
        self.orientation = orientation
        self.rgbs = rgbs
        self.rgbs_merged = map(merge_rgb, rgbs)

    def __str__(self):
        return "ImageData<name: " + self.name + "\n" + \
               "          orientation: " + str(self.orientation) + "\n" + \
               "          rgbs: " + str(self.rgbs) + ">"

    def __repr__(self):
        return self.__str__()


def parse_img_file(file):
    f = open(file, 'r')

    ret = []

    for line in f.readlines():
        parts = line.split()
        name = parts[0]
        orient = int(parts[1])

        assert ((len(parts) - 2) % 3 == 0)

        rgbs = []

        for i in xrange(2, len(parts), 3):
            r = int(parts[i  ])
            g = int(parts[i+1])
            b = int(parts[i+2])

            rgbs.append((r, g, b))

        ret.append(ImageData(name, orient, rgbs))

    return ret

def merge_rgb((r, g, b)):
    return (r << 16) + (g << 8) + b

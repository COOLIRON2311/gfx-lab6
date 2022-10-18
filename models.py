from lab6 import Point, Polygon, Polyhedron

class Models:
    """
    Tetrahedron = 0
    Hexahedron = 1
    Octahedron = 2
    Icosahedron = 3
    Dodecahedron = 4
    """
    class Cube(Polyhedron):
        def __init__(self, size = 100):
            p1 = Point(0, 0, 0)
            p2 = Point(size, 0, 0)
            p3 = Point(size, size, 0)
            p4 = Point(0, size, 0)
            p5 = Point(0, 0, size)
            p6 = Point(size, 0, size)
            p7 = Point(size, size, size)
            p8 = Point(0, size, size)
            polygons = [
                Polygon([p1, p2, p3, p4]),
                Polygon([p1, p2, p6, p5]),
                Polygon([p2, p3, p7, p6]),
                Polygon([p3, p4, p8, p7]),
                Polygon([p4, p1, p5, p8]),
                Polygon([p5, p6, p7, p8])
            ]
            super().__init__(polygons)
    class Tetrahedron(Polyhedron):
        def __init__(self, size = 100):
            t = Models.Cube(size)
            p1 = t.polygons[0].points[0]
            p2 = t.polygons[0].points[1]
            p3 = t.polygons[0].points[2]
            p4 = t.polygons[0].points[3]
            polygons = [
                Polygon([p1, p2, p3]),
                Polygon([p1, p2, p4]),
                Polygon([p1, p3, p4]),
                Polygon([p2, p3, p4])
            ]
            super().__init__(polygons)

    class Octahedron(Polyhedron):
        def __init__(self, size = 100):
            t = Models.Cube(size)
            p1 = t.polygons[0].center
            p2 = t.polygons[1].center
            p3 = t.polygons[2].center
            p4 = t.polygons[3].center
            p5 = t.polygons[4].center
            p6 = t.polygons[5].center
            polygons = [
                Polygon([p1, p2, p3]),
                Polygon([p1, p2, p4]),
                Polygon([p1, p3, p5]),
                Polygon([p1, p4, p5]),
                Polygon([p2, p3, p6]),
                Polygon([p2, p4, p6]),
                Polygon([p3, p5, p6]),
                Polygon([p4, p5, p6])
            ]
            super().__init__(polygons)

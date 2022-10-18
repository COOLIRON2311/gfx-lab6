import tkinter as tk
from dataclasses import dataclass
from enum import Enum
from math import cos, radians, sin, tan
from tkinter import messagebox as mb
from tkinter import simpledialog as sd
import numpy as np

class Projection(Enum):
    Perspective = 0
    Axonometric = 1

    def __str__(self) -> str:
        match self:
            case Projection.Perspective:
                return "Перспективная"
            case Projection.Axonometric:
                return "Аксонометрическая"
        return "Неизвестная проекция"


class Mode(Enum):
    Translate = 0  # перемещение
    Rotate = 1  # вращение
    Scale = 2  # масштабирование

    def __str__(self) -> str:
        return super().__str__().split(".")[-1]


class Function(Enum):
    None_ = 0
    ReflectOverPlane = 1
    ScaleAboutCenter = 2
    RotateAroundAxis = 3
    RotateAroundLine = 4

    def __str__(self) -> str:
        match self:
            case Function.None_:
                return "Не выбрано"
            case Function.ReflectOverPlane:
                return "Отражение относительно плоскости"
            case Function.ScaleAboutCenter:
                return "Масштабирование относительно центра"
            case Function.RotateAroundAxis:
                return "Вращение относительно оси"
            case Function.RotateAroundLine:
                return "Вращение вокруг прямой"
            case _:
                pass
        return "Неизвестная функция"


class ShapeType(Enum):
    Tetrahedron = 0
    Hexahedron = 1
    Octahedron = 2
    Icosahedron = 3
    Dodecahedron = 4

    def __str__(self) -> str:
        match self:
            case ShapeType.Tetrahedron:
                return "Тетраэдр"
            case ShapeType.Hexahedron:
                return "Гексаэдр"
            case ShapeType.Octahedron:
                return "Октаэдр"
            case ShapeType.Icosahedron:
                return "Икосаэдр"
            case ShapeType.Dodecahedron:
                return "Додекаэдр"
            case _:
                pass
        return "Неизвестная фигура"


class Shape:
    """Base class for all shapes"""

    def draw(self, canvas: tk.Canvas, projection: Projection, **kwargs) -> None:
        pass

    def transform(self, matrix: np.ndarray) -> None:
        pass

    def highlight(self, canvas: tk.Canvas, timeout: int = 200, r: int = 5) -> None:
        pass

    @property
    def center(self):
        pass


@dataclass
class Point(Shape):
    x: float
    y: float
    z: float

    def draw(self, canvas: tk.Canvas, projection: Projection, **kwargs):
        # if projection == Projection.Perspective:
        #     x = self.x / (1 - self.z / 1000)
        #     y = self.y / (1 - self.z / 1000)
        # else:
        #     x = self.x
        #     y = self.y
        # canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill="black")
        ...

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z

    # def in_rect(self, p1: "Point", p2: "Point") -> bool:
    #     maxx = max(p1.x, p2.x)
    #     minx = min(p1.x, p2.x)
    #     maxy = max(p1.y, p2.y)
    #     miny = min(p1.y, p2.y)
    #     return minx <= self.x <= maxx and miny <= self.y <= maxy

    def transform(self, matrix: np.ndarray):
        p = np.array([self.x, self.y, self.z, 1])
        p = np.dot(matrix, p)
        self.x = p[0]
        self.y = p[1]
        self.z = p[2]

    def highlight(self, canvas: tk.Canvas, timeout: int = 200, r: int = 5):
        highlight = canvas.create_oval(self.x - r, self.y - r, self.x + r,
                                       self.y + r, fill="red", outline="red")
        canvas.after(timeout, canvas.delete, highlight)

    @property
    def center(self) -> 'Point':
        return Point(self.x, self.y, self.z)


@dataclass
class Line(Shape):
    p1: Point
    p2: Point

    def draw(self, canvas: tk.Canvas, projection: Projection, **kwargs):
        ...

    # def in_rect(self, p1: Point, p2: Point) -> bool:
    #     """Проверка, что линия пересекает прямоугольник"""
    #     return all((self.p1.in_rect(p1, p2), self.p2.in_rect(p1, p2)))

    def transform(self, matrix: np.ndarray):
        self.p1.transform(matrix)
        self.p2.transform(matrix)

    def highlight(self, canvas: tk.Canvas, timeout: int = 200, r: int = 5):
        self.p1.highlight(canvas, timeout, r)
        self.p2.highlight(canvas, timeout, r)

    @property
    def center(self) -> 'Point':
        return Point((self.p1.x + self.p2.x) / 2, (self.p1.y + self.p2.y) / 2,
                     (self.p1.z + self.p2.z) / 2)


@dataclass
class Polygon(Shape):
    points: list[Point]

    def draw(self, canvas: tk.Canvas, projection: Projection, **kwargs):
        ...

    # def in_rect(self, p1: Point, p2: Point) -> bool:
    #     """Проверка, что полигон пересекает прямоугольник"""
    #     return all((point.in_rect(p1, p2) for point in self.points))

    def transform(self, matrix: np.ndarray):
        for point in self.points:
            point.transform(matrix)

    def highlight(self, canvas: tk.Canvas, timeout: int = 200, r: int = 5):
        for point in self.points:
            point.highlight(canvas, timeout, r)

    @property
    def center(self) -> 'Point':
        return Point(sum(point.x for point in self.points) / len(self.points),
                     sum(point.y for point in self.points) / len(self.points),
                     sum(point.z for point in self.points) / len(self.points))


@dataclass
class Polyhedron(Shape):
    polygons: list[Polygon]

    def draw(self, canvas: tk.Canvas, projection: Projection, **kwargs):
        ...

    # def in_rect(self, p1: Point, p2: Point) -> bool:
    #     """Проверка, что многогранник пересекает прямоугольник"""
    #     return all((polygon.in_rect(p1, p2) for polygon in self.polygons))

    def transform(self, matrix: np.ndarray):
        for polygon in self.polygons:
            polygon.transform(matrix)

    def highlight(self, canvas: tk.Canvas, timeout: int = 200, r: int = 5):
        for polygon in self.polygons:
            polygon.highlight(canvas, timeout, r)

    @property
    def center(self) -> 'Point':
        return Point(sum(polygon.center.x for polygon in self.polygons) /
                     len(self.polygons),
                     sum(polygon.center.y for polygon in self.polygons) /
                     len(self.polygons),
                     sum(polygon.center.z for polygon in self.polygons) /
                     len(self.polygons))

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

class App(tk.Tk):
    W: int = 1000
    H: int = 600
    shape: Shape = None
    shape_type_idx: int
    shape_type: ShapeType
    func_idx: int
    func: Function
    projection: Projection
    projection_idx: int

    def __init__(self):
        super().__init__()
        self.title("ManualCAD 3D")
        self.resizable(0, 0)
        self.geometry(f"{self.W}x{self.H}")
        self.shape_type_idx = 0
        self.shape_type = ShapeType(self.shape_type_idx)
        self.func_idx = 0
        self.func = Function(self.func_idx)
        self.projection_idx = 0
        self.projection = Projection(self.projection_idx)
        self.create_widgets()

    def create_widgets(self):
        self.canvas = tk.Canvas(self, width=self.W, height=self.H - 35)
        self.buttons = tk.Frame(self)
        self.translateb = tk.Button(self.buttons, text="Смещение", command=self.translate)
        self.rotateb = tk.Button(self.buttons, text="Поворот", command=self.rotate)
        self.scaleb = tk.Button(self.buttons, text="Масштаб", command=self.scale)
        self.shapesbox = tk.Listbox(self.buttons, selectmode=tk.SINGLE, height=1, width=15)
        self.scroll1 = tk.Scrollbar(self.buttons, orient=tk.VERTICAL, command=self._scroll1)
        self.funcsbox = tk.Listbox(self.buttons, selectmode=tk.SINGLE, height=1, width=40)
        self.scroll2 = tk.Scrollbar(self.buttons, orient=tk.VERTICAL, command=self._scroll2)
        self.projectionsbox = tk.Listbox(self.buttons, selectmode=tk.SINGLE, height=1, width=20)
        self.scroll3 = tk.Scrollbar(self.buttons, orient=tk.VERTICAL, command=self._scroll3)

        self.canvas.pack()
        self.canvas.config(cursor="cross")
        self.buttons.pack(fill=tk.X)
        self.translateb.pack(side=tk.LEFT, padx=5)
        self.rotateb.pack(side=tk.LEFT, padx=5)
        self.scaleb.pack(side=tk.LEFT, padx=5)

        self.scroll1.pack(side=tk.RIGHT, fill=tk.Y)
        self.shapesbox.pack(side=tk.RIGHT, padx=1)
        self.shapesbox.config(yscrollcommand=self.scroll1.set)

        self.scroll3.pack(side=tk.RIGHT, fill=tk.Y)
        self.projectionsbox.pack(side=tk.RIGHT, padx=1)
        self.projectionsbox.config(yscrollcommand=self.scroll3.set)

        self.scroll2.pack(side=tk.RIGHT, fill=tk.Y)
        self.funcsbox.pack(side=tk.RIGHT, padx=1)
        self.funcsbox.config(yscrollcommand=self.scroll2.set)

        self.shapesbox.delete(0, tk.END)
        self.shapesbox.insert(tk.END, *ShapeType)
        self.shapesbox.selection_set(0)

        self.funcsbox.delete(0, tk.END)
        self.funcsbox.insert(tk.END, *Function)
        self.funcsbox.selection_set(0)

        self.projectionsbox.delete(0, tk.END)
        self.projectionsbox.insert(tk.END, *Projection)
        self.projectionsbox.selection_set(0)

        self.canvas.bind("<Button-1>", self.l_click)
        self.canvas.bind("<Button-3>", self.r_click)
        self.bind("<Escape>", self.reset)

    def reset(self, *_):
        self.canvas.delete("all")
        self.shape = None

    def rotate(self):
        inp = sd.askfloat("Поворот", "Введите угол поворота в градусах")
        if inp is None:
            return
        phi = radians(inp)
        ...
        # TODO: реализовать поворот

    def scale(self):
        inp = sd.askstring("Масштаб", "Введите коэффициенты масштабирования по осям x, y, z:")
        if inp is None:
            return
        sx, sy, sz = map(float, inp.split(','))
        ...
        # TODO: сделать масштабирование

    def translate(self):
        inp = sd.askstring("Смещение", "Введите вектор смещения по осям x, y, z:")
        if inp is None:
            return
        dx, dy, dz = map(float, inp.split(','))
        ...
        # TODO: смещение

    def _scroll1(self, *args):
        d = int(args[1])
        self.shape_type_idx = (self.shape_type_idx + d) % len(ShapeType)
        self.shape_type = ShapeType(self.shape_type_idx)
        self.shapesbox.yview(*args)

    def _scroll2(self, *args):
        d = int(args[1])
        self.func_idx = (self.func_idx + d) % len(Function)
        self.func = Function(self.func_idx)
        self.funcsbox.yview(*args)

    def _scroll3(self, *args):
        d = int(args[1])
        self.projection_idx = (self.projection_idx + d) % len(Projection)
        self.projection = Projection(self.projection_idx)
        self.projectionsbox.yview(*args)
        # TODO: перерисовать фигуру с новой проекцией

    def __translate(self, x, y, z):
        ...

    def l_click(self, event: tk.Event):
        if self.shape is not None:
            return
        self.reset()
        match self.shape_type:
            case ShapeType.Tetrahedron:
                self.shape = Models.Tetrahedron()
                self.__translate(event.x, event.y, 0)
            case ShapeType.Octahedron:
                self.shape = Models.Octahedron()
                self.__translate(event.x, event.y, 0)
            # case ShapeType.Hexahedron:
            #     self.shape = Models.Hexahedron()
            #     self.__translate(event.x, event.y, 0)
            # case ShapeType.Icosahedron:
            #     self.shape = Models.Icosahedron()
            #     self.__translate(event.x, event.y, 0)
            # case ShapeType.Dodecahedron:
            #     self.shape = Models.Dodecahedron()
            #     self.__translate(event.x, event.y, 0)
        self.shape.draw(self.canvas, self.projection)

    def r_click(self, event: tk.Event):
        if self.shape is None:
            return
        match self.func:
            case Function.None_:
                return
            case Function.ReflectOverPlane:
                ...  # TODO: отражение относительно плоскости
            case Function.ScaleAboutCenter:
                ...  # TODO: масштабирование относительно центра
            case Function.RotateAroundAxis:
                ...  # TODO: поворот относительно оси
            case Function.RotateAroundLine:
                ...  # TODO: поворот относительно прямой

    def run(self):
        self.mainloop()


if __name__ == "__main__":
    app = App()
    app.run()

import tkinter as tk
from dataclasses import dataclass
from enum import Enum
from math import cos, pi, radians, sin
from tkinter import simpledialog as sd
from tkinter import messagebox as mb
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

    def __hash__(self) -> int:
        return hash((self.x, self.y, self.z))

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Point):
            return self.x == __o.x and self.y == __o.y and self.z == __o.z
        return False

    def draw(self, canvas: tk.Canvas, projection: Projection, **kwargs):
        if projection == Projection.Perspective:
            # print(App.dist)
            x = self.x / (1 - self.z / App.dist) + 450
            y = self.y / (1 - self.z / App.dist) + 250
            z = self.z
        elif projection == Projection.Axonometric:
            #print(App.phi, App.theta)
            phi = App.phi*(pi/180)
            theta = App.theta*(pi/180)
            iso = np.array([
                [cos(phi), cos(theta)*sin(phi), 0, 0],
                [0, cos(theta), 0, 0],
                [sin(phi), -sin(theta)*cos(phi), 0, 0],
                [0, 0, 0, 1]])
            coor = np.array([self.x, self.y, self.z, 1])
            res = np.matmul(coor, iso)
            x = res[0] + 600
            y = res[1] + 250
            z = res[2]
        else:
            x = self.x
            y = self.y
            z = self.z
        canvas.create_oval(x - 2, y - 2, x + 2, y + 2,
                           fill=kwargs.get("col", "white"))
        return x, y, z

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z

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
        p1X, p1Y, _ = self.p1.draw(canvas, projection)
        p2X, p2Y, _ = self.p2.draw(canvas, projection)
        canvas.create_line(p1X, p1Y, p2X, p2Y, fill=kwargs.get("col", "white"))

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
        ln = len(self.points)
        lines = [Line(self.points[i], self.points[(i + 1) % ln])
                 for i in range(ln)]
        for line in lines:
            line.draw(canvas, projection)

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
        for poly in self.polygons:
            poly.draw(canvas, projection)

    def transform(self, matrix: np.ndarray):
        points = {point for poly in self.polygons for point in poly.points}
        for point in points:
            point.transform(matrix)

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
    class Tetrahedron(Polyhedron):
        def __init__(self, size=100):
            t = Models.Hexahedron(size)
            p1 = t.polygons[0].points[1]
            p2 = t.polygons[0].points[3]
            p3 = t.polygons[2].points[2]
            p4 = t.polygons[1].points[3]
            polygons = [
                Polygon([p1, p2, p3]),
                Polygon([p1, p2, p4]),
                Polygon([p1, p3, p4]),
                Polygon([p2, p3, p4])
            ]
            super().__init__(polygons)

    class Hexahedron(Polyhedron):
        def __init__(self, size=100):
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

    class Octahedron(Polyhedron):
        def __init__(self, size=100):
            t = Models.Hexahedron(size)
            p1 = t.polygons[0].center
            p2 = t.polygons[1].center
            p3 = t.polygons[2].center
            p4 = t.polygons[3].center
            p5 = t.polygons[4].center
            p6 = t.polygons[5].center
            polygons = [
                Polygon([p1, p2, p3]),
                Polygon([p1, p3, p4]),
                Polygon([p1, p5, p4]),
                Polygon([p1, p2, p5]),
                Polygon([p2, p3, p6]),
                Polygon([p5, p4, p6]),
                Polygon([p3, p4, p6]),
                Polygon([p2, p5, p6])
            ]
            super().__init__(polygons)

    class Icosahedron(Polyhedron):
        def __init__(self, size=100):
            r = size
            _bottom = []
            for i in range(5):
                angle = 2 * pi * i / 5
                _bottom.append(Point(r * cos(angle), r * sin(angle), -r/2))

            _top = []
            for i in range(5):
                angle = 2 * pi * i / 5 + pi / 5
                _top.append(Point(r * cos(angle), r * sin(angle), r/2))

            top = Polygon(_top)
            bottom = Polygon(_bottom)

            polygons = []

            bottom_p = bottom.center
            top_p = top.center

            bottom_p.z -= r / 2
            top_p.z += r / 2

            for i in range(5):
                polygons.append(
                    Polygon([_bottom[i], bottom_p, _bottom[(i + 1) % 5]]))

            for i in range(5):
                polygons.append(
                    Polygon([_bottom[i], _top[i], _bottom[(i + 1) % 5]]))

            for i in range(5):
                polygons.append(
                    Polygon([_top[i], _top[(i + 1) % 5], _bottom[(i + 1) % 5]]))

            for i in range(5):
                polygons.append(Polygon([_top[i], top_p, _top[(i + 1) % 5]]))

            super().__init__(polygons)

    class Dodecahedron(Polyhedron):
        def __init__(self, size=100):
            t = Models.Icosahedron(size)
            points = []
            for polygon in t.polygons:
                points.append(polygon.center)
            p = points
            polygons = [
                Polygon([p[0], p[1], p[2], p[3], p[4]]),
                Polygon([p[0], p[4], p[9], p[14], p[5]]),
                Polygon([p[0], p[5], p[10], p[6], p[1]]),
                Polygon([p[1], p[2], p[7], p[11], p[6]]),
                Polygon([p[2], p[3], p[8], p[12], p[7]]),
                Polygon([p[3], p[8], p[13], p[9], p[4]]),
                Polygon([p[5], p[14], p[19], p[15], p[10]]),
                Polygon([p[6], p[11], p[16], p[15], p[10]]),
                Polygon([p[7], p[12], p[17], p[16], p[11]]),
                Polygon([p[8], p[13], p[18], p[17], p[12]]),
                Polygon([p[9], p[14], p[19], p[18], p[13]]),
                Polygon([p[15], p[16], p[17], p[18], p[19]])
            ]
            super().__init__(polygons)


class App(tk.Tk):
    W: int = 1200
    H: int = 600
    shape: Shape = None
    shape_type_idx: int
    shape_type: ShapeType
    func_idx: int
    func: Function
    projection: Projection
    projection_idx: int
    phi: int = 60
    theta: int = 45
    dist: int = 1000

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
        self.canvas = tk.Canvas(self, width=self.W, height=self.H - 75, bg="#393939")
        self.buttons = tk.Frame(self)
        self.translateb = tk.Button(
            self.buttons, text="Смещение", command=self.translate)
        self.rotateb = tk.Button(
            self.buttons, text="Поворот", command=self.rotate)
        self.scaleb = tk.Button(
            self.buttons, text="Масштаб", command=self.scale)
        self.phis = tk.Scale(self.buttons, from_=0, to=360,
                             orient=tk.HORIZONTAL, label="φ", command=self._phi_changed)
        self.thetas = tk.Scale(self.buttons, from_=0, to=360, orient=tk.HORIZONTAL,
                               label="θ", command=self._theta_changed)
        self.dists = tk.Scale(self.buttons, from_=1, to=self.W, orient=tk.HORIZONTAL,
                              label="Расстояние", command=self._dist_changed)

        self._axis = tk.BooleanVar()
        self.axis = tk.Checkbutton(self.buttons, text="Оси", var=self._axis, command=self.reset)

        self._grid = tk.BooleanVar()
        self.grid = tk.Checkbutton(self.buttons, text="Сетка", var=self._grid, command=self.reset)

        self.shapesbox = tk.Listbox(
            self.buttons, selectmode=tk.SINGLE, height=1, width=15)
        self.scroll1 = tk.Scrollbar(
            self.buttons, orient=tk.VERTICAL, command=self._scroll1)
        self.funcsbox = tk.Listbox(
            self.buttons, selectmode=tk.SINGLE, height=1, width=40)
        self.scroll2 = tk.Scrollbar(
            self.buttons, orient=tk.VERTICAL, command=self._scroll2)
        self.projectionsbox = tk.Listbox(
            self.buttons, selectmode=tk.SINGLE, height=1, width=20)
        self.scroll3 = tk.Scrollbar(
            self.buttons, orient=tk.VERTICAL, command=self._scroll3)

        self.canvas.pack()
        self.canvas.config(cursor="cross")
        self.buttons.pack(fill=tk.X)
        self.translateb.pack(side=tk.LEFT, padx=5)
        self.rotateb.pack(side=tk.LEFT, padx=5)
        self.scaleb.pack(side=tk.LEFT, padx=5)
        self.phis.pack(side=tk.LEFT, padx=5)
        self.thetas.pack(side=tk.LEFT, padx=5)
        self.dists.pack(side=tk.LEFT, padx=5)
        self.axis.pack(side=tk.LEFT, padx=5)
        self.grid.pack(side=tk.LEFT, padx=5)

        self.phis.set(self.phi)
        self.thetas.set(self.theta)
        self.dists.set(self.dist)

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

    def reset(self, *_, del_shape=True):
        self.canvas.delete("all")
        if del_shape:
            self.shape = None
        if self._axis.get():
            ln = 100
            Line(Point(-ln, 0, 0), Point(ln, 0, 0)).draw(self.canvas, self.projection, col='red') # x axis
            Line(Point(0, -ln, 0), Point(0, ln, 0)).draw(self.canvas, self.projection, col='green') # y axis
            Line(Point(0, 0, -ln), Point(0, 0, ln)).draw(self.canvas, self.projection, col='blue') # z axis
        if self._grid.get():
            for i in range(-self.W, self.W, 50):
                Line(Point(i, 0, -self.H), Point(i, 0, self.H)).draw(self.canvas, self.projection, col='gray')
            for i in range(-self.H, self.H, 50):
                Line(Point(-self.W, 0, i), Point(self.W, 0, i)).draw(self.canvas, self.projection, col='gray')


    def rotate(self):
        inp = sd.askstring(
            "Поворот", "Введите угол поворота в градусах по x, y, z:")
        if inp is None:
            return
        phi, theta, psi = map(radians, map(float, inp.split(', ')))
        m, n, k = self.shape.center

        mat_back = np.array([
            [1, 0, 0, -m],
            [0, 1, 0, -n],
            [0, 0, 1, -k],
            [0, 0, 0, 1]
        ])

        mat_x = np.array([
            [1, 0, 0, 0],
            [0, cos(phi), sin(phi), 0],
            [0, -sin(phi), cos(phi), 0],
            [0, 0, 0, 1]])

        mat_y = np.array([
            [cos(theta), 0, -sin(theta), 0],
            [0, 1, 0, 0],
            [sin(theta), 0, cos(theta), 0],
            [0, 0, 0, 1]])

        mat_z = np.array([
            [cos(psi), -sin(psi), 0, 0],
            [sin(psi), cos(psi), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]])

        mat_fwd = np.array([
            [1, 0, 0, m],
            [0, 1, 0, n],
            [0, 0, 1, k],
            [0, 0, 0, 1]
        ])

        mat = mat_fwd @ mat_x @ mat_y @ mat_z @ mat_back
        self.shape.transform(mat)
        self.reset(del_shape=False)
        self.shape.draw(self.canvas, self.projection)

    def scale(self):
        inp = sd.askstring(
            "Масштаб", "Введите коэффициенты масштабирования по осям x, y, z:")
        if inp is None:
            return
        sx, sy, sz = map(float, inp.split(','))
        mat = np.array([
            [sx, 0, 0, 0],
            [0, sy, 0, 0],
            [0, 0, sz, 0],
            [0, 0, 0, 1]])
        self.shape.transform(mat)
        self.reset(del_shape=False)
        self.shape.draw(self.canvas, self.projection)

    def translate(self):
        inp = sd.askstring(
            "Смещение", "Введите вектор смещения по осям x, y, z:")
        if inp is None:
            return
        dx, dy, dz = map(float, inp.split(','))
        mat = np.array([
            [1, 0, 0, dx],
            [0, 1, 0, dy],
            [0, 0, 1, dz],
            [0, 0, 0, 1]])
        self.shape.transform(mat)
        self.reset(del_shape=False)
        self.shape.draw(self.canvas, self.projection)

    def _scroll1(self, *args):
        try:
            d = int(args[1])
        except ValueError:
            return
        if 0 <= self.shape_type_idx + d < len(ShapeType):
            self.shape_type_idx += d
            self.shape_type = ShapeType(self.shape_type_idx)
            self.shape = None
            self.shapesbox.yview(*args)

    def _scroll2(self, *args):
        try:
            d = int(args[1])
        except ValueError:
            return
        if 0 <= self.func_idx + d < len(Function):
            self.func_idx += d
            self.func = Function(self.func_idx)
            self.funcsbox.yview(*args)

    def _scroll3(self, *args):
        try:
            d = int(args[1])
        except ValueError:
            return
        if 0 <= self.projection_idx + d < len(Projection):
            self.projection_idx += d
            self.projection = Projection(self.projection_idx)
            self.projectionsbox.yview(*args)
            self.reset(del_shape=False)
            if self.shape is not None:
                self.shape.draw(self.canvas, self.projection)

    def _dist_changed(self, *_):
        App.dist = self.dists.get()
        self.reset(del_shape=False)
        if self.shape is not None:
            self.shape.draw(self.canvas, self.projection)

    def _phi_changed(self, *_):
        App.phi = self.phis.get()
        self.reset(del_shape=False)
        if self.shape is not None:
            self.shape.draw(self.canvas, self.projection)

    def _theta_changed(self, *_):
        App.theta = self.thetas.get()
        self.reset(del_shape=False)
        if self.shape is not None:
            self.shape.draw(self.canvas, self.projection)

    def l_click(self, _: tk.Event):
        self.reset()
        match self.shape_type:
            case ShapeType.Tetrahedron:
                self.shape = Models.Tetrahedron()
            case ShapeType.Octahedron:
                self.shape = Models.Octahedron()
            case ShapeType.Hexahedron:
                self.shape = Models.Hexahedron()
            case ShapeType.Icosahedron:
                self.shape = Models.Icosahedron()
            case ShapeType.Dodecahedron:
                self.shape = Models.Dodecahedron()

        self.shape.draw(self.canvas, self.projection)

    def r_click(self, _: tk.Event):
        if self.shape is None:
            return
        match self.func:
            case Function.None_:
                return
            case Function.ReflectOverPlane:
                # https://www.gatevidyalay.com/3d-reflection-in-computer-graphics-definition-examples/
                inp = sd.askstring(
                    "Отражение", "Введите плоскость отражения (н-р: XY):")
                if inp is None:
                    return
                plane = ''.join(sorted(inp.strip().upper()))

                mat_xy = np.array([
                    [1, 0, 0, 0],
                    [0, 1, 0, 0],
                    [0, 0, -1, 0],
                    [0, 0, 0, 1]])

                mat_yz = np.array([
                    [-1, 0, 0, 0],
                    [0, 1, 0, 0],
                    [0, 0, 1, 0],
                    [0, 0, 0, 1]])

                mat_xz = np.array([
                    [1, 0, 0, 0],
                    [0, -1, 0, 0],
                    [0, 0, 1, 0],
                    [0, 0, 0, 1]])

                match plane:
                    case 'XY':
                        self.shape.transform(mat_xy)
                    case 'YZ':
                        self.shape.transform(mat_yz)
                    case 'XZ':
                        self.shape.transform(mat_xz)
                    case _:
                        mb.showerror("Ошибка", "Неверно указана плоскость")
                self.reset(del_shape=False)
                self.shape.draw(self.canvas, self.projection)

            case Function.ScaleAboutCenter:
                inp = sd.askstring("Масштаб", "Введите коэффициенты масштабирования по осям x, y, z:")
                if inp is None:
                    return
                sx, sy, sz = map(float, inp.split(','))
                m, n, k = self.shape.center
                mat = np.array([
                    [sx, 0, 0, -m*sx+m],
                    [0, sy, 0, -n*sy+n],
                    [0, 0, sz, -k*sz+k],
                    [0, 0, 0, 1]])
                self.shape.transform(mat)
                self.reset(del_shape=False)
                self.shape.draw(self.canvas, self.projection)

            case Function.RotateAroundAxis:
                m, n, k = self.shape.center
                inp = sd.askstring("Поворот", "Введите ось вращения (н-р: X), угол в градусах:")
                if inp is None:
                    return
                try:
                    axis, phi = inp.split(',')
                    axis = axis.strip().upper()
                    phi = radians(float(phi))
                except ValueError:
                    mb.showerror("Ошибка", "Неверно указаны ось и угол")
                    return

                mat_back = np.array([
                    [1, 0, 0, -m],
                    [0, 1, 0, -n],
                    [0, 0, 1, -k],
                    [0, 0, 0, 1]])
                self.shape.transform(mat_back)

                match axis:
                    case 'X':
                        mat = np.array([
                            [1, 0, 0, 0],
                            [0, cos(phi), -sin(phi), 0],
                            [0, sin(phi), cos(phi), 0],
                            [0, 0, 0, 1]])  # вращение вокруг оси x
                    case 'Z':
                        mat = np.array([
                            [cos(phi), -sin(phi), 0, 0],
                            [sin(phi), cos(phi), 0, 0],
                            [0, 0, 1, 0],
                            [0, 0, 0, 1]])  # вращение вокруг оси z
                    case 'Y':
                        mat = np.array([
                            [cos(phi), 0, sin(phi), 0],
                            [0, 1, 0, 0],
                            [-sin(phi), 0, cos(phi), 0],
                            [0, 0, 0, 1]])  # вращение вокруг оси y

                self.shape.transform(mat)
                mat_fwd = np.array([
                    [1, 0, 0, m],
                    [0, 1, 0, n],
                    [0, 0, 1, k],
                    [0, 0, 0, 1]])
                self.shape.transform(mat_fwd)
                self.reset(del_shape=False)
                self.shape.draw(self.canvas, self.projection)
            case Function.RotateAroundLine:
                inp = sd.askstring("Поворот", "Введите координаты начала и конца линии в формате x1, y1, z1, x2, y2, z2, угол в градусах:")
                if inp is None:
                    return
                try:
                    a, b, c, x, y, z, phi = map(float, inp.split(','))
                    phi = radians(phi)
                except ValueError:
                    mb.showerror("Ошибка", "Неверно указаны координаты начала и конца линии")
                    return

                d = np.linalg.norm([x, y, z])
                x = x / d
                y = y / d
                z = z / d

                mat_back = np.array([
                    [1, 0, 0, -a],
                    [0, 1, 0, -b],
                    [0, 0, 1, -c],
                    [0, 0, 0, 1]])

                mat_rot = np.array([
                    [cos(phi) + (1 - cos(phi)) * x ** 2, (1 - cos(phi)) * x * y - sin(phi)*z, (1 - cos(phi)) * x * z + sin(phi)*y, 0],
                    [(1 - cos(phi)) * x * y + sin(phi)*z, cos(phi) + (1 - cos(phi)) * y ** 2, (1 - cos(phi)) * y * z - sin(phi)*x, 0],
                    [(1 - cos(phi)) * z * x - sin(phi)*y, (1 - cos(phi)) * z * y + sin(phi)*x, cos(phi) + (1 - cos(phi)) * z ** 2, 0],
                    [0, 0, 0, 1]
                ])  # 0, 0, 150, 120, 300, -50, 90

                mat_fwd = np.array([
                    [1, 0, 0, a],
                    [0, 1, 0, b],
                    [0, 0, 1, c],
                    [0, 0, 0, 1]])

                self.shape.transform(mat_back)
                self.shape.transform(mat_rot)
                self.shape.transform(mat_fwd)
                self.reset(del_shape=False)
                self.shape.draw(self.canvas, self.projection)

    def run(self):
        self.mainloop()


if __name__ == "__main__":
    app = App()
    app.run()

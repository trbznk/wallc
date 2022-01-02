import random

from dataclasses import dataclass
from typing import Optional, Sequence
from PIL import Image, ImageDraw


def mid_to_bbox(mx, my):
    k = 10
    return [
        (mx-k, my-k),
        (mx+k, my+k)
    ]


@dataclass
class Wall:
    width: float
    height: float


@dataclass
class Suspension:
    distance: float
    padding: float


@dataclass
class Position:
    x: float
    y: float


@dataclass
class Picture:
    width: float
    height: float
    suspension: Suspension
    mid: Optional[Position] = None

    @property
    def top_left(self):
        return Position(
            self.mid.x-self.width/2,
            self.mid.y-self.height/2
        )

    @property
    def top_right(self):
        return Position(
            self.mid.x+self.width/2,
            self.mid.y-self.height/2
        )

    @property
    def bottom_right(self):
        return Position(
            self.mid.x+self.width/2,
            self.mid.y+self.height/2
        )

    @property
    def bottom_left(self):
        return Position(
            self.mid.x-self.width/2,
            self.mid.y+self.height/2
        )

    def suspension_positions(self):
        mx0 = self.mid.x-self.suspension.distance/2
        my0 = self.top_left.y+self.suspension.padding

        mx1 = self.mid.x+self.suspension.distance/2
        my1 = self.top_left.y+self.suspension.padding

        return [
            Position(mx0, my0),
            Position(mx1, my1)
        ]

    @staticmethod
    def random():
        width = random.randrange(400, 1000)
        height = random.randrange(400, 1000)

        distance = random.randrange(width-100, width-50)
        padding = random.randrange(50, height//2)
        suspension = Suspension(distance, padding)
        return Picture(
            width,
            height,
            suspension=suspension
        )


class Layout:
    def __init__(self, wall=None, pictures=None) -> None:
        self.wall: Wall = wall
        self.pictures: Sequence[Picture] = pictures

    @staticmethod
    def example():
        wall = Wall(4000.0, 2000.0)
        pictures = [
            Picture.random(),
            Picture.random(),
            Picture.random()
        ]
        return Layout(wall, pictures)

    def layout(self):
        width_per_part = self.wall.width/(len(self.pictures)+1)
        for i, picture in enumerate(self.pictures):
            x = width_per_part*(i+1)
            y = self.wall.height/3
            picture.mid = Position(x, y)

    def draw_wall(self):
        # Wall
        x0, y0 = 0, 0
        x1, y1 = self.wall.width, self.wall.height
        xy = [x0, y0, x1, y1]
        self.draw.rectangle(xy, outline=(0, 0, 0), width=5)

    def draw_frame(self, picture):
        xy = [
            (picture.top_left.x, picture.top_left.y),
            (picture.bottom_right.x, picture.bottom_right.y)
        ]
        self.draw.rectangle(xy, width=2, outline="black")

    def draw_diagonals(self, picture):
        xy = [
            (picture.top_left.x, picture.top_left.y),
            (picture.bottom_right.x, picture.bottom_right.y)
        ]
        self.draw.line(xy, width=2, fill=0)

        xy = [
            (picture.top_right.x, picture.top_right.y),
            (picture.bottom_left.x, picture.bottom_left.y)
        ]
        self.draw.line(xy, width=2, fill="black")

    def draw_suspension(self, picture):
        s1, s2 = picture.suspension_positions()
        self.draw.ellipse(mid_to_bbox(s1.x, s1.y), outline="black")
        self.draw.ellipse(mid_to_bbox(s2.x, s1.y), outline="black")

    def draw_vline(self, picture):
        xy = [
            (picture.mid.x, 0),
            (picture.mid.x, picture.suspension.padding+picture.top_left.y)
        ]
        self.draw.line(xy, fill="blue", width=2)

        # TODOO: add dynamic font scaling
        # TODO: implement anchor and align functionality
        # TODO: add unicode arrows
        text = f"<{picture.mid.x}"
        x0, y0 = picture.mid.x+5, 5
        self.draw.text((x0, y0), text, fill="blue")

    def draw_hline(self, picture):
        s1, s2 = picture.suspension_positions()
        xy = [
            (s1.x, s1.y),
            (s2.x, s2.y)
        ]
        self.draw.line(xy, width=2, fill="blue")

        text = f"^{round(s1.y, 2)}"
        x0 = s1.x+picture.suspension.distance/2+5
        y0 = s1.y-15
        self.draw.text((x0, y0), text, fill="blue")

        x0 = s1.x+picture.suspension.distance/2-15
        y0 = s1.y+5
        text = f"<{picture.suspension.distance}>"
        self.draw.text((x0, y0), text, fill="blue")

        x0 = s1.x+10
        y0 = s1.y+10
        text = f"{picture.suspension.distance/2}>"
        self.draw.text((x0, y0), text, fill="blue")
        x0 = s2.x-60
        y0 = s2.y+10
        text = f"<{picture.suspension.distance/2}"
        self.draw.text((x0, y0), text, fill="blue")

    def draw(self):
        size = (int(self.wall.width), int(self.wall.height))
        im = Image.new("RGB", size, color=(255, 255, 255))
        self.draw = ImageDraw.Draw(im)

        self.draw_wall()
        for picture in self.pictures:
            self.draw_frame(picture)
            self.draw_diagonals(picture)
            self.draw_suspension(picture)
            self.draw_vline(picture)
            self.draw_hline(picture)

        padding = 100
        size = tuple(e+padding*2 for e in size)
        result = Image.new("RGB", size, color=(255, 255, 255))
        result.paste(im, (padding, padding))
        result.show()


if __name__ == "__main__":
    layout = Layout.example()
    layout.layout()
    layout.draw()

import random
import time
import sys
import math


class Particle:
    def __init__(self, x, y, vx, vy, color, life, char="*"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.life = life
        self.max_life = life
        self.char = char

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.05
        self.vx *= 0.99
        self.life -= 1

    def is_alive(self):
        return self.life > 0


class Firework:
    COLORS = [
        "\033[91m",  # Red
        "\033[92m",  # Green
        "\033[93m",  # Yellow
        "\033[94m",  # Blue
        "\033[95m",  # Magenta
        "\033[96m",  # Cyan
        "\033[97m",  # White
    ]

    def __init__(self, width, height):
        self.x = random.randint(5, width - 5)
        self.y = height
        self.target_y = random.randint(int(height * 0.2), int(height * 0.5))
        self.vy = -1.5
        self.color = random.choice(self.COLORS)
        self.exploded = False
        self.particles = []
        self.width = width
        self.height = height
        self.trail = []

    def update(self):
        if not self.exploded:
            self.trail.append((self.x, self.y))
            if len(self.trail) > 5:
                self.trail.pop(0)
            self.y += self.vy
            if self.y <= self.target_y:
                self.explode()
        else:
            for p in self.particles:
                p.update()
            self.particles = [p for p in self.particles if p.is_alive()]

    def get_text_points(self, text):
        font = {
            "k": ["  X  ", " X   ", "XX   ", " X   ", "  X  "],
            "e": ["XXXX ", "X    ", "XXX  ", "X    ", "XXXX "],
            "n": ["X   X", "XX  X", "X X X", "X  XX", "X   X"],
            "t": ["XXXXX", "  X  ", "  X  ", "  X  ", "  X  "],
            "r": ["XXXX ", "X   X", "XXXX ", "X X  ", "X  X "],
            "a": [" XXX ", "X   X", "XXXXX", "X   X", "X   X"],
        }
        points = []
        scale = 0.5
        text_width = sum(len(font.get(c, font["a"])[0]) for c in text.lower()) - 1
        offset_x = -text_width * scale / 2
        offset_y = -2.5

        curr_x = offset_x
        for char in text.lower():
            if char not in font:
                curr_x += 4 * scale
                continue
            char_rows = font[char]
            for row_idx, row in enumerate(char_rows):
                for col_idx, cell in enumerate(row):
                    if cell == "X":
                        points.append(
                            (curr_x + col_idx * scale, offset_y + row_idx * scale)
                        )
            curr_x += (len(char_rows[0])) * scale
        return points

    def explode(self):
        self.exploded = True
        text_points = self.get_text_points("Kentra")
        for px, py in text_points:
            vx = px * 0.15
            vy = py * 0.15
            life = random.randint(40, 60)
            char = random.choice(["*", ".", "+", "o"])
            self.particles.append(
                Particle(self.x, self.y, vx, vy, self.color, life, char)
            )
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.3, 0.8)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            life = random.randint(15, 30)
            char = random.choice([".", "+"])
            self.particles.append(
                Particle(self.x, self.y, vx, vy, self.color, life, char)
            )

    def is_alive(self):
        return not self.exploded or len(self.particles) > 0

    def draw(self, buffer, width, height):
        if not self.exploded:
            for i, (tx, ty) in enumerate(self.trail):
                if 0 <= int(ty) < height and 0 <= int(tx) < width:
                    intensity = int((i / len(self.trail)) * 255)
                    buffer[int(ty)][int(tx)] = self.color + "|" + "\033[0m"
            if 0 <= int(self.y) < height and 0 <= int(self.x) < width:
                buffer[int(self.y)][int(self.x)] = self.color + "*" + "\033[0m"
        else:
            for p in self.particles:
                px, py = int(p.x), int(p.y)
                if 0 <= py < height and 0 <= px < width:
                    alpha = p.life / p.max_life
                    if alpha > 0.5:
                        buffer[py][px] = p.color + p.char + "\033[0m"
                    else:
                        buffer[py][px] = "\033[90m" + p.char + "\033[0m"


def main():
    print("\033[2J\033[?25l")

    try:
        import shutil

        width = shutil.get_terminal_size().columns
        height = shutil.get_terminal_size().lines
    except:
        width = 80
        height = 24

    fireworks = []
    frame = 0

    try:
        while True:
            buffer = [[" " for _ in range(width)] for _ in range(height)]

            if frame % 15 == 0:
                fireworks.append(Firework(width, height))

            for fw in fireworks:
                fw.update()
                fw.draw(buffer, width, height)

            fireworks = [fw for fw in fireworks if fw.is_alive()]

            print("\033[H", end="")
            for row in buffer:
                print("".join(row))

            frame += 1
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\033[?25h\033[0m\033[2J\033[H")
        print("Fireworks show ended!")


if __name__ == "__main__":
    main()

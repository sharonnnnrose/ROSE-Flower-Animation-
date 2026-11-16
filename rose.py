
import pygame
import math
import random

pygame.init()

# ---------------- WINDOW ----------------

WIDTH, HEIGHT = 1000, 750
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ROSE - A Magical Bloom")

clock = pygame.time.Clock()

CENTER_X = WIDTH // 2
GROUND_Y = HEIGHT - 65

# ---------------- COLORS ----------------

BLACK = (5, 5, 18)
DARK_GREEN = (8, 75, 35)
GREEN = (35, 180, 65)
LIGHT_GREEN = (120, 255, 115)

# ---------------- HELPERS ----------------

def smooth(value):
    value = max(0, min(1, value))
    return value * value * (3 - 2 * value)


def interpolate(a, b, progress):
    return a + (b - a) * progress


def rotate_point(x, y, angle):
    rad = math.radians(angle)
    return (
        x * math.cos(rad) - y * math.sin(rad),
        x * math.sin(rad) + y * math.cos(rad)
    )


def bezier(p0, p1, p2, p3, steps=18):
    points = []

    for i in range(steps + 1):
        t = i / steps
        u = 1 - t

        x = (
            u**3 * p0[0]
            + 3 * u**2 * t * p1[0]
            + 3 * u * t**2 * p2[0]
            + t**3 * p3[0]
        )

        y = (
            u**3 * p0[1]
            + 3 * u**2 * t * p1[1]
            + 3 * u * t**2 * p2[1]
            + t**3 * p3[1]
        )

        points.append((x, y))

    return points


# ---------------- STARS ----------------

stars = []

for _ in range(190):
    stars.append({
        "x": random.randint(0, WIDTH),
        "y": random.randint(0, HEIGHT),
        "size": random.choice([1, 2, 2, 3]),
        "phase": random.random() * math.tau,
        "color": random.choice([
            (255, 255, 255),
            (90, 160, 255),
            (255, 190, 100)
        ])
    })


def draw_stars(t):
    for star in stars:
        brightness = (
            0.55 + 0.45 * math.sin(t * 2 + star["phase"])
        )

        color = tuple(
            int(c * brightness) for c in star["color"]
        )

        pygame.draw.circle(
            screen,
            color,
            (star["x"], star["y"]),
            star["size"]
        )


# ---------------- FLOATING PARTICLES ----------------

particles = []

for _ in range(100):
    particles.append({
        "x": random.randint(0, WIDTH),
        "y": random.randint(0, HEIGHT),
        "speed": random.uniform(8, 30),
        "size": random.choice([1, 2, 3]),
        "phase": random.random() * math.tau
    })


def draw_particles(t):
    for p in particles:
        x = p["x"] + math.sin(t + p["phase"]) * 12
        y = (p["y"] - t * p["speed"]) % HEIGHT

        pygame.draw.circle(
            screen,
            (255, 195, 95),
            (int(x), int(y)),
            p["size"]
        )


# ---------------- GLOW ----------------

def draw_glow(x, y, radius, color, strength=1):
    glow_surface = pygame.Surface(
        (WIDTH, HEIGHT), pygame.SRCALPHA
    )

    for i in range(8, 0, -1):
        r = int(radius * i / 8)
        alpha = int(3 * strength * (9 - i))

        pygame.draw.circle(
            glow_surface,
            (*color, alpha),
            (int(x), int(y)),
            r
        )

    screen.blit(glow_surface, (0, 0))


# ---------------- STEM ----------------

def get_stem_points(progress, t):
    points = []

    sway = math.sin(t * 1.4) * 8

    for i in range(50):
        p = i / 49

        x = CENTER_X + math.sin(p * 1.3) * 18 * progress
        x += sway * p * progress

        y = GROUND_Y - p * 340 * progress

        points.append((int(x), int(y)))

    return points


def draw_stem(progress, t):
    if progress <= 0:
        return

    points = get_stem_points(progress, t)

    if len(points) > 1:
        pygame.draw.lines(
            screen, DARK_GREEN, False, points, 13
        )

        pygame.draw.lines(
            screen, GREEN, False, points, 7
        )

        pygame.draw.lines(
            screen, LIGHT_GREEN, False, points, 2
        )


# ---------------- LEAVES ----------------

def draw_leaf(x, y, direction, progress, t):
    if progress <= 0:
        return

    length = 105 * progress
    width = 42 * progress

    sway = math.sin(t * 1.8 + direction) * 7

    points = []

    for i in range(25):
        p = i / 24

        px = length * p

        py = math.sin(p * math.pi) * width
        py += math.sin(p * math.pi * 2) * 5

        points.append((
            x + direction * px + sway * p,
            y - py
        ))

    for i in range(24, -1, -1):
        p = i / 24

        px = length * p

        py = -math.sin(p * math.pi) * width
        py += math.sin(p * math.pi * 2) * 5

        points.append((
            x + direction * px + sway * p,
            y - py
        ))

    points = [(int(a), int(b)) for a, b in points]

    pygame.draw.polygon(screen, (15, 125, 45), points)
    pygame.draw.polygon(screen, (55, 205, 75), points, 3)

    vein_end = (
        int(x + direction * length),
        int(y)
    )

    pygame.draw.line(
        screen,
        (165, 255, 125),
        (int(x), int(y)),
        vein_end,
        2
    )


# ---------------- ROSE PETALS ----------------

def draw_petal(surface, cx, cy, length, width,
               angle, color, highlight=None, scale=1):

    length *= scale
    width *= scale

    # Petal shape
    left = bezier(
        (0, 0),
        (-width * 0.75, -length * 0.22),
        (-width * 0.65, -length * 0.85),
        (0, -length)
    )

    right = bezier(
        (0, -length),
        (width * 0.65, -length * 0.85),
        (width * 0.75, -length * 0.22),
        (0, 0)
    )

    shape = left + right

    rotated = []

    for px, py in shape:
        rx, ry = rotate_point(px, py, angle)

        rotated.append((
            int(cx + rx),
            int(cy + ry)
        ))

    pygame.draw.polygon(surface, color, rotated)

    # Petal outline
    pygame.draw.lines(
        surface,
        tuple(min(255, c + 30) for c in color),
        True,
        rotated,
        2
    )

    # Soft central highlight
    if highlight:
        line_points = bezier(
            (0, -length * 0.12),
            (-width * 0.15, -length * 0.40),
            (width * 0.12, -length * 0.75),
            (0, -length * 0.88),
            12
        )

        highlight_points = []

        for px, py in line_points:
            rx, ry = rotate_point(px, py, angle)

            highlight_points.append((
                int(cx + rx),
                int(cy + ry)
            ))

        pygame.draw.lines(
            surface,
            highlight,
            False,
            highlight_points,
            2
        )


def draw_rose(cx, cy, bloom, t):
    if bloom <= 0:
        return

    flower = pygame.Surface(
        (WIDTH, HEIGHT), pygame.SRCALPHA
    )

    # Bloom slowly expands
    scale = 0.15 + bloom * 0.85

    # Outer petals
    outer_colors = [
        (130, 8, 35),
        (165, 12, 48),
        (190, 18, 60),
        (155, 10, 42)
    ]

    for i in range(9):
        angle = i * 40 + 10

        draw_petal(
            flower,
            cx,
            cy,
            125,
            48,
            angle,
            outer_colors[i % len(outer_colors)],
            (235, 85, 110),
            scale
        )

    # Middle petals
    middle_colors = [
        (190, 15, 55),
        (220, 25, 75),
        (175, 12, 55),
        (235, 40, 85)
    ]

    for i in range(7):
        angle = i * 51 + 20

        draw_petal(
            flower,
            cx,
            cy,
            92,
            39,
            angle,
            middle_colors[i % len(middle_colors)],
            (255, 115, 145),
            scale
        )

    # Inner petals
    inner_colors = [
        (220, 30, 75),
        (245, 55, 105),
        (195, 15, 65),
        (255, 85, 125)
    ]

    for i in range(6):
        angle = i * 60 + 35

        draw_petal(
            flower,
            cx,
            cy,
            61,
            30,
            angle,
            inner_colors[i % len(inner_colors)],
            (255, 155, 175),
            scale
        )

    # Curled central petals
    for i in range(5):
        angle = i * 72 + 15

        draw_petal(
            flower,
            cx,
            cy,
            38,
            21,
            angle,
            (235, 55, 100),
            (255, 175, 185),
            scale
        )

    # Rose heart
    center_radius = int(13 * scale)

    pygame.draw.circle(
        flower,
        (155, 12, 55),
        (int(cx), int(cy)),
        center_radius
    )

    pygame.draw.circle(
        flower,
        (255, 110, 145),
        (int(cx - 3 * scale), int(cy - 4 * scale)),
        max(2, int(5 * scale))
    )

    screen.blit(flower, (0, 0))


# ---------------- BUD ----------------

def draw_bud(cx, cy, progress):
    if progress <= 0:
        return

    scale = 1 + progress * 0.4

    # Sepals
    pygame.draw.polygon(
        screen,
        (20, 120, 45),
        [
            (int(cx - 35 * scale), int(cy + 15)),
            (int(cx), int(cy + 55)),
            (int(cx + 35 * scale), int(cy + 15)),
            (int(cx), int(cy + 5))
        ]
    )

    # Bud
    pygame.draw.ellipse(
        screen,
        (120, 8, 40),
        (
            int(cx - 35 * scale),
            int(cy - 55 * scale),
            int(70 * scale),
            int(85 * scale)
        )
    )

    pygame.draw.ellipse(
        screen,
        (210, 25, 65),
        (
            int(cx - 28 * scale),
            int(cy - 48 * scale),
            int(56 * scale),
            int(70 * scale)
        )
    )

    pygame.draw.arc(
        screen,
        (255, 120, 155),
        (
            int(cx - 25 * scale),
            int(cy - 48 * scale),
            int(50 * scale),
            int(65 * scale)
        ),
        0.5,
        2.5,
        3
    )


# ---------------- GOLDEN POLLEN ----------------

pollen = []


def create_pollen(cx, cy):
    for _ in range(3):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(20, 95)

        pollen.append({
            "x": cx,
            "y": cy,
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,
            "life": random.uniform(1.2, 2.8),
            "size": random.randint(2, 4)
        })


def update_pollen(dt):
    for p in pollen[:]:
        p["x"] += p["vx"] * dt
        p["y"] += p["vy"] * dt

        p["vy"] -= 12 * dt
        p["life"] -= dt

        if p["life"] <= 0:
            pollen.remove(p)


def draw_pollen():
    for p in pollen:
        alpha = max(0, min(255, int(p["life"] * 120)))

        particle_surface = pygame.Surface(
            (12, 12), pygame.SRCALPHA
        )

        pygame.draw.circle(
            particle_surface,
            (255, 205, 90, alpha),
            (6, 6),
            p["size"]
        )

        screen.blit(
            particle_surface,
            (int(p["x"] - 6), int(p["y"] - 6))
        )


# ---------------- MAIN ANIMATION ----------------

start_time = pygame.time.get_ticks()

running = True
last_pollen = 0

while running:
    dt = clock.tick(FPS) / 1000
    t = (pygame.time.get_ticks() - start_time) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                start_time = pygame.time.get_ticks()
                pollen.clear()
                last_pollen = 0

    screen.fill(BLACK)

    # Background
    draw_stars(t)
    draw_particles(t)

    # Timeline
    stem_progress = smooth((t - 2) / 5)
    leaf_progress = smooth((t - 7) / 3)
    bud_progress = smooth((t - 10) / 3)
    bloom_progress = smooth((t - 13) / 7)

    # Flower position
    sway = math.sin(t * 1.4) * 8

    flower_x = CENTER_X + sway
    flower_y = GROUND_Y - 340

    # Magical light
    if bloom_progress > 0:
        draw_glow(
            flower_x,
            flower_y,
            int(115 + bloom_progress * 45),
            (255, 45, 110),
            bloom_progress
        )

    # Stem and leaves
    draw_stem(stem_progress, t)

    if leaf_progress > 0:
        draw_leaf(
            CENTER_X - 3,
            GROUND_Y - 155,
            -1,
            leaf_progress,
            t
        )

        draw_leaf(
            CENTER_X + 3,
            GROUND_Y - 245,
            1,
            leaf_progress,
            t
        )

    # Bud transforms into blooming rose
    if bloom_progress < 1:
        draw_bud(
            flower_x,
            flower_y,
            bud_progress * (1 - bloom_progress)
        )

    if bloom_progress > 0:
        draw_rose(
            flower_x,
            flower_y,
            bloom_progress,
            t
        )

    # Golden pollen
    if bloom_progress > 0.65:
        if t - last_pollen > 0.035:
            create_pollen(flower_x, flower_y)
            last_pollen = t

    update_pollen(dt)
    draw_pollen()

    pygame.display.flip()

pygame.quit()

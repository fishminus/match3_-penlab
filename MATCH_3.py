import json
import math
import sys

from uib_inf100_graphics.event_app import run_app
from uib_inf100_graphics.helpers import load_image, image_in_box

import python.match3_logic as match3

imagelink = {
    'P': "assets/Python.png",
    'X': "assets/x.png",
    'M': "assets/M.jpg",
    "O": "assets/O.png",
}

# ---------------------------------------------------------------- tuning ---
LEVELS_FILE  = "assets/levels.json"
MIN_SIZE     = 4
MAX_SIZE     = 8
TIMER_DELAY  = 16      # ms per frame (~60 fps)
EASE         = 0.30    # share of the remaining distance covered per frame
GRAVITY      = 0.035   # cells / frame^2 for falling tiles
CLEAR_FRAMES = 10      # how long matched tiles take to shrink away
COMMIT       = 0.40    # drag at least this far (in cells) to commit a swap
END_DELAY    = 35      # frames to look at the final board before win/lose screen
HUD_HEIGHT   = 40

BG           = "#1e1e2e"
CELL_A       = "#2a2a3d"
CELL_B       = "#313147"
BTN          = "#44446a"
BTN_HOVER    = "#5b5b91"
TEXT         = "#ffffff"
SUBTEXT      = "#b4b4d0"
GOOD         = "#6fdc8c"
BAD          = "#ff6b6b"
WARN         = "#ffb454"

# Used if levels.json is missing or broken, so the game always starts.
DEFAULT_LEVELS = [
    {"name": "Warm-up", "size": 5, "max_turns": 20, "score": 400},
    {"name": "Easy Does It", "size": 5, "max_turns": 18, "score": 600},
    {"name": "Getting Warmer", "size": 6, "max_turns": 20, "score": 900},
]


# ------------------------------------------------------------ level loading --
def load_levels(path=LEVELS_FILE):
    """Read levels from JSON. Accepts {"levels": [...]} or a bare list.
    Every field is validated/clamped so a typo can't crash the game."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        raw = data["levels"] if isinstance(data, dict) else data
        levels = []
        for i, lv in enumerate(raw):
            levels.append({
                "name": str(lv.get("name", f"Level {i + 1}")),
                "size": max(MIN_SIZE, min(MAX_SIZE, int(lv["size"]))),
                "max_turns": max(1, int(lv["max_turns"])),
                "score": max(1, int(lv["score"])),
            })
        if levels:
            return levels
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as e:
        print(f"Could not load {path} ({e!r}); using built-in levels.")
    return list(DEFAULT_LEVELS)


# ------------------------------------------------------------------ sprite --
class Sprite:
    """Visual tile. Positions are in *cell units*, so (2.5, 1.0) is half way
    between column 2 and 3 on row 1. The logic board stays the source of truth;
    sprites only decide where things are drawn."""

    def __init__(self, symbol, x, y):
        self.symbol = symbol
        self.x, self.y = float(x), float(y)
        self.tx, self.ty = float(x), float(y)   # where it is heading
        self.vy = 0.0
        self.falling = False                    # True -> gravity physics
        self.scale = 1.0

    def settled(self):
        return self.x == self.tx and self.y == self.ty

    def step(self):
        self.x += (self.tx - self.x) * EASE
        if abs(self.tx - self.x) < 0.002:
            self.x = self.tx

        if self.falling and self.ty > self.y:
            self.vy += GRAVITY
            self.y = min(self.ty, self.y + self.vy)
            if self.y == self.ty:
                self.vy = 0.0
                self.falling = False
        else:
            self.falling = False
            self.vy = 0.0
            self.y += (self.ty - self.y) * EASE
            if abs(self.ty - self.y) < 0.002:
                self.y = self.ty


# ------------------------------------------------------------------ layout --
def layout(app):
    n = app.game.board.x_width
    avail_h = app.height - HUD_HEIGHT - 10
    size = min(app.width * 0.9, avail_h) / n
    left = (app.width - size * n) / 2
    top = HUD_HEIGHT
    return left, top, size


def cell_at(app, px, py):
    """Pixel -> (x, y) cell (col, row), or None if outside the board."""
    left, top, size = layout(app)
    x = int((px - left) // size)
    y = int((py - top) // size)
    if app.game.board.CheckSquare(x, y) is None:
        return None
    return (x, y)


# ------------------------------------------------------------------ buttons --
def button(bid, label, x0, y0, x1, y1, sub=None):
    return {"id": bid, "label": label, "sub": sub,
            "x0": x0, "y0": y0, "x1": x1, "y1": y1}


def stack(app, items, top, w=240, h=44, gap=14):
    """Vertically stacked, horizontally centred buttons. items = [(id, label)]"""
    x0 = (app.width - w) / 2
    out = []
    for i, (bid, label) in enumerate(items):
        y0 = top + i * (h + gap)
        out.append(button(bid, label, x0, y0, x0 + w, y0 + h))
    return out


def screen_buttons(app):
    """Buttons for the current screen. Recomputed on demand, so resizing and
    hit-testing always agree with what is drawn."""
    s, w, h = app.screen, app.width, app.height

    if s == 'menu':
        return stack(app, [('play', 'Play'), ('settings', 'Settings'),
                           ('exit', 'Exit')], top=150)

    if s == 'settings':
        return stack(app, [('back_menu', 'Back')], top=h - 80)

    if s == 'levels':
        cols, gap, bw = 3, 14, 190
        rows = math.ceil(len(app.levels) / cols)
        top0, bottom = 80, h - 80
        bh = max(36, min(64, (bottom - top0 - (rows - 1) * gap) / rows))
        left0 = (w - (cols * bw + (cols - 1) * gap)) / 2
        out = []
        for i, lv in enumerate(app.levels):
            r, c = divmod(i, cols)
            x0 = left0 + c * (bw + gap)
            y0 = top0 + r * (bh + gap)
            sub = f"{lv['size']}x{lv['size']} · {lv['max_turns']} turns · {lv['score']} pts"
            out.append(button(f"level:{i}", f"{i + 1}. {lv['name']}",
                              x0, y0, x0 + bw, y0 + bh, sub))
        out += stack(app, [('back_menu', 'Back')], top=h - 62, h=40)
        return out

    if s == 'game':
        return [button('menu', 'Menu', 10, 8, 80, 32)]

    if s == 'win':
        items = []
        if app.level_index + 1 < len(app.levels):
            items.append(('next', 'Next level'))
        items += [('levels', 'Level select'), ('menu', 'Main menu')]
        return stack(app, items, top=200, h=40, gap=10)

    if s == 'lose':
        return stack(app, [('retry', 'Try again'), ('levels', 'Level select'),
                           ('menu', 'Main menu')], top=200, h=40, gap=10)
    return []


def button_at(app, px, py):
    for b in screen_buttons(app):
        if b['x0'] <= px <= b['x1'] and b['y0'] <= py <= b['y1']:
            return b
    return None


def on_button(app, bid):
    if bid == 'play' or bid == 'levels':
        app.screen = 'levels'
    elif bid == 'settings':
        app.screen = 'settings'
    elif bid in ('back_menu', 'menu'):
        app.screen = 'menu'
    elif bid == 'exit':
        quit_app(app)
    elif bid.startswith('level:'):
        start_level(app, int(bid.split(':')[1]))
    elif bid == 'retry':
        start_level(app, app.level_index)
    elif bid == 'next':
        start_level(app, app.level_index + 1)
    app.hover = None


def quit_app(app):
    try:
        app.canvas_ref.winfo_toplevel().destroy()   # closes the Tk window
    except Exception:
        sys.exit()


# ------------------------------------------------------------- game helpers --
def try_swap(board, a, b):
    """Swap a<->b on the logic board. Keep it if it creates a match, otherwise
    swap back. Returns True if the move was valid."""
    (x1, y1), (x2, y2) = a, b
    board.swapSquare(x1, y1, x2, y2)
    if board.Match3() is not None:
        return True
    board.swapSquare(x1, y1, x2, y2)
    return False


def all_sprites(app):
    for row in app.sprites:
        for s in row:
            if s is not None:
                yield s


def all_settled(app):
    return all(s.settled() for s in all_sprites(app))


def snap_home(app):
    """Send every sprite to the cell it occupies in the grid."""
    for y, row in enumerate(app.sprites):
        for x, s in enumerate(row):
            if s is not None:
                s.tx, s.ty = float(x), float(y)


def start_level(app, index):
    """(Re)start a level: new game, fresh counters, board drops in."""
    lv = app.levels[index]
    app.level_index = index
    # If your Game now takes turns too, pass lv["max_turns"] here as well.
    app.game = match3.Game(lv["score"], lv["max_turns"], lv["size"])
    app.turns_left = lv["max_turns"]

    app.drag = None
    app.dying = []
    app.matched = []
    app.clear_left = 0
    app.combo = 0
    app.end_left = 0
    app.result = None

    board = app.game.board
    w, h = board.x_width, board.y_heigth
    app.sprites = []
    for y in range(h):
        row = []
        for x in range(w):
            s = Sprite(board.CheckSquare(x, y), x, y - h)   # drops in from above
            s.ty = float(y)
            s.falling = True
            row.append(s)
        app.sprites.append(row)
    app.phase = 'fall'
    app.screen = 'game'


def check_end(app):
    """Called when the board has fully settled after a move."""
    if app.game.points >= app.game.pointCondition:
        app.result = 'win'
    elif app.turns_left <= 0:
        app.result = 'lose'
    else:
        app.phase = 'idle'
        return
    app.end_left = END_DELAY
    app.phase = 'ending'


# ------------------------------------------------------------ cascade steps --
def begin_clear(app):
    """Look for matches. If any: score them and start the shrink animation."""
    matches = app.game.board.Match3()
    if matches is None:
        app.combo = 0
        check_end(app)
        return

    cells = {(x, y) for x, y in matches}   # Match3 can return duplicates
    app.combo += 1
    app.game.points += 10 * len(cells) * app.combo
    app.matched = list(cells)

    app.dying = []
    for x, y in cells:
        app.dying.append(app.sprites[y][x])
        app.sprites[y][x] = None
    app.clear_left = CLEAR_FRAMES
    app.phase = 'clear'


def begin_fall(app):
    """Clear the logic board, let the logic refill it, and turn the result into
    falling animations (survivors drop, new tiles enter from above)."""
    board = app.game.board
    w, h = board.x_width, board.y_heigth

    board.Clear(app.matched)

    new_grid = [[None] * w for _ in range(h)]
    gaps = []
    for x in range(w):
        survivors = [y for y in range(h) if board.CheckSquare(x, y) != match3.empty]
        k = h - len(survivors)                  # empty cells in this column
        gaps.append(k)
        for j, y in enumerate(survivors):       # order is preserved by gravity
            s = app.sprites[y][x]
            s.ty = float(k + j)
            s.falling = s.ty > s.y
            new_grid[k + j][x] = s

    board.gravity()                             # logic fills the top with new symbols

    for x in range(w):
        k = gaps[x]
        for r in range(k):
            s = Sprite(board.CheckSquare(x, r), x, r - k)   # spawn above the board
            s.ty = float(r)
            s.falling = True
            new_grid[r][x] = s

    app.sprites = new_grid
    app.phase = 'fall'


# -------------------------------------------------------------------- app ---
def app_started(app):
    app.images = {sym: load_image(path) for sym, path in imagelink.items()}
    app.timer_delay = TIMER_DELAY
    app.levels = load_levels()
    app.level_index = 0
    app.screen = 'menu'      # menu | levels | settings | game | win | lose
    app.hover = None
    app.canvas_ref = None


def timer_fired(app):
    if app.screen != 'game':
        return

    for s in all_sprites(app):
        s.step()

    if app.phase == 'clear':
        app.clear_left -= 1
        for s in app.dying:
            s.scale = max(0.0, app.clear_left / CLEAR_FRAMES)
        if app.clear_left <= 0:
            app.dying = []
            begin_fall(app)

    elif app.phase in ('fall', 'swap') and all_settled(app):
        begin_clear(app)                 # chains/cascades come from looping here

    elif app.phase == 'reject' and all_settled(app):
        snap_home(app)                   # bounce back after the failed swap
        app.phase = 'return'

    elif app.phase == 'return' and all_settled(app):
        app.phase = 'idle'

    elif app.phase == 'ending':
        app.end_left -= 1
        if app.end_left <= 0:
            app.screen = app.result      # 'win' or 'lose'


# ------------------------------------------------------------------ mouse ---
def mouse_moved(app, event):
    b = button_at(app, event.x, event.y)
    app.hover = b['id'] if b else None


def mouse_pressed(app, event):
    b = button_at(app, event.x, event.y)
    if b:
        on_button(app, b['id'])
        return
    if app.screen != 'game' or app.phase != 'idle':
        return
    cell = cell_at(app, event.x, event.y)
    if cell is None:
        return
    app.drag = {'cell': cell, 'start': (event.x, event.y),
                'axis': None, 'target': None, 'progress': 0.0}
    app.phase = 'drag'


def mouse_dragged(app, event):
    if app.screen != 'game' or app.phase != 'drag' or app.drag is None:
        return
    d = app.drag
    x, y = d['cell']
    left, top, size = layout(app)
    dx = (event.x - d['start'][0]) / size
    dy = (event.y - d['start'][1]) / size

    # Lock to the dominant axis so tiles only move horizontally OR vertically
    if d['axis'] is None:
        if max(abs(dx), abs(dy)) < 0.10:
            return
        d['axis'] = 'x' if abs(dx) > abs(dy) else 'y'

    raw = dx if d['axis'] == 'x' else dy
    direction = 1 if raw > 0 else -1
    if d['axis'] == 'x':
        target = (x + direction, y)
    else:
        target = (x, y + direction)
    if app.game.board.CheckSquare(*target) is None:
        target = None                                   # edge of board

    # Past the edge the tile "rubber-bands" instead of following the mouse
    amount = min(abs(raw), 1.0) * (1.0 if target else 0.15)
    off = direction * amount
    ox, oy = (off, 0.0) if d['axis'] == 'x' else (0.0, off)

    # Dragged tile follows the cursor 1:1 (no easing = feels instant)
    dragged = app.sprites[y][x]
    dragged.x, dragged.y = x + ox, y + oy
    dragged.tx, dragged.ty = dragged.x, dragged.y

    # If the user reversed direction, release the neighbour we were pushing
    if d['target'] is not None and d['target'] != target:
        px, py = d['target']
        n = app.sprites[py][px]
        n.tx, n.ty = float(px), float(py)

    d['target'] = target
    d['progress'] = amount if target else 0.0

    # Neighbour slides the opposite way (eased) as a live preview of the swap
    if target:
        nx, ny = target
        n = app.sprites[ny][nx]
        n.tx, n.ty = nx - ox, ny - oy


def mouse_released(app, event):
    if app.screen != 'game' or app.phase != 'drag':
        return
    d, app.drag = app.drag, None
    a, b = d['cell'], d['target']

    # Not dragged far enough -> spring back
    if b is None or d['progress'] < COMMIT:
        snap_home(app)
        app.phase = 'return'
        return

    sa = app.sprites[a[1]][a[0]]
    sb = app.sprites[b[1]][b[0]]

    if try_swap(app.game.board, a, b):
        app.turns_left -= 1                       # only valid moves cost a turn
        app.sprites[a[1]][a[0]], app.sprites[b[1]][b[0]] = sb, sa
        snap_home(app)
        app.phase = 'swap'
    else:
        # Invalid: finish the swap visually, then bounce back (see timer_fired)
        sa.tx, sa.ty = float(b[0]), float(b[1])
        sb.tx, sb.ty = float(a[0]), float(a[1])
        app.phase = 'reject'


# ---------------------------------------------------------------- drawing ---
def draw_button(app, canvas, b):
    hovered = app.hover == b['id']
    canvas.create_rectangle(b['x0'], b['y0'], b['x1'], b['y1'],
                            fill=BTN_HOVER if hovered else BTN,
                            outline=SUBTEXT if hovered else "", width=2)
    cx = (b['x0'] + b['x1']) / 2
    cy = (b['y0'] + b['y1']) / 2
    small = (b['y1'] - b['y0']) < 30
    if b['sub']:
        canvas.create_text(cx, cy - 10, text=b['label'], fill=TEXT,
                           font="Arial 12 bold")
        canvas.create_text(cx, cy + 12, text=b['sub'], fill=SUBTEXT,
                           font="Arial 9")
    else:
        canvas.create_text(cx, cy, text=b['label'], fill=TEXT,
                           font="Arial 10 bold" if small else "Arial 14 bold")


def draw_tile(app, canvas, s, lift=False):
    left, top, size = layout(app)
    cx = left + (s.x + 0.5) * size
    cy = top + (s.y + 0.5) * size
    half = (size / 2 - size * 0.08) * s.scale * (1.12 if lift else 1.0)
    if half <= 0:
        return
    image_in_box(canvas, cx - half, cy - half, cx + half, cy + half,
                 app.images[s.symbol])


def draw_game(app, canvas):
    left, top, size = layout(app)
    n = app.game.board.x_width

    for y in range(n):
        for x in range(n):
            canvas.create_rectangle(
                left + x * size, top + y * size,
                left + (x + 1) * size, top + (y + 1) * size,
                fill=CELL_A if (x + y) % 2 == 0 else CELL_B, outline="")

    # Dragged tile is drawn last (on top) and slightly enlarged
    dragged = None
    if app.drag is not None:
        dx, dy = app.drag['cell']
        dragged = app.sprites[dy][dx]
    for s in all_sprites(app):
        if s is not dragged:
            draw_tile(app, canvas, s)
    for s in app.dying:
        draw_tile(app, canvas, s)
    if dragged is not None:
        draw_tile(app, canvas, dragged, lift=True)

    # Hide new tiles that are still above the board
    canvas.create_rectangle(0, 0, app.width, top, fill=BG, outline="")

    # HUD
    score = f"Score: {app.game.points} / {app.game.pointCondition}"
    if app.combo > 1:
        score += f"   x{app.combo} combo!"
    canvas.create_text(app.width / 2, HUD_HEIGHT / 2, text=score,
                       fill=TEXT, font="Arial 14 bold")
    low = app.turns_left <= 3
    canvas.create_text(app.width - 14, HUD_HEIGHT / 2, anchor="e",
                       text=f"Turns: {app.turns_left}",
                       fill=WARN if low else TEXT, font="Arial 14 bold")


def draw_menu_background(app, canvas):
    """Hook for your menu graphics later (logo, animated tiles, ...)."""
    pass


def draw_title(app, canvas, text, y=70, color=TEXT, size=36):
    canvas.create_text(app.width / 2, y, text=text, fill=color,
                       font=f"Arial {size} bold")


def draw_panel(app, canvas):
    canvas.create_rectangle(app.width / 2 - 200, 30, app.width / 2 + 200,
                            app.height - 30, fill=CELL_A, outline=BTN, width=3)


def draw_end_screen(app, canvas, won):
    lv = app.levels[app.level_index]
    draw_panel(app, canvas)
    draw_title(app, canvas, "LEVEL CLEARED!" if won else "OUT OF TURNS",
               y=85, color=GOOD if won else BAD, size=28)
    canvas.create_text(app.width / 2, 135, fill=TEXT, font="Arial 14",
                       text=f"Score: {app.game.points} / {lv['score']}")
    if won:
        info = f"Turns left: {app.turns_left}"
    else:
        info = f"You were {lv['score'] - app.game.points} points short"
    canvas.create_text(app.width / 2, 162, fill=SUBTEXT, font="Arial 12",
                       text=info)


def redraw_all(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill=BG, outline="")

    if app.screen == 'game':
        draw_game(app, canvas)
    elif app.screen == 'menu':
        draw_menu_background(app, canvas)
        draw_title(app, canvas, "MATCH 3", y=80, size=44)
    elif app.screen == 'levels':
        draw_title(app, canvas, "Select level", y=40, size=26)
    elif app.screen == 'settings':
        draw_title(app, canvas, "Settings", y=40, size=26)
        canvas.create_text(app.width / 2, app.height / 2, fill=SUBTEXT,
                           font="Arial 14", text="Nothing here yet.")
    elif app.screen == 'win':
        draw_end_screen(app, canvas, True)
    elif app.screen == 'lose':
        draw_end_screen(app, canvas, False)
    for b in screen_buttons(app):
        draw_button(app, canvas, b)
    


run_app(width=900, height=600)
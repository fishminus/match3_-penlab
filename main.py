from uib_inf100_graphics.event_app import run_app
from uib_inf100_graphics.helpers import load_image, image_in_box


import python.match3_logic as match3

imagelink = {
    'P':"assets/Python.png",
    'X':"assets/x.png",
    'M':"assets/M.jpg",
    "O":"assets/O.png"
}

def app_started(app):
    app.game = match3.Game(100, 5)
    app.images = {
        'P':load_image(imagelink['P']),
        'X':load_image(imagelink['X']),
        'M':load_image(imagelink['M']),
        'O':load_image(imagelink['O'])
    }
    app.rows = 5
    app.cols = 5
    app.margin = 50 # margin rundt rutenettet
    app.selection = (-1, -1) # (row, col) for valgt rute, (-1,-1) for ingen
    while (app.game.points < app.game.pointCondition):
        #swap input
        x1 = int(input("X1 -> "))
        y1 = int(input("Y1 -> "))
        x2 = int(input("X2 -> "))
        y2 = int(input("Y2 -> "))
        if app.game.myboard.CheckSquare(x1, y1) != None or app.game.myboard.CheckSquare(x2, y2) != None:
            if abs(x2 - x1) == 1 or abs(y2 - y1) == 1:#sjekk at de er ved siden
                #Check if move is valid
                cloneBoard = app.game.myboard
                cloneBoard.swapSquare(x1, y1, x2, y2)
                cloneBoard.print()
                if cloneBoard.Match3() != None:
                    print("Commencing main")
                    app.game.myboard.Clone(cloneBoard)
                    matches = app.game.myboard.Match3()
                    while matches != None:
                        app.game.myboard.print()
                        app.game.myboard.Clear(matches)
                        app.game.myboard.gravity()
                        matches = app.game.myboard.Match3()
                else:
                    print("Invalid move!")
            else:
                print("Invalid move!")
            app.game.myboard.print()

def point_in_grid(app, x, y):
    # returner True hvis piksel-koordinatet (x, y) er på innsiden av
    # rutenettet slik det blir tegnet i visningen.
    return ((app.margin <= x <= app.width-app.margin) and
            (app.margin <= y <= app.height-app.margin))

def get_cell(app, x, y):
    # "visning-til-modell"
    # returnerer (row, col) for ruten hvor piksel-koordnatet (x, y) hører
    # hjemme, eller (-1, -1) hvis koodinatet er utenfor rutenettet
    if (not point_in_grid(app, x, y)):
        return (-1, -1)
    grid_width  = app.width - 2*app.margin
    grid_height = app.height - 2*app.margin
    cell_width  = grid_width / app.cols
    cell_height = grid_height / app.rows

    # Merk: vi trenger å konvertere til int her; det er ikke 
    # tilstrekkelig å benytte //, siden x, y, eller app.margin kan
    # være flyttall, og da vil også // returnere flyttall
    row = int((y - app.margin) / cell_height)
    col = int((x - app.margin) / cell_width)

    return (row, col)

def get_cell_bounds(app, row, col):
    # "modell-til-visning"
    # returnerer (x0, y0, x1, y1), piksel-koordinater for hjørnene til
    # den gitte ruten
    grid_width  = app.width - 2*app.margin
    grid_height = app.height - 2*app.margin
    column_width = grid_width / app.cols
    row_height = grid_height / app.rows
    x0 = app.margin + col * column_width
    x1 = app.margin + (col+1) * column_width
    y0 = app.margin + row * row_height
    y1 = app.margin + (row+1) * row_height
    return (x0, y0, x1, y1)

def mouse_pressed(app, event):
    (row, col) = get_cell(app, event.x, event.y)
    # velg denne ruten med mindre den allerede er valgt
    if (app.selection == (row, col)):
        app.selection = (-1, -1)
    else:
        app.selection = (row, col)

def mouse_released(app, event):
    app.selection = (-1, -1)

def mouse_moved(app, event):
    pass

def redraw_all(app, canvas):
    # tegn alle rutene
    for row in range(app.rows):
        for col in range(app.cols):
            (x0, y0, x1, y1) = get_cell_bounds(app, row, col)
            fill = app.images[app.game.myboard.CheckSquare(row, col)]
            if (app.selection == (row, col)):
                fill = app.images['X']

            image_in_box(canvas, x0, y0, x1, y1, fill)

run_app(width=680, height=400)

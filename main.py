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
    app.selection = (-1, -1) # (row, col) for valgt rute, (-1,-1) for ingen

    app.game.board.print()
    x1 = int(input("X1 -> "))
    y1 = int(input("Y1 -> "))
    x2 = int(input("X2 -> "))
    y2 = int(input("Y2 -> "))
    move_iteration(app, x1, y1, x2, y2)
        
def move_iteration(app, x1, y1, x2, y2):
    if app.game.board.CheckSquare(x1, y1) != None or app.game.board.CheckSquare(x2, y2) != None:#finnes trekkene
        if abs(x2 - x1) == 1 or abs(y2 - y1) == 1:#sjekk at de er ved siden
            #Check if move is valid
            cloneBoard = app.game.board
            cloneBoard.swapSquare(x1, y1, x2, y2)
            if cloneBoard.Match3() != None:
                print("Commencing main")
                app.game.board.Clone(cloneBoard)
                matches = app.game.board.Match3()
                while matches != None:
                    app.game.board.print()
                    app.game.board.Clear(matches)
                    app.game.board.gravity()
                    matches = app.game.board.Match3()
            else:
                print("Invalid move: Move has to have matches!")
        else:
            print("Invalid move: Move has to be adjacent!")
    else:
        print("Invalid move: Move has to be in bounds!")

def mouse_pressed(app, event):
    #(row, col) = get_cell(app, event.x, event.y)
    ...

def mouse_released(app, event):
    app.selection = (-1, -1)

def mouse_moved(app, event):
    ...

def redraw_all(app, canvas):
    ...

run_app(width=680, height=400)

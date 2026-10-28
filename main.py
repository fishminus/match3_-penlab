import math
import random
from uib_inf100_graphics.simple import canvas, display
from uib_inf100_graphics.helpers import load_image_http, scaled_image

default_symbols = ['X', 'O', 'P', 'M']
empty = '_'

class Board():
    def __init__(self, x_width, y_width, symbols, seed):
        self.x_width, self.y_heigth = x_width, y_width
        self.symbolset = symbols
        random.seed, self.seed = seed, seed
        self.current = []
        for y in range(y_width):
            line = []
            for x in range(x_width):
                line.append(symbols[random.randrange(0, len(symbols))])
            self.current.append(line)

    def CheckSquare(self, x, y):
        #sjekk at den eksisterer
        if x >= 0 and y >= 0 and x < self.x_width and y < self.y_heigth:
            return self.current[y][x]
        return None#eksisterer ikke

    def Clone(self, board):
        self.current = board.current
    
    def swapSquare(self, x1, y1, x2, y2):
        #directly swap p1, p2
        p1 = self.CheckSquare(x1, y1)
        p2 = self.CheckSquare(x2, y2)
        if p1 != None and p2 != None:
            self.SetSquare(x1, y1, p2)
            self.SetSquare(x2, y2, p1)

    def SetSquare(self, x, y, value):
        if self.CheckSquare(x, y) != None:
            self.current[y][x] = value
        else:
            print("No square at", x, y)

    def randomizeSquare(self, x, y):
        self.current[y][x] = self.symbolset[random.randrange(0, len(self.symbolset))]

    def Match3(self):
        matches = []
        for y in range(self.y_heigth):#Horizontal matches through the ROW
            matchnumber = 1
            temp = []
            for x in range(self.x_width):
                symbol = self.CheckSquare(x, y)#get current
                x_r = x + 1

                if matchnumber == 1:#start
                    temp = [[x, y]]

                if symbol == self.CheckSquare(x_r, y):
                    matchnumber += 1
                    temp.append([x_r, y])
                else:
                    if matchnumber >= 3:
                        print("MatchH found", temp)
                        matches+=temp
                    matchnumber = 1
        for x in range(self.x_width):#Horizontal matches through the COLLUM
            matchnumber = 1
            temp = []
            for y in range(self.y_heigth):
                symbol = self.CheckSquare(x, y)#get current
                y_r = y + 1

                if matchnumber == 1:#start
                    temp = [[x, y]]

                if symbol == self.CheckSquare(x, y_r):
                    matchnumber += 1
                    temp.append([x, y_r])
                else:
                    if matchnumber >= 3:
                        print("MatchV found", temp)
                        matches+=temp
                    matchnumber = 1      

        if len(matches) > 0:
            return matches
        return None
    
    def ClearALL(self):
        for x in range(self.x_width):
            for y in range(self.y_width):
                self.SetSquare(x, y, empty)

    def Clear(self, list):
        if list != None:
            for node in list:
                self.SetSquare(node[0], node[1], empty)

    def gravity(self):
        #move elements down until there are no empty spaces
        #generate new items at index 0
        do_over = False
        for x in range(self.x_width):
            for i in range(self.y_heigth):
                y_r = self.y_heigth - i - 1#reverse y order
                symbol = self.CheckSquare(x, y_r)
                symbol_over = self.CheckSquare(x, y_r-1)
                #print(x, i, y_r, symbol)
                if symbol == empty and symbol_over != None:#falls
                    if symbol_over == empty:
                        do_over = True
                    self.swapSquare(x, y_r, x, y_r-1)
                elif symbol == empty and symbol_over == None:
                    self.randomizeSquare(x, y_r)
        if do_over:#denne rekursjonen er utrolig dum TODO: consider removing complexity layer
            self.gravity()

    def print(self):
        out = ""
        for y in self.current:
            for x in y:
                out += x + " "
            out += "\n"
        print(out)


class Game():
    def __init__(self, pointCondition):
        self.points = 0
        self.myboard = Board(5,5,default_symbols,2005)
        self.myboard.print()
        matches = self.myboard.Match3()
        self.myboard.Clear(matches)
        while matches != None:
            self.myboard.gravity()
            matches = self.myboard.Match3()
            self.myboard.Clear(matches) 

        self.myboard.print()
    
        while (self.points < pointCondition):
            #swap input
            x1 = int(input("X1 -> "))
            y1 = int(input("Y1 -> "))
            x2 = int(input("X2 -> "))
            y2 = int(input("Y2 -> "))
            if self.myboard.CheckSquare(x1, y1) != None or self.myboard.CheckSquare(x2, y2) != None:
                if abs(x2 - x1) == 1 or abs(y2 - y1) == 1:#sjekk at de er ved siden
                    #Check if move is valid
                    cloneBoard = self.myboard
                    cloneBoard.swapSquare(x1, y1, x2, y2)
                    cloneBoard.print()
                    if cloneBoard.Match3() != None:
                        print("Commencing main")
                        self.myboard.Clone(cloneBoard)
                        matches = self.myboard.Match3()
                        while matches != None:
                            self.myboard.print()
                            self.myboard.Clear(matches)
                            self.myboard.gravity()
                            matches = self.myboard.Match3()
                else:
                    print("Invalid move!")
            else:
                print("Invalid move!")

            self.myboard.print()
    

newgame = Game(10)

#image= load_image_http("https://bluemoji.io/cdn-proxy/646218c67da47160c64a84d5/66b3e5d0c2ab246786ca1d5e_86.png")
#canvas.create_image(200,200,pil_image=image)

#display(canvas)

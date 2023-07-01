#Import Modules
import pygame
pygame.init()

import os
import math
import random
import copy

from ASprites import *

#Settings
clock = pygame.time.Clock()
FPS = 30

Objects = []
PersisObjects = []
Removes = []

Rooms = []
CurrentRoom = ""

Sombre = True
player = None
playerSwitchKey = pygame.K_LCTRL

#Screen
screenWidth = 768
screenHeight = 480
screen = pygame.display.set_mode((screenWidth, screenHeight))

roomWidth = screenWidth*2
roomHeight = screenHeight*2

#Colours
white = (255,255,255)
midWhite = (205,205,205)
grey = (128,128,128)
midBlack = (51,51,51)
black = (0,0,0)

red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)

yellow = (255,255,0)
magenta = (255,0,255)
turquoise = (0,255,255)

boyCol = (219,172,18)
girlCol = (0,255,156)
manCol = (48,26,255)
womanCol = (157,215,29)

graceCol = (130,249,255)
janitorColour = (25,44,57)
sarahColour = (235,255,56)

#Music
CurrentSong = ""
persisSong = False

def FadeIn(inc):
    pygame.mixer.music.set_volume(0)

    def func(inc):
        vol = pygame.mixer.music.get_volume()
        if vol == 1:
            return 0

        if vol < 1-inc:
            vol += inc
        else:
            vol = 1

        pygame.mixer.music.set_volume(vol)
        AddPersis(Timer(.5, lambda:func(inc)))
    AddPersis(Timer(.5, lambda:func(inc)))

def PlaySong(name, inc=.05):
    if persisSong:
        return 0

    global CurrentSong
    if name != CurrentSong:
        CurrentSong = name
    else:
        return 0

    pygame.mixer.music.load("Music/"+name+".mp3")
    pygame.mixer.music.play(-1)
    FadeIn(inc)

def PersisSong(name, inc=.05):
    PlaySong(name)

    global persisSong
    persisSong = True

def StopPersisSong():
    global persisSong
    persisSong = False

#Sounds
def Sound(name):
    return pygame.mixer.Sound("Music/"+name+".wav")

GetHurtSound = Sound("GetHurt")
DieSound = Sound("Die")

DashSound = Sound("Dash")
LifeOrbSound = Sound("LifeOrb")
PowerUpSound = Sound("PowerUp")

#Helpful Funcs
def hasis(obj, attr):
    if hasattr(obj, attr):
        return eval("obj."+attr)
    return False

def checksHasis(obj, attr):
    if hasattr(obj, "checks"):
        if attr in obj.checks:
            return eval("obj.checks['"+attr+"']")
    return False

def sign(x):
    if x < 0:
        return -1
    elif x > 0:
        return 1
    else:
        return 0

def dist(a, b):
    if type(a) == tuple:
        ax, ay = a
    elif hasattr(a, "rect"):
        ax, ay = a.rect.center

    if type(b) == tuple:
        bx, by = b
    elif hasattr(b, "rect"):
        bx, by = b.rect.center

    x = ax-bx
    y = ay-by
    
    c = math.sqrt(x**2+y**2)
    return c

def minDist(a, b):
    if type(a) == tuple:
        ad = 0
    elif hasattr(a, "rect"):
        ad = dist(a.rect.topleft, a.rect.center)

    if type(b) == tuple:
        bd = 0
    elif hasattr(b, "rect"):
        bd = dist(b.rect.topleft, b.rect.center)

    td = ad+bd+1
    return td

def BckRect(rect):
    rect.x *= bck.scale
    rect.y *= bck.scale
    rect.w *= bck.scale
    rect.h *= bck.scale

    return rect

def SetPosition(rect, hs, vs, x, y):
    obj = None
    if hasattr(rect, "rect"):
        obj = rect
        rect = obj.rect
        
    exec("rect."+hs+"="+str(x))
    exec("rect."+vs+"="+str(y))

    if obj != None:
        if "cam" in globals():
            Rects(obj)

        if player != None:
            if obj == player:
                CamSkip()

def SetPositionBck(rect, hs, vs, x, y):
    x *= bck.scale
    y *= bck.scale

    SetPosition(rect, hs, vs, x, y)
            
def SetPositionGrid(self, grid, hs="centerx", vs="centery"):
    x = grid[0]*cellSize+cellSize*.5
    y = grid[1]*cellSize+cellSize*.5
    
    SetPosition(self, hs, vs, x, y)

def Outside(self):
    if self.rect.left < 0:
        self.rect.left = 0
    elif self.rect.right > roomWidth:
        self.rect.right = roomWidth

    if self.rect.top < 0:
        self.rect.top = 0
    elif self.rect.bottom > roomHeight:
        self.rect.bottom = roomHeight

    Rects(self)

def OutsideScreen(self):
    if self.camRect.left < 0:
        self.rect.left = cam[0]
    elif self.camRect.right > screenWidth:
        self.rect.right = cam[0]+screenWidth

    if self.camRect.top < 0:
        self.rect.top = cam[1]
    elif self.camRect.bottom > screenHeight:
        self.rect.bottom = cam[1]+screenHeight

    Rects(self)

def CheckOutside(obj):
    if obj.rect.left > roomWidth:
        return True
    if obj.rect.right < 0:
        return True

    if obj.rect.top > roomHeight:
        return True
    if obj.rect.bottom < 0:
        return True

    return False

def OnScreen(obj):
    if checksHasis(obj, "OnScreen"):
        return True
    
    if hasattr(obj, "rect"):
        Rects(obj)
    if not hasattr(obj, "camRect"):
        return True
    
    if obj.camRect.left > screenWidth:
        return False
    if obj.camRect.right < 0:
        return False
    if obj.camRect.top > screenHeight:
        return False
    if obj.camRect.bottom < 0:
        return False
    return True

def OffScreen(obj):
    return not OnScreen(obj)

def HelpFind(obj):
    if OnScreen(obj):
        return 0
    
    sprite = obj.Sprite.sprite.copy()
    width, height = sprite.get_size()

    sw, sh = obj.Sprite.rect.size

    if sw > sh:
        nw, nh = 32*obj.Sprite.frames, sh/sw*32
    else:
        nw, nh = sw/sh*32*obj.Sprite.frames, 32

    sw, sh = nw/obj.Sprite.frames, nh

    nw, nh = int(nw), int(nh)
    sprite = pygame.transform.scale(sprite, (nw, nh))

    rect = pygame.Rect(obj.camRect)
    rect.size = (sw, sh)
    
    if rect.left < 0:
        rect.left = 0
    if rect.right > screenWidth:
        rect.right = screenWidth

    if rect.top < 0:
        rect.top = 0
    if rect.bottom > screenHeight:
        rect.bottom = screenHeight

    screen.blit(sprite, rect.topleft, (obj.Sprite.frameCount*sw, 0, sw, sh))
        
font = pygame.font.Font("calibri.ttf", 18)
menuFont = pygame.font.Font("calibri.ttf", 24)
def text(txt, col, hs, vs, x, y, fnt=font, alpha=255):
    msg = fnt.render(txt, True, col)
    width, height = msg.get_size()

    changeAlpha = alpha/255
    for xx in range(width):
        for yy in range(height):
            col = msg.get_at((xx, yy))
            alph = col[3]

            if alph > 0:
                newAlpha = alph*changeAlpha
                newCol = (col[0], col[1], col[2], newAlpha)
                msg.set_at((xx, yy), newCol)
    
    rect = pygame.Rect((0, 0), msg.get_size())
    SetPosition(rect, hs, vs, x, y)
    
    screen.blit(msg, rect.topleft)

def WhenNormal():
    if "SB" in globals():
        if CheckSpeech():
            return False
    if PMoving:
        return False

    return True

def ReturnToNormal():
    def func():
        for o in Objects:
            if not hasattr(o, "checks") or not hasattr(o, "ochecks"):
                continue

            for c in o.ochecks:
                ChangeCheck(o, c, o.ochecks[c])
            o.ochecks = {}

    Check(WhenNormal, func)

def Players():
    objs = []
    for o in Objects:
        if issubclass(type(o), Player):
            objs.append(o)
    return objs

def SetPlayer(p):
    global player
    player = p

    global camTarget
    camTarget = p

    for p in players:
        if p == player:
            p.Control()
        else:
            p.Hide()

def NextPlayer():
    global player, camTarget

    first = False

    roomPlayers = []
    for r in Rooms[CurrentRoom][1]:
        if issubclass(type(r), Player):
            roomPlayers.append(r)

    if player == None:
        player = random.choice(roomPlayers)
        first = True
    else:
        closest = None
        for p in Players():
            if p == player:
                continue
            if closest == None:
                closest = p
            elif dist(player, p) < dist(player, closest):
                closest = p

        if closest != None:
            player = closest
    camTarget = player
    if first:
        CamSkip()

    if first:
        objs = players
    else:
        objs = roomPlayers

    for p in objs:
        if p == player:
            p.Control()
        else:
            p.Hide()

def RemovePersis(obj):
    if obj in PersisObjects:
        PersisObjects.remove(obj)

    for r in Rooms:
        if obj in Rooms[r][1] and r != CurrentRoom:
            Rooms[r][1].remove(obj)

    # if CurrentRoom != "":
    #     if obj not in Rooms[CurrentRoom][1]:
    #         Rooms[CurrentRoom][1].append(obj)

def AddPersis(obj):
    if obj in PersisObjects:
        return 0

    PersisObjects.append(obj)

PMoving = False
def PersonMove(obj, hs, xy, spd, eFunc=None):
    global PMoving
    PMoving = True

    def func0():
        for o in Objects:
            if hasattr(o, "checks"):
                if not hasattr(o, "ochecks"):
                    o.ochecks = {}

                ChangeCheckTemp(o, "Moving", False)
                ChangeCheckTemp(o, "Input", False)
                ChangeCheckTemp(o, "Shooting", False)

    if not CheckSpeech():
        func0

    if bck != None:
        xy = list(xy)
        xy[0] *= bck.scale
        xy[1] *= bck.scale

    xy = (int(xy[0]), int(xy[1]))
    
    def check(o):
        c = "o.rect."+hs[0]+"!="+str(xy[0])+" or o.rect."+hs[1]+"!="+str(xy[1])
        val = eval(c)
        
        return val
        
    def func(o):
        global camTarget
        camTarget = o

        x = xy[0] - eval("o.rect."+str(hs[0]))
        y = xy[1] - eval("o.rect."+str(hs[1]))

        if abs(x) > abs(spd):
            x = sign(x)*spd
        if abs(y) > abs(spd):
            y = sign(y)*spd

        x, y = int(x), int(y)
        Move(o, x, y)

        if x != 0:
            if x < 0:
                ChangeSprite(o, o.name+"RunLeft")
            else:
                ChangeSprite(o, o.name+"RunRight")

        elif y != 0:
            if y < 0:
                ChangeSprite(o, o.name+"RunUp")
            else:
                ChangeSprite(o, o.name+"RunDown")

    def endFunc(o):
        global PMoving
        PMoving = False

        if not CheckSpeech():
            global camTarget
            camTarget = player

        if o.Sprite.name == o.name+"RunUp":
            ChangeSprite(o, o.name+"IdleUp")
        else:
            ChangeSprite(o, o.name+"IdleDown")

        if eFunc != None:
            eFunc()

        ReturnToNormal()
            
    DoCheck(lambda:check(obj), lambda:func(obj)).endFunc = lambda:endFunc(obj)

def PersonMoves(lst):
    def CreatePersonMove(lst):
        if len(lst) == 4:
            r = lambda:PersonMove(lst[0], lst[1], lst[2], lst[3])
        elif len(lst) == 5:
            r = lambda:PersonMove(lst[0], lst[1], lst[2], lst[3], lst[4])
        else:
            print("Not enough arguments:", lst, len(lst))
        return r

    if len(lst) == 1:
        CreatePersonMove(lst[0])()

    def LstCreatePersonMove(i=0):
        if i < len(lst)-1:
            if len(lst[i]) == 4:
                lst[i].append(LstCreatePersonMove(i+1))
            else:
                def newFunc():
                    LstCreatePersonMove(i+1)
                    lst[i][4]()
                lst[i][4] = newFunc

        return CreatePersonMove(lst[i])
    LstCreatePersonMove()()

def Drop(source, obj):
    obj.finishDrop = False
    if type(source) == tuple:
        xy = source
    elif hasattr(source, "rect"):
        xy = source.rect.center

    obj.rect.center = xy
    
    obj.grav = 1
    obj.dropHspd = random.randint(2, 4)*random.choice([-1, 1])
    obj.odropVspd = obj.dropVspd = random.randint(-5, -3)

    def timerFunc():
        if obj.dropVspd < abs(obj.odropVspd):
            obj.dropVspd += obj.grav
            Timer(.1, timerFunc)
    timerFunc()
    
    def func():
        Move(obj, obj.dropHspd, obj.dropVspd)
    def endFunc():
        obj.finishDrop = True
    DoCheck(lambda:obj.dropVspd<abs(obj.odropVspd), func).endFunc = endFunc

def Peace():
    global Objects
    
    newObjects = []
    for o in Objects:
        if issubclass(type(o), Enemy):
            continue
        if type(o) == Bullet or issubclass(type(o), Bullet):
            continue
        newObjects.append(o)
    Objects = newObjects

def ChangeCheck(obj, check, val):
    if WhenNormal():
        obj.checks[check] = val
    else:
        if not hasattr(obj, "ochecks"):
            obj.ochecks = {}

        obj.ochecks[check] = val

def ChangeCheckNow(obj, check, val):
    obj.checks[check] = val

def ChangeCheckPerm(obj, check, val):
    if not hasattr(obj, "ochecks"):
        obj.ochecks = {}

    obj.checks[check] = val
    obj.ochecks[check] = val

def ChangeCheckTemp(obj, check, val):
    if check in obj.ochecks:
        return 0

    obj.ochecks[check] = copy.copy(obj.checks[check])
    obj.checks[check] = val

def Burst(obj):
    if hasattr(obj, "speechColour"):
        colour = obj.speechColour
    else:
        colour = midBlack

    for i in range(5):
        Drop(obj, Particle(colour))

def Explode(obj):
    colour = midBlack
    if hasattr(obj, "speechColour"):
        colour = obj.speechColour

    Burst(obj)
    RoomoveObject(obj)

def RandomSpawn(obj):
    SetPosition(obj, "left", "top", random.randint(0, roomWidth-obj.rect.w), 
        random.randint(0, roomHeight-obj.rect.height))

    while True:
        SetPosition(obj, "left", "top", random.randint(0, roomWidth-obj.rect.w), 
            random.randint(0, roomHeight-obj.rect.height))

        if dist(obj, player) < 96: 
            continue
        if Collide(obj):
            continue

        tranCon = False
        for o in Objects:
            if type(o) != Tran:
                continue

            if dist(obj, o) < minDist(obj, o)*2:
                tranCon = True
                break
        if tranCon:
            continue

        break

#Helpful Objs
class Timer:
    def __init__(self, time, func):
        RoomObject(self)
        self.func = func
        
        self.time = time*FPS
        self.count = 0

    def Update(self):
        if self.count < self.time:
            self.count += 1
        else:
            self.func()
            RoomoveObject(self)

class DoTimer(Timer):
    def Update(self):
        if self.count < self.time:
            self.count += 1
            self.func()
        else:
            if hasattr(self, "endFunc"):
                self.endFunc()
                
            RoomoveObject(self)

class Repeater(Timer):
    def Update(self):
        if self.count < self.time:
            self.count += 1
        else:
            self.func()
            self.count = 0

class Check:
    def __init__(self, checkFunc, doFunc, die=True):
        RoomObject(self)
        self.checkFunc = checkFunc
        self.doFunc = doFunc

        self.die = die

    def Update(self):
        if self.checkFunc():
            self.doFunc()

            if self.die:
                RoomoveObject(self)

class DoCheck(Check):
    def Update(self):
        if self.checkFunc():
            self.doFunc()
        else:
            if not hasis(self, "persis"):
                if hasattr(self, "endFunc"):
                    self.endFunc()
                RoomoveObject(self)

class CollideFunc:
    def __init__(self, rect, func, dis=True):
        RoomObject(self)
        self.dis = dis
        self.func = func

        self.colour = white
        self.alpha = 192
        self.blend = None
        self.rect = rect

        SurfaceUpdate(self)

        self.checks = {
        "Display":False
        }

    def Update(self):
        Rects(self)
        if self.checks["Display"]:
            screen.blit(self.surf, self.camRect.topleft)

        if player != None:
            if self.rect.colliderect(player.rect):
                self.func()
                if self.dis:
                    if not hasis(self, "persis"):
                        RoomoveObject(self)
                        self.func = lambda:None

class Tran(CollideFunc):
    def __init__(self, rect, func):
        super().__init__(rect, func, False)

        self.rect.x, self.rect.y = self.rect.x*bck.scale, self.rect.y*bck.scale
        self.rect.w, self.rect.h = self.rect.w*bck.scale, self.rect.h*bck.scale

class ScreenShake:
    def __init__(self):
        RoomObject(self)
        self.time = .5

        self.rhspd = (1, 3)
        self.rvspd = (1, 3)
        self.hspd = random.randint(self.rhspd[0], self.rhspd[1])
        self.vspd = random.randint(self.rvspd[0], self.rvspd[1])
        
        self.xdir = -1
        self.ydir = -1

        self.offSet = [0, 0]

        self.checks = {
            "Shake":False
            }

    def Update(self):
        global camOffset
        
        if self.checks["Shake"]:
            x = self.hspd*self.xdir
            y = self.vspd*self.ydir
            
            camOffset = [x, y]
            self.offSet = (x, y)

    def Shake(self, spd=((1, 3), (1, 3))):
        global camFreeze
        camFreeze = True
        
        ChangeCheck(self, "Shake", True)

        def xTimer():
            self.xdir *= -1
            self.hspd = random.randint(self.rhspd[0], self.rvspd[1])

            Timer(abs(self.hspd)/FPS, xTimer)
        def yTimer():
            self.ydir *= -1
            self.vspd = random.randint(self.rvspd[0], self.rvspd[1])

            Timer(abs(self.vspd/FPS), yTimer)

        xTimer()
        yTimer()
        Timer(self.time, self.Stop)

    def Stop(self):
        global camOffset, camFreeze
        camFreeze = False
        
        ChangeCheck(self, "Shake", False)
        camOffset[0] -= self.offSet[0]
        camOffset[1] -= self.offSet[1]
        self.offSet = (0, 0)

#Status Effects
def StartPoison(obj):
    if obj.checks["Poison"] or obj.checks["Invinsibility"]:
        return 0
    
    ChangeCheckPerm(obj, "Poison", True)
    AddPersis(Timer(4, lambda:StopPoison(obj)))

    def func():
        if obj.checks["Poison"]:
            obj.GetHurt(2)
            Timer(2, func)

    Timer(2, func)
    
def Poison(obj):
    SurfaceBlend(obj, green)

    obj.hspd = int(obj.hspd*.5)
    obj.vspd = int(obj.vspd*.5)

def StopPoison(obj):
    ChangeCheckPerm(obj, "Poison", False)
    if not hasattr(obj, "Sprite"):
        SurfaceUpdate(obj)
    else:
        StopSurfaceBlend(obj)

def StartFire(obj):
    if obj.checks["Fire"] or obj.checks["Invinsibility"]:
        return 0
    
    ChangeCheckPerm(obj, "Fire", True)
    AddPersis(Timer(2, lambda:StopFire(obj)))

    def func():
        if obj.checks["Fire"]:
            obj.GetHurt(1)
            Timer(.5, func)

    Timer(.5, func)

def Fire(obj):
    SurfaceBlend(obj, red)

    obj.hspd *= 2
    obj.vspd *= 2

def StopFire(obj):
    ChangeCheckPerm(obj, "Fire", False)
    if not hasattr(obj, "Sprite"):
        SurfaceUpdate(obj)
    else:
        StopSurfaceBlend(obj)

def StartConfused(obj):
    if obj.checks["Confused"] or obj.checks["Invinsibility"]:
        return 0
    
    ChangeCheckPerm(obj, "Confused", True)
    AddPersis(Timer(3, lambda:StopConfused(obj)))
    SurfaceBlend(obj, yellow)

def Confused(obj):
    SurfaceBlend(obj, yellow)

def StopConfused(obj):
    ChangeCheckPerm(obj, "Confused", False)
    if not hasattr(obj, "Sprite"):
        SurfaceUpdate(obj)
    else:
        StopSurfaceBlend(obj)

def StartFreeze(obj):
    if obj.checks["Freeze"] or obj.checks["Invinsibility"]:
        return 0
    
    ChangeCheckPerm(obj, "Freeze", True)
    AddPersis(Timer(2, lambda:StopFreeze(obj)))
    SurfaceBlend(obj, blue)

    obj.checks["Animate"] = False

def Freeze(obj):
    SurfaceBlend(obj, blue)

def StopFreeze(obj):
    ChangeCheckPerm(obj, "Freeze", False)
    if not hasattr(obj, "Sprite"):
        SurfaceUpdate(obj)
    else:
        StopSurfaceBlend(obj)
        obj.checks["Animate"] = True

def Earthquake():
    Shakey.Shake()

    for o in range(len(Objects)-1, 0, -1):
        obj = Objects[o]

        if not hasattr(obj, "Enemy"):
            continue

        obj.GetHurt(1)

def PoisonEverything():
    for o in range(len(Objects)-1, 0, -1):
        obj = Objects[o]

        if not hasattr(obj, "Enemy"):
            continue

        StartPoison(obj)

def FireEverything():
    for o in range(len(Objects)-1, 0, -1):
        obj = Objects[o]

        if not hasattr(obj, "Enemy"):
            continue

        StartFire(obj)

def ConfusedEverything():
    for o in range(len(Objects)-1, 0, -1):
        obj = Objects[o]

        if not hasattr(obj, "Enemy"):
            continue

        StartConfused(obj)

def FreezeEverything():
    for o in range(len(Objects)-1, 0, -1):
        obj = Objects[o]

        if not hasattr(obj, "Enemy"):
            continue

        StartFreeze(obj)

#Surface
def FirstSprite(obj, sprName):
    if checksHasis(obj, "Sombre"):
        if sprName[:len("Sombre")] != "Sombre":
            sprName = "Sombre"+sprName
                
    obj.Sprite = Sprite.New(sprName)
    
    obj.rect.size = obj.Sprite.rect.size
    obj.crect = pygame.Rect(obj.Sprite.crect)
    obj.crect.x += obj.rect.x
    obj.crect.y += obj.rect.y
    
    SurfaceUpdate(obj)
    
def ChangeSprite(obj, sprName):
    if obj.Sprite.name == sprName:
        if checksHasis(obj, "Sombre"):
            if sprName[:len("Sombre")] != "Sombre":
                sprName = "Sombre"+sprName
                
    if obj.Sprite.name == sprName:
        return 0
    if obj.Sprite.name[:len("Sombre")] == "Sombre":
        if checksHasis(obj, "Sombre"):
            if obj.Sprite.name[len("Sombre"):] == sprName:
                return 0
    
    oldCenter = obj.rect.center
    
    FirstSprite(obj, sprName)
    obj.rect.center = oldCenter

def ChangeColour(obj, colour):
    obj.colour = colour
    SurfaceUpdate(obj)
    
def ChangeRect(obj, rect):
    oldCenter = obj.rect.center
    obj.rect = rect
    obj.rect.center = oldCenter
        
    SurfaceUpdate(obj)

def ChangeScale(obj, scale):
    if not hasattr(obj, "Sprite"):
        newRect = pygame.Rect(obj.rect)
        newRect.w *= scale
        newRect.h *= scale
        ChangeRect(obj, newRect)
        return 0

    obj.scale *= scale
    SurfaceUpdate(obj)

def ChangeAlpha(obj, alpha):
    if obj.alpha == alpha:
        return 0
    
    obj.alpha = alpha

    if hasattr(obj, "colour"):
        oldCol = obj.colour[:3]
        oldCol = list(oldCol)

        oldCol.append(obj.alpha)
        oldCol = tuple(oldCol)
        obj.colour = oldCol

    SurfaceUpdate(obj)

def SurfaceBlend(obj, colour):
    if hasattr(obj, "Sprite"):
        if obj.blend == list(colour):
            return 0
        obj.blend = list(colour)
    else:
        oldCol = copy.deepcopy(obj.colour)
        newCol = [0, 0, 0, obj.alpha]

        for i in range(3):
            num = oldCol[i]+colour[i]
            num /= 2
            newCol[i] = num
            
        obj.colour = newCol
        
    SurfaceUpdate(obj)

    if not hasattr(obj, "Sprite"):
        obj.colour = oldCol

def StopSurfaceBlend(obj):
    obj.blend = None
    SurfaceUpdate(obj)

def SurfaceUpdate(obj):
    if not hasattr(obj, "Sprite"):
        s = pygame.Surface(obj.rect.size, pygame.SRCALPHA)
        s.fill(obj.colour)
        obj.surf = s
    else:
        oldFrameCount = obj.Sprite.frameCount
        obj.Sprite = Sprite.New(obj.Sprite.name)
        obj.Sprite.frameCount = oldFrameCount

        width, height = obj.Sprite.sprite.get_size()
        fwidth, fheight = width/obj.Sprite.frames, height

        #Scaling
        oldCenter = obj.rect.center

        newWidth = fwidth*obj.scale
        newHeight = fheight*obj.scale
        obj.rect.size = (newWidth, newHeight)
        obj.rect.center = oldCenter

        obj.Sprite.rect = pygame.Rect(obj.rect)

        newWidth = int(width*obj.scale)
        newHeight = int(height*obj.scale)
        obj.Sprite.sprite = pygame.transform.scale(obj.Sprite.sprite, (newWidth, newHeight))

        #Alpha/Blend
        finalScale = int(obj.Sprite.scale*obj.scale)
        if finalScale < 1:
            finalScale = 1

        width, height = obj.Sprite.sprite.get_size()
            
        for x in range(0, width, finalScale):
            for y in range(0, height, finalScale):
                col = obj.Sprite.sprite.get_at((x, y))
                visible = col[3] > 0

                if visible:
                    multiplier = obj.alpha/255
                    newAlpha = col[3]*multiplier

                    newCol = list(col[:3])
                    if obj.blend != None:
                        for i in range(3):
                            newCol[i] += obj.blend[i]
                            newCol[i] /= 2
                    newCol.append(newAlpha)

                    for xx in range(x, x+finalScale):
                        for yy in range(y, y+finalScale):
                            obj.Sprite.sprite.set_at((xx, yy), newCol)

#Object Funcs
def Instances(typ):
    objs = []
    for o in Objects:
        if o in Removes:
            continue

        if type(o) == typ:
            objs.append(o)
    return objs

def Collide(self):
    for o in Objects:
        if o == self:
            continue

        if hasattr(o, "crect"):
            if self.crect.colliderect(o.crect):
                if hasattr(self, "Collide"):
                    self.Collide(o)
                if checksHasis(o, "Solid"):
                    if checksHasis(self, "Colliding"):
                        return True
    return False

def WhatCollide(self):
    if Collide(self):
        for o in Objects:
            if o == self:
                continue
            
            if hasattr(o, "crect"):
                if self.crect.colliderect(o.crect):
                    if checksHasis(o, "Solid"):
                        return o

def Separate(self):
    if not checksHasis(self, "Colliding"):
        return 0
    
    if Collide(self):
        obj = WhatCollide(self)
        if obj != None:
            difx = self.crect.centerx-obj.crect.centerx
            dify = self.crect.centery-obj.crect.centery

            self.rect.x += sign(difx)
            self.rect.y += sign(dify)
            Rects(self)

def Move(self, x, y):
    if checksHasis(self, "Freeze"):
        return 0
    
    if checksHasis(self, "Confused"):
        x *= -1
        y *= -1
        
    for xx in range(abs(int(x))):
        self.rect.x += sign(x)
        Rects(self)
        
        if Collide(self):
            self.rect.x -= sign(x)
        Rects(self)

    for yy in range(abs(int(y))):
        self.rect.y += sign(y)
        Rects(self)
        
        if Collide(self):
            self.rect.y -= sign(y)
        Rects(self)

    #Direction
    if x != 0:
        if x < 0:
            self.lastH = "Left"
        elif x > 0:
            self.lastH = "Right"
        self.facing = self.lastH

    if y != 0:
        if y < 0:
            self.lastV = "Up"
        elif y > 0:
            self.lastV = "Down"
        self.facing = self.lastV

def Replace(obj, newObj):
    Explode(obj)
    newObj.rect.center = obj.rect.center

class InventoryBox:
    def Order():
        for i in Instances(InventoryBox)[::-1]:
            if i.index == len(Instances(InventoryBox))-1:
                SetPosition(i, "right", "top", screenWidth-8, 8)
            else:
                nextBox = Instances(InventoryBox)[i.index+1]
                SetPosition(i, "right", "top", nextBox.rect.left-8, 8)
            SurfaceUpdate(i)

    def __init__(self):
        self.index = len(Instances(InventoryBox))
        RoomObject(self)
        self.highDepth = True

        self.colour = midBlack
        self.alpha = 128
        self.blend = None

        self.size = 48
        self.rect = pygame.Rect(0, 0, self.size, self.size)

        InventoryBox.Order()
        self.item = None

    def Update(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.select = True
        else:
            self.select = False

        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if self.select:
                    self.Grab()

            if e.type == pygame.KEYDOWN:
                if e.key == eval("pygame.K_"+str(self.index+1)):
                    if self.item != None:
                        self.item.Use()

        if self.select:
            ChangeAlpha(self, 255)
        else:
            ChangeAlpha(self, 160)

        screen.blit(self.surf, self.rect.topleft)
        pygame.draw.rect(screen, self.colour, self.rect, 1)

        if self.boxItem != None:
            self.UpdateItem()

            w, h = self.boxItem.Sprite.sprite.get_size()
            r = pygame.Rect(0, 0, w, h)
            r.center = self.rect.center
            screen.blit(self.boxItem.Sprite.sprite, r.topleft)

            txt = str(self.index+1)
            w, h = font.size(txt)

            if w > h:
                gl = w
            else:
                gl = h

            numRect = pygame.Rect(0, 0, gl, gl)
            numRect.center = self.rect.bottomleft

            pygame.draw.ellipse(screen, black, numRect)
            text(txt, white, "centerx", "centery", numRect.centerx, numRect.centery)

    def AssignItem(self, item):
        self.item = item
        RoomoveObject(self.item)

        self.UpdateItem()

    def UpdateItem(self):
        if self.item == None:
            return 0

        self.boxItem = copy.copy(self.item)

        w, h = self.boxItem.Sprite.sprite.get_size()
        msize = self.size-8

        if w > h:
            w, h = msize, h/w*msize
        else:
            w, h = w/h*msize, msize

        self.boxItem.Sprite.sprite = pygame.transform.scale(self.boxItem.Sprite.sprite, (int(w), int(h)))

    def Remove(self):
        RoomoveObject(self)

        for i in Instances(InventoryBox):
            if i.index > self.index:
                i.index -= 1

        InventoryBox.Order()

    def Grab(self):
        self.boxItem = None
        RoomAdd(self.item)

        def func0():
            x, y = pygame.mouse.get_pos()
            x += cam[0]
            y += cam[1]

            oldCenter = self.item.rect.center
            SetPosition(self.item, "centerx", "centery", x, y)

            if Collide(self.item):
                self.item.rect.center = oldCenter

        DoCheck(lambda:pygame.mouse.get_pressed()[0], func0).endFunc = lambda:self.Release()

    def Release(self):
        if self.select:
            self.AssignItem(self.item)
        else:
            self.Remove()

def AddInventory(obj):
    if len(Instances(InventoryBox)) >= 9:
        Speech("I don't have enough space for this", player)
    invenBox = InventoryBox()
    invenBox.AssignItem(obj)

    AddPersis(invenBox)

def RemoveInventory(obj):
    for i in Instances(InventoryBox):
        if i.item == obj:
            i.Remove()
            break

def CheckInventory(obj):
    for i in Instances(InventoryBox):
        if i.item == obj:
            return True
    return False

#Parent Objects    
class Button:
    Colours = {
        (0,255,255):(255,0,255),
        (0,255,0):(255,255,0),
        (255,0,0):(255,128,0)
        }
    def __init__(self, buttonName):
        RoomObject(self)

        self.col0 = random.choice(list(Button.Colours.keys()))
        self.col1 = Button.Colours[self.col0]
        
        self.colour = self.col0
        self.textColour = self.col1

        self.buttonName = buttonName
        w, h = menuFont.size(self.buttonName)
        w += 8
        h += 4
        
        self.alpha = 255
        self.rect = pygame.Rect(0, 0, w, h)
        self.ChangeRect(self.rect)
        self.scale = 1
        self.blend = None

        SurfaceUpdate(self)

        self.checks = {
            "Display":True,
            "Grow":True,
            "Freeze":False}

    def Update(self):
        global currentHover

        if not self.checks["Freeze"]:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                currentHover = self
            elif currentHover == self:
                if not totalRect.collidepoint(pygame.mouse.get_pos()):
                    currentHover = None

            for e in events:
                if e.type == pygame.MOUSEBUTTONUP:
                    if currentHover == self:
                        self.func()

            if currentHover == None:
                ChangeAlpha(self, 255)
                if self.checks["Grow"]:
                    ChangeRect(self, self.normRect)
            elif currentHover == self:
                ChangeAlpha(self, 255)
                if self.checks["Grow"]:
                    ChangeRect(self, self.bigRect)
            else:
                ChangeAlpha(self, 64)
                if self.checks["Grow"]:
                    ChangeRect(self, self.normRect)
                
        if self.checks["Display"]:
            screen.blit(self.surf, self.rect.topleft)
            pygame.draw.rect(screen, self.textColour, self.rect, 2)
            text(self.buttonName, self.textColour, "centerx", "centery", self.rect.centerx, self.rect.centery, fnt=menuFont, alpha=self.alpha)

    def ChangeRect(self, rect):
        ChangeRect(self, rect)
        self.HoverRects()
        
    def HoverRects(self):
        self.normRect = pygame.Rect(self.rect)
        self.bigRect = pygame.Rect(self.rect)
        self.bigRect.w *= 1.5

    def Freeze(self):
        ChangeCheck(self, "Freeze", True)
        ChangeAlpha(self, 128)
            
class Lifeform:
    def HpRefill(self, amount):
        if self.hp+amount > self.mhp:
            amount = self.mhp-self.hp

        self.hp += amount

    def StamRefill(self, amount):           
        if self.stam+amount > self.mstam:
            amount = self.mstam-self.stam

        self.stam += amount
  
    def __init__(self):
        RoomObject(self)

        self.rect = pygame.Rect(0, 0, 0, 0)
        self.colour = white
        self.blend = None
        self.alpha = 255
        self.scale = 1

        SurfaceUpdate(self)

        self.ohspd = 0
        self.ovspd = 0
        self.xchange = 0
        self.ychange = 0

        self.acc = .2

        self.lastH = "Right"
        self.lastV = "Down"
        self.facing = "Down"

        self.mhp = self.hp = 3
        self.mstam = self.stam = 6

        self.bullet = Bullet

        self.bulletHspd = 4
        self.bulletVspd = 3
        self.bulletDamage = 1
        self.bulletLifetime = FPS*.75

        self.shootReload = FPS
        self.shootCount = 0

        self.checks = {
            "Display":True,
            "Animate":True,
            "Solid":True,
            "Sombre":Sombre,
            "Moving":True,
            "Colliding":True,
            "Shooting":True,
            "Invinsibility":False,
            "Poison":False,
            "Fire":False,
            "Confused":False,
            "Freeze":False,
            "Dead":False
            }

    def Update(self):        
        Rects(self)
        Separate(self)
        if not CheckSpeech():
            Outside(self)

        self.hspd = copy.deepcopy(self.ohspd)
        self.vspd = copy.deepcopy(self.ovspd)

        if self.checks["Shooting"]:
            if self.shootCount < self.shootReload:
                self.shootCount += 1
                
        if self.checks["Invinsibility"]:
            SurfaceBlend(self, white)
        else:
            if self.checks["Poison"]:
                Poison(self)
            if self.checks["Fire"]:
                Fire(self)
            if self.checks["Confused"]:
                Confused(self)
            if self.checks["Freeze"]:
                Freeze(self)

        if abs(self.xchange) > abs(self.hspd):
            self.xchange = sign(self.xchange)*self.hspd
        if abs(self.ychange) > abs(self.vspd):
            self.ychange = sign(self.ychange)*self.vspd

        if self.checks["Display"]:
            if not hasattr(self, "Sprite"):
                screen.blit(self.surf, self.camRect.topleft)
            else:
                if self.checks["Animate"]:
                    self.Sprite.Animate()
                screen.blit(self.Sprite.sprite, self.camRect.topleft, self.Sprite.showRect)

    def DrawStats(self, stats=[]):
        #Stats
        '''
        stat, maxStat, col
        '''

        if stats == []:
            stats = self.DrawStats

        totalHeight = 0
        padding = 2
        
        for s in stats:
            stat = s[0]
            maxStat = s[1]
            col = s[2]
            
            bckRect = pygame.Rect(0, 0, self.rect.w, 6)
            SetPosition(bckRect, "centerx", "bottom", self.camRect.centerx, self.camRect.top-4-totalHeight)

            statRect = pygame.Rect(bckRect.x+padding, bckRect.y+padding,
                                   stat/maxStat*(bckRect.w-padding*2), bckRect.h-(padding*2))

            pygame.draw.rect(screen, black, bckRect)
            if stat > 0:
                pygame.draw.rect(screen, col, statRect)

            totalHeight += bckRect.h+2

    def Okay(self):
        if self.checks["Poison"]:
            return False
        if self.checks["Fire"]:
            return False
        if self.checks["Invinsibility"]:
            return False
        if self.checks["Poison"]:
            return False

        return True

    def Invinsible(self):
        ChangeCheckPerm(self, "Invinsibility", True)
        SurfaceBlend(self, white)

    def StopInvinsible(self):
        ChangeCheckPerm(self, "Invinsibility", False)
        StopSurfaceBlend(self)

    def Shoot(self, dr):
        b = self.bullet()
        b.AssignOwner(self)

        if dr[0] < 0:
            b.rect.right = self.rect.left
        elif dr[0] > 0:
            b.rect.left = self.rect.right

        if dr[1] < 0:
            b.rect.bottom = self.rect.top
        elif dr[1] > 0:
            b.rect.top = self.rect.bottom
        
        b.dr = dr
        b.rect.x += dr[0]
        b.rect.y += dr[1]

        self.shootCount = 0

    def GetHurt(self, amount):
        if issubclass(type(self), Player):
            if not WhenNormal():
                return 0

        if self.checks["Invinsibility"]:
            return 0
        
        if not hasattr(self, "Sprite"):
            dt = DoTimer(.25, lambda:SurfaceBlend(self, red))
            dt.endFunc = lambda:SurfaceUpdate(self)
            AddPersis(dt)
        else:
            if self.Okay():
                SurfaceBlend(self, red)
                AddPersis(Timer(.25, lambda:StopSurfaceBlend(self)))

        if self.hp > amount:
            self.hp -= amount
        else:
            self.hp = 0
            if not self.checks["Dead"]:
                self.Die()

        GetHurtSound.play()

    def BulletHurt(self, bullet):
        self.GetHurt(bullet.damage)
        Removes.append(bullet)

    def Die(self):
        ChangeCheck(self, "Dead", True)
        Explode(self)

        DieSound.play()

class Bullet:
    def __init__(self):
        RoomObject(self)
        self.removeTran = True

        self.rect = pygame.Rect(0, 0, 10, 10)
        self.colour = black
        self.alpha = 255
        self.scale = 1
        ChangeAlpha(self, 128)
        SurfaceUpdate(self)

        self.dr = (0, 0)
        self.hspd = 0
        self.vspd = 0
        
        self.damage = 0
        self.lifetime = 0
        self.lifetimeCount = 0

        self.checks = {
            "Display":True,
            "Solid":False,
            "Moving":True,
            "Colliding":False,
            "Damage":True,
            "Living":True
            }

    def Update(self):
        Rects(self)
        
        if self.checks["Moving"]:
            xchange = self.dr[0]*self.hspd
            ychange = self.dr[1]*self.vspd

            Move(self, xchange, ychange)

        if self.checks["Living"]:
            if self.lifetimeCount < self.lifetime:
                self.lifetimeCount += 1
            else:
                RoomoveObject(self)
                return 0
            
        if self.checks["Display"]:
            screen.blit(self.surf, self.camRect.topleft)

    def Collide(self, obj):
        if issubclass(type(obj), Player) and not checksHasis(obj, "Control"):
            return 0
        if hasis(self.owner, "Enemy") and hasis(obj, "Enemy"):
            return 0

        if self.checks["Damage"]:
            if obj != self.owner:
                if hasattr(obj, "BulletHurt"):
                    obj.BulletHurt(self)
                    if "BonusDamage" in dir(self):
                        try:
                            self.BonusDamage(obj)
                        except:
                            pass
                    ChangeCheck(self, "Damage", False)
                if checksHasis(obj, "Solid"):
                    RoomoveObject(self)

    def AssignOwner(self, owner):
        self.owner = owner
        
        self.hspd = owner.bulletHspd
        self.vspd = owner.bulletVspd
        
        self.damage = owner.bulletDamage
        self.lifetime = owner.bulletLifetime

        ChangeScale(self, self.damage)
        self.rect.center = owner.rect.center
        
class Player(Lifeform):
    def __init__(self):
        super().__init__()
        self.Objects = {}

        if not hasattr(self, "clothes"):
            self.clothes = ""
        FirstSprite(self, self.clothes+self.name+"IdleDown")

        self.lifeOrbSprite = Sprite.New("OrbLife")
        self.lifeOrbRect = pygame.Rect(self.lifeOrbSprite.rect)

        self.ohspd = 5
        self.ovspd = 4
        self.acc = .75

        self.mhp = self.hp = 10
        self.hpCol = white

        self.bulletHspd = 15
        self.bulletVspd = 9

        self.shootReload = FPS*.35
        self.bulletLifetime = 24

        self.safe = True
        self.Interact = None
        self.Ignores = []

        self.leftMoveKey = pygame.K_LEFT
        self.rightMoveKey = pygame.K_RIGHT
        self.upMoveKey = pygame.K_UP
        self.downMoveKey = pygame.K_DOWN

        self.leftShootKey = pygame.K_a
        self.rightShootKey = pygame.K_d
        self.upShootKey = pygame.K_w
        self.downShootKey = pygame.K_s
        self.powerKey = pygame.K_q

        self.dashKey = pygame.K_LSHIFT
        self.InteractSwitchKey = pygame.K_SPACE
        self.deselectKey = pygame.K_LCTRL

        ChangeCheckNow(self, "Control", True)
        ChangeCheckNow(self, "Hide", False)
        ChangeCheckNow(self, "Solid", False)

        ChangeCheckNow(self, "Input", True)
        ChangeCheckNow(self, "CanDash", True)
        ChangeCheckNow(self, "Dash", False)

        if not hasattr(self, "self.ochecks"):
            self.ochecks = {}

    def Update(self):
        global player, camTarget
        
        super().Update()

        #Both control or no control
        if self.checks["Display"]:
            self.DrawStats([
                (self.stam, self.mstam, green),
                (self.hp, self.mhp, self.hpCol)
                ])

            self.DisplayInteract()

        #Must be in control
        if self.checks["Control"]:
            if self.CheckDanger():
                PlaySong("FightMusic", .2)
                self.safe = False
            else:
                if not self.safe:
                    def func():
                        if not self.CheckDanger():
                            PlaySong("BackgroundMusic")
                    t = Timer(5, func)
                    AddPersis(t)

                    self.safe = True
                    Check(lambda:not self.safe, lambda:RoomoveObject(t))

            if self.checks["Moving"]:                            
                xdr = pygame.key.get_pressed()[self.rightMoveKey]-pygame.key.get_pressed()[self.leftMoveKey]
                if xdr != 0:
                    self.xchange += sign(xdr)*self.acc
                elif self.xchange != 0:
                    self.xchange -= sign(self.xchange)*self.acc

                    if abs(self.xchange) < self.acc:
                        self.xchange = 0

                ydr = pygame.key.get_pressed()[self.downMoveKey]-pygame.key.get_pressed()[self.upMoveKey]
                if ydr != 0:
                    self.ychange += sign(ydr)*self.acc
                elif self.ychange != 0:
                    self.ychange -= sign(self.ychange)*self.acc

                    if abs(self.ychange) < self.acc:
                        self.ychange = 0
                
                if self.checks["Input"]:
                    for e in events:
                        if e.type == pygame.KEYDOWN:
                            if e.key == self.InteractSwitchKey:
                                if self.Interact != None:
                                    self.Ignores.append(self.Interact)
                                    StopSurfaceBlend(self.Interact)
                                    self.Interact = None
                                    
                                    self.FindInteract()
                                    if self.Interact == None:
                                        self.Ignores = []
                                        self.FindInteract()

                            if e.key == self.powerKey:
                                self.Power()
                                        
                            if e.key == self.dashKey:
                                moving = self.xchange != 0 or self.ychange != 0
                                if moving:
                                    self.StartDash()
                                    
                if self.Interact == None:
                    self.FindInteract()
                else:
                    self.LoseInteract()

                if self.checks["Dash"]:
                    moving = self.xchange != 0 or self.ychange != 0
                    if moving:
                        self.Dash(self.xchange, self.ychange)
                    else:
                        ChangeCheck(self, "Dash", False)
                else:
                    Move(self, self.xchange, self.ychange)

                self.SetSprite()
                    
                if self.checks["Shooting"]:
                    if self.shootCount >= self.shootReload:
                        if pygame.key.get_pressed()[self.leftShootKey]:
                            self.Shoot((-1, 0))
                        elif pygame.key.get_pressed()[self.rightShootKey]:
                            self.Shoot((1, 0))
                        elif pygame.key.get_pressed()[self.upShootKey]:
                            self.Shoot((0, -1))
                        elif pygame.key.get_pressed()[self.downShootKey]:
                            self.Shoot((0, 1))
            else:
                ChangeSprite(self, self.clothes+self.name+"IdleDown")

    def SetSprite(self):
        if self.xchange == 0:
            if self.ychange != 0:
                ChangeSprite(self, self.clothes+self.name+"Run"+self.lastV)
            else:
                if self.facing == self.lastV:
                    ChangeSprite(self, self.clothes+self.name+"Idle"+self.lastV)
                else:
                    ChangeSprite(self, self.clothes+self.name+"IdleDown")
        else:
            ChangeSprite(self, self.clothes+self.name+"Run"+self.lastH)

    def SetClothes(self, name):
        self.clothes = name
        self.SetSprite()

    def Collide(self, obj):
        if hasis(obj, "pickup"):
            obj.func()

        if type(obj) == Block:
            obj.Push(self)

    def Die(self):
        ChangeCheck(self, "Dead", True)
        GameOver()

    def BulletHurt(self, bullet):
        if issubclass(type(bullet.owner), Player):
            return 0

        super().BulletHurt(bullet)

    def Control(self):
        ChangeCheckPerm(self, "Control", True)
        ChangeCheckPerm(self, "Hide", False)

        ChangeCheck(self, "Colliding", True)

        if self not in PersisObjects:
            AddPersis(self)
        ChangeAlpha(self, 255)

        self.ShowObjects()

    def Hide(self):
        ChangeCheckPerm(self, "Hide", True)
        
        ChangeCheck(self, "Colliding", False)
        ChangeCheckPerm(self, "Control", False)

        RemovePersis(self)
        ChangeSprite(self, self.clothes+self.name+"IdleDown")
        ChangeAlpha(self, 128)

        self.HideObjects()

    def AddObject(self, obj):
        if CurrentRoom not in self.Objects:
            self.Objects[CurrentRoom] = []

        self.Objects[CurrentRoom].append(obj)

        if player != self:
            RoomoveObjectPlayer(obj, self)

    def ShowObjects(self):
        if CurrentRoom not in self.Objects:
            return 0

        for o in self.Objects[CurrentRoom]:
            RoomAdd(o)

    def HideObjects(self):
        if CurrentRoom not in self.Objects:
            return 0

        myObjects = []
        for o in self.Objects[CurrentRoom]:
            myObjects.append(o)

        for o in myObjects:
            RoomoveObjectPlayer(o, self)

    def Power(self):
        if self.stam != self.mstam:
            return 0
        self.stam = 0

        self.Invinsible()
        Timer(4, lambda:self.StopInvinsible())

        if self.bullet == Bullet:
            Earthquake()
        elif self.bullet == PoisonBullet:
            PoisonEverything()
        elif self.bullet == FireBullet:
            FireEverything()
        elif self.bullet == ConfusedBullet:
            ConfusedEverything()
        elif self.bullet == FreezeBullet:
            FreezeEverything()

    def StartDash(self):
        if not self.checks["CanDash"]:
            return 0
        if self.checks["Dash"]:
            return 0
        
        if self.stam >= 2 and not self.checks["Dash"]:
            ChangeCheck(self, "Dash", True)
            self.stam -= 2
            
            def func():
                ChangeCheck(self, "Dash", False)
            AddPersis(Timer(5/FPS, func))

            def func():
                if self.checks["Dash"]:
                    Shadow(self)
                    Timer(2/FPS, func)
            Shadow(self)
            Timer(2/FPS, func)

            DashSound.play()

    def Dash(self, xchange, ychange):
        xchange *= 5
        ychange *= 5

        Move(self, xchange, ychange)

    def FindInteract(self):
        if self.Interact != None:
            return 0
        
        close = None
        
        for o in Objects:
            if type(o) != Interact and not issubclass(type(o), Interact):
                continue
            if not o.checks["Interact"]:
                continue
            if o in self.Ignores:
                continue

            if dist(self, o) <= minDist(self, o)+24:
                if close == None:
                    close = o
                elif dist(self, o) < dist(self, close):
                    close = o

        self.Interact = close
        if self.Interact != None:
            SurfaceBlend(self.Interact, white)

    def LoseInteract(self):
        if dist(self, self.Interact) > minDist(self, self.Interact)+24:
            self.ForseLoseInteract()
        elif self.Interact not in Objects:
            self.ForseLoseInteract()
        elif not self.Interact.checks["Interact"]:
            self.ForseLoseInteract()

    def ForseLoseInteract(self):
        if self.Interact == None:
            return 0

        StopSurfaceBlend(self.Interact)
        self.Interact = None

    def DisplayInteract(self):
        if self.Interact == None:
            return 0

        totalHeight = 0
        for i in list(self.Interact.interactions.keys())[::-1]:
            string = self.Interact.interactions[i][0]
            if string == "":
                continue
            string = i.upper()+": "+string
            w, h = font.size(string)
            w += 8
            h += 4

            rect = pygame.Rect((0, 0), (w, h))
            rect.bottomleft = self.Interact.camRect.topleft
            rect.y -= 4
            rect.y -= totalHeight

            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            if hasattr(self.Interact, "speechColour") and not Sombre:
                col = self.Interact.speechColour
            else:
                col = midBlack

            totalHue = col[0]+col[1]+col[2]
            if totalHue > 255*3/2:
                textCol = midBlack
            else:
                textCol = midWhite
                
            surf.fill((col[0], col[1], col[2], 196))
            screen.blit(surf, rect.topleft)
            text(string, textCol, "left", "top", rect.left+4, rect.top+2)

            totalHeight += rect.h+2

    def CheckDanger(self):
        Threats = [
            "Find",
            "Chase"
            ]
        
        for o in Objects:
            if not issubclass(type(o), Enemy):
                continue

            if o.state in Threats:
                return True

class Enemy(Lifeform):
    def __init__(self):
        super().__init__()
        self.Enemy = True
        ChangeCheckPerm(self, "Angry", True)

        self.mhp = self.hp = 4

        self.state = None
        self.sightRange = 160
        self.fleeRange = 240

        self.ohspd = 2
        self.ovspd = 2

    def Update(self):
        super().Update()

        if self.checks["Display"]:
            self.DrawStats([
                (self.hp, self.mhp, red)
                ])

        if self.state == None:
            self.Idle()

        if not self.checks["Angry"]:
            return 0

        if self.state == "Idle":
            if player != None:
                if dist(self, player) <= self.sightRange:
                    self.state = "Chase"
                else:
                    if self.idleCount < self.idleMax:
                        self.idleCount += 1
                    else:
                        self.Wander()

        if self.state == "Wander":
            if player != None:
                if dist(self, player) <= self.sightRange:
                    self.state = "Chase"
            else:
                if self.wanderCount < self.wanderMax:
                    self.wanderCount += 1
                else:
                    self.Idle()

        if self.state == "Find" and self.checks["Moving"]:
            if player != None:
                if dist(self, player) <= self.sightRange:
                    self.state = "Chase"
                else:
                    if self.findCount < self.findMax:
                        self.findCount += 1
                    else:
                        self.Idle()

        if self.state == "Chase":
            if player != None:
                if dist(self, player) > self.fleeRange:
                    self.Idle()

    def Count():
        count = 0
        for o in Objects:
            if issubclass(type(o), Enemy):
                count += 1
        return count

    def Die(self):
        super().Die()
        for i in range(random.randint(1, 3)):
            Drop(self, LifeOrb())

        if random.randint(0, 3) == 0:
            Drop(self, eval(random.choice(["PoisonOrb",
                                           "FireOrb",
                                           "ConfusedOrb",
                                           "FreezeOrb"])+"()"))

    def Collide(self, obj):
        if self.state == "Wander":
            self.Idle()

    def BulletHurt(self, bullet):
        super().BulletHurt(bullet)
        if player != None:
            if bullet.owner == player:
                self.Find()

    def Idle(self):
        self.state = "Idle"

        self.idleMax = FPS*random.randint(2, 5)
        self.idleCount = 0

    def Wander(self):
        self.state = "Wander"
        
        self.wanderMax = FPS*random.randint(1, 3)
        self.wanderCount = 0

    def Find(self):
        self.state = "Find"

        self.findMax = FPS*random.randint(8, 12)
        self.findCount = 0

class Ghost(Enemy):
    def __init__(self):
        super().__init__()
        FirstSprite(self, "Ghost")
        self.speechColour = black
        
        self.shootReload = FPS*1.25
        self.bulletLifetime = FPS*.75
        
    def Update(self):
        super().Update()

        if self.state == "Chase":
            if player != None:
                if self.checks["Moving"]:
                    xchange = player.rect.centerx-self.rect.centerx
                    if abs(xchange) > self.hspd:
                        xchange = sign(xchange)*self.hspd

                    ychange = player.rect.centery-self.rect.centery
                    if abs(ychange) > self.vspd:
                        ychange = sign(ychange)*self.vspd

                    if dist(self, player) > minDist(self, player)*1.5:
                        Move(self, xchange, ychange)

                if self.checks["Shooting"]:
                    if self.shootCount >= self.shootReload:
                        x = player.rect.centerx-self.rect.centerx
                        y = player.rect.centery-self.rect.centery

                        if abs(x) < player.rect.w/2:
                            x = 0
                        else:
                            x = sign(x)

                        if abs(y) < player.rect.h/2:
                            y = 0
                        else:
                            y = sign(y)

                        self.Shoot((x, y))

        elif self.state == "Wander":
            if self.checks["Moving"]:
                xchange, ychange = self.dr
                self.hspd = int(self.hspd*.5)
                self.vspd = int(self.vspd*.5)

                if self.hspd == 0:
                    self.hspd = sign(self.ohspd)
                if self.vspd == 0:
                    self.vspd = sign(self.ohspd)
                
                xchange *= self.hspd
                ychange *= self.vspd
                Move(self, xchange, ychange)

        elif self.state == "Find":
            xchange = player.rect.centerx-self.rect.centerx
            if abs(xchange) > self.hspd:
                xchange = sign(xchange)*self.hspd

            ychange = player.rect.centery-self.rect.centery
            if abs(ychange) > self.vspd:
                ychange = sign(ychange)*self.vspd

            Move(self, xchange, ychange)

    def Wander(self):
        super().Wander()
        self.dr = (random.choice([-1, 1]), random.choice([-1, 1]))

class GhostPoison(Ghost):
    def __init__(self):
        super().__init__()
        ChangeSprite(self, "GhostPoison")

        self.speechColour = green
        self.bullet = PoisonBullet

class GhostFire(Ghost):
    def __init__(self):
        super().__init__()
        ChangeSprite(self, "GhostFire")

        self.speechColour = red
        self.bullet = FireBullet
        
class GhostConfused(Ghost):
    def __init__(self):
        super().__init__()
        ChangeSprite(self, "GhostConfused")

        self.speechColour = yellow
        self.bullet = ConfusedBullet

class GhostFreeze(Ghost):
    def __init__(self):
        super().__init__()
        ChangeSprite(self, "GhostFreeze")

        self.speechColour = blue
        self.bullet = FreezeBullet

def RandomGhost():
    Ghosts = [
    GhostPoison,
    GhostFire,
    GhostConfused,
    GhostFreeze
    ]
    return random.choice(Ghosts)()

class Jumpy(Enemy):
    def __init__(self, gen=1):
        super().__init__()
        self.name = "Jumpy"

        FirstSprite(self, self.name+"Idle")
        self.speechColour = midBlack

        self.sightRange = 320
        self.fleeRange = 480

        self.moving = False
        self.gen = gen

        self.bulletDamage = self.gen
        self.bulletLifetime = self.gen*FPS*.75

        self.shootReload = FPS*self.gen

        ChangeScale(self, self.gen)

        self.restTime = self.gen*1.5
        self.mhp = self.hp = self.gen**2*3
        self.stopDamage = False

    def Update(self):
        super().Update()

        if self.state == "Idle" and not self.moving:
            ChangeSprite(self, self.name+"Idle")

        if self.state == "Wander":
            self.Move(self.hspd*random.randint(-1, 1), self.vspd*random.randint(-1, 1))

        if self.state == "Chase" or self.state == "Find":
            x = sign(player.rect.centerx-self.rect.centerx)
            y = sign(player.rect.centery-self.rect.centery)
            self.Move(x*self.hspd, y*self.vspd)

            if self.checks["Shooting"]:
                if self.shootCount >= self.shootReload:
                    x = player.rect.centerx-self.rect.centerx
                    y = player.rect.centery-self.rect.centery

                    if abs(x) < player.rect.w/2:
                        x = 0
                    else:
                        x = sign(x)

                    if abs(y) < player.rect.h/2:
                        y = 0
                    else:
                        y = sign(y)

                    self.Shoot((x, y))

    def Move(self, xchange, ychange):
        if not self.checks["Moving"] or (xchange == 0 and ychange == 0):
            return 0

        self.checks["Moving"] = False
        self.moving = True

        ChangeSprite(self, self.name+"Jump")

        def endFunc():
            def func0():
                self.checks["Moving"] = True
            self.moving = False
            self.stopDamage = False

            Timer(self.restTime, func0)
            ChangeSprite(self, self.name+"Idle")

            if self.gen > 1:
                Shakey.Shake()
        DoCheck(lambda:self.Sprite.frameCount!=self.Sprite.frames-1, lambda:Move(self, xchange, ychange)).endFunc = endFunc

    def BulletHurt(self, bullet):
        if self.stopDamage:
            return 0

        if self.moving:
            self.stopDamage = True

        super().BulletHurt(bullet)

    def Die(self):
        super().Die()
        if self.gen > 1:
            for i in range(2):
                Drop(self, Jumpy(self.gen-1))

class JumpyRandom(Jumpy):
    def __init__(self, gen=1):
        super().__init__(gen)

        self.name = "JumpyRandom"
        self.bullet = RandomBullet()

    def Shoot(self, xy):
        super().Shoot(xy)
        self.bullet = RandomBullet()

class EPerson(Enemy):
    def __init__(self, name):
        super().__init__()

        self.name = name
        FirstSprite(self, self.name+"IdleDown")

        self.mhp = self.hp = player.mhp

        self.lastH = "Right"
        self.lastV = "Down"

    def Update(self):
        super().Update()

        if self.state == "Idle":
            ChangeSprite(self, self.name+"Idle"+self.lastV)

        if self.state == "Chase" or self.state == "Find":
            if player != None:
                if self.checks["Moving"]:
                    xchange = player.rect.centerx-self.rect.centerx
                    if abs(xchange) > self.hspd:
                        xchange = sign(xchange)*self.hspd

                    ychange = player.rect.centery-self.rect.centery
                    if abs(ychange) > self.vspd:
                        ychange = sign(ychange)*self.vspd

                    if dist(self, player) > minDist(self, player)*1.5:
                        self.Move(xchange, ychange)

                if self.checks["Shooting"] and self.state == "Chase":
                    if self.shootCount >= self.shootReload:
                        x = player.rect.centerx-self.rect.centerx
                        y = player.rect.centery-self.rect.centery

                        if abs(x) < player.rect.w/2:
                            x = 0
                        else:
                            x = sign(x)

                        if abs(y) < player.rect.h/2:
                            y = 0
                        else:
                            y = sign(y)

                        self.Shoot((x, y))

    def Move(self, xchange, ychange):
        if xchange != 0:
            ChangeSprite(self, self.name+"Run"+self.lastH)
        elif ychange != 0:
            ChangeSprite(self, self.name+"Run"+self.lastV)

        Move(self, xchange, ychange)

class Private(Enemy):
    def __init__(self):
        super().__init__()

        FirstSprite(self, "PrivateIdle")
        self.speechColour = (85, 10, 25)

        self.sightRange = 320
        self.fleeRange = 384

        self.bullet = PrivateBullet
        self.shootReload = FPS*(2/3)

        self.bulletHspd = 8
        self.bulletVspd = 6

        self.moving = False
        self.stopHurt = False

    def Update(self):
        super().Update()

        if self.state == "Chase" or self.state == "Find":
            if player != None:
                if self.checks["Shooting"] and not self.moving:
                    if self.shootCount >= self.shootReload:
                        x = player.rect.centerx-self.rect.centerx
                        y = player.rect.centery-self.rect.centery

                        if abs(x) < player.rect.w/2:
                            x = 0
                        else:
                            x = sign(x)

                        if abs(y) < player.rect.h/2:
                            y = 0
                        else:
                            y = sign(y)

                        self.Shoot((x, y))

                if self.checks["Moving"]:
                    xchange = player.rect.centerx-self.rect.centerx
                    if abs(xchange) > self.hspd:
                        xchange = sign(xchange)*self.hspd

                    ychange = player.rect.centery-self.rect.centery
                    if abs(ychange) > self.vspd:
                        ychange = sign(ychange)*self.vspd

                    if dist(self, player) > minDist(self, player)*1.5:
                        self.Move(xchange, ychange)

    def Move(self, xchange, ychange):
        if self.moving:
            return 0

        self.moving = True
        self.stopHurt = True

        ChangeSprite(self, "PrivateHide")

        def AMove():
            def Return():
                ChangeSprite(self, "PrivateShow")

                ChangeCheckPerm(self, "Display", True)
                ChangeCheckPerm(self, "Solid", True)

                def Return():
                    ChangeSprite(self, "PrivateIdle")
                    self.stopHurt = False

                    def MoveAgain():
                        self.moving = False
                    AddPersis(Timer(3, MoveAgain))
                    ChangeCheckPerm(self, "Shooting", True)

                AddPersis(Check(lambda:self.Sprite.frameCount==self.Sprite.frames-1, Return))

            ChangeCheckPerm(self, "Display", False)
            ChangeCheckPerm(self, "Solid", False)
            ChangeCheckPerm(self, "Shooting", False)

            dt = DoTimer(2, lambda:Move(self, xchange, ychange))
            dt.endFunc = Return
        AddPersis(Check(lambda:self.Sprite.frameCount==self.Sprite.frames-1, AMove))

    def BulletHurt(self, bullet):
        if self.stopHurt:
            return 0

        super().BulletHurt(bullet)
        if issubclass(type(bullet.owner), Player):
            StartFreeze(bullet.owner)

class GraceDoll(Enemy):
    def __init__(self):
        super().__init__()

        FirstSprite(self, "DollEnemyIdle")

        self.sightRange = 320
        self.fleeRange = 384

        self.bullet = FireBullet
        self.shootReload = FPS*(4/6)

        self.bulletHspd = 5
        self.bulletVspd = 3

        self.ohspd = 1
        self.ovspd = 1

    def Update(self):
        super().Update()

        if self.state == "Chase" or self.state == "Find":
            if player != None:
                if self.checks["Shooting"]:
                    if self.shootCount >= self.shootReload:
                        x = player.rect.centerx-self.rect.centerx
                        y = player.rect.centery-self.rect.centery

                        if abs(x) < player.rect.w/2:
                            x = 0
                        else:
                            x = sign(x)

                        if abs(y) < player.rect.h/2:
                            y = 0
                        else:
                            y = sign(y)

                        self.Shoot((x, y))

                if self.checks["Moving"]:
                    xchange = player.rect.centerx-self.rect.centerx
                    if abs(xchange) > self.hspd:
                        xchange = sign(xchange)*self.hspd

                    ychange = player.rect.centery-self.rect.centery
                    if abs(ychange) > self.vspd:
                        ychange = sign(ychange)*self.vspd

                    if dist(self, player) > minDist(self, player)*1.5:
                        Move(self, xchange, ychange)

class PickUp:
    def __init__(self, dis=True):
        RoomObject(self)
        self.pickup = True

        self.rect = pygame.Rect(0, 0, 0, 0)
        self.colour = red
        self.blend = None
        self.alpha = 255
        self.scale = 1

        self.checks = {
            "Display":True,
            "Solid":False,
            "Colliding":True
            }

        if dis:
            Timer(10, lambda:RoomoveObject(self))

    def Update(self):
        Rects(self)
        Outside(self)
        
        if self.checks["Display"]:
            screen.blit(self.Sprite.sprite, self.camRect.topleft)

    def func(self):
        Objects.remove(self)

class Wall:
    def __init__(self, size=(0, 0)):
        RoomObject(self)

        self.rect = pygame.Rect(0, 0, size[0], size[1])
        Rects(self)
        
        self.colour = white
        self.blend = None
        self.alpha = 255
        self.scale = 1
        
        SurfaceUpdate(self)

        self.checks = {
            "Display":False,
            "Solid":True,
            "Sombre":Sombre,
            "Colliding":True,
            "Animate":True
            }

    def Update(self):
        Rects(self)
        Outside(self)
        
        if self.checks["Display"]:
            if not hasattr(self, "Sprite"):
                screen.blit(self.surf, self.camRect.topleft)
            else:
                if self.checks["Animate"]:
                    self.Sprite.Animate()
                screen.blit(self.Sprite.sprite, self.camRect.topleft, self.Sprite.showRect)

class Block(Wall):
    def __init__(self):
        super().__init__()
        ChangeCheckPerm(self, "Display", True)

        ChangeColour(self, midBlack)
        ChangeAlpha(self, 160)

        self.pushX = 0
        self.pushY = 0

        self.ox = 0
        self.oy = 0

        self.hspd = 4
        self.vspd = 3

    def Update(self):
        super().Update()

        Separate(self)

    def Push(self, obj):
        if obj.crect.centery > self.crect.top and obj.crect.centery < self.crect.bottom:
            self.rect.x += sign(obj.xchange)
            if Collide(self):
                self.rect.x -= sign(obj.xchange)

            if obj.xchange > 0:
                obj.crect.right = self.crect.left
            elif obj.xchange < 0:
                obj.crect.left = self.crect.right

        if obj.crect.centerx > self.crect.left and obj.crect.centerx < self.crect.right:
            self.rect.y += sign(obj.ychange)
            if Collide(self):
                self.rect.y -= sign(obj.ychange)

            if obj.ychange > 0:
                obj.crect.bottom = self.crect.top
            elif obj.ychange < 0:
                obj.crect.top = self.crect.bottom

class JustThere(Wall):
    def __init__(self):
        super().__init__()
        ChangeCheckPerm(self, "Solid", False)
        ChangeCheckPerm(self, "Colliding", False)
        ChangeCheckPerm(self, "Display", True)

class Particle(JustThere):
    def __init__(self, colour):
        super().__init__()
        self.highDepth = True
        self.removeTran = True

        ChangeColour(self, colour)
        ChangeAlpha(self, random.randint(64, 160))

        size = random.randint(4, 12)
        rect = pygame.Rect(0, 0,size,size)
        ChangeRect(self, rect)

        self.checks["Colliding"] = False

    def Update(self):
        super().Update()

        if self.finishDrop:
            Removes.append(self)

class Shadow(JustThere):
    def __init__(self, obj):
        super().__init__()
        self.Sprite = copy.copy(obj.Sprite)
        self.Sprite.sprite = obj.Sprite.sprite.copy()
        self.removeTran = True
        
        self.scale = obj.scale
        self.blend = obj.blend

        SetPosition(self, "centerx", "centery", obj.rect.centerx, obj.rect.centery)
        self.count = FPS

        ChangeCheck(self, "Animate", False)
        self.Sprite.showRect = obj.Sprite.showRect
        SurfaceUpdate(self)

        def func():
            if self.alpha > 75:
                ChangeAlpha(self, self.alpha-75)
                Timer(.1, func)
            else:
                RoomoveObject(self)
        func()

    def Update(self):
        super().Update()

class Interact(Wall):
    def __init__(self):
        super().__init__()
        ChangeCheckPerm(self, "Interact", False)
        ChangeCheckPerm(self, "Display", True)

        self.interactions = {} #Key : (Name, Func, Dissapear)
        self.Removes = []

    def Update(self):
        super().Update()
        self.Input()
                                                
        for r in self.Removes:
            self.RemoveInteraction(r)
        self.Removes = []

    def Input(self):
        if player == None:
            return 0
        if not player.checks["Input"]:
            return 0
        
        if player.Interact != self:
            return 0
        if len(self.interactions.keys()) == 0:
            return 0
        
        for e in events:
            if e.type == pygame.KEYDOWN:
                for i in self.interactions:
                    key = i.lower()
                    if e.unicode == key:
                        func = self.interactions[i][1]
                        if func != None:
                            if self.interactions[i][2]:
                                self.Removes.append(i)
                            func()
                            player.ForseLoseInteract()

    def AssignInteraction(self, key, name, func, dissapear):
        self.interactions[key.upper()] = (name, func, dissapear)
        ChangeCheckPerm(self, "Interact", True)

    def RemoveInteraction(self, key):
        key = key.upper()

        if key not in self.interactions:
            return 0

        self.interactions.pop(key.upper())
        
        if len(list(self.interactions.keys())) == 0:
            ChangeCheckPerm(self, "Interact", False)

    def RemoveAllInteractions(self):
        for i in self.interactions:
            self.Removes.append(i)
        ChangeCheckPerm(self, "Interact", False)

    def GetFunc(self, key):
        return self.interactions[key.upper()][1]

class InteractChar(Interact):
    def __init__(self):
        super().__init__()

        ChangeCheck(self, "Solid", False)
        FirstSprite(self, self.name+"IdleDown")

class InventoryInteract(Interact):
    def __init__(self):
        super().__init__()
        ChangeCheckPerm(self, "Solid", False)

        def func():
            StopSurfaceBlend(self)
            AddInventory(self)
        self.AssignInteraction("P", "Pickup", func, False)

    def Update(self):
        super().Update()

        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0] and self.camRect.collidepoint(pygame.mouse.get_pos()):
                    AddInventory(self)
                    for i in Instances(InventoryBox):
                        if i.item == self:
                            i.Grab()

    def Use(self):
        if player != None:
            Speech("I can't use that here", player)

class Box(Interact):
    def Open(self):
        if issubclass(type(self.item), InventoryInteract):
            AddInventory(self.item)
        else:
            RoomAdd(self.item)
            self.item.rect.center = self.rect.center

        RoomoveObject(self)

        if hasattr(self, "BonusOpen"):
            self.BonusOpen()

    def __init__(self, item=None):
        super().__init__()
        FirstSprite(self, random.choice(["BoxSmall", "BoxMed"]))
        RandomSpawn(self)

        self.item = item
        self.AssignInteraction("O", "Open", self.Open, True)

class Milk(InventoryInteract):
    def __init__(self):
        super().__init__()

        self.fill = 3
        FirstSprite(self, "Milk"+str(self.fill)+"3")

    def Use(self):
        if self.fill > 0:
            if player != None:
                if player.hp == player.mhp:
                    Speech("I already have full health", player)
                    return 0

                player.hp = player.mhp
                self.Empty()

    def Empty(self):
        self.fill -= 1

        if self.fill > 0:
            ChangeSprite(self, "Milk"+str(self.fill)+"3")
        else:
            for i in Instances(InventoryBox):
                if i.item == self:
                    i.Remove()

class EnergyDrink(InventoryInteract):
    def __init__(self):
        super().__init__()

        self.fill = 3
        FirstSprite(self, "Energy"+str(self.fill)+"3")

    def Use(self):
        if self.fill > 0:
            if player != None:
                if player.stam == player.mstam:
                    Speech("I already have full stamina", player)
                    return 0

                player.stam = player.mstam
                self.Empty()

    def Empty(self):
        self.fill -= 1

        if self.fill > 0:
            ChangeSprite(self, "Energy"+str(self.fill)+"3")
        else:
            for i in Instances(InventoryBox):
                if i.item == self:
                    i.Remove()

class Powerup(InventoryInteract):
    def __init__(self):
        super().__init__()

        self.fill = 3
        FirstSprite(self, "Powerup")

    def Use(self):
        def Return():
            ChangeScale(player, .5)
            player.StopInvinsible()
            player.bulletDamage /= 2

        ChangeScale(player, 2)
        player.Invinsible()
        player.bulletDamage *= 2
        player.Power()

        for i in Instances(InventoryBox):
            if i.item == self:
                i.Remove()
                break

        def OP():
            player.stam = player.mstam

        AddPersis(Timer(5, Return))
        AddPersis(DoTimer(5, OP))

#Objects
class Boy(Player):
    def __init__(self):
        self.name = "Boy"
        self.speechColour = boyCol
        
        super().__init__()
class BoyChar(InteractChar):
    def __init__(self):
        self.name = "Boy"
        self.speechColour = boyCol

        super().__init__()

class Girl(Player):
    def __init__(self):
        self.name = "Girl"
        self.speechColour = girlCol
        
        super().__init__()
class GirlChar(InteractChar):
    def __init__(self):
        self.name = "Girl"
        self.speechColour = girlCol

        super().__init__()

class Man(Player):
    def __init__(self):
        self.name = "Man"
        self.speechColour = manCol

        super().__init__()
class ManChar(InteractChar):
    def __init__(self):
        self.name = "Man"
        self.speechColour = manCol

        super().__init__()

class Woman(Player):
    def __init__(self):
        self.name = "Woman"
        self.speechColour = womanCol
        
        super().__init__()
class WomanChar(InteractChar):
    def __init__(self):
        self.name = "Woman"
        self.speechColour = womanCol

        super().__init__()

class Grace(Player):
    def __init__(self):
        self.name = "Grace"
        self.speechColour = graceCol
        
        super().__init__()
class GraceChar(InteractChar):
    def __init__(self):
        self.name = "Grace"
        self.speechColour = graceCol

        super().__init__()
        ChangeCheck(self, "Solid", True)

class Janitor(Player):
    def __init__(self):
        self.name = "Janitor"
        self.speechColour = janitorColour
        
        super().__init__()
class JanitorChar(InteractChar):
    def __init__(self):
        self.name = "Janitor"
        self.speechColour = janitorColour

        super().__init__()

class Sarah(Player):
    def __init__(self):
        self.name = "Sarah"
        self.speechColour = sarahColour
        
        super().__init__()
class SarahChar(InteractChar):
    def __init__(self):
        self.name = "Sarah"
        self.speechColour = sarahColour

        super().__init__()

class PoisonBullet(Bullet):
    def __init__(self):
        super().__init__()
        ChangeColour(self, green)

    def BonusDamage(self, obj):
        StartPoison(obj)

class FireBullet(Bullet):
    def __init__(self):
        super().__init__()
        ChangeColour(self, red)

    def BonusDamage(self, obj):
        StartFire(obj)

class ConfusedBullet(Bullet):
    def __init__(self):
        super().__init__()
        ChangeColour(self, yellow)

    def BonusDamage(self, obj):
        StartConfused(obj)

class FreezeBullet(Bullet):
    def __init__(self):
        super().__init__()
        ChangeColour(self, blue)

    def BonusDamage(self, obj):
        StartFreeze(obj)

class PrivateBullet(Bullet):
    def __init__(self):
        super().__init__()
        ChangeColour(self, (180, 20, 50))

    def BonusDamage(self, obj):
        if not tempBattling:
            TempBattle(self.owner)

def RandomBullet():
    bullets = [
    PoisonBullet,
    FireBullet,
    ConfusedBullet,
    FreezeBullet
    ]

    return random.choice(bullets)
        
class Memory(Interact):
    def __init__(self, num):
        super().__init__()
        FirstSprite(self, "Memory"+str(num))

        def first():
            Speech("Are you ready to look at the picture?", self)
            Speech("Once you do, you will not be able to change player", self)
            Speech("To change players, press ctrl (will only work if the player is in the room)", self)
            Check(WhenNormal, lambda:self.AssignInteraction("C", "Continue", second, True))
        def second():
            RoomoveObject(self)
            Peace()
            Game(level, "b")
        self.AssignInteraction("L", "Look", first, False)

class LifeOrb(PickUp):
    def __init__(self):
        super().__init__()
        FirstSprite(self, "OrbLife")
        
    def func(self):
        global lifeOrbCount
        lifeOrbCount += 1

        if player != None:
            player.HpRefill(1)
            player.StamRefill(1)
            LifeOrbSound.play()
        super().func()

class PoisonOrb(PickUp):
    def __init__(self):
        super().__init__()
        FirstSprite(self, "OrbLife")
        SurfaceBlend(self, green)

    def func(self):
        def func():
            if player != None:
                player.bullet = PoisonBullet
        def endFunc():
            if player != None:
                player.bullet = Bullet
            
        t = DoTimer(10, func)
        t.endFunc = endFunc
        AddPersis(t)

        PowerUpSound.play()

        super().func()

class FireOrb(PickUp):
    def __init__(self):
        super().__init__()
        FirstSprite(self, "OrbLife")
        SurfaceBlend(self, red)

    def func(self):
        def func():
            if player != None:
                player.bullet = FireBullet
        def endFunc():
            if player != None:
                player.bullet = Bullet
            
        t = DoTimer(10, func)
        t.endFunc = endFunc
        AddPersis(t)

        PowerUpSound.play()

        super().func()

class ConfusedOrb(PickUp):
    def __init__(self):
        super().__init__()
        FirstSprite(self, "OrbLife")
        SurfaceBlend(self, yellow)

    def func(self):
        def func():
            if player != None:
                player.bullet = ConfusedBullet
        def endFunc():
            if player != None:
                player.bullet = Bullet
            
        t = DoTimer(10, func)
        t.endFunc = endFunc
        AddPersis(t)

        PowerUpSound.play()

        super().func()

class FreezeOrb(PickUp):
    def __init__(self):
        super().__init__()
        FirstSprite(self, "OrbLife")
        SurfaceBlend(self, blue)

    def func(self):
        def func():
            if player != None:
                player.bullet = FreezeBullet
        def endFunc():
            if player != None:
                player.bullet = Bullet
            
        t = DoTimer(10, func)
        t.endFunc = endFunc
        AddPersis(t)

        PowerUpSound.play()

        super().func()

class PushSwitch(CollideFunc):
    def __init__(self, rect, func):
        super().__init__(rect, func, True)
        ChangeCheckPerm(self, "Display", True)

class Tree(Interact):
    def Chop(self):
        SetPosition(Ghost(), "centerx", "centery", self.rect.centerx, self.rect.centery)
        RoomoveObject(self)

class Puddle(JustThere):
    def __init__(self):
        super().__init__()
        self.speechColour = (56,136,255)
        self.lowDepth = True

        FirstSprite(self, "PuddleWater")
        ChangeCheckPerm(self, "Animate", False)

    def Mop(self):
        Burst(self)
        if self.Sprite.frameCount < self.Sprite.frames-1:
            self.Sprite.frameCount += 1
            self.Sprite.UpdateShowRect()
        else:
            RoomoveObject(self)

class Bomb(Wall):
    def __init__(self):
        super().__init__()

        FirstSprite(self, "Bomb")
        ChangeCheckPerm(self, "Animate", False)
        ChangeCheckPerm(self, "Display", True)

        def func():
            if self in Objects and self not in Removes:
                self.Tick()
                Timer(1.5, func)
        Timer(1.5, func)

        self.Sprite.frameCount = int(self.Sprite.frames/2)
        self.Sprite.UpdateShowRect()

    def Update(self):
        super().Update()

    def BulletHurt(self, bullet):
        for i in range(bullet.damage):
            self.ReverseTick()

    def Tick(self):
        if self.Sprite.frameCount < self.Sprite.frames-1:
            self.Sprite.frameCount += 1
            self.Sprite.UpdateShowRect()
        else:
            self.Explode()

    def ReverseTick(self):
        if self.Sprite.frameCount > 0:
            self.Sprite.frameCount -= 1
            self.Sprite.UpdateShowRect()
        else:
            Explode(self)

    def Explode(self):
        Explode(self)
        if hasattr(self, "BonusExplode"):
            self.BonusExplode()

class SpeechBox:
    def __init__(self):
        RoomObject(self)
        self.highDepth = True

        self.rect = pygame.Rect(0, 0, 0, 0)
        self.colour = midBlack
        self.textColour = midWhite
        self.alpha = 255
        
        SurfaceUpdate(self)
        ChangeAlpha(self, 196)

        self.messages = []
        
        self.maxMessage = None
        self.currentMessage = ""
        
        self.maxCount = 0
        self.count = 0

        self.ochecks = {}

        self.checks = {
            "OnScreen":True
            }

    def Update(self):
        global camTarget, camFreeze
        
        if len(self.messages) > 0:
            if self.maxMessage == None:
                camFreeze = False
                
                self.maxMessage = self.messages[0]
                self.oldCamTarget = camTarget
                camTarget = self.maxMessage.point
                    
                for o in Objects:
                    if not hasattr(o, "checks"):
                        continue
                    if not hasattr(o, "ochecks"):
                        o.ochecks = {}

                    if "Moving" in o.checks:
                        ChangeCheckTemp(o, "Moving", False)
                    if "Shooting" in o.checks:
                        ChangeCheckTemp(o, "Shooting", False)
                    if "Input" in o.checks:
                        ChangeCheckTemp(o, "Input", False)

                if hasattr(self.maxMessage.point, "speechColour"):
                    col = self.maxMessage.point.speechColour
                    ChangeColour(self, col)

                    totalHue = col[0]+col[1]+col[2]
                    
                    if totalHue > 255*3/2:
                        self.textColour = midBlack
                    else:
                        self.textColour = midWhite
                else:
                    ChangeColour(self, midBlack)
                    self.textColour = midWhite
                
                if self.maxMessage.func != None:
                    if self.maxMessage.whenFunc == "Start":
                        self.maxMessage.func()
                
            for e in events:
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_RETURN:
                        if self.currentMessage == self.maxMessage.string and not PMoving:
                            self.Stop()
                            return 0
                        else:
                            self.currentMessage = self.maxMessage.string

            if self.currentMessage != self.maxMessage.string:
                if self.count < self.maxCount:
                    self.count += 1
                else:
                    self.count = 0
                    self.currentMessage += self.maxMessage.string[len(self.currentMessage)]

                    pause = [".", ",", "?", "!", ":"]
                    if self.currentMessage[-1] in pause and self.currentMessage != self.maxMessage.string:
                        self.maxCount = FPS/3
                    else:
                        self.maxCount = 1

            w, h = font.size(self.currentMessage)
            w += 8
            h += 4

            if type(self.maxMessage.point) == tuple:
                x, y = self.maxMessage.point
            else:
                if hasattr(self.maxMessage.point, "rect") and self.maxMessage.point in Rooms[CurrentRoom][1]:
                    x, y = self.maxMessage.point.rect.midbottom
                else:
                    x, y = (0, 0)
            
            newRect = pygame.Rect((0, 0), (w, h))
            ChangeRect(self, newRect)
            if (x, y) != (0, 0):
                SetPosition(self.rect, "centerx", "top", x, y+4)
            
            Rects(self)
            OutsideScreen(self)
            
            screen.blit(self.surf, self.camRect.topleft)
            text(self.currentMessage, self.textColour, "left", "top", self.camRect.left+4, self.camRect.top+2)

            if self.currentMessage == self.maxMessage.string:
                self.PressEnter()

    def Stop(self):
        global camFreeze, camTarget
        camFreeze = True
        if not PMoving:
            camTarget = player
        
        if self.maxMessage.func != None:
            if self.maxMessage.whenFunc == "End":
                self.maxMessage.func()
        
        del self.messages[0]
        self.maxMessage = None
        self.currentMessage = ""

        if len(self.messages) != 0:
            return 0

        camFreeze = False
        ReturnToNormal()

    def PressEnter(self):
        string = "Enter"
        w, h = font.size(string)
        w += 8
        h += 4
        
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill((self.colour[0], self.colour[1], self.colour[2], 196))

        rect = pygame.Rect(0,0,w,h)
        rect.centerx = self.camRect.centerx
        rect.top = self.camRect.bottom+4
        
        screen.blit(surf, rect.topleft)
        text(string, self.textColour, "left", "top", rect.left+4, rect.top+2)

    class Message:
        def __init__(self, string, point, func):
            self.string = string
            self.point = point

            self.func = func[0]
            self.whenFunc = func[1]

def Speech(string, point, func=(None, "")):
    mes = SB.Message(string, point, func)
    SB.messages.append(mes)

def CheckSpeech():
    return len(SB.messages) > 0
        
def CamUpdate():
    global cam

    cam[0] += camOffset[0]
    cam[1] += camOffset[1]

    if camTarget == None or camFreeze:
        return 0

    if type(camTarget) == tuple:
        x, y = camTarget
    elif type(camTarget) == pygame.Rect:
        x, y = camTarget.center
    elif hasattr(camTarget, "rect"):
        if camTarget in Objects:
            x, y = camTarget.rect.center
        else:
            return 0
    
    cam[0] += ((x-screenWidth*.5)-cam[0])*.1
    cam[1] += ((y-screenHeight*.5)-cam[1])*.1

def CamSkip():
    global cam

    if camTarget == None:
        return 0

    if type(camTarget) == tuple:
        x, y = camTarget
    elif hasattr(camTarget, "rect"):
        x, y = camTarget.rect.center

    cam[0] = x-screenWidth*.5
    cam[1] = y-screenHeight*.5
  
def Rects(rect):
    if hasattr(rect, "rect"):
        arect = rect.rect
    else:
        arect = rect

    camRect = pygame.Rect(rect)
    camRect.x -= cam[0]
    camRect.y -= cam[1]

    if hasattr(rect, "rect"):
        rect.camRect = camRect
        rect.depth = -rect.camRect.bottom
    else:
        return camRect

    if hasattr(rect, "Sprite"):
        crect = pygame.Rect(rect.Sprite.crect)
        crect.x *= rect.scale
        crect.y *= rect.scale

        crect.x += rect.rect.x
        crect.y += rect.rect.y

        crect.w *= rect.scale
        crect.h *= rect.scale

        rect.crect = crect

    elif hasattr(rect, "rect"):
        crect = pygame.Rect(rect.rect)
        rect.crect = crect

    if hasattr(rect, "crect"):
        camCrect = pygame.Rect(rect.crect)
        camCrect.x -= cam[0]
        camCrect.y -= cam[1]
        rect.camCrect = camCrect

#Depth
def DepthSort():
    global Objects

    highDepth = []
    lowDepth = []
    
    depth = []
    noDepth = []

    def MaxList():
        return noDepth+lowDepth+depth+highDepth

    while True:
        maxDepth = None
        for o in Objects:
            if o in MaxList():
                continue

            if hasis(o, "lowDepth"):
                lowDepth.append(o)
            elif hasis(o, "highDepth"):
                highDepth.append(o)
            elif hasattr(o, "depth"):
                if maxDepth == None:
                    maxDepth = o
                elif o.depth > maxDepth.depth:
                    maxDepth = o
            else:
                noDepth.append(o)
                
        if maxDepth != None:
            depth.append(maxDepth)
        else:
           break

    Objects = MaxList()

def SolidObject(name):
    w = Wall()
    FirstSprite(w, name)
    ChangeCheckPerm(w, "Display", True)

    return w

def GenerateForest():
    for x in range(0, roomWidth):
        for y in range(0, roomHeight):
            randomNum = random.randint(0, 50)

            if randomNum == 0:
                tree = Tree()
                FirstSprite(tree, "Tree1")
                SetPosition(tree, random.choice(["left", "right", "centerx"]),
                            random.choice(["top", "bottom", "centery"]),
                            x, y)
                
                s = Objects[-1]
                for o in Objects:
                    if o == s:
                        continue
                    if type(o) != Wall:
                        continue

                    if s.rect.colliderect(o.rect):
                        RoomoveObject(s)
                        break
            else:
                randomNum = random.randint(0, 200)

                if randomNum == 0:
                    tree = Tree()
                    FirstSprite(tree, "Tree2")
                    SetPosition(tree, random.choice(["left", "right", "centerx"]),
                                random.choice(["top", "bottom", "centery"]),
                                x, y)
                                
                    s = Objects[-1]
                    for o in Objects:
                        if o == s:
                            continue
                        if type != Wall:
                            continue

                        if s.rect.colliderect(o.rect):
                            RoomoveObject(o)

def SetBck(b):
    global bck
    
    bckPlanName = b+"Plan"
    bckPlanFilename = bckPlanName+".png"
    
    if Sombre:
        b = "Sombre"+b
    bck = Sprite.New(b)

    global roomWidth, roomHeight
    roomWidth, roomHeight = bck.sprite.get_size()

    if bckPlanFilename not in os.listdir("Sprites"):
        return 0
    
    bckPlan = pygame.image.load("Sprites/"+bckPlanFilename)
    width, height = bckPlan.get_size()

    width *= bck.scale
    height *= bck.scale
    bckPlan = pygame.transform.scale(bckPlan, (width, height))

    cols = {
        (85,255,0):(42,128,0)
        }
    
    for x in range(0, width, bck.scale):
        for y in range(0, height, bck.scale):
            col = bckPlan.get_at((x, y))[:3]

            if col in cols:
                lookCol = cols[col]

                w = 1
                for xx in range(x+bck.scale, width, bck.scale):
                    lCol = bckPlan.get_at((xx, y))[:3]
                    if lCol == lookCol:
                        w += 1
                    else:
                        break

                h = 1
                for yy in range(y+bck.scale, height, bck.scale):
                    lCol = bckPlan.get_at((x, yy))[:3]
                    if lCol == lookCol:
                        h += 1
                    else:
                        break

                w, h = w*bck.scale, h*bck.scale
                
                wall = Wall((w, h))
                wall.removeTran = True
                
                SetPosition(wall, "left", "top", x, y)
                ChangeCheck(wall, "Display", False)

def RemoveBck():
    global bck
    bck = None

def RoomEmpty():
    return Rooms[CurrentRoom][2]

def RoomMake():
    global Objects

    Rooms[CurrentRoom][0]()
    Rooms[CurrentRoom][2] = False

    Objects = Rooms[CurrentRoom][1]+PersisObjects

def RoomChange(newRoom):
    global CurrentRoom

    if CurrentRoom != "":
        for o in Rooms[CurrentRoom][1]:
            if hasis(o, "removeTran"):
                Rooms[CurrentRoom][1].remove(o)

        player.HideObjects()
            
    oldRoom = CurrentRoom
    CurrentRoom = newRoom
    RoomMake()

    for p in PersisObjects:
        if p not in Rooms[CurrentRoom][1]:
            Rooms[CurrentRoom][1].append(p)
        if oldRoom != "":
            if p in Rooms[oldRoom][1]:
                RoomoveObjectFrom(p, oldRoom)

    if player == None:
        NextPlayer()

    for p in players:
        if p == player:
            p.ShowObjects()
        else:
            p.HideObjects()
    
def RoomObject(obj):
    try:
        Objects.append(obj)
        Rooms[CurrentRoom][1].append(obj)
    except:
        Objects.append(obj)

def RoomoveObject(obj):
    if obj in Objects and obj not in Removes:
        Removes.append(obj)

    if obj in PersisObjects:
        PersisObjects.remove(obj)

    for p in players:
        if CurrentRoom in p.Objects:
            if obj in p.Objects[CurrentRoom]:
                p.Objects[CurrentRoom].remove(obj)

    if CurrentRoom not in Rooms:
        return 0
    
    if obj in Rooms[CurrentRoom][1]:
        Rooms[CurrentRoom][1].remove(obj)

def RoomoveObjectPlayer(obj, player):
    RoomoveObject(obj)
    if obj not in player.Objects[CurrentRoom]:
        player.Objects[CurrentRoom].append(obj)

def RoomoveObjectNow(obj):
    Objects.remove(obj)
    RoomoveObject(obj)

def RoomoveObjectFrom(obj, room):
    if obj in Rooms[room][1]:
        Rooms[room][1].remove(obj)

def RoomAdd(obj):
    #Object MUST already exists
    for r in Rooms:
        if r == CurrentRoom:
            continue

        if obj in Rooms[r][1]:
            RoomoveObject(obj)

    if obj not in Objects:
        Objects.append(obj)
    if obj not in Rooms[CurrentRoom][1]:
        Rooms[CurrentRoom][1].append(obj)

#Rooms
def KidsRoom():
    SetBck("KidsRoom")

def KidsRoomNoBoy():
    SetBck("KidsRoomNoBoy")
def KidsRoomNoGirl():
    SetBck("KidsRoomNoGirl")
def StorageRoom():
    SetBck("StorageRoom")

def BaseParentsRoom():
    if RoomEmpty():
        global Plant
        Plant = Interact()
        ChangeCheck(Plant, "Solid", False)
        FirstSprite(Plant, "Plant")
        SetPositionBck(Plant, "left", "bottom", 24, 14)
        
def ParentsRoom():
    SetBck("ParentsRoom")
    BaseParentsRoom()
def ParentsRoomNoWoman():
    SetBck("ParentsRoomNoWoman")
    BaseParentsRoom()
def ParentsRoomNoMan():
    SetBck("ParentsRoomNoMan")
    BaseParentsRoom()

def BaseLivingRoom():
    if RoomEmpty():
        global Sofa
        Sofa = SolidObject("Sofa")
        SetPositionBck(Sofa, "left", "top", 40, 14)

        global television
        television = Interact()
        FirstSprite(television, "Television")
        SetPositionBck(television, "left", "top", 44, 37)

def LivingRoom():
    SetBck("LivingRoom")
    BaseLivingRoom()
def BattleLivingRoom():
    SetBck("BattleLivingRoom")
    BaseLivingRoom()

def RoadToSchool():
    SetBck("RoadToSchool")
def Playground():
    SetBck("Playground")

def Corridor1():
    SetBck("Corridor1")
def Corridor2():
    SetBck("Corridor2")

def BaseClass():
    if RoomEmpty():
        global Tables
        Tables = []

        for i in range(3):
            if i == 0:
                x = roomWidth*.25
            elif i == 1:
                x = roomWidth*.5
            elif i == 2:
                x = roomWidth*.75

            Tables.append([])

            for j in range(3):
                if j == 0:
                    y = roomHeight*.5
                elif j == 1:
                    y = roomHeight*.65
                elif j == 2:
                    y = roomHeight*.8

                t = SolidObject("SchoolTable")
                SetPosition(t, "centerx", "centery", x, y)
                Tables[i].append(t)

def ScienceClass():
    SetBck("ScienceClass")
    BaseClass()
def MathsClass():
    SetBck("MathsClass")
    BaseClass()
def EnglishClass():
    SetBck("EnglishClass")
    BaseClass()
def GeographyClass():
    SetBck("GeographyClass")
    BaseClass()

def JanitorsRoom():
    SetBck("JanitorsRoom")

    if RoomEmpty():
        mbox = Interact()
        FirstSprite(mbox, "BoxSmall")
        SetPositionBck(mbox, "left", "top", 7, 24)

        milk = Milk()
        RoomoveObject(milk)

        def func():
            AddInventory(milk)
            RoomoveObject(mbox)
        mbox.AssignInteraction("O", "Open", func, True)

        ebox = Interact()
        FirstSprite(ebox, "BoxSmall")
        SetPositionBck(ebox, "left", "top", 10, 37)

        energy = EnergyDrink()
        RoomoveObject(energy)

        def func():
            AddInventory(energy)
            RoomoveObject(ebox)
        ebox.AssignInteraction("O", "Open", func, True)

        pbox = Interact()
        FirstSprite(pbox, "BoxMed")
        SetPositionBck(pbox, "left", "top", 5, 31)

        powerUp = Powerup()
        RoomoveObject(powerUp)

        def func():
            AddInventory(powerUp)
            RoomoveObject(pbox)
        pbox.AssignInteraction("O", "Open", func, True)
def JanitorsMiniBossRoom():
    SetBck("JanitorsMiniBossRoom")

    if RoomEmpty():
        bigBox = SolidObject("BoxBig")
        bigBox.rect.center = (roomWidth*.25, roomHeight*.5)

        medBox = SolidObject("BoxMed")
        medBox.rect.topleft = bigBox.rect.topright
        medBox.rect.x += 4

        medBox = SolidObject("BoxMed")
        medBox.rect.topleft = bigBox.rect.bottomleft
        medBox.rect.y += 4

        bigBox = SolidObject("BoxBig")
        bigBox.rect.center = (roomWidth*.75, roomHeight*.5)

        medBox = SolidObject("BoxMed")
        medBox.rect.topright = bigBox.rect.topleft
        medBox.rect.x -= 4

        medBox = SolidObject("BoxMed")
        medBox.rect.topright = bigBox.rect.bottomright
        medBox.rect.y += 4

        bigBox = SolidObject("BoxBig")
        bigBox.rect.center = (roomWidth*.25, roomHeight*.75)

        medBox = SolidObject("BoxMed")
        medBox.rect.bottomleft = bigBox.rect.bottomright
        medBox.rect.x += 4

        medBox = SolidObject("BoxMed")
        medBox.rect.bottomleft = bigBox.rect.topleft
        medBox.rect.y -= 4

        bigBox = SolidObject("BoxBig")
        bigBox.rect.center = (roomWidth*.75, roomHeight*.75)

        medBox = SolidObject("BoxMed")
        medBox.rect.bottomright = bigBox.rect.bottomleft
        medBox.rect.x -= 4

        medBox = SolidObject("BoxMed")
        medBox.rect.bottomright = bigBox.rect.topright
        medBox.rect.y -= 4

def BaseWeddingRoom():
    SetBck("WeddingRoom")
def WeddingRoom():
    BaseWeddingRoom()

    if RoomEmpty():
        coords = (
            (6, 36),
            (6, 48),
            (6, 60),
            (40, 36),
            (40, 48),
            (40, 60)
            )

        Seats = []
        for c in coords:
            seat = SolidObject("WeddingSeat")
            SetPositionBck(seat, "left", "top", c[0], c[1])

            Seats.append(seat)

def SuperMarket():
    SetBck("SuperMarket")

def GraceHouse():
    SetBck("GraceHouse")
def GraceRoom():
    SetBck("GraceRoom")

    global ParentsBed, GraceBed, Doll
    ParentsBed = Interact()
    FirstSprite(ParentsBed, "GraceParentsBed")
    SetPositionBck(ParentsBed, "right", "top", 93, 20)

    GraceBed = Interact()
    FirstSprite(GraceBed, "GraceBed")
    SetPositionBck(GraceBed, "left", "top", 2, 20)

    Doll = Interact()
    FirstSprite(Doll, "GraceDoll")
    SetPositionBck(Doll, "right", "bottom", 35, 46)

def BaseGraceGarden():
    SetBck("GraceGarden")

def GraceGarden():
    BaseGraceGarden()

    if RoomEmpty():
        t = SolidObject("Tree2")
        SetPositionBck(t, "left", "bottom", 48, 48)
def YoungGraceGarden():
    BaseGraceGarden()

def Overlay(col, alpha):
    global overlay, overlaySurface
    overlay = True
    
    overlaySurface = pygame.Surface((screenWidth, screenHeight), pygame.SRCALPHA)
    overlaySurface.fill((col[0], col[1], col[2], alpha))

def StopOverlay():
    global overlay
    overlay = False
StopOverlay()

def CreateFlashlight():
    global flashlightSurface
    
    flashlightSurface = pygame.Surface((screenWidth, screenHeight), pygame.SRCALPHA)
    maxDist = dist((0, 0), (screenWidth/3, screenHeight/3))

    square = 2
    for w in range(0, screenWidth, square):
        for h in range(0, screenHeight, square):
            currentDist = dist((w, h), (screenWidth/2, screenHeight/2))
            alpha = currentDist/maxDist*255

            if alpha > 255:
                alpha = 255

            for i in range(square):
                for j in range(square):
                    flashlightSurface.set_at((w+i, h+j), (0, 0, 0, alpha))
        
def Flashlight():
    CreateFlashlight()
    
    global flashlight
    flashlight = True

def StopFlashlight():
    global flashlight
    flashlight = False
StopFlashlight()

def ResetSaveFile():
    saveFile = open("SaveFile.txt", "w")
    resetFile = open("ResetFile.txt", "r")

    for line in resetFile.readlines():
        saveFile.write(line)

    resetFile.close()
    saveFile.close()

def CheckFinishLevel(level):
    go = False
    
    saveFile = open("SaveFile.txt", "r")
    for line in saveFile.readlines():
        l = line.strip()
        l = l.replace(" ", "")

        string = "Level"+str(level)
        if l[:len(string)] == string:
            go = eval(l[len(string)+1:])
    saveFile.close()

    return go

def UnlockLevel(level):
    saveFile = open("SaveFile.txt", "r")
    lines = []

    for line in saveFile.readlines():
        l = line.strip()
        l = l.replace(" ", "")

        string = "Level"+str(level)
        if l[:len(string)] == string:
            l = string+":True"
        lines.append(l)

    saveFile.close()

    saveFile = open("SaveFile.txt", "w")
    for l in lines:
        saveFile.write(l+"\n")
    saveFile.close()

def CheckLevelExists(lv):
    go = False
    saveFile = open("SaveFile.txt", "r")

    for line in saveFile.readlines():
        l = line.strip()
        l = l.replace(" ", "")

        string = "Level"+str(lv)
        if l[:len(string)] == string:
            go = True
    
    saveFile.close()
    return go

def Start():
    PlaySong("BackgroundMusic")
    pygame.mixer.music.set_volume(1)

    global bckCol, events, Objects, Removes, currentHover, totalRect
    Objects = []
    Removes = []
    currentHover = None

    StartButton = Button("Start")
    LevelSelectButton = Button("Level Select")
    QuitButton = Button("Quit")

    StartButton.func = Game
    LevelSelectButton.func = LevelSelect
    QuitButton.func = End

    totalRect = pygame.Rect(0,0,0,0)
    longestWidth = None
    
    for o in Objects:
        if type(o) != Button:
            continue

        if longestWidth == None:
            longestWidth = o
        elif longestWidth.rect.w < o.rect.w:
            longestWidth = o

        totalRect.w = longestWidth.rect.w
        totalRect.h += o.rect.h+4
        
    totalRect.h -= 4
    totalRect.center = (screenWidth/2, screenHeight/2)

    totalHeight = 0
    for o in Objects:
        if type(o) != Button:
            continue

        newRect = pygame.Rect(o.rect)
        newRect.w = longestWidth.rect.w
        
        o.ChangeRect(newRect)
        o.rect.left = totalRect.left
        
        o.rect.y = totalRect.y
        o.rect.y += totalHeight

        totalHeight += o.rect.h+4

    ResetButton = Button("Reset Savefile")
    ChangeCheck(ResetButton, "Grow", False)
    ResetButton.func = ResetSaveFile
    ResetButton.rect.bottomright = (screenWidth-4, screenHeight-4)

    bck1 = pygame.image.load("Sprites/StartScreen.png")
    bck1 = pygame.transform.scale(bck1, (screenWidth, screenHeight))

    bck2 = pygame.image.load("Sprites/SombreStartScreen.png")
    bck2 = pygame.transform.scale(bck2, (screenWidth, screenHeight))
    
    bckCol = white
    while True:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                End()

        screen.fill(bckCol)
        screen.blit(bck1, (0, 0), (0, 0, screenWidth/2, screenHeight))
        screen.blit(bck2, (screenWidth/2, 0), (screenWidth/2, 0, screenWidth/2, screenHeight))

        for o in Objects:
            if hasattr(o, "Update"):
                o.Update()

        for r in Removes:
            Objects.remove(r)
        Removes = []

        clock.tick(FPS)
        pygame.display.update()

def LevelSelect():
    global events, Objects, currentHover, totalRect
    Objects = []
    currentHover = None

    class LevelButton(Button):
        def __init__(self, buttonName):
            super().__init__(buttonName)
            ChangeCheckPerm(self, "Grow", False)
            
        def Update(self):
            super().Update()

        def AssignLevel(self, level):
            self.level = level
            self.func = lambda:ChooseLevel(self.level)

            finishLevel = CheckFinishLevel(self.level)
            if not finishLevel:
                self.Freeze()

    Level1 = LevelButton("Level 1")
    Level2 = LevelButton("Level 2")
    Level3 = LevelButton("Level 3")
    Level4 = LevelButton("Level 4")

    def ChooseLevel(level):
        if CheckFinishLevel(level):
            Game(level)

    Level1.AssignLevel("1")
    Level2.AssignLevel("2")
    Level3.AssignLevel("3")
    Level4.AssignLevel("4")

    totalWidth = Level1.rect.w*3+4*3
    totalHeight = Level1.rect.h*2+4*1
    totalRect = pygame.Rect(0, 0, totalWidth, totalHeight)
    totalRect.center = (screenWidth/2, screenHeight/2)

    width = 0
    for i in range(1, 4):
        button = eval("Level"+str(i))
        
        button.rect.topleft = totalRect.topleft
        button.rect.x += width
        width += button.rect.w+4

    Level4.rect.midtop = (Level2.rect.centerx, Level2.rect.bottom+4)

    BackButton = Button("Back")
    BackButton.rect.topleft = (4, 4)
    BackButton.func = Start

    bck1 = pygame.image.load("Sprites/StartScreen.png")
    bck1 = pygame.transform.scale(bck1, (screenWidth, screenHeight))

    bck2 = pygame.image.load("Sprites/SombreStartScreen.png")
    bck2 = pygame.transform.scale(bck2, (screenWidth, screenHeight))

    while True:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                End()

        screen.fill(bckCol)
        screen.blit(bck1, (0, 0), (0, 0, screenWidth/2, screenHeight))
        screen.blit(bck2, (screenWidth/2, 0), (screenWidth/2, 0, screenWidth/2, screenHeight))
        
        for o in Objects:
            if hasattr(o, "Update"):
                o.Update()

        clock.tick(FPS)
        pygame.display.update()

def Pause():
    global Objects, Removes, events, currentHover
    oldObjects = copy.copy(Objects)
    oldRemoves = copy.copy(Removes)
    oldScreen = copy.copy(screen)

    Objects = []
    Removes = []
    currentHover = None

    ContinueButton = Button("Continue")
    ReplayButton = Button("Replay")
    MainMenuButton = Button("Main Menu")

    longestWidth = None
    for o in Objects:
        if type(o) != Button:
            continue

        if longestWidth == None:
            longestWidth = o
        elif o.rect.w > longestWidth.rect.w:
            longestWidth = o

    for o in Objects:
        if type(o) != Button:
            continue

        rect = o.rect
        rect.w = longestWidth.rect.w
        ChangeRect(o, rect)

    ReplayButton.rect.center = (screenWidth/2, screenHeight/2)
    ContinueButton.rect.midbottom = (ReplayButton.rect.centerx, ReplayButton.rect.top-4)
    MainMenuButton.rect.midtop = (screenWidth/2, ReplayButton.rect.bottom+4)

    def Unpause():
        global Pausing
        Pausing = False

    ReplayButton.func = lambda:Game(level)
    ContinueButton.func = Unpause
    MainMenuButton.func = Start

    global Pausing
    Pausing = True

    darkSurf = pygame.Surface((screenWidth, screenHeight), pygame.SRCALPHA)
    darkSurf.fill((black[0], black[1], black[2], 96))

    while Pausing:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                End()

        screen.blit(oldScreen, (0, 0))
        screen.blit(darkSurf, (0, 0))

        for o in Objects:
            if hasattr(o, "Update"):
                o.Update()

        for r in Removes:
            Objects.remove(r)
        Removes = []

        clock.tick(FPS)
        pygame.display.update((0, 0, screenWidth, screenHeight))

    for o in Objects:
        RoomoveObject(o)

    Objects = oldObjects
    Removes = oldRemoves

tempBattling = False
def TempBattle(enemy):
    if not WhenNormal():
        return 0

    global tempBattling
    tempBattling = True

    global bck, bckCol
    oldBck = bck
    oldBckCol = bckCol

    global Objects, oldPos, eoldPos
    oldObjects = Objects
    oldPos = player.rect.center
    eoldPos = enemy.rect.center

    bck = None
    bckCol = (85,10,25)
    Objects = PersisObjects + [enemy]

    global oldInput
    oldInput = player.checks["Input"]
    ChangeCheckPerm(player, "Input", False)

    def CheckToNormal():
        if enemy not in Rooms[CurrentRoom][1]:
            return True
        if enemy not in Objects:
            return True

    def ReturnToNormal():
        global tempBattling
        tempBattling = False

        global bck, bckCol
        bck = oldBck
        bckCol = oldBckCol

        global Objects
        enemyDie = enemy not in Objects

        Objects = oldObjects
        player.rect.center = oldPos
        CamSkip()

        for p in PersisObjects:
            if p not in Objects:
                Objects.append(p)

        ChangeCheckPerm(player, "Input", oldInput)

        if enemyDie:
            RoomoveObject(enemy)
        else:
            enemy.rect.center = eoldPos

    Check(CheckToNormal, ReturnToNormal)
    t = Timer(10, ReturnToNormal)
    Check(lambda:not tempBattling, lambda:RoomoveObject(t))

def Game(lv=1, part="a"):
    global events, Objects, Removes, level, player, cam, camTarget, camFreeze, SB
    level = lv

    def NewLevela():
        global Objects, Removes
        Objects = []
        Removes = []

        global Rooms, CurrentRoom
        Rooms = {}
        CurrentRoom = ""
            
        global cam, camTarget, camFreeze, camOffset
        cam = [0, 0]
        camOffset = [0, 0]
        camTarget = None
        camFreeze = False
        CamSkip()

        global Sombre, player, Inventory
        Sombre = True
        player = None
        Inventory = []

        for p in players:
            ChangeCheckPerm(p, "Sombre", Sombre)

        global SB, Shakey
        SB = SpeechBox()
        Shakey = ScreenShake()

        global PersisObjects
        PersisObjects = [SB, Shakey]

        def hpRegen():
            if not player.CheckDanger() and player.hp < player.mhp:
                player.HpRefill(1)
        AddPersis(Repeater(4, hpRegen))

        def stamRegen():
            if player != None:
                player.StamRefill(1)
        AddPersis(Repeater(1, stamRegen))

        def enemyFind():
            for o in Objects:
                if hasis(o, "Enemy"):
                    HelpFind(o)
        AddPersis(DoCheck(lambda:True, enemyFind))
        
        global memoryFound, lifeOrbCount
        memoryFound = False
        lifeOrbCount = 0

        global bck, bckCol
        bck = None
        bckCol = grey
        
        Overlay(black, 128)

    def NewLevelb():
        global CurrentRoom
        CurrentRoom = ""

        global Sombre, memoryFound
        Sombre = False
        memoryFound = True
        
        StopOverlay()

        for o in Objects:
            if hasattr(o, "checks"):
                if "Sombre" in o.checks:
                    ChangeCheck(o, "Sombre", False)

        for p in players:
            p.Objects = {}

    def Level1a():
        global players

        global boy, girl, woman, man
        boy = Boy()
        girl = Girl()
        woman = Woman()
        man = Man()
        
        players = [
            boy,
            girl,
            woman,
            man
            ]

        for p in players:
            ChangeCheck(p, "CanDash", False)
            ChangeCheck(p, "Shooting", False)
        
        NewLevela()

        global Quests
        Quests = {}

        #KidsRoom
        def KRoom():
            KidsRoom()
            
            if RoomEmpty():
                # Flashlight()

                RoomAdd(boy)
                RoomAdd(girl)

                SetPositionBck(boy, "right", "top", 81, 31)
                SetPositionBck(girl, "left", "top", 14, 31)

                def check0():
                    for e in events:
                        if e.type == pygame.KEYDOWN:
                            return True
                def func0():
                    Speech("Use the arrow keys to move", player)
                    Speech("And the control (crtl) button to switch players", player)
                    
                Check(check0, func0)

                def ParentsRoomTran():
                    RoomChange("ParentsRoom")
                    SetPositionBck(player, "centerx", "top", player.rect.centerx/bck.scale, 1)
                rect = pygame.Rect(41, 47, 15, 1)
                rect.x, rect.y = rect.x*bck.scale, rect.y*bck.scale
                rect.w, rect.h = rect.w*bck.scale, rect.h*bck.scale

                CollideFunc(rect, ParentsRoomTran).persis = True

            if "Follow Grace" in Quests:
                if not Quests["Follow Grace"]:
                    Quests["Follow Grace"] = True
                    
                    def func0():
                        def func0():
                            def func0():
                                Speech('"This should answer all of your questions"', player)
                                Speech("What's that supposed to mean? Nothing's changed", player)
                                if player.name == "Boy" or player.name == "Girl":
                                    Speech("Actually... My door is shut. I never shut my door", player)

                            m = Memory(2)
                            SetPositionBck(m, "centerx", "centery", 48, 12)

                            AddPersis(Check(lambda:memoryFound, func0))
                        Speech("Wh- Who are you?", player)
                        Speech("My name is Grace, but I'm afraid we do not have time to chat", grace)
                        Speech("Here. Take this photo of your family", grace, func=(func0, "End"))
                        Speech("This should answer all of your questions", grace)
                        Speech("Goodbye for now", grace, func=(lambda:Explode(grace), "End"))

                    RoomAdd(grace)
                    SetPosition(grace, "centerx", "centery", roomWidth/2, roomHeight/2)
                    grace.AssignInteraction("C", "Chat", func0, True)

        def PRoom():
            ParentsRoom()

            if RoomEmpty():
                RoomAdd(woman)
                SetPositionBck(woman, "left", "bottom", 2, 27)
                    
                def SpawnGhost():
                    global ghst
                    ghst = Ghost()
                    SetPositionBck(ghst, "centerx", "bottom", 48, 33)

                    ChangeCheck(ghst, "Shooting", False)
                    
                    ghst.ohspd = int(ghst.ohspd/2)
                    ghst.ovspd = int(ghst.ovspd/2)
                SpawnGhost()

                def enemyCheck():
                    if player != None:
                        return player.CheckDanger()
                    return False
                
                def enemyFunc():
                    if player != None:
                        Speech("What... Is... That...", player)
                        if player.name == "Boy":
                            Speech("Go away whatever you are!", player)
                        if player.name == "Girl":
                            Speech("Mummy help me!", player)

                        def check():
                            if player == None:
                                return False
                            
                            for o in Objects:
                                if issubclass(type(o), Enemy):
                                    if dist(o, player) < minDist(o, player):
                                        return True
                        def func():
                            def func():
                                def func0():
                                    def func0():
                                        RoomoveObject(grace)
                                        Quests["Follow Grace"] = False
                                    PersonMove(grace, ("centerx", "top"), (48, 0), 3, eFunc=func0)

                                for o in Objects:
                                    if issubclass(type(o), Enemy):
                                        Explode(o)
                                        if player.rect.colliderect(ToKidsRoom.rect):
                                            SetPosition(player, "centerx", "top", player.rect.centerx, ToKidsRoom.rect.bottom+2)

                                global grace
                                grace = GraceChar()
                                SetPosition(grace, "centerx", "centery", roomWidth/2, roomHeight/2)
                                Speech("Do not worry... I am here to protect you", grace)
                                Speech("Follow me", grace, func=(func0, "End"))
                                
                            Speech("GO! AWAY!", player, func=(func, "End"))

                            ChangeCheck(ghst, "Moving", False)
                        Check(check, func)
                Check(enemyCheck, enemyFunc)
                
                def KidsRoomTran():
                    if ghst in Objects:
                        return 0

                    RoomChange("KidsRoom")
                    SetPositionBck(player, "centerx", "bottom", player.rect.centerx/bck.scale, 46)
                rect = pygame.Rect(41, 0, 15, 1)
                rect.x, rect.y = rect.x*bck.scale, rect.y*bck.scale
                rect.w, rect.h = rect.w*bck.scale, rect.h*bck.scale

                ToKidsRoom = CollideFunc(rect, KidsRoomTran)
                ToKidsRoom.persis = True
                
                def LivingRoomTran():
                    RoomChange("LivingRoom")
                    SetPositionBck(player, "centerx", "top", 8, 13)
                rect = pygame.Rect(41, 33, 15, 2)
                rect.x, rect.y = rect.x*bck.scale, rect.y*bck.scale
                rect.w, rect.h = rect.w*bck.scale, rect.h*bck.scale

                CollideFunc(rect, LivingRoomTran).persis = True

        def LRoom():
            LivingRoom()

            if RoomEmpty():
                RoomAdd(man)
                SetPositionBck(man, "centerx", "bottom", 48, 28)
                
                def ParentsRoomTran():
                    RoomChange("ParentsRoom")
                    SetPositionBck(player, "centerx", "bottom", 48, 32)
                rect = pygame.Rect(5, 12, 7, 1)
                rect.x, rect.y = rect.x*bck.scale, rect.y*bck.scale
                rect.w, rect.h = rect.w*bck.scale, rect.h*bck.scale

                CollideFunc(rect, ParentsRoomTran).persis = True

        global Rooms
        Rooms = {
            "KidsRoom":[KRoom, [], True],
            "ParentsRoom":[PRoom, [], True],
            "LivingRoom":[LRoom, [], True]
            }
        RoomChange("KidsRoom")

    def Level1b():
        NewLevelb()

        global Quests
        Quests = {
            "ArgueSibling":False,
            "MumIgnore":False,
            "DadIgnore":False,
            "ChildIgnore":False
            }

        global man, woman, grace
        man = ManChar()
        RoomoveObject(man)

        woman = WomanChar()
        RoomoveObject(woman)

        grace = GraceChar()
        RoomoveObject(grace)

        def WildGraceAppears(hs, vs, x, y):
            def func0():
                ChangeCheck(player, "Shooting", True)
            
            def check1():
                return ghstWaves == []
            def func1():
                def HpRefill():
                    if player.hp < player.mhp:
                        player.HpRefill(1)
                    else:
                        RoomoveObject(hpRepeater)
                def func0():
                    Speech("First of all what you saw just there...", grace)

                    string = "That was not your {}"
                    if player.name == "Boy" or player.name == "Girl":
                        string = string.format("Mother")
                    elif player.name == "Woman":
                        string = string.format("husband")
                    elif player.name == "Man":
                        string = string.format("wife")
                    Speech(string, grace)

                    Speech("That creature is one of many that want to steal your memories", grace)
                    Speech("This world in fact is one of your memories", grace)
                    Speech("They will be the key in restoring your life with your family", grace)
                    Speech("If you ever wish to see your family again, I suggest you never lose sight of them", grace, func=(LevelComplete, "End"))

                Speech("Well done, I knew you could do it", grace)
                Speech("When you're ready, meet me here", grace)

                grace.AssignInteraction("T", "Talk", func0, True)
                StopPersisSong()

                if player.checks["Invinsibility"]:
                    ChangeCheckPerm(player, "Invinsibility", False)
                    global hpRepeater
                    hpRepeater = Repeater(1, HpRefill)

            def check2():
                return player.hp <= 2
            def func2():
                if player.hp == 0:
                    player.hp = 1

                player.checks["Invinsibility"] = True
                Speech("Don't worry I am here to protect you", grace)

            RoomAdd(grace)
            SetPositionBck(grace, hs, vs, x, y)

            Speech("Prepare yourself... This creature is not friendly", grace)
            Speech("Use the WASD keys to shoot in the corresponding direction", player)

            Check(WhenNormal, func0)
            Check(check1, func1)
            Check(check2, func2)

        def GhostAppears(who):
            global ghstWaves
            ghstWaves = []

            def ghst0():
                ghst = Ghost()
                ChangeCheckNow(ghst, "Moving", False)
                ChangeCheckNow(ghst, "Shooting", False)

                ghst.rect.center = who.rect.center
                Explode(who)
                return ghst

            def ghst1():
                ghst = GhostPoison()
                RandomSpawn(ghst)
                return ghst
            def ghst2():
                ghst = GhostFire()
                RandomSpawn(ghst)
                return ghst
            def ghst3():
                ghst = GhostConfused()
                RandomSpawn(ghst)
                return ghst
            def ghst4():
                ghst = GhostFreeze()
                RandomSpawn(ghst)
                return ghst

            ghstWaves.append([ghst0])
            ghstWaves.append([ghst1, ghst3])
            ghstWaves.append([ghst2, ghst4])

            def StartWave():
                if ghstWaves != []:
                    for g in range(len(ghstWaves[0])):
                        ghstWaves[0][g] = ghstWaves[0][g]()

                def check0():
                    if ghstWaves == []:
                        return False

                    newWave = True
                    for g in ghstWaves[0]:
                        if g in Rooms[CurrentRoom][1]:
                            newWave = False
                            break

                    return newWave

                def func0():
                    ghstWaves.remove(ghstWaves[0])
                    StartWave()
                Check(check0, func0)
            
            #Wave Control
            StartWave()

            #Explain types
            def checkType(typ):
                for o in Objects:
                    if type(o) == typ:
                        return True
                return False

            def CamGhst(typ):
                for o in Objects:
                    if type(o) == typ:
                        ghst = o
                        break

                def func0():
                    global camTarget
                    camTarget = ghst
                def endFunc():
                    global camTarget
                    camTarget = player
                DoCheck(lambda:not WhenNormal(), func0).endFunc = endFunc

            def funcPoison():
                Speech("A green ghost can poison you : It will slow you down and drain health over time", grace, func=(lambda:CamGhst(GhostPoison), "Start"))

            def funcFire():
                Speech("A red ghost can burn you : It will increase your speed and drain health quickly", grace, func=(lambda:CamGhst(GhostFire), "Start"))

            def funcConfused():
                Speech("A yellow ghost can confuse you : It will reverse the direction you move", grace, func=(lambda:CamGhst(GhostConfused), "Start"))

            def funcFreeze():
                Speech("A blue ghost can freeze you : It will stop you from moving momentarily", grace, func=(lambda:CamGhst(GhostFreeze), "Start"))

            Check(lambda:checkType(GhostPoison), funcPoison)
            Check(lambda:checkType(GhostFire), funcFire)
            Check(lambda:checkType(GhostConfused), funcConfused)
            Check(lambda:checkType(GhostFreeze), funcFreeze)

        def KRoom():
            if player.name == "Boy":
                newBck = "KidsRoomNoBoy"
            elif player.name == "Girl":
                newBck = "KidsRoomNoGirl"
            elif player.name == "Woman" or player.name == "Man":
                newBck = "KidsRoom"
            exec(newBck+"()")
            
            if RoomEmpty():
                StopFlashlight()

                global Sibling, boy, girl
                boy = BoyChar()
                girl = GirlChar()

                SetPositionBck(girl, "left", "top", 14, 31)
                SetPositionBck(boy, "right", "top", 81, 31)
                
                if player.name == "Boy":
                    RoomoveObject(boy)
                    Sibling = girl
                elif player.name == "Girl":
                    RoomoveObject(girl)
                    Sibling = boy

                elif player.name == "Man" or player.name == "Woman":
                    def TalkToChild(obj):
                        global IgnoreChild
                        IgnoreChild = obj
                        Quests["ChildIgnore"] = True

                        string = "How are you {}"
                        if obj.name == "Boy":
                            string = string.format("Edward")
                        elif obj.name == "Girl":
                            string = string.format("Annabelle")
                        Speech(string, player)

                        Speech("...", player)
                        Speech("Why are you ignoring me?", player)
                        Speech("...", player)
                        Speech("That's it your grounded", player)

                        if obj.name == "Boy":
                            girl.AssignInteraction("T", "Talk", lambda:TalkToChildPt2(girl), True)
                        elif obj.name == "Girl":
                            boy.AssignInteraction("T", "Talk", lambda:TalkToChildPt2(boy), True)

                    def TalkToChildPt2(child):
                        childName = ""
                        ochildName = ""

                        if child.name == "Boy":
                            childName = "Edward"
                        elif child.name == "Girl":
                            childName = "Annabelle"

                        if IgnoreChild.name == "Boy":
                            ochildName = "Edward"
                        elif IgnoreChild.name == "Girl":
                            ochildName = "Annabelle"

                        Speech("Hey {}, I don't suppose you know why {} isn't talking to me".format(childName, ochildName), player)
                        Speech("...", player)
                        Speech("Not you too?", player)
                        Speech("I don't know what kind of joke you two think you're playing but it's not funny", player)
                        Speech("...", player)
                        Speech("Fine, you're both grounded", player)

                    boy.AssignInteraction("T", "Talk", lambda:TalkToChild(boy), True)
                    girl.AssignInteraction("T", "Talk", lambda:TalkToChild(girl), True)

                def ChildFunc():
                    Speech("Why is the door locked?", player)
                    string = "{} I hope you haven't been tampering with my room!"

                    if player.name == "Boy":
                        string = string.format("Annabelle")
                    elif player.name == "Girl":
                        string = string.format("Edward")

                    def func0():
                        def Talk():
                            string = "Hey {}, why is my door locked?"

                            if player.name == "Boy":
                                string = string.format("Annabelle")
                            elif player.name == "Girl":
                                string = string.format("Edward")

                            Speech(string, player)
                            string = "{}... Why aren't you listening to me?"

                            if player.name == "Boy":
                                string = string.format("Annabelle")
                            elif player.name == "Girl":
                                string = string.format("Edward")

                            Speech(string, player)

                            def func0():
                                Quests["ArgueSibling"] = True
                            Speech("I'm telling on you", player, func=(func0, "Start"))

                        Sibling.AssignInteraction("T", "Talk", Talk, True)

                    Speech(string, player, func=(func0, "End"))

                if player.name == "Boy" or player.name == "Girl":
                    if player.name == "Boy":
                        rect = pygame.Rect(53, 28, 3, 10)
                    elif player.name == "Girl":
                        rect = pygame.Rect(40, 28, 3, 10)
                    rect.x, rect.y = rect.x*bck.scale, rect.y*bck.scale
                    rect.w, rect.h = rect.w*bck.scale, rect.h*bck.scale
                    
                    CollideFunc(rect, ChildFunc)

                def ParentsRoomTran():
                    RoomChange("ParentsRoom")
                    SetPosition(player, "centerx", "top", player.rect.centerx, bck.scale)
                rect = pygame.Rect(41, 47, 15, 1)
                rect.x, rect.y = rect.x*bck.scale, rect.y*bck.scale
                rect.w, rect.h = rect.w*bck.scale, rect.h*bck.scale

                CollideFunc(rect, ParentsRoomTran).persis = True

        def SRoom():
            StorageRoom()

            if RoomEmpty():
                def func0():
                    PersisSong("BossMusic")

                    GhostAppears(woman)
                    WildGraceAppears("left", "bottom", 1, 46)
                    
                RoomAdd(woman)
                ChangeSprite(woman, woman.name+"IdleDown")
                SetPositionBck(woman, "centerx", "bottom", 48, 26)

                Speech("You...", woman)
                Speech("You broke my plant", woman)
                Speech("You will pay for what you have done", woman, func=(func0, "End"))

        def PRoom():
            if player.name == "Woman":
                ParentsRoomNoWoman()
            elif player.name == "Man":
                ParentsRoomNoMan()
            else:
                ParentsRoom()

            def BreakPlant():
                def Break():
                    def func0():
                        def func0():
                            def func0():
                                def func0():
                                    def func0():
                                        def func0():
                                            def WalkToPlant():
                                                def PickUpPlant():
                                                    RoomoveObject(Plant)
                                                    PersonMove(woman, ("centerx", "top"), (48, 0), 2, eFunc=lambda:RoomoveObject(woman))
                                                PersonMove(woman, ("centerx", "centery"), (Plant.rect.centerx/bck.scale, Plant.rect.centery/bck.scale), 2, eFunc=PickUpPlant)
                                            RoomoveObject(man)
                                            SetPositionBck(man, "centerx", "bottom", 48, 28)

                                            Speech("Looks like this plant needs to go into storage", woman, func=(WalkToPlant, "End"))
                                        PersonMove(man, ("centerx", "bottom"), (48, 32), 3, eFunc=func0)
                                    PersonMove(man, ("left", "bottom"), (40, 23), 3, eFunc=func0)

                                Speech("What's the problem?", man)
                                Speech("The plant just fell down!", woman)
                                Speech("I'll buy another one later, my program's almost over", man, func=(func0, "End"))
                                
                            xy = list(woman.rect.bottomright)
                            xy[0] += 4
                            xy[0] /= bck.scale
                            xy[1] /= bck.scale
                            PersonMove(man, ("left", "bottom"), xy, 3, eFunc=func0)
                            
                        RoomAdd(man)
                        SetPositionBck(man, "centerx", "bottom", 48, 32)
                        PersonMove(man, ("left", "bottom"), (40, 23), 3, eFunc=func0)
                        
                    Quests["BreakPlant"] = True
                    ChangeSprite(Plant, "PlantBroke")
                    SetPositionBck(Plant, "left", "top", 22, 22)
                    woman.RemoveAllInteractions()

                    Speech("Wha- What's going on?", woman)
                    Speech("Gerald! Could you come over here please?", woman, func=(func0, "End"))
                        
                Plant.AssignInteraction("B", "Break", Break, True)
                Quests["BreakPlant"] = False

            if RoomEmpty():
                if player.name != "Woman":
                    RoomAdd(woman)
                    SetPositionBck(woman, "left", "bottom", 2, 27)

                def MumFunc():
                    def func0():
                        def func0():
                            def func0():
                                def func0():
                                    def func0():
                                        RoomoveObject(sib2)
                                        Rooms["LivingRoom"][1].append(sib2)
                                        SetPositionBck(sib2, "left", "top", 35, 29)

                                        Quests["TalkToHusband"] = False

                                    PersonMove(sib2, ("centerx", "bottom"), (48, 32), 4, eFunc=func0)

                                RoomoveObject(sib1)
                                Rooms["LivingRoom"][1].append(sib1)
                                SetPositionBck(sib1, "right", "top", 61, 29)

                                RoomoveObjectFrom(sib2, "KidsRoom")
                                RoomAdd(sib2)
                                SetPosition(sib2, "centerx", "top", roomWidth/2, bck.scale)
                                Speech("No I'm not!", sib2, func=(func0, "Start"))
                            PersonMove(sib1, ("centerx", "bottom"), (48, 32), 3, eFunc=func0)

                        global sib1, sib2
                        sib1 = random.choice([boy, girl])
                        if sib1 == boy:
                            sib2 = girl
                        elif sib1 == girl:
                            sib2 = boy

                        RoomoveObjectFrom(sib1, "KidsRoom")
                        RoomAdd(sib1)
                        SetPosition(sib1, "centerx", "top", roomWidth/2, bck.scale)

                        string = "Daaad! {} is annoying me"
                        if sib1.name == "Boy":
                            string = string.format("Annabelle")
                        elif sib1.name == "Girl":
                            string = string.format("Edward")

                        Speech(string, sib1, func=(func0, "Start"))
                    Speech("What's... Happened... To my... ROOM!", player)
                    Speech("Gerald what have you done", player, func=(func0, "End"))

                def DadFunc():
                    def func0():
                        def func0():
                            def func0():
                                RoomoveObject(woman)
                                Quests["WifeIgnore"] = True

                                if Quests["ChildIgnore"]:
                                    Speech("Don't mind me, I'm just going to put this bedroom back to how it was", player)
                            PersonMoves([
                                [woman, ("left", "bottom"), (40, 23), 3],
                                [woman, ("centerx", "bottom"), (48, 33), 3, func0]
                                ])
                        if Quests["ChildIgnore"]:
                            Speech("Hey Elizabeth, do you know why the kids aren't talking to me?", player)
                            Speech("...", player)
                            Speech("Elizabeth don't do this to me", player)
                            Speech("Fine, ignore me then", player, func=(func0, "End"))
                        else:
                            Speech("Hey Elizabeth, I'm not sure about these bed covers...", player)
                            Speech("Elizabeth?", player)
                            Speech("I'm sorry, I didn't mean to upset you", player, func=(func0, "End"))
                    Speech("I didn't know Elizabeth was renovating our room", player)
                    Speech("Not sure about the choice of bed covers though...", player)

                    woman.AssignInteraction("T", "Talk", func0, True)

                if player.name == "Woman" or player.name == "Man":
                    rect = pygame.Rect(40, 16, 1, 9)
                    rect.x, rect.y = rect.x*bck.scale, rect.y*bck.scale
                    rect.w, rect.h = rect.w*bck.scale, rect.h*bck.scale

                    if player.name == "Woman":
                        func = MumFunc
                    elif player.name == "Man":
                        func = DadFunc
                        
                    CollideFunc(rect, func)

                elif player.name == "Boy" or player.name == "Girl":
                    def ChildFunc():
                        Speech("Hi mum", player)
                        Speech("Mum?", player)
                        Speech("Why are you ignoring me?", player)
                        Speech("I'm so angry I could just break something", player, func=(BreakPlant, "End"))

                        Quests["MumIgnore"] = True
                        woman.RemoveAllInteractions()
                    woman.AssignInteraction("T", "Talk", ChildFunc, True)
                
                def KidsRoomTran():
                    RoomChange("KidsRoom")
                    SetPositionBck(player, "centerx", "bottom", player.rect.centerx/bck.scale, 46)

                    if player.name == "Boy" or player.name == "Girl":
                        if "BreakPlant" in Quests:
                            if Quests["BreakPlant"]:
                                RoomChange("StorageRoom")

                rect = pygame.Rect(41, 0, 15, 1)
                rect.x, rect.y = rect.x*bck.scale, rect.y*bck.scale
                rect.w, rect.h = rect.w*bck.scale, rect.h*bck.scale

                CollideFunc(rect, KidsRoomTran).persis = True
                
                def LivingRoomTran():
                    if player.name == "Man":
                        if "WifeIgnore" in Quests:
                            if Quests["WifeIgnore"]:
                                RoomChange("BattleLivingRoom")
                                SetPositionBck(player, "centerx", "top", 8, 14)
                                return 0

                    RoomChange("LivingRoom")
                    SetPositionBck(player, "centerx", "top", 8, 14)
                rect = pygame.Rect(41, 33, 15, 2)
                rect.x, rect.y = rect.x*bck.scale, rect.y*bck.scale
                rect.w, rect.h = rect.w*bck.scale, rect.h*bck.scale

                CollideFunc(rect, LivingRoomTran).persis = True

            if player.name == "Boy" or player.name == "Girl":
                if Quests["ArgueSibling"] and not Quests["MumIgnore"]:
                    def func0():
                        def func0():
                            Quests["MumIgnore"] = True

                        string = "Mum! {} is annoying me"
                        if player.name == "Boy":
                            string = string.format("Annabelle")
                        elif player.name == "Girl":
                            string = string.format("Edward")
                            
                        Speech(string, player)
                        Speech("Muuuum", player)

                        Speech("Why is everybody ignoring me", player, func=(func0, "End"))
                        Speech("I'm so angry I could just break something", player, func=(BreakPlant, "End"))
                        woman.RemoveAllInteractions()
                    woman.AssignInteraction("C", "Complain", func0, True)

        def LRoom():
            LivingRoom()

            def TurnOffTv():
                def func0():
                    def func0():
                        def func0():
                            def func0():
                                def func0():
                                    RoomoveObject(woman)
                                    Rooms["ParentsRoom"][1].append(woman)
                                    SetPositionBck(woman, "left", "bottom", 2, 27)

                                    if not Quests["MumIgnore"]:
                                        Speech("I'll try talking to mum instead", player)
                                    elif "BreakPlant" in Quests:
                                        if Quests["BreakPlant"]:
                                            Speech("Now I feel bad for breaking the plant, I wonder how she's doing", player)
                                        else:
                                            Speech("Hmm... Maybe if her plant just so happened to fall, she'd notice me", player)
                                PersonMove(woman, ("centerx", "top"), (8, 14), 3, eFunc=func0)
                            Speech("Gerald, there is no problem. You just need to turn it on", woman)
                            Speech("I was just watching it and then it turned off by itself", man)
                            Speech("Well here you go, it's on now", woman, func=(func0, "End"))
                            if "BreakPlant" in Quests:
                                if Quests["BreakPlant"]:
                                    Speech("I'll join you when I finish putting the plant away", woman)
                        RoomAdd(woman)
                        SetPositionBck(woman, "centerx", "top", 8, 14)
                        PersonMove(woman, ("right", "centery"), (40, 40), 3, eFunc=func0)
                    Speech("*Bleep*", television)
                    Speech("What's going on?", man)
                    Speech("Elizabeth! The TV is doing that thing again!", man, func=(func0, "End"))

                television.AssignInteraction("T", "Turn Off", func0, True)

            if RoomEmpty():
                RoomAdd(man)
                SetPositionBck(man, "centerx", "bottom", 48, 28)

                if player.name == "Man":
                    RoomoveObject(man)

                elif player.name == "Woman":
                    def MumFunc():
                        if Quests["ChildIgnore"]:
                            Speech("Gerald, why don't the kids want to talk to me", player)
                            Speech("...", player)
                            Speech("Gerald? Why are you doing this to me?", player)
                            Speech("Can't you hear me?", player, func=(lambda:RoomChange("BattleLivingRoom"), "End"))
                        else:
                            Speech("What are you watching?", player)
                            Speech("Mind if I join in?", player)
                            Speech("...", player)
                            Speech("Gerald are you listening to me?", player, func=(lambda:RoomChange("BattleLivingRoom"), "End"))
                    man.AssignInteraction("T", "Talk", MumFunc, True)

                elif player.name == "Boy" or player.name == "Girl":
                    def ChildFunc():
                        Speech("Hi Dad", player)
                        Speech("Dad?", player)
                        Speech("The television can't be that intresting", player)
                        Speech("Hmmm I'm sure he'd notice me if I turned the television off", player, func=(TurnOffTv, "End"))
                    man.AssignInteraction("T", "Talk", ChildFunc, True)
                def ParentsRoomTran():
                    RoomChange("ParentsRoom")
                    SetPositionBck(player, "centerx", "bottom", 48, 32)
                rect = pygame.Rect(5, 12, 7, 1)
                rect.x, rect.y = rect.x*bck.scale, rect.y*bck.scale
                rect.w, rect.h = rect.w*bck.scale, rect.h*bck.scale

                CollideFunc(rect, ParentsRoomTran).persis = True

            if Quests["ArgueSibling"] and not Quests["DadIgnore"]:
                def func():
                    def func0():
                        Quests["DadIgnore"] = True

                    string = "Dad! {} is annoying me"
                    if player.name == "Boy":
                        string = string.format("Annabelle")
                    elif player.name == "Girl":
                        string = string.format("Edward")
                        
                    Speech(string, player)
                    Speech("Daaaad", player)

                    Speech("Why is everybody ignoring me!", player, func=(func0, "End"))
                    Speech("The television is getting more attention than I am", player, func=(TurnOffTv, "End"))
                man.AssignInteraction("C", "Complain", func, True)

            if "TalkToHusband" in Quests:
                if not Quests["TalkToHusband"]:
                    def func0():
                        def func0():
                            def func1(sib):
                                if sib.name == "Boy":
                                    SetPositionBck(sib, "right", "top", 81, 31)
                                elif sib.name == "Girl":
                                    SetPositionBck(sib, "left", "top", 14, 31)
                            def func0():
                                def func0():
                                    def func0():
                                        def func0():
                                            RoomoveObject(sib2)
                                            Rooms["KidsRoom"][1].append(sib2)
                                            func1(sib2)

                                            Speech("What were the kids up to now?", player)
                                            Speech("...", player)
                                            Speech("Gerald?", player)
                                            Speech("Gerald can't you here me?", player, func=(lambda:RoomChange("BattleLivingRoom"), "End"))
                                        PersonMove(sib2, ("centerx", "top"), (8, 14), 3, eFunc=func0)
                                    Speech("I didn't do anything!", sib2, func=(func0, "Start"))
                                RoomoveObject(sib1)
                                Rooms["KidsRoom"][1].append(sib1)
                                func1(sib1)

                                string = "You too, {}"
                                if sib2.name == "Boy":
                                    string = string.format("Edward")
                                if sib2.name == "Girl":
                                    string = string.format("Annabelle")
                                Speech(string, man, func=(func0, "End"))
                            PersonMove(sib1, ("centerx", "top"), (8, 14), 3, eFunc=func0)
                        Speech("Gerald, what's going on down here?", player)
                        Speech("Both of you to your rooms... Now!", man)

                        string = "You're so annoying {}"
                        if sib1.name == "Boy":
                            string = string.format("Annabelle")
                        elif sib1.name == "Girl":
                            string = string.format("Edward")
                        Speech(string, sib1, func=(func0, "Start"))
                    man.AssignInteraction("T", "Talk", func0, True)

        def BLRoom():
            BattleLivingRoom()

            if RoomEmpty():
                if player.name == "Man":
                    who = woman
                elif player.name == "Woman":
                    who = man

                def BattleStart():
                    PersisSong("BossMusic")

                    GhostAppears(who)
                    WildGraceAppears("left", "bottom", 1, 46)

                RoomAdd(who)
                ChangeSprite(who, who.name+"IdleDown")

                if who.name == "Man":
                    SetPositionBck(who, "centerx", "top", 48, Sofa.rect.bottom/bck.scale)
                    Speech("Yes I can hear you...", man)
                    Speech("But not for long", man, func=(BattleStart, "End"))
                elif who.name == "Woman":
                    def func0():
                        Speech("Well, that's fine, you don't need to like it", who, func=(BattleStart, "End"))
                    SetPositionBck(who, "left", "top", 15, 14)
                    Speech("So... You don't like the amendments I made to the room?", who, func=(lambda:PersonMove(who, ("centerx", "top"), 
                        (Sofa.rect.centerx/bck.scale, Sofa.rect.bottom/bck.scale), 3, eFunc=func0), "End"))

        global Rooms
        Rooms = {
            "KidsRoom":[KRoom, [], True],
            "StorageRoom":[SRoom, [], True],
            "ParentsRoom":[PRoom, [], True],
            "LivingRoom":[LRoom, [], True],
            "BattleLivingRoom":[BLRoom, [], True]
            }
        RoomChange("KidsRoom")

    def Level2a():
        global players

        global boy, girl
        boy = Boy()
        girl = Girl()

        players = [
        boy,
        girl
        ]

        for p in players:
            p.SetClothes("School")

        NewLevela()

        global grace
        grace = GraceChar()

        global Quests
        Quests = {
        "JRoomOpen":False,
        "TryOpenJRoom":False
        }

        def classRoomShift(ghstTyp):
            ranTables = []
            while len(ranTables) < 3:
                t = random.choice(Tables[random.randint(0, 2)])
                if t in ranTables:
                    continue

                ranTables.append(t)

            def func0():
                if len(ranTables) == 0:
                    return 0

                Replace(ranTables[0], ghstTyp())
                del ranTables[0]
            r = Repeater(3, func0)

        def Pground():
            Playground()

            def GiveKey():
                Quests["GetKey"] = False
                pygame.mixer.music.stop()

                global key
                key = InventoryInteract()
                FirstSprite(key, "Key")
                SetPosition(key, "centerx", "bottom", grace.rect.centerx, grace.rect.top-24)

                jumpy = Jumpy(2)
                jumpy.restTime = 1
                SetPosition(jumpy, "centerx", "bottom", grace.rect.centerx, cam[1]-24)
                ChangeCheckPerm(jumpy, "Angry", False)

                ChangeCheckPerm(player, "Moving", False)
                ChangeCheckPerm(player, "Shooting", False)

                def doCheck():
                    return not jumpy.rect.colliderect(key.rect)
                def doFunc():
                    jumpy.Move(0, jumpy.vspd)
                def endFunc():
                    RoomoveObject(key)

                    def func0():
                        def func0():
                            ChangeCheckPerm(jumpy, "Angry", True)
                            ChangeCheckPerm(jumpy, "Moving", True)
                        Timer(2, func0)

                        ChangeCheckPerm(player, "Moving", True)
                        ChangeCheckPerm(player, "Shooting", True)

                        PersisSong("UnexpectedFightMusic", 1)
                    Speech("That creature just swallowed the key?!", grace)
                    Speech("You know what to do", grace, func=(func0, "End"))

                DoCheck(doCheck, doFunc).endFunc = endFunc

                def doFunc0():
                    global dropJumpy
                    for r in Removes:
                        if hasis(r, "Enemy"):
                            dropJumpy = r
                DoCheck(lambda:True, doFunc0).highDepth = True
                
                def check0():
                    r = True
                    for o in Objects:
                        if hasis(o, "Enemy"):
                            r = False
                            break
                    return r
                def func0():
                    RoomAdd(key)
                    Drop(dropJumpy, key)
                    Quests["GetKey"] = True

                    Speech("Phew... That was a close one", grace)
                    StopPersisSong()
                    PlaySong("BackgroundMusic")
                Check(check0, func0)

            if RoomEmpty():
                #Players
                RoomAdd(boy)
                RoomAdd(girl)

                SetPosition(boy, "right", "bottom", roomWidth/2, roomHeight)
                SetPosition(girl, "left", "bottom", roomWidth/2, roomHeight)

                boy.rect.x -= 4
                girl.rect.x += 4

                RoomAdd(grace)
                SetPosition(grace, "centerx", "bottom", roomWidth/2, boy.rect.top-24)

                def Start():
                    global FirstGhosts
                    FirstGhosts = []

                    ghsts = [Ghost,
                        GhostPoison,
                        GhostFire,
                        GhostConfused,
                        GhostFreeze]

                    for g in ghsts:
                        ghst = g()
                        RandomSpawn(ghst)
                        FirstGhosts.append(ghst)

                    Speech("Here we are at your school... Hopefully it helps in the restoration of your memory", grace)
                    Speech("I'd transport you to the memory realm now but there is too much darkness here", grace)
                    Speech("If you would like to be transported there I suggest you reduce the amount of darkness", grace)

                    def check0():
                        for g in FirstGhosts:
                            if g in Rooms[CurrentRoom][1]:
                                return False
                        return True
                    def func0():
                        Quests["RemoveSchoolGhosts"] = False

                        def func0():
                            global GhostKills
                            GhostKills = 8

                            def func0():
                                global GhostKills
                                text("Ghosts Left: "+str(GhostKills), black, "centerx", "top", screenWidth/2, 4)

                                for r in Removes:
                                    if hasis(r, "Enemy"):
                                        GhostKills -= 1

                            def func1():
                                Quests["RemoveSchoolGhosts"] = True
                                Quests["RSCGrace"] = False
                                Speech("Okay I think this is enough", player)

                            global GhostKillsCheck
                            GhostKillsCheck = DoCheck(lambda:GhostKills>0, func0)

                            GhostKillsCheck.highDepth = True
                            AddPersis(GhostKillsCheck)

                            AddPersis(Check(lambda:GhostKills==0, func1))

                        Speech("Hmmm this is a good start but there's still darkness lurking in this school", grace, func=(func0, "End"))
                        Speech("This school is quite big, dashing might make traversing easier (shift)", grace)

                    Check(check0, func0)

                Check(lambda:player!=None, Start)

                def Cor1Tran():
                    if "GetKey" in Quests:
                        if not Quests["GetKey"]:
                            return 0

                    for g in FirstGhosts:
                        if g in Rooms[CurrentRoom][1]:
                            return 0

                    RoomChange("Corridor1")
                    SetPositionBck(player, "centerx", "bottom", 11, 79)
                Tran(pygame.Rect(73, 36, 21, 1), Cor1Tran)

            if "RemoveSchoolGhosts" in Quests:
                if Quests["RemoveSchoolGhosts"]:
                    if not Quests["RSCGrace"]:
                        Quests["RSCGrace"] = True

                        def func0():
                            Speech("Back so soon?", grace)
                            Speech("I thought I finished removing the darkness?", player)
                            Speech("I'm not sure about that, perhaps you forogt a room?", grace)
                            if Quests["TryOpenJRoom"]:
                                Speech("Well there was the janitor's room but it's locked", player)
                                Speech("Oh... Here, this key should work", grace, func=(GiveKey, "End"))
                            else:
                                Speech("Oh yes there was another room actually at the end of the corridor", player)
                                Speech("Well try looking there", grace)
                                Quests["TryOpenJRoom2"] = False

                                def func0():
                                    Speech("Hurry to the room you missed!", grace)
                                Check(WhenNormal, lambda:grace.AssignInteraction("T", "Talk", func0, False))

                        grace.AssignInteraction("T", "Talk", func0, True)
            if "TOJ2Grace" in Quests:
                if not Quests["TOJ2Grace"]:
                    Quests["TOJ2Grace"] = True
                    def func0():
                        Speech("It was locked...", grace)
                        Speech("Oh... This is awkward", grace)
                        Speech("Here take this key, it will be able to open the door", grace, func=(GiveKey, "End"))

                    grace.AssignInteraction("T", "Talk", func0, True)

            if "Finish" in Quests:
                if not Quests["Finish"]:
                    def func0():
                        Speech("Well done, it's definitely feeling a lot brighter already", grace)
                        Speech("Get ready... Memory realm here we come", grace)
                        Check(WhenNormal, lambda:Game(level, "b"))
                    grace.AssignInteraction("T", "Talk", func0, True)

        def Cor1():
            Corridor1()

            if RoomEmpty():
                def PgroundTran():
                    RoomChange("Playground")
                    SetPositionBck(player, "centerx", "top", 83, 37)
                Tran(pygame.Rect(0, 80, 24, 1), PgroundTran)

                def SClassTran():
                    RoomChange("ScienceClass")
                    SetPositionBck(player, "centerx", "bottom", 86, 95)
                Tran(pygame.Rect(25, 25, 10, 1), SClassTran)

                def MClassTran():
                    RoomChange("MathsClass")
                    SetPositionBck(player, "centerx", "bottom", 86, 95)
                Tran(pygame.Rect(65, 25, 9, 1), MClassTran)

                def Cor2Tran():
                    RoomChange("Corridor2")
                    SetPositionBck(player, "left", "centery", 1, player.rect.centery/bck.scale)
                Tran(pygame.Rect(95, 25, 1, 23), Cor2Tran)

        def Cor2():
            Corridor2()

            global lockedMes
            lockedMes = False

            if RoomEmpty():
                def Cor1Tran():
                    RoomChange("Corridor1")
                    SetPositionBck(player, "right", "centery", 94, player.rect.centery/bck.scale)
                Tran(pygame.Rect(0, 25, 1, 22), Cor1Tran)

                def EClassTran():
                    RoomChange("EnglishClass")
                    SetPositionBck(player, "centerx", "bottom", 86, 95)
                Tran(pygame.Rect(5, 25, 9, 1), EClassTran)

                def GClassTran():
                    RoomChange("GeographyClass")
                    SetPositionBck(player, "centerx", "bottom", 86, 95)
                Tran(pygame.Rect(43, 25, 9, 1), GClassTran)

                def JRoomTran():
                    global lockedMes
                    if not Quests["JRoomOpen"]:
                        if "GetKey" in Quests:
                            if Quests["GetKey"]:
                                if CheckInventory(key):
                                    Quests["JRoomOpen"] = True
                                    RemoveInventory(key)
                                    return 0

                        if not lockedMes:
                            Speech("It's locked", player)
                            lockedMes = True

                        if not Quests["TryOpenJRoom"] and "TryOpenJRoom2" not in Quests:
                            Quests["TryOpenJRoom"] = True
                        if "TryOpenJRoom2" in Quests:
                            if not Quests["TryOpenJRoom2"]:
                                Quests["TryOpenJRoom2"] = True
                                Quests["TOJ2Grace"] = False

                        return 0

                    RoomChange("JanitorsRoom")
                    SetPositionBck(player, "centerx", "bottom", 21, 46)
                Tran(pygame.Rect(80, 25, 9, 1), JRoomTran)

        def SClass():
            ScienceClass()

            if RoomEmpty():
                classRoomShift(GhostPoison)

                def Cor1Tran():
                    RoomChange("Corridor1")
                    SetPositionBck(player, "centerx", "top", 29, 26)
                Tran(pygame.Rect(85, 96, 12, 1), Cor1Tran)

        def MClass():
            MathsClass()

            if RoomEmpty():
                classRoomShift(GhostFreeze)

                def Cor1Tran():
                    RoomChange("Corridor1")
                    SetPositionBck(player, "centerx", "top", 69, 26)
                Tran(pygame.Rect(85, 96, 12, 1), Cor1Tran)

        def EClass():
            EnglishClass()

            if RoomEmpty():
                classRoomShift(GhostConfused)

                def Cor2Tran():
                    RoomChange("Corridor2")
                    SetPositionBck(player, "centerx", "top", 9, 26)
                Tran(pygame.Rect(85, 96, 12, 1), Cor2Tran)

        def GClass():
            GeographyClass()

            if RoomEmpty():
                classRoomShift(GhostFire)

                def Cor2Tran():
                    RoomChange("Corridor2")
                    SetPositionBck(player, "centerx", "top", 47, 26)
                Tran(pygame.Rect(85, 96, 12, 1), Cor2Tran)

        def JRoom():
            JanitorsRoom()

            if RoomEmpty():
                Speech("What is Grace talking about, there's nothing here", player)
                Quests["ExitJRoom"] = False

                def Cor2Tran():
                    if not Quests["ExitJRoom"]:
                        Quests["ExitJRoom"] = True
                        RoomChange("JanitorsMiniBossRoom")
                        SetPositionBck(player, "centerx", "top", 49, 19)
                        return 0

                    RoomChange("Corridor2")
                    SetPositionBck(player, "centerx", "top", 84, 26)
                Tran(pygame.Rect(15, 47, 13, 1), Cor2Tran)

        def JMBRoom():
            JanitorsMiniBossRoom()
            global Leave
            Leave = False

            if RoomEmpty():
                Speech("Oh...", player)
                PersisSong("BossMusic", 1)

                SetPosition(Jumpy(3), "centerx", "centery", roomWidth/2, roomHeight/2)

                def func0():
                    obj = None
                    for o in Objects:
                        if not hasattr(o, "Sprite"):
                            continue
                        if "BoxBig" in o.Sprite.name:
                            obj = o
                            break

                    if obj != None:
                        Replace(obj, RandomGhost())
                        Timer(5, func0)
                Timer(5, func0)

                def check1():
                    for o in Objects:
                        if hasis(o, "Enemy"):
                            return False
                    return True
                def func1():
                    global Leave
                    Leave = True

                    Speech("I need to get out of here", player)
                    StopPersisSong()
                    PlaySong("BackgroundMusic")
                Check(check1, func1)

                #Transitions
                def JRoomTran():
                    if not Leave:
                        return 0
                    
                    Quests["Finish"] = False
                    RoomChange("JanitorsRoom")
                    SetPositionBck(player, "centerx", "bottom", 21, 46)
                Tran(pygame.Rect(43, 17, 13, 1), JRoomTran)

        global Rooms
        Rooms = {
        "Playground":[Pground, [], True],
        "Corridor1":[Cor1, [], True],
        "Corridor2":[Cor2, [], True],

        "ScienceClass":[SClass, [], True],
        "MathsClass":[MClass, [], True],
        "EnglishClass":[EClass, [], True],
        "GeographyClass":[GClass, [], True],

        "JanitorsRoom":[JRoom, [], True],
        "JanitorsMiniBossRoom":[JMBRoom, [], True]
        }
        RoomChange("Playground")

    def Level2b():
        NewLevelb()

        global boy, girl
        boy = BoyChar()
        girl = GirlChar()

        global grace
        grace = GraceChar()
        RoomoveObject(grace)

        global jani
        jani = JanitorChar()
        RoomoveObject(jani)

        global ejani
        ejani = EPerson("Janitor")
        ejani.bullet = FireBullet
        ejani.mhp = ejani.hp = 3
        RoomoveObject(ejani)

        global MinionCount
        MinionCount = 1

        global woman
        woman = WomanChar()
        RoomoveObject(woman)

        global eman
        eman = EPerson("Man")
        eman.bullet = ConfusedBullet
        RoomoveObject(eman)

        global Sibling
        if player.name == "Boy":
            Sibling = girl
            RoomoveObject(boy)
        elif player.name == "Girl":
            Sibling = boy
            RoomoveObject(girl)
        Sibling.name = "School"+Sibling.name
        ChangeSprite(Sibling, Sibling.name+"IdleDown")

        global Quests
        Quests = {
        "Boss":False
        }

        def RTS():
            RoadToSchool()

            if RoomEmpty():
                RoomAdd(Sibling)

                SetPositionBck(player, "left", "centery", 1, 24)
                SetPosition(Sibling, "left", "bottom", player.rect.right+8, player.rect.bottom)

                def RunLate():
                    def Transis():
                        RoomoveObject(Sibling)
                    PersonMoves([
                        [Sibling, ("centerx", "centery"), (97, 24), 4],
                        [Sibling, ("centerx", "top"), (97, 18), 4, Transis]
                        ])
                Speech("I'm going to be late!", Sibling, func=(RunLate, "Start"))
                Speech("I remember this day... It was so funny to look back on", player)

                def PgroundTran():
                    RoomChange("Playground")
                    SetPosition(player, "centerx", "bottom", roomWidth/2, roomHeight-4)
                Tran(pygame.Rect(79, 18, 37, 1), PgroundTran)

        def Pground():
            Playground()

            if RoomEmpty():
                RoomAdd(Sibling)
                SetPositionBck(Sibling, "centerx", "bottom", 83, 126)

                def RunLate():
                    PersonMove(Sibling, ("centerx", "top"), (83, 35), 6, eFunc=lambda:RoomoveObject(Sibling))
                Speech("Ahh! Everyone has already gone into class!", Sibling, func=(RunLate, "Start"))
                Speech("I guess I'll follow", player)

                def RTSTran():
                    if Quests["Boss"]:
                        return 0

                    RoomChange("RoadToSchool")
                    SetPositionBck(player, "centerx", "top", 97, 19)
                Tran(pygame.Rect(50, 127, 67, 1), RTSTran)
                def Cor1Tran():
                    if Quests["Boss"]:
                        return 0

                    RoomChange("Corridor1")
                    SetPositionBck(player, "centerx", "bottom", 11, 79)
                Tran(pygame.Rect(73, 36, 21, 1), Cor1Tran)

            if "Confrontation" in Quests:
                if not Quests["Boss"]:
                    Quests["Boss"] = True

                    RoomAdd(ejani)
                    SetPositionBck(ejani, "centerx", "centery", 25, 98)

                    global minions
                    minions = []

                    def SpawnMinions():
                        global MinionCount

                        ejani.Invinsible()
                        coords = [
                        ["right", "centery", ejani.rect.left-8, ejani.rect.centery],
                        ["left", "centery", ejani.rect.right+8, ejani.rect.centery],
                        ["centerx", "bottom", ejani.rect.centerx, ejani.rect.top-8],
                        ["centerx", "top", ejani.rect.centerx, ejani.rect.bottom+8]
                        ]

                        for i in range(MinionCount):
                            co = coords[i]

                            minion = JumpyRandom()
                            SetPosition(minion, co[0], co[1], co[2], co[3])

                            minions.append(minion)
                        MinionCount += 1

                        def check():
                            for o in Objects:
                                if o not in minions:
                                    continue
                                
                                return False
                            return True
                        def func():
                            ejani.StopInvinsible()
                            Speech("Here's my chance!", player)

                            global oldHp
                            oldHp = ejani.hp

                            def check():
                                if ejani.checks["Dead"]:
                                    return False

                                if ejani.hp < oldHp:
                                    return True
                            def func():
                                ejani.Invinsible()
                                Timer(1, SpawnMinions)
                            Check(check, func)
                        Check(check, func)

                    def Start():
                        def func0():
                            SpawnMinions()
                            Speech("No way! He's invinsible while his minions are out", player)
                        Speech("Well, well, well... If it isn't the trespasser's accomplice", ejani, func=(func0, "End"))
                        PersisSong("BossMusic", 1)
                    Check(lambda:dist(player, ejani) < minDist(player, ejani)*3, Start)

                    def WinFunc():
                        RoomAdd(grace)
                        SetPosition(grace, "left", "bottom", player.rect.right+8, player.rect.bottom)

                        Speech("Woah that was some wicked action! You did it!", grace)
                        Speech("Alas our journey must continue onward", grace)

                        Check(WhenNormal, LevelComplete)
                    Check(lambda:ejani not in Objects, WinFunc)

        def Cor1():
            Corridor1()

            if RoomEmpty():
                RoomAdd(Sibling)
                SetPositionBck(Sibling, "centerx", "bottom", 12, 80)

                def RunLate():
                    def func0():
                        RoomoveObject(Sibling)

                        def func0():
                            def func0():
                                RoomoveObject(Sibling)

                                def func0():
                                    RoomAdd(Sibling)
                                    Speech("Not this one either!", Sibling, func=(lambda:PersonMove(Sibling, ("right", "top"), (95, 25), 4, eFunc=lambda:RoomoveObject(Sibling)), "End"))
                                    Check(WhenNormal, lambda:Speech("I can't wait to see this", player))
                                Check(WhenNormal, lambda:Timer(1, func0))
                            RoomAdd(Sibling)
                            Speech("Nope not this one", Sibling, func=(lambda:PersonMove(Sibling, ("centerx", "top"), (69, 25), 4, eFunc=func0), "End"))
                        Check(WhenNormal, lambda:Timer(1, func0))
                    PersonMoves([
                        [Sibling, ("centerx", "bottom"), (12, 47), 4],
                        [Sibling, ("centerx", "top"), (30, 25), 4, func0]
                        ])
                Speech("What classroom is mine again?", Sibling, func=(RunLate, "Start"))

                #Transitions
                def PgroundTran():
                    RoomChange("Playground")
                    SetPositionBck(player, "centerx", "top", 83, 37)
                Tran(pygame.Rect(0, 80, 24, 1), PgroundTran)

                def SClassTran():
                    if "Confrontation" in Quests:
                        if Rooms["ScienceClass"][0] == SClass:
                            global GoToIndex
                            Rooms["ScienceClass"] = [lambda:GoToRooms[GoToIndex]("Corridor1", (25, 26)), [], True]
                            GoToIndex += 1
                    RoomChange("ScienceClass")

                    if "Confrontation" in Quests:
                        SetPositionBck(player, "centerx", "bottom", 48, 46)
                    else:
                        SetPositionBck(player, "centerx", "bottom", 86, 95)
                Tran(pygame.Rect(25, 25, 10, 1), SClassTran)

                def MClassTran():
                    if "Confrontation" in Quests:
                        if Rooms["MathsClass"][0] == MClass:
                            global GoToIndex
                            Rooms["MathsClass"] = [lambda:GoToRooms[GoToIndex]("Corridor1", (69, 26)), [], True]
                            GoToIndex += 1
                    RoomChange("MathsClass")

                    if "Confrontation" in Quests:
                        SetPositionBck(player, "centerx", "bottom", 48, 46)
                    else:
                        SetPositionBck(player, "centerx", "bottom", 86, 95)
                Tran(pygame.Rect(65, 25, 9, 1), MClassTran)

                def Cor2Tran():
                    RoomChange("Corridor2")
                    SetPositionBck(player, "left", "centery", 1, player.rect.centery/bck.scale)
                Tran(pygame.Rect(95, 25, 1, 23), Cor2Tran)

            if "Confrontation" in Quests:
                if not Quests["Confrontation"]:
                    Quests["Confrontation"] = True

                    Shakey.Shake()
                    Speech("Woah what's going on?", player)
                    Speech("That sounded like it came from the playground!", player)

        def Cor2():
            Corridor2()

            if RoomEmpty():
                RoomAdd(Sibling)
                SetPositionBck(Sibling, "left", "centery", 0, 35)

                def func0():
                    PersonMove(Sibling, ("centerx", "centery"), (47, 35), 4)

                    def func0():
                        RoomAdd(jani)
                        SetPositionBck(jani, "centerx", "top", 84, 25)

                        Speech("Hey, you know that school's not on today right?", jani, func=(lambda:PersonMove(jani, ("left", "centery"), (60, 35), 2), "Start"))
                        Speech("Oh... Sorry, I'll make my way out", Sibling)

                        def func0():
                            PersonMove(Sibling, ("centerx", "centery"), (28, 35), 4)

                            def func0():
                                SetPosition(jani, "right", "bottom", Sibling.rect.left-8, Sibling.rect.bottom)
                                Speech("Stop right there... Where do you think you're going?", jani)
                                Speech("Wait a minute... This never happened", player)

                                if player.name == "Boy":
                                    playerName = "Edward"
                                    SibName = "Annabelle"
                                    pronoun = "her"
                                elif player.name == "Girl":
                                    playerName = "Annabelle"
                                    SibName = "Edward"
                                    pronoun = "him"

                                def func0():
                                    def func0():
                                        Explode(Sibling)
                                        Explode(jani)
                                    RoomAdd(grace)
                                    SetPosition(grace, "left", "bottom", Sibling.rect.right+32, Sibling.rect.bottom)
                                    Speech("Don't worry {}, this isn't real, it's just the darkness trying to corrupt your memory!".format(playerName), grace, func=(func0, "End"))

                                    Speech("I know... I just hate seeing {} in trouble and the thought of anything happening to {}".format(SibName, pronoun), player)
                                    Speech("Real... Or not...", player)
                                    Speech("I know it's hard but just try not to become attatched to these memories", grace, func=(lambda:Explode(grace), "End"))

                                    Speech("I know- but... It's hard", player)

                                    Quests["Confrontation"] = False
                                
                                Speech("Hey get away from {}!".format(pronoun), player, func=(func0, "End"))

                            Check(WhenNormal, func0)
                        Speech("Ha ha ha! Priceless", player, func=(func0, "End"))
                    Check(WhenNormal, func0)
                Speech("Urmm", Sibling, func=(func0, "Start"))

                def Cor1Tran():
                    if GoToIndex == -1:
                        SetPosition(player, "right", "centery", roomWidth, player.rect.centery)
                        return 0
                    RoomChange("Corridor1")
                    SetPositionBck(player, "right", "centery", 94, player.rect.centery/bck.scale)
                Tran(pygame.Rect(0, 25, 1, 22), Cor1Tran)

                def EClassTran():
                    if "Confrontation" in Quests:
                        if Rooms["EnglishClass"][0] == EClass:
                            global GoToIndex
                            Rooms["EnglishClass"] = [lambda:GoToRooms[GoToIndex]("Corridor2", (9, 26)), [], True]
                            GoToIndex += 1
                    RoomChange("EnglishClass")

                    if "Confrontation" in Quests:
                        SetPositionBck(player, "centerx", "bottom", 48, 46)
                    else:
                        SetPositionBck(player, "centerx", "bottom", 86, 95)
                Tran(pygame.Rect(5, 25, 9, 1), EClassTran)

                def GClassTran():
                    if "Confrontation" in Quests:
                        if Rooms["GeographyClass"][0] == GClass:
                            global GoToIndex
                            Rooms["GeographyClass"] = [lambda:GoToRooms[GoToIndex]("Corridor2", (47, 26)), [], True]
                            GoToIndex += 1
                    RoomChange("GeographyClass")

                    if "Confrontation" in Quests:
                        SetPositionBck(player, "centerx", "bottom", 48, 46)
                    else:
                        SetPositionBck(player, "centerx", "bottom", 86, 95)
                Tran(pygame.Rect(43, 25, 9, 1), GClassTran)

                def JRoomTran():
                    RoomChange("JanitorsRoom")
                    SetPositionBck(player, "centerx", "bottom", 21, 46)
                Tran(pygame.Rect(80, 25, 9, 1), JRoomTran)

        def SClass():
            ScienceClass()

            if RoomEmpty():
                def Cor1Tran():
                    RoomChange("Corridor1")
                    SetPositionBck(player, "centerx", "top", 30, 26)
                Tran(pygame.Rect(82, 96, 15, 1), Cor1Tran)

        def MClass():
            MathsClass()

            if RoomEmpty():
                def Cor1Tran():
                    RoomChange("Corridor1")
                    SetPositionBck(player, "centerx", "top", 69, 26)
                Tran(pygame.Rect(82, 96, 15, 1), Cor1Tran)

        def EClass():
            EnglishClass()

            if RoomEmpty():
                def Cor2Tran():
                    RoomChange("Corridor2")
                    SetPositionBck(player, "centerx", "top", 9, 26)
                Tran(pygame.Rect(82, 96, 15, 1), Cor2Tran)

        def GClass():
            GeographyClass()

            if RoomEmpty():
                def Cor2Tran():
                    RoomChange("Corridor2")
                    SetPositionBck(player, "centerx", "top", 47, 26)
                Tran(pygame.Rect(82, 96, 15, 1), Cor2Tran)

        def KRoom0(room="", xy=(0, 0)):
            if player.name == "Boy":
                KidsRoomNoBoy()
            elif player.name == "Girl":
                KidsRoomNoGirl()

            if RoomEmpty():
                RoomAdd(woman)
                SetPositionBck(woman, "centerx", "top", 48, 19)

                Speech("Shouldn't you be in school?", woman)
                Check(WhenNormal, lambda:Replace(woman, Ghost()))

                def CorxTran():
                    for o in Objects:
                        if hasis(o, "Enemy"):
                            return 0

                    RoomChange(room)
                    SetPositionBck(player, "centerx", "top", xy[0], xy[1])

                Tran(pygame.Rect(41, 47, 15, 1), CorxTran)

        def KRoom1(room="", xy=(0, 0)):
            if player.name == "Boy":
                KidsRoomNoBoy()
            elif player.name == "Girl":
                KidsRoomNoGirl()

            if RoomEmpty():
                RoomAdd(grace)
                SetPositionBck(grace, "centerx", "top", 48, 19)

                Speech("Don't believe everything you see...", grace)
                Check(WhenNormal, lambda:Replace(grace, GhostPoison()))

                def CorxTran():
                    for o in Objects:
                        if hasis(o, "Enemy"):
                            return 0

                    RoomChange(room)
                    SetPositionBck(player, "centerx", "top", xy[0], xy[1])
                Tran(pygame.Rect(41, 47, 15, 1), CorxTran)

        def KRoom2(room="", xy=(0, 0)):
            if player.name == "Boy":
                KidsRoomNoBoy()
            elif player.name == "Girl":
                KidsRoomNoGirl()

            if RoomEmpty():
                RoomAdd(Sibling)
                SetPositionBck(Sibling, "centerx", "top", 48, 19)

                if player.name == "Boy":
                    sib = "brother"
                elif player.name == "Girl":
                    sib = "sister"

                Speech("I wish I had a {}".format(sib), Sibling)
                Check(WhenNormal, lambda:Replace(Sibling, Jumpy()))

                def CorxTran():
                    for o in Objects:
                        if hasis(o, "Enemy"):
                            return 0

                    RoomChange(room)
                    SetPositionBck(player, "centerx", "top", xy[0], xy[1])
                Tran(pygame.Rect(41, 47, 15, 1), CorxTran)

        def KRoom3(room="", xy=(0, 0)):
            if player.name == "Boy":
                KidsRoomNoBoy()
            elif player.name == "Girl":
                KidsRoomNoGirl()

            if RoomEmpty():
                RoomAdd(jani)
                SetPositionBck(jani, "centerx", "top", 48, 19)

                Speech("Why are you still here?", jani)
                Speech("Did you not hear me tell that other student to go?", jani)

                Check(WhenNormal, lambda:Replace(jani, GhostFreeze()))

                def CorxTran():
                    for o in Objects:
                        if hasis(o, "Enemy"):
                            return 0

                    RoomChange(room)
                    SetPositionBck(player, "centerx", "top", xy[0], xy[1])
                Tran(pygame.Rect(41, 47, 15, 1), CorxTran)

        def LRoom():
            LivingRoom()

            if RoomEmpty():
                def JRoomTran():
                    RoomChange("JanitorsRoom")
                    SetPosition(player, "")

        def JRoom():
            JanitorsRoom()

            if RoomEmpty():
                Quests["LivingRoomTran"] = False

                def Cor2Tran():
                    if not Quests["LivingRoomTran"]:
                        RoomChange("LivingRoom")
                        SetPositionBck(player, "centerx", "top", 8, 14)
                        Quests["LivingRoomTran"] = True
                        return 0

                    RoomChange("Corridor2")
                    SetPositionBck(player, "centerx", "top", 84, 26)
                Tran(pygame.Rect(15, 47, 13, 1), Cor2Tran)

        def LRoom():
            LivingRoom()

            if RoomEmpty():
                RoomAdd(eman)
                SetPositionBck(eman, "centerx", "bottom", 48, 32)

                if player.name == "Boy":
                    playerName = "Edward"
                    childPro = "son"
                elif player.name == "Girl":
                    playerName = "Annabelle"
                    childPro = "daughter"

                PersisSong("UnexpectedFightMusic", 1)

                Speech("You wouldn't hurt your dad would you?", eman)
                Speech("You're not real", player)
                Speech("Well... That's a bit harsh {}".format(playerName), eman)

                Check(lambda:eman.hp <= 2, lambda:Speech("I thought you were my {}...".format(childPro), eman))

                def JRoomTran():
                    for o in Objects:
                        if hasis(o, "Enemy"):
                            return 0
                    StopPersisSong()

                    RoomChange("JanitorsRoom")
                    SetPositionBck(player, "centerx", "bottom", 21, 46)
                Tran(pygame.Rect(5, 13, 7, 1), JRoomTran)

        global GoToRooms, GoToIndex
        GoToIndex = -1

        GoToRooms = [
        KRoom0,
        KRoom1,
        KRoom2,
        KRoom3
        ]

        global Rooms
        Rooms = {
        "RoadToSchool":[RTS, [], True],
        "Playground":[Pground, [], True],
        "Corridor1":[Cor1, [], True],
        "Corridor2":[Cor2, [], True],

        "ScienceClass":[SClass, [], True],
        "MathsClass":[MClass, [], True],
        "EnglishClass":[EClass, [], True],
        "GeographyClass":[GClass, [], True],

        "JanitorsRoom":[JRoom, [], True],
        "LivingRoom":[LRoom, [], True]
        }
        RoomChange("RoadToSchool")

    def Level3a():
        global man, woman
        man = Man()
        woman = Woman()

        global players
        players = [
        man,
        woman
        ]

        for p in players:
            AddPersis(p)
            p.SetClothes("Wedding")

        NewLevela()

        global grace
        grace = GraceChar()

        global boy, girl
        boy = BoyChar()
        girl = GirlChar()

        def Ghostify(obj):
            ChangeAlpha(obj, 128)

        Ghostify(boy)
        Ghostify(girl)

        global oldItem, newItem, borItem, bluItem
        oldItem = InventoryInteract()
        newItem = InventoryInteract()
        borItem = InventoryInteract()
        bluItem = InventoryInteract()

        FirstSprite(oldItem, "oldItem")
        FirstSprite(newItem, "newItem")
        FirstSprite(borItem, "borItem")
        FirstSprite(bluItem, "bluItem")

        global Quests
        Quests = {
        "Start":False
        }

        def OtherPlayer():
            if player.name == "Man":
                return woman
            elif player.name == "Woman":
                return man

        def WRoom():
            WeddingRoom()

            if RoomEmpty():
                RoomAdd(woman)
                RoomAdd(grace)

                RoomAdd(man)

                SetPositionBck(woman, "left", "bottom", 6, 35)
                SetPositionBck(grace, "right", "bottom", 20, 35)

                SetPositionBck(man, "right", "bottom", 49, 35)

                def Start():
                    for i in range(3):
                        if i < 2:
                            e = Ghost()
                        else:
                            e = Jumpy()
                        RandomSpawn(e)
                        man.AddObject(e)

                    pos = (
                        (roomWidth*.25/bck.scale, 17),
                        (roomWidth*.5/bck.scale, 17),
                        (roomWidth*.75/bck.scale, 17)
                        )

                    for i in range(3):
                        ghst = Ghost()
                        ghst.mhp = ghst.hp = 1
                        SetPositionBck(ghst, "centerx", "top", pos[i][0], pos[i][1])

                    Speech("This is...", grace)
                    Speech("My wedding day..", player)
                    Speech("I'm not letting the darkness take this memory from me!", player, func=(Earthquake, "End"))

                    Speech("Wow... I didn't know you had that in you", grace)
                    Speech("Nothing is going to ruin my wedding day", player)

                    Speech("Well...", grace)
                    Speech("What?", player)
                    Speech("I know you can't see him but your husband...", grace)
                    Speech("He's still in danger, press ctrl to help him", grace)

                    def What():
                        Speech("My wedding day?", player)
                        Speech("Yes, it might help restore your memory", grace)
                        Speech("Before we can do that you must eliminate the darkness!", grace)

                        def check0():
                            for o in Objects:
                                if hasis(o, "Enemy"):
                                    return False
                            return True
                        def func0():
                            Quests["Start"] = True
                            Speech("Okay now what?", man)
                            Speech("Well... There are children haunting the room outside this one", grace)
                            Speech("I don't like ghosts... They creep me out", grace)

                            def Talk():
                                if player.name == "Man":
                                    if "MBoss" in Quests:
                                        if Quests["MBoss"]:
                                            Speech("Well done... You have freed this area of darkness", grace)
                                            Speech("Now we depart to the memory realm", grace)
                                            Check(WhenNormal, lambda:Game(level, "b"))
                                            return 0
                                elif player.name == "Woman":
                                    if "WBoss" in Quests:
                                        if Quests["WBoss"]:          

                                            def GiveItems():
                                                for g in GetItems:
                                                    for i in Instances(InventoryBox):
                                                        if i.item == g:
                                                            i.Remove()

                                            Speech("Here is everything you asked for", player, func=(GiveItems, "End"))
                                            Speech("Thank you.", grace)
                                            Speech("I'm sure all of our happy endings are near", grace, func=(lambda:Explode(grace), "End"))
                                            Speech("All? What's that supposed to mean?", player)

                                            Check(WhenNormal, lambda:Game(level, "b"))
                                            return 0

                                Speech("Please come back to me when you have finished the task I gave you", grace)
                            grace.AssignInteraction("T", "Talk", Talk, False)

                        c = Check(check0, func0)
                        man.AddObject(c)
                    Check(lambda:player.name=="Man", What)

                Check(lambda:player!=None, Start)

                def checkWomanStart():
                    if Quests["Start"]:
                        if player.name == "Woman":
                            return True

                def WomanGiveQuest():
                    def StartQuest():   
                        Quests["SpawnWItems"] = False
                        global GetItems

                        GetItems = [
                        oldItem,
                        newItem,
                        borItem,
                        bluItem,
                        ]

                        def check():
                            if player.name != "Woman":
                                return False

                            for g in GetItems:
                                if not CheckInventory(g):
                                    return False

                            return True

                        def func():
                            Speech("There... I have all the items she asked for", player)

                        AddPersis(Check(check, func))

                        def doCheck():
                            if player.name != "Woman":
                                return False

                            for g in GetItems:
                                if not CheckInventory(g):
                                    return True
                            return False

                        def doFunc():
                            findItems = []
                            for g in GetItems:
                                if not CheckInventory(g):
                                    if g == oldItem:
                                        name = "Old Item"
                                    elif g == newItem:
                                        name = "New Item"
                                    elif g == borItem:
                                        name = "Borrowed Item"
                                    elif g == bluItem:
                                        name = "Blue Item"
                                    findItems.append(name)

                            txt = "Items to find: "

                            l = len(findItems)
                            for i in range(l):
                                txt += findItems[i]

                                if i < l-1:
                                    txt += ", "

                            text(txt, midBlack, "centerx", "top", screenWidth/2, 4)
                        AddPersis(DoCheck(doCheck, doFunc))

                    Speech("Elizabeth?", grace)
                    Speech("What?", player)
                    Speech("I was thinking about how you said this was your special day", grace)
                    Speech("If you want we can prepare for it. It just requires that you collect some things", grace)
                    Speech("Like what?", player)
                    Speech("Oh you know, something old, something new, something borrowed and something blue?", grace, func=(StartQuest, "End"))
                    Speech("Is that all?", player)
                    Speech("Yes, now get going. Neither of us want to be here I'm sure", grace)

                    Quests["WomanWarn"] = False

                Check(checkWomanStart, WomanGiveQuest)

                def SRoomTran():
                    if not Quests["Start"]:
                        if player.name == "Woman":
                            if "StartWomanPrompt" not in Quests:
                                Quests["StartWomanPrompt"] = True
                                Speech("Elizabeth, your husband is still in danger", grace)
                                Speech("You can't see the trouble he faces, only he can save himself (press ctrl)", grace)
                        elif player.name == "Man":
                            if "StartManPrompt" not in Quests:
                                Quests["StartManPrompt"] = True
                                Speech("Gerald you will need to clear this room of darkness before you can progress", grace)
                        return 0

                    if "WomanWarn" in Quests:
                        if not Quests["WomanWarn"]:
                            Quests["WomanWarn"] = True
                            Speech("By the way... The next room is haunted", grace, func=(lambda:Quests.pop("WomanWarn"), "End"))

                        return 0

                    RoomChange("SuperMarket")
                    SetPositionBck(player, "centerx", "top", 32, 17)

                    player.SetClothes("")
                Tran(pygame.Rect(24, 86, 17, 1), SRoomTran)

        def BWRoom():
            BaseWeddingRoom()

            if RoomEmpty():
                j = Jumpy(2)
                RoomoveObject(j)

                box = Box(j)
                ChangeSprite(box, "BoxBig")
                SetPosition(box, "centerx", "centery", roomWidth/2, roomHeight/2)

        def SRoom():
            SuperMarket()

            def Barrier(x, y, w, h, player=None):
                wall = Wall()
                rect = pygame.Rect(0, 0, w, h)
                ChangeRect(wall, rect)
                ChangeScale(wall, bck.scale)
                SetPositionBck(wall, "left", "top", x, y)

                wall.checks["Display"] = True

                if player != None:
                    player.AddObject(wall)

                return wall

            if RoomEmpty():
                coords = (
                    (32, 62),
                    (70, 62),
                    (108, 62)
                    )

                for i in range(len(coords)):
                    SetPositionBck(Private(), "centerx", "bottom", coords[i][0], coords[i][1])

                def WRoomTran():
                    player.SetClothes("Wedding")

                    if "WBoss" in Quests and player.name == "Woman":
                        if not Quests["WBoss"]:
                            Quests["WBoss"] = True

                            RoomChange("StorageRoom")
                            SetPositionBck(player, "centerx", "bottom", 48, 46)
                            return 0

                    RoomChange("WeddingRoom")
                    SetPositionBck(player, "centerx", "bottom", 32, 85)

                Tran(pygame.Rect(23, 15, 19, 1), WRoomTran)

            if CurrentRoom not in player.Objects:
                player.Objects[CurrentRoom] = []

                if player.name == "Man":
                    b = [
                    Barrier(22, 16, 1, 20, player),
                    Barrier(42, 16, 1, 20, player),
                    Barrier(23, 36, 19, 1, player)
                    ]

                    rect = pygame.Rect(44, 17, 7, 7)
                    rect = BckRect(rect)

                    def func():
                        Speech("It doesn't look like this button did anything", player)
                        for wall in b:
                            RoomoveObject(wall)
                        Quests["ManTrapped"] = False

                    button = PushSwitch(rect, func)

                    Speech("Why are there walls here?", player)
                    Speech("And that button is so close yet so far...", player)
                    Speech("Only if someone could press it.", player)

                    Quests["ManTrapped"] = True

                elif player.name == "Woman":
                    Barrier(84, 16, 1, 20, player)

                    def func():
                        bars = [
                        Barrier(118, 63, 1, 24),
                        Barrier(99,62,19,1)
                        ]

                        rect = pygame.Rect(120, 74, 7, 7)
                        rect = BckRect(rect)
                        SetPositionBck(rect, "left", "centery", 120, 74)

                        def func():
                            Speech("Where did the bar go?", player)
                            for bar in bars:
                                RoomoveObject(bar)
                            Quests["WomanTrapped"] = False

                        button = PushSwitch(rect, func)
                        Speech("Who's idea was it to put a button BEHIND the barrier?", player)
                        Speech("There's no way for me to reach it", player)

                        Quests["WomanTrapped"] = True

                    rect = pygame.Rect(84, 63, 15, 24)
                    rect = BckRect(rect)
                    player.AddObject(CollideFunc(rect, func))

            if "SpawnWItems" in Quests:
                if not Quests["SpawnWItems"] and player.name == "Woman":
                    Quests["SpawnWItems"] = True

                    class WeddingBox(Box):
                        def BonusOpen(self):
                            if self.item == oldItem:
                                Speech("These were the earrings I wore when I first met Gerald", player)
                            elif self.item == newItem:
                                Speech("Hmm I bought these new shoes but I don't even wear shoes", player)
                            elif self.item == borItem:
                                Speech("This was the bracelet my mum wore at her wedding", player)
                            elif self.item == bluItem:
                                Speech("I'm sure this blue hair bow will go well with my white dress", player)

                            def Haunt():
                                hauntSpeech = [
                                "Wow, you find your first item!",
                                "Another one?! You're good at this!",
                                "Third... Hmm I wonder where the fourth is..."
                                ]

                                itemsFound = 0
                                for g in GetItems:
                                    if CheckInventory(g):
                                        itemsFound += 1

                                RoomAdd(boy)
                                boy.rect.center = self.rect.center
                                Speech(hauntSpeech[itemsFound-1], boy, func=(lambda:Explode(boy), "End"))

                            Check(WhenNormal, Haunt)

                    numChoice = [0,1,2,3]
                    for i in range(3):
                        ranIndex = random.choice(numChoice)
                        numChoice.remove(ranIndex)

                        box = WeddingBox(GetItems[ranIndex])
                        player.AddObject(box)

                    global finalBox
                    finalBox = WeddingBox(GetItems[numChoice[0]])
                    RoomoveObject(finalBox)

                    for i in range(6):
                        j = Jumpy()
                        RoomoveObject(j)
                        
                        box = Box(j)
                        player.AddObject(box)

                    def ThreeFound():
                        found = 0
                        for g in GetItems:
                            if CheckInventory(g):
                                found += 1

                        return found == 3

                    def PrepareBossBattle():
                        Quests["WBoss"] = False

                    Check(ThreeFound, PrepareBossBattle)

            if "ManTrapped" in Quests and player.name == "Man":
                if not Quests["ManTrapped"]:
                    Quests.pop("ManTrapped")

                    def Haunt(i=0):
                        hauntSpeech = [
                        "You can't catch me!",
                        "Come on! Play with me!",
                        "...",
                        "Why aren't you moving?",
                        "Don't you like me?",
                        "Hellooo?",
                        "... You're weird."
                        ]

                        if i >= len(hauntSpeech):
                            Explode(girl)

                            def Reappear():
                                RoomAdd(girl)
                                SetPositionBck(girl, "right", "bottom", 169, 60)

                                player.AddObject(girl)
                                Quests["TalkToGirl"] = False

                                Speech("I'm sorry... I was mean...", girl)
                                Speech("I'll just wait here so we can play when you're ready!", girl)

                                global waitTime
                                waitTime = 0

                                def IncreaseTime():
                                    global waitTime
                                    waitTime += 1/FPS
                                DoCheck(lambda:not Quests["TalkToGirl"], IncreaseTime)

                                def Game():
                                    Quests["TalkToGirl"] = True

                                    Speech("Yay! You're here!", girl)
                                    Speech("...You took "+str(round(waitTime))+" seconds to do so", girl)

                                    if waitTime <= 10:
                                        Speech("That's really good! Thanks for not keeping me waiting, I'm not very patient", girl)
                                    elif waitTime < 60:
                                        Speech("That's not too bad! Any longer than a minute and I might have gone craaazy!", girl)
                                    else:
                                        Speech(str(round(waitTime))+"... Seconds... Do you not know how long that is?!", girl)
                                        Speech("I don't want to play with you anymore", girl)
                                        Speech("I'm sorry!", player)
                                        Speech("Nope. Too late", girl)
                                        Speech("You had your chance and you blew it", girl)
                                        Speech("Next time be less than a minute", girl)

                                        def Battle():
                                            RoomChange("NoWhere")

                                            global egirl, egirls
                                            egirls = []

                                            dist = 256

                                            def Egirl():
                                                egirl = EPerson("Girl")
                                                egirl.rect.center = girl.rect.center

                                                egirl.mhp = egirl.hp = 4
                                                egirl.bullet = ConfusedBullet

                                                egirl.sightRange = egirl.fleeRange = int(dist*1.5)

                                                return egirl

                                            egirl = Egirl()
                                            egirls.append(egirl)

                                            deats = [
                                            [(0, -dist), "Hello"],
                                            [(-dist, 0), "More like hasta la vista"],
                                            [(0, dist), "Come on guys, let's be kind!"]
                                            ]

                                            def Friends(i=0):
                                                if i >= len(deats):
                                                    Speech("This is no time for jokes...", egirl)
                                                    Speech("Now... We must begin", egirl)

                                                    song = [
                                                    "Ring-a-ring o' roses",
                                                    "A pocket full of posies",
                                                    "A-tishoo! A-tishoo!",
                                                    "We all fall down!"
                                                    ]

                                                    for i in range(len(song)):
                                                        g = egirls[i%len(egirls)]
                                                        Speech(song[i], g)

                                                    def check():
                                                        for g in egirls:
                                                            if g in Objects:
                                                                return False
                                                        return True

                                                    def func():
                                                        global bckCol
                                                        bckCol = grey

                                                        RoomChange("SuperMarket")
                                                        player.rect.center = oldPos

                                                        Speech("I take back what I said... YOU are mean", girl, func=(lambda:Explode(girl), "End"))

                                                        StopPersisSong()
                                                        PlaySong("BackgroundMusic")

                                                        Quests["MBoss"] = True

                                                    Check(check, func)

                                                    def BulletChange():
                                                        player.bullet = ConfusedBullet
                                                    def Return():
                                                        player.bullet = Bullet

                                                    DoCheck(lambda:not check(), BulletChange).endFunc = Return

                                                    PersisSong("BossMusic", 1)

                                                    return lambda:None

                                                x = player.rect.centerx+deats[i][0][0]
                                                y = player.rect.centery+deats[i][0][1]

                                                s = deats[i][1]

                                                e = Egirl()
                                                SetPosition(e, "centerx", "centery", x, y)

                                                egirls.append(e)
                                                Speech(s, e, func=(lambda:Friends(i+1), "End"))

                                            Speech("Yes... This is much better", egirl, func=(lambda:PersonMove(egirl, ("centerx", "centery"), (player.rect.centerx+dist, player.rect.centery), 2), "Start"))
                                            Speech("It's looking quite empty here though...", egirl)
                                            Speech("I know! How about I call some of my friends?", egirl, func=(Friends, "End"))

                                        global oldPos
                                        oldPos = player.rect.center

                                        Speech("...I think this calls for a change of scene", girl, func=(Battle, "End"))
                                        return 0

                                    def StartGame():
                                        Explode(girl)

                                        bars = [
                                        (132, 16, 1, 20),
                                        (98, 63, 1, 24),
                                        (56, 16, 1, 20),
                                        (0, 62, 8, 1)
                                        ]

                                        for b in bars:
                                            b = Barrier(b[0], b[1], b[2], b[3], player)

                                        def SchoolTran():
                                            RoomChange("School")
                                            SetPositionBck(player, "centerx", "bottom", 83, 126)
                                        def ParentsTran():
                                            RoomChange("ParentsRoom")
                                            SetPositionBck(player, "centerx", "bottom", 48, 32)

                                        global STran, PTran
                                        STran = Tran(pygame.Rect(99, 49, 19, 1), SchoolTran)
                                        PTran = Tran(pygame.Rect(23, 49, 19, 1), ParentsTran)

                                        player.AddObject(STran)
                                        player.AddObject(PTran)

                                    Speech("Let's play hide and seek!", girl)
                                    Speech("Try and find me!", girl, func=(StartGame, "End"))

                                girl.AssignInteraction("T", "Talk", Game, True)

                            player.AddObject(Timer(5, Reappear))
                            return 0

                        if i == 0:
                            RoomAdd(girl)
                            DoCheck(lambda:girl in Objects, CamSkip)

                        RandomSpawn(girl)
                        Speech(hauntSpeech[i], girl, func=(lambda:Haunt(i+1), "End"))

                    Speech("Huh... The walls have vanished", player)
                    Speech("And the button by the looks of things... How peculiar", player, func=(Haunt, "End"))

            if "WomanTrapped" in Quests and player.name == "Woman":
                if not Quests["WomanTrapped"]:
                    Quests.pop("WomanTrapped")
                    Speech("It looks like the barrier's been taken away", player)

        def NoWhere():
            global bck, bckCol

            bck = None
            bckCol = (245, 155, 70)

        def SchoolRoom():
            Playground()

            if RoomEmpty():
                def SuperRoomTran():
                    RoomChange("SuperMarket")
                    SetPositionBck(player, "centerx", "top", 108, 50)
                Tran(pygame.Rect(50,127,67,1), SuperRoomTran)

                def SRoomTran():
                    RoomChange("SuperMarket")
                    SetPositionBck(player, "centerx", "bottom", 108, 48)
                Tran(pygame.Rect(73, 36, 32, 1), SRoomTran)

        def PRoom():
            ParentsRoom()

            if RoomEmpty():
                def SuperRoomTran():
                    RoomChange("SuperMarket")
                    SetPositionBck(player, "centerx", "top", 32, 50)
                Tran(pygame.Rect(41,34,15,1), SuperRoomTran)

                def SRoomTran():
                    RoomChange("StorageRoom")
                    SetPosition(player, "centerx", "bottom", roomWidth/2, roomHeight-bck.scale)

                    global oldPos
                    oldPos = player.rect.center

                Tran(pygame.Rect(41, 0, 15, 1), SRoomTran)

        def StorRoom():
            StorageRoom()

            def OtherChild():
                if child.name == "Boy":
                    return girl
                elif child.name == "Girl":
                    return boy

            def Evilise():
                global eChild, eOChild

                eChild = EPerson(child.name)
                eOChild = EPerson(otherChild.name)

                ChangeAlpha(eChild, child.alpha)
                ChangeAlpha(eOChild, child.alpha)

                eChild.mhp = eChild.hp = 5
                eOChild.mhp = eOChild.hp = 5

                eChild.rect.center = child.rect.center
                eOChild.rect.center = otherChild.rect.center

                RoomoveObject(child)
                RoomoveObject(otherChild)

                eOChild.Find() #Change to find state

                PersisSong("BossMusic", 1)

            if RoomEmpty():
                global child
                if player.name == "Man":
                    child = girl
                elif player.name == "Woman":
                    child = boy

                global otherChild
                otherChild = OtherChild()

                RoomAdd(child)
                SetPositionBck(child, "centerx", "bottom", 48, 26)

                if child.name == "Boy":
                    Speech("Oh... I guess I had the last item all along...", child)
                    Speech("I'm sorry I didn't tell you sooner", child)

                    Speech("It's just that I wanted to give it to my sister as a birthday present", child)

                    def func():
                        RoomAdd(otherChild)
                        SetPosition(otherChild, "right", "bottom", player.rect.left-24, player.rect.bottom)

                        Speech("A present! For Me!", otherChild)
                        Speech("Urr yes?", child)
                        Speech("That's so out the blue! Is it my birthday?", otherChild)
                        Speech("Shhhh!", child)
                        Speech("What?", otherChild)
                        Speech("I was tricking her!", child)
                        Speech("Ohhh. Why yes it IS my birthday", otherChild)
                        Speech("It's too late, let's get her", child)

                        def Battle():
                            Evilise()

                            def check():
                                r = eChild not in Objects and eOChild not in Objects
                                return r

                            def func():
                                StopPersisSong()
                                PlaySong("BackgroundMusic")

                                for g in GetItems:
                                    if not CheckInventory(g):
                                        lastItem = g
                                        break

                                RoomAdd(lastItem)
                                SetPositionBck(lastItem, "centerx", "bottom", 48, 26)

                                def func():
                                    Rooms[CurrentRoom] = [StorRoom, [], True]
                                        
                                    player.SetClothes("Wedding")
                                    RoomChange("WeddingRoom")
                                    SetPositionBck(player, "centerx", "bottom", 32, 85)
                                player.AddObject(Check(lambda:CheckInventory(lastItem), func))
                            Check(check, func)

                        Check(WhenNormal, Battle)

                    Check(WhenNormal, func)

                elif child.name == "Girl":
                    def Find0():
                        Speech("I found you!", player)

                        def Reset():
                            player.rect.center = oldPos
                        Check(WhenNormal, Reset)

                        def Find1():
                            Speech("I found-", player)
                            Speech("Shhhh I'm hiding", child)
                            Speech("I- I know and now I've found you", player)

                            def func0():
                                RoomAdd(otherChild)
                                SetPositionBck(otherChild, "centerx", "bottom", 48, 46)

                                Speech("I can hear you!", otherChild)
                                Speech("Now look what you've done! You've blown my cover!", child)

                                Speech("What's wrong?", otherChild)
                                Speech("This person cheated!", child)
                                Speech("Oh no! That's not good at all...", otherChild)

                                if player.name == "Man":
                                    pro = "him"
                                elif player.name == "Woman":
                                    pro = "her"

                                Speech("Let's get {}!".format(pro), child)

                                def checkFinish():
                                    r = eChild not in Objects and eOChild not in Objects
                                    return r

                                def Finish():
                                    StopPersisSong()
                                    PlaySong("BackgroundMusic")

                                    Quests["MBoss"] = True
                                    def func():
                                        Rooms[CurrentRoom] = [StorRoom, [], True]

                                        player.SetClothes("Wedding")
                                        RoomChange("WeddingRoom")
                                        SetPositionBck(player, "centerx", "bottom", 32, 85)
                                    Timer(5, func)

                                Check(WhenNormal, Evilise)
                                Check(WhenNormal, lambda:Check(checkFinish, Finish))
                            Check(WhenNormal, func0)

                        child.AssignInteraction("F", "Find", Find1, True)
                    child.AssignInteraction("F", "Find", Find0, False)

        global Rooms
        Rooms = {
        "WeddingRoom":[WRoom, [], True],

        "SuperMarket":[SRoom, [], True],
        "NoWhere":[NoWhere, [], True],

        "School":[SchoolRoom, [], True],
        "ParentsRoom":[PRoom, [], True],
        "StorageRoom":[StorRoom, [], True]
        }
        RoomChange("WeddingRoom")

        SetPlayer(woman)

    def Level3b():
        NewLevelb()

        def Spouse():
            if player.name == "Man":
                return WomanChar()
            elif player.name == "Woman":
                return ManChar()

        def NewSpouse():
            if player.name == "Man":
                return jani
            elif player.name == "Woman":
                return sarah

        global grace
        grace = GraceChar()

        global jani, sarah
        jani = JanitorChar()
        sarah = SarahChar()

        global spouse, newSpouse
        spouse = Spouse()
        newSpouse = NewSpouse()

        global Quests
        Quests = {}

        def WRoom():
            WeddingRoom()

            if RoomEmpty():
                RoomAdd(grace)

                SetPositionBck(grace, "left", "top", 2, 18)
                SetPosition(player, "left", "bottom", grace.rect.right+bck.scale*2, grace.rect.bottom)

                Speech("Well... It seems as though we're a bit early", grace)
                Speech("Feel free to look around", grace)

                def SRoomTran():
                    if "Boss" in Quests:
                        if Quests["Boss"]:
                            return 0

                    RoomChange("SuperMarket")
                    SetPositionBck(player, "centerx", "top", 32, 17)

                    player.SetClothes("")
                Tran(pygame.Rect(24, 86, 17, 1), SRoomTran)

            if "AskGrace" in Quests:
                if not Quests["AskGrace"]:
                    Quests["AskGrace"] = True

                    if player.name == "Man":
                        playerName = "Gerald"
                        spouseName = "Elizabeth"
                    elif player.name == "Woman":
                        playerName = "Elizabeth"
                        spouseName = "Gerald"

                    def func():
                        Speech("I was just in the supermarket...", player)
                        Speech("And?", grace)
                        Speech("{} has already forgotten about me...".format(spouseName), player)
                        Speech("{}, how many times must I tell you".format(playerName), grace)
                        Speech("This is exactly what the darkness is trying to do to you", grace)
                        Speech("They're trying to make you weak and then at that stage, they can steal you memories", grace)
                        Speech("What's so special about MY memories?", player)
                        Speech("Nothing... You're just one of the many people that they've targeted", grace)
                        Speech("Now, now, there's no time to chat", grace)
                        Speech("Why?", player)
                        Speech("The wedding has started...", grace, func=(Wedding, "End"))

                    grace.AssignInteraction("T", "Talk", func, True)

                    def Wedding():
                        RoomAdd(spouse)
                        spouse.name = "Wedding"+spouse.name

                        RoomAdd(newSpouse)

                        if player.name == "Man":
                            male = newSpouse
                            female = spouse

                            maleName, femaleName = "Bob", "Elizabeth"

                        elif player.name == "Woman":
                            male = spouse
                            female = newSpouse

                            maleName, femaleName = "Gerald", "Sarah"

                        SetPosition(male, "left", "bottom", roomWidth*.5+8, roomHeight*.4)
                        SetPosition(female, "right", "bottom", roomWidth*.5-8, roomHeight)

                        ChangeSprite(male, male.name+"IdleDown")
                        ChangeSprite(female, female.name+"IdleUp")

                        def func():
                            SetPosition(grace, "centerx", "bottom", roomWidth*.5, male.rect.top)
                            ChangeSprite(male, male.name+"IdleUp")

                            Speech("If this couple shouldn't marry, please say now", grace)

                            Speech("I object!", player)
                            Speech("...", grace)
                            Speech("No one? Well then, it looks like we can continue", grace)
                            Speech("It is now time to say the I dos", grace)
                            Speech("{}, do you take {} to be your wife".format(maleName, femaleName), grace)
                            Speech("I do", male)
                            Speech("{}, do you take {} to be your husband".format(femaleName, maleName), grace)
                            Speech("I do", female)

                            Speech("I now pronounce you man and wife", grace)

                            def Woo():
                                Explode(grace)
                                Explode(spouse)

                                def func():
                                    Speech("Ahh boo-hoo, everyone has forgotten about you", newSpouse)
                                    Speech("Don't worry, I'll take care of {}".format(spouseName), newSpouse)

                                    Speech("Now... To take care of you...", newSpouse)

                                    def Battle():
                                        PersisSong("BossMusic", 1)
                                        Quests["Boss"] = True

                                        global espouse
                                        espouse = EPerson(newSpouse.name)
                                        espouse.mhp = espouse.hp = 5

                                        espouse.rect.center = newSpouse.rect.center
                                        RoomoveObject(newSpouse)

                                        global oldHp
                                        oldHp = espouse.hp

                                        class BossBomb(Bomb):
                                            def BonusExplode(self):
                                                RandomGhost().rect.center = self.rect.center

                                                for o in Objects:
                                                    if type(o) != Wall:
                                                        continue

                                                    if not hasattr(o, "Sprite"):
                                                        continue
                                                    if "WeddingSeat" not in o.Sprite.name:
                                                        continue

                                                    if dist(self, o) < minDist(self, o)*1.5:
                                                        Explode(o)

                                        SetPositionBck(BossBomb(), "left", "top", 2, 18)
                                        SetPositionBck(BossBomb(), "right", "top", 62, 18)
                                        SetPositionBck(BossBomb(), "left", "bottom", 2, 84)
                                        SetPositionBck(BossBomb(), "right", "bottom", 62, 84)

                                        def PlaceBomb():
                                            if espouse not in Objects:
                                                return 0

                                            BossBomb().rect.center = espouse.rect.center
                                            RandomSpawn(espouse)

                                        def Hit():
                                            global oldHp
                                            oldHp = espouse.hp

                                            PlaceBomb()
                                        dc = DoCheck(lambda:espouse.hp < oldHp, Hit)
                                        dc.persis = True

                                        Check(lambda:espouse not in Objects, lambda:RoomoveObject(dc))

                                        def WhenEnd():
                                            if espouse in Objects:
                                                return False

                                            for o in Objects:
                                                if hasis(o, "Enemy"):
                                                    return False
                                                if issubclass(type(o), Bomb):
                                                    return False

                                            return True
                                        def WhatEnd():
                                            RoomAdd(grace)
                                            SetPositionBck(grace, "centerx", "bottom", 32, 85)

                                            if player.name == "Man":
                                                spouseType = "wife"
                                                spousePro = "her"
                                            elif player.name == "Woman":
                                                spouseType = "husband"
                                                spousePro = "him"

                                            StopPersisSong()
                                            PlaySong("BackgroundMusic")

                                            Speech("What's been going on here?", grace)
                                            Speech("I don't know but I need to see my {}".format(spouseType), player)
                                            Speech("Don't worry... You'll see {} soon, I promise".format(spousePro), grace)

                                            Check(WhenNormal, LevelComplete)

                                        Check(WhenEnd, lambda:Timer(5, WhatEnd))

                                    Check(WhenNormal, Battle)

                                Timer(2, func)

                            Check(WhenNormal, Woo)

                        PersonMove(female, ("right", "bottom"), ((roomWidth*.5-8)/bck.scale, (roomHeight*.4)/bck.scale), 2, eFunc=func)

        def SRoom():
            SuperMarket()

            if RoomEmpty():
                RoomAdd(spouse)
                RoomAdd(sarah)

                SetPositionBck(spouse, "right", "centery", 116, 49)
                SetPositionBck(sarah, "centerx", "bottom", 180, 47)

                global bottle
                bottle = Interact()
                FirstSprite(bottle, "WaterBottle")
                SetPositionBck(bottle, "right", "bottom", 116, 62)

                def NearFunc():
                    Quests["NoLeave"] = True

                    puddle = Puddle()
                    SetPositionBck(puddle, "centerx", "centery", 108, 49)

                    Speech("Clean up in aisle 1", sarah)

                    def func():
                        RoomAdd(jani)
                        SetPositionBck(jani, "centerx", "top", 32, 17)

                        def Walk():
                            PersonMoves([
                                [jani, ("centerx", "top"), (puddle.rect.centerx/bck.scale, jani.rect.top/bck.scale), 5],
                                [jani, ("centerx", "centery"), (puddle.rect.centerx/bck.scale, puddle.rect.centery/bck.scale), 3]
                                ])

                        Speech("Can I just go one day without a spillage?", jani, func=(Walk, "Start"))

                        if spouse.name == "Man":
                            spouseName = "Gerald"
                        elif spouse.name == "Woman":
                            spouseName = "Elizabeth"

                        Speech("This can't be...", player)
                        Speech("This was the first day I met  {}".format(spouseName), player)

                        def Mop():
                            def GoBack():
                                PersonMoves([
                                    [jani, ("centerx", "top"), (jani.rect.centerx/bck.scale, 18), 3],
                                    [jani, ("centerx", "top"), (32, 18), 5, lambda:Explode(jani)]
                                    ])

                            if puddle in Objects:
                                puddle.Mop()
                                Timer(2, Mop)
                            else:
                                Speech("All done! Now I'm going back for a rest...", jani)
                                Speech("I'm ever so sorry for all this", spouse)

                                if spouse.name == "Man":
                                    Speech("Whatever", jani, func=(GoBack, "End"))

                                    def func():
                                        def Walk():
                                            PersonMoves([
                                                [sarah, ("left", "bottom"), (135, 47), 3],
                                                [sarah, ("left", "bottom"), (135, 33), 3],
                                                [sarah, ("centerx", "bottom"), (108, 33), 3],
                                                [sarah, ("centerx", "bottom"), (108, spouse.rect.bottom/bck.scale), 3]
                                                ])

                                        Speech("Are you alright?", sarah, func=(Walk, "Start"))
                                        Speech("Yes of course, I'm just so clumsy", spouse)
                                        Speech("You're a funny one...", sarah)
                                        Speech("My shift finishes at 5 so maybe we can talk more then?", sarah)
                                        Speech("Yeah sure", spouse)
                                        Speech("It was nice meeting you...", sarah)
                                        Speech("Oh no you don't", player)

                                        def func():
                                            PersonMoves([
                                                [sarah, ("centerx", "bottom"), (108, 33), 3],
                                                [sarah, ("left", "bottom"), (135, 33), 3],
                                                [sarah, ("left", "bottom"), (135, 47), 3],
                                                [sarah, ("centerx", "bottom"), (180, 47), 3]
                                                ])
                                        Check(WhenNormal, func)
                                    Check(WhenNormal, func)

                                elif spouse.name == "Woman":
                                    Speech("That's fine... I'd do anything for you", jani)
                                    Speech("Well thank you, that is very kind", spouse)
                                    Speech("Maybe we could talk more sometime?", jani)
                                    Speech("Elizabeth?", player)
                                    Speech("Yes! I'd love that", spouse)
                                    Speech("I'll see you later then", jani, func=(GoBack, "End"))

                                Quests["AskGrace"] = False

                                if player.name == "Man":
                                    playerName = "Gerald"
                                    spouseName = "Elizabeth"
                                elif player.name == "Woman":
                                    playerName = "Elizabeth"
                                    spouseName = "Gerald"

                                def Continue():
                                    Speech("What's going on? Am I being replaced?", player)
                                    Speech("I was the one that helped {} after they spilt their water".format(spouseName), player)
                                    Speech("Maybe Grace knows what's going on?", player)
                                Check(WhenNormal, Continue)

                        Check(WhenNormal, lambda:Timer(1.5, Mop))

                    Check(WhenNormal, func)

                Check(lambda:dist(player, spouse)<minDist(player, spouse)*2, NearFunc)

                def WRoomTran():
                    if "NoLeave" in Quests:
                        if Quests["NoLeave"]:
                            if "NoLeavePrompt" not in Quests:
                                Quests["NoLeavePrompt"] = True
                                if player.name == "Man":
                                    sirmiss = "sir"
                                elif player.name == "Woman":
                                    sirmiss = "miss"

                                Speech("I'm sorry {}, but you're not allowed there, that's for staff only".format(sirmiss), sarah)
                                Speech("But my wedding's in there!", player)
                                Speech("I'm sorry but that's the supermarket staffroom, no wedding", sarah)
                                Speech("Maybe you're just a little ill? Medicine is in aisle 2", sarah)

                                def func():
                                    Speech("Who does she think she is?", player)
                                    Speech("My wedding is through those doors and I'll do whatever it takes to get through them", player)
                                    Speech("The question is... Where does one find a distraction?", player)

                                    def func():
                                        puddle = Puddle()
                                        Replace(bottle, puddle)

                                        puddle.rect.centerx = 108*bck.scale

                                        Speech("Clean up in aisle 1... Again...", sarah)
                                        Speech("...", sarah)
                                        Speech("Bob?", sarah)
                                        Speech("Hello? We have an aisle that needs cleaning!", sarah)
                                        Speech("Where's he gone to?", sarah)

                                        Check(WhenNormal, lambda:PersonMoves([
                                            [sarah, ("left", "top"), (135, sarah.rect.top/bck.scale), 4],
                                            [sarah, ("left", "top"), (135, 18), 4],
                                            [sarah, ("centerx", "top"), (32, 18), 4, lambda:Explode(sarah)]
                                            ]))

                                        def Continue():
                                            Speech("Finally, now that she's gone, I can find Grace", player)
                                            Quests["NoLeave"] = False
                                        Check(WhenNormal, Continue)
                                    bottle.AssignInteraction("S", "Spill", func, True)
                                Check(WhenNormal, lambda:Timer(3, func))

                            return 0

                    player.SetClothes("Wedding")

                    RoomChange("WeddingRoom")
                    SetPositionBck(player, "centerx", "bottom", 32, 85)

                Tran(pygame.Rect(23, 15, 19, 1), WRoomTran)

        global Rooms
        Rooms = {
        "WeddingRoom":[WRoom, [], True],
        "SuperMarket":[SRoom, [], True]
        }
        RoomChange("WeddingRoom")

    def Level4a():
        global man, woman, boy, girl
        man = Man()
        woman = Woman()
        boy = Boy()
        girl = Girl()

        global players
        players = [
        man,
        woman,
        boy,
        girl
        ]

        NewLevela()

        global grace
        grace = GraceChar()

        global Quests
        Quests = {}

        def GHouse():
            GraceHouse()

            if RoomEmpty():
                RoomAdd(grace)
                SetPositionBck(grace, "centerx", "top", 47, 61)

                for p in players:
                    RoomAdd(p)

                for p in players:
                    i = players.index(p)
                    p.rect.midbottom = (roomWidth/(len(players)+1)*(i+1), roomHeight-bck.scale*4)

                def Start():
                    SetPlayer(man)

                    Speech("We have finally reached our last destination...", grace)
                    Speech("That's strange, I don't remember this place", man, func=(lambda:SetPlayer(man), "Start"))
                    Speech("Perhaps you have just forgotten it, your memories have become fragile after all", grace)
                    Speech("I guess so...", woman, func=(lambda:SetPlayer(woman), "Start"))
                    Speech("Why so grim? We're only a few steps away from restoring your life with your family!", grace)
                    Speech("It's just that... Well... I haven't seen them in forever", boy, func=(lambda:SetPlayer(boy), "Start"))
                    Speech("I know it's hard, I understand...", grace)
                    Speech("What do you mean?", girl, func=(lambda:SetPlayer(girl), "Start"))
                    Speech("Now, now, no need to dwell in the present, let's make our future!", grace, func=(lambda:Explode(grace), "End"))

                Check(lambda:player != None, Start)

                def GRoomTran():
                    RoomChange("GraceRoom")
                    SetPositionBck(player, "centerx", "bottom", 48, 46)
                Tran(pygame.Rect(43, 59, 10, 1), GRoomTran)

        def GRoom():
            GraceRoom()

            if RoomEmpty():
                Speech("Wow... This house is very empty...", player)
                Speech("I guess the people who lived here weren't very materialistic", player)

                def func0():
                    AddInventory(Milk())
                    Speech("What's this doing down there?", player)
                    Speech("Oh well, I guess it's mine now", player)
                GraceBed.AssignInteraction("L", "Look", func0, True)

                def func1():
                    AddInventory(Powerup())
                    Speech("Why am I looking under this bed?", player)
                    Speech("Oh well, I'm sure this item I found will come in handy", player)
                ParentsBed.AssignInteraction("L", "Look", func1, True)

                def func2():
                    if "GraceDollSway" in Doll.Sprite.name:
                        return 0

                    ChangeSprite(Doll, "GraceDollSway")
                    Timer(5, lambda:ChangeSprite(Doll, "GraceDoll"))
                Doll.AssignInteraction("L", "Look", func2, False)

                def GHouseTran():
                    RoomChange("GraceHouse")
                    SetPositionBck(player, "centerx", "top", 48, 61)
                Tran(pygame.Rect(41, 47, 15, 1), GHouseTran)

                def GGardenTran():
                    RoomChange("GraceGarden")
                    SetPositionBck(player, "centerx", "bottom", 48, 93)
                Tran(pygame.Rect(41, 0, 15, 1), GGardenTran)

        def GGarden():
            GraceGarden()

            if RoomEmpty():
                RoomAdd(grace)

                def func():
                    Speech("Here we are...", grace)
                    Speech("You're former life is very close, I can feel it", grace)

                    Speech("But first I need one item...", grace)
                    Speech("What is it?", player)
                    Speech("My doll", grace)

                    Speech("Wow really? I'm so close to seeing my family and you want a doll?", player)
                    Speech("Do you want to see your family or not?", grace)
                    Speech("Fine.", player)

                    Quests["SearchDoll"] = True

                grace.AssignInteraction("T", "Talk", func, True)

                def GRoomTran():
                    if "SearchDoll" in Quests:
                        if Quests["SearchDoll"]:
                            RoomChange("ParentsRoom")
                            SetPositionBck(player, "centerx", "top", 48, 1)
                            return 0

                    RoomChange("GraceRoom")
                    SetPositionBck(player, "centerx", "top", 48, 1)
                Tran(pygame.Rect(40, 95, 20, 1), GRoomTran)

            if "SearchDoll" in Quests:
                if not Quests["SearchDoll"]:
                    Quests.pop("SearchDoll")
                    RemoveInventory(pickUpDoll)

                    Speech("Thank you...", grace)
                    Speech("This doll is the last thing I needed in order to restore myself", grace)
                    Speech("Restore me you mean?", player)
                    Speech("No, I meant me", grace)
                    Speech("But I do need your memories...", grace)

                    def Battle():
                        PersisSong("BossMusic")

                        egrace = EPerson("Grace")
                        Replace(grace, egrace)

                        global gd
                        gd = GraceDoll()
                        gd.rect.bottomleft = (egrace.rect.right+8, egrace.rect.bottom)

                        def func():
                            if gd in Objects:
                                Explode(gd)

                            egrace.hp = 1
                            Speech("Please... Spare me...", egrace)

                            for p in players:
                                ChangeCheckPerm(p, "Shooting", False)

                            def func():
                                RoomoveObject(annoyingCheck)
                                RoomAdd(grace)
                                Replace(egrace, grace)

                                global oldRoom, oldPlayer
                                oldRoom = CurrentRoom
                                oldPlayer = player

                                global playerGrace
                                playerGrace = Grace()
                                players.append(playerGrace)

                                SetPlayer(playerGrace)
                                RoomChange("StoryGraceRoom")
                                SetPositionBck(player, "centerx", "bottom", 48, 47)
                                StopPersisSong()
                                PlaySong("BackgroundMusic")
                            global annoyingCheck
                            annoyingCheck = Check(WhenNormal, func)
                        Check(lambda:egrace.hp <= 2, func)

                    Check(WhenNormal, Battle)

        def PRoom():
            ParentsRoom()

            if RoomEmpty():
                global pickUpDoll
                pickUpDoll = InventoryInteract()
                FirstSprite(pickUpDoll, "GraceDoll")
                SetPositionBck(pickUpDoll, "centerx", "bottom", 86, 30)

                def pickup():
                    Speech("Okay... I've got the doll", player)
                    Quests["SearchDoll"] = False
                Check(lambda:CheckInventory(pickUpDoll), pickup)

                def GGardenTran():
                    RoomChange("GraceGarden")
                    SetPositionBck(player, "centerx", "bottom", 48, 93)
                Tran(pygame.Rect(41, 0, 15, 1), GGardenTran)

        def SGRoom():
            GraceRoom()

            if RoomEmpty():
                Speech("I'm home!", player)
                Speech("...", player)
                Speech("Mum! Dad! Where are you?", player)

                Speech("Hmm, maybe they're hiding under the bed?", player)
                def func0():
                    Speech("Nope not here...", player)
                    Speech("Maybe they're under my bed?", player)

                    def func0():
                        Speech("Not here either...", player)
                        Speech("Maybe dolly has seen them", player)

                        def func0():
                            Speech("Hello dolly. Have you seen my parents", player)

                            def func0():
                                ChangeSprite(Doll, "GraceDollSway")

                                def stop():
                                    ChangeSprite(Doll, "GraceDoll")
                                    Speech("You haven't? Don't worry, I'll try looking in the garden", player)

                                    Quests["Garden"] = True
                                Timer(2, stop)

                            Check(WhenNormal, func0)

                        Doll.AssignInteraction("T", "Talk", func0, True)

                    GraceBed.AssignInteraction("L", "Look", func0, True)

                ParentsBed.AssignInteraction("L", "Look", func0, True)

                def SGGardenTran():
                    if "Garden" not in Quests:
                        return 0

                    RoomChange("StoryGraceGarden")
                    SetPositionBck(player, "centerx", "bottom", 48, 93)
                Tran(pygame.Rect(41, 0, 15, 1), SGGardenTran)

        def SGGarden():
            YoungGraceGarden()

            if RoomEmpty():
                BagSeed = Interact()
                FirstSprite(BagSeed, "BagSeed")
                SetPositionBck(BagSeed, "left", "top", 39, 56)

                def Plant():
                    Speech("There we go! That's a seed planted", player)
                    Speech("Mum and Dad are going to be so impressed by this!", player)
                    Speech("I guess I'll just wait for them to come home...", player)

                    def func():
                        SetPlayer(oldPlayer)
                        RoomChange(oldRoom)

                        Speech("But they never came...", grace)
                        Speech("I've been trapped on my own for so long", grace)
                        Speech("I just want to see my parents... Is that so much to ask?", grace)
                        Speech("But I need to see my family too!", player)

                        Check(WhenNormal, lambda:Speech("It's time... For me to make my choice", player))

                        def Kill():
                            Speech("I'm sorry Grace but I need to see my family", player, func=(lambda:Explode(grace), "End"))

                            def func():
                                RoomChange("NoWhere")
                                SetPosition(player, "centerx", "centery", screenWidth/2, screenHeight/2)
                            Check(WhenNormal, func)

                        def Spare():
                            Speech("You're right... You deserve to see them", player)
                            Speech("Wow... I never thought you'd say that...", grace)
                            Speech("You know what? Not many people would have done what you did", grace)
                            Speech("That was very honourable of you", grace)
                            Speech("I promised you that you'd see your family, so that is what I'm going to do", grace)
                            Speech("Don't worry about me... I'll find my parents someday", grace)

                            def func():
                                RoomChange("LivingRoom")
                                SetPositionBck(player, "centerx", "top", 84, 13)
                            Check(WhenNormal, func)

                        grace.AssignInteraction("K", "Kill", Kill, True)
                        grace.AssignInteraction("S", "Spare", Spare, True)

                    Check(WhenNormal, func)
                BagSeed.AssignInteraction("P", "Plant Seed", Plant, True)

        def NoWhere():
            global bck, bckCol
            bck = None
            bckCol = black

            if RoomEmpty():
                Speech("Woah... What's happened?", player)
                Speech("Grace was the only person holding you and your memories together...", (screenWidth/2, screenHeight*.25))
                Speech("Your selfishness has costed you...", (screenWidth/2, screenHeight*.25))
                Speech("I hope you enjoy what you have brought upon yourself...", (screenWidth/2, screenHeight*.25))

                Check(WhenNormal, lambda:Timer(5, LevelComplete))

        def LRoom():
            LivingRoom()

            if RoomEmpty():
                if playerGrace in players:
                    players.remove(playerGrace)

                fam = []
                for p in players:
                    if p == player:
                        continue
                    fam.append(eval(p.name+"Char")())

                SetPositionBck(fam[0], "centerx", "bottom", 48, 33)
                SetPosition(fam[1], "right", "bottom", fam[0].rect.left-4, fam[0].rect.bottom)
                SetPosition(fam[2], "left", "bottom", fam[0].rect.right+4, fam[0].rect.bottom)

                Speech("Where have you been?!", fam[0])
                Speech("Don't ever do that again!", fam[1])
                Speech("I thought that we'd lost you forever", fam[1])
                Speech("We all missed you, and I'm just glad your back safe and sound", fam[2])

                Check(WhenNormal, LevelComplete)

        global Rooms
        Rooms = {
        "GraceHouse":[GHouse, [], True],
        "GraceRoom":[GRoom, [], True],
        "GraceGarden":[GGarden, [], True],

        "ParentsRoom":[PRoom, [], True],

        "StoryGraceRoom":[SGRoom, [], True],
        "StoryGraceGarden":[SGGarden, [], True],

        "NoWhere":[NoWhere, [], True],
        "LivingRoom":[LRoom, [], True]
        }
        RoomChange("GraceHouse")

    exec("Level"+str(level)+part+"()")

    gameloop = True
    while gameloop:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    Pause()

                if player != None:
                    if e.key == playerSwitchKey and player.checks["Input"]:
                        NextPlayer()
                    
            if e.type == pygame.QUIT:
                gameloop = False
                
        CamUpdate()
        screen.fill(bckCol)
        if bck != None:
            bck.Animate()
            screen.blit(bck.sprite, (-cam[0], -cam[1]), bck.showRect)

        DepthSort()
        for o in Objects:
            if o in Removes:
                continue
            if o not in Rooms[CurrentRoom][1]:
                continue

            if hasattr(o, "Update"):
                o.Update()
            
        for r in Removes:
            if r not in Objects:
                continue
            Objects.remove(r)
        Removes = []

        if overlay:
            screen.blit(overlaySurface, (0, 0))
        if flashlight:    
            screen.blit(flashlightSurface, (0, 0))

        # text(str(clock.get_fps()), white, "left", "top", 4, 4)

        clock.tick(FPS)
        pygame.display.update((0, 0, screenWidth, screenHeight))

    End()

def LevelComplete():
    if not WhenNormal():
        Check(WhenNormal, LevelComplete)
    global bckCol, events, Objects, currentHover, totalRect
    Objects = []
    currentHover = None

    ContinueButton = Button("Continue")
    ReplayButton = Button("Replay")
    LevelSelectButton = Button("Level Select")
    MainMenuButton = Button("Main Menu")

    ContinueButton.func = lambda:Game(int(level)+1)
    lv = int(level)+1
    if not CheckLevelExists(lv):
        ContinueButton.Freeze()
    ReplayButton.func = lambda:Game(level)
    LevelSelectButton.func = LevelSelect
    MainMenuButton.func = Start

    totalRect = pygame.Rect(0,0,0,0)
    longestWidth = None

    for o in Objects:
        if type(o) != Button:
            continue

        if longestWidth == None:
            longestWidth = o
        elif longestWidth.rect.w < o.rect.w:
            longestWidth = o

        totalRect.w = longestWidth.rect.w
        totalRect.h += o.rect.h+4
        
    totalRect.h -= 4
    totalRect.center = (screenWidth/2, screenHeight/2)

    totalHeight = 0
    for o in Objects:
        if type(o) != Button:
            continue

        newRect = pygame.Rect(o.rect)
        newRect.w = longestWidth.rect.w
        
        o.ChangeRect(newRect)
        o.rect.left = totalRect.left
        
        o.rect.y = totalRect.y
        o.rect.y += totalHeight

        totalHeight += o.rect.h+4

    blalph = pygame.Surface((screenWidth, screenHeight), pygame.SRCALPHA)
    col = (black[0], black[1], black[2], 128)
    blalph.fill(col)

    UnlockLevel(int(level)+1)
        
    oldSurf = screen.copy()
    bckCol = white

    while True:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                End()

        screen.blit(oldSurf, (0, 0))
        screen.blit(blalph, (0, 0))

        for o in Objects:
            if hasattr(o, "Update"):
                o.Update()

        clock.tick(FPS)
        pygame.display.update()

def GameOver():
    global Objects, Removes, events, currentHover
    oldScreen = copy.copy(screen)

    Objects = []
    Removes = []
    currentHover = None

    YouDiedButton = Button("You Died")
    ReplayButton = Button("Replay")
    MainMenuButton = Button("Main Menu")

    longestWidth = None
    for o in Objects:
        if type(o) != Button:
            continue

        if longestWidth == None:
            longestWidth = o
        elif o.rect.w > longestWidth.rect.w:
            longestWidth = o

    for o in Objects:
        if type(o) != Button:
            continue

        rect = o.rect
        rect.w = longestWidth.rect.w
        ChangeRect(o, rect)

    ReplayButton.rect.center = (screenWidth/2, screenHeight/2)
    YouDiedButton.rect.midbottom = (ReplayButton.rect.centerx, ReplayButton.rect.top-4)
    MainMenuButton.rect.midtop = (screenWidth/2, ReplayButton.rect.bottom+4)

    def Unpause():
        global Pausing
        Pausing = False

    YouDiedButton.func = lambda:None
    ReplayButton.func = lambda:Game(level)
    MainMenuButton.func = Start

    global Pausing
    Pausing = True

    darkSurf = pygame.Surface((screenWidth, screenHeight), pygame.SRCALPHA)
    darkSurf.fill((black[0], black[1], black[2], 96))

    while Pausing:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                End()

        screen.blit(oldScreen, (0, 0))
        screen.blit(darkSurf, (0, 0))

        for o in Objects:
            if hasattr(o, "Update"):
                o.Update()

        for r in Removes:
            Objects.remove(r)
        Removes = []

        clock.tick(FPS)
        pygame.display.update((0, 0, screenWidth, screenHeight))

def End():
    pygame.quit()
    quit()

Start()

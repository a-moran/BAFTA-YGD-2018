import pygame
import os
import copy

Sprites = {}

class Sprite:
    def UpdateShowRect(self):
        self.showRect = pygame.Rect((self.rect.w*self.frameCount, 0), self.rect.size)

    def __init__(self,
                 name,
                 frames=1,
                 frameRate=1,
                 scale=1,
                 crect=None):

        self.name = name
        self.filename = name+".png"
        
        Sprites[self.name] = self
        self.sprite = pygame.image.load("Sprites/"+self.filename)
        self.blend = None

        self.rect = pygame.Rect((0, 0), self.sprite.get_size())
        self.scale = scale
        self.sprite = pygame.transform.scale(self.sprite, (int(self.rect.w*self.scale),
                                                           int(self.rect.h*self.scale)))

        self.frames = frames
        self.frameRate = frameRate

        self.rect.w /= self.frames
        self.rect.w *= self.scale
        self.rect.h *= self.scale

        if crect == None:
            self.crect = pygame.Rect(self.rect)
        else:
            self.crect = pygame.Rect(crect)
            
            self.crect.topleft = (self.crect.x*self.scale,
                                  self.crect.y*self.scale)
            self.crect.size = (self.crect.w*self.scale,
                               self.crect.h*self.scale)

        #Animation Stuff
        self.frameCount = 0
        self.frameRateCount = 0

        self.UpdateShowRect()

        if self.name[:len("Sombre")] != "Sombre":
            self.sombreName = "Sombre"+self.name
            self.sombreFilename = "Sombre"+self.filename
            if self.sombreFilename not in os.listdir("Sprites"):
                Sprite.Sombre(self)
                
            Sprite(self.sombreName,
                   frames,
                   frameRate,
                   scale,
                   crect)

    def New(sprName):
        sprite = Sprites[sprName]
        
        newSprite = copy.copy(sprite)
        newSprite.sprite = newSprite.sprite.copy()
        
        return newSprite

    def Animate(self):
        if self.frameRateCount < self.frameRate:
            self.frameRateCount += 1
        else:
            self.frameRateCount = 0

            if self.frameCount < self.frames-1:
                self.frameCount += 1
            else:
                self.frameCount = 0

        self.UpdateShowRect()

    def Sombre(sprite):
        print("Sombre-fying", sprite.name)
        sombreVal = 1

        newSprite = pygame.image.load("Sprites\\"+sprite.filename)
        width, height = newSprite.get_size()

        for x in range(width):
            for y in range(height):
                col = newSprite.get_at((x, y))
                alpha = col[3]

                if alpha == 0:
                    continue
                
                val = 0

                for c in range(3):
                    val += col[c]
                val /= 3

                newCol = []
                for c in range(3):
                    vr = col[c]+(val-col[c])*sombreVal

                    newCol.append(vr)

                newCol = (newCol[0], newCol[1], newCol[2], alpha)
                newSprite.set_at((x, y), newCol)

        pygame.image.save(newSprite, "Sprites\\Sombre"+sprite.name+".png")

#Bck
Sprite("StartScreen")

Sprite("KidsRoom", scale=8)
Sprite("KidsRoomNoGirl", scale=8)
Sprite("KidsRoomNoBoy", scale=8)
Sprite("StorageRoom", scale=8)

Sprite("ParentsRoom", scale=8)
Sprite("ParentsRoomNoWoman", scale=8)
Sprite("ParentsRoomNoMan", scale=8)

Sprite("LivingRoom", scale=8)
Sprite("BattleLivingRoom", scale=8)

Sprite("RoadToSchool", scale=8)
Sprite("Playground", scale=8)
Sprite("Corridor1", scale=8)
Sprite("Corridor2", scale=8)

Sprite("ScienceClass", scale=8)
Sprite("MathsClass", scale=8)
Sprite("EnglishClass", scale=8)
Sprite("GeographyClass", scale=8)

Sprite("JanitorsRoom", scale=8)
Sprite("JanitorsMiniBossRoom", scale=10)

Sprite("WeddingRoom", scale=8)
Sprite("SuperMarket", scale=8)

Sprite("GraceHouse", scale=8)
Sprite("GraceRoom", scale=8)
Sprite("GraceGarden", scale=8)

#Everything else
Sprite("ButtonStart")
Sprite("ButtonLevelSelect")
Sprite("ButtonOptions")
Sprite("ButtonQuit")

Sprite("ButtonLevel1",scale=2)
Sprite("ButtonLevel2",scale=2)
Sprite("ButtonLevel3",scale=2)
Sprite("ButtonLevel4",scale=2)
Sprite("ButtonLevel5",scale=2)
Sprite("ButtonLevel6",scale=2)

Sprite("ButtonFullScreen")

Sprite("Memory1", scale=2)
Sprite("Memory2", scale=2)

Sprite("BoyIdleDown", frames=5, frameRate=6, crect=(1, 6, 5, 7), scale=4)
Sprite("BoyIdleUp", frames=5, frameRate=6, crect=(0, 6, 7, 7), scale=4)
Sprite("BoyRunLeft",frames=8,frameRate=4,crect=(2, 6, 5, 8), scale=4)
Sprite("BoyRunRight",frames=8,frameRate=4,crect=(2, 6, 5, 8), scale=4)
Sprite("BoyRunUp",frames=8,frameRate=4,crect=(1, 6, 5, 8), scale=4)
Sprite("BoyRunDown",frames=8,frameRate=4,crect=(1, 6, 5, 8), scale=4)

Sprite("SchoolBoyIdleDown", frames=5, frameRate=6, crect=(1, 6, 5, 7), scale=4)
Sprite("SchoolBoyIdleUp", frames=5, frameRate=6, crect=(0, 6, 7, 7), scale=4)
Sprite("SchoolBoyRunLeft",frames=8,frameRate=4,crect=(2, 6, 5, 8), scale=4)
Sprite("SchoolBoyRunRight",frames=8,frameRate=4,crect=(2, 6, 5, 8), scale=4)
Sprite("SchoolBoyRunUp",frames=8,frameRate=4,crect=(1, 6, 5, 8), scale=4)
Sprite("SchoolBoyRunDown",frames=8,frameRate=4,crect=(1, 6, 5, 8), scale=4)

Sprite("GirlIdleDown", frames=4, frameRate=6, crect=(1, 6, 5, 6), scale=4)
Sprite("GirlIdleUp", frames=4, frameRate=6, crect=(1, 6, 5, 6), scale=4)
Sprite("GirlRunLeft",frames=8,frameRate=4,crect=(2, 7, 5, 7), scale=4)
Sprite("GirlRunRight",frames=8,frameRate=4,crect=(2, 7, 5, 7), scale=4)
Sprite("GirlRunUp",frames=8,frameRate=4,crect=(1, 7, 5, 7), scale=4)
Sprite("GirlRunDown",frames=8,frameRate=4,crect=(1, 7, 5, 7), scale=4)

Sprite("SchoolGirlIdleDown", frames=4, frameRate=6, crect=(1, 6, 5, 6), scale=4)
Sprite("SchoolGirlIdleUp", frames=4, frameRate=6, crect=(1, 6, 5, 6), scale=4)
Sprite("SchoolGirlRunLeft",frames=8,frameRate=4,crect=(2, 7, 5, 7), scale=4)
Sprite("SchoolGirlRunRight",frames=8,frameRate=4,crect=(2, 7, 5, 7), scale=4)
Sprite("SchoolGirlRunUp",frames=8,frameRate=4,crect=(1, 7, 5, 7), scale=4)
Sprite("SchoolGirlRunDown",frames=8,frameRate=4,crect=(1, 7, 5, 7), scale=4)

Sprite("ManIdleDown", frames=5, frameRate=6, crect=(1, 6, 5, 7), scale=4)
Sprite("ManIdleUp", frames=5, frameRate=6, crect=(1, 6, 5, 7), scale=4)
Sprite("ManRunLeft",frames=8,frameRate=4,crect=(2, 6, 5, 8), scale=4)
Sprite("ManRunRight",frames=8,frameRate=4,crect=(2, 6, 5, 8), scale=4)
Sprite("ManRunUp",frames=8,frameRate=4,crect=(1, 6, 5, 8), scale=4)
Sprite("ManRunDown",frames=8,frameRate=4,crect=(1, 6, 5, 8), scale=4)

Sprite("WomanIdleDown", frames=4, frameRate=6, crect=(1, 6, 5, 6), scale=4)
Sprite("WomanIdleUp", frames=4, frameRate=6, crect=(1, 6, 5, 6), scale=4)
Sprite("WomanRunLeft",frames=8,frameRate=4,crect=(2, 7, 5, 7), scale=4)
Sprite("WomanRunRight",frames=8,frameRate=4,crect=(2, 7, 5, 7), scale=4)
Sprite("WomanRunUp",frames=8,frameRate=4,crect=(1, 7, 5, 7), scale=4)
Sprite("WomanRunDown",frames=8,frameRate=4,crect=(1, 7, 5, 7), scale=4)

Sprite("WeddingManIdleDown", frames=5, frameRate=6, crect=(1, 6, 5, 7), scale=4)
Sprite("WeddingManIdleUp", frames=5, frameRate=6, crect=(1, 6, 5, 7), scale=4)
Sprite("WeddingManRunLeft",frames=8,frameRate=4,crect=(2, 6, 5, 8), scale=4)
Sprite("WeddingManRunRight",frames=8,frameRate=4,crect=(2, 6, 5, 8), scale=4)
Sprite("WeddingManRunUp",frames=8,frameRate=4,crect=(1, 6, 5, 8), scale=4)
Sprite("WeddingManRunDown",frames=8,frameRate=4,crect=(1, 6, 5, 8), scale=4)

Sprite("WeddingWomanIdleDown", frames=4, frameRate=6, crect=(1, 6, 5, 6), scale=4)
Sprite("WeddingWomanIdleUp", frames=4, frameRate=6, crect=(1, 6, 5, 6), scale=4)
Sprite("WeddingWomanRunLeft",frames=8,frameRate=4,crect=(2, 7, 5, 7), scale=4)
Sprite("WeddingWomanRunRight",frames=8,frameRate=4,crect=(2, 7, 5, 7), scale=4)
Sprite("WeddingWomanRunUp",frames=8,frameRate=4,crect=(1, 7, 5, 7), scale=4)
Sprite("WeddingWomanRunDown",frames=8,frameRate=4,crect=(1, 7, 5, 7), scale=4)

Sprite("GraceIdleDown", frames=4, frameRate=6, crect=(1, 6, 5, 6), scale=4)
Sprite("GraceIdleUp", frames=4, frameRate=6, crect=(1, 6, 5, 6), scale=4)
Sprite("GraceRunLeft",frames=8,frameRate=4,crect=(2, 7, 5, 7), scale=4)
Sprite("GraceRunRight",frames=8,frameRate=4,crect=(2, 7, 5, 7), scale=4)
Sprite("GraceRunUp",frames=8,frameRate=4,crect=(1, 7, 5, 7), scale=4)
Sprite("GraceRunDown",frames=8,frameRate=4,crect=(1, 7, 5, 7), scale=4)

Sprite("JanitorIdleDown", frames=5, frameRate=6, crect=(1, 6, 5, 7), scale=4)
Sprite("JanitorIdleUp", frames=5, frameRate=6, crect=(1, 6, 5, 7), scale=4)
Sprite("JanitorRunLeft",frames=8,frameRate=4,crect=(2, 6, 5, 8), scale=4)
Sprite("JanitorRunRight",frames=8,frameRate=4,crect=(2, 6, 5, 8), scale=4)
Sprite("JanitorRunUp",frames=8,frameRate=4,crect=(1, 6, 5, 8), scale=4)
Sprite("JanitorRunDown",frames=8,frameRate=4,crect=(1, 6, 5, 8), scale=4)

Sprite("SarahIdleDown", frames=4, frameRate=6, crect=(1, 6, 5, 6), scale=4)
Sprite("SarahIdleUp", frames=4, frameRate=6, crect=(1, 6, 5, 6), scale=4)
Sprite("SarahRunLeft",frames=8,frameRate=4,crect=(2, 7, 5, 7), scale=4)
Sprite("SarahRunRight",frames=8,frameRate=4,crect=(2, 7, 5, 7), scale=4)
Sprite("SarahRunUp",frames=8,frameRate=4,crect=(1, 7, 5, 7), scale=4)
Sprite("SarahRunDown",frames=8,frameRate=4,crect=(1, 7, 5, 7), scale=4)

Sprite("Ghost",scale=2)
Sprite("GhostPoison",scale=2)
Sprite("GhostFire",scale=2)
Sprite("GhostFreeze",scale=2)
Sprite("GhostConfused",scale=2)

Sprite("JumpyIdle",scale=4)
Sprite("JumpyJump",frames=13,frameRate=2,scale=4)

Sprite("JumpyRandomIdle",scale=4)
Sprite("JumpyRandomJump",frames=13,frameRate=2,scale=4)

Sprite("PrivateIdle",scale=4)
Sprite("PrivateHide",frames=7,frameRate=3,scale=4)
Sprite("PrivateShow",frames=7,frameRate=3,scale=4)

Sprite("OrbLife",scale=2)
Sprite("Key", scale=3)

Sprite("Milk33", scale=4)
Sprite("Milk23", scale=4)
Sprite("Milk13", scale=4)

Sprite("Energy33", scale=4)
Sprite("Energy23", scale=4)
Sprite("Energy13", scale=4)

Sprite("Powerup", scale=4)

Sprite("BoxBig",scale=8)
Sprite("BoxMed",scale=8)
Sprite("BoxSmall",scale=8)

Sprite("Plant",scale=8)
Sprite("PlantBroke",scale=8)
Sprite("Sofa",crect=(0,5,17,8),scale=8)
Sprite("Television",scale=8)

Sprite("SchoolTable", scale=6)

Sprite("oldItem", scale=4)
Sprite("newItem", scale=4)
Sprite("borItem", scale=4)
Sprite("bluItem", scale=4)

Sprite("WeddingSeat", scale=8)
Sprite("Bomb", frames=6, scale=2)

Sprite("PuddleWater", frames=3, scale=4)
Sprite("WaterBottle", scale=2)

Sprite("GraceBed", scale=8)
Sprite("GraceParentsBed", scale=8)

Sprite("GraceDoll", crect=(0, 5, 5, 5), scale=6)
Sprite("GraceDollSway", frames=4, frameRate=8, crect=(2, 5, 5, 5), scale=6)
Sprite("DollEnemyIdle", frames=4, frameRate=4, crect=(4, 7, 7, 7), scale=4)

Sprite("Tree1", scale=4, crect=(4, 28, 3, 7))
Sprite("Tree2", scale=5, crect=(0, 33, 3, 3))
Sprite("PicnicBlanket", scale=4)
Sprite("BagSeed", scale=4)

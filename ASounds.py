import pygame
pygame.mixer.init()

Sounds = {}

def NewSound(name):
    filename = name+".wav"
    Sounds[name] = pygame.mixer.Sound("Sounds\\"+filename)

#Level 1
NewSound("WhereAmI")

#Level 2
NewSound("BadHideAndSeek")
NewSound("ThereYouAre")
NewSound("Huh")
NewSound("ImRightHere")

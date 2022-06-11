"""
Le jeu avoidThem est un jeu à obstacle.

Vous incarnerez un petit oiseau, allant rejoindre sa grand-mère, qui attend de l'autre coté de la route.

    - Le personnage doit se déplacer sur la route en utilisant les flèches du clavier, ou les touches ZQSD.
    - Le personnage doit éviter les obstacles.
    - A chaque réussite, la vitesse d'apparition des voitures, ainsi que leurs vitesses seront augmentées.

Vous devez traverser le plus de fois la route en un minimum de temps, tout en essayant de garder des vies.
"""

import pyxel
import random
import datetime
import json
import os

class Game(object):
    """
    Classe pour gérer le joueur, les véhicules et leurs attributs.
    """
    def __init__(self):
        self.x = self.y = 128
        
        pyxel.init(self.x, self.y, "Avoid Them", fps=60)
        pyxel.load("assets/avoidThem.pyxres")
        self.player = Player()
        self.lstvehicules = []
        self.speedMultiplier = 1
        self.frame = 300
        self.lastVehSpawn = [0, 0, 0, 0]
        self.lvl = 400
        self.levelLabel = 1

        #States
        self.wining = False 
        self.loosing = False

        pyxel.run(self.update, self.draw)

    def win(self):
        self.wining = True
        
    def loose(self):
        self.loosing = True

    def update(self):
        """
        Méthode permettant de gérer les évenements du jeu.
        """
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()
            
        for veh in self.lstvehicules:
            if veh.isOnScreen():
                veh.update(self.speedMultiplier)
            else:
                self.lstvehicules.remove(veh)

        self.player.update(self.lstvehicules)
        rand = random.randint(0, 3)
        if random.randint(0, self.lvl) < 10 and pyxel.frame_count - self.lastVehSpawn[rand] > 60:
            self.lastVehSpawn[rand] = pyxel.frame_count
            if rand == 0:
                newY = 10 
                arg = True
            elif rand == 1:
                newY = 29
                arg = False
            elif rand == 2:
                newY = 75
                arg = True
            else:
                newY = 94
                arg = False
            self.lstvehicules.append(Vehicle(newY, arg))
            
        if self.player.y < 9:
            self.player.resetCoords()
            self.lvl -= 15
            self.levelLabel += 1

        if self.lvl < 130:
            self.win() 

        if self.player.GetSetLives() == 0:
            self.loose()


    def draw(self):
        """
        Méthode permettant de dessiner le jeu.
        """
        pyxel.cls(0)
        if self.loosing: 
            pyxel.text(50, 64, "GAME OVER", 8)
        elif self.wining:
            pyxel.text("You Win", 50, 50, 11)
        else:
            pyxel.blt(0, 0, 1, 0, 0, 128, 64)
            pyxel.blt(0, 64, 1, 0, 0, 128, 64)
            self.player.draw()
            for veh in self.lstvehicules:
                veh.draw()
            pyxel.blt(110, 3, 0, 32, 88, 7, 8, 0)
            if self.player.GetSetLives() == 1:
                pyxel.text(120, 5, str(self.player.GetSetLives()), 8)
            else:
                pyxel.text(120, 5, str(self.player.GetSetLives()), 7 )
            pyxel.text(5, 2, f"Duree: {pyxel.frame_count // 60}", 7)
            pyxel.text(5, 120, f"Niveau: {self.levelLabel}", 7)


class Player(object):
    """
    Classe pour gérer le personnage et ses attributs
    """

    def __init__(self):
        """
        Méthode pour initialiser les attributs du joueur.
        """
        self.x = 60
        self.y = 115
        self.lives = 3
        self.wait = 180
        #Hit logic 
        self.hitByCar = False
        self.hitLeft = False
        self.hitX = 0
        self.timeSave = 0

    def playerDead(self):
        """
        Méthode pour la mort du joueur
        """
        self.resetCoords()
        self.timeSave = 0
        self.hitByCar = False
        self.GetSetLives(False) 

    def resetCoords(self):
        """
        Méthode pour réinitialiser les coordonnées du joueur.
        """
        self.wait = pyxel.frame_count + 30
        self.x = 60
        self.y = 115

    def movement(self):
        """
        Méthode pour gérer les déplacements du joueur.
        """
        if pyxel.frame_count > self.wait + 60:
            if not self.hitByCar:
                if (pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_Q)) and self.x > -2:
                    self.x -= 1
                elif (pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_D)) and self.x < 115:
                    self.x += 1
                elif (pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.KEY_Z)) and self.y > -1:
                    self.y -= 1
                elif (pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.KEY_S)) and self.y < 118:
                    self.y += 1
            else: 
                time = float(datetime.datetime.timestamp(datetime.datetime.utcnow()))
                if self.hitLeft:
                    if self.hitX - 45 < self.x:
                        self.x -= 0.75
                    else :
                        if self.timeSave == 0:
                            self.timeSave = time 
                        elif time > self.timeSave + 1.1:
                            self.playerDead()
                else :
                    if self.hitX + 45 > self.x:
                        self.x += 0.75
                    else :
                        if self.timeSave == 0:
                            self.timeSave = time 
                        elif time > self.timeSave + 1.1:
                            self.playerDead()


    def GetSetLives(self, get=True):
        """
        Méthode / getter et setter pour récupérer ou éditer les vies du joueur
        """
        if not get:
            self.lives -= 1
        return self.lives

    def driveBy(self, vehicule):
        vehicule.stopVehicle()
        self.hitByCar = True 
        self.hitLeft = vehicule.isLeft
        self.hitX = self.x           

    def checkCollision(self, vehicule):
        """
        Méthode pour vérifier la collision entre le joueur et les véhicules.
        """
        if not self.hitByCar:
            for veh in vehicule:
                if (self.x + 12 >= veh.x and self.x <= veh.x + 4) and (self.y+8 >= veh.y and self.y <= veh.y + 8):
                    self.driveBy(veh)
            
    def update(self, vehicules):
        """
        Méthode pour gérer les déplacements du joueur.
        """
        self.movement()
        self.checkCollision(vehicules)
    
    def draw(self):
        """
        Méthode pour déssiner le personnage sur l'écran.
        """
        if self.hitByCar :
            pyxel.circ(self.x + 7, self.y + 7, self.r, 8)
            self.r += 0.04
        else :
            self.r = 0.5
        if self.wait > pyxel.frame_count:
            pyxel.text(30, 60, "Veuillez patienter", 7)
        pyxel.blt(self.x, self.y, 0, 0, 0, 16, 16, 0)
        
    
    
class Vehicle(object):
    """
    Classe utilisée pour créer et gérer un véhicule
    """

    def __init__(self, y, isLeft = True):
        """
        Méthonde d'initialisation de la classe Vehicle, permettant de créer et gérer les attributs des véhicules.
        """
        self.x = 120 if isLeft else -10
        self.y = y
        self.isLeft = isLeft
        #Stopping methods
        self.stop = False
        self.stopMultiplier = 0.8

    def movement(self, speedMultiplier):
        """
        Méthode pour gérer le déplacement des véhicules.
        """
        if self.stop:
            self.x += 0.7 * speedMultiplier * self.stopMultiplier if self.isLeft else -0.5 * speedMultiplier * self.stopMultiplier
            self.stopMultiplier -= 0.04
        else:
            self.x -= 0.7 * speedMultiplier if self.isLeft else -0.5 * speedMultiplier    
        
    def isOnScreen(self):
        """
        Méthode pour vérifier si le véhicule à dépasser la taille de l'écran
        """
        if self.x < - 50 or self.x > 160 :
            return False
        return True

    def stopVehicle(self):
        """
        Méthode pour stopper les véhicules
        """
        self.stop = True

    def update(self, speedMultiplier):
        """
        Méthode pour mettre à jour le véhicule
        """
        self.movement(speedMultiplier)            

    def draw(self):
        """
        Méthode pour déssiner chaque véhicules sur l'écran.
        """
        if self.isLeft:
            pyxel.blt(self.x, self.y, 0, 2, 88, 28, 16, 0)
        else:
            pyxel.blt(self.x - 20, self.y, 0, 2, 88, -28, 16, 0)

if __name__ == '__main__':
    game = Game()
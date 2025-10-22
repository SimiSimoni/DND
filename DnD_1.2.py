
import random
import os
import time
import csv
import shutil

# make csv
def create_csv(path="SaveFileDnD.csv"):
    if os.path.exists(path):
        return
    data = [
        ["Name", "HP", "Dmg", "ENG", "WEAPON"],
        ["Simone", 20, 4, 10, "Sword"],
        ["TheSerpentofPride", 20, 1, 10, "Fangs"],
        ["TheDevourerofGluttony", 20, 2, 10, "Bite"],
        ["TheBeastofLust", 20, 3, 10, "Slam"],
        ["TheColossusofGreed", 20, 4, 10, "Grab"],
        ["TheDemonofEnvy", 20, 5, 10, "Pitchfork"],
        ["TheWarriorofWrath", 20, 6, 10, "Sword"],
        ["TheSpectreofSloth", 20, 7, 10, "Freeze"]
    ]
    with open(path, "w", newline="") as f:
        csv.writer(f).writerows(data)

# clear screen
def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

# draw board
def dibujar_tablero(tamano, jugador, enemigos, objetos):
    for y in range(tamano):
        fila = ""
        for x in range(tamano):
            if jugador.x == x and jugador.y == y:
                fila += jugador.simbolo
            elif any(e.x == x and e.y == y and e.sigue_vivo() for e in enemigos):
                fila += "E"
            elif any(o.x == x and o.y == y for o in objetos):
                fila += "O"
            else:
                fila += "."
        print(fila)
    print()

# move
def mover(entidad, direccion, tamano):
    if direccion == "w" and entidad.y > 0:
        entidad.y -= 1
    elif direccion == "s" and entidad.y < tamano - 1:
        entidad.y += 1
    elif direccion == "a" and entidad.x > 0:
        entidad.x -= 1
    elif direccion == "d" and entidad.x < tamano - 1:
        entidad.x += 1

# distance
def distancia(e1, e2):
    return abs(e1.x - e2.x) + abs(e1.y - e2.y)

# attack
def atacar(atacante, defensor):
    if atacante.energia < 2:
        print(f"{atacante.nombre} está cansado!")
        return
    dist = distancia(atacante, defensor)
    if atacante.tipo_ataque.lower() == "magia":
        if dist > 3:
            print(f"{atacante.nombre} está lejos!")
            return
    else:
        if dist > 1:
            print(f"{atacante.nombre} está lejos!")
            return
    defensor.hp -= atacante.dmg
    atacante.energia -= 2
    print(f"{atacante.nombre} golpea a {defensor.nombre} por {atacante.dmg}!")

# use item
def usar_objeto(jugador, obj):
    if obj.efecto == "hp":
        jugador.hp += obj.valor
    elif obj.efecto == "dmg":
        jugador.dmg += obj.valor
    elif obj.efecto == "energia":
        jugador.energia += obj.valor
    print(f"{jugador.nombre} usó {obj.nombre}! ({obj.efecto}+{obj.valor})")

# entity class
class Entidad:
    def __init__(self, nombre, hp, dmg, energia, tipo_ataque, x, y, simbolo):
        self.nombre = nombre
        self.hp = hp
        self.dmg = dmg
        self.energia = energia
        self.tipo_ataque = tipo_ataque
        self.x = x
        self.y = y
        self.simbolo = simbolo
    def sigue_vivo(self):
        return self.hp > 0

# object class
class Objeto:
    def __init__(self, nombre, efecto, valor, simbolo="O"):
        self.nombre = nombre
        self.efecto = efecto
        self.valor = valor
        self.simbolo = simbolo

# main game
def main():
    # setup csv
    Name = input("Enter your name: ")
    create_csv("SaveFileDnD.csv")
    shutil.copyfile('SaveFileDnD.csv', 'SaveFileDnDRunning.csv')

    # read csv
    Names, Hps, Dmg, Energies, weapons = [], [], [], [], []
    with open('SaveFileDnDRunning.csv', 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            Names.append(row["Name"])
            Hps.append(int(row["HP"]))
            Dmg.append(int(row["Dmg"]))
            Energies.append(int(row["ENG"]))
            weapons.append(row["WEPON"])

    if not Names:
        raise ValueError("CSV vacío")

    tamano = 8

    # player
    jugador = Entidad(Name, Hps[0], Dmg[0], Energies[0], weapons[0], 0, 0, Name[0].upper())

    # enemy queue
    cola = [
        (Names[i], Hps[i], Dmg[i], Energies[i], weapons[i])
        for i in range(1, len(Names))
    ]

    # spawn func
    def spawn_next():
        if not cola:
            return None
        n, h, d, e, w = cola.pop(0)
        return Entidad(n, h, d, e, w, tamano - 1, tamano - 1, n[0].upper())

    # first enemy
    actual = spawn_next()
    enemigos = [actual] if actual else []

    # items
    objetos = [
        Objeto("Comida", "hp", 5),
        Objeto("Poción", "dmg", 2),
        Objeto("Elixir", "energia", 5)
    ]
    for obj in objetos:
        obj.x = random.randint(1, tamano - 1)
        obj.y = random.randint(1, tamano - 1)

    # loop
    while jugador.sigue_vivo() and (enemigos or cola):
        limpiar_pantalla()
        dibujar_tablero(tamano, jugador, [e for e in enemigos if e], objetos)
        print(f"{jugador.nombre}: HP={jugador.hp} DMG={jugador.dmg} EN={jugador.energia}")

        accion = input("(w/a/s/d) move, (f) attack: ").strip().lower()

        if accion in ["w", "a", "s", "d"]:
            mover(jugador, accion, tamano)
            for obj in list(objetos):
                if obj.x == jugador.x and obj.y == jugador.y:
                    usar_objeto(jugador, obj)
                    objetos.remove(obj)
                    break
        elif accion == "f":
            vivos = [e for e in enemigos if e and e.sigue_vivo()]
            if vivos:
                target = vivos[0]
                atacar(jugador, target)

        jugador.energia = min(jugador.energia + 1, 10)

        for enemigo in [e for e in enemigos if e]:
            if not enemigo.sigue_vivo():
                continue
            rango_magia = enemigo.tipo_ataque.lower() == "magia"
            if (not rango_magia and distancia(enemigo, jugador) <= 1) or (rango_magia and distancia(enemigo, jugador) <= 3):
                atacar(enemigo, jugador)
            else:
                if enemigo.x < jugador.x:
                    enemigo.x += 1
                elif enemigo.x > jugador.x:
                    enemigo.x -= 1
                elif enemigo.y < jugador.y:
                    enemigo.y += 1
                elif enemigo.y > jugador.y:
                    enemigo.y -= 1
            enemigo.energia = min(enemigo.energia + 1, 10)

        # spawn next
        if enemigos and not enemigos[0].sigue_vivo():
            print(f"{enemigos[0].nombre} derrotado!")
            time.sleep(1)
            enemigos = []
            nuevo = spawn_next()
            if nuevo:
                print(f"¡Aparece {nuevo.nombre}!")
                time.sleep(1)
                enemigos = [nuevo]

        time.sleep(1)

    limpiar_pantalla()
    print("¡Ganaste!" if jugador.sigue_vivo() else "Has muerto...")


main()

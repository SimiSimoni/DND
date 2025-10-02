import random
import os
import time

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


class Objeto:
    def __init__(self, nombre, efecto, valor, simbolo="O"):
        self.nombre = nombre
        self.efecto = efecto  
        self.valor = valor
        self.simbolo = simbolo


def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')


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


def mover(entidad, direccion, tamano):
    if direccion == "w" and entidad.y > 0:
        entidad.y -= 1
    elif direccion == "s" and entidad.y < tamano - 1:
        entidad.y += 1
    elif direccion == "a" and entidad.x > 0:
        entidad.x -= 1
    elif direccion == "d" and entidad.x < tamano - 1:
        entidad.x += 1


def distancia(e1, e2):
    return abs(e1.x - e2.x) + abs(e1.y - e2.y)


def atacar(atacante, defensor):
    if atacante.energia < 2:
        print(f"{atacante.nombre} está demasiado cansado para atacar!")
        return

    dist = distancia(atacante, defensor)
    if atacante.tipo_ataque == "espada" and dist > 1:
        print(f"{atacante.nombre} está demasiado lejos para usar la espada!")
        return
    if atacante.tipo_ataque == "magia" and dist > 3:
        print(f"{atacante.nombre} está demasiado lejos para lanzar magia!")
        return

    defensor.hp -= atacante.dmg
    atacante.energia -= 2
    print(f"{atacante.nombre} golpea a {defensor.nombre} causando {atacante.dmg} de daño!")


def usar_objeto(jugador, obj):
    if obj.efecto == "hp":
        jugador.hp += obj.valor
    elif obj.efecto == "dmg":
        jugador.dmg += obj.valor
    elif obj.efecto == "energia":
        jugador.energia += obj.valor
    print(f"{jugador.nombre} usó {obj.nombre}! ({obj.efecto}+{obj.valor})")


def main():
    tamano = 8
    jugador = Entidad("Héroe", 20, 4, 10, "espada", 0, 0, "J")

    enemigos = [
        Entidad("Goblin", 10, 3, 5, "espada", 5, 5, "E"),
        Entidad("Mago", 8, 5, 10, "magia", 6, 2, "E")
    ]

    objetos = [
        Objeto("Comida", "hp", 5),
        Objeto("Poción de fuerza", "dmg", 2),
        Objeto("Elixir", "energia", 5)
    ]
    for obj in objetos:
        obj.x = random.randint(1, tamano-1)
        obj.y = random.randint(1, tamano-1)

    while jugador.sigue_vivo() and any(e.sigue_vivo() for e in enemigos):
        limpiar_pantalla()
        dibujar_tablero(tamano, jugador, enemigos, objetos)
        print(f"{jugador.nombre}: HP={jugador.hp}, DMG={jugador.dmg}, EN={jugador.energia}")

        accion = input("Mover (w/a/s/d), Atacar (f), o Esperar (enter): ").strip().lower()

        if accion in ["w", "a", "s", "d"]:
            mover(jugador, accion, tamano)

            for obj in objetos:
                if obj.x == jugador.x and obj.y == jugador.y:
                    usar_objeto(jugador, obj)
                    objetos.remove(obj)
                    break

        elif accion == "f":
            enemigos_vivos = [e for e in enemigos if e.sigue_vivo()]
            if enemigos_vivos:
                mas_cercano = min(enemigos_vivos, key=lambda e: distancia(jugador, e))
                atacar(jugador, mas_cercano)

        jugador.energia = min(jugador.energia + 1, 10)

        for enemigo in enemigos:
            if not enemigo.sigue_vivo():
                continue
            if distancia(enemigo, jugador) <= 1 and enemigo.tipo_ataque == "espada":
                atacar(enemigo, jugador)
            elif distancia(enemigo, jugador) <= 3 and enemigo.tipo_ataque == "magia":
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

        time.sleep(0.5)

    limpiar_pantalla()
    if jugador.sigue_vivo():
        print("¡Has derrotado a todos los enemigos!")
    else:
        print("Has muerto...")


if __name__ == "__main__":
    main()
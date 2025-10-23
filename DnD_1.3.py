import random
import os
import time
import csv
import shutil

# make csv
def create_csv(path="SaveFileDnD.csv"):
    recrear = True
    if os.path.exists(path):
        with open(path, newline='') as f:
            reader = csv.reader(f)
            header = next(reader, [])
            if header == ["Name", "HP", "Dmg", "ENG", "WEAPON"]:
                recrear = False
    if recrear:
        data = [
            ["Name", "HP", "Dmg", "ENG", "WEAPON"],
            ["Jugador", 20, 4, 10, "Espada "],
            ["Araña", 20, 1, 10, "Mordida"],
            ["Bruja", 20, 2, 10, "Magia"],
            ["Duende", 20, 3, 10, "Lanza"],
            ["Ogro", 20, 4, 10, "Martillo"],
            ["Gigante", 20, 5, 10, "Pisada"],
            ["Elfo", 20, 6, 10, "Magia"],
            ["Dragon", 20, 7, 10, "Aliento de Fuego"]
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

# moverse
def mover(entidad, direccion, tamano):
    if direccion == "w" and entidad.y > 0:
        entidad.y -= 1
    elif direccion == "s" and entidad.y < tamano - 1:
        entidad.y += 1
    elif direccion == "a" and entidad.x > 0:
        entidad.x -= 1
    elif direccion == "d" and entidad.x < tamano - 1:
        entidad.x += 1

# distancia
def distancia(e1, e2):
    return abs(e1.x - e2.x) + abs(e1.y - e2.y)

# ataque
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

# usar item
def usar_objeto(jugador, obj):
    if obj.efecto == "hp":
        jugador.hp += obj.valor
    elif obj.efecto == "dmg":
        jugador.dmg += obj.valor
    elif obj.efecto == "energia":
        jugador.energia += obj.valor
    print(f"{jugador.nombre} usó {obj.nombre}! ({obj.efecto}+{obj.valor})")
    # marcar el objeto como recogido (fuera del tablero)
    obj.x = -1
    obj.y = -1

# clase de entidad
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

# clase objeto
class Objeto:
    def __init__(self, nombre, efecto, valor, simbolo="O"):
        self.nombre = nombre
        self.efecto = efecto
        self.valor = valor
        self.simbolo = simbolo
        # posición -1 indica "no en el tablero"
        self.x = -1
        self.y = -1

# juego principal
def main():
    # Historia del juego
    print("Erase una vez un reino lejano en el que había existido mucha tranquilidad...")
    time.sleep(3)
    print("Pero todo cambió cuando un libro prohibido de magia es abierto por accidedente")
    print("liberando criaturas y enigmas que amenzan el reino.")
    time.sleep(3)
    print("Tu misión es derrotar a los enemigos y sobrevivir en este mundo peligroso.")
    print("¡Prepárate para la batalla!")
    time.sleep(3)
    
    # Menú inicial
    limpiar_pantalla()
 
    create_csv("SaveFileDnD.csv")
    shutil.copyfile('SaveFileDnD.csv', 'SaveFileDnDRunning.csv')
    

   
    Nombres, Hps, Dmg, Energias, Armas = [], [], [], [], []
    with open('SaveFileDnDRunning.csv', 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            Nombres.append(row["Name"])
            Hps.append(int(row["HP"]))
            Dmg.append(int(row["Dmg"]))
            Energias.append(int(row["ENG"]))
            Armas.append(row["WEAPON"])

    if not Nombres:
        raise ValueError("CSV vacío")

    tamano = 8

    # Player
    nombre = input("Ingresa tu nombre: ")
    jugador = Entidad(nombre, Hps[0], Dmg[0], Energias[0], Armas[0], 0, 0, nombre[0].upper())
    with open('SaveFileDnDRunning.csv', 'r') as f:
        lines = f.readlines()
    lines[1] = f"{nombre},{jugador.hp},{jugador.dmg},{jugador.energia},{jugador.tipo_ataque}\n"
    with open('SaveFileDnDRunning.csv', 'w') as f:
        f.writelines(lines)
    print(f"{nombre[0]} representa al jugador,'E' a los enemigos y'O' son objetos que puedes recoger.")
    time.sleep(3)
    limpiar_pantalla()
    # Enemy queue
    cola = [
        (Nombres[i], Hps[i], Dmg[i], Energias[i], Armas[i])
        for i in range(1, len(Nombres))
    ]

    # Spawn function
    def spawn_next():
        if not cola:
            return None
        n, h, d, e, w = cola.pop(0)
        return Entidad(n, h, d, e, w, tamano - 1, tamano - 1, n[0].upper())

    # First enemy
    actual = spawn_next()
    enemigos = [actual] if actual else []

    # Items
    objetos = [
        Objeto("Comida", "hp", 5),
        Objeto("Poción", "dmg", 2),
        Objeto("Elixir", "energia", 5)
    ]

    # Respawn: coloca solo objetos que estén fuera del tablero y evita solapamientos
    def respawnObjetos():
        ocupado = set()
        # marcar posiciones ocupadas por jugador y enemigos
        ocupado.add((jugador.x, jugador.y))
        for e in enemigos:
            if e and e.sigue_vivo():
                ocupado.add((e.x, e.y))
        # también añadir objetos ya colocados
        for o in objetos:
            if o.x >= 0 and o.y >= 0:
                ocupado.add((o.x, o.y))

        for obj in objetos:
            if obj.x < 0 or obj.y < 0:
                # buscar posición libre
                intentos = 0
                while True:
                    intentos += 1
                    nx = random.randint(0, tamano - 1)
                    ny = random.randint(0, tamano - 1)
                    if (nx, ny) not in ocupado:
                        obj.x = nx
                        obj.y = ny
                        ocupado.add((nx, ny))
                        break
                    if intentos > 200:
                        # en caso extremo, dejar el objeto fuera (no hay espacio)
                        obj.x = -1
                        obj.y = -1
                        break

    respawnObjetos()

    # Loop
    while jugador.sigue_vivo() and (enemigos or cola):
        limpiar_pantalla()
        dibujar_tablero(tamano, jugador, [e for e in enemigos if e], objetos)
        print(f"{jugador.nombre}: HP={jugador.hp} DMG={jugador.dmg} EN={jugador.energia}")

        accion = input("(w/a/s/d) move, (f) attack: ").strip().lower()

        if accion in ["w", "a", "s", "d"]:
            mover(jugador, accion, tamano)
            for obj in objetos:
                if obj.x == jugador.x and obj.y == jugador.y:
                    usar_objeto(jugador, obj)
                    # no removemos el objeto de la lista: se marcó como fuera (-1,-1)
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

        
        if enemigos and not enemigos[0].sigue_vivo():
            print(f"{enemigos[0].nombre} derrotado!")
            time.sleep(1)
            enemigos = []
            nuevo = spawn_next()
            if nuevo:
                print(f"¡Aparece {nuevo.nombre}!")
                time.sleep(1)
                enemigos = [nuevo]
                # al aparecer nuevo enemigo, respawn de objetos faltantes
                respawnObjetos()  

        time.sleep(1)

    limpiar_pantalla()
    print("¡Ganaste!" if jugador.sigue_vivo() else "Has muerto...")

if __name__ == "__main__":
    main()

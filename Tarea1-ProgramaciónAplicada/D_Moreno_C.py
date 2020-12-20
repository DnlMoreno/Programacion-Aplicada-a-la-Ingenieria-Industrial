# -*- coding: utf-8 -*-
"""
Created on Fri Oct 23 17:33:09 2020

@author: dnlmo
"""
# Se crea el nodo caja
class Caja(object):
    def __init__ (self, caja, persona):
        self.caja = caja
        self.persona = persona
        self.siguiente = None

# Se crea el nodo cliente
class Cliente(object):
    def __init__(self, identificador, tipo, preferencia, tpo_llegada, tpo_demora):
        self.identificador = identificador
        self.tipo = tipo
        self.preferencia = preferencia
        self.tpo_llegada = tpo_llegada
        self.tpo_demora = tpo_demora
        
        self.anterior = None
        self.siguiente = None
    
    # Para poder ordenar a los clientes por orden de llegada.
    def __lt__(self, otro):
        return self.tpo_llegada < otro.tpo_llegada   
        
class ListaD(object):
    # Constructor: crea la lista 
    def __init__(self):
        self.inicio = None
        self.fin = None
        self.tamano = 0
        
    # Inserta al inicio multiples atributos 
    def insertarInicioCl(self, identificador, tipo, preferencia, tpo_llegada, tpo_demora):
        nuevoNodo = Cliente(identificador, tipo, preferencia, tpo_llegada, tpo_demora)
        nuevoNodo.siguiente = self.inicio
        if self.tamano == 0:
            self.fin = nuevoNodo
        else:
            self.inicio.anterior = nuevoNodo
        self.inicio = nuevoNodo
        self.tamano += 1
        
    # Insertar al final multiples atributos 
    def insertarAtrasCl(self, identificador, tipo, preferencia, tpo_llegada, tpo_demora):
        nuevoNodo = Cliente(identificador, tipo, preferencia, tpo_llegada, tpo_demora)
        nuevoNodo.anterior = self.fin
        if self.tamano == 0:
            self.inicio = nuevoNodo
        else:
            self.fin.siguiente = nuevoNodo
        self.fin = nuevoNodo
        self.tamano += 1
    
    # Recorre e imprime los valores del inicio al fin
    def recorrerAdelanteCl(self):
        lista_i = self.inicio
        while lista_i is not None:
                print(lista_i.identificador, lista_i.tipo, lista_i.preferencia, lista_i.tpo_llegada, lista_i.tpo_demora)
                lista_i = lista_i.siguiente
                
    # Recorre e imprime los valores del fin al inicio de los multiples atributos
    def recorrerAtrasCl(self):
        lista_i = self.fin
        while lista_i is not None:
            print(lista_i.identificador, lista_i.tipo, lista_i.preferencia, lista_i.tpo_llegada, lista_i.tpo_demora)
            lista_i = lista_i.anterior
            
    # Elimina el primer elemento
    def eliminar(self):
        aux = self.inicio
        if (aux == None): # Lista vacía: también puede ser self.tamano == 0
            return
        self.inicio = aux.siguiente
        retornar = aux
        self.tamano -= 1
        if (self.tamano == 0):
            self.fin = None
        aux = None
        return retornar.identificador, retornar.tipo, retornar.preferencia, retornar.tpo_llegada, retornar.tpo_demora
        
    # Largo de la lista
    def largo(self):
        return int(self.tamano)
        
    # Obtiene el indice del nodo    
    def __getitem__(self, indice):
        if indice >= 0 and indice < self.tamano:
            actual = self.inicio
            for _ in range(indice):
                actual = actual.siguiente           
            return actual.identificador, actual.tipo, actual.preferencia, actual.tpo_llegada, actual.tpo_demora
        else:
            raise Exception('Índice no válido. Está por fuera del rango.')

    # Modifica el indice de un nodo. En este caso especificamente el idenfiticador
    def __setitem__(self, indice, identificador):
        if indice >= 0 and indice < self.tamano:
            actual = self.inicio
            for _ in range(indice):
                actual = actual.siguiente            
            actual.identificador = identificador
        else:
            raise Exception('Índice no válido. Está por fuera del rango.')      
    
    
class ListaE(object):
    # Constructor: crea la lista 
    def __init__(self):
        self.inicio = None
        self.fin = None
        self.tamano = 0
        
    def insertar(self, caja, persona):
        nuevoNodo = Caja(caja, persona)
        nuevoNodo.siguiente = self.inicio
        self.inicio = nuevoNodo
        if self.tamano == 0:
            self.fin = nuevoNodo
        self.tamano += 1

    def recorrer(self):
        lista_i = self.inicio
        while lista_i is not None:
            print(lista_i.caja, lista_i.persona)
            lista_i = lista_i.siguiente
        
    def eliminar (self):
        aux = self.inicio
        if (aux == None):
            return
        self.inicio = aux.siguiente
        retornar = aux
        self.tamano -= 1
        if (self.tamano == 0):
            self.fin = None
        aux = None
        return retornar.caja, retornar.persona
    
    def largo (self):
        return int (self.tamano)
    
    # Obtiene el indice del nodo  
    def __getitem__(self, indice):
        if indice >= 0 and indice < self.tamano:
            actual = self.inicio
            for i in range(indice):
                actual = actual.siguiente        
            return actual.caja, actual.persona
        else:
            raise Exception('Índice no válido. Está por fuera del rango.')    
    
    # Modifica el indice de un nodo. En este caso, solo a la persona que se encuentra en la caja, ya que ese es el unico valor que se ira modificando.       
    def __setitem__(self, indice, persona):
        if indice >= 0 and indice < self.tamano:
            actual = self.inicio
            for i in range(indice):
                actual = actual.siguiente           
            actual.persona = persona
        else:
            raise Exception('Índice no válido. Está por fuera del rango.')

# Se guardan en una lista la cantidad de cajas por tipo de caja que tiene el banco. Primero las cajas g, luego las cajas t y despues las cajas e.
# Se guarda en una lista el tiempo respectivo que tendra cada caja por cada cliente que atienda.
def creacionCajas(n, cajas_g, cajas_t, cajas_e):
    for caja in range(cajas_g):
        lista_cajas.insertar(n, '-')
        lista_tiempo.insertar(n, 0)
        n -= 1
        
    for caja in range(cajas_t):
        lista_cajas.insertar(n, '-')
        lista_tiempo.insertar(n, 0)
        n -= 1        

    for caja in range(cajas_e):
        lista_cajas.insertar(n, '-')
        lista_tiempo.insertar(n, 0)    
        n -= 1
    return                    

##### En primer lugar se ordenan las colas con los clientes de llegada y preferencia, y luego se analiza el tema de las cajas y los traspaso de clientes a otras cajas vacias. #####

# Función que permite ordenar las colas g y t segun los atributos de cada cliente.
# Si la cola esta vacia, simplemente añade al cliente en la cola respectiva.
# Si hay clientes en la cola, se verifica si el cliente que esta llegando tiene preferencia. 
    # Si el cliente tiene preferencia se observa si al principio de la cola hay mas clientes con preferencia, luego el cliente se ingresa detras del ultimo cliente con preferencia y antes que los que no tienen preferencia.
    # Si el cliente no tiene preferenia simplemente se añade a la cola. 
def ordenarCola_gt(cola, tipo):
    if len(cola) == 0:
        if lista_clientes[c][1] == tipo:
            cola.append(lista_clientes[c])
    
    elif len(cola) != 0 and lista_clientes[c][1] == tipo:
        if int(lista_clientes[c][2]) == 1:
            g = 0
            try:
                while int(cola[g][2]) == 1:
                    g += 1
                cola.insert(g, lista_clientes[c])
            except IndexError:
                cola.append(lista_clientes[c])                         
        else:
            cola.append(lista_clientes[c])           
    return

# Funcion que va añadiendo directamente a los clientes en la "cola e", ya que la caja e no cuenta con cliente con preferencia
def ordenarCola_e(cola, tipo):
    if lista_clientes[c][1] == tipo:
        cola.append(lista_clientes[c])     
    return

# Funcion que permite el movimiento de los clientes entre cajas y los elimina cuando se acabo su tiempo de demora
def movimiento1Cajas(cola1, cola2, cola3, tipo): 
    # Se compara si el tiempo de demora del cliente que esta en la caja es igual al tiempo de haber estado en la caja.
    if lista_cajas[w][1] != '-':
        if int(lista_cajas[w][1][4]) == lista_tiempo[w][1]:
            x = lista_cajas[w][1] ## Cliente que sale de la caja
            lista_cajas[w] = '-'
            lista_tiempo[w] = 0
            pila_clientes.append(x) # Pila de clientes que salen
      
    # Si no hay nadie en el caja w entonces se ingresa al primer cliente de su cola respectiva    
    if lista_cajas[w][1] == '-' and len(cola1) != 0:
        try:
            if cola1[0][1] == tipo:
                a = cola1.popleft()
                lista_cajas[w] = a
        except IndexError:
            pass
            
    # Si no hay nadie en la caja w y la cola de ese tipo de caja esta vacia, entonces se comprueba que cola de los otros dos tipos de colas es mas larga
    # La cola mas larga es la que permite ingresar al cliente a la caja vacia (otro tipo de caja). 
    # En caso de que las dos colas tengan el mismo largo, se le da preferencia a la caja T > E > G en ese orden. (LEEME.txt)
    if lista_cajas[w][1] == '-'  and len(cola1) == 0 and len(cola2) != 0 and len(cola3) != 0:
        if len(cola2) > len(cola3):
            a = cola2.popleft()
            lista_cajas[w] = a
        elif len(cola2) == len(cola3) and len(cola2) != 0:
            a = cola2.popleft()
            lista_cajas[w] = a 
        else:
            a = cola3.popleft()
            lista_cajas[w] = a
    return

# Este segundo movimiento de las cajas es en el caso de que un cliente salga de la caja en un instante t y hayan clientes en otra cola.
# Esto les permite a los clientes de otra cola ingresar en ese mismo instante t a la caja que se desocupo recien.
def movimiento2Cajas(cola1, cola2):
    if lista_cajas[aux][1] == '-' and len(cola2) != 0:
        if len(cola2) > len(cola1):
            a = cola2.popleft()
            lista_cajas[aux] = a
        elif len(cola1) == len(cola2) and len(cola1) != 0:
            a = cola1.popleft()
            lista_cajas[aux] = a                                                
        else:
            a = cola1.popleft()
            lista_cajas[aux] = a  
    return

# Aqui simplemente se muestra la salida en consola dividida en intervalos de los distintos tipos de clientes 
def salidaConsola(caja_g, caja_t, caja_e, cola_g, cola_t, cola_e):                                               
    if caja_g > aux:                    
        print(f'En el tiempo {i}, la caja tipo G n°{lista_cajas[aux][0]}, esta atendiendo a la persona {lista_cajas[aux][1]}')
    if aux == caja_g:
        q = 0
        for cliente in range(len(cola_g)):
            print(f'En la cola G se encuentra el cliente {cola_g[q]}')
            q += 1
        print("")
            
    if caja_t + caja_g > aux >= caja_g:                        
        print(f'En el tiempo {i}, la caja tipo T n°{lista_cajas[aux][0]}, esta atendiendo a la persona {lista_cajas[aux][1]}')
    if aux == caja_t + caja_g:
        q = 0
        for cliente in range(len(cola_t)):
            print(f'En la cola T se encuentra el cliente {cola_t[q]}')
            q += 1 
        print("")

    if (caja_e + caja_t + caja_g) > aux >= caja_t + caja_g:
        print(f'En el tiempo {i}, la caja tipo E n°{lista_cajas[aux][0]}, esta atendiendo a la persona {lista_cajas[aux][1]}')
    if aux == caja_e + caja_t + caja_g - 1:
        q = 0
        for cliente in range(len(cola_e)):
            print(f'En la cola E se encuentra el cliente {cola_e[q]}')
            q += 1
        print("")
    return

# Para guardar las colas en el archivo de salida
def ultimaEscritura(cola):
    archivo.write('\n')
    cont = 0
    if len(cola) == 0:
        archivo.write(f'-')     
    else:
        for personas in range(len(cola)):
            archivo.write(f'{cola[cont][0]} ')
            cont += 1
    return

# Para salir de la ejecución del programa
def salir():
    print("")
    print('Has salido de la ejecución del programa')

# Las opciones de menu que tendra el usuario para ingresar
def menu():
    print("")
    print(f'1. Avanzar en una instancia de tiempo.')    
    print(f'2. Ir a una instancia de tiempo en particular.')
    print(f'3. Ir a la ultima instancia de tiempo de la ejecución del programa.')     
    print(f'4. Terminar la ejecución del programa.')      
    return            
            
from queue import PriorityQueue
from collections import deque

clientes_ordenados = PriorityQueue()
lista_clientes = ListaD()
lista_cajas = ListaE()
lista_tiempo = ListaE()

# Se leen y se ordenan los clientes por hora de llegada con el metodo cola prioridad, para luego insertarlos en la lista clientes, la cual ya estara ordenada
with open('banco.in') as f: 
    for linea in f:
        a = linea.split()
        if len(a) == 4:
            cajas = (int(a[0]), int(a[1]), int(a[2]), int(a[3]))
        if len(a) == 5:
            clientes_ordenados.put(Cliente(int(a[0]), a[1], int(a[2]), int(a[3]), int(a[4])))
while not clientes_ordenados.empty():
    c = clientes_ordenados.get()
    lista_clientes.insertarAtrasCl(c.identificador, c.tipo, c.preferencia, c.tpo_llegada, c.tpo_demora)

pila_clientes = list()
    
cola_g = deque()
cola_t = deque()
cola_e = deque()

i = 0 # El instante de tiempo
op = 0
c = 0 # Para ir contando a los clientes que vayan ingresando del archivo txt.
cant_personas_acumulado = 0 # Para saber si llegamos al ultimo cliente del texto de entrada
creacionCajas(cajas[0], cajas[1], cajas[2], cajas[3])
        
while op != 4:
    menu()
    # Seguira en el while hasta que el usuario ingrese algun valor correcto (robustez).
    while True:
        try:
            op = int(input("Elige una opción: "))
            print("")
            break
        except ValueError:
            print("Valor ingresado no es valido, intente nuevamente")
    
    # Para avanzar instancia por instancia como una simulación del proceso       
    if op == 1:
        # Se abre el archivo con 'w' para que se vaya sobreescribiendo instancia por instancia.
        archivo = open('banco.out', 'w')
        
        # Mientras aun queden clientes en el archivo de entrada, se activara esta parte.
        if cant_personas_acumulado < lista_clientes.largo():
            print(f'Usted se encuentra en el instante de tiempo {i}.')
            print("")
            
            # Para saber si llegamos al ultimo cliente del texto de entrada.
            # Ademas se obtienen a los clientes que llegan en el mismo instante de tiempo en el que se encuentra el programa
            j = 0           
            while int(lista_clientes[j + cant_personas_acumulado][3]) == i:
                j += 1
                if j + cant_personas_acumulado == lista_clientes.largo():
                    print("Este es el último instante de tiempo en el que llegaran clientes por hoy")
                    print("")
                    break
                
            cant_personas_ll = j
            cant_personas_acumulado += cant_personas_ll
            
            # En primer lugar, se ordena en las colas a los clientes que llegaron en un mismo instante de tiempo, teniendo en cuenta la preferencia y el tipo
            for k in range(cant_personas_ll):
                ordenarCola_gt(cola_g, 'g')
                ordenarCola_gt(cola_t, 't')
                ordenarCola_e(cola_e, 'e')
                c += 1               
            
            # Se comienzan a ingresar a los clientes que estan en la cola ya ordenados en las cajas desocupadas, teniendo en cuenta que si una caja esta vacia puede recibir a otro tipo de cliente que esta en otra cola
            w = 0
            for u in range(cajas[0]):       
                if cajas[1] > w:
                    movimiento1Cajas(cola_g, cola_t, cola_e, 'g')            
                
                if cajas[2] + cajas[1] > w >= cajas[1]:
                    movimiento1Cajas(cola_t, cola_e, cola_g, 't')                                     
                
                if (cajas[3] + cajas[2] + cajas[1]) > w >= cajas[2] + cajas[1]:
                    movimiento1Cajas(cola_e, cola_t, cola_g, 'e')                
                                                                                                                                        
                w += 1
                
            # Aqui se hace el segundo movimiento de las cajas, la cual es en el caso de que un cliente se vaya de la caja en un instante de tiempo t y haya otro cliente en otra cola en ese instante t. 
            # Entonces esta parte permite ingresar al cliente que se encuentra en la cola, a la caja que se desocupo recien (en el mismo instante t).
            aux = 0
            for u in range(cajas[0]):  
                movimiento2Cajas(cola_t, cola_g)
                movimiento2Cajas(cola_e, cola_g)
                movimiento2Cajas(cola_t, cola_e)           
                
                # Se compara si el tiempo de demora del cliente que esta en la caja es igual al tiempo de haber estado en la caja.
                if lista_cajas[aux][1] != '-':
                    if int(lista_cajas[aux][1][4]) == lista_tiempo[aux][1]:
                        x = lista_cajas[aux][1] ## Cliente que sale de la caja
                        lista_cajas[aux] = '-'
                        lista_tiempo[aux] = 0
                        pila_clientes.append(x) 
                
                # Se suma un instante de tiempo para lo clientes que estan en cajas
                if lista_cajas[aux][1] != '-':                    
                    lista_tiempo[aux] = lista_tiempo[aux][1] + 1
                
                # La salida de consola + el guardar las cajas en el archivo de salida.
                salidaConsola(cajas[1], cajas[2], cajas[3], cola_g, cola_t, cola_e)  
                archivo = open('banco.out', 'a')
                archivo.write(f'{lista_cajas[aux][0]} {lista_cajas[aux][1][0]}\n') 
                      
                aux += 1
            
            # Se guardan las colas en el archivo y ademas se crea la pila de clientes que han salido
            ultimaEscritura(cola_g)
            ultimaEscritura(cola_t)
            ultimaEscritura(cola_e)
            archivo.write('\n')
            if len(pila_clientes) == 0:
                archivo.write(f'-')
            else:
                pila = 0
                for client in range(len(pila_clientes)):
                    archivo.write(f'{pila_clientes[pila][0]} ')
                    pila += 1            
            archivo.close()                 
            i += 1                
         
        # Esta parte se activa cuando ya no llegaran mas clientes al banco y solo quedan clientes en las colas
        # Aqui solo se considera el movimiento de las colas con las cajas. Es el mismo codigo de arriba, solo se agrego el termino de la ejecucion del programa, que se activa cuando no quedan mas clientes en las cajas ni en las colas
        else:
            archivo = open('banco.out', 'w')                   
            print(f'Usted se encuentra en el instante de tiempo {i}.')
            print("")                

            w = 0
            for u in range(cajas[0]):
                if cajas[1] > w:
                    movimiento1Cajas(cola_g, cola_t, cola_e, 'g')            
                
                if cajas[2] + cajas[1] > w >= cajas[1]:
                    movimiento1Cajas(cola_t, cola_e, cola_g, 't')                                     
                
                if (cajas[3] + cajas[2] + cajas[1]) > w >= cajas[2] + cajas[1]:
                    movimiento1Cajas(cola_e, cola_t, cola_g, 'e')                                             
                                                                            
                w += 1
                
            m = 0    
            aux = 0
            for u in range(cajas[0]): 
                movimiento2Cajas(cola_t, cola_g)
                movimiento2Cajas(cola_e, cola_g)
                movimiento2Cajas(cola_t, cola_e) 
                
                if lista_cajas[aux][1] != '-':
                    if int(lista_cajas[aux][1][4]) == lista_tiempo[aux][1]:
                        x = lista_cajas[aux][1] ## Cliente que sale de la caja
                        lista_cajas[aux] = '-'
                        lista_tiempo[aux] = 0
                        pila_clientes.append(x) 
                        
                if lista_cajas[aux][1] != '-':                    
                    lista_tiempo[aux] = lista_tiempo[aux][1] + 1            
                        
                salidaConsola(cajas[1], cajas[2], cajas[3], cola_g, cola_t, cola_e) 
                archivo = open('banco.out', 'a')
                archivo.write(f'{lista_cajas[aux][0]} {lista_cajas[aux][1][0]}\n')
                        
                aux += 1   
                
                # Cuando todas las cajas esten desocupadas significa que la simulación acabo.                 
                if lista_cajas[m][1] == '-':
                    m += 1
                    if m < cajas[0]:
                        pass
                    else:
                        print("")
                        print(f'La simulación ha finalizado en el instante de tiempo {i}, ya que no queda ningun cliente en las cajas')
                        op = 4 
                        
            ultimaEscritura(cola_g)
            ultimaEscritura(cola_t)
            ultimaEscritura(cola_e)
            archivo.write('\n')
            if len(pila_clientes) == 0:
                archivo.write(f'-')
            else:
                pila = 0
                for client in range(len(pila_clientes)):
                    archivo.write(f'{pila_clientes[pila][0]} ')
                    pila += 1            
            archivo.close()                               
            i += 1        
    
    # Para ir a una instancia de tiempo en particular, permitiendo el avanzar o retroceder.
    # El codigo es igual a la parte de arriba solo que se añade un contador que permite ir a la instancia que ingrese el usuario.
    elif op == 2:
        # Se ingresan las variables de inicio adentro para que se pueda retroceder a alguna instancia o avanzar sin ningun problema
        pila_clientes = list()
        cola_g = deque()
        cola_t = deque()
        cola_e = deque()
        c = 0 # para el for
        cant_personas_acumulado = 0
        i = 0
        creacionCajas(cajas[0], cajas[1], cajas[2], cajas[3])
        
        while True:
            try:
                instancia = int(input("Elige una instancia a la cual quieras ir: "))
                print("")
                break
            except ValueError:
                print("Valor ingresado no es valido, intente nuevamente")
                
        contador = 0
        while instancia >= contador:                       
            if cant_personas_acumulado < lista_clientes.largo():
                archivo = open('banco.out', 'w') 
                print(f'Usted se encuentra en el instante de tiempo {i}.')
                print("")
                
                j = 0           
                while int(lista_clientes[j + cant_personas_acumulado][3]) == i:
                    j += 1
                    if j + cant_personas_acumulado == lista_clientes.largo():
                        print("Este es el último instante de tiempo en el que llegaran clientes por hoy")
                        print("")
                        break
                    
                cant_personas_ll = j
                cant_personas_acumulado += cant_personas_ll       
    
                for k in range(cant_personas_ll):
                    ordenarCola_gt(cola_g, 'g')
                    ordenarCola_gt(cola_t, 't')
                    ordenarCola_e(cola_e, 'e')   
                    c += 1  
                         
                w = 0
                for u in range(cajas[0]):       
                    if cajas[1] > w:
                        movimiento1Cajas(cola_g, cola_t, cola_e, 'g')            
                    
                    if cajas[2] + cajas[1] > w >= cajas[1]:
                        movimiento1Cajas(cola_t, cola_e, cola_g, 't')                                     
                    
                    if (cajas[3] + cajas[2] + cajas[1]) > w >= cajas[2] + cajas[1]:
                        movimiento1Cajas(cola_e, cola_t, cola_g, 'e')
                                                                                                                                 
                    w += 1
    
                aux = 0
                for u in range(cajas[0]):  
                    movimiento2Cajas(cola_t, cola_e)
                    movimiento2Cajas(cola_e, cola_g)
                    movimiento2Cajas(cola_t, cola_g)           
                    
                    if lista_cajas[aux][1] != '-':
                        if int(lista_cajas[aux][1][4]) == lista_tiempo[aux][1]:
                            x = lista_cajas[aux][1] ## Cliente que sale de la caja
                            lista_cajas[aux] = '-'
                            lista_tiempo[aux] = 0
                            pila_clientes.append(x) 
                            
                    if lista_cajas[aux][1] != '-':                    
                        lista_tiempo[aux] = lista_tiempo[aux][1] + 1
                    
                    salidaConsola(cajas[1], cajas[2], cajas[3], cola_g, cola_t, cola_e)
                    archivo = open('banco.out', 'a')
                    archivo.write(f'{lista_cajas[aux][0]} {lista_cajas[aux][1][0]}\n') 
                          
                    aux += 1
                    
                ultimaEscritura(cola_g)
                ultimaEscritura(cola_t)
                ultimaEscritura(cola_e)
                archivo.write('\n')
                if len(pila_clientes) == 0:
                    archivo.write(f'-')
                else:
                    pila = 0
                    for client in range(len(pila_clientes)):
                        archivo.write(f'{pila_clientes[pila][0]} ')
                        pila += 1            
                archivo.close() 
                        
                contador += 1
                i += 1                
                    
            else:  
                archivo = open('banco.out', 'w')                    
                print(f'Usted se encuentra en el instante de tiempo {i}.')
                print("")                
    
                w = 0
                for u in range(cajas[0]):
                    if cajas[1] > w:
                        movimiento1Cajas(cola_g, cola_t, cola_e, 'g')            
                    
                    if cajas[2] + cajas[1] > w >= cajas[1]:
                        movimiento1Cajas(cola_t, cola_e, cola_g, 't')                                     
                    
                    if (cajas[3] + cajas[2] + cajas[1]) > w >= cajas[2] + cajas[1]:
                        movimiento1Cajas(cola_e, cola_t, cola_g, 'e')                                             
                                                                                
                    w += 1
                    
                m = 0    
                aux = 0
                for u in range(cajas[0]): 
                    movimiento2Cajas(cola_t, cola_e)
                    movimiento2Cajas(cola_e, cola_g)
                    movimiento2Cajas(cola_t, cola_g) 
                    
                    if lista_cajas[aux][1] != '-':
                        if int(lista_cajas[aux][1][4]) == lista_tiempo[aux][1]:
                            x = lista_cajas[aux][1] ## Cliente que sale de la caja
                            lista_cajas[aux] = '-'
                            lista_tiempo[aux] = 0
                            pila_clientes.append(x) 
                            
                    if lista_cajas[aux][1] != '-':                    
                        lista_tiempo[aux] = lista_tiempo[aux][1] + 1            
                            
                    salidaConsola(cajas[1], cajas[2], cajas[3], cola_g, cola_t, cola_e)
                    archivo = open('banco.out', 'a')
                    archivo.write(f'{lista_cajas[aux][0]} {lista_cajas[aux][1][0]}\n')                     
                            
                    aux += 1   
                                     
                    if lista_cajas[m][1] == '-':
                        m += 1
                        if m < cajas[0]:
                            pass
                        else:
                            print("")
                            print(f'La simulación ha finalizado en el instante de tiempo {i}, ya que no queda ningun cliente en las cajas')
                            print("")
                            op = 4
                            
                ultimaEscritura(cola_g)
                ultimaEscritura(cola_t)
                ultimaEscritura(cola_e)
                archivo.write('\n')
                if len(pila_clientes) == 0:
                    archivo.write(f'-')
                else:
                    pila = 0
                    for client in range(len(pila_clientes)):
                        archivo.write(f'{pila_clientes[pila][0]} ')
                        pila += 1            
                archivo.close() 
                                           
                i += 1
                contador += 1
    
    # Nuevamente el codigo es el mismo del de arriba, solamente que aqui se agrega un while que corre el programa hasta que no quede ningun cliente en las cajas. En ese momento f cambia a True y se sale del while, mostrando la ultima instancia de la ejecución del programa.    
    elif op == 3: 
        f = True
        while f:                       
            if cant_personas_acumulado < lista_clientes.largo():
                archivo = open('banco.out', 'w')
                print(f'Usted se encuentra en el instante de tiempo {i}.')
                print("")
                
                j = 0           
                while int(lista_clientes[j + cant_personas_acumulado][3]) == i:
                    j += 1
                    if j + cant_personas_acumulado == lista_clientes.largo():
                        print("Este es el último instante de tiempo en el que llegaran clientes por hoy")
                        print("")
                        break
                    
                cant_personas_ll = j
                cant_personas_acumulado += cant_personas_ll       
    
                for k in range(cant_personas_ll):
                    ordenarCola_gt(cola_g, 'g')
                    ordenarCola_gt(cola_t, 't')
                    ordenarCola_e(cola_e, 'e')   
                    c += 1  
                         
                w = 0
                for u in range(cajas[0]):       
                    if cajas[1] > w:
                        movimiento1Cajas(cola_g, cola_t, cola_e, 'g')            
                    
                    if cajas[2] + cajas[1] > w >= cajas[1]:
                        movimiento1Cajas(cola_t, cola_e, cola_g, 't')                                     
                    
                    if (cajas[3] + cajas[2] + cajas[1]) > w >= cajas[2] + cajas[1]:
                        movimiento1Cajas(cola_e, cola_t, cola_g, 'e')
                                                                                                                                 
                    w += 1
    
                aux = 0
                for u in range(cajas[0]):  
                    movimiento2Cajas(cola_t, cola_e)
                    movimiento2Cajas(cola_e, cola_g)
                    movimiento2Cajas(cola_t, cola_g)           
                    
                    if lista_cajas[aux][1] != '-':
                        if int(lista_cajas[aux][1][4]) == lista_tiempo[aux][1]:
                            x = lista_cajas[aux][1] ## Cliente que sale de la caja
                            lista_cajas[aux] = '-'
                            lista_tiempo[aux] = 0
                            pila_clientes.append(x) 
                            
                    if lista_cajas[aux][1] != '-':                    
                        lista_tiempo[aux] = lista_tiempo[aux][1] + 1
                    
                    salidaConsola(cajas[1], cajas[2], cajas[3], cola_g, cola_t, cola_e)
                    archivo = open('banco.out', 'a')
                    archivo.write(f'{lista_cajas[aux][0]} {lista_cajas[aux][1][0]}\n')                     
                          
                    aux += 1

                ultimaEscritura(cola_g)
                ultimaEscritura(cola_t)
                ultimaEscritura(cola_e)
                archivo.write('\n')
                if len(pila_clientes) == 0:
                    archivo.write(f'-')
                else:
                    pila = 0
                    for client in range(len(pila_clientes)):
                        archivo.write(f'{pila_clientes[pila][0]} ')
                        pila += 1            
                archivo.close()                     
                    
                i += 1                
                    
            else:   
                archivo = open('banco.out', 'w')                
                print(f'Usted se encuentra en el instante de tiempo {i}.')
                print("")                
    
                w = 0
                for u in range(cajas[0]):
                    if cajas[1] > w:
                        movimiento1Cajas(cola_g, cola_t, cola_e, 'g')            
                    
                    if cajas[2] + cajas[1] > w >= cajas[1]:
                        movimiento1Cajas(cola_t, cola_e, cola_g, 't')                                     
                    
                    if (cajas[3] + cajas[2] + cajas[1]) > w >= cajas[2] + cajas[1]:
                        movimiento1Cajas(cola_e, cola_t, cola_g, 'e')                                             
                                                                                
                    w += 1
                    
                m = 0    
                aux = 0
                for u in range(cajas[0]): 
                    movimiento2Cajas(cola_t, cola_e)
                    movimiento2Cajas(cola_e, cola_g)
                    movimiento2Cajas(cola_t, cola_g) 
                    
                    if lista_cajas[aux][1] != '-':
                        if int(lista_cajas[aux][1][4]) == lista_tiempo[aux][1]:
                            x = lista_cajas[aux][1] ## Cliente que sale de la caja
                            lista_cajas[aux] = '-'
                            lista_tiempo[aux] = 0
                            pila_clientes.append(x) 
                            
                    if lista_cajas[aux][1] != '-':                    
                        lista_tiempo[aux] = lista_tiempo[aux][1] + 1            
                            
                    salidaConsola(cajas[1], cajas[2], cajas[3], cola_g, cola_t, cola_e)
                    archivo = open('banco.out', 'a')
                    archivo.write(f'{lista_cajas[aux][0]} {lista_cajas[aux][1][0]}\n')                      
                            
                    aux += 1   
                                     
                    if lista_cajas[m][1] == '-':
                        m += 1
                        if m < cajas[0]:
                            pass
                        else:
                            print("")
                            print(f'La simulación ha finalizado en el instante de tiempo {i}, ya que no queda ningun cliente en las cajas')
                            print("")
                            op = 4
                            f = False
                            
                ultimaEscritura(cola_g)
                ultimaEscritura(cola_t)
                ultimaEscritura(cola_e)
                archivo.write('\n')
                if len(pila_clientes) == 0:
                    archivo.write(f'-')
                else:
                    pila = 0
                    for client in range(len(pila_clientes)):
                        archivo.write(f'{pila_clientes[pila][0]} ')
                        pila += 1            
                archivo.close()
                                              
                i += 1        
        
    elif op == 4:
        salir()
    
    else:
        print("")
        print('Has ingresado un valor fuera de rango. Por favor intentalo nuevamente')  


        



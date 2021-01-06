# -*- coding: utf-8 -*-
"""
Created on Tue Jan  5 20:48:43 2021

@author: dnlmo
"""

import tsplib95
import matplotlib.pyplot as plt
import random
import time
import copy
import numpy as np

import csv

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

# Lista circular ocupada en el crossover DPX, ya que ahorra varias condiciones que deberian hacerse con una lista normal.
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class CircularLinkedList:
    def __init__(self, head):
        self.head = head
        self.head.next = head

    def length(self):
        current = self.head.next
        count = 1
        if self.head is not None:
            while current != self.head:
                count += 1
                current = current.next
            return count
        else:
            return 0

    def search(self, position, prev=False):
        # Busca el elemento en la posición dada. Si position es negativo busca el último elemento
        # El argumento prev sirve para devolver en una lista tanto el nodo buscado como el anterior.
        if position == 0:
            if prev is False:
                return self.head
            else:
                return [self.search(-1), self.head]
        elif position < 0:
            current = self.head
            while current.next !=self.head:
                previous = current
                current = current.next
            return current if prev is False else [previous, current]
        else:
            k = 1
            current = self.head
            while k < position and current.next !=self.head:
                k += 1
                previous = current
                current = current.next
            return current if prev is False else [previous, current]

    def insert(self, node, position):
        # Inserta el nodo después de la posición indicada. Si se indica una posición negativa, o mayor que
        # el tamaño de la lista, se inserta al final
        if position == 0:
            last_element = self.search(-1)
            last_element.next = node
            node.next = self.head
            self.head = node
        elif position < 0:
            last_element = self.search(-1)
            last_element.next = node
            node.next = self.head
        else:
            element = self.search(position)
            node.next = element.next
            element.next = node

    def delete(self, position):
        # Para posiciones con valor negativo, borra el último nodo
        if position > 1:
            previous = self.search(position-1)
        elif position < 0:
            previous = self.search(-1, True)[0]
        else:
            previous = self.search(-1)
            self.head = previous.next.next
        previous.next = previous.next.next
        
    # Permite acceder a los indices de la lista circular 
    def __getitem__(self, indice):
        if indice >= 0:
            actual = self.head
            for i in range(indice):
                actual = actual.next       
            return actual.data

###### FUNCIONES GENERALES #######

def distancia(i, j):
    u = i + tipo_var, j + tipo_var
    return problem.get_weight(*u)

# Costo de la ruta
def costoTotal(ciudad):
    suma = 0
    i = 0
    while i < len(ciudad) - 1:
        # print(ciudad[i], ciudad[i +1])
        suma += distancia(ciudad[i], ciudad[i + 1])
        i += 1
    suma += distancia(ciudad[-1], ciudad[0])
    return suma

# heurística del vecino más cercano
def vecinoMasCercano(n, desde): 
    actual = desde         #se manda la ciudad que queremos que parta, ciudad de 'origen' 
    ciudad = []
    ciudad.append(desde)
    seleccionada = [False] * n
    seleccionada[actual] = True   #se crea una lista con las ciudades ya visitadas para no pasar por ellas nuevamente

    while len(ciudad) < n:  #aca se crean las conexiones. se agrega la ciudad que tenga la menor distancia con la actual y asi susecivamente
        min = 9999999
        for candidata in range(n):
            if seleccionada[candidata] == False and candidata != actual:
                costo = distancia(actual, candidata)
                if costo < min:
                    min = costo
                    siguiente = candidata

        ciudad.append(siguiente)
        seleccionada[siguiente] = True
        actual = siguiente
    #ciudad.append(desde) se agregaria en caso de no considerar en el costo ir de la ultima a la primera
    return ciudad   #finalmente se retorna la lista de ciudades

def nueva_distancia_propuesta(x1,x2,y1,y2,z1,z2,ciudad): #calcula la diferencia entre una nueva ruta y la actual. Se llama desde OrOpt y OrOpt_m
    actual = distancia(ciudad[x1], ciudad[x2]) + distancia(ciudad[y1], ciudad[y2]) + distancia(ciudad[z1], ciudad[z2]) 
    nueva = distancia(ciudad[x1], ciudad[y2]) + distancia(ciudad[x2], ciudad[z1]) + distancia(ciudad[y1], ciudad[z2])
    resultado = actual - nueva
    return resultado

#OR-opt es un cambio de 3 aristas que abarca casi las mismas posibilidades del 3 Opt pero con un costo computacional de 2 Opt. Esto se debe a que se consideran dos aristas muy cernanas o adayacentes
#para evitar hacer un ciclo for adicinal de k.Este codigo es una mofidicacion de la siguiente fuente : http://tsp-basics.blogspot.com/2017/03/or-opt.html ; https://www.tandfonline.com/doi/abs/10.1057/palgrave.jors.2602160 ; https://blogue.hec.ca/permanent/babin/pub/Babi05a.pdf
def OrOpt(ciudad):
    n = len(ciudad)
    min_change= 0
    iterar= False
    for adyacencia in range(3,1,-1): #esa es la distancia o adayancencia entre los vertices i y j
        for i in range(n - adyacencia - 1): 
            x1= i
            x2= i+1
            
            j = i + adyacencia
            y1 = j
            y2= j+1
            interar= True
            for k in range(j+1,n-1):
                z1= k
                z2= k+1
                evaluar = nueva_distancia_propuesta(x1,x2,y1,y2,z1,z2,ciudad) #se llama al metodo para calcular la nueva distancia
                if evaluar > min_change:
                    min_change = evaluar
                    ciudad[x1 + 1 : y1 + 1] = ciudad[x1 + 1 : y1 + 1][::-1]
            
                    ciudad[y1 + 1 : z1 + 1] =ciudad[y1 + 1 : z1 + 1][::-1]
            
                    ciudad[x1+ 1 : z1 + 1] = ciudad[x1+ 1 : z1 + 1][::-1]
                    iterar= False
                    
                    break

#Es la misma logica del OrOpt pero con la diferencia de que con cualquier cambio sale del ciclo y no necesariamente busca el mejor cambio.Esto reduce el tiempo computacional bastante
def OrOpt_m(ciudad):
    n = len(ciudad)
    min_change= 0
    iterar= False
    for adyacencia in range(3,1,-1): 
        for i in range(n - adyacencia - 1): 
            x1= i
            x2= i+1
            
            j = i + adyacencia
            y1 = j
            y2= j+1
            interar= True
            for k in range(j+1,n-1):
                z1= k
                z2= k+1
                evaluar = nueva_distancia_propuesta(x1,x2,y1,y2,z1,z2,ciudad)
                if evaluar > min_change:
                    min_change = evaluar
                    ciudad[x1 + 1 : y1 + 1] = ciudad[x1 + 1 : y1 + 1][::-1]
            
                    ciudad[y1 + 1 : z1 + 1] =ciudad[y1 + 1 : z1 + 1][::-1]
            
                    ciudad[x1+ 1 : z1 + 1] = ciudad[x1+ 1 : z1 + 1][::-1]
                    iterar= False
                    
                    break
            break #se dejara debido al costo compuracional. Sin este break los resultados mejoran pero el tiempo sube exponencialmente
                                                      
# Búsqueda local 3-opt. Cambia 3 aritas evaluando entre 8 posibles combinaciones la que ofrezca la mejorar mas significativa. Su costo computacional es muy alto lo que provoca que para algunas problemas sea poco practica.
#Este codigo es una mofidicacion de la siguiente fuente :http://matejgazda.com/tsp-algorithms-2-opt-3-opt-in-python/ ; https://github.com/BraveDistribution/pytsp/blob/master/pytsp/k_opt_tsp.py
def TresOpt(ciudad):
    n = len(ciudad)
    flag = True
    contar = 0
    min_change=0
    for i in range(n - 2):
        for j in range(i + 1, n - 1):
            for k in range ( j + 1, n - 1):
                
                lista_1= []
                nuevoCosto_1 = 0 #sin cambio de nada ciudades
                lista_1.append(nuevoCosto_1)
                nuevoCosto_2 = distancia(ciudad[i], ciudad[i + 1]) + distancia(ciudad[k], ciudad[k + 1]) - (distancia(ciudad[i], ciudad[k]) + distancia(ciudad[i + 1], ciudad[k + 1]))
                lista_1.append(nuevoCosto_2)
                nuevoCosto_3 = distancia(ciudad[j], ciudad[j + 1]) + distancia(ciudad[k], ciudad[k + 1]) - (distancia(ciudad[j], ciudad[k]) + distancia(ciudad[j + 1], ciudad[k + 1]))
                lista_1.append(nuevoCosto_3)
                nuevoCosto_4 = distancia(ciudad[i], ciudad[i + 1]) + distancia(ciudad[j], ciudad[j + 1]) + distancia(ciudad[k], ciudad[k + 1]) - (distancia(ciudad[i], ciudad[j + 1]) + distancia(ciudad[i + 1], ciudad[k + 1]) + distancia(ciudad[j], ciudad[k]))
                lista_1.append(nuevoCosto_4)
                nuevoCosto_5 = distancia(ciudad[i], ciudad[i + 1]) + distancia(ciudad[j], ciudad[j + 1]) + distancia(ciudad[k], ciudad[k + 1]) - (distancia(ciudad[j], ciudad[k + 1]) + distancia(ciudad[i + 1], ciudad[j + 1]) + distancia(ciudad[i], ciudad[k]))
                lista_1.append(nuevoCosto_5)
                nuevoCosto_6 = distancia(ciudad[i], ciudad[i + 1]) + distancia(ciudad[j], ciudad[j + 1]) - (distancia(ciudad[i], ciudad[j]) + distancia(ciudad[i + 1], ciudad[j + 1]))
                lista_1.append(nuevoCosto_6)
                nuevoCosto_7 = distancia(ciudad[i], ciudad[i + 1]) + distancia(ciudad[j], ciudad[j + 1]) + distancia(ciudad[k], ciudad[k + 1]) - (distancia(ciudad[i + 1], ciudad[k]) + distancia(ciudad[j + 1], ciudad[k + 1]) + distancia(ciudad[i], ciudad[j]))
                lista_1.append(nuevoCosto_7)
                nuevoCosto_8 = distancia(ciudad[i], ciudad[i + 1]) + distancia(ciudad[j], ciudad[j + 1]) + distancia(ciudad[k], ciudad[k + 1]) - (distancia(ciudad[i], ciudad[j + 1]) + distancia(ciudad[j], ciudad[k + 1]) + distancia(ciudad[i + 1], ciudad[k]))
                lista_1.append(nuevoCosto_8)
                # min_i, min_j, min_k = i, j, k
                nuevoCosto=max(lista_1)
                
                if nuevoCosto > min_change: #si el calculo es mejor se acepta, sino no se acepta
                    min_change = nuevoCosto
                    min_i, min_j, min_k = i, j, k 
                    contar += 1
                    if contar == 1:
                        flag = False
            if flag == False:
                break

    if contar > 0: #si se enconetro una solucion mejor contar se igualaba a 1, entonces se acepta el cambio y se realiza
        primer_seg = ciudad[min_i + 1 : min_k + 1] 
        segundo_seg = ciudad[min_j + 1 : min_k + 1]
        tercer_seg = ciudad[min_i + 1 : min_j + 1]
        #Case 2
        if nuevoCosto_2 == nuevoCosto:
            ciudad[min_i + 1 : min_k + 1] = reversed(primer_seg) 
        #Case 3
        elif nuevoCosto_3 == nuevoCosto:
            ciudad[min_j + 1 : min_k + 1] =reversed(segundo_seg)
        #Case 4
        elif nuevoCosto_4 == nuevoCosto :
            ciudad[min_i + 1 : min_k + 1] = reversed(primer_seg)
                    
            ciudad[min_j + 1 : min_k + 1] =reversed(segundo_seg)
        #Case 5
        elif nuevoCosto_5 == nuevoCosto :
            ciudad[min_i + 1 : min_k + 1] = reversed(primer_seg)
        
            ciudad[min_i + 1 : min_j + 1] = reversed(tercer_seg)   
        #Case 6
        elif nuevoCosto_6 == nuevoCosto:
            ciudad[min_i + 1 : min_j + 1] = reversed(tercer_seg)   
        #Case 7
        elif nuevoCosto_7 == nuevoCosto:
            ciudad[min_i + 1 : min_j + 1] = reversed(tercer_seg)   
                    
            ciudad[min_j + 1 : min_k + 1] =reversed(segundo_seg)
        #Case 8
        elif nuevoCosto_8 == nuevoCosto:
            ciudad[min_i + 1 : min_j + 1] = reversed(tercer_seg)
            
            ciudad[min_j + 1 : min_k + 1] =reversed(segundo_seg)
            
            ciudad[min_i + 1 : min_k + 1] = reversed(primer_seg)
  
# perturbación: se escogen dos ciudades aleatorias y las intercambia
def perturbation(ciudad):
    i = 0
    j = 0
    n = len(ciudad)
    while i == j:
        i = random.randint(0, n - 1)
        j = random.randint(0, n - 1)

    # intercambio
    temp = ciudad[i]
    ciudad[i] = ciudad[j]
    ciudad[j] = temp

# Perturbacion que selecciona a dos ciudades dentro de un individuo e invierte los valores de estas    
def perturbation2(ciudad):
    i = 0
    j = 0
    n = len(ciudad)
    while i >= j:
        i = random.randint(0, n - 1)
        j = random.randint(0, n - 1)
    ciudad[i : j] = ciudad[i : j][::-1]

# Perturbacion que cambia una ciudad con otra
def perturbation3(ciudad):
    j = 0
    n = len(ciudad)
    i = random.randint(0, n - 1)

    if i == n - 1:
        j = 0
    else:
        j = i + 1
    # intercambio
    temp = ciudad[i]
    ciudad[i] = ciudad[j]
    ciudad[j] = temp

#Movimiento aleatorio de doble puente, divide un vector en varias partes y luego los reordena de forma aleatoria
#Fuente: https://github.com/cfld/simple_tsp/blob/master/simple_tsp/perturb.py
def perturbation4(ciudad): 
    #(https://github.com/cfld/simple_tsp/blob/master/simple_tsp/perturb.py)
    n_nodos = len(ciudad)  
    
    cortar = 1 + np.random.choice(n_nodos - 1, 4, replace=False) 
    cortar = np.sort(cortar)
    
    zero  = ciudad[:cortar[0]]
    one   = ciudad[cortar[0]:cortar[1]]
    two   = ciudad[cortar[1]:cortar[2]]
    three = ciudad[cortar[2]:cortar[3]]
    four  = ciudad[cortar[3]:]
    new_route = np.hstack([zero, three, two, one, four])
    return random.shuffle(new_route)


###### FUNCIONES PROPIAS DEL ILS ######

# Búsqueda local 2-opt
def DosOpt(ciudad):
    n = len(ciudad)
    flag = True
    contar = 0
    for i in range(n - 2):
        for j in range(i + 1, n - 1):
            nuevoCosto = distancia(ciudad[i], ciudad[j]) + distancia(ciudad[i + 1], ciudad[j + 1]) - distancia(ciudad[i], ciudad[i + 1]) - distancia(ciudad[j], ciudad[j + 1])
            if nuevoCosto < 0: #si el calculo es mejor se acepta, sino no se acepta
                min_i, min_j = i, j
                contar += 1
                if contar == 1:
                    flag = False

        if flag == False:
            break
    if contar > 0: #si se enconetro una solucion mejor contar se igualaba a 1, entonces se acepta el cambio y se realiza
        ciudad[min_i + 1 : min_j + 1] = ciudad[min_i + 1 : min_j + 1][::-1] #se invierten rutas
 
#Combina tres tipos de busqueda local. Se elige en base a un valor aleatorio
def s_mixto(ciudad):
    x= random.randint(0,1)
    if x < 0.3:
        DosOpt(ciudad)
    elif 0.3 < x <= 0.9:
        OrOpt(ciudad)
    else:
        TresOpt(ciudad)
        
def per_mixto(ciudad):
    x= random.randint(0,1)
    if x < 0.5:
        perturbation2(ciudad)
    elif 0.5 < x < 0.8:
        perturbation3(ciudad)
    else:
        perturbation(ciudad)
  
#Metodo para elegir la mejor ciudad como punto de partida. Se considera que un TSP es un ciclo, entonces independiente de la ciudad que se elija para NN se puede partir de donde uno desee.
def mejor_vecino(n):
    mejor = 9999999999
    for l in range(n): #aplicamos esto dado que dependiendo de que ciudad comience el resultado tambien cambia
        s_1 = vecinoMasCercano(n,l)
        costo = costoTotal(s_1)
        if costo < mejor:
            mejor=costo
            partida = s_1
    return partida
    

def ILS(ciudad,semilla): #Metahuristica iterated local search.
    random.seed(semilla) #se define una semilla random 
    inicioTiempo = time.time() #tiempo inicial
    n = len(ciudad)
    
    # Solución inicial
    s = mejor_vecino(n) #punto de partida desde mejor resultado de NN

    DosOpt(s)
    OrOpt_m(s)
    #OrOpt_m(s)    entrega mejores resultados pero su tiempo de ejecucion es el doble que con la version modificada
    #TresOpt(s)   #es la primera busqueda local (3-opt)

    s_mejor = s[:]
    costoMejor = costoTotal(s_mejor)

    print("inicial %d" % costoMejor)
    iterMax = 1000
    for iter in range(iterMax):
        # Perturbación
        #s = perturbation4(s)
        #perturbation3(s)
        perturbation2(s)
        #per_mixto(s)
        
        # Búsqueda local
        #s_mixto(s)
        # TresOpt(s)
        #OrOpt(s)
        DosOpt(s)
        OrOpt_m(s)
        costo_candidato = costoTotal(s)
        # Actualizar mejor solución
        if costoMejor > costo_candidato:
            s_mejor = s[:]
            costoMejor = costo_candidato
            print("%d\t%d" % (iter, costoMejor))

        # criterio de aceptación de la solución actual
        if abs(costoMejor - costo_candidato) / costoMejor > 0.05:
            s = s_mejor[:]
        if costo_optimo == costoMejor: #si encuentra el optimo lo saca del ciclo
            break

    finTiempo = time.time()
    tiempo = finTiempo - inicioTiempo
    
    global tiempo_total
    tiempo_total= tiempo_total + tiempo #para obtener el tiempo total de ejecucion
    global costo_total
    costo_total = costo_total + costoMejor # para obtener el costo total 
    global costo_minimo
    if costo_minimo > costoMejor:
        costo_minimo = costoMejor
    global error_total
    error_instancia = ((costoMejor - costo_optimo)/costo_optimo)*100
    error_total = error_total + error_instancia
    global cantidad_ciudades
    cantidad_ciudades = n 
    
 
    print("Costo  : %d" % costoMejor)
    print("Tiempo : %f" % tiempo)
    print(s_mejor)

def ILS1(ciudad,semilla):
    random.seed(semilla) #se define una semilla random 
    inicioTiempo = time.time() #tiempo inicial
    n = len(ciudad) 
    # Solución inicial
    s = mejor_vecino(n) #punto de partida desde mejor resultado de NN
    DosOpt(s)
    OrOpt_m(s)
    #OrOpt_m(s)    entrega mejores resultados pero su tiempo de ejecucion es el doble que con la version modificada
    #TresOpt(s)   #es la primera busqueda local (3-opt)
    s_mejor = s[:]
    costoMejor = costoTotal(s_mejor)
    print("inicial %d" % costoMejor)
    iterMax = 1000
    for iter in range(iterMax):
        # Perturbación
        #s = perturbation4(s)
        #perturbation2(s)
        perturbation3(s)
        #per_mixto(s)
        
        # Búsqueda local
        #s_mixto(s)
        # TresOpt(s)
        #OrOpt(s)
        DosOpt(s)
        OrOpt_m(s)
        costo_candidato = costoTotal(s)
        # Actualizar mejor solución
        if costoMejor > costo_candidato:
            s_mejor = s[:]
            costoMejor = costo_candidato
            print("%d\t%d" % (iter, costoMejor))

        if abs(costoMejor - costo_candidato) / costoMejor > 0.05:
            s = s_mejor[:]
        if costo_optimo == costoMejor: #si encuentra el optimo lo saca del ciclo
            break

    finTiempo = time.time()
    tiempo = finTiempo - inicioTiempo
    
    global tiempo_total
    tiempo_total= tiempo_total + tiempo #para obtener el tiempo total de ejecucion
    global costo_total
    costo_total = costo_total + costoMejor # para obtener el costo total 
    global costo_minimo
    if costo_minimo > costoMejor:
        costo_minimo = costoMejor
    global error_total
    error_instancia = ((costoMejor - costo_optimo)/costo_optimo)*100
    error_total = error_total + error_instancia
    global cantidad_ciudades
    cantidad_ciudades = n 
    
 
    print("Costo  : %d" % costoMejor)
    print("Tiempo : %f" % tiempo)
    print(s_mejor)

    # if graficar_ruta:
    #     graficar(coord_x, coord_y, s_mejor)

###### FUNCIONES PROPIAS DEL GA ######
        
# Costo de la ruta
def costoTotalGA(ciudad):
    suma = 0
    i = 0
    while i < len(ciudad) - 1:
        suma += distancia(ciudad[i], ciudad[i + 1]) # Para conectar todas las ciudades
        i += 1
    suma += distancia(ciudad[-1], ciudad[0]) # Para conectar la primera ciudad con la ultima
    return suma,

# Heurística del vecino más cercano
def vecinoMasCercanoGA(n):
    desde = random.randrange(0, n)
    actual = desde
    ciudad = []
    ciudad.append(desde)
    seleccionada = [False] * n
    seleccionada[actual] = True
    while len(ciudad) < n:
        minimo = 9999999
        for candidata in range(n):
            if seleccionada[candidata] == False and candidata != actual:
                costo = distancia(actual, candidata)
                if costo < minimo:
                    minimo = costo
                    siguiente = candidata
        ciudad.append(siguiente)
        seleccionada[siguiente] = True
        actual = siguiente
    return ciudad        
        
# Busqueda local que utiliza un cambio de dos aristas para buscar un mejor resultado
def DosOptGA(ciudad):
    actual = 0
    n = len(ciudad)
    flag = True
    contar = 0
    k = random.randint(0, len(ciudad) - 1)
    ciudad = ciudad[k:] + ciudad[:k]
    for i in range(n - 2):
        for j in range(i + 1, n - 1):
            nuevoCosto = distancia(ciudad[i], ciudad[j]) + distancia(ciudad[i + 1], ciudad[j + 1]) - distancia(ciudad[i], ciudad[i + 1]) - distancia(ciudad[j], ciudad[j + 1])
            if nuevoCosto < actual:
                actual = nuevoCosto
                min_i, min_j = i, j
                # Al primer cambio se sale
                contar += 1
                if contar == 1 :
                    flag = False
        if flag == False:
            break
    # Actualiza la subruta se encontró
    if actual < 0:
        ciudad[min_i + 1 : min_j + 1] = ciudad[min_i + 1 : min_j + 1][::-1]
    return ciudad      

# Cruzamiento DPX basado en: "A 2opt-DPX Genetic Local Search for Solving Symmetric Traveling Salesman Problem"       
def crossoverDPX_AG(padre1, padre2):
    parent1 = CircularLinkedList(Node(padre1[0]))
    for i in range(1,len(padre1)):
        parent1.insert(Node(padre1[i]), i)
    
    parent2 = CircularLinkedList(Node(padre2[0]))  
    for i in range(1,len(padre2)):
        parent2.insert(Node(padre2[i]), i)

    fragments = []
    index1 = 0
    bandera = False
    for i in range(parent1.length()):
        if index1 == i:
            aux = []
            place = parent1[i] 
            aux.append(place) 
            for index2 in range(parent2.length()): # 
                #print('1')
                if place == parent2[index2]:
                    #print('2')
                    sig = 1
                    
                    if len(fragments) != 0 and fragments[0][0] == parent1[index1+sig]:
                     #   print('3')
                        bandera = True
                        
                    if parent1[index1 + sig] == parent2[index2 + sig] and bandera == False:
                      #  print('4')
                        aux.append(parent1[index1 + sig])                       
                        sig += 1      
                        
                        if len(fragments) != 0 and fragments[0][0] == parent1[index1+sig]:
                            bandera = True
                         
                        c = 1 
                        while parent1[index1 + sig] == parent2[index2 + sig] and bandera == False:
                            #print(f'while1')
                            aux.append(parent1[index1 + sig])            
                            sig += 1
                            c += 1
                            #print(f'1. parent1: {parent1.length()} c: {c}')
                            if c == parent1.length():
                                bandera = True
                            
                            if len(fragments) != 0 and fragments[0][0] == parent1[index1+sig]:
                                bandera = True
    
                        index1 += sig
                        
                    elif parent1[index1 + sig] == parent2[index2 - sig] and bandera == False:
                        aux.append(parent1[index1 + sig]) 
                        sig += 1
                        
                        if len(fragments) != 0 and fragments[0][0] == parent1[index1+sig]:
                            bandera = True                        
                        
                        c = 1
                        while parent1[index1 + sig] == parent2[index2 - sig] and bandera == False:
                            #print(f'while2')
                            aux.append(parent1[index1 + sig])
                            sig += 1
                            c += 1
                            
                            #print(f'2. parent1: {parent1.length()}')
                            if c == parent1.length():
                                bandera = True
                            
                            if len(fragments) != 0 and fragments[0][0] == parent1[index1+sig]:
                                bandera = True                            

                        index1 += sig

                    else:
                        index1 += sig     

                    fragments.append(aux)
    
    if fragments[0][0] == fragments[0][-1]:
        return
    else:
        #print(f'fragments: {fragments}')
        offspring = greedyDPX(fragments)
        #print(offspring)
        
        padre1[:] = offspring
        return padre1,

# Se utiliza la heuristica del vecino mas cercano para reconstruir los fragmentos iguales entre los dos padres, para asi crear al hijo.
def greedyDPX(fragments):
    costo_p1 = 10000000000
    costo_p2 = 10000000000
    costo_u1 = 10000000000
    costo_u2 = 10000000000
    segundo = 0
    n = len(fragments)
    starting_node = random.randint(0, n - 1)
    actual = starting_node
    offspring = []
    frag_aux = [] # Esta lista crecera hasta el mismo largo de fragments
    seleccionada = [False] * n
    seleccionada[starting_node] = True # Lista donde se van guardando las ciudades que ya se visitaron para hacer condiciones
    
    for i in range(len(fragments[starting_node])):
        offspring.append(fragments[starting_node][i])

    frag_aux.append(fragments[starting_node]) 
    
    while len(frag_aux) < n:
        minimo = 9999999
        primero = offspring[0]
        ultimo = offspring[-1]
    
        if primero == ultimo: # Evaluo el primer elemento que ingreso a la lista offspring
            for candidata in range(n):
                if seleccionada[candidata] == False and candidata != actual:
                    
                    if len(fragments[candidata]) == 1:
                        costo_p1 = distancia(primero, fragments[candidata][0])
                        
                        costo = costo_p1
                    
                    else: 
                        costo_p1 = distancia(primero, fragments[candidata][0])
                        costo_p2 = distancia(primero, fragments[candidata][-1])
                    
                        costo = min(costo_p1, costo_p2)
                    
                    if costo < minimo:
                        minimo = costo
                        siguiente = candidata
                        costop1_aux = costo_p1
                        costop2_aux = costo_p2
            
            if minimo == costop2_aux:
                fragments[siguiente] = fragments[siguiente][::-1]            
                        
            for i in range(len(fragments[siguiente])):
                offspring.append(fragments[siguiente][i])
                
            frag_aux.append(fragments[siguiente])
            
            seleccionada[siguiente] = True
            actual = siguiente
            
        else: # Para el caso de que offspring tuviera un largo mayor que 1
            for candidata in range(n):
                if seleccionada[candidata] == False and candidata != actual:
                    
                    if len(fragments[candidata]) == 1: 
                        costo_p1 = distancia(primero, fragments[candidata][0])
                        costo_u1 = distancia(ultimo, fragments[candidata][0])
                        
                        costo = min(costo_p1, costo_u1)
                        
                    else:            
                        costo_p1 = distancia(primero, fragments[candidata][0])
                        costo_p2 = distancia(primero, fragments[candidata][-1])
                        costo_u1 = distancia(ultimo, fragments[candidata][0])
                        costo_u2 = distancia(ultimo, fragments[candidata][-1])
                        
                        costo = min(costo_p1, costo_p2, costo_u1, costo_u2)
                    
                    if costo < minimo:
                        minimo = costo
                        siguiente = candidata
                        costop1_aux = costo_p1
                        costop2_aux = costo_p2
                        costou1_aux = costo_u1
                        costou2_aux = costo_u2 
            
            # Condiciones para conectar los elementos de la listas y tengan consistencia
            if minimo == costop1_aux:
                offspring = offspring[::-1]  

            elif minimo == costop2_aux:
                offspring = offspring[::-1] 
                fragments[siguiente] = fragments[siguiente][::-1]  
                
            elif minimo == costou2_aux:
                fragments[siguiente] = fragments[siguiente][::-1]  
                
            for i in range(len(fragments[siguiente])):
                offspring.append(fragments[siguiente][i])
                
            frag_aux.append(fragments[siguiente])
            
            seleccionada[siguiente] = True
            actual = siguiente 
    return offspring

# Funcion ocupada para buscar la mejor combinacion del non-sequential 3-change que se hizo en la mutación
def DosOptGAChange(ciudad,min_i,min_j,min_k):
    i = min_i
    j = min_j
    k = min_k
    opcion_1 = distancia(ciudad[j], ciudad[j+1]) + distancia(ciudad[k], ciudad[k+1]) - (distancia(ciudad[j+1], ciudad[k+1]) + distancia(ciudad[j], ciudad[k])) #i no cambia con nadie
    opcion_2 = distancia(ciudad[i], ciudad[i+1]) + distancia(ciudad[k], ciudad[k+1]) - (distancia(ciudad[i+1], ciudad[k+1]) + distancia(ciudad[i], ciudad[k])) #j no cambia con nadie
    opcion_3 = distancia(ciudad[i], ciudad[i+1]) + distancia(ciudad[j], ciudad[j+1]) - ( distancia(ciudad[i+1], ciudad[j+1]) + distancia(ciudad[i], ciudad[j]))  #k no cambia con nadie
    
    mejor=max(opcion_1,opcion_2,opcion_3)

    if mejor == opcion_1:
        ciudad[j + 1 : k + 1] = ciudad[j + 1 : k + 1][::-1]
    elif mejor == opcion_2:
        ciudad[i + 1 : k + 1] = ciudad[i + 1 : k + 1][::-1]
    elif mejor == opcion_3:
        ciudad[i + 1 : j + 1] = ciudad[i + 1 : j + 1][::-1]      
    return ciudad

# Funcion ocupada para la mutacion, la cual aplica 3 cambios no secuenciales
def TresChange(ciudad):
    n = len(ciudad)
    var=0
    i = random.randint(0,round(n/3)-1)
    j = random.randint(round(n/3),round(2*n/3)-1)
    k = random.randint(round(2*n/3), n-2)   
    min_i, min_j, min_k = i, j, k

    ciudad[i + 1 : j + 1] = ciudad[i + 1 : j + 1][::-1]
    ciudad[j + 1 : k + 1] =ciudad[j + 1 : k + 1][::-1]              
    ciudad[i + 1 : k + 1] = ciudad[i + 1 : k + 1][::-1]
    
    ciudad_final = DosOptGAChange(ciudad,min_i,min_j,min_k) 
    return ciudad_final

# Mutacion implementada en: "A 2opt-DPX Genetic Local Search for Solving Symmetric Traveling Salesman Problem"
  # Esta consiste en tres cambios no secuenciales (Funcion TresChange) a los que luego se les aplica un 2-opt (Funcion DosOptGAChange).
def mutation(padre1):
    offspring = TresChange(padre1)
    return offspring,    

# Conjunto de mutaciones a ocupar por probabilidades en el algoritmo genetico
def mutSetAG(ciudad):
    value = random.uniform(0, 1)
    if value < 0.7:
        perturbation3(ciudad)
    else:
        perturbation2(ciudad)
    return ciudad,

def GA2_AG(ciudad, semilla):
    n = len(ciudad)
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,)) 
    creator.create("Individual", list, typecode='i', fitness=creator.FitnessMin) 
    toolbox = base.Toolbox()

    # Attribute generator
    toolbox.register("indices", vecinoMasCercanoGA, n) 
    print(toolbox.indices()) 

    # Structure initializers
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.indices) 
    toolbox.register("population", tools.initRepeat, list, toolbox.individual) 
    toolbox.register("select", tools.selTournament, tournsize=2)
    toolbox.register("mate", crossoverDPX_AG)
    toolbox.register("mutate", mutSetAG)
    toolbox.register("evaluate", costoTotalGA)

    random.seed(semilla)
    pop = toolbox.population(n=100) 
    hof = tools.HallOfFame(1)
    
    stats = tools.Statistics(lambda ind: ind.fitness.values) 
    stats.register("avg", np.mean)
    stats.register("std", np.std)
    stats.register("min", np.min)
    stats.register("max", np.max)
    log = tools.Logbook() 
    log.header = "gen", "evals", "std", "min", "avg", "max"
    
    #Probabilidad de cruce y mutación
    CXPB, MUTPB = 0.9, 0.2
    
    print("Start of evolution")
    inicioTiempo = time.time()
    
    #for i in pop:
     #   DosOpt(i)
    
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit 
    print("Evaluated %i individuals" % len(pop))
    
    g = 0
    padres = []
    lista_soluciones = []
    lista_costos = []
    iterMax = 250

    record = stats.compile(pop) 
    log.record(gen=g, evals=len(pop), **record)
    print(log[-1]["gen"], log[-1]["avg"], log[-1]["min"]) 

    # Algoritmo genetico
    while g < iterMax:
        hijos = []
        g = g + 1
        #print("-- Generation %i --" % g)
        
        # Selección
        offspring = toolbox.select(pop, len(pop)) 

        padres[:] = offspring

        # Cruzamiento
        offspring = list(map(toolbox.clone, offspring))
        for child1, child2 in zip(offspring[::2], offspring[1::2]): 
            if random.random() < CXPB and child1 != child2:
                a = toolbox.mate(child1, child2) # Tupla de un individuo 
                if a == None:
                    pass
                else:
                    del child1.fitness.values 
                    del child2.fitness.values
                    child1_aux = copy.deepcopy(child1)
                    hijos.append(child1_aux)
                       
        # Mutación
        i = 0
        for mutant in offspring:
            if random.random() < MUTPB:
                toolbox.mutate(mutant)  # Tupla de un individuo 
                #DosOptGA(mutant)
                del mutant.fitness.values
                mutant_aux = copy.deepcopy(mutant)
                hijos.append(mutant_aux)

        invalid_ind = [ind for ind in hijos if not ind.fitness.valid] 
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit 

        # Reemplazamiento
            # Escoge a los mejores padres para agregarlo a la lista de hijos, hasta que el tamaño de la poblacion sea la inicial
        largo = len(padres)
        while len(hijos) < largo:  
            menor = padres[0].fitness.values
            indice_menor = 0
            for i in range(len(padres)):
                if padres[i].fitness.values < menor:
                    menor = padres[i].fitness.values
                    indice_menor = i
            hijos.append(padres[indice_menor])
            padres.pop(indice_menor)

        invalid_ind = [ind for ind in hijos if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit 

        pop[:] = hijos
  
        # Registro de estadisticas
        hof.update(hijos)
        record = stats.compile(hijos) 
        log.record(gen=g, evals=len(hijos), **record)
        print(log[-1]["gen"], log[-1]["avg"], log[-1]["min"])

        top = tools.selBest(hijos, k=1)
        lista_costos.append(int(log[-1]["min"]))
        lista_soluciones.append(top[0])
        
        if costo_optimo == min(lista_costos):
            break

    finTiempo = time.time()
    tiempo = finTiempo - inicioTiempo
    
    global tiempo_total
    tiempo_total= tiempo_total + tiempo # para obtener el tiempo total de ejecucion
    global costo_total
    costoMejor = min(lista_costos)
    costo_total = costo_total + costoMejor # para obtener el costo total 
    global costo_minimo
    if costo_minimo > costoMejor:
        costo_minimo = costoMejor
    global error_total
    error_instancia = ((costoMejor - costo_optimo)/costo_optimo)*100
    error_total = error_total + error_instancia
    global cantidad_ciudades
    cantidad_ciudades = n
    
    minimo, promedio = log.select("min", "avg")

    print('Costo  : %d' % min(lista_costos))
    print("Tiempo : %f" % tiempo)

###### FUNCIONES DE LA IMPLEMENTACION HIBRIDA ######

# Heuristica ILS_GA que construye la solucion inicial que se le entrega al GA
def ILS_GA(n):
    s = vecinoMasCercanoGA(n)

    DosOptGA(s)
    OrOpt(s)

    s_mejor = s[:]
    costoMejor = costoTotalGA(s_mejor)

    iterMax = 2
    for iter in range(iterMax):
        perturbation3(s)

        DosOptGA(s)
        OrOpt_m(s)
        costo_candidato = costoTotalGA(s)
        # Actualizar mejor solución
        if costoMejor[0] > costo_candidato[0]:
            s_mejor = s[:]
            costoMejor = costo_candidato

        if abs(costoMejor[0] - costo_candidato[0]) / costoMejor[0] > 0.05:
            s = s_mejor[:]
    return s
  
# Cruzamiento DPX basado en: "A 2opt-DPX Genetic Local Search for Solving Symmetric Traveling Salesman Problem"   
    # Este consiste en copiar el contenido del primer padre a la descendencia y eliminar todos los bordes que no son comunes con el otro padre. 
# La funcion fragmenta en trozos las ciudades que tienen las mismas conexiones en los dos padres obteniendo por ejemplo: [[1,6,7,8], [3,2,5], [4], [9, 10]] (Conexiones iguales entre padres)
# Luego, las partes resultantes del recorrido roto se vuelven a conectar empleando un procedimiento de reconexión codicioso (Funcion greedyDPX). 
def crossoverDPX(padre1, padre2):    
    # Crea dos listas circulares de los padres entregados
    parent1 = CircularLinkedList(Node(padre1[0]))
    for i in range(1,len(padre1)):
        parent1.insert(Node(padre1[i]), i)
    
    parent2 = CircularLinkedList(Node(padre2[0]))  
    for i in range(1,len(padre2)):
        parent2.insert(Node(padre2[i]), i)

    fragments = []
    index1 = 0
    bandera = False
    for i in range(parent1.length()):
        if index1 == i:
            aux = [] ## Lista de lista que se crea por trozos y va dentro de la lista fragments.
            place = parent1[i] 
            aux.append(place) 
            for index2 in range(parent2.length()): 
                # Ingresa cuando la ciudad i del padre 1 es igual a la ciudad j del padre 2
                if place == parent2[index2]:
                    sig = 1
                    
                    # Se utiliza para saber cuando se llega al valor final del padre1. Condicion evaluada en cada momento que se quiere agregar una nueva ciudad. 
                    if len(fragments) != 0 and fragments[0][0] == parent1[index1+sig]:
                        bandera = True
                    
                    ## Caso 1: Evalua la ciudad siguiente de ambos padres, si son iguales la agrega a aux 
                    if parent1[index1 + sig] == parent2[index2 + sig] and bandera == False:
                        aux.append(parent1[index1 + sig])                       
                        sig += 1      
                        
                        if len(fragments) != 0 and fragments[0][0] == parent1[index1+sig]:
                            bandera = True
                         
                        # Sigue revisando si la ciudad siguiente del padre 1 es igual a la ciudad siguiente del padre 2
                        c = 1 
                        while parent1[index1 + sig] == parent2[index2 + sig] and bandera == False:
                            aux.append(parent1[index1 + sig])            
                            sig += 1
                            c += 1
                            # Interruptor que permite salirse del while en caso de que ambas ciudades evaluadas eran iguales
                            if c == parent1.length():
                                bandera = True
                            
                            if len(fragments) != 0 and fragments[0][0] == parent1[index1+sig]:
                                bandera = True
    
                        index1 += sig
                        
                    ## Caso 2: Evalua la ciudad siguiente del padre 1 y ciudad anterior del padre 2, si son iguales la agrega a aux     
                    elif parent1[index1 + sig] == parent2[index2 - sig] and bandera == False:
                        aux.append(parent1[index1 + sig]) 
                        sig += 1
                        
                        if len(fragments) != 0 and fragments[0][0] == parent1[index1+sig]:
                            bandera = True                        
                        
                        c = 1
                        while parent1[index1 + sig] == parent2[index2 - sig] and bandera == False:
                            aux.append(parent1[index1 + sig])
                            sig += 1
                            c += 1
                            
                            if c == parent1.length():
                                bandera = True
                            
                            if len(fragments) != 0 and fragments[0][0] == parent1[index1+sig]:
                                bandera = True                            

                        index1 += sig

                    else:
                        index1 += sig     
                    
                    # Trozos de ciudades que tienen las mismas conexiones en los dos padres
                    fragments.append(aux)
    
    # En un caso especial, en el que se haya repetido la ciudad inicial con la final. Poco probable.
        # Implica no hacer el cruzamiento. Por eso al cruzamiento se le dara un porcentaje alto 
    if fragments[0][0] == fragments[0][-1]:
        return
        
    else:
        # Reconexion codiciosa de los fragmentos
        offspring = greedyDPX(fragments)    

        # Cambio aleatorio de uno de los dos padres por el hijo
        if random.random() < 0.5:
            padre1[:] = offspring
            return padre1,
        else:
            padre2[:] = offspring
            return padre2,
 
# Conjunto de mutaciones a ocupar por probabilidades en el algoritmo hibrido
def mutSet(ciudad):
    value = random.uniform(0, 1)
    if value < 0.4:
        perturbation2(ciudad)
    elif value >= 0.4 and value <= 9:
        mutation(ciudad)
    else:
        pertubation4(ciudad) 
    return ciudad,     

def GA2(ciudad, semilla):
    n = len(ciudad)
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, typecode='i', fitness=creator.FitnessMin)
    toolbox = base.Toolbox()

    # Attribute generator
    toolbox.register("indices", ILS_GA, n)
    print(toolbox.indices())

    # Structure initializers
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.indices)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    toolbox.register("select", tools.selTournament, tournsize=2)
    toolbox.register("mate", crossoverDPX)
    toolbox.register("mutate", mutSet)
    toolbox.register("evaluate", costoTotalGA)

    random.seed(semilla)
    pop = toolbox.population(n=80)
    hof = tools.HallOfFame(1)
    
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("std", np.std)
    stats.register("min", np.min)
    stats.register("max", np.max)
    log = tools.Logbook()
    log.header = "gen", "evals", "std", "min", "avg", "max"
    
    CXPB, MUTPB = 0.9, 0.2
    
    print("Start of evolution")
    inicioTiempo = time.time()

    #for i in pop:
     #   OrOpt(i)   
    
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit
    print("Evaluated %i individuals" % len(pop))
    
    g = 0
    padres = []
    lista_soluciones = []
    lista_costos = []
    iterMax = 250

    record = stats.compile(pop)
    log.record(gen=g, evals=len(pop), **record) 
    print(log[-1]["gen"], log[-1]["avg"], log[-1]["min"])

    # Algoritmo genetico
    while g < iterMax:
        hijos = []
        g = g + 1
        #print("-- Generation %i --" % g)
        
        # Selección
        offspring = toolbox.select(pop, len(pop))
        padres[:] = offspring
    
        # Cruzamiento
        offspring = list(map(toolbox.clone, offspring))
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CXPB and child1 != child2:
                a = toolbox.mate(child1, child2) # Tupla de un individuo 
                if a == None:
                    pass
                else:
                    del child1.fitness.values
                    del child2.fitness.values
                    child1_aux = copy.deepcopy(child1)
                    hijos.append(child1_aux)
        
        #for i in hijos:
          #  OrOpt(i) 
                       
        # Mutación
        i = 0
        for mutant in offspring:
            if random.random() < MUTPB:
                toolbox.mutate(mutant)  # Tupla de un individuo 
                if random.random() < 0.6:
                    OrOpt_m(mutant)
                    #DosOptGA(mutant)                        
                del mutant.fitness.values
                mutant_aux = copy.deepcopy(mutant)
                hijos.append(mutant_aux)

        invalid_ind = [ind for ind in hijos if not ind.fitness.valid] # Para reevaluar el fitness de la lista que contiene a los hijos y a la descendencia mutada
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # Reemplazamiento  
            # Escoge a los mejores padres para agregarlo a la descendencia, hasta que el tamaño de la poblacion sea la inicial
        largo = len(padres)
        while len(hijos) < largo:  
            menor = padres[0].fitness.values
            indice_menor = 0
            for i in range(len(padres)):
                if padres[i].fitness.values < menor:
                    menor = padres[i].fitness.values
                    indice_menor = i
            hijos.append(padres[indice_menor])
            padres.pop(indice_menor)    

        invalid_ind = [ind for ind in hijos if not ind.fitness.valid] # Se calcula el fitness de los padres que no tenian fitness y que fueron ingrgesados a la lista de hijos
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        pop[:] = hijos 
  
    # Registro de estadisticas
        hof.update(hijos) 
        record = stats.compile(hijos)
        log.record(gen=g, evals=len(hijos), **record)
        print(log[-1]["gen"], log[-1]["avg"], log[-1]["min"])

        top = tools.selBest(hijos, k=1)
        lista_costos.append(int(log[-1]["min"]))
        lista_soluciones.append(top[0]) 
    
        if costo_optimo == min(lista_costos):
            break

    finTiempo = time.time()
    tiempo = finTiempo - inicioTiempo
    
    global tiempo_total
    tiempo_total= tiempo_total + tiempo # para obtener el tiempo total de ejecucion
    global costo_total
    costoMejor = min(lista_costos)
    costo_total = costo_total + costoMejor # para obtener el costo total 
    global costo_minimo
    if costo_minimo > costoMejor:
        costo_minimo = costoMejor
    global error_total
    error_instancia = ((costoMejor - costo_optimo)/costo_optimo)*100
    error_total = error_total + error_instancia
    global cantidad_ciudades
    cantidad_ciudades = n
    
    minimo, promedio = log.select("min", "avg")

    print('Costo  : %d' % min(lista_costos))
    print("Tiempo : %f" % tiempo)

def graficar(x, y, solucion):
    plt.figure(figsize = (20,20))
    plt.scatter(x, y, color = 'green')
    s = []
    for n in range(len(x)):
        s_temp = []
        s_temp.append("%.1f" % x[n])
        s_temp.append("%.1f" % y[n])
        s.append(s_temp)

        plt.xlabel("Distancia X")
        plt.ylabel("Distancia Y")
        plt.title("Ubicacion de las ciudades - TSP")
        
    for f in range(len(solucion)):
        plt.annotate(str(f), xy=(x[f],y[f]),xytext = (x[f]-2, y[f]-4),color= 'blue')
    for n in range (len(solucion)-1):
        plt.plot([x[solucion[n]],x[solucion[n+1]]],[y[solucion[n]],y[solucion[n+1]]],color = 'purple')
        
    plt.plot([x[solucion[-1]],x[solucion[0]]],[y[solucion[-1]],y[solucion[0]]],color = 'purple')
    
# Para salir de la ejecución del programa
def salir():
    print("")
    print('Has salido de la ejecución del programa')

# Las opciones de menu que tendra el usuario para ingresar
def menu():
    print("")
    print(f'1. Iterated Local Search')    
    print(f'2. Genetic Algorithm')
    print(f'3. Hybrid Algorithm')     
    print(f'4. Terminar la ejecución del programa.')      
    return                 

fuente= open('instancias.txt','r')
lista_total = fuente.readlines()

# Variables para sacar promedio final y entregar datos promedio en csv
global total_ciudades
global costo_optimo_total
global costo_minimo_total
global error_minimo_total
global costo_promedio_total
global error_promedio_total
global tiempo_promedio_total
global aristas_total
op = 0

while op != 4:
    menu()
    # Seguira en el while hasta que el usuario ingrese algun valor correcto (robustez).
    while True:
        try:
            op = int(input("SELECCIONE LA METAHEURISTICA A UTILIZAR: "))
            print("")
            break
        except ValueError:
            print("")
            print("Valor ingresado no es valido, intente nuevamente")
    
    # Para avanzar instancia por instancia como una simulación del proceso       
    if op == 1:
        #inicializacion de variables a utilizar 
        total_para_tabular=[]
        promedios_lista=[]
        total_ciudades=0
        costo_optimo_total = 0
        costo_minimo_total=0
        error_minimo_total=0
        costo_promedio_total=0
        error_promedio_total=0
        tiempo_promedio_total = 0
        aristas_total = 0
        contador = 1  #identificar en que instancia se esta        
        
        for instancia in lista_total:  
            #Guardar datos de archivo y separarlos por espacio
            b = instancia.split()
            id_instancia = b[0]
            nombre_instancia = b[1]
            costo_optimo = int(b[2])
            
            graficar_ruta = False
            coord_x = []
            coord_y = []
            problem =tsplib95.load('instancias/'+ nombre_instancia + '.tsp') #para cargar instancias
            info = dict()   
            #variables a utilizar    
            para_tabular=[]
            tiempo_total=0
            costo_total=0
            ejecuciones = 10
            costo_minimo = 99999999
            error_total = 0
            #Variable para identificar a que tipo de problema corresponde, y ver si a la distancia se le suma 1 o 0
            tipo_var = 0
            
            def main1(): #para leer la instancia 
                G = problem.get_graph()
                #ciudad = [i-1 for i in list(problem.get_nodes())]
                numero = len(list(problem.get_nodes()))
                ciudad = [i for i in range(numero)]
                global info
                info = problem.as_keyword_dict() 
                #Si corresponde a ese tipo de instancia , se puede graficar
                if info['EDGE_WEIGHT_TYPE']== 'EUC_2D' : # se puede graficar la ruta
                    global graficar_ruta
                    graficar_ruta = True
                    
                    for i in range(1, len(ciudad) + 1):
                        x, y = info['NODE_COORD_SECTION'][i]
                        coord_x.append(x)
                        coord_y.append(y)
                        
                #Esta seccion es para ver a que tipo de problema corresponde y asignar un 1 o 0 a tipo_var para resolver las distancias        
                global tipo_var
                if info['EDGE_WEIGHT_TYPE']== 'EUC_2D' or info['EDGE_WEIGHT_TYPE']== 'GEO' or info['EDGE_WEIGHT_TYPE']== 'ATT': #or info['EDGE_WEIGHT_TYPE']== 'EXPLICIT' and info['DISPLAY_DATA_TYPE'] != 'TWOD_DISPLAY'
                    tipo_var = 1
                elif info['NAME'] == 'dantzig42' or info['NAME'] == 'gr120':
                    tipo_var = 1
                elif info['NAME'] == 'gr17' or info['NAME'] == 'gr21' or info['NAME'] == 'gr24' or info['NAME'] == 'swiss42' or info['NAME'] == 'gr48' or info['NAME'] == 'fri26' or info['NAME'] == 'brazil58':
                    tipo_var = 0
                elif info['EDGE_WEIGHT_TYPE']== 'EXPLICIT' and info['EDGE_WEIGHT_FORMAT'] != 'LOWER_DIAG_ROW' and info['EDGE_WEIGHT_FORMAT'] != 'FULL_MATRIX ':
                    tipo_var = 1
                else:
                    tipo_var = 0  
                # Es para asigar un tipo de perturbacion, mas brusca o menos brusca dependiendo la instancia. Se tiene un ciclo for de 10.    
                global contador
                if contador <= 18 or contador == 23 or contador == 24 or contador == 27 or contador == 29 or contador == 31 or contador == 35:
                    for semilla in range(1,ejecuciones + 1):
                        print('------------- Semilla ', semilla,'------------')
                        ILS(ciudad,semilla)
                else:
                    for semilla in range(1,ejecuciones + 1):
                        print('------------- Semilla ', semilla,'------------')
                        ILS1(ciudad,semilla)
        
                contador += 1
                
            if __name__ == "__main__":
                main1()
                
        #Esta seccion guarda el mejor resultado entre las mejores 10 iteraciones de cada instancia y acumula los valores para sacar el promedio posteriormente.
        # la lista para_tabular guarda los mejores resultados de cada instancia
        #1 : ID INSTANCIA
            print('ID: ', id_instancia)
            para_tabular.append(id_instancia)
                
        #2 : NOMBRE INSTANCIA 
            print('Nombre: ',nombre_instancia)
            para_tabular.append(nombre_instancia)
                
        #3 : NUMERO DE VERTICES INSTANCIA
            print('N° Vertices: ',cantidad_ciudades)
            para_tabular.append(round(cantidad_ciudades,2))
            total_ciudades= total_ciudades + cantidad_ciudades
                
        #4 :  NUMERO DE ARISTAS 
            aristas= (cantidad_ciudades*(cantidad_ciudades-1))/2
            print('N° Aristas: ', aristas)
            para_tabular.append(aristas)
            aristas_total = aristas_total + aristas
                
        #5 : COSTOS OPTIMOS INSTANCIA
            print('Costo optimo: ',costo_optimo)
            para_tabular.append(round(costo_optimo,2))
            costo_optimo_total = costo_optimo_total + costo_optimo
                
        #6 : COSTO MINIMO DE LAS 10 INSTANCIAS
            print('Costo mínimo de ejecuciones: ',costo_minimo) 
            para_tabular.append(round(costo_minimo,2))
            costo_minimo_total = costo_minimo_total + costo_minimo
                
        #7 : ERROR RELATIVO MINIMO
            error_minimo = ((costo_minimo - costo_optimo)/costo_optimo) * 100
            print('ERM: ',error_minimo) 
            para_tabular.append(round(error_minimo,2))
            error_minimo_total = error_minimo_total + error_minimo
                
        #8 : COSTO PROMEDIO 10 EJECUCIONES
            costo_promedio = (costo_total) / ejecuciones
            print('Costo promedio ejecuciones:', costo_promedio)
            para_tabular.append(round(costo_promedio,2))
            costo_promedio_total = costo_promedio_total + costo_promedio
                
        #9 : ERROR RELATIVO PROMEDIO 10 EJECUCIONES
            error_promedio = error_total / ejecuciones
            print('ERP: ',error_promedio)
            para_tabular.append(round(error_promedio,2))
            error_promedio_total = error_promedio_total + error_promedio
        #10 : TIEMPO PROMEDIO EJECUCIONES
            tiempo_promedio = (tiempo_total)/ejecuciones
            print('Tiempo promedio de ejecución:', tiempo_promedio)
            para_tabular.append(round(tiempo_promedio,2))
            tiempo_promedio_total = tiempo_promedio_total + tiempo_promedio
        #La lista total_para_tabular la informacion de los resultados de las 40 instancias 
            total_para_tabular.append(para_tabular)
   
    elif op == 2:
        # Inicializacion de variables a utilizar 
        total_para_tabular=[]
        promedios_lista=[]
        total_ciudades=0
        costo_optimo_total = 0
        costo_minimo_total=0
        error_minimo_total=0
        costo_promedio_total=0
        error_promedio_total=0
        tiempo_promedio_total = 0
        aristas_total = 0        

        for instancia in lista_total:
            b = instancia.split()
            id_instancia = b[0]
            nombre_instancia = b[1]
            costo_optimo = int(b[2])
            
            para_tabular = []
            graficar_ruta = False
            coord_x = []
            coord_y = []
            problem = tsplib95.load('instancias/'+ nombre_instancia + '.tsp')
            
            #variables a utilizar
            tiempo_total=0
            costo_total=0
            ejecuciones = 10
            costo_minimo = 99999999
            error_total = 0
        
            tipo_var = 0     
            
            def main2():
                G = problem.get_graph()
                ciudad = list(problem.get_nodes())
                info = problem.as_keyword_dict()
                
                # En caso de querer graficar
                if info['EDGE_WEIGHT_TYPE'] == 'EUC_2D':
                    global graficar_ruta
                    graficar_ruta = True
                    for i in range(1, len(ciudad) + 1):
                        x, y = info['NODE_COORD_SECTION'][i]
                        coord_x.append(x)
                        coord_y.append(y)
                        
                global tipo_var
                if info['EDGE_WEIGHT_TYPE']== 'EUC_2D' or info['EDGE_WEIGHT_TYPE']== 'GEO' or info['EDGE_WEIGHT_TYPE']== 'ATT': #or info['EDGE_WEIGHT_TYPE']== 'EXPLICIT' and info['DISPLAY_DATA_TYPE'] != 'TWOD_DISPLAY'
                    tipo_var = 1
                elif info['NAME'] == 'dantzig42' or info['NAME'] == 'gr120':
                    tipo_var = 1
                elif info['NAME'] == 'gr17' or info['NAME'] == 'gr21' or info['NAME'] == 'gr24' or info['NAME'] == 'swiss42' or info['NAME'] == 'gr48' or info['NAME'] == 'fri26' or info['NAME'] == 'brazil58':
                    tipo_var = 0
                elif info['EDGE_WEIGHT_TYPE']== 'EXPLICIT' and info['EDGE_WEIGHT_FORMAT'] != 'LOWER_DIAG_ROW' and info['EDGE_WEIGHT_FORMAT'] != 'FULL_MATRIX ':
                    tipo_var = 1
                else:
                    tipo_var = 0
                        
                for semilla in range(1, ejecuciones + 1):
                    print('------------- Semilla ', semilla,'------------')                    
                    GA2_AG(ciudad, semilla)
                    
            if __name__ == "__main__":
                main2()
                
        #PARTES O DATOS SOLICITADOS
        #1 : ID INSTANCIA
            print('ID: ', id_instancia)
            para_tabular.append(id_instancia)
        
        #2 : NOMBRE INSTANCIA 
            print('Nombre: ',nombre_instancia)
            para_tabular.append(nombre_instancia)
        
        #3 : NUMERO DE VERTICES INSTANCIA
            print('N° Vertices: ',cantidad_ciudades)
            para_tabular.append(round(cantidad_ciudades,2))
            total_ciudades= total_ciudades + cantidad_ciudades
        
        #4 :  NUMERO DE ARISTAS INSTANCIA
            aristas= (cantidad_ciudades*(cantidad_ciudades-1))/2
            print('N° Aristas: ', aristas)
            para_tabular.append(aristas)
            aristas_total = aristas_total + aristas
        
        #5 : COSTOS OPTIMOS INSTANCIA
            print('Costo optimo: ',costo_optimo)
            para_tabular.append(round(costo_optimo,2))
            costo_optimo_total = costo_optimo_total + costo_optimo
        
        #6 : COSTO MINIMO DE LAS 10 INSTANCIAS
            print('Costo mínimo de ejecuciones: ',costo_minimo) 
            para_tabular.append(round(costo_minimo,2))
            costo_minimo_total = costo_minimo_total + costo_minimo
        #7 : ERROR RELATIVO MINIMO
            error_minimo = ((costo_minimo - costo_optimo)/costo_optimo) * 100
            print('ERM: ',error_minimo) 
            para_tabular.append(round(error_minimo,2))
            error_minimo_total = error_minimo_total + error_minimo
        
        #8 : COSTO PROMEDIO 10 EJECUCIONES
            costo_promedio = (costo_total) / ejecuciones
            print('Costo promedio ejecuciones:', costo_promedio)
            para_tabular.append(round(costo_promedio,2))
            costo_promedio_total = costo_promedio_total + costo_promedio
        
        #9 : ERROR RELATIVO PROMEDIO 10 EJECUCIONES
            error_promedio = error_total / ejecuciones
            print('ERP: ',error_promedio)
            para_tabular.append(round(error_promedio,2))
            error_promedio_total = error_promedio_total + error_promedio
        #10 : TIEMPO PROMEDIO EJECUCIONES
            tiempo_promedio = (tiempo_total)/ejecuciones
            print('Tiempo promedio de ejecución:', tiempo_promedio)
            para_tabular.append(round(tiempo_promedio,2))
            tiempo_promedio_total = tiempo_promedio_total + tiempo_promedio
        
            total_para_tabular.append(para_tabular)
        
    elif op == 3:
        # Inicializacion de variables a utilizar 
        total_para_tabular=[]
        promedios_lista=[]
        total_ciudades=0
        costo_optimo_total = 0
        costo_minimo_total=0
        error_minimo_total=0
        costo_promedio_total=0
        error_promedio_total=0
        tiempo_promedio_total = 0
        aristas_total = 0               
        
        for instancia in lista_total:
            b = instancia.split()
            id_instancia = b[0]
            nombre_instancia = b[1]
            costo_optimo = int(b[2])
            
            para_tabular = []
            graficar_ruta = False
            coord_x = []
            coord_y = []
            problem = tsplib95.load('instancias/'+ nombre_instancia + '.tsp')
            
            #variables a utilizar
            tiempo_total=0
            costo_total=0
            ejecuciones = 10
            costo_minimo = 99999999
            error_total = 0
        
            tipo_var = 0          
        
            def main3():
                G = problem.get_graph()
                ciudad = list(problem.get_nodes())
                info = problem.as_keyword_dict()
                
                # En caso de querer graficar
                if info['EDGE_WEIGHT_TYPE'] == 'EUC_2D':
                    global graficar_ruta
                    graficar_ruta = True
                    for i in range(1, len(ciudad) + 1):
                        x, y = info['NODE_COORD_SECTION'][i]
                        coord_x.append(x)
                        coord_y.append(y)
                        
                global tipo_var
                if info['EDGE_WEIGHT_TYPE']== 'EUC_2D' or info['EDGE_WEIGHT_TYPE']== 'GEO' or info['EDGE_WEIGHT_TYPE']== 'ATT': #or info['EDGE_WEIGHT_TYPE']== 'EXPLICIT' and info['DISPLAY_DATA_TYPE'] != 'TWOD_DISPLAY'
                    tipo_var = 1
                elif info['NAME'] == 'dantzig42' or info['NAME'] == 'gr120':
                    tipo_var = 1
                elif info['NAME'] == 'gr17' or info['NAME'] == 'gr21' or info['NAME'] == 'gr24' or info['NAME'] == 'swiss42' or info['NAME'] == 'gr48' or info['NAME'] == 'fri26' or info['NAME'] == 'brazil58':
                    tipo_var = 0
                elif info['EDGE_WEIGHT_TYPE']== 'EXPLICIT' and info['EDGE_WEIGHT_FORMAT'] != 'LOWER_DIAG_ROW' and info['EDGE_WEIGHT_FORMAT'] != 'FULL_MATRIX ':
                    tipo_var = 1
                else:
                    tipo_var = 0
                        
                for semilla in range(1, ejecuciones + 1):
                    print('------------- Semilla ', semilla,'------------')                    
                    GA2(ciudad, semilla)
                    
            if __name__ == "__main__":
                main3()
                
        #PARTES O DATOS SOLICITADOS
        #1 : ID INSTANCIA
            print('ID: ', id_instancia)
            para_tabular.append(id_instancia)
        
        #2 : NOMBRE INSTANCIA 
            print('Nombre: ',nombre_instancia)
            para_tabular.append(nombre_instancia)
        
        #3 : NUMERO DE VERTICES INSTANCIA
            print('N° Vertices: ',cantidad_ciudades)
            para_tabular.append(round(cantidad_ciudades,2))
            total_ciudades= total_ciudades + cantidad_ciudades
        
        #4 :  NUMERO DE ARISTAS INSTANCIA
            aristas= (cantidad_ciudades*(cantidad_ciudades-1))/2
            print('N° Aristas: ', aristas)
            para_tabular.append(aristas)
            aristas_total = aristas_total + aristas
        
        #5 : COSTOS OPTIMOS INSTANCIA
            print('Costo optimo: ',costo_optimo)
            para_tabular.append(round(costo_optimo,2))
            costo_optimo_total = costo_optimo_total + costo_optimo
        
        #6 : COSTO MINIMO DE LAS 10 INSTANCIAS
            print('Costo mínimo de ejecuciones: ',costo_minimo) 
            para_tabular.append(round(costo_minimo,2))
            costo_minimo_total = costo_minimo_total + costo_minimo
        #7 : ERROR RELATIVO MINIMO
            error_minimo = ((costo_minimo - costo_optimo)/costo_optimo) * 100
            print('ERM: ',error_minimo) 
            para_tabular.append(round(error_minimo,2))
            error_minimo_total = error_minimo_total + error_minimo
        
        #8 : COSTO PROMEDIO 10 EJECUCIONES
            costo_promedio = (costo_total) / ejecuciones
            print('Costo promedio ejecuciones:', costo_promedio)
            para_tabular.append(round(costo_promedio,2))
            costo_promedio_total = costo_promedio_total + costo_promedio
        
        #9 : ERROR RELATIVO PROMEDIO 10 EJECUCIONES
            error_promedio = error_total / ejecuciones
            print('ERP: ',error_promedio)
            para_tabular.append(round(error_promedio,2))
            error_promedio_total = error_promedio_total + error_promedio
        #10 : TIEMPO PROMEDIO EJECUCIONES
            tiempo_promedio = (tiempo_total)/ejecuciones
            print('Tiempo promedio de ejecución:', tiempo_promedio)
            para_tabular.append(round(tiempo_promedio,2))
            tiempo_promedio_total = tiempo_promedio_total + tiempo_promedio
        
            total_para_tabular.append(para_tabular)
    
    elif op == 4:
        salir()
        break
    
    else:
        print('Has ingresado un valor fuera de rango. Por favor intentalo nuevamente')    
        continue

         
    #GENERAL
    #En esta seccion se procesan los resultados de las 40 instancias
    print("\n")
    print("\n")
    print("------------- GENERAL-------------")
    promedios_lista.append('')
    promedios_lista.append('promedio')
            
    #3 : NUMERO DE VERTICES INSTANCIA
    total_ciudades_promedio= total_ciudades/40
    promedios_lista.append(round(total_ciudades_promedio,2))
    print('Promedio n° Vertices: ',total_ciudades_promedio)
    
            
    #4 :  NUMERO DE ARISTAS INSTANCIA
    aristas_total_promedio = aristas_total/40
    promedios_lista.append(round(aristas_total_promedio,2))
    print('Promedio n° de Aristas: ',aristas_total_promedio)
            
    #5 : COSTOS OPTIMOS INSTANCIA
    costo_optimo_total_promedio = costo_optimo_total/40
    promedios_lista.append(round(costo_optimo_total_promedio,2))
    print('Costo optimo promedio: ',costo_optimo_total_promedio)
            
    #6 : COSTO MINIMO DE LAS 10 INSTANCIAS
    costo_minimo_total_promedio = costo_minimo_total/40
    promedios_lista.append(round(costo_minimo_total_promedio,2))
    print('Costo mínimo promedio de ejecuciones: ',costo_minimo_total_promedio) 
            
    #7 : ERROR RELATIVO MINIMO
    error_minimo_total_promedio = error_minimo_total/40
    promedios_lista.append(round(error_minimo_total_promedio,2))
    print('ERM promedio: ',error_minimo_total_promedio)
            
    #8 : COSTO PROMEDIO 10 EJECUCIONES
    costo_promedio_total_promedio = costo_promedio_total/40
    promedios_lista.append(round(costo_promedio_total_promedio,2))
    print('Costo promedio ejecuciones:', costo_promedio_total_promedio)
            
    #9 : ERROR RELATIVO PROMEDIO 10 EJECUCIONES
    error_promedio_total_promedio = error_promedio_total / 40
    promedios_lista.append(round(error_promedio_total_promedio,2))
    print('ERP promedio: ',error_promedio_total_promedio)
            
    #10 : TIEMPO PROMEDIO EJECUCIONES
    tiempo_promedio_total_promedio = tiempo_promedio_total/40
    promedios_lista.append(round(tiempo_promedio_total_promedio,2))
    print('Tiempo promedio de ejecución:', tiempo_promedio_total_promedio)
    
    if op == 1:   
        #Titulos para el archivo csv
        titulos=['#','instancia','|V|','|A|','costo óptimo','mínimo','ERM','promedio','ERP','tiempo']
        
        #Creacion de archivo csv
        with open('ILS.csv','w') as new_file:
            write= csv.writer(new_file,delimiter ='\t')
            
            write.writerow(titulos)
            write.writerows(total_para_tabular)
            write.writerow(promedios_lista)       
            
    elif op == 2:
        #Titulos para el archivo csv
        titulos=['#','instancia','|V|','|A|','costo óptimo','mínimo','ERM','promedio','ERP','tiempo']
        
        #Creacion de archivo csv
        with open('GA.csv','w') as new_file:
            write= csv.writer(new_file,delimiter ='\t')
            
            write.writerow(titulos)
            write.writerows(total_para_tabular)
            write.writerow(promedios_lista)     
            
    elif op == 3:
        #Titulos para el archivo csv
        titulos=['#','instancia','|V|','|A|','costo óptimo','mínimo','ERM','promedio','ERP','tiempo']
        
        #Creacion de archivo csv
        with open('Hybrid.csv','w') as new_file:
            write= csv.writer(new_file,delimiter ='\t')
            
            write.writerow(titulos)
            write.writerows(total_para_tabular)
            write.writerow(promedios_lista)               
            

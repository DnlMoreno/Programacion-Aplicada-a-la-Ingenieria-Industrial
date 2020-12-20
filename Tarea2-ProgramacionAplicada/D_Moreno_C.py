# -*- coding: utf-8 -*-
"""
Created on Fri Dec  4 16:05:44 2020

@author: dnlmo
"""

# Entrada de datos y separación para ser usadas en el Cplex
class datos:
    def __init__(self):
        self.archivo = 'entrada.txt'
        self.num_var = 0
        self.tpo_lim = 0
        self.tipo_fo = 0
        self.fun_obj = 0
        self.linea_res = []
        
        self.f_const = []
        self.f_var = []
        self.r_const = []
        self.r_var = []
        self.op_log = []
        self.b = []
        
        self.var_totales = set()
        
    def __str__(self):
        return f'num_var: {self.num_var} \ntpo_lim: {self.tpo_lim} \ntipo_fo: {self.tipo_fo} \nfun_obj: {self.fun_obj} \nlinea_res: {self.linea_res} \nf_const: {self.f_const} \nf_var: {self.f_var} \nr_const: {self.r_const} \nr_var: {self.r_var} \nop_log: {self.op_log} \nb: {self.b}'
        
    # Se leen los datos de entrada
    def entrada(self):
        with open(self.archivo) as f:
            i = 1
            for linea in f:
                a = linea.split() 
                if len(a) == 2 and a[0] != 'Sujeto':
                    self.num_var, self.tpo_lim = float(a[0]), float(a[1])
                if a[0] == 'Maximizar' or a[0] == 'Minimizar':
                    self.tipo_fo = a[0]
                if a[0] == 'Fobjetivo:':
                    self.fun_obj = a[1:]
                if a[0] == f'Restriccion_{i}:':
                    self.linea_res.append(a[1:])
                    i += 1
    
    # Se estandariza la FO y las restricciones de la siguiente forma: 
    # Para la FO: ['operador (suma o resta)', 'costo numerico', 'variable']
    # Para las restricciones: ['operador (suma o resta)', 'costo numerico', 'variable', ...., 'operador logico', 'operador (suma o resta)', 'costo numerico']  
    # La FO se guarda en una lista y las restricciones en una matriz
    def estandarizarFoRes(self):
        
        # Para estandarizar la funcion objetivo
        if self.fun_obj[0] != '-':
            self.fun_obj.insert(0, '+')
        e = 0
        while len(self.fun_obj) != e:
            if self.fun_obj[e] == '+' or self.fun_obj[e] == '-':
                try:
                    if self.fun_obj[e+1][1] != '_':
                        pass
                    else:
                        self.fun_obj.insert(e+1, '1')
                except IndexError:
                    pass    
            e += 1
        
        # Para estandarizar las restricciones
        for e in range(len(self.linea_res)):    
            if self.linea_res[e][0] != '-':
                self.linea_res[e].insert(0, '+')
        e = 0
        while len(self.linea_res) != e:
            i = 0
            while len(self.linea_res[e]) != i:
                if self.linea_res[e][i] == '+' or self.linea_res[e][i] == '-':
                    try:
                        if self.linea_res[e][i+1][1] != '_' or self.linea_res[e][i+3] == '<=' or self.linea_res[e][i+3] == '==' or self.linea_res[e][i+3] == '>=':
                            pass
                        else:
                            self.linea_res[e].insert(i+1, '1')
                    except IndexError:
                        pass
                i += 1
            e += 1
    
    # Se separan los datos estandarizados en listas (FO) y matriz (restricciones) para trabajarlos en Cplex
    # Dejando las constantes de la funcion objetivo y restricciones en f_const y r_const respectivamente
    # y las variables de la funcion objetivo y restricciones en f_var y r_var respectivamente
    def separarDatos(self):
        # Para separar los valores de la funcion objetivo
        s = 0
        c = 1
        q = 2    
        for e in range(0, len(self.fun_obj), 3):
            self.f_const.append(float(self.fun_obj[s]+self.fun_obj[c]))
            self.f_var.append(self.fun_obj[q])
            s += 3
            c += 3
            q += 3
        
        # Para separar los valores de las restricciones
        for e in range(len(self.linea_res)):
            self.r_const.append([])
            self.r_var.append([])
            s = 0
            c = 1
            q = 2  
            if self.linea_res[e][-2] == '-':
                self.op_log.append(self.linea_res[e][-3])
                self.b.append(float(self.linea_res[e][-2] + self.linea_res[e][-1]))
                for p in range(0, len(self.linea_res[e])-3, 3):
                    self.r_const[e].append(float(self.linea_res[e][s]+self.linea_res[e][c]))
                    self.r_var[e].append(self.linea_res[e][q])
                    s += 3
                    c += 3
                    q += 3
            else:
                self.op_log.append(self.linea_res[e][-2])
                self.b.append(float(self.linea_res[e][-1]))
                for p in range(0, len(self.linea_res[e])-2, 3):
                    self.r_const[e].append(float(self.linea_res[e][s]+self.linea_res[e][c]))
                    self.r_var[e].append(self.linea_res[e][q])
                    s += 3
                    c += 3
                    q += 3
                
        # Para obtener todos los nombres de las variables que hay
        for e in range(len(self.f_var)):
            self.var_totales.add(self.f_var[e])
        
        for e in range(len(self.r_var)):
            for i in range(len(self.r_var[e])):
                self.var_totales.add(self.r_var[e][i])  
    
    # Muestra la salida en consola de los datos y crea un txt con la salida      
    def salidaDatos(self, bb, node):
        archivo = open('salida.txt', 'w')
        archivo.write(f'Nodos: {Nodo.num_nodos_exp}\n')  
        print(f'Nodos: {Nodo.num_nodos_exp}')
        archivo.write(f'{bb}\n')   
        print(f'{bb}')
        if self.tipo_fo == 'Maximizar':
            archivo.write(f'Fobjetivo: {Nodo.mejor_fo_max}\n')
            print(f'Fobjetivo: {Nodo.mejor_fo_max}')
        else:
            archivo.write(f'Fobjetivo: {Nodo.mejor_fo_min}\n')
            print(f'Fobjetivo: {Nodo.mejor_fo_min}')
        c = 0
        try:
            for i in Nodo.variables_fo:
                if i == 1:
                    archivo.write(f'{node.x[c]} = {i}\n')
                    print(f'{node.x[c]} = {i}')   
                c += 1
        except TypeError:
            print()
            print('No se alcanzo a encontrar una solución entera en el tiempo dado... Intente con un mayor tiempo límite.')
            pass
                              
from collections import deque
import time
import copy

import docplex.mp
from docplex.mp.model import Model

import graphviz  
from graphviz import Digraph

# La clase nodo se inicia con los datos listos para ingresar al cplex obtenidos de la clase datos y sus metodos
# De esta forma cuando se utilice el metodo Cplex el nodo guardara los valores de salida del Cplex como sus atributos
# Lo que guardara también si es posible la ramificacion de este nodo, para luego ocuparlo en la clase branchAndBound
class Nodo:
    # Valor muy grande para inicializar el valor de la funcion objetivo dependiendo si el problema es de minimo o maximo
    M = 10000000000000
    mejor_fo_max = -M
    mejor_fo_min = M
    num_nodos_exp = 0
    variables_fo = None
    # Constructor
    def __init__(self, datos, tipo_restriccion_bin, izq = None, der = None):
        # VALORES DE ENTRADA AL CPLEX
        self.fobjetivo = 0   
        self.tipo_fo = datos.tipo_fo
        self.var_totales = datos.var_totales
        
        self.f_const = datos.f_const
        self.f_var = datos.f_var
        self.r_const = datos.r_const
        self.r_var = datos.r_var
        self.op_log = datos.op_log
        self.b = datos.b
        
        self.num_var = datos.num_var
        self.tpo_lim = datos.tpo_lim
        
        # VALORES DE SALIDA
        self.id = 1 # Para identificar a los nodos y poder graficar el arbol
        self.fo = None
        self.var = 0
        self.solucion = None
        self.tipo_restriccion_bin = tipo_restriccion_bin # Para ver si el nodo tendra una nueva restriccion de x = 0 ó x = 1
        self.pos_valor_binario = [None] # Para obtener la posicion de la variables que se van haciendo binarias por restriccion
        
        self.factibilidad = None # Por si la funcion objetivo da infactible
        self.estado = None # Si todas las variables del nodo son binarias es True, en caso contrario, False
        self.ramificacion = None
        self.tipo_solucion = None # Programación lineal (PL) o programación entera (PE), para mostrarlo en la visualización del arbol
        
        self.izquierdo = izq
        self.derecho = der
        
        self.x = None # Variables del modelo
        self.modelo = None # Modelo
        
    def __str__(self):
        return f'ID: {self.id}, FO: {self.fo}, Variables: {self.var}, Pos_valor_binario: {self.pos_valor_binario}, Tipo_restriccion_bin: {self.tipo_restriccion_bin}, Factibilidad: {self.factibilidad}, Estado: {self.estado}, Ramificación: {self.ramificacion}'
                             
    def cplex(self):
        ########################### RESOLUCION PROBLEMA CON DATOS DE ENTRADA ###########################
        
        self.modelo = Model('B&B')
        self.x = self.modelo.continuous_var_list(self.var_totales)
            
        for i in range(len(self.x)):
            for j in range(len(self.f_var)):
                if f'{self.x[i]}' == self.f_var[j]:
                    self.fobjetivo += self.modelo.sum(self.f_const[j] * self.x[i]) 
                else:
                    pass
                
        if self.tipo_fo == 'Maximizar':
            self.modelo.maximize(self.fobjetivo)
        else:
            self.modelo.minimize(self.fobjetivo)
        
        c = 0
        for op in self.op_log:
            self.__restGenerales(c, self.x, self.r_var, self.r_const, op)
            c += 1
            
        for j in range(int(self.num_var)):
            self.modelo.add_constraint(self.modelo.sum(self.x[j]) <= 1)
            self.modelo.add_constraint(self.modelo.sum(self.x[j]) >= 0)
                       
        ########################### AGREGAR RESTRICCION BINARIA EN UNA VARIABLE ###########################
        
        # El criterio para agregar la restricciones es ir agregando la restriccion segun el orden en el que se crearon las variables
        if self.tipo_restriccion_bin == 0:
            binario = 0
            self.__restBinarias(self.x, binario)
            self.__solucionCplex(self.x)
                           
        elif self.tipo_restriccion_bin == 1:
            binario = 1
            self.__restBinarias(self.x, binario)
            self.__solucionCplex(self.x)
            
        else:          
            self.__solucionCplex(self.x)
            
        ########################### VERIFICACION DE VARIABLES ENTERAS y GUARDAR EL MEJOR VALOR DE LA FO ###########################
        
        if self.var != 0:
            p = len(self.var)
            for i in range(p):
                if self.var[i] == 0 or self.var[i] == 1:               
                    p -= 1
                    if p == 0:
                        self.estado = True # Se encontro una solucion entera
                        self.tipo_solucion = 'PE'
                        if self.tipo_fo == 'Maximizar' and self.fo > Nodo.mejor_fo_max:
                            Nodo.mejor_fo_max = self.fo
                            Nodo.num_nodos_exp = self.id
                            Nodo.variables_fo = self.var
                        elif self.tipo_fo == 'Minimizar' and self.fo < Nodo.mejor_fo_min:
                            Nodo.mejor_fo_min = self.fo
                            Nodo.num_nodos_exp = self.id
                            Nodo.variables_fo = self.var   
                else:
                    self.estado = False # Aun hay un valor que no es binario
                    self.tipo_solucion = 'PL'
                    break
                    
        ########################### VERIFICACION DE FACTIBILIDAD ###########################
                
        if self.solucion: # Si la solucion es factible
            self.factibilidad = True # El nodo tiene la posibilidad de ramificarse
            
        else: # Solucion no factible
            self.factibilidad = False # El nodo no se pueda ramificar
         
        ########################### VERIFICACION DE RAMIFICACIÓN ###########################
            
        if self.factibilidad == True and self.estado == False:
            self.ramificacion = True
        elif self.factibilidad == True and self.estado == True:
            self.ramificacion = False # No se puede seguir ramificando porque encontro una solucion binaria
        elif self.factibilidad == False:
            self.ramificacion = False # No se puede seguir ramificando
        
        if self.estado == False and self.tipo_fo == 'Maximizar':
            if self.fo <= Nodo.mejor_fo_max:
                self.ramificacion = False 
                
        if self.estado == False and self.tipo_fo == 'Minimizar':
            if self.fo >= Nodo.mejor_fo_min:
                self.ramificacion = False    
     
    # Metodo que agrega las restricciones con los datos de entrada   
    def __restGenerales(self, c, x, r_var, r_const, op):
        rest_n = 0
        for i in range(len(x)):
            for j in range(len(r_var[c])):
                if f'{x[i]}' == r_var[c][j]:
                    rest_n += self.modelo.sum(r_const[c][j] * x[i])
                else:
                    pass
        if op == '<=':
            self.modelo.add_constraint(rest_n <= self.b[c])
        elif op == '<':
            self.modelo.add_constraint(rest_n < self.b[c])
        elif op == '>=':
            self.modelo.add_constraint(rest_n >= self.b[c])
        elif op == '>':
            self.modelo.add_constraint(rest_n > self.b[c])            
        elif op == '=' or op == '==':
            self.modelo.add_constraint(rest_n == self.b[c])
             
    # Metodo que agrega las restricciones binarias 
    def __restBinarias(self, x, binario):
        j = 0      
        for i in self.pos_valor_binario: 
            if i == 0:
                self.modelo.add_constraint(x[j] == 0)
            elif i == 1:
                self.modelo.add_constraint(x[j] == 1)
            elif i == None:
                self.pos_valor_binario.insert(j, binario)
                self.modelo.add_constraint(x[j] == binario) 
                break
            j += 1
    
    # Metodo que resuelve y guarda los valores del Cplex         
    def __solucionCplex(self, x):
        print()
        print(self.modelo.export_to_string()) # Imprimir OPL de cplex
        self.modelo.print_information() # Imprimir información
        self.solucion = self.modelo.solve(log_output=False) # resolver
        try:
            self.solucion.display() # Mostrar solución
            self.fo = self.solucion.get_objective_value()
            self.var = self.solucion.get_values(x)  
        except AttributeError:
            self.fo = 'Infactible'

# Se resuelve el Branch and Bound considerando los atributos que obtuvieron cada nodo en la resolucion del Cplex 
# Además se grafica y se toma el tiempo de resolucion del metodo B&B
# El analisis del B&B se va haciendo por nivel mediante una cola para ir analizando al nodo padre y a sus hijos
class branchAndBound: 
    def __init__(self, datos):
        self.datos = datos
        self.cola = deque()
        self.dot = Digraph(comment='B&B')
        #self.dot.attr(size='1000,1000')
        #self.dot.attr(size='6,6')
        self.dot.attr(size='100,100')
        self.inicio = 0
        self.stop = 0
        self.final = 0
        
    def __str__(self):
        return f'Tiempo: {self.final}'
        
    def resolver(self, nodo):
        self.inicio = time.time()
        self.cola.append(nodo) 
        self.dot.node(f'{nodo.id}', f'{nodo.id}')
        while self.cola:
            nodo = self.cola[0]
            ultimo_nodo = self.cola[-1] 
            nodo.cplex()
            if nodo.fo == 'Infactible':
                self.dot.node(f'{nodo.id}', f'ID: {nodo.id} - FO: {nodo.fo}')
            else: 
                self.dot.node(f'{nodo.id}', f'ID: {nodo.id} - FO: {nodo.fo:.2f} - {nodo.tipo_solucion}')
            nodo.tipo_restriccion_bin = None
            
            if nodo.ramificacion == True:
                nodo.izquierdo = Nodo(self.datos, tipo_restriccion_bin = 0)
                nodo.izquierdo.pos_valor_binario = copy.deepcopy(nodo.pos_valor_binario)
                nodo.izquierdo.id = copy.copy(ultimo_nodo.id) + 1
                self.__graficarIzquierdo(nodo, nodo.izquierdo)
                
                nodo.derecho = Nodo(self.datos, tipo_restriccion_bin = 1)
                nodo.derecho.pos_valor_binario = copy.deepcopy(nodo.pos_valor_binario)
                nodo.derecho.id = copy.copy(nodo.izquierdo.id) + 1    
                self.__graficarDerecho(nodo, nodo.derecho)
                
                self.cola.append(nodo.izquierdo) 
                self.cola.append(nodo.derecho) 
                
            else:
                pass
            
            self.cola.popleft()
            self.stop = time.time()
            
            if self.stop - self.inicio >= nodo.tpo_lim:
                self.final = self.stop - self.inicio
                print()
                print('El tiempo de ejecución del algoritmo sobrepaso el tiempo límite de ejecución')
                self.__graficaTotal()
                break
        
        self.final = self.stop - self.inicio           
        self.__graficaTotal()        
         
    def __graficarIzquierdo(self, nodo, nodoIzquierdo):
        self.dot.node(f'{nodoIzquierdo.id}', f'ID: {nodoIzquierdo.id}')
        self.dot.edge(f'{nodo.id}', f'{nodoIzquierdo.id}')
        
    def __graficarDerecho(self, nodo, nodoDerecho):
        self.dot.node(f'{nodoDerecho.id}', f'ID: {nodoDerecho.id}')
        self.dot.edge(f'{nodo.id}', f'{nodoDerecho.id}')
            
    def __graficaTotal(self):
        self.dot.render('Branch-and-Bound.gv', view=True)

        
def main():
    data = datos()
    data.entrada()
    data.estandarizarFoRes()
    data.separarDatos()
    node = Nodo(data, tipo_restriccion_bin = None)
    Nodo.num_nodos_exp = 0
    bb = branchAndBound(data)
    bb.resolver(node)
   
    ########## ARCHIVO DE SALIDA #########
    print()
    print('--------------------- DATOS DE SALIDA ---------------------')
    data.salidaDatos(bb, node)
 
if __name__ == "__main__":
    main()

import qasm
import numpy as np
import pylatexenc
import matplotlib
import  random
import math
import os
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister


qc = QuantumCircuit(3)
qc.h(0)
qc.h(2)
qc.cx(2,0)
qc.cx(0,1)
qc.h(2)

a = qc.qasm(filename = "test.qasm")
print(a)


'''
считываем  с кискита в qasm
'''
def find(vector, array):
    for elem in array:
        if np.allclose(vector, elem, rtol=1e-03):
            return True

    return False

def read_qasm(file):
    t = None
    with open(file) as file:
        t = file.read()
        t = t.split(";\n")
        file.close()
    n = t[2]
    return int(n[7:-1]) , t[3:-1] # передает количество кубит и список операций

def text_to_function(text):
    text = text.split(" ")
    func = text[0]
    qubits = [int(x)  for x in text[1]  if x.isdigit() == True]
    return func, qubits

'''
указываем входные и выходные параметры для каждой функции 
глобальная фаза не учтена, но это важно
'''

#math.isclose(0.1 + 0.2, 0.3, rel_tol=1e-20)
#numpy.allclose()

class Hoare_function:
    def __init__(self, name, q1, q2 = None):
        self.name = name
        self.trivial = []
        self.q1 = q1
        self.q2 = q2
        self.matrix = None

    def P(self, vector_global):   #функция на проверку условия тривиальности
        #print(self.trivial, vector_global)
        if self.name == "swap" and vector_global[2*self.q1:2*self.q1+2] == vector_global[2 * self.q2:2 * self.q2 + 2] :
            return False

        if self.q2 == None:
            vector = vector_global[2*self.q1:2*self.q1+2]
            if vector in self.trivial:
                return False
        else:
            vector1 =vector_global[2 * self.q1:2 * self.q1 + 2]
            if np.allclose(vector1, np.array([1,0]), rtol=1e-03):
                return False
            else:
                vector2 = vector_global[2 * self.q2:2 * self.q2 + 2]
                if find(vector2,self.trivial ):   #может быть ошибка, но можно просто написать функцию
                    return False
        return  True

    def Q(self):
        if self.name == "x":
            self.trivial = [np.array([1,1])/math.sqrt(2), np.array([1,-1])/math.sqrt(2)]  # тут прикол с фазой 1-1 фаза в pi
            self.matrix  = np.array([
                [0,1],
                [1,0]
            ])
        elif self.name == "z":
            self.trivial = [np.array([1,0]), np.array([0,1])] # тут прикол с фазой 1-1 фаза в pi
            self.matrix = np.array([
                [1,0],
                [0,-1]
            ])
        elif self.name == "y":
            self.trivial =  [np.array([1,0]), np.array([0,1])] # тут прикол с фазой 2-0  фаза в pi
            self.matrix = np.array([
                [0,-1j],
                [1j,0]
            ])
        elif self.name == "h":
            self.matrix =  np.array([
                [1,1],
                [1,-1]
            ])/math.sqrt(2)
        elif self.name == "cx":
            self.trivial = [np.array([1, 1]) / math.sqrt(2), np.array([1, -1]) / math.sqrt(2)]
            self.matrix =  np.array([
                [1, 0, 0, 0],
                [0, 1 ,0, 0],
                [0, 0, 0, 1],
                [0, 0, 1, 0]
            ])
        elif self.name == "cz":
            self.trivial = [np.array([1, 0]), np.array([0, 1])]
            self.matrix =  np.array([
                [1, 0, 0, 0],
                [0, 1 ,0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, -1]
            ])
        elif self.name == "cy":
            self.trivial = [np.array([1, 0]), np.array([0, 1])]
            self.matrix = np.array([
                [1, 0, 0, 0],
                [0, 1 ,0, 0],
                [0, 0, 0, -1j],
                [0, 0, 1j, 0]
            ])
        elif self.name == "ch":
            self.matrix = np.array([
                [1, 0, 0, 0],
                [0, 1 ,0, 0],
                [0, 0, math.sqrt(1/2), math.sqrt(1/2)],
                [0, 0, math.sqrt(1/2), -math.sqrt(1/2)]
            ])
        elif self.name == "swap":
            self.matrix = np.array([
                [1, 0, 0, 0],
                [0, 0 ,1, 0],
                [0, 1, 0, 0],
                [0, 0, 0, 1]
            ])
        else:
            #тут можно найти вектора собственного базиса
            return print("no working")



    def R(self, vector_global):
        self.Q()
        if self.P(vector_global) == True:
            #продолжаем делать цепочку и преобразуем вектор
            if self.q2 == None:
                vector = vector_global[2 * self.q1:2 * self.q1 + 2]
            else:
                vector = np.hstack((vector_global[2 * self.q1:2 * self.q1 + 2] , vector_global[2 * self.q2:2 * self.q2 + 2]))

            new_vector = np.dot(self.matrix, vector)

            vector_global[2 * self.q1] = new_vector[0]
            vector_global[2 * self.q1 +1] =new_vector[1]

            #print(new_vector[0], vector_global[2 * self.q1], a[2 * self.q1])
            #print(vector_global)

            if self.q2 != None:
                vector_global[2 * self.q2] = new_vector[2]
                vector_global[2 * self.q2 + 1] = new_vector[3]
            return vector_global
        else:
            return vector_global  #выводим прошлым вектор, не учитываем преобразование в новой цепочки


    def RR(self, state_matrix, vector_global):
        self.Q()
        if self.P(vector_global) == True:

            n = state_matrix.shape[0]
            local_matrix = np.diag([1] * n).astype(float)
            #print(local_matrix)
            local_matrix[2 * self.q1][2 * self.q1],    local_matrix[2 * self.q1][2 * self.q1+1]   = self.matrix[0][0], self.matrix[0][1]
            local_matrix[2 * self.q1+1][2 * self.q1],  local_matrix[2 * self.q1+1][2 * self.q1+1] = self.matrix[1][0], self.matrix[1][1]
            if self.q2 != None:
                local_matrix[2 * self.q2][2 * self.q2], local_matrix[2 * self.q2][2 * self.q2 + 1] = self.matrix[2][2], self.matrix[2][3]
                local_matrix[2 * self.q2 + 1][2 * self.q2], local_matrix[2 * self.q2 + 1][2 * self.q2 + 1] = self.matrix[3][2], self.matrix[3][3]
            #print(local_matrix)
            new_matrix =  np.dot(state_matrix, local_matrix)
            return new_matrix
        else:
            return state_matrix



    def h_con(self): #находим обратную матрицу

        return print("No working")

class np_dict:
    def __init__(self, keys = [], values = []):
        self.keys = keys
        self.values = values

    def remove(self):

        return print("don not work")

    def place(self, key):

        for i in range(len(self.keys)):
            if np.allclose(self.keys[i], key, rtol=1e-03):
                return i
        else:
            return False

    def append(self, key, value:list):
        if not find(key, self.keys):
            self.keys.append(key)
            self.values.append(value)
        else:
            n = self.place(key)
            self.values[n] = self.values[n] + value

    def replace(self, key, value):
        if not find(key, self.keys):
            return print("Нет значения в словаре")
        else:
            n = self.place(key)
            self.values[n] = value
    def all_vectors(self):
        all = []
        for i in self.values:
            a = all + i
            all = a
        return all

def removing(listt, del1, del2):
    list_new = []
    for i in listt:
        if not (del1 <= i  <del2):
            list_new.append(i)
    return list_new

##############################################################################################################3

number_q, operation_list = read_qasm("test.qasm")
#print(number_q, operation_list)

#qc_new = QuantumCircuit(number_q)
'''
хранение списка векторов после каждого выполнения - а нужно ли вообще?
'''
vector_array = [np.array([1,0]*number_q, dtype=float)]


'''
итеррация по циклу
'''

state_matrix = np.diag([1] * 2*number_q).astype(float)


for operation in operation_list:
    name, qubits_list = text_to_function(operation)
    if len(qubits_list) ==2:
        object = Hoare_function(name , qubits_list[0], qubits_list[1])
    else:
        object = Hoare_function(name, qubits_list[0])
    #print(vector_array[-1], "----было так")
    #print(object.R(vector_array[-1]))
    #vector_array.append(object.R(vector_array[-1]))  <---- старый вариант
    matrix = object.RR(state_matrix, vector_array[-1])
    a = np.dot(state_matrix, matrix)
    state_matrix = a
    vector_array.append( np.dot(state_matrix, vector_array[-1]))

    #print(vector_array[-1], "----стало так")
#print(vector_array)

# есть лист с операциями и векторами находим похожие вектора, записывваем в слварь

vectors_dict = np_dict()
new_operation_list = []
#print(vectors_dict.keys, "fkfkfkfkf")

'''
создаем словарь из векторов и заполняем его
'''

for i in range(len(vector_array)):
    vectors_dict.append(vector_array[i], [i])
    if i !=len(vector_array)-1:
        name, qubits_list = text_to_function(operation_list[i])
        if len(qubits_list) == 2:
            object = Hoare_function(name, qubits_list[0], qubits_list[1])
        else:
            object = Hoare_function(name, qubits_list[0])
        if object.P(vector_array[i]) :
            new_operation_list.append(1)
        else:
            new_operation_list.append(0)


#print(new_operation_list)
#print(vectors_dict.values)




while True:
    maxi = 0
    del1 = None
    del2 = None
    for listt in vectors_dict.values:
        if listt == []:
            continue
        raz = listt[-1] - listt[0]

        if raz > maxi:
            maxi = raz
            del1 = listt[0]
            del2 = listt[-1]

    if maxi >0:
        for i in range(len(vectors_dict.values)):
            a = removing(vectors_dict.values[i], del1, del2)
            vectors_dict.values[i] = a

    else:
        break



#print(vectors_dict.values)
#print(vectors_dict.values[2])
#print(vectors_dict.all_vectors())



with open("new.qasm", "w") as text:
    a, b= read_qasm("test.qasm")
    text.write("OPENQASM 2.0; \n")
    text.write('include "qelib1.inc"; \n')
    text.write('qreg q[' + str(a)+']; \n')
    for i in range(len(operation_list)):
        if i in vectors_dict.all_vectors() and i != len(vector_array) - 1:
            text.write((operation_list[i]) +";\n")
    text.close()



new_qc = QuantumCircuit.from_qasm_file("new.qasm")
print(new_qc.draw())

'''
выкидываем очевидные тривиальные гейты
'''

#print(vectors_dict.keys)
#print(vectors_dict.values)
#print(vector_array[0])
#print(vector_array[1])
#print(vector_array[2])
#print(vector_array[3])
#print(vector_array[4])
#print(vector_array[5])

import qasm
import numpy as np
import pylatexenc
import matplotlib
import  random
import math
import os
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit import QuantumCircuit, execute, Aer


qc = QuantumCircuit(3)
#qc.cx(0,1)
qc.rx(0.5, 0)
qc.h(0)
qc.h(2)
qc.swap(0,2)

qc.cx(2,1)
qc.cx(0,1)
qc.cx(2,0)
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


def comparsion(array, ind1, ind2):
    l_str = int(math.log(len(array), 2.0))
    l_str -= 1
    for i in range(2 ** l_str):
        line = '{0:0' + str(l_str) + 'b}'
        a = line.format(i)

        q10 = a[:ind1] + "0" + a[ind1:]
        q11 = a[:ind1] + "1" + a[ind1:]
        q20 = a[:ind2] + "0" + a[ind2:]
        q21 = a[:ind2] + "1" + a[ind2:]
        q10, q11, q20, q21 = q10[::-1], q11[::-1], q20[::-1], q21[::-1]
        if q10 != q20 or q11 != q21:
            return False
    return True

def perebor(array,ind:int, param, state = None): #принимает массив, индекс, режим
    l_str = int(math.log(len(array), 2.0))
    l_str -= 1

    if param == "0":  #проверка на ноль
        for i in range(2 ** l_str):

            line = '{0:0' + str(l_str) + 'b}'
            a = line.format(i)

            a = a[:ind] + "1" + a[ind:]
            a = a[::-1]
            if array[int(a,2)] != 0:
                return False

        return True

    if param == "0":  #проверка на единицу
        for i in range(2 ** l_str):

            line = '{0:0' + str(l_str) + 'b}'
            a = line.format(i)

            a = a[:ind] + "0" + a[ind:]
            a = a[::-1]
            if array[int(a,2)] != 0:
                return False

        return True

    if param == "srav":   # проверяет, находится ли кубит в одном из состояний |+> |->
        for i in range(2 ** l_str):
            line = '{0:0' + str(l_str) + 'b}'
            c = line.format(i)

            a = c[:ind] + "1" + c[ind:]
            a = a[::-1]
            b = c[:ind] + "0" + c[ind:]
            b = b[::-1]

            if array[int(a,2)] != array[int(b,2)]  and  array[int(a,2)] != -array[int(b,2)]:
                return False
        return True



class Hoare_function:
    def __init__(self, name, q1, q2 = None):
        self.name = name
        self.trivial = []
        self.q1 = q1
        self.q2 = q2
        self.matrix = None
        self.matrix2 = None

    def P(self, vector_global):

        if self.name == "swap": #нужно сравнение двух кубитов отдельной функцией
            return not(comparsion(vector_global,self.q1, self.q2))


        if self.q2 == None:
            if self.name in ["y", "z"]:
                if perebor(vector_global, self.q1, "0") or perebor(vector_global, self.q1, "1"):
                    return False
            if self.name == "x":
                if perebor(vector_global, self.q1, "srav"):
                    return False
        else:
            if perebor(vector_global, self.q1, "0"):
                return False

            else:
                if self.name in ["cy", "cz"]:
                    if perebor(vector_global, self.q2, "0") or perebor(vector_global, self.q2, "1"):
                        return False
                if self.name == "cx":
                    if perebor(vector_global, self.q2, "srav"):
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
            self.matrix2 = np.array([
                [0,1],
                [1,0]
            ])
            self.matrix =  np.array([
                [1, 0, 0, 0],
                [0, 1 ,0, 0],
                [0, 0, 0, 1],
                [0, 0, 1, 0]
            ])
        elif self.name == "cz":
            self.trivial = [np.array([1, 0]), np.array([0, 1])]
            self.matrix2 = np.array([
                [1,0],
                [0,-1]
            ])
            self.matrix =  np.array([
                [1, 0, 0, 0],
                [0, 1 ,0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, -1]
            ])
        elif self.name == "cy":
            self.trivial = [np.array([1, 0]), np.array([0, 1])]
            self.matrix2  = np.array([
                [0,-1j],
                [1j,0]
            ])
            self.matrix = np.array([
                [1, 0, 0, 0],
                [0, 1 ,0, 0],
                [0, 0, 0, -1j],
                [0, 0, 1j, 0]
            ])
        elif self.name == "ch":
            self.matrix = np.array([
                [1, 1],
                [1, -1]
            ]) / math.sqrt(2)
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
            # в цепочку добавляем   <---- при выполнении команды qc.from_qasm_str("h q[0];") выдает ошибку, поэтому обработка "вручную"
            if self.name == "x":
                qc.x(self.q1)
            elif self.name == "z":
                qc.z(self.q1)
            elif self.name == "y":
                qc.y(self.q1)
            elif self.name == "h":
                qc.h(self.q1)
            elif self.name == "cx":
                qc.cx(self.q1, self.q2)
            elif self.name == "cy":
                qc.cy(self.q1, self.q2)
            elif self.name == "cz":
                qc.cz(self.q1, self.q2)
            elif self.name == "ch":
                qc.ch(self.q1, self.q2)
            elif self.name == "swap":
                qc.swap(self.q1, self.q2)


            simulator = Aer.get_backend('statevector_simulator')
            vector_global = execute(qc, simulator).result().get_statevector()

            return vector_global

        simulator = Aer.get_backend('statevector_simulator')
        vector_global = execute(qc, simulator).result().get_statevector()

        return vector_global



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

qc = QuantumCircuit(number_q)
simulator = Aer.get_backend('statevector_simulator')


vector_array = [execute(qc, simulator).result().get_statevector()]
state_matrix = np.diag([1] * 2*number_q).astype(float)
print(operation_list)

for operation in operation_list:
    name, qubits_list = text_to_function(operation)

    if len(qubits_list) ==2:
        object = Hoare_function(name , qubits_list[0], qubits_list[1])
    else:
        object = Hoare_function(name, qubits_list[0])

    a = object.R(vector_array[-1])
    vector_array.append(a)


print(qc.draw())
print(vector_array)

vectors_dict = np_dict()
new_operation_list = []


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

print(vectors_dict.values)
#уничтожение похожих векторов

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




#формирование нового файла
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
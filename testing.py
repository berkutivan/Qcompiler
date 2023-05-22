import numpy as np

from optimize_Hoare import optimizate
import os, shutil
from Qrandom import create


n =  20
folder = 'circuits_give'
folder_out = 'circuits_exit'
'''
чистим папку от старых схем
'''
mean_before = []
mean_after =  []
for j in range(3,20):

    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

    for filename in os.listdir(folder_out):
        file_path = os.path.join(folder_out, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
    '''
    создаем новые 
    '''
    create(n, 20, j, folder)  # первое число - количество цепочек, второе - глубина

    '''
    делаем обработку
    '''

    qubits_before = []
    qubits_after = []
    for i in range(n):
        file_in = "circuit" + str(i) + ".qasm"
        file_out = "circuit_optimize" + str(i) + ".qasm"
        way_in = folder + "/" + file_in
        way_out = folder_out + "/" + file_out
        a, b = optimizate(way_in, way_out)
        qubits_before.append(a)
        qubits_after.append(b)
    qubits_before = np.array(qubits_before)
    qubits_after = np.array(qubits_after)
    mean_before.append(qubits_before.mean())
    mean_after.append(qubits_after.mean())
print(mean_before)
print(mean_after)
#for i in range()
#file = "circuit" + str(k) + ".qasm"


#print(optimizate("test.qasm", "new.qasm"))
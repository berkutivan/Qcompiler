import qasm
import numpy as np
import pylatexenc
import matplotlib
import  random
import os
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister



#считываем json - а как?о\
# файл с информацией о квантовом процессоре, на котором будет
# запускаться заданная квантовая логическая цепочка [подается с ключом
# -q или --qprocessor, по умолчанию используется файл
# qprocessor_info.json]Поддерживаемые гейты- H,X,Z,T,S,Y,CX,CZ,SWAP,ISWAP, CCX,CCZ. Кроме того,
# возможно добавление многокубитных гейтов контролируемой унитарной
# операции: ControlledGate(<U>, 3)( qb[<L0>], qb[ <L1>], … , qb[<LM>])

"""
"single_ion_gate_fidelity": 0.998,
"two_ion_gate_fidelity": 0.975,
"ions_num": 5,
"levels_num": 8,
"2_lvl_measurement_fid": 0.9
"4_lvl_measurement_fid": 0.85
"8_lvl_measurement_fid": 0.8
"desired_gates:"  <------------- нужно ли?
"supported_gates:"
"""
#cоздание jsonБ так удобнееБ в целом, код не нужен
import json
data = {
"single_ion_gate_fidelity": 0.998,
"two_ion_gate_fidelity": 0.975,
"ions_num": 7,
"levels_num": 8,
"2_lvl_measurement_fid": 0.9,
"4_lvl_measurement_fid": 0.85,
"8_lvl_measurement_fid": 0.8,
"desired_gates": ["H","X","Z","T","S","Y","CX","CZ","SWAP","ISWAP", "CCX","CCZ"],
"supported_gates": ["H","X","Z","T","S","Y","CX","CZ","SWAP","ISWAP", "CCX","CCZ"]
}
with open("qprocessor_info.json", "w") as write_file:
    json.dump(data, write_file)
    write_file.close()

#открытие  json

info_dict = {}
with open("qprocessor_info.json", "r") as write_file:
    info_dict = json.load(write_file)
    write_file.close()
#print(info_dict)


count_qbits = int(info_dict["ions_num"])
count_bits = int(info_dict["ions_num"])
#deep = int(info_dict["levels_num"])
all_1gates = ["H","X","Z","T","S","Y","Tdg"]
all_2gates = ["CX","CZ","SWAP","ISWAP"]
all_3gates = ["CCX","CCZ"]

#n = int(input("Число нужных цепочек"))

def create(n,deep,qubits, folder):
    count_qbits = qubits
    for k in range(n):
        circuit = QuantumCircuit(count_qbits)

        for i in range(deep):
            block = random.randint(1, 5)
            if block == 0:
                q = random.randint(0, count_qbits - 1)
                s = random.randint(0, count_bits - 1)
                circuit.measure(q, s)
            elif block == 1 or block == 2 or block ==5:
                gate = random.choice(all_1gates)
                qbit = random.randint(0, count_qbits - 1)
                if gate == "H":
                    circuit.h(qbit)
                elif gate == "X":
                    circuit.x(qbit)
                elif gate == "Z":
                    circuit.z(qbit)
                elif gate == "T":
                    circuit.t(qbit)
                elif gate == "S":
                    circuit.s(qbit)
                elif gate == "Y":
                    circuit.y(qbit)
                elif gate == "Tdg":
                    circuit.tdg(qbit)
            elif (block == 3 or block == 4):
                if count_qbits < 2:
                    deep += 1
                    continue
                gate = random.choice(all_2gates)
                listt = [j for j in range(count_qbits)]
                random.shuffle(listt)
                qbit1, qbit2 = listt[0], listt[1]
                if gate == "CX":
                    circuit.cx(qbit1, qbit2)
                elif gate == "CY":
                    circuit.cy(qbit1, qbit2)
                elif gate == "CZ":
                    circuit.cz(qbit1, qbit2)
                elif gate == "CH":
                    circuit.ch(qbit1, qbit2)
            else:
                if count_qbits < 3:
                    deep += 1
                    continue
                gate = random.choice(all_3gates)
                listt = [j for j in range(count_qbits)]
                random.shuffle(listt)
                qbit1, qbit2, qbit3 = listt[0], listt[1], listt[2]
                if gate == "CCX":
                    circuit.ccx(qbit1, qbit2, qbit3)
                elif gate == "CCZ":
                    circuit.ccz(qbit1, qbit2, qbit3)

        file = "circuit" + str(k) + ".qasm"
        circuit.qasm(filename=file)
        file_replace = folder + "/" + file
        os.rename(file, file_replace)

#create(10, 10, "circuits_give")
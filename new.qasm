OPENQASM 2.0; 
include "qelib1.inc"; 
qreg q[3]; 
h q[0];
h q[2];
cx q[0],q[1];
h q[2];

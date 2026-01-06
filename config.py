# Holds setpoints and data accumulated through program
data = [["Setpoint"],["Measure Voltage [V]"],["Measured Current [A]"],["Log(Measure Voltage)"],["Log(Measured Current)"],["Bad Data Flag"]]

# VISA addresses for devices in test apparatus; change these to match those in your system
ps_VISA = 'TCPIP0::172.29.0.41::inst0::INSTR'
dmm_VISA = 'TCPIP0::172.29.0.36::inst0::INSTR'

# Refer to the board schematic for the value of the protect resistor; usually 1kOhm
prot_res = 1000

# Populate voltage setpoint array

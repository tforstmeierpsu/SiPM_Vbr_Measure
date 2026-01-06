# Description: This script automates SiPM Vbr validation. Two instruments are used in this test procedure:
# a high fidelity DMM and a power supply. The primary objective of this test is to gather and I-V plot for each
# SiPM device, controlling the bias voltage while measuring the DC output current. Test details
# live in the same folder as this script.

# Version: 2.0
# Date: 01/04/2025

# Author: Mary Siepierski, Tom Forstmeier (tmf5239@psu.edu)

# Imports
import pyvisa as visa # Python package that provides bindings to Virtual Instrument Software Architecture (VISA)
from pathlib import Path
from time import gmtime, strftime, localtime, sleep
import time
import numpy as n
import matplotlib.pyplot as plt
from functions import D

# Functions
# Loop function for setting voltage and gathering data
def extractVbr(test_title, avg_num):

    # Create storage variables
    currentArray = n.zeros(avg_num, dtype=n.float64)  # current array containing floats
    voltageArray = n.zeros(avg_num, dtype=n.float64)  # voltage array containing floats

    for i in range(len(voltset)):  # Outer loop walks through all voltage set points
        # Set voltage; loop for 3 channels of ps
        for j in range(3):
            if j == 0:
                mult = (5.0 / 65.0)
            else:
                mult = (30.0 / 65.0)
            write_val = mult * voltset[i]
            ps.write("VOLT {0}, (@{1})".format(f"{write_val:.3f}", str(j + 1)))
            ps.write("*WAI")
            time.sleep(0.5)

        # Reset storage variables
        voltage = voltageSDIV = current = currentSDIV = 0


        # Measure voltage and current
        for k in range(len(voltageArray)):
            for l in range(3):
                voltageArray[k] = voltageArray[k] + float(ps.query("MEAS:VOLT? (@{0})".format(str(l + 1))))
                time.sleep(0.02)
            currentArray[k] = float(dmm.query("READ?"))
            voltageArray[k] = voltageArray[k] - currentArray[k] * float(prot_res)
            time.sleep(0.02)

        # Populate storage arrays
        voltage = voltageArray.mean()
        avg_volt.append(voltage)
        voltageSDIV = n.std(voltageArray)
        current = currentArray.mean()

        avg_curr.append(current)

        currentSDIV = n.std(currentArray)

        currentArray = n.zeros(avg_num, dtype=n.float64)  # reset arrays
        voltageArray = n.zeros(avg_num, dtype=n.float64)  # reset arrays

    avg_curr_log = n.log(avg_curr)
    xprime, yprime = D(avg_volt, avg_curr_log)
    max_deriv_index = yprime.argmax()
    Vbr = xprime[max_deriv_index]

    Vbr_index = (n.abs(voltset - Vbr)).argmin()

    text_file.write("Test: {0} ({1} samples averaged for each datapoint):\n".format(test_title, str(avg_num)))
    text_file.write("Vbr [V]: {0}\n\n".format(Vbr))
    clean_volt = [float(x) for x in avg_volt]
    clean_curr = [float(y) for y in avg_curr]
    text_file.write("Set-point Array [V]:\n{0}\n\n".format(voltset))
    text_file.write("Voltage Array [V]:\n{0}\n\n".format(clean_volt))
    text_file.write("Current Array [A]:\n{0}\n\n\n".format(clean_curr))

    log_i_br = find_vbr_y_value(avg_curr_log, avg_volt, Vbr)

    # Plot the data:
    title = board_ID + ": " + SiPM_ID + " " + test_title

    plt.figure(1)
    plt.semilogy(avg_volt, avg_curr)
    plt.xlabel('Voltage [V]')
    plt.ylabel('Current [A]')
    plt.scatter(Vbr, log_i_br, color='red')
    label = str(Vbr) + ',' + str(log_i_br)
    plt.annotate(label, (Vbr, log_i_br), textcoords="offset points", xytext=(0, 10), ha='center')
    plt.title("{0} {1} VoltVSCurr".format(SiPM_ID,test_title))
    plt.savefig("{0}/{1}_{2}_VoltVSCurr.png".format(folder_path_text, SiPM_ID,test_title))

    plt.figure(2)
    plt.plot(xprime, yprime)
    plt.xlabel('Reverse Voltage [V]')
    plt.ylabel('SiPM d(log(I))/d(V)')
    plt.title("{0} {1} Vbr".format(SiPM_ID, test_title))
    plt.savefig("{0}/{1}_{2}_Vbr.png".format(folder_path_text, SiPM_ID, test_title))

    print(f"Step {i} of {len(voltset)}")

# Find associated current for plotting Vbr point on log(I) vs V plot
def find_vbr_y_value(log_curr, volt, vbr ):
    for i in range(len(volt)):
        if vbr < volt[i]:
            index1 = i
            index2 = i-1
            break
    log_i = (log_curr[index1]+log_curr[index2])/2
    return log_i

# Establish VISA  with devices
rm = visa.ResourceManager()
ps = rm.open_resource('TCPIP0::172.29.0.41::inst0::INSTR') # Power supply
dmm = rm.open_resource('TCPIP0::172.29.0.36::inst0::INSTR') # Digital multimeter


# Initialize instruments
ps.write("*CLS")
ps.write("*RST")
ps.write("CURR:PROT:CLE (@1,2,3)")
ps.write("CURR:PROT:STAT ON,(@1,2,3)")
ps.write("CURR 0.5, (@1,2,3)")
ps.write("VOLT 0,(@1,2,3)")
ps.write("OUTP 1, (@1,2,3)")

dmm.write("*RST")
dmm.write("CONF:CURR:DC")
dmm.write("CURR:NPLC 10")
dmm.write("CURR:DC:TERM 3")
dmm.write("SENS:CURR:RANG 1e-6")

# Gather date/time and open a text file
time_stamp = strftime("%m%d%Y_hr%Hmin%M", localtime())
test_name = input("Enter test name (Pre Shake Test, Post Shake Test).")
board_ID = input("Enter the board for this SiPM (TSM Shake 003 or TSM Shake 002).")
SiPM_ID = input("Enter the SiPM ID (002 TR: 87075, 002 TL: 87076, 003 BR: 87010, 003 BL: 86984).")

# Refer to the board schematic for the value of the protect resistor; usually 1kOhm
prot_res = 1000

# Make board folder if it does not exist already
folder_path_text = "SiPM Validation Data/{0}/{1}/{2}".format(str(test_name), str(SiPM_ID), str(time_stamp))
folder_path = Path(folder_path_text)
try:
    folder_path.mkdir(parents=True, exist_ok=True)
except OSError as e:
    print(f"Error creating directory: {e}")

# Create and open data storage file
file_name = "{0}_{1}_Data.txt".format(str(SiPM_ID), str(time_stamp))
text_file = open("{0}/{1}".format(folder_path_text, file_name), 'a+')

# Populate text file with header information
text_file.write("Description: This text document contains test information for TIGERISS SiPM validation.\n\n")
text_file.write("Date: {0}\n\nTest apparatus details:\n".format(time_stamp))
text_file.write("     Power supply: " + ps.query("*IDN?").rstrip('\n') + "+\n")
text_file.write("     Multimeter: " + dmm.query("*IDN?").rstrip('\n') + "+\n\n")
text_file.write("DUT Details:\n     Board: {0}\n     SiPM ID: {1}\n\n".format(board_ID, SiPM_ID))
text_file.write("----------Test 1 Begin----------\n\n")

avg_volt = []
avg_curr = []
commands = []

# General Test
coarse_volt = n.arange(5, 60, 5, dtype=n.float64)
#fine_volt = n.arange(51, 55, 0.1, dtype=n.float64)
#voltset = n.sort(n.append(coarse_volt, fine_volt)).tolist()
voltset = coarse_volt

extractVbr(test_name,5)

# Power down instrument
ps.write("VOLT 0,(@1,2,3)")
ps.write("OUTP 0,(@1,2,3)")
ps.write("*CLS")
ps.close()
dmm.close()

print('\a')
plt.show()

text_file.write("----------Test completed----------\n")
text_file.close()

exit()
import numpy as n
import time
from time import gmtime, strftime, localtime, sleep
from pathlib import Path
import config
import matplotlib.pyplot as plt
import math

# Initialize instruments
def inst_init(ps, dmm):
    ps.write("*CLS")
    ps.write("*RST")
    ps.write("CURR:PROT:CLE (@1,2,3)")
    ps.write("CURR:PROT:STAT ON,(@1,2,3)")
    ps.write("CURR 0.6, (@1,2,3)")
    ps.write("VOLT 0,(@1,2,3)")
    ps.write("OUTP 1, (@1,2,3)")

    dmm.write("*RST")
    dmm.write("CONF:CURR:DC")
    dmm.write("CURR:NPLC 10")
    dmm.write("CURR:DC:TERM 3")
    dmm.write("SENS:CURR:RANG 1e-6")

def inst_off(ps, dmm):
    ps.write("*CLS")
    ps.write("VOLT 0,(@1,2,3)")
    ps.write("OUTP 0,(@1,2,3)")
    ps.write("*RST")
    ps.close()

    dmm.write("*CLS")
    dmm.write("*RST")
    dmm.close()

def filestruct_init(ps, dmm):
    # Gather date/time and open a text file
    config.time_stamp = strftime("%m%d%Y_hr%Hmin%M", localtime())
    if config.test:
        config.test_name = "Pre Shake Test 01072026"
        config.board_ID = "TSM Shake 003"
        config.SiPM_ID = "86984"
        config.text_note = "None"
    else:
        #config.test_name = input("Enter test name (Pre Shake Test, Post Shake Test).")
        config.test_name = "Pre Shake 01212026"
        config.board_ID = input("Enter the board for this SiPM (TSM Shake 003 or TSM Shake 002).")
        config.SiPM_ID = input("Enter the SiPM ID (002 TR: 87075, 002 TL: 87076, 003 BR: 87010, 003 BL: 86984).")
        #config.text_note = input("Enter any identifying notes for this test.")

    # Make board folder if it does not exist already
    config.folder_path_text = "SiPM Validation Data/{0}/{1}/{2}".format(str(config.test_name), str(config.SiPM_ID), str(config.time_stamp))
    folder_path = Path(config.folder_path_text)
    try:
        folder_path.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"Error creating directory: {e}")

    # Create and open data storage file
    config.file_name = "{0}_{1}_Data.txt".format(str(config.SiPM_ID), str(config.time_stamp))
    config.text_file = open("{0}/{1}".format(config.folder_path_text, config.file_name), 'a+')

    # Populate text file with header information
    config.text_file.write("Description: This text document contains test information for TIGERISS SiPM validation.\n\n")
    config.text_file.write("Date: {0}\n\nTest apparatus details:\n".format(config.time_stamp))
    config.text_file.write("     Power supply: " + ps.query("*IDN?").rstrip('\n') + "+\n")
    config.text_file.write("     Multimeter: " + dmm.query("*IDN?").rstrip('\n') + "+\n\n")
    config.text_file.write("DUT Details:\n     Board: {0}\n     SiPM ID: {1}\n     Limit Resistor: {2}\n\n".format(config.board_ID, config.SiPM_ID, config.prot_res))
    config.text_file.write("----------Test 1 Begin----------\n\n")

def volt_set(start,stop,step,Vbr_set):
    coarse_volt = n.arange(start, stop, step, dtype=n.float64)
    if Vbr_set == None:
        print("\n\nBeginning coarse pass...\n")
        fine_volt = []
    else:
        print("\n\nBeginning fine pass around coarse Vbr...\n")
        #del config.data[0][1]
        start = int((10 * Vbr_set) - 10)
        stop = int((10 * Vbr_set) + 10)
        fine_volt = n.arange(start, stop, 1, dtype=n.float64)
    voltset_handle = ((n.sort(n.append(coarse_volt, fine_volt))) / 10).tolist()
    config.data[0].append(voltset_handle)

def extractVbr(type, ps, dmm):
    print(config.data[0][1])
    # Obtain setpoints from storage variable
    voltset = config.data[0][1]
    avg_num = 5 if type == 'coarse' else 50

    SCPI_word = ''
    voltage_temp = []
    current_temp = []

    # Create storage variables

    voltageSDIV = currentSDIV = 0

    for i in range(len(voltset)):  # Outer loop walks through all voltage set points
        print("Set point: {0}...\n".format(voltset[i]))
        currentArray = n.zeros(avg_num, dtype=n.float64)  # current array containing floats
        voltageArray = n.zeros(avg_num, dtype=n.float64)  # voltage array containing floats
        # Set voltage; loop for 3 channels of ps
        for j in range(1, 4):  # 1, 2, 3
            mult = (5.0 if j == 1 else 30.0) / 65.0
            write_val = mult * voltset[i]
            SCPI_word = "VOLT {0}, (@{1})".format(f"{write_val:.3f}", str(j))
            print("Sending [{0}] to power supply... ".format(SCPI_word))
            ps.write(SCPI_word)
            ps.write("*WAI")

        #time.sleep(3)
        temp_c_0 = 0
        temp_c_1 = 1000

        while abs(10000000000 * (temp_c_1 - temp_c_0)) > 1.5:
            temp_c_0 = float(dmm.query("READ?"))
            dmm.write("*WAI")
            time.sleep(0.5)
            temp_c_1 = float(dmm.query("READ?"))
            dmm.write("*WAI")
            time.sleep(0.5)
            print("Temp current 0: {0}...".format(str(temp_c_0)))
            print("Temp current 1: {0}...".format(str(temp_c_1)))
            print(abs(10000000000 * (temp_c_1 - temp_c_0)) > 1.5)

        # Measure voltage and current
        for k in range(len(voltageArray)):

            SCPI_word = ps.query("MEAS:VOLT? (@1,2,3)")

            while (currentArray[k]<=0 or currentArray[k]>2):
                time.sleep(0.05)
                currentArray[k] = float(dmm.query("READ?"))
                dmm.write("*WAI")

            voltage_handle = SCPI_word.split(",")
            voltageArray[k] = sum([float(i) for i in voltage_handle])
            #voltageArray[k] = sum([float(i) for i in voltage_handle]) - currentArray[k] * float(config.prot_res)

            time.sleep(0.05)

        print("\nVoltage Samples: {0}...Current Samples: {1}\n".format(str(voltageArray), str(currentArray)))

        # Populate storage arrays
        voltageSDIV = n.std(voltageArray)
        currentSDIV = n.std(currentArray)
        voltage_temp.append(float(voltageArray.mean()))
        current_temp.append(float(currentArray.mean()))
        print("Average voltage: {0}...Average current: {1}\n".format(voltageArray.mean(),currentArray.mean()))
        SCPI_word = "VOLT {0}, (@{1})".format(f"{write_val:.3f}", str(j))
        print("Percentage complete: {0}...".format(f"{100*((i+1)/len(voltset)):.1f}"))

    Vbr_temp = Vbr_from_data(current_temp, voltage_temp)

    if type == 'fine':
        config.data[1].append(voltage_temp)
        config.data[2].append(current_temp)
    else:
        print("Coarse Vbr: {0}".format(Vbr_temp))

    ps.write("VOLT 0,(@1,2,3)")
    ps.write("*WAI")
    time.sleep(2)

    return Vbr_temp

def save_data():
    config.text_note = input("Enter any notes for this test.\n")
    temp_numpy_array = n.array(config.data[2][1])
    valid_mask = temp_numpy_array > 0
    avg_curr_log = n.full(temp_numpy_array.shape, n.nan)
    avg_curr_log[valid_mask] = n.log(temp_numpy_array[valid_mask])

    XPRIME, YPRIME = D(config.data[1][1], avg_curr_log)
    max_deriv_index = YPRIME.argmax()
    Vbr = XPRIME[max_deriv_index]

    log_i_br = find_vbr_y_value(avg_curr_log, config.data[1][1], Vbr)

    # Populate text document
    config.text_file.write("Test: {0}:\n".format(config.test_name))
    config.text_file.write("Vbr [V]: {0}\n\n".format(Vbr))
    config.text_file.write("Set-point Array [V]:\n{0}\n\n".format(config.data[0][1]))
    config.text_file.write("Voltage Array [V]:\n{0}\n\n".format(config.data[1][1]))
    config.text_file.write("Current Array [A]:\n{0}\n\n\n".format(config.data[2][1]))
    config.text_file.write("Notes: {0}\n\n\n".format(config.text_note))
    config.text_file.write("----------Test completed----------\n")
    config.text_file.close()

    # Plot the data:
    plt.figure(1)
    plt.semilogy(config.data[1][1], config.data[2][1])
    plt.xlabel('Voltage [V]')
    plt.ylabel('Current [A]')
    plt.scatter(Vbr, log_i_br, color='red')
    label = str(Vbr) + ',' + str(log_i_br)
    plt.annotate(label, (Vbr, log_i_br), textcoords="offset points", xytext=(0, 10), ha='center')
    plt.title("{0} {1} VoltVSCurr".format(config.SiPM_ID,config.test_name))
    plt.savefig("{0}/{1}_{2}_VoltVSCurr.png".format(config.folder_path_text, config.SiPM_ID,config.test_name))

    plt.figure(2)
    plt.plot(XPRIME, YPRIME)
    plt.xlabel('Reverse Voltage [V]')
    plt.ylabel('SiPM d(log(I))/d(V)')
    plt.title("{0} {1} Vbr".format(config.SiPM_ID, config.test_name))
    plt.savefig("{0}/{1}_{2}_Vbr.png".format(config.folder_path_text, config.SiPM_ID,config.test_name))

# Safely extracts Vbr with numpy log
def Vbr_from_data(current_list, voltage_list):
    temp_numpy_array = n.array(current_list)
    valid_mask = temp_numpy_array > 0
    avg_curr_log = n.full(temp_numpy_array.shape, n.nan)
    avg_curr_log[valid_mask] = n.log(temp_numpy_array[valid_mask])
    XPRIME, YPRIME = D(voltage_list, avg_curr_log)
    max_deriv_index = YPRIME.argmax()
    return XPRIME[max_deriv_index]

# Determine the numerical derivative of the dataset
def D(xlist, ylist):
    yprime = n.diff(ylist)/n.diff(xlist)
    xprime =[]
    for p in range(len(yprime)):
        xtemp = (xlist[p+1]+xlist[p])/2
        xprime = n.append(xprime,xtemp)
    return xprime, yprime

# Find associated current for plotting Vbr point on log(I) vs V plot
def find_vbr_y_value(log_curr, volt, vbr):
    for i in range(len(volt)):
        if vbr < volt[i]:
            index1 = i
            index2 = i-1
            break
    log_i = (log_curr[index1]+log_curr[index2])/2
    return log_i
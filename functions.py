import numpy as n
import time
from time import gmtime, strftime, localtime
from pathlib import Path
import config


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
    time_stamp = strftime("%m%d%Y_hr%Hmin%M", localtime())
    test_name = input("Enter test name (Pre Shake Test, Post Shake Test).")
    board_ID = input("Enter the board for this SiPM (TSM Shake 003 or TSM Shake 002).")
    SiPM_ID = input("Enter the SiPM ID (002 TR: 87075, 002 TL: 87076, 003 BR: 87010, 003 BL: 86984).")
    text_note = input("Enter any identifying notes for this test.")

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
    text_file.write("DUT Details:\n     Board: {0}\n     SiPM ID: {1}\n     Limit Resistor: {2}\n     Notes: {3}\n\n".format(board_ID, SiPM_ID, config.prot_res, text_note))
    text_file.write("----------Test 1 Begin----------\n\n")

def volt_set():
    coarse_volt = n.arange(50, 650, 50, dtype=n.float64)
    fine_volt = n.arange(510, 550, 1, dtype=n.float64)
    voltset_handle = ((n.sort(n.append(coarse_volt, fine_volt))) / 10).tolist()
    config.data[0].append(voltset_handle)

def extractVbr(test_title, avg_num, ps, dmm):

    voltset = config.data[0]

    # Create storage variables
    currentArray = n.zeros(avg_num, dtype=n.float64)  # current array containing floats
    voltageArray = n.zeros(avg_num, dtype=n.float64)  # voltage array containing floats

    for i in range(len(voltset-1)):  # Outer loop walks through all voltage set points
        # Set voltage; loop for 3 channels of ps
        for j in range(3):
            if j == 0:
                mult = (5.0 / 65.0)
            else:
                mult = (30.0 / 65.0)
            write_val = mult * voltset[i+1]
            ps.write("VOLT {0}, (@{1})".format(f"{write_val:.3f}", str(j + 1)))
            ps.write("*WAI")
            time.sleep(0.5)

# Determine the numerical derivative of the dataset
def D(xlist, ylist):
    yprime = n.diff(ylist)/n.diff(xlist)
    xprime =[]
    for p in range(len(yprime)):
        xtemp = (xlist[p+1]+xlist[p])/2
        xprime = n.append(xprime,xtemp)
    return xprime, yprime

# Find associated current for plotting Vbr point on log(I) vs V plot
def find_vbr_y_value(log_curr, volt, vbr ):
    for i in range(len(volt)):
        if vbr < volt[i]:
            index1 = i
            index2 = i-1
            break
    log_i = (log_curr[index1]+log_curr[index2])/2
    return log_i
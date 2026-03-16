# Description: This script automates SiPM Vbr validation. Two instruments are used in this test procedure:
# a high fidelity DMM and a power supply. The primary objective of this test is to gather and I-V plot for each
# SiPM device, controlling the bias voltage while measuring the DC output current. Test details
# live in the same folder as this script.
import time

# Version: 2.0
# Date: 01/04/2025

# Author: Mary Siepierski, Tom Forstmeier (tmf5239@psu.edu)

# Imports
import pyvisa as visa # Python package that provides bindings to Virtual Instrument Software Architecture (VISA)
import config
import functions
# import os

# Establish VISA  with devices
rm = visa.ResourceManager()
dmm = rm.open_resource(config.dmm_VISA) # Digital multimeter
ps = rm.open_resource(config.ps_VISA) # Power supply
# Initialize instruments
functions.inst_init(ps, dmm)

# TEST BODY

cont = 'Y'

while(cont == 'Y'):
    print('This program aims to facilitate extraction of SiPM breakdown voltage.\n\n')
    test_type = input("Select test type: \n  [1] Inflexible Vibration Test Sequence\n   [2] Programmable Vibration Test Sequence\n   [3] Test apparatus validation\n")

    # Initialize variables and filestructure

    # Switch statement
    if test_type == '1':
        functions.filestruct_init(ps, dmm, test_type)

        print("The first two SiPMs are on TSM Shake 002, which is loaded in the ")

        functions.volt_set(50, 650, 50, None)

    # Coarse pass
    functions.volt_set(50,650,50,None)
    Vbr_coarse = functions.extractVbr('save_data',ps,dmm)

    # Fine pass around Vbr
    functions.volt_set(50,650,50,52.5)
    time.sleep(5)
    config.Vbr = functions.extractVbr('fine',ps,dmm)

    # Save text data and plots to folder
    functions.save_data()



# Power down instrument
functions.inst_off(ps, dmm)

exit()
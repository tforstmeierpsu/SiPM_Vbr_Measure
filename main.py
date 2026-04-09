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

print('This program aims to facilitate extraction of SiPM breakdown voltage.\n\n')

while(cont == 'Y'):
    test_type = input("Select test type: \n  [1] Inflexible Vibration Test Sequence\n  [2] Programmable Vibration Test Sequence\n  [3] Test apparatus validation\n  [4] Exit program\n")

    # Switch statement
    if test_type == '1':
        print("---> [1] Inflexible Vibration Test Sequence...\n")
        dmm = rm.open_resource(config.dmm_VISA)  # Digital multimeter
        ps = rm.open_resource(config.ps_VISA)  # Power supply

        # Initialize filestructure
        functions.filestruct_init(ps, dmm, test_type)

        # Print test fixture information
        print("Power supply: " + ps.query("*IDN?").rstrip('\n') + "+\n")
        print("Multimeter: " + dmm.query("*IDN?").rstrip('\n') + "+\n\n")

        config.test_ct = 0

        for s in range(1, 5):
            if s == 1:
                print("First SiPM ID: 87076; Location: TSM_002 pos 8 (TR)\n")
                print("***NOTE THAT WILL HOLD CONNECTION INFORMATION (red plug vbias, etc.)***\n")
            elif s == 2:
                print("Second SiPM ID: 87075; Location: TSM_002 pos 12 (TL)\n")
                print("***NOTE THAT WILL HOLD CONNECTION INFORMATION (red plug vbias, etc.)***\n")
            elif s == 3:
                print("Third SiPM ID: 86984; Location: TSM_003 pos 21 (??)\n")
                print("***NOTE THAT WILL HOLD CONNECTION INFORMATION (red plug vbias, etc.)***\n")
            elif s == 4:
                print("Fourth SiPM ID: 87010; Location: TSM_003 pos 25 (??)\n")
                print("***NOTE THAT WILL HOLD CONNECTION INFORMATION (red plug vbias, etc.)***\n")


            functions.volt_set(50, 650, 50, None)
            config.Vbr_5 = functions.extractVbr('pre_data', ps, dmm)

            functions.volt_set(50, 650, 50, config.Vbr_5)
            config.Vbr_1 = functions.extractVbr('save_data', ps, dmm)
            functions.save_data()
            config.test_ct = config.test_ct + 1

    if test_type == '2':
        print("---> [2] Programmable Vibration Test Sequence...\n")

        dmm = rm.open_resource(config.dmm_VISA)  # Digital multimeter
        ps = rm.open_resource(config.ps_VISA)  # Power supply

        # Initialize filestructure
        functions.filestruct_init(ps, dmm, test_type)

        # Print test fixture information
        print("Power supply: " + ps.query("*IDN?").rstrip('\n') + "+\n")
        print("Multimeter: " + dmm.query("*IDN?").rstrip('\n') + "+\n\n")

        Vbr_coarse = 52.5
        functions.volt_set(50, 650, 50, Vbr_coarse)
        config.Vbr_1 = functions.extractVbr('save_data', ps, dmm)
        functions.save_data()

    if test_type == '3':
        print("---> [3] Test apparatus validation...\n")
        dmm = rm.open_resource(config.dmm_VISA)  # Digital multimeter
        ps = rm.open_resource(config.ps_VISA)  # Power supply

        # Print test fixture information
        print("   Power supply: " + ps.query("*IDN?").rstrip('\n'))
        print("   Multimeter: " + dmm.query("*IDN?").rstrip('\n'))

        functions.volt_set(0, 600, 100,'Test_Fixture')
        functions.extractVbr('pre_data',ps,dmm)
        print("Test apparatus verification completed.\n\n")

    if test_type == '4':
        cont = 'N'

# Power down instrument
functions.inst_off(ps, dmm)

exit()
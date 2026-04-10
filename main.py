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
from config import SiPM_ID
from functions import print_write

# import os

# Establish VISA
rm = visa.ResourceManager()

# TEST BODY

print('This program aims to facilitate extraction of SiPM breakdown voltage.\n\n')

while config.cont == 'Y':

    test_type = input("Select test type: \n  [1] Inflexible Vibration Test Sequence\n  [2] Programmable Vibration Test Sequence\n  [3] Test apparatus validation\n  [4] Exit program\n")

    # Switch statement
    if test_type == '1':
        print("---> [1] Inflexible Vibration Test Sequence...\n")

        # Establish communication with test instruments
        dmm = rm.open_resource(config.dmm_VISA)  # Digital multimeter
        ps = rm.open_resource(config.ps_VISA)  # Power supply

        # Initialize instruments
        functions.inst_init(ps, dmm)

        # Initialize filestructure
        functions.filestruct_init(ps, dmm, test_type)

        config.test_ct = 0

        for s in range(1, 5):
            config.board_ID = config.board_list[s]
            config.SiPM_ID = config.SiPM_ID_list[s]
            print_write("SiPM_ID: {0}; Location: {1}\n".format(config.SiPM_ID, config.board_ID))
            print("Check wiring: {0}\n".format(config.wiring[s]))

            functions.volt_set(0, 700, 100, 550, 10)
            config.Vbr_1 = functions.extractVbr('save_data', ps, dmm)
            print("First pass Vbr: {0}".format(config.Vbr_1))
            functions.save_data("1V Res")

            functions.volt_set(100, 700, 100, round(config.Vbr_1 * 10), 5)
            config.Vbr_1 = functions.extractVbr('save_data', ps, dmm)
            print("Second pass Vbr: {0}".format(config.Vbr_1))
            functions.save_data("0.5V Res")

            functions.volt_set(100, 700, 100, round(config.Vbr_1 * 100) / 10, 2.5)
            functions.extractVbr('save_data', ps, dmm)
            print("Third pass Vbr: {0}".format(config.Vbr_1))
            functions.save_data("0.25V Res")

            config.test_ct = config.test_ct + 1


    if test_type == '2':
        print("---> [2] Programmable Vibration Test Sequence...\n")

        dmm = rm.open_resource(config.dmm_VISA)  # Digital multimeter
        ps = rm.open_resource(config.ps_VISA)  # Power supply
        functions.inst_init(ps,dmm)

        # Initialize filestructure
        functions.filestruct_init(ps, dmm, test_type)

        config.board_ID = input("Enter the board for this SiPM.\n")
        config.SiPM_ID = input("Enter the SiPM ID.\n")

        functions.volt_set(100, 700, 100, 550,10)
        config.Vbr_1 = functions.extractVbr('save_data', ps, dmm)
        print("First pass Vbr: {0}".format(config.Vbr_1))
        functions.save_data("1V Res")

        functions.volt_set(100, 700, 100, round(config.Vbr_1*10),5)
        config.Vbr_1= functions.extractVbr('save_data', ps, dmm)
        print("Second pass Vbr: {0}".format(config.Vbr_1))
        functions.save_data("0.5V Res")

        functions.volt_set(100, 700, 100, round(config.Vbr_1*100)/10,2.5)
        functions.extractVbr('save_data', ps, dmm)
        print("Third pass Vbr: {0}".format(config.Vbr_1))
        functions.save_data("0.25V Res")

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
        config.cont = 'N'

# Power down instrument
functions.test_off(ps, dmm)

exit()
# Description: This script automates SiPM Vbr validation. Two instruments are used in this test procedure:
# a high fidelity DMM and a power supply. The primary objective of this test is to gather and I-V plot for each
# SiPM device, controlling the bias voltage while measuring the DC output current. Test details
# live in the same folder as this script.

# Version: 2.0
# Date: 01/04/2025

# Author: Mary Siepierski, Tom Forstmeier (tmf5239@psu.edu)

# Imports
import pyvisa as visa # Python package that provides bindings to Virtual Instrument Software Architecture (VISA)
import config
import functions
import numpy as n

# Establish VISA  with devices
#rm = visa.ResourceManager()
#ps = rm.open_resource(config.ps_VISA) # Power supply
#dmm = rm.open_resource(config.dmm_VISA) # Digital multimeter

#functions.inst_init(ps, dmm)
#functions.filestruct_init(ps, dmm)

functions.volt_set()
print(config.data[0][1])

# General Test


#extractVbr(test_name,5)

# Power down instrument
#functions.inst_off(ps, dmm)

#text_file.write("----------Test completed----------\n")
#text_file.close()

exit()
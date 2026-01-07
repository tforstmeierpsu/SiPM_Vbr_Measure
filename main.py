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
import os

# Establish VISA  with devices
rm = visa.ResourceManager()
dmm = rm.open_resource(config.dmm_VISA) # Digital multimeter
ps = rm.open_resource(config.ps_VISA) # Power supply

# Initialize instruments
functions.inst_init(ps, dmm)

# Initialize variables and filestructure
functions.filestruct_init(ps, dmm)

# TEST BODY

# Coarse pass
functions.volt_set(50,650,50,None)
Vbr_coarse = functions.extractVbr('coarse',ps,dmm)

# Fine pass around Vbr
functions.volt_set(50,650,50,Vbr_coarse)
config.Vbr = functions.extractVbr('fine',ps,dmm)

# Save text data and plots to folder
functions.save_data()

# Power down instrument
functions.inst_off(ps, dmm)

# Trigger a beep sound

exit()
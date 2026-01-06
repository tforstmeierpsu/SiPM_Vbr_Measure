import numpy as n
import time


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
            print("Set-point: {0}".format(i))
            print("VOLT {0}, (@{1})".format(f"{write_val:.3f}", str(j + 1)))
            print("\n")

            time.sleep(0.5)

        # Reset storage variables
        voltage = voltageSDIV = current = currentSDIV = 0


        # Measure voltage and current
        for k in range(len(voltageArray)):
            for l in range(3):
                voltageArray[k] = voltageArray[k] + float(ps.query("MEAS:VOLT? (@{0})".format(str(l + 1))))
                time.sleep(0.02)
            current_handle = dmm.query("READ?")
            if voltset[i] > 50.0:
                print("DMM Read? result: {0}".format(current_handle))
            currentArray[k] = float(current_handle)
            #voltageArray[k] = voltageArray[k] - currentArray[k] * float(prot_res)
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
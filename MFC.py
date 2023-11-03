import PySimpleGUI as sg
import propar
from constants import GasesFactors
from datetime import datetime
import time
import threading
import numpy as np
from serial.serialutil import SerialException


class MFC:

    def __init__(self, port, gas, tag, axis, saver):

        self.port = port
        self.gas = gas
        self.tag = tag
        self.saver = saver

        self.MFC = propar.instrument(port)

        self.serial = self.MFC.readParameter(92) or "44"
        if (len(self.serial) == 0):
            raise SerialException("Unable to connect")

        self.unit = self.MFC.readParameter(129)
        self.min = float(self.MFC.readParameter(
            183) or "0.0") * GasesFactors[self.gas]
        self.max = float(self.MFC.readParameter(
            21) or "0.0") * GasesFactors[self.gas]
        
        if ( self.max == self.min ):
            del self.MFC
            raise SerialException("Error in connection")

        self.layout = [[
            sg.Frame(f"{tag} ({gas}, {port})", [
                [sg.Text(f"SN: {self.serial}", font=('Helvetica', 7))],
                [sg.Text(f"{self.min:.1f} to {self.max:.1f} {self.unit}", font=(
                    'Helvetica', 7))],
                [sg.Text(f"...", key=f'mfc:{port}:current_value', font=(
                    'Helvetica', 18)), sg.Text(self.unit)],
                [
                    sg.Text("Target: "),
                    sg.Text(self.get_current_set_value(str=True),
                            key=f'mfc:{port}:target_value'),
                    sg.Input(
                        default_text=self.get_current_set_value(str=True), key=f'mfc:{port}:set_point', size=8)
                ],
                [sg.ProgressBar(max_value=100, orientation='h',
                                size=(40, 10), key=f'mfc:{port}:progress')]
            ])
        ]]

        self.data = {
            'times': [],
            'reads': []
        }

        self.thread = threading.Thread(target=self.pool_thrd)
        self.thread.start()

        self.line, = axis.plot([], [], label=tag)

    def bind_events(self, window):
        window[f'mfc:{self.port}:set_point'].bind("<Return>", "_Enter")

    def parse_events(self, event, values, window):

        if event == f'mfc:{self.port}:set_point_Enter':

            try:
                setpoint = float(values[f'mfc:{self.port}:set_point'])
                if (setpoint > self.max):
                    setpoint = self.max
                if (setpoint < self.min):
                    setpoint = self.min
                self.set_current_set_value(setpoint)
                window[f'mfc:{self.port}:set_point'].update(
                    self.get_current_set_value(str=True))
            except ValueError:
                return

    def update_window(self, window):

        # Read
        if (len(self.data['reads']) > 0):
            window[f'mfc:{self.port}:current_value'].update(
                f"{self.data['reads'][-1]:.2f}")

        # Set point
        window[f'mfc:{self.port}:target_value'].update(
            self.get_current_set_value(str=True))
        window[f'mfc:{self.port}:progress'].update(
            current_count=(self.get_current_set_value() - self.min) / (self.max - self.min) * 100)

        # Plot
        self.line.set_data((np.array(
            self.data['times']) - datetime.now().timestamp()) / 60, self.data['reads'])

    def pool_thrd(self):
        while True:
            try:
                newval = self.get_current_value()
                newtime = datetime.now().timestamp()
                self.data['reads'].append(newval)
                self.data['times'].append(newtime)
                self.saver.save_callback(self, newtime, newval)
            except Exception:
                pass

            time.sleep(0.1)

    def get_current_value(self, str=False):
        meas = float(self.MFC.readParameter(205) or "0.0") * \
            GasesFactors[self.gas]
        if (str):
            return f"{meas:.2f}"
        return meas

    def get_current_set_value(self, str=False):
        meas = float(self.MFC.readParameter(206) or "0.0") * \
            GasesFactors[self.gas]
        if (str):
            return f"{meas:.2f}"
        return meas

    def set_current_set_value(self, val):
        self.MFC.writeParameter(206, val / GasesFactors[self.gas])

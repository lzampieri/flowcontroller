import PySimpleGUI as sg
import AddMFCWindow
import Saver
import MFC
import SmoothTransition
from serial.serialutil import SerialException

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')


class MainWindow:

    def __init__(self):

        self.MFC_ID = 0
        self.connectedMFC = []

        self.saver = Saver.Saver(self.connectedMFC)
        self.st = SmoothTransition.SmoothTransition(self.connectedMFC)

        self.layout = [[
            sg.Column([
                [sg.Text("0", key="main:cnum"), sg.Text(" MFC connessi")],
                [sg.Column([], key="main:col")],
                [sg.Button("Aggiungi MFC", key='main:addMFC')],
                self.saver.layout,
                self.st.layout,
                [sg.Text("L. Zampieri - 11/2023", font=('Helvetica', 7))]
            ]),
            sg.Canvas(key='canvas')
        ]]

        sg.theme('Dark')
        self.window = sg.Window(title="Flow Controller",
                                layout=self.layout, finalize=True)

        self.init_plot()
        self.st.refreshMFC()

        # TODO remove
        if (len(self.connectedMFC) == 0):
            self.addMFC()

    def init_plot(self):
        self.fig = matplotlib.figure.Figure(figsize=(5, 4), dpi=100)
        self.axis = self.fig.add_subplot(111)
        self.tkcanvas = FigureCanvasTkAgg(
            self.fig, self.window['canvas'].TKCanvas)
        self.tkcanvas.draw()
        self.tkcanvas.get_tk_widget().pack(side='top', fill='both', expand=1)

        self.axis.set_xlim(- 5, 0)
        self.axis.set_xlabel("Time [min]")

    def loop(self):
        while True:
            event, values = self.window.read(timeout=100)

            if (event == 'main:addMFC'):
                self.addMFC()

            if event == sg.WIN_CLOSED:
                return

            for MFC in self.connectedMFC:
                MFC.parse_events(event, values, self.window)

            self.saver.parse_events(event, values, self.window)

            if( self.st is not None ):
                self.st.parse_mainwindow_events( event, values )

            for MFC in self.connectedMFC:
                MFC.update_window(self.window)

            self.axis.relim()  # scale the y scale
            self.axis.autoscale_view()  # scale the y scale
            self.tkcanvas.draw()

    def addMFC(self):
        amw = AddMFCWindow.AddMFCWindow(
            alreadyConn=[d.port for d in self.connectedMFC])
        newMFC = amw.run()
        if (newMFC):
            self.saveMFC(newMFC)

    def saveMFC(self, data):
        try:
            self.MFC_ID += 1
            newMFC = MFC.MFC(**data, axis=self.axis,
                             saver=self.saver, ID=self.MFC_ID)
        except SerialException as e:
            sg.popup_error("Impossibile connettersi alla porta")
            return

        self.connectedMFC.append(newMFC)
        self.window.extend_layout(self.window['main:col'], newMFC.layout)
        newMFC.bind_events(self.window)
        self.window['main:cnum'].update(len(self.connectedMFC))
        self.axis.legend()
        
        self.st.refreshMFC()

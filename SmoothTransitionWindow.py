import PySimpleGUI as sg
import threading

class SmoothTransitionWindow:

    def __init__(self, connectedMFC):

        self.connectedMFC = connectedMFC

        self.layout = [[
            sg.Column([
                [sg.Frame("MFC", [[sg.Column([], key="st:col")]])],
                [sg.Text("Durata [s]: "), sg.Input("30", key="st:duration")],
                [
                    sg.Button("Start", key="sg:start"),
                    sg.Button("Abort", key="sg:abort", disabled=True),
                    sg.Button("Refresh MFC", key="sg:refresh")],
                [sg.ProgressBar(100, orientation='h', size=(
                    40, 10), key='sg:progress')],
            ]),
        ]]

        # sg.theme('Dark')
        self.window = sg.Window(title="Smooth Transition",
                                layout=self.layout, finalize=True)

        self.refreshMFC()

        self.loopthread = threading.Thread( target=self.loop )

    def loop( self ):
        while True:
            event, values = self.window.read(timeout=100)

            if( event == 'sg:refresh' ):
                self.refreshMFC()

            print(event)

    def parse_mainwindow_events(self, event, values):
        pass

    def refreshMFC(self):
        for MFC in self.connectedMFC:
            print(MFC.ID)
            if f'st:{MFC.ID}' not in self.window.AllKeysDict:
                self.window.extend_layout(self.window['st:col'], [[
                    sg.Text(f"{MFC.tag} ({MFC.gas}): from "),
                    sg.Input(default_text=MFC.get_current_set_value(str=True), key=f"st:{MFC.ID}:from", size=7),
                    sg.Text(" to "),
                    sg.Input(default_text=MFC.get_current_set_value(str=True), key=f"st:{MFC.ID}:to", size=7),
                ]])
import PySimpleGUI as sg


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

    def parse_events(self, event, values, window):
        if( event == 'sg:refresh' ):
            self.refreshMFC()
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
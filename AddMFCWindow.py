import PySimpleGUI as sg
from serial.tools import list_ports
from constants import GasesFactors


class AddMFCWindow:

    def __init__(self, alreadyConn):
        self.layout = [[
            sg.Column([
                [sg.Text("Aggiungi MFC", font=('Helvetica', 20))],
                [sg.Text("Porta:")],
                [sg.Combo([], key='addMFC:ports_combo',
                          expand_x=True, size=(50, 10), readonly=True), sg.Button("↻", key="addMFC:refresh")],
                [sg.Text("Gas:")],
                [sg.Combo(list(GasesFactors.keys()), key='addMFC:gases_combo',
                          expand_x=True, size=(50, 10), readonly=True, default_value='Air')],
                [sg.Text("Nome:")],
                [sg.Input(
                    default_text=f"MFC{len(alreadyConn)+1}", key="addMFC:tag")],
                [sg.Button('Salva', key='addMFC:save'), sg.Text('Errore', text_color='red',
                                                                key='addMFC:error', visible=False)]
            ])
        ]]

        self.window = sg.Window(title="Aggiungi MFC",
                                layout=self.layout)

        self.alreadyConn = alreadyConn

    def refresh_ports(self):
        ports = list(filter(lambda p: p.device not in self.alreadyConn,
                            list_ports.comports()))
        self.window['addMFC:ports_combo'].update(
            values=[p for p in ports], value=(ports[0] if len(ports) > 0 else ""))

    def run(self):
        self.window.finalize()
        self.refresh_ports()

        return self.loop()

    def loop(self):
        while True:
            event, values = self.window.read(timeout=100)

            if event == 'addMFC:refresh':
                self.refresh_ports()

            if event == sg.WIN_CLOSED:
                return False

            if event == 'addMFC:save':

                # Check for port
                port = getattr( values['addMFC:ports_combo'], 'device', "" )

                if port not in [p.device for p in list_ports.comports()]:
                    self.showError('Porta non valida')
                    continue
                if port in [self.alreadyConn]:
                    self.showError('Porta già registrata')
                    continue

                # Check for gas
                gas = values['addMFC:gases_combo']

                if gas not in GasesFactors.keys():
                    self.showError('Gas non valido')
                    continue

                # Load the tag
                tag = values['addMFC:tag']

                self.window.close()
                return {
                    'port': port,
                    'gas': gas,
                    'tag': tag
                }

    def showError(self, error):
        self.window['addMFC:error'].update(error, visible=True)

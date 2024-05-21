import pandas as pd
import PySimpleGUI as sg
from serial.tools import list_ports
import propar

class ConfSaver:
    def __init__(self, connectedMFC, saveMFC):
        self.connectedMFC = connectedMFC
        self.saveMFC = saveMFC

        self.layout = [
            sg.Button("Salva conf.", key="conf:save"),
            sg.Button("Carica conf.", key="conf:load")]

    def parse_events(self, event, values, window):

        if event == "conf:save":
            self.save()

        if event == "conf:load":
            self.load()

    def save(self):
        pd.DataFrame.from_records([{
            'serial': MFC.serial,
            'gas': MFC.gas,
            'tag': MFC.tag
        } for MFC in self.connectedMFC]).to_csv("flowcontroller_ser.conf", index=False)

    def load(self):
        try:
            data = pd.read_csv("flowcontroller_ser.conf",
                               index_col=0).to_dict("index")

            # Scan over all the ports
            occupied_ports = [d.port for d in self.connectedMFC]
            available_ports = [ d.device for d in list_ports.comports() if d.device not in occupied_ports ]
            for p in available_ports:
                print( f"Checking port {p}" )
                try:
                    # Try to open the port
                    device = propar.instrument(p)
                    # Read the serial
                    serial = ( device.readParameter(92) or "44" ).strip()
                    if( serial in data.keys() ):
                        # device.master.stop()
                        self.saveMFC( p, data[serial]['gas'], data[serial]['tag'] )
                        continue
                    else:
                        print(f"Nothing found on port {p}")
                except Exception as e:
                    print(f"Nothing found on port {p}; {e}")
                    continue

        except FileNotFoundError as e:
            sg.popup_error("Impossibile trovare una configurazione salvata")
            return

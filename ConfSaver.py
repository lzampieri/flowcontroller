import pandas as pd
import PySimpleGUI as sg

class ConfSaver:
    def __init__( self, connectedMFC, saveMFC ):
        self.connectedMFC = connectedMFC
        self.saveMFC = saveMFC

        self.layout = [
            sg.Button( "Salva conf.", key="conf:save" ),
            sg.Button( "Carica conf.", key="conf:load" )  ]

    def parse_events(self, event, values, window):

        if event == "conf:save":
            self.save()

        if event == "conf:load":
            self.load()
            window['conf:load'].update( disabled=True )

    def save(self):
        pd.DataFrame.from_records([ {
            'port': MFC.port,
            'gas': MFC.gas,
            'tag': MFC.tag
        } for MFC in self.connectedMFC ]).to_csv( "flowcontroller.conf", index=False )

    def load(self):
        try:
            data = pd.read_csv( "flowcontroller.conf", index_col=False ).to_dict( "records" )
            for d in data:
                self.saveMFC( d )
        except FileNotFoundError as e:
            sg.popup_error("Impossibile trovare una configurazione salvata")
            return

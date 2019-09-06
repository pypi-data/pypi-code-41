"""
Example accessing API of the Fake Temperature Device
"""


import loader, protocol

class Cleverlab:
    accessManager = None
    token = None

    def __init__(self, name, password):
        # Do Login
        self.accessManager = protocol.AccessManager(name, password)
        self.token = self.accessManager.login()[1]
        print("logged in")

    def addNote(self,note):
        notemakerDescriptor = loader.DeviceDescriptor(loader.Protocol.CLEVERLAB, "cleverlab.ai", "laboratory-note-maker")
        # Example: add a new note, raise error if not succeed
        if 1 == 1:
            storeNoteRequest = notemakerDescriptor.newMessage("StoreNoteRequest")
            storeNoteRequest.Note.Id = 0 # server will generate itself, useless to set this by client
            storeNoteRequest.Note.Timestamp = 0 # server will generate itself, useless to set this by client
            storeNoteRequest.Note.Content = note
            result = protocol.makeRequest(self.token, notemakerDescriptor, storeNoteRequest)

            storeNoteResponse = notemakerDescriptor.newMessage("StoreNoteResponse")
            newNoteId =  protocol.deserializeMessage(storeNoteResponse, result).Id
            print("New note ID:", newNoteId)

    def getNoteList(self):
        notemakerDescriptor = loader.DeviceDescriptor(loader.Protocol.CLEVERLAB, "cleverlab.ai", "laboratory-note-maker")
        # Example query for note öist
        getNotesRequest = notemakerDescriptor.newMessage("GetNoteListRequest")
        getNotesRequest.Offset = 0 # Offset remain untouch or set as 0: no offset
        getNotesRequest.Limit = 0 # Limit remain untouch or set as 0: no limit
        result = protocol.makeRequest(self.token, notemakerDescriptor, getNotesRequest)

        getNoteListResponse = notemakerDescriptor.newMessage("GetNoteListResponse")
        print(protocol.deserializeMessage(getNoteListResponse, result).Notes)

    def getTemperature(self):
        # Load device Descirptor
        deviceDescriptor = loader.DeviceDescriptor(loader.Protocol.CLEVERLAB, "cleverlab.ai", "system-enviroment")
        
        getEnvRequest = deviceDescriptor.newMessage("GetSysEnviromentRequest")
        #Invoke request
        result = protocol.makeRequest(self.token, deviceDescriptor, getEnvRequest)

        # build response receiving object
        getEnvResponse = deviceDescriptor.newMessage("GetSysEnviromentResponse")
        # parse response into object just built and print the 'Value' field set
        print(protocol.deserializeMessage(getEnvResponse, result))


    def logout():
        # cleanup
        self.accessManager.logout()
        print("logged out...")
"""
Example accessing API of the Fake Temperature Device
"""


import loader, protocol

def getTemp():
    # Do Login
    accessManager = protocol.AccessManager("test", "cleverlab")
    isok, token = accessManager.login()

    # Load device Descirptor
    fakeTempDeviceDescriptor = loader.DeviceDescriptor(loader.Protocol.CLEVERLAB, "cleverlab.ai", "test-temperature")

    print("This device having message types avalible:", fakeTempDeviceDescriptor.messageTypesAvailable())



    #### Get Temperature 

    # Build request message: GetTempertureRequest take no arguments (See devices/CL.cleverlab.ai.test-temperature.proto) 
    getTempRequest = fakeTempDeviceDescriptor.newMessage("GetTempertureRequest")
    #Invoke request
    result = protocol.makeRequest(token, fakeTempDeviceDescriptor, getTempRequest)

    # build response receiving object
    getTempResponse = fakeTempDeviceDescriptor.newMessage("GetTempertureResponse")
    # parse response into object just built and print the 'Value' field set
    print(protocol.deserializeMessage(getTempResponse, result).Value)


    """
    Example accessing API of the laboratory notemaker
    """

    notemakerDescriptor = loader.DeviceDescriptor(loader.Protocol.CLEVERLAB, "cleverlab.ai", "laboratory-note-maker")

    print("This device involving with message types:", notemakerDescriptor.messageTypesAvailable())

    # Example: add a new note, raise error if not succeed
    if 1 == 1:
        storeNoteRequest = notemakerDescriptor.newMessage("StoreNoteRequest")
        storeNoteRequest.Note.Id = 0 # server will generate itself, useless to set this by client
        storeNoteRequest.Note.Timestamp = 0 # server will generate itself, useless to set this by client
        storeNoteRequest.Note.Content = "this is a new note"
        result = protocol.makeRequest(token, notemakerDescriptor, storeNoteRequest)

        storeNoteResponse = notemakerDescriptor.newMessage("StoreNoteResponse")
        newNoteId =  protocol.deserializeMessage(storeNoteResponse, result).Id
        print("New note ID:", newNoteId)

    # Example: edit a existed not, raise error if not succeed
    if 1 == 1:
        editNotesRequest = notemakerDescriptor.newMessage("EditNoteRequest")
        editNotesRequest.Id = newNoteId
        editNotesRequest.Newcontent = "test"
        result = protocol.makeRequest(token, notemakerDescriptor, editNotesRequest)

    # Example: delete a note by id, raise error if not succeed
    if 1 == 1:
        delNotesRequest = notemakerDescriptor.newMessage("DeleteNoteRequest")
        delNotesRequest.Id = newNoteId
        result = protocol.makeRequest(token, notemakerDescriptor, delNotesRequest)

    # Example query for note öist
    getNotesRequest = notemakerDescriptor.newMessage("GetNoteListRequest")
    getNotesRequest.Offset = 0 # Offset remain untouch or set as 0: no offset
    getNotesRequest.Limit = 0 # Limit remain untouch or set as 0: no limit
    result = protocol.makeRequest(token, notemakerDescriptor, getNotesRequest)

    getNoteListResponse = notemakerDescriptor.newMessage("GetNoteListResponse")
    print(protocol.deserializeMessage(getNoteListResponse, result).Notes)


    # cleanup
    accessManager.logout()
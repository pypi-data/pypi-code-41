# psf: ta=4, -*-Python-*-, vi: set et ts=4: coding: utf-8
#
__doc__ = """
  This module holds patterns for the different:

   -  commands (Remote/local)
   -  Email messages (subject and text)
   -  logging messages
"""


def this_function_is_for_documentation_only():
    pass


import inspect

PATTERN_LANGUAGES = ["DE", "EN"]
SUBJECT_PATTERNS = {
    "DE": {
        "PROD_LOCKED": "%(snapshot_name)s LOCKED ",
        "NO_PID": "Fehler beim Transfer aus %(sourcedir_p)s von %(snapshot_name)s",
        "NO_EMAIL_TO": "Fehler beim Transfer aus %(sourcedir_p)s von %(snapshot_name)s",
        "SUCC_TRANSFER": "[SYSTEM-DATA] SUCCESS %(user_identification)s:%(PID)s transfer ",
        "FAIL_TRANSFER": "[SYSTEM-DATA] FAILURE %(user_identification)s:%(PID)s transfer ",
        "RSYNC_FAILED": "Der rsync Aufruf/transfer hatte einen Fehler. Abort now.",
        "RSYNC_SUCC": "SUCCESS rsync uebermittelte %(asia_cloud_host)s/%(srcdir_on_asia_host)s ==>%(PATH_TO_LOCAL_MIRROR_DIR)s",
        "QUARANTINED_TRANSFER": "Fehler beim Viruscheck",
        "FAIL_PRODMON_NOTIFICATION": "Fehler beim prodmon Aufruf   %(theurl)s fuer %(dst)s ",
        "SUCC_PRODMON_NOTIFICATION": "Erfolgreicher prodmon Aufruf %(theurl)s fuer %(dst)s ",
    },
    "EN": {
        "PROD_LOCKED": "%(snapshot_name)s LOCKED ",
        "NO_PID": "Error in Transfer from %(sourcedir_p)s of %(snapshot_name)s",
        "NO_EMAIL_TO": "Error in Transfer from %(sourcedir_p)s of %(snapshot_name)s",
        "SUCC_TRANSFER": "[SYSTEM-DATA] SUCCESS %(user_identification)s:%(PID)s transfer ",
        "FAIL_TRANSFER": "[SYSTEM-DATA] FAILURE %(user_identification)s:%(PID)s transfer ",
        "RSYNC_FAILED": "The rsync transfer exited with an error. Abort now.",
        "RSYNC_SUCC": "SUCCESS rsync transfered %(asia_cloud_host)s/%(srcdir_on_asia_host)s ==>%(PATH_TO_LOCAL_MIRROR_DIR)s",
        "QUARANTINED_TRANSFER": "Suspicous transmission qurantined ",
        "FAIL_PRODMON_NOTIFICATION": "FAILURE %(dst)s for %(theurl)s",
        "SUCC_PRODMON_NOTIFICATION": "SUCCESS %(dst)s for %(theurl)s",
    },
}
TEXT_PATTERNS = {
    "DE": {
        "PROD_LOCKED": "%(snapshot_name)s LOCKED ",
        "NO_PID": "PID aus ~/body konnte nicht bestimmt werden<br> s",
        "NO_EMAIL_TO": "Empfaenger konnten nicht bestimmt werden. Existiert  ~/mail?<br> ",
        "SUCC_TRANSFER": "%(PID)s<br>Kuerzel: %(Kuerzel)s<br>Bezeichnung: %(Bezeichnung)s<br>%(MESSAGE)s<br>%(email_footer)s<br> <br>",
        "FAIL_TRANSFER": "%(PID)s<br>Kuerzel: %(Kuerzel)s<br>Bezeichnung: %(Bezeichnung)s<br>%(MESSAGE)s<br>%(email_footer)s<br>  ----  <br>%(retval)s <br> ",
        "RSYNC_FAILED": "Der rsync Aufruf/transfer hatte einen Fehler. Abort now.",
        "RSYNC_SUCC": "SUCCESS rsync uebermittelte %(asia_cloud_host)s/%(srcdir_on_asia_host)s ==>%(PATH_TO_LOCAL_MIRROR_DIR)s",
        "QUARANTINED_TRANSFER": "Fehler beim Viruscheck <br> %(cmd)s",
        "FAIL_PRODMON_NOTIFICATION": "Fehler beim prodmon Aufruf %(dst)s   fuer %(theurl)s %(html)s",
        "SUCC_PRODMON_NOTIFICATION": "Erfolgreicher prodmon Aufruf %(dst)s fuer %(theurl)s %(html)s",

    },
    "EN": {
        "PROD_LOCKED": "%(snapshot_name)s LOCKED ",
        "NO_PID": "PID in ~/body not found <br> ",
        "NO_EMAIL_TO": "Unable to locate E-Mail Address.  Does ~/mail exist?<br> ",
        "SUCC_TRANSFER": "%(PID)s<br>shortname: %(Kuerzel)s<br>title:  %(Bezeichnung)s<br>%(MESSAGE)s<br>%(email_footer)s<br>",
        "FAIL_TRANSFER": "%(PID)s<br>shortname: %(Kuerzel)s<br>title:  %(Bezeichnung)s<br>%(MESSAGE)s<br>%(email_footer)s<br> \
                     ----  <br>%(retval)s <br> ",
        "RSYNC_FAILED": "The rsync transfer exited with an error. Abort now.",
        "RSYNC_SUCC": "SUCCESS rsync transfered %(asia_cloud_host)s/%(srcdir_on_asia_host)s ==>%(PATH_TO_LOCAL_MIRROR_DIR)s",
        "QUARANTINED_TRANSFER": "Suspicous transmission qurantined  %(cmd)s ",
        "FAIL_PRODMON_NOTIFICATION": "FAILURE %(dst)s for %(theurl)s %(html)s",
        "SUCC_PRODMON_NOTIFICATION": "SUCCESS %(dst)s for %(theurl)s %(html)s",

    },
}

LOGGING_PATTERNS = {
    "DE": {
        "CREATE_INPROGRESS_DIR": "LOCK Verzeichnis %(name)s angelegt",
        "PROD_LOCKED": "%(snapshot_name)s LOCKED ",
        "NO_PID": "%(snapshot_name)s hatt keine PID:      in %(sourcedir_p)s/%(snapshot_name)s/body",
        "NO_EMAIL_TO": "%(snapshot_name)s hat keine  EMAIL_TO: in %(sourcedir_p)s/%(snapshot_name)s/mail",
        "SUCC_TRANSFER": "%(MESSAGE)s",
        "FAIL_TRANSFER": "[SYSTEM-DATA] FAILURE %(user_identification)s:%(PID)s transfer ",
        "EMAIL_FOOTER": 'Bei Fragen bitte an _EP-Produktionsstrecke wenden.',
        "PREPARE_CALLED": "prepare aufgerufen, fand:    %(l_product_snapshots)s )",
        "CREATED_CLOUD_LOCKFILE": "%(cloud_lockfile_name)s CREATED",
        "ERROR_RM_CLOUD_LOCKFILE": "FEHLER %(cloud_lockfile_name)s kann nicht geloescht werden.",
        "ERROR_CREATED_CLOUD_LOCKFILE": "Fehler %(cloud_lockfile_name)s konnte nicht angelegt werden",
        "ALREADY_IN_TRANSFER": "%(snapshot_name)s  bereits in transfer - ???? ",
        "NOT_LOCKED": "%(snapshot_name)s  ist nicht gesperrt",
        "TRANSFER_SUCC": "SUCCESS: Transfer von %(user_identification)s:%(sourcedir_p)s/%(snapshot_name)s \
                                     zur SYSTEM-EU Machine",
        "TRANSFER_FAIL": "FAILURE Transfer von %(user_identification)s:%(sourcedir_p)s/%(snapshot_name)s \
                                     zur SYSTEM-EU Machine",
        "CLOUD_TRANSFER_LOCKED": "%(cloud_lockfile_name)s existiert. Transfer gesperrt!",
        # TRANSFER
        "TRANSFER_STARTED": "Transfer von %(path_to_product_dir)s initiiert",
        "TRANSFER_NO_PROD_FOUND": "%(path_to_product_dir)s ist kein Verzeichnis - Abort",
        "INITIAL_TRANSFER": "Es ist ein initialer transfer  des Produktes %(product_name)s",
        "NO_INITIAL_TRANSFER": "%(destination_dir)s/%(product_name)s-* existiert  (%(dirname_found)s)",
        "ALREADY_TRANSFERED": "%(product_id_stamp_p)s bereits transferiert",
        "CHK_IF_TRANSFER_WAS_OK": "Pruefe, ob der vorherige  transfer von %(product_id_stamp_p)s erfolgreich war.",
        "PRECEEDING_TRANSF_OK": "Der vorherige  transfer von %(product_id_stamp_p)s war erfolgreich. Skip Retransmission",
        "PRECEEDING_TRANSF_FAIL": "FAILURE des vorherigen  transfers von %(product_id_stamp_p)s ",
        "MAYBE_REMOVE_WORK": "Ggf. muss %(product_id_stamp_p)s auf Zielrechner geloescht werden. ",
        "TRY_RETRANSMISSION": "Versuche Retransmission .... . ",
        "VERSION_IS_BASE_FOR_RSYNC": "Die neueste Version %(dirname_found)s,  wird als rsync-basis fuer %(product_id_stamp_p)s genommen. ",
        "SSH_EXIT_CODE_VULNERABILITY": "cp -al %(dirname_found)s ==>  %(product_id_stamp_p)s.",
        "RSYNC_FAILED": "Der rsync Aufruf/transfer hatte einen Fehler. Abort now.",
        "RSYNC_SUCC": "SUCCESS rsync uebermittelte %(path_to_product_dir)s",
        "TOUCH_TRANSM_OK_FILE_SUCC": "SUCCESS anlegen OK Datei in %(destination_dir)s/%(product_id_stamp_p)s",
        "TOUCH_TRANSM_OK_FILE_FAIL": "FAILURE.Anlegen remote OK File. Abort Now.",
        "START_FREESPACE": "===== Bereinige Festplatte fuer %(product_name)s falls moeglich ========",
        "NUMBER_OF_FOUND_OK_FILES": "Anzahl %(number_of_ok_files)d gefundener OK-Files auf der remote site",
        "ERR_NUMBER_OF_FOUND_OK_FILES": "FAILURE beim zaehlen der remote OK Dateien. Abort Now.",
        "AMOUNT_PRODUCT_DIRS_SUCC": "%(number_of_products_dirs)s product Verzeichnisse auf der remote site gefunden.",
        "ERR_AMOUNT_PRODUCT_DIRS": "FAILURE. Zaehlen der remote OK Dateien. Abort Now.",
        "RM_DATA_ON_REMOTE": "Loesche altes Verzeichnis %(name_of_oldest_product_dir)s auf remote",
        "RM_DATA_ON_REMOTE_SUCC": "SUCCESS Loesche altes Verzeichnis %(name_of_oldest_product_dir)s",
        "RM_DATA_ON_REMOTE_FAIL": "FAILURE Loesche altes Verzeichnis %(name_of_oldest_product_dir)s",
        "CALL_HELP_FOR_CLEANUP": "Anzahl ok-Files ungleich der Anzahl der Datenverzeichnisse - bitte aufraumen",
        "NOTHING_TO_CLEAN": "Es wurde kein Speicherplatz freigegeben.",
        "AVAILABLE_OK_FILES": "Die vorhanden ok Files: %(ok_files)s",
        "AVAILABLE_PRODUCT_DIRS": "Die vorhanden Verzeichnisse %(l_product_dirs)s",
        "RSYNC_FAILED": "Der rsync Aufruf/transfer hatte einen Fehler. Abort now.",
        "RSYNC_SUCC": "SUCCESS ",
        "LANGUAGE_PATTERN_FAILED": "Fehler beim setzen der LANGUAGE_PATTERN. Verwende default %(PATTERN_LANGUAGE)s.",

    },
    "EN": {
        "CREATE_INPROGRESS_DIR": "LOCK Directory %(name)s created",
        "PROD_LOCKED": "%(snapshot_name)s LOCKED ",
        "NO_PID": "%(snapshot_name)s has no PID:      in file %(sourcedir_p)s/%(snapshot_name)s/body",
        "NO_EMAIL_TO": "%(snapshot_name)s has no EMAIL_TO: in file %(sourcedir_p)s/%(snapshot_name)s/mail",
        "SUCC_TRANSFER": "%(MESSAGE)s",
        "FAIL_TRANSFER": "[SYSTEM-DATA] FAILURE %(user_identification)s:%(PID)s transfer ",
        "EMAIL_FOOTER": "In case of questions ... contact  xx@somewhere.com.",
        "PREPARE_CALLED": " prepare Called, found:    %(l_product_snapshots)s )",
        "CREATED_CLOUD_LOCKFILE": "%(cloud_lockfile_name)s CREATED",
        "ERROR_RM_CLOUD_LOCKFILE": "FAILURE %(cloud_lockfile_name)s could not be deleted.",
        "ERROR_CREATED_CLOUD_LOCKFILE": "FAILURE %(cloud_lockfile_name)s NOT CREATED",
        "ALREADY_IN_TRANSFER": "%(snapshot_name)s  already in transfer - ???? ",
        "NOT_LOCKED": "%(snapshot_name)s  is not locked",
        "TRANSFER_SUCC": "SUCCESS: Transfer from %(user_identification)s:%(sourcedir_p)s/%(snapshot_name)s \
                                     to DEST Machine",
        "TRANSFER_FAIL": "FAILURE Transfer from %(user_identification)s:%(sourcedir_p)s/%(snapshot_name)s \
                                     to DEST Machine",
        "CLOUD_TRANSFER_LOCKED": "%(cloud_lockfile_name)s existits. Transfer blocked!",
        # TRANSFER
        "TRANSFER_STARTED": "Transfer of %(path_to_product_dir)s Initiated",
        "TRANSFER_NO_PROD_FOUND": "%(path_to_product_dir)s Not a file - Abort",
        "INITIAL_TRANSFER": "It is an initial transfer  of product %(product_name)s",
        "NO_INITIAL_TRANSFER": "%(destination_dir)s/%(product_name)s-* exists (%(dirname_found)s)",
        "ALREADY_TRANSFERED": "%(product_id_stamp_p)s already transfered",
        "CHK_IF_TRANSFER_WAS_OK": "Check, if the (before) transfer of %(product_id_stamp_p)s was successfull",
        "PRECEEDING_TRANSF_OK": "The (before) transfer of %(product_id_stamp_p)s was successfull. Skip Retransmission",
        "PRECEEDING_TRANSF_FAIL": "FAILURE of the (before) transfer of %(product_id_stamp_p)s ",
        "MAYBE_REMOVE_WORK": "Maybe a remove of %(product_id_stamp_p)s on destination host is necessary. ",
        "TRY_RETRANSMISSION": "Try Retransmission .... . ",
        "VERSION_IS_BASE_FOR_RSYNC": "The newest version %(dirname_found)s,  will be the rsync-base for %(product_id_stamp_p)s ",
        "SSH_EXIT_CODE_VULNERABILITY": "DO NOT CARE ON SUCCESS cp -al %(dirname_found)s to  %(product_id_stamp_p)s ",
        "RSYNC_FAILED": "The rsync transfer exited with an error. Abort now.",
        "RSYNC_SUCC": "SUCCESS rsync transfering %(path_to_product_dir)s",
        "TOUCH_TRANSM_OK_FILE_SUCC": "SUCCESS creating OK file in %(destination_dir)s/%(product_id_stamp_p)s",
        "TOUCH_TRANSM_OK_FILE_FAIL": "Creating Remote OK File Failed. Abort Now.",
        "START_FREESPACE": "===== FREE DISK SPACE for %(product_name)s IF POSSIBLE ========",
        "NUMBER_OF_FOUND_OK_FILES": "Found %(number_of_ok_files)d OK-Files on the remote site",
        "ERR_NUMBER_OF_FOUND_OK_FILES": "Unable to count the remote OK File. Abort Now.",
        "AMOUNT_PRODUCT_DIRS_SUCC": "Found %(number_of_products_dirs)s product dirs on the remote site",
        "ERR_AMOUNT_PRODUCT_DIRS": "Unable to count the product dirs on the remote site . Abort Now.",
        "RM_DATA_ON_REMOTE": "REMOVE DATA ON DESTINATION %(name_of_oldest_product_dir)s",
        "RM_DATA_ON_REMOTE_SUCC": "SUCCESS REMOVE DATA ON DESTINATION %(name_of_oldest_product_dir)s",
        "RM_DATA_ON_REMOTE_FAIL": "FAILURE REMOVE DATA ON DESTINATION %(name_of_oldest_product_dir)s",
        "CALL_HELP_FOR_CLEANUP": "Amount of ok-Files does not match amount of Data directories - please take care",
        "NOTHING_TO_CLEAN": "No disk space freed on remote machine.",
        "AVAILABLE_OK_FILES": "Available ok Files: %(ok_files)s",
        "AVAILABLE_PRODUCT_DIRS": "Available Data directories %(l_product_dirs)s",
        "RSYNC_FAILED": "The rsync transfer exited with an error. Abort now.",
        "RSYNC_SUCC": "SUCCESS",
        "LANGUAGE_PATTERN_FAILED": "Error setting PATTERN_LANGUAGE. Use default %(PATTERN_LANGUAGE)s.",

    },
}

PATTERN_NAMES = [name for name in globals().keys() if name.endswith("PATTERNS")]

LOCAL_SHELL_CMDS = {
    # USED IN PREPARE
    "L_TOUCH_CLOUD_LOCKFILE": "touch %(cloud_lockfile_name)s",
    "L_TOUCH_PROD_LOCKFILE": "touch %(product_lockfile_name)s",
    "L_ZIP_TAR_INTO_PRODUCT_DIR": "gzip %(sourcedir_p)s/ERROR/%(snapshot_name)s-%(prepare_started_at)s.tar.gz \
                                  %(sourcedir_p)s/%(snapshot_name)s ",
    "L_CREATE_ZIP_TAR_IN_ERR_DIR": "cd %(sourcedir_p)s ; \
                                  tar cfvz %(sourcedir_p)s/ERROR/%(snapshot_name)s_%(prepare_started_at)s.tar.gz \
                                  %(snapshot_name)s ;",
    # XXX  make shure, this is an absolute path
    "L_RM_OLD_TRANSMISSIONS": "rm -r  %(filename)s",  # make shure we get an error indicator
    "L_RM_PROD_TS_DIR_HU2HU": "rm -rf %(path_to_import_dir)s/%(snapshot_name)s",
    "L_RM_PROD_TS_DIR": "rm -rf %(sourcedir_p)s/%(snapshot_name)s",
    "L_RM_PROD_X_DIR": "rm -rf %(path_to_import_dir)s/%(dir_name)s",
    "L_RM_PROD_LOCKFILE": "rm %(product_lockfile_name)s",
    "L_RM_CLOUD_LOCKFILE": "rm  %(cloud_lockfile_name)s",
    # USED IN TRANSFER
    "L_TOUCH_PROD_LOGFILE": "touch   %(logfile_name)s",
}

# Snapshotnames on the way to europe have a - (hyphen)  in between Pi-Name and timestamp.
# Snapshotnames on the way to china have a _ (underscore) in between Pi-Name and timestamp.
# Therefore we distinguish _ and - versions for the following commands.
# The value (hyphen or underscore) is set via  the global variable DIRECTION_ISOLATOR.

REMOTE_SHELL_CMDS = {
    "R_FIND_YOUNGEST_PRODUCT_DIR": "find %(destination_dir)s/%(product_name)s%(DIRECTION_ISOLATOR)s* -maxdepth 0 -type d | tail -1",
    "R_FIND_YOUNGEST_PRODUCT_DIR": "find %(destination_dir)s/%(product_name)s%(DIRECTION_ISOLATOR)s* -maxdepth 0 -type d | tail -1",
    "R_FIND_OK_FILE_OF_CURRENT_TRANSMISSION": "find %(destination_dir)s/%(expected_name_of_ok_file)s -maxdepth 0 -type f",
    "R_CP_OLD_TO_STATIC_LINKED_NEW": "cp -al %(dirname_found)s %(destination_dir)s/%(product_id_stamp_p)s",
    "R_TOUCH_TRANSMISSION_OK_FILE": "touch %(destination_dir)s/%(product_id_stamp_p)s.ok",
    "R_GET_AMOUNT_PRODUCT_DIRS": 'find %(destination_dir)s/%(product_name)s%(DIRECTION_ISOLATOR)s* -maxdepth 0 -type d | wc -l',
    "R_NAME_OF_OLDEST_PRODUCT_DIR": 'find %(destination_dir)s/%(product_name)s%(DIRECTION_ISOLATOR)s* -maxdepth 0 -type d | head -1',
    "R_REMOVE_OLDEST_PRODUCT_DIR": "rm -rf %(name_of_oldest_product_dir)s*",
    "R_GET_AMOUNT_PRODUCT_OK_FILES": 'find %(destination_dir)s/%(product_name)s%(DIRECTION_ISOLATOR)s*ok -maxdepth 0 -type f | wc -l',
    "R_GET_OLDEST_PRODUCT_DIR": 'find %(destination_dir)s/%(product_name)s%(DIRECTION_ISOLATOR)s* -maxdepth 0 -type d | head -1',
    "R_RM_OLDEST_PRODUCT_DIR": "rm -rf %(oldest_data)s*",
    "R_LIST_PRODUCT_OK_FILES": 'find %(destination_dir)s/%(product_name)s%(DIRECTION_ISOLATOR)s*ok -maxdepth 0 -type f',
    "R_LIST_PRODUCT_DIRS": 'find %(destination_dir)s/%(product_name)s%(DIRECTION_ISOLATOR)s* -maxdepth 0 -type d ',
    "R_FIND_CLEANME_DIRS": "find %(dstdir_on_eu_host)s -name PI*CLEANME  -print  ",
}

from datetime import date


def master_replication_gtid_dump(db_name, access_options=""):
    return "mysqldump {access_options} {databases} --master-data --set-gtid-purged > {filename}".format(
        access_options=access_options,
        databases="--databases %s" % db_name,
        filename="master_replication_gtid_%s.dump" % date.today().isoformat())

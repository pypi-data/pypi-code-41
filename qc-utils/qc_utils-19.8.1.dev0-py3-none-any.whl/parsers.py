# Parser functions


def parse_starlog(path_to_log):
    """Parse star logfile into a dict.
    Args:
        path_to_log: filepath containing the star run log
    Returns:
        dict that contains metrics from star log
    """
    qc_dict = {}
    with open(path_to_log) as f:
        for line in f:
            if "|" in line:
                tokens = line.split("|")
                qc_dict[tokens[0].strip()] = tokens[1].strip()
    return qc_dict


# format pergentage points


def percentage_to_float(line):
    return float(line.strip("%"))


def parse_flagstats(filePath):
    """Parse samtools flagstat file into a dict
    Args:
        filePath: path to samtools flagstat file
    Returns:
        dict that contains metrics from flagstats
    """
    pairs = {}
    numbers_type = int
    with open(filePath, "r") as fh:
        while True:
            line = fh.readline()
            if line is None:
                break
            line.strip()
            if line == "":
                continue
            # 2826233 + 0 in total (QC-passed reads + QC-failed reads)
            if line.find("QC-passed reads") > 0:
                # 2826233 + 0 in total (QC-passed reads + QC-failed reads)
                parts = line.split()
                pairs["total"] = numbers_type(parts[0])
                pairs["total_qc_failed"] = numbers_type(parts[2])
            # 0 + 0 duplicates
            elif line.find("duplicates") > 0:
                parts = line.split()
                pairs["duplicates"] = numbers_type(parts[0])
                pairs["duplicates_qc_failed"] = numbers_type(parts[2])
            # 2826233 + 0 mapped (100.00%:-nan%)
            elif "mapped" not in pairs and line.find("mapped") > 0:
                parts = line.split()
                pairs["mapped"] = numbers_type(parts[0])
                pairs["mapped_qc_failed"] = numbers_type(parts[2])
                val = parts[4][1:].split(":")[0]
                pairs["mapped_pct"] = percentage_to_float(val)
            # 2142 + 0 paired in sequencing
            elif line.find("paired in sequencing") > 0:
                parts = line.split()
                if int(parts[0]) <= 0:  # Not paired-end, so nothing more needed
                    break
                pairs["paired"] = numbers_type(parts[0])
                pairs["paired_qc_failed"] = numbers_type(parts[2])
            # 107149 + 0 read1
            elif line.find("read1") > 0:
                parts = line.split()
                pairs["read1"] = numbers_type(parts[0])
                pairs["read1_qc_failed"] = numbers_type(parts[2])
            # 107149 + 0 read2
            elif line.find("read2") > 0:
                parts = line.split()
                pairs["read2"] = numbers_type(parts[0])
                pairs["read2_qc_failed"] = numbers_type(parts[2])
            # 2046 + 0 properly paired (95.48%:-nan%)
            elif line.find("properly paired") > 0:
                parts = line.split()
                pairs["paired_properly"] = numbers_type(parts[0])
                pairs["paired_properly_qc_failed"] = numbers_type(parts[2])
                val = parts[5][1:].split(":")[0]
                pairs["paired_properly_pct"] = percentage_to_float(val)
            # 0 + 0      singletons (0.00%:-nan%)
            elif line.find("singletons") > 0:
                parts = line.split()
                pairs["singletons"] = numbers_type(parts[0])
                pairs["singletons_qc_failed"] = numbers_type(parts[2])
                val = parts[4][1:].split(":")[0]
                pairs["singletons_pct"] = percentage_to_float(val)
            # 2046212 + 0 with itself and mate mapped
            elif line.find("with itself and mate mapped") > 0:
                parts = line.split()
                pairs["with_itself"] = numbers_type(parts[0])
                pairs["with_itself_qc_failed"] = numbers_type(parts[2])
            # 0 + 0 with mate mapped to a different chr (mapQ>=5)
            elif line.find("with mate mapped to a different chr") > 0:
                parts = line.split()
                pairs["diff_chroms"] = numbers_type(parts[0])
                pairs["diff_chroms_qc_failed"] = numbers_type(parts[2])
                break
    return pairs

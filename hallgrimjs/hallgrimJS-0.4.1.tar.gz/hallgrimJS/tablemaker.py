import re
import collections

def prepareTables(raw: str) -> str:
    """
    scans given string for use of [table]-tags and inserts necessary markup
    all '&' used in the table will be inserted as HALLGRIMTABLEAND due to
    conversion of '&' by IliasXMLCreator, these will have to be replaced later
    """
    # following regex finds text enclosed in the [table]-tag
    tableregex = re.compile('\[table\]([\w\W]+?)(\[\/table\])', re.MULTILINE) # [\w\W]+? contains ? so + is not greedy -> does not take string tu last end of table
    tablestrings = collections.deque(); # for containing the ready table-strings
    latexstrings = collections.deque(); # for containing latex-content
    latexregex=re.compile('\[\[([\w\W]+?)\]\]', re.MULTILINE)
    for latex in re.finditer(latexregex,raw): # filter out latex parts
        latexstrings.append(latex.group(0))
    raw=re.sub(latexregex,'HALLGRIMTABLELATEX',raw)
    for table in re.finditer(tableregex,raw):
        tagged = collections.deque(); # for containing the areas of internal tags
        # following regex finds all internal tagged strings, assuming correct and non-intersecting (therefore unnested) tags
        internalregex = re.compile('\[([\w\W]+?)\]([\w\W]+?)\[\/([\w\W]+?)\]', re.MULTILINE)
        for tag in re.finditer(internalregex,table.group(1)): # group(1) is matching text without [table]-tags
            tagged.append(tag.group(0)) # group(0) contains both tags and the content
        untagged=re.sub(internalregex, "HALLGRIMTABLETAGGED", table.group(1)) # temporarily replace all internal tags with HALLGRIMTABLETAGGED
        tablestring = ""
        for line in collections.deque(untagged.split(";")): # for each row (split by ;)
            linestring = ""
            for row in collections.deque(line.split(",")): # for each cell in row (split by ,)
                linestring += "HALLGRIMTABLEANDgt;HALLGRIMTABLEAND#13;HALLGRIMTABLEAND#10;HALLGRIMTABLEANDlt;tdHALLGRIMTABLEANDgt;\u00A0\u00A0" + row + "\u00A0\u00A0HALLGRIMTABLEANDlt;/td" # add cell to row, reverse-engineered from XML, & replaced with HALLGRIMTABLEAND, also added NBS (\u00A0) for space between content and walls
            tablestring += "HALLGRIMTABLEANDgt;HALLGRIMTABLEAND#13;HALLGRIMTABLEAND#10;HALLGRIMTABLEANDlt;tr" + linestring + "HALLGRIMTABLEANDgt;HALLGRIMTABLEAND#13;HALLGRIMTABLEAND#10;HALLGRIMTABLEANDlt;/tr" # add row to table, reverse-engineered from XML, & replaced with HALLGRIMTABLEAND
        tablestring = "HALLGRIMTABLEANDlt;table border=HALLGRIMTABLEANDquot;1HALLGRIMTABLEANDquot;" + tablestring + "HALLGRIMTABLEANDgt;HALLGRIMTABLEAND#13;HALLGRIMTABLEAND#10;HALLGRIMTABLEANDlt;/tableHALLGRIMTABLEANDgt;" # start and end of table, reverse-engineered from XML, & replaced with HALLGRIMTABLEAND
        untagged = collections.deque(tablestring.split('HALLGRIMTABLETAGGED'))
        completetable = collections.deque()
        for tablepart in range(min(len(untagged), len(tagged))): # put string for table back together
            text = untagged.popleft()
            if text != "":
                completetable.append(text)
            completetable.append(tagged.popleft())
        completetable.extend(untagged)
        completetable.extend(tagged)
        tablestrings.append("".join(completetable))
    untabled = re.sub(tableregex, "HALLGRIMTABLEREMOVED", raw)
    untabled = collections.deque(untabled.split('HALLGRIMTABLEREMOVED'))
    fulltable = collections.deque();
    for textpart in range(min(len(untabled),len(tablestrings))): # put complete string (with HALLGRIMTABLELATEX tokens) back together
        text = untabled.popleft()
        if text != "":
            fulltable.append(text)
        fulltable.append(tablestrings.popleft())
    fulltable.extend(untabled)
    fulltable.extend(tablestrings)
    fulltable = "".join(fulltable)
    fulltable = collections.deque(fulltable.split('HALLGRIMTABLELATEX'))
    final = collections.deque()
    for latexpart in range(min(len(fulltable),len(latexstrings))): # put latex back in
        text = fulltable.popleft()
        if text != "":
            final.append(text)
        final.append(latexstrings.popleft())
    final.extend(fulltable)
    final.extend(latexstrings)
    final = "".join(final)
    return final
        
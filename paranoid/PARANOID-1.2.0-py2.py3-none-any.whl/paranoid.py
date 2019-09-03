#! /usr/bin/env python
import argparse
import logging
import os
import random
import string
import sys
from io import StringIO

# Proved timestamps lengths
_stamps_lens = (17, 20, 23, 24, 28)

# to check python version and modify for the code to run in python2 versions
if sys.version_info[0] < 3:
    from io import open
    from timestamp_validator_27 import validate_timestamp
else:
    from timestamp_validator_3 import validate_timestamp


# reads the file in chunks of default 2000 bytes this can be specified by users
def read_in_chunks(file_object, chunk_size=2000):
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


def maskGenerator(word, flag=False, is_json=False):
    # iterates through word letter by letter and
    # replaces the same by random character
    c = ""
    r = False
    f = None
    if len(word) in _stamps_lens:
        r, f = validate_timestamp(word)

    if r:  # checking if it is a time stamp
        return f

    i = 0

    cdata = False
    if "[CDATA" in word:
        cdata = True
        word = word.replace("[CDATA", "***")

    while i < len(word):
        if word[i].isdigit():
            c += str(random.randint(1, 9))
        elif word[i].isupper():
            c += random.choice(string.ascii_letters).upper()
        elif word[i].isspace():
            c = c + word[i]
        elif word[i].islower():
            if is_json and word[i:i + 4] == 'true':
                i += 3  # below is other +1
                c += 'true'
            elif is_json and word[i:i + 5] == 'false':
                i += 4  # below is other +1
                c += 'false'
            elif is_json and word[i:i + 4] == 'null':
                i += 3  # below is other +1
                c += 'null'
            else:
                c += random.choice(string.ascii_letters).lower()

        elif word[i] == '\\' and is_json:
            # if re.match(r'\\u(\d{4})', word[i:i+6]):
            if word[i + 1] == 'u':
                c += word[i:i + 6]
                i += 5
            else:
                c += word[i:i + 2]
                i += 1
        else:
            # if flag:
            try:
                if word[i] == "&":
                    while word[i] != ";":
                        c += word[i]
                        i += 1
                    c = c + ';'
                else:
                    c += word[i]
            except:
                pass
        i += 1

    if cdata:
        c = c.replace("***", "[CDATA")
    return c


# masks the xml attributes
def xmlTagMask(s):
    # exception for the xml header tag
    if "xsi" in s:
        return s
    elif "Namespace" in s:
        return s
    elif "?xml version=" in s :
        return s
    elif 'xmlns' in s: # new at 21-08-19
        return s

    # masking xml attributes
    if ("=" in s) and ("\"" in s):
        y = ""
        i = 0
        while i < len(s):
            # find content of attribute with quotes and "="
            if s[i] == "=" and '"' in s[i +1]:
                _cur_word = s[i : s.find('"', i +2) +1]
                y = y + maskGenerator(_cur_word)
                i += len(_cur_word)
                continue
            y = y + s[i]
            i += 1
        return y

    else:
        return s


def xmlSpecificTagMask(s, masked, tag_mask_flag, user_input=None,
                       xpath=""):
    if user_input is None:
        user_input = []
    if "<?" in s:
        return xmlTagMask(s), True, xpath, masked
    elif "!--" in s:
        return xmlTagMask(s), True, xpath, masked
    else:
        r = s.strip()

        if "=" in r:
            xmlAttList = r.split("=")
            xmlTag = xmlAttList[0].split(' ')[0]
            xmlTag = xmlTag[1:]
            if 'ns:' in xmlTag:
                x = xmlTag.split(":")
                xmlTag = x[1]
        else:
            xmlTag = r[1:]
            if 'ns:' in xmlTag:
                x = xmlTag.split(":")
                xmlTag = x[1]

        if xpath == "" or xpath is None:

            xpath = "/" + xmlTag
        else:
            if xmlTag is not None:
                xpath = xpath + "/" + xmlTag
        if len(user_input) > 0:
            for i in user_input:
                if i == xpath:
                    if tag_mask_flag:
                        masked += 1
                    return xmlTagMask(s), True, xpath, masked
        else:
            return xmlTagMask(s), True, xpath, masked

        return s, False, xpath, masked


def xpathModification(xpath, end_tag, tag_count):
    if xpath == "":
        return "", tag_count

    if 'ns:' in end_tag:
        x = end_tag.split(":")
        end_tag = "/" + x[1]

    end_tag = end_tag.strip()
    xpathList = xpath.split("/")
    if xpathList[-1] == end_tag[1:]:
        del xpathList[-1]
        tag_count = tag_count + 1

    c = "/"
    xpath = c.join(xpathList)
    return xpath, tag_count


# function to mask json content
def json_mask_generator(s):
    # checking for : sign
    if ":" not in s:
        return s

    if ("}" in s) or ("]" in s):
        c = 0
        r = ""
        i = 0
        # iterating and appending the content of the xml attributes and then performing slicing to mask the content
        while (s[i] != "}") or (s[i] != "]"):

            r = r + s[i]
            c += 1
            i += 1
            if i >= (len(s) - 1):
                break
        k = r.split(':')
        s = s[c:]
        m = maskGenerator(k[1], is_json=True)
        return ":" + m + s
    else:
        m = s.split(':')
        # fix 30th May 2019
        # to handle when there are ":" in the contents as well
        if len(m) > 2:
            m = m[1:]
            k = ':'.join(m)
            c = ['', k]
            m = c
        # end of fix
        n = maskGenerator(m[1], is_json=True)
        return ":" + n


def xmlParse(input_file, out, buffer_size, tag_count, masked, mask="", additional=None):
    # tag_count -> abs. waste argument
    # masked -> abs. waste argument
    # additional  -> abs. waste argument
    cdataStart = "<![CDATA["  # Valdemar
    breakFlag = False  # Valdemar
    is_double_quoted = False  # Valdemar

    list_mask = []
    xpath = ""
    cdata = False
    mask = str(mask)
    tag_mask_flag = True
    # tag_mask_flag - one assignment here and no redefition
    # but used as argument near 29 times
    file_content = ""

    if ',' in mask:
        list_mask = mask.split(',')
    elif mask == "" or mask == "None":
        list_mask = []
    else:
        list_mask.append(mask)

    if len(list_mask) > 0:
        should_mask = False
    else:
        should_mask = True
    with open(input_file, buffering=buffer_size, encoding="utf-8") as file:
        # read first chunk
        generator = read_in_chunks(file, buffer_size)
        while True:
            try:
                if not additional:
                    file_content = next(generator)
                else:
                    file_content = additional
                    additional = ""
                cdata = True if cdataStart in file_content else False

                if not cdata:
                    file_content_parts = file_content.split(u'"')
                    countingContent = " ".join([file_content_parts[i] for i in range(len(file_content_parts)) if
                                                i % 2 == int(is_double_quoted)])
                    count_lt = countingContent.count("<")
                    count_gt = countingContent.count(">")

                    if count_lt == count_gt:
                        tag_count, masked, xpath = XmlHandleNormalContent(
                                file_content, out, tag_count, masked, tag_mask_flag,
                                list_mask, xpath, should_mask)
                        file_content = ""
                    else:  # elif count_lt>count_gt:
                        delta_tag_count = count_lt - count_gt
                        while delta_tag_count > 0:
                            additional = next(generator)
                            if cdataStart not in additional:
                                _interm = ''
                                for symbol_i in range(len(additional)):
                                    symbol = additional[symbol_i]

                                    if symbol == '"':
                                        is_double_quoted = not is_double_quoted

                                    elif not is_double_quoted:
                                        if symbol == "<":
                                            delta_tag_count += 1
                                        elif symbol == ">":
                                            delta_tag_count -= 1
                                    _interm += symbol
                                    # file_content += symbol
                                    if delta_tag_count == 0:
                                        file_content += _interm
                                        additional = additional[symbol_i + 1:]
                                        tag_count, masked, xpath = XmlHandleNormalContent(
                                            file_content, out, tag_count, masked, tag_mask_flag,
                                            list_mask, xpath, should_mask)
                                        file_content = ""
                                        breakFlag = True
                                        break
                                file_content += _interm
                                if breakFlag:
                                    breakFlag = False
                                    break
                            else:
                                result = additional.find(cdataStart)
                                cdataContent = additional[result:]
                                # file_content+= additional[:result]
                                if additional[:result]:

                                    file_content_parts = additional[:result].split('"')
                                    countingContent = " ".join(
                                        [file_content_parts[i] for i in range(len(file_content_parts)) if
                                         i % 2 == int(is_double_quoted)])

                                    new_count_lt = countingContent.count("<")
                                    new_count_gt = countingContent.count(">")
                                    if delta_tag_count + new_count_lt - new_count_gt == 0:
                                        # all tags closed before cdata
                                        file_content += additional[:result]
                                        tag_count, masked, xpath = XmlHandleNormalContent(
                                            file_content, out, tag_count, masked, tag_mask_flag,
                                            list_mask, xpath, should_mask)
                                        file_content = ""
                                        additional = cdataContent

                                        break  # while delta_tag_count>0:
                                    else:  # close maximum tags before cdata
                                        for symbol_i in range(len(additional[:result])):
                                            symbol = additional[:result][symbol_i]

                                            if symbol == '"':
                                                is_double_quoted = not is_double_quoted

                                            elif not is_double_quoted:
                                                if symbol == "<":
                                                    delta_tag_count += 1
                                                elif symbol == ">":
                                                    delta_tag_count -= 1
                                            file_content += symbol
                                            if delta_tag_count == 0:
                                                additional = additional[symbol_i + 1:]
                                                tag_count, masked, xpath = XmlHandleNormalContent(
                                                    file_content, out, tag_count, masked, tag_mask_flag,
                                                    list_mask, xpath, should_mask)
                                                file_content = ""
                                                breakFlag = True
                                                break  # for symbol_i

                                        if not breakFlag:
                                            tag_count, masked, additional, is_double_quoted = XmlHandleCdata(
                                                file_content,
                                                cdataContent,
                                                generator,
                                                out,
                                                tag_count,
                                                delta_tag_count,
                                                should_mask,
                                                masked,
                                                tag_mask_flag,
                                                list_mask,
                                                xpath,
                                                is_double_quoted)
                                            breakFlag = True

                                        if breakFlag:
                                            breakFlag = False
                                            break  # while delta_tag_count>0:
                                else:
                                    tag_count, masked, additional, is_double_quoted = XmlHandleCdata(
                                            file_content, cdataContent, generator, out, tag_count,
                                             delta_tag_count, should_mask, masked,  tag_mask_flag,
                                              list_mask, xpath, is_double_quoted)
                else:  # if cdata
                    result = file_content.find(cdataStart)
                    cdataContent = file_content[result:]
                    file_content = file_content[:result]
                    delta_tag_count = 0
                    if file_content:

                        file_content_parts = file_content.split('"')

                        new_count_lt = file_content_parts.count("<")
                        new_count_gt = file_content_parts.count(">")
                        if delta_tag_count + new_count_lt - new_count_gt == 0:
                            tag_count, masked, xpath = XmlHandleNormalContent(
                                file_content, out, tag_count, masked, tag_mask_flag,
                                list_mask, xpath, should_mask)
                            file_content = ""
                            additional = cdataContent

                        else:  # close maximum tags before cdata
                            for symbol_i in range(len(file_content)):
                                symbol = file_content[symbol_i]

                                if symbol == '"':
                                    is_double_quoted = not is_double_quoted

                                elif not is_double_quoted:
                                    if symbol == "<":
                                        delta_tag_count += 1
                                    elif symbol == ">":
                                        delta_tag_count -= 1

                                file_content += symbol
                                if delta_tag_count == 0:
                                    additional = file_content[symbol_i + 1:]
                                    tag_count, masked, xpath = XmlHandleNormalContent(
                                        file_content, out, tag_count, masked, tag_mask_flag,
                                        list_mask, xpath, should_mask)
                                    file_content = ""
                                    break  # for symbol_i
                            if delta_tag_count != 0:
                                tag_count, masked, additional, is_double_quoted = XmlHandleCdata(
                                        file_content, cdataContent, generator,  out, tag_count,
                                       delta_tag_count, should_mask, masked, tag_mask_flag, list_mask,
                                        xpath, is_double_quoted)

                    else:
                        tag_count, masked, additional, is_double_quoted = XmlHandleCdata(
                                file_content, cdataContent,  generator, out, tag_count,
                                delta_tag_count, should_mask,
                                masked, tag_mask_flag, list_mask, xpath,
                                is_double_quoted)
                        break
            except StopIteration:
                if not cdata and file_content:
                    tag_count, masked, xpath = XmlHandleNormalContent(
                        file_content, out, tag_count, masked, tag_mask_flag,
                        list_mask, xpath, should_mask)
                break

        if len(list_mask) < 1:
            masked = tag_count

    return tag_count, masked


def XmlHandleNormalContent(
        file_content, out, tag_count, masked, tag_mask_flag,
        list_mask, xpath, should_mask):

    if file_content:
        lines = file_content.split('>')
        if type(out) == str:
            file2 = open(out, "a+", encoding="utf-8")
        else:
            file2 = out

        for i in lines:  # iterating through the lines
            i_strip = i.strip()
            if len(i_strip) <= 1:
                continue

            if i_strip.startswith('<') and i_strip[1] != "/":

                i, should_mask, xpath, masked = xmlSpecificTagMask(i, masked, tag_mask_flag,
                                                                   list_mask,
                                                                   xpath)  # masking xml attribute

                file2.write(i + ">")  # writing in the output file

            else:
                b = i.split("<")  # splitting based on opening tag

                # since below python 3 we do not have unicode characters by default.
                if sys.version_info[0] < 3:
                    if should_mask:
                        file2.write(
                            maskGenerator(b[0], True).decode('utf-8'))  # masking the attributes

                    else:
                        file2.write(b[0].decode('utf-8'))
                    if len(b) > 1:
                        # Fix May19 issue reported by kris
                        try:
                            xpath, tag_count = xpathModification(xpath, xmlTagMask(b[1]), tag_count)
                        except Exception:
                            xpathModification(xpath, xmlTagMask(b[1]), tag_count)
                        # Fix complete
                        file2.write("<" + xmlTagMask(b[1]) + ">")  # appending the closing tags

                else:
                    if should_mask:
                        file2.write(maskGenerator(b[0], True))  # masking the attributes
                    else:
                        file2.write(b[0])
                    if len(b) > 1:
                        xpath, tag_count = xpathModification(xpath, xmlTagMask(b[1]), tag_count)

                        file2.write("<" + xmlTagMask(b[1]) + ">")  # appending the closing tags

        if type(out) == str:
            file2.close()  # close only regular file with string name and do not touch StringIO's

    if len(list_mask) < 1:
        masked = tag_count

    return tag_count, masked, xpath


def XmlHandleCdata(file_content, cdata_content, generator, out, tag_count, delta_tag_count, should_mask, masked,
                   tag_mask_flag, list_mask, xpath, is_double_quoted):
    cdataEnding = "]]>"
    cdataStart = "<![CDATA["
    tempFile, tempFile_Cdata = StringIO(), StringIO()
    cdataStartPosition = len(file_content)
    additional = ""
    new_count_lt = 0
    new_count_gt = 0

    if cdataEnding in cdata_content:  # short cdata
        result = cdata_content.find(cdataEnding) + len(cdataEnding)
        additional = cdata_content[result:]
        cdata_content = cdata_content[:result]

        file_content_parts = additional.split('"')
        countingContent = " ".join(
            [file_content_parts[i] for i in range(len(file_content_parts)) if i % 2 == int(is_double_quoted)])

        new_count_lt = countingContent.count("<")
        new_count_gt = countingContent.count(">")
    else:
        while cdataEnding not in cdata_content:
            cdataExtra = next(generator)
            if cdataEnding in cdataExtra:
                result = cdataExtra.find(cdataEnding) + len(cdataEnding)  # < tag should not be counted
                cdata_content += cdataExtra[:result]
                additional = cdataExtra[result:]

                file_content_parts = additional.split('"')
                countingContent = " ".join(
                    [file_content_parts[i] for i in range(len(file_content_parts)) if i % 2 == int(is_double_quoted)])

                new_count_lt = countingContent.count("<")
                new_count_gt = countingContent.count(">")
                break
            else:
                cdata_content += cdataExtra

    if sys.version_info[0] < 3:  # since below python 3 we do not have unicode characters by default.
        if should_mask:
            tempFile_Cdata.write(u'' + maskGenerator(cdata_content, True))  # masking the attributes

        else:
            tempFile_Cdata.write(cdata_content.decode('utf-8'))

    else:
        if should_mask:
            tempFile_Cdata.write(maskGenerator(cdata_content, True))  # masking the attributes

        else:
            tempFile_Cdata.write(cdata_content)

    # cdata part ends!!!!

    if additional:
        if delta_tag_count + new_count_lt - new_count_gt == 0:
            file_content += additional
            if cdataStart not in additional:
                tag_count, masked, xpath = XmlHandleNormalContent(file_content, tempFile, tag_count, masked, tag_mask_flag,
                                                           list_mask, xpath, should_mask)
                additional = ""
        else:

            for symbol_i in range(len(additional)):
                symbol = additional[symbol_i]

                if symbol == '"':
                    is_double_quoted = not is_double_quoted

                elif not is_double_quoted:
                    if symbol == "<":
                        delta_tag_count += 1
                    elif symbol == ">":
                        delta_tag_count -= 1
                file_content += symbol
                if delta_tag_count == 0:
                    additional = additional[symbol_i + 1:]
                    tag_count, masked, xpath = XmlHandleNormalContent(file_content, tempFile, tag_count, masked, tag_mask_flag,
                                                               list_mask, xpath, should_mask)
                    file_content = ""
                    break

            if delta_tag_count != 0:
                while True:

                    additional = next(generator)
                    if cdataStart in additional:
                        print("We don't expect 2 cdata's! Generally this case should'n happen. Please report the issue")
                        # TODO: fix multiply CDATA isuue
                        return 0, False, '', False
                        #raise ValueError(
                         #   "We don't expect 2 cdata's! Generally this case should'n happen. Please report the issue")

                    for symbol_i in range(len(additional)):
                        symbol = additional[symbol_i]
                        if symbol == "<":
                            delta_tag_count += 1
                        elif symbol == ">":
                            delta_tag_count -= 1
                        file_content += symbol
                        if delta_tag_count == 0:
                            additional = additional[symbol_i + 1:]
                            tag_count, masked, xpath = XmlHandleNormalContent(file_content, tempFile, tag_count, masked,
                                                                       tag_mask_flag, list_mask, xpath, should_mask)
                            file_content = ""
                            break

                    if delta_tag_count == 0:
                        break

    firstPart = tempFile.getvalue()
    secondPart = tempFile_Cdata.getvalue()
    finalString = firstPart[:cdataStartPosition] + secondPart + firstPart[cdataStartPosition:]
    with open(out, 'a+', encoding='utf8') as f:
        f.write(finalString)

    if len(list_mask) < 1:
        masked = tag_count

    return tag_count, masked, additional, is_double_quoted


def jsonParse2(input_file, out, buffer_size):
    isDblQuoted = False  # cannot use same name to easier search
    isKey = False
    temp = ""
    valueToMask = ""
    skipI = 0

    with open(input_file, buffering=buffer_size, encoding="utf-8") as file:
        content = file.read()

        with open(out, "a+", encoding="utf-8") as file2:
            for i in range(len(content)):
                if skipI > 0:
                    skipI -= 1
                    continue
                symbol = content[i]

                if not isKey and symbol == "\\":
                    # if re.match(r'\\u(\d{4})', content[i:i+6]):
                    if content[i + 1] == 'u':
                        valueToMask += content[i:i + 6]
                        skipI += 5

                        continue
                    valueToMask += content[i:i + 2]
                    skipI += 1
                    continue

                if symbol in '[]{}' and not isDblQuoted:
                    if not isKey:
                        if valueToMask:
                            result = maskGenerator(valueToMask, is_json=True)
                            file2.write(result)
                            valueToMask = ""
                    isKey = True
                    temp += symbol

                elif symbol == '"' or isDblQuoted:
                    if symbol == '"':
                        isDblQuoted = not isDblQuoted
                    if isKey:
                        temp += symbol
                    else:
                        valueToMask += symbol
                    continue

                elif symbol == ':':
                    if not isKey:
                        print('logic error, `isKey==True` should be ' +
                              'always set for non-quoted `:`%s' % i)
                        # raise ValueError('logic error, `isKey==True` should be always set for non-quoted `:`%s' % i)

                    file2.write(temp + ':')
                    temp = ""
                    isKey = False
                    # else: valueToMask+=symbol

                elif symbol == ',':
                    """
                    if isKey: raise ValueError('logic error, `isKey==False` 
                    should be always set for non-quoted `,`, %s'%i)
                    """
                    if temp and valueToMask:
                        raise ValueError('logic error, both `isKey` and `valueToMask`')
                    if isKey and temp:
                        file2.write(temp)
                        temp = ""
                    if not isKey and valueToMask:
                        result = maskGenerator(valueToMask, is_json=True)
                        valueToMask = ""
                        file2.write(u'' + result)
                    file2.write(u",")

                    isKey = True

                elif not isDblQuoted and isKey:  # digit key
                    temp += symbol

                elif not isDblQuoted and not isKey:  # digit values, true, false
                    valueToMask += symbol

                else:
                    raise ValueError('Unknown issue, please contact support')

            if temp and valueToMask:
                raise ValueError('both `temp` and `ValueToMask` stays')
            if temp:
                file2.write(temp)
            elif valueToMask:

                result = maskGenerator(valueToMask, is_json=True)
                file2.write(result)


def commandLine(input_args):
    file_count = 0
    if input_args.log != "":
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
            handlers=[
                logging.FileHandler(input_args.log),
                logging.StreamHandler()
            ])

    else:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
            handlers=[
                logging.StreamHandler()
            ])

    logger = logging.getLogger()

    if input_args.input != "":

        if os.path.isdir(input_args.input):
            inputDirectory = input_args.input + os.path.sep
            if not os.path.exists(input_args.outputDir):
                try:
                    os.makedirs(input_args.outputDir)
                except OSError:
                    logger.warning("Exiting no write access")
                    sys.exit()
            if not os.access(input_args.outputDir, os.W_OK):
                logger.warning('Exiting no write access')
                sys.exit()
            files = []
            logger.info("Initializing Masking")
            logger.info("Processing")
            for subdir, dirs, allfiles in os.walk(inputDirectory):
                for file in allfiles:
                    files.append(os.path.join(subdir, file))
            for names in files:
                tag_count = 0
                tag_mask = 0
                name, ext = os.path.splitext(names)
                fileName = name.split(inputDirectory)
                output = input_args.outputDir + os.path.sep + fileName[-1] + ext
                if not os.path.exists(os.path.dirname(output)):
                    os.makedirs(os.path.dirname(output))
                if os.path.exists(output):
                    os.remove(output)

                if ext == ".xml":
                    tag_count, tag_mask = xmlParse(names, output, input_args.byteSize, tag_count, tag_mask,
                                                   input_args.mask)
                    logger.info("Completed Processing " + inputDirectory + names + " Masked file location " + output)
                    logger.info("Total tags found in " + name + " = " + str(tag_count))
                    logger.info("Total tags masked in  " + name + " = " + str(tag_mask))

                elif ext == ".json":

                    # jsonParse((names), output, args.byteSize)
                    jsonParse2(names, output, input_args.byteSize)
                    logger.info("Completed Processing " + names + " Masked file location " + output)
                file_count += 1

            logger.info("Total files Masked " + str(file_count))

        elif os.path.isfile(input_args.input):
            tag_count = 0
            tag_mask = 0
            name, ext = os.path.splitext(input_args.input)
            fileName = os.path.basename(name)
            if not os.path.exists(input_args.outputDir):
                try:
                    os.makedirs(input_args.outputDir)
                except OSError:
                    logger.warning("Exiting no write access")
                    sys.exit()
            if not os.access(input_args.outputDir, os.W_OK):
                logger.warning("Exiting no write access")
                sys.exit()
            output = input_args.outputDir + os.path.sep + fileName + ext
            if os.path.exists(output):
                os.remove(output)

            logger.info("Initialising Masking")

            if ext == ".xml":
                tag_count, tag_mask = xmlParse(input_args.input, output, input_args.byteSize, tag_count, tag_mask,
                                               input_args.mask)
                logger.info("Completed Processing " + input_args.input + " Masked file location " + output)
                logger.info("Total tags found in " + fileName + " = " + str(tag_count))
                logger.info("Total tags masked in  " + fileName + " = " + str(tag_mask))

            elif ext == ".json":
                logger.info("Processing " + fileName)

                # jsonParse(args.input, output, args.byteSize)
                jsonParse2(input_args.input, output, input_args.byteSize)
                logger.info("Completed Processing " + input_args.input + " Masked file location " + output)

            else:
                logger.warning("Please provide valid xml/json file")
                sys.exit()

            logger.info("Masking Completed")
        else:
            logger.warning("Invalid directory/ File ")
            sys.exit()

    else:
        logger.warning("Please provide input")
        sys.exit()


def main():
    parser = argparse.ArgumentParser(description="Data Masking")
    parser.add_argument("-i", help="Input Directory Name / File Name", dest="input", type=str, required=True)
    parser.add_argument("-b", help="Provide byte size to buffer", dest="byteSize", type=int, default="2000000")
    parser.add_argument("-o", help="Output Directory Name", dest="outputDir", type=str, required=True)
    parser.add_argument("-l", help="Input xpath or xpaths separated by ,", dest="mask", type=str)
    parser.add_argument("-L", help="Output in Log File", dest="log", type=str, default="")
    parser.set_defaults(func=commandLine)
    parsed_args = parser.parse_args()
    parsed_args.func(parsed_args)
    return parsed_args


if __name__ == "__main__":
    args = main()

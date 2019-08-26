import xml.etree.ElementTree as et
import urllib.parse as url
import base64

from .xmlBuildingBlocks import *
from .abstract_question import IliasQuestion
from .. import messages

class JavaScriptQuestion(IliasQuestion):
    """This class contains all functions, needed for creating
    the XML file for ILIAS, that are special to the JavaScript question type."""

    __slots__ = ('question_text', 'points', 'javaScript',)
    external_type = 'CLOZE QUESTION'
    internal_type = 'javaScript'
    usable_data_type = ('png', 'jpg', 'jpeg', 'gif', 'bmp')

    def __init__(self, question_text, author, title, correctAnswers, appendedData, javaScriptCode, feedback):
        self.question_text  = question_text
        self.author         = author
        self.title          = title
        self.correctAnswers = correctAnswers
        self.appendedData   = appendedData
        self.javaScriptCode = javaScriptCode
        self.feedback       = feedback

    def itemmetadata(self, feedback_setting=1):
        """This function adds all necessary XML tags and their content that
        need to appear inbetween the "itemmetadata" tags of the XML file for
        ILIAS."""

        subroot = et.Element('qtimetadata')
        subroot.append(qtimetadatafield('ILIAS_VERSION', '5.1.11 2016-10-28'))
        subroot.append(qtimetadatafield('QUESTIONTYPE', self.external_type))
        subroot.append(qtimetadatafield('AUTHOR', self.author))
        subroot.append(qtimetadatafield('additional_cont_edit_mode', 'default'))
        subroot.append(qtimetadatafield('externalId', '99.99'))
        subroot.append(qtimetadatafield('textgaprating', 'ci'))
        subroot.append(qtimetadatafield('identicalScoring', '1'))
        subroot.append(qtimetadatafield('combinations', 'W10='))
        root = et.Element('itemmetadata')
        root.append(subroot)
        return root

    ############################################################################
    def presentation(self):
        """This function adds all necessary XML tags and their content that
        need to appear inbetween the "presentation" tags of the XML file for
        ILIAS (question title, question text, gap)."""

        root = et.Element('presentation', attrib={'label': self.title})
        flow = et.Element('flow')

        response_str = et.Element('response_str', attrib={
            'ident': 'gap_0',
            'rcardinality': 'Single',
        })

        render_fib = et.Element('render_fib', attrib={
            'fibtype': 'String', 
            'prompt': 'Box',
            'columns': '9',
            'maxchars': '999999',})

        root.append(flow)
        flow.append(response_str)
        response_str.append(render_fib)
        flow.append(material(''))

        # Here the question text, the javaScript code and the appended data
        # get appendend to the xml file.
        flow.append(material(
            self.question_text +
            "<script>eval(decodeURIComponent('{0}'));</script>"
            .format(url.quote(
                """document.getElementsByName("gap_0")[0].type="hidden";
                if(document.getElementsByClassName("ilc_qinput_TextInput solutionbox")[0]){
                    document.getElementsByClassName("ilc_qinput_TextInput solutionbox")[0].style.visibility = 'hidden';
                }"""
                + self.javaScriptCode 
                + self.appendedDataToString()
        ))))

        return root

    ############################################################################
    def resprocessing(self):
        """This function adds all necessary XML tags and their content that
        need to appear inbetween the "resprocessing" tags of the XML file for
        ILIAS. It adds all (answer, points) tuple to the XML file."""

        root = et.Element('resprocessing')
        outcomes = et.Element('outcomes')
        outcomes.append(simple_element('decvar'))
        root.append(outcomes)

        answer_count = 0
        for i in self.correctAnswers.splitlines():
            if i !='':
                answer_count += 1 
                root.append(
                    self.respcondition(i.partition(':')[0].strip().replace('<p>', ''), 
                    float(i.partition(':')[2].replace('P', '').replace('</p>', '')), 
                    answer_count))

        return root

    ############################################################################
    @staticmethod
    def respcondition(answer, points, answer_count):
        """This function adds all necessary XML tags and their content that
        need to appear inbetween the "respcondition" tags of the XML file for
        ILIAS. Gets called by :func:`~javaScript.JavaScriptQuestion.resprocessing`
        and adds a (answer, points) tuple to the XML file.
        
        Arguments:
            answer (string): answer that will receive points
            points (int): points given for entering the answer
            answer_count (int): number of previous answers
        """

        root = et.Element('respcondition', attrib={'continue': 'Yes'})
        conditionvar = et.Element('conditionvar')
        varequal = simple_element(
            'varequal',
            text=answer,
            attrib={'respident': 'gap_0'}
        )

        conditionvar.append(varequal)
        setvar = simple_element(
            'setvar',
            text=str(points),
            attrib={'action': 'Add'}
        )

        displayfeedback = et.Element(
            'displayfeedback',
            attrib={'feedbacktype': 'Response',
                    'linkrefid': '0_Response_{}'.format(answer_count)})
        root.append(conditionvar)
        root.append(setvar)
        root.append(displayfeedback)
        return root

    ############################################################################
    def appendedDataToString(self):
        """This function will tanslate all appended image files in the template
        with bas64 to a string and returns that string. It also ensures that
        the images can be called in the question via HTML."""

        data_string = ""
        for i in self.appendedData.splitlines():
            if i !='':

                # This will result in the path and the name of the 
                # data to append, because theappendedData in the 
                # Template will always have the following 
                # format: 'name of image' : 'path
                path = i.partition(':')[2].strip()
                image_name = i.partition(':')[0].strip()

                # Aborts if type of appended data is not in  
                # usable_data_type (currently 'png', 'jpg', 'jpeg', 
                # 'gif' and 'bmp') or if there are formate errors
                # else returns the data type as string
                data_type = self.hasSupportedDataType(path, image_name)

                try:
                    image = open(path, 'rb')
                except FileNotFoundError:
                    messages.abort('File: {0} was not found!'.format(path))   
           
                image_encoded = base64.encodestring(image.read())
                data_string += """
                document.getElementsByName("{0}").forEach(function(img){{
                    img.src = 'data:image/{1};base64,{2}';
                }})""".format(image_name, data_type, image_encoded)

        # The base64.encodestring() will add a "b'" at the beginning and a
        # "\n'" at the and of the string. These need to be removed, hence the replace()
        return data_string.replace('b\'','').replace('\\n\'', '')


    ############################################################################
    def hasSupportedDataType(self, path, image_name):
        """Is called by :func:`~javaScript.JavaScriptQuestion.appendedDataToString`
        and checks wheter the appended files have a supported file type.
        
        Arguments:
            path (string): path to the image to append
            image_name (string): name of the image to append
        """

        if(image_name == ''):
            messages.abort('An image in the template has no name!')
        if(path == ''):
            messages.abort('The image \"{0}\" in the template has no path'.format(image_name))
        for i in self.usable_data_type:
            if path.endswith(i):
                return i

        messages.abort('{0} has an unsupported file type'.format(path))


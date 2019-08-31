'''
Chaton Script Language Parser

Written by Minsu Jang (minsu@etri.re.kr)

Todo:
    * (put_event() 메쏘드) self.events 안의 이벤트들은 시간이 지나면 일찍 들어온 것들부터 천천히 사라진다.
'''

import random 
import re
import logging
import string
import pkgutil
from queue import Queue
from queue import Empty
from lark.lexer import Token
from lark import Lark

logger = logging.getLogger(__name__)

def mock():
    return (u'chaton init...')

class Variable(object):
    def __init__(self, name):
        self.name = name

    def __str__( self ):
        return self.name


class Matcher(object):
    def __init__(self):
        pass

    def match(self, pattern, input):
        pass


class SentenceMatcher(Matcher):
    def __init__(self):
        super(SentenceMatcher, self).__init__()

    def match(self, pattern, text):
        return self.matches(pattern, text)

    def matches(self, pattern, text):
        logger.info('pattern: ' + str(pattern))
        logger.info('text: ' + str(text))
        input_words = text.split(" ")
        if len(pattern.words) != len(input_words):
            logger.info("matching failed")
            return False, None
        variables = {}
        for pword, iword in zip(pattern.words, input_words):
            if isinstance(pword, Variable):
                logger.info("Variable %s = %s", pword, iword)
                variables[pword.name] = iword
            elif pword != iword:
                logger.info("matching failed: %s", variables)
                return False, None
        logger.info("matching succeeded: %s", variables)
        return True, variables


class SentenceMatcherViaRegex(Matcher):
    def __init__(self, pattern):
        super(SentenceMatcherViaRegex, self).__init__()
        self.pattern = pattern

    def match(self, pattern, text):
        matching_succeeded = self.matches(self.pattern, input)
        return matching_succeeded, None

    def matches(self, pattern, text):
        logger.info('pattern: ' + str(pattern))
        logger.info('text: ' + str(text))
        pattern = str(pattern)
        text = str(text)
        regexobj = re.compile(pattern)
        if regexobj.search(text) != None:
            logger.info('----- matched.')
            return True
        else:
            logger.info('----- not matched.')
            return False


class Sentence(object):
    def __init__(self, engine, subtree):
        self.words = []
        self.engine = engine
        self.create_sentence(subtree)
        self.matcher = SentenceMatcher()

    def create_sentence(self, subtree):
        for child in subtree:
            if child.type == 'WORD':
                self.words.append(child.value)
            elif child.type == 'VAR':
                self.words.append(Variable(child.value[1:-1]))

    def match(self, text):
        return self.matcher.match(self, text)

    def __str__( self ):
        return ' '.join(map(str, self.words))


class You(object):
    def __init__(self, engine, subtree):
        self.patterns = []  # input sentence patterns
        self.events = []    # input events
        self.queries = []   # queries to be tested 
        self.assignments = [] 
        self.engine = engine  
        self.category = -1
        self.create_you(engine, subtree)
    
    def create_you(self, engine, subtree):
        if subtree == None:
            self.category = 3
        else:
            for child in subtree:
                if isinstance(child, Token):
                    self.patterns.append(child.value.replace('"',''))
                    self.category = 0
                elif child.data == 'sentence':
                    self.patterns.append(Sentence(engine, child.children))
                    self.category = 0
                elif child.data == 'query':
                    self.queries.append((child.children[0], child.children[1]))
                    self.category = 1
                elif child.data == 'event':
                    self.events.append(child.children[0].value)
                    self.category = 2
                elif child.data == 'assignment':
                    self.assignments.append((child.children[0], child.children[1]))

    def match(self, events, event_data):
        prop_table = {}
        print("YOU matching... ", self.category)
        print ("    event_data: {}".format(event_data))
        if len(self.assignments) > 0:
            for assignment in self.assignments:
                print("  assignment: ", assignment, " (", assignment[0].type, ")")
                if assignment[0].type == "VAR":
                    if assignment[1].value in event_data:
                        print("    val: ", event_data[assignment[1].value])
                        prop_table[assignment[0].value[1:-1]] = event_data[assignment[1].value]

        if self.category == 0:
            print("  Category 0: Sentence")
            pattern = self.patterns[0]
            for event in events:
                print("    cur_event: ", event)
                if event == 'speech_recognized':
                    text = event_data["sentence"]
                    succeeded, variables = pattern.match(text)
                    if succeeded:
                        return self.category, variables
            return -1, None
        elif self.category == 1: # TODO: query processing
            print("  Category 1: Query")
            for query in self.queries:
                print("    my_query: ", query)
                if query[0].type == 'VAR':
                    var_name = query[0].value[1:-1]
                    print("    var name: {}".format(var_name))
                    value = None
                    if var_name in event_data:
                        value = str(event_data[var_name])
                    elif var_name in self.engine.variables:
                        value = str(self.engine.variables[var_name])
                    if value is not None:
                        print("    {}'s value is {}".format(var_name, value))
                        if value == query[1].value:
                            print(" YOU matched with value = {}".format(value))
                            return self.category, {}
                    print("    var {} is not in event_data".format(var_name))
            return -1, None
        elif self.category == 2: # event processing
            print("  Category 2: Event")
            for my_event in self.events:
                print("    my_event: ", my_event)
                if my_event not in events:
                    return -1, None
            print(" YOU matched: prop_table = ", prop_table)
            return self.category, prop_table
        elif self.category == 3: # init processing
            print("  Category 3: Init")
            return self.category, {}

    def __str__( self ):
        pattern_str = ' '.join(map(str, self.patterns))
        event_str = ' '.join(map(str, self.events))
        query_str = ' '.join(map(str, self.queries))
        return pattern_str + " / " + event_str + " / " + query_str

    
class Me(object):
    def __init__(self, engine, subtree):
        self.assignments = []
        self.sentence = ''
        self.jump = ''
        self.engine = engine
        self.create_me(engine, subtree)
        
    def create_me(self, engine, subtree):
        for child in subtree:
            if isinstance(child, Token):
                self.sentence = child.value.replace('"','')
            elif child.data == 'sentence':
                self.sentence = Sentence(engine, child.children)
            elif child.data == 'assignment':
                self.assignments.append((child.children[0], child.children[1]))
            elif child.data == 'jump_directive':
                self.jump = child.children[0].children[0]

    def make_reply(self, matches):
        reply = ''
        prop_table = {}
        if self.sentence == '':
            reply = ''
        else:
            reply = ''
            for item in self.sentence.words:
                if isinstance(item, Variable):
                    if item.name in matches:
                        reply = reply + str(matches[item.name])
                    elif item.name in self.engine.variables:
                        reply = reply + str(self.engine.variables[item.name])
                else:
                    reply = reply + ' ' + item
        if len(self.assignments) > 0:
            for assignment in self.assignments:
                print("assignment: ", assignment, " (", assignment[1].type, ")")
                if assignment[1].type == "VAR":
                    print("val: ", matches[assignment[1].value[1:-1]])
                    prop_table[assignment[0].value] = matches[assignment[1].value[1:-1]]
        print("var_table: ", prop_table)
        return reply, prop_table

    def __str__( self ):
        return str(self.sentence) + " / " + str(self.assignments) + " / " + str(self.jump)


class Turn(object):
    def __init__(self, engine, subtree):
        self.you = []
        self.mes = []
        self.engine = engine
        self.create_turn(engine, subtree)
        
    def create_turn(self, engine, subtree):
        for child in subtree:
            if child.data == 'you':
                self.you.append(You(engine, child.children))
            elif child.data == 'me':
                self.mes.append(Me(engine, child.children))
        # if there is no you, create an init event matching you
        if self.you == []:
            self.you.append(You(engine, None))

    def match(self, events, event_data):
        print(">> Finding matches...")
        matches = []
        for matching_rule in self.you:
            print("matching_rule: ", str(matching_rule))
            print("events: ", events)
            print("event_data: ", event_data)
            print(matching_rule.match(events, event_data))
            category, variables = matching_rule.match(events, event_data)
            if category == -1: # no matches!
                continue
            matches.append((category, variables))
        print("<< Finding matches done. Found {} matches.".format(len(matches)))
        return matches

    def make_reply(self, variables):
        """Make a reply.

        Returns:
            A reply string, and a topic name to jump if a jump directive exists otherwise a blank string.
        """
        print("TURN: making a reply...")
        me = random.choice(self.mes)
        print("   chose a me: {}".format(me))
        reply, prop_table = me.make_reply(variables)
        print("   made a reply: {}".format(reply))
        topic_to_jump = me.jump
        print("TURN: making a reply... done.")
        return reply, prop_table, topic_to_jump

    def get_you(self):
        return self.you
    
    def get_mes(self):
        return self.mes


class Topic(object):
    def __init__(self, engine, subtree):
        self.id = subtree.children[0].children[0]
        self.turns = []
        self.engine = engine
        self.create_turns(self.engine, subtree.children)
        self.is_new_entrance = False

    def new_entrance_made(self):
        self.is_new_entrance = True

    def create_turns(self, engine, subtree):
        for child in subtree[1:]:
            turn = Turn(engine, child.children)
            self.turns.append(turn)

    def add_turn(self, turn):
        self.turns.append(turn)
        
    def get_turns(self):
        return self.turns
    
    def is_done(self):
        return False
    
    def find_turns(self, events, event_data):
        """Find turns in this topic that match with given events and event_data.

        Args:
            events: a list of events received
            event_data: a set of event data

        Returns:
            A list of tuples each of which includes a turn and its accompanying table of variables and their values
        """
        turn_tuples = []
        for turn in self.turns:
            matches = turn.match(events, event_data)
            for cat, variables in matches:
                turn_tuples.append((cat, turn, variables))
        return turn_tuples
    

    def choose_turn(self, turns):
        """Choose a turn from turns.

        Args:
            turns: a list of (match_category, turn, variables) tuples

        Returns:
            A chosen turn and a dictionary of variables and their values
        """
        print(">> Choosing a turn from {} turns".format(len(turns)))

        turn_tuples = []
        if self.is_new_entrance:
            for turn_tuple in turns:
                cat = turn_tuple[0]
                if cat == 3:
                    turn_tuples.append(turn_tuple)
                    break
            if len(turn_tuples) == 0:
                turn_tuples = turns
            self.is_new_entrance = False
        else:
            for turn_tuple in turns:
                cat = turn_tuple[0]
                if cat != 3:
                    turn_tuples.append(turn_tuple)

        if len(turn_tuples) <= 0:
            return None, {}

        turn_tuple = random.choice(turn_tuples)
        print("  chose a turn {}".format(turn_tuple[1]))
        '''
        for cat, turn, variables in turns:
            if cat == 0:
                return turn, variables
        '''
        return turn_tuple[1], turn_tuple[2] # turn, variables


    def make_reply(self, turn, variables):
        """Make a reply from the given turn.

        Args:
            turn: a turn
            variables: a dictionary of variable names and their values

        Returns:
            A reply string and the name of next topic
        """
        reply, prop_table, next_topic_name = turn.make_reply(variables)
        if next_topic_name == '':
            next_topic_name = self.id
        return reply, prop_table, next_topic_name

    '''
    def toss_init_event(self):
        if self.is_new_entrance:
            self.is_new_entrance = False
            return self.get_reply(["init"], {})
        else:
            return '', {}, {}, self.id
    '''

    def get_reply(self, events, event_data):
        """Get a reply from this topic with given events and event data.
        """
        reply = ''
        prop_table = {}
        next_topic_name = self.id

        # Find a set of possible turns
        turns = self.find_turns(events, event_data)

        # Choose a turn
        turn, variables = self.choose_turn(turns)

        # Determine a reply
        if turn != None:
            reply, prop_table, next_topic_name = self.make_reply(turn, variables)

        logger.debug('Topic::get_reply(): next topic id = ' + str(next_topic_name) + ' self id = ' + self.id)

        return reply, variables, prop_table, next_topic_name

        '''
        mes, matches = self.find_mes(events)
        if matches is not None and len(matches) > 0:
            self.engine.variables.update(matches)
        if mes != None:
            me = random.choice(mes)
            reply = me.make_reply(self.engine.variables)
            if me.jump != '':
                next_topic_id = me.jump
        logger.debug('Topic::get_reply(): next topic id = ' + str(next_topic_id) + ' self id = ' + self.id)
        return reply, next_topic_id
        '''
    
class Script(object):
    def __init__(self, engine, tree):
        self.topics = []
        self.engine = engine
        self.create_script(tree.children)
        
    def create_script(self, subtree):
        for child in subtree:
            self.topics.append(Topic(self.engine, child))
            
    def get_topics(self):
        return self.topics


class ChatonException(Exception):
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return repr(self.value)


class Chaton(object):
    """
    Chaton chatbot engine
    """
    def __init__(self, output_queue=None):
        #self.grammar = pkgutil.get_data(__package__, 'chaton.lark')
        #self.grammar = self.grammar.decode('utf-8')
        f = open("./chaton.lark", 'r')
        self.grammar = f.read()
        print(self.grammar)
        self.parser = Lark(self.grammar, start='script', parser='lalr')
        self.script = None
        self.topics = None
        self.cur_topic = None
        self.cur_topic_name = ""
        self.cur_topic_index = 0
        self.next_topic_name = ""
        self.variables = {}
        self.events = []
        self.event_data = {}
        if output_queue == None:
            self.output_queue = Queue()
        else:
            self.output_queue = output_queue

    def get_output_queue(self):
        return self.output_queue

    # Utility Methods
    def remove_punctuations(self, text):
        """Remove punctuation characters from the input text.

        Args:
            text: an input text

        Returns:
            string: a text without punctuation marks
        """
        for c in string.punctuation:
            text = text.replace(c, "")
        return text

    def set_variable(self, name, value):
        """Set the value of a variable.

        Args:
            name: the name of a variable
            value: the value of the variable
        """
        self.variables[name] = value

    def get_value(self, name):
        """Get the value of a variable.

        Args:
            name: the name of a variable

        Returns:
            The value of the variable with the given name if it is in this engine's memory, 
            a blank string otherwise.
        """
        if name in self.variables:
            return self.variables[name]
        else:
            return ''

    def get_topic_index(self, topic_name):
        """Get the index of a topic with a given topic name.

        Args:
            topic_name: The name of a topic    
        """
        for index, topic in enumerate(self.topics):
            if topic.id == topic_name:
                return index
        raise ChatonException('Topic Not Found: ' + topic_name)

    def load(self, script_file):
        """Load a chaton script.

        Args:
            script_file: the path to the script file
        """
        f = open(script_file, 'r')
        content = f.read()
        tree = self.parser.parse(content)
        self.script = Script(self, tree)
        self.topics = self.script.get_topics()
        # the first indexed topic is the first topic
        self.next_topic_name = self.topics[0].id


    def set_next_topic(self, topic_name):
        """Set the name of the next topic.
        """
        self.next_topic_name = topic_name


    def determine_current_topic(self):
        """Determine the current topic.
        """
        if self.next_topic_name == "":
            self.next_topic_name = self.topics[0].id
        elif self.next_topic_name == 'END':
            self.cur_topic = None
            return

        topic_changed = self.cur_topic_name != self.next_topic_name
        self.cur_topic_index = self.get_topic_index(self.next_topic_name)
        self.cur_topic_name = self.next_topic_name
        self.cur_topic = self.topics[self.cur_topic_index]
        if topic_changed:
            self.cur_topic.new_entrance_made()
        logger.debug("current topic = %s", self.cur_topic.id)


    def have_a_turn(self):
        """Notify this engine has a turn.
        """
        print("HAVING A TURN...")
        # Determine the topic
        self.determine_current_topic()

        if self.cur_topic is None:
            print("NO MORE CHAT!! ENDED.")
            return 

        # Process init event first.
        print(" cur_topic = ", self.cur_topic.id)

        reply, variables, prop_table, next_topic_name = self.cur_topic.get_reply([], {})
        self.variables.update(variables)
        self.next_topic_name = next_topic_name       
        if reply != '':
            self.output_queue.put((reply, prop_table))
        if self.next_topic_name == 'END':
            self.output_queue.put(('END', {}))
        print("HAD A TURN... DONE.")


    def update_state(self):
        """Update this engine's state, determine a reply if possible and put the reply into the output queue.
        """
        if len(self.events) <= 0:
            return

        events = self.events[:]
        self.events = [] # 이벤트 저장소 초기화
        if "sentence" in self.event_data:
            self.event_data["sentence"] = self.remove_punctuations(self.event_data["sentence"])

        self.determine_current_topic()
        if self.cur_topic is None:
            print("NO MORE CHAT!! ENDED.")
            return

        reply, variables, prop_table, next_topic_name = self.cur_topic.get_reply(events, self.event_data)
        self.variables.update(variables)
        logger.debug('reply and next topic: ' + reply + " , " + next_topic_name)
            
        self.next_topic_name = next_topic_name

        if reply != '':
            self.output_queue.put((reply, prop_table))
        if self.next_topic_name == 'END':
            self.output_queue.put(('END', {}))


    def put_event(self, event, event_data):
        """Put an event into this engine.

        Args:
            event: a string name of an event
            event_data: a dictionary of property-value pairs
            
        Examples: 
            - face_recognized / {"이름":"민수", "나이":30, "성별":"남성"}
            - speech_recognized / {"문장":"안녕하세요"}
        """
        print("HAVING A TURN BY AN EVENT...")
        self.events.append(event)
        self.event_data.update(event_data)
        self.update_state()
        print("HAD A TURN BY AN EVENT... DONE.")
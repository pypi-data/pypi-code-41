#!/usr/bin/env python


'''
Usage: 
    mklookups <metadata_file> --list
    mklookups <metadata_file> --add
'''

import os, sys
import docopt
import copy
from os import system, name
import json
from cmd import Cmd
from snap import common
from snap import cli_tools as cli


def create_table_metadata(**kwargs):
    print('placeholder for metadata creation logic')
    return kwargs

COLUMN_TYPES = [
    {
        'label': 'integer',
        'value': 'int',
    },
    {
        'label': 'floating-point',
        'value': 'float'
    },
    {
        'label': 'string',
        'value': 'varchar(64)'
    }
]

def create_table_column(**kwargs):
    return kwargs

add_column_sequence = {
'marquee': '''
  +++
  +++ Add column metadata for new table 
  +++
  ''',
  'builder_func': create_table_column,
  'steps': [
    {
      'field_name': 'column_name',
      'prompt': cli.InputPrompt('Column name'),
      'required': True
    },
    {
      
      'field_name': 'column_type',
      'prompt': cli.MenuPrompt('Column type', COLUMN_TYPES),
      'required': True
    },
  ]
}

add_table_sequence = {
  'marquee': '''
  +++
  +++ Add metadata for new table 
  +++
  ''',
  'builder_func': create_table_metadata,
  'steps': [
    {
      'field_name': 'table_name',
      'prompt': cli.InputPrompt('Lookup table name'),
      'required': True
    },
    {
      
      'field_name': 'columns',
      'sequence': add_column_sequence,
      'repeat': True,
      'required': True
    },
  ]
}

class UISequenceRunner(object):
  def __init__(self, **kwargs):
    #
    # keyword args:
    # override_create_prompts is an optional dictionary
    # where <key> is the field name of a step in a UI sequence
    # and <value> is a prompt instance from the cli library.
    # This gives users of the UISequenceRunner the option to 
    # override the default Prompt type specified in the ui sequence 
    # dictionary passed to the create() method.
    #
    
    self.create_prompts = kwargs.get('override_create_prompts', {})


  def process_edit_sequence(self, config_object, **sequence):
    
    print(sequence['marquee'])
    context = {}
    for step in sequence['steps']:

      current_target = getattr(config_object, step['field_name'])
      if step.get('sequence'):
        if isinstance(current_target, list):
          # recursively edit embedded lists 
          response = []
          for obj in current_target:
            output = self.process_edit_sequence(obj, **step['sequence'])
            if output is not None:
              response.append(output)

          setattr(config_object, step['field_name'], response)
          continue

        else:
          output = self.process_edit_sequence(**step['sequence'])
          if output:
            setattr(config_object, step['field_name'], output)
          continue
      else:
        if isinstance(current_target, list):
          raise Exception('!!! An edit sequence which handles a list-type attribute must use a child sequence.')   

      context['current_value'] = getattr(config_object, step['field_name'])
      label = step.get('label', step['field_name'])
      context['current_name'] = getattr(config_object, label)      
      prompt = step['prompt_type']
      args = []
      for a in step['prompt_args']:
        args.append(a.format(**context))
      response = prompt(*args).show()
      if response is not None:
        setattr(config_object, step['field_name'], response)
    return config_object


  def process_create_sequence(self, init_context=None, **sequence):
    print(sequence['marquee'])
    context = {}
    if init_context:
      context.update(init_context)
    
    if sequence.get('inputs'):
      context.update(sequence['inputs'])

    for step in sequence['steps']:
      #print(step)
      if not step.get('prompt'):
        if not step.get('conditions') and not step.get('sequence'):
          # hard error
          raise Exception('step "%s" in this UI sequence has no prompt and does not branch to a child sequence') 

      # this is an input-dependent branch 
      if step.get('conditions'):        
        answer = step['prompt'].show()
        if not step['conditions'].get(answer):
          raise Exception('a step "%s" in the UI sequence returned an answer "%s" for which there is no condition.' 
                          % (step['field_name'], answer))

        next_sequence = step['conditions'][answer]['sequence']
        outgoing_context = copy.deepcopy(context)
        context[step['field_name']] = self.create(**next_sequence)
         
      # unconditional branch
      elif step.get('sequence'):
        next_sequence = step['sequence']
        outgoing_context = copy.deepcopy(context)
        is_repeating_step =  step.get('repeat', False)

        while True:                 
          sequence_output = self.create(**next_sequence)
          if not sequence_output: 
            break

          if is_repeating_step:
            if not context.get(step['field_name']):
              context[step['field_name']] = []
            context[step['field_name']].append(sequence_output)
          else:
            context[step['field_name']] = sequence_output

          if is_repeating_step:
            repeat_prompt = step.get('repeat_prompt', cli.InputPrompt('create another (Y/n)', 'y'))
            should_repeat = repeat_prompt.show().lower()
            if should_repeat == 'n':
              break
          else:
            break

      else:
        # follow the prompt -- but override the one in the UI sequence if one was passed to us
        # in our constructor
        prompt =  self.create_prompts.get(step['field_name'], step['prompt'])         
        answer = prompt.show()
        if not answer and step['required'] == True:        
          break
        if not answer and hasattr(step, 'default'):        
          answer = step['default']
        else:        
          context[step['field_name']] = answer
  
    return context


  def create(self, **create_sequence):
    context = self.process_create_sequence(**create_sequence)
    output_builder = create_sequence.get('builder_func')
    if output_builder:
      return output_builder(**context)
    return context


  def edit(self, config_object, **edit_sequence):
    self.process_edit_sequence(config_object, **edit_sequence)
    return config_object



def clear(): 
    # for windows 
    if name == 'nt': 
        _ = system('cls') 

    # for mac and linux(here, os.name is 'posix') 
    else: 
        _ = system('clear') 

class MkLookupsCLI(Cmd):
    def __init__(self,
                 name,
                 metadata):

        Cmd.__init__(self)
        self.name = name
        self.prompt = '__[%s]> ' % (self.name)
        self.metadata = metadata
        self.new_table_configs = []
        #self.replay_stack = Stack()

    def generate_metadata(self):
        return self.new_table_configs

    def do_new(self, *cmd_args):
        newdata = UISequenceRunner().create(**add_table_sequence)
        print(newdata)
        self.new_table_configs.append(newdata)


    def matching_csv_exists(self, tablename):
        target_filename = '%s.csv' % tablename
        if os.path.isfile(target_filename):
            return True
        return False


    def read_csv_header(self, filename, delimiter_char):
        header_fields = []
        with open(filename, 'r') as f:
            header = f.readline()
            for token in header.split(delimiter_char):
                header_fields.append(token.lstrip().rstrip())
        return header_fields


    def do_validate(self, *cmd_args):
        # verify the existence of a CSV file where:
        # - the column names match the created ones
        # - the filename (minus extension suffix) matches the table name

        errors = []

        for tbl_config in self.new_table_configs:
            tablename = tbl_config['table_name']
            print('### checking table "%s"...' % tablename)
            if not self.matching_csv_exists(tablename):
                errors.append('no datafile found with name "%s.csv".' % tablename)
            else:
                filename = '%s.csv' % tablename
                header_fields = self.read_csv_header(filename, '|')
                for col in tbl_config['columns']:
                    if col['column_name'] not in header_fields:
                        errors.append('metadata for table %s has columns not found in the CSV file %s.' 
                                      % (tablename, filename))


        print(common.jsonpretty(errors))

    def do_save(self, *cmd_args):
        while True:
            filename = cli.InputPrompt('output filename').show()
            if not filename:
                return
            if os.path.isfile(filename):
                answer = cli.InputPrompt('filename "%s" already exists. Overwrite (y/N)?' % filename, 'n').show()
                should_overwrite = answer.lower()
                if should_overwrite == 'n':
                    print('\n')
                    continue

            new_metadata_config = self.generate_metadata()
            for config in new_metadata_config:
              self.metadata['tables'].append(config)

            with open(filename, 'w') as f:
                #f.write(json.dumps(self.metadata))
                f.write(common.jsonpretty(self.metadata))
            break

    def do_quit(self, *cmd_args):
        print('%s CLI exiting.' % self.name)        
        raise SystemExit

    do_q = do_quit

def main(args):
    metadata = None
    metadata_file = args['<metadata_file>']
    with open(metadata_file) as f:
        meta_string = f.read()
        metadata = json.loads(meta_string)

    list_mode = args.get('--list')
    add_mode = args.get('--add')
    if list_mode:
        #print(common.jsonpretty(metadata))
        table_list = [t['table_name'] for t in metadata['tables']]
        print('\n'.join(table_list))
    if add_mode:
        clear()
        config_cli = MkLookupsCLI('mklookups', metadata)
        config_cli.cmdloop()
if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    main(args)

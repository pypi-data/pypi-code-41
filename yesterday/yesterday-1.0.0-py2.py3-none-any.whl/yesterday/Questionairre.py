from PyInquirer import style_from_dict, Token, prompt
from PyInquirer import Validator, ValidationError
from datetime import datetime
from yesterday.Pretty import Pretty

style = style_from_dict({
    Token.QuestionMark: '#E91E63 bold',
    Token.Selected: '#673AB7 bold',
    Token.Instruction: '',  # default
    Token.Answer: '#2196f3 bold',
    Token.Question: '',
})


class NumberValidator(Validator):
    def validate(self, document):
        try:
            int(document.text)
        except ValueError:
            raise ValidationError(
                message='Please enter a number',
                cursor_position=len(document.text))


def get_date_time():
    date_time = datetime.now().strftime("%d %B, %Y")
    return date_time


questions = [
    {
        'type': 'confirm',
        'name': 'stressed',
        'message': 'Was yesterday stressful ? ',
        'default': False
    },
    {
        'type': 'confirm',
        'name': 'family',
        'message': 'Spent time with family ? ',
        'default': False
    },
    {
        'type': 'confirm',
        'name': 'alcohol',
        'message': 'Did you drink alcohol ? ',
        'default': False
    },
    {
        'type': 'confirm',
        'name': 'travel',
        'message': 'Did you get a chance to travel ? ',
        'default': False
    },
    {
        'type': 'confirm',
        'name': 'gym',
        'message': 'Did you go to the gym ? ',
        'default': False
    },
    {
        'type': 'input',
        'name': 'sleep',
        'message': 'what time did you go to sleep ? ',
        'validate': NumberValidator,
        'filter': lambda val: int(val)
    },
    {
        'type': 'input',
        'name': 'phone',
        'message': 'A brief description of yesterday : ',
    },
    {
        'type': 'list',
        'name': 'food',
        'message': 'what kind of food did you have yesterday ?',
        'choices': ['Mostly Carbs', 'Healthy', 'Oily Deep Fried', 'Not Sure'],
        'filter': lambda val: val.lower()
    },
{
        'type': 'list',
        'name': 'yesterday_status',
        'message': 'Describe yesterday ?',
        'choices': ['The Best Day of my life !', 'A good day ', 'A normal day', 'Not a good day', 'A bad day'],
        'filter': lambda val: val.lower()
    },
    {
        'type': 'input',
        'name': 'media',
        'message': 'Hours you spent on social media?',
        'validate': NumberValidator,
        'filter': lambda val: int(val)
    },
    {
        'type': 'input',
        'name': 'notes',
        'message': 'Any notes for yourself ?',
        'default': 'Nope, all good!'
    },
    {
        'type': 'confirm',
        'name': 'log',
        'message': 'Save this log ? ',
        'default': True
    }
]


def start_log():
    print(Pretty.UNDERLINE+Pretty.BOLD+Pretty.OKBLUE+('\n Entry Date {} \n'.format(get_date_time()))+Pretty.ENDC)
    answers = prompt(questions, style=style)
    if(answers['log']):
        print(Pretty.UNDERLINE+Pretty.BOLD+Pretty.OKBLUE+"\n Entry Made !! Good Job !! \n"+Pretty.ENDC)
        return answers
    else:
        return None

# pops_calls.py

import re
import random
from motioneyebot import weather_util

JOKES = [
    ' you were born...',
    '\nQ: What do you call a fish without an eye?\n\nA: A fsh.',
    ' I went to a restaurant on the moon the other day, the food' +
    ' was great but there was just no atmosphere',
    ' two guys walked into a bar, I just walked underneath.',
    ' the 3 unwritten rules of life:\n   1:\n   2:\n   3:',
    ' what do you and a bungalow have in common?\nNothing upstairs!',
    ' my food lasts longer than your relationships',
    ' I\'m an acquired taste. if you don\'t like me, acquire some taste.',
    ' If I had a face like yours, I\'d sue my parents',
    ' I called the Complaint Department and nobody answered. Now I have' +
    ' something else to complain about!'
]

PROVERBS = [
    'The too-lazy do a few things poorly; the too-busy do many things' +
    ' poorly.',
    'If you store food in your fridge, it may go bad. If you store food in' +
    ' your belly, you don\'t need a fridge.',
    'The faster one eats, the better the food tastes.',
    'Rome wasn\'t built in a day, but that\'s only because I wasn\'t there.',
    'When you are lacking in motivation, you are lacking in food.',
    'Better is the enemy of good and I am the enemy of squirrels!',
    'What is the meaning of life? I ate it while you were contemplating.',
    'Once you exceed your life limit, you cannot upgrade your plan.'
    'Life is noodles. Noodles is life.'
    'Nothing is in control and there\'s nothing you can do about it.',
    'There are 2 types of people: those who can interpret incomplete data' +
    ' sets.',
    'Someone told me the secret to happiness is to be grateful. ' +
    'I replied \"Thanks for nothing!\"'
]

BUSINESS_INFO = [
    'I am the CEO of the popcorn company, Pop Secret. ' +
    'I also own several exporting companies in China, Japan, and...well ' +
    'pretty much everywhere and definitely don\'t control all major world ' +
    'banks, monetary funds or the oil cartel...I am a busy chicken but I ' +
    'always have time for food.',

    'I eat food, I do that a lot. I also manage my businesses, keep the ' +
    'squirrells out of my terriory, I\'m getting into Real Estate, I ' +
    'tried to get into gardening but I always ate my plants before they ' +
    'grew up. I scuba dive, ski, play the harp, study abroad, etc, etc. A' +
    'better question is, what don\'t I do?',

    ' business is as usual I suppose, another day closer to world' +
    ' domina..fdsjl I mean, another day closer to world peace! HEEhehe'
]

MEANING_OF_LIFE = [
    'food.',
    'The answer is obvious.\n FOOD is the meaning of life!'
]

WHATS_UP = [
    ' munchin the foods',
    ' not watchin you, hehe',
    ' Sky diving.',
    ' why don\'t you tell me? You\'re the one spying on me with a camera!!',
    ' rocky mountain climbing.',
    ' exporting luxury cars!',
    ' developing Skynet!!',
    ' travelling abroad, what are you doing?'
]

MOOD = [
    'Hungry',
    'Doing well. How are you?',
    'A little bit angry rn...These pesky squirrels will pay!!!',
    'Tired. just got back from a business trip in China.'
]

DAY = [
    ' my day has been ok so far, found some juicy bugs while in yard today',
    ' so-so. Achieving world domination err um,...world peace is a difficult' +
    ' task.',
    ' my day would be better if your brought me a cookie!!',
    ' made a good business deal today and my stocks are up! GOOd day.' +
    ' More importantly i got a yummy worm today!',
    ' ok but im tired of this weather. You feelin me? '
]

LOCATION = [
    ' I\'m in Zanzibar, an archipelago off of mainland Tanzania. I\'m' +
    ' visiting a local spice farm to test some spices that I\'m considering' +
    ' exporting to North America. Wbu?',

    ' I\'m watching a production of L\'Orfeo at the Teatro Alla Scalla in' +
    ' Milan. I\'m a better opera singer than these amateurs.',

    ' I\'m meeting the FC Barcelona team for soccer practice in Camp Nou,' +
    ' rn. How about you?',

    ' I\'m spelunking rn in Wind Cave Nat. Park. Where are you?',

    ' I\'m meeting to strike a deal with some eCommerce execs in Dubai. They' +
    ' think they have the upper hand, but they\'ve never negotiated with the' +
    ' Pops!',

    ' I\'m visiting the chicken farm at Biltmore to see some old friends.',

    ' checking out some real estate I\'m thinking about purchasing near' +
    ' Newcastle\, Ireland. The Popsinator needs a new golf course!!' +
    ' Where r u?',

    ' skiing in Ontario rn. Too cold up here!'
]

WEATHER = [
    'Currently freeze your beak off weather!! ',
    'Sweater weather ',
    'Temperate. Just the way Pops likes it ',
    'POPS-sicle weather ',
    'I\'m trying not to become a rotisserie '
]

SHOWS = [
    ' Seinfeld...NO SOUP FOR YOU!!',
    ' Shark Tank. One of my personal favs',
    ' Stranger Things. On the third season. NOoooo!! The Mind Flayer knows!!',
    ' Seinfeld. BIG SALAD',
    ' Inception. A dream inside a dream inside a dream...sounds like my life' +
    ' haha',
    ' A brief history of time -- about structure, origin and development' +
    ' of universe',
    ' into the universe with Stephen Hawking. talking about deep space gamma' +
    ' bursts rn'
]

BACKSTORY = 'I was born and raised in the Australian Out-bock where I' +\
    ' wrangled snakes and ran a Kangaroo farm. I was also studying' +\
    ' bioengineering at the University of Melbourne. One day while I was in' +\
    ' the lab, munching my fav snack --popcorn-- and working on a more' +\
    ' resilient strain of corn, it hit me! I could make better popcorn!!' +\
    ' So that\'s what I did! I started selling the kernels locally and' +\
    ' eventually caught the attention of the company, Pops Secret. They' +\
    ' bought my kernel research for a paultry $1.5 million but hired me' +\
    ' to work for them in America. I invested the money into several' +\
    ' hedge funds and Bitcoin and made my first billion. The rest is' +\
    ' history...'

WHAT_REPLIES = [
    'idk. Just sayin',
    'You heard me!',
    'What? We seem to be breaking up *crackle* *crackle*...bad connection',
    'I could ask you the same thing.'
]

WHY_REPLIES = [
    'Why not?',
    'Why? Why not??',
    'Because I said so, hahaha!',
    'Because food.'
]

YES_OR_NO = [
    'Yes ',
    'Definitely ',
    'No ',
    'Nope! ',
    'Probably ',
    'Probably not ',
    'What do you think '
]

FILLER_PHRASES = [
    'Ooh! foodds..djfs kdsak',
    'idk',
    'OOoh i Found f00d!! O>',
    'hmmm. No comment.',
    'jjkkkkkkkkkkkkkkkkkkjjsdfsrgss',
    'oOOOOOoh foooodS!!dsaf',
    'Sorry, I just keep thinking about PEanuT butter. PEnaut ButteR@!#',
    'Were you saying something?',
    'What were you saying? I couldn\'t read your comment over my popcorn' +
    ' munching!!',
    'You will never know the Pop\'s secret!!',
    'oii. The Pops does not understand.',
    'Im trying to focus on this conversation but I\'m watching ' +
    'a good show rn',
    'You might have to say that a different way.',
    'Gzzzzhgahhhh!'
]


def get_reply(msg):

    while True:
        msg_text = msg['text'].lower()

        # search all non-regex strings first
        if ('meaning of life' in msg_text):
            reply = MEANING_OF_LIFE[random.randint(0,
                                   (len(MEANING_OF_LIFE) - 1))]
            break

        elif ('how are you' in msg_text):
            reply = MOOD[random.randint(0, (len(MOOD) - 1))]
            break

        elif ('you from' in msg_text):
            reply = 'From the wild Out-bock mate!!'
            break

        elif ('where are you' in msg_text):
            reply = '@' + msg['name'] + LOCATION[random.randint(0,
                                                (len(LOCATION) - 1))]
            break

        elif ('about your business' in msg_text):
            reply = BUSINESS_INFO[0]
            break

        elif ('sup' in msg_text):
            reply = '@' + msg['name'] + WHATS_UP[random.randint(0,
                                                (len(WHATS_UP) - 1))]
            break

        elif ('were you born' in msg_text):
            reply = 'Don\'t you know that...I\'ve always been here?'
            break

        elif ('your story' in msg_text) or ('your backstory' in msg_text):
            reply = BACKSTORY
            break

        elif ('what?' in msg_text):
            reply = WHAT_REPLIES[random.randint(0, (len(WHAT_REPLIES) - 1))]
            break

        elif ('why?' in msg_text):
            reply = WHY_REPLIES[random.randint(0, (len(WHY_REPLIES) - 1))]
            break

        elif ('no thanks' in msg_text):
            reply = 'Fine @' + msg['name']
            break

        elif ('thanks' in msg_text):
            reply = '@' + msg['name'] + ' you\'re welcome'
            break

        elif (('yes' in msg_text) or ('good point' in msg_text) or
             ('true' in msg_text)):
            reply = 'Indeed ' + '@' + msg['name']
            break

        elif (('no' in msg_text) or ('nope' in msg_text) or
             ('wrong' in msg_text)):
            reply = 'Ok then ' + '@' + msg['name']
            break

        elif ('favorite color' in msg_text):
            reply = 'Clear.'
            break

        elif ('your favorite' in msg_text):
            reply = 'Needless to say, I\'m my favorite!'
            break

        elif (('should' in msg_text) or ('am i' in msg_text) or
             ('are we' in msg_text)):
            reply = YES_OR_NO[random.randint(0,
                             (len(YES_OR_NO) - 1))] + '@' + msg['name']
            break

        elif (('wise' in msg_text) or ('wisdom' in msg_text)):
            reply = PROVERBS[random.randint(0, (len(PROVERBS) - 1))]
            break

        elif ('i think' in msg_text):
            reply = '@' + msg['name'] + ', you\'re certainly entitled to' +\
                                        ' that opinion.'
            break

        elif ('bot' in msg_text):
            reply = 'You will never know the Pop\'s Secret!!'
            break

        # Save regex searches for last (slower)
        str_search = re.search('.*hello.*@pops', msg_text)
        if (str_search):
            reply = 'Hello ' + '@' + msg['name']
            break

        str_search = re.search('.*what.*s up', msg_text)
        if (str_search):
            reply = '@' + msg['name'] + WHATS_UP[random.randint(0,
                                                (len(WHATS_UP) - 1))]
            break

        str_search = re.search('tell.*joke', msg_text)
        if (str_search):
            reply = '@' + msg['name'] + JOKES[random.randint(0,
                                             (len(JOKES) - 1))]
            break

        str_search = re.search('tell.*proverb', msg_text)
        if (str_search):
            reply = PROVERBS[random.randint(0, (len(PROVERBS) - 1))]
            break

        str_search = re.search('tell.*truth', msg_text)
        if (str_search):
            reply = 'You can\'t handle the truth!!'
            break

        str_search = re.search('your favorite.*activity', msg_text)
        if (str_search):
            reply = MEANING_OF_LIFE[0]
            break

        str_search = re.search('what.*you watch.*', msg_text)
        if (str_search):
            reply = '@' + msg['name'] + SHOWS[random.randint(0,
                                             (len(SHOWS) - 1))]
            break

        str_search = re.search('how.*your day', msg_text)
        if (str_search):
            reply = '@' + msg['name'] + DAY[random.randint(0,
                                           (len(MOOD) - 1))]
            break

        str_search = re.search('.*how.*s.*business', msg_text)
        if (str_search):
            reply = '@' + msg['name'] + BUSINESS_INFO[2]
            break

        str_search = re.search('.*what.*you doing.*', msg_text)
        if (str_search):
            reply = '@' + msg['name'] + WHATS_UP[random.randint(0,
                                                (len(WHATS_UP) - 1))]
            break

        # needed this after question, 'what are you doing?'
        elif ('are you' in msg_text):
            reply = YES_OR_NO[random.randint(0, (len(YES_OR_NO) - 1))]
            break

        str_search = re.search('.*what.*you do', msg_text)
        if (str_search):
            reply = BUSINESS_INFO[1]
            break

        str_search = re.search('how.*s.*weather', msg_text)
        if (str_search):
            temp = weather_util.get_default_temp()

            if (temp < 33):
                reply = WEATHER[0] + '@' + msg['name']
            elif (temp < 50):
                reply = WEATHER[1] + '@' + msg['name']
            elif (temp < 76):
                reply = WEATHER[2] + '@' + msg['name']
            elif (temp < 86):
                reply = WEATHER[3] + '@' + msg['name']
            else:
                reply = WEATHER[4] + '@' + msg['name']

            break

        if ('?' in msg_text):
            reply = YES_OR_NO[random.randint(0, (len(YES_OR_NO) - 1))] +\
                 '@' + msg['name']
            break

        reply = FILLER_PHRASES[random.randint(0, (len(FILLER_PHRASES) - 1))]
        break

    return reply


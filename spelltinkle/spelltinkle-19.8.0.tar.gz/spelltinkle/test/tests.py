import time

from .selftest import test


@test(args=['asdf'])
def writeas(session):
    yield '^d^k^k12345<enter><home><home>^k^p^p^a^k^p^p^a^k^p^p^p^p.<enter>'
    yield '# hello<enter>'
    yield 'A' * 25 * 1
    yield '<up>^a^b^b<down>^c<page-up>^p'
    yield 'if 1:<enter>a = 1<enter>b = a'
    yield '<enter>^t^s<bs><bs><bs><bs>writeas.txt<enter>'


@test(args=['open2.py'])
def open2(session):
    with open('open2.py', 'w') as fd:
        fd.write('# hello\na = 42\n')
    yield '<home><home>^fhello^f <home>^b^b<up>^d'
    yield '^fA<right>^k^t^s'
    yield '<bs>' * len('open2.py')
    yield 'open2b.py<enter>'
    yield '^oopen2.py<enter>^s2^q'


@test
def mouse(session):
    session.scr.position = (3, 1)
    yield 'a.bc<enter><mouse1-clicked>^d'
    assert session.docs[-1].lines[0] == 'abc'
    session.scr.position = (3, 4)
    yield '<mouse1-clicked>'
    assert session.docs[-1].view.pos == (1, 0)
    yield '1<enter>2<enter><up><up><up><end><down>'
    assert session.docs[-1].view.pos == (1, 1)


@test
def noend(session):
    with open('noend.py', 'w') as fd:
        fd.write('a = {\n}')
    yield '^onoend.py<enter>'
    assert session.docs[-1].lines[1] == '}'
    yield '^q'


@test(args=['hmm1.py'])
def complete_import(session):
    yield 'from collect'
    session.docs[-1].completion.thread.join()
    yield '<tab>'
    assert session.docs[-1].lines[0].endswith('collections')
    yield '.ab'
    session.docs[-1].completion.thread.join()
    yield '<tab>'
    assert session.docs[-1].lines[0].endswith('collections.abc')
    yield ' import Seq'
    session.docs[-1].completion.thread.join()
    yield '<tab>'
    assert session.docs[-1].lines[0].endswith('Sequence')


@test
def replace(session):
    with open('Replace.py', 'w') as fd:
        fd.write('a = {\n}')
    yield '^oRepl<tab><enter><end><end><enter>aa<enter>aaa<enter>aaaa<enter>'
    yield '<home><home>^x/a/12<enter>ynyyynn!<down>.'
    yield '<home><home>^x/12/A<enter>!^s'
    txt = '|'.join(session.docs[-1].lines)
    assert txt == 'A = {|}|aA|AAa|aAAA|.', txt
    yield '^q'


@test(args=['openline.txt:2'], files=[('openline.txt', '1\n2\n')])
def openline(session):
    assert session.docs[-1].view.pos == (1, 0), session.docs[-1].view.pos
    yield '^q'


@test
def test9(session):
    yield 'abc<enter>'
    yield '123<enter>'
    session.scr.position = (4, 1)
    yield '<mouse1-clicked>'
    session.scr.position = (5, 2)
    yield '<mouse1-released>'
    time.sleep(0.5)
    session.scr.position = (2, 1)
    yield '<mouse2-clicked>'
    assert ''.join(session.doc.lines) == 'c123abc123'


@test
def test10(session):
    yield 'AAA^rA^r^r'
    pos = session.docs[0].view.pos
    assert pos == (0, 1), pos


@test(args=['hmm.py'])
def jedi(session):
    yield 'a11 = 8<enter>'
    yield 'a12 = 8<enter>'
    yield 'a1'
    session.docs[-1].completion.thread.join()
    yield '<tab>'
    x = session.docs[-1].lines[-1]
    assert x == 'a11', session.docs[-1].lines


@test
def write(session):
    yield 'abc'
    with open('abc.123', 'w') as fd:
        fd.write('123')
    yield '^sabc.123<enter><enter>abc.1234<enter>...^s'


@test(files=[('mmmm/grrr/abc.txt', 'hmm')])
def fileinput(session):
    yield '^ommm<tab><tab><tab><enter>'
    print(session.docs[1].lines)
    assert session.docs[1].lines[0] == 'hmm'
    yield '^q'


@test
def rectangle_insert(session):
    yield 'aaa<enter>'
    yield 'a<enter>'
    yield 'aa<enter>'
    yield 'aaa<enter>'
    yield '12^a^k<up><right><ctrl_up><up><up><right>^b^p'
    assert '+'.join(session.docs[0].lines) == 'a12a+a+a12+a12a+'


@test
def mark_and_copy(session):
    yield 'a1234<left>^w^p'
    assert session.docs[0].lines[0] == 'a1234a1234'


# @test
def mail(session):
    from ..config import conf
    conf.mail = {'test': {'host': 'test', 'user': 'test'}}
    (session.folder / 'mail/test').mkdir(parents=True)
    (session.folder / 'mail/test/pw').write_text('test')
    (session.folder / 'mail/addresses.csv').write_text(
        'test@test.org,test,Sloof Lirpa\n')
    yield '^vm^q^q'


def calender(session):
    yield '^vc^q^q'


@test
def goto_line(session):
    yield '1<enter>2<enter>3^x2<enter>'
    print(session.docs[0].view.pos)
    assert session.docs[0].view.pos == (1, 0)


@test
def resolve_conflict(session):
    yield '<<<<<<<<<<<<<<<enter>1<enter>=======<enter>2<enter>>>>>>>>><enter>'
    print(session.docs[0].view.pos)
    yield '^x1<enter>^t^r'
    assert session.docs[0].lines == ['1', '']


@test
def diff(session):
    yield '1<enter>2<enter>3<enter>4<enter>'
    yield '^s1234<enter>'
    yield '^x2<enter>.'
    yield '^t^d'
    yield '^x6<enter>^t^r^t^d'
    assert ''.join(session.docs[0].lines) == '1234'


@test
def indent(session):
    yield 'def f(<enter>):<enter>'
    print(session.docs[0].view.pos)
    assert session.docs[0].view.pos == (2, 4)

from io import StringIO

from lxml import etree as et

punc_endings = ('.', '?', '!')


def cooked_citation(func):
    def wrapper(**kwargs):
        text = func(**kwargs)
        try:
            et.XML(text)
        except et.XMLSyntaxError:
            # try to escape ampersands, prevent double escape
            text = text.replace("&amp;", "$$_pubtools_amp;")
            text = text.replace("&lt;", "$$_pubtools_lt;")
            text = text.replace("&gt;", "$$_pubtools_gt;")
            text = text.replace("&quot;", "$$_pubtools_quot;")
            text = text.replace("&", "&amp;")
            text = text.replace("$$_pubtools_amp;", "&amp;")
            text = text.replace("$$_pubtools_lt;", "&lt;")
            text = text.replace("$$_pubtools_gt;", "&gt;")
            text = text.replace("$$_pubtools_quot;", "&quot;")
        if kwargs.get('use_abstract'):
            return text.replace('\n', '').strip()
        else:
            return text.strip()

    return wrapper


def punctuate(text, punctuation, space=''):
    if not text:
        return text
    if punctuation in punc_endings and text[-1] in punc_endings:
        return text + space
    elif punctuation not in punc_endings and text[-1] == punctuation:
        return text + space
    elif text[-1] == ' ':
        return punctuate(text.strip(), punctuation, space)
    else:
        return text + punctuation + space


def period(text):
    return punctuate(text, '.', ' ')


def comma(text):
    return punctuate(text, ',', ' ')


def colon(text):
    return punctuate(text, ':', ' ')


def colon_no_space(text):
    return punctuate(text, ':', '')


def semi_colon(text):
    return punctuate(text, ';', ' ')


def semi_colon_no_space(text):
    return punctuate(text, ';', '')


def cookauthor(author):
    if isinstance(author, dict):
        suffix = author.get('suffix') and ' ' + author['suffix'] or ''
        initial = author.get('iname') or author.get('fname') and author['fname'][0].upper() or ''
        if initial:
            initial = ' ' + initial
        return (author.get('cname', '') or author.get('lname') or '') + initial + suffix
    return author


@cooked_citation
def book_citation(authors=(), editors=(), title='', pubdate='', pagination='',
                  edition='', series='', pubplace='', publisher='', html=False, **kwargs):
    """ book citation

    :param authors: iterable. Individual elements can be dict or plain text
    :param editors: same functionality as authors
    :param title: str
    :param pubdate: str formatted date
    :param pagination: str
    :param edition: str
    :param series: str
    :param pubplace: str
    :param publisher: str
    :param html: boolean
    :param kwargs: additional params catchall
    :return: str
    """
    out = StringIO()
    if html:
        out.write('<span>')
    if editors and not authors:
        out.write(period('{}, editor{}'.format(
            ', '.join([cookauthor(e).replace(',', ' ') for e in editors]), len(editors) > 1 and 's' or '')))
    if authors:
        out.write(period(', '.join([cookauthor(a).replace(',', ' ') for a in authors])))
    if title:
        out.write(period(title))
    if edition:
        out.write(period(edition))
    if editors and authors:
        out.write(period('{}, editor{}'.format(
            ', '.join([cookauthor(e).replace(',', ' ') for e in editors]), len(editors) > 1 and 's' or '')))
    if pubplace:
        if publisher:
            out.write(colon(pubplace))
        else:
            out.write(period(pubplace))
    if publisher:
        if pubdate:
            out.write(semi_colon(publisher))
        else:
            out.write(period(publisher))
    if pubdate:
        out.write(period(pubdate))
    if pagination:
        out.write('p. {0}'.format(period(pagination)))
    if series:
        out.write('({})'.format(series))
    out = out.getvalue().strip()
    if html:
        out += '</span>'
    return out


@cooked_citation
def chapter_citation(authors=(), editors=(), title='', pubdate='', pagination='',
                     edition='', series='', pubplace='', booktitle='', publisher='', html=False, **kwargs):
    """ book chapter citation

    :param authors: iterable. Individual elements can be dict or plain text
    :param editors: same functionality as authors
    :param title: str (chapter title)
    :param pubdate: str formatted date
    :param pagination: str
    :param edition: str
    :param series: str
    :param pubplace: str
    :param booktitle: str
    :param publisher: str
    :param html: boolean
    :param kwargs: additional params catchall
    :return: str
    """
    out = StringIO()
    if html:
        out.write('<span>')
    if editors and not authors:
        out.write(period('{}, editor{}'.format(
            ', '.join([cookauthor(e).replace(',', ' ') for e in editors]), len(editors) > 1 and 's' or '')))
    if authors:
        out.write(period(', '.join([cookauthor(a).replace(',', ' ') for a in authors])))
    if title:
        out.write(period(title))
    if edition or editors or booktitle:
        out.write('In: ')
    if editors and authors:
        out.write(period('{}, editor{}'.format(
            ', '.join([cookauthor(e).replace(',', ' ') for e in editors]), len(editors) > 1 and 's' or '')))
    if booktitle:
        out.write(period(booktitle))
    if edition:
        out.write(period(edition))
    if pubplace:
        if publisher:
            out.write(colon(pubplace))
        else:
            out.write(period(pubplace))
    if publisher:
        if pubdate:
            out.write(semi_colon(publisher))
        else:
            out.write(period(publisher))
    if pubdate:
        out.write(period(pubdate))
    if pagination:
        out.write('p. {}'.format(period(pagination)))
    if series:
        out.write('({})'.format(series))
    out = out.getvalue().strip()
    if html:
        out += '</span>'
    return out


@cooked_citation
def conference_citation(authors=(), editors=(), title='', pubdate='', pagination='', pubplace='', place='',
                        conferencename='', conferencedate='', publisher='', html=None, **kwargs):
    """ conference citation

    :param authors: iterable. Individual elements can be dict or plain text
    :param editors: same functionality as authors
    :param title: str
    :param pubdate: str formatted date
    :param pagination: str
    :param pubplace: str (location of publication)
    :param place: str (location of conference event)
    :param conferencename: str
    :param conferencedate: str formatted
    :param publisher: str
    :param html: boolean
    :param kwargs: additional params catchall
    :return: str (unicode in py2) if not not italicize, otherwise HTML
    """
    out = StringIO()
    if html:
        out.write('<span>')
    if editors and not authors:
        out.write(period('{}, editor{}'.format(
            ', '.join([cookauthor(e).replace(',', ' ') for e in editors]), len(editors) > 1 and 's' or '')))
    if authors:
        out.write(period(', '.join([cookauthor(a).replace(',', ' ') for a in authors])))
    if title:
        out.write(period(title))
    if editors and authors:
        out.write(period('{}, editor{}'.format(
            ', '.join([cookauthor(e).replace(',', ' ') for e in editors]), len(editors) > 1 and 's' or '')))
    if conferencename and html:
        out.write(semi_colon('<i>Proceedings of {}</i>'.format(conferencename)))
    elif conferencename:
        out.write(semi_colon('Proceedings of {}'.format(conferencename)))
    if conferencedate:
        if place or pubdate or publisher:
            out.write(semi_colon(conferencedate))
        else:
            out.write(period(conferencedate))
    if place:
        out.write(period(place))
    if pubplace:
        if publisher or pubdate:
            out.write(colon(pubplace))
        else:
            out.write(period(pubplace))
    if publisher:
        if pubdate:
            out.write(semi_colon(publisher))
        else:
            out.write(period(publisher))
    if pubdate:
        out.write(period(pubdate))
    if pagination:
        out.write('p. {}'.format(period(pagination)))
    out = out.getvalue().strip()
    if html:
        out += '</span>'
    return out


@cooked_citation
def journal_citation(authors=(), title='', journal='', pubdate='', volume='', issue='', pagination='', abstract=None,
                     pubmodel='Print', edate='', doi='', use_abstract=False, html=False, **kwargs):
    """ journal citation

    :param authors: iterable. Individual elements can be dict or plain text
    :param title: str
    :param journal: str
    :param pubdate: str formatted date
    :param volume: str
    :param issue: str
    :param pagination: str
    :param abstract: iterable. Individual elements can be dict or plain text
    :param pubmodel: determines which date types to use
    :param edate: str formatted date
    :param doi: str
    :param use_abstract: boolean. If using abstract, result will be HTML
    :param html: boolean
    :param kwargs: additional params catchall
    :return: str (unicode in py2) if not abstract and not italicize, otherwise HTML
    """
    if not abstract:
        abstract = {}
    out = StringIO()
    if html:
        out.write('<span>')
    if authors:
        out.write(period(', '.join([cookauthor(a).replace(',', ' ') for a in authors if a])))
    if title:
        out.write(period(title))
    if journal and html:
        out.write('<i>{}</i> '.format(journal.strip()))
    elif journal:
        out.write(period(journal.strip()))

    if pubmodel in ('Print', 'Electronic', 'Print-Electronic'):  # use the publication date
        date = pubdate
    elif pubmodel in ('Electronic-Print', 'Electronic-eCollection'):  # use the electronic date
        date = edate
    else:
        date = pubdate or edate

    if date:
        if pagination and not (volume or issue):
            out.write(colon(date))
        elif volume or issue:
            out.write(semi_colon_no_space(date))
        else:
            out.write(period(date))
    if volume:
        if pagination and not issue:
            out.write(colon_no_space(volume))
        elif pagination:
            out.write(volume)
        else:
            out.write(period(volume))
    if issue:
        if pagination:
            out.write(colon_no_space('({})'.format(issue)))
        else:
            out.write(period('({})'.format(issue)))
    if pagination:
        out.write(period(pagination))
    if pubmodel in ('Print-Electronic',):
        if edate:
            out.write('Epub ' + period(edate))
    if pubmodel in ('Electronic-Print',):
        if pubdate:
            out.write('Print ' + period(pubdate))
    if pubmodel in ('Electronic-eCollection',):
        if pubdate:
            if doi:
                out.write('doi: {}. eCollection {}'.format(doi, period(pubdate)))
            else:
                out.write('eCollection {}'.format(period(pubdate)))

    if use_abstract:
        out.write('<br/>')
        abstracts = []
        for seg in abstract:
            abst = seg.get('label') or ''
            abst += abst and ': ' or ''
            abst += seg.get('text') or ''
            if abst:
                abstracts.append('<p>{}</p>'.format(abst))
        abstract = ' '.join(abstracts)
        if abstract:
            out.write(
                '<div class="citationAbstract"><p class="abstractHeader"><strong>Abstract</strong></p>{}</div>'.format(
                    abstract))
    out = out.getvalue().strip()
    if html:
        out += '</span>'
    return out


@cooked_citation
def monograph_citation(authors=(), title='', pubdate='', series='', pubplace='', weburl='', reportnum='', publisher='',
                       serieseditors=(), html=False, **kwargs):
    """ book chapter citation

    :param authors: iterable. Individual elements can be dict or plain text
    :param serieseditors: same functionality as authors
    :param title: str
    :param pubdate: str formatted date
    :param series: str
    :param pubplace: str
    :param publisher: str
    :param weburl: str
    :param reportnum: str
    :param kwargs: additional params catchall
    :return: str
    """
    out = StringIO()
    if html:
        out.write('<span>')
    if serieseditors and not authors:
        out.write(period('{}, editor{}'.format(
            ', '.join([cookauthor(e).replace(',', ' ') for e in serieseditors]),
            len(serieseditors) > 1 and 's' or '')))
    if authors:
        out.write(semi_colon(', '.join([cookauthor(a).replace(',', ' ') for a in authors])))
    if title:
        out.write(period(title))
    if series:
        out.write(period(series))
    if serieseditors and authors:
        out.write(period('{}, editor{}'.format(
            ', '.join([cookauthor(e).replace(',', ' ') for e in serieseditors]),
            len(serieseditors) > 1 and 's' or '')))
    if pubplace:
        if publisher:
            out.write(colon(pubplace))
        elif pubdate:
            out.write(semi_colon(pubplace))
        else:
            out.write(period(pubplace))
    if publisher:
        if pubdate:
            out.write(semi_colon(publisher))
        else:
            out.write(period(publisher))
    if pubdate:
        out.write(period(pubdate))
    if reportnum:
        out.write(period(reportnum))
    if weburl:
        out.write('Available at {0}.'.format(weburl))
    out = out.getvalue().strip()
    if html:
        out += '</span>'
    return out


@cooked_citation
def report_citation(authors=(), editors=(), title='', pubdate='', pagination='', series='', pubplace='', weburl='',
                    reportnum='', publisher='', html=False, **kwargs):
    """ book chapter citation

    :param authors: iterable. Individual elements can be dict or plain text
    :param editors: same functionality as authors
    :param title: str
    :param pubdate: str formatted date
    :param pagination: str
    :param series: str
    :param pubplace: str
    :param publisher: str
    :param weburl: str
    :param reportnum: str
    :param kwargs: additional params catchall
    :return: str
    """
    out = StringIO()
    if html:
        out.write('<span>')
    if editors and not authors:
        out.write(period('{}, editor{}'.format(
            ', '.join([cookauthor(e).replace(',', ' ') for e in editors]), len(editors) > 1 and 's' or '')))
    if authors:
        out.write(period(', '.join([cookauthor(a).replace(',', ' ') for a in authors])))
    if title:
        out.write(period(title))
    if series:
        out.write(period(series))
    if editors and authors:
        out.write(period('{}, editor{}'.format(
            ', '.join([cookauthor(e).replace(',', ' ') for e in editors]), len(editors) > 1 and 's' or '')))
    if pubplace:
        if publisher:
            out.write(colon(pubplace))
        elif pubdate:
            out.write(semi_colon(pubplace))
        else:
            out.write(period(pubplace))
    if publisher:
        if pubdate:
            out.write(semi_colon(publisher))
        else:
            out.write(period(publisher))
    if pubdate:
        out.write(period(pubdate))
    if reportnum:
        out.write(period(reportnum))
    if pagination:
        out.write(period('p. {0}'.format(pagination)))
    if weburl:
        out.write('Available at {0}.'.format(weburl))
    out = out.getvalue().strip()
    if html:
        out += '</span>'
    return out

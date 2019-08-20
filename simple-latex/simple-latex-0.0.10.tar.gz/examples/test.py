from simple_latex import Preamble, Package, Documentclass, Definition, Command, NewCommand, RenewCommand, BeginClass, EndClass, Document, SimpleLatexDocument
sld = SimpleLatexDocument()
# Create Preamble with documentclass
preamble = Preamble("Feedback on Items for Santa Monica City Council Agenda on \\today", "prepared by sm.engage.town", "\\today",
                    documentclass=Documentclass("scrbook", {"oneside": None}))
# Packages
preamble.add(Package('geometry', {"top": "2.5cm",
                                  "right": "2.5cm",
                                  "bottom": "2.5cm",
                                  "left": "2.5cm"}))
preamble.add(Package('hyperref', {"pdfpagelayout": "useoutlines",
                                  "bookmarks": None,
                                  "bookmarksopen": "true",
                                  "bookmarksnumbered": "true",
                                  "breaklinks": "true",
                                  "linktocpage": None,
                                  "pagebackref": None,
                                  "colorlinks": "false",
                                  "linkcolor": "blue",
                                  "urlcolor": "blue",
                                  "citecolor": "red",
                                  "anchorcolor": "gren",
                                  "pdftex": None,
                                  "plainpages": "false",
                                  "pdfpagelabels": None,
                                  "hyperindex": "true",
                                  "hyperfigures": None}))

preamble.add(Package("inputenc", {"utf8": None}))
preamble.add(Package("tocbibind", {"nottoc": None}))
preamble.add(Package("setspace"))
preamble.add(Package("fancyhdr"))
preamble.add(Package("xcolor"))
preamble.add(Package("lastpage"))
preamble.add(Package("titlesec"))
preamble.add(Package("mdframed", {"framemethod": "tikz"}))
preamble.add(Command("hypersetup", values=["colorlinks=false, linktoc=all, linkcolor=black"]))
preamble.add(Command(command="titleformat",
                     optional="\\chapter",
                     parameters={"display": None},
                     values=["\\normalfont\\huge\\bfseries", "", "0pt", "\\Huge"]))
preamble.add(Command("titlespacing", "\\chapter", values=[
             "0pt", "-30pt", "20pt"], starred=True))
preamble.add(Command("pagestyle", values=["fancy"]))
preamble.add(Command("fancyhf", values=[""]))
preamble.add(RenewCommand("familydefault", "\\sfdefault"))
preamble.add(RenewCommand(
    "chaptermark", "\\markboth{\\MakeUppercase{#1}}{}", arguments="1"))
preamble.add(Command("fancyhead", parameters={
             "R": None}, values=["\\leftmark"]))
preamble.add(Command("fancyhead", parameters={
             "L": None}, values=["\\rightmark"]))
preamble.add(Command("fancyfoot", parameters={"R": None}, values=[
             "\\thepage \\ of \\pageref{LastPage}"]))
preamble.add(Command("newmdenv", parameters={
             "tikzsetting": "{fill=blue, draw=white}",
             "innerlinewidth": "0.5pt",
             "roundcorner": "4pt",
             "innerleftmargin": "6pt",
             "innerrightmargin": "6pt",
             "innertopmargin": "6pt",
             "innerbottommargin": "6pt"
             }, values=["titlebox"]))
preamble.add(Command("newmdenv", parameters={
             "tikzsetting": "{fill=green, draw=white}",
             "innerlinewidth": "1.5pt",
             "roundcorner": "4pt",
             "innerleftmargin": "6pt",
             "innerrightmargin": "6pt",
             "innertopmargin": "6pt",
             "innerbottommargin": "6pt"
             }, values=["probox"]))
preamble.add(Command("newmdenv", parameters={
             "tikzsetting": "{fill=red, draw=white}",
             "innerlinewidth": "1.5pt",
             "roundcorner": "4pt",
             "innerleftmargin": "6pt",
             "innerrightmargin": "6pt",
             "innertopmargin": "6pt",
             "innerbottommargin": "6pt"
             }, values=["conbox"]))
preamble.add(Command("newmdenv", parameters={
             "tikzsetting": "{fill=black, draw=white}",
             "innerlinewidth": "1.5pt",
             "roundcorner": "4pt",
             "innerleftmargin": "6pt",
             "innerrightmargin": "6pt",
             "innertopmargin": "6pt",
             "innerbottommargin": "6pt"
             }, values=["needbox"]))
preamble.add(Command("definecolor", values=["blue", "RGB", "225,225,255"]))
preamble.add(Command("definecolor", values=["white", "RGB", "255,255,255"]))
preamble.add(Command("definecolor", values=["green", "RGB", "0,150,0"]))
preamble.add(Command("definecolor", values=["black", "RGB", "0,0,0"]))
preamble.add(Command("definecolor", values=["red", "RGB", "255,0,0"]))

preamble.add(Definition("meetingdate", "Santa Monica City Council \\today"))
sld.add(preamble)

document = Document()
document.add(Command("maketitle"))
document.add(Command("thispagestyle", values=["fancy"]))
document.add(Command("tableofcontents"))
document.add(Command("thispagestyle", values=["fancy"]))
document.add(Command("chapter", values=["Item 3430", "Award Bid #4369 and enter into agreement with Mariposa Landscapes, Inc. for Citywide Landscape Maintenance Services"]))
document.add(Command("thispagestyle", values=["fancy"]))
document.add(BeginClass("probox"))
document.add(Command("textbf", values=[Command("color", values=["white"], text="Pro feedback")]))
document.add(EndClass("probox"))
document.add(BeginClass("enumerate"))
document.add(Command("item", text="Some pro feedback\n\nSome person\n\nsomeemail@email.com"))
document.add(Command("item", text="Some other pro feedback\n\nSome other person\n\nsomeotheremail@email.com"))
document.add(EndClass("enumerate"))


document.add(BeginClass("conbox"))
document.add(Command("textbf", values=[Command("color", values=["white"], text="Con feedback")]))
document.add(EndClass("conbox"))
document.add(BeginClass("enumerate"))
document.add(Command("item", text="Some con feedback\n\nSome person\n\nsomeemail@email.com"))
document.add(Command("item", text="Some other con feedback\n\nSome other person\n\nsomeotheremail@email.com"))
document.add(EndClass("enumerate"))


document.add(BeginClass("needbox"))
document.add(Command("textbf", values=[Command("color", values=["white"], text="Need more information feedback")]))
document.add(EndClass("needbox"))
document.add(Command("thispagestyle", values=["fancy"]))
sld.add(document)
print("XXXXXX")
sld.pdf("/Users/eliselkin/pdf", "something.tex", clean_output_directory=True, DEBUG=False)

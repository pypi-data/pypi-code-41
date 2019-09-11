def dat2irc(filename="mol.dat"):
    f=open(filename)
    content=f.read()
    f.close()

    header=" $contrl runtyp=irc $end\n"
    forward=" $irc saddle=.true. npoint=10 forwrd=.true. $end\n"
    backward=" $irc saddle=.true. npoint=10 forwrd=.false. $end\n"
    irc_forward=header + forward + content
    irc_backward=header + backward +content

    out=open("mol_ircfor.inp", 'w')
    out.write(irc_forward)
    out.close()

    out=open("mol_ircbak.inp", 'w')
    out.write(irc_backward)
    out.close()

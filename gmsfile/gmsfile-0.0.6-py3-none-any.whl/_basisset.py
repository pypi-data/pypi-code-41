class basisset:
	def basis(self, gbasis='sto3g'):
		sto3g =' $basis gbasis=sto ngauss=3 $end\n'
		g321  =' $basis gbasis=N21 ngauss=3 $end\n'
                g631d =' $basis gbasis=N31 ngauss=6 ndfunc=1 $end\n'
                g631dp=' $basis gbasis=N31 ngauss=6 ndfunc=1 npfunc=1 $end\n'
                g631plusdp=' $basis gbasis=N31 ngauss=6 $end\n'+ \
                            ' $basis ndfunc=1 npfunc=1 diffsp=.true. $end\n'
                g631doubleplusdp =' $basis gbasis=N31 ngauss=6 $end\n'+ \
                            ' $basis ndfunc=1 npfunc=1 $end\n' +\
                            ' $basis diffsp=.true. diffs=.true. $end\n'
                sbkjc = ' $basis gbasis=sbk ngauss=3 ndfunc=1 $end\n'+\
                        ' $contrl ecp=sbk $end\n'

                hw = ' $basis gbasis=hw ndfunc=1 $end\n' +\
                    '$contrl ecp=hw $end'

		card={
			'STO3G'  : sto3g,
			'STO-3G' : sto3g,

			'321G'   : g321,
			'3-21G'  : g321,


                        '631GD' : g631d,
                        '6-31GD' : g631d,
                        '6-31G(D)': g631d,
                        '631G(D)': g631d,
                        '631G*' : g631d,
                        '6-31G*' : g631d,

                        '631GDP': g631dp,
                        '6-31GDP':g631dp,
                        '631G(D,P)' : g631dp,
                        '6-31G(D,P)' : g631dp,
                        '631G**' : g631dp,
                        '6-31G**' : g631dp,

                        '631++GDP' : g631doubleplusdp,
                        '631++GDP' : g631doubleplusdp,
                        '631++G(D,P)' : g631doubleplusdp,
                        '6-31++G(D,P)' : g631doubleplusdp,
                        '631++G**' : g631doubleplusdp,
                        '631++G**' : g631doubleplusdp,

                        'SBKJC': sbkjc,
                        'HW': hw,
		}

		self.__basis__ = card[gbasis.upper()]

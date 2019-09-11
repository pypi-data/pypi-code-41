class purpose:

	def runtyp(self, purpose='opt'):

		energy=' $contrl runtyp=energy $end\n'

		opt   =' $contrl runtyp=optimize $end\n'+ \
		       ' $statpt opttol=0.0001 nstep=100 $end\n'

		freq  =' $contrl runtyp=hessian $end\n'+ \
		       ' $force method=analytic vibanl=.true. $end\n'

                sadpoint=' $contrl runtyp=sadpoint $end\n' +\
                         " $force method=analytic $end\n" +\
		         ' $statpt opttol=0.0001 nstep=30 hess=calc $end\n'

		card= {
			'ENERGY':energy,
			'OPT'   :opt, 
			'FREQ'  :freq, 
			'SADPOINT'   :sadpoint,
			}
		self.__purpose__= card[purpose.upper()]

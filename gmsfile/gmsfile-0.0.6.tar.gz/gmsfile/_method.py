class method:
	def method(self, type="rhf"):

		rhf   = ' $contrl scftyp=rhf maxit=100 $end\n'
		uhf   = ' $contrl scftyp=uhf maxit=100 $end\n'
		rohf  = ' $contrl scftyp=rohf maxit=100 $end\n'

		list={
			'RHF' :rhf,
			'UHF' :uhf,
			'ROHF':rohf,
		}
		self.__method__=list[type.upper()]

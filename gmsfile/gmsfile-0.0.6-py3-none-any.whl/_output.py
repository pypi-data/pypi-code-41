class output:
	def writefile(self, outfile="mol.inp"):
		data=''
		data += self.__purpose__
		data +=self.__method__
		data +=self.__basis__
		data +=self.__data__
		f=open(outfile, 'w')
		f.write(data)
		f.close()

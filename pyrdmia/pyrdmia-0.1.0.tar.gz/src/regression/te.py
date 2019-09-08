#Caso teste



	'''

def billard(x):
	data = []
	l = Rdmia.number(0)
	u = Rdmia.number(0)
	for val in range(len(x.data)):
		l = 29.664 + 0.330*x.data[val][1].lower()
		u = 45.070 + 0.308*x.data[val][1].upper()
		data.append(Rdmia.number(l,u))
	return data

		
	print("R^2 :",coefDetermination(y,r_list,y_mean))
	print("R^2 Billard:",coefDetermination(y,billard_r,y_mean))
	print("RMSE (lower,upper)",RMSE(r_list,y))
	print("RMSE_Billard (lower,upper)",RMSE(billard_r,y))
	cov_b_l,cov_b_u = cov(y.data,billard_r)
	aux_b_l,aux_b_u = (var(billard_r,y_mean))
	aux_2b_l,aux_2b_u = var_array(y.data,y_mean)
	print ("Covariancia BILLAR (lower,upper)",(cov_b_l/(aux_b_l*aux_2b_l)),(cov_b_u/(aux_b_u*aux_2b_u)))
	
	cov_b_l,cov_b_u = cov(y.data,r_list)
	aux_b_l,aux_b_u = (var(r_list,y_mean))
	aux_2b_l,aux_2b_u = var_array(y.data,y_mean)

	print ("Covariancia (lower,upper)",(cov_b_l/(aux_b_l*aux_2b_l)),(cov_b_u/(aux_b_u*aux_2b_u)))
	print ("Resultado Teste: ",z.data[0][0] + z.data[1][0]*Rdmia.number(118,126))
	'''

import biogeme.results as res


structResults = res.bioResults(pickleFile='05latentChoiceFull.pickle')
#structResults = res.bioResults(pickleFile='04latentChoiceSeq.pickle')
#structResults = res.bioResults(pickleFile='02oneLatentOrdered.pickle')
structBetas = structResults.getBetaValues()

for k,v in structBetas.items():
    print(f"{k} = Beta('{k}',{v},None,None,0)")

#for k,v in structBetas.items():
#    print(f"{k} = {v}")
    

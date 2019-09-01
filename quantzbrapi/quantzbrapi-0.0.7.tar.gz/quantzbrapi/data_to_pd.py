import pandas as pd 

def quote_to_pandas(data=None):
    df = pd.DataFrame(columns=["ativo","time", "volume", "open", "high", "low", "close"])
    for e in data:
        df = df.append(
            {
            "ativo"  : e["ativo"], 
            "time"   : e["time"],
            "volume" : e["volume"],
            "open"   : e["o"],
            "high"   : e["h"], 
            "low"    : e["l"], 
            "close"  : e["c"] 
            }, ignore_index=True ) 
    return df

def carteiras_to_pandas(data=None):
    df = pd.DataFrame(columns=["carteira","ativo", "tipo", "nome", "descricao"])
    carteira = data[0]['carteira']
    for e in data[0]['ativos']:
        df = df.append(
            {
            "carteira" : carteira,                    
            "ativo"  : e["ativo"], 
            "tipo"   : e["tipo_de_ativo"],
            "nome"   : e["nome_do_ativo"],
            "descricao" : e["descricao_do_ativo"]
            }, ignore_index=True )
    return df
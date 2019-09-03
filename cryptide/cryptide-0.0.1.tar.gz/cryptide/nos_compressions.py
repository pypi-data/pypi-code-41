Alphabet_default = "ABCDEFGHIJKLMNOPQRSTUVWXYZ &é\"'(-è_çà)=#{[|^$@]}\\*!:;.?,^ù%*+°/abcdefghijklmnopqrstuvwxyz1234567890"  # Alphabet du codex
dim_default = 3  # Dimension a CHOISIR


def Alphabet(texte):
    """Retourne les valeurs unique du texte donnee en parametre"""
    if isinstance(texte, bytes):
        texte = ''.join(map(chr, texte))

    return ''.join(sorted(list(set(texte))))


def generation_codex(dim, Alphabet):
    """
    :param dim: [Obligatoire] INT : La dimmension du codex
    :param Alphabet: [Obligatoire] STRING : l'Alphabet du codex

        Genere le codex a "dim" dimension et met a chaque dimension son alphabet

    :return: tableau a "dim" dimension
    """
    if ' ' not in Alphabet:
        Alphabet = Alphabet + ' '

    return [Alphabet] * dim


def echantinage_de(mot, dim):
    """
    :param mot: [Obligatoire] STRING : texte a coder
    :param dim: [Obligatoire] INT : La dimmension du codex

        Fais des paquet de lettre de taille "dim"

    :return:
    """
    var = ''
    decoupe_mot = []
    while len(mot) % dim != 0:
        mot += " "
    for i in range(len(mot)):
        var += mot[i]
        if len(var) % dim == 0:
            decoupe_mot.append(var)
            var = ''
    return decoupe_mot


def recherche_codex_equivalent_de(mot_decoupe, dim, cle, Alphabet):
    """Donne le nombre correspondant a chaque groupe de lettre donnees en parametre"""
    minicodex = generation_codex(dim, Alphabet)
    lon = len(minicodex[0])
    position_codex = []
    somme = 0
    for elem in mot_decoupe:
        for i in range(len(minicodex)):
            somme += minicodex[i].index(elem[i]) * (lon ** i)
        position_codex.append(somme)
        somme = 0
        Alphabet = permutation_codex(str(cle),Alphabet)
        minicodex = generation_codex(dim, Alphabet)
    return position_codex


def encodage(mot, dim=dim_default, Alphabet=Alphabet_default, cle="0000"):
    """Methode mere pour l encodage des fichiers"""
    if type(mot) == type(b'A'):
        mot = ''.join(map(chr, mot))
    mot_decoupe = echantinage_de(mot, dim)
    ensemble_des_localisations = recherche_codex_equivalent_de(mot_decoupe, dim, cle, Alphabet)
    # print(ensemble_des_localisations)
    return ''.join(map(chr, ensemble_des_localisations))


def auto_encodage(texte, dim=dim_default, cle = "0000"):
    """Encode en generent automatiquement l' Alphabet necessaire"""
    return encodage(texte, dim, Alphabet(texte))


def decodage(envoie, dim=dim_default, Alphabet=Alphabet_default, cle="0000", back='bytes'):
    """decode le texte"""
    minicodex = generation_codex(dim, Alphabet)
    nombre_a_localiser = []
    for i in range(len(envoie)):
        nombre_a_localiser.append(ord(envoie[i]))
    mot_recu = ""
    lon = len(minicodex[0])
    for elem in nombre_a_localiser:
        for i in range(dim):
            mot_recu += minicodex[i][(elem // lon ** i) % lon]
        Alphabet = permutation_codex(str(cle),Alphabet)
        minicodex = generation_codex(dim, Alphabet)

    while mot_recu[-1] == ' ':
        mot_recu = mot_recu[:-1]
    if back == 'bytes':
        return bytes(map(ord, mot_recu))
    else:
        return mot_recu

def permutation_codex(cle, alphabet):
	"""fais les permtation du codex partie chiffrment"""
	while len(cle) % 4 != 0:
		cle += '5'

	for i in range(0,len(cle),4):
		# print(i)
		deb = int(cle[i] + cle[i+1]) % len(alphabet)
		fin = int(cle[i+2] + cle[i+3]) % len(alphabet)
		if deb > fin:
			fin, deb = deb, fin
		# print (deb,fin)
		# print (alphabet[fin:] , alphabet[deb:fin] , alphabet [:deb])
		alphabet = alphabet[fin:] + alphabet[deb:fin] + alphabet [:deb]
	return alphabet

def main():
    message = 'Dev by Ursial'
    cle = "1212"
    x=encodage("Bonjour, MASTER Cyber défense et sécurité de l'information",cle=cle)
    open("compress.bal",'wb').write(x.encode())
    x=decodage(x ,cle=cle)
    print(x)
    open("uncompress.bal",'wb').write(x)

if __name__ == '__main__':
    main()

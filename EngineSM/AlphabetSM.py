class AlphabetSM:
    
    #Les ponctuations sont cumulables, pas les délimiteurs
    seprs = {\
        'punctuation' : ([".", "!", "?", ";", ":", ","], [0, 1, 1, 0, 0, 0]), \
        'delimiters' : (" ", "\'", "’", "«", "»", "\n", "\t", "\r", "(", ")", "[", "]", "{", "}", "\"", "$", "£", "€", "§", "/"),\
        'all' : (".", "!", "?", ";", ":", ",", " ", "\'", "’", "«", "»", "\n", "\t", "\r", "(", ")", "[", "]", "{", "}", "\"", "$", "£", "€", "§", "/", "-")}

    vowels = ['a','e','i','o','u','y','ë','ï','ö','â','ê','î','ô','û','ù','é','è'] #'ä' 'ü' 'ÿ'
    vowelsAccented = ['ë','ï','ö','â','ê','î','ô','û','ù','é','è', 'ä', 'ü', 'ÿ']
    consonants = ('z','r','t','p','q','s','d','f','g','h','j','k','l','m','w','x','c','v','b','n','ç')

    v = ''.join(vowels)
    c = ''.join(consonants)

    polygV = r'[' + v + ']+'
    #polygC = r'[' + c + ']{1} \1'
    monog = r'[' + v + ']{1}(?=[' + c + ']?)' #(?<=[^v]*)[v]{1}(?=[^v]*)
    accent = r'[' + ''.join(vowelsAccented) + r']{1}'
    sigle = r'([A-Z]\.){2,}'


    @classmethod
    def findIter(cls, st, sub):
        counts = []
        temp = False

        for i in range(0, len(st)):
            if st[i:i+len(sub)] == sub:
                counts.append(i)


        return counts

    pass

    @classmethod
    def generateDigraphsVowels(cls):

        v = ''.join(cls.vowels)
        listDig = ""

        for c in v:
            for d in v:
                listDig += c + d + "\n"
        return listDig
    pass

    @classmethod
    def generateTrigraphsVowels(cls):

        v = ''.join(cls.vowels)
        listTrig = ""

        for c in v:
            for d in v:
                for e in v:
                    listTrig += c + d + e + "\n"
        return listTrig
    pass

    @classmethod
    def generateDigraphsConsonants(cls):

        cn = ''.join(cls.consonants)
        listDig = ""

        for c in cn:
            for d in cn:
                listDig += c + d + "\n"
        return listDig
    pass

    @classmethod
    def generateTrigraphsConsonants(cls):

        cn = ''.join(cls.consonants)
        listTrig = ""

        for c in cn:
            for d in cn:
                for e in cn:
                    listTrig += c + d + e + "\n"
        return listTrig
    pass
pass


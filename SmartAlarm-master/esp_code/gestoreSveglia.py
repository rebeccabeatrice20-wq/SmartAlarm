"""
File che si occupa della definizione delle strutture necessarie ad implementare ogni singola sveglia e la relativa collezione di sveglie
La collezione di sveglie contiene sia un dizionario [id]:{sveglia} che una lista contenente tutti gli ids delle sveglie presenti,
per facilitare lo scorrimento della struttura
"""
from machine import RTC

class SVEGLIA:
    def __init__(self, id, nome, giorno, mese, anno, ora, minuti, suoneria, luci,serranda):
        self.id = id
        self.nome = nome
        self.giorno = giorno
        self.mese = mese
        self.anno = anno
        self.ora = ora
        self.minuti = minuti
        self.suoneria = suoneria
        self.luci = luci
        self.serranda = serranda
    def __str__(self):
        return str(self.id)+":"+str(self.nome)+","+str(self.giorno)+","+str(self.mese)+","+str(self.anno)+","+str(self.ora)+","+str(self.minuti)+","+str(self.suoneria)+","+str(self.luci)+","+str(self.serranda)
    def getName(self):
        return str(self.nome)
    def getLuci(self):
        return self.luci
    def getSuoneria(self):
        return self.suoneria
    def getSerranda(self):
        return self.serranda
    
class SVEGLIE:
    def __init__(self):
        self.dict={}
        #lista che contiene tutti gli id delle sveglie presenti - facilita lo scorrimento
        self.ids=[]
       
    def aggiungisveglia(self,id,nome,giorno,mese,anno,ora,minuti,suoneria,luci,serranda):
        self.dict[id] =SVEGLIA(id,nome,giorno,mese,anno,ora,minuti,suoneria,luci,serranda)
        self.ids.append(id)

    def rimuovisveglia(self,id):
        del self.dict[id]
        self.ids.remove(id)


    def __str__(self):
        if self.dict == {}:
            print('{}')
        else:
            str=""
            for id in self.ids:
                str+=self.dict[id].__str__()
                str+='\n'
            return str
    
    def confrontoDataOra(self,giorno1,mese1,anno1,ora1,minuto1):
        for id in self.ids:
            if self.dict[id].anno == anno1 and self.dict[id].mese == mese1 and self.dict[id].giorno == giorno1:
                if self.dict[id].ora == ora1 and self.dict[id].minuti == minuto1:
                    print(id)
                    return id
            else:
                return -1

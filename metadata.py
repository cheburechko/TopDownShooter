class PlayerEntry():

    def __init__(self, id, name, score=0, deaths=0, latency=0):
        self.id = id;
        self.name = name;
        self.score = score
        self.deaths = deaths
        self.latency = latency

    def toString(self):
        return self.name + ' ' + str(self.score) + ' ' + str(self.deaths)


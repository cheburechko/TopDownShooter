class StateHistory():

    def __init__(self, size):
        self.states = []
        self.timestamps = []
        self.size = size

    def getTimestamps(self, timestamp):
        for i in range(len(self.timestamps)):
            if timestamp <= self.timestamps[i]:
                return self.timestamps[i:]
        return self.timestamps[-1:]

    def storeState(self, world, timestamp):
        state = {}
        for key in world:
            obj = world[key]
            state[obj.id] = (obj.size, obj.x, obj.y, obj)
        self.states += [(timestamp, state)]
        self.timestamps += [timestamp]
        if len(self.states) > self.size:
            self.states = self.states[1:]
            self.timestamps = self.timestamps[1:]

    def updateState(self, obj, timestamp):
        for state in self.states:
            if timestamp <= state[0]:
                state[1][obj.id] = (obj.size, obj.x, obj.y, obj)
                break

    def deleteState(self, obj, timestamp):
        for state in self.states:
            if timestamp <= state[0]:
                del state[1][obj.id]

    def collisions(self, obj, timestamp, solidOnly=False):
        result = []

        curState = self.states[-1][1]
        for state in self.states:
            if timestamp <= state[0]:
                curState = state[1]

        for key in curState:
            if key == obj.id:
                continue
            if (obj.x - curState[key][1])**2 + (obj.y - curState[key][2])**2 <=\
                    (obj.size + curState[key][0])**2:
                if solidOnly and curState[key][3].solid or not solidOnly:
                    result += [curState[key][3]]
                    if solidOnly:
                        return result

        return result

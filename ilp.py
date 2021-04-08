#!usr/bin/env python3

import mip
import pickle
import tempfile

MAX_TIME = 300

class IlpSolution:
    def __init__(self, solved_ilp):
        self.ilp_id = solved_ilp.uid
        self.results = [(v.name, v.x) for v in solved_ilp.mip_ilp.vars]

    @classmethod
    def deserialize(cls, raw_bytes : bytes):
        return pickle.loads(raw_bytes)

    def serialize(self) -> bytes:
        return picke.dumps(self)

    def print_soln(self):
        # ToDo
        pass

class Ilp:

    # Contains the subset of the state from the more complex Ilp class that we want to serialize and send around
    class SerializableIlp:
        # create these from full-blown Ilp objects
        def __init__(self, full_ilp):
            # we need temp files to use mip's built in serialization; this is an ugly hack
            with  tempfile.NamedTemporaryFile(suffix=".lp") as tempOutputFile:
                full_ilp.mip_ilp.write(tempOutputFile.name)
                self.serialized_ilp = tempOutputFile.read()
                self.uid = full_ilp.uid

        # convert back to a full ilp.
        # any solution progress will be lost.
        def to_full_ilp(self):
            with  tempfile.NamedTemporaryFile(suffix=".lp") as tempOutputFile:
                tempOutputFile.write(self.serialized_ilp)
                deserialized_ilp = mip.Model()
                deserialized_ilp.read(tempOutputFile.name)
                return Ilp(self.uid, deserialized_ilp)

    # create an Ilp from a mip model
    def __init__(self, uid : int, mip_ilp : mip.Model):
        self.mip_ilp = mip_ilp
        self.uid = uid

    def setId(self, uid: int):
        self.uid = uid

    def getId(self) -> int:
        return self.uid

    # try to solve for up to MAX_TIME and return a solution class
    def solve(self) -> IlpSolution:
        status = self.mip_ilp.optimize(max_seconds = MAX_TIME)
        if (status == OptimizationStatus.INFEASIBLE or status == OptimizationStatus.OPTIMAL):
            return IlpSolution(self)
        else:
            return None

    # dump bytes
    def serialize(self) -> bytes:
        return pickle.dumps(SerializableIlp(self))

    # from bytes
    @classmethod
    def deserialize(cls, raw_bytes : bytes):
        return pickle.loads(raw_bytes).to_full_ilp()

    def check(self, solution : IlpSolution):
        # how the heck do we do this?
        pass



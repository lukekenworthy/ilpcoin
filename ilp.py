#!usr/bin/env python3

import mip
import pickle
import tempfile

MAX_TIME = 300

class IlpSolution:
    def __init__(self, ilp_uid, solved_ilp):
        self.ilp_id = ilp_uid
        self.results = [(v.name, v.x) for v in solved_ilp.vars]

    @staticmethod
    def deserialize(self, raw_bytes) -> IlpSolution:
        return pickle.loads(raw_bytes)

    def serialize(self) -> bytes:
        return picke.dumps(self)

    def print_soln(self):
        # ToDo
        pass

class Ilp:

    class SerializableIlp:
        def __init__(self, full_ilp):
            with  tempfile.NamedTemporaryFile(suffix=".lp") as tempOutputFile:
                full_ilp.mip_ilp.write(tempOutputFile.name)
                self.serialized_ilp = tempOutputFile.read()
                self.uid = full_ilp.uid

        def to_full_ilp(self) -> Ilp:
            with  tempfile.NamedTemporaryFile(suffix=".lp") as tempOutputFile:
                tempOutputFile.write(self.serialized_ilp)
                deserialized_ilp = mip.Model()
                deserialized_ilp.read(tempOutputFile.name)
                return Ilp(self.uid, deserialized_ilp)

    def __init__(self, uid, mip_ilp):
        self.mip_ilp = mip_ilp
        self.uid = uid

    def getId(self) -> int:
        return self.uid

    def solve(self) -> IlpSolution:
        status = self.mip_ilp.optimize(max_seconds = MAX_TIME)
        if status == OptimizationStatus.INFEASIBLE || status == OptimizationStatus.OPTIMAL:
            return IlpSolution(self.uid, self)
        else:
            return None

    def serialize(self) -> bytes:
        return pickle.dumps(SerializableIlp(self))

    @classmethod
    def deserialize(cls, raw_bytes):
        return pickle.loads(raw_bytes).to_full_ilp()

    def check(self, solution : IlpSolution):
        # how the heck do we do this?
        pass



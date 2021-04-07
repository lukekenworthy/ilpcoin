#!usr/bin/env python3

import mip
import pickle
import tempfile

class IlpSolution:
    def __init__(self, ilp_id, solved_ilp):
        # ensure it is solved
        # extract the vars unto a list
        self.mip_soln = mip_soln

    @staticmethod
    def deserialize(self, raw_bytes) -> IlpSolution:
        return pickle.loads(raw_bytes)

    def serialize(self) -> bytes:
        return picke.dumps(self)

    def print_soln(self):
        pass

class Ilp:

    class SerializableIlp:
        def __init__(self, full_ilp):
            # set up the dumping and stuff in a nicely pickelable way dealing with files
            pass

        def to_full_ilp(self) -> Ilp:
            # restore here
            pass

    def __init__(self, uid, mip_ilp):
        self.mip_ilp = mip_ilp
        self.uid = uid

    def getId(self) -> int:
        return self.uid

    def solve(self) -> IlpSolution:
        pass

    def serialize(self) -> bytes:
        return pickle.dumps(SerializableIlp(self))

    @classmethod
    def deserialize(cls, raw_bytes):
        return pickle.loads(raw_bytes).to_full_ilp()

    def check(self, solution : IlpSolution):
        # how the heck do we do this?
        pass



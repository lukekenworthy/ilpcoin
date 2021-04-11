#!usr/bin/env python3

import mip
import pickle
import tempfile

MAX_TIME = 300

class IlpSolution:
    def __init__(self, solved_ilp : 'Ilp'):
        self.ilp_id = solved_ilp.uid
        self.variable_results = [(v.name, v.x) for v in solved_ilp.mip_ilp.vars]

    @classmethod
    def deserialize(cls, raw_bytes : bytes):
        return pickle.loads(raw_bytes)

    def serialize(self) -> bytes:
        return pickle.dumps(self)

    def print_soln(self):
        # ToDo
        pass

class Ilp:

    # Contains the subset of the state from the more complex Ilp class that we want to serialize and send around
    class SerializableIlp:
        # create these from full-blown Ilp objects
        def __init__(self, full_ilp : 'Ilp', k : int):
            # we need temp files to use mip's built in serialization; this is an ugly hack
            with  tempfile.NamedTemporaryFile(suffix=".lp") as tempOutputFile:
                full_ilp.mip_ilp.write(tempOutputFile.name)
                self.serialized_ilp = tempOutputFile.read()
                self.uid = full_ilp.uid
                self.k = k

        # convert back to a full ilp.
        # any solution progress will be lost.
        def to_full_ilp(self) -> 'Ilp':
            with  tempfile.NamedTemporaryFile(suffix=".lp") as tempOutputFile:
                tempOutputFile.write(self.serialized_ilp)
                deserialized_ilp = mip.Model()
                deserialized_ilp.read(tempOutputFile.name)
                return Ilp(self.uid, deserialized_ilp, self.k)

    # create an Ilp from a mip model
    def __init__(self, uid : int, mip_ilp : mip.Model, k : float):
        self.mip_ilp = mip_ilp
        self.uid = uid
        self.k = k

    def setId(self, uid: int) -> None:
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
    def deserialize(cls, raw_bytes : bytes) -> 'Ilp':
        return pickle.loads(raw_bytes).to_full_ilp()

    def __eval_objective_function(solution):
        objective_function = self.mip_ilp.objective
        res = objective_function.const
        for v, coeff in self.mip_ilp.expr.items():
            v_value = solution.variable_results[v.name]
            res += v_value * coeff

        return res

    def check(self, solution : IlpSolution) -> bool:
        solution_value = __eval_objective_function(solution)
        return solution_value < k





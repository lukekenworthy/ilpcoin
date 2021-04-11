#!usr/bin/env python3

import mip
import pickle
import tempfile

MAX_TIME = 300

class IlpSolution:
    def __init__(self, solved_ilp : 'Ilp'):
        self.ilp_id = solved_ilp.uid
        self.variable_results = {v.name : v.x for v in solved_ilp.mip_ilp.vars}

    @classmethod
    def deserialize(cls, raw_bytes : bytes):
        return pickle.loads(raw_bytes)

    def serialize(self) -> bytes:
        return picke.dumps(self)

    def print_soln(self):
        # ToDo
        pass

# Contains the subset of the state from the more complex Ilp class that we want to serialize and send around
class SerializableIlp:
    # create these from full-blown Ilp objects
    def __init__(self, full_ilp : 'Ilp'):
        # we need temp files to use mip's built in serialization; this is an ugly hack
        with  open("temp_serialize_file.lp", "w+") as tempOutputFile:
        # with tempfile.NamedTemporaryFile(suffix=".lp") as tempOutputFile:
            full_ilp.mip_ilp.write(tempOutputFile.name)
            self.serialized_ilp = tempOutputFile.read()
            self.uid = full_ilp.uid
            self.k = full_ilp.k
            # print("Serialized: \n" + str(self.serialized_ilp)+ "\n")

    # convert back to a full ilp.
    # any solution progress will be lost.
    def to_full_ilp(self) -> 'Ilp':
        with open("temp_deserialize_file.lp", "w+") as tempOutputFile:
        # with tempfile.NamedTemporaryFile(suffix=".lp") as tempOutputFile:
            # print("Deserialized: \n" + str(self.serialized_ilp) + "\n")
            tempOutputFile.write(self.serialized_ilp)
            deserialized_ilp = mip.Model()
        deserialized_ilp.read("temp_deserialize_file.lp")
        return Ilp(deserialized_ilp, self.k, self.uid)
        
class Ilp:
    # create an Ilp from a mip model
    def __init__(self, mip_ilp : mip.Model, k : float, uid : int = -1):
        self.mip_ilp = mip_ilp
        self.uid = uid
        self.k = k

    def setId(self, uid: int) -> None:
        self.uid = uid

    def getId(self) -> int:
        return self.uid
    
    def __eq__(self, other):
        # k is the same
        result = self.k == other.k

        # same uid
        result = result and self.uid == other.uid
        print("result", result)

        # same objectives
        # result = result and self.mip_ilp.objective.equals(other.mip_ilp.objective)

        # same vars
        result = result and (self.mip_ilp.vars == other.mip_ilp.vars)
        print("result", self.mip_ilp.vars[1])


        # same constraints
        num_constrs = len(self.mip_ilp.constrs)
        result = result and (num_constrs == len(other.mip_ilp.constrs))
        print("numconst", len(other.mip_ilp.constrs))


        if not result: 
            return False

        for i in range(num_constrs): 
            result = result and (self.mip_ilp.constrs[i].expr() == other.mip_ilp.constrs[i].expr())
        return result

 
    # try to solve for up to MAX_TIME and return a solution class
    def solve(self) -> IlpSolution:
        status = self.mip_ilp.optimize(max_seconds = MAX_TIME)
        if (status == mip.OptimizationStatus.INFEASIBLE or status == mip.OptimizationStatus.OPTIMAL):
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

    def __eval_objective_function(self, solution):
        objective_function = self.mip_ilp.objective
        res = objective_function.const
        for v, coeff in self.mip_ilp.objective.expr.items():
            v_value = solution.variable_results[v.name]
            res += v_value * coeff

        return res

    def check(self, solution : IlpSolution) -> bool:
        solution_value = self.__eval_objective_function(solution)
        return solution_value < self.k






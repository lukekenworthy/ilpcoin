#!usr/bin/env python3

from typing import Optional
import mip
import pickle
import tempfile

from ilpcoin.common.constants import ILP_NOT_FOUND

# Class representing the solution to an Ilp. 
class IlpSolution:
    # Create a solution from an Ilp class that has bee
    def __init__(self, solved_ilp : 'Ilp', status=mip.OptimizationStatus.OPTIMAL):
        self.ilp_id = solved_ilp.uid

        # No solution is set when the ilp has been proven to have no solution.
        self.no_solution = status == mip.OptimizationStatus.INFEASIBLE
        # Associates a solution with its ilp by ID
        
        # The results for each variable, as a dict
        # Keys are python-mip generated variables names, and values are the value of 
        # that variable in the solution.
        self.variable_results = {v.name : v.x for v in solved_ilp.mip_ilp.vars}

    # Pickling; safe to send around
    @classmethod
    def deserialize(cls, raw_bytes : bytes):
        return pickle.loads(raw_bytes)

    def serialize(self) -> bytes:
        return pickle.dumps(self)

    def serialize_s(self) -> str:
        return self.serialize().hex()

    @classmethod
    def deserialize_s(cls, hex_string : str):
        return cls.deserialize(bytes.fromhex(hex_string))

    def __eq__(self, other):
        try: 
            return self.ilp_id == other.ilp_id and self.no_solution == other.no_solution and self.variable_results == other.variable_results
        except: 
            return False

    def print_soln(self):
        # ToDo
        pass

# Contains the subset of the state from the more complex Ilp class that we want to serialize and send around
# Internal to this module. Never manually instantiate or use. 
class _SerializableIlp:
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
    # this is a terrible hack
    def to_full_ilp(self) -> 'Ilp':
        with open("temp_deserialize_file.lp", "w+") as tempOutputFile:
        # with tempfile.NamedTemporaryFile(suffix=".lp") as tempOutputFile:
            # print("Deserialized: \n" + str(self.serialized_ilp) + "\n")
            tempOutputFile.write(self.serialized_ilp)
            deserialized_ilp = mip.Model()
        deserialized_ilp.read("temp_deserialize_file.lp")
        return Ilp(deserialized_ilp, self.k, self.uid)
        
# Universal representation of a decision-problem ILP for all of ilpcoin.
class Ilp:

    # Create a decision Ilp from a mip model, some k, a uid (set by the queue after instantiation, typically).
    # Set maximize to true for the ilp to be solved if objective function evaluates > k, rather than less.
    def __init__(self, mip_ilp : mip.Model, k : float, uid : int = -1, maximize = False):
        self.mip_ilp = mip_ilp
        self.uid = uid
        self.k = k
        self.maximize = False

    # Set this Ilp's system wide UID. Normally the queue does this when it is added by a client. 
    def set_id(self, uid: int) -> None:
        self.uid = uid

    def get_id(self) -> int:
        return self.uid
    
    # # DANGER: THIS DOES NOT WORK
    # def __eq__(self, other):
    #     # k is the same
    #     result = self.k == other.k

    #     # same uid
    #     result = result and self.uid == other.uid
    #     # print("result", result)

    #     # same objectives
    #     # result = result and self.mip_ilp.objective.equals(other.mip_ilp.objective)

    #     # same vars
    #     result = result and (self.mip_ilp.vars == other.mip_ilp.vars)
    #     # print("result", self.mip_ilp.vars[1])

    #     # same constraints
    #     num_constrs = len(self.mip_ilp.constrs)
    #     result = result and (num_constrs == len(other.mip_ilp.constrs))
    #     # print("numconst", len(other.mip_ilp.constrs))

    #     if not result: 
    #         return False

    #     for i in range(num_constrs): 
    #         result = result and (self.mip_ilp.constrs[i].expr() == other.mip_ilp.constrs[i].expr())
    #     return result

 
    # Try to solve for up to max_time and return a solution object, described above.
    def solve(self, max_time = 300) -> Optional[IlpSolution]:
        status = self.mip_ilp.optimize(max_seconds = max_time)
        # Solution can be infeasible (no solution) or the actual solution. 
        if (status == mip.OptimizationStatus.INFEASIBLE or status == mip.OptimizationStatus.OPTIMAL):
            return IlpSolution(self, mip.OptimizationStatus.INFEASIBLE )
        else:
            # No solution found in time. 
            return None

    # Serialize ilp to bytes. 
    # Preserves only information about the ilp problem, not any of the solving machinery 
    # or internal solutions. 
    def serialize(self) -> bytes:
        return pickle.dumps(_SerializableIlp(self))

    # Serialize ilp to string. 
    # Preserves only information about the ilp problem, not any of the solving machinery 
    # or internal solutions. 
    def serialize_s(self) -> str:
        return self.serialize().hex()

    # Deserialize an ilp from bytes. See `serialize` note about what is preserved. 
    @classmethod
    def deserialize(cls, raw_bytes : bytes) -> 'Ilp':
        return pickle.loads(raw_bytes).to_full_ilp()

    # Deserialize an ilp from hex string. See `serialize` note about what is preserved. 
    @classmethod
    def deserialize_s(cls, hex_string : str) -> 'Ilp':
        return cls.deserialize(bytes.fromhex(hex_string))

    def __eval_objective_function(self, solution):
        objective_function = self.mip_ilp.objective
        res = objective_function.const
        for v, coeff in self.mip_ilp.objective.expr.items():
            v_value = solution.variable_results[v.name]
            res += v_value * coeff

        return res

    # Check if an IlpSolution object ssatisfies this ilp. 
    def check(self, solution : IlpSolution) -> bool:
        try: 
            # The solution isn't for this ilp. 
            if solution.ilp_id != self.uid: 
                return False

            solution_value = self.__eval_objective_function(solution)
            return float(solution_value) > self.k if self.maximize else solution_value < self.k 
        except: 
            # If we can't check it, it's not a solution. 
            return False
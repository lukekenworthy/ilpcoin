#!usr/bin/env python3

from typing import Optional
import mip
import pickle
import tempfile

from ilpcoin.common.constants import ILP_NOT_FOUND

class IlpSolution:
    """
    A class to represent a solution to an ILP.

    Attributes
    ----------
    ilp_id : int
        The id of the ilp for which this object is a solution
    no_solution : bool
        Set to `True` if this solution represents the fact
        that the associated Ilp has been proven to have no solution
    variable_results : Dict[string: float]
        A dictionary associating each variable to its value in the solution
        by its python-mip generated name.
    """

    def __init__(self, solved_ilp : 'Ilp', status=mip.OptimizationStatus.OPTIMAL):
        '''Constructs an IlpSolution from a solved Ilp.

        Parameters
        ----------    
        solved_ilp : Ilp
            The Ilp instance, already solved with the .solve() method.
        
        status : mip.OptimizationStatus 
            The exit status from solved_ilp's internal mip solve.
        '''

        self.ilp_id = solved_ilp.uid

        # No solution is set when the ilp has been proven to have no solution.
        self.no_solution = status == mip.OptimizationStatus.INFEASIBLE
        
        self.variable_results = {v.name : v.x for v in solved_ilp.mip_ilp.vars}

    @classmethod
    def deserialize(cls, raw_bytes : bytes):
        '''Create an ilp_solution from raw_bytes'''
        return pickle.loads(raw_bytes)

    def serialize(self) -> bytes:
        '''Convert this ilp_solution to bytes'''
        return pickle.dumps(self)

    def serialize_s(self) -> str:
        '''Convert this IlpSolution to a hex string, when more convenient than raw bytes.'''
        return self.serialize().hex()

    @classmethod
    def deserialize_s(cls, hex_string : str):
        '''Convert the hex string representation of this solution to an IlpSolution'''
        return cls.deserialize(bytes.fromhex(hex_string))

    def __eq__(self, other):
        try: 
            return self.ilp_id == other.ilp_id and self.no_solution == other.no_solution and self.variable_results == other.variable_results
        except: 
            return False


class _SerializableIlp:
    # Contains the subset of the state from the more complex Ilp class that we want to serialize and send around
    # Internal to this module. Never manually instantiate or use. 
    
    # Create these from full-blown Ilp objects
    def __init__(self, full_ilp : 'Ilp'):
        # We need temp files to use mip's built in serialization; this is an ugly hack
        with  open("temp_serialize_file.lp", "w+") as tempOutputFile:
            full_ilp.mip_ilp.write(tempOutputFile.name)
            self.serialized_ilp = tempOutputFile.read()
            self.uid = full_ilp.uid
            self.k = full_ilp.k
            self.maximuze = full_ilp.maximize

    # Convert back to a full ilp.
    # Any solution progress will be lost.
    def to_full_ilp(self) -> 'Ilp':
        with open("temp_deserialize_file.lp", "w+") as tempOutputFile:
            tempOutputFile.write(self.serialized_ilp)
            deserialized_ilp = mip.Model()
        deserialized_ilp.read("temp_deserialize_file.lp")
        return Ilp(deserialized_ilp, self.k, self.uid)
        

class Ilp:
    '''
    Universal representation of a decision-problem ILP for all of ilpcoin.

    Attributes
    ----------
    mip_ilp : mip.Model
        The internal mip model that this ilp object represents. 
        Much of this class's functionality just passes through to this internal object.
    uid : int
        A globally unique ID for this ilp, set by the queue. Initialized to -1 on construction. 
    k : float
        The threshold above (if a maximization problem) or below (if minimization) that the objective function
        must evalute to for a set of values for each variable to be considered a solution to this Ilp.
    maximize : bool
        Is this a maximization problem? Minimization if false. 
    '''

    def __init__(self, mip_ilp : mip.Model, k : float, uid : int = -1, maximize = False):
        '''Create a decision Ilp from a mip model.'''
        self.mip_ilp = mip_ilp
        self.uid = uid
        self.k = k
        self.maximize = maximize

    def set_id(self, uid: int) -> None:
        '''Set this Ilp's system wide UID. Normally the queue does this when it is added by a client. '''
        self.uid = uid

    def get_id(self) -> int:
        '''Return the Ilp's global UID'''
        return self.uid
 
    def solve(self, max_time = 300) -> Optional[IlpSolution]:
        '''Try to solve for up to max_time seconds and return an IlpSolution object. See IlpSolution documentation for details
        
        Makes use of the mip library's internal solving tools.
        '''
        status = self.mip_ilp.optimize(max_seconds = max_time)

        # Solution can be infeasible (no solution) or the actual solution. 
        if (status == mip.OptimizationStatus.INFEASIBLE or status == mip.OptimizationStatus.OPTIMAL):
            return IlpSolution(self, mip.OptimizationStatus.INFEASIBLE )
        else:
            # No solution found in time. 
            return None


    def serialize(self) -> bytes:
        '''Serialize ilp to bytes. 

        Preserves information about the ilp problem, but not any of the solving machinery 
        or any solutions stored internally.    
        '''
        return pickle.dumps(_SerializableIlp(self))

    def serialize_s(self) -> str:
        '''Serialize ilp to hex string, when more convenient than raw bytes. 

        Preserves information about the ilp problem, but not any of the solving machinery 
        or any solutions stored internally.    
        '''
        return self.serialize().hex()

    @classmethod
    def deserialize(cls, raw_bytes : bytes) -> 'Ilp':
        '''Deserialize an ilp from raw_bytes
        
        Inverse of `serialize` above.
        '''
        return pickle.loads(raw_bytes).to_full_ilp()

    @classmethod
    def deserialize_s(cls, hex_string : str) -> 'Ilp':
        '''Deserialize an ilp from hex_string
        
        Inverse of `serialize)s` above.
        '''
        return cls.deserialize(bytes.fromhex(hex_string))

    # Internal use only, as part of check
    def __eval_objective_function(self, solution):
        objective_function = self.mip_ilp.objective
        res = objective_function.const
        for v, coeff in self.mip_ilp.objective.expr.items():
            v_value = solution.variable_results[v.name]
            res += v_value * coeff

        return res

    def check(self, solution : IlpSolution) -> bool:
        '''Return true iff solution's variables solve this decision Ilp'''
        try:             
            # The solution isn't for this ilp. 
            # if solution.ilp_id != self.uid: 
            #     return False

            solution_value = self.__eval_objective_function(solution)
            return float(solution_value) > self.k if self.maximize else solution_value < self.k 
        except: 
            # If we can't check it, it's not a solution. 
            return False
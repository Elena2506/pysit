import scipy.sparse.linalg as spspla

from pysit.util import ConstructableDict

from ..constant_density_acoustic_base import *

from pysit.util.solvers import inherit_dict

__all__ = ['ConstantDensityAcousticFrequencyBase']

__docformat__ = "restructuredtext en"

solver_style_map = {'sparseLU': '_build_sparseLU_solver',
                    'amg': '_build_amg_solver',
                    'iterative': '_build_iterative_solver'}


@inherit_dict('supports', '_local_support_spec')
class ConstantDensityAcousticFrequencyBase(ConstantDensityAcousticBase):

    _local_support_spec = {'equation_dynamics': 'frequency',
                           # These should be defined by subclasses.
                           'spatial_discretization': None,
                           'spatial_accuracy_order': None,
                           'spatial_dimension': None,
                           'boundary_conditions': None}

    def __init__(self, mesh, solver_style='sparseLU', spatial_shifted_differences=True, **kwargs):

        # A dictionary that holds the helmholtz operators as a function of nu
        self.linear_operators = ConstructableDict(self._build_helmholtz_operator)

        # A dictionary that holds the helmholtz solver as a function of nu
        solver_builder = self.__getattribute__(solver_style_map[solver_style])
        self.solvers = ConstructableDict(solver_builder)

        ConstantDensityAcousticBase.__init__(self,
                                             mesh,
                                             spatial_shifted_differences=spatial_shifted_differences,
                                             **kwargs)

    def _process_mp_reset(self, *args, **kwargs):

        self.linear_operators.clear()
        self.solvers.clear()
        self._rebuild_operators()

    def _rebuild_operators(self):
        raise NotImplementedError("'_rebuild_operators' must be implemented in a subclass")

    def _build_sparseLU_solver(self, nu):
        return spspla.factorized(self.linear_operators[nu])

    def _build_amg_solver(self, nu):
        raise NotImplementedError('AMG solver for helmholtz is not implemented.')

    def _build_iterative_solver(self, nu):
        raise NotImplementedError('Iterative solver for helmholtz is not implemented.')

    def solve(self, *args, **kwargs):
        """Framework for a single execution of the solver at a given frequency. """
        raise NotImplementedError("Function 'solve' Must be implemented by subclass.")

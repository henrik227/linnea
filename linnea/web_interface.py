from .frontend.utils import parse_input
from .frontend.export import export_expression
from .derivation.graph.derivation import DerivationGraph
from . import utils

import linnea.config
import linnea.algebra.validity as validity
import linnea.algebra.expression as ae

import json

class SizeMismatch(Exception):
    pass

class InvalidExpression(Exception):
    pass

def run_linnea(input, time_limit=10):
    """Run Linnea code generation.

    This function runs the code generation of Linnea on the input and returns
    the code that implements the optimal algorithm as a string.

    For the input, the custom input language of Linnea has to be used.
    
    Args:
        input (str): Description of the input.
        time_limit (int, optional): Time limit for the generation in seconds.

    Returns:
        str: The generated code.
    """
    
    linnea.config.set_verbosity(0)

    equations = parse_input(input)

    graph = DerivationGraph(equations)
    graph.derivation(time_limit=time_limit, merging=True, pruning_factor=1.)

    return graph.optimal_algorithm_to_str()


def dependent_dimensions(input):
    """Computes dependent dimensions.

    The dependent dimensions are all sets of dimensions that have to be the same
    for the input equations to be valid. The output is a JSON string, and
    dependent dimensions are represented as nested arrays. The innermost arrays
    represent the dimensions; they contain two elements: The first element is
    the name of the operand as a string, the second element is an integer; 0
    stands for rows, 1 for columns. All dimensions that have to be the same are
    in the same array.

    For the input, the custom input language of Linnea has to be used.
    
    Args:
        input (str): Description of the input.

    Returns:
        string: A JSON string of nested arrays.
    """
    equations = parse_input(input)
    try:
        equations.check_validity()
    except validity.SizeMismatch as e:
        if not e.error_info is None:
            expr_type, expr1, expr2 = e.error_info
            msg = "Size mismatch in {}: {} and {} are not compatible.".format(expr_type, export_expression(expr1, dict()), export_expression(expr2, dict()))
            raise SizeMismatch(msg)
        else:
            raise e
    except validity.InvalidExpression as e:
        if not e.error_info is None:
            msg = "Only square expressions can be inverted: {}.".format(export_expression(e.error_info, dict()))
            raise InvalidExpression(msg)
        else:
            raise e
    dimensions = utils.dependent_dimensions(equations)
    return json.dumps(list(map(list, dimensions)))
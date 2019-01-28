import logging
from enum import Enum

import ServerSideExtension_pb2 as SSE
import grpc


class ArgType(Enum):
    """
    Represents data types that can be used
    as arguments in different script functions.
    """
    Undefined = -1
    Empty = 0
    String = 1
    Numeric = 2
    Mixed = 3


class ReturnType(Enum):
    """
    Represents return types that can
    be used in script evaluation.
    """
    Undefined = -1
    String = 0
    Numeric = 1
    Dual = 2


class FunctionType(Enum):
    """
    Represents function types.
    """
    Scalar = 0
    Aggregation = 1
    Tensor = 2


def get_func_type(header):
    """
    Retrieves the function type.
    :param header:
    :return:
    """
    func_type = header.functionType
    if func_type == SSE.SCALAR:
        return FunctionType.Scalar
    elif func_type == SSE.AGGREGATION:
        return FunctionType.Aggregation
    elif func_type == SSE.TENSOR:
        return FunctionType.Tensor


def get_arguments(arg_types, duals):
    """
    Gets the array of arguments based on
    the duals, and the type (string, numeric)
    specified in the header.
    :param arg_types: argument types
    :param duals: an iterable sequence of duals.
    :return: list of string arguments
    """
    if arg_types == ArgType.String:
        # All parameters are of string type
        script_args = [d.strData for d in duals]
    else:
        # This plugin does not support other arg types than string
        raise grpc.RpcError(grpc.StatusCode.UNIMPLEMENTED,
                            'Argument type {} is not supported in this plugin.'.format(arg_types))

    return script_args


def get_arg_types(header):
    """
    Determines the argument types for all parameters.
    :param header:
    :return: ArgType
    """
    data_types = [param.dataType for param in header.params]

    if not data_types:
        return ArgType.Empty
    elif len(set(data_types)) > 1 or all(data_type == SSE.DUAL for data_type in data_types):
        return ArgType.Mixed
    elif all(data_type == SSE.STRING for data_type in data_types):
        return ArgType.String
    elif all(data_type == SSE.NUMERIC for data_type in data_types):
        return ArgType.Numeric
    else:
        return ArgType.Undefined


def get_return_type(header):
    """
    :param header:
    :return: Return type
    """
    if header.returnType == SSE.STRING:
        return ReturnType.String
    elif header.returnType == SSE.NUMERIC:
        return ReturnType.Numeric
    elif header.returnType == SSE.DUAL:
        return ReturnType.Dual
    else:
        return ReturnType.Undefined


def evaluate(script, ret_type, params=[]):
    """
    Evaluates a script with given parameters.
    :param script:  script to evaluate
    :param ret_type: return data type
    :param params: params to evaluate. Default: []
    :return: a RowData of string dual
    """
    if ret_type == ReturnType.String:
        # Evaluate script
        result = eval(script, {'args': params})
        # Transform the result to an iterable of Dual data with a string value
        duals = iter([SSE.Dual(strData=result)])

        # Create row data out of duals
        return SSE.BundledRows(rows=[SSE.Row(duals=duals)])
    else:
        # This plugin does not support other return types than string
        raise grpc.RpcError(grpc.StatusCode.UNIMPLEMENTED,
                            'Return type {} is not supported in this plugin.'.format(ret_type))

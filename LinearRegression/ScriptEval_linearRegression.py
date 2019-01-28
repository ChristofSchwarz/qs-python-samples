import logging
import logging.config

import grpc

from SSEData_linearRegression import ArgType, \
                               evaluate, \
                               get_arg_types, \
                               get_return_type, \
                               FunctionType, \
                               get_arguments


class ScriptEval:
    """
    Class for SSE plugin ScriptEval functionality.
    """

    def EvaluateScript(self, header, request, func_type):
        """
        Evaluates script provided in the header, given the
        arguments provided in the sequence of RowData objects, the request.

        :param header:
        :param request: an iterable sequence of RowData.
        :param func_type: function type.
        :return: an iterable sequence of RowData.
        """
        # Retrieve data types from header
        arg_types = get_arg_types(header)
        ret_type = get_return_type(header)

        logging.info('EvaluateScript: {} ({} {}) {}'
                     .format(header.script, arg_types, ret_type, func_type))

        aggr = (func_type == FunctionType.Aggregation)

        # Check if parameters are provided
        if header.params:
            # Verify argument type
            if arg_types == ArgType.String:
                # Create an empty list if tensor function
                if aggr:
                    all_rows = []

                # Iterate over bundled rows
                for request_rows in request:
                    # Iterate over rows
                    for row in request_rows.rows:
                        # Retrieve numerical data from duals
                        params = get_arguments(arg_types, row.duals)

                        if aggr:
                            # Append value to list, for later aggregation
                            all_rows.append(params)
                        else:
                            # Evaluate script row wise
                            yield evaluate(header.script, ret_type, params=params)

                # Evaluate script based on data from all rows
                if aggr:
                    params = [list(param) for param in zip(*all_rows)]
                    yield evaluate(header.script, ret_type, params=params)
            else:
                # This plugin does not support other argument types than string.
                raise grpc.RpcError(grpc.StatusCode.UNIMPLEMENTED,
                                    'Argument type: {} not supported in this plugin.'.format(arg_types))
        else:
            # This plugin does not support script evaluation without parameters
            raise grpc.RpcError(grpc.StatusCode.UNIMPLEMENTED,
                                'Script evaluation with no parameters is not supported in this plugin.')

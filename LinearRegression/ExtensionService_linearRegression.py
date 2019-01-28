#! /usr/bin/env python3
import argparse
import json
import logging
import logging.config
import os
import sys
import time
from concurrent import futures
from datetime import datetime

import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime

import ServerSideExtension_pb2 as SSE
import grpc
from SSEData_linearRegression import FunctionType, \
                               get_func_type
from ScriptEval_linearRegression import ScriptEval

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
##logger = os.getcwd().replace('\\','/') + '/' + 'linearRegressionLogger.txt'

class ExtensionService(SSE.ConnectorServicer):
    """
    A simple SSE-plugin created for the ARIMA example.
    """

    def __init__(self, funcdef_file):
        """
        Class initializer.
        :param funcdef_file: a function definition JSON file
        """
        self._function_definitions = funcdef_file
        self.scriptEval = ScriptEval()
        if not os.path.exists('logs'):
            os.mkdir('logs')
        logging.config.fileConfig('logger.config')
        logging.info('Logging enabled')

    @property
    def function_definitions(self):
        """
        :return: json file with function definitions
        """
        return self._function_definitions

    @property
    def functions(self):
        """
        :return: Mapping of function id and implementation
        """
        return {
            0: '_linearRegression'
        }

    @staticmethod
    def _get_function_id(context):
        """
        Retrieve function id from header.
        :param context: context
        :return: function id
        """
        metadata = dict(context.invocation_metadata())
        header = SSE.FunctionRequestHeader()
        header.ParseFromString(metadata['qlik-functionrequestheader-bin'])

        return header.functionId

    """
    Implementation of added functions.
    """

    @staticmethod
    def _linearRegression(request, context):
        # clear the log for ARIMA details
##        f = open(logger,'w')
##        f.write('New function call\n')

        # instantiate a list for measure data
        dataList = []
        
        for request_rows in request:
            # iterate over each request row (contains rows, duals, numData)
##            f.write('Request Rows: ' + str(request_rows) + '\n')

            # pull duals from each row, and the numData from duals
            for row in request_rows.rows:
                # the first numData contains the measure data
                data = [d.numData for d in row.duals][0]

                # try to convert number to float
                try:
                    float(data)
                except ValueError:
                    data = 0
                
                # append each data point to a list and log it
                dataList.append(data)  
##                f.write('Row: ' + str(data) + '\n')

        # grab the length of the data list and convert
        X_len = len(dataList)
        X = np.asarray(range(X_len))

        # convert the data into an array
        Y = np.asarray(dataList)

        # fit linear regression model
        mdl = LinearRegression().fit(X.reshape(-1, 1),Y)

        # grab m and b from y = mx + b
        m = mdl.coef_[0]
        b = mdl.intercept_
        
        # calculate regression line points
        regressionResults = []
        gen = (i for i in range(X_len))

        for i in gen:
            y = m * i + b
            regressionResults.append(y)


        # Create an iterable of dual with the result
        duals = iter([[SSE.Dual(numData=d)] for d in regressionResults])

        # Yield the row data as bundled rows
        yield SSE.BundledRows(rows=[SSE.Row(duals=d) for d in duals])


    """
    Implementation of rpc functions.
    """

    def GetCapabilities(self, request, context):
        """
        Get capabilities.
        Note that either request or context is used in the implementation of this method, but still added as
        parameters. The reason is that gRPC always sends both when making a function call and therefore we must include
        them to avoid error messages regarding too many parameters provided from the client.
        :param request: the request, not used in this method.
        :param context: the context, not used in this method.
        :return: the capabilities.
        """
        logging.info('GetCapabilities')
        # Create an instance of the Capabilities grpc message
        # Enable(or disable) script evaluation
        # Set values for pluginIdentifier and pluginVersion
        capabilities = SSE.Capabilities(allowScript=True,
                                        pluginIdentifier='Hello World - Qlik',
                                        pluginVersion='v1.0.0-beta1')

        # If user defined functions supported, add the definitions to the message
        with open(self.function_definitions) as json_file:
            # Iterate over each function definition and add data to the capabilities grpc message
            for definition in json.load(json_file)['Functions']:
                function = capabilities.functions.add()
                function.name = definition['Name']
                function.functionId = definition['Id']
                function.functionType = definition['Type']
                function.returnType = definition['ReturnType']

                # Retrieve name and type of each parameter
                for param_name, param_type in sorted(definition['Params'].items()):
                    function.params.add(name=param_name, dataType=param_type)

                logging.info('Adding to capabilities: {}({})'.format(function.name,
                                                                     [p.name for p in function.params]))

        return capabilities

    def ExecuteFunction(self, request_iterator, context):
        """
        Execute function call.
        :param request_iterator: an iterable sequence of Row.
        :param context: the context.
        :return: an iterable sequence of Row.
        """
        # Retrieve function id
        func_id = self._get_function_id(context)

        # Call corresponding function
        logging.info('ExecuteFunction (functionId: {})'.format(func_id))

        return getattr(self, self.functions[func_id])(request_iterator, context)

    def EvaluateScript(self, request, context):
        """
        This plugin provides functionality only for script calls with no parameters and tensor script calls.
        :param request:
        :param context:
        :return:
        """
        # Parse header for script request
        metadata = dict(context.invocation_metadata())
        header = SSE.ScriptRequestHeader()
        header.ParseFromString(metadata['qlik-scriptrequestheader-bin'])

        # Retrieve function type
        func_type = get_func_type(header)

        # Verify function type
        if (func_type == FunctionType.Aggregation) or (func_type == FunctionType.Tensor):
            return self.scriptEval.EvaluateScript(header, request, func_type)
        else:
            # This plugin does not support other function types than aggregation  and tensor.
            raise grpc.RpcError(grpc.StatusCode.UNIMPLEMENTED,
                                'Function type {} is not supported in this plugin.'.format(func_type.name))

    """
    Implementation of the Server connecting to gRPC.
    """

    def Serve(self, port, pem_dir):
        """
        Sets up the gRPC Server with insecure connection on port
        :param port: port to listen on.
        :param pem_dir: Directory including certificates
        :return: None
        """
        # Create gRPC server
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        SSE.add_ConnectorServicer_to_server(self, server)

        if pem_dir:
            # Secure connection
            with open(os.path.join(pem_dir, 'sse_server_key.pem'), 'rb') as f:
                private_key = f.read()
            with open(os.path.join(pem_dir, 'sse_server_cert.pem'), 'rb') as f:
                cert_chain = f.read()
            with open(os.path.join(pem_dir, 'root_cert.pem'), 'rb') as f:
                root_cert = f.read()
            credentials = grpc.ssl_server_credentials([(private_key, cert_chain)], root_cert, True)
            server.add_secure_port('[::]:{}'.format(port), credentials)
            logging.info('*** Running server in secure mode on port: {} ***'.format(port))
        else:
            # Insecure connection
            server.add_insecure_port('[::]:{}'.format(port))
            logging.info('*** Running server in insecure mode on port: {} ***'.format(port))

        # Start gRPC server
        server.start()
        try:
            while True:
                time.sleep(_ONE_DAY_IN_SECONDS)
        except KeyboardInterrupt:
            server.stop(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', nargs='?', default='50059')
    parser.add_argument('--pem_dir', nargs='?')
    parser.add_argument('--definition-file', nargs='?', default='FuncDefs_linearRegression.json')
    args = parser.parse_args()

    # need to locate the file when script is called from outside it's location dir.
    def_file = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), args.definition_file)

    calc = ExtensionService(def_file)
    calc.Serve(args.port, args.pem_dir)

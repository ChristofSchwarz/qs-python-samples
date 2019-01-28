   
#! /usr/bin/env python3
import argparse
import json
import logging
import logging.config
import os
import sys
import time
import re
from concurrent import futures
from datetime import datetime
import pandas as pd
import numpy as np
import json
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules

# Add Generated folder to module path.
PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(PARENT_DIR, 'generated'))

import ServerSideExtension_pb2 as SSE
import grpc
from ssedata import FunctionType
from scripteval import ScriptEval

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class ExtensionService(SSE.ConnectorServicer):
    """
    A simple SSE-plugin created for the HelloWorld example.
    """

    def __init__(self, funcdef_file):
        """
        Class initializer.
        :param funcdef_file: a function definition JSON file
        """
        self._function_definitions = funcdef_file
        self.ScriptEval = ScriptEval()
        os.makedirs('logs', exist_ok=True)
        log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logger.config')
        logging.config.fileConfig(log_file)
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
            0: '_marketBasket' #ADD YOUR FUNCTION HERE
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
    def _marketBasket(request, context):
        """
        Mirrors the input and sends back the same data.
        :param request: iterable sequence of bundled rows
        :return: the same iterable sequence as received
        """
        orderIdList = []
        productIdList = []
        purchasedList = []
        for request_rows in request:
            #print(request_rows)
            for row in request_rows.rows:
                # the first numData contains the orderIds
                orderIdList.append([d.numData for d in 	row.duals][0])

                # the second numData contains the figures
                productIdList.append([d.numData for d in row.duals][1])

                # the third numData contains the figures
                purchasedList.append([d.numData for d in row.duals][2])

        #print(orderIdList[:10]) #first 10 entries of array
        datafrm = pd.DataFrame({'orderId': orderIdList, 'productId': productIdList, 'purchased': purchasedList})
        #print(datafrm.head()) #.head returns only the first 5 elements
        basket = (
            datafrm.groupby(['orderId', 'productId'])['purchased']
            .sum().unstack().reset_index().fillna(0)
            .set_index('orderId'))
        #print(basket.head())

        # Create 
        frequent_itemsets = apriori(basket, min_support=0.005, use_colnames=True)
        #print(frequent_itemsets.head())

        rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1)
        #print(rules.head())

        antList = rules['antecedents'].values.tolist()
        antList = [list(x) for x in antList]
        antList = [int(x[0]) for x in antList]
        conList = rules['consequents'].values.tolist()
        conList = [list(x) for x in conList]
        conList = [int(x[0]) for x in conList]
        dualsList = []
        dualsList.append([SSE.Dual(numData=d) for d in antList])
        dualsList.append([SSE.Dual(numData=d) for d in conList])
        dualsList.append([SSE.Dual(numData=d) for d in rules['support'].values.tolist()])
        dualsList.append([SSE.Dual(numData=d) for d in rules['confidence'].values.tolist()])
        dualsList.append([SSE.Dual(numData=d) for d in rules['lift'].values.tolist()])
        #print(dualsList)

        response_rows = []
        for i in range(len(antList)):
            duals = [dualsList[z][i] for z in range(len(dualsList))]
            response_rows.append(SSE.Row(duals=iter(duals)))
            
        print(request_rows)
        yield SSE.BundledRows(rows=response_rows)




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
                                        pluginIdentifier='Sentiment',
                                        pluginVersion='v1.1.0')

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
        func_type = self.ScriptEval.get_func_type(header)

        # Verify function type
        if (func_type == FunctionType.Aggregation) or (func_type == FunctionType.Tensor):
            return self.ScriptEval.EvaluateScript(header, request, context, func_type)
        else:
            # This plugin does not support other function types than aggregation  and tensor.
            # Make sure the error handling, including logging, works as intended in the client
            msg = 'Function type {} is not supported in this plugin.'.format(func_type.name)
            context.set_code(grpc.StatusCode.UNIMPLEMENTED)
            context.set_details(msg)
            # Raise error on the plugin-side
            raise grpc.RpcError(grpc.StatusCode.UNIMPLEMENTED, msg)

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
    parser.add_argument('--port', nargs='?', default='50088')
    parser.add_argument('--pem_dir', nargs='?')
    parser.add_argument('--definition_file', nargs='?', default='functions.json')
    args = parser.parse_args()

    # need to locate the file when script is called from outside it's location dir.
    def_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.definition_file)

    calc = ExtensionService(def_file)
    calc.Serve(args.port, args.pem_dir)

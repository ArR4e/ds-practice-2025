# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import suggestions_pb2 as suggestions__pb2


class SuggestionsServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.InitializeRequestData = channel.unary_unary(
                '/frauddetection.SuggestionsService/InitializeRequestData',
                request_serializer=suggestions__pb2.SuggestionsData.SerializeToString,
                response_deserializer=suggestions__pb2.InitializeResponse.FromString,
                )
        self.SuggestBooks = channel.unary_unary(
                '/frauddetection.SuggestionsService/SuggestBooks',
                request_serializer=suggestions__pb2.BookSuggestionRequest.SerializeToString,
                response_deserializer=suggestions__pb2.BookSuggestionResponse.FromString,
                )
        self.ClearData = channel.unary_unary(
                '/frauddetection.SuggestionsService/ClearData',
                request_serializer=suggestions__pb2.ClearSuggestionsDataRequest.SerializeToString,
                response_deserializer=suggestions__pb2.ClearSuggestionsDataResponse.FromString,
                )


class SuggestionsServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def InitializeRequestData(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SuggestBooks(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ClearData(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_SuggestionsServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'InitializeRequestData': grpc.unary_unary_rpc_method_handler(
                    servicer.InitializeRequestData,
                    request_deserializer=suggestions__pb2.SuggestionsData.FromString,
                    response_serializer=suggestions__pb2.InitializeResponse.SerializeToString,
            ),
            'SuggestBooks': grpc.unary_unary_rpc_method_handler(
                    servicer.SuggestBooks,
                    request_deserializer=suggestions__pb2.BookSuggestionRequest.FromString,
                    response_serializer=suggestions__pb2.BookSuggestionResponse.SerializeToString,
            ),
            'ClearData': grpc.unary_unary_rpc_method_handler(
                    servicer.ClearData,
                    request_deserializer=suggestions__pb2.ClearSuggestionsDataRequest.FromString,
                    response_serializer=suggestions__pb2.ClearSuggestionsDataResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'frauddetection.SuggestionsService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class SuggestionsService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def InitializeRequestData(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/frauddetection.SuggestionsService/InitializeRequestData',
            suggestions__pb2.SuggestionsData.SerializeToString,
            suggestions__pb2.InitializeResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SuggestBooks(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/frauddetection.SuggestionsService/SuggestBooks',
            suggestions__pb2.BookSuggestionRequest.SerializeToString,
            suggestions__pb2.BookSuggestionResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ClearData(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/frauddetection.SuggestionsService/ClearData',
            suggestions__pb2.ClearSuggestionsDataRequest.SerializeToString,
            suggestions__pb2.ClearSuggestionsDataResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import nexus_transfer_pb2 as nexus__transfer__pb2


class NexusTransferStub(object):
    """File transfering service, interface exported by the server.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Login = channel.unary_unary(
                '/nexustransfer.NexusTransfer/Login',
                request_serializer=nexus__transfer__pb2.Credentials.SerializeToString,
                response_deserializer=nexus__transfer__pb2.Response.FromString,
                )
        self.Logout = channel.unary_unary(
                '/nexustransfer.NexusTransfer/Logout',
                request_serializer=nexus__transfer__pb2.Peer.SerializeToString,
                response_deserializer=nexus__transfer__pb2.Response.FromString,
                )
        self.Ping = channel.unary_unary(
                '/nexustransfer.NexusTransfer/Ping',
                request_serializer=nexus__transfer__pb2.Call.SerializeToString,
                response_deserializer=nexus__transfer__pb2.Response.FromString,
                )
        self.SendDirectory = channel.unary_unary(
                '/nexustransfer.NexusTransfer/SendDirectory',
                request_serializer=nexus__transfer__pb2.Dir.SerializeToString,
                response_deserializer=nexus__transfer__pb2.Response.FromString,
                )
        self.Download = channel.unary_stream(
                '/nexustransfer.NexusTransfer/Download',
                request_serializer=nexus__transfer__pb2.FileRequest.SerializeToString,
                response_deserializer=nexus__transfer__pb2.Peer.FromString,
                )
        self.Upload = channel.unary_unary(
                '/nexustransfer.NexusTransfer/Upload',
                request_serializer=nexus__transfer__pb2.FileRequest.SerializeToString,
                response_deserializer=nexus__transfer__pb2.Peer.FromString,
                )


class NexusTransferServicer(object):
    """File transfering service, interface exported by the server.
    """

    def Login(self, request, context):
        """login peer
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Logout(self, request, context):
        """logout peer
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Ping(self, request, context):
        """reply to ping
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SendDirectory(self, request, context):
        """send peer's files directory
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Download(self, request, context):
        """download a file
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Upload(self, request, context):
        """upload a file
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_NexusTransferServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Login': grpc.unary_unary_rpc_method_handler(
                    servicer.Login,
                    request_deserializer=nexus__transfer__pb2.Credentials.FromString,
                    response_serializer=nexus__transfer__pb2.Response.SerializeToString,
            ),
            'Logout': grpc.unary_unary_rpc_method_handler(
                    servicer.Logout,
                    request_deserializer=nexus__transfer__pb2.Peer.FromString,
                    response_serializer=nexus__transfer__pb2.Response.SerializeToString,
            ),
            'Ping': grpc.unary_unary_rpc_method_handler(
                    servicer.Ping,
                    request_deserializer=nexus__transfer__pb2.Call.FromString,
                    response_serializer=nexus__transfer__pb2.Response.SerializeToString,
            ),
            'SendDirectory': grpc.unary_unary_rpc_method_handler(
                    servicer.SendDirectory,
                    request_deserializer=nexus__transfer__pb2.Dir.FromString,
                    response_serializer=nexus__transfer__pb2.Response.SerializeToString,
            ),
            'Download': grpc.unary_stream_rpc_method_handler(
                    servicer.Download,
                    request_deserializer=nexus__transfer__pb2.FileRequest.FromString,
                    response_serializer=nexus__transfer__pb2.Peer.SerializeToString,
            ),
            'Upload': grpc.unary_unary_rpc_method_handler(
                    servicer.Upload,
                    request_deserializer=nexus__transfer__pb2.FileRequest.FromString,
                    response_serializer=nexus__transfer__pb2.Peer.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'nexustransfer.NexusTransfer', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class NexusTransfer(object):
    """File transfering service, interface exported by the server.
    """

    @staticmethod
    def Login(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/nexustransfer.NexusTransfer/Login',
            nexus__transfer__pb2.Credentials.SerializeToString,
            nexus__transfer__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Logout(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/nexustransfer.NexusTransfer/Logout',
            nexus__transfer__pb2.Peer.SerializeToString,
            nexus__transfer__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Ping(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/nexustransfer.NexusTransfer/Ping',
            nexus__transfer__pb2.Call.SerializeToString,
            nexus__transfer__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SendDirectory(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/nexustransfer.NexusTransfer/SendDirectory',
            nexus__transfer__pb2.Dir.SerializeToString,
            nexus__transfer__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Download(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/nexustransfer.NexusTransfer/Download',
            nexus__transfer__pb2.FileRequest.SerializeToString,
            nexus__transfer__pb2.Peer.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Upload(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/nexustransfer.NexusTransfer/Upload',
            nexus__transfer__pb2.FileRequest.SerializeToString,
            nexus__transfer__pb2.Peer.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
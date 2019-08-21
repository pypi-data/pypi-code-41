import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@aws-cdk/aws-appmesh", "1.5.0", __name__, "aws-appmesh@1.5.0.jsii.tgz")
class CfnMesh(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-appmesh.CfnMesh"):
    """A CloudFormation ``AWS::AppMesh::Mesh``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-mesh.html
    cloudformationResource:
    :cloudformationResource:: AWS::AppMesh::Mesh
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, mesh_name: str, spec: typing.Optional[typing.Union[typing.Optional["MeshSpecProperty"], typing.Optional[aws_cdk.core.IResolvable]]]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::AppMesh::Mesh``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param mesh_name: ``AWS::AppMesh::Mesh.MeshName``.
        :param spec: ``AWS::AppMesh::Mesh.Spec``.
        :param tags: ``AWS::AppMesh::Mesh.Tags``.
        """
        props = CfnMeshProps(mesh_name=mesh_name, spec=spec, tags=tags)

        jsii.create(CfnMesh, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        :param props: -
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class."""
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Arn
        """
        return jsii.get(self, "attrArn")

    @property
    @jsii.member(jsii_name="attrMeshName")
    def attr_mesh_name(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: MeshName
        """
        return jsii.get(self, "attrMeshName")

    @property
    @jsii.member(jsii_name="attrUid")
    def attr_uid(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Uid
        """
        return jsii.get(self, "attrUid")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::AppMesh::Mesh.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-mesh.html#cfn-appmesh-mesh-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="meshName")
    def mesh_name(self) -> str:
        """``AWS::AppMesh::Mesh.MeshName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-mesh.html#cfn-appmesh-mesh-meshname
        """
        return jsii.get(self, "meshName")

    @mesh_name.setter
    def mesh_name(self, value: str):
        return jsii.set(self, "meshName", value)

    @property
    @jsii.member(jsii_name="spec")
    def spec(self) -> typing.Optional[typing.Union[typing.Optional["MeshSpecProperty"], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::AppMesh::Mesh.Spec``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-mesh.html#cfn-appmesh-mesh-spec
        """
        return jsii.get(self, "spec")

    @spec.setter
    def spec(self, value: typing.Optional[typing.Union[typing.Optional["MeshSpecProperty"], typing.Optional[aws_cdk.core.IResolvable]]]):
        return jsii.set(self, "spec", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnMesh.EgressFilterProperty", jsii_struct_bases=[], name_mapping={'type': 'type'})
    class EgressFilterProperty():
        def __init__(self, *, type: str):
            """
            :param type: ``CfnMesh.EgressFilterProperty.Type``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-mesh-egressfilter.html
            """
            self._values = {
                'type': type,
            }

        @property
        def type(self) -> str:
            """``CfnMesh.EgressFilterProperty.Type``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-mesh-egressfilter.html#cfn-appmesh-mesh-egressfilter-type
            """
            return self._values.get('type')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'EgressFilterProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnMesh.MeshSpecProperty", jsii_struct_bases=[], name_mapping={'egress_filter': 'egressFilter'})
    class MeshSpecProperty():
        def __init__(self, *, egress_filter: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnMesh.EgressFilterProperty"]]]=None):
            """
            :param egress_filter: ``CfnMesh.MeshSpecProperty.EgressFilter``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-mesh-meshspec.html
            """
            self._values = {
            }
            if egress_filter is not None: self._values["egress_filter"] = egress_filter

        @property
        def egress_filter(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnMesh.EgressFilterProperty"]]]:
            """``CfnMesh.MeshSpecProperty.EgressFilter``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-mesh-meshspec.html#cfn-appmesh-mesh-meshspec-egressfilter
            """
            return self._values.get('egress_filter')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'MeshSpecProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnMeshProps", jsii_struct_bases=[], name_mapping={'mesh_name': 'meshName', 'spec': 'spec', 'tags': 'tags'})
class CfnMeshProps():
    def __init__(self, *, mesh_name: str, spec: typing.Optional[typing.Union[typing.Optional["CfnMesh.MeshSpecProperty"], typing.Optional[aws_cdk.core.IResolvable]]]=None, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None):
        """Properties for defining a ``AWS::AppMesh::Mesh``.

        :param mesh_name: ``AWS::AppMesh::Mesh.MeshName``.
        :param spec: ``AWS::AppMesh::Mesh.Spec``.
        :param tags: ``AWS::AppMesh::Mesh.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-mesh.html
        """
        self._values = {
            'mesh_name': mesh_name,
        }
        if spec is not None: self._values["spec"] = spec
        if tags is not None: self._values["tags"] = tags

    @property
    def mesh_name(self) -> str:
        """``AWS::AppMesh::Mesh.MeshName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-mesh.html#cfn-appmesh-mesh-meshname
        """
        return self._values.get('mesh_name')

    @property
    def spec(self) -> typing.Optional[typing.Union[typing.Optional["CfnMesh.MeshSpecProperty"], typing.Optional[aws_cdk.core.IResolvable]]]:
        """``AWS::AppMesh::Mesh.Spec``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-mesh.html#cfn-appmesh-mesh-spec
        """
        return self._values.get('spec')

    @property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        """``AWS::AppMesh::Mesh.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-mesh.html#cfn-appmesh-mesh-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnMeshProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnRoute(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-appmesh.CfnRoute"):
    """A CloudFormation ``AWS::AppMesh::Route``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-route.html
    cloudformationResource:
    :cloudformationResource:: AWS::AppMesh::Route
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, mesh_name: str, route_name: str, spec: typing.Union[aws_cdk.core.IResolvable, "RouteSpecProperty"], virtual_router_name: str, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::AppMesh::Route``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param mesh_name: ``AWS::AppMesh::Route.MeshName``.
        :param route_name: ``AWS::AppMesh::Route.RouteName``.
        :param spec: ``AWS::AppMesh::Route.Spec``.
        :param virtual_router_name: ``AWS::AppMesh::Route.VirtualRouterName``.
        :param tags: ``AWS::AppMesh::Route.Tags``.
        """
        props = CfnRouteProps(mesh_name=mesh_name, route_name=route_name, spec=spec, virtual_router_name=virtual_router_name, tags=tags)

        jsii.create(CfnRoute, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        :param props: -
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class."""
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Arn
        """
        return jsii.get(self, "attrArn")

    @property
    @jsii.member(jsii_name="attrMeshName")
    def attr_mesh_name(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: MeshName
        """
        return jsii.get(self, "attrMeshName")

    @property
    @jsii.member(jsii_name="attrRouteName")
    def attr_route_name(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: RouteName
        """
        return jsii.get(self, "attrRouteName")

    @property
    @jsii.member(jsii_name="attrUid")
    def attr_uid(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Uid
        """
        return jsii.get(self, "attrUid")

    @property
    @jsii.member(jsii_name="attrVirtualRouterName")
    def attr_virtual_router_name(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: VirtualRouterName
        """
        return jsii.get(self, "attrVirtualRouterName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::AppMesh::Route.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-route.html#cfn-appmesh-route-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="meshName")
    def mesh_name(self) -> str:
        """``AWS::AppMesh::Route.MeshName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-route.html#cfn-appmesh-route-meshname
        """
        return jsii.get(self, "meshName")

    @mesh_name.setter
    def mesh_name(self, value: str):
        return jsii.set(self, "meshName", value)

    @property
    @jsii.member(jsii_name="routeName")
    def route_name(self) -> str:
        """``AWS::AppMesh::Route.RouteName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-route.html#cfn-appmesh-route-routename
        """
        return jsii.get(self, "routeName")

    @route_name.setter
    def route_name(self, value: str):
        return jsii.set(self, "routeName", value)

    @property
    @jsii.member(jsii_name="spec")
    def spec(self) -> typing.Union[aws_cdk.core.IResolvable, "RouteSpecProperty"]:
        """``AWS::AppMesh::Route.Spec``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-route.html#cfn-appmesh-route-spec
        """
        return jsii.get(self, "spec")

    @spec.setter
    def spec(self, value: typing.Union[aws_cdk.core.IResolvable, "RouteSpecProperty"]):
        return jsii.set(self, "spec", value)

    @property
    @jsii.member(jsii_name="virtualRouterName")
    def virtual_router_name(self) -> str:
        """``AWS::AppMesh::Route.VirtualRouterName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-route.html#cfn-appmesh-route-virtualroutername
        """
        return jsii.get(self, "virtualRouterName")

    @virtual_router_name.setter
    def virtual_router_name(self, value: str):
        return jsii.set(self, "virtualRouterName", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnRoute.HttpRouteActionProperty", jsii_struct_bases=[], name_mapping={'weighted_targets': 'weightedTargets'})
    class HttpRouteActionProperty():
        def __init__(self, *, weighted_targets: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnRoute.WeightedTargetProperty"]]]):
            """
            :param weighted_targets: ``CfnRoute.HttpRouteActionProperty.WeightedTargets``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-httprouteaction.html
            """
            self._values = {
                'weighted_targets': weighted_targets,
            }

        @property
        def weighted_targets(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnRoute.WeightedTargetProperty"]]]:
            """``CfnRoute.HttpRouteActionProperty.WeightedTargets``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-httprouteaction.html#cfn-appmesh-route-httprouteaction-weightedtargets
            """
            return self._values.get('weighted_targets')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'HttpRouteActionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnRoute.HttpRouteMatchProperty", jsii_struct_bases=[], name_mapping={'prefix': 'prefix'})
    class HttpRouteMatchProperty():
        def __init__(self, *, prefix: str):
            """
            :param prefix: ``CfnRoute.HttpRouteMatchProperty.Prefix``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-httproutematch.html
            """
            self._values = {
                'prefix': prefix,
            }

        @property
        def prefix(self) -> str:
            """``CfnRoute.HttpRouteMatchProperty.Prefix``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-httproutematch.html#cfn-appmesh-route-httproutematch-prefix
            """
            return self._values.get('prefix')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'HttpRouteMatchProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnRoute.HttpRouteProperty", jsii_struct_bases=[], name_mapping={'action': 'action', 'match': 'match'})
    class HttpRouteProperty():
        def __init__(self, *, action: typing.Union[aws_cdk.core.IResolvable, "CfnRoute.HttpRouteActionProperty"], match: typing.Union[aws_cdk.core.IResolvable, "CfnRoute.HttpRouteMatchProperty"]):
            """
            :param action: ``CfnRoute.HttpRouteProperty.Action``.
            :param match: ``CfnRoute.HttpRouteProperty.Match``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-httproute.html
            """
            self._values = {
                'action': action,
                'match': match,
            }

        @property
        def action(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnRoute.HttpRouteActionProperty"]:
            """``CfnRoute.HttpRouteProperty.Action``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-httproute.html#cfn-appmesh-route-httproute-action
            """
            return self._values.get('action')

        @property
        def match(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnRoute.HttpRouteMatchProperty"]:
            """``CfnRoute.HttpRouteProperty.Match``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-httproute.html#cfn-appmesh-route-httproute-match
            """
            return self._values.get('match')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'HttpRouteProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnRoute.RouteSpecProperty", jsii_struct_bases=[], name_mapping={'http_route': 'httpRoute', 'tcp_route': 'tcpRoute'})
    class RouteSpecProperty():
        def __init__(self, *, http_route: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnRoute.HttpRouteProperty"]]]=None, tcp_route: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnRoute.TcpRouteProperty"]]]=None):
            """
            :param http_route: ``CfnRoute.RouteSpecProperty.HttpRoute``.
            :param tcp_route: ``CfnRoute.RouteSpecProperty.TcpRoute``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-routespec.html
            """
            self._values = {
            }
            if http_route is not None: self._values["http_route"] = http_route
            if tcp_route is not None: self._values["tcp_route"] = tcp_route

        @property
        def http_route(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnRoute.HttpRouteProperty"]]]:
            """``CfnRoute.RouteSpecProperty.HttpRoute``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-routespec.html#cfn-appmesh-route-routespec-httproute
            """
            return self._values.get('http_route')

        @property
        def tcp_route(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnRoute.TcpRouteProperty"]]]:
            """``CfnRoute.RouteSpecProperty.TcpRoute``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-routespec.html#cfn-appmesh-route-routespec-tcproute
            """
            return self._values.get('tcp_route')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'RouteSpecProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnRoute.TcpRouteActionProperty", jsii_struct_bases=[], name_mapping={'weighted_targets': 'weightedTargets'})
    class TcpRouteActionProperty():
        def __init__(self, *, weighted_targets: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnRoute.WeightedTargetProperty"]]]):
            """
            :param weighted_targets: ``CfnRoute.TcpRouteActionProperty.WeightedTargets``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-tcprouteaction.html
            """
            self._values = {
                'weighted_targets': weighted_targets,
            }

        @property
        def weighted_targets(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnRoute.WeightedTargetProperty"]]]:
            """``CfnRoute.TcpRouteActionProperty.WeightedTargets``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-tcprouteaction.html#cfn-appmesh-route-tcprouteaction-weightedtargets
            """
            return self._values.get('weighted_targets')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'TcpRouteActionProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnRoute.TcpRouteProperty", jsii_struct_bases=[], name_mapping={'action': 'action'})
    class TcpRouteProperty():
        def __init__(self, *, action: typing.Union[aws_cdk.core.IResolvable, "CfnRoute.TcpRouteActionProperty"]):
            """
            :param action: ``CfnRoute.TcpRouteProperty.Action``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-tcproute.html
            """
            self._values = {
                'action': action,
            }

        @property
        def action(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnRoute.TcpRouteActionProperty"]:
            """``CfnRoute.TcpRouteProperty.Action``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-tcproute.html#cfn-appmesh-route-tcproute-action
            """
            return self._values.get('action')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'TcpRouteProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnRoute.WeightedTargetProperty", jsii_struct_bases=[], name_mapping={'virtual_node': 'virtualNode', 'weight': 'weight'})
    class WeightedTargetProperty():
        def __init__(self, *, virtual_node: str, weight: jsii.Number):
            """
            :param virtual_node: ``CfnRoute.WeightedTargetProperty.VirtualNode``.
            :param weight: ``CfnRoute.WeightedTargetProperty.Weight``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-weightedtarget.html
            """
            self._values = {
                'virtual_node': virtual_node,
                'weight': weight,
            }

        @property
        def virtual_node(self) -> str:
            """``CfnRoute.WeightedTargetProperty.VirtualNode``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-weightedtarget.html#cfn-appmesh-route-weightedtarget-virtualnode
            """
            return self._values.get('virtual_node')

        @property
        def weight(self) -> jsii.Number:
            """``CfnRoute.WeightedTargetProperty.Weight``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-route-weightedtarget.html#cfn-appmesh-route-weightedtarget-weight
            """
            return self._values.get('weight')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'WeightedTargetProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnRouteProps", jsii_struct_bases=[], name_mapping={'mesh_name': 'meshName', 'route_name': 'routeName', 'spec': 'spec', 'virtual_router_name': 'virtualRouterName', 'tags': 'tags'})
class CfnRouteProps():
    def __init__(self, *, mesh_name: str, route_name: str, spec: typing.Union[aws_cdk.core.IResolvable, "CfnRoute.RouteSpecProperty"], virtual_router_name: str, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None):
        """Properties for defining a ``AWS::AppMesh::Route``.

        :param mesh_name: ``AWS::AppMesh::Route.MeshName``.
        :param route_name: ``AWS::AppMesh::Route.RouteName``.
        :param spec: ``AWS::AppMesh::Route.Spec``.
        :param virtual_router_name: ``AWS::AppMesh::Route.VirtualRouterName``.
        :param tags: ``AWS::AppMesh::Route.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-route.html
        """
        self._values = {
            'mesh_name': mesh_name,
            'route_name': route_name,
            'spec': spec,
            'virtual_router_name': virtual_router_name,
        }
        if tags is not None: self._values["tags"] = tags

    @property
    def mesh_name(self) -> str:
        """``AWS::AppMesh::Route.MeshName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-route.html#cfn-appmesh-route-meshname
        """
        return self._values.get('mesh_name')

    @property
    def route_name(self) -> str:
        """``AWS::AppMesh::Route.RouteName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-route.html#cfn-appmesh-route-routename
        """
        return self._values.get('route_name')

    @property
    def spec(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnRoute.RouteSpecProperty"]:
        """``AWS::AppMesh::Route.Spec``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-route.html#cfn-appmesh-route-spec
        """
        return self._values.get('spec')

    @property
    def virtual_router_name(self) -> str:
        """``AWS::AppMesh::Route.VirtualRouterName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-route.html#cfn-appmesh-route-virtualroutername
        """
        return self._values.get('virtual_router_name')

    @property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        """``AWS::AppMesh::Route.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-route.html#cfn-appmesh-route-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnRouteProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnVirtualNode(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-appmesh.CfnVirtualNode"):
    """A CloudFormation ``AWS::AppMesh::VirtualNode``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualnode.html
    cloudformationResource:
    :cloudformationResource:: AWS::AppMesh::VirtualNode
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, mesh_name: str, spec: typing.Union[aws_cdk.core.IResolvable, "VirtualNodeSpecProperty"], virtual_node_name: str, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::AppMesh::VirtualNode``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param mesh_name: ``AWS::AppMesh::VirtualNode.MeshName``.
        :param spec: ``AWS::AppMesh::VirtualNode.Spec``.
        :param virtual_node_name: ``AWS::AppMesh::VirtualNode.VirtualNodeName``.
        :param tags: ``AWS::AppMesh::VirtualNode.Tags``.
        """
        props = CfnVirtualNodeProps(mesh_name=mesh_name, spec=spec, virtual_node_name=virtual_node_name, tags=tags)

        jsii.create(CfnVirtualNode, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        :param props: -
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class."""
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Arn
        """
        return jsii.get(self, "attrArn")

    @property
    @jsii.member(jsii_name="attrMeshName")
    def attr_mesh_name(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: MeshName
        """
        return jsii.get(self, "attrMeshName")

    @property
    @jsii.member(jsii_name="attrUid")
    def attr_uid(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Uid
        """
        return jsii.get(self, "attrUid")

    @property
    @jsii.member(jsii_name="attrVirtualNodeName")
    def attr_virtual_node_name(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: VirtualNodeName
        """
        return jsii.get(self, "attrVirtualNodeName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::AppMesh::VirtualNode.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualnode.html#cfn-appmesh-virtualnode-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="meshName")
    def mesh_name(self) -> str:
        """``AWS::AppMesh::VirtualNode.MeshName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualnode.html#cfn-appmesh-virtualnode-meshname
        """
        return jsii.get(self, "meshName")

    @mesh_name.setter
    def mesh_name(self, value: str):
        return jsii.set(self, "meshName", value)

    @property
    @jsii.member(jsii_name="spec")
    def spec(self) -> typing.Union[aws_cdk.core.IResolvable, "VirtualNodeSpecProperty"]:
        """``AWS::AppMesh::VirtualNode.Spec``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualnode.html#cfn-appmesh-virtualnode-spec
        """
        return jsii.get(self, "spec")

    @spec.setter
    def spec(self, value: typing.Union[aws_cdk.core.IResolvable, "VirtualNodeSpecProperty"]):
        return jsii.set(self, "spec", value)

    @property
    @jsii.member(jsii_name="virtualNodeName")
    def virtual_node_name(self) -> str:
        """``AWS::AppMesh::VirtualNode.VirtualNodeName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualnode.html#cfn-appmesh-virtualnode-virtualnodename
        """
        return jsii.get(self, "virtualNodeName")

    @virtual_node_name.setter
    def virtual_node_name(self, value: str):
        return jsii.set(self, "virtualNodeName", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualNode.AccessLogProperty", jsii_struct_bases=[], name_mapping={'file': 'file'})
    class AccessLogProperty():
        def __init__(self, *, file: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualNode.FileAccessLogProperty"]]]=None):
            """
            :param file: ``CfnVirtualNode.AccessLogProperty.File``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-accesslog.html
            """
            self._values = {
            }
            if file is not None: self._values["file"] = file

        @property
        def file(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualNode.FileAccessLogProperty"]]]:
            """``CfnVirtualNode.AccessLogProperty.File``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-accesslog.html#cfn-appmesh-virtualnode-accesslog-file
            """
            return self._values.get('file')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'AccessLogProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualNode.AwsCloudMapInstanceAttributeProperty", jsii_struct_bases=[], name_mapping={'key': 'key', 'value': 'value'})
    class AwsCloudMapInstanceAttributeProperty():
        def __init__(self, *, key: str, value: str):
            """
            :param key: ``CfnVirtualNode.AwsCloudMapInstanceAttributeProperty.Key``.
            :param value: ``CfnVirtualNode.AwsCloudMapInstanceAttributeProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-awscloudmapinstanceattribute.html
            """
            self._values = {
                'key': key,
                'value': value,
            }

        @property
        def key(self) -> str:
            """``CfnVirtualNode.AwsCloudMapInstanceAttributeProperty.Key``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-awscloudmapinstanceattribute.html#cfn-appmesh-virtualnode-awscloudmapinstanceattribute-key
            """
            return self._values.get('key')

        @property
        def value(self) -> str:
            """``CfnVirtualNode.AwsCloudMapInstanceAttributeProperty.Value``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-awscloudmapinstanceattribute.html#cfn-appmesh-virtualnode-awscloudmapinstanceattribute-value
            """
            return self._values.get('value')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'AwsCloudMapInstanceAttributeProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualNode.AwsCloudMapServiceDiscoveryProperty", jsii_struct_bases=[], name_mapping={'namespace_name': 'namespaceName', 'service_name': 'serviceName', 'attributes': 'attributes'})
    class AwsCloudMapServiceDiscoveryProperty():
        def __init__(self, *, namespace_name: str, service_name: str, attributes: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnVirtualNode.AwsCloudMapInstanceAttributeProperty"]]]]]=None):
            """
            :param namespace_name: ``CfnVirtualNode.AwsCloudMapServiceDiscoveryProperty.NamespaceName``.
            :param service_name: ``CfnVirtualNode.AwsCloudMapServiceDiscoveryProperty.ServiceName``.
            :param attributes: ``CfnVirtualNode.AwsCloudMapServiceDiscoveryProperty.Attributes``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-awscloudmapservicediscovery.html
            """
            self._values = {
                'namespace_name': namespace_name,
                'service_name': service_name,
            }
            if attributes is not None: self._values["attributes"] = attributes

        @property
        def namespace_name(self) -> str:
            """``CfnVirtualNode.AwsCloudMapServiceDiscoveryProperty.NamespaceName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-awscloudmapservicediscovery.html#cfn-appmesh-virtualnode-awscloudmapservicediscovery-namespacename
            """
            return self._values.get('namespace_name')

        @property
        def service_name(self) -> str:
            """``CfnVirtualNode.AwsCloudMapServiceDiscoveryProperty.ServiceName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-awscloudmapservicediscovery.html#cfn-appmesh-virtualnode-awscloudmapservicediscovery-servicename
            """
            return self._values.get('service_name')

        @property
        def attributes(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnVirtualNode.AwsCloudMapInstanceAttributeProperty"]]]]]:
            """``CfnVirtualNode.AwsCloudMapServiceDiscoveryProperty.Attributes``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-awscloudmapservicediscovery.html#cfn-appmesh-virtualnode-awscloudmapservicediscovery-attributes
            """
            return self._values.get('attributes')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'AwsCloudMapServiceDiscoveryProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualNode.BackendProperty", jsii_struct_bases=[], name_mapping={'virtual_service': 'virtualService'})
    class BackendProperty():
        def __init__(self, *, virtual_service: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualNode.VirtualServiceBackendProperty"]]]=None):
            """
            :param virtual_service: ``CfnVirtualNode.BackendProperty.VirtualService``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-backend.html
            """
            self._values = {
            }
            if virtual_service is not None: self._values["virtual_service"] = virtual_service

        @property
        def virtual_service(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualNode.VirtualServiceBackendProperty"]]]:
            """``CfnVirtualNode.BackendProperty.VirtualService``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-backend.html#cfn-appmesh-virtualnode-backend-virtualservice
            """
            return self._values.get('virtual_service')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'BackendProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualNode.DnsServiceDiscoveryProperty", jsii_struct_bases=[], name_mapping={'hostname': 'hostname'})
    class DnsServiceDiscoveryProperty():
        def __init__(self, *, hostname: str):
            """
            :param hostname: ``CfnVirtualNode.DnsServiceDiscoveryProperty.Hostname``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-dnsservicediscovery.html
            """
            self._values = {
                'hostname': hostname,
            }

        @property
        def hostname(self) -> str:
            """``CfnVirtualNode.DnsServiceDiscoveryProperty.Hostname``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-dnsservicediscovery.html#cfn-appmesh-virtualnode-dnsservicediscovery-hostname
            """
            return self._values.get('hostname')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'DnsServiceDiscoveryProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualNode.FileAccessLogProperty", jsii_struct_bases=[], name_mapping={'path': 'path'})
    class FileAccessLogProperty():
        def __init__(self, *, path: str):
            """
            :param path: ``CfnVirtualNode.FileAccessLogProperty.Path``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-fileaccesslog.html
            """
            self._values = {
                'path': path,
            }

        @property
        def path(self) -> str:
            """``CfnVirtualNode.FileAccessLogProperty.Path``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-fileaccesslog.html#cfn-appmesh-virtualnode-fileaccesslog-path
            """
            return self._values.get('path')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'FileAccessLogProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualNode.HealthCheckProperty", jsii_struct_bases=[], name_mapping={'healthy_threshold': 'healthyThreshold', 'interval_millis': 'intervalMillis', 'protocol': 'protocol', 'timeout_millis': 'timeoutMillis', 'unhealthy_threshold': 'unhealthyThreshold', 'path': 'path', 'port': 'port'})
    class HealthCheckProperty():
        def __init__(self, *, healthy_threshold: jsii.Number, interval_millis: jsii.Number, protocol: str, timeout_millis: jsii.Number, unhealthy_threshold: jsii.Number, path: typing.Optional[str]=None, port: typing.Optional[jsii.Number]=None):
            """
            :param healthy_threshold: ``CfnVirtualNode.HealthCheckProperty.HealthyThreshold``.
            :param interval_millis: ``CfnVirtualNode.HealthCheckProperty.IntervalMillis``.
            :param protocol: ``CfnVirtualNode.HealthCheckProperty.Protocol``.
            :param timeout_millis: ``CfnVirtualNode.HealthCheckProperty.TimeoutMillis``.
            :param unhealthy_threshold: ``CfnVirtualNode.HealthCheckProperty.UnhealthyThreshold``.
            :param path: ``CfnVirtualNode.HealthCheckProperty.Path``.
            :param port: ``CfnVirtualNode.HealthCheckProperty.Port``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-healthcheck.html
            """
            self._values = {
                'healthy_threshold': healthy_threshold,
                'interval_millis': interval_millis,
                'protocol': protocol,
                'timeout_millis': timeout_millis,
                'unhealthy_threshold': unhealthy_threshold,
            }
            if path is not None: self._values["path"] = path
            if port is not None: self._values["port"] = port

        @property
        def healthy_threshold(self) -> jsii.Number:
            """``CfnVirtualNode.HealthCheckProperty.HealthyThreshold``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-healthcheck.html#cfn-appmesh-virtualnode-healthcheck-healthythreshold
            """
            return self._values.get('healthy_threshold')

        @property
        def interval_millis(self) -> jsii.Number:
            """``CfnVirtualNode.HealthCheckProperty.IntervalMillis``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-healthcheck.html#cfn-appmesh-virtualnode-healthcheck-intervalmillis
            """
            return self._values.get('interval_millis')

        @property
        def protocol(self) -> str:
            """``CfnVirtualNode.HealthCheckProperty.Protocol``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-healthcheck.html#cfn-appmesh-virtualnode-healthcheck-protocol
            """
            return self._values.get('protocol')

        @property
        def timeout_millis(self) -> jsii.Number:
            """``CfnVirtualNode.HealthCheckProperty.TimeoutMillis``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-healthcheck.html#cfn-appmesh-virtualnode-healthcheck-timeoutmillis
            """
            return self._values.get('timeout_millis')

        @property
        def unhealthy_threshold(self) -> jsii.Number:
            """``CfnVirtualNode.HealthCheckProperty.UnhealthyThreshold``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-healthcheck.html#cfn-appmesh-virtualnode-healthcheck-unhealthythreshold
            """
            return self._values.get('unhealthy_threshold')

        @property
        def path(self) -> typing.Optional[str]:
            """``CfnVirtualNode.HealthCheckProperty.Path``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-healthcheck.html#cfn-appmesh-virtualnode-healthcheck-path
            """
            return self._values.get('path')

        @property
        def port(self) -> typing.Optional[jsii.Number]:
            """``CfnVirtualNode.HealthCheckProperty.Port``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-healthcheck.html#cfn-appmesh-virtualnode-healthcheck-port
            """
            return self._values.get('port')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'HealthCheckProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualNode.ListenerProperty", jsii_struct_bases=[], name_mapping={'port_mapping': 'portMapping', 'health_check': 'healthCheck'})
    class ListenerProperty():
        def __init__(self, *, port_mapping: typing.Union[aws_cdk.core.IResolvable, "CfnVirtualNode.PortMappingProperty"], health_check: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualNode.HealthCheckProperty"]]]=None):
            """
            :param port_mapping: ``CfnVirtualNode.ListenerProperty.PortMapping``.
            :param health_check: ``CfnVirtualNode.ListenerProperty.HealthCheck``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-listener.html
            """
            self._values = {
                'port_mapping': port_mapping,
            }
            if health_check is not None: self._values["health_check"] = health_check

        @property
        def port_mapping(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnVirtualNode.PortMappingProperty"]:
            """``CfnVirtualNode.ListenerProperty.PortMapping``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-listener.html#cfn-appmesh-virtualnode-listener-portmapping
            """
            return self._values.get('port_mapping')

        @property
        def health_check(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualNode.HealthCheckProperty"]]]:
            """``CfnVirtualNode.ListenerProperty.HealthCheck``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-listener.html#cfn-appmesh-virtualnode-listener-healthcheck
            """
            return self._values.get('health_check')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ListenerProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualNode.LoggingProperty", jsii_struct_bases=[], name_mapping={'access_log': 'accessLog'})
    class LoggingProperty():
        def __init__(self, *, access_log: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualNode.AccessLogProperty"]]]=None):
            """
            :param access_log: ``CfnVirtualNode.LoggingProperty.AccessLog``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-logging.html
            """
            self._values = {
            }
            if access_log is not None: self._values["access_log"] = access_log

        @property
        def access_log(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualNode.AccessLogProperty"]]]:
            """``CfnVirtualNode.LoggingProperty.AccessLog``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-logging.html#cfn-appmesh-virtualnode-logging-accesslog
            """
            return self._values.get('access_log')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'LoggingProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualNode.PortMappingProperty", jsii_struct_bases=[], name_mapping={'port': 'port', 'protocol': 'protocol'})
    class PortMappingProperty():
        def __init__(self, *, port: jsii.Number, protocol: str):
            """
            :param port: ``CfnVirtualNode.PortMappingProperty.Port``.
            :param protocol: ``CfnVirtualNode.PortMappingProperty.Protocol``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-portmapping.html
            """
            self._values = {
                'port': port,
                'protocol': protocol,
            }

        @property
        def port(self) -> jsii.Number:
            """``CfnVirtualNode.PortMappingProperty.Port``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-portmapping.html#cfn-appmesh-virtualnode-portmapping-port
            """
            return self._values.get('port')

        @property
        def protocol(self) -> str:
            """``CfnVirtualNode.PortMappingProperty.Protocol``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-portmapping.html#cfn-appmesh-virtualnode-portmapping-protocol
            """
            return self._values.get('protocol')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'PortMappingProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualNode.ServiceDiscoveryProperty", jsii_struct_bases=[], name_mapping={'aws_cloud_map': 'awsCloudMap', 'dns': 'dns'})
    class ServiceDiscoveryProperty():
        def __init__(self, *, aws_cloud_map: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualNode.AwsCloudMapServiceDiscoveryProperty"]]]=None, dns: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualNode.DnsServiceDiscoveryProperty"]]]=None):
            """
            :param aws_cloud_map: ``CfnVirtualNode.ServiceDiscoveryProperty.AWSCloudMap``.
            :param dns: ``CfnVirtualNode.ServiceDiscoveryProperty.DNS``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-servicediscovery.html
            """
            self._values = {
            }
            if aws_cloud_map is not None: self._values["aws_cloud_map"] = aws_cloud_map
            if dns is not None: self._values["dns"] = dns

        @property
        def aws_cloud_map(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualNode.AwsCloudMapServiceDiscoveryProperty"]]]:
            """``CfnVirtualNode.ServiceDiscoveryProperty.AWSCloudMap``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-servicediscovery.html#cfn-appmesh-virtualnode-servicediscovery-awscloudmap
            """
            return self._values.get('aws_cloud_map')

        @property
        def dns(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualNode.DnsServiceDiscoveryProperty"]]]:
            """``CfnVirtualNode.ServiceDiscoveryProperty.DNS``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-servicediscovery.html#cfn-appmesh-virtualnode-servicediscovery-dns
            """
            return self._values.get('dns')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'ServiceDiscoveryProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualNode.VirtualNodeSpecProperty", jsii_struct_bases=[], name_mapping={'backends': 'backends', 'listeners': 'listeners', 'logging': 'logging', 'service_discovery': 'serviceDiscovery'})
    class VirtualNodeSpecProperty():
        def __init__(self, *, backends: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnVirtualNode.BackendProperty"]]]]]=None, listeners: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnVirtualNode.ListenerProperty"]]]]]=None, logging: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualNode.LoggingProperty"]]]=None, service_discovery: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualNode.ServiceDiscoveryProperty"]]]=None):
            """
            :param backends: ``CfnVirtualNode.VirtualNodeSpecProperty.Backends``.
            :param listeners: ``CfnVirtualNode.VirtualNodeSpecProperty.Listeners``.
            :param logging: ``CfnVirtualNode.VirtualNodeSpecProperty.Logging``.
            :param service_discovery: ``CfnVirtualNode.VirtualNodeSpecProperty.ServiceDiscovery``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-virtualnodespec.html
            """
            self._values = {
            }
            if backends is not None: self._values["backends"] = backends
            if listeners is not None: self._values["listeners"] = listeners
            if logging is not None: self._values["logging"] = logging
            if service_discovery is not None: self._values["service_discovery"] = service_discovery

        @property
        def backends(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnVirtualNode.BackendProperty"]]]]]:
            """``CfnVirtualNode.VirtualNodeSpecProperty.Backends``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-virtualnodespec.html#cfn-appmesh-virtualnode-virtualnodespec-backends
            """
            return self._values.get('backends')

        @property
        def listeners(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional[typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnVirtualNode.ListenerProperty"]]]]]:
            """``CfnVirtualNode.VirtualNodeSpecProperty.Listeners``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-virtualnodespec.html#cfn-appmesh-virtualnode-virtualnodespec-listeners
            """
            return self._values.get('listeners')

        @property
        def logging(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualNode.LoggingProperty"]]]:
            """``CfnVirtualNode.VirtualNodeSpecProperty.Logging``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-virtualnodespec.html#cfn-appmesh-virtualnode-virtualnodespec-logging
            """
            return self._values.get('logging')

        @property
        def service_discovery(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualNode.ServiceDiscoveryProperty"]]]:
            """``CfnVirtualNode.VirtualNodeSpecProperty.ServiceDiscovery``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-virtualnodespec.html#cfn-appmesh-virtualnode-virtualnodespec-servicediscovery
            """
            return self._values.get('service_discovery')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'VirtualNodeSpecProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualNode.VirtualServiceBackendProperty", jsii_struct_bases=[], name_mapping={'virtual_service_name': 'virtualServiceName'})
    class VirtualServiceBackendProperty():
        def __init__(self, *, virtual_service_name: str):
            """
            :param virtual_service_name: ``CfnVirtualNode.VirtualServiceBackendProperty.VirtualServiceName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-virtualservicebackend.html
            """
            self._values = {
                'virtual_service_name': virtual_service_name,
            }

        @property
        def virtual_service_name(self) -> str:
            """``CfnVirtualNode.VirtualServiceBackendProperty.VirtualServiceName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualnode-virtualservicebackend.html#cfn-appmesh-virtualnode-virtualservicebackend-virtualservicename
            """
            return self._values.get('virtual_service_name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'VirtualServiceBackendProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualNodeProps", jsii_struct_bases=[], name_mapping={'mesh_name': 'meshName', 'spec': 'spec', 'virtual_node_name': 'virtualNodeName', 'tags': 'tags'})
class CfnVirtualNodeProps():
    def __init__(self, *, mesh_name: str, spec: typing.Union[aws_cdk.core.IResolvable, "CfnVirtualNode.VirtualNodeSpecProperty"], virtual_node_name: str, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None):
        """Properties for defining a ``AWS::AppMesh::VirtualNode``.

        :param mesh_name: ``AWS::AppMesh::VirtualNode.MeshName``.
        :param spec: ``AWS::AppMesh::VirtualNode.Spec``.
        :param virtual_node_name: ``AWS::AppMesh::VirtualNode.VirtualNodeName``.
        :param tags: ``AWS::AppMesh::VirtualNode.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualnode.html
        """
        self._values = {
            'mesh_name': mesh_name,
            'spec': spec,
            'virtual_node_name': virtual_node_name,
        }
        if tags is not None: self._values["tags"] = tags

    @property
    def mesh_name(self) -> str:
        """``AWS::AppMesh::VirtualNode.MeshName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualnode.html#cfn-appmesh-virtualnode-meshname
        """
        return self._values.get('mesh_name')

    @property
    def spec(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnVirtualNode.VirtualNodeSpecProperty"]:
        """``AWS::AppMesh::VirtualNode.Spec``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualnode.html#cfn-appmesh-virtualnode-spec
        """
        return self._values.get('spec')

    @property
    def virtual_node_name(self) -> str:
        """``AWS::AppMesh::VirtualNode.VirtualNodeName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualnode.html#cfn-appmesh-virtualnode-virtualnodename
        """
        return self._values.get('virtual_node_name')

    @property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        """``AWS::AppMesh::VirtualNode.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualnode.html#cfn-appmesh-virtualnode-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnVirtualNodeProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnVirtualRouter(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-appmesh.CfnVirtualRouter"):
    """A CloudFormation ``AWS::AppMesh::VirtualRouter``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualrouter.html
    cloudformationResource:
    :cloudformationResource:: AWS::AppMesh::VirtualRouter
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, mesh_name: str, spec: typing.Union[aws_cdk.core.IResolvable, "VirtualRouterSpecProperty"], virtual_router_name: str, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::AppMesh::VirtualRouter``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param mesh_name: ``AWS::AppMesh::VirtualRouter.MeshName``.
        :param spec: ``AWS::AppMesh::VirtualRouter.Spec``.
        :param virtual_router_name: ``AWS::AppMesh::VirtualRouter.VirtualRouterName``.
        :param tags: ``AWS::AppMesh::VirtualRouter.Tags``.
        """
        props = CfnVirtualRouterProps(mesh_name=mesh_name, spec=spec, virtual_router_name=virtual_router_name, tags=tags)

        jsii.create(CfnVirtualRouter, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        :param props: -
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class."""
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Arn
        """
        return jsii.get(self, "attrArn")

    @property
    @jsii.member(jsii_name="attrMeshName")
    def attr_mesh_name(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: MeshName
        """
        return jsii.get(self, "attrMeshName")

    @property
    @jsii.member(jsii_name="attrUid")
    def attr_uid(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Uid
        """
        return jsii.get(self, "attrUid")

    @property
    @jsii.member(jsii_name="attrVirtualRouterName")
    def attr_virtual_router_name(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: VirtualRouterName
        """
        return jsii.get(self, "attrVirtualRouterName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::AppMesh::VirtualRouter.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualrouter.html#cfn-appmesh-virtualrouter-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="meshName")
    def mesh_name(self) -> str:
        """``AWS::AppMesh::VirtualRouter.MeshName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualrouter.html#cfn-appmesh-virtualrouter-meshname
        """
        return jsii.get(self, "meshName")

    @mesh_name.setter
    def mesh_name(self, value: str):
        return jsii.set(self, "meshName", value)

    @property
    @jsii.member(jsii_name="spec")
    def spec(self) -> typing.Union[aws_cdk.core.IResolvable, "VirtualRouterSpecProperty"]:
        """``AWS::AppMesh::VirtualRouter.Spec``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualrouter.html#cfn-appmesh-virtualrouter-spec
        """
        return jsii.get(self, "spec")

    @spec.setter
    def spec(self, value: typing.Union[aws_cdk.core.IResolvable, "VirtualRouterSpecProperty"]):
        return jsii.set(self, "spec", value)

    @property
    @jsii.member(jsii_name="virtualRouterName")
    def virtual_router_name(self) -> str:
        """``AWS::AppMesh::VirtualRouter.VirtualRouterName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualrouter.html#cfn-appmesh-virtualrouter-virtualroutername
        """
        return jsii.get(self, "virtualRouterName")

    @virtual_router_name.setter
    def virtual_router_name(self, value: str):
        return jsii.set(self, "virtualRouterName", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualRouter.PortMappingProperty", jsii_struct_bases=[], name_mapping={'port': 'port', 'protocol': 'protocol'})
    class PortMappingProperty():
        def __init__(self, *, port: jsii.Number, protocol: str):
            """
            :param port: ``CfnVirtualRouter.PortMappingProperty.Port``.
            :param protocol: ``CfnVirtualRouter.PortMappingProperty.Protocol``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualrouter-portmapping.html
            """
            self._values = {
                'port': port,
                'protocol': protocol,
            }

        @property
        def port(self) -> jsii.Number:
            """``CfnVirtualRouter.PortMappingProperty.Port``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualrouter-portmapping.html#cfn-appmesh-virtualrouter-portmapping-port
            """
            return self._values.get('port')

        @property
        def protocol(self) -> str:
            """``CfnVirtualRouter.PortMappingProperty.Protocol``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualrouter-portmapping.html#cfn-appmesh-virtualrouter-portmapping-protocol
            """
            return self._values.get('protocol')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'PortMappingProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualRouter.VirtualRouterListenerProperty", jsii_struct_bases=[], name_mapping={'port_mapping': 'portMapping'})
    class VirtualRouterListenerProperty():
        def __init__(self, *, port_mapping: typing.Union[aws_cdk.core.IResolvable, "CfnVirtualRouter.PortMappingProperty"]):
            """
            :param port_mapping: ``CfnVirtualRouter.VirtualRouterListenerProperty.PortMapping``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualrouter-virtualrouterlistener.html
            """
            self._values = {
                'port_mapping': port_mapping,
            }

        @property
        def port_mapping(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnVirtualRouter.PortMappingProperty"]:
            """``CfnVirtualRouter.VirtualRouterListenerProperty.PortMapping``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualrouter-virtualrouterlistener.html#cfn-appmesh-virtualrouter-virtualrouterlistener-portmapping
            """
            return self._values.get('port_mapping')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'VirtualRouterListenerProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualRouter.VirtualRouterSpecProperty", jsii_struct_bases=[], name_mapping={'listeners': 'listeners'})
    class VirtualRouterSpecProperty():
        def __init__(self, *, listeners: typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnVirtualRouter.VirtualRouterListenerProperty"]]]):
            """
            :param listeners: ``CfnVirtualRouter.VirtualRouterSpecProperty.Listeners``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualrouter-virtualrouterspec.html
            """
            self._values = {
                'listeners': listeners,
            }

        @property
        def listeners(self) -> typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnVirtualRouter.VirtualRouterListenerProperty"]]]:
            """``CfnVirtualRouter.VirtualRouterSpecProperty.Listeners``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualrouter-virtualrouterspec.html#cfn-appmesh-virtualrouter-virtualrouterspec-listeners
            """
            return self._values.get('listeners')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'VirtualRouterSpecProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualRouterProps", jsii_struct_bases=[], name_mapping={'mesh_name': 'meshName', 'spec': 'spec', 'virtual_router_name': 'virtualRouterName', 'tags': 'tags'})
class CfnVirtualRouterProps():
    def __init__(self, *, mesh_name: str, spec: typing.Union[aws_cdk.core.IResolvable, "CfnVirtualRouter.VirtualRouterSpecProperty"], virtual_router_name: str, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None):
        """Properties for defining a ``AWS::AppMesh::VirtualRouter``.

        :param mesh_name: ``AWS::AppMesh::VirtualRouter.MeshName``.
        :param spec: ``AWS::AppMesh::VirtualRouter.Spec``.
        :param virtual_router_name: ``AWS::AppMesh::VirtualRouter.VirtualRouterName``.
        :param tags: ``AWS::AppMesh::VirtualRouter.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualrouter.html
        """
        self._values = {
            'mesh_name': mesh_name,
            'spec': spec,
            'virtual_router_name': virtual_router_name,
        }
        if tags is not None: self._values["tags"] = tags

    @property
    def mesh_name(self) -> str:
        """``AWS::AppMesh::VirtualRouter.MeshName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualrouter.html#cfn-appmesh-virtualrouter-meshname
        """
        return self._values.get('mesh_name')

    @property
    def spec(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnVirtualRouter.VirtualRouterSpecProperty"]:
        """``AWS::AppMesh::VirtualRouter.Spec``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualrouter.html#cfn-appmesh-virtualrouter-spec
        """
        return self._values.get('spec')

    @property
    def virtual_router_name(self) -> str:
        """``AWS::AppMesh::VirtualRouter.VirtualRouterName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualrouter.html#cfn-appmesh-virtualrouter-virtualroutername
        """
        return self._values.get('virtual_router_name')

    @property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        """``AWS::AppMesh::VirtualRouter.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualrouter.html#cfn-appmesh-virtualrouter-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnVirtualRouterProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


class CfnVirtualService(aws_cdk.core.CfnResource, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-appmesh.CfnVirtualService"):
    """A CloudFormation ``AWS::AppMesh::VirtualService``.

    see
    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualservice.html
    cloudformationResource:
    :cloudformationResource:: AWS::AppMesh::VirtualService
    """
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, mesh_name: str, spec: typing.Union[aws_cdk.core.IResolvable, "VirtualServiceSpecProperty"], virtual_service_name: str, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None) -> None:
        """Create a new ``AWS::AppMesh::VirtualService``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param props: - resource properties.
        :param mesh_name: ``AWS::AppMesh::VirtualService.MeshName``.
        :param spec: ``AWS::AppMesh::VirtualService.Spec``.
        :param virtual_service_name: ``AWS::AppMesh::VirtualService.VirtualServiceName``.
        :param tags: ``AWS::AppMesh::VirtualService.Tags``.
        """
        props = CfnVirtualServiceProps(mesh_name=mesh_name, spec=spec, virtual_service_name=virtual_service_name, tags=tags)

        jsii.create(CfnVirtualService, self, [scope, id, props])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(self, props: typing.Mapping[str,typing.Any]) -> typing.Mapping[str,typing.Any]:
        """
        :param props: -
        """
        return jsii.invoke(self, "renderProperties", [props])

    @classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> str:
        """The CloudFormation resource type name for this resource class."""
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @property
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Arn
        """
        return jsii.get(self, "attrArn")

    @property
    @jsii.member(jsii_name="attrMeshName")
    def attr_mesh_name(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: MeshName
        """
        return jsii.get(self, "attrMeshName")

    @property
    @jsii.member(jsii_name="attrUid")
    def attr_uid(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: Uid
        """
        return jsii.get(self, "attrUid")

    @property
    @jsii.member(jsii_name="attrVirtualServiceName")
    def attr_virtual_service_name(self) -> str:
        """
        cloudformationAttribute:
        :cloudformationAttribute:: VirtualServiceName
        """
        return jsii.get(self, "attrVirtualServiceName")

    @property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[str,typing.Any]:
        return jsii.get(self, "cfnProperties")

    @property
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::AppMesh::VirtualService.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualservice.html#cfn-appmesh-virtualservice-tags
        """
        return jsii.get(self, "tags")

    @property
    @jsii.member(jsii_name="meshName")
    def mesh_name(self) -> str:
        """``AWS::AppMesh::VirtualService.MeshName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualservice.html#cfn-appmesh-virtualservice-meshname
        """
        return jsii.get(self, "meshName")

    @mesh_name.setter
    def mesh_name(self, value: str):
        return jsii.set(self, "meshName", value)

    @property
    @jsii.member(jsii_name="spec")
    def spec(self) -> typing.Union[aws_cdk.core.IResolvable, "VirtualServiceSpecProperty"]:
        """``AWS::AppMesh::VirtualService.Spec``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualservice.html#cfn-appmesh-virtualservice-spec
        """
        return jsii.get(self, "spec")

    @spec.setter
    def spec(self, value: typing.Union[aws_cdk.core.IResolvable, "VirtualServiceSpecProperty"]):
        return jsii.set(self, "spec", value)

    @property
    @jsii.member(jsii_name="virtualServiceName")
    def virtual_service_name(self) -> str:
        """``AWS::AppMesh::VirtualService.VirtualServiceName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualservice.html#cfn-appmesh-virtualservice-virtualservicename
        """
        return jsii.get(self, "virtualServiceName")

    @virtual_service_name.setter
    def virtual_service_name(self, value: str):
        return jsii.set(self, "virtualServiceName", value)

    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualService.VirtualNodeServiceProviderProperty", jsii_struct_bases=[], name_mapping={'virtual_node_name': 'virtualNodeName'})
    class VirtualNodeServiceProviderProperty():
        def __init__(self, *, virtual_node_name: str):
            """
            :param virtual_node_name: ``CfnVirtualService.VirtualNodeServiceProviderProperty.VirtualNodeName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualservice-virtualnodeserviceprovider.html
            """
            self._values = {
                'virtual_node_name': virtual_node_name,
            }

        @property
        def virtual_node_name(self) -> str:
            """``CfnVirtualService.VirtualNodeServiceProviderProperty.VirtualNodeName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualservice-virtualnodeserviceprovider.html#cfn-appmesh-virtualservice-virtualnodeserviceprovider-virtualnodename
            """
            return self._values.get('virtual_node_name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'VirtualNodeServiceProviderProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualService.VirtualRouterServiceProviderProperty", jsii_struct_bases=[], name_mapping={'virtual_router_name': 'virtualRouterName'})
    class VirtualRouterServiceProviderProperty():
        def __init__(self, *, virtual_router_name: str):
            """
            :param virtual_router_name: ``CfnVirtualService.VirtualRouterServiceProviderProperty.VirtualRouterName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualservice-virtualrouterserviceprovider.html
            """
            self._values = {
                'virtual_router_name': virtual_router_name,
            }

        @property
        def virtual_router_name(self) -> str:
            """``CfnVirtualService.VirtualRouterServiceProviderProperty.VirtualRouterName``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualservice-virtualrouterserviceprovider.html#cfn-appmesh-virtualservice-virtualrouterserviceprovider-virtualroutername
            """
            return self._values.get('virtual_router_name')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'VirtualRouterServiceProviderProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualService.VirtualServiceProviderProperty", jsii_struct_bases=[], name_mapping={'virtual_node': 'virtualNode', 'virtual_router': 'virtualRouter'})
    class VirtualServiceProviderProperty():
        def __init__(self, *, virtual_node: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualService.VirtualNodeServiceProviderProperty"]]]=None, virtual_router: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualService.VirtualRouterServiceProviderProperty"]]]=None):
            """
            :param virtual_node: ``CfnVirtualService.VirtualServiceProviderProperty.VirtualNode``.
            :param virtual_router: ``CfnVirtualService.VirtualServiceProviderProperty.VirtualRouter``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualservice-virtualserviceprovider.html
            """
            self._values = {
            }
            if virtual_node is not None: self._values["virtual_node"] = virtual_node
            if virtual_router is not None: self._values["virtual_router"] = virtual_router

        @property
        def virtual_node(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualService.VirtualNodeServiceProviderProperty"]]]:
            """``CfnVirtualService.VirtualServiceProviderProperty.VirtualNode``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualservice-virtualserviceprovider.html#cfn-appmesh-virtualservice-virtualserviceprovider-virtualnode
            """
            return self._values.get('virtual_node')

        @property
        def virtual_router(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualService.VirtualRouterServiceProviderProperty"]]]:
            """``CfnVirtualService.VirtualServiceProviderProperty.VirtualRouter``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualservice-virtualserviceprovider.html#cfn-appmesh-virtualservice-virtualserviceprovider-virtualrouter
            """
            return self._values.get('virtual_router')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'VirtualServiceProviderProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


    @jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualService.VirtualServiceSpecProperty", jsii_struct_bases=[], name_mapping={'provider': 'provider'})
    class VirtualServiceSpecProperty():
        def __init__(self, *, provider: typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualService.VirtualServiceProviderProperty"]]]=None):
            """
            :param provider: ``CfnVirtualService.VirtualServiceSpecProperty.Provider``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualservice-virtualservicespec.html
            """
            self._values = {
            }
            if provider is not None: self._values["provider"] = provider

        @property
        def provider(self) -> typing.Optional[typing.Union[typing.Optional[aws_cdk.core.IResolvable], typing.Optional["CfnVirtualService.VirtualServiceProviderProperty"]]]:
            """``CfnVirtualService.VirtualServiceSpecProperty.Provider``.

            see
            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appmesh-virtualservice-virtualservicespec.html#cfn-appmesh-virtualservice-virtualservicespec-provider
            """
            return self._values.get('provider')

        def __eq__(self, rhs) -> bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs) -> bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return 'VirtualServiceSpecProperty(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())



@jsii.data_type(jsii_type="@aws-cdk/aws-appmesh.CfnVirtualServiceProps", jsii_struct_bases=[], name_mapping={'mesh_name': 'meshName', 'spec': 'spec', 'virtual_service_name': 'virtualServiceName', 'tags': 'tags'})
class CfnVirtualServiceProps():
    def __init__(self, *, mesh_name: str, spec: typing.Union[aws_cdk.core.IResolvable, "CfnVirtualService.VirtualServiceSpecProperty"], virtual_service_name: str, tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]]=None):
        """Properties for defining a ``AWS::AppMesh::VirtualService``.

        :param mesh_name: ``AWS::AppMesh::VirtualService.MeshName``.
        :param spec: ``AWS::AppMesh::VirtualService.Spec``.
        :param virtual_service_name: ``AWS::AppMesh::VirtualService.VirtualServiceName``.
        :param tags: ``AWS::AppMesh::VirtualService.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualservice.html
        """
        self._values = {
            'mesh_name': mesh_name,
            'spec': spec,
            'virtual_service_name': virtual_service_name,
        }
        if tags is not None: self._values["tags"] = tags

    @property
    def mesh_name(self) -> str:
        """``AWS::AppMesh::VirtualService.MeshName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualservice.html#cfn-appmesh-virtualservice-meshname
        """
        return self._values.get('mesh_name')

    @property
    def spec(self) -> typing.Union[aws_cdk.core.IResolvable, "CfnVirtualService.VirtualServiceSpecProperty"]:
        """``AWS::AppMesh::VirtualService.Spec``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualservice.html#cfn-appmesh-virtualservice-spec
        """
        return self._values.get('spec')

    @property
    def virtual_service_name(self) -> str:
        """``AWS::AppMesh::VirtualService.VirtualServiceName``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualservice.html#cfn-appmesh-virtualservice-virtualservicename
        """
        return self._values.get('virtual_service_name')

    @property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        """``AWS::AppMesh::VirtualService.Tags``.

        see
        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-appmesh-virtualservice.html#cfn-appmesh-virtualservice-tags
        """
        return self._values.get('tags')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'CfnVirtualServiceProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["CfnMesh", "CfnMeshProps", "CfnRoute", "CfnRouteProps", "CfnVirtualNode", "CfnVirtualNodeProps", "CfnVirtualRouter", "CfnVirtualRouterProps", "CfnVirtualService", "CfnVirtualServiceProps", "__jsii_assembly__"]

publication.publish()

# coding=utf-8
# Licensed Materials - Property of IBM
# Copyright IBM Corp. 2019

import os
from tempfile import mkstemp
import streamsx.spl.op
import streamsx.spl.types
from streamsx.topology.schema import CommonSchema, StreamSchema
from streamsx.spl.types import rstring
import datetime
from streamsx.toolkits import download_toolkit

_TOOLKIT_NAME = 'com.ibm.streamsx.jms'



#ProducerInputSchema = StreamSchema('tuple<>')
#"""Input schema for the data that is put onto the JMS broker.
#"""

#ProducerErrorOutputSchema = StreamSchema('tuple<tuple<> inputTuple, rstring errMsg>')
#"""Output schema for optional error output port.
#"""

#ConsumerOutputSchema = StreamSchema('tuple<>')
#"""Output schema for the data that is received from the JMS broker.
#"""

ConsumerErrorOutputSchema = StreamSchema('tuple<rstring errMsg>')
"""Output schema for optional error output port.
"""



def _add_connection_document_file(topology, connectionDocument):
    if os.path.isfile(connectionDocument):
        return topology.add_file_dependency(connectionDocument, 'etc')
    else:
        raise ValueError("Parameter connectionDocument=" + connectionDocument + " does not point to an existing file.")



def download_toolkit(url=None, target_dir=None):
    r"""Downloads the latest JMS toolkit from GitHub.

    Example for updating the JMS toolkit for your topology with the latest toolkit from GitHub::

        import streamsx.jms as jms
        # download JMS toolkit from GitHub
        jms_toolkit_location = jms.download_toolkit()
        # add the toolkit to topology
        streamsx.spl.toolkit.add_toolkit(topology, jms_toolkit_location)

    Example for updating the topology with a specific version of the JMS toolkit using a URL::

        import streamsx.jms as jms
        url122 = 'https://github.com/IBMStreams/streamsx.jms/releases/download/v1.2.2/streamsx.jms.toolkits-1.2.2-20190826-1516.tgz'
        jms_toolkit_location = jms.download_toolkit(url=url122)
        streamsx.spl.toolkit.add_toolkit(topology, jms_toolkit_location)

    Args:
        url(str): Link to toolkit archive (\*.tgz) to be downloaded. Use this parameter to download a specific version of the toolkit.
        target_dir(str): the directory where the toolkit is unpacked to. If a relative path is given,
            the path is appended to the system temporary directory, for example to /tmp on Unix/Linux systems.
            If target_dir is ``None`` a location relative to the system temporary directory is chosen.

    Returns:
        str: the location of the downloaded Avro toolkit

    .. note:: This function requires an outgoing Internet connection
    .. versionadded:: 0.1
    """
    _toolkit_location = streamsx.toolkits.download_toolkit (toolkit_name=_TOOLKIT_NAME, url=url, target_dir=target_dir)
    return _toolkit_location



def consume(topology, schemas, connection, access, connectionDocument=None, name=None):
    """Consume messages provided by a JMS broker.

    Args:
        topology: The Streams topology.
        schemas: The schemas of the output ports. There is the mandatory data output port containing the data of the received messages and an optional error output port. The latter expecting something like the ConsumerErrorOutputSchema.
        
        connection(str): This mandatory parameter identifies the name of the connection specification that contains an JMS element.
        access(str): This mandatory parameter identifies the access specification name.
        connectionDocument(str): Specifies the path name to the file that contains the connection and access specifications, which are identified by the **connection** and **access** parameters. If this parameter is not specified, the operator uses the file that is in the default location `./etc/connections.xml`.
        
        appConfigName(str): Specifies the name of application configuration that stores client credential information, the credential specified via application configuration overrides the one specified in connections file.
        userPropName(str): Specifies the property name of user name in the application configuration. If the appConfigName parameter is specified and the userPropName parameter is not set, a compile time error occurs.
        passwordPropName(str): Specifies the property name of the password in the application configuration. If the appConfigName parameter is specified and the passwordPropName parameter is not set, a compile time error occurs.

        sslConnection(bool): Specifies whether the operator should attempt to connect using SSL. If this parameter is specified, then the *keyStore* and *trustStore* parameters must also be specified.
        sslDebug(bool): Enable SSL/TLS protocol debugging. If enabled all protocol data and information is logged to the console.
        keyStore(str): Specifies the path to the keyStore. If a relative path is specified, the path is relative to the application directory.
        keyStorePassword(str): Specifies the password for the keyStore.
        trustStore(str): Specifies the path to the trustStore. If a relative path is specified, the path is relative to the application directory.
        trustStorePassword(str): Specifies the password for the trustStore.

        jmsDestinationOutAttrName(str): Output attribute on output data stream to assign JMSDestination to, the specified attribute in output stream must be of type rstring.
        jmsDeliveryModeOutAttrName(str): Output attribute on output data stream to assign JMSDeliveryMode to, the specified attribute in output stream must be of type int32.
        jmsExpirationOutAttrName(str): Output attribute on output data stream to assign JMSExpiration to, the specified attribute in output stream must be of type int64.
        jmsPriorityOutAttrName(str): Output attribute on output data stream to assign JMSPriority to, the specified attribute in output stream must be of type int32.
        jmsMessageIDOutAttrName(str): Output attribute on output data stream to assign JMSMessageID to, the specified attribute in output stream must be of type rstring.
        jmsTimestampOutAttrName(str): Output attribute on output data stream to assign JMSTimestamp to, the specified attribute in output stream must be of type int64.
        jmsCorrelationIDOutAttrName(str): Output attribute on output data stream to assign JMSCorrelationID to, the specified attribute in output stream must be of type rstring.
        jmsReplyToOutAttrName(str): Output attribute on output data stream to assign JMSReplyTo to, the specified attribute in output stream must be of type rstring.
        jmsTypeOutAttrName(str): Output attribute on output data stream to assign JMSType to, the specified attribute in output stream must be of type rstring.
        jmsRedeliveredOutAttrName(str): Output attribute on output data stream to assign JMSRedelivered to, the specified attribute in output stream must be of type boolean.
        jmsHeaderProperties(str): Specifies the mapping between JMS Header property values and Streams tuple attributes. The format of the mapping is: propertyName1/streamsAttributeName1/typeSpecifier1, propertyName2/streamsAttributeName2/typeSpecifier2,...
        jmsHeaderPropertiesOutAttrName(str): Output attribute on output data stream to assign to the map containing all received properties. The specified attribute in output stream must be of type map<ustring,ustring>.
        
        messageSelector(str): This optional parameter is used as JMS Message Selector.
        triggerCount(int): Specifies how many messages are submitted before the JMSSource operator starts to drain the pipeline and establish a consistent state. This parameter must be greater than zero and must be set if the JMSSource operator is the start operator of an operatorDriven consistent region.
        codepage(str): Specifies the code page of the target system that is used to convert ustring for a Bytes message type.
        reconnectionPolicy(str): Specifies the reconnection policy. Valid values are `NoRetry`, `InfiniteRetry`, and `BoundedRetry`. If the parameter is not specified, the reconnection policy is set to `BoundedRetry` with a **reconnectionBound** of `5` and a **period** of 60 seconds.
        reconnectionBound(int): Specifies the number of successive connections that are attempted for an operator. You can use this parameter only when the **reconnectionPolicy** parameter is specified and set to `BoundedRetry`, otherwise a run time error occurs. If the **reconnectionBound** parameter is specified and the **reconnectionPolicy** parameter is not set, a compile time error occurs. The default value for the **reconnectionBound** parameter is `5`.
        period(double): Specifies the time period in seconds the operator waits before it tries to reconnect. You can use this parameter only when the **reconnectionPolicy** parameter is specified, otherwise a compile time error occurs. The default value for the **period** parameter is `60`.

        vmArg(str): Contains arguments to pass to the Java VM.
        
        name(str): Source name in the Streams context, defaults to a generated name.

    Returns:
        Output Stream containing the data of the received messages.
        Optional Error Output Stream with schema :py:const:`~streamsx.jms.ConsumerErrorOutputSchema`.
    """
    
    # Plausible check if SSL parameters are set
    if (sslConnection is not None and (keyStore is None or keyStorePassword is None or trustStore is None or trustStorePassword is None)):
        raise ValueError("If sslConnection is enabled, parameters 'keyStore', 'keyStorePassword', 'trustStore', and 'trustStorePassword' must be set, too.")

    _op = _JMSSource(topology, schemas=schemas, connection=connection, access=access, connectionDocument=connectionDocument, name=name)
    
    if connectionDocument is not None:
        _op.params['connectionDocument'] = _op.expression('getThisToolkitDir() + "/' + _add_connection_document_file(topology, connectionDocument) + '"')

    return _op.outputs



def produce(stream, schema, connection, access, connectionDocument=None, name=None):
    """Send messages to a JMS broker.

    Args:
        stream: The input stream containing the data to send to the JMS broker
        schema: The schema of the optional error output port.
        
        connection(str): This mandatory parameter identifies the name of the connection specification that contains an JMS element.
        access(str): This mandatory parameter identifies the access specification name.
        connectionDocument(str): Specifies the path name to the file that contains the connection and access specifications, which are identified by the **connection** and **access** parameters. If this parameter is not specified, the operator uses the file that is in the default location `./etc/connections.xml`.

        appConfigName(str): Specifies the name of application configuration that stores client credential information, the credential specified via application configuration overrides the one specified in connections file.
        userPropName(str): Specifies the property name of user name in the application configuration. If the appConfigName parameter is specified and the userPropName parameter is not set, a compile time error occurs.
        passwordPropName(str): Specifies the property name of the password in the application configuration. If the appConfigName parameter is specified and the passwordPropName parameter is not set, a compile time error occurs.
        
        sslConnection(bool): Specifies whether the operator should attempt to connect using SSL. If this parameter is specified, then the *keyStore* and *trustStore* parameters must also be specified.
        sslDebug(bool): Enable SSL/TLS protocol debugging. If enabled all protocol data and information is logged to the console.
        keyStore(str): Specifies the path to the keyStore. If a relative path is specified, the path is relative to the application directory.
        keyStorePassword(str): Specifies the password for the keyStore.
        trustStore(str): Specifies the path to the trustStore. If a relative path is specified, the path is relative to the application directory.
        trustStorePassword(str): Specifies the password for the trustStore.
        
        jmsHeaderProperties(str): Specifies the mapping between JMS Header property values and Streams tuple attributes. The format of the mapping is: propertyName1/streamsAttributeName1/typeSpecifier1, propertyName2/streamsAttributeName2/typeSpecifier2,...

        codepage(str): Specifies the code page of the target system that is used to convert ustring for a Bytes message type.
        reconnectionPolicy(str): Specifies the reconnection policy. Valid values are `NoRetry`, `InfiniteRetry`, and `BoundedRetry`. If the parameter is not specified, the reconnection policy is set to `BoundedRetry` with a **reconnectionBound** of `5` and a **period** of 60 seconds.
        reconnectionBound(int): Specifies the number of successive connections that are attempted for an operator. You can use this parameter only when the **reconnectionPolicy** parameter is specified and set to `BoundedRetry`, otherwise a run time error occurs. If the **reconnectionBound** parameter is specified and the **reconnectionPolicy** parameter is not set, a compile time error occurs. The default value for the **reconnectionBound** parameter is `5`.
        period(double): Specifies the time period in seconds the operator waits before it tries to reconnect. You can use this parameter only when the **reconnectionPolicy** parameter is specified, otherwise a compile time error occurs. The default value for the **period** parameter is `60`.
        
        consistentRegionQueueName(str): This is a required parameter if this operator is participating in a consistent region. This parameter specifies the queue to be used to store consistent region specific information and the operator will perform a JNDI lookup with the queue name specified at initialization state. The queue name specified must also exist on the same messaging server where this operator is establishing the connection.
        
        maxMessageSendRetries(int): Specifies the number of successive retries that are attempted for a message if a failure occurs when the message is sent. The default value is zero; no retries are attempted.
        messageSendRetryDelay(long): Specifies the time in milliseconds to wait before the next delivery attempt. If the **maxMessageSendRetries** is specified, you must also specify a value for this parameter.

        vmArg(str): Contains arguments to pass to the Java VM.
        
        name(str): Source name in the Streams context, defaults to a generated name.

    Returns:
        Optional output Stream with schema ???
    """
    
    # Plausible check if SSL parameters are set
    if (sslConnection is not None and (keyStore is None or keyStorePassword is None or trustStore is None or trustStorePassword is None)):
        raise ValueError("If sslConnection is enabled, parameters 'keyStore', 'keyStorePassword', 'trustStore', and 'trustStorePassword' must be set, too.")

    _op = _JMSSink(stream, schema, connection=connection, access=access, connectionDocument=connectionDocument, name=name)

    if connectionDocument is not None:
        _op.params['connectionDocument'] = _op.expression('getThisToolkitDir() + "/' + _add_connection_document_file(topology, connectionDocument) + '"')

    return _op.outputs[0]



class _JMSSource(streamsx.spl.op.Invoke):
    def __init__(self, topology, schemas, connection=None, access=None, connectionDocument=None,
                 appConfigName=None, userPropName=None, passwordPropName=None,
                 sslConnection=None, sslDebug=None, keyStore=None, keyStorePassword=None, trustStore=None, trustStorePassword=None,
                 jmsDestinationOutAttrName=None, jmsDeliveryModeOutAttrName=None, jmsExpirationOutAttrName=None, jmsPriorityOutAttrName=None,
                 jmsMessageIDOutAttrName=None, jmsTimestampOutAttrName=None, jmsCorrelationIDOutAttrName=None, jmsReplyToOutAttrName=None,
                 jmsTypeOutAttrName=None, jmsRedeliveredOutAttrName=None, jmsHeaderProperties=None, jmsHeaderPropertiesOutAttrName=None,
                 messageSelector=None, triggerCount=None, codepage=None, reconnectionPolicy=None, reconnectionBound=None, period=None,
                 vmArg=None, name=None):

        kind="com.ibm.streamsx.jms::JMSSource"

        params = dict()
        
        if connection is not None:
            params['connection'] = connection
        if connection is not None:
            params['access'] = access
        if connectionDocument is not None:
            params['connectionDocument'] = connectionDocument
        
        if appConfigName is not None:
            params['appConfigName'] = appConfigName
        if userPropName is not None:
            params['userPropName'] = userPropName
        if passwordPropName is not None:
            params['passwordPropName'] = passwordPropName
            
        if sslConnection is not None:
            params['sslConnection'] = sslConnection
        if sslDebug is not None:
            params['sslDebug'] = sslDebug
        if keyStore is not None:
            params['keyStore'] = keyStore
        if keyStorePassword is not None:
            params['keyStorePassword'] = keyStorePassword
        if trustStore is not None:
            params['trustStore'] = trustStore
        if trustStorePassword is not None:
            params['trustStorePassword'] = trustStorePassword
            
        if jmsDestinationOutAttrName is not None:
            params['jmsDestinationOutAttrName'] = jmsDestinationOutAttrName
        if jmsDeliveryModeOutAttrName is not None:
            params['jmsDeliveryModeOutAttrName'] = jmsDeliveryModeOutAttrName
        if jmsExpirationOutAttrName is not None:
            params['jmsExpirationOutAttrName'] = jmsExpirationOutAttrName
        if jmsPriorityOutAttrName is not None:
            params['jmsPriorityOutAttrName'] = jmsPriorityOutAttrName
        if jmsMessageIDOutAttrName is not None:
            params['jmsMessageIDOutAttrName'] = jmsMessageIDOutAttrName
        if jmsTimestampOutAttrName is not None:
            params['jmsTimestampOutAttrName'] = jmsTimestampOutAttrName
        if jmsCorrelationIDOutAttrName is not None:
            params['jmsCorrelationIDOutAttrName'] = jmsCorrelationIDOutAttrName
        if jmsReplyToOutAttrName is not None:
            params['jmsReplyToOutAttrName'] = jmsReplyToOutAttrName
        if jmsTypeOutAttrName is not None:
            params['jmsTypeOutAttrName'] = jmsTypeOutAttrName
        if jmsRedeliveredOutAttrName is not None:
            params['jmsRedeliveredOutAttrName'] = jmsRedeliveredOutAttrName
        if jmsHeaderProperties is not None:
            params['jmsHeaderProperties'] = jmsHeaderProperties
        if jmsHeaderPropertiesOutAttrName is not None:
            params['jmsHeaderPropertiesOutAttrName'] = jmsHeaderPropertiesOutAttrName
            
        if messageSelector is not None:
            params['messageSelector'] = messageSelector 
        if triggerCount is not None:
            params['triggerCount'] = triggerCount
        if codepage is not None:
            params['codepage'] = codepage
        if reconnectionPolicy is not None:
            params['reconnectionPolicy'] = reconnectionPolicy
        if reconnectionBound is not None:
            params['reconnectionBound'] = reconnectionBound
        if period is not None:
            params['period'] = period

        if vmArg is not None:
            params['vmArg'] = vmArg

        super(_JMSSource, self).__init__(topology, kind, inputs=None, schemas=schemas, params=params, name=name)



class _JMSSink(streamsx.spl.op.Invoke):
    def __init__(self, stream, schema=None, connection=None, access=None, connectionDocument=None,
                 appConfigName=None, userPropName=None, passwordPropName=None,
                 sslConnection=None, sslDebug=None, keyStore=None, keyStorePassword=None, trustStore=None, trustStorePassword=None,
                 jmsHeaderProperties=None, codepage=None, reconnectionPolicy=None, reconnectionBound=None, period=None,
                 consistentRegionQueueName=None, maxMessageSendRetries=None, messageSendRetryDelay=None,
                 vmArg=None, name=None):

        topology = stream.topology
        kind="com.ibm.streamsx.jms::JMSSink"
        inputs=stream
        schemas=schema
        params = dict()

        if connection is not None:
            params['connection'] = connection
        if connection is not None:
            params['access'] = access
        if connectionDocument is not None:
            params['connectionDocument'] = connectionDocument

        if appConfigName is not None:
            params['appConfigName'] = appConfigName
        if userPropName is not None:
            params['userPropName'] = userPropName
        if passwordPropName is not None:
            params['passwordPropName'] = passwordPropName

        if sslConnection is not None:
            params['sslConnection'] = sslConnection
        if sslDebug is not None:
            params['sslDebug'] = sslDebug
        if keyStore is not None:
            params['keyStore'] = keyStore
        if keyStorePassword is not None:
            params['keyStorePassword'] = keyStorePassword
        if trustStore is not None:
            params['trustStore'] = trustStore
        if trustStorePassword is not None:
            params['trustStorePassword'] = trustStorePassword
        
        if jmsHeaderProperties is not None:
            params['jmsHeaderProperties'] = jmsHeaderProperties

        if codepage is not None:
            params['codepage'] = codepage
        if reconnectionPolicy is not None:
            params['reconnectionPolicy'] = reconnectionPolicy
        if reconnectionBound is not None:
            params['reconnectionBound'] = reconnectionBound
        if period is not None:
            params['period'] = period
            
        if consistentRegionQueueName is not None:
            params['consistentRegionQueueName'] = consistentRegionQueueName

        if maxMessageSendRetries is not None:
            params['maxMessageSendRetries'] = maxMessageSendRetries
        if messageSendRetryDelay is not None:
            params['messageSendRetryDelay'] = messageSendRetryDelay

        if vmArg is not None:
            params['vmArg'] = vmArg

        super(_JMSSink, self).__init__(topology, kind, inputs, schemas, params, name)


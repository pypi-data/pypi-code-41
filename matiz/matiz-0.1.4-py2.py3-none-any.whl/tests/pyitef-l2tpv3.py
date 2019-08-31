"""
  module: ietf-l2tpv3

      +--rw l2tpv3CtrlInstances
      |  +--rw l2tpv3CtrlInstance* [ctrlName]
      |     +-- rw ctrlName     string
      |     +-- rw hostName     string
      |     +-- rw routerID     uint16
      |     +-- rw rcvWinSize?      uint16
      |     +-- rw helloInterval?   uint16
      |     +-- rw digestType?      enum
      |     +-- rw authenNonce?     password
      +--rw l2tpv3TunnelInstances
   +--rw l2tpv3TunnelInstance* [tunnelName]
      +-- rw tunnelName    string
      +-- rw sourceIfName  if:interface-ref
      +-- rw sourceIP      inet:ip-address
      +-- rw destIP    inet:ip-address
      +-- rw tunnelType    enum
      |     +-- rw static:
      |     |   +-- rw localSessionId?      uint32
      |     |   +-- rw remoteSessionId?     uint32
      |     |   +-- rw localCookieAutoMode? enum
      |     |   |   +-- rw authNone:
      |     |   |   +-- rw authPlain:
      |     |   |   +-- rw localCookieLength enum
      |     |   |   +-- rw localHighCookie   hexBinary
      |     |   |   +-- rw localLowCookie    hexBinary
      |     |   |   +-- rw authCipher:
      |     |   |       +--rw localCookieCipher   password
      |     |   +-- rw remoteCookieAutoMode?      enum
      |     |       +-- rw authNone:
      |     |       +-- rw authPlain:
      |     |       +--rw remoteCookieLength enum
      |     |       +--rw remoteHighCookie   hexBinary
      |     |       +--rw remoteLowCookie    hexBinary
      |     |       +-- rw authCipher:
      |     |     +--rw remoteCookieCipher password
      |     +-- rw auto:
      |     +-- rw ctrlName      string
      |     +-- rw encapType     enum
      +-- ro sendPacket       uint64
      +-- ro sendByte         uint64
      +-- ro rcvPacket        uint64
      +-- ro receiveByte      uint64
      +-- ro recvDropPacket       uint64
      +-- ro cookieMisDropPacket  uint64
      +-- ro state        enum



"""
import dataclasses


@dataclasses.dataclass
class hexBinary:
    """This is a hexadecimal variable."""
    type_ = "string"
    length = "1..127"
    pattern = "0[xX][0-9a-fA-F]+"


def z_enum(*a):
    return a


@dataclasses.dataclass
class password:
    """This is a dedicated password variable."""
    type_ = "string"
    length = "1..127"


@dataclasses.dataclass
class l2tpv3CtrlInstance:
    """There could be multiple control instances, each of them is mapping to a tunnel instance."""
    key = "ctrlName"

    ctrlName = dict(
        type_="string",
        length="1..19",
        description="""The name of the control instance.""",
    )

    hostName = dict(
        type_="string",
        mandatory="true",
        description="The name of the host.",
    )
    routerID = dict(
        type_="uint16",
        mandatory="true",
        description="Router ID.",
    )
    rcvWinSize = dict(
        type_="uint16",
        description="Receiving window size.",
    )
    helloInterval = dict(
        type_="uint16",
        description="Hello interval time.",
    )
    digestType = dict(
        type_="enumeration",
        description="Digest algorithm selection.",
        enums=[
            z_enum("HMAC_MD5", "HMAC_MD5 algorithm."),
            z_enum("HMAC_SHA_1", "HMAC_SHA_1 algorithm."),
        ],
    )

    authenNonce = dict(
        type_='password',
        length="1..16",
        description="The authentication Nonce is in the password format.",
    )


class l2tpv3CtrlInstances:
    instances = list()
    """This is some general configuration of an l2tpv3 tunnel."""


"""

class l2tpv3TunnelInstance:
  description "In contrast to the above control instance,
           this configuration is regarding to the
           tunnel interface itself."

    list l2tpv3TunnelInstance:
      key "tunnelName"
      description "There could be multiple tunnel instance."

        leaf tunnelName:
            type_ = "string":
                length "1..19"

            description "The tunnel name."

        leaf sourceIfName:
    type_ = if:interface-ref
    description
    "Interface name as defined by ietf-interfaces"


        leaf sourceIP:
            type_ = inet:ip-address
            mandatory "true"
            description "Source IP address."

        leaf destIP:
            type_ = inet:ip-address
            mandatory "true"
            description "Destination IP address."

        leaf tnlType:
                  type_ = enumeration:
                    enum "static":
                      description "Static tunnel."

                    enum "auto":
                      description "Automatic IP address."


                mandatory "true"
                description "Tunnel type."

        choice tunnelType:
        mandatory "true"
        description "Each tunnel can be configured to only one type."
        case static:
            when "tnltype_ = = 'static'"
            leaf localSessionId:
                type_ = uint32:
                    range "1..4294967295"

                default "4294967295"
                description "Local session ID of the tunnel."

            leaf remoteSessionId:
                type_ = uint32:
                    range "1..4294967295"

                default "4294967295"
                description "Remote session ID of the tunnel."

            leaf localCookieAutoMode:
                type_ = enumeration:
                    enum "authNone":
                      description "No authentication."

                    enum "authPlain":
                      description "Plain text authentication."

                    enum "authCipher":
                      description "Ciper authentication."


                mandatory "true"
                description "Local cookie authentication mode."


        choice localCookieMode:
           default authNone
           description "Each tunnel can be configured to only one local cookie mode."

                case authNone:
                when "localCookieAutoMode = 'authNone'"


                case authPlain:
                when "localCookieAutoMode = 'authPlain'"
                    leaf localCookieLength:
                        type_ = enumeration:
                            enum "4":
                             description "4 byte cookie."

                            enum "8":
                             description "8 byte cookie."


                        default "4"
                        description "Local cookie length."

                    leaf localHighCookie:
                        type_ = "hexBinary":
                            length "3..6"

                        description "Local high cookie."

                    leaf localLowCookie:
                        type_ = "hexBinary":
                            length "3..6"

                        description "Local low cookie."

                case authCipher:
                when "localCookieAutoMode = 'authCipher'"
                    leaf localCookieCipher:
                        type_ = password:
                        length "1..8"

                        description "Local cookie cipher."


            leaf remoteCookieAutoMode:
                type_ = enumeration:
                    enum "authNone":
                      description "No authentication."

                    enum "authPlain":
                      description "Plain text authentication."

                    enum "authCipher":
                      description "Plain text authentication."

                mandatory "true"
                description "Remote Cookie AutoMode."

            choice remoteCookieMode:
                default authNone
                description "Choosing one remote cookie mode."
                case authNone:
        when "remoteCookieAutoMode = 'authNone'"

                case authPlain:
                when "remoteCookieAutoMode = 'authPlain'"
                    leaf remoteCookieLength:
                        type_ = enumeration:
                            enum "4":
                              description "Cookie length is 4 byte."

                            enum "8":
                              description "Cookie length is 4 byte."


                        default "4"
                        description "Remote Cookie length."

                    leaf remoteHighCookie:
                        type_ = "hexBinary":
                            length "3..6"

                        description "Remote high Cookie."

                    leaf remoteLowCookie:
                        type_ = "hexBinary":
                            length "3..6"

                        description "Remote low Cookie."


                case authCipher:
                when "remoteCookieAutoMode = 'authCipher'"
                    leaf remoteCookieCipher:
                        type_ = password:
                            length "1..8"

                        description "Remote Cookie cipher."

        case auto:
        when "tnltype_ = = 'auto'"
            leaf ctrlName:
                type_ = string:
                    length "1..19"

                mandatory "true"
                description "Relevant control instance name."

            leaf encapType:
                type_ = enumeration:
                    enum "HDLC":
                      description "HDLC encapsulation."

                    enum "Ethernet":
                      description "Ethernet encapsulation."

                    enum "VLAN":
                      description "VLAN encapsulation."

                    enum "ATM":
                      description "ATM encapsulation."


                mandatory "true"
                description "Encapsulation type."



        leaf sendPacket:
            type_ = "uint64"
            config "false"
            description "Sent packet count."

        leaf sendByte:
            type_ = "uint64"
            config "false"
            description "Sent byte count."

        leaf rcvPacket:
            type_ = "uint64"
            config "false"
            description "Received packet count."

        leaf receiveByte:
            type_ = "uint64"
            config "false"
            description "Received byte count."

        leaf recvDropPacket:
            type_ = "uint64"
            config "false"
            description "Drop packet count among the received packets."

        leaf cookieMisDropPacket:
            type_ = "uint64"
            config "false"
            description "Cookie mis-drop packet count."

        leaf state:
            type_ = enumeration:
            enum "down":
                value "0"
                description "down:"

            enum "up":
                value "1"
                description "up:"


            config "false"
            description "Tunnel running state."

"""

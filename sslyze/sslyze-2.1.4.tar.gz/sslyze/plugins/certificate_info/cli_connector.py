@classmethod
def get_title(cls) -> str:
    return "Certificate Information"


@classmethod
def get_cli_argument(cls) -> str:
    return "certinfo"


@classmethod
def get_available_commands(cls) -> List[Type[PluginScanCommand]]:
    return [CertificateInfoScanCommand]


@classmethod
def get_cli_option_group(cls) -> List[optparse.Option]:
    options = super().get_cli_option_group()

    # Add the special optional argument for this plugin's commands
    # They must match the names in the commands' contructor
    options.append(
        optparse.make_option(
            "--ca_file",
            help="Path to a local trust store file (with root certificates in PEM format) to verify the validity "
            "of the server(s) certificate's chain(s) against.",
            dest="ca_file",
        )
    )
    return options


class CertificateInfoScanResult(PluginScanResult):
    """The result of running a CertificateInfoScanCommand on a specific server.

    Any certificate available as an attribute is parsed using the cryptography module; documentation is available at
    https://cryptography.io/en/latest/x509/reference/#x-509-certificate-object

    Attributes:
        received_certificate_chain (List[cryptography.x509.Certificate]): The certificate chain sent by the server;
            index 0 is the leaf certificate.
        verified_certificate_chain: (Optional[List[cryptography.x509.Certificate]]): The verified certificate chain
            returned by OpenSSL for one of the trust stores packaged within SSLyze. Will be None if the validation
            failed with all of the available trust stores (Apple, Mozilla, etc.). This is essentially  a shortcut to
            path_validation_result_list[0].verified_certificate_chain.
        path_validation_result_list (List[PathValidationResult]): The result of validating the server's
            certificate chain using each trust store that is packaged with SSLyze (Mozilla, Apple, etc.).
            If for a given trust store, the validation was successful, the verified certificate chain built by OpenSSL
            can be retrieved from the PathValidationResult.
        path_validation_error_list (List[PathValidationError]):  The list of attempts at validating the server's
            certificate chain path that triggered an unexpected error.
        leaf_certificate_subject_matches_hostname (bool)
        leaf_certificate_is_ev (bool): True if the leaf certificate is Extended Validation according to Mozilla.
        leaf_certificate_has_must_staple_extension (bool)
        leaf_certificate_signed_certificate_timestamps_count (Optional[int]): The number of Signed Certificate
            Timestamps (SCTs) for Certificate Transparency embedded in the leaf certificate. None if the version of
            OpenSSL installed on the system is too old to be able to parse the SCT extension.
        received_chain_has_valid_order (bool)
        received_chain_contains_anchor_certificate (Optional[bool]): True if the server included the anchor/root
            certificate in the chain it sends back to clients. None if the verified chain could not be built.
        verified_chain_has_sha1_signature (Optional[bool]): True if any of the leaf or intermediate certificates are
            signed using the SHA-1 algorithm. None if the verified chain could not be built.
        verified_chain_has_legacy_symantec_anchor (Optional[bool]): True if the certificate chain contains a distrusted
            Symantec anchor
            (https://blog.qualys.com/ssllabs/2017/09/26/google-and-mozilla-deprecating-existing-symantec-certificates).
            None if the verified chain could not be built.
        ocsp_response (Optional[Dict[Text, Any]]): The OCSP response returned by the server. None if no response was
            sent by the server.
        ocsp_response_status (Optional[OcspResponseStatusEnum]): The status of the OCSP response returned by the server.
            None if no response was sent by the server.
        ocsp_response_is_trusted (Optional[bool]): True if the OCSP response is trusted using the Mozilla trust store.
            None if no OCSP response was sent by the server.

    """

    def __init__(
        self,
        server_info: ServerConnectivityInfo,
        scan_command: CertificateInfoScanCommand,
        received_certificate_chain: List[Certificate],
        path_validation_result_list: List[PathValidationResult],
        path_validation_error_list: List[PathValidationError],
        ocsp_response: Optional[OcspResponse],
    ) -> None:
        super().__init__(server_info, scan_command)

        self.received_certificate_chain = received_certificate_chain
        self.path_validation_result_list = path_validation_result_list
        self.path_validation_error_list = path_validation_error_list
        # We only keep the dictionary as an OcspResponse is not pickable
        self.ocsp_response = ocsp_response.as_dict() if ocsp_response else None

        # Sort the path_validation_result_list so the same successful_trust_store always get picked for a given server
        # because threading timings change the order of path_validation_result_list
        def sort_function(path_validation: PathValidationResult) -> str:
            return path_validation.trust_store.name.lower()

        # Find the first trust store that successfully validated the certificate chain
        trust_store_used_to_build_verified_chain = None
        self.verified_certificate_chain = None
        path_validation_result_list.sort(key=sort_function)
        for path_result in path_validation_result_list:
            if path_result.was_validation_successful:
                trust_store_used_to_build_verified_chain = path_result.trust_store
                self.verified_certificate_chain = path_result.verified_certificate_chain
                break

        # Analyze the certificate chain deployment
        analyzer = CertificateChainDeploymentAnalyzer(
            server_hostname=server_info.tls_server_name_indication,
            received_chain=self.received_certificate_chain,
            verified_chain=self.verified_certificate_chain,
            trust_store_used_to_build_verified_chain=trust_store_used_to_build_verified_chain,
            received_ocsp_response=ocsp_response,
        )
        analysis_result = analyzer.perform()

        # Store the result of the analysis
        self.leaf_certificate_subject_matches_hostname = analysis_result.leaf_certificate_subject_matches_hostname
        self.leaf_certificate_is_ev = analysis_result.leaf_certificate_is_ev
        self.leaf_certificate_has_must_staple_extension = analysis_result.leaf_certificate_has_must_staple_extension
        self.leaf_certificate_signed_certificate_timestamps_count = (
            analysis_result.leaf_certificate_signed_certificate_timestamps_count
        )  # noqa: E501
        self.received_chain_contains_anchor_certificate = analysis_result.received_chain_contains_anchor_certificate
        self.received_chain_has_valid_order = analysis_result.received_chain_has_valid_order
        self.verified_chain_has_sha1_signature = analysis_result.verified_chain_has_sha1_signature
        self.verified_chain_has_legacy_symantec_anchor = analysis_result.verified_chain_has_legacy_symantec_anchor
        self.ocsp_response_status = analysis_result.ocsp_response_status
        self.ocsp_response_is_trusted = analysis_result.ocsp_response_is_trusted

    TRUST_FORMAT = "{store_name} CA Store ({store_version}):"
    NO_VERIFIED_CHAIN_ERROR_TXT = "ERROR - Could not build verified chain (certificate untrusted?)"

    def as_text(self) -> List[str]:
        text_output = [self._format_title(self.scan_command.get_title()), self._format_subtitle("Content")]
        text_output.extend(self._get_basic_certificate_text())

        # Trust section
        text_output.extend(["", self._format_subtitle("Trust")])

        # Hostname validation
        server_name_indication = self.server_info.tls_server_name_indication
        if self.server_info.tls_server_name_indication != self.server_info.hostname:
            text_output.append(self._format_field("SNI enabled with virtual domain:", server_name_indication))

        hostname_validation_text = (
            "OK - Certificate matches {hostname}".format(hostname=server_name_indication)
            if self.leaf_certificate_subject_matches_hostname
            else "FAILED - Certificate does NOT match {hostname}".format(hostname=server_name_indication)
        )
        text_output.append(self._format_field("Hostname Validation:", hostname_validation_text))

        # Path validation that was successfully tested
        for path_result in self.path_validation_result_list:
            if path_result.was_validation_successful:
                # EV certs - Only Mozilla supported for now
                ev_txt = ""
                if self.leaf_certificate_is_ev and path_result.trust_store.ev_oids:
                    ev_txt = ", Extended Validation"
                path_txt = "OK - Certificate is trusted{}".format(ev_txt)

            else:
                path_txt = "FAILED - Certificate is NOT Trusted: {}".format(path_result.verify_string)

            text_output.append(
                self._format_field(
                    self.TRUST_FORMAT.format(
                        store_name=path_result.trust_store.name, store_version=path_result.trust_store.version
                    ),
                    path_txt,
                )
            )

        # Path validation that ran into errors
        for path_error in self.path_validation_error_list:
            error_txt = "ERROR: {}".format(path_error.error_message)
            text_output.append(
                self._format_field(
                    self.TRUST_FORMAT.format(
                        store_name=path_error.trust_store.name, store_version=path_error.trust_store.version
                    ),
                    error_txt,
                )
            )

        if self.verified_chain_has_legacy_symantec_anchor is not None:
            timeline_str = (
                "March 2018"
                if self.verified_chain_has_legacy_symantec_anchor == SymantecDistrustTimelineEnum.MARCH_2018
                else "September 2018"
            )
            symantec_str = "WARNING: Certificate distrusted by Google and Mozilla on {}".format(timeline_str)
        else:
            symantec_str = "OK - Not a Symantec-issued certificate"
        text_output.append(self._format_field("Symantec 2018 Deprecation:", symantec_str))

        # Print the Common Names within the certificate chain
        cns_in_certificate_chain = [
            CertificateUtils.get_name_as_short_text(cert.subject) for cert in self.received_certificate_chain
        ]
        text_output.append(self._format_field("Received Chain:", " --> ".join(cns_in_certificate_chain)))

        # Print the Common Names within the verified certificate chain if validation was successful
        if self.verified_certificate_chain:
            cns_in_certificate_chain = [
                CertificateUtils.get_name_as_short_text(cert.subject) for cert in self.verified_certificate_chain
            ]
            verified_chain_txt = " --> ".join(cns_in_certificate_chain)
        else:
            verified_chain_txt = self.NO_VERIFIED_CHAIN_ERROR_TXT
        text_output.append(self._format_field("Verified Chain:", verified_chain_txt))

        if self.verified_certificate_chain:
            chain_with_anchor_txt = (
                "OK - Anchor certificate not sent"
                if not self.received_chain_contains_anchor_certificate
                else "WARNING - Received certificate chain contains the anchor certificate"
            )
        else:
            chain_with_anchor_txt = self.NO_VERIFIED_CHAIN_ERROR_TXT
        text_output.append(self._format_field("Received Chain Contains Anchor:", chain_with_anchor_txt))

        chain_order_txt = (
            "OK - Order is valid" if self.received_chain_has_valid_order else "FAILED - Certificate chain out of order!"
        )
        text_output.append(self._format_field("Received Chain Order:", chain_order_txt))

        if self.verified_certificate_chain:
            sha1_text = (
                "OK - No SHA1-signed certificate in the verified certificate chain"
                if not self.verified_chain_has_sha1_signature
                else "INSECURE - SHA1-signed certificate in the verified certificate chain"
            )
        else:
            sha1_text = self.NO_VERIFIED_CHAIN_ERROR_TXT
        text_output.append(self._format_field("Verified Chain contains SHA1:", sha1_text))

        # Extensions section
        text_output.extend(["", self._format_subtitle("Extensions")])

        # OCSP must-staple
        must_staple_txt = (
            "OK - Extension present"
            if self.leaf_certificate_has_must_staple_extension
            else "NOT SUPPORTED - Extension not found"
        )
        text_output.append(self._format_field("OCSP Must-Staple:", must_staple_txt))

        # Look for SCT extension
        scts_count = self.leaf_certificate_signed_certificate_timestamps_count
        if scts_count is None:
            sct_txt = "OK - Extension present"
        elif scts_count == 0:
            sct_txt = "NOT SUPPORTED - Extension not found"
        elif scts_count < 3:
            sct_txt = "WARNING - Only {} SCTs included but Google recommends 3 or more".format(str(scts_count))
        else:
            sct_txt = "OK - {} SCTs included".format(str(scts_count))
        text_output.append(self._format_field("Certificate Transparency:", sct_txt))

        # OCSP stapling
        text_output.extend(["", self._format_subtitle("OCSP Stapling")])

        if self.ocsp_response is None:
            text_output.append(self._format_field("", "NOT SUPPORTED - Server did not send back an OCSP response"))

        else:
            if self.ocsp_response_status != OcspResponseStatusEnum.SUCCESSFUL:
                ocsp_resp_txt = [
                    self._format_field(
                        "",
                        "ERROR - OCSP response status is not successful: {}".format(
                            self.ocsp_response_status.name  # type: ignore
                        ),
                    )
                ]
            else:
                ocsp_trust_txt = (
                    "OK - Response is trusted" if self.ocsp_response_is_trusted else "FAILED - Response is NOT trusted"
                )

                ocsp_resp_txt = [
                    self._format_field("OCSP Response Status:", self.ocsp_response["responseStatus"]),
                    self._format_field("Validation w/ Mozilla Store:", ocsp_trust_txt),
                    self._format_field("Responder Id:", self.ocsp_response["responderID"]),
                ]

                if "successful" in self.ocsp_response["responseStatus"]:
                    ocsp_resp_txt.extend(
                        [
                            self._format_field("Cert Status:", self.ocsp_response["responses"][0]["certStatus"]),
                            self._format_field(
                                "Cert Serial Number:", self.ocsp_response["responses"][0]["certID"]["serialNumber"]
                            ),
                            self._format_field("This Update:", self.ocsp_response["responses"][0]["thisUpdate"]),
                            self._format_field("Next Update:", self.ocsp_response["responses"][0]["nextUpdate"]),
                        ]
                    )
            text_output.extend(ocsp_resp_txt)

        # All done
        return text_output

    @staticmethod
    def _certificate_chain_to_xml(certificate_chain: List[Certificate]) -> List[Element]:
        cert_xml_list = []
        for certificate in certificate_chain:
            cert_xml = Element(
                "certificate",
                attrib={
                    "sha1Fingerprint": binascii.hexlify(certificate.fingerprint(hashes.SHA1())).decode("ascii"),
                    "hpkpSha256Pin": CertificateUtils.get_hpkp_pin(certificate),
                },
            )

            # Add the PEM cert
            cert_as_pem_xml = Element("asPEM")
            cert_as_pem_xml.text = certificate.public_bytes(Encoding.PEM).decode("ascii")
            cert_xml.append(cert_as_pem_xml)

            # Add some of the fields of the cert
            elem_xml = Element("subject")
            elem_xml.text = CertificateUtils.get_name_as_text(certificate.subject)
            cert_xml.append(elem_xml)

            elem_xml = Element("issuer")
            elem_xml.text = CertificateUtils.get_name_as_text(certificate.issuer)
            cert_xml.append(elem_xml)

            elem_xml = Element("serialNumber")
            elem_xml.text = str(certificate.serial_number)
            cert_xml.append(elem_xml)

            elem_xml = Element("notBefore")
            elem_xml.text = certificate.not_valid_before.strftime("%Y-%m-%d %H:%M:%S")
            cert_xml.append(elem_xml)

            elem_xml = Element("notAfter")
            elem_xml.text = certificate.not_valid_after.strftime("%Y-%m-%d %H:%M:%S")
            cert_xml.append(elem_xml)

            elem_xml = Element("signatureAlgorithm")
            elem_xml.text = certificate.signature_hash_algorithm.name
            cert_xml.append(elem_xml)

            key_attrs = {"algorithm": CertificateUtils.get_public_key_type(certificate)}
            public_key = certificate.public_key()
            key_attrs["size"] = str(public_key.key_size)
            if isinstance(public_key, EllipticCurvePublicKey):
                key_attrs["curve"] = public_key.curve.name
            else:
                key_attrs["exponent"] = str(public_key.public_numbers().e)

            elem_xml = Element("publicKey", attrib=key_attrs)
            cert_xml.append(elem_xml)

            dns_alt_names = CertificateUtils.get_dns_subject_alternative_names(certificate)
            if dns_alt_names:
                san_xml = Element("subjectAlternativeName")
                for dns_name in dns_alt_names:
                    dns_xml = Element("DNS")
                    dns_xml.text = dns_name
                    san_xml.append(dns_xml)
                cert_xml.append(san_xml)

            cert_xml_list.append(cert_xml)
        return cert_xml_list

    def as_xml(self) -> Element:
        xml_output = Element(self.scan_command.get_cli_argument(), title=self.scan_command.get_title())

        # Certificate chain
        contains_anchor = str(False) if not self.received_chain_contains_anchor_certificate else str(True)
        cert_chain_attrs = {
            "isChainOrderValid": str(self.received_chain_has_valid_order),
            "suppliedServerNameIndication": self.server_info.tls_server_name_indication,
            "containsAnchorCertificate": contains_anchor,
            "hasMustStapleExtension": str(self.leaf_certificate_has_must_staple_extension),
            "includedSctsCount": str(self.leaf_certificate_signed_certificate_timestamps_count),
        }
        cert_chain_xml = Element("receivedCertificateChain", attrib=cert_chain_attrs)
        for cert_xml in self._certificate_chain_to_xml(self.received_certificate_chain):
            cert_chain_xml.append(cert_xml)
        xml_output.append(cert_chain_xml)

        # Trust
        trust_validation_xml = Element("certificateValidation")

        # Hostname validation
        host_validation_xml = Element(
            "hostnameValidation",
            serverHostname=self.server_info.tls_server_name_indication,
            certificateMatchesServerHostname=str(self.leaf_certificate_subject_matches_hostname),
        )
        trust_validation_xml.append(host_validation_xml)

        # Path validation that was successful
        for path_result in self.path_validation_result_list:
            path_attrib_xml = {
                "usingTrustStore": path_result.trust_store.name,
                "trustStoreVersion": path_result.trust_store.version,
                "validationResult": path_result.verify_string,
            }

            # Things we only do with the Mozilla store: EV certs
            if self.leaf_certificate_is_ev and path_result.trust_store.ev_oids:
                path_attrib_xml["isExtendedValidationCertificate"] = str(self.leaf_certificate_is_ev)

            path_valid_xml = Element("pathValidation", attrib=path_attrib_xml)
            trust_validation_xml.append(path_valid_xml)

        # Path validation that ran into errors
        for path_error in self.path_validation_error_list:
            error_txt = "ERROR: {}".format(path_error.error_message)
            path_attrib_xml = {
                "usingTrustStore": path_result.trust_store.name,
                "trustStoreVersion": path_result.trust_store.version,
                "error": error_txt,
            }
            trust_validation_xml.append(Element("pathValidation", attrib=path_attrib_xml))

        # Verified chain
        if self.verified_certificate_chain:
            is_affected_by_symantec = str(True if self.verified_chain_has_legacy_symantec_anchor else False)
            verified_cert_chain_xml = Element(
                "verifiedCertificateChain",
                {
                    "hasSha1SignedCertificate": str(self.verified_chain_has_sha1_signature),
                    "suppliedServerNameIndication": self.server_info.tls_server_name_indication,
                    "hasMustStapleExtension": str(self.leaf_certificate_has_must_staple_extension),
                    "includedSctsCount": str(self.leaf_certificate_signed_certificate_timestamps_count),
                    "isAffectedBySymantecDeprecation": is_affected_by_symantec,
                },
            )
            for cert_xml in self._certificate_chain_to_xml(self.verified_certificate_chain):
                verified_cert_chain_xml.append(cert_xml)
            trust_validation_xml.append(verified_cert_chain_xml)

        xml_output.append(trust_validation_xml)

        # OCSP Stapling
        ocsp_xml = Element("ocspStapling", attrib={"isSupported": "False" if self.ocsp_response is None else "True"})

        if self.ocsp_response is not None:
            if self.ocsp_response_status != OcspResponseStatusEnum.SUCCESSFUL:
                ocsp_resp_xmp = Element(
                    "ocspResponse",
                    attrib={
                        "status": self.ocsp_response_status.name  # type: ignore
                    },
                )
            else:
                ocsp_resp_xmp = Element(
                    "ocspResponse",
                    attrib={
                        "isTrustedByMozillaCAStore": str(self.ocsp_response_is_trusted),
                        "status": self.ocsp_response_status.name,  # type: ignore
                    },
                )

                responder_xml = Element("responderID")
                responder_xml.text = self.ocsp_response["responderID"]
                ocsp_resp_xmp.append(responder_xml)

                produced_xml = Element("producedAt")
                produced_xml.text = self.ocsp_response["producedAt"]
                ocsp_resp_xmp.append(produced_xml)

            ocsp_xml.append(ocsp_resp_xmp)
        xml_output.append(ocsp_xml)

        # All done
        return xml_output

    def _get_basic_certificate_text(self) -> List[str]:
        certificate = self.received_certificate_chain[0]
        public_key = self.received_certificate_chain[0].public_key()
        text_output = [
            self._format_field(
                "SHA1 Fingerprint:", binascii.hexlify(certificate.fingerprint(hashes.SHA1())).decode("ascii")
            ),
            self._format_field("Common Name:", CertificateUtils.get_name_as_short_text(certificate.subject)),
            self._format_field("Issuer:", CertificateUtils.get_name_as_short_text(certificate.issuer)),
            self._format_field("Serial Number:", certificate.serial_number),
            self._format_field("Not Before:", certificate.not_valid_before),
            self._format_field("Not After:", certificate.not_valid_after),
            self._format_field("Signature Algorithm:", certificate.signature_hash_algorithm.name),
            self._format_field("Public Key Algorithm:", CertificateUtils.get_public_key_type(certificate)),
        ]

        if isinstance(public_key, EllipticCurvePublicKey):
            text_output.append(self._format_field("Key Size:", public_key.curve.key_size))
            text_output.append(self._format_field("Curve:", public_key.curve.name))
        elif isinstance(public_key, RSAPublicKey):
            text_output.append(self._format_field("Key Size:", public_key.key_size))
            text_output.append(self._format_field("Exponent:", "{0} (0x{0:x})".format(public_key.public_numbers().e)))
        else:
            # DSA Key? https://github.com/nabla-c0d3/sslyze/issues/314
            pass

        try:
            # Print the SAN extension if there's one
            text_output.append(
                self._format_field(
                    "DNS Subject Alternative Names:",
                    str(CertificateUtils.get_dns_subject_alternative_names(certificate)),
                )
            )
        except KeyError:
            pass

        return text_output

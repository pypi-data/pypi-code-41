ENTREZ_TOOL = "pub.tools"
ENTREZ_EMAIL = "plone.administration@imsweb.com"
ENTREZ_API_KEY = 'b8a3037bf326a4742928b8769831b7769707'
NO_VALUE = "<<blank>>"
MAX_PUBS = 9000
# Biopython will put a count greater than 200 ids into a post, so we don't need to worry about request size
# But there does seem to be a 9999 limit either from Biopython or from NCBI
MAX_RETRIES = 3
RETRY_SLEEP = 0.25

from unittest import TestCase, mock

from mbq import env


# keys generated JUST for tests
RSA_1024 = """\
-----BEGIN RSA PRIVATE KEY-----
MIICXAIBAAKBgQCeHEGkmRJxAt6CKfByYx1imCEMl15CNNk63QPvssNYjFLcZfDX
PXlCGlVVBLnD9p387LuVqoDzDnw+DyQ5Vqu7uYYDVDtMeyHYzRLciTUCmTO68sNH
fGoqqMguqqt5AiOBU/rHSaIGvjAA55rWY36XwuPW2vJut4//vWcEKfLrhQIDAQAB
AoGACSaXggA9+f5xhFULDoPAAqHNX94u3WQTon2CKdBN0AUnEoxv2PU83F+LysTg
P4A5epb08F+S4P5YoHrd3NewTrDPK4oIOSJMFA8PMWlThznAbtlvBlw71EesLcFx
4MKQY71bk+VZM9NXJfBJ0YrkA8vwzLca4qbKAKMGEoEg9k0CQQDKzUbNI2Ln+Bvn
9wx/mhuAVuNdRvjFyAJZaRk36wVI6V4oKLxjwJuHSrd6KOCeb7feaJ9/00Vp8xa9
8felIR6bAkEAx5XRtO/gxANyCUSL5vxB7Ghxrcqc64jyr9rncY/GpG3iQpySOdW7
FtafP7OTDChobu+qGZz7+FNQdmYqM7qwXwJAOPKJtiMArAjUtT9/R/mbTV+YuuGq
C8fNORQ1G6moM0Asy3Qc6pn0UnpdqTT/Vh4i8JZKa5eE/2pecXoXw0vYjwJANyL7
eQnfxSbShR7rq1c6+w1rgkB8E1GVAeHumF/I17oHjLFmcBXMhqWp/tYkJHKxTxxk
mIjWzyZtDxhwRjQn7wJBAMBHszJrhF4emxAU8QTJwxUe+tg9hYSJRmu+bcCvKpHv
oVLBHGp4vGWCYMCQcMPbPILmR+nEr1EF0eBEQKMWCp8=
-----END RSA PRIVATE KEY-----\
"""

CERT_4096 = """\
-----BEGIN CERTIFICATE-----
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
-----END CERTIFICATE-----\
"""


def environ(**kwargs):
    return mock.patch('mbq.env.os.environ', kwargs)


class EnvTests(TestCase):

    def setUp(self):
        self.env = env.Env()

    def test_missing(self):
        with self.assertRaisesRegex(env.EnvException, 'Missing key "MISSING"'):
            self.env.get('MISSING')

    def test_missing_with_default(self):
        self.assertIs(
            self.env.get('MISSING', default=mock.sentinel.default),
            mock.sentinel.default,
        )

    def test_missing_with_default_not_required(self):
        val = self.env.get('MISSING', default=mock.sentinel.default,
                           required=False)
        self.assertIs(val, mock.sentinel.default)

    @environ(KEY='     value     ')
    def test_strips_whitespace(self):
        self.assertEqual(self.env.get('KEY'), 'value')

    @environ(KEY='     value     ')
    def test_passes_stripped_val_to_coerce(self):
        passthru = mock.MagicMock(return_value=mock.sentinel.coerced)
        self.assertEqual(
            self.env.get('KEY', coerce=passthru),
            mock.sentinel.coerced,
        )

        args, kwargs = passthru.call_args
        self.assertEqual(args[0], 'value')

    @environ(GOOD='prd', BAD='BACON')
    def test_get_environment(self):
        self.assertIs(self.env.get_environment('GOOD'), env.Environment.PRODUCTION)

        with self.assertRaises(ValueError):
            self.env.get_environment('BAD')

    @environ(ONE='1', BAD='BACON')
    def test_get_int(self):
        self.assertEqual(self.env.get_int('ONE'), 1)
        with self.assertRaisesRegex(env.EnvException, 'invalid literal'):
            self.env.get_int('BAD')

    @environ(TRUE='1', FALSE='0', BAD='BACON', TRUE_STRING='true', FALSE_STRING='false')
    def test_get_bool(self):
        self.assertTrue(self.env.get_bool('TRUE'))
        self.assertFalse(self.env.get_bool('FALSE'))
        with self.assertRaises(ValueError):
            self.env.get_bool('BAD')
        with self.assertRaises(ValueError):
            self.env.get_bool('BAD', default=True)
        self.assertTrue(self.env.get_bool('MISSING', default=True))
        self.assertFalse(self.env.get_bool('MISSING', default=False))
        with self.assertRaises(ValueError):
            self.env.get_bool('TRUE_STRING')
        with self.assertRaises(ValueError):
            self.env.get_bool('FALSE_STRING')

    @environ(ONE='a', TWO='a,,b,')
    def test_get_csv(self):
        self.assertEqual(self.env.get_csv('ONE'), ['a'])
        self.assertEqual(self.env.get_csv('TWO'), ['a', 'b'])

    @environ(ONE='a', THREE='a   b\tc')
    def test_get_tokens(self):
        self.assertEqual(self.env.get_tokens('ONE'), ['a'])
        self.assertEqual(self.env.get_tokens('THREE'), ['a', 'b', 'c'])

    @environ(RSA=RSA_1024.replace('\n', ''))
    def test_get_rsa(self):
        self.assertEqual(self.env.get_key('RSA PRIVATE KEY', 'RSA'), RSA_1024)

    @environ(CERT=CERT_4096.replace('\n', ''))
    def test_get_cert(self):
        self.assertEqual(self.env.get_key('CERTIFICATE', 'CERT'), CERT_4096)


class EnvironmentEnumTest(TestCase):
    def test_value_lookup(self):
        self.assertIs(env.Environment.PRODUCTION, env.Environment('prd'))
        self.assertIs(env.Environment.PRODUCTION, env.Environment('PRD'))
        self.assertIs(env.Environment.PRODUCTION, env.Environment('production'))
        self.assertIs(env.Environment.PRODUCTION, env.Environment('PrOdUcTiOn'))

    def test_is_deployed(self):
        self.assertTrue(env.Environment.PRODUCTION.is_deployed)
        self.assertTrue(env.Environment.DEVELOPMENT.is_deployed)
        self.assertFalse(env.Environment.LOCAL.is_deployed)

        # no different than the above but testing explicitly to ensure we
        # maintain the api
        current = env.Environment('prd')
        self.assertTrue(current.is_deployed)

    def test_names(self):
        # trivial tests to prevent api regressions
        for member in list(env.Environment):
            self.assertIsInstance(member.short_name, str)
            self.assertIsInstance(member.long_name, str)

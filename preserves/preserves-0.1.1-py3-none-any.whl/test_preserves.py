from .preserves import *
import unittest
import sys

if isinstance(chr(123), bytes):
    def _byte(x):
        return chr(x)
    def _hex(x):
        return x.encode('hex')
else:
    def _byte(x):
        return bytes([x])
    def _hex(x):
        return x.hex()

def _buf(*args):
    result = []
    for chunk in args:
        if isinstance(chunk, bytes):
            result.append(chunk)
        elif isinstance(chunk, basestring):
            result.append(chunk.encode('utf-8'))
        elif isinstance(chunk, numbers.Number):
            result.append(_byte(chunk))
        else:
            raise Exception('Invalid chunk in _buf %r' % (chunk,))
    result = b''.join(result)
    return result

def _varint(v):
    e = Encoder()
    e.varint(v)
    return e.contents()

def _d(bs):
    return decode(bs, placeholders={
        0: Symbol('discard'),
        1: Symbol('capture'),
        2: Symbol('observe'),
    })

def _e(v):
    return encode(v, placeholders={
        Symbol('discard'): 0,
        Symbol('capture'): 1,
        Symbol('observe'): 2,
    })

def _R(k, *args):
    return Record(Symbol(k), args)

class CodecTests(unittest.TestCase):
    def _roundtrip(self, forward, expected, back=None, nondeterministic=False):
        if back is None: back = forward
        self.assertEqual(_d(_e(forward)), back)
        self.assertEqual(_d(_e(back)), back)
        self.assertEqual(_d(expected), back)
        if not nondeterministic:
            actual = _e(forward)
            self.assertEqual(actual, expected, '%s != %s' % (_hex(actual), _hex(expected)))

    def test_decode_varint(self):
        with self.assertRaises(DecodeError):
            Decoder(_buf()).varint()
        self.assertEqual(Decoder(_buf(0)).varint(), 0)
        self.assertEqual(Decoder(_buf(10)).varint(), 10)
        self.assertEqual(Decoder(_buf(100)).varint(), 100)
        self.assertEqual(Decoder(_buf(200, 1)).varint(), 200)
        self.assertEqual(Decoder(_buf(0b10101100, 0b00000010)).varint(), 300)
        self.assertEqual(Decoder(_buf(128, 148, 235, 220, 3)).varint(), 1000000000)

    def test_encode_varint(self):
        self.assertEqual(_varint(0), _buf(0))
        self.assertEqual(_varint(10), _buf(10))
        self.assertEqual(_varint(100), _buf(100))
        self.assertEqual(_varint(200), _buf(200, 1))
        self.assertEqual(_varint(300), _buf(0b10101100, 0b00000010))
        self.assertEqual(_varint(1000000000), _buf(128, 148, 235, 220, 3))

    def test_shorts(self):
        self._roundtrip(_R('capture', _R('discard')), _buf(0x82, 0x11, 0x81, 0x10))
        self._roundtrip(_R('observe', _R('speak', _R('discard'), _R('capture', _R('discard')))),
                        _buf(0x82, 0x12, 0x83, 0x75, "speak", 0x81, 0x10, 0x82, 0x11, 0x81, 0x10))

    def test_simple_seq(self):
        self._roundtrip([1,2,3,4], _buf(0x94, 0x31, 0x32, 0x33, 0x34), back=(1,2,3,4))
        self._roundtrip(SequenceStream([1,2,3,4]), _buf(0x29, 0x31, 0x32, 0x33, 0x34, 0x04),
                        back=(1,2,3,4))
        self._roundtrip((-2,-1,0,1), _buf(0x94, 0x3E, 0x3F, 0x30, 0x31))

    def test_str(self):
        self._roundtrip(u'hello', _buf(0x55, 'hello'))
        self._roundtrip(StringStream([b'he', b'llo']), _buf(0x25, 0x62, 'he', 0x63, 'llo', 0x04),
                        back=u'hello')
        ## TODO: error with zero-size chunks
        self._roundtrip(StringStream([b'he', b'll', b'', b'',  b'o']),
                        _buf(0x25, 0x62, 'he', 0x62, 'll', 0x60, 0x60, 0x61, 'o', 0x04),
                        back=u'hello')
        self._roundtrip(BinaryStream([b'he', b'll', b'', b'',  b'o']),
                        _buf(0x26, 0x62, 'he', 0x62, 'll', 0x60, 0x60, 0x61, 'o', 0x04),
                        back=b'hello')
        self._roundtrip(SymbolStream([b'he', b'll', b'', b'',  b'o']),
                        _buf(0x27, 0x62, 'he', 0x62, 'll', 0x60, 0x60, 0x61, 'o', 0x04),
                        back=Symbol(u'hello'))

    def test_mixed1(self):
        self._roundtrip((u'hello', Symbol(u'there'), b'world', (), set(), True, False),
                        _buf(0x97, 0x55, 'hello', 0x75, 'there', 0x65, 'world', 0x90, 0xa0, 1, 0))

    def test_signedinteger(self):
        self._roundtrip(-257, _buf(0x42, 0xFE, 0xFF))
        self._roundtrip(-256, _buf(0x42, 0xFF, 0x00))
        self._roundtrip(-255, _buf(0x42, 0xFF, 0x01))
        self._roundtrip(-254, _buf(0x42, 0xFF, 0x02))
        self._roundtrip(-129, _buf(0x42, 0xFF, 0x7F))
        self._roundtrip(-128, _buf(0x41, 0x80))
        self._roundtrip(-127, _buf(0x41, 0x81))
        self._roundtrip(-4, _buf(0x41, 0xFC))
        self._roundtrip(-3, _buf(0x3D))
        self._roundtrip(-2, _buf(0x3E))
        self._roundtrip(-1, _buf(0x3F))
        self._roundtrip(0, _buf(0x30))
        self._roundtrip(1, _buf(0x31))
        self._roundtrip(12, _buf(0x3C))
        self._roundtrip(13, _buf(0x41, 0x0D))
        self._roundtrip(127, _buf(0x41, 0x7F))
        self._roundtrip(128, _buf(0x42, 0x00, 0x80))
        self._roundtrip(255, _buf(0x42, 0x00, 0xFF))
        self._roundtrip(256, _buf(0x42, 0x01, 0x00))
        self._roundtrip(32767, _buf(0x42, 0x7F, 0xFF))
        self._roundtrip(32768, _buf(0x43, 0x00, 0x80, 0x00))
        self._roundtrip(65535, _buf(0x43, 0x00, 0xFF, 0xFF))
        self._roundtrip(65536, _buf(0x43, 0x01, 0x00, 0x00))
        self._roundtrip(131072, _buf(0x43, 0x02, 0x00, 0x00))

    def test_floats(self):
        self._roundtrip(Float(1.0), _buf(2, 0x3f, 0x80, 0, 0))
        self._roundtrip(1.0, _buf(3, 0x3f, 0xf0, 0, 0, 0, 0, 0, 0))
        self._roundtrip(-1.202e300, _buf(3, 0xfe, 0x3c, 0xb7, 0xb7, 0x59, 0xbf, 0x04, 0x26))

    def test_badchunks(self):
        self.assertEqual(_d(_buf(0x25, 0x61, 'a', 0x04)), u'a')
        self.assertEqual(_d(_buf(0x26, 0x61, 'a', 0x04)), b'a')
        self.assertEqual(_d(_buf(0x27, 0x61, 'a', 0x04)), Symbol(u'a'))
        for a in [0x25, 0x26, 0x27]:
            for b in [0x51, 0x71]:
                with self.assertRaises(DecodeError, msg='Unexpected non-binary chunk') as cm:
                    _d(_buf(a, b, 'a', 0x04))

    def test_dict(self):
        self._roundtrip({ Symbol(u'a'): 1,
                          u'b': True,
                          (1, 2, 3): b'c',
                          ImmutableDict({ Symbol(u'first-name'): u'Elizabeth', }):
                            { Symbol(u'surname'): u'Blackwell' } },
                        _buf(0xB8,
                             0x71, "a", 0x31,
                             0x51, "b", 0x01,
                             0x93, 0x31, 0x32, 0x33, 0x61, "c",
                             0xB2, 0x7A, "first-name", 0x59, "Elizabeth",
                             0xB2, 0x77, "surname", 0x59, "Blackwell"),
                        nondeterministic = True)

    def test_iterator_stream(self):
        d = {u'a': 1, u'b': 2, u'c': 3}
        r = r'29(92516.3.){3}04'
        if hasattr(d, 'iteritems'):
            # python 2
            bs = _e(d.iteritems())
            self.assertRegexpMatches(_hex(bs), r)
        else:
            # python 3
            bs = _e(d.items())
            self.assertRegex(_hex(bs), r)
        self.assertEqual(sorted(_d(bs)), [(u'a', 1), (u'b', 2), (u'c', 3)])

    def test_long_sequence(self):
        # Short enough to not need a varint:
        self._roundtrip((False,) * 14, _buf(0x9E, b'\x00' * 14))
        # Varint-needing:
        self._roundtrip((False,) * 15, _buf(0x9F, 0x0F, b'\x00' * 15))
        self._roundtrip((False,) * 100, _buf(0x9F, 0x64, b'\x00' * 100))
        self._roundtrip((False,) * 200, _buf(0x9F, 0xC8, 0x01, b'\x00' * 200))

    def test_format_c_twice(self):
        self._roundtrip(SequenceStream([StringStream([b'abc']), StringStream([b'def'])]),
                        _buf(0x29, 0x25, 0x63, 'abc', 0x04, 0x25, 0x63, 'def', 0x04, 0x04),
                        back=(u'abc', u'def'))

def add_method(d, tName, fn):
    if hasattr(fn, 'func_name'):
        # python2
        fname = str(fn.func_name + '_' + tName)
        fn.func_name = fname
    else:
        # python3
        fname = str(fn.__name__ + '_' + tName)
        fn.__name__ = fname
    d[fname] = fn

expected_values = {
    "annotation1": { "forward": annotate(9, u"abc"), "back": 9 },
    "annotation2": { "forward": annotate([[], annotate([], u"x")], u"abc", u"def"), "back": ((), ()) },
    "annotation3": { "forward": annotate(5, annotate(2, 1), annotate(4, 3)), "back": 5 },
    "annotation5": { "forward": annotate(_R('R', annotate(Symbol('f'), Symbol('af'))),
                                         Symbol('ar')),
                     "back": _R('R', Symbol('f')) },
    "annotation6": { "forward": Record(annotate(Symbol('R'), Symbol('ar')),
                                       [annotate(Symbol('f'), Symbol('af'))]),
                     "back": _R('R', Symbol('f')) },
    "annotation7": { "forward": annotate([], Symbol('a'), Symbol('b'), Symbol('c')),
                     "back": () },
    "bytes1": { "forward": BinaryStream([b'he', b'll', b'o']), "back": b'hello' },
    "list1": { "forward": SequenceStream([1, 2, 3, 4]), "back": (1, 2, 3, 4) },
    "list2": { "forward": SequenceStream([ StringStream([b'abc']), StringStream([b'def']) ]),
               "back": (u"abc", u"def") },
    "list3": { "forward": SequenceStream([[u"a", 1], [u"b", 2], [u"c", 3]]),
               "back": ((u"a", 1), (u"b", 2), (u"c", 3)) },
    "record2": { "value": _R('observe', _R('speak', _R('discard'), _R('capture', _R('discard')))) },
    "string0a": { "forward": StringStream([]), "back": u'' },
    "string1": { "forward": StringStream([b'he', b'll', b'o']), "back": u'hello' },
    "string2": { "forward": StringStream([b'he', b'llo']), "back": u'hello' },
    "symbol1": { "forward": SymbolStream([b'he', b'll', b'o']), "back": Symbol('hello') },
}

def get_expected_values(tName, textForm):
    entry = expected_values.get(tName, {"value": textForm})
    if 'value' in entry:
        return { "forward": entry['value'], "back": entry['value'] }
    elif 'forward' in entry and 'back' in entry:
        return entry
    else:
        raise Exception('Invalid expected_values entry for ' + tName)

def install_test(d, variant, tName, binaryForm, annotatedTextForm):
    textForm = annotatedTextForm.strip()
    entry = get_expected_values(tName, textForm)
    forward = entry['forward']
    back = entry['back']
    def test_match_expected(self): self.assertEqual(textForm, back)
    def test_roundtrip(self): self.assertEqual(self.DS(self.E(textForm)), back)
    def test_forward(self): self.assertEqual(self.DS(self.E(forward)), back)
    def test_back(self): self.assertEqual(self.DS(binaryForm), back)
    def test_back_ann(self): self.assertEqual(self.D(self.E(annotatedTextForm)), annotatedTextForm)
    def test_encode(self): self.assertEqual(self.E(forward), binaryForm)
    def test_encode_ann(self): self.assertEqual(self.E(annotatedTextForm), binaryForm)
    add_method(d, tName, test_match_expected)
    add_method(d, tName, test_roundtrip)
    add_method(d, tName, test_forward)
    add_method(d, tName, test_back)
    add_method(d, tName, test_back_ann)
    if variant not in ['nondeterministic']:
        add_method(d, tName, test_encode)
    if variant not in ['nondeterministic', 'streaming']:
        add_method(d, tName, test_encode_ann)

def install_exn_test(d, tName, bs, check_proc):
    def test_exn(self):
        try:
            self.D(bs)
        except:
            check_proc(self, sys.exc_info()[1])
            return
        self.fail('did not fail as expected')
    add_method(d, tName, test_exn)

class CommonTestSuite(unittest.TestCase):
    import os
    with open(os.path.join(os.path.dirname(__file__),
                           '../../../tests/samples.bin'), 'rb') as f:
        samples = Decoder(f.read(), include_annotations=True).next()

    TestCases = Record.makeConstructor('TestCases', 'mapping cases')
    ExpectedPlaceholderMapping = Record.makeConstructor('ExpectedPlaceholderMapping', 'table')

    m = TestCases._mapping(samples.peel()).strip()
    placeholders_decode = ExpectedPlaceholderMapping._table(m)
    placeholders_encode = dict((v,k) for (k,v) in placeholders_decode.items())

    tests = TestCases._cases(samples.peel()).peel()
    for (tName0, t0) in tests.items():
        tName = tName0.strip().name
        t = t0.peel()
        if t.key == Symbol('Test'):
            install_test(locals(), 'normal', tName, t[0].strip(), t[1])
        elif t.key == Symbol('StreamingTest'):
            install_test(locals(), 'streaming', tName, t[0].strip(), t[1])
        elif t.key == Symbol('NondeterministicTest'):
            install_test(locals(), 'nondeterministic', tName, t[0].strip(), t[1])
        elif t.key == Symbol('DecodeError'):
            def expected_err(self, e):
                self.assertIsInstance(e, DecodeError)
                self.assertNotIsInstance(e, ShortPacket)
            install_exn_test(locals(), tName, t[0].strip(), expected_err)
        elif t.key == Symbol('DecodeShort'):
            def expected_short(self, e):
                self.assertIsInstance(e, ShortPacket)
            install_exn_test(locals(), tName, t[0].strip(), expected_short)
        elif t.key == Symbol('ParseError') or \
             t.key == Symbol('ParseShort'):
            # Skipped for now, until we have an implementation of text syntax
            pass
        else:
            raise Exception('Unsupported test kind', t.key)

    def DS(self, bs):
        return decode(bs, placeholders=self.placeholders_decode)

    def D(self, bs):
        return decode_with_annotations(bs, placeholders=self.placeholders_decode)

    def E(self, v):
        return encode(v, placeholders=self.placeholders_encode)

class RecordTests(unittest.TestCase):
    def test_getters(self):
        T = Record.makeConstructor('t', 'x y z')
        T2 = Record.makeConstructor('t', 'x y z')
        U = Record.makeConstructor('u', 'x y z')
        t = T(1, 2, 3)
        self.assertTrue(T.isClassOf(t))
        self.assertTrue(T2.isClassOf(t))
        self.assertFalse(U.isClassOf(t))
        self.assertEqual(T._x(t), 1)
        self.assertEqual(T2._y(t), 2)
        self.assertEqual(T._z(t), 3)
        with self.assertRaises(TypeError):
            U._x(t)

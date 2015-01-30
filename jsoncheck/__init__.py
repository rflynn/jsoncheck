
'''
check a json-decoded object for compliance with a simple schema.
example:

import jsoncheck
jsoncheck.check({'x':int,
                 'y':float,
                 'z':{'foo':list}},
                {'x':1,
                 'y':2,
                 'z':{'foo':[]}})

'''

import types
import re
import uuid as uuid_module
from datetime import datetime


def check(obj, spec, ctx=None):
    if ctx is None:
        ctx = []
    # print 'check obj=%s spec=%s ctx=%s' % (obj, spec, ctx)
    if isinstance(spec, Nullable):
        if not spec.check(obj):
            return "%s%s does not match %s" % (''.join(ctx), obj, sig(spec))
    elif isinstance(spec, Enum):
        err = spec.check(obj)
        if err:
            return err
    elif is_scalar(obj):
        return check_scalar(obj, spec, ctx=ctx)
    elif isinstance(obj, dict):
        return check_dict(obj, spec, ctx)
    elif isinstance(obj, list):
        return check_list(obj, spec, ctx)
    else:
        return 'expected type %s, got %s' % (sig(spec), obj)


def check_dict(obj, spec, ctx):
    if spec is dict:
        pass
    elif isinstance(spec, dict):
        if spec:
            for k in obj.keys():
                if k not in spec:
                    return 'unknown key: %s%s' % (''.join(ctx), k)
            for k in spec.keys():
                # if k not in obj:
                #     return 'key missing: %s%s' % (''.join(ctx), k)
                v = obj.get(k)
                if is_scalar(v):
                    e = check_scalar(v, spec[k], ctx=ctx+[k+':'])
                else:
                    e = check(v, spec[k], ctx=ctx+[k+':'])
                if e:
                    return e
    else:
        return 'expected type %s, got %s' % (sig(spec), obj)

def check_list(obj, spec, ctx):
    # print 'check_list obj=%s spec=%s ctx=%s' % (obj, spec, ctx)
    if spec is list:
        return None
    elif isinstance(spec, list):
        if spec:
            for i, x in enumerate(obj):
                e = check(x, spec[0], ctx=ctx+['[%s]' % i])
                if e:
                    return e
        return None
    return 'expected type %s, got %s' % (sig(spec), obj)

def check_scalar(x, spec, ctx=None):
    if ctx is None:
        ctx = []
    # print 'check_scalar spec=%s x=%s ctx=%s' % (spec, x, ctx)
    if spec is bool:
        if x is not True and x is not False:
            return "%s%s is not a bool" % (''.join(ctx), repr(x))
    elif spec is int or spec is long:
        if not isinstance(x, (int, long)):
            return "%s%s is not an int" % (''.join(ctx), repr(x))
    elif spec is float:
        if not isinstance(x, (float, int)):
            return "%s%s is not a float" % (''.join(ctx), repr(x))
    elif spec is str or spec is unicode:
        if not isinstance(x, basestring):
            return "%s%s is not a string" % (''.join(ctx), repr(x))
    elif spec is list:
        if not isinstance(x, list):
            return "%s:%s is not a list" % (''.join(ctx), repr(x))
        else:
            return check(x, spec, ctx=ctx)
    elif isinstance(spec, Nullable):
        if not spec.check(x):
            return "%s%s does not match %s" % (''.join(ctx), x, sig(spec))
    elif isinstance(spec, Enum):
        err = spec.check(x)
        if err:
            return err
    elif isinstance(spec, types.FunctionType):
        if not spec(x):
            fs = "%s" % spec # '<function int8s at 0x10fda16e0>'
            fs = fs.split(' ')[1]
            return "%s%s does not match '%s'" % (''.join(ctx), x, fs)
    else:
        return "%s%s does not match '%s'" % (''.join(ctx), x, sig(spec))
    return None

def sig(x):
    if x is None: return 'null'
    if x is True: return 'true'
    if x is False: return 'false'
    if x is int: return 'int'
    if x is long: return 'int'
    if isinstance(x, (int, long)): return 'int'
    if x is str: return 'str'
    if x is unicode: return 'str'
    if isinstance(x, basestring): return 'str'
    if x is dict: return '{}'
    if isinstance(x, dict): return '{}'
    if x is list: return '[]'
    if isinstance(x, list):
        if x: return '[' + sig(x[0]) + ']'
        return '[]'
    if isinstance(x, float): return 'float'
    if isinstance(x, Nullable): return repr(x)
    if isinstance(x, Enum): return repr(x)
    return str(type(x))

def is_composite(x):
    return isinstance(x, (list, dict))

def is_scalar(x):
    return not is_composite(x)

class Nullable:

    def __init__(self, t):
        self.t = t

    def check(self, obj):
        return obj is None or not check(obj, self.t)

    def __repr__(self):
        return 'Nullable(%s)' % sig(self.t)

def nullable(t):
    return Nullable(t)

def optional(t):
    return Nullable(t)

class Enum:

    def __init__(self, allowed):
        self.allowed = allowed

    def __repr__(self):
        return 'Enum(%s)' % str(self.allowed)

    def check(self, obj):
        if obj in self.allowed:
            return None
        return '%s not in %s' % (str(obj), str(self))

# convenience functions

def int8u(x):
    return isinstance(x, (int, long)) and \
        (x >= 0 and x < (1 << 8))

def int8s(x):
    return isinstance(x, (int, long)) and \
        (x >= -(1 << 7) and x < (1 << 7))

def int16u(x):
    return isinstance(x, (int, long)) and \
        (x >= 0 and x < (1 << 16))

def int16s(x):
    return isinstance(x, (int, long)) and \
        (x >= -(1 << 16) and x < (1 << 16))

def int32u(x):
    return isinstance(x, (int, long)) and \
        (x >= 0 and x < (1L << 32))

def int32s(x):
    return isinstance(x, (int, long)) and \
        (x >= -(1L << 32) and x < (1L << 32))

def int64u(x):
    return isinstance(x, (int, long)) and \
        (x >= 0 and x < (1L << 64))

def int64s(x):
    return isinstance(x, (int, long)) and \
        (x >= -(1L << 64) and x < (1L << 64))

def iso8601_year_month(x):
    try:
        return datetime.strptime(x, '%Y-%m') is not None
    except TypeError:
        return None
    except ValueError:
        return None

def iso8601_date(x):
    try:
        return datetime.strptime(x, '%Y-%m-%d') is not None
    except TypeError:
        return None
    except ValueError:
        return None

def iso8601(x):
    try:
        return datetime.strptime(x, '%Y-%m-%dT%H:%M:%SZ') is not None
    except TypeError:
        return None
    except ValueError:
        return None

def url_http_abs(x):
    return x and re.match('^https?://.+$', x)

def uuid(x):
    try:
        uuid_module.UUID(x)
        return True
    except:
        return False

def sha1(x):
    return x and re.match('^[a-fA-F0-9]{40}$', x)

def enum(allowed_values):
    assert isinstance(allowed_values, list)
    return Enum(allowed_values)

def str_not_empty(x):
    return isinstance(x, basestring) and x != ''

"""
unit tests via nosetest
run: $ nosetests path/to/this/file
"""

def test_bool_ok():
    assert check(True, bool) is None
    assert check(False, bool) is None

def test_int8s():
    assert check( 128,   int8s) == "128 does not match 'int8s'" # too high
    assert check( 127,   int8s) is None
    assert check(   0,   int8s) is None
    assert check(-128,   int8s) is None
    assert check(-129,   int8s) == "-129 does not match 'int8s'" # too low
    assert check(   0.0, int8s) == "0.0 does not match 'int8s'" # no floats

def test_int8u():
    assert check( 256,   int8u) == "256 does not match 'int8u'" # too high
    assert check( 255,   int8u) is None
    assert check(   0,   int8u) is None
    assert check(  -1,   int8u) == "-1 does not match 'int8u'" # too low
    assert check(   0.0, int8u) == "0.0 does not match 'int8u'" # no floats

def test_int16u():
    assert check(65536,   int16u) == "65536 does not match 'int16u'" # too high
    assert check(65535,   int16u) is None
    assert check(    0,   int16u) is None
    assert check(   -1,   int16u) == "-1 does not match 'int16u'" # too low
    assert check(    0.0, int16u) == "0.0 does not match 'int16u'" # no floats

def test_dict():
    assert check({'x': None}, {'x': nullable(int)}) is None
    assert check({'x': 5   }, {'x': nullable(int)}) is None
    assert check({'x': 5   }, {'x': int}) is None
    assert check({'x': None}, {'x': int}) == '''x:None is not an int'''

def test_dict_empty():
    assert check({}, {'x': optional(int)}) is None
    assert check({}, {'x': nullable(int)}) is None

def test_dict_wrongtype():
    assert check({'x': 5}, {'x': dict}) == "x:5 does not match '{}'"

def test_unknown_key():
    obj = {
        'due': '2014-04-0',
        'dueDate': '2014-04-01',
        'foo': {
            'bar': 123
        }
    }
    assert check(obj, {
        'due': iso8601_date,
        'foo': {
            'bar': list
        }
    }) == '''unknown key: dueDate'''

def test_int_is_float():
    assert check(0, float) is None

def test_float_is_not_int():
    assert check(0.0, int) == '0.0 is not an int'

def test_schema2():
    assert check({'x': 1,   'y': 1,     'z': {'foo': []}},
                 {'x': int, 'y': float, 'z': {'foo': list}}) is None

def test_list_empty_root_spec_nonempty_ok():
    assert check([], [{'foo': [int]}]) is None

def test_list_empty_spec_nonempty_ok():
    assert check([{'foo': []}], [{'foo': [int]}]) is None

def test_list_dict_empty():
    assert check([{}], [{'foo': [int]}]) == "[0]foo:None does not match '[int]'"

def test_list_wrongtype():
    assert check([{'foo': ['bar']}],
                 [{'foo': [int]}]) == "[0]foo:[0]'bar' is not an int"
    assert check([{'foo': [1, 2, 3, 'bar']}],
                 [{'foo': [int]}]) == "[0]foo:[3]'bar' is not an int"

def test_uuid():
    assert check('00000000-0000-0000-0000-000000000000', uuid) is None # empty guid
    assert check('gggggggg-gggg-gggg-gggg-gggggggggggg', uuid) is not None # out-of-range alpha
    assert check('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', uuid) is None # all lowercase ok
    assert check('AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA', uuid) is None # all uppercase ok
    assert check('AaAaAaAa-AaAa-AaAa-AaAa-AaAaAaAaAaAa', uuid) is None # mixed case ok. argh

def test_sha1():
    assert check('da39a3ee5e6b4b0d3255bfef95601890afd80709', sha1) is None

def test_iso8601():
    assert check('2014-08-20T10:04:30Z', iso8601) is None

def test_iso8601_date():
    assert check('2014-08-20', iso8601_date) is None

def test_iso8601_year_month():
    assert check('2014-08', iso8601_year_month) is None
    assert check('2014-08-10', iso8601_year_month) is not None

def test_list_of_list():
    # ok
    assert check([[0]],            [[int]]) is None # ok
    assert check([[0, 1, 2]],      [[int]]) is None # ok
    # empty lists are still lists; if you want to enforce list size you need a custom function
    assert check([[]],             [[int]]) is None
    # errors
    assert check([[[]]],           [[int]]) == 'expected type int, got []'
    assert check([[0, 1, 2, 3.5]], [[int]]) == '[0][3]3.5 is not an int'

def test_optional_list():
    assert check([], optional([])) is None
    assert check([[]], optional([[]])) is None
    assert check([[]], optional([[int]])) is None
    assert check([[0]], optional([[int]])) is None
    assert check([[0.0]], optional([[int]])) == '[[0.0]] does not match Nullable([[int]])'

def test_enum():
    assert check(0, enum([0])) is None
    assert check(1, enum([1])) is None
    assert check(None, enum([None])) is None
    assert check(None, optional(enum([]))) is None
    assert check('a', enum(['a', 'b', 'c'])) is None

    assert check(0, enum([])) == '0 not in Enum([])' # impossible
    assert check('d', enum(['a', 'b', 'c'])) == "d not in Enum(['a', 'b', 'c'])"
    assert check('d', optional(enum(['a']))) == "d does not match Nullable(Enum(['a']))"

def test_str_not_empty():
    assert check('asdf', str_not_empty) is None
    assert check('', str_not_empty) == " does not match 'str_not_empty'"
    assert check(1234, str_not_empty) == "1234 does not match 'str_not_empty'"

if __name__ == '__main__':
    pass

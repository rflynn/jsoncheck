
# Description
jsoncheck is a simple schema validator for json decoded into python
it returns human-readable error messages when supplied data doesn't match the schema spec
it comes with built-in types, or you can define your own functions to check for arbitrary values

# Install
```
$ sudo pip install jsoncheck
```

...or...

```
$ git clone https://github.com/rflynn/jsoncheck.git
$ cd jsoncheck
$ sudo python setup.py install
```

# Examples
jsoncheck.check returns None on success, or a human-readable string on error
```
$ python -i
>>> import jsoncheck
>>> jsoncheck.check({'a':1,'b':2}, {'a':int})
'unknown key: b'
>>> def string_len3plus(x):
...     return isinstance(x, (str, unicode)) and len(x) >= 3
... 
>>> jsoncheck.check(42, string_len3plus)
"42 does not match 'string_len3plus'"
>>> jsoncheck.check("ab", string_len3plus)
"ab does not match 'string_len3plus'"
>>> jsoncheck.check("abc", string_len3plus)
>>> 
```

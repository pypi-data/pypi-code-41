import dis
from inspect import signature
from types import CodeType, FunctionType
from functools import wraps

def hoc(func):

    def wrapper(*args, **kwargs):

        _LC = dis.opmap['LOAD_CONST'].to_bytes(1, byteorder='little')
        _LF = dis.opmap['LOAD_FAST'].to_bytes(1, byteorder='little')
        
        # Get the signature of the wrapped function
        from inspect import signature
        func_sig = signature(func)

        byte_code = func.__code__.co_code
        _byte_code = b''
        # constant shifting
        for i in range(0,len(byte_code),2):
            ith_byte = bytes([byte_code[i]])
            iplus1th_byte = bytes([byte_code[i+1]])
            if ith_byte == _LC:
                _byte_code = _byte_code + ith_byte + bytes([int.from_bytes(iplus1th_byte, 'little')+1])
            else:
                _byte_code = _byte_code + ith_byte + iplus1th_byte
        
        # constant updating
        _co_consts = ((func.__code__.co_consts[0],)) + (args[0],) 
        _new_co_consts = _co_consts + func.__code__.co_consts[1:]
        if len(func.__code__.co_consts) > 1:
            _co_consts = _co_consts + func.__code__.co_consts[1:]
        _co_varnames = func.__code__.co_varnames[1:] + ('self',)

        # constant loading
        const_load = dis.opmap['LOAD_CONST'].to_bytes(1, byteorder='little')+b'\x01'
        const_store = dis.opmap['STORE_FAST'].to_bytes(1, byteorder='little')+b'\x02'
        __byte_code = const_load + const_store + _byte_code[:]
        ___byte_code = b''
        for i in range(0,len(__byte_code),2):
            ith_byte = bytes([__byte_code[i]])
            iplus1th_byte = bytes([__byte_code[i+1]])
            if ith_byte == _LF and iplus1th_byte in [b'\x00']:
                ___byte_code = ___byte_code + ith_byte + bytes([int.from_bytes(iplus1th_byte, 'little')+len(func_sig.parameters)-1])
            elif ith_byte == _LF and iplus1th_byte in list(map(lambda x: bytes([x]), list(range(1,len(func_sig.parameters))))):
                ___byte_code = ___byte_code + ith_byte + bytes([int.from_bytes(iplus1th_byte, 'little')-1])
            else:
                ___byte_code = ___byte_code + ith_byte + iplus1th_byte
        _func_code = CodeType(
            func.__code__.co_argcount-1,
            func.__code__.co_kwonlyargcount,
            func.__code__.co_nlocals,
            func.__code__.co_stacksize,
            func.__code__.co_flags,
            ___byte_code,
            _co_consts,
            func.__code__.co_names,
            _co_varnames,
            func.__code__.co_filename,
            func.__code__.co_name,
            func.__code__.co_firstlineno,
            func.__code__.co_lnotab,
            func.__code__.co_freevars,
            func.__code__.co_cellvars
        )
        # Create a callable function from code object
        return FunctionType(_func_code, func.__globals__)
    return wrapper
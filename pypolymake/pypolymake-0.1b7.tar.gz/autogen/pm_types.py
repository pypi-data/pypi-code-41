"""
Generate the types handled by pypolymake.
"""
atomic_types = {
    "Bool":
    {
        "name"  : "Bool",
        "simple": True,
        "module": None,
        "perl"  : "Bool",
        "cpp"   : "bool",
        "cython": "bool",
        "cppcython": "bool"
    },

    "Int":
    {
        "name"   : "Int",
        "simple" : True,
        "module" : None,
        "perl"   : "Int",
        "cpp"    : "int",
        "cython" : "int",
        "cppcython": "int"
    },

    "Float":
    {
        "name"   : "Float",
        "simple" : True,
        "module" : None,
        "perl"   : "Float",
        "cpp"    : "float",
        "cython" : "float",
        "cppcython": "float"
    },


    "String":
    {
        "name"   : "String",
        "simple" : True,
        "module" : None,
        "perl"   : "String",
        "cpp"    : "std::string",
        "cython" : "string",
        "cppcython": "string",
    },

    "Integer":
    {
        "parent" : "PmObject",
        "name"   : "Integer",
        "simple" : False,
        "module" : "Integer",
        "perl"   : "Integer",
        "cpp"    : "Integer",
        "cython" : "Integer",
        "cppcython": "pm_Integer"
    },

    "Rational":
    {
        "parent" : "PmObject",
        "name"   : "Rational",
        "simple" : False,
        "module" : "Rational",
        "perl"   : "Rational",
        "cpp"    : "Rational",
        "cython" : "Rational",
        "cppcython": "pm_Rational"
    },

    "QuadraticExtension":
    {
        "parent" : "PmObject",
        "name"   : "QuadraticExtension",
        "simple" : False,
        "module" : "QuadraticExtension",
        "perl"   : "QuadraticExtension<Rational>",
        "cpp"    : "QuadraticExtension",
        "cython" : "QuadraticExtension",
        "cppcython": "pm_QuadraticExtension"
    },

    "PairStringString":
    {
        "name"   : "PairStringString",
        "simple" : False,
        "module" : None,
        "perl"   : "Pair<String, String>",
        "cpp"    : "std::pair<std::string, std::string>",
        "cython" : "PairStringString",
        "cppcython" : "pair[string, string]",
    },

    "PairStringArrayString":
    {
        "name"   : "PairStringArrayString",
        "simple" : False,
        "module" : None,
        "perl"   : "Pair<String, Array<String>>",
        "cpp"    : "std::pair<std::string, Array<std::string>>",
        "cython" : "PairStringArrayString",
        "cppcython": "pair[string, pm_Array[string]]",
    }
}

Scalars = ["Int", "Float", "Integer", "Rational", "QuadraticExtension"]

module_data = {
# unique types
    "Integer":  None,
    "Rational": None,
    "IncidenceMatrix": None,

# vectors and matrices
    "Vector": Scalars,
    "Matrix": Scalars,

    "SparseMatrix":
    [
        "Int",
        "Rational"
    ],

# polynomials, rational functions

    "Polynomial":
    [
        ("Rational", "Int")
    ],

    "RationalFunction":
    [
        ("Rational", "Int")
    ],

# containers
    "Array":
    [
        "Bool",
        "Int",
        "Rational",
        "String",
        "ArrayInt",
        "ArrayString",
        "SetInt",
        "PairStringString",
        "MatrixInteger",
        "ArrayPairStringString",
        "PairStringArrayString",
        "PowerSetInt",
        "SetArrayInt"
    ],

    "Set":
    [
        "Int",
        "SetInt",
        "MatrixRational",
        "ArrayInt"
    ],

    "PowerSet":
    [
        "Int"
    ],

# maps
    "Map":
    [
        ("String", "String"),
        ("Rational", "Rational"),
        ("Int", "Int"),
        ("Integer", "Int")
    ],
}


def caml_to_python(s):
    if not s or not s[0].isupper():
        raise ValueError("not Caml case")
    cap = [i for i,j in enumerate(s) if j.isupper()]
    cap.append(len(s))
    return '_'.join(s[cap[i]].lower() + s[cap[i]+1:cap[i+1]] for i in range(len(cap)-1))
def python_to_caml(s):
    und = [0]
    und.extend(i for i,j in enumerte(s) if j == '_')
    und.append(len(s))
    return ''.join(s[und[i+1]].upper() + s[und[i+1]+1:und[i+1]] for i in range(len(und)-1))

def pm_types():
    r"""
    Construct the list of supported polymake types from the dictionaries ``atomic_types`` and
    ``module_data``.

    OUTPUT:

    A dictionary:

      name -> dictionary of properties
    """
    ans = atomic_types.copy()

    for scal in module_data["Vector"]:
        cython = "Vector{scal}".format(scal=scal)
        cppcython = "pm_Vector[{scal}]".format(scal=atomic_types[scal]["cppcython"])
        perl = "Vector<{scal}>".format(scal=scal)
        cpp = "Vector<{scal}>".format(scal=atomic_types[scal]["cpp"])

        ans[cython] = {
            "parent": "PmObject",
            "name"  : cython,
            "simple": False,
            "module": "Vector",
            "cython": cython,
            "cppcython": cppcython,
            "perl"  : perl,
            "cpp"   : cpp}

    for scal in module_data["Matrix"]:
        cppcython = "pm_Matrix[{scal}]".format(scal=atomic_types[scal]["cppcython"])
        cython = "Matrix{scal}".format(scal=scal)
        perl = "Matrix<{scal}>".format(scal=atomic_types[scal]["perl"])
        cpp = "Matrix<{scal}>".format(scal=atomic_types[scal]["cpp"])

        ans[cython] = {
            "parent": "PmMatrix",
            "name"  : cython,
            "simple": False,
            "module": "Matrix",
            "cython": cython,
            "cppcython": cppcython,
            "perl"  : perl,
            "cpp"   : cpp}

    for scal in module_data["SparseMatrix"]:
        cppcython = "pm_SparseMatrix[{scal}]".format(scal=atomic_types[scal]["cppcython"])
        cython = "SparseMatrix{scal}".format(scal=scal)
        perl = "SparseMatrix<{scal}>".format(scal=atomic_types[scal]["perl"])
        cpp = "SparseMatrix<{scal}>".format(scal=atomic_types[scal]["cpp"])

        ans[cython] = {
            "parent": "PmObject",
            "name"  : cython,
            "simple": False,
            "module": "SparseMatrix",
            "cython": cython,
            "cppcython": cppcython,
            "perl"  : perl,
            "cpp"   : cpp}

    for (coeff, exp) in module_data["Polynomial"]:
        cython = "UniPolynomial{coeff}{exp}".format(coeff=coeff, exp=exp)
        perl = "UniPolynomial<{coeff}, {exp}>".format(coeff=coeff, exp=exp)
        cpp = "UniPolynomial<{coeff}, {exp}>".format(coeff=atomic_types[coeff]["cpp"],
                                                     exp=atomic_types[exp]["cpp"])

        ans[cython] = {
            "parent": "PmObject",
            "name"  : cython,
            "simple": False,
            "module": "Polynomial",
            "cython": cython,
            "cppcython": "pm_{}".format(cython),
            "perl"  : perl,
            "cpp"   : cpp}

    for (coeff, exp) in module_data["RationalFunction"]:
        cython = "RationalFunction{coeff}{exp}".format(coeff=coeff, exp=exp)
        perl = "RationalFunction<{coeff}, {exp}>".format(coeff=coeff, exp=exp)
        cpp = "RationalFunction<{coeff}, {exp}>".format(coeff=atomic_types[coeff]["cpp"],
                                                        exp=atomic_types[exp]["cpp"])

        ans[cython] = {
            "parent": "PmObject",
            "name"  : cython,
            "simple": False,
            "module": "RationalFunction",
            "cython": cython,
            "cppcython": "pm_{}".format(cython),
            "perl"  : perl,
            "cpp"   : cpp}

    ans["IncidenceMatrixNonSymmetric"] = {
        "parent": "PmObject",
        "name"  : "IncidenceMatrixNonSymmetric",
        "simple": False,
        "module": "IncidenceMatrix",
        "cython": "IncidenceMatrixNonSymmetric",
        "cppcython": "pm_IncidenceMatrixNonSymmetric",
        "perl"  : "IncidenceMatrix<NonSymmetric>",
        "cpp"   : "IncidenceMatrix<NonSymmetric>"
        }

    # containers
    todo = set((c,s) for c in ("Array","Set","PowerSet") for s in module_data[c])

    while todo:
        todo2 = set()
        while todo:
            c, s = todo.pop()
            if s not in ans:
                todo2.add((c,s))
                continue
            
            data = ans[s]
            
            cppcython = "pm_{container}[{subtype}]".format(container=c, subtype=data["cppcython"])
            cython = "{container}{subtype}".format(container=c, subtype=s)
            perl = "{container}<{subtype}>".format(container=c, subtype=data["perl"])
            cpp = "{container}<{subtype}>".format(container=c, subtype=data["cpp"])

            ans[cython] = {
                "parent": "PmObject",
                "name"  : cython,
                "simple": False,
                "module": c,
                "cython": cython,
                "cppcython": cppcython,
                "perl"  : perl,
                "cpp"   : cpp}

        todo = todo2

    # map
    for s1,s2 in module_data["Map"]:
        data1 = ans[s1]
        data2 = ans[s2]
        cppcython = "pm_Map[{s1},{s2}]".format(s1=data1["cppcython"], s2=data2["cppcython"])
        cython = "Map{s1}{s2}".format(s1=s1,s2=s2)
        perl = "Map<{s1}, {s2}>".format(s1=data1["perl"], s2=data2["perl"])
        cpp = "Map<{s1}, {s2}>".format(s1=data1["cpp"], s2=data2["cpp"])

        ans[cython] = {
            "parent": "PmObject",
            "name" : cython,
            "simple": False,
            "module": "Map",
            "cython": cython,
            "cppcython": cppcython,
            "perl" : perl,
            "cpp": cpp}

    return ans

def pm_modules():
    ans = set(typ["module"] for typ in pm_types().values())
    ans.remove(None)
    return sorted(caml_to_python(x) for x in ans)

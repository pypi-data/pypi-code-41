import rdflib
import jinja2

SHACL_NS = "http://www.w3.org/ns/shacl#"

TEXT_REPORT_TEMPLATE = """Validation Report
Conforms: {{report.conforms}}
{% if not report.conforms -%}
Results ({{report.num_results}}):
{% for focus_node, results in report.results.items() -%}
Results for focus node {{focus_node}}:
{%- for result in results %}
  Path: {{result.path}}
  Severity: {{result.severity}}
  Constraint violation in {{result.constraint}}
  Message: {{result.message}}
  Source shape: {{result.source_shape}}
{% endfor %}
{% endfor %} 
{% endif %}
"""

def objectToText(o):
    if isinstance(o, rdflib.term.URIRef):
        v = str(o)
        if v.startswith(SHACL_NS):
            return v.replace(SHACL_NS,'')
        return v
    elif isinstance(o, rdflib.term.Literal):
        return str(o)
    return o


def reportDictFromGraph(result_ttl, shape_file=None):
    """
    Hack for getting conformance boolean.
    """

    R_CON = rdflib.URIRef(SHACL_NS + "conforms")
    R_RES = rdflib.URIRef(SHACL_NS + "result")
    R_MSG = rdflib.URIRef(SHACL_NS + "resultMessage")
    R_PTH = rdflib.URIRef(SHACL_NS + "resultPath")
    R_SEV = rdflib.URIRef(SHACL_NS + "resultSeverity")
    R_CST = rdflib.URIRef(SHACL_NS + "sourceConstraintComponent")
    R_FOC = rdflib.URIRef(SHACL_NS + "focusNode")
    R_SSP = rdflib.URIRef(SHACL_NS + "sourceShape")

    results = {
        "conforms":False,
        "num_results": 0,
        "results": {},
    }

    def resultDict(g, o):
        res = {
            "severity": objectToText(g.value(subject=o, predicate=R_SEV)),
            "path": objectToText(g.value(subject=o, predicate=R_PTH)),
            "message":objectToText(g.value(subject=o, predicate=R_MSG)),
            "constraint":objectToText(g.value(subject=o, predicate=R_CST)),
            "source_shape":objectToText(g.value(subject=o, predicate=R_SSP))
        }
        focus_node = str(g.value(subject=o, predicate=R_FOC))
        if not focus_node in results['results'].keys():
            results['results'][focus_node] = [res, ]
        else:
            results['results'][focus_node].append(res)

    sg = rdflib.Graph()
    if shape_file is not None:
        sg.parse(source=shape_file, format="turtle")
    rg = rdflib.Graph()
    rg.parse(data=result_ttl, format="turtle")
    for subject, predicate, obj in rg:
        if predicate == R_CON:
            results["conforms"] = (obj.lower() in ['true', ])
        elif predicate == R_RES:
            results["num_results"] += 1
            resultDict(rg, obj)
    return results


def reportDictToText(report):
    template = jinja2.Template(TEXT_REPORT_TEMPLATE)
    return template.render(report=report)

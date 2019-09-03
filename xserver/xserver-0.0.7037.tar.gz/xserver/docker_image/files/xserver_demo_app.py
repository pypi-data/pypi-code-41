import json,base64
files_data="""{"Dockerfile": "RlJPTSBoZXBvY2hlbi9weXdlYjoyMDE4CgpSVU4gcGlwIGluc3RhbGwgeHNlcnZlcg=="}"""
files_data=json.loads(files_data)
files_data={k:base64.b64decode(v) for k,v in files_data.items()}
from core import eamonn

q=eamonn.queue()

q.put(1)
q.put(2)
print(q.get())
print(q.get())
print(q.get(timeout=2))

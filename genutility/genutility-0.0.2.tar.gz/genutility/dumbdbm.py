from io import open
from dbm.dumb import _Database
from typing import TYPE_CHECKING

from genutility.os import lock as lock_file, unlock as unlock_file

if TYPE_CHECKING:
	from typing import List, IO
	LOCKOBJ = List[IO]

def wlock(dumbdbm):
	try: # check if there are any other locks already
		lockobj = lock(dumbdbm, True)
		unlock(lockobj)
	except PermissionError: # a (shared) lock already exists, don't do anything
		print("Cannot aquire exclusive lock, because shared lock was already found")
		return None
	else:
		print("Aquired shared lock")
		return lock(dumbdbm, False)

def lock(dumbdbm, exclusive=True, block=False):
	# type:(_Database, ) -> LOCKOBJ

	""" Locks dumbdbm for writing.
		Return a lock object which can be used to unlock the db again.
		Warning: The return value must be stored, otherwise the Python garbage collector
			might unlock the file.
	"""

	if not isinstance(dumbdbm, _Database):
		raise TypeError("Argument must be a dumbdbm")

	lockobj = []
	for attr in ("_datfile", ): # ("_dirfile", "_datfile", "_bakfile")
		path = getattr(dumbdbm, attr)
		fp = open(path, "rb")
		lockobj.append(fp)
		lock_file(fp, exclusive, block)

	return lockobj

def unlock(lockobj):
	# type: (Optional[LOCKOBJ], ) -> None

	""" Unlocks the dumbdbm given the `lockobj` obtained from `lock()`. """

	if lockobj is not None:
		for fp in lockobj:
			unlock_file(fp)
			fp.close()

if __name__ == "__main__":
	import shelve
	s = shelve.open("D:/test.shelve")
	input("opened")
	lockobj = wlock(s.dict)
	input("locked")
	print(s.get("asd", "not found"))
	input("read")
	s["asd"] = "qwe"
	input("written")
	unlock(lockobj)
	input("unlocked")

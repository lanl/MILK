
from pathlib import Path
from time import time
NTEST=10

#Test
t0 = time()
from MILK.MAUDText.callMaudText import run_MAUD
t1 = time()
for _ in range(0,NTEST):
    run_MAUD('/Users/dansavage/Documents/Maud.app',"mx8G",timeout=None, simple_call=True,ins_paths=str(Path().cwd() / "MAUDText.ins"))
t2 = time()

#Results
print(f"MILK import overhead: {t1-t0} seconds")
print(f"run time: {(t2-t1)/NTEST} seconds")
print(f"total time: {(t2-t1)/NTEST+t1-t0} seconds/call")

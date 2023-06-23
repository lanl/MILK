from time import time
NTEST=10

#Test
t0 = time()
from GSASIIscriptable import G2Project
t1 = time()
for _ in range(0,NTEST):
    gpx = G2Project(gpxfile='test.gpx')
    gpx.save('test_out.gpx')
    gpx.set_Controls('cycles',5)
    gpx.refine()
t2 = time()

#Results
print(f"GSASIIscriptable import overhead: {t1-t0} seconds")
print(f"run time: {(t2-t1)/NTEST} seconds")
print(f"total time: {(t2-t1)/NTEST+t1-t0} seconds/call")



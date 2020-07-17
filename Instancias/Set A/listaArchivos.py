import so
import re

a = so.listdir()
a.sort()

for i in a:
    print(re.findall(r"[0-9A-Za-z\-]+",i)[0])

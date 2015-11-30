#!/usr/bin/env python3

from sys import argv

for n in range(15,41,5):
    with open("fixedbandwidth-{}.matrix".format(n), "w") as f:
        print(n,n,file=f)
        pattern = [1,1,0,1,0,0,0,1] + [0]*(n-8)
        print(" ".join(map(str,(pattern[:-1] + [1]))),file=f)
        for i in range(1,n):
            print(" ".join(map(str,pattern[-i:] + pattern[:-i])),file=f)

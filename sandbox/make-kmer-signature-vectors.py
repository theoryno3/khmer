#! /usr/bin/env python
import sys
import khmer
import screed

KSIZE=5

def main(inp_name, outp_name, min_seq_len):
    outfp = open(outp_name, 'w')

    min_seq_len = int(min_seq_len)
    
    for record in screed.open(inp_name):
        if len(record.sequence) < min_seq_len:
            continue
        
        kt = khmer.new_ktable(KSIZE)
        kt.consume(record.sequence)

        x = []
        for i in range(4**KSIZE):
            x.append("%s" % (kt.get(i),))

        print >>outfp, " ".join(x)

if __name__ == '__main__':
    main(*sys.argv[1:4])
    

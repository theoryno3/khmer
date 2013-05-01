#! /usr/bin/env python
"""
Error correct reads based on a counting hash from a diginorm step.
Output sequences will be put in @@@.

% python scripts/error-correct-pass2 <counting.kh> <data1> [ <data2> <...> ]

Use '-h' for parameter help.
"""
import sys
import screed.fasta
import os
import khmer
from khmer.thread_utils import ThreadedSequenceProcessor, verbose_loader

from khmer.counting_args import build_construct_args

###

DEFAULT_COVERAGE = 20
DEFAULT_MAX_ERROR_REGION = 40


def main():
    parser = build_construct_args()
    parser.add_argument('input_filenames', nargs='+')
    parser.add_argument('--cutoff', '-C', dest='coverage',
                        default=DEFAULT_COVERAGE, type=int,
                        help="Diginorm coverage.")
    parser.add_argument('--max-error-region', '-M', dest='max_error_region',
                        default=DEFAULT_MAX_ERROR_REGION, type=int,
                        help="Max length of error region allowed")
    args = parser.parse_args()

    infiles = args.input_filenames

    K = args.ksize
    HT_SIZE = args.min_hashsize
    N_HT = args.n_hashes

    ht = khmer.new_counting_hash(K, HT_SIZE, N_HT)
    ht.set_use_bigcount(False)

    print 'creating hashtable'
    C = args.coverage
    max_error_region = args.max_error_region

    print "K:", K
    print "C:", C
    print "max error region:", max_error_region

    ### the filtering function.
    def process_fn(record):
        # read_aligner is probably not threadsafe?
        aligner = khmer.new_readaligner(ht, 1, C, max_error_region)
    
        name = record['name']
        seq = record['sequence']

        seq = seq.replace('N', 'A')

        grXreAlign, reXgrAlign = aligner.align(seq)

        keep = False
        if not grXreAlign or grXreAlign.startswith('-') or \
           grXreAlign.endswith('-'):
            keep = True
        else:
            graph_seq = grXreAlign.replace('-', '')
            mincount = ht.get_min_count(graph_seq)

            if mincount < C:
                keep = True
                seq = graph_seq
                    
        if keep:
            ht.consume(record.sequence)
            return record.name, record.sequence

        return None, None
        
    ### the filtering loop
    for infile in infiles:
        print 'filtering', infile
        outfile = os.path.basename(infile) + '.keepalign'
        outfp = open(outfile, 'w')

        tsp = ThreadedSequenceProcessor(process_fn)
        tsp.start(verbose_loader(infile), outfp)

        print 'output in', outfile

if __name__ == '__main__':
    main()

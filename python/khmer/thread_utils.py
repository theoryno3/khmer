"""
Utilities for dealing with multithreaded processing of short reads.
"""
import threading, Queue
import sys

def verbose_fasta_iter(filename):
    from screed.fasta import fasta_iter
    it = fasta_iter(open(filename))
    for n, record in enumerate(it):
        if n % 10000 == 0:
            print >>sys.stderr, '... filtering', n
        yield record

class SequenceGroup(object):
    def __init__(self, order, seqlist):
        self.order = order
        self.seqlist = seqlist

def is_pair(r1, r2):
    a = r1['name'].split('/')[0]
    b = r2['name'].split('/')[0]

    return (a==b)

class ThreadedSequenceProcessor(object):
    QUEUESIZE = 50
    
    def __init__(self, process_fn, n_workers, group_size, verbose=True):
        self.process_fn = process_fn
        self.n_workers = n_workers
        self.group_size = group_size
        
        self.inqueue = Queue.Queue(self.QUEUESIZE)
        self.outqueue = Queue.Queue(self.QUEUESIZE)

        self.worker_count = 0
        self.done = False
        self.verbose = verbose
        
        self.n_processed = 0
        self.n_written = 0
        self.bp_processed = 0
        self.bp_written = 0

    def start(self, inputiter, outfp):
        if self.verbose:
            print >>sys.stderr, 'starting threads'

        try:
            for i in range(self.n_workers):
                t = threading.Thread(target=self.do_process)
                self.worker_count += 1
                t.start()

            if self.verbose:
                print >>sys.stderr, 'starting writer'

            w = threading.Thread(target=self.do_write, args=(outfp,))
            w.start()

            if self.verbose:
                print >>sys.stderr, 'loading...'

            batch = []
            last_record = None
            i = 0
            for record in inputiter:
                if i >= self.group_size:
                    # keep pairs together in batches, to retain the interleaving.
                    if is_pair(record, last_record):
                        batch.append(record)
                        g = SequenceGroup(0, batch)
                        self.inqueue.put(g)

                        batch = []
                    else:
                        g = SequenceGroup(0, batch)
                        self.inqueue.put(g)
                        batch = [record]

                    i = 0
                else:
                    batch.append(record)

                last_record = record
                i += 1

            # submit last set of sequences
            if batch:
                g = SequenceGroup(0, batch)
                self.inqueue.put(g)

            if self.verbose:
                print >>sys.stderr, 'done loading in sequences'
            self.done = True

            w.join()
        finally:
            self.done = True

    def do_process(self):
        inq = self.inqueue
        outq = self.outqueue
        
        while not self.done or not inq.empty():
            try:
                g = inq.get(True, 1)
            except Queue.Empty:
                continue

            bp_processed = 0
            bp_written = 0

            keep = []
            for record in g.seqlist:
                name, sequence = self.process_fn(record)
                bp_processed += len(record['sequence'])
                if name:
                    bp_written += len(sequence)
                    keep.append((name, sequence))

            self.outqueue.put(SequenceGroup(0, keep))

            self.n_processed += len(g.seqlist)
            self.n_written += len(keep)
            self.bp_processed += bp_processed
            self.bp_written += bp_written
            
            if self.verbose and self.n_processed % 100000 == 0:
                print >>sys.stderr, "processed %d / wrote %d / removed %d" % \
                      (self.n_processed, self.n_written,
                       self.n_processed - self.n_written)
                print >>sys.stderr, "processed %d bp / wrote %d bp / removed %d bp" % \
                      (self.bp_processed, self.bp_written,
                       self.bp_processed - self.bp_written)

        # end of thread; exit, decrement worker count.
        self.worker_count -= 1

    def do_write(self, outfp):
        outq = self.outqueue
        while self.worker_count > 0 or not outq.empty():
            if self.done:
                break
            
            try:
                g = outq.get(True, 1)
            except Queue.Empty:
                continue

            for name, seq in g.seqlist:
                outfp.write('>%s\n%s\n' % (name, seq,))

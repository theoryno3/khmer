import khmer

def test_alignnocov():
   # test read alignment in situation where there is no match.
   
   ch = khmer.new_counting_hash(10, 1048576, 1)
   read = "ACCTAGGTTCGACATGTACC"
   aligner = khmer.new_readaligner(ch)
   for i in range(20):
      ch.consume("AGAGGGAAAGCTAGGTTCGACAAGTCCTTGACAGAT")
   ch.consume("ACCTAGGTTCGACATGTACC")
   graphAlign, readAlign = aligner.align(read)

   # should be the same
   assert readAlign ==   'ACCTAGGTTCGACATGTACC'
   assert graphAlign  == 'ACCTAGGTTCGACATGTACC'


def test_readalign():
   # test a clear example of an alignment
   
   ch = khmer.new_counting_hash(10, 1048576, 1)
   aligner = khmer.new_readaligner(ch, 1, 20)
   for i in range(20):
      ch.consume("AGAGGGAAAGCTAGGTTCGACAAGTCCTTGACAGAT")
   read =                "ACCTAGGTTCGACATGTACC"
   #                      ^^            ^  ^
      
   ch.consume("GCTTTTAAAAAGGTTCGACAAAGGCCCGGG")



   graphAlign, readAlign = aligner.align(read)

   assert readAlign ==  'ACCTAGGTTCGACATGTACC'
   assert graphAlign == 'AGCTAGGTTCGACAAGT-CC'
   #                                   ^  ^

def test_alignerrorregion():
   # test a situation where is no good alignment.
   
   ch = khmer.new_counting_hash(10, 1048576, 1)
   read = "AAAAAGTTCGAAAAAGGCACG"
   aligner = khmer.new_readaligner(ch, 1, 20, 11)
   for i in range(20):
      ch.consume("AGAGGGAAAGCTAGGTTCGACAAGTCCTTGACAGAT")
   ch.consume("ACTATTAAAAAAGTTCGAAAAAGGCACGGG")
   graphAlign, readAlign = aligner.align(read)

   assert readAlign == ''
   assert graphAlign  == ''

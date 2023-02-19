import unittest
import gzip
import struct

import FileNames, MyDirectories
from BinReader import BinReader


class Test(unittest.TestCase):

    def test1(self):
        
        filePathName = MyDirectories.getTempDir() / "test.gz"
        
        # Create fake data
        out = gzip.open( filePathName, "wb" )
        fmt = ">if"
        out.write( struct.pack( fmt, 3712, 18.3 ) )
        out.write( struct.pack( fmt, 1802, 17.3 ) )
        out.write( struct.pack( fmt, 5803, 14.3 ) )
        out.close()

        # Read fake data
        bufSizeInNRecs = 2
        br = BinReader( filePathName, fmt, bufSizeInNRecs )
        self.assertTrue( br.hasNext())
        rec = br.next()
        self.assertAlmostEqual(rec[0], 3712 )
        self.assertAlmostEqual(rec[1], 18.3, 2)
        self.assertTrue( br.hasNext() )
        rec = br.next()
        self.assertAlmostEqual(rec[0], 1802 )
        self.assertAlmostEqual(rec[1], 17.3, 2)
        self.assertTrue( br.hasNext() )
        rec = br.next()
        self.assertAlmostEqual(rec[0], 5803 )
        self.assertAlmostEqual(rec[1], 14.3, 2)
        self.assertFalse( br.hasNext() )
        br.close()

    def test2(self):
        
        filePathName = MyDirectories.getTempDir() / "test.gz"
        
        # Create fake data
        out = gzip.open( filePathName, "wb" )
        fmt = ">Qf"
        out.write( struct.pack( fmt, 1, 18.3 ) )
        out.write( struct.pack( fmt, 2, 17.3 ) )
        out.write( struct.pack( fmt, 2, 16.3 ) )
        out.write( struct.pack( fmt, 3, 15.3 ) )
        out.write( struct.pack( fmt, 3, 14.3 ) )
        out.write( struct.pack( fmt, 3, 13.3 ) )
        out.close()

        # Read fake data
        bufSizeInNRecs = 2
        br = BinReader( filePathName, fmt, bufSizeInNRecs )
        recs = br.readThrough(1)
        self.assertTrue( len( recs ) == 1 )
        recs = br.readThrough(2)
        self.assertTrue( len( recs ) == 2 )
        recs = br.readThrough(2)
        self.assertTrue( len( recs ) == 0 )
        self.assertTrue( br.hasNext() )
        recs = br.readThrough(3)
        self.assertFalse( br.hasNext() )
        self.assertTrue( len( recs ) == 3 )
        self.assertAlmostEqual(recs[0][1], 15.3, 4 )
        self.assertAlmostEqual(recs[2][1], 13.3, 4 )
        br.close()


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.test1']
    unittest.main()
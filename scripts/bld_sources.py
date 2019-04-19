#!/usr/bin/env python

import argparse
import os
import sys
import re
import numpy as np
import scipy.interpolate as _interp
#import matplotlib.pyplot as plt

from glob import glob
from os.path import abspath, join
#from seisflows.tools.graphics import plot_gll
#from seisflows.plugins.solver_io.fortran_binary import _read
#from seisflows.tools.tools import exists

pgmDesc = 'Builds multiple specFEM2d source files from template file'

def parseArgs():
   
    # Set up the run by parsing arguments
    note = '''NOTE: A file SOURCE_nnnn file is written for each source 
    from the supplied template, with xs and zs values substituted.
    Sources are generated in a straight line with the specified geometry, or
    are read from an existing 'sourcelist' file if 'nsources' is not given.
    '''
    ap = argparse.ArgumentParser( description='%(prog)s -- '+pgmDesc, epilog=note )

    ap.add_argument( 'template', 
        help='Template SOURCE file as for SpecFEM2D.')
    
    ap.add_argument('-l','--sourcelist',
        default='sources.dat',
        help='File with (x z) coordinates of sources, one pair per line. \
Will be written if --nsources option is supplied.')

    ap.add_argument('-n','--nsources',
        type=int, default=0,
        help='Number of sources to create.')

    ap.add_argument('-f','--freq',
        type=float, 
        help='Number of sources to create.')

    ap.add_argument('-b','--begin',
        type=float, nargs=2, metavar=('xbgn','zbgn'),
        default=[0.,0.],
        help='Coordinates of first source position.')

    ap.add_argument('-e','--end',
        type=float, nargs=2, metavar=('xend','zend'),
        default=[0.,0.],
        help='Coordinates of last source position.')

    return ap.parse_args()

class SourceBuilder(object):
    template = ''
    sourcelist = ''
    nsources = 0
    begin = None
    end = None
    
    def __init__(self,args):
        self.template = args.template
        self.sourcelist = args.sourcelist
        self.nsources = args.nsources
        self.begin = args.begin
        self.end = args.end
        self.freq = args.freq

    def __str__(self):
        str = 'SourceBuilder:\n  From template file: '+self.template \
            + '\n  Source list file: '+self.sourcelist \
            + '\n  Positions: nsources= %d'%self.nsources \
            + ', begin= (%f, %f)'%(self.begin[0],self.begin[1]) \
            + ', end= (%f, %f)'%(self.end[0],self.end[1])
        return str

    def run(self):
        nsrc = self.nsources
        if( nsrc > 0 ):
            xlist = np.linspace( self.begin[0], self.end[0], nsrc )
            zlist = np.linspace( self.begin[1], self.end[1], nsrc )
            if not os.path.exists(self.sourcelist): 
              fd = open(self.sourcelist,'w')
              for isrc in range(len(xlist)):
                print >>fd, '%f %f'%(xlist[isrc],zlist[isrc]) 
              fd.close()
            else:
              print 'Skipped over-writing existing file:',self.sourcelist
        else:
            xlist = []
            zlist = []
            with open(self.sourcelist) as fd:
                for line in fd:
                    x,z = map(float, line.split())
                    xlist.append(x)
                    zlist.append(z)
            fd.close()
            nsrc = len(xlist)

        # Write the individual SOURCE_nnnn files
        print 'Writing %d SOURCE files ...'%nsrc
        fbase = os.path.basename(self.template)
        for isrc in range(nsrc):
          x = xlist[isrc]
          z = zlist[isrc]
          fnm = fbase+'_%04d'%isrc
          fs = open(fnm,'w')
          with open(self.template) as ft:
              for line in ft:
                line = re.sub(r'^ *xs *=.*$', 'xs = %f'%x, line)
                line = re.sub(r'^ *zs *=.*$', 'zs = %f'%z, line)
                if self.freq is not None:
                    line = re.sub(r'^ *f0 *=.*$', 'f0 = %.2f'%self.freq, line)
                print >>fs, line.strip()
          ft.close()
          fs.close()

if __name__ == '__main__':

    bldr = SourceBuilder( parseArgs() )

    print bldr

    bldr.run()

#END

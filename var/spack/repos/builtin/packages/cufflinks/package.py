##############################################################################
# Copyright (c) 2013-2016, Lawrence Livermore National Security, LLC.
# Produced at the Lawrence Livermore National Laboratory.
#
# This file is part of Spack.
# Created by Todd Gamblin, tgamblin@llnl.gov, All rights reserved.
# LLNL-CODE-647188
#
# For details, see https://github.com/llnl/spack
# Please also see the NOTICE and LICENSE files for our notice and the LGPL.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License (as
# published by the Free Software Foundation) version 2.1, February 1999.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the IMPLIED WARRANTY OF
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the terms and
# conditions of the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##############################################################################
from spack import *


class Cufflinks(Package):
    """Cufflinks assembles transcripts, estimates their abundances, and tests
       for differential expression and regulation in RNA-Seq samples."""

    homepage = "http://cole-trapnell-lab.github.io/cufflinks"
    url      = "http://cole-trapnell-lab.github.io/cufflinks/assets/downloads/cufflinks-2.2.1.Linux_x86_64.tar.gz"

    version('2.2.1', '7e693d182dcfda8aeef8523219ea9ea7')

    def install(self, spec, prefix):
        mkdirp(prefix.bin)
        install('cuffcompare', prefix.bin)
        install('cuffdiff', prefix.bin)
        install('cufflinks', prefix.bin)
        install('cuffmerge', prefix.bin)
        install('cuffnorm', prefix.bin)
        install('cuffquant', prefix.bin)
        install('gffread', prefix.bin)
        install('gtf_to_sam', prefix.bin)

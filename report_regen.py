import sys
import Latex_Report
from pkg_resources import require
require("numpy == 1.13.1")
require("scipy == 0.19.1")


# results_location = sys.argv[1]
results_location = '/dls/science/groups/b01/BPM_bench_tests/00-d0-50-31-02-84/20-12-2019_T_08-59/'

Latex_Report.assemble_report(subdirectory=results_location)
print 'Report written to ', results_location



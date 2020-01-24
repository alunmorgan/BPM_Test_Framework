import sys, os
import Latex_Report
from pkg_resources import require
require("numpy == 1.16.6")
require("scipy == 1.2.2")


# results_location = sys.argv[1]
# results_location = '/dls/science/groups/b01/BPM_bench_tests/00-d0-50-31-02-84/20-12-2019_T_08-59/'
results_location = os.path.join('Z:', os.sep, 'BPM_bench_tests', '00-d0-50-31-02-84', '20-01-2020_T_15-33')
Latex_Report.assemble_report(subdirectory=results_location)
print 'Report written to ', results_location



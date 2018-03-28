from pkg_resources import require
require("numpy")
require("matplotlib")
require("scipy")
import sys
from Latex_Report.report_sections import assemble_report

assemble_report(sys.argv[1])

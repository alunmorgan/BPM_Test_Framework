from pylatex import Document, Section, Figure, NoEscape, Command, Tabular
from math import ceil
import os
import json
from pkg_resources import require
require("matplotlib")
import matplotlib.pyplot as plt
import numpy as np


def takespread(sequence, num):
    length = float(len(sequence))
    for i in range(num):
        yield sequence[int(ceil(i * length / num))]


class TexReport:

    """A LaTeX test report object with APIs for writing the BPM report.

    This class uses the pylatex Document class as a base, it creates an
    instance of this class and all of the report values are then written
    to that document. Custom APIs are used to make the BPM report writing 
    a bit simpler. 

    Attributes:
        doc (pylatex document Obj): LaTeX document that all text and figures
            for the report are written to. 
    """
    def __init__(self, subdirectory):
        """Initialise the test report and start to record the data.

        Creates an instance of the pylatex document object, this is stored as class
        data. Introduction text and contents pages are then set up for the report,
        so that they will all have the same standard front page and look. The report
        name will be saved as the "fname" argument. 

        Args: 
            subdirectory (str): The name of the folder the test data is stored..
            
        Returns:
            
        """
        with open(''.join((subdirectory, 'initial_BPM_state.json')), 'r') as read_data:
            test_system_state = json.load(read_data)
        logo_path = os.path.split(os.path.realpath(__file__))
        print test_system_state['mac_address'].replace(':', '-')
        self.doc = Document('/'.join((subdirectory,
                                      "".join(("BPMTestReport_", test_system_state['mac_address'].replace(':', '-'))))))
        self.doc.documentclass = Command(
            'documentclass',
            options=['a4paper, 11pt'],
            arguments=['article'],
        )
        self.doc.preamble.append(NoEscape(r'\newcommand\tab[1][1cm]{\hspace*{#1}}'))
        self.doc.preamble.append(NoEscape(r'\usepackage{fullpage}'))
        self.doc.preamble.append(NoEscape(r'\usepackage{graphicx}'))
        self.doc.append(NoEscape(r'\noindent'))
        self.doc.append(NoEscape(r'\large\textbf{Diamond Light Source Ltd} \hfill\large\textbf{Date: \today}'))
        self.doc.append(NoEscape(r'\\\normalsize Beam Diagnostics Group \hfill\\'))
        self.doc.append(NoEscape(''.join(
            (r'\\\\\includegraphics[width = 1\textwidth]{', '/'.join((logo_path[0], 'Logo.PNG')), r'}\\\\'))))
        self.doc.append(NoEscape(''.join((r'\section*{BPM Test Report for ', test_system_state['mac_address'], '}'))))

        intro_text = r'This is a test report for the, beam profile monitor electronics that are used at ' \
                     r'Diamond. ' \
                     r'In this document the different tests will be recorded in their own individual section. ' \
                     r'along with the specific parameters that are being tested and the test method used.\\\\'
        self.doc.append(NoEscape(intro_text))

        # Get the device names for the report
        device_names = []
        device_names.append('RF source is ' + test_system_state['rf_id'])
        device_names.append('Programmable attenuator is ' + test_system_state['prog_atten_id'])
        self.doc.append(NoEscape(r'\textbf{The controllable devices used in this test system are:}\\\\'))
        for i in device_names:
            self.doc.append(NoEscape(i + r'\\'))

        self.doc.append(NoEscape(r'\clearpage'))
        self.doc.append(NoEscape(r'\tableofcontents'))
        self.doc.append(NoEscape(r'\listoffigures'))

    def _decimate_list(self, signal, size):
        step = len(signal) / size
        step = ceil(step)
        items = range(step, len(signal) - step, step)
        subset = []
        subset.append(signal[0])
        for item in items:
            subset.append(signal[item])
        subset.append(signal[len(signal) - 1])
        return subset

    def setup_test(self, section_title, introduction_text, device_names, parameter_names):
        """Creates a new LaTeX section for a new test

        Creates a LaTeX section for the report, this will format and load into it 
        text to describe the test, the parameters and hardware used in the test, 
        and will also name the section. 
    
        Args: 
            section_title (str): The name that the new section of the report will be. 
            introduction_text (str): A paragraph of text that will introduce the test
                and what it hopes to achieve. 
            device_names (str list): A list of strings where a single string will 
                contain a hardware device name as well as what the device is. These
                will be copied over to the report.
            parameter_names (str list): A list of strings where a single string will 
                contain a parameter name as well as what the value. These
                will be copied over to the report.
                
        Returns:
            
        """
        self.doc.append(NoEscape(r'\clearpage'))
        with self.doc.create(Section(section_title)):
            self.doc.append(NoEscape(introduction_text))
            if parameter_names:
                self.doc.append(NoEscape(r'\\'))
                self.doc.append(NoEscape(r'\textbf{The parameters used in this test are:}\\\\'))
                for i in parameter_names:
                    self.doc.append(NoEscape(i + r'\\'))

    def add_figure_to_test(self, image_name, caption="", fig_width=0.8):
        """Adds a figure to the current section of the report

        Adds a pdf image in the form of a figure to the current section of the report. 
        The image name specifies the image, without the pdf extension. 

        Args: 
            image_name (str): The name of the image to be placed into the report.
            caption (str): The caption to be placed below the image.
            fig_width (float): The width of the figure in fraction of textwidth.

        Returns:
            
        """
        with self.doc.create(Figure(position='htbp')) as plot:
            plot.add_image(image_name, width=NoEscape(r'%s\textwidth' % fig_width))
            plot.add_caption(str(caption))
            plt.close()  # Close a figure window

    def add_table_to_test(self, format_string, data, headings, caption=""):
        """Adds a figure to the current section of the report

        Adds a pdf image in the form of a figure to the current section of the report. 
        The image name specifies the image, without the pdf extension. 

        Args: 
            format_string (str): defines the format of the table.
            data (array or list of list): The data to fill the table.
            headings (list of str): The column headings.
            caption (str): The caption to be placed below the table.

        Returns:
        """

        self.doc.append(NoEscape(r'\begin{figure}[htbp]'))
        self.doc.append(NoEscape(r'\centering'))
        self.doc.append(NoEscape(r'\caption{'+caption+'}'))
        table = Tabular(format_string)
        table.add_hline()

        for index in range(len(headings)):
            table.add_row(headings[index])

        table.add_hline()

        for index in range(len(data)):

            data[index] = np.round_(data[index], 2)
            data[index] = data[index].tolist()
            if len(data[index]) > 20:
                data[index] = self._decimate_list(data[index], 20)  # number of samples in table

        for iterations in range(len(data[0])):
            row = []
            for index in range(len(data)):
                row.append((data[index]).pop(0))
            table.add_row(row)
        table.add_hline()
        self.doc.append(table)
        self.doc.append(NoEscape(r'\end{figure}'))

    def create_report(self):
        """Creates the report
        
        Compiles the tex file written by this object and creates a pdf output of the report. 

        Args: 

        Returns:
            
        """
        self.doc.generate_pdf(clean_tex=False)
        self.doc.generate_pdf(clean_tex=False)
        self.doc.generate_pdf(clean_tex=False)

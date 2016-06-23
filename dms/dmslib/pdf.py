# Library to manipulate PDF files
#

import os
import re
import subprocess


class Pdf(object):
    def __init__(self, infile):
        """
        A library to extract images from PDFs.

        Uses pdftohtml behind the scenes, which works on PDFs containing one
        image per page. On some PDFs, this approach will fail

        A fallback (not implemented) is to use Imagemagic.
        """
        self.input_file = infile

    def parse(self):
        self._run_pdf_prog()

    def get_images(self):
        self.parse()
        return self._get_image_list_from_html()



    def _local(self, command):
        """ run a command (syntax is like the local() call in fab)
        """
        return subprocess.check_output(command, shell=True)

    def _run_pdf_prog(self):
        """
        The pdftohtml program does report progress back- extracting images
        can take about 1s per image.
        """
        tmp_dir = 'zzz'
        if os.path.exists(tmp_dir):
            self._local("rm -r " + tmp_dir)
        os.mkdir(tmp_dir)
        # TODO -q  to suppress output when it's working.
        #
        # TODO: Handle errors,
        #     e.g. missing dir 'zzz' => subprocess.CalledProcessError: Command
        #                               '/usr/bin/pdftohtml x..pdf zzz/z.html'
        #                               returned non-zero exit status -11
        # TODO: progress indicator to show that something's happening on long PDFs.
        #
        r = self._local("/usr/bin/pdftohtml " + self.input_file + " " + os.path.join(tmp_dir, "z.html"))
        # print "response was %s" % r

    def _get_image_list_from_html(self):
        """
        Get the list of images from the PDF, in the correct order, by reading
        the generated HTML file

        output from pdftohtml lists the page numbers created.
        work through zs.html looking for re.search('<img src="zzz/z-(\d+)_(\d).png"/>'

        returns: a list of the filenames (without path component)
        """
        html_file = "zzz/zs.html"  # based on 'z.html', with an extra 's'
        image_files = []
        with open(html_file, "r") as html:
            for line in html.readlines():
                m = re.search('<img src="zzz/(z-\d+_\d+.png)"/>', line)
                if m:
                    image_files.append(m.group(1))
        return image_files



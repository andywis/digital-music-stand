#!/usr/bin/env python

from dmslib.pdf import Pdf

input_file = "../Sample_music/Happy_Birthday/IMSLP46152-PMLP98386-Hill-GoodMorningtoAll1893.pdf"

# This file does NOT contain images; instead, the music is recorded in
# a different way
# input_file = "../Sample_music/Variations_theme_Sax_Quartet/IMSLP31910-PMLP72522-Variations_on_a_Theme__Sax_Quartet_.pdf"
# May need to use Imagemagick
# see http://stackoverflow.com/questions/331918/converting-a-pdf-to-a-series-of-images-with-python

# input_file = "../Sample_music/Rapsodie_for_Orchestra_and_Saxophone/IMSLP13914-Debussy_-_Rapsodie_for_Orchestra_and_Saxophone__sax._and_piano_.pdf"

pdf_parser = Pdf(input_file)
png_files = pdf_parser.get_images()
print png_files

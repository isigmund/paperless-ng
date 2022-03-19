import os
import shutil
import tempfile

from django.core.management import call_command
from django.test import override_settings
from django.test import TestCase
from documents.tests.utils import DirectoriesMixin
from pdfminer.high_level import extract_pages
from pdfminer.high_level import extract_text as pdfminer_extract_text


class TestGenerateAsnLabels(DirectoriesMixin, TestCase):
    def setUp(self) -> None:
        self.target = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.target)

        super(TestGenerateAsnLabels, self).setUp()

    @override_settings(PAPERLESS_EXTRACT_ASN_REGEX="<ASN:([0-9]{9})>")
    def _generate_labels(self, start_asn=1, pages=1):
        args = ["generate_asn_labels", self.target]
        if start_asn != 1:
            args += ["--asn_start", start_asn]
        if pages != 1:
            args += ["--pages", pages]

        call_command(*args)

    def test_generate_single_label_page(self):
        self._generate_labels()
        result = (
            "<ASN:000000001>\n\n<ASN:000000002>\n\n<ASN:000000003>\n\n<ASN:000000004>\n\n"
            "<ASN:000000005>\n\n<ASN:000000006>\n\n<ASN:000000007>\n\n<ASN:000000008>\n\n"
            "<ASN:000000009>\n\n<ASN:000000010>\n\n<ASN:000000011>\n\n<ASN:000000012>\n\n"
            "<ASN:000000013>\n\n<ASN:000000014>\n\n<ASN:000000015>\n\n<ASN:000000016>\n\n"
            "<ASN:000000017>\n\n<ASN:000000018>\n\n<ASN:000000019>\n\n<ASN:000000020>\n\n"
            "<ASN:000000021>\n\n<ASN:000000022>\n\n<ASN:000000023>\n\n<ASN:000000024>\n\n"
            "<ASN:000000025>\n\n<ASN:000000026>\n\n<ASN:000000027>\n\n<ASN:000000028>\n\n"
            "<ASN:000000029>\n\n<ASN:000000030>\n\n<ASN:000000031>\n\n<ASN:000000032>\n\n"
            "<ASN:000000033>\n\n<ASN:000000034>\n\n<ASN:000000035>\n\n<ASN:000000036>\n\n"
            "<ASN:000000037>\n\n<ASN:000000038>\n\n<ASN:000000039>\n\n<ASN:000000040>\n\n"
            "<ASN:000000041>\n\n<ASN:000000042>\n\n<ASN:000000043>\n\n<ASN:000000044>\n\n"
            "<ASN:000000045>\n\n<ASN:000000046>\n\n<ASN:000000047>\n\n<ASN:000000048>\n\n"
            "<ASN:000000049>\n\n<ASN:000000050>\n\n<ASN:000000051>\n\n<ASN:000000052>\n\n"
            "<ASN:000000053>\n\n<ASN:000000054>\n\n<ASN:000000055>\n\n<ASN:000000056>\n\n\x0c"
        )

        # check if resulting pdf contains exact text
        for file in os.listdir(self.target):
            if file.endswith(".pdf"):
                contained_text = pdfminer_extract_text(os.path.join(self.target, file))
        self.assertEqual(contained_text, result)

    def test_generate_10_label_pages(self):

        self._generate_labels(pages=10)

        # check if resulting pdf has exactely 10 pages
        for file in os.listdir(self.target):
            if file.endswith(".pdf"):
                number_of_pages = len(
                    list(extract_pages(os.path.join(self.target, file))),
                )
        self.assertEqual(number_of_pages, 10)

    def test_generate_labels_start_asn(self):

        self._generate_labels(start_asn=990000001)

        # check starting and ending asn on document
        for file in os.listdir(self.target):
            if file.endswith(".pdf"):
                contained_text = pdfminer_extract_text(os.path.join(self.target, file))
                first_asn = contained_text[0:15]
                last_asn = contained_text[
                    len(contained_text) - 18 : len(contained_text) - 3
                ]
            self.assertEqual(first_asn, "<ASN:990000001>")
            self.assertEqual(last_asn, "<ASN:990000056>")

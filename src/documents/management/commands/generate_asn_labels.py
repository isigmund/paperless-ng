import logging
import os

from fpdf import FPDF
from django.core.management.base import BaseCommand, CommandError


logger = logging.getLogger("paperless.management.generate_asn_labels")


class Command(BaseCommand):

    help = """
        Allows to generate a PDF file in th egiven target folder containing
        lables for ASNs (Archive Serial Numbers) that can be used to attach
        to documents before they are scanned and consumed.
        The ASN on these lables are then extracted and assigned to the
        document during consumption if the corresponding parameter
        PAPERLESS_EXTRACT_ASN_REGEX is used define a corresponding regex
    """.replace(
        "    ", ""
    )

    def add_arguments(self, parser):
        parser.add_argument("target")

        parser.add_argument(
            "-a",
            "--asn_start",
            default=1,
            type=int,
            required=False,
            help="The starting ASN used to produce labels",
        )

        parser.add_argument(
            "-f",
            "--format",
            default="<ASN:{:09}>",
            type=str,
            required=False,
            help="Format of the ASN generated "
            "defaults to <ASN:{:09}> which "
            "produces an ASN like <ASN:000000123>",
        )
        "ASN:{:09}"
        parser.add_argument(
            "-r",
            "--rows",
            type=int,
            default=14,
            required=False,
            help="Number of rows on a single label sheet defaults to 14",
        )
        parser.add_argument(
            "-c",
            "--columns",
            type=int,
            default=4,
            required=False,
            help="Number of columns on a single label sheet defaults to 4",
        )
        parser.add_argument(
            "-p",
            "--pages",
            type=int,
            default=1,
            required=False,
            help="Number of label sheets generated defaults to 1",
        )
        parser.add_argument(
            "-s",
            "--sheet_size",
            type=str,
            default="A4",
            required=False,
            help="Size of the label sheet "
            "defaults to A4 "
            "Supported formats : A3, A4, A5, letter, legal ",
        )
        parser.add_argument(
            "--color",
            nargs=3,
            type=int,
            default=[0, 0, 0],
            required=False,
            help="Color used to produce ASNs as RGB values "
            "defaults to 0 0 0 (black)",
        )

        parser.add_argument(
            "--fontsize",
            type=int,
            default=12,
            required=False,
            help="Fontsize used to produce ASNs defaults to 12",
        )

    def handle(self, *args, **options):

        target = options["target"]

        # check for valid and writable path
        if not os.path.exists(target):
            raise CommandError("That path doesn't exist")

        if not os.access(target, os.W_OK):
            raise CommandError("That path doesn't appear to be writable")

        asn_end = (
            options["asn_start"]
            + options["pages"] * options["rows"] * options["columns"]
            - 1
        )

        pdf = FPDF(orientation="Portrait", format=options["sheet_size"])
        pdf.set_font("helvetica", size=options["fontsize"])
        pdf.set_text_color(
            options["color"][0], options["color"][1], options["color"][2]
        )
        pdf.set_margin(0)

        cell_width = pdf.epw / options["columns"]
        cell_height = pdf.eph / options["rows"]

        asn = options["asn_start"]
        for page in range(0, options["pages"]):
            logger.info(f"page:{page}")
            pdf.add_page()
            for row in range(0, options["rows"]):
                for column in range(0, options["columns"]):
                    pdf.cell(
                        w=cell_width,
                        h=cell_height,
                        align="C",
                        txt=options["format"].format(asn),
                    )
                    asn += 1
                pdf.ln(cell_height)

        filename = options["format"].format(options["asn_start"])
        filename += "-"
        filename += options["format"].format(asn_end)
        filename += ".pdf"

        pdf.output(os.path.abspath(os.path.join(target, filename)))

        logger.info(f"Produced ASN labels from " "{options['asn_start']} to {asn_end}.")

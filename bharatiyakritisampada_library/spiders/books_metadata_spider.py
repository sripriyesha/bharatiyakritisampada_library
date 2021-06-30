import os
from pathlib import Path
import urllib.parse
import re
import time

import scrapy
from scrapy.http import Request


class BooksMetadataSpider(scrapy.Spider):
    name = "books_metadata"

    def __init__(self, page=None, *args, **kwargs):
        super(BooksMetadataSpider, self).__init__(*args, **kwargs)
        self.page = page
        with open(f"./links/links_page_{page}.txt", "rt") as f:
            self.start_urls = [url.strip() for url in f.readlines()]

    def parse(self, response):
        def get_next_div_text(key):
            return (
                response.xpath(
                    "//div[contains(text(), '"
                    + key
                    + "')]"
                    + "/following-sibling::div[1]"
                    + "//text()"
                )
                .get(default="")
                .replace("--", "")
                .strip()
            )

        def get_metadata(filename):
            return {
                "title": get_next_div_text("Title of The Text :"),
                "manuscript_id": response.xpath(
                    "//span[contains(text(), 'Manus Id (manus_code) :')]/following-sibling::text()"
                )
                .get(default="")
                .strip(),
                "mrc_name": response.xpath(
                    "//span[contains(text(), 'MRC Name :')]/following-sibling::a//text()"
                )
                .get(default="")
                .strip(),
                "institute_name": response.xpath(
                    "//span[contains(text(), 'Institute Name :')]/following-sibling::a//text()"
                )
                .get(default="")
                .strip(),
                "other_title": get_next_div_text("Other Title :"),
                "title_other_languages": get_next_div_text(
                    "Title in other languages :"
                ),
                "record_number": get_next_div_text("Record No. :"),
                "author": get_next_div_text("Author :"),
                "scribe": get_next_div_text("Scribe :"),
                "language": get_next_div_text("Language :"),
                "script": get_next_div_text("Script :"),
                "commentary": get_next_div_text("Commentary :"),
                "commentator": get_next_div_text("Commentator :"),
                "commentary_language": get_next_div_text(
                    "Language of the Commentary :"
                ),
                "script_commentary": get_next_div_text("Script Commentary :"),
                "sub_commentary": get_next_div_text("Sub - Commentary :"),
                "sub_commentator": get_next_div_text("Sub - Commentator :"),
                "sub_commentary_language": get_next_div_text(
                    "Language of the Sub - Commentary :"
                ),
                "sub_commentary_script": get_next_div_text(
                    "Script of the Sub - Commentary :"
                ),
                "bundle_number": get_next_div_text("Bundle No :"),
                "manuscript_number": get_next_div_text("Acc No./Man No :"),
                "digitization": get_next_div_text("Digitization :"),
                "complete_incomplete": get_next_div_text("Complete/Incomplete :"),
                "folios_number": get_next_div_text("No of Folios :"),
                "pages_number": get_next_div_text("No. of Pages :"),
                "missing_portion_folios": get_next_div_text("Missing Portion Folios :"),
                "size_length": get_next_div_text("Size Length :"),
                "size_width": get_next_div_text("Size Width :"),
                "size_height": get_next_div_text("Size Height :"),
                "material": get_next_div_text("Material :"),
                "condition": get_next_div_text("Condition :"),
                "subject_1": get_next_div_text("Subject 1 :"),
                "subject_2": get_next_div_text("Subject 2 :"),
                "subject_3": get_next_div_text("Subject 3 :"),
                "data_collection_date": get_next_div_text("Date of Data Collection :"),
                "manuscript_date_samvat": get_next_div_text(
                    "Date of Manuscript - Samvat :"
                ),
                "manuscript_date_century": get_next_div_text(
                    "Date of Manuscript - Century :"
                ),
                "illustrations": get_next_div_text("Illustrations :"),
                "illustrations_number": get_next_div_text("No of Illustrations :"),
                "illustrations_type": get_next_div_text("Illustrations Type :"),
                "illustrations_quality": get_next_div_text("Illustrations Quality :"),
                "manuscript_type": get_next_div_text("Manuscript Type :"),
                "landscape_view": get_next_div_text("Landscape view:"),
                "awarded_manuscript": get_next_div_text("Awarded Manuscript :"),
                "awarded_manuscript_order": get_next_div_text(
                    "Awarded manuscript order :"
                ),
                "lines_number_per_page": get_next_div_text("No. of line per page :"),
                "beginning_line": get_next_div_text("Beginning Line :"),
                "ending_line": get_next_div_text("Ending Line :"),
                "colophon": get_next_div_text("Colophon :"),
                "description": get_next_div_text("Description :"),
                "extra_remarks": get_next_div_text("Extra Remarks :"),
                "christian_era": get_next_div_text("Christian Era :"),
                "filename": filename,
            }

        pdf_webpage_link = (
            response.xpath("//div[@class='pull-right']//a//@href")
            .get(default="")
            .strip()
        )
        # print(pdf_webpage_link)

        filename = ""

        if pdf_webpage_link != "":
            title = get_next_div_text("Title of The Text :")
            manuscript_number = get_next_div_text("Acc No./Man No :")

            pdf_webpage_link_abs_url = response.urljoin(pdf_webpage_link)

            self.logger.info("getting pdf container webpage")
            self.logger.info(pdf_webpage_link_abs_url)

            filename = (title + "_" + manuscript_number).replace(" ", "_") + ".pdf"

            # yield Request(
            #     pdf_webpage_link_abs_url,
            #     callback=self.get_pdf,
            #     cb_kwargs=dict(filename=filename),
            #     dont_filter=True,
            # )

        self.logger.info("getting metadata")
        yield get_metadata(filename)

    def get_pdf(self, response, filename):
        self.logger.info("getting pdf url and requesting the file")

        # get the script tag containing the pdf url
        script_text = response.xpath("(//script)[1]/text()")
        # print(script_text.get(default="").strip())

        pattern = re.compile(r"/uploads/manusdata/.*\.pdf")
        file_relative_url = script_text.re(pattern)[0]

        file_abs_url = response.urljoin(file_relative_url)
        yield Request(
            file_abs_url,
            callback=self.save_file,
            cb_kwargs=dict(filename=filename),
            dont_filter=True,
        )

    def save_file(self, response, filename):
        Path(f"./books/page_{self.page}/").mkdir(parents=True, exist_ok=True)

        path = f"./books/page_{self.page}/" + filename
        self.logger.info("Saving file %s", path)
        with open(path, "wb") as f:
            f.write(response.body)

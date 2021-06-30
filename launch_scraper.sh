# launch script with page number as first argument

# for i in {16..383}
# do
    # python3 fetch_links_with_selenium.py "$i"
    scrapy crawl books_metadata -s JOBDIR=crawls/books_metadata_page_"$1" -o metadata/metadata_page_"$1".csv -a page="$1"
# done
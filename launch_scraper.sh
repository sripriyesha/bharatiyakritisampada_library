# launch script with page number as first argument

for i in {160..160}
do
    # python3 fetch_links_with_selenium.py "$i"
    scrapy crawl books_metadata -s JOBDIR=crawls/books_metadata_page_"$i" -o metadata/metadata_page_"$i".csv -a page="$i"
done
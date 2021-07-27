import sys
import urllib.request

for x in range(10, 29):
    url = (
        "https://www.bharatiyakritisampada.nic.in/uploads/manusdata/1585574/manuscript_000"
        + str(x)
        + ".JPG"
    )
    print(url)
    urllib.request.urlretrieve(url, "manuscript_000" + str(x) + ".jpeg")

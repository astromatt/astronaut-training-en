docs:
    @sphinx-build -j4 -b html . _build/

help:
    @sphinx-build -M help help help

clean:
    -rm -fr _book/
    -rm -fr _slides/

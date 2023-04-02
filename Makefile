all: scraper.o scraper

scraper.o: scraper.c
	clang -Wall  -c scraper.c -o scraper.o
	
scraper:
	clang -Wall  scraper.o -o scraper
	
	rm -f scraper.o

clean:
	rm -f scraper
	
	 
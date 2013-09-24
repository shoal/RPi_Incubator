CC = gcc
CFLAGS =  -std=c99 -I. -lbcm2835 -Wall -g
DEPS = 
OBJ = Adafruit_DHT.o

%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

Adafruit_DHT: $(OBJ)
	gcc -o $@ $^ $(CFLAGS)

clean:
	rm $(OBJ)

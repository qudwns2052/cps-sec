TARGET	=arp_spoofing
SRCS	=$(wildcard *.cpp)
OBJECTS	=$(SRCS:.cpp=.o)

CC=g++
$(TARGET) : $(OBJECTS)
	$(CC) $(TARGET_ARCH) $(OBJECTS) -lpcap -o $(TARGET)

main.o : main.cpp
arp.o : arp.cpp

clean:
	rm -f $(TARGET)
	rm -f *.o


default: compile
all: compile
compile:
	python -c "from py_compile import compile; compile('libest.py')"

clean:
	rm *.pyc

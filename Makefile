default: compile
all: compile
2: compile2
3: compile3

compile:
	python -c "from py_compile import compile; compile('libest.py')"

compile2:
	python2 -c "from py_compile import compile; compile('libest.py')"

compile3:
	python3 -c "from py_compile import compile; compile('libest.py')"
	mv ./__pycache__/*.pyc .

clean:
	rm *.pyc
	rm -rf ./__pycache__

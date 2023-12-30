# use `nano makefile` to edit this file
# run `make`
# run `make [target name]` e.g., make run_test

target: print

print:
	echo "Makefile's working."

infra_setup:
	sh infra*sh
	sh app-dev*sh

cleanup:
	sh cleanup*sh

run_test:
	sh test/test.sh
	python test/test.py

# For Development

dev_setup:
	sh app-dev.sh

dev_cleanup:
	sh app-dev-cleanup.sh







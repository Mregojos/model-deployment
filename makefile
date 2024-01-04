# use `nano makefile` to edit this file
# run `make`
# run `make [target name]` e.g., make run_test

target: print

print:
	echo "Makefile's working."

# Deployment and Development

run_infra:
	# source env*
	sh infra*sh
	sh app-dev-multimodal.sh

run_cleanup:
	sh cleanup*sh

run_test:
	sh test/test.sh
	python test/test.py

# For Development (with its own dedicated database)

run_dev:
	sh app-dev.sh

run_dev_cleanup:
	sh app-dev-cleanup.sh


# For Development (Version II)

run_dev_ii:
	sh app-dev-ii.sh

run_dev_ii_cleanup:
	sh app-dev-ii-cleanup.sh

# For CLI Development

run_dev_cli:
	sh app-dev-cli.sh

run_dev_cli_cleanup:
	sh app-dev-cli-cleanup.sh

# use `nano makefile` to edit this file
# run `make`
# run `make [target name]` e.g., make run_test

target: print

print:
	echo "Makefile's working."

# Deployment

run_infra:
	# source env*
	sh infra*sh

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


# For Multimodal App Collection

run_apps:
	sh app-collection.sh

run_apps_cleanup:
	sh app-collection-cleanup.sh

# For Multimodal in Terminal (CLI)

run_cli:
	# cd app-cli
	# README.md

run_cli_cleanup:
	sh app-cli/app-cli-cleanup.sh

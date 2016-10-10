.PHONY: yapf
yapf:
	yapf -ri spider/

.PHONY: run
run:
	python spider/cli.py run

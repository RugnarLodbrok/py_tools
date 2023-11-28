MAKE_SCRIPTS = make_scripts.sh
CODE = tests py_tools

check: format lint test

lint:
	@source $(MAKE_SCRIPTS) ; \
	lint_code $(CODE)
format:
	@source $(MAKE_SCRIPTS) ; \
	format_code $$(pwd)
test:
	@source $(MAKE_SCRIPTS) ; \
	test_code $(ARG) $(K)
test-fast:
	@source $(MAKE_SCRIPTS) ; \
	test_code  $(ARG) $(K) --exitfirst
test-failed:
	@source $(MAKE_SCRIPTS) ; \
	test_code  $(ARG) $(K) --last-failed

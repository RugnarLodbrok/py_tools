set CODE="tests py_tools"
set LINT_JOBS=4
flake8 --jobs %LINT_JOBS% --statistics --show-source "%CODE%" || exit /b
pylint --jobs %LINT_JOBS% --rcfile=pyproject.toml "%CODE%" || exit /b
mypy "%CODE%" || exit /b
black --check "%CODE%" || exit /b
ruff "%CODE%" --show-source --show-fixes -n || true || exit /b
pytest --dead-fixtures --dup-fixtures "%CODE%" || exit /b

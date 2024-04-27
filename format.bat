set CODE="tests py_tools"
autoflake --recursive --in-place --remove-all-unused-imports "%CODE%" || exit /b
isort "%CODE%" || exit /b
black  "%CODE%" || exit /b
unify --in-place --recursive "%CODE%" || exit /b

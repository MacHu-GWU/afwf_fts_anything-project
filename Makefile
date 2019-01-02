include ./make/python_env.mk


.PHONY: build_wf
build_wf: ## ** Build Alfred Workflow
	( \
		rm -r ./workflow; \
		mkdir ./workflow; \
		${BIN_PIP} install Alfred-Workflow --target=./workflow; \
		${BIN_PIP} install . --target=./workflow/lib; \
		cp ./main.py ./workflow/main.py; \
		cp ./icon.png ./workflow/icon.png; \
	)

# ilpcoin

A toy implementation of a crypto currency that solves integer linear programs for its proof-of-work.

See finalreport.pdf for the full description. Sections 1 and 2 give a brief overview, and section 3 discusses a theoretical model for using such a proof-of-work scheme on a block chain.

To run, just do:

```
pip3 install --editable .
```
in the root of the project.

You can then directly invoke the `console_scripts` available in setup.cfg to run the different components. For example, to run the queue, execute

```
ilp-queue <args>
```

or to run the verifier, run

```
verifier <args>
```

To run the test suite (all files beginning matching `test_<module_name>.py`), run
```
pytest
```
in the root directory.

## Documentation

See `docs/` for complete documentation and API reference. To see pretty rendered HTML, go [here](https://htmlpreview.github.io/?https://raw.githubusercontent.com/lsingh123/ilpcoin/main/docs/index.html).

## Paper

See the paper [here](https://github.com/lsingh123/ilpcoin/blob/main/ilpcoin_paper.pdf) for details.

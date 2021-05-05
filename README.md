# ilpcoin

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

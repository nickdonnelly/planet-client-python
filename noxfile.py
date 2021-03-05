import nox

nox.options.stop_on_first_error = True
nox.options.reuse_existing_virtualenvs = True
nox.options.keywords = "test + check"

source_files = ("planet", "tests", "setup.py", "noxfile.py")


@nox.session(python=["3.7", "3.8", "3.9"])
def test(session):
    session.install("-e", ".[test]")

    options = session.posargs
    if '-x' in options and '--no-cov' not in options:
        options.append("--no-cov")

    session.run("pytest", "-v", *options)


@nox.session
def lint(session):
    session.install("-e", ".[lint]")

    session.run("flake8", *source_files)


@nox.session()
def docs(session):
    session.install("--upgrade", "-e", ".[docs]")

    session.run("mkdocs", "build")


@nox.session()
def watch(session):
    session.install("--upgrade", "-e", ".[docs]")

    session.run("mkdocs", "serve")

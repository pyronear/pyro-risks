# Contributing to Pyro-Risks

Everything you need to know to contribute efficiently to the project.

## Project structure and conventions

### Codebase structure

-   [pyro-risks](https://github.com/pyronear/pyro-risks/tree/master/pyro_risks) - the pyro-risks library
-   [examples](https://github.com/pyronear/pyro-risks/tree/master/scripts) - examples scripts
-   [test](https://github.com/pyronear/pyro-risks/blob/master/test) - python unit tests

### Continuous Integration

This project uses the following integrations to ensure proper codebase maintenance:

-   [Github Actions](https://docs.github.com/en/free-pro-team@latest/actions/guides/about-continuous-integration) - run workflows for building and testing the package
-   [Codacy](https://www.codacy.com/) - analyzes commits for code quality
-   [Codecov](https://codecov.io/) - reports back coverage results

As a contributor, you will only have to ensure coverage of your code by adding appropriate unit testing of your code.

### Style conventions

-   **Code**:
    -   Setup the `__all__` special variable for each module
    -   Use type hints for every functions ([type hints cheat sheet](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html))
    -   Format your code using the [black](https://github.com/psf/black) auto-formatter
    -   Ensure to document your code using type hints compatible docstrings. In doing so, please follow [Google-style](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) so it can ease the process of documentation later.

-   **Commit message**: please follow [Udacity guide](http://udacity.github.io/git-styleguide/)

## Contributing to the project 

In order to contribute to project, you will first need to **set up your *pyro-risks* development environment** and then follow the **contributing workflow** and the **code & commit guidelines**.

-   [Project Setup](#project-setup): *fork the project and install dependencies in a well-encapsulated development environment*

    1.  [**Create a virtual environment**](#create-a-virtual-environment) to avoid collision with our OS and other projects
    2.  [**Fork the pyro-risks project**](#fork-the-repository) to be able to start working on a local copy of the project
    3.  [**Set origin and upstream remotes**](#set-origin-and-upstream-remotes-repositories) repositories: 
    4.  [**Install project dependencies**](#install-project-dependencies)

-   [Contributing workflow](#contributing-workflow): *pull remote changes/new contributions and push your contributions to the original project*

-   [Follow the repository style conventions](#style-conventions)

### Project Setup

* * *

#### 1. Create a virtual environment

<br>

-   We are going to create a python3.6 virtual environment dedicated to the `pyro-risks` project using [conda](https://docs.conda.io/en/latest/) as an environment management system. Please open a terminal and follow the instructions.

    ```shell
    conda create --name pyro-risks python=3.6 anaconda 
    conda activate pyro-risks
    ```

#### 2. Fork the repository

<br>

-   We are going to get a local copy of the remote project (*fork*) and set remotes so we stay up to date to recent contributions.

    1.  **Create a fork** by clicking on the **fork button** on the current repository page

    2.  Clone *your* fork locally.

        ```shell
        # change directory to one for the project
        cd /path/to/local/pyronear/project/

        # clone your fork. replace YOUR_USERNAME accordingly
        git clone https://github.com/YOUR_USERNAME/pyro-risks.git

        # cd to pyro-risks
        cd pyro-risks
        ```

#### 3. Set origin and upstream remotes repositories

<br>

1.  Configure your fork `YOUR_USERNAME/pyro-risks` as `origin` remote

2.  Configure `pyronear/pyro-risks repository` as `upstream` remote

    ```shell
    # add the original repository as remote repository called "upstream"
    git remote add upstream https://github.com/pyronear/pyro-risks.git

    # verify repository has been correctly added
    git remote -v

    # fetch all changes from the upstream repository
    git fetch upstream

    # switch to the master branch of your fork
    git checkout master

    # merge changes from the upstream repository into your fork
    git merge upstream/master
    ```

#### 4. Install project dependencies

<br>

```shell
# install dependencies
pip install black
pip install -r requirements.txt

# install current project in editable mode,
# so local changes will be reflected locally (ie:at import)
pip install -e .
```

### Contributing workflow

* * *

Once the project is well set up, we are going to detail step by step a usual contributing workflow.

1.  Merge recent contributions onto master (do this frequently to stay up-to-date)

    ```shell
    # fetch all changes from the upstream repository
    git fetch upstream

    # switch to the master branch of your fork
    git checkout master

    # merge changes from the upstream repository into your fork
    git merge upstream/master
    ```

    Note: Since, we are going to create features on separate local branches so they'll be merged onto **original project remote master** via pull requests, we may use **pulling** instead of fetching & merging. This way our **local master branch** will reflect **remote original project**. We don't expect to make changes on local master in this workflow so no conflict should arise when merging:

    ```shell
    # switch to local master
    git checkout master

    #  merge remote master of original project onto local master
    git pull upstream/master
    ```

2.  Create a local feature branch to work on

    ```shell
    # Create a new branch with the name of your feature
    git checkout -b feature-branch
    ```

3.  Commit your changes (remember to add unit tests for your code). Feel free to interactively rebase your history to improve readability. Follow the style guide See [Style Conventions](#style-conventions) to follow guidelines.

4.  Rebase your feature branch so that merging it will be a simple fast-forward that won't require any conflict resolution work.

    ```shell
    # Switch to feature branch
    git checkout feature-branch

    # Rebase on master
    git rebase master
    ```

5.  Push your changes on remote feature branch.

    ```shell
    git checkout feature-branch

    # Push first time (we create remote branch at the same time)
    git push -u origin feature-branch

    # Next times, we simply push commits
    git push origin
    # Format your code with 
    black /path/to/local/pyronear/project/pyro-risks/
    ```

6.  When satisfied with your branch, open a [PR](https://help.github.com/en/articles/creating-a-pull-request-from-a-fork) from your fork in order to integrate your contribution to original project.

## Opening an issue

Use Github [issues](https://github.com/pyronear/pyro-risks/issues) for feature requests, or bug reporting. When doing so, use issue templates whenever possible and provide enough information for other contributors to jump in.

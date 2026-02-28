# GDatalog

**Generative Datalog with Stable Negation**

GDatalog is a Python framework for declarative probabilistic programming using Datalog with stable model semantics.
It extends Answer Set Programming (ASP) with probabilistic inference capabilities through **delta terms** (`@delta`), enabling reasoning over random variables and uncertainty.


## Features

- **Probabilistic Datalog**: Combine declarative logic programming with probability distributions
- **Stable Model Semantics**: Full support for negation as failure and multiple stable models
- **Delta Terms**: Built-in probabilistic primitives for modeling randomness
- **Statistical Analysis**: Run programs multiple times to compute frequency distributions and probabilities
- **Smart Enumeration**: Efficient probabilistic enumeration of all possible outcomes
- **ASP Integration**: Built on top of [Clingo](https://potassco.org/clingo/), a powerful ASP solver
- **REST API Server**: Serve your probabilistic programs via HTTP
- **CLI Tools**: Easy-to-use command-line interface for running and analyzing programs


## Installation

Requires Python 3.11+

```bash
pip install gdatalog
```

Or using Poetry:

```bash
poetry add gdatalog
```


## Quick Start

### Basic Example: Flipping a Coin

Create a file `flip-coin.asp`:

```prolog
coin(1..3).

head(C, @delta(flip(1,3), C)) :- coin(C).

#show.
#show heads(C) : heads(C,1).
#show tails(C) : heads(C,0).
```

Run the program:

```bash
gdatalog -f flip-coin.asp run
```

This will execute the program once, showing one possible outcome.
The `@delta(flip(1,3), C)` call represents a coin flip with probability 1/3 for heads.


### Running Multiple Times

Analyze the probabilistic distribution by running the program 1000 times:

```bash
gdatalog -f flip-coin.asp repeat -n 1000
```

This generates statistics showing the frequency of different outcomes, which approximate the true probabilities.


## Core Concepts

### Delta Terms

Delta terms (`@delta`) are the core mechanism for introducing randomness.
The syntax is:

```prolog
@delta(function_name(args...), signature...)
```

**Built-in Delta Functions:**

- `flip(n, d)`: Bernoulli distribution with probability `n/d` for success.
- `mass(options...)`: Categorical distribution over multiple outcomes.
- `randint(a, b)`: Uniform discrete distribution between `a` and `b` (inclusive).
- `binom(n, p_num, p_den)`: Binomial distribution with `n` trials and probability `p_num/p_den`.
- `poisson(lambda_num, lambda_den)`: Poisson distribution with rate `lambda_num/lambda_den`.
- `wikipedia_neighbors(page)`: Number of outgoing links from a Wikipedia page.
- `wikipedia_neighbor(page, index)`: Title of the i-th outgoing link from a Wikipedia page.

**Extensibility**

GDatalog is designed to be extensible.
You can easily register custom delta functions to support domain-specific distributions or integrate with external data sources.
This is achieved by registering Python functions that return a value and its associated probability.


### Example: Probabilistic Graph Coloring

```prolog
color(red). color(green). color(blue).

node(1..4).
edge(X,Y) :- node(X), node(Y), X < Y.

% Each edge has a 5% chance of being ignored
removed(X,Y,@delta(flip(5,100), X,Y)) :- edge(X,Y).

% Each node gets exactly one color
{assign(X,C) : color(C)} = 1 :- node(X).

% Constraint: adjacent nodes must have different colors (unless edge is removed)
:- edge(X,Y), not removed(X,Y,1), assign(X,C), assign(Y,C).

#show.
#show colorable.
```


### Example: Conditional Randomness

The virus spread example shows how randomness can be conditional:

```prolog
infected(a,1).

% A virus spreads from infected to connected nodes with 10% probability
infected(Y,@delta(flip(10,100), X,Y)) :- infected(X,1), connection(X,Y).

healthy(X) :- router(X), not infected(X,1).

% Constraint: If two neighbors are both healthy, the network is valid
:- healthy(X), healthy(Y), connection(X,Y).

#show.
#show infected(X) : infected(X,1).
```


## API Usage

### Python API

```python
from gdatalog.program import Program, Repeat

# Define a program
program = Program("""
coin(1..3).
head(C, @delta(flip(1,3), C)) :- coin(C).
""")

# Run once
result = program.sms()
print(f"Delta terms: {result.delta_terms}")
print(f"Models: {result.models}")

# Run multiple times for statistics
repeat = Repeat.on(program, times=1000)
freq = repeat.sets_of_stable_models_frequency()

for models, (probability, model_list) in freq.values():
    print(f"Outcome (probability {probability}): {model_list}")
```


### Smart Enumeration

For efficient probabilistic exploration, use smart enumeration:

```python
repeat = Repeat.on(program, times=1000, smart=True)
```

Smart enumeration exhaustively explores all possible outcomes without repetition, then assigns probabilities based on delta term probabilities.


## Command Line Interface

### Main Options

```bash
gdatalog -f <file1> -f <file2> ... [options] <command>
```

**Global Options:**
- `-f, --filename`: Program files to load (can be specified multiple times)
- `-n, --number-of-models`: Maximum number of stable models to compute (0 for all)
- `--debug`: Don't minimize errors in output

### Commands

#### `run`

Execute the program once and display the result.

```bash
gdatalog -f program.asp run
```

Output shows:
- Delta terms (probabilistic choices made)
- Probability of this specific outcome
- All stable models resulting from those choices

#### `repeat`

Run the program multiple times and analyze the distribution.

```bash
gdatalog -f program.asp repeat -n 1000 -u 100
```

**Options:**
- `-n, --number-of-times`: Number of runs (default: 1000)
- `-u, --update-frequency`: Update display every N runs (default: 100)
- `-s, --smart-enumeration`: Use smart enumeration for exhaustive exploration

Output shows a table with:
- Probability of each outcome
- Number of stable models per outcome
- List of all stable models

#### `server`

Run as a REST API server.

```bash
gdatalog server -p 8000
```

**Options:**
- `-p, --port`: Port to listen on (default: 8000)
- `--reload`: Auto-reload on source changes (development mode)

The server accepts JSON requests with programs and options, making it easy to integrate GDatalog into web applications.

## Examples

The `examples/` directory contains several demonstrations:

- **flip-coin.asp**: Simple coin flip
- **flip-coins-until-tail.asp**: Sequence of flips until a specific outcome
- **colorable.asp**: Probabilistic graph coloring problem
- **virus-spread.asp**: Epidemic modeling with conditional probabilities
- **flip-dimes-then-quarters.asp**: Sequential probabilistic events
- **earthquakes-and-burglaries.asp**: Bayesian network reasoning
- **random-walk.asp**: Probabilistic path generation
- **meteors.asp**: Astronomical event simulation

Run any example:

```bash
gdatalog -f examples/flip-coin.asp run
gdatalog -f examples/colorable.asp repeat -n 1000
gdatalog -f examples/virus-spread.asp repeat -n 500
```

## Testing

Run the test suite:

```bash
pytest
```

Tests cover:
- Delta term functionality
- Probabilistic inference
- Conditional randomness
- Complex logic programs with negation
- Frequency analysis

## Architecture

### Key Components

- **Program**: Core class representing a Datalog program with delta terms
- **DeltaTermsContext**: Manages probabilistic choices during grounding
- **SmsResult**: Result of a single program execution (stable models + delta terms)
- **Repeat**: Manages multiple executions for statistical analysis
- **SmartRepeat**: Exhaustive probabilistic exploration

### Dependencies

- [Clingo](https://potassco.org/clingo/): ASP solver
- [Dumbo ASP](https://github.com/alviano/dumbo-asp): ASP utilities
- [Typer](https://typer.tiangelo.com/): CLI framework
- [Rich](https://rich.readthedocs.io/): Beautiful terminal output
- [FastAPI](https://fastapi.tiangolo.com/): HTTP server
- [SciPy](https://scipy.org/): Statistical functions

## Technical Details

### How Stable Models Work

GDatalog computes the **stable models** of a Datalog program, which are answer sets that satisfy:

1. All facts and rules are true
2. Negation as failure is correctly applied
3. The model is minimal (no proper subset also satisfies the program)

With delta terms, each stable model is paired with probabilistic choices that determined its outcome.

### Probability Computation

Probabilities are computed as fractions and displayed as:
- **Exact fraction**: e.g., 3/8
- **Approximate decimal**: e.g., ~0.375

When running a program multiple times, observed frequencies approximate the true probabilistic distribution.

## Contributing

GDatalog is open-source and welcomes contributions. For more information, see the LICENSE file.

## References

- **Answer Set Programming**: [Handbook of Knowledge Representation](https://www.elsevier.com/books/handbook-of-knowledge-representation/van-harmelen/978-0-444-52211-5)
- **Clingo**: [https://potassco.org/clingo/](https://potassco.org/clingo/)
- **Probabilistic Logic Programming**: [A recent survey](https://arxiv.org/abs/1902.01046)

## Citation

If you use GDatalog in research, please cite:

```bibtex
@software{gdatalog,
  title={GDatalog: Generative Datalog with Stable Negation},
  author={Alviano, Mario},
  year={2024}
}
```

## License

See LICENSE file for details.

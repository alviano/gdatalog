import clingo
from dumbo_asp.primitives.atoms import GroundAtom
from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware

from gdatalog.program import Program


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_credentials=False,
    allow_methods=["POST"],
    allow_headers=["*"],
)


def term_to_json(term: clingo.Symbol):
    res = {
        "str": str(term),
        "type": str(term.type),
    }
    if term.type == clingo.SymbolType.Number:
        res["number"] = term.number
    elif term.type == clingo.SymbolType.String:
        res["string"] = term.string
    elif term.type == clingo.SymbolType.Function:
        res["function"] = term.name
        res["arguments"] = [term_to_json(t) for t in term.arguments]
    return res


def atom_to_json(atom: GroundAtom):
    return {
        "str": str(atom),
        "predicate": atom.predicate,
        "arguments": [
            term_to_json(term) for term in atom.arguments
        ],
    }


@app.post("/run/")
async def _(request: Request):
    json = await request.json()
    try:
        max_stable_models = int(json["max_stable_models"]) if "max_stable_models" in json else 1
        program = Program(json["program"], max_stable_models=max_stable_models)

        sms = program.sms()

        return {
            "state": str(sms.state),
            "models": [[atom_to_json(atom) for atom in model] for model in sms.models],
            "delta_terms": [str(delta_term) for delta_term in sms.delta_terms],
        }
    except Exception as e:
        return {
            "error": str(e)
        }


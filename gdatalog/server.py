from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware

from gdatalog.program import Program


def endpoint(router, path):
    def wrapper(func):
        @router.post(path)
        async def wrapped(request: Request):
            json = await request.json()
            try:
                return await func(json)
            except Exception as e:
                return {
                    "error": str(e)
                }
        return wrapped
    return wrapper


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=False,
    allow_methods=["POST"],
    allow_headers=["*"],
)


@app.post("/run/")
async def _(request: Request):
    json = await request.json()
    try:
        max_stable_models = int(json["max_stable_models"]) if "max_stable_models" in json else 1
        program = Program(json["program"], max_stable_models=max_stable_models)

        sms = program.sms()

        return {
            "state": str(sms.state),
            "models": [[str(atom) for atom in model] for model in sms.models],
            "delta_terms": [str(delta_term) for delta_term in sms.delta_terms],
        }
    except Exception as e:
        return {
            "error": str(e)
        }


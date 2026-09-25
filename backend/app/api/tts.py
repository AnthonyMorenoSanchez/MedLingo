from fastapi import APIRouter, HTTPException, Request

router = APIRouter()

@router.get("/tts/providers",response_model=list[dict])
def providers(request: Request):
    return [{"id":"web_speech","label":"Device voices (offline)","enabled":True}]+[{"id":p.id,"label":p.id,"enabled":True} for p in request.app.state.plugins if p.id=="cloud_tts"]
@router.post("/tts/synthesize",response_model=dict)
async def synthesize(request: Request,body: dict):
    plugin=next((p for p in request.app.state.plugins if p.id=="cloud_tts"),None)
    if not plugin:raise HTTPException(409,"Cloud speech is disabled")
    try:return await plugin.synthesize(body)
    except Exception as e:raise HTTPException(502,"Speech provider could not synthesize audio. Check credentials and connectivity.") from e
@router.get("/plugins",response_model=list[dict])
def plugins(request: Request):
    return [{"id":p.id,**p.frontend_manifest()} for p in request.app.state.plugins]

from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get('/test')
def test():
    return {'message': 'test'}

uvicorn.run(app, host='127.0.0.1', port=8001)
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn
from contextlib import asynccontextmanager
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import  AsyncSession
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Annotated
from fastapi import Depends
from http import HTTPStatus


from bd import create_tables, delete_tables, insert_user_data, new_session, User
from jwt_gen import cookie

templates = Jinja2Templates(directory="templates")

@asynccontextmanager
async def lifespan(app: FastAPI):
   await create_tables()
   await insert_user_data()
   print("База готова")
   yield
   

app = FastAPI(lifespan=lifespan)
app.mount("/css", StaticFiles(directory="templates/css"), name="css")

async def get_session():
    async with new_session() as session:
        yield session

SessionDepend = Annotated[AsyncSession, Depends(get_session)]

class UserSchema(BaseModel):
    name: str
    password: str = Field(min_length=8, max_length=12) 


@app.get('/', response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")

@app.post('/register', response_class=HTMLResponse)
async def register(request: Request, session: SessionDepend, name: str=Form(), password: str=Form()):

    data = UserSchema(name=name, password=password)

    result = await session.execute(select(User).where(User.name == name))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        return templates.TemplateResponse(
            request=request, name="register.html",
            context={"error": "User is already existing"}
        )

    new_user = User(name=data.name, password=data.password)
    
    session.add(new_user)
    await session.commit()

    return RedirectResponse(url="/login", status_code=HTTPStatus.SEE_OTHER)

@app.get('/login', response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")


@app.post('/login', response_class=HTMLResponse)
async def login_user(request: Request, session: SessionDepend, name: str=Form(), password: str=Form()):

    result = await session.execute(
        select(User).where((User.name == name) | (User.password == password))
    )
    user = result.scalar_one_or_none()
    if user:
        redirect = RedirectResponse(url="/checkuser", status_code=HTTPStatus.SEE_OTHER)

        cookie(redirect, str(user.id))

        return redirect

        
    else: 
        return {"error": False}


#vulnerable input
@app.get('/checkuser', response_class=HTMLResponse)
def check(request: Request):
    return templates.TemplateResponse(request=request, name="check.html")



@app.post("/checkuser")
async def find_user(input: str=Form()):
    async with new_session() as conn:
        query = text(f"SELECT name FROM users  WHERE '{input}'=name")
        res = await conn.execute(query)
        ret = res.fetchall()
    if ret:  
        names = [row[0] for row in ret] 
        return {"match": True, "names": names}
    return {"match": False}
    

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
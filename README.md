This is a [fastapi] project built within python 3.9.


## Project Layout
>VivEngineProject/ </br>
├── app/ </br>
│   ├── __init__.py </br>
│   ├── main.py </br>
│   ├── models/           ← SQLModel DB models </br>
│   │   └──  </br>
│   ├── routers/          ← Route handlers </br>
│   │   └──  </br>
│   ├── schemas/          ← Pydantic response/request models </br>
│   │   └──  </br>
│   ├── utils/            ← Data fetcher and parser </br>
│   │   └── </br>
│   │   └── </br>
│   └── config.py         ← config injection from env vars </br>
│   └── db.py             ← DB engine, session, etc. </br>


Run the server:
    
    make dev

    
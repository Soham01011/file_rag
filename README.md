1) Run venv and install required modules
2) run server with command : 
```
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
3) Make sure your mongodb is runing 
4) now cd into forntend folder and run a small http server to run angular JS , to do this run : 
```
    python3 -m http.server 8080
```
5) one the server is running go to : 
```
    http://127.0.0.1:8080/
```
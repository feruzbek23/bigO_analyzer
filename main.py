from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import ast
from analyzer.models import CodeInput

app = FastAPI()

templates = Jinja2Templates(directory="templates")



class ComplexityAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.max_depth = 0
        self.current_depth = 0

    def visit_FunctionDef(self, node):
        self.current_depth = 0
        self.max_depth = 0
        self.generic_visit(node)
        complexity = f"O(n^{self.max_depth})" if self.max_depth > 1 else "O(n)" if self.max_depth == 1 else "O(1)"
        print(f"Function '{node.name}' has a time complexity of {complexity}")

    def visit_For(self, node):
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1

    def visit_While(self, node):
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1

def analyze_complexity(code):
    tree = ast.parse(code)
    analyzer = ComplexityAnalyzer()
    return analyzer.visit(tree)
    

@app.post("/analyze_complexity", response_model=dict)
async def analyze_python_code(request: CodeInput):
    analyzer = ComplexityAnalyzer()
    try:
        analyze_complexity(request.code)
        complexity_result = analyze_complexity(request.code)
        return {"message": "Code complexity analyzed successfully", "time_complexity": complexity_result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/console", response_class=HTMLResponse)
async def open_console(request: Request):
    return templates.TemplateResponse(request=request, name="main.html")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Big O Complexity Analyzer API"}




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

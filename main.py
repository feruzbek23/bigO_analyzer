from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import ast
import pprint
from analyzer.models import CodeInput

app = FastAPI()

templates = Jinja2Templates(directory="templates")


class ComplexityAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.max_depth = 0       # Initialize maximum depth of nested loops or conditions
        self.current_depth = 0   # Initialize current depth during traversal

    def analyze(self, code):
        try:
            # Parse the code into an AST
            parsed_code = ast.parse(code)
            
            # Visit the parsed AST
            self.visit(parsed_code)
            
            # Determine complexity based on the maximum depth observed
            complexity = f"O(n^{self.max_depth})" if self.max_depth > 1 else "O(n)" if self.max_depth == 1 else "O(1)"
            return complexity
        except Exception as e:
            raise ValueError(f"Error analyzing code: {str(e)}")

    def visit_FunctionDef(self, node):
        self.current_depth = 0  # Reset current depth for each function definition
        self.max_depth = 0      # Reset maximum depth for each function definition
        self.generic_visit(node)  # Visit all child nodes of the FunctionDef node
        
        # Determine complexity based on the maximum depth observed
        complexity = f"O(n^{self.max_depth})" if self.max_depth > 1 else "O(n)" if self.max_depth == 1 else "O(1)"
        return complexity

    def visit_For(self, node):
        self.current_depth += 1  # Increase depth when entering a 'for' loop
        if self.current_depth > self.max_depth:
            self.max_depth = self.current_depth
        self.generic_visit(node)  # Visit all child nodes of the For node
        self.current_depth -= 1  # Decrease depth when exiting the 'for' loop

    def visit_While(self, node):
        self.current_depth += 1  # Increase depth when entering a 'while' loop
        if self.current_depth > self.max_depth:
            self.max_depth = self.current_depth
        self.generic_visit(node)  # Visit all child nodes of the While node
        self.current_depth -= 1  # Decrease depth when exiting the 'while' loop

    def visit_If(self, node):
        self.current_depth += 1  # Increase depth when entering an 'if' statement
        if self.current_depth > self.max_depth:
            self.max_depth = self.current_depth
        self.generic_visit(node)  # Visit all child nodes of the If node
        self.current_depth -= 1  # Decrease depth when exiting the 'if' statement

# Instantiate ComplexityAnalyzer
analyzer = ComplexityAnalyzer()


    

@app.post("/analyze", response_model=dict)
def analyze_python_code(request: CodeInput):
    try:
        # Execute the code snippet
        exec(request.code)
        
        # Analyze time complexity
        complexity = analyzer.analyze(request.code)
        
        return {
            "message": "Code executed successfully",
            "time_complexity": complexity
        }
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

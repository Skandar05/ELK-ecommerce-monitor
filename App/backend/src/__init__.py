from apiflask import APIFlask

def create_app():
    app = APIFlask(
        __name__,
        title="E-Commerce API",
        version="1.0.0",
        docs_path="/docs"
    )

    # Configuration
    app.config.from_object("app.config.development")

   
    
 

    return app
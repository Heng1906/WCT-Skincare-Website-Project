from fastapi import FastAPI
import modules.authentication.controller as authController
import modules.user.controller as userController
import modules.admin.controller as adminController
import modules.staff.controller as staffController  # Corrected typo
from database import engine
import entities

app = FastAPI(
    title="Food and Beverage App API",
    description="APIs for Food and Beverage Application Backend Development.",
    version="1.0.0",
    docs_url="/",
)

# Create all the tables in the database
entities.Base.metadata.create_all(engine)

# Include the routers for different modules
app.include_router(authController.router)
app.include_router(userController.router)
app.include_router(staffController.router)  # Corrected typo
app.include_router(adminController.router)

# Main entry point
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)  # Use reload=True instead of debug=True

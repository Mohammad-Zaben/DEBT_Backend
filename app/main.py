from fastapi import FastAPI

from app.routes import auth, user, provider, user_provider, transaction, otp, employer, work_payment

app = FastAPI(title="DebtMe API")

# Routers will be included after implementation to avoid import cycles if any.
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(provider.router, prefix="/providers", tags=["providers"])
app.include_router(user_provider.router, prefix="/links", tags=["links"])
app.include_router(transaction.router, prefix="/transactions", tags=["transactions"])
app.include_router(otp.router, prefix="/otp", tags=["otp"])
app.include_router(employer.router, prefix="/employers", tags=["employers"])
app.include_router(work_payment.router, prefix="/work-payments", tags=["work-payments"])

@app.get("/health")
async def health():
    return {"status": "ok"}

import asyncio
from sqlalchemy import select
from data.database import AsyncSessionLocal
from data.models import Chemical

async def check_data():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Chemical))
        chemicals = result.scalars().all()
        
        for chem in chemicals:
            print(f"{chem.name.upper()} | Formula: {chem.formula} | Health Score: {chem.toxicity_score}/100 | Reason: {chem.ghs_classification}")

if __name__ == "__main__":
    asyncio.run(check_data())
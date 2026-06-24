# data/etl_pipeline.py
from __future__ import annotations

import asyncio
from sqlalchemy.dialects.postgresql import insert

from data.database import AsyncSessionLocal, init_db
from data.models import Chemical
from core.pubchem_client import PubChemClient
from core.evaluator import evaluate_chemical

# Keep the excellent list of chemicals your Codex generated!
PUBCHEM_TOP_50 = [
    "acetone", "ethanol", "methanol", "toluene", "o-xylene", "hexane", 
    "isopropanol", "acetonitrile", "chloroform", "dichloromethane", 
    "formaldehyde", "benzene", "ethyl acetate", "cyclohexane", "diethyl ether", 
    "acetyl chloride", "sulfuric acid", "hydrochloric acid", "nitric acid", 
    "phosphoric acid", "ammonia", "sodium hydroxide", "potassium hydroxide", 
    "hydrogen peroxide", "phenol", "aniline", "dimethylformamide", 
    "dimethyl sulfoxide", "tetrahydrofuran", "n-hexane", "methyl isobutyl ketone", 
    "isobutyl alcohol", "propanol", "butanol", "acetic acid", "triethylamine", 
    "pyridine", "dioxane", "carbon tetrachloride", "methyl alcohol", 
    "ethylene glycol", "glycerol", "propylene glycol", "sodium hypochlorite", 
    "potassium permanganate", "silver nitrate", "copper sulfate",
]

async def load_chemicals() -> int:
    await init_db()
    client = PubChemClient()
    count = 0
    
    print(f"🚀 Starting ETL for {len(PUBCHEM_TOP_50)} chemicals...")
    
    async with AsyncSessionLocal() as session:
        for name in PUBCHEM_TOP_50:
            print(f"Processing {name}...")
            try:
                # 1. Fetch the specific properties (XLogP, BP, FP, GHS) using our client
                data = await client.get_chemical(name)
                if not data:
                    print(f"Skipping {name}: Not found in PubChem.")
                    continue
                    
                # 2. RUN THE DETERMINISTIC EVALUATOR with the 5-Criteria Matrix!
                ehs_result = evaluate_chemical(data)
                
                # 3. Prepare the database payload
                values = {
                    "cas_number": f"CID-{name}", # Placeholder unique ID
                    "name": name,
                    "formula": data.formula,
                    "ghs_classification": data.ghs_classification or "No GHS data",
                    "toxicity_score": float(ehs_result.total_score), # Uses the new total_score!
                    "raw_pubchem_json": data.model_dump(),
                }
                
                # 4. Upsert into Postgres
                statement = insert(Chemical).values(**values)
                update_dict = {
                    "name": statement.excluded.name,
                    "formula": statement.excluded.formula,
                    "ghs_classification": statement.excluded.ghs_classification,
                    "toxicity_score": statement.excluded.toxicity_score,
                    "raw_pubchem_json": statement.excluded.raw_pubchem_json,
                }
                
                await session.execute(
                    statement.on_conflict_do_update(
                        index_elements=[Chemical.cas_number],
                        set_=update_dict,
                    )
                )
                await session.commit()
                count += 1
                print(f"Scored {name}: {ehs_result.total_score}/100 (Missing data: {ehs_result.missing_data})")
                
            except Exception as e:
                print(f"Failed {name}: {e}")
                
    await client.close()
    return count

if __name__ == "__main__":
    total = asyncio.run(load_chemicals())
    print(f"\nETL Complete! Processed {total} chemicals.")
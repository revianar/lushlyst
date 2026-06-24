import asyncio
from core.pubchem_client import PubChemClient
from core.evaluator import evaluate_chemical

async def verify():
    client = PubChemClient()
    
    test_chemicals = ["acetone", "benzene", "chloroform", "ethanol"]
    
    for name in test_chemicals:
        print(f"\n{name.upper()}")
        print("-" * 80)
        
        data = await client.get_chemical(name)
        
        if not data:
            print("ERROR: No data returned from PubChem")
            continue
        
        print(f"Formula:          {data.formula}")
        print(f"XLogP:            {data.xlogp}")
        print(f"Flash Point:      {data.flash_point}")
        print(f"Boiling Point:    {data.boiling_point}")
        print(f"GHS:              {data.ghs_classification}")
        
        result = evaluate_chemical(data)
        
        print(f"\nSCORING BREAKDOWN:")
        print(f"    Acute Health:    {result.acute_health}/30")
        print(f"    Flammability:    {result.flammability}/25")
        print(f"    Environmental:   {result.environmental}/20")
        print(f"    Volatility:      {result.volatility}/15")
        print(f"    Sustainability:  {result.sustainability}/10")
        print(f"    TOTAL:           {result.total_score}/100")
        print(f"    Missing Data:    {result.missing_data}")
        
        # Show which fields are None
        missing_fields = []
        if data.xlogp is None:
            missing_fields.append("XLogP")
        print(f"  Flash Point:      {data.flash_point}")
        print(f"  Boiling Point:    {data.boiling_point}")
        print(f"  GHS:              {data.ghs_classification}")
        
        # Run evaluator
        result = evaluate_chemical(data)
        
        print(f"\nSCORING BREAKDOWN:")
        print(f"    Acute Health:    {result.acute_health}/30")
        print(f"    Flammability:    {result.flammability}/25")
        print(f"    Environmental:   {result.environmental}/20")
        print(f"    Volatility:      {result.volatility}/15")
        print(f"    Sustainability:  {result.sustainability}/10")
        print(f"    TOTAL:           {result.total_score}/100")
        print(f"    Missing Data:    {result.missing_data}")
        
        # Show which fields are None
        missing_fields = []
        if data.xlogp is None:
            missing_fields.append("XLogP")
        if data.flash_point is None:
            missing_fields.append("Flash Point")
        if data.boiling_point is None:
            missing_fields.append("Boiling Point")
        if data.ghs_classification is None:
            missing_fields.append("GHS")
        
        if missing_fields:
            print(f"MISSING FIELDS:  {', '.join(missing_fields)}")
        else:
            print(f"MISSING FIELDS:  None")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(verify())
import asyncio
import httpx

async def debug():
    url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/acetone/JSON"
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(url)
        payload = response.json()
        
        compound = payload["PC_Compounds"][0]
        props = compound.get("props", [])
        
        print("=== ALL PROPERTY LABELS AND VALUES ===")
        for prop in props:
            label = prop.get("urn", {}).get("label", "NO_LABEL")
            name = prop.get("urn", {}).get("name", "NO_NAME")
            val = prop.get("value", {})
            print(f"Label: {label:30} | Name: {name:20} | Value: {val}")

if __name__ == "__main__":
    asyncio.run(debug())
import asyncio
import httpx
import json

async def debug():
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Get CID for acetone
        url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/acetone/JSON"
        response = await client.get(url)
        compound = response.json()["PC_Compounds"][0]
        cid = compound["id"]["id"]["cid"]
        
        # Fetch pug_view data
        view_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON"
        response = await client.get(view_url)
        payload = response.json()
        
        print(f"GHS DATA STRUCTURE FOR ACETONE (CID: {cid})")
        
        sections = payload.get("Record", {}).get("Section", [])
        
        for section in sections:
            if section.get("TOCHeading") == "Safety and Hazards":
                print("\nFound 'Safety and Hazards' section")
                subsections = section.get("Section", [])
                
                for subsec in subsections:
                    if subsec.get("TOCHeading") == "Hazards Identification":
                        print("\nFound 'Hazards Identification' subsection")
                        hazard_sections = subsec.get("Section", [])
                        
                        for hazard_sec in hazard_sections:
                            if hazard_sec.get("TOCHeading") == "GHS Classification":
                                print("\nFound 'GHS Classification' section")
                                print("\nFull structure:")
                                print(json.dumps(hazard_sec, indent=2))
                                return
        
        print("\nGHS Classification section not found")

if __name__ == "__main__":
    asyncio.run(debug())
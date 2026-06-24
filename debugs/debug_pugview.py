# debug_pugview.py
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
        
        print("=" * 80)
        print(f"PUG_VIEW STRUCTURE FOR ACETONE (CID: {cid})")
        print("=" * 80)
        
        # Print top-level sections
        sections = payload.get("Record", {}).get("Section", [])
        for section in sections:
            heading = section.get("TOCHeading", "NO_HEADING")
            print(f"\nTOP SECTION: {heading}")
            
            # Print subsections
            subsections = section.get("Section", [])
            for subsec in subsections[:5]:  # Limit to first 5
                subheading = subsec.get("TOCHeading", "NO_HEADING")
                print(f"  - {subheading}")
                
                # Print sub-subsections
                subsubsections = subsec.get("Section", [])
                for subsubsec in subsubsections[:3]:  # Limit to first 3
                    subsubheading = subsubsec.get("TOCHeading", "NO_HEADING")
                    print(f"      - {subsubheading}")

if __name__ == "__main__":
    asyncio.run(debug())
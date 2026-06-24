import re
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from pydantic import BaseModel

class PubChemData(BaseModel):
    name: str
    formula: str | None = None
    xlogp: float | None = None
    flash_point: float | None = None
    boiling_point: float | None = None
    ghs_classification: str | None = None

def _parse_temp(value) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        match = re.search(r"[-+]?\d*\.\d+|\d+", value.replace("\u2212", "-").replace("−", "-"))
        if match:
            temp = float(match.group())
            if "F" in value.upper():
                temp = (temp - 32) * 5.0 / 9.0
            return temp
    return None

def _extract_unique_h_codes(ghs_text: str) -> str:
    """Extract unique H-codes from GHS text and return them as a clean string."""
    if not ghs_text:
        return None
    
    h_codes = re.findall(r'H\d{3}', ghs_text)
    unique_codes = sorted(set(h_codes))
    return ", ".join(unique_codes) if unique_codes else None

class PubChemClient:
    BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name"
    VIEW_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound"

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    # Only retry on HTTP errors (500s) and connection errors
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException))
    )
    async def get_chemical(self, name: str) -> PubChemData | None:
        # Step 1: Get CID and basic properties
        url = f"{self.BASE_URL}/{name}/JSON"
        response = await self.client.get(url)
        
        # This part stops retrying on 404 errors, as they indicate the chemical was not found
        if response.status_code == 404:
            return None
        
        # Retry on 500s or other server errors
        response.raise_for_status()
        
        payload = response.json()
        if not payload.get("PC_Compounds"):
            return None
            
        compound = payload["PC_Compounds"][0]
        cid = compound.get("id", {}).get("id", {}).get("cid")
        
        # Extract XLogP and Molecular Formula from standard endpoint
        props = compound.get("props", [])
        prop_map = {}
        for prop in props:
            label = prop.get("urn", {}).get("label", "")
            prop_name = prop.get("urn", {}).get("name", "")
            val = prop.get("value", {})
            
            extracted_val = val.get("sval") or val.get("ival") or val.get("fval")
            
            if label == "Log P" and "XLogP" in prop_name:
                prop_map["XLogP"] = extracted_val
            elif label == "Molecular Formula":
                prop_map["Molecular Formula"] = extracted_val

        # Step 2: Fetch detailed data from pug_view
        view_data = await self._fetch_view_data(cid) if cid else {}

        return PubChemData(
            name=name,
            formula=prop_map.get("Molecular Formula"),
            xlogp=prop_map.get("XLogP"),
            flash_point=view_data.get("flash_point"),
            boiling_point=view_data.get("boiling_point"),
            ghs_classification=view_data.get("ghs")
        )

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException))
    )
    async def _fetch_view_data(self, cid: int) -> dict:
        url = f"{self.VIEW_URL}/{cid}/JSON"
        response = await self.client.get(url)
        
        if response.status_code != 200:
            return {}
            
        payload = response.json()
        result = {}
        
        sections = payload.get("Record", {}).get("Section", [])
        
        for section in sections:
            heading = section.get("TOCHeading", "")
            
            # Extract Physical Properties (Boiling Point, Flash Point)
            if heading == "Chemical and Physical Properties":
                subsections = section.get("Section", [])
                for subsec in subsections:
                    if subsec.get("TOCHeading") == "Experimental Properties":
                        exp_props = subsec.get("Section", [])
                        for prop in exp_props:
                            prop_heading = prop.get("TOCHeading", "")
                            if "Boiling Point" in prop_heading:
                                result["boiling_point"] = self._extract_physical_property(prop)
                            elif "Flash Point" in prop_heading:
                                result["flash_point"] = self._extract_physical_property(prop)
            
            # Extract GHS Classification
            elif heading == "Safety and Hazards":
                subsections = section.get("Section", [])
                for subsec in subsections:
                    if subsec.get("TOCHeading") == "Hazards Identification":
                        hazard_sections = subsec.get("Section", [])
                        for hazard_sec in hazard_sections:
                            if hazard_sec.get("TOCHeading") == "GHS Classification":
                                raw_ghs = self._extract_ghs_hazards(hazard_sec)
                                result["ghs"] = _extract_unique_h_codes(raw_ghs)
        
        return result

    def _extract_physical_property(self, section: dict) -> float | None:
        """Extract boiling point or flash point value."""
        info_list = section.get("Information", [])
        for info in info_list:
            value = info.get("Value", {})
            
            if "StringWithMarkup" in value:
                strings = value["StringWithMarkup"]
                if strings:
                    return _parse_temp(strings[0].get("String", ""))
            
            if "String" in value:
                return _parse_temp(value["String"])
            
            if "Number" in value:
                return float(value["Number"])
        
        return None

    def _extract_ghs_hazards(self, section: dict) -> str | None:
        """Extract GHS hazard statements from the Information array."""
        info_list = section.get("Information", [])
        hazards = []
        
        for info in info_list:
            if info.get("Name") == "GHS Hazard Statements":
                value = info.get("Value", {})
                
                if "StringWithMarkup" in value:
                    for item in value["StringWithMarkup"]:
                        text = item.get("String", "")
                        if text:
                            hazards.append(text)
                
                elif "String" in value:
                    hazards.append(value["String"])
        
        return " ".join(hazards) if hazards else None

    async def close(self):
        await self.client.aclose()
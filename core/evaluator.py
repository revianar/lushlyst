from pydantic import BaseModel
from core.pubchem_client import PubChemData

class EHSResult(BaseModel):
    """The 5-Criteria EHS scoring result."""
    acute_health: int
    flammability: int
    environmental: int
    volatility: int
    sustainability: int
    total_score: int
    missing_data: bool
    explanation: str

def evaluate_chemical(data: PubChemData) -> EHSResult:
    """
    Pure Python deterministic scoring logic based on the 5-Criteria EHS Matrix.
    """
    name = data.name.lower()
    ghs = data.ghs_classification or ""
    
    # Track if we are missing critical data
    missing_data = False
    
    # 1. Acute Health (Max 30 pts)
    if data.xlogp is None and data.ghs_classification is None: 
        acute_health = 0
        missing_data = True
    else:
        acute_health = 30
        if any(code in ghs for code in ["H300", "H314", "H330"]): 
            acute_health = 0
        elif any(code in ghs for code in ["H351", "H319"]): 
            acute_health = 15

    # 2. Flammability (Max 25 pts)
    if data.flash_point is None:
        flammability = 0
        missing_data = True
    else:
        if data.flash_point < 23: flammability = 0
        elif 23 <= data.flash_point <= 60: flammability = 10
        else: flammability = 25

    # 3. Environmental (Max 20 pts)
    env = 20
    if data.xlogp is None:
        env -= 10
        missing_data = True
    elif data.xlogp > 4.0:
        env -= 10
        
    if data.ghs_classification is None:
        missing_data = True
    elif any(code in ghs for code in ["H400", "H410"]):
        env -= 10
    environmental = max(0, env)

    # 4. Volatility (Max 15 pts)
    if data.boiling_point is None:
        volatility = 0
        missing_data = True
    else:
        if data.boiling_point < 40: volatility = 5
        elif 40 <= data.boiling_point <= 150: volatility = 15
        else: volatility = 10

    # 5. Sustainability (Max 10 pts)
    sustainability = 10
    if "chloro" in name or "bromo" in name:
        sustainability -= 5

    # Calculate Total
    total_score = acute_health + flammability + environmental + volatility + sustainability
    
    # Handle Missing Data Rule
    if missing_data:
        explanation = "Data unavailable in PubChem."
    else:
        # Placeholder for Phase 2 LLM integration. 
        # For now, we generate a deterministic summary string.
        explanation = (
            f"Scored {total_score}/100. "
            f"Health: {acute_health}/30, Flammability: {flammability}/25, "
            f"Env: {environmental}/20, Volatility: {volatility}/15, Sustainability: {sustainability}/10."
        )

    return EHSResult(
        acute_health=acute_health,
        flammability=flammability,
        environmental=environmental,
        volatility=volatility,
        sustainability=sustainability,
        total_score=total_score,
        missing_data=missing_data,
        explanation=explanation
    )
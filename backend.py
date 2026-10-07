"""SheSafe@School FastAPI backend."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="SheSafe@School API", description="Student safety guidance API.", version="2.0.0")

class AnalyzeRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1500)

class AnalyzeResponse(BaseModel):
    category: str
    risk: str
    risk_color: str
    response: str
    steps: List[str]
    emergency: bool
    why: str

HIGH_RISK_PHRASES={"weapon","knife","gun","attack","kidnap","kidnapped","bleeding","kill me","kill","immediate danger","following me","stalking me","locked me","forced me","can't escape","cannot escape"}
MEDIUM_RISK_PHRASES={"threat","threatening","threaten","harass","harassment","alone","afraid","scared","bully","bullying","touching","uncomfortable","blackmail","following","stalking"}
CATEGORY_KEYWORDS: Dict[str,set[str]]={
"Bullying / Personal Safety":{"bully","bullying","senior","teasing","threatening","threaten","mocking","fight","classmate","school","after school"},
"Harassment / Personal Safety":{"harass","harassment","touching","uncomfortable","staring","comment","blackmail","inappropriate","follow me","stalking"},
"Cyber Safety":{"online","instagram","whatsapp","password","photo","cyber","account","message","dm","social media","fake account","hack"},
"Unsafe Travel":{"bus","cab","taxi","travel","driver","road","station","metro","auto","rickshaw","route","ride"}}

@dataclass(frozen=True)
class AdviceTemplate:
    response: str
    steps: List[str]
    why: str

TEMPLATES={
"High":AdviceTemplate("This may be an urgent safety situation. Move to a safe, public place and contact a trusted adult or emergency service immediately.",["Move to a safe and populated place now.","Call a parent, teacher, guardian, or another trusted adult immediately.","If you are in immediate danger in India, call 112."],"Your message contains signs of possible immediate danger. The safest response is to prioritize physical safety and involve a trusted adult or emergency service."),
"Medium":AdviceTemplate("Your safety matters, and you do not have to handle this alone. Here is some guidance to help you stay safe.",["Stay near teachers, friends, or other trusted people and avoid being alone with the person.","Tell a trusted adult today — a parent, teacher, counsellor, or guardian.","Do not confront them alone. Keep a simple record of incidents if it is safe to do so."],"The situation sounds concerning but does not clearly describe an immediate emergency. The advice focuses on reducing exposure and involving a trusted adult quickly."),
"Low":AdviceTemplate("I can help you think through this safely. Share only what you are comfortable sharing, and involve a trusted adult if the situation continues or worries you.",["Move to a place where you feel safe and comfortable.","Talk to a trusted adult if the problem continues or makes you worried.","Do not share passwords, private photos, or sensitive personal information."],"Your message does not show a clear sign of immediate danger, so the guidance starts with prevention, privacy, and trusted-adult support.")}

def _contains_any(text,phrases): return any(p in text for p in phrases)

def classify_category(text):
    scores={category:sum(1 for k in keywords if k in text) for category,keywords in CATEGORY_KEYWORDS.items()}
    best=max(scores,key=scores.get)
    return best if scores[best]>0 else "Personal Safety"

def classify_risk(text):
    if _contains_any(text,HIGH_RISK_PHRASES): return "High"
    if _contains_any(text,MEDIUM_RISK_PHRASES): return "Medium"
    return "Low"

def analyze_message(message):
    text=(message or "").strip().lower()
    if not text: raise ValueError("Please describe what is happening.")
    category=classify_category(text); risk=classify_risk(text); template=TEMPLATES[risk]
    return AnalyzeResponse(category=category,risk=risk,risk_color={"Low":"green","Medium":"amber","High":"red"}[risk],response=template.response,steps=template.steps,emergency=risk=="High",why=template.why)

@app.get("/api/health")
def health(): return {"status":"ok","service":"SheSafe@School","version":"2.0.0"}

@app.post("/api/analyze",response_model=AnalyzeResponse)
def analyze(request:AnalyzeRequest): return analyze_message(request.message)

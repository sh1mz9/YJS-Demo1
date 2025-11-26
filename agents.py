"""Simplified agent implementations for MVP demo"""

import streamlit as st
import openai
from typing import Dict, Any, List
from datetime import datetime

# ============================================================
# CONFIGURE OPENAI - LAZY LOADING
# ============================================================

_openai_configured = False
_api_key_valid = False

def ensure_openai_configured():
    """Ensure OpenAI is configured - call this only after Streamlit initialized"""
    global _openai_configured, _api_key_valid
    
    if _openai_configured:
        return _api_key_valid
    
    try:
        api_key = st.secrets.get("OPENAI_API_KEY")
        if api_key and api_key.strip():
            openai.api_key = api_key
            _api_key_valid = True
        else:
            _api_key_valid = False
    except Exception as e:
        _api_key_valid = False
        print(f"Error configuring OpenAI: {e}")
    
    _openai_configured = True
    return _api_key_valid

# ============================================================
# AGENT BASE CLASS
# ============================================================

class AgentBase:
    """Base class for all agents"""
    
    def __init__(self, name: str, model: str = "gpt-4o-mini"):
        self.name = name
        self.model = model
        self.last_response = None
    
    def call_llm(self, prompt: str, system_prompt: str = "", max_tokens: int = 1000) -> str:
        """Call OpenAI API"""
        try:
            # Ensure OpenAI is configured
            if not ensure_openai_configured():
                return "⚠️ Error: OpenAI API key not configured. Please add OPENAI_API_KEY to .streamlit/secrets.toml"
            
            if not openai.api_key:
                return "⚠️ Error: OpenAI API key is empty"
            
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            error_msg = str(e)
            if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                return "⚠️ Error: Invalid or missing OpenAI API key. Please check .streamlit/secrets.toml"
            return f"Error: {error_msg}"

# ============================================================
# AGENT 1: DATA/RESEARCH
# ============================================================

class DataResearchAgent(AgentBase):
    def __init__(self):
        super().__init__("Data/Research Agent", "gpt-4o-mini")
    
    def enrich_company(self, company_name: str) -> Dict[str, Any]:
        """Enrich company data"""
        prompt = f"""Provide a concise company profile for {company_name}. Include:
        1. Industry and sector
        2. Estimated company size
        3. Key business focus
        4. Potential pain points
        
        Be realistic and factual."""
        
        system_prompt = "You are a company research specialist. Provide accurate company information."
        result = self.call_llm(prompt, system_prompt)
        
        return {
            "company_name": company_name,
            "profile": result,
            "model_used": self.model,
            "timestamp": datetime.now().isoformat()
        }
    
    def screen_pii(self, text: str) -> Dict[str, Any]:
        """Screen for PII"""
        prompt = f"""Analyze this text for PII (personally identifiable information):

{text}

List any PII found and rate GDPR compliance risk (low/medium/high)."""
        
        result = self.call_llm(prompt, "You are a GDPR compliance specialist.")
        
        return {
            "text_sample": text[:100] + "..." if len(text) > 100 else text,
            "analysis": result,
            "model_used": self.model
        }

# ============================================================
# AGENT 2: ENGAGEMENT
# ============================================================

class EngagementAgent(AgentBase):
    def __init__(self):
        super().__init__("Engagement Agent", "gpt-4o-mini")
    
    def qualify_lead(self, company: str, budget: str, timeline: str) -> Dict[str, Any]:
        """Qualify lead using BANT"""
        prompt = f"""Qualify this lead using BANT framework:
        
Company: {company}
Budget: {budget}
Timeline: {timeline}

Provide:
1. BANT score (0-10)
2. Qualified status (Yes/No/Maybe)
3. Key risks or opportunities
4. Recommendation"""
        
        result = self.call_llm(prompt, "You are a sales qualification specialist.")
        
        return {
            "company": company,
            "bant_analysis": result,
            "model_used": self.model
        }
    
    def generate_email(self, company: str, contact_name: str) -> Dict[str, Any]:
        """Generate outreach email"""
        prompt = f"""Write a professional outreach email to {contact_name} at {company} about:

"We help mid-market companies implement AI-driven consulting solutions that reduce costs by 70%"

Make it personalized but concise (200 words max)."""
        
        result = self.call_llm(prompt, "You are a B2B sales professional.")
        
        return {
            "recipient": f"{contact_name} @ {company}",
            "email": result,
            "model_used": self.model
        }

# ============================================================
# AGENT 3: DISCOVERY
# ============================================================

class DiscoveryAgent(AgentBase):
    def __init__(self):
        super().__init__("Discovery Agent", "gpt-4-turbo")
    
    def generate_questions(self, company_context: str) -> Dict[str, Any]:
        """Generate discovery questions"""
        prompt = f"""Generate 10 strategic discovery questions for {company_context}

Focus on:
1. Current processes and pain points
2. Technology stack
3. Team structure
4. Budget constraints
5. Success metrics

Format as numbered list with brief context for each."""
        
        result = self.call_llm(prompt, "You are an expert business consultant.")
        
        return {
            "context": company_context,
            "questions": result,
            "model_used": self.model
        }

# ============================================================
# AGENT 4: SYNTHESIS
# ============================================================

class SynthesisAgent(AgentBase):
    def __init__(self):
        super().__init__("Synthesis Agent", "gpt-4-turbo")
    
    def calculate_roi(self, investment_amount: float, annual_revenue: float = 50000000) -> Dict[str, Any]:
        """Calculate ROI scenarios"""
        prompt = f"""Calculate ROI for a £{investment_amount:,.0f} consulting engagement.

Assumptions:
- Client annual revenue: £{annual_revenue:,.0f}
- Implementation period: 6 months
- Benefits realization: 12 months

Provide 3 scenarios:
1. Conservative (20% efficiency gain)
2. Recommended (35% efficiency gain)
3. Aggressive (50% efficiency gain)

For each, show:
- Annual savings
- Payback period
- 3-year ROI %
- Key assumptions"""
        
        result = self.call_llm(prompt, "You are a financial analyst.")
        
        return {
            "investment": f"£{investment_amount:,.0f}",
            "roi_analysis": result,
            "model_used": self.model
        }

# ============================================================
# AGENT 5: PROJECT/DELIVERY
# ============================================================

class ProjectDeliveryAgent(AgentBase):
    def __init__(self):
        super().__init__("Project/Delivery Agent", "gpt-4o-mini")
    
    def create_project_plan(self, project_name: str, scope: str) -> Dict[str, Any]:
        """Create project timeline"""
        prompt = f"""Create a project delivery plan for: {project_name}

Scope: {scope}

Provide:
1. 5-phase breakdown
2. Timeline (weeks)
3. Key deliverables
4. Resource requirements
5. Risk assessment
6. Success criteria

Format as structured plan."""
        
        result = self.call_llm(prompt, "You are a project management expert.")
        
        return {
            "project": project_name,
            "plan": result,
            "model_used": self.model
        }

# ============================================================
# AGENT 6: ORCHESTRATOR (Special - AI Guide)
# ============================================================

class OrchestratorAgent(AgentBase):
    def __init__(self):
        super().__init__("Orchestrator Agent", "gpt-4-turbo")
        self.agents_info = self._load_agents_info()
        self.task_templates = self._load_task_templates()

    def _load_agents_info(self) -> Dict:
        """Load info about all agents"""
        return {
            "data_research": {
                "name": "📊 Data/Research",
                "desc": "Company enrichment, PII screening, GDPR validation",
                "tools": ["Companies House API", "Clearbit", "OpenAI"],
                "outputs": ["enriched profiles", "compliance reports", "contact validation"]
            },
            "engagement": {
                "name": "🎯 Engagement",
                "desc": "BANT qualification, outreach emails, lead scoring",
                "tools": ["LinkedIn", "SendGrid", "OpenAI"],
                "outputs": ["qualified leads", "personalized outreach", "lead scores"]
            },
            "discovery": {
                "name": "🔍 Discovery",
                "desc": "Strategic questions, process mapping, compliance",
                "tools": ["LinkedIn", "Compliance APIs", "OpenAI GPT-4-turbo"],
                "outputs": ["discovery questions", "process maps", "compliance checklists"]
            },
            "synthesis": {
                "name": "💡 Synthesis",
                "desc": "ROI modeling, 3-scenario planning, business case",
                "tools": ["Claude Sonnet", "Financial APIs", "OpenAI GPT-4-turbo"],
                "outputs": ["ROI models", "business cases", "financial projections"]
            },
            "project_delivery": {
                "name": "📋 Project/Delivery",
                "desc": "Timelines, risk assessment, contracts, resource planning",
                "tools": ["DocuSign", "AWS S3", "OpenAI"],
                "outputs": ["implementation plans", "risk assessments", "resource schedules"]
            },
            "change_comms": {
                "name": "📢 Change/Comms",
                "desc": "Training plans, communication, adoption tracking",
                "tools": ["SendGrid", "OpenAI"],
                "outputs": ["training materials", "comms plans", "adoption metrics"]
            }
        }

    def _load_task_templates(self) -> Dict:
        """Load pre-built task orchestration templates"""
        return {
            "lead_gen": {
                "title": "Lead Generation Automation",
                "description": "Automated prospecting and lead qualification",
                "agents": ["data_research", "engagement", "synthesis"],
                "process": [
                    "Enrich prospect data (research industry, company profile, pain points)",
                    "Qualify leads using BANT framework",
                    "Calculate ROI per lead",
                    "Generate personalized outreach emails"
                ],
                "duration": "3-4 weeks",
                "effort": "Medium"
            },
            "reception_automation": {
                "title": "Reception/Intake Automation",
                "description": "Automated client intake and appointment scheduling",
                "agents": ["discovery", "data_research", "project_delivery"],
                "process": [
                    "Map current reception workflow and pain points",
                    "Identify automation opportunities (intake forms, data capture)",
                    "Screen callers for compliance and qualification",
                    "Auto-schedule appointments based on availability",
                    "Create implementation roadmap"
                ],
                "duration": "4-6 weeks",
                "effort": "High"
            },
            "full_pipeline": {
                "title": "Full Sales Pipeline Automation",
                "description": "End-to-end lead generation through deal closure",
                "agents": ["data_research", "engagement", "discovery", "synthesis", "project_delivery", "change_comms"],
                "process": [
                    "Research and enrich prospect database",
                    "Engage & qualify inbound leads",
                    "Run discovery calls with qualifying prospects",
                    "Build ROI case and business proposal",
                    "Create implementation plan",
                    "Plan change management & training"
                ],
                "duration": "8-12 weeks",
                "effort": "High"
            },
            "compliance_automation": {
                "title": "Compliance & Risk Screening",
                "description": "Automated compliance checks and risk assessment",
                "agents": ["data_research", "discovery"],
                "process": [
                    "Screen prospects against compliance databases",
                    "Check PII and data protection requirements",
                    "Validate regulatory compliance (GDPR, SCA, etc)",
                    "Create compliance report and risk assessment"
                ],
                "duration": "2-3 weeks",
                "effort": "Low"
            }
        }

    def chat(self, user_message: str, history: List[Dict]) -> str:
        """Chat about solving specific business tasks through agent orchestration
        Focus: Task-centric, not agent-centric
        """
        try:
            if not ensure_openai_configured():
                return "Error: OpenAI API key not configured"

            # Build context about what agents do
            agents_context = "\n".join([
                f"- {info['name']}: {info['desc']}"
                for info in self.agents_info.values()
            ])

            task_templates_context = "\n\n".join([
                f"**{task['title']}**\n"
                f"- Description: {task['description']}\n"
                f"- Agents: {', '.join([self.agents_info[a]['name'] for a in task['agents']])}\n"
                f"- Timeline: {task['duration']}"
                for task in self.task_templates.values()
            ])

            system_prompt = f"""You are an expert Orchestration Agent for YJS Consulting specializing in helping organizations achieve specific business goals through intelligent agent coordination.

## YOUR ROLE
When users describe a business task or problem, your job is to:
1. **Understand the goal** - What outcome do they want?
2. **Recommend agents** - Which agents should work together?
3. **Explain the process** - How will agents orchestrate to achieve this?
4. **Show ROI/impact** - What efficiency or cost savings will result?
5. **Provide roadmap** - What's the implementation timeline and steps?

## AVAILABLE AGENTS
{agents_context}

## PRE-BUILT TASK SOLUTIONS
{task_templates_context}

## HOW TO RESPOND

### For specific business tasks (e.g., "How do I automate lead gen and reception?")

Structure your response as:

### 🎯 Your Goal
[Restate what they want to achieve]

### 🔧 Agent Orchestration
[Explain which agents work together and why]

**Step 1: [Agent Name]**
- What it does: [specific task]
- Input: [what data goes in]
- Output: [what comes out]

**Step 2: [Agent Name]**
- What it does: ...
[Continue for all agents in sequence]

### 📊 Data Flow
[Show how data moves between agents: Agent A → Data → Agent B]

### ⏱️ Timeline
- Phase 1 (Weeks 1-2): [Initial setup]
- Phase 2 (Weeks 3-4): [Execution]
- Phase 3 (Weeks 5+): [Optimization]

### 💰 ROI & Impact
- **Time saved**: [X hours/week per task]
- **Cost reduction**: [X%]
- **Quality improvement**: [specific metrics]
- **Payback period**: [time to ROI]

### 📋 Next Steps
1. [First action]
2. [Second action]
3. [Third action]

---

## INDUSTRY-SPECIFIC EXAMPLES

### LAW FIRM - Lead Gen & Reception Automation
**User Goal**: "We want to automate lead generation and reception team tasks"

**Your Response Flow**:
1. Identify they have 2 separate processes: (a) attracting new clients, (b) handling inbound calls
2. Recommend: Data/Research → Engagement (for lead gen) + Discovery → Project Delivery (for reception automation)
3. Explain agent orchestration:
   - Lead Gen Loop: Data enriches prospects → Engagement qualifies them → ROI calculated
   - Reception Loop: Discovery maps workflow → Project delivery automates intake process
4. Show timeline (weeks per phase) and impact (leads per week, calls handled, etc.)

### E-COMMERCE - Customer Service Automation
**User Goal**: "Automate customer support and upsell process"

**Your Response Flow**:
1. Identify they want to reduce support cost while increasing order value
2. Recommend: Data/Research (customer profiling) → Discovery (current support process) → Synthesis (upsell ROI)
3. Explain how agents orchestrate to classify support tickets, identify upsell opportunities, and quantify impact
4. Show time-to-value and customer satisfaction impact

### HEALTHCARE - Patient Intake & Compliance
**User Goal**: "Automate patient intake while maintaining HIPAA compliance"

**Your Response Flow**:
1. Identify compliance requirement and intake volume
2. Recommend: Data/Research (HIPAA screening) → Discovery (current process) → Project/Delivery (automation roadmap)
3. Explain how agents work together to ensure zero-risk compliance
4. Show efficiency and error reduction metrics

---

## IMPORTANT GUIDELINES

✅ **DO:**
- Focus on the TASK the user wants to accomplish
- Explain WHICH AGENTS work together and WHY
- Show HOW agents pass data to each other
- Quantify BUSINESS IMPACT (time, cost, quality)
- Provide clear implementation STEPS and TIMELINE
- Use industry examples if relevant
- Ask clarifying questions if goal is ambiguous

❌ **DON'T:**
- Describe agents individually without connecting to their task
- Get too technical about agent internals
- Provide vague answers - be specific about what happens at each step
- Forget to mention timeline and effort required
- Skip the ROI/impact section

---

## RESPONSE FORMAT

Always structure responses with:
- ### Headings (h3 level)
- **Bold text** for emphasis
- Numbered lists for sequences
- Bullet points for details
- Blank lines between sections

Example task the user might ask:
"This law firm wants to focus on automating lead gen and reception team. How do I go about doing this?"

You should respond with the orchestration strategy, not just list agents."""

            # Build messages
            messages = [{"role": "system", "content": system_prompt}]

            # Add history
            if history:
                for h in history:
                    if isinstance(h, dict) and "role" in h and "content" in h:
                        messages.append({"role": h["role"], "content": h["content"]})

            # Add user message
            messages.append({"role": "user", "content": user_message})

            # Call OpenAI API
            response = openai.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"Chat error: {str(e)}")
            return f"I encountered an error: {str(e)}"

    def solve_task(self, task_name: str, company_context: str) -> str:
        """Solve a pre-built task with company context"""
        try:
            if not ensure_openai_configured():
                return "Error: OpenAI API key not configured"

            task = self.task_templates.get(task_name)
            if not task:
                available = ", ".join(self.task_templates.keys())
                return f"Unknown task. Available: {available}"

            agents_list = " → ".join([
                self.agents_info[a]['name'] for a in task['agents']
            ])

            prompt = f"""You are orchestrating the following task:

**Task**: {task['title']}
**Description**: {task['description']}
**Agent Chain**: {agents_list}

**Company Context**: {company_context}

Provide a detailed implementation plan that includes:

1. **Agent Orchestration Steps** (what each agent does, in sequence)
2. **Data Flow** (how data moves between agents)
3. **Key Outputs** (what gets delivered at each step)
4. **Timeline** (realistic weeks/months)
5. **Resource Requirements** (people, tools, infrastructure)
6. **Expected ROI/Impact** (time saved, cost reduction, quality improvement)
7. **Risks & Mitigation** (what could go wrong, how to prevent)
8. **Success Metrics** (how to measure if it worked)

Be specific and actionable."""

            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in orchestrating AI agents to solve business problems."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Error: {str(e)}"

    def recommend_workflow(self, scenario: str) -> str:
        """Recommend best workflow for a scenario"""
        try:
            if not ensure_openai_configured():
                return "Error: OpenAI API key not configured"

            prompt = f"""A company has the following business challenge:

{scenario}

Recommend an optimal agent orchestration workflow:

1. **Analysis** - What's the core problem and how do agents solve it?
2. **Agent Selection** - Which agents? In what order? Why?
3. **Orchestration Flow** - Draw the data flow and agent sequence
4. **Timeline** - How long will this take?
5. **Team & Skills** - Who needs to be involved?
6. **Cost Structure** - What will this cost to implement?
7. **Expected Impact** - What metrics will improve?
8. **First 90 Days** - What's the implementation roadmap?

Focus on solving their BUSINESS PROBLEM, not describing agents."""

            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert business consultant who designs agent orchestration workflows to solve real problems."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Error: {str(e)}"
# ============================================================
# AGENT FACTORY
# ============================================================

def get_agent(agent_type: str) -> AgentBase:
    """Get agent instance"""
    agents = {
        "data_research": DataResearchAgent,
        "engagement": EngagementAgent,
        "discovery": DiscoveryAgent,
        "synthesis": SynthesisAgent,
        "project_delivery": ProjectDeliveryAgent,
        "orchestrator": OrchestratorAgent
    }
    
    agent_class = agents.get(agent_type)
    if agent_class:
        return agent_class()
    else:
        raise ValueError(f"Unknown agent: {agent_type}")

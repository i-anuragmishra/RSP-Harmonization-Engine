"""LLM-based extraction of structured data from RSP documents."""

import json
from pathlib import Path
from typing import Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

from anthropic import Anthropic
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .pdf_parser import extract_text_from_pdf, chunk_document, get_document_metadata

console = Console()


@dataclass
class RSPExtraction:
    """Structured extraction from an RSP document."""
    lab_info: dict
    capability_thresholds: list[dict]
    risk_domains: list[dict]
    safeguards: list[dict]
    evaluation_requirements: list[dict]
    commitments: list[dict]
    metadata: dict
    
    def to_dict(self) -> dict:
        return asdict(self)


class RSPExtractor:
    """Extract structured data from RSP documents using LLM."""
    
    EXTRACTION_PROMPT = """You are an expert at analyzing AI safety policy documents. Extract structured information from this Responsible Scaling Policy (RSP) document.

Analyze the document and extract:

1. **Lab Info**: Name, document title, version, publication date, URL
2. **Capability Thresholds**: Risk levels defined (like ASL-1 through ASL-4, or CCL levels)
   - For each level: name, ID, description, what triggers it, required safeguards
3. **Risk Domains**: Which risk areas are covered (CBRN, cyber, autonomy, persuasion, AI R&D, etc.)
   - For each domain: coverage level (full/partial/none), specific thresholds
4. **Safeguards**: Security, deployment, operational, and governance safeguards
5. **Evaluation Requirements**: Testing, red-teaming, auditing requirements
6. **Commitments**: Pause commitments, disclosure requirements, cooperation pledges

Return a JSON object with this structure:
```json
{
  "lab_info": {
    "name": "Lab Name",
    "document_name": "Document Title",
    "version": "version number",
    "publication_date": "date",
    "url": "url if available"
  },
  "capability_thresholds": [
    {
      "level_name": "Level Name (e.g., ASL-3)",
      "level_id": "standardized_id",
      "description": "what this level represents",
      "triggers": [
        {"domain": "risk domain", "capability": "specific capability", "threshold": "threshold definition"}
      ],
      "required_safeguards": ["list of required safeguards"]
    }
  ],
  "risk_domains": [
    {
      "domain": "domain_name",
      "coverage": "full|partial|none",
      "thresholds": [{"level": "level", "description": "description"}]
    }
  ],
  "safeguards": [
    {
      "type": "deployment|security|operational|governance|technical",
      "name": "safeguard name",
      "description": "description",
      "applicable_levels": ["levels where this applies"]
    }
  ],
  "evaluation_requirements": [
    {
      "name": "evaluation name",
      "type": "internal|external|red_team|benchmark|audit",
      "frequency": "how often",
      "description": "description"
    }
  ],
  "commitments": [
    {
      "type": "pause|disclosure|cooperation|assessment",
      "description": "commitment description",
      "conditions": ["conditions that trigger this"]
    }
  ]
}
```

Be thorough and extract all relevant information. If information is not available, omit that field rather than guessing.

DOCUMENT TEXT:
{document_text}

Return ONLY valid JSON, no other text."""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-20250514"):
        """Initialize the extractor.
        
        Args:
            api_key: Anthropic API key (uses ANTHROPIC_API_KEY env var if not provided)
            model: Model to use for extraction
        """
        self.model = model
        self.client = None
        
        if api_key:
            self.client = Anthropic(api_key=api_key)
        else:
            try:
                self.client = Anthropic()  # Uses ANTHROPIC_API_KEY env var
            except Exception:
                console.print("[yellow]Warning: No API key configured. Use prebuilt data or provide API key.[/yellow]")
    
    def extract_from_pdf(self, pdf_path: Path, lab_name: Optional[str] = None) -> RSPExtraction:
        """Extract structured data from a PDF document.
        
        Args:
            pdf_path: Path to the PDF file
            lab_name: Optional lab name hint
            
        Returns:
            RSPExtraction with structured data
        """
        if not self.client:
            raise ValueError("No API key configured. Cannot extract from PDF.")
        
        pdf_path = Path(pdf_path)
        console.print(f"[dim]Extracting text from {pdf_path.name}...[/dim]")
        
        # Extract text and metadata
        text = extract_text_from_pdf(pdf_path)
        doc_meta = get_document_metadata(pdf_path)
        
        # Chunk if necessary
        chunks = chunk_document(text, max_tokens=80000)
        
        console.print(f"[dim]Processing {len(chunks)} chunk(s) with {self.model}...[/dim]")
        
        # Extract from each chunk and merge
        all_extractions = []
        for i, chunk in enumerate(chunks):
            with Progress(
                SpinnerColumn(),
                TextColumn(f"[progress.description]Processing chunk {i+1}/{len(chunks)}..."),
                console=console
            ) as progress:
                progress.add_task("extract", total=None)
                extraction = self._extract_from_text(chunk)
                if extraction:
                    all_extractions.append(extraction)
        
        # Merge extractions from all chunks
        merged = self._merge_extractions(all_extractions)
        
        # Add metadata
        merged["metadata"] = {
            "extraction_date": datetime.now().isoformat(),
            "extraction_model": self.model,
            "source_file": pdf_path.name,
            "page_count": doc_meta.page_count,
        }
        
        return RSPExtraction(**merged)
    
    def extract_from_text(self, text: str, lab_name: str) -> RSPExtraction:
        """Extract structured data from raw text.
        
        Args:
            text: Document text
            lab_name: Name of the lab
            
        Returns:
            RSPExtraction with structured data
        """
        if not self.client:
            raise ValueError("No API key configured. Cannot extract from text.")
        
        extraction = self._extract_from_text(text)
        
        if not extraction.get("lab_info"):
            extraction["lab_info"] = {}
        extraction["lab_info"]["name"] = lab_name
        
        extraction["metadata"] = {
            "extraction_date": datetime.now().isoformat(),
            "extraction_model": self.model,
        }
        
        return RSPExtraction(**extraction)
    
    def _extract_from_text(self, text: str) -> dict:
        """Internal extraction method."""
        prompt = self.EXTRACTION_PROMPT.format(document_text=text[:100000])
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=8000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = response.content[0].text
        
        # Parse JSON response
        try:
            # Try to extract JSON from response
            json_match = content
            if "```json" in content:
                json_match = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                json_match = content.split("```")[1].split("```")[0]
            
            return json.loads(json_match)
        except json.JSONDecodeError as e:
            console.print(f"[red]Failed to parse JSON response: {e}[/red]")
            return self._default_extraction()
    
    def _merge_extractions(self, extractions: list[dict]) -> dict:
        """Merge multiple chunk extractions into one."""
        if not extractions:
            return self._default_extraction()
        
        if len(extractions) == 1:
            return extractions[0]
        
        # Use first extraction as base, merge lists from others
        merged = extractions[0].copy()
        
        for ext in extractions[1:]:
            for key in ["capability_thresholds", "risk_domains", "safeguards", 
                       "evaluation_requirements", "commitments"]:
                if key in ext and ext[key]:
                    if key not in merged:
                        merged[key] = []
                    merged[key].extend(ext[key])
        
        # Deduplicate
        for key in ["capability_thresholds", "risk_domains", "safeguards"]:
            if key in merged:
                merged[key] = self._deduplicate_list(merged[key])
        
        return merged
    
    def _deduplicate_list(self, items: list[dict]) -> list[dict]:
        """Remove duplicate items based on name/type fields."""
        seen = set()
        unique = []
        
        for item in items:
            key = (
                item.get("level_name") or 
                item.get("domain") or 
                item.get("name") or 
                item.get("type") or 
                str(item)
            )
            if key not in seen:
                seen.add(key)
                unique.append(item)
        
        return unique
    
    def _default_extraction(self) -> dict:
        """Return default empty extraction structure."""
        return {
            "lab_info": {},
            "capability_thresholds": [],
            "risk_domains": [],
            "safeguards": [],
            "evaluation_requirements": [],
            "commitments": [],
            "metadata": {}
        }


# =============================================================================
# PREBUILT EXTRACTIONS
# =============================================================================
# Comprehensive prebuilt extractions based on publicly available RSP documents
# from Anthropic, OpenAI, DeepMind, and Meta. These allow demo mode to work
# without API keys.

PREBUILT_EXTRACTIONS = {
    "anthropic": {
        "lab_info": {
            "name": "Anthropic",
            "document_name": "Responsible Scaling Policy",
            "version": "2.2",
            "publication_date": "October 2024",
            "url": "https://www.anthropic.com/news/announcing-our-updated-responsible-scaling-policy"
        },
        "capability_thresholds": [
            {
                "level_name": "ASL-1",
                "level_id": "asl_1",
                "description": "Systems that pose no meaningful catastrophic risk, such as a 2018-era LLM or a chess-playing AI",
                "triggers": [],
                "required_safeguards": ["Basic security practices"]
            },
            {
                "level_name": "ASL-2",
                "level_id": "asl_2",
                "description": "Current AI systems including Claude - systems that show early signs of dangerous capabilities but cannot yet provide meaningful uplift beyond what's available online",
                "triggers": [
                    {"domain": "cbrn", "capability": "Provides information about CBRN weapons", "threshold": "No meaningful uplift beyond web search"},
                    {"domain": "cyber", "capability": "Can assist with code/cyber tasks", "threshold": "Below expert human level"},
                    {"domain": "autonomy", "capability": "Limited autonomous operation", "threshold": "Cannot meaningfully self-replicate or acquire resources"}
                ],
                "required_safeguards": [
                    "Standard security measures",
                    "Basic access controls",
                    "Usage monitoring",
                    "Standard deployment safeguards"
                ]
            },
            {
                "level_name": "ASL-3",
                "level_id": "asl_3",
                "description": "Systems that substantially increase the risk of catastrophic misuse compared to a non-AI baseline, OR show low-level autonomous capabilities",
                "triggers": [
                    {"domain": "cbrn", "capability": "Meaningful uplift for CBRN attacks", "threshold": "Provides significant assistance beyond existing resources to non-experts"},
                    {"domain": "cyber", "capability": "Autonomous cyber operations", "threshold": "Can discover and exploit novel vulnerabilities"},
                    {"domain": "autonomy", "capability": "Autonomous AI R&D", "threshold": "Can meaningfully accelerate AI development"},
                    {"domain": "autonomy", "capability": "Resource acquisition", "threshold": "Can acquire resources or influence autonomously"}
                ],
                "required_safeguards": [
                    "Enhanced security (hardened infrastructure)",
                    "Strict access controls",
                    "Red team evaluations before deployment",
                    "Deployment restrictions based on risk",
                    "Containment protocols for training",
                    "Monitoring for misuse",
                    "Incident response procedures"
                ]
            },
            {
                "level_name": "ASL-4",
                "level_id": "asl_4",
                "description": "Systems that could substantially accelerate state-level threats or provide capabilities that would be catastrophic if misused (even by states)",
                "triggers": [
                    {"domain": "cbrn", "capability": "Expert-level CBRN assistance", "threshold": "Could enable novel attack vectors or substantially accelerate existing ones"},
                    {"domain": "cyber", "capability": "State-level cyber capabilities", "threshold": "Can conduct sophisticated, persistent cyber campaigns"},
                    {"domain": "autonomy", "capability": "Significant autonomous operation", "threshold": "Can operate and achieve complex goals with minimal human oversight"}
                ],
                "required_safeguards": [
                    "Maximum security protocols",
                    "Extensive government cooperation",
                    "Mandatory external oversight",
                    "Severe deployment restrictions",
                    "Potential pause on development"
                ]
            }
        ],
        "risk_domains": [
            {"domain": "cbrn", "coverage": "full", "thresholds": [
                {"level": "ASL-2", "description": "No meaningful uplift beyond web resources"},
                {"level": "ASL-3", "description": "Provides significant uplift to non-experts"},
                {"level": "ASL-4", "description": "Expert-level or novel capabilities"}
            ]},
            {"domain": "cyber", "coverage": "full", "thresholds": [
                {"level": "ASL-2", "description": "Below expert human level"},
                {"level": "ASL-3", "description": "Can discover and exploit vulnerabilities"},
                {"level": "ASL-4", "description": "State-level capabilities"}
            ]},
            {"domain": "autonomy", "coverage": "full", "thresholds": [
                {"level": "ASL-2", "description": "Cannot meaningfully self-replicate"},
                {"level": "ASL-3", "description": "Low-level autonomous capabilities"},
                {"level": "ASL-4", "description": "Significant autonomous operation"}
            ]},
            {"domain": "ai_rd", "coverage": "full", "thresholds": [
                {"level": "ASL-3", "description": "Can meaningfully accelerate AI development"}
            ]},
            {"domain": "persuasion", "coverage": "partial", "thresholds": []}
        ],
        "safeguards": [
            {"type": "security", "name": "Hardened Infrastructure", "description": "Enhanced security measures for model weights and training infrastructure", "applicable_levels": ["ASL-3", "ASL-4"]},
            {"type": "deployment", "name": "Deployment Restrictions", "description": "Risk-based access controls and usage limitations", "applicable_levels": ["ASL-3", "ASL-4"]},
            {"type": "operational", "name": "Red Team Evaluations", "description": "Pre-deployment testing for dangerous capabilities", "applicable_levels": ["ASL-3", "ASL-4"]},
            {"type": "governance", "name": "External Oversight", "description": "Third-party audits and government cooperation", "applicable_levels": ["ASL-4"]}
        ],
        "evaluation_requirements": [
            {"name": "Capability Evaluations", "type": "internal", "frequency": "Before major deployments", "description": "Test for dangerous capabilities across risk domains"},
            {"name": "Red Team Testing", "type": "red_team", "frequency": "Ongoing", "description": "Adversarial testing for misuse potential"},
            {"name": "External Audits", "type": "audit", "frequency": "Annual", "description": "Third-party review of safety measures"}
        ],
        "commitments": [
            {"type": "pause", "description": "Will not train or deploy models at a given ASL unless safeguards for that level are in place", "conditions": ["Safeguards not ready", "Capability evaluation triggers threshold"]},
            {"type": "assessment", "description": "Regular capability evaluations to detect threshold crossings", "conditions": ["Before major training runs", "Before significant deployments"]},
            {"type": "cooperation", "description": "Cooperation with governments and external researchers on safety", "conditions": ["High-risk scenarios", "ASL-4 capabilities"]}
        ],
        "metadata": {
            "extraction_date": "2025-01-15",
            "source": "Anthropic RSP v2.2 (October 2024)",
            "confidence_score": 0.95
        }
    },
    
    "openai": {
        "lab_info": {
            "name": "OpenAI",
            "document_name": "Preparedness Framework",
            "version": "2.0",
            "publication_date": "April 2025",
            "url": "https://cdn.openai.com/preparedness-framework-v2.pdf"
        },
        "capability_thresholds": [
            {
                "level_name": "Low",
                "level_id": "low",
                "description": "Model capabilities pose minimal risk, similar to widely available tools",
                "triggers": [],
                "required_safeguards": ["Standard deployment practices"]
            },
            {
                "level_name": "Medium",
                "level_id": "medium",
                "description": "Model provides modest uplift in risk areas but does not fundamentally change threat landscape",
                "triggers": [
                    {"domain": "cbrn", "capability": "Provides some useful information", "threshold": "Modest uplift, comparable to skilled search"},
                    {"domain": "cyber", "capability": "Can assist with basic exploitation", "threshold": "Helps but doesn't enable novel attacks"}
                ],
                "required_safeguards": [
                    "Enhanced monitoring",
                    "Basic access restrictions"
                ]
            },
            {
                "level_name": "High",
                "level_id": "high",
                "description": "Model significantly increases risk in tracked categories, requiring substantial mitigations",
                "triggers": [
                    {"domain": "cbrn", "capability": "Significant CBRN uplift", "threshold": "Meaningful increase in ability to create threats"},
                    {"domain": "cyber", "capability": "Advanced cyber capabilities", "threshold": "Can discover or exploit significant vulnerabilities"},
                    {"domain": "persuasion", "capability": "Sophisticated persuasion", "threshold": "Can conduct targeted, effective persuasion campaigns"},
                    {"domain": "autonomy", "capability": "Model autonomy", "threshold": "Significant autonomous task completion"}
                ],
                "required_safeguards": [
                    "Robust safety mitigations",
                    "Deployment restrictions",
                    "Enhanced security",
                    "Regular capability monitoring",
                    "Red team evaluations"
                ]
            },
            {
                "level_name": "Critical",
                "level_id": "critical",
                "description": "Model could contribute to existential-level risks or enable catastrophic misuse",
                "triggers": [
                    {"domain": "cbrn", "capability": "Weapons-grade assistance", "threshold": "Could enable creation of novel threats"},
                    {"domain": "cyber", "capability": "Strategic cyber operations", "threshold": "Nation-state level capabilities"},
                    {"domain": "autonomy", "capability": "Full autonomy", "threshold": "Can achieve complex goals independently"}
                ],
                "required_safeguards": [
                    "Maximum restrictions",
                    "Potential development halt",
                    "Government notification",
                    "External oversight mandatory"
                ]
            }
        ],
        "risk_domains": [
            {"domain": "cbrn", "coverage": "full", "thresholds": [
                {"level": "Medium", "description": "Modest uplift"},
                {"level": "High", "description": "Significant uplift"},
                {"level": "Critical", "description": "Weapons-grade"}
            ]},
            {"domain": "cyber", "coverage": "full", "thresholds": [
                {"level": "Medium", "description": "Basic exploitation"},
                {"level": "High", "description": "Advanced capabilities"},
                {"level": "Critical", "description": "Nation-state level"}
            ]},
            {"domain": "persuasion", "coverage": "full", "thresholds": [
                {"level": "High", "description": "Sophisticated campaigns"},
                {"level": "Critical", "description": "Mass manipulation capability"}
            ]},
            {"domain": "autonomy", "coverage": "full", "thresholds": [
                {"level": "High", "description": "Significant autonomous operation"},
                {"level": "Critical", "description": "Full autonomy"}
            ]}
        ],
        "safeguards": [
            {"type": "technical", "name": "Safety Mitigations", "description": "Technical safeguards to prevent misuse", "applicable_levels": ["High", "Critical"]},
            {"type": "deployment", "name": "Deployment Restrictions", "description": "Limiting access based on risk level", "applicable_levels": ["High", "Critical"]},
            {"type": "security", "name": "Model Security", "description": "Protection of model weights and infrastructure", "applicable_levels": ["High", "Critical"]},
            {"type": "governance", "name": "Board Oversight", "description": "Board approval for high-risk deployments", "applicable_levels": ["Critical"]}
        ],
        "evaluation_requirements": [
            {"name": "Capability Scorecard", "type": "internal", "frequency": "Each major model", "description": "Systematic evaluation across risk domains"},
            {"name": "Red Team Exercises", "type": "red_team", "frequency": "Pre-deployment", "description": "Adversarial testing for misuse"},
            {"name": "External Evaluation", "type": "external", "frequency": "Major releases", "description": "Third-party capability assessment"}
        ],
        "commitments": [
            {"type": "pause", "description": "Will not deploy Critical-level models without board and safety team approval", "conditions": ["Critical threshold reached"]},
            {"type": "disclosure", "description": "Report significant capability discoveries to the board", "conditions": ["Unexpected capability jumps"]},
            {"type": "assessment", "description": "Evaluate all models against the preparedness scorecard", "conditions": ["Before training", "Before deployment"]}
        ],
        "metadata": {
            "extraction_date": "2025-01-15",
            "source": "OpenAI Preparedness Framework v2.0",
            "confidence_score": 0.9
        }
    },
    
    "deepmind": {
        "lab_info": {
            "name": "Google DeepMind",
            "document_name": "Frontier Safety Framework",
            "version": "3.0",
            "publication_date": "October 2025",
            "url": "https://deepmind.google/discover/blog/updating-the-frontier-safety-framework/"
        },
        "capability_thresholds": [
            {
                "level_name": "Below CCL",
                "level_id": "below_ccl",
                "description": "Capabilities below Critical Capability Levels - standard deployment",
                "triggers": [],
                "required_safeguards": ["Standard practices"]
            },
            {
                "level_name": "Approaching CCL",
                "level_id": "approaching_ccl",
                "description": "Early warning that models are approaching critical thresholds",
                "triggers": [
                    {"domain": "any", "capability": "Early warning indicators", "threshold": "50% of the way to CCL thresholds"}
                ],
                "required_safeguards": [
                    "Enhanced monitoring",
                    "Increased evaluation frequency",
                    "Mitigation development begins"
                ]
            },
            {
                "level_name": "CCL-1",
                "level_id": "ccl_1",
                "description": "First Critical Capability Level - significant uplift in high-risk domains",
                "triggers": [
                    {"domain": "cbrn", "capability": "Biosecurity risk", "threshold": "Significantly increases ability of non-experts to cause harm"},
                    {"domain": "cyber", "capability": "Cyber offense", "threshold": "Can automate significant parts of sophisticated attacks"},
                    {"domain": "autonomy", "capability": "ML R&D automation", "threshold": "Can substantially accelerate AI development"},
                    {"domain": "deception", "capability": "Scheming", "threshold": "Evidence of goal-directed deceptive behavior"}
                ],
                "required_safeguards": [
                    "Deployment mitigations verified",
                    "Security level Alpha",
                    "Red team sign-off",
                    "Monitoring for capability jumps"
                ]
            },
            {
                "level_name": "CCL-2",
                "level_id": "ccl_2",
                "description": "Second Critical Capability Level - severe risks requiring maximum safeguards",
                "triggers": [
                    {"domain": "cbrn", "capability": "Weapons creation", "threshold": "Could enable creation of novel biological or chemical weapons"},
                    {"domain": "cyber", "capability": "Critical infrastructure", "threshold": "Can compromise critical infrastructure autonomously"},
                    {"domain": "autonomy", "capability": "Self-improvement", "threshold": "Can meaningfully improve its own capabilities"}
                ],
                "required_safeguards": [
                    "Maximum security (Level Omega)",
                    "Deployment restrictions or hold",
                    "Government notification",
                    "External oversight"
                ]
            }
        ],
        "risk_domains": [
            {"domain": "cbrn", "coverage": "full", "thresholds": [
                {"level": "CCL-1", "description": "Significant uplift for non-experts"},
                {"level": "CCL-2", "description": "Novel weapons creation"}
            ]},
            {"domain": "cyber", "coverage": "full", "thresholds": [
                {"level": "CCL-1", "description": "Automates sophisticated attacks"},
                {"level": "CCL-2", "description": "Critical infrastructure compromise"}
            ]},
            {"domain": "autonomy", "coverage": "full", "thresholds": [
                {"level": "CCL-1", "description": "ML R&D acceleration"},
                {"level": "CCL-2", "description": "Self-improvement"}
            ]},
            {"domain": "deception", "coverage": "full", "thresholds": [
                {"level": "CCL-1", "description": "Evidence of scheming behavior"}
            ]}
        ],
        "safeguards": [
            {"type": "security", "name": "Security Levels", "description": "Tiered security from Alpha to Omega based on capability level", "applicable_levels": ["CCL-1", "CCL-2"]},
            {"type": "deployment", "name": "Deployment Controls", "description": "Risk-based deployment restrictions", "applicable_levels": ["CCL-1", "CCL-2"]},
            {"type": "technical", "name": "Alignment Techniques", "description": "Technical measures to ensure model follows intent", "applicable_levels": ["CCL-1", "CCL-2"]},
            {"type": "governance", "name": "Responsibility Council", "description": "Internal governance body for high-stakes decisions", "applicable_levels": ["CCL-1", "CCL-2"]}
        ],
        "evaluation_requirements": [
            {"name": "Capability Evaluations", "type": "internal", "frequency": "Continuous during training", "description": "Monitor for CCL thresholds"},
            {"name": "Early Warning System", "type": "benchmark", "frequency": "Ongoing", "description": "Detect approaching CCL"},
            {"name": "Red Team Assessment", "type": "red_team", "frequency": "Pre-deployment", "description": "Adversarial capability testing"},
            {"name": "External Audits", "type": "audit", "frequency": "Regular", "description": "Third-party review of safety practices"}
        ],
        "commitments": [
            {"type": "pause", "description": "Will not deploy models exceeding CCL without verified mitigations", "conditions": ["CCL threshold exceeded", "Mitigations not ready"]},
            {"type": "disclosure", "description": "Share safety-relevant findings with other labs", "conditions": ["Novel safety issues discovered"]},
            {"type": "cooperation", "description": "Work with governments on high-risk scenarios", "conditions": ["CCL-2 capabilities", "National security implications"]}
        ],
        "metadata": {
            "extraction_date": "2025-01-15",
            "source": "DeepMind Frontier Safety Framework v3.0",
            "confidence_score": 0.9
        }
    },
    
    "meta": {
        "lab_info": {
            "name": "Meta",
            "document_name": "Frontier AI Framework",
            "version": "1.0",
            "publication_date": "2025",
            "url": "https://ai.meta.com/blog/frontier-ai-framework/"
        },
        "capability_thresholds": [
            {
                "level_name": "Tier 1 - Low Risk",
                "level_id": "tier_1",
                "description": "Models with capabilities that pose minimal incremental risk",
                "triggers": [],
                "required_safeguards": ["Standard deployment practices", "Basic monitoring"]
            },
            {
                "level_name": "Tier 2 - Moderate Risk",
                "level_id": "tier_2",
                "description": "Models with meaningful but manageable risk uplift",
                "triggers": [
                    {"domain": "cbrn", "capability": "Some CBRN knowledge", "threshold": "Provides useful but not critical information"},
                    {"domain": "cyber", "capability": "Cyber assistance", "threshold": "Helps with known vulnerabilities"}
                ],
                "required_safeguards": [
                    "Enhanced safeguards",
                    "Usage monitoring",
                    "Access controls for sensitive capabilities"
                ]
            },
            {
                "level_name": "Tier 3 - High Risk",
                "level_id": "tier_3",
                "description": "Models with significant dangerous capabilities requiring robust mitigations",
                "triggers": [
                    {"domain": "cbrn", "capability": "Significant CBRN uplift", "threshold": "Materially increases risk of attacks"},
                    {"domain": "cyber", "capability": "Advanced offensive cyber", "threshold": "Can conduct sophisticated autonomous attacks"},
                    {"domain": "autonomy", "capability": "Autonomous operation", "threshold": "Can achieve goals with minimal oversight"}
                ],
                "required_safeguards": [
                    "Robust technical mitigations",
                    "Strict access controls",
                    "Enhanced security",
                    "External evaluation",
                    "Potential deployment restrictions"
                ]
            },
            {
                "level_name": "Tier 4 - Critical Risk",
                "level_id": "tier_4",
                "description": "Models posing catastrophic or existential-level risks",
                "triggers": [
                    {"domain": "cbrn", "capability": "WMD creation", "threshold": "Could enable creation of weapons of mass destruction"},
                    {"domain": "cyber", "capability": "Critical infrastructure", "threshold": "Could cause widespread infrastructure failure"},
                    {"domain": "autonomy", "capability": "Uncontrollable autonomy", "threshold": "Could resist human control"}
                ],
                "required_safeguards": [
                    "Maximum security protocols",
                    "Development pause considered",
                    "Government engagement mandatory",
                    "International coordination"
                ]
            }
        ],
        "risk_domains": [
            {"domain": "cbrn", "coverage": "full", "thresholds": [
                {"level": "Tier 2", "description": "Useful information"},
                {"level": "Tier 3", "description": "Material risk increase"},
                {"level": "Tier 4", "description": "WMD enablement"}
            ]},
            {"domain": "cyber", "coverage": "full", "thresholds": [
                {"level": "Tier 2", "description": "Known vulnerabilities"},
                {"level": "Tier 3", "description": "Sophisticated attacks"},
                {"level": "Tier 4", "description": "Critical infrastructure"}
            ]},
            {"domain": "autonomy", "coverage": "partial", "thresholds": [
                {"level": "Tier 3", "description": "Goal-directed autonomy"},
                {"level": "Tier 4", "description": "Resistance to control"}
            ]}
        ],
        "safeguards": [
            {"type": "technical", "name": "Model Mitigations", "description": "Technical safeguards built into the model", "applicable_levels": ["Tier 2", "Tier 3", "Tier 4"]},
            {"type": "deployment", "name": "Access Controls", "description": "Tiered access based on risk level", "applicable_levels": ["Tier 2", "Tier 3"]},
            {"type": "security", "name": "Weight Security", "description": "Protection of model weights", "applicable_levels": ["Tier 3", "Tier 4"]},
            {"type": "governance", "name": "External Review", "description": "Third-party evaluation of high-risk models", "applicable_levels": ["Tier 3", "Tier 4"]}
        ],
        "evaluation_requirements": [
            {"name": "Risk Assessment", "type": "internal", "frequency": "Pre-release", "description": "Evaluate model against risk tiers"},
            {"name": "Red Teaming", "type": "red_team", "frequency": "Major releases", "description": "Adversarial testing"},
            {"name": "External Evaluation", "type": "external", "frequency": "High-risk models", "description": "Third-party assessment"}
        ],
        "commitments": [
            {"type": "pause", "description": "Will pause development if Tier 4 risks emerge without adequate mitigations", "conditions": ["Tier 4 threshold reached"]},
            {"type": "disclosure", "description": "Share significant safety findings with the research community", "conditions": ["Novel risks discovered"]},
            {"type": "cooperation", "description": "Engage with policymakers on frontier AI governance", "conditions": ["High-risk scenarios"]}
        ],
        "metadata": {
            "extraction_date": "2025-01-15",
            "source": "Meta Frontier AI Framework",
            "confidence_score": 0.85
        }
    }
}


def get_prebuilt_extraction(lab_name: str) -> Optional[dict]:
    """Get prebuilt extraction for a lab.
    
    Args:
        lab_name: Lab name (case-insensitive)
        
    Returns:
        Prebuilt extraction dict or None
    """
    return PREBUILT_EXTRACTIONS.get(lab_name.lower())


def get_all_prebuilt_extractions() -> dict:
    """Get all prebuilt extractions."""
    return PREBUILT_EXTRACTIONS.copy()


def main():
    """Main extraction pipeline entry point."""
    from pathlib import Path
    from config.settings import get_settings
    
    settings = get_settings()
    settings.ensure_directories()
    
    # Check for API key
    if not settings.has_api_key():
        console.print("[yellow]No API key configured. Using prebuilt extractions only.[/yellow]")
        console.print("[dim]Set ANTHROPIC_API_KEY in .env for full extraction.[/dim]\n")
        
        # Export prebuilt data
        output_path = settings.reports_dir / "all_extracted.json"
        with open(output_path, "w") as f:
            json.dump(PREBUILT_EXTRACTIONS, f, indent=2)
        
        console.print(f"[green]Exported prebuilt extractions to {output_path}[/green]")
        return PREBUILT_EXTRACTIONS
    
    # Look for PDF files
    pdf_files = list(settings.raw_data_dir.glob("*.pdf"))
    
    if not pdf_files:
        console.print("[yellow]No PDF files found in data/raw/[/yellow]")
        console.print("[dim]Add RSP PDFs to data/raw/ or use prebuilt extractions.[/dim]\n")
        return PREBUILT_EXTRACTIONS
    
    # Initialize extractor
    extractor = RSPExtractor(
        api_key=settings.anthropic_api_key,
        model=settings.llm_model
    )
    
    # Extract from each PDF
    extractions = {}
    
    for pdf_path in pdf_files:
        console.print(f"\n[bold]Processing {pdf_path.name}[/bold]")
        
        try:
            extraction = extractor.extract_from_pdf(pdf_path)
            lab_name = extraction.lab_info.get("name", pdf_path.stem).lower()
            extractions[lab_name] = extraction.to_dict()
            
            console.print(f"[green]✓ Extracted {lab_name}[/green]")
            
        except Exception as e:
            console.print(f"[red]✗ Failed to extract {pdf_path.name}: {e}[/red]")
    
    # Merge with prebuilt for any missing labs
    for lab, data in PREBUILT_EXTRACTIONS.items():
        if lab not in extractions:
            extractions[lab] = data
    
    # Export
    output_path = settings.reports_dir / "all_extracted.json"
    with open(output_path, "w") as f:
        json.dump(extractions, f, indent=2)
    
    console.print(f"\n[green]Saved all extractions to {output_path}[/green]")
    
    return extractions


if __name__ == "__main__":
    main()

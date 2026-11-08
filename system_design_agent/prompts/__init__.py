from system_design_agent.prompts.stage1_requirements import STAGE1_PROMPT_TEMPLATE
from system_design_agent.prompts.stage2_hld import STAGE2_PROMPT_TEMPLATE
from system_design_agent.prompts.stage3_lld import STAGE3_PROMPT_TEMPLATE
from system_design_agent.prompts.stage4_resilience import STAGE4_PROMPT_TEMPLATE
from system_design_agent.prompts.stage5_scaffolding import STAGE5_PROMPT_TEMPLATE
from system_design_agent.prompts.system_persona import PRINCIPAL_ARCHITECT_PERSONA

__all__ = [
    "PRINCIPAL_ARCHITECT_PERSONA",
    "STAGE1_PROMPT_TEMPLATE",
    "STAGE2_PROMPT_TEMPLATE",
    "STAGE3_PROMPT_TEMPLATE",
    "STAGE4_PROMPT_TEMPLATE",
    "STAGE5_PROMPT_TEMPLATE",
]

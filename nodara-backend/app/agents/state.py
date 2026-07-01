from typing import TypedDict, List, Dict, Any, Annotated
from langchain_core.messages import BaseMessage
import operator

class NodaraState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    user_id: str
    exam_id: str
    company_code: str
    current_question_index: int
    total_questions: int
    source_manual_language: str
    target_training_language: str
    target_sap_process: str
    active_question_text: str
    active_rubric_json: Dict[str, Any]
    extracted_sap_fields: Dict[str, Any]
    audit_findings: str
    is_approved: bool
    retry_count: int
